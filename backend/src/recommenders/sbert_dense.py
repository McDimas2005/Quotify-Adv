from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .base import BaseRecommender
from ..schemas import Alternative, RecommendationResult, ScoreBreakdown
from ..utils import normalize_rows, normalize_vector, score_with_emotion_boost, write_json


class SbertDenseRecommender(BaseRecommender):
    strategy_id = "sbert_dense"
    label = "Dense Semantic Search"
    description = "Uses SentenceTransformer embeddings for meaning-based quote retrieval with emotion weighting."

    def __init__(self, config, quotes, emotion_classifier):
        super().__init__(config, quotes, emotion_classifier)
        self.model = None
        self.embeddings = None
        self.embedding_path = self.config.artifacts_dir / "quote_embeddings.npy"
        self.metadata_path = self.config.artifacts_dir / "quote_metadata.csv"
        self.manifest_path = self.config.artifacts_dir / "artifact_manifest.json"
        self._load_model_and_artifacts()

    def _load_model_and_artifacts(self) -> None:
        if not self.config.enable_sbert:
            self.unavailable_reason = "Dense retrieval is disabled by QUOTIFY_ENABLE_SBERT."
            return
        try:
            from sentence_transformers import SentenceTransformer
        except Exception as exc:
            self.unavailable_reason = f"sentence-transformers is unavailable: {exc}"
            return

        try:
            self.model = SentenceTransformer(self.config.sbert_model_name)
            self.config.artifacts_dir.mkdir(parents=True, exist_ok=True)
            if self.embedding_path.exists():
                embeddings = np.load(self.embedding_path)
                if embeddings.shape[0] == len(self.quotes):
                    self.embeddings = normalize_rows(embeddings.astype("float32"))
                else:
                    self.embeddings = self._build_embeddings()
            else:
                self.embeddings = self._build_embeddings()
        except Exception as exc:
            self.unavailable_reason = f"Failed to load dense retrieval model/artifacts: {exc}"

    def _build_embeddings(self) -> np.ndarray:
        embeddings = self.model.encode(
            self.quotes["Quote"].tolist(),
            batch_size=64,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,
        ).astype("float32")
        np.save(self.embedding_path, embeddings)
        self.quotes.to_csv(self.metadata_path, index=False)
        write_json(
            self.manifest_path,
            {
                "model": self.config.sbert_model_name,
                "quote_count": int(len(self.quotes)),
                "embedding_file": self.embedding_path.name,
                "metadata_file": self.metadata_path.name,
            },
        )
        return embeddings

    def recommend(self, input_text: str, top_k: int = 5) -> RecommendationResult:
        self._require_available()
        user_emotion = self.emotion_classifier.predict(input_text)
        query = self.model.encode([input_text], convert_to_numpy=True, normalize_embeddings=True)[0].astype("float32")
        query = normalize_vector(query)
        semantic_scores = np.dot(self.embeddings, query)
        return self._format_result(input_text, user_emotion, semantic_scores, top_k)

    def _format_result(self, input_text: str, user_emotion: str, semantic_scores, top_k: int) -> RecommendationResult:
        final_scores = []
        boosts = []
        for score, quote_emotion in zip(semantic_scores, self.quotes["emotion"]):
            final, boost = score_with_emotion_boost(float(score), quote_emotion, user_emotion, self.config.emotion_boost)
            final_scores.append(final)
            boosts.append(boost)

        final_scores = np.array(final_scores)
        boosts = np.array(boosts)
        indices = self._top_indices(final_scores, max(top_k, 1))
        selected_idx = indices[0]
        selected = self.quotes.iloc[selected_idx]
        alternatives = [
            Alternative(
                quote=str(self.quotes.iloc[idx]["Quote"]),
                author=str(self.quotes.iloc[idx]["Author"]),
                quote_emotion=str(self.quotes.iloc[idx]["emotion"]),
                final_score=round(float(final_scores[idx]), 4),
            )
            for idx in indices[1:top_k]
        ]
        return RecommendationResult(
            quote=str(selected["Quote"]),
            author=str(selected["Author"]),
            emotion=user_emotion,
            quote_emotion=str(selected["emotion"]),
            strategy=self.strategy_id,
            strategy_label=self.label,
            scores=ScoreBreakdown(
                semantic_score=round(float(semantic_scores[selected_idx]), 4),
                cross_encoder_score=None,
                emotion_boost=round(float(boosts[selected_idx]), 4),
                final_score=round(float(final_scores[selected_idx]), 4),
            ),
            alternatives=alternatives,
        )

    def artifact_status(self) -> dict:
        manifest = {}
        if self.manifest_path.exists():
            try:
                manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception:
                manifest = {}
        return {
            "quote_embeddings.npy": self.embedding_path.exists(),
            "quote_metadata.csv": self.metadata_path.exists(),
            "artifact_manifest.json": self.manifest_path.exists(),
            "manifest": manifest,
        }

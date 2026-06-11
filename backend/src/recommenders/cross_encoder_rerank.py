from __future__ import annotations

import numpy as np

from .base import BaseRecommender
from .sbert_dense import SbertDenseRecommender
from ..schemas import Alternative, RecommendationResult, ScoreBreakdown
from ..utils import normalize_vector, score_with_emotion_boost


class CrossEncoderRerankRecommender(BaseRecommender):
    strategy_id = "cross_encoder_rerank"
    label = "AI Reranker"
    description = (
        "Retrieves candidates with dense embeddings, then reranks them with a Cross-Encoder "
        "and emotion-aware scoring."
    )

    def __init__(self, config, quotes, emotion_classifier, dense_recommender: SbertDenseRecommender):
        super().__init__(config, quotes, emotion_classifier)
        self.dense_recommender = dense_recommender
        self.cross_encoder = None
        if not self.config.enable_cross_encoder:
            self.unavailable_reason = "Cross-Encoder mode is disabled by QUOTIFY_ENABLE_CROSS_ENCODER."
            return
        if not dense_recommender.available:
            self.unavailable_reason = "Dense retriever is unavailable, so reranking cannot run."
            return
        self._load_cross_encoder()

    def _load_cross_encoder(self) -> None:
        try:
            from sentence_transformers import CrossEncoder
        except Exception as exc:
            self.unavailable_reason = f"CrossEncoder dependency unavailable: {exc}"
            return
        try:
            self.cross_encoder = CrossEncoder(self.config.cross_encoder_model_name)
        except Exception as exc:
            self.unavailable_reason = f"Failed to load Cross-Encoder model: {exc}"

    def recommend(self, input_text: str, top_k: int = 5) -> RecommendationResult:
        self._require_available()
        user_emotion = self.emotion_classifier.predict(input_text)
        query = self.dense_recommender.model.encode(
            [input_text], convert_to_numpy=True, normalize_embeddings=True
        )[0].astype("float32")
        query = normalize_vector(query)
        semantic_scores = np.dot(self.dense_recommender.embeddings, query)
        retrieve_count = max(top_k, min(self.config.top_k_retrieve, len(self.quotes)))
        candidate_indices = self._top_indices(semantic_scores, retrieve_count)

        pairs = [(input_text, str(self.quotes.iloc[idx]["Quote"])) for idx in candidate_indices]
        cross_scores = np.array(self.cross_encoder.predict(pairs), dtype="float32")
        if cross_scores.size:
            min_score = float(cross_scores.min())
            max_score = float(cross_scores.max())
            if max_score > min_score:
                normalized_cross = (cross_scores - min_score) / (max_score - min_score)
            else:
                normalized_cross = np.ones_like(cross_scores)
        else:
            normalized_cross = cross_scores

        ranked = []
        for position, idx in enumerate(candidate_indices):
            semantic = float(semantic_scores[idx])
            cross = float(normalized_cross[position])
            blended = (0.35 * semantic) + (0.65 * cross)
            final, boost = score_with_emotion_boost(
                blended, self.quotes.iloc[idx]["emotion"], user_emotion, self.config.emotion_boost
            )
            ranked.append((idx, semantic, cross, boost, final))

        ranked.sort(key=lambda item: item[-1], reverse=True)
        selected_idx, semantic, cross, boost, final = ranked[0]
        selected = self.quotes.iloc[selected_idx]
        alternatives = [
            Alternative(
                quote=str(self.quotes.iloc[idx]["Quote"]),
                author=str(self.quotes.iloc[idx]["Author"]),
                quote_emotion=str(self.quotes.iloc[idx]["emotion"]),
                final_score=round(float(item_final), 4),
            )
            for idx, _, _, _, item_final in ranked[1:top_k]
        ]
        return RecommendationResult(
            quote=str(selected["Quote"]),
            author=str(selected["Author"]),
            emotion=user_emotion,
            quote_emotion=str(selected["emotion"]),
            strategy=self.strategy_id,
            strategy_label=self.label,
            scores=ScoreBreakdown(
                semantic_score=round(float(semantic), 4),
                cross_encoder_score=round(float(cross), 4),
                emotion_boost=round(float(boost), 4),
                final_score=round(float(final), 4),
            ),
            alternatives=alternatives,
        )


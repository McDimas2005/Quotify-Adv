from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .base import BaseRecommender
from ..schemas import Alternative, RecommendationResult, ScoreBreakdown
from ..utils import score_with_emotion_boost


class LegacyTfidfRecommender(BaseRecommender):
    strategy_id = "legacy_tfidf_bert"
    label = "Legacy BERT + TF-IDF"
    description = (
        "Original project method using fine-tuned BERT emotion classification, "
        "TF-IDF cosine similarity, and emotion weighting."
    )

    def __init__(self, config, quotes, emotion_classifier):
        super().__init__(config, quotes, emotion_classifier)
        try:
            self.vectorizer = TfidfVectorizer()
            self.matrix = self.vectorizer.fit_transform(self.quotes["Quote"].tolist())
        except Exception as exc:
            self.unavailable_reason = f"Failed to build TF-IDF matrix: {exc}"

    def recommend(self, input_text: str, top_k: int = 5) -> RecommendationResult:
        self._require_available()
        user_emotion = self.emotion_classifier.predict(input_text)
        input_vec = self.vectorizer.transform([input_text])
        semantic_scores = cosine_similarity(input_vec, self.matrix).flatten()

        final_scores = []
        boosts = []
        for score, quote_emotion in zip(semantic_scores, self.quotes["emotion"]):
            final, boost = score_with_emotion_boost(score, quote_emotion, user_emotion, self.config.emotion_boost)
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


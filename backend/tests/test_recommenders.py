from dataclasses import replace

import pandas as pd

from src.config import config
from src.emotion_classifier import EmotionClassifier
from src.recommenders.legacy_tfidf import LegacyTfidfRecommender


def test_legacy_recommender_returns_quote_from_fixture():
    quotes = pd.DataFrame(
        [
            {"Quote": "Be happy with this moment.", "Author": "Unknown", "emotion": "joy"},
            {"Quote": "Fear can be a teacher.", "Author": "Unknown", "emotion": "fear"},
        ]
    )
    classifier = EmotionClassifier(replace(config, enable_sbert=False), ["joy", "fear", "anger"])
    recommender = LegacyTfidfRecommender(replace(config, emotion_boost=0.08), quotes, classifier)

    result = recommender.recommend("I am happy and grateful", top_k=2)

    assert result.quote
    assert result.author
    assert result.strategy == "legacy_tfidf_bert"
    assert result.scores.final_score >= result.scores.semantic_score

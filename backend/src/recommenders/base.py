from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from ..config import AppConfig
from ..emotion_classifier import EmotionClassifier
from ..schemas import RecommendationResult, StrategyInfo


class BaseRecommender(ABC):
    strategy_id: str
    label: str
    description: str

    def __init__(self, config: AppConfig, quotes: pd.DataFrame, emotion_classifier: EmotionClassifier):
        self.config = config
        self.quotes = quotes.reset_index(drop=True)
        self.emotion_classifier = emotion_classifier
        self.unavailable_reason = ""

    @property
    def available(self) -> bool:
        return not self.unavailable_reason

    def info(self) -> StrategyInfo:
        return StrategyInfo(
            id=self.strategy_id,
            label=self.label,
            description=self.description,
            available=self.available,
            reason=self.unavailable_reason or None,
        )

    @abstractmethod
    def recommend(self, input_text: str, top_k: int = 5) -> RecommendationResult:
        raise NotImplementedError

    def _require_available(self) -> None:
        if not self.available:
            raise RuntimeError(f"{self.label} is unavailable: {self.unavailable_reason}")

    @staticmethod
    def _top_indices(scores, limit: int) -> List[int]:
        limit = max(1, min(int(limit), len(scores)))
        return list(scores.argsort()[-limit:][::-1])


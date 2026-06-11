from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ScoreBreakdown:
    semantic_score: Optional[float]
    cross_encoder_score: Optional[float]
    emotion_boost: float
    final_score: float

    def to_dict(self) -> Dict[str, Optional[float]]:
        return {
            "semantic_score": self.semantic_score,
            "cross_encoder_score": self.cross_encoder_score,
            "emotion_boost": self.emotion_boost,
            "final_score": self.final_score,
        }


@dataclass
class Alternative:
    quote: str
    author: str
    quote_emotion: str
    final_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quote": self.quote,
            "author": self.author,
            "quote_emotion": self.quote_emotion,
            "final_score": self.final_score,
        }


@dataclass
class RecommendationResult:
    quote: str
    author: str
    emotion: str
    quote_emotion: str
    strategy: str
    strategy_label: str
    scores: ScoreBreakdown
    alternatives: List[Alternative] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "quote": self.quote,
            "author": self.author,
            "emotion": self.emotion,
            "quote_emotion": self.quote_emotion,
            "strategy": self.strategy,
            "strategy_label": self.strategy_label,
            "scores": self.scores.to_dict(),
            "alternatives": [item.to_dict() for item in self.alternatives],
        }


@dataclass
class StrategyInfo:
    id: str
    label: str
    description: str
    available: bool
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "available": self.available,
        }
        if self.reason:
            payload["reason"] = self.reason
        return payload


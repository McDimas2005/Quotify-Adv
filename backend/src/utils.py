from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import numpy as np


def normalize_emotion(value: Any) -> str:
    return str(value or "").strip().lower()


def normalize_rows(scores: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(scores, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return scores / norms


def normalize_vector(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def score_with_emotion_boost(score: float, quote_emotion: str, user_emotion: str, boost: float) -> tuple[float, float]:
    applied_boost = boost if normalize_emotion(quote_emotion) == normalize_emotion(user_emotion) else 0.0
    return float(score + applied_boost), float(applied_boost)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


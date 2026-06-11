from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from .config import AppConfig
from .utils import normalize_emotion


@dataclass
class LoadedData:
    emotion_data: pd.DataFrame
    quotes: pd.DataFrame


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Required dataset is missing: {path}")
    return pd.read_csv(path)


def load_data(config: AppConfig, quotes_override: Optional[pd.DataFrame] = None) -> LoadedData:
    emotion_data = _read_csv(config.emotion_dataset_path)
    emotion_data = emotion_data.dropna(subset=["Comment", "Emotion"]).drop_duplicates(subset="Comment")
    emotion_data["Emotion"] = emotion_data["Emotion"].map(normalize_emotion)

    if quotes_override is None:
        quotes = _read_csv(config.quotes_dataset_path)
    else:
        quotes = quotes_override.copy()

    quotes = quotes.dropna(subset=["Quote", "Author", "emotion"]).drop_duplicates(subset="Quote")
    quotes["emotion"] = quotes["emotion"].map(normalize_emotion)
    quotes = quotes.reset_index(drop=True)
    return LoadedData(emotion_data=emotion_data, quotes=quotes)


#!/usr/bin/env python3
"""Build and cache SentenceTransformer quote embeddings."""

from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from src.config import config
from src.data_loader import load_data
from src.emotion_classifier import EmotionClassifier
from src.recommenders.sbert_dense import SbertDenseRecommender


def main() -> int:
    loaded = load_data(config)
    classifier = EmotionClassifier(config, loaded.emotion_data["Emotion"].unique())
    recommender = SbertDenseRecommender(config, loaded.quotes, classifier)
    if not recommender.available:
        print(f"Could not build dense index: {recommender.unavailable_reason}")
        return 1
    print(f"Built dense index for {len(loaded.quotes)} quotes.")
    print(f"Artifacts directory: {config.artifacts_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


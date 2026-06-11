#!/usr/bin/env python3
"""Validate model and strategy availability without starting a server."""

from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from src.config import config


def main() -> int:
    app = create_app(config)
    state = app.extensions["quotify"]
    print(f"{config.app_name} {config.version}")
    print("Strategies:")
    for strategy in state["recommenders"].values():
        status = "available" if strategy.available else f"unavailable - {strategy.unavailable_reason}"
        print(f"- {strategy.strategy_id}: {status}")
    print("Emotion classifier:")
    print(state["emotion_classifier"].status.to_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


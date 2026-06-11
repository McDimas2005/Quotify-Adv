from __future__ import annotations

from pathlib import Path
from typing import Dict

from .config import AppConfig


def artifact_status(config: AppConfig, dense_recommender=None) -> Dict[str, object]:
    status = {
        "artifacts_dir": str(config.artifacts_dir),
        "quote_embeddings.npy": (config.artifacts_dir / "quote_embeddings.npy").exists(),
        "quote_metadata.csv": (config.artifacts_dir / "quote_metadata.csv").exists(),
        "artifact_manifest.json": (config.artifacts_dir / "artifact_manifest.json").exists(),
    }
    if dense_recommender is not None and hasattr(dense_recommender, "artifact_status"):
        status.update(dense_recommender.artifact_status())
    return status


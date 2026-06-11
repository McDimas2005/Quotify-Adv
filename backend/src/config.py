import os
from dataclasses import dataclass
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppConfig:
    app_name: str = "Quotify"
    version: str = "2.0.0"
    root_dir: Path = Path(__file__).resolve().parents[2]
    backend_dir: Path = Path(__file__).resolve().parents[1]
    default_strategy: str = os.getenv("QUOTIFY_DEFAULT_STRATEGY", "sbert_dense")
    enable_sbert: bool = _env_bool("QUOTIFY_ENABLE_SBERT", True)
    enable_cross_encoder: bool = _env_bool("QUOTIFY_ENABLE_CROSS_ENCODER", True)
    emotion_boost: float = float(os.getenv("QUOTIFY_EMOTION_BOOST", "0.08"))
    top_k_retrieve: int = int(os.getenv("QUOTIFY_TOP_K_RETRIEVE", "50"))
    model_checkpoint_path: Path = Path(
        os.getenv("QUOTIFY_MODEL_CHECKPOINT_PATH", "last_trained_model_checkpoint.pth")
    )
    sbert_model_name: str = os.getenv("QUOTIFY_SBERT_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    cross_encoder_model_name: str = os.getenv(
        "QUOTIFY_CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L6-v2"
    )
    port: int = int(os.getenv("PORT", "7860"))
    cors_origins: str = os.getenv("QUOTIFY_CORS_ORIGINS", "")

    @property
    def emotion_dataset_path(self) -> Path:
        return self.backend_dir / "(Preprocessed)Emotion_classify_Data(Labeled).csv"

    @property
    def quotes_dataset_path(self) -> Path:
        return self.backend_dir / "(Preprocessed)quotes.csv"

    @property
    def artifacts_dir(self) -> Path:
        return self.backend_dir / "artifacts"

    @property
    def frontend_build_dir(self) -> Path:
        return self.root_dir / "frontend" / "build"

    @property
    def resolved_checkpoint_path(self) -> Path:
        if self.model_checkpoint_path.is_absolute():
            return self.model_checkpoint_path
        return self.backend_dir / self.model_checkpoint_path


config = AppConfig()

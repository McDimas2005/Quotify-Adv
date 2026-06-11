from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

from sklearn.preprocessing import LabelEncoder

from .config import AppConfig
from .utils import normalize_emotion


@dataclass
class EmotionClassifierStatus:
    available: bool
    backend: str
    checkpoint_loaded: bool
    fallback: bool
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "available": self.available,
            "backend": self.backend,
            "checkpoint_loaded": self.checkpoint_loaded,
            "fallback": self.fallback,
            "reason": self.reason,
        }


class EmotionClassifier:
    def __init__(self, config: AppConfig, labels: Iterable[str]):
        self.config = config
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit([normalize_emotion(label) for label in labels])
        self.device = None
        self.tokenizer = None
        self.model = None
        self._status = EmotionClassifierStatus(
            available=True,
            backend="keyword_fallback",
            checkpoint_loaded=False,
            fallback=True,
            reason="Fine-tuned BERT checkpoint was not loaded; using keyword fallback.",
        )
        self._load_bert_if_possible()

    @property
    def status(self) -> EmotionClassifierStatus:
        return self._status

    def _load_bert_if_possible(self) -> None:
        checkpoint_path = self.config.resolved_checkpoint_path
        if not checkpoint_path.exists():
            return

        try:
            import torch
            from transformers import BertForSequenceClassification, BertTokenizer
        except Exception as exc:  # pragma: no cover - depends on optional runtime packages
            self._status = EmotionClassifierStatus(
                available=True,
                backend="keyword_fallback",
                checkpoint_loaded=False,
                fallback=True,
                reason=f"BERT dependencies unavailable: {exc}",
            )
            return

        try:  # pragma: no cover - exercised only when checkpoint/model deps exist
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
            self.model = BertForSequenceClassification.from_pretrained(
                "bert-base-uncased", num_labels=len(self.label_encoder.classes_)
            )
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            self.model.load_state_dict(checkpoint["model_state_dict"], strict=False)
            self.model.to(self.device)
            self.model.eval()
            self._status = EmotionClassifierStatus(
                available=True,
                backend="fine_tuned_bert",
                checkpoint_loaded=True,
                fallback=False,
            )
        except Exception as exc:
            self.tokenizer = None
            self.model = None
            self._status = EmotionClassifierStatus(
                available=True,
                backend="keyword_fallback",
                checkpoint_loaded=False,
                fallback=True,
                reason=f"Failed to load BERT checkpoint: {exc}",
            )

    def predict(self, text: str) -> str:
        if self.model is not None and self.tokenizer is not None:
            return self._predict_with_bert(text)
        return self._predict_with_keywords(text)

    def _predict_with_bert(self, text: str) -> str:  # pragma: no cover - requires external checkpoint
        import torch

        inputs = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=128,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)

        predicted_label = torch.argmax(outputs.logits, dim=1).item()
        return normalize_emotion(self.label_encoder.inverse_transform([predicted_label])[0])

    def _predict_with_keywords(self, text: str) -> str:
        lowered = text.lower()
        keyword_map = {
            "anger": {
                "angry",
                "mad",
                "hate",
                "annoyed",
                "furious",
                "irritated",
                "frustrated",
                "upset",
            },
            "fear": {
                "afraid",
                "fear",
                "scared",
                "nervous",
                "worried",
                "anxious",
                "panic",
                "terrified",
            },
            "joy": {
                "happy",
                "joy",
                "excited",
                "grateful",
                "hopeful",
                "great",
                "love",
                "calm",
            },
        }
        scores = {
            emotion: sum(1 for keyword in keywords if keyword in lowered)
            for emotion, keywords in keyword_map.items()
        }
        best_emotion, best_score = max(scores.items(), key=lambda item: item[1])
        if best_score > 0:
            return best_emotion
        if "fear" in self.label_encoder.classes_:
            return "fear"
        return normalize_emotion(self.label_encoder.classes_[0])


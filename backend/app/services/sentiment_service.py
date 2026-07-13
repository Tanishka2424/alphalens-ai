"""
FinBERT-based financial sentiment analysis service.

Design notes (useful for interview defense):
- The model is loaded lazily on first use and cached as a module-level
  singleton, so repeated requests don't pay the model-load cost again.
- This module has no FastAPI imports. It's a plain Python service class,
  independent of the web framework, so it's unit-testable on its own and
  reusable if the API layer ever changes.
"""
import threading
import time
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.sentiment import SentimentLabel, SentimentResponse

logger = get_logger(__name__)

# FinBERT's label order from the ProsusAI/finbert model config.
# This mapping is model-specific and MUST match the model's actual output
# order — verified against the model's config.json id2label field.
_FINBERT_LABEL_ORDER = ["positive", "negative", "neutral"]

_LABEL_TO_SENTIMENT = {
    "positive": SentimentLabel.BULLISH,
    "negative": SentimentLabel.BEARISH,
    "neutral": SentimentLabel.NEUTRAL,
}


class SentimentService:
    """Loads FinBERT once and serves sentiment predictions."""

    def __init__(self) -> None:
        self._tokenizer = None
        self._model = None
        self._lock = threading.Lock()
        self._device = torch.device(
            settings.DEVICE if torch.cuda.is_available() or settings.DEVICE == "cpu" else "cpu"
        )

    def _ensure_loaded(self) -> None:
        """Lazy-load the model on first use, not at import time. Thread-safe:
        this singleton is shared between /sentiment/analyze and the
        consensus fallback path, which can be called concurrently from the
        frontend's parallel requests - a race here caused a real crash in
        the sibling retrieval_service, fixed the same way here."""
        if self._model is not None:
            return

        with self._lock:
            if self._model is not None:
                return

            logger.info(f"Loading FinBERT model '{settings.FINBERT_MODEL_NAME}' onto {self._device}...")
            self._tokenizer = AutoTokenizer.from_pretrained(settings.FINBERT_MODEL_NAME)
            model = AutoModelForSequenceClassification.from_pretrained(settings.FINBERT_MODEL_NAME)
            model.to(self._device)
            model.eval()
            self._model = model
            logger.info("FinBERT model loaded successfully.")

    def predict(self, text: str) -> SentimentResponse:
        self._ensure_loaded()

        start = time.perf_counter()

        inputs = self._tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        ).to(self._device)

        with torch.no_grad():
            logits = self._model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze().tolist()

        elapsed_ms = (time.perf_counter() - start) * 1000

        scores = {
            _FINBERT_LABEL_ORDER[i]: round(probs[i], 4)
            for i in range(len(_FINBERT_LABEL_ORDER))
        }

        top_label_raw = max(scores, key=scores.get)
        predicted_label = _LABEL_TO_SENTIMENT[top_label_raw]
        confidence = scores[top_label_raw]

        # Re-key scores to the public Bullish/Bearish/Neutral vocabulary
        public_scores = {
            _LABEL_TO_SENTIMENT[raw].value: score for raw, score in scores.items()
        }

        return SentimentResponse(
            label=predicted_label,
            confidence=confidence,
            scores=public_scores,
            inference_time_ms=round(elapsed_ms, 2),
        )


# Module-level singleton — imported by the route handler, shared across requests.
sentiment_service = SentimentService()

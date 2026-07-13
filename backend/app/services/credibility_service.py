"""
Fake/real classifier service - loads the DistilBERT model we fine-tuned
ourselves (see training/), not a hub model. Same lazy-load-once, cache-as-
singleton pattern as sentiment_service.py.

Known limitation (document this, don't hide it): fine-tuned on general/
political news, not financial news specifically - no open labeled dataset
for financial fake-news exists at the time of writing. Test-set accuracy
is high (~99.7%) because real/fake in this dataset differ sharply in
writing style (formal wire copy vs. tabloid tone); that doesn't guarantee
the same performance on calmly-worded financial misinformation. This is
exactly why it's one signal among several in the final credibility score,
not used alone.
"""
import os
import time
import threading
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.credibility import ClassifierLabel, ClassifierResponse

logger = get_logger(__name__)

_LABEL_MAP = {0: ClassifierLabel.REAL, 1: ClassifierLabel.FAKE}


class CredibilityClassifierService:
    def __init__(self) -> None:
        self._tokenizer = None
        self._model = None
        self._lock = threading.Lock()

        self._device = torch.device("cpu")

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return

        with self._lock:
            if self._model is not None:
                return

            model_path = settings.CREDIBILITY_MODEL_PATH
            if not os.path.isdir(model_path):
                raise FileNotFoundError(
                    f"Credibility model not found at '{model_path}'. Did you download "
                    f"the fine-tuned checkpoint from Colab and place it there?"
                )

            logger.info(f"Loading credibility classifier from '{model_path}'...")
            self._tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForSequenceClassification.from_pretrained(model_path)
            model.to(self._device)
            model.eval()
            self._model = model
            logger.info("Credibility classifier loaded successfully.")

    def predict(self, text: str) -> ClassifierResponse:
        self._ensure_loaded()

        start = time.perf_counter()

        inputs = self._tokenizer(
            text, return_tensors="pt", truncation=True, max_length=256
        ).to(self._device)

        with torch.no_grad():
            logits = self._model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze().tolist()

        elapsed_ms = (time.perf_counter() - start) * 1000

        scores = {_LABEL_MAP[i].value: round(probs[i], 4) for i in range(len(probs))}
        top_idx = max(range(len(probs)), key=lambda i: probs[i])

        return ClassifierResponse(
            label=_LABEL_MAP[top_idx],
            confidence=round(probs[top_idx], 4),
            scores=scores,
            inference_time_ms=round(elapsed_ms, 2),
        )


credibility_classifier_service = CredibilityClassifierService()
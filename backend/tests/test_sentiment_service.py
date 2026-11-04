import os
from types import SimpleNamespace

import pytest
import torch

from app.core.config import settings
from app.services.sentiment_service import _FINBERT_LABEL_ORDER, SentimentService


class FakeEncoding(dict):
    def to(self, device):
        return self


class FakeTokenizer:
    def __init__(self):
        self.calls = []

    def __call__(self, text, **kwargs):
        self.calls.append((text, kwargs))
        return FakeEncoding(input_ids=torch.tensor([[1, 2, 3]]))


class FakeModel:
    def __init__(self, logits):
        self._logits = torch.tensor([logits])

    def __call__(self, **kwargs):
        return SimpleNamespace(logits=self._logits)


def make_service(logits):
    s = SentimentService()
    s._tokenizer = FakeTokenizer()
    s._model = FakeModel(logits)
    return s


@pytest.mark.parametrize("logits,expected", [
    ([5.0, 0.0, 0.0], "Bullish"),
    ([0.0, 5.0, 0.0], "Bearish"),
    ([0.0, 0.0, 5.0], "Neutral"),
])
def test_label_mapping_follows_finbert_output_order(logits, expected):
    r = make_service(logits).predict("Some financial headline text")
    assert r.label.value == expected


def test_scores_use_public_labels_only():
    r = make_service([2.0, 1.0, 0.5]).predict("Some financial headline text")
    assert set(r.scores) == {"Bullish", "Bearish", "Neutral"}


def test_scores_sum_to_about_one_and_stay_in_range():
    r = make_service([2.0, 1.0, 0.5]).predict("Some financial headline text")
    assert sum(r.scores.values()) == pytest.approx(1.0, abs=1e-3)
    assert all(0.0 <= v <= 1.0 for v in r.scores.values())


def test_confidence_equals_the_score_of_the_predicted_label():
    r = make_service([0.2, 3.0, 0.1]).predict("Some financial headline text")
    assert r.label.value == "Bearish"
    assert r.confidence == r.scores["Bearish"]
    assert 0.0 <= r.confidence <= 1.0


def test_equal_logits_do_not_crash_and_give_a_valid_label():
    r = make_service([0.0, 0.0, 0.0]).predict("Some financial headline text")
    assert r.label.value in {"Bullish", "Bearish", "Neutral"}
    assert r.confidence == pytest.approx(0.3333, abs=1e-3)


def test_text_is_truncated_to_the_model_limit():
    s = make_service([1.0, 0.0, 0.0])
    s.predict("Some financial headline text")
    text, kwargs = s._tokenizer.calls[0]
    assert text == "Some financial headline text"
    assert kwargs["truncation"] is True
    assert kwargs["max_length"] == 512


def test_inference_time_is_reported():
    r = make_service([1.0, 0.0, 0.0]).predict("Some financial headline text")
    assert r.inference_time_ms >= 0


# ---- Real-model checks: skipped by default (they load FinBERT) ----
needs_model = pytest.mark.skipif(
    os.environ.get("RUN_MODEL_TESTS") != "1",
    reason="loads the real FinBERT model; set RUN_MODEL_TESTS=1 to run",
)


@needs_model
def test_hardcoded_label_order_matches_the_model_config():
    from transformers import AutoConfig

    id2label = AutoConfig.from_pretrained(settings.FINBERT_MODEL_NAME).id2label
    assert [id2label[i].lower() for i in range(3)] == _FINBERT_LABEL_ORDER


@needs_model
def test_real_model_clearly_positive_sentence():
    from app.services.sentiment_service import sentiment_service

    r = sentiment_service.predict("The company reported record profits and raised its dividend.")
    assert r.label.value == "Bullish"


@needs_model
def test_real_model_clearly_negative_sentence():
    from app.services.sentiment_service import sentiment_service

    r = sentiment_service.predict("The company reported a huge loss and announced mass layoffs.")
    assert r.label.value == "Bearish"
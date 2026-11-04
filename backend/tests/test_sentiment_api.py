import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import sentiment as sentiment_endpoint
from app.main import app
from app.schemas.sentiment import SentimentLabel, SentimentResponse

client = TestClient(app)
URL = "/api/v1/sentiment/analyze"
GOOD = {"text": "Fed signals possible rate cuts as inflation cools further."}


def fake_result():
    return SentimentResponse(
        label=SentimentLabel.BULLISH,
        confidence=0.9,
        scores={"Bullish": 0.9, "Bearish": 0.05, "Neutral": 0.05},
        inference_time_ms=1.0,
    )


@pytest.fixture(autouse=True)
def fake_model(monkeypatch):
    """No test in this file may load the real model."""
    monkeypatch.setattr(sentiment_endpoint.sentiment_service, "predict", lambda text: fake_result())


def test_success_returns_expected_shape():
    r = client.post(URL, json=GOOD)
    assert r.status_code == 200
    body = r.json()
    assert body["label"] == "Bullish"
    assert set(body["scores"]) == {"Bullish", "Bearish", "Neutral"}
    assert 0.0 <= body["confidence"] <= 1.0


@pytest.mark.parametrize("payload", [
    {},
    {"text": ""},
    {"text": "short"},
    {"text": " " * 20},
    {"text": "x" * 5001},
    {"text": 12345},
    {"text": None},
])
def test_invalid_or_blank_input_returns_422(payload):
    assert client.post(URL, json=payload).status_code == 422


def test_surrounding_whitespace_is_stripped_before_the_model(monkeypatch):
    seen = {}

    def capture(text):
        seen["text"] = text
        return fake_result()

    monkeypatch.setattr(sentiment_endpoint.sentiment_service, "predict", capture)
    client.post(URL, json={"text": "   " + GOOD["text"] + "   "})
    assert seen["text"] == GOOD["text"]


def test_model_failure_returns_500_without_leaking_details(monkeypatch):
    def boom(text):
        raise RuntimeError("secret model path C:\\models\\finbert")

    monkeypatch.setattr(sentiment_endpoint.sentiment_service, "predict", boom)
    r = client.post(URL, json=GOOD)
    assert r.status_code == 500
    assert "secret" not in r.text
import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import explain as explain_endpoint
from app.main import app
from app.schemas.explain import ExplainResponse
from app.services.explanation_service import ExplanationUnavailableError

client = TestClient(app)
URL = "/api/v1/explain/analyze"
GOOD = {"text": "Sensex jumps 500 points after the Fed holds rates", "top_k": 5}


def test_success_returns_200_with_expected_shape(monkeypatch):
    monkeypatch.setattr(
        explain_endpoint, "explain_claim",
        lambda text, k: ExplainResponse(status="insufficient_evidence", uncertainty="None found."),
    )
    r = client.post(URL, json=GOOD)
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "insufficient_evidence"
    assert body["statements"] == [] and body["evidence"] == []
    assert "not decide whether a claim is true or false" in body["disclaimer"]


@pytest.mark.parametrize("payload", [
    {},
    {"text": "short"},
    {"text": "x" * 5001},
    {"text": GOOD["text"], "top_k": 0},
    {"text": GOOD["text"], "top_k": 11},
])
def test_invalid_requests_return_422(payload):
    assert client.post(URL, json=payload).status_code == 422


def test_llm_unavailable_returns_503_without_leaking_details(monkeypatch):
    def boom(text, k):
        raise ExplanationUnavailableError("LLM call failed: secret-key-abc123")
    monkeypatch.setattr(explain_endpoint, "explain_claim", boom)
    r = client.post(URL, json=GOOD)
    assert r.status_code == 503
    assert "secret" not in r.text
    assert "unavailable" in r.json()["detail"].lower()


def test_missing_vector_store_returns_503(monkeypatch):
    def boom(text, k):
        raise FileNotFoundError("Vector store not found")
    monkeypatch.setattr(explain_endpoint, "explain_claim", boom)
    assert client.post(URL, json=GOOD).status_code == 503


def test_unexpected_error_returns_500_without_leaking_details(monkeypatch):
    def boom(text, k):
        raise RuntimeError("internal boom detail")
    monkeypatch.setattr(explain_endpoint, "explain_claim", boom)
    r = client.post(URL, json=GOOD)
    assert r.status_code == 500
    assert "boom" not in r.text
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
ALLOWED = "http://localhost:5173"
OTHER = "https://evil.example.com"


def test_allowed_origin_gets_cors_header():
    r = client.get("/health", headers={"Origin": ALLOWED})
    assert r.headers.get("access-control-allow-origin") == ALLOWED


def test_other_origin_gets_no_cors_header():
    r = client.get("/health", headers={"Origin": OTHER})
    assert "access-control-allow-origin" not in r.headers


def test_wildcard_is_not_used():
    r = client.get("/health", headers={"Origin": ALLOWED})
    assert r.headers.get("access-control-allow-origin") != "*"


def test_preflight_from_allowed_origin_succeeds():
    r = client.options(
        "/api/v1/explain/analyze",
        headers={
            "Origin": ALLOWED,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") == ALLOWED


def test_preflight_from_other_origin_is_rejected():
    r = client.options(
        "/api/v1/explain/analyze",
        headers={"Origin": OTHER, "Access-Control-Request-Method": "POST"},
    )
    assert r.status_code == 400


def test_ready_reports_checks_without_leaking_secrets():
    r = client.get("/ready")
    assert r.status_code in (200, 503)
    body = r.json()
    assert set(body["checks"]) == {"vector_store_present", "llm_configured"}
    assert all(isinstance(v, bool) for v in body["checks"].values())
    assert "key" not in r.text.lower()


def test_ready_is_503_when_vector_store_is_missing(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "VECTOR_STORE_PATH", "does/not/exist")
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json()["status"] == "not_ready"
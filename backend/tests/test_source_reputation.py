import pytest

from app.services.source_reputation_service import lookup_source_reputation


@pytest.mark.parametrize("url", [
    "https://www.reuters.com/markets/article-1",
    "reuters.com/markets/article-1",
    "HTTPS://WWW.REUTERS.COM/x",
])
def test_known_domain_in_url_is_a_known_outlet(url):
    r = lookup_source_reputation(None, url)
    assert r.tier == "Known outlet"
    assert r.matched_via == "url"
    assert r.resolved_domain == "reuters.com"


@pytest.mark.parametrize("name", ["Reuters", "  REUTERS  ", "The Wall Street Journal"])
def test_known_name_is_a_known_outlet(name):
    r = lookup_source_reputation(name, None)
    assert r.tier == "Known outlet"
    assert r.matched_via == "source_name"


def test_unknown_source_is_not_in_our_list_and_not_called_unreliable():
    r = lookup_source_reputation("Some Blog", "https://myblog.example.org/post")
    assert r.tier == "Not in our list"
    assert r.matched_via is None
    assert r.resolved_domain == "myblog.example.org"


def test_no_input_is_not_in_our_list():
    r = lookup_source_reputation(None, None)
    assert r.tier == "Not in our list"
    assert r.resolved_domain is None


def test_unknown_url_but_known_name_matches_by_name():
    r = lookup_source_reputation("Reuters", "https://unknown-site.org/x")
    assert r.tier == "Known outlet"
    assert r.matched_via == "source_name"


def test_response_has_no_risk_score():
    assert "risk_score" not in lookup_source_reputation("Reuters", None).model_dump()
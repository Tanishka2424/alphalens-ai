"""
Source reputation lookup - a curated ALLOWLIST, deliberately not a
blocklist. We only claim "on our verified list" vs "not verified" -
we never label a named outlet as "unreliable", which would be a much
stronger and harder-to-defend claim for a heuristic project like this.

Covers well-established wire services and financial/business outlets.
Not exhaustive - that's expected and fine for a heuristic signal.
"""
from urllib.parse import urlparse

from app.schemas.source_reputation import SourceReputationResponse

# Keys are lowercase: either a bare domain (no "www.") or a common outlet name.
REPUTATION_ALLOWLIST = {
    # domains
    "reuters.com": "Reputable",
    "apnews.com": "Reputable",
    "bloomberg.com": "Reputable",
    "wsj.com": "Reputable",
    "ft.com": "Reputable",
    "cnbc.com": "Reputable",
    "marketwatch.com": "Reputable",
    "economist.com": "Reputable",
    "npr.org": "Reputable",
    "bbc.com": "Reputable",
    "nytimes.com": "Reputable",
    # common name aliases
    "reuters": "Reputable",
    "associated press": "Reputable",
    "ap": "Reputable",
    "bloomberg": "Reputable",
    "wall street journal": "Reputable",
    "the wall street journal": "Reputable",
    "financial times": "Reputable",
    "cnbc": "Reputable",
    "marketwatch": "Reputable",
    "the economist": "Reputable",
    "npr": "Reputable",
    "bbc": "Reputable",
    "new york times": "Reputable",
    "the new york times": "Reputable",
}


def _extract_domain(url: str) -> str:
    if "://" not in url:
        url = "http://" + url
    domain = urlparse(url).netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def lookup_source_reputation(source_name: str | None, url: str | None) -> SourceReputationResponse:
    resolved_domain = None
    tier = "Unverified"
    matched_via = None

    if url:
        resolved_domain = _extract_domain(url)
        if resolved_domain in REPUTATION_ALLOWLIST:
            tier = "Reputable"
            matched_via = "url"

    if tier == "Unverified" and source_name:
        name_key = source_name.strip().lower()
        if name_key in REPUTATION_ALLOWLIST:
            tier = "Reputable"
            matched_via = "source_name"

    risk_score = 0.0 if tier == "Reputable" else 0.4

    return SourceReputationResponse(
        tier=tier,
        resolved_domain=resolved_domain,
        matched_via=matched_via,
        risk_score=risk_score,
    )
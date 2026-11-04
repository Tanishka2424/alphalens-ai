"""
Runs the standalone writing-style and source-context signals together.

There is NO combined score and NO verdict. These signals do not measure
factual accuracy, so they are returned separately with their reasons.
(DistilBERT was removed from this path: it was trained on general/political
fake news and is not validated for financial news.)
"""
from app.schemas.credibility_analyze import CredibilityAnalyzeResponse
from app.services.clickbait_service import detect_clickbait
from app.services.emotional_language_service import score_emotional_language
from app.services.source_reputation_service import lookup_source_reputation


def analyze_credibility(
    text: str, source_name: str | None, url: str | None
) -> CredibilityAnalyzeResponse:
    return CredibilityAnalyzeResponse(
        clickbait=detect_clickbait(text),
        emotional_language=score_emotional_language(text),
        source_context=lookup_source_reputation(source_name, url),
    )
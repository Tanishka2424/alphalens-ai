"""
Combines all four credibility signals into one risk score + action bucket.

Weights and thresholds below are a DESIGNED heuristic, not statistically
fit to data - say so plainly in any writeup, don't imply more rigor than
this has. Rationale for the weights:
- classifier (0.35): the strongest individual signal (99.7% test accuracy)
  but capped below 0.5 because of its documented domain-shift limitation
  on financial-style neutral text (see credibility_service.py docstring).
- clickbait (0.25) and emotional_language (0.25): explainable, domain-
  general heuristics that catch some of what the classifier misses.
- source_reputation (0.15): weakest signal on its own - an unverified
  source isn't proof of anything, just an absence of verification.
"""
from app.schemas.credibility_analyze import CredibilityAnalyzeResponse
from app.schemas.credibility import ClassifierLabel
from app.services.clickbait_service import detect_clickbait
from app.services.credibility_service import credibility_classifier_service
from app.services.emotional_language_service import score_emotional_language
from app.services.source_reputation_service import lookup_source_reputation

CLASSIFIER_WEIGHT = 0.35
CLICKBAIT_WEIGHT = 0.25
EMOTIONAL_WEIGHT = 0.25
SOURCE_WEIGHT = 0.15

RELIABLE_THRESHOLD = 0.35
NEEDS_VERIFICATION_THRESHOLD = 0.65


def analyze_credibility(
    text: str, source_name: str | None, url: str | None
) -> CredibilityAnalyzeResponse:
    classifier_result = credibility_classifier_service.predict(text)
    clickbait_result = detect_clickbait(text)
    emotional_result = score_emotional_language(text)
    source_result = lookup_source_reputation(source_name, url)

    classifier_risk = classifier_result.scores[ClassifierLabel.FAKE.value]

    risk_score = (
        classifier_risk * CLASSIFIER_WEIGHT
        + clickbait_result.score * CLICKBAIT_WEIGHT
        + emotional_result.score * EMOTIONAL_WEIGHT
        + source_result.risk_score * SOURCE_WEIGHT
    )
    risk_score = round(min(risk_score, 1.0), 4)

    if risk_score < RELIABLE_THRESHOLD:
        action_bucket = "Reliable"
    elif risk_score < NEEDS_VERIFICATION_THRESHOLD:
        action_bucket = "Needs Verification"
    else:
        action_bucket = "High Risk"

    return CredibilityAnalyzeResponse(
        risk_score=risk_score,
        action_bucket=action_bucket,
        classifier=classifier_result,
        clickbait=clickbait_result,
        emotional_language=emotional_result,
        source_reputation=source_result,
    )
from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.schemas.clickbait import ClickbaitRequest, ClickbaitResponse
from app.schemas.credibility_analyze import CredibilityAnalyzeRequest, CredibilityAnalyzeResponse
from app.schemas.emotional_language import EmotionalLanguageRequest, EmotionalLanguageResponse
from app.schemas.source_reputation import SourceReputationRequest, SourceReputationResponse
from app.services.clickbait_service import detect_clickbait
from app.services.credibility_aggregator_service import analyze_credibility
from app.services.emotional_language_service import score_emotional_language
from app.services.source_reputation_service import lookup_source_reputation

logger = get_logger(__name__)

router = APIRouter(prefix="/credibility", tags=["Credibility"])


@router.post(
    "/clickbait-check",
    response_model=ClickbaitResponse,
    summary="Rule-based clickbait phrase/formatting detector - a writing-style signal only",
)
def clickbait_check(payload: ClickbaitRequest) -> ClickbaitResponse:
    try:
        result = detect_clickbait(payload.text)
        logger.info(f"Clickbait check: score={result.score} phrases={result.matched_phrases}")
        return result
    except Exception:
        logger.exception("Clickbait detection failed")
        raise HTTPException(status_code=500, detail="Clickbait detection failed.")


@router.post(
    "/emotional-language-check",
    response_model=EmotionalLanguageResponse,
    summary="Rule-based emotional/loaded language detector - a writing-style signal only",
)
def emotional_language_check(payload: EmotionalLanguageRequest) -> EmotionalLanguageResponse:
    try:
        result = score_emotional_language(payload.text)
        logger.info(f"Emotional language check: score={result.score} words={result.matched_words}")
        return result
    except Exception:
        logger.exception("Emotional language detection failed")
        raise HTTPException(status_code=500, detail="Emotional language detection failed.")


@router.post(
    "/source-reputation-check",
    response_model=SourceReputationResponse,
    summary="Curated outlet list lookup: 'Known outlet' or 'Not in our list'. Not a reliability judgment.",
)
def source_reputation_check(payload: SourceReputationRequest) -> SourceReputationResponse:
    try:
        result = lookup_source_reputation(payload.source_name, payload.url)
        logger.info(f"Source check: tier={result.tier} matched_via={result.matched_via}")
        return result
    except Exception:
        logger.exception("Source lookup failed")
        raise HTTPException(status_code=500, detail="Source lookup failed.")


@router.post(
    "/analyze",
    response_model=CredibilityAnalyzeResponse,
    summary="Writing-style and source-context signals (no combined score, not a truth check)",
)
def analyze(payload: CredibilityAnalyzeRequest) -> CredibilityAnalyzeResponse:
    try:
        return analyze_credibility(payload.text, payload.source_name, payload.url)
    except Exception:
        logger.exception("Credibility analysis failed")
        raise HTTPException(status_code=500, detail="Credibility analysis failed.")
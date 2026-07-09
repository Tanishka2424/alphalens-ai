from fastapi import APIRouter, HTTPException
from app.schemas.credibility_analyze import CredibilityAnalyzeRequest, CredibilityAnalyzeResponse
from app.services.credibility_aggregator_service import analyze_credibility
from app.core.logging import get_logger
from app.schemas.clickbait import ClickbaitRequest, ClickbaitResponse
from app.schemas.credibility import ClassifierRequest, ClassifierResponse
from app.schemas.emotional_language import EmotionalLanguageRequest, EmotionalLanguageResponse
from app.services.clickbait_service import detect_clickbait
from app.services.credibility_service import credibility_classifier_service
from app.services.emotional_language_service import score_emotional_language
from app.schemas.source_reputation import SourceReputationRequest, SourceReputationResponse
from app.services.source_reputation_service import lookup_source_reputation
logger = get_logger(__name__)

router = APIRouter(prefix="/credibility", tags=["Credibility"])


@router.post(
    "/classify",
    response_model=ClassifierResponse,
    summary="Raw fine-tuned classifier signal (Real/Fake) - not the final credibility score",
)
def classify(payload: ClassifierRequest) -> ClassifierResponse:
    try:
        result = credibility_classifier_service.predict(payload.text)
        logger.info(
            f"Credibility classifier: label={result.label.value} "
            f"confidence={result.confidence} time_ms={result.inference_time_ms}"
        )
        return result
    except FileNotFoundError as e:
        logger.error(str(e))
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        logger.exception("Credibility classification failed")
        raise HTTPException(
            status_code=500,
            detail="Credibility classification failed. Please try again or check server logs.",
        )


@router.post(
    "/clickbait-check",
    response_model=ClickbaitResponse,
    summary="Rule-based clickbait phrase/formatting detector - one of several heuristic signals",
)
def clickbait_check(payload: ClickbaitRequest) -> ClickbaitResponse:
    try:
        result = detect_clickbait(payload.text)
        logger.info(
            f"Clickbait check: score={result.score} phrases={result.matched_phrases}"
        )
        return result
    except Exception:
        logger.exception("Clickbait detection failed")
        raise HTTPException(status_code=500, detail="Clickbait detection failed.")


@router.post(
    "/emotional-language-check",
    response_model=EmotionalLanguageResponse,
    summary="Rule-based emotional/loaded language detector - one of several heuristic signals",
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
    summary="Curated allowlist lookup - 'Reputable' (verified) vs 'Unverified', never a blocklist claim",
)
def source_reputation_check(payload: SourceReputationRequest) -> SourceReputationResponse:
    try:
        result = lookup_source_reputation(payload.source_name, payload.url)
        logger.info(f"Source reputation check: tier={result.tier} matched_via={result.matched_via}")
        return result
    except Exception:
        logger.exception("Source reputation lookup failed")
        raise HTTPException(status_code=500, detail="Source reputation lookup failed.") 

@router.post(
    "/analyze",
    response_model=CredibilityAnalyzeResponse,
    summary="Combined credibility score: classifier + clickbait + emotional language + source reputation",
)
def analyze(payload: CredibilityAnalyzeRequest) -> CredibilityAnalyzeResponse:
    try:
        result = analyze_credibility(payload.text, payload.source_name, payload.url)
        logger.info(f"Credibility analyze: risk_score={result.risk_score} bucket={result.action_bucket}")
        return result
    except FileNotFoundError as e:
        logger.error(str(e))
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        logger.exception("Credibility analysis failed")
        raise HTTPException(status_code=500, detail="Credibility analysis failed.")       
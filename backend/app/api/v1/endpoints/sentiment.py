from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.schemas.sentiment import SentimentRequest, SentimentResponse
from app.services.sentiment_service import sentiment_service

logger = get_logger(__name__)

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])


@router.post(
    "/analyze",
    response_model=SentimentResponse,
    summary="Analyze financial sentiment of a news headline or article",
)
def analyze_sentiment(payload: SentimentRequest) -> SentimentResponse:
    """
    Runs FinBERT over the submitted text and returns a Bullish / Bearish /
    Neutral classification with a confidence score and full class
    probability distribution.
    """
    try:
        result = sentiment_service.predict(payload.text)
        logger.info(
            f"Sentiment prediction: label={result.label.value} "
            f"confidence={result.confidence} time_ms={result.inference_time_ms}"
        )
        return result
    except Exception:
        logger.exception("Sentiment analysis failed")
        raise HTTPException(
            status_code=500,
            detail="Sentiment analysis failed. Please try again or check server logs.",
        )

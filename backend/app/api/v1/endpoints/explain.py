from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.schemas.explain import ExplainRequest, ExplainResponse
from app.services.explanation_service import ExplanationUnavailableError, explain_claim

logger = get_logger(__name__)

router = APIRouter(prefix="/explain", tags=["Explain"])


@router.post(
    "/analyze",
    response_model=ExplainResponse,
    summary="Explanation grounded in retrieved articles, with validated citations (not a truth check)",
)
def analyze(payload: ExplainRequest) -> ExplainResponse:
    try:
        result = explain_claim(payload.text, payload.top_k)
        logger.info(
            f"Explain: status={result.status} statements={len(result.statements)} "
            f"dropped={result.dropped_statements}"
        )
        return result
    except ExplanationUnavailableError as e:
        logger.warning(str(e))
        raise HTTPException(
            status_code=503,
            detail="The explanation service is unavailable. Related articles can still be shown.",
        )
    except FileNotFoundError as e:
        logger.error(str(e))
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        logger.exception("Explanation failed")
        raise HTTPException(status_code=500, detail="Explanation failed.")
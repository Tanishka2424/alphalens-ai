from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.schemas.consensus import ConsensusRequest, ConsensusResponse
from app.services.consensus_fallback_service import analyze_consensus_fallback
from app.services.llm_consensus_service import LLMUnavailableError, analyze_consensus_llm

logger = get_logger(__name__)

router = APIRouter(prefix="/consensus", tags=["Consensus"])


@router.post(
    "/fallback-check",
    response_model=ConsensusResponse,
    summary="Rule-based consensus reasoning (no LLM) - the required, always-available fallback path",
)
def fallback_check(payload: ConsensusRequest) -> ConsensusResponse:
    try:
        result = analyze_consensus_fallback(payload.text, payload.top_k)
        logger.info(f"Consensus fallback: verdict={result.verdict} exaggeration={result.exaggeration_flag}")
        return result
    except FileNotFoundError as e:
        logger.error(str(e))
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        logger.exception("Consensus fallback analysis failed")
        raise HTTPException(status_code=500, detail="Consensus fallback analysis failed.")

@router.post(
    "/analyze",
    response_model=ConsensusResponse,
    summary="Consensus reasoning: tries GPT-4o-mini first, automatically falls back to rule-based if unavailable",
)
def analyze(payload: ConsensusRequest) -> ConsensusResponse:
    try:
        result = analyze_consensus_llm(payload.text, payload.top_k)
        logger.info(f"Consensus analyze (LLM path): verdict={result.verdict}")
        return result
    except LLMUnavailableError as e:
        logger.warning(f"LLM consensus path unavailable, using fallback: {e}")
        try:
            result = analyze_consensus_fallback(payload.text, payload.top_k)
            logger.info(f"Consensus analyze (fallback path): verdict={result.verdict}")
            return result
        except FileNotFoundError as fe:
            logger.error(str(fe))
            raise HTTPException(status_code=503, detail=str(fe))
        except Exception:
            logger.exception("Consensus fallback analysis also failed")
            raise HTTPException(status_code=500, detail="Consensus analysis failed.")    
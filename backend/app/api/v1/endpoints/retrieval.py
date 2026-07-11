from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.schemas.retrieval import SimilarArticlesRequest, SimilarArticlesResponse
from app.services.retrieval_service import retrieval_service

logger = get_logger(__name__)

router = APIRouter(prefix="/retrieval", tags=["Retrieval"])


@router.post(
    "/similar-articles",
    response_model=SimilarArticlesResponse,
    summary="Find semantically similar financial articles from the indexed corpus",
)
def similar_articles(payload: SimilarArticlesRequest) -> SimilarArticlesResponse:
    try:
        result = retrieval_service.find_similar(payload.text, payload.top_k)
        logger.info(f"Retrieval: found {len(result.results)} similar articles")
        return result
    except FileNotFoundError as e:
        logger.error(str(e))
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        logger.exception("Similarity retrieval failed")
        raise HTTPException(status_code=500, detail="Similarity retrieval failed.")
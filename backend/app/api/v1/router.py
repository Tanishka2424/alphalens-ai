from fastapi import APIRouter

from app.api.v1.endpoints import consensus, credibility, retrieval, sentiment

api_router = APIRouter()
api_router.include_router(sentiment.router)
api_router.include_router(credibility.router)
api_router.include_router(retrieval.router)
api_router.include_router(consensus.router)
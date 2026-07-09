"""
Aggregates all v1 endpoint routers into a single router mounted in main.py.

Adding a new feature (credibility scoring, similarity retrieval, consensus
reasoning in later phases) means: add its endpoint module, import it here,
include it. main.py never needs to change again.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import credibility, sentiment

api_router = APIRouter()
api_router.include_router(sentiment.router)
api_router.include_router(credibility.router)

# Phase 3+: api_router.include_router(retrieval.router)
# Phase 4+: api_router.include_router(consensus.router)
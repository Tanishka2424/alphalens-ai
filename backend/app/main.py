import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting up (env={settings.ENV})")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Financial news intelligence: sentiment, writing-style signals, related coverage, "
        "and explanations grounded in retrieved articles. This is a heuristic assistance "
        "tool, not a factual truth-verification system."
    ),
    lifespan=lifespan,
)

# Only the listed browser origins may call the API (set CORS_ORIGINS in backend/.env).
allowed_origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last-resort handler: log the full error, return a generic message (no internals)."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred."})


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Liveness: the process is up. Says nothing about whether it can do useful work."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.get("/ready", tags=["Health"])
def readiness_check() -> JSONResponse:
    """Readiness: can the app do its job? Cheap checks only; no models are loaded here."""
    checks = {
        "vector_store_present": os.path.isdir(settings.VECTOR_STORE_PATH),
        "llm_configured": bool(
            settings.OPENAI_API_KEY and settings.OPENAI_MODEL_NAME and settings.OPENAI_BASE_URL
        ),
    }
    # Retrieval and sentiment need the vector store. Explanations need the LLM, but the
    # app still works without it (the explain endpoint returns 503), so it is not required.
    ready = checks["vector_store_present"]
    return JSONResponse(
        status_code=200 if ready else 503,
        content={"status": "ready" if ready else "not_ready", "checks": checks},
    )


app.include_router(api_router, prefix="/api/v1")
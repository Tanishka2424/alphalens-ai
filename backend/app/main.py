from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered financial news intelligence platform. Provides sentiment "
        "analysis, credibility indicators, and source consensus signals to "
        "help users evaluate financial news faster. This is a heuristic "
        "assistance tool, not a factual truth-verification system."
    ),
)

# CORS: open for now (dev + single-frontend deployment). Tighten to a
# specific origin list before considering this production-hardened.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Centralized catch-all so an unexpected error never returns a raw 500
    stack trace to the client, and always gets logged with context."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )


@app.get("/health", tags=["Health"])
def health_check() -> dict:
    """Basic liveness check — does not verify model is loaded, just that
    the service is up. Useful for Render's health check and for a quick
    demo sanity check."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup() -> None:
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} starting up (env={settings.ENV})")

"""
Structured logging setup.

Uses Python's standard logging module with a consistent format across the
app: timestamp, level, logger name (module), and message. This is enough to
be genuinely useful in a demo/interview without pulling in a heavier stack
(e.g. structlog, ELK) that would be overkill for this project's scope.
"""
import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    """Call once at app startup, before anything else logs."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    # Avoid duplicate handlers if configure_logging() is ever called twice
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet down noisy third-party loggers so real signal isn't buried
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

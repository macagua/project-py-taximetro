"""Logging configuration for the taximeter."""

import logging
from pathlib import Path

LOG_PATH = Path("logs") / "taximeter.log"

_configured = False


def setup(path: Path = LOG_PATH) -> logging.Logger:
    """Configure root logger to file + console and return the app logger.

    Idempotent: calling it twice keeps the existing handlers.
    """
    global _configured
    logger = logging.getLogger("taximeter")

    if _configured:
        return logger

    path.parent.mkdir(parents=True, exist_ok=True)

    fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setFormatter(fmt)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    _configured = True
    return logger


def get() -> logging.Logger:
    """Return the app logger (must call setup() first)."""
    return logging.getLogger("taximeter")

"""Structured logging configuration."""

import logging
import sys
from typing import Any

from app.core.config import get_settings


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger with consistent format."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    level = logging.DEBUG if get_settings().debug else logging.INFO
    logger.setLevel(level)
    return logger

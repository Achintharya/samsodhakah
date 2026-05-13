"""
Structured logging configuration.
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from backend.config.settings import settings


def setup_logging(name: str = "samsodhakah") -> logging.Logger:
    """Configure structured logging for the application."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Ensure log directory exists
    settings.log_dir.mkdir(parents=True, exist_ok=True)

    # File handler
    file_handler = logging.FileHandler(
        settings.log_dir / f"{name}.log",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


# Global logger
logger = setup_logging()
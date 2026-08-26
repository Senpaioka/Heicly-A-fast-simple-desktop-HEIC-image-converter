"""Logging configuration for Heicly application."""

import logging
import sys
from typing import Optional

_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """Retrieve application logger instance."""
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger("heicly")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _logger = logger
    return _logger

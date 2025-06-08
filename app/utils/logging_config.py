"""Logging helpers with rotation."""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(log_file: str = "logs/api.log", level: int = logging.INFO) -> None:
    """Configure root logger with rotation for info and error messages."""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    info_handler = RotatingFileHandler(log_file, maxBytes=1_048_576, backupCount=3)
    error_handler = RotatingFileHandler(
        log_file.replace("api", "error"), maxBytes=1_048_576, backupCount=3
    )
    info_handler.setLevel(level)
    error_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    logging.basicConfig(level=level, handlers=[info_handler, error_handler])

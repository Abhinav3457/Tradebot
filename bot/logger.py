"""
Logging configuration for the trading bot.

Uses ``RotatingFileHandler`` to write timestamped, level-coded log
entries to ``logs/app.log``. Logs are rotated at 5 MB with up to 3
backup files retained.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR: Path = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE: Path = LOG_DIR / "app.log"
LOG_FORMAT: str = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
MAX_BYTES: int = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT: int = 3

# Valid log-level names exposed for CLI consumption
LOG_LEVELS: tuple[str, ...] = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def setup_logger(name: str = "trading_bot") -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=str(LOG_FILE),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)

    file_fmt = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    file_handler.setFormatter(file_fmt)

    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(stream=sys.stderr)
    console_handler.setLevel(logging.WARNING)

    console_fmt = logging.Formatter(
        "%(levelname)s: %(message)s",
        datefmt=LOG_DATE_FORMAT,
    )
    console_handler.setFormatter(console_fmt)

    logger.addHandler(console_handler)

    return logger

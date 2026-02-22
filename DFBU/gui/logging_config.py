"""
DFBU Logging Configuration

Description:
    Centralized logging configuration for DFBU GUI application.
    Provides structured logging with rotation, multiple handlers,
    and appropriate log levels.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-03-2025
Date Changed: 11-03-2025
License: MIT

Features:
    - Rotating file handler for persistent logs
    - Console handler for development
    - Structured log format with timestamps
    - Configurable log levels
    - Log rotation to prevent disk space issues

Requirements:
    - Python 3.14+ for latest language features
    - Standard library logging module

Functions:
    - setup_logging: Configure application logging
    - get_logger: Get logger instance for module
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Final


LOG_DIR: Final[Path] = Path.home() / ".config" / "dfbu_gui" / "logs"
LOG_FILE: Final[Path] = LOG_DIR / "dfbu_gui.log"
MAX_LOG_SIZE: Final[int] = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT: Final[int] = 5  # Keep 5 rotated files

LOG_FORMAT: Final[str] = (
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)
DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    level: int = logging.INFO,
    console_output: bool = True,
    file_output: bool = True,
) -> None:
    """
    Configure application-wide logging.

    Sets up rotating file handler and optional console handler with
    structured formatting.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to output logs to console
        file_output: Whether to output logs to file

    Example:
        # In main application
        setup_logging(level=logging.INFO, console_output=True, file_output=True)
    """
    if file_output:
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # CONSTRAINT: Clear handlers first — prevents duplicate output if called multiple times
    root_logger.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    if file_output:
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                LOG_FILE,
                maxBytes=MAX_LOG_SIZE,
                backupCount=BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            # CONSTRAINT: Fail open — log file unavailable is non-fatal; continue console-only
            print(f"Warning: Could not create log file: {e}")

    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance for a module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance configured with application settings

    Example:
        # In any module
        logger = get_logger(__name__)
        logger.info("Operation started")
        logger.error("Operation failed", exc_info=True)
    """
    return logging.getLogger(name)


def setup_default_logging() -> None:
    """
    Set up logging with default configuration.

    INFO level with both console and file output enabled.
    """
    setup_logging(level=logging.INFO, console_output=True, file_output=True)

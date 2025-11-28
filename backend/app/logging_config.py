"""Logging configuration for Chat Magic"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = "INFO"):
    """
    Configure logging with file and console handlers

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    simple_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels, handlers will filter

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    # === File Handlers ===

    # 1. Debug log - captures everything (DEBUG and above)
    debug_handler = RotatingFileHandler(
        log_dir / "debug.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(debug_handler)

    # 2. Application log - INFO and above
    app_handler = RotatingFileHandler(
        log_dir / "application.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(app_handler)

    # 3. Error log - WARNING and above
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)

    # === Console Handler ===
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # Set specific log levels for noisy third-party libraries
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)
    logging.getLogger("presidio-analyzer").setLevel(logging.INFO)
    logging.getLogger("apscheduler").setLevel(logging.INFO)
    logging.getLogger("atlassian").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    # Log the initialization
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {log_level}")
    logger.info(f"Log files location: {log_dir.absolute()}")
    logger.debug("Debug logging enabled - detailed logs will be written to debug.log")

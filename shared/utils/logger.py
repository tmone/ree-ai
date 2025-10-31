"""Logging utilities with emoji indicators."""
import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup logger with emoji-based formatting.

    Args:
        name: Logger name (usually service name)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string (optional)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Create formatter
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


# Emoji helpers for consistent logging
class LogEmoji:
    """Emoji constants for structured logging."""
    STARTUP = "🚀"
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    AI = "🤖"
    SEARCH = "🔍"
    DATABASE = "💾"
    CACHE = "⚡"
    NETWORK = "🌐"
    USER = "👤"
    TIME = "⏱️"
    MONEY = "💰"
    PROPERTY = "🏠"
    CHART = "📊"
    DOCUMENT = "📄"
    ROCKET = "🚀"
    GEAR = "⚙️"
    FIRE = "🔥"
    TARGET = "🎯"
    LOCK = "🔐"

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
    RETRY = "🔄"
    CIRCUIT_BREAKER = "⚡"


class StructuredLogger:
    """
    Wrapper for structured logging with consistent format across services

    This provides a standardized way to log common operations with:
    - Request IDs for distributed tracing
    - Service names for multi-service debugging
    - Consistent emoji indicators
    - Timing information for performance monitoring

    Usage:
        ```python
        from shared.utils.logger import StructuredLogger, setup_logger

        raw_logger = setup_logger("my_service")
        logger = StructuredLogger(raw_logger, "MY_SERVICE")

        # Log incoming request
        logger.log_request(request_id, "SEARCH", {"query": "căn hộ quận 1"})

        # Log external service call
        logger.log_external_call(request_id, "DB_GATEWAY", "/search", duration_ms=123.4)

        # Log error with context
        try:
            ...
        except Exception as e:
            logger.log_error(request_id, e, {"query": query, "user_id": user_id})
        ```
    """

    def __init__(self, logger: logging.Logger, service_name: str):
        """
        Initialize structured logger

        Args:
            logger: Base logger instance (from setup_logger)
            service_name: Short service name for log prefixes (e.g., "RAG", "ORCH")
        """
        self.logger = logger
        self.service_name = service_name

    def log_request(
        self,
        request_id: str,
        method: str,
        details: dict
    ):
        """
        Log incoming request

        Args:
            request_id: Unique request ID for tracing
            method: API method/endpoint being called
            details: Request details (query, user_id, filters, etc.)
        """
        self.logger.info(
            f"{LogEmoji.TARGET} [{self.service_name}] [{request_id}] {method} | {details}"
        )

    def log_external_call(
        self,
        request_id: str,
        target_service: str,
        endpoint: str,
        duration_ms: Optional[float] = None,
        status_code: Optional[int] = None
    ):
        """
        Log external service call

        Args:
            request_id: Request ID for tracing
            target_service: Name of service being called (e.g., "DB_GATEWAY")
            endpoint: API endpoint (e.g., "/search")
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code if available
        """
        duration_str = f" ({duration_ms:.0f}ms)" if duration_ms else ""
        status_str = f" [{status_code}]" if status_code else ""
        self.logger.info(
            f"{LogEmoji.NETWORK} [{self.service_name}] [{request_id}] → {target_service}{endpoint}{duration_str}{status_str}"
        )

    def log_success(
        self,
        request_id: str,
        message: str,
        details: Optional[dict] = None
    ):
        """
        Log successful operation

        Args:
            request_id: Request ID for tracing
            message: Success message
            details: Additional context
        """
        details_str = f" | {details}" if details else ""
        self.logger.info(
            f"{LogEmoji.SUCCESS} [{self.service_name}] [{request_id}] {message}{details_str}"
        )

    def log_error(
        self,
        request_id: str,
        error: Exception,
        context: Optional[dict] = None
    ):
        """
        Log error with context

        Args:
            request_id: Request ID for tracing
            error: Exception that occurred
            context: Additional context for debugging
        """
        context_str = f" | {context}" if context else ""
        self.logger.error(
            f"{LogEmoji.ERROR} [{self.service_name}] [{request_id}] "
            f"{error.__class__.__name__}: {error}{context_str}"
        )

    def log_warning(
        self,
        request_id: str,
        message: str,
        details: Optional[dict] = None
    ):
        """
        Log warning

        Args:
            request_id: Request ID for tracing
            message: Warning message
            details: Additional context
        """
        details_str = f" | {details}" if details else ""
        self.logger.warning(
            f"{LogEmoji.WARNING} [{self.service_name}] [{request_id}] {message}{details_str}"
        )

    def log_retry(
        self,
        request_id: str,
        attempt: int,
        max_attempts: int,
        error: Exception,
        wait_seconds: float
    ):
        """
        Log retry attempt

        Args:
            request_id: Request ID for tracing
            attempt: Current attempt number
            max_attempts: Maximum attempts allowed
            error: Error that triggered retry
            wait_seconds: Seconds to wait before next attempt
        """
        self.logger.warning(
            f"{LogEmoji.RETRY} [{self.service_name}] [{request_id}] "
            f"Retry {attempt}/{max_attempts} after {error.__class__.__name__}: {error}. "
            f"Waiting {wait_seconds:.1f}s..."
        )

    def log_performance(
        self,
        request_id: str,
        operation: str,
        duration_ms: float,
        threshold_ms: Optional[float] = None
    ):
        """
        Log performance metric

        Args:
            request_id: Request ID for tracing
            operation: Operation name
            duration_ms: Duration in milliseconds
            threshold_ms: Performance threshold (log warning if exceeded)
        """
        if threshold_ms and duration_ms > threshold_ms:
            self.logger.warning(
                f"{LogEmoji.TIME} [{self.service_name}] [{request_id}] "
                f"{operation} took {duration_ms:.0f}ms (threshold: {threshold_ms:.0f}ms)"
            )
        else:
            self.logger.info(
                f"{LogEmoji.TIME} [{self.service_name}] [{request_id}] "
                f"{operation} completed in {duration_ms:.0f}ms"
            )

    def log_cache_hit(self, request_id: str, key: str):
        """Log cache hit"""
        self.logger.info(
            f"{LogEmoji.CACHE} [{self.service_name}] [{request_id}] Cache HIT: {key}"
        )

    def log_cache_miss(self, request_id: str, key: str):
        """Log cache miss"""
        self.logger.info(
            f"{LogEmoji.CACHE} [{self.service_name}] [{request_id}] Cache MISS: {key}"
        )

    def log_circuit_breaker_open(self, request_id: str, service: str):
        """Log circuit breaker opening"""
        self.logger.error(
            f"{LogEmoji.CIRCUIT_BREAKER} [{self.service_name}] [{request_id}] "
            f"Circuit breaker OPEN for {service} (too many failures)"
        )

    def log_circuit_breaker_closed(self, request_id: str, service: str):
        """Log circuit breaker closing (recovery)"""
        self.logger.info(
            f"{LogEmoji.SUCCESS} [{self.service_name}] [{request_id}] "
            f"Circuit breaker CLOSED for {service} (service recovered)"
        )

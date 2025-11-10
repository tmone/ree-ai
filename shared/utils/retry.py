"""
Reusable retry logic for inter-service communication

This module provides decorators for retrying HTTP calls with exponential backoff,
improving resilience against transient network errors and temporary service failures.

Usage:
    from shared.utils.retry import retry_on_http_error, retry_on_service_error

    # Automatic retry on network errors and 5xx responses
    @retry_on_http_error
    async def call_external_service():
        response = await http_client.post(url, json=data)
        response.raise_for_status()
        return response.json()

    # Custom retry configuration
    @retry_with_config(max_attempts=5, min_wait=1, max_wait=30)
    async def critical_service_call():
        ...
"""
import httpx
import logging
from typing import Callable, Type, Tuple
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryCallState
)
from shared.config import settings
from shared.exceptions import ServiceUnavailableError, ServiceTimeoutError

logger = logging.getLogger(__name__)


def retry_on_http_error(func: Callable) -> Callable:
    """
    Decorator for retrying HTTP calls with exponential backoff

    Retries on:
    - Network errors (httpx.RequestError)
    - 5xx server errors (httpx.HTTPStatusError with status >= 500)

    Does NOT retry on:
    - 4xx client errors (bad request, not found, unauthorized, etc.)
    - Successful responses (2xx, 3xx)

    Configuration:
    - Max attempts: settings.RETRY_MAX_ATTEMPTS (default: 3)
    - Backoff multiplier: settings.RETRY_BACKOFF_MULTIPLIER (default: 2.0)
    - Min wait: 2 seconds
    - Max wait: 10 seconds

    Example:
        ```python
        @retry_on_http_error
        async def call_rag_service(query: str):
            response = await http_client.post("/query", json={"query": query})
            response.raise_for_status()
            return response.json()
        ```
    """

    def is_retryable_http_error(exception: Exception) -> bool:
        """Check if HTTP error is retryable (5xx only, not 4xx)"""
        if isinstance(exception, httpx.HTTPStatusError):
            # Retry on 5xx server errors, not 4xx client errors
            return exception.response.status_code >= 500
        # Always retry network errors (connection refused, timeout, etc.)
        return isinstance(exception, httpx.RequestError)

    return retry(
        stop=stop_after_attempt(settings.RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(
            multiplier=settings.RETRY_BACKOFF_MULTIPLIER,
            min=2,
            max=10
        ),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )(func)


def retry_on_service_error(func: Callable) -> Callable:
    """
    Decorator for retrying on custom service exceptions

    Retries on:
    - ServiceUnavailableError
    - ServiceTimeoutError

    Does NOT retry on:
    - Domain errors (PropertyNotFoundError, InvalidQueryError, etc.)
    - Authentication/authorization errors

    This is useful for wrapping service calls that raise custom exceptions
    instead of raw httpx exceptions.

    Example:
        ```python
        @retry_on_service_error
        async def get_user_properties(user_id: str):
            try:
                response = await http_client.get(f"/users/{user_id}/properties")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise ServiceUnavailableError("db_gateway", {"original_error": str(e)})
        ```
    """
    return retry(
        stop=stop_after_attempt(settings.RETRY_MAX_ATTEMPTS),
        wait=wait_exponential(
            multiplier=settings.RETRY_BACKOFF_MULTIPLIER,
            min=2,
            max=10
        ),
        retry=retry_if_exception_type((ServiceUnavailableError, ServiceTimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )(func)


def retry_with_config(
    max_attempts: int = 3,
    min_wait: float = 2,
    max_wait: float = 10,
    retry_on: Tuple[Type[Exception], ...] = (httpx.RequestError, httpx.HTTPStatusError)
) -> Callable:
    """
    Decorator factory for custom retry configuration

    Use this when you need fine-grained control over retry behavior.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait: Minimum wait time in seconds before retry
        max_wait: Maximum wait time in seconds before retry
        retry_on: Tuple of exception types to retry on

    Example:
        ```python
        # Retry up to 5 times with longer waits for critical operations
        @retry_with_config(max_attempts=5, min_wait=5, max_wait=60)
        async def critical_database_operation():
            ...

        # Fast retry for quick operations
        @retry_with_config(max_attempts=2, min_wait=0.5, max_wait=2)
        async def quick_cache_lookup():
            ...
        ```
    """

    def decorator(func: Callable) -> Callable:
        return retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(
                multiplier=2.0,
                min=min_wait,
                max=max_wait
            ),
            retry=retry_if_exception_type(retry_on),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True
        )(func)

    return decorator


def retry_with_circuit_breaker(
    max_attempts: int = 3,
    circuit_breaker=None
) -> Callable:
    """
    Decorator combining retry logic with circuit breaker pattern

    Use this for critical services where you want both retry resilience
    and circuit breaker protection.

    Args:
        max_attempts: Maximum retry attempts
        circuit_breaker: PyBreaker CircuitBreaker instance

    Example:
        ```python
        from pybreaker import CircuitBreaker

        db_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

        @retry_with_circuit_breaker(max_attempts=3, circuit_breaker=db_breaker)
        async def query_database(query: str):
            ...
        ```
    """

    def decorator(func: Callable) -> Callable:
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=2.0, min=2, max=10),
            retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True
        )
        async def wrapper(*args, **kwargs):
            if circuit_breaker:
                # Call through circuit breaker
                return await circuit_breaker.call_async(func, *args, **kwargs)
            else:
                # No circuit breaker, call directly
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# ==================== LOGGING HELPERS ====================

def log_retry_attempt(retry_state: RetryCallState):
    """
    Custom callback for logging retry attempts with detailed context

    Usage:
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(min=2, max=10),
            before_sleep=log_retry_attempt
        )
        async def my_func():
            ...
    """
    attempt_number = retry_state.attempt_number
    exception = retry_state.outcome.exception()
    wait_time = retry_state.next_action.sleep if retry_state.next_action else 0

    logger.warning(
        f"🔄 Retry attempt {attempt_number} after error: {exception.__class__.__name__}: {exception}. "
        f"Waiting {wait_time:.1f}s before next attempt..."
    )

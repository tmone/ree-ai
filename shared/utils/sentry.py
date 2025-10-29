"""
Sentry error tracking and performance monitoring integration
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from functools import wraps
from typing import Callable, Optional, Dict, Any
import logging
from shared.config import settings

logger = logging.getLogger(__name__)


def init_sentry(service_name: str) -> None:
    """
    Initialize Sentry for error tracking and performance monitoring

    Args:
        service_name: Name of the service (e.g., "core-gateway", "api-gateway")
    """
    if not settings.SENTRY_DSN:
        logger.warning("⚠️  Sentry DSN not configured - skipping Sentry initialization")
        return

    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,

            # Integrations
            integrations=[
                FastApiIntegration(
                    transaction_style="endpoint",  # Group by endpoint
                    failed_request_status_codes=[403, range(500, 599)],
                ),
                LoggingIntegration(
                    level=logging.INFO,  # Breadcrumbs from INFO level
                    event_level=logging.ERROR  # Send errors to Sentry
                ),
            ],

            # Service identification
            server_name=service_name,

            # Performance monitoring
            enable_tracing=True,
            profiles_sample_rate=1.0,

            # Privacy & data filtering
            send_default_pii=False,  # Don't send PII by default

            # Request body
            max_request_body_size="medium",  # small/medium/large/always

            # Breadcrumbs
            max_breadcrumbs=50,

            # Release tracking (can be set via env var)
            release=None,  # Set via SENTRY_RELEASE env var if needed

            # Sample rate for error events
            sample_rate=1.0,

            # Before send hook for data filtering
            before_send=_before_send,

            # Before breadcrumb hook
            before_breadcrumb=_before_breadcrumb,
        )

        # Set global tags
        sentry_sdk.set_tag("service", service_name)
        sentry_sdk.set_tag("environment", settings.SENTRY_ENVIRONMENT)

        logger.info(f"✅ Sentry initialized for {service_name} in {settings.SENTRY_ENVIRONMENT} environment")

    except Exception as e:
        logger.error(f"❌ Failed to initialize Sentry: {str(e)}")


def _before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter and modify events before sending to Sentry
    Removes sensitive data like passwords, tokens, etc.
    """
    # Filter sensitive data from request data
    if "request" in event:
        request = event["request"]

        # Filter headers
        if "headers" in request:
            headers = request["headers"]
            sensitive_headers = [
                "authorization", "cookie", "x-api-key", "x-auth-token",
                "api-key", "api_key", "auth-token", "auth_token"
            ]
            for header in sensitive_headers:
                if header in headers:
                    headers[header] = "[Filtered]"
                if header.upper() in headers:
                    headers[header.upper()] = "[Filtered]"

        # Filter request body
        if "data" in request and isinstance(request["data"], dict):
            data = request["data"]
            sensitive_fields = [
                "password", "token", "secret", "api_key", "apikey",
                "access_token", "refresh_token", "auth_token",
                "authorization", "credentials", "private_key"
            ]
            for field in sensitive_fields:
                if field in data:
                    data[field] = "[Filtered]"

        # Filter query string
        if "query_string" in request:
            query = request["query_string"]
            if "token" in query.lower() or "key" in query.lower():
                request["query_string"] = "[Filtered]"

    # Filter user data
    if "user" in event:
        user = event["user"]
        # Keep id and username, but filter other sensitive data
        if "email" in user:
            # Partially mask email
            email = user["email"]
            parts = email.split("@")
            if len(parts) == 2:
                user["email"] = f"{parts[0][:2]}***@{parts[1]}"

    return event


def _before_breadcrumb(crumb: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter breadcrumbs before they are added
    """
    # Filter HTTP breadcrumbs with sensitive data
    if crumb.get("category") == "httplib":
        if "data" in crumb:
            data = crumb["data"]
            # Filter sensitive headers
            if "Authorization" in data:
                data["Authorization"] = "[Filtered]"
            if "Cookie" in data:
                data["Cookie"] = "[Filtered]"

    return crumb


def capture_exception(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, str]] = None,
    level: str = "error"
) -> Optional[str]:
    """
    Manually capture an exception with additional context

    Args:
        error: The exception to capture
        context: Additional context data
        tags: Additional tags for filtering
        level: Severity level (error, warning, info)

    Returns:
        Event ID if captured, None otherwise
    """
    if not settings.SENTRY_DSN:
        return None

    try:
        with sentry_sdk.push_scope() as scope:
            # Set level
            scope.level = level

            # Add context
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)

            # Add tags
            if tags:
                for key, value in tags.items():
                    scope.set_tag(key, value)

            # Capture exception
            event_id = sentry_sdk.capture_exception(error)
            logger.info(f"🔍 Exception captured in Sentry: {event_id}")
            return event_id

    except Exception as e:
        logger.error(f"❌ Failed to capture exception in Sentry: {str(e)}")
        return None


def capture_message(
    message: str,
    level: str = "info",
    tags: Optional[Dict[str, str]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Manually capture a message

    Args:
        message: The message to capture
        level: Severity level (info, warning, error)
        tags: Additional tags
        context: Additional context data

    Returns:
        Event ID if captured, None otherwise
    """
    if not settings.SENTRY_DSN:
        return None

    try:
        with sentry_sdk.push_scope() as scope:
            # Set level
            scope.level = level

            # Add tags
            if tags:
                for key, value in tags.items():
                    scope.set_tag(key, value)

            # Add context
            if context:
                for key, value in context.items():
                    scope.set_context(key, value)

            # Capture message
            event_id = sentry_sdk.capture_message(message, level)
            return event_id

    except Exception as e:
        logger.error(f"❌ Failed to capture message in Sentry: {str(e)}")
        return None


def set_user_context(
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
    **kwargs
) -> None:
    """
    Set user context for error tracking

    Args:
        user_id: User identifier
        username: Username
        email: User email
        **kwargs: Additional user data
    """
    if not settings.SENTRY_DSN:
        return

    user_data = {}
    if user_id:
        user_data["id"] = user_id
    if username:
        user_data["username"] = username
    if email:
        user_data["email"] = email

    user_data.update(kwargs)

    sentry_sdk.set_user(user_data)


def set_request_context(
    request_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    **kwargs
) -> None:
    """
    Set request context for error tracking

    Args:
        request_id: Unique request identifier
        endpoint: API endpoint
        method: HTTP method
        **kwargs: Additional request data
    """
    if not settings.SENTRY_DSN:
        return

    request_data = {}
    if request_id:
        request_data["request_id"] = request_id
    if endpoint:
        request_data["endpoint"] = endpoint
    if method:
        request_data["method"] = method

    request_data.update(kwargs)

    sentry_sdk.set_context("request", request_data)


def add_breadcrumb(
    message: str,
    category: str = "custom",
    level: str = "info",
    data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Add a breadcrumb for debugging

    Args:
        message: Breadcrumb message
        category: Breadcrumb category (e.g., "auth", "query", "http")
        level: Severity level
        data: Additional data
    """
    if not settings.SENTRY_DSN:
        return

    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )


def start_transaction(
    name: str,
    op: str = "function",
    **kwargs
) -> Any:
    """
    Start a performance monitoring transaction

    Args:
        name: Transaction name
        op: Operation type (e.g., "http.server", "db.query", "function")
        **kwargs: Additional transaction data

    Returns:
        Transaction object (context manager)
    """
    if not settings.SENTRY_DSN:
        # Return a dummy context manager
        class DummyTransaction:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def start_child(self, *args, **kwargs):
                return self
        return DummyTransaction()

    return sentry_sdk.start_transaction(name=name, op=op, **kwargs)


def trace_function(operation: str = "function"):
    """
    Decorator to trace function execution in Sentry

    Args:
        operation: Operation type for the span

    Example:
        @trace_function(operation="db.query")
        async def get_user(user_id: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not settings.SENTRY_DSN:
                return await func(*args, **kwargs)

            with sentry_sdk.start_span(op=operation, description=func.__name__):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not settings.SENTRY_DSN:
                return func(*args, **kwargs)

            with sentry_sdk.start_span(op=operation, description=func.__name__):
                return func(*args, **kwargs)

        # Return appropriate wrapper based on whether function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def capture_exception_decorator(
    tags: Optional[Dict[str, str]] = None,
    context: Optional[Dict[str, Any]] = None,
    re_raise: bool = True
):
    """
    Decorator to automatically capture exceptions from functions

    Args:
        tags: Additional tags to add
        context: Additional context to add
        re_raise: Whether to re-raise the exception after capturing

    Example:
        @capture_exception_decorator(tags={"service": "auth"})
        async def authenticate_user(token: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                capture_exception(e, context=context, tags=tags)
                if re_raise:
                    raise
                return None

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                capture_exception(e, context=context, tags=tags)
                if re_raise:
                    raise
                return None

        # Return appropriate wrapper based on whether function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Convenience aliases
sentry_trace = trace_function
sentry_capture = capture_exception_decorator

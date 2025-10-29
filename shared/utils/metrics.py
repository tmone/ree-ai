"""
Prometheus metrics utilities for services
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from functools import wraps
from typing import Callable

# ============================================================
# METRICS DEFINITIONS
# ============================================================

# Request counters
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Request duration histogram
request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Active requests gauge
active_requests = Gauge(
    'http_requests_active',
    'Number of active HTTP requests',
    ['method', 'endpoint']
)

# LLM-specific metrics
llm_request_count = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['model', 'status']
)

llm_token_usage = Counter(
    'llm_tokens_total',
    'Total tokens used',
    ['model', 'type']  # type: prompt or completion
)

llm_request_duration = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['model']
)

# Database metrics
db_query_count = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation', 'status']
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

# Service health
service_health = Gauge(
    'service_health',
    'Service health status (1 = healthy, 0 = unhealthy)'
)


# ============================================================
# DECORATORS
# ============================================================

def track_request_metrics(endpoint: str):
    """Decorator to track HTTP request metrics"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            method = kwargs.get('request', None)
            method_str = method.method if method else 'UNKNOWN'

            # Increment active requests
            active_requests.labels(method=method_str, endpoint=endpoint).inc()

            # Start timer
            start_time = time.time()

            try:
                # Execute function
                result = await func(*args, **kwargs)
                status = 200

                return result

            except Exception as e:
                status = 500
                raise

            finally:
                # Record metrics
                duration = time.time() - start_time
                request_count.labels(
                    method=method_str,
                    endpoint=endpoint,
                    status=status
                ).inc()
                request_duration.labels(
                    method=method_str,
                    endpoint=endpoint
                ).observe(duration)
                active_requests.labels(
                    method=method_str,
                    endpoint=endpoint
                ).dec()

        return wrapper
    return decorator


def track_llm_metrics(model: str):
    """Decorator to track LLM request metrics"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Start timer
            start_time = time.time()

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Track success
                llm_request_count.labels(model=model, status='success').inc()

                # Track token usage if available
                if hasattr(result, 'usage'):
                    llm_token_usage.labels(
                        model=model,
                        type='prompt'
                    ).inc(result.usage.prompt_tokens)
                    llm_token_usage.labels(
                        model=model,
                        type='completion'
                    ).inc(result.usage.completion_tokens)

                return result

            except Exception as e:
                # Track failure
                llm_request_count.labels(model=model, status='error').inc()
                raise

            finally:
                # Record duration
                duration = time.time() - start_time
                llm_request_duration.labels(model=model).observe(duration)

        return wrapper
    return decorator


def track_db_metrics(operation: str):
    """Decorator to track database operation metrics"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Start timer
            start_time = time.time()

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Track success
                db_query_count.labels(operation=operation, status='success').inc()

                return result

            except Exception as e:
                # Track failure
                db_query_count.labels(operation=operation, status='error').inc()
                raise

            finally:
                # Record duration
                duration = time.time() - start_time
                db_query_duration.labels(operation=operation).observe(duration)

        return wrapper
    return decorator


# ============================================================
# ENDPOINTS
# ============================================================

def metrics_endpoint():
    """FastAPI endpoint for Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def register_metrics_endpoint(app):
    """Register /metrics endpoint to FastAPI app"""
    app.add_api_route(
        "/metrics",
        metrics_endpoint,
        methods=["GET"],
        tags=["monitoring"]
    )


# ============================================================
# HELPERS
# ============================================================

def set_service_health(healthy: bool):
    """Set service health status"""
    service_health.set(1 if healthy else 0)


def record_llm_usage(model: str, prompt_tokens: int, completion_tokens: int):
    """Record LLM token usage"""
    llm_token_usage.labels(model=model, type='prompt').inc(prompt_tokens)
    llm_token_usage.labels(model=model, type='completion').inc(completion_tokens)


def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record HTTP request"""
    request_count.labels(method=method, endpoint=endpoint, status=status).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)

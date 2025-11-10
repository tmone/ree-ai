"""
Prometheus Metrics Utilities

Centralized metrics collection for monitoring and observability
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Dict, Any
import time
from functools import wraps


# ==================== REQUEST METRICS ====================

# HTTP request counter
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'method', 'endpoint', 'status_code']
)

# HTTP request duration histogram
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['service', 'method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# HTTP request errors counter
http_request_errors_total = Counter(
    'http_request_errors_total',
    'Total HTTP request errors',
    ['service', 'method', 'endpoint', 'error_type']
)

# ==================== SERVICE METRICS ====================

# Service health gauge
service_health = Gauge(
    'service_health',
    'Service health status (1=healthy, 0=unhealthy)',
    ['service']
)

# Service info
service_info = Info(
    'service_info',
    'Service information'
)

# Active connections gauge
active_connections = Gauge(
    'active_connections',
    'Number of active connections',
    ['service', 'target']
)

# ==================== RETRY METRICS ====================

# Retry attempts counter
retry_attempts_total = Counter(
    'retry_attempts_total',
    'Total retry attempts',
    ['service', 'target', 'success']
)

# Retry duration histogram
retry_duration_seconds = Histogram(
    'retry_duration_seconds',
    'Retry duration in seconds',
    ['service', 'target'],
    buckets=[1.0, 2.0, 5.0, 10.0, 30.0]
)

# ==================== CIRCUIT BREAKER METRICS ====================

# Circuit breaker state gauge
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['service', 'target']
)

# Circuit breaker failures counter
circuit_breaker_failures_total = Counter(
    'circuit_breaker_failures_total',
    'Total circuit breaker failures',
    ['service', 'target']
)

# ==================== CACHE METRICS ====================

# Cache hits counter
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['service', 'cache_type']
)

# Cache misses counter
cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['service', 'cache_type']
)

# Cache size gauge
cache_size = Gauge(
    'cache_size',
    'Current cache size',
    ['service', 'cache_type']
)

# ==================== LLM METRICS ====================

# LLM requests counter
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['service', 'model', 'success']
)

# LLM request duration histogram
llm_request_duration_seconds = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['service', 'model'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

# LLM tokens used counter
llm_tokens_used_total = Counter(
    'llm_tokens_used_total',
    'Total LLM tokens used',
    ['service', 'model', 'token_type']
)

# ==================== DATABASE METRICS ====================

# Database queries counter
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['service', 'operation', 'success']
)

# Database query duration histogram
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['service', 'operation'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)

# Connection pool gauge
db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Database connection pool size',
    ['service', 'state']
)

# ==================== RAG METRICS ====================

# RAG queries counter
rag_queries_total = Counter(
    'rag_queries_total',
    'Total RAG queries',
    ['service', 'pipeline']
)

# RAG retrieved documents histogram
rag_retrieved_documents = Histogram(
    'rag_retrieved_documents',
    'Number of documents retrieved',
    ['service', 'pipeline'],
    buckets=[0, 1, 5, 10, 20, 50]
)

# RAG quality score histogram
rag_quality_score = Histogram(
    'rag_quality_score',
    'RAG response quality score',
    ['service', 'pipeline'],
    buckets=[0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
)

# ==================== DECORATORS ====================

def track_request_metrics(service_name: str):
    """
    Decorator to track HTTP request metrics

    Usage:
        @track_request_metrics("my_service")
        async def my_endpoint():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method = kwargs.get('method', 'POST')
            endpoint = func.__name__

            try:
                result = await func(*args, **kwargs)
                status_code = 200
                http_requests_total.labels(
                    service=service_name,
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()

                return result

            except Exception as e:
                status_code = getattr(e, 'status_code', 500)
                http_requests_total.labels(
                    service=service_name,
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()

                http_request_errors_total.labels(
                    service=service_name,
                    method=method,
                    endpoint=endpoint,
                    error_type=type(e).__name__
                ).inc()

                raise

            finally:
                duration = time.time() - start_time
                http_request_duration_seconds.labels(
                    service=service_name,
                    method=method,
                    endpoint=endpoint
                ).observe(duration)

        return wrapper
    return decorator


def track_llm_metrics(service_name: str, model: str):
    """
    Decorator to track LLM request metrics

    Usage:
        @track_llm_metrics("rag_service", "gpt-4o-mini")
        async def call_llm():
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                llm_requests_total.labels(
                    service=service_name,
                    model=model,
                    success="true"
                ).inc()

                # Track tokens if available
                if isinstance(result, dict):
                    if 'prompt_tokens' in result:
                        llm_tokens_used_total.labels(
                            service=service_name,
                            model=model,
                            token_type="prompt"
                        ).inc(result['prompt_tokens'])

                    if 'completion_tokens' in result:
                        llm_tokens_used_total.labels(
                            service=service_name,
                            model=model,
                            token_type="completion"
                        ).inc(result['completion_tokens'])

                return result

            except Exception as e:
                llm_requests_total.labels(
                    service=service_name,
                    model=model,
                    success="false"
                ).inc()
                raise

            finally:
                duration = time.time() - start_time
                llm_request_duration_seconds.labels(
                    service=service_name,
                    model=model
                ).observe(duration)

        return wrapper
    return decorator


# ==================== HELPER FUNCTIONS ====================

def set_service_health(service_name: str, is_healthy: bool):
    """Set service health status"""
    service_health.labels(service=service_name).set(1 if is_healthy else 0)


def track_cache_operation(service_name: str, cache_type: str, hit: bool):
    """Track cache hit/miss"""
    if hit:
        cache_hits_total.labels(service=service_name, cache_type=cache_type).inc()
    else:
        cache_misses_total.labels(service=service_name, cache_type=cache_type).inc()


def track_retry(service_name: str, target: str, success: bool, duration: float):
    """Track retry attempt"""
    retry_attempts_total.labels(
        service=service_name,
        target=target,
        success="true" if success else "false"
    ).inc()

    retry_duration_seconds.labels(
        service=service_name,
        target=target
    ).observe(duration)


def set_circuit_breaker_state(service_name: str, target: str, state: str):
    """
    Set circuit breaker state

    Args:
        state: "closed" (0), "open" (1), or "half_open" (2)
    """
    state_value = {"closed": 0, "open": 1, "half_open": 2}.get(state, 0)
    circuit_breaker_state.labels(service=service_name, target=target).set(state_value)

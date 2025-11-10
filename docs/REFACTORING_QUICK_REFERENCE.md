# Refactoring Quick Reference Card

**Quick lookup guide for using new refactored utilities**

---

## 📦 Import Cheat Sheet

```python
# HTTP Client
from shared.utils.http_client import HTTPClientFactory

# Logging
from shared.utils.logger import StructuredLogger, setup_logger, LogEmoji

# Retry Logic
from shared.utils.retry import retry_on_http_error, retry_with_config

# Exceptions
from shared.exceptions import (
    ServiceUnavailableError,
    PropertyNotFoundError,
    InvalidQueryError,
    RAGPipelineError
)

# Validators
from shared.models.base import (
    QueryRequest,
    PaginationParams,
    PropertyFilters,
    UserIdentifiable
)

# Config
from shared.config import settings
```

---

## 🌐 HTTP Client Factory

### Create Client

```python
# Default client (60s timeout, 100 connections)
client = HTTPClientFactory.create_client()

# Service-specific optimized clients
rag_client = HTTPClientFactory.create_rag_client()  # 90s timeout
classification_client = HTTPClientFactory.create_classification_client()  # 30s
core_gateway_client = HTTPClientFactory.create_core_gateway_client()  # 60s

# Custom configuration
client = HTTPClientFactory.create_client(
    timeout=120.0,
    max_connections=200,
    max_keepalive=50
)
```

### Usage in Service

```python
class MyService(BaseService):
    def __init__(self):
        super().__init__(...)
        self.http_client = HTTPClientFactory.create_client()

    async def on_shutdown(self):
        await self.http_client.aclose()  # Don't forget to close!
        await super().on_shutdown()
```

---

## 📝 Structured Logging

### Setup

```python
# In __init__
raw_logger = setup_logger(self.name, level=settings.LOG_LEVEL)
self.structured_logger = StructuredLogger(raw_logger, "SVC_PREFIX")
```

### Usage

```python
# Generate request ID
request_id = str(uuid.uuid4())[:8]

# Log incoming request
self.structured_logger.log_request(
    request_id, "METHOD_NAME", {"query": "...", "user_id": "123"}
)

# Log external service call
start = time.time()
response = await http_client.post(...)
duration_ms = (time.time() - start) * 1000

self.structured_logger.log_external_call(
    request_id, "TARGET_SERVICE", "/endpoint",
    duration_ms=duration_ms, status_code=200
)

# Log success
self.structured_logger.log_success(
    request_id, "Operation complete", {"count": 5}
)

# Log error
try:
    ...
except Exception as e:
    self.structured_logger.log_error(
        request_id, e, {"query": query, "user_id": user_id}
    )

# Log retry
self.structured_logger.log_retry(
    request_id, attempt=2, max_attempts=3,
    error=e, wait_seconds=4.0
)

# Log performance (warns if exceeds threshold)
self.structured_logger.log_performance(
    request_id, "search_operation",
    duration_ms=1500, threshold_ms=1000
)

# Log cache
self.structured_logger.log_cache_hit(request_id, "user:123")
self.structured_logger.log_cache_miss(request_id, "user:456")

# Log circuit breaker
self.structured_logger.log_circuit_breaker_open(request_id, "db_gateway")
```

---

## 🔄 Retry Decorators

### Basic Retry

```python
@retry_on_http_error  # Retries on network errors + 5xx
async def call_service():
    response = await http_client.post(url, json=data)
    response.raise_for_status()  # Important!
    return response.json()
```

### Custom Retry

```python
@retry_with_config(
    max_attempts=5,
    min_wait=1,
    max_wait=30
)
async def critical_operation():
    ...
```

### Service-Specific Retry

```python
@retry_on_service_error  # Retries on ServiceUnavailableError, ServiceTimeoutError
async def call_with_custom_exceptions():
    try:
        response = await http_client.post(...)
    except httpx.RequestError as e:
        raise ServiceUnavailableError("db_gateway", {"error": str(e)})
```

---

## ❌ Custom Exceptions

### Common Exceptions

```python
# Service errors
raise ServiceUnavailableError("db_gateway", {"reason": "timeout"})
raise ServiceTimeoutError("rag_service", timeout_seconds=90.0)
raise CircuitBreakerOpenError("core_gateway")

# Data/domain errors
raise PropertyNotFoundError(property_id="abc123")
raise UserNotFoundError(user_id="user123")
raise ConversationNotFoundError(conversation_id="conv123")

# Validation errors
raise InvalidQueryError(query="ab", reason="Query too short")
raise InvalidFiltersError(filters={...}, reason="price_min > price_max")
raise MissingRequiredFieldError(field_name="user_id", context="search")

# LLM/AI errors
raise LLMGenerationError(model="gpt-4o-mini", reason="API rate limit")
raise ClassificationError(query="...", reason="Unable to detect intent")
raise RAGPipelineError(stage="retrieval", reason="OpenSearch timeout")

# Database errors
raise DatabaseError(operation="insert", reason="Duplicate key")
raise SearchError(query="...", reason="Index not found")

# Auth errors
raise AuthenticationError(reason="Invalid JWT token")
raise AuthorizationError(user_id="123", action="delete_property")

# Rate limiting
raise RateLimitExceededError(limit=100, window_seconds=60)

# Configuration
raise ConfigurationError(setting_name="OPENAI_API_KEY", reason="Not set")
```

### Exception Handling

```python
try:
    result = await some_operation()
except ServiceUnavailableError as e:
    # Structured error with context
    self.structured_logger.log_error(request_id, e, {"operation": "search"})
    # Return structured error to client
    raise HTTPException(
        status_code=e.status_code,
        detail=e.to_dict()  # {"error": "SERVICE_UNAVAILABLE", "message": "...", "details": {...}}
    )
```

---

## ✅ Pydantic Validators

### Inherit Base Models

```python
from shared.models.base import QueryRequest, PaginationParams, PropertyFilters

class MyRequest(QueryRequest, PaginationParams, PropertyFilters):
    '''
    Inherits validation:
    - query: 3-1000 chars, non-empty
    - limit: 1-100
    - offset: >= 0
    - filters: sanitized, price_min <= price_max
    '''
    custom_field: Optional[str] = None
```

### Use in Endpoints

```python
@app.post("/search")
async def search(request: MyRequest):
    # Validation happens automatically!
    # No need for manual if/else checks
    ...
```

### Available Base Models

```python
# QueryRequest - query validation (3-1000 chars)
class MyRequest(QueryRequest):
    pass

# PaginationParams - limit/offset validation
class MyRequest(PaginationParams):
    pass

# UserIdentifiable - user_id validation
class MyRequest(UserIdentifiable):
    pass

# PropertyFilters - property search filter validation
class MyRequest(PropertyFilters):
    pass

# ConversationRequest - user_id + conversation_id
class MyRequest(ConversationRequest):
    pass

# TimestampedModel - created_at/updated_at timestamps
class MyModel(TimestampedModel):
    pass

# ErrorResponse - standard error format
# HealthCheckResponse - standard /health format
```

---

## ⚙️ Configuration Settings

### New Settings (All Configurable via .env)

```bash
# HTTP Client
HTTP_TIMEOUT_DEFAULT=60
HTTP_TIMEOUT_RAG=90
HTTP_TIMEOUT_CLASSIFICATION=30
HTTP_MAX_CONNECTIONS=100
HTTP_MAX_KEEPALIVE=20

# Query/Search Limits
CONVERSATION_HISTORY_LIMIT=10
SEARCH_RESULTS_DEFAULT_LIMIT=5
TOP_SOURCES_LIMIT=3

# Retry
RETRY_MAX_ATTEMPTS=3
RETRY_BACKOFF_MULTIPLIER=2.0

# Circuit Breaker
CIRCUIT_BREAKER_FAIL_MAX=5
CIRCUIT_BREAKER_RESET_TIMEOUT=60
```

### Use in Code

```python
from shared.config import settings

# HTTP timeouts
client = HTTPClientFactory.create_client(timeout=settings.HTTP_TIMEOUT_RAG)

# Limits
history = await get_history(limit=settings.CONVERSATION_HISTORY_LIMIT)
results = await search(limit=settings.SEARCH_RESULTS_DEFAULT_LIMIT)

# Retry config (automatic via @retry_on_http_error)
# Uses settings.RETRY_MAX_ATTEMPTS, settings.RETRY_BACKOFF_MULTIPLIER
```

---

## 🎨 Log Emoji Reference

```python
from shared.utils.logger import LogEmoji

LogEmoji.STARTUP         # 🚀 Service startup
LogEmoji.SUCCESS         # ✅ Success operation
LogEmoji.ERROR           # ❌ Error occurred
LogEmoji.WARNING         # ⚠️ Warning
LogEmoji.INFO            # ℹ️ Information
LogEmoji.AI              # 🤖 AI/LLM operation
LogEmoji.SEARCH          # 🔍 Search operation
LogEmoji.DATABASE        # 💾 Database operation
LogEmoji.CACHE           # ⚡ Cache operation
LogEmoji.NETWORK         # 🌐 Network/HTTP call
LogEmoji.USER            # 👤 User-related
LogEmoji.TIME            # ⏱️ Performance/timing
LogEmoji.TARGET          # 🎯 Incoming request
LogEmoji.RETRY           # 🔄 Retry attempt
LogEmoji.CIRCUIT_BREAKER # ⚡ Circuit breaker
```

---

## 🚀 Complete Service Template

```python
import uuid
import time
from typing import Dict, Any
from fastapi import HTTPException

from core.base_service import BaseService
from shared.config import settings
from shared.utils.logger import StructuredLogger, setup_logger
from shared.utils.http_client import HTTPClientFactory
from shared.utils.retry import retry_on_http_error
from shared.exceptions import ServiceUnavailableError
from shared.models.base import QueryRequest, PaginationParams


class MyRequest(QueryRequest, PaginationParams):
    pass


class MyService(BaseService):
    def __init__(self):
        super().__init__(
            name="my_service",
            version="1.0.0",
            capabilities=["my_capability"],
            port=8080
        )

        # HTTP client
        self.http_client = HTTPClientFactory.create_client()

        # Structured logging
        raw_logger = setup_logger(self.name, level=settings.LOG_LEVEL)
        self.structured_logger = StructuredLogger(raw_logger, "MY_SVC")

    def setup_routes(self):
        @self.app.post("/process")
        async def process(request: MyRequest):
            request_id = str(uuid.uuid4())[:8]

            self.structured_logger.log_request(
                request_id, "PROCESS", {"query": request.query}
            )

            start = time.time()

            try:
                result = await self._call_external(request.query)
                duration_ms = (time.time() - start) * 1000

                self.structured_logger.log_performance(
                    request_id, "external_call", duration_ms
                )

                self.structured_logger.log_success(
                    request_id, "Complete", {"count": len(result)}
                )

                return {"results": result}

            except ServiceUnavailableError as e:
                self.structured_logger.log_error(request_id, e)
                raise HTTPException(e.status_code, e.to_dict())

    @retry_on_http_error
    async def _call_external(self, query: str):
        import httpx

        try:
            response = await self.http_client.post(
                "http://external:8080/endpoint",
                json={"query": query}
            )
            response.raise_for_status()
            return response.json()

        except httpx.RequestError as e:
            raise ServiceUnavailableError("external", {"error": str(e)})

    async def on_shutdown(self):
        await self.http_client.aclose()
        await super().on_shutdown()
```

---

## 📚 See Also

- **Full Documentation:** `docs/REFACTORING_GUIDE.md`
- **Migration Example:** `examples/service_migration_example.py`
- **Project Structure:** `PROJECT_STRUCTURE.md`
- **CLAUDE.md:** Project instructions and language policy

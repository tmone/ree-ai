"""
Example: How to Migrate an Existing Service to Use New Refactored Utilities

This file shows BEFORE and AFTER code when migrating a service to use:
- Shared HTTP Client Factory
- Structured Logging
- Retry Decorators
- Custom Exceptions
- Pydantic Validators

Use this as a template when refactoring existing services.
"""

# ==================== BEFORE REFACTORING ====================

"""
# services/old_service/main.py (BEFORE)

import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from core.base_service import BaseService
from shared.config import settings
from shared.utils.logger import LogEmoji


class OldServiceRequest(BaseModel):
    query: str
    limit: int = 10


class OldService(BaseService):
    def __init__(self):
        super().__init__(
            name="old_service",
            version="1.0.0",
            capabilities=["some_capability"],
            port=8080
        )

        # ❌ Problem: Creating HTTP client without connection pooling
        self.http_client = httpx.AsyncClient(timeout=60.0)

        # ❌ Problem: Hardcoded timeout (magic number)
        # ❌ Problem: No connection reuse

    def setup_routes(self):
        @self.app.post("/process")
        async def process(request: OldServiceRequest):
            # ❌ Problem: No request ID for tracing
            # ❌ Problem: Inconsistent logging format
            self.logger.info(f"Processing query: {request.query}")

            # ❌ Problem: Manual validation
            if not request.query or len(request.query) < 3:
                raise HTTPException(400, "Query too short")

            if request.limit < 1 or request.limit > 100:
                raise HTTPException(400, "Invalid limit")

            # ❌ Problem: No retry on network errors
            # ❌ Problem: Generic error handling
            try:
                result = await self._call_external_api(request.query)
            except Exception as e:
                self.logger.error(f"Error: {e}")
                raise HTTPException(500, "Internal server error")

            return {"results": result}

    async def _call_external_api(self, query: str):
        # ❌ Problem: No retry logic
        # ❌ Problem: Generic Exception on failure
        try:
            response = await self.http_client.post(
                "http://external-api:8080/endpoint",
                json={"query": query},
                timeout=30.0  # ❌ Hardcoded timeout
            )

            if response.status_code != 200:
                # ❌ Problem: Not distinguishing 4xx vs 5xx errors
                raise Exception(f"API returned {response.status_code}")

            return response.json()

        except httpx.RequestError as e:
            # ❌ Problem: Generic error message
            raise Exception(f"Network error: {e}")

    async def on_shutdown(self):
        await self.http_client.aclose()
        await super().on_shutdown()
"""

# ==================== AFTER REFACTORING ====================

"""
# services/new_service/main.py (AFTER - REFACTORED)

import uuid
import time
from typing import Dict, Any, Optional
from fastapi import HTTPException

from core.base_service import BaseService
from shared.config import settings
from shared.utils.logger import LogEmoji, StructuredLogger, setup_logger
from shared.utils.http_client import HTTPClientFactory
from shared.utils.retry import retry_on_http_error
from shared.exceptions import ServiceUnavailableError, InvalidQueryError
from shared.models.base import QueryRequest, PaginationParams


# ✅ IMPROVEMENT: Use Pydantic base models for automatic validation
class NewServiceRequest(QueryRequest, PaginationParams):
    '''
    Inherits validation from:
    - QueryRequest: query length (3-1000 chars), non-empty
    - PaginationParams: limit (1-100), offset (>= 0)
    '''
    pass


class NewService(BaseService):
    def __init__(self):
        super().__init__(
            name="new_service",
            version="2.0.0",  # Bumped version after refactoring
            capabilities=["some_capability"],
            port=8080
        )

        # ✅ IMPROVEMENT: Use shared HTTP client factory with connection pooling
        self.http_client = HTTPClientFactory.create_client()
        # Benefits:
        # - Connection pooling (reuses TCP connections)
        # - Consistent timeout (settings.HTTP_TIMEOUT_DEFAULT)
        # - HTTP/2 support
        # - Configurable via environment variables

        # ✅ IMPROVEMENT: Use structured logging with request IDs
        raw_logger = setup_logger(self.name, level=settings.LOG_LEVEL)
        self.structured_logger = StructuredLogger(raw_logger, "NEW_SVC")
        # Benefits:
        # - Request ID tracing across services
        # - Consistent log format
        # - Performance metrics (duration logging)

    def setup_routes(self):
        @self.app.post("/process")
        async def process(request: NewServiceRequest):
            # ✅ IMPROVEMENT: Generate request ID for distributed tracing
            request_id = str(uuid.uuid4())[:8]

            # ✅ IMPROVEMENT: Structured logging with request ID
            self.structured_logger.log_request(
                request_id,
                "PROCESS",
                {"query": request.query, "limit": request.limit}
            )

            # ✅ IMPROVEMENT: No manual validation needed (Pydantic does it)
            # request.query is already validated (3-1000 chars)
            # request.limit is already validated (1-100)

            # ✅ IMPROVEMENT: Call with retry + structured error handling
            start_time = time.time()

            try:
                result = await self._call_external_api(request.query)
                duration_ms = (time.time() - start_time) * 1000

                # ✅ IMPROVEMENT: Log performance metrics
                self.structured_logger.log_performance(
                    request_id,
                    "external_api_call",
                    duration_ms,
                    threshold_ms=1000  # Warn if > 1s
                )

                # ✅ IMPROVEMENT: Log success with details
                self.structured_logger.log_success(
                    request_id,
                    "Processing complete",
                    {"result_count": len(result)}
                )

                return {"results": result}

            except ServiceUnavailableError as e:
                # ✅ IMPROVEMENT: Structured error logging
                self.structured_logger.log_error(
                    request_id,
                    e,
                    {"query": request.query}
                )
                # ✅ IMPROVEMENT: Return structured error response
                raise HTTPException(
                    status_code=e.status_code,
                    detail=e.to_dict()
                )

    # ✅ IMPROVEMENT: Add retry decorator for automatic retries
    @retry_on_http_error
    async def _call_external_api(self, query: str):
        '''
        Calls external API with automatic retry on failures

        Retries:
        - Network errors (connection refused, timeout)
        - 5xx server errors (service temporarily unavailable)

        Does NOT retry:
        - 4xx client errors (bad request, not found, etc.)

        Configuration:
        - Max attempts: settings.RETRY_MAX_ATTEMPTS (default: 3)
        - Backoff: Exponential (2s -> 4s -> 8s, max 10s)
        '''
        import httpx  # Import for exception handling

        try:
            response = await self.http_client.post(
                "http://external-api:8080/endpoint",
                json={"query": query},
                # ✅ IMPROVEMENT: Use settings instead of hardcoded timeout
                timeout=settings.HTTP_TIMEOUT_DEFAULT
            )

            # ✅ IMPROVEMENT: raise_for_status() triggers retry on 5xx
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            # ✅ IMPROVEMENT: Distinguish 4xx vs 5xx errors
            if e.response.status_code >= 500:
                # 5xx errors will be retried by @retry_on_http_error decorator
                raise  # Re-raise for retry
            else:
                # 4xx errors should NOT be retried (client error)
                raise InvalidQueryError(query, f"API returned {e.response.status_code}")

        except httpx.RequestError as e:
            # ✅ IMPROVEMENT: Raise structured exception
            # Network errors will be retried by decorator
            raise ServiceUnavailableError(
                "external_api",
                {"original_error": str(e), "query": query}
            )

    async def on_shutdown(self):
        '''Cleanup on shutdown'''
        await self.http_client.aclose()
        await super().on_shutdown()
"""

# ==================== COMPARISON SUMMARY ====================

"""
BEFORE vs AFTER Comparison:

1. HTTP CLIENT
   ❌ Before: httpx.AsyncClient(timeout=60.0)
   ✅ After: HTTPClientFactory.create_client()
   Benefits: Connection pooling, HTTP/2, configurable via env vars

2. LOGGING
   ❌ Before: self.logger.info(f"Processing query: {query}")
   ✅ After: self.structured_logger.log_request(request_id, "PROCESS", {...})
   Benefits: Request IDs, consistent format, distributed tracing

3. VALIDATION
   ❌ Before: Manual if/else validation
   ✅ After: Pydantic base models (QueryRequest, PaginationParams)
   Benefits: Automatic validation, type safety, consistent errors

4. RETRY LOGIC
   ❌ Before: No retry (fails immediately on network error)
   ✅ After: @retry_on_http_error decorator
   Benefits: Resilient to transient failures, exponential backoff

5. ERROR HANDLING
   ❌ Before: raise Exception("Generic error")
   ✅ After: raise ServiceUnavailableError("service", {...})
   Benefits: Structured errors, easy to catch/monitor, error codes

6. CONFIGURATION
   ❌ Before: Hardcoded timeout=30.0, limit checks
   ✅ After: settings.HTTP_TIMEOUT_DEFAULT, settings.RETRY_MAX_ATTEMPTS
   Benefits: Easy to tune, env var overrides, centralized config
"""

# ==================== MIGRATION CHECKLIST ====================

"""
✅ Step-by-Step Migration Checklist:

□ 1. Update imports
     Add: StructuredLogger, HTTPClientFactory, retry_on_http_error, exceptions, base models

□ 2. Replace HTTP client
     Change: httpx.AsyncClient() → HTTPClientFactory.create_client()

□ 3. Add structured logging
     Add in __init__: self.structured_logger = StructuredLogger(...)
     Replace: self.logger.info() → self.structured_logger.log_request()

□ 4. Add request IDs
     Add at start of each endpoint: request_id = str(uuid.uuid4())[:8]
     Pass to all log calls

□ 5. Use Pydantic validators
     Change: Manual validation → Inherit from QueryRequest, PaginationParams

□ 6. Add retry decorators
     Add: @retry_on_http_error to external service calls
     Ensure: response.raise_for_status() is called

□ 7. Use custom exceptions
     Replace: HTTPException(500, ...) → ServiceUnavailableError(...)
     Replace: Exception(...) → InvalidQueryError(...), DatabaseError(...), etc.

□ 8. Use config settings
     Replace: Hardcoded numbers → settings.HTTP_TIMEOUT_DEFAULT, etc.

□ 9. Test thoroughly
     Run: pytest tests/
     Check: Logs have request IDs
     Verify: Retries happen on network errors

□ 10. Update version
     Bump: version="2.0.0" (major refactor)
     Document: Changes in service README.md
"""

# ==================== EXAMPLE LOGS ====================

"""
BEFORE (Inconsistent logging):
2025-11-11 10:30:45 - old_service - INFO - Processing query: căn hộ quận 1
2025-11-11 10:30:46 - old_service - ERROR - Error: Connection refused

AFTER (Structured logging with request IDs):
🎯 [NEW_SVC] [a1b2c3d4] PROCESS | {'query': 'căn hộ quận 1', 'limit': 10}
🌐 [NEW_SVC] [a1b2c3d4] → EXTERNAL_API/endpoint (234ms) [200]
✅ [NEW_SVC] [a1b2c3d4] Processing complete | {'result_count': 5}

With retry (on failure):
🎯 [NEW_SVC] [x9y8z7w6] PROCESS | {'query': 'test'}
🔄 [NEW_SVC] [x9y8z7w6] Retry 1/3 after RequestError: Connection refused. Waiting 2.0s...
🔄 [NEW_SVC] [x9y8z7w6] Retry 2/3 after RequestError: Connection refused. Waiting 4.0s...
🌐 [NEW_SVC] [x9y8z7w6] → EXTERNAL_API/endpoint (8234ms) [200]
✅ [NEW_SVC] [x9y8z7w6] Processing complete | {'result_count': 3}
"""

# ==================== TESTING THE REFACTORED SERVICE ====================

"""
# tests/test_new_service.py

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from services.new_service.main import NewService, NewServiceRequest


@pytest.fixture
def service():
    return NewService()


@pytest.mark.asyncio
async def test_process_with_retry_success():
    '''Test that retry works on network failures'''
    service = NewService()

    # Mock: First 2 calls fail, 3rd succeeds
    mock_post = AsyncMock(
        side_effect=[
            httpx.RequestError("Connection refused"),
            httpx.RequestError("Timeout"),
            AsyncMock(status_code=200, json=lambda: {"results": [1, 2, 3]})
        ]
    )

    with patch.object(service.http_client, 'post', mock_post):
        result = await service._call_external_api("test query")

    # Verify: 3 calls made (2 retries + 1 success)
    assert mock_post.call_count == 3
    assert result == {"results": [1, 2, 3]}


@pytest.mark.asyncio
async def test_validation_rejects_short_query():
    '''Test Pydantic validation rejects invalid queries'''
    with pytest.raises(ValueError, match="Query cannot be empty"):
        NewServiceRequest(query="ab")  # Too short (< 3 chars)


@pytest.mark.asyncio
async def test_validation_rejects_invalid_limit():
    '''Test Pydantic validation rejects invalid limits'''
    with pytest.raises(ValueError):
        NewServiceRequest(query="valid query", limit=200)  # > 100
"""

print(__doc__)
print("\n✅ This example demonstrates all refactoring best practices!")
print("📖 See docs/REFACTORING_GUIDE.md for full documentation")

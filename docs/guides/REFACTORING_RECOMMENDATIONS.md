# REE AI - Refactoring Recommendations

## 🎯 Tổng Quan

Document này chứa các đề xuất refactoring để cải thiện chất lượng code, giảm technical debt, và tăng maintainability.

## 🚨 Issues Cần Xử Lý NGAY

### 1. Xóa File Versioned và Backup

**Vấn đề:** Có nhiều file versioned vi phạm quy tắc Git
```bash
services/semantic_chunking/main_v2.py
services/orchestrator/main_v2.py
```

**Giải pháp:**
```bash
# So sánh 2 versions
diff services/semantic_chunking/main.py services/semantic_chunking/main_v2.py

# Nếu v2 tốt hơn -> merge vào main
mv services/semantic_chunking/main_v2.py services/semantic_chunking/main.py

# Nếu không cần -> xóa
rm services/semantic_chunking/main_v2.py
rm services/orchestrator/main_v2.py

# Commit
git add services/
git commit -m "refactor: consolidate versioned files into main.py"
```

### 2. Tổ Chức Lại Documentation

**Vấn đề:** Quá nhiều markdown files ở root (15+ files)

**Files cần di chuyển vào docs/:**
```bash
# Di chuyển files
mkdir -p docs/guides docs/architecture docs/setup

mv QUICKSTART.md docs/guides/quickstart.md
mv QUICKSTART_COMPLETE.md docs/guides/quickstart-complete.md
mv DEPLOYMENT.md docs/guides/deployment.md
mv TESTING.md docs/guides/testing.md
mv SENTRY_SETUP.md docs/setup/sentry.md
mv OPEN_WEBUI_SETUP.md docs/setup/open-webui.md
mv MICROSERVICES_ARCHITECTURE.md docs/architecture/microservices.md
mv README_FRAMEWORK.md docs/architecture/framework.md

# Xóa duplicates (đã có trong README.md)
rm IMPLEMENTATION_SUMMARY.md
rm TEST_SUMMARY.md
rm BACKUP_IMPLEMENTATION_COMPLETE.md
rm PROJECT_COMPLETION.md
rm COMPLETE_FRAMEWORK_SUMMARY.md
```

**Files giữ lại ở root:**
- `README.md` - Main documentation
- `CLAUDE.md` - Claude Code guidance
- `PROJECT_STRUCTURE.md` - Structure rules
- `REFACTORING_RECOMMENDATIONS.md` - This file

### 3. Xóa Backup Files

**Vấn đề:** Có folder và files backup không cần thiết
```bash
# Xóa backup files
rm -rf docs/backup/
rm scripts/BACKUP_*.md
rm scripts/.backup.env.example

# Chỉ giữ functional scripts
# Keep: backup.sh, backup.ps1 (functional scripts)
# Remove: BACKUP documentation
```

## 🔧 Code Refactoring Recommendations

### 1. Shared Models - Consistency

**File:** `shared/models/core_gateway.py`

**Issue:** Method `dict()` is deprecated in Pydantic v2
```python
# ❌ Current
request.dict()

# ✅ Should be
request.model_dump()
```

**Action:**
```bash
# Find all usages
grep -r "\.dict()" services/
grep -r "\.dict()" shared/

# Replace with model_dump()
# Update in all service files
```

### 2. BaseService - Error Handling

**File:** `core/base_service.py`

**Improvement:** Thêm retry logic cho service registration

```python
# Current: Chỉ warning nếu registration fails
# Suggested: Retry với exponential backoff

async def _register_service(self):
    """Register with retry logic"""
    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            # ... existing registration code ...
            return
        except Exception as e:
            if attempt < max_retries - 1:
                self.logger.warning(f"⚠️ Registration attempt {attempt + 1} failed, retrying...")
                await asyncio.sleep(retry_delay * (attempt + 1))
            else:
                self.logger.warning(f"⚠️ Could not register after {max_retries} attempts: {e}")
```

### 3. Orchestrator - Intent Detection

**File:** `services/orchestrator/main.py`

**Issue:** Simple keyword matching không scale được

**Suggested Refactoring:**
```python
# Current: Hardcoded keywords
def detect_intent(query: str) -> ServiceType:
    query_lower = query.lower()
    if any(kw in query_lower for kw in ["tìm", "search"]):
        return ServiceType.SEARCH
    # ...

# Suggested: Use LangChain RouterChain
from langchain.chains.router import LLMRouterChain

class IntentRouter:
    def __init__(self):
        self.router_chain = self._build_router_chain()

    def _build_router_chain(self):
        # Define routing prompts
        destinations = [
            {
                "name": "search",
                "description": "For property search queries"
            },
            {
                "name": "price",
                "description": "For price-related questions"
            },
            # ... more routes
        ]
        return LLMRouterChain.from_prompts(destinations)

    async def route(self, query: str) -> ServiceType:
        result = await self.router_chain.arun(query)
        return ServiceType(result["destination"])
```

### 4. Config Management - Type Safety

**File:** `shared/config.py`

**Improvement:** Thêm validation cho URLs và ports

```python
from pydantic import field_validator, HttpUrl
from typing import Optional

class Settings(BaseSettings):
    # Current
    POSTGRES_HOST: str = "postgres"

    # Suggested: Add validation
    @field_validator('POSTGRES_PORT')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v

    @field_validator('OPENAI_API_KEY')
    def validate_api_key(cls, v):
        if v == "sk-dummy-key":
            logger.warning("⚠️ Using dummy API key - set OPENAI_API_KEY")
        return v
```

### 5. Logger - Structured Logging

**File:** `shared/utils/logger.py`

**Current:** Simple emoji logging
**Suggested:** Add structured logging với context

```python
import structlog

def setup_logger(name: str) -> structlog.BoundLogger:
    """Setup structured logger with context"""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )

    return structlog.get_logger(name)

# Usage with context
logger.info("request_received",
           user_id=user_id,
           query=query,
           service="orchestrator")
```

## 📊 Testing Improvements

### 1. Test Coverage

**Current:** Basic integration tests
**Suggested:** Thêm coverage targets

```bash
# Add to pytest.ini
[pytest]
addopts =
    --cov=core
    --cov=shared
    --cov=services
    --cov-report=html
    --cov-report=term
    --cov-fail-under=80
```

### 2. Mock Objects

**Create:** `tests/mocks.py` để reuse mock objects

```python
# tests/mocks.py
from unittest.mock import Mock, AsyncMock

class MockCoreGateway:
    @staticmethod
    async def chat_completion(request):
        return {
            "content": "Mock response",
            "model": "gpt-4o-mini",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }

class MockDBGateway:
    @staticmethod
    async def search(query, limit=10):
        return {
            "results": [
                {"id": 1, "title": "Test Property", "price": 1000000}
            ]
        }
```

### 3. Performance Tests

**Create:** `tests/performance/` folder

```python
# tests/performance/test_load.py
import asyncio
import time

async def test_orchestrator_load():
    """Test orchestrator under load"""
    tasks = []
    for i in range(100):
        task = http_client.post("/orchestrate", json={
            "user_id": f"user_{i}",
            "query": "Test query"
        })
        tasks.append(task)

    start = time.time()
    results = await asyncio.gather(*tasks)
    duration = time.time() - start

    assert duration < 10  # Should handle 100 requests in < 10s
    assert all(r.status_code == 200 for r in results)
```

## 🏗️ Architecture Improvements

### 1. Service Communication - Circuit Breaker

**Add:** Circuit breaker pattern cho service calls

```python
# shared/utils/circuit_breaker.py
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def call_service(url: str, data: dict):
    """Call service with circuit breaker"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
        return response.json()
```

### 2. Caching Strategy

**Add:** Redis caching layer

```python
# shared/utils/cache.py improvements
from functools import wraps
import hashlib
import json

def cache_result(ttl: int = 300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{func.__name__}:{hashlib.md5(
                json.dumps([args, kwargs], sort_keys=True).encode()
            ).hexdigest()}"

            # Try cache first
            cached = await redis_client.get(key)
            if cached:
                return json.loads(cached)

            # Call function
            result = await func(*args, **kwargs)

            # Cache result
            await redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=600)
async def search_properties(query: str):
    # ... expensive operation ...
```

### 3. Rate Limiting

**File:** `services/api_gateway/main.py`

**Add:** Per-user rate limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/orchestrate")
@limiter.limit("10/minute")  # 10 requests per minute
async def orchestrate(request: Request, data: OrchestrationRequest):
    # ...
```

## 📝 Documentation Improvements

### 1. API Documentation

**Add:** OpenAPI examples cho tất cả endpoints

```python
@app.post(
    "/orchestrate",
    response_model=OrchestrationResponse,
    summary="Orchestrate user request",
    description="Routes user query to appropriate AI service",
    responses={
        200: {
            "description": "Successful response",
            "content": {
                "application/json": {
                    "example": {
                        "response": "Tìm thấy 5 bất động sản...",
                        "service_used": "search",
                        "took_ms": 234
                    }
                }
            }
        }
    }
)
async def orchestrate(request: OrchestrationRequest):
    # ...
```

### 2. Service README Templates

**Create:** `services/README.template.md`

```markdown
# Service Name

## Purpose
Brief description of what this service does

## API Endpoints
- `POST /endpoint` - Description

## Dependencies
- Service Registry (required)
- Core Gateway (optional)

## Environment Variables
- `VAR_NAME` - Description

## Running Locally
```bash
python main.py
```

## Running Tests
```bash
pytest tests/test_service_name.py
```
```

## 🔒 Security Improvements

### 1. Input Validation

**Add:** Request validation middleware

```python
# shared/middleware/validation.py
from fastapi import Request, HTTPException
import re

async def validate_input(request: Request, call_next):
    """Validate all input for SQL injection, XSS"""
    body = await request.body()
    body_str = body.decode()

    # Check for SQL injection patterns
    sql_patterns = [
        r"(\bor\b.*=.*)",
        r"(\bunion\b.*\bselect\b)",
        r"(drop\s+table)",
    ]

    for pattern in sql_patterns:
        if re.search(pattern, body_str, re.IGNORECASE):
            raise HTTPException(400, "Invalid input detected")

    return await call_next(request)
```

### 2. Secret Management

**Use:** Docker secrets hoặc Vault thay vì environment variables

```yaml
# docker-compose.yml
services:
  core-gateway:
    secrets:
      - openai_api_key
      - jwt_secret

secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

## 📋 Priority Action Items

### High Priority 🔴
1. ✅ Update .gitignore - COMPLETED
2. ✅ Create PROJECT_STRUCTURE.md - COMPLETED
3. 🔴 Xóa versioned files (`main_v2.py`)
4. 🔴 Di chuyển docs vào docs/ folder
5. 🔴 Replace `.dict()` với `.model_dump()`

### Medium Priority 🟡
6. 🟡 Thêm retry logic vào BaseService
7. 🟡 Refactor intent detection sang LangChain
8. 🟡 Thêm structured logging
9. 🟡 Thêm test coverage targets

### Low Priority 🟢
10. 🟢 Thêm circuit breaker pattern
11. 🟢 Thêm caching decorators
12. 🟢 Thêm rate limiting
13. 🟢 Thêm performance tests

## 🎯 Next Steps

1. Review và approve recommendations này
2. Tạo GitHub issues cho từng refactoring task
3. Assign priority và owner
4. Execute theo priority order
5. Update documentation sau mỗi refactoring

---

**Note:** Không làm tất cả cùng lúc! Refactor từng phần, test kỹ, rồi mới tiếp tục.

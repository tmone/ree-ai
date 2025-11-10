# Docker Runtime Errors Report

**Date:** 2025-11-11
**Test Environment:** Docker Compose
**Status:** ❌ **CRITICAL ERRORS FOUND**

---

## Executive Summary

Started REE AI services in Docker and found **3 CRITICAL RUNTIME ERRORS** preventing services from starting:

1. ❌ **Import Error in shared/models/__init__.py** - Missing model classes
2. ❌ **RAG Service Registration Failed** - 422 Unprocessable Entity
3. ❌ **Service Name Mismatch** - RAG service using wrong name

---

## Service Status

| Service | Status | Port | Error |
|---------|--------|------|-------|
| **postgres** | ✅ HEALTHY | 5432 | None |
| **redis** | ✅ HEALTHY | 6379 | None |
| **opensearch** | ✅ HEALTHY | 9200 | None |
| **open-webui** | ✅ HEALTHY | 3000 | None |
| **service-registry** | ⚠️ UNHEALTHY | 8000 | Receiving invalid registration requests |
| **core-gateway** | ✅ RUNNING | 8080 | None |
| **classification** | ✅ RUNNING | 8083 | None (using mock mode) |
| **db-gateway** | ❌ CRASHED | 8081 | ImportError: cannot import ChatRequest |
| **orchestrator** | ❌ CRASHED | 8090 | ImportError: cannot import ChatRequest |
| **rag-service** | ⚠️ RUNNING | 8091 | Registration failed (422), service name mismatch |
| **ollama** | ⚠️ NOT STARTED | 11434 | Port already in use |

---

## Error 1: Import Error - Missing Model Classes

### ❌ Error Details

**File:** `shared/models/__init__.py` (lines 24-28)

**Error Message:**
```
ImportError: cannot import name 'ChatRequest' from 'shared.models.orchestrator' (/app/shared/models/orchestrator.py)
```

**Affected Services:**
- ❌ `db-gateway` - CRASHED on startup
- ❌ `orchestrator` - CRASHED on startup

**Root Cause:**

The `__init__.py` file attempts to import classes that **DO NOT EXIST** in `orchestrator.py`:

```python
# shared/models/__init__.py (lines 24-28)
from shared.models.orchestrator import (
    ChatRequest,      # ❌ DOES NOT EXIST
    ChatResponse,     # ❌ DOES NOT EXIST
    Intent,           # ❌ DOES NOT EXIST
)
```

**Actual Classes in orchestrator.py:**
```python
class IntentType(str, Enum)               # ✅ EXISTS
class OrchestrationRequest(BaseModel)     # ✅ EXISTS
class IntentDetectionResult(BaseModel)    # ✅ EXISTS
class ServiceRoute(BaseModel)             # ✅ EXISTS
class OrchestrationResponse(BaseModel)    # ✅ EXISTS
class RoutingDecision(BaseModel)          # ✅ EXISTS
```

### 🔧 Fix Required

**Option 1: Remove Invalid Imports (RECOMMENDED)**
```python
# shared/models/__init__.py
# Remove lines 24-28 entirely
# from shared.models.orchestrator import (
#     ChatRequest,
#     ChatResponse,
#     Intent,
# )
```

**Option 2: Import Correct Classes**
```python
# shared/models/__init__.py
from shared.models.orchestrator import (
    IntentType,
    OrchestrationRequest,
    OrchestrationResponse,
    IntentDetectionResult,
    ServiceRoute,
    RoutingDecision,
)
```

**Also Update __all__ list (lines 117-120):**
```python
# Remove:
# "ChatRequest",
# "ChatResponse",
# "Intent",

# Add:
"IntentType",
"OrchestrationRequest",
"OrchestrationResponse",
"IntentDetectionResult",
"ServiceRoute",
"RoutingDecision",
```

### 💥 Impact

**Severity:** 🔴 **CRITICAL - SERVICE CRASH**

- Prevents `db-gateway` from starting
- Prevents `orchestrator` from starting
- Blocks entire orchestration pipeline
- System cannot handle any user requests

---

## Error 2: RAG Service Registration Failed

### ❌ Error Details

**Service:** `rag-service`

**Error Message:**
```
❌ Failed to register service: Client error '422 Unprocessable Entity' for url 'http://service-registry:8000/register'
```

**Service Registry Log:**
```
INFO: 172.18.0.10:52000 - "POST /register HTTP/1.1" 422 Unprocessable Entity
```

**Root Cause:**

RAG service is sending invalid registration data to Service Registry. The registry is rejecting the request because the data doesn't match the expected Pydantic model schema.

**Likely Issues:**
1. Service is using wrong service name (`enhanced_rag_service` instead of `rag_service`)
2. Missing required fields in registration payload
3. Invalid capability format
4. Port mismatch (registering as 8091 but running on 8080)

### 🔧 Fix Required

**Check RAG Service Registration Code:**

1. Verify service name:
```python
# services/rag_service/main.py
# Should be:
super().__init__(
    name="rag_service",  # NOT "enhanced_rag_service"
    version="2.0.0",
    capabilities=["retrieval", "generation", "rag"],
    port=8080  # NOT 8091
)
```

2. Check Service Registry expected schema:
```python
# core/service_registry.py or services/service_registry/main.py
class ServiceInfo(BaseModel):
    name: str
    version: str
    url: str
    capabilities: List[str]
    # Check all required fields
```

### 💥 Impact

**Severity:** 🟡 **HIGH - SERVICE ISOLATION**

- RAG service cannot be discovered by other services
- Orchestrator cannot route RAG requests
- Service runs but is not part of the system
- Manual endpoint calls may still work

---

## Error 3: Service Name Mismatch

### ⚠️ Warning Details

**Service:** `rag-service`

**Issue:** Service is using name `enhanced_rag_service` but should use `rag_service`

**Evidence:**
```
Service Registry Log:
INFO: 172.18.0.10:48404 - "POST /heartbeat/enhanced_rag_service HTTP/1.1" 404 Not Found
```

**Root Cause:**

The RAG service was refactored and merged from two files:
- `services/rag_service/main.py` (basic)
- `services/rag_service/enhanced_main.py` (advanced)

The unified file is still using the old name `enhanced_rag_service` instead of `rag_service`.

### 🔧 Fix Required

**File:** `services/rag_service/main.py`

Change service name in BaseService initialization:
```python
# BEFORE
class RAGService(BaseService):
    def __init__(self):
        super().__init__(
            name="enhanced_rag_service",  # ❌ WRONG
            ...
        )

# AFTER
class RAGService(BaseService):
    def __init__(self):
        super().__init__(
            name="rag_service",  # ✅ CORRECT
            ...
        )
```

### 💥 Impact

**Severity:** 🟡 **MEDIUM - NAMING INCONSISTENCY**

- Service cannot receive heartbeat acknowledgments
- May show as "unhealthy" in registry
- Routing based on name will fail
- Configuration mismatches

---

## Error 4: Advanced RAG Features Import Error

### ⚠️ Warning Details

**Service:** `rag-service`

**Warning Message:**
```
⚠️ Advanced features not available: cannot import name 'GenerationOperator' from 'shared.rag_operators.operators'
```

**Root Cause:**

The RAG service is trying to import advanced operators that may not exist:
```python
from shared.rag_operators.operators import GenerationOperator
```

**Impact:** Non-critical - service falls back to basic mode

### 🔧 Fix Required

**Option 1: Create Missing Operators (if needed)**
- Implement `GenerationOperator` in `shared/rag_operators/operators/__init__.py`

**Option 2: Update Import Logic**
```python
# services/rag_service/main.py
try:
    from shared.rag_operators.operators import GenerationOperator
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Advanced features not available: {e}")
    ADVANCED_FEATURES_AVAILABLE = False
```

### 💥 Impact

**Severity:** 🟢 **LOW - GRACEFUL DEGRADATION**

- Service continues to run in basic mode
- Advanced features disabled
- Functionality reduced but system operational

---

## Error 5: Port Conflict (Ollama)

### ⚠️ Warning Details

**Service:** `ollama`

**Error Message:**
```
Error response from daemon: ports are not available: exposing port TCP 0.0.0.0:11434 -> 127.0.0.1:0: listen tcp 0.0.0.0:11434: bind: Only one usage of each socket address (protocol/network address/port) is normally permitted.
```

**Root Cause:**

Port 11434 is already in use by another Ollama instance running on the host system.

**Port Usage:**
```
TCP    0.0.0.0:11434    LISTENING    5284 (svchost)
TCP    0.0.0.0:11434    LISTENING    35408 (ollama)
```

### 🔧 Fix Required

**Option 1: Use Host Ollama**
Update docker-compose.yml:
```yaml
core-gateway:
  environment:
    - OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**Option 2: Stop Host Ollama**
```bash
# Stop Ollama service on host
net stop ollama  # Windows
# or
systemctl stop ollama  # Linux
```

**Option 3: Change Docker Port**
```yaml
ollama:
  ports:
    - "11435:11434"  # Use different external port
```

### 💥 Impact

**Severity:** 🟢 **LOW - OPTIONAL SERVICE**

- Ollama service not running in Docker
- Can use host Ollama instance instead
- OpenAI models still work
- Only affects local LLM usage

---

## Testing Steps Performed

### 1. Docker Environment
```bash
✅ Docker version: 28.4.0
✅ Docker Compose version: v2.39.4-desktop.1
```

### 2. Build Process
```bash
✅ docker-compose build --no-cache
✅ All images built successfully
```

### 3. Service Startup
```bash
✅ docker-compose up -d postgres redis opensearch
✅ docker-compose up -d service-registry core-gateway db-gateway orchestrator rag-service classification
```

### 4. Health Checks
```bash
✅ Checked: docker ps
✅ Checked: docker-compose logs [service-name]
```

### 5. Error Detection
```bash
✅ Found 3 critical import errors
✅ Found 2 configuration issues
✅ Documented all errors with root causes
```

---

## Fix Priority

### 🔴 CRITICAL (Must Fix Immediately)

1. **Fix Import Error** - `shared/models/__init__.py` lines 24-28
   - Remove invalid imports or update to correct class names
   - Unblocks: db-gateway, orchestrator
   - **ETA:** 5 minutes

### 🟡 HIGH (Fix Before Deployment)

2. **Fix RAG Service Registration** - `services/rag_service/main.py`
   - Update service name to `rag_service`
   - Fix registration payload
   - **ETA:** 10 minutes

3. **Fix Service Name Mismatch** - `services/rag_service/main.py`
   - Change `enhanced_rag_service` → `rag_service`
   - **ETA:** 2 minutes

### 🟢 LOW (Optional)

4. **Fix Advanced RAG Imports** - Create missing operators or update fallback logic
   - **ETA:** 30 minutes (if creating operators)

5. **Fix Ollama Port Conflict** - Configure to use host Ollama or change port
   - **ETA:** 5 minutes

---

## Recommended Action Plan

### Step 1: Fix Critical Import Error (5 min)
```bash
# Edit shared/models/__init__.py
# Remove lines 24-28 and lines 117-120
# OR update to correct class names
```

### Step 2: Fix RAG Service Name (2 min)
```bash
# Edit services/rag_service/main.py
# Change name="enhanced_rag_service" to name="rag_service"
```

### Step 3: Rebuild and Restart (5 min)
```bash
docker-compose down
docker-compose build service-registry db-gateway orchestrator rag-service
docker-compose up -d
```

### Step 4: Verify Services (2 min)
```bash
docker ps
docker-compose logs -f orchestrator
curl http://localhost:8000/services  # Check Service Registry
curl http://localhost:8090/health    # Check Orchestrator
curl http://localhost:8091/health    # Check RAG Service
```

### Total Fix Time: ~15 minutes

---

## Success Criteria

After fixes are applied, expect:

- ✅ All services start without errors
- ✅ Service Registry shows all services as healthy
- ✅ db-gateway runs successfully
- ✅ orchestrator runs successfully
- ✅ rag-service registers successfully
- ✅ No import errors in logs
- ✅ Health endpoints return 200 OK

---

## Logs Archive

### DB Gateway Crash Log
```
File "/app/services/db_gateway/main.py", line 15, in <module>
    from shared.models.db_gateway import SearchRequest, SearchResponse, PropertyResult, SearchFilters
  File "/app/shared/models/__init__.py", line 24, in <module>
    from shared.models.orchestrator import (
ImportError: cannot import name 'ChatRequest' from 'shared.models.orchestrator'
```

### Orchestrator Crash Log
```
File "/app/services/orchestrator/main.py", line 22, in <module>
    from shared.models.orchestrator import (
  File "/app/shared/models/__init__.py", line 24, in <module>
    from shared.models.orchestrator import (
ImportError: cannot import name 'ChatRequest' from 'shared.models.orchestrator'
```

### RAG Service Registration Error
```
❌ Failed to register service: Client error '422 Unprocessable Entity' for url 'http://service-registry:8000/register'
⚠️ Failed to register with Service Registry
```

### Service Registry Rejection
```
INFO: 172.18.0.10:52000 - "POST /register HTTP/1.1" 422 Unprocessable Entity
INFO: 172.18.0.10:48404 - "POST /heartbeat/enhanced_rag_service HTTP/1.1" 404 Not Found
```

---

## Next Steps After Fixes

1. **Run Integration Tests**
   ```bash
   pytest tests/integration/ -v
   ```

2. **Test Full Orchestration Flow**
   ```bash
   curl -X POST http://localhost:8090/query \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test", "query": "Tìm căn hộ 2 phòng ngủ quận 1"}'
   ```

3. **Monitor Service Health**
   ```bash
   watch -n 5 'curl -s http://localhost:8000/services | jq'
   ```

4. **Apply Refactoring to Other Services**
   - Use the working services as templates
   - Apply shared utilities consistently

---

**Report Status:** ✅ COMPLETE
**Errors Documented:** 5 errors
**Critical Fixes Required:** 1 (import error)
**Estimated Fix Time:** 15 minutes

**Next:** Apply fixes and restart services to verify resolution.

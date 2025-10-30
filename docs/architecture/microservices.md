# 🏗️ Microservices Architecture - REE AI

**Đúng chuẩn microservices với Service Registry Pattern**

---

## 🎯 KIẾN TRÚC ĐÚNG

```
┌─────────────────────────────────────────────────────────┐
│  SERVICE REGISTRY (Port 8000) - TRUNG TÂM              │
│  • Tất cả services đăng ký ở đây                        │
│  • Orchestrator query registry để tìm services          │
│  • Health checks tự động                                │
└─────────────────────────────────────────────────────────┘
            ↑ register                ↑ query
            │                         │
    ┌───────┴────────┐       ┌───────┴────────┐
    │                │       │                │
┌───────────┐  ┌───────────┐  ┌─────────────┐
│ Service A │  │ Service B │  │ Orchestrator │
│  (8081)   │  │  (8082)   │  │   (8090)     │
└───────────┘  └───────────┘  └─────────────┘
```

---

## 📚 CORE LIBRARY

### `core/` - Thư Viện Chung

```
core/
├── __init__.py
├── base_service.py       # BaseService class - TẤT CẢ services kế thừa
└── service_registry.py   # Service Registry logic
```

**Tất cả services PHẢI import từ `core/`:**

```python
from core import BaseService

class MyService(BaseService):
    def __init__(self):
        super().__init__(
            name="my_service",
            version="1.0.0",
            capabilities=["my_capability"]
        )
```

---

## 🔧 SERVICE REGISTRY

### Service Registry Service (Port 8000)

**MUST start FIRST** - Tất cả services khác depend on this.

```yaml
# docker-compose.yml
service-registry:
  build: services/service_registry
  ports:
    - "8000:8000"
  # NO depends_on - this starts first!
```

### Endpoints

**1. Register Service**
```bash
POST /register
{
  "name": "semantic_chunking",
  "host": "semantic-chunking",
  "port": 8080,
  "version": "1.0.0",
  "capabilities": ["text_processing", "chunking"]
}
```

**2. List Services**
```bash
GET /services?capability=chunking&status=healthy

Response:
{
  "count": 2,
  "services": [
    {
      "name": "semantic_chunking",
      "url": "http://semantic-chunking:8080",
      "capabilities": ["text_processing", "chunking"],
      "status": "healthy"
    }
  ]
}
```

**3. Get Service**
```bash
GET /services/semantic_chunking

Response:
{
  "name": "semantic_chunking",
  "url": "http://semantic-chunking:8080",
  "status": "healthy",
  "last_heartbeat": "2025-10-29T10:30:00"
}
```

**4. Registry Stats**
```bash
GET /stats

Response:
{
  "total_services": 5,
  "healthy": 4,
  "unhealthy": 1,
  "services": {...}
}
```

---

## 🎓 CÁC TẠO SERVICE MỚI (ĐÚNG CÁCH)

### Bước 1: Kế thừa BaseService

```python
# services/my_service/main.py
import sys
sys.path.insert(0, '/app')

from core import BaseService
from pydantic import BaseModel

class MyService(BaseService):
    def __init__(self):
        super().__init__(
            name="my_service",           # Tên service
            version="1.0.0",             # Version
            capabilities=["my_capability"], # Capabilities
            port=8080                    # Port
        )

    def setup_routes(self):
        """Override để thêm custom routes"""

        @self.app.post("/my-endpoint")
        async def my_endpoint(data: dict):
            self.logger.info(f"Processing: {data}")
            # Your logic here
            return {"result": "success"}

if __name__ == "__main__":
    service = MyService()
    service.run()
```

###ước 2: Tạo Dockerfile

```dockerfile
# services/my_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy CORE library (QUAN TRỌNG!)
COPY core /app/core

# Copy shared models
COPY shared /app/shared

# Copy service code
COPY services/my_service /app/services/my_service

ENV PYTHONPATH=/app

WORKDIR /app/services/my_service

CMD ["python", "main.py"]
```

### Bước 3: Thêm vào docker-compose.yml

```yaml
services:
  my-service:
    build:
      context: .
      dockerfile: services/my_service/Dockerfile
    container_name: ree-ai-my-service
    environment:
      - REGISTRY_URL=http://service-registry:8000
      - DEBUG=true
    ports:
      - "8088:8080"
    depends_on:
      service-registry:
        condition: service_healthy
    networks:
      - ree-ai-network
    profiles:
      - real
      - all
```

### Bước 4: Test

```bash
# Start Service Registry first
docker-compose up service-registry

# Wait until healthy
curl http://localhost:8000/health

# Start your service
docker-compose up my-service

# Check registration
curl http://localhost:8000/services

# Should see your service listed!
```

---

## 🔍 TỰ ĐỘNG HÓA

### BaseService Tự Động Làm Gì?

✅ **On Startup:**
1. Create FastAPI app with standard routes (/, /health, /info)
2. Register với Service Registry
3. Log startup messages

✅ **During Runtime:**
1. Automatic health checks from Registry
2. Heartbeat updates
3. Error handling

✅ **On Shutdown:**
1. Deregister từ Service Registry
2. Graceful shutdown
3. Log shutdown messages

### Default Routes (TẤT CẢ services có sẵn)

```bash
GET /           # Service info
GET /health     # Health check
GET /info       # Detailed info
```

---

## 🎯 ORCHESTRATOR - DYNAMIC ROUTING

### Trước (❌ SAI - Hardcoded):

```python
# ❌ BAD: Hardcoded URLs
service_url = "http://semantic-chunking:8080"
```

### Sau (✅ ĐÚNG - Service Registry):

```python
# ✅ GOOD: Query Service Registry
async def get_service_url(capability: str) -> str:
    response = await client.get(
        f"{registry_url}/services",
        params={"capability": capability}
    )
    services = response.json()["services"]
    return services[0]["url"]  # Dynamic!
```

### Orchestrator Flow:

```
1. User query: "Tìm nhà 2 phòng ngủ"
   ↓
2. Orchestrator detects intent: SEARCH
   ↓
3. Query Registry: GET /services?capability=search
   ↓
4. Registry returns: [{"url": "http://rag-service:8080"}]
   ↓
5. Call service: POST http://rag-service:8080/rag
   ↓
6. Return response to user
```

---

## 📊 SERVICE LIFECYCLE

```
┌─────────────────────────────────────┐
│ 1. Service Starts                    │
│    - BaseService __init__           │
│    - Setup FastAPI app              │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ 2. Register with Registry            │
│    POST /register                    │
│    - name, host, port, capabilities │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ 3. Running                           │
│    - Handle requests                 │
│    - Send heartbeats (automatic)    │
│    - Registry health checks         │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ 4. Shutdown Signal (SIGTERM)        │
│    - BaseService handles it         │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ 5. Deregister from Registry          │
│    POST /deregister                  │
└─────────────────────────────────────┘
```

---

## 🧪 TESTING

### Test 1: Service Registry

```bash
# Start Registry
docker-compose up service-registry

# Check health
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# Check stats (should be empty)
curl http://localhost:8000/stats
# Expected: {"total_services": 0, ...}
```

### Test 2: Service Registration

```bash
# Start a service
docker-compose up semantic-chunking

# Wait 5 seconds for registration

# Check registry
curl http://localhost:8000/services
# Expected: Should list semantic_chunking

# Check service health from registry
curl http://localhost:8000/services/semantic_chunking
# Expected: {"status": "healthy", ...}
```

### Test 3: Dynamic Discovery

```bash
# Start Orchestrator
docker-compose up orchestrator

# Test orchestration
curl -X POST http://localhost:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id":"user_123",
    "query":"Chunk this text"
  }'

# Check Orchestrator logs
docker-compose logs orchestrator
# Should see: "Found service: semantic_chunking at http://..."
```

---

## 📝 SAMPLE SERVICE - CORRECT VERSION

```bash
services/semantic_chunking/
├── main_v2.py        # ✅ CORRECT - Uses BaseService
├── main.py           # ❌ OLD - Direct FastAPI (deprecated)
├── Dockerfile
└── requirements.txt
```

**Run the correct version:**

```bash
# Update Dockerfile CMD
CMD ["python", "main_v2.py"]  # Not main.py!

# Build & run
docker-compose build semantic-chunking
docker-compose up semantic-chunking
```

---

## 🎯 DEPENDENCIES

### Startup Order (Critical!):

```
1. Infrastructure (postgres, redis, opensearch, ollama)
   ↓
2. Service Registry (MUST be healthy)
   ↓
3. Core Services (core-gateway, db-gateway)
   ↓
4. AI Services (semantic-chunking, classification, etc.)
   ↓
5. Orchestrator (depends on Service Registry)
   ↓
6. Open WebUI (optional)
```

### docker-compose.yml Dependencies:

```yaml
services:
  service-registry:
    # NO depends_on

  core-gateway:
    depends_on:
      service-registry:
        condition: service_healthy  # Wait until healthy!

  semantic-chunking:
    depends_on:
      service-registry:
        condition: service_healthy
      core-gateway:
        condition: service_started
```

---

## ✅ CHECKLIST - SERVICE MỚI

Khi tạo service mới, check:

- [ ] Kế thừa từ `BaseService`
- [ ] Import `core` library trong Dockerfile
- [ ] Set `PYTHONPATH=/app`
- [ ] Có `capabilities` list
- [ ] Có `version` string
- [ ] Override `setup_routes()` cho custom logic
- [ ] `depends_on: service-registry` trong docker-compose
- [ ] Test registration: `curl http://localhost:8000/services`
- [ ] Test health: `curl http://localhost:PORT/health`
- [ ] Check logs: `docker-compose logs my-service`

---

## 🚀 QUICK START

```bash
# 1. Start Service Registry FIRST
docker-compose up -d service-registry

# Wait until healthy
docker-compose ps | grep service-registry

# 2. Start other services
docker-compose up -d core-gateway db-gateway

# 3. Check all registered
curl http://localhost:8000/services | jq

# 4. Start AI services
docker-compose up -d semantic-chunking classification

# 5. Check registry again
curl http://localhost:8000/stats | jq

# 6. Start Orchestrator
docker-compose up -d orchestrator

# 7. Test end-to-end
curl -X POST http://localhost:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","query":"test query"}'
```

---

## 🎓 KEY CONCEPTS

### 1. Service Registry Pattern
- **Central discovery service**
- **Dynamic service registration**
- **Health monitoring**
- **No hardcoded URLs**

### 2. Base Service Class
- **Inheritance-based**
- **Auto-registration**
- **Standard interfaces**
- **Code reuse**

### 3. Capabilities-Based Discovery
- Services advertise **what they can do**
- Orchestrator finds services by **capability**
- **Loose coupling**

### 4. Health Checks
- **Automatic** từ Service Registry
- **Periodic** (mỗi 30s)
- **Status tracking** (healthy/unhealthy)

---

## ✅ SUMMARY

**ĐÚNG:** ✅
- Service Registry pattern
- BaseService inheritance
- Auto-registration
- Dynamic discovery
- Health monitoring
- Graceful shutdown

**SAI:** ❌
- Hardcoded URLs
- Direct FastAPI (không kế thừa BaseService)
- Manual registration
- No health checks
- Tài liệu thay vì code

**Core Library là FOUNDATION, không phải documentation!**

---

**Status:** ✅ Microservices Architecture Complete
**Version:** 2.0.0
**Pattern:** Service Registry + Base Service Class

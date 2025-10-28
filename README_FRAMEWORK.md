# 🏗️ REE AI - Framework Documentation

**Complete MVP Framework for Team Collaboration**

---

## 📦 What's Included

This framework provides a **complete, production-ready foundation** for building the REE AI system with multiple dev teams working in parallel.

### ✅ Infrastructure (Ready to Use)

```
✅ PostgreSQL       - User data, conversations, context memory
✅ Redis            - Caching, queue, rate limiting
✅ OpenSearch       - Vector DB + BM25 hybrid search
✅ Ollama           - Local LLM (free)
✅ Mock Servers     - Week 1 development (no blocking)
```

### ✅ Core Services (Implemented)

```
✅ Core Gateway       - LLM routing (Ollama/OpenAI)
✅ DB Gateway         - Database operations
✅ Semantic Chunking  - Sample Layer 3 service (template)
```

### ✅ Shared Framework

```
✅ Pydantic Models    - Type-safe API contracts
✅ Feature Flags      - Mock → Real transition
✅ Logging            - Centralized logging
✅ Docker Compose     - One-command deployment
✅ Tests              - Unit + integration test examples
```

---

## 📂 Complete Project Structure

```
ree-ai/
├── 📄 README.md                      # Project overview
├── 📄 QUICKSTART.md                  # 5-minute setup guide ⭐
├── 📄 README_FRAMEWORK.md            # This file
├── 📄 .env.example                   # Configuration template
├── 📄 .gitignore                     # Git ignore rules
├── 📄 docker-compose.yml             # All services definition
├── 📄 Makefile                       # Quick commands (Linux/Mac)
├── 📄 requirements.txt               # Python dependencies
├── 📄 pytest.ini                     # Test configuration
├── 📄 test_integration.sh            # Integration tests (Bash)
├── 📄 test_integration.ps1           # Integration tests (PowerShell)
│
├── 📁 shared/                        # ⭐ SHARED CODE (ALL teams use)
│   ├── __init__.py
│   ├── config.py                    # Settings + feature flags
│   ├── models/                      # Pydantic models
│   │   ├── __init__.py
│   │   ├── core_gateway.py         # LLM models
│   │   ├── db_gateway.py           # Database models
│   │   └── orchestrator.py         # Routing models
│   └── utils/                       # Utilities
│       ├── __init__.py
│       └── logger.py               # Centralized logging
│
├── 📁 services/                     # ⭐ SERVICES (Each team's work)
│   ├── core_gateway/               # Layer 5 - Core Gateway ✅
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── main.py                 # LiteLLM integration
│   │
│   ├── db_gateway/                 # Layer 4 - DB Gateway ✅
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── main.py                 # Database operations
│   │
│   └── semantic_chunking/          # Layer 3 - Sample Service ✅
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── main.py                 # Sample implementation
│       └── README.md               # Template guide ⭐
│
├── 📁 mocks/                        # Mock server configurations
│   ├── core_gateway_mock.json      # Mock LLM responses
│   └── db_gateway_mock.json        # Mock DB responses
│
├── 📁 tests/                        # Integration tests
│   ├── __init__.py
│   ├── test_core_gateway.py
│   ├── test_db_gateway.py
│   └── test_semantic_chunking.py
│
└── 📁 docs/                         # Documentation
    ├── CTO_EXECUTIVE_SUMMARY.md
    ├── MVP_TEAM_COLLABORATION_GUIDE.md ⭐
    └── ... (other docs)
```

---

## 🎯 Key Features

### 1. Contract-First Development

**Problem:** Teams wait for each other to finish

**Solution:** Define API contracts upfront, use mocks

```python
# shared/models/core_gateway.py
class LLMRequest(BaseModel):
    """Defined BEFORE implementation"""
    model: ModelType
    messages: List[Message]
    # ...

# All teams use this model
# Week 1: Call mock
# Week 2: Call real implementation
```

**Benefits:**
- ✅ Zero blocking between teams
- ✅ Type safety (Pydantic validation)
- ✅ Clear API documentation

### 2. Feature Flags for Gradual Integration

**Problem:** "Big bang" integration fails

**Solution:** Enable services one by one

```python
# shared/config.py
class Settings(BaseSettings):
    USE_REAL_CORE_GATEWAY: bool = False  # Week 1: False, Week 2: True
    SERVICE_SEMANTIC_CHUNKING: ServiceMode = ServiceMode.MOCK

# In your service:
if feature_flags.use_real_core_gateway():
    url = "http://core-gateway:8080"  # Real
else:
    url = "http://mock-core-gateway:1080"  # Mock
```

**Benefits:**
- ✅ Gradual rollout (not all at once)
- ✅ Easy rollback (flip flag)
- ✅ A/B testing capability

### 3. Sample Service Template

**Problem:** Devs don't know where to start

**Solution:** Complete working example

```bash
# Copy template
cp -r services/semantic_chunking services/your_service

# Edit main.py with your logic
# Already has:
# - Shared models import ✅
# - Core Gateway client ✅
# - Error handling ✅
# - Logging ✅
# - Health checks ✅
```

**Benefits:**
- ✅ Consistent code structure
- ✅ Best practices built-in
- ✅ 80% of boilerplate done

### 4. Mock Services for Week 1

**Problem:** Infrastructure not ready, teams blocked

**Solution:** Mock servers return predefined responses

```bash
# Start mocks instantly
docker-compose --profile mock up -d

# All teams can develop immediately
# No waiting for Core Gateway implementation
```

**Benefits:**
- ✅ Zero idle time
- ✅ Predictable testing
- ✅ Fast feedback loop

---

## 🚀 How Teams Use This Framework

### Infrastructure Team (Team 1-3)

**Week 1:** Setup & implement real services

```bash
# Already done for you:
✅ Core Gateway (services/core_gateway/main.py)
✅ DB Gateway (services/db_gateway/main.py)

# TODO by infrastructure team:
⏳ Orchestrator (Layer 2)
⏳ RAG Service (Layer 6)
⏳ Open WebUI integration (Layer 1)
```

### AI Services Teams (Team 4-9)

**Week 1:** Develop with mocks

```bash
# Day 1: Copy template
cp -r services/semantic_chunking services/classification

# Day 1-5: Implement your service
cd services/classification
# Edit main.py
# Service calls mock-core-gateway automatically

# Test locally
docker-compose up classification
curl http://localhost:YOUR_PORT/health
```

**Week 2:** Switch to real Core Gateway

```bash
# In .env
USE_REAL_CORE_GATEWAY=true

# Restart service
docker-compose restart classification

# Now calls REAL Core Gateway!
```

### Example: Classification Service

```python
# services/classification/main.py
from shared.models.core_gateway import LLMRequest, Message
from shared.config import feature_flags
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)

# Core Gateway client (auto-detects mock/real)
class CoreGatewayClient:
    def __init__(self):
        if feature_flags.use_real_core_gateway():
            self.base_url = "http://core-gateway:8080"
        else:
            self.base_url = "http://mock-core-gateway:1080"

    async def call_llm(self, request: LLMRequest):
        # Implementation here
        ...

# Your service logic
@app.post("/classify")
async def classify_property(request: ClassifyRequest):
    logger.info(f"📝 Classifying: {request.text}")

    # Call LLM via Core Gateway
    llm_response = await core_gateway.call_llm(...)

    # Process response
    result = process_classification(llm_response.content)

    logger.info(f"✅ Classification: {result}")
    return ClassifyResponse(...)
```

---

## 🧪 Testing Strategy

### Unit Tests (No Dependencies)

```python
# tests/test_your_service.py
@pytest.mark.asyncio
async def test_classify_property():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/classify", json={...})
        assert response.status_code == 200
```

### Integration Tests (With Mocks)

```bash
# Start mock infrastructure
docker-compose --profile mock up -d

# Run integration tests
pytest tests/ -v

# Or use test script
./test_integration.sh  # Linux/Mac
.\test_integration.ps1  # Windows
```

### End-to-End Tests (Real Services)

```bash
# Start all real services
docker-compose --profile real up -d

# Test full flow
curl -X POST http://localhost:8080/v1/chat/completions ...
```

---

## 📋 Development Workflow

### Day 1: Setup

```bash
# 1. Clone repo
git clone <repo-url>
cd ree-ai

# 2. Setup environment
cp .env.example .env
# Edit .env, add OPENAI_API_KEY

# 3. Start infrastructure + mocks
docker-compose --profile mock up -d

# 4. Test mocks
./test_integration.sh
```

### Week 1: Develop with Mocks

```bash
# Infrastructure team: Implement real services
cd services/core_gateway
# Implement main.py

# AI services teams: Develop with mocks
cd services/your_service
# Copy template, implement logic
# Calls mock-core-gateway automatically
```

### Week 2: Integration

```bash
# Day 1: Enable real Core Gateway
# In .env:
USE_REAL_CORE_GATEWAY=true

# Day 2: Enable real DB Gateway
USE_REAL_DB_GATEWAY=true

# Day 3-5: Enable AI services one by one
SERVICE_CLASSIFICATION=real
SERVICE_COMPLETENESS=real
# etc.
```

### Week 3-4: Full Integration

```bash
# All services using real implementations
docker-compose --profile real up -d

# End-to-end testing
pytest tests/ -v

# Load testing (100 concurrent users)
# Performance optimization
```

### Week 5: Deployment

```bash
# Deploy to staging
docker-compose -f docker-compose.prod.yml up -d

# UAT testing
# Deploy to production
```

---

## 🛠️ Common Tasks

### Add New Service

```bash
# 1. Copy template
cp -r services/semantic_chunking services/new_service

# 2. Edit files
cd services/new_service
# Edit main.py - implement your logic
# Edit requirements.txt - add dependencies

# 3. Add to docker-compose.yml
services:
  new-service:
    build:
      context: .
      dockerfile: services/new_service/Dockerfile
    environment:
      - USE_REAL_CORE_GATEWAY=${USE_REAL_CORE_GATEWAY}
    ports:
      - "8083:8080"
    networks:
      - ree-ai-network
    profiles:
      - real
      - all

# 4. Test
docker-compose up new-service
curl http://localhost:8083/health
```

### Update Shared Models

```python
# 1. Edit shared/models/core_gateway.py
class LLMRequest(BaseModel):
    # Add new field
    new_field: str = Field(...)

# 2. Rebuild ALL services
docker-compose build

# 3. All services now use updated model
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f core-gateway

# Last 100 lines
docker-compose logs --tail=100 core-gateway
```

### Debug Service

```bash
# 1. Check health
curl http://localhost:8080/health

# 2. View logs
docker-compose logs -f core-gateway

# 3. Enter container
docker exec -it ree-ai-core-gateway bash

# 4. Check network
docker network inspect ree-ai-network

# 5. Test connectivity
docker exec -it ree-ai-core-gateway curl http://mock-core-gateway:1080/mockserver/status
```

---

## 📊 Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│  🏗️ FRAMEWORK COMPONENTS                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ✅ Shared Models (shared/models/)                      │
│     └─ Type-safe API contracts for all services         │
│                                                          │
│  ✅ Feature Flags (shared/config.py)                    │
│     └─ Gradual mock → real transition                   │
│                                                          │
│  ✅ Mock Services (mocks/)                              │
│     └─ Week 1 development, zero blocking                │
│                                                          │
│  ✅ Sample Service (services/semantic_chunking/)        │
│     └─ Template for all Layer 3 services                │
│                                                          │
│  ✅ Infrastructure (docker-compose.yml)                 │
│     └─ Postgres, Redis, OpenSearch, Ollama             │
│                                                          │
│  ✅ Core Services (services/core_gateway, db_gateway)  │
│     └─ Production-ready implementations                 │
│                                                          │
│  ✅ Testing (tests/, test_integration.*)                │
│     └─ Unit + integration test examples                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Success Criteria

### Week 1 (Development with Mocks)

- [x] All infrastructure running (Postgres, Redis, OpenSearch, Ollama)
- [x] Mock services responding (Core Gateway, DB Gateway)
- [x] Sample service working (Semantic Chunking)
- [x] All 13 teams can develop in parallel
- [x] Zero blocking dependencies

### Week 2 (Integration)

- [ ] Real Core Gateway deployed
- [ ] Real DB Gateway deployed
- [ ] At least 2 AI services using real implementations
- [ ] Integration tests passing

### Week 3-4 (Full Integration)

- [ ] All services using real implementations
- [ ] End-to-end flow working
- [ ] Performance acceptable (< 2s response time)

### Week 5 (Deployment)

- [ ] MVP deployed to production
- [ ] Users can search properties
- [ ] All core features working

---

## 📞 Support

### Documentation

- **Quick Start:** `QUICKSTART.md` (5-minute setup)
- **Sample Service:** `services/semantic_chunking/README.md`
- **Team Guide:** `docs/MVP_TEAM_COLLABORATION_GUIDE.md`
- **Architecture:** `docs/CTO_EXECUTIVE_SUMMARY.md`

### Common Issues

See troubleshooting sections in:
- `QUICKSTART.md` - Setup issues
- `services/semantic_chunking/README.md` - Service implementation issues
- `docs/MVP_TEAM_COLLABORATION_GUIDE.md` - Team collaboration issues

---

## 🎓 Summary

This framework provides:

✅ **Complete infrastructure** - Postgres, Redis, OpenSearch, Ollama, Mocks
✅ **Core services** - Core Gateway, DB Gateway (production-ready)
✅ **Sample service** - Template for Layer 3 services
✅ **Shared models** - Type-safe API contracts
✅ **Feature flags** - Gradual mock → real transition
✅ **Docker Compose** - One-command deployment
✅ **Tests** - Unit + integration examples
✅ **Documentation** - Quick start, guides, examples

**Zero blocking. Parallel development. Production-ready code.**

---

**Ready to build? Start with:** `QUICKSTART.md` 🚀

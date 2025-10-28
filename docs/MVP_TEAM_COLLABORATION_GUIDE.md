# 🤝 REE AI - MVP Team Collaboration Guide

**Purpose:** Giải quyết dependency blocking giữa các dev teams khi làm MVP
**Target:** 13 teams working in parallel WITHOUT blocking each other
**Timeline:** 25 days (không cần thêm thời gian cho HA/scalability)

---

## 🚨 VẤN ĐỀ CHÍNH (Nếu Không Có Strategy)

### Dependency Hell

```
┌─────────────────────────────────────────────────────────────┐
│ TRADITIONAL APPROACH (Serial Development)                   │
└─────────────────────────────────────────────────────────────┘

Week 1:
  Day 1-2: Team 1 builds Core Gateway
           → Teams 6-11 (AI Services) BLOCKED ⏸️

  Day 2-3: Team 2 builds DB Gateway
           → Team 12 (RAG) BLOCKED ⏸️
           → Team 13 (Crawler) BLOCKED ⏸️

  Day 3-4: Team 3 setup OpenSearch
           → Team 12 (RAG) still BLOCKED ⏸️

  Day 4-5: Team 4 builds Orchestrator
           → Team 5 (Frontend) BLOCKED ⏸️

Result: 8 teams IDLE for 5 days = 40 man-days wasted ❌
```

**Total Waste:** 40 man-days × $500/day = **$20,000 wasted** 💸

---

## ✅ GIẢI PHÁP: 4-Strategy Approach

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│ MVP PARALLEL APPROACH (All teams work from Day 1)           │
└─────────────────────────────────────────────────────────────┘

Day 1: ALL 13 teams start working simultaneously
       ↓
Strategy 1: Contract-First (API mocking)
Strategy 2: Shared Models (Pydantic interfaces)
Strategy 3: Docker Compose Mocks (Integration testing)
Strategy 4: Feature Flags (Gradual integration)
       ↓
Week 2: Swap mocks → real services (1 by 1)
       ↓
Week 3-4: Full integration testing
       ↓
Week 5: MVP deployment

Result: ZERO idle time = $0 wasted ✅
```

---

## 🎯 STRATEGY 1: Contract-First Development

### Principle

**"Define interfaces FIRST, implement LATER"**

### Step 1: Define All API Contracts (Day 1, Morning)

```yaml
# contracts/core_gateway.yaml
openapi: 3.0.0
info:
  title: Core Gateway API
  version: 1.0.0
servers:
  - url: http://localhost:8000
    description: Core Gateway (LiteLLM)

paths:
  /v1/chat/completions:
    post:
      summary: Call LLM (Ollama or OpenAI)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - model
                - messages
              properties:
                model:
                  type: string
                  enum: ["ollama/llama2", "gpt-4o-mini"]
                  example: "gpt-4o-mini"
                messages:
                  type: array
                  items:
                    type: object
                    properties:
                      role:
                        type: string
                        enum: ["user", "assistant", "system"]
                      content:
                        type: string
                  example:
                    - role: "user"
                      content: "Tìm nhà Quận 1"
                max_tokens:
                  type: integer
                  default: 1000
      responses:
        200:
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  choices:
                    type: array
                    items:
                      type: object
                      properties:
                        message:
                          type: object
                          properties:
                            role:
                              type: string
                            content:
                              type: string
                  usage:
                    type: object
                    properties:
                      prompt_tokens:
                        type: integer
                      completion_tokens:
                        type: integer
                      total_tokens:
                        type: integer
        500:
          description: LLM call failed
```

**Similarly define:**
- `contracts/db_gateway.yaml` - Search properties, CRUD operations
- `contracts/orchestrator.yaml` - Route requests to services
- `contracts/rag_service.yaml` - RAG pipeline
- `contracts/ai_services/*.yaml` - 6 AI services

**Timeline:** 4 hours (1 architect + 1 dev)

### Step 2: Generate Mock Servers (Day 1, Afternoon)

```bash
# Generate mock server from OpenAPI spec
npm install -g @stoplight/prism-cli

# Start mock Core Gateway
prism mock contracts/core_gateway.yaml --port 8000

# Start mock DB Gateway
prism mock contracts/db_gateway.yaml --port 8001

# Start mock Orchestrator
prism mock contracts/orchestrator.yaml --port 8002
```

**Result:**
- ✅ All APIs available on **Day 1**
- ✅ Teams can integrate immediately
- ✅ Predictable responses (from examples in OpenAPI)

### Step 3: Teams Develop Against Mocks (Week 1)

```python
# Team 6: Semantic Chunking Service
# Starts development on Day 1 (no waiting!)

import requests

class CoreGatewayClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def call_llm(self, model: str, messages: list):
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            json={
                "model": model,
                "messages": messages
            }
        )
        return response.json()

# Week 1: Point to mock
gateway = CoreGatewayClient("http://mock-core-gateway:8000")

# Week 2: Point to real (just change URL!)
gateway = CoreGatewayClient("http://real-core-gateway:8000")

def semantic_chunking(text: str):
    response = gateway.call_llm(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a text chunking expert"},
            {"role": "user", "content": f"Chunk this: {text}"}
        ]
    )
    return response["choices"][0]["message"]["content"]
```

**Benefits:**
- ✅ Team 6 works independently (no blocking)
- ✅ Easy testing (mock = deterministic)
- ✅ Seamless transition (mock → real = URL change)

---

## 🎯 STRATEGY 2: Shared Interface Definitions

### Principle

**"One source of truth for data models"**

### Setup Shared Package (Day 1)

```
ree-ai/
├── shared/                    # ← All teams import from here
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── core_gateway.py   # LLM interfaces
│   │   ├── db_gateway.py     # DB interfaces
│   │   ├── orchestrator.py   # Routing interfaces
│   │   └── rag.py            # RAG interfaces
│   └── constants.py          # Shared constants
│
├── services/                  # ← Each team's service
│   ├── semantic_chunking/
│   ├── classification/
│   ├── completeness/
│   └── ...
│
└── docker-compose.yml
```

### Define Pydantic Models

```python
# shared/models/core_gateway.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class LLMRequest(BaseModel):
    model: Literal["ollama/llama2", "gpt-4o-mini"]
    messages: List[Message]
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    temperature: float = Field(default=0.7, ge=0, le=2)

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class LLMResponse(BaseModel):
    content: str
    model: str
    usage: TokenUsage

# shared/models/db_gateway.py
from pydantic import BaseModel
from typing import List, Dict, Optional

class PropertyFilter(BaseModel):
    region: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None

class Property(BaseModel):
    id: str
    title: str
    price: float
    location: str
    bedrooms: int
    description: str

class SearchRequest(BaseModel):
    query: str
    filters: PropertyFilter = PropertyFilter()
    limit: int = Field(default=10, ge=1, le=100)

class SearchResponse(BaseModel):
    results: List[Property]
    total: int
    took_ms: int

# shared/models/rag.py
from pydantic import BaseModel
from typing import List

class RAGRequest(BaseModel):
    query: str
    user_id: str
    conversation_id: str
    use_history: bool = True

class RAGContext(BaseModel):
    retrieved_docs: List[Property]
    conversation_history: List[Message]

class RAGResponse(BaseModel):
    answer: str
    sources: List[Property]
    context_used: RAGContext
```

### Usage by Teams

```python
# Team 1: Core Gateway Implementation
from shared.models.core_gateway import LLMRequest, LLMResponse, TokenUsage
from litellm import completion

class CoreGateway:
    def call_llm(self, request: LLMRequest) -> LLMResponse:
        # Pydantic validates input automatically
        response = completion(
            model=request.model,
            messages=[m.dict() for m in request.messages],
            max_tokens=request.max_tokens
        )

        # Return validated response
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=TokenUsage(**response.usage.dict())
        )

# Team 6: Semantic Chunking (Consumer)
from shared.models.core_gateway import LLMRequest, LLMResponse, Message

def semantic_chunking(text: str) -> list:
    request = LLMRequest(
        model="gpt-4o-mini",
        messages=[
            Message(role="system", content="Chunking expert"),
            Message(role="user", content=f"Chunk: {text}")
        ]
    )

    # Type-safe! IDE autocomplete works!
    response: LLMResponse = core_gateway.call_llm(request)
    return response.content.split("\n")
```

**Benefits:**
- ✅ **Type safety:** Pydantic validates at runtime
- ✅ **No format conflicts:** All teams use same models
- ✅ **Easy refactoring:** Change `shared/models/*.py` once → All teams update
- ✅ **IDE support:** Autocomplete, type hints, error checking

---

## 🎯 STRATEGY 3: Docker Compose Mock Services

### Principle

**"Test integration early, even without real services"**

### Setup Mock Infrastructure (Day 1)

```yaml
# docker-compose.mock.yml
version: '3.8'

services:
  # Mock Core Gateway (for AI services)
  mock-core-gateway:
    image: mockserver/mockserver:latest
    ports:
      - "8000:1080"
    environment:
      MOCKSERVER_INITIALIZATION_JSON_PATH: /config/expectations.json
    volumes:
      - ./mocks/core_gateway_expectations.json:/config/expectations.json

  # Mock DB Gateway
  mock-db-gateway:
    image: mockserver/mockserver:latest
    ports:
      - "8001:1080"
    volumes:
      - ./mocks/db_gateway_expectations.json:/config/expectations.json

  # Mock Orchestrator
  mock-orchestrator:
    image: mockserver/mockserver:latest
    ports:
      - "8002:1080"
    volumes:
      - ./mocks/orchestrator_expectations.json:/config/expectations.json

  # Redis (real, simple to setup)
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  # PostgreSQL (real, for Context Memory)
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ree_ai
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Team services connect to mocks
  semantic-chunking:
    build: ./services/semantic_chunking
    environment:
      CORE_GATEWAY_URL: http://mock-core-gateway:1080
      DB_GATEWAY_URL: http://mock-db-gateway:1080
    depends_on:
      - mock-core-gateway
      - mock-db-gateway

  classification:
    build: ./services/classification
    environment:
      CORE_GATEWAY_URL: http://mock-core-gateway:1080
    depends_on:
      - mock-core-gateway

volumes:
  postgres_data:
```

### Configure Mock Responses

```json
// mocks/core_gateway_expectations.json
{
  "httpRequest": {
    "method": "POST",
    "path": "/v1/chat/completions",
    "body": {
      "type": "JSON",
      "json": {
        "model": "gpt-4o-mini"
      }
    }
  },
  "httpResponse": {
    "statusCode": 200,
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "choices": [
        {
          "message": {
            "role": "assistant",
            "content": "Đây là mock response từ GPT-4"
          }
        }
      ],
      "usage": {
        "prompt_tokens": 20,
        "completion_tokens": 30,
        "total_tokens": 50
      }
    }
  }
}
```

### Team Workflow

```bash
# Week 1: All teams work with mocks
docker-compose -f docker-compose.mock.yml up

# Test your service
curl http://localhost:8000/v1/chat/completions \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [...]}'

# Week 2: Gradually swap to real services
# 1. Core Gateway ready → Update docker-compose.yml
# 2. Test with real Core Gateway
# 3. If works → Keep real, else rollback to mock
```

**Benefits:**
- ✅ Integration testing from **Day 1**
- ✅ Fast feedback (no waiting for other teams)
- ✅ Realistic testing environment
- ✅ Easy rollback (mock ↔ real)

---

## 🎯 STRATEGY 4: Feature Flags

### Principle

**"Integrate gradually, rollback easily"**

### Setup Feature Flag System

```python
# shared/feature_flags.py
from enum import Enum
from typing import Dict
import os

class ServiceMode(str, Enum):
    MOCK = "mock"
    REAL = "real"

class FeatureFlags:
    def __init__(self):
        # Can override via environment variables
        self.use_real_core_gateway = os.getenv("USE_REAL_CORE_GATEWAY", "false").lower() == "true"
        self.use_real_db_gateway = os.getenv("USE_REAL_DB_GATEWAY", "false").lower() == "true"
        self.use_real_orchestrator = os.getenv("USE_REAL_ORCHESTRATOR", "false").lower() == "true"

        self.services: Dict[str, ServiceMode] = {
            "semantic_chunking": ServiceMode(os.getenv("SERVICE_SEMANTIC_CHUNKING", "mock")),
            "classification": ServiceMode(os.getenv("SERVICE_CLASSIFICATION", "mock")),
            "attribute_extraction": ServiceMode(os.getenv("SERVICE_ATTRIBUTE_EXTRACTION", "mock")),
            "completeness": ServiceMode(os.getenv("SERVICE_COMPLETENESS", "mock")),
            "price_suggestion": ServiceMode(os.getenv("SERVICE_PRICE_SUGGESTION", "mock")),
            "rerank": ServiceMode(os.getenv("SERVICE_RERANK", "mock")),
            "rag": ServiceMode(os.getenv("SERVICE_RAG", "mock"))
        }

    def is_service_real(self, service_name: str) -> bool:
        return self.services.get(service_name) == ServiceMode.REAL

# Global instance
feature_flags = FeatureFlags()
```

### Usage in Services

```python
# services/orchestrator/main.py
from shared.feature_flags import feature_flags
from shared.models.core_gateway import LLMRequest

# Import both real and mock implementations
from clients.core_gateway_real import RealCoreGateway
from clients.core_gateway_mock import MockCoreGateway

def get_core_gateway():
    if feature_flags.use_real_core_gateway:
        return RealCoreGateway(url="http://core-gateway:8000")
    else:
        return MockCoreGateway()

def get_ai_service(service_name: str):
    if feature_flags.is_service_real(service_name):
        # Call real service
        return f"http://{service_name}:8080"
    else:
        # Use mock
        return f"http://mock-{service_name}:1080"

# Example: Route request
async def handle_search_request(query: str):
    # Check which services are enabled
    if feature_flags.is_service_real("semantic_chunking"):
        # Call real Semantic Chunking
        chunks = await call_service("semantic_chunking", query)
    else:
        # Use mock chunks
        chunks = ["Quận 1", "2 phòng ngủ"]

    # Continue with next service...
```

### Integration Timeline

```bash
# Week 1: All mocks
export USE_REAL_CORE_GATEWAY=false
export SERVICE_SEMANTIC_CHUNKING=mock
docker-compose up

# Week 2, Day 1: Core Gateway ready
export USE_REAL_CORE_GATEWAY=true  # ← Enable!
export SERVICE_SEMANTIC_CHUNKING=mock
docker-compose up

# Week 2, Day 3: Semantic Chunking ready
export USE_REAL_CORE_GATEWAY=true
export SERVICE_SEMANTIC_CHUNKING=real  # ← Enable!
docker-compose up

# If Semantic Chunking has bugs:
export SERVICE_SEMANTIC_CHUNKING=mock  # ← Instant rollback!
docker-compose restart orchestrator
```

**Benefits:**
- ✅ Gradual integration (no "big bang")
- ✅ Easy rollback (flip environment variable)
- ✅ A/B testing (compare mock vs real performance)
- ✅ Production-ready (can use in prod for canary deployments)

---

## 📋 WEEK-BY-WEEK WORKFLOW

### Week 1: Parallel Development (All Mocks)

**Day 1 (Setup):**
- ⏰ Morning: Tech lead defines all API contracts (OpenAPI specs)
- ⏰ Afternoon:
  - Setup `shared/models/` with Pydantic
  - Start all mock servers
  - Create `docker-compose.mock.yml`
  - All teams clone repo, can run `docker-compose up`

**Day 2-5 (Development):**
- **Infrastructure Teams (1-5):**
  - Team 1: Build real Core Gateway (LiteLLM)
  - Team 2: Build real DB Gateway (FastAPI + SQLAlchemy)
  - Team 3: Setup OpenSearch (Docker)
  - Team 4: Build Orchestrator (LangChain Router)
  - Team 5: Build Open WebUI (integrate with mock Orchestrator)

- **AI Services Teams (6-11):** Develop services using mocks
  - Team 6: Semantic Chunking
  - Team 7: Attribute Extraction
  - Team 8: Classification
  - Team 9: Completeness
  - Team 10: Price Suggestion
  - Team 11: Rerank

- **Data Teams:**
  - Team 12: RAG Service (develop with mock DB/Core Gateway)
  - Team 13: Crawl4AI (develop with mock DB Gateway)

**End of Week 1:**
- ✅ All 13 teams have working code (with mocks)
- ✅ All services can run locally via Docker Compose
- ✅ Unit tests pass

---

### Week 2: Integration (Swap Mocks → Real)

**Day 1:**
- Team 1 deploys real Core Gateway
- **Action:** Enable feature flag
  ```bash
  export USE_REAL_CORE_GATEWAY=true
  ```
- **Test:** All AI services (Teams 6-11) test with real Core Gateway
- **Result:** If tests pass → Keep real. If fail → Rollback to mock, Team 1 fixes bugs.

**Day 2:**
- Teams 2, 3 deploy real DB Gateway + OpenSearch
- **Action:**
  ```bash
  export USE_REAL_DB_GATEWAY=true
  ```
- **Test:** Team 12 (RAG), Team 13 (Crawler) test with real storage
- **Result:** If pass → Keep. Else → Rollback.

**Day 3:**
- Team 4 deploys real Orchestrator
- **Action:**
  ```bash
  export USE_REAL_ORCHESTRATOR=true
  ```
- **Test:** Team 5 (Frontend) test full flow
- **Result:** If pass → Keep. Else → Rollback.

**Day 4-5:**
- Enable AI services one by one:
  ```bash
  export SERVICE_SEMANTIC_CHUNKING=real
  export SERVICE_CLASSIFICATION=real
  # ... enable 1 per day
  ```

**End of Week 2:**
- ✅ All core infrastructure (Core Gateway, DB Gateway, Orchestrator) using REAL
- ✅ 2-3 AI services using REAL
- ✅ Integration tests pass

---

### Week 3-4: Full Integration

**Week 3:**
- Enable remaining AI services (Teams 7-11)
- Enable RAG Service (Team 12)
- Enable Crawler (Team 13)
- End-to-end testing:
  ```
  User → Open WebUI → Orchestrator → AI Services → RAG → Storage
  ```

**Week 4:**
- Bug fixing
- Performance testing (not optimization, just measure baseline)
- Documentation

**End of Week 4:**
- ✅ All services using REAL implementations
- ✅ MVP features complete
- ✅ End-to-end flow working

---

### Week 5: Testing & Deployment

- Load testing (100 concurrent users)
- Security testing (basic OWASP checks)
- Deploy to staging
- User acceptance testing (UAT)
- Deploy to production

**End of Week 5:**
- ✅ MVP deployed
- ✅ Users can use the system

---

## 🛠️ TOOLS & SETUP

### Required Tools (Day 1 Setup)

```bash
# 1. OpenAPI Mock Server (for Strategy 1)
npm install -g @stoplight/prism-cli

# 2. Docker + Docker Compose (for Strategy 3)
# Install from: https://docs.docker.com/get-docker/

# 3. Python environment (all teams)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Shared Requirements

```txt
# requirements.txt (root of repo)
# Shared by all teams
pydantic==2.5.0
fastapi==0.104.0
uvicorn==0.24.0
httpx==0.25.0
redis==5.0.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pytest==7.4.3
pytest-asyncio==0.21.1

# Team-specific dependencies in their folders
# services/semantic_chunking/requirements.txt
# services/classification/requirements.txt
# ...
```

### Repository Structure

```
ree-ai/
├── README.md
├── docker-compose.mock.yml        # Week 1
├── docker-compose.yml             # Week 2+
├── requirements.txt               # Shared dependencies
│
├── contracts/                     # OpenAPI specs (Strategy 1)
│   ├── core_gateway.yaml
│   ├── db_gateway.yaml
│   ├── orchestrator.yaml
│   └── ai_services/
│       ├── semantic_chunking.yaml
│       └── ...
│
├── mocks/                         # Mock server configs (Strategy 3)
│   ├── core_gateway_expectations.json
│   ├── db_gateway_expectations.json
│   └── orchestrator_expectations.json
│
├── shared/                        # Shared code (Strategy 2)
│   ├── __init__.py
│   ├── models/                   # Pydantic models
│   │   ├── __init__.py
│   │   ├── core_gateway.py
│   │   ├── db_gateway.py
│   │   ├── orchestrator.py
│   │   └── rag.py
│   ├── feature_flags.py          # Strategy 4
│   └── constants.py
│
├── services/                      # Each team's service
│   ├── core_gateway/             # Team 1
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── main.py
│   ├── db_gateway/               # Team 2
│   ├── orchestrator/             # Team 4
│   ├── semantic_chunking/        # Team 6
│   ├── classification/           # Team 7
│   ├── attribute_extraction/     # Team 8
│   ├── completeness/             # Team 9
│   ├── price_suggestion/         # Team 10
│   ├── rerank/                   # Team 11
│   ├── rag_service/              # Team 12
│   └── crawler/                  # Team 13
│
├── frontend/                      # Team 5 (Open WebUI)
│   └── open-webui/
│
├── tests/                         # Integration tests
│   ├── test_core_gateway.py
│   ├── test_orchestrator.py
│   └── test_end_to_end.py
│
└── docs/
    ├── MVP_TEAM_COLLABORATION_GUIDE.md  # This file
    ├── API_CONTRACTS.md                 # Auto-generated from OpenAPI
    └── DEPLOYMENT.md
```

---

## 🚫 ANTI-PATTERNS (Tránh)

### ❌ Anti-Pattern 1: "Wait for Infrastructure"

```python
# ❌ BAD: Team 6 waits for Team 1
# Week 1: "Core Gateway chưa xong, tôi không làm gì được"
# Result: 5 days idle

# ✅ GOOD: Use mock
mock_gateway = MockCoreGateway()
# Continue development immediately
```

### ❌ Anti-Pattern 2: "Hardcoded Mock Data in Service Code"

```python
# ❌ BAD: Mock data inside service
def semantic_chunking(text: str):
    if os.getenv("ENV") == "dev":
        return ["mock", "chunks"]  # ← Hard to maintain!
    else:
        # Real implementation
        ...

# ✅ GOOD: Use Strategy 3 (External mock server)
# Service code remains clean, mock is external
```

### ❌ Anti-Pattern 3: "Big Bang Integration"

```bash
# ❌ BAD: Enable all services at once
export USE_REAL_CORE_GATEWAY=true
export USE_REAL_DB_GATEWAY=true
export SERVICE_SEMANTIC_CHUNKING=real
export SERVICE_CLASSIFICATION=real
# ... enable all
# Result: If fails, hard to debug which service caused it

# ✅ GOOD: Enable 1 by 1 (Strategy 4)
export USE_REAL_CORE_GATEWAY=true  # Day 1
# Test → Works → Next
export SERVICE_SEMANTIC_CHUNKING=real  # Day 2
# Test → Works → Next
```

### ❌ Anti-Pattern 4: "Inconsistent Data Models"

```python
# ❌ BAD: Each team defines their own models
# Team 6:
class LLMRequest:
    model: str
    prompt: str  # ← "prompt"

# Team 7:
class LLMRequest:
    model: str
    messages: list  # ← "messages"

# Result: Integration fails!

# ✅ GOOD: Use Strategy 2 (shared/models/)
from shared.models.core_gateway import LLMRequest
# All teams use same model
```

---

## 📊 SUCCESS METRICS

### Week 1 (All Mocks)

- [ ] All 13 teams have runnable services
- [ ] `docker-compose -f docker-compose.mock.yml up` starts all services
- [ ] Unit tests pass for all services
- [ ] 0 teams blocked (no idle time)

### Week 2 (Integration Start)

- [ ] Real Core Gateway deployed
- [ ] Real DB Gateway + OpenSearch deployed
- [ ] Real Orchestrator deployed
- [ ] At least 2 AI services using REAL implementations
- [ ] Frontend can make end-to-end call (even if 4 services still mocked)

### Week 3-4 (Full Integration)

- [ ] All services using REAL implementations
- [ ] End-to-end flow works:
  ```
  User → UI → Orchestrator → AI Service → RAG → Storage → LLM
  ```
- [ ] Integration tests pass

### Week 5 (Deployment)

- [ ] MVP deployed to production
- [ ] Users can:
  - Create property listing
  - Search properties
  - Get price suggestions
  - Receive completeness feedback

---

## 🆘 TROUBLESHOOTING

### Issue 1: "Mock server not returning expected response"

```bash
# Check mock server logs
docker logs mock-core-gateway

# Verify expectations file
cat mocks/core_gateway_expectations.json

# Test mock directly
curl http://localhost:8000/v1/chat/completions -X POST -d '{...}'
```

**Solution:** Update expectations file, restart mock server

### Issue 2: "Shared models changed, my service broke"

```bash
# Update shared models
cd shared/
git pull origin main

# Reinstall shared package
pip install -e .

# Fix your code to match new interface
```

**Solution:** Use semantic versioning for `shared/` package

### Issue 3: "Feature flag not working"

```bash
# Check environment variables
docker-compose config

# Verify feature flag read correctly
docker exec service_name env | grep USE_REAL
```

**Solution:** Restart service after changing env vars

### Issue 4: "Integration test fails after enabling real service"

```bash
# Rollback to mock
export SERVICE_NAME=mock
docker-compose restart orchestrator

# Check service logs
docker logs service_name

# Debug real service
docker exec -it service_name bash
```

**Solution:** Fix bugs in real service, then re-enable

---

## ✅ CHECKLIST (Day 1 Setup)

### Tech Lead / Architect (4 hours)

- [ ] Define all OpenAPI specs (`contracts/*.yaml`)
- [ ] Create `shared/models/` with Pydantic models
- [ ] Setup `docker-compose.mock.yml`
- [ ] Start all mock servers, verify reachable
- [ ] Create repository structure (folders for 13 teams)
- [ ] Write README with setup instructions
- [ ] Record setup video (10 minutes) for all teams

### Each Team (2 hours)

- [ ] Clone repository
- [ ] Run `docker-compose -f docker-compose.mock.yml up`
- [ ] Verify can call mock APIs
- [ ] Read OpenAPI spec for your service
- [ ] Import `shared.models` in your code
- [ ] Write first unit test (with mock)
- [ ] Commit & push code

### End of Day 1

- [ ] All 13 teams can run full system locally
- [ ] All mocks responding
- [ ] All teams writing code (no blockers)

---

## 🎓 SUMMARY

### Key Principles

1. **Contract-First:** Define APIs before implementation
2. **Shared Models:** One source of truth (Pydantic)
3. **Mock Everything:** No team waits for others
4. **Gradual Integration:** Enable real services 1 by 1
5. **Easy Rollback:** Feature flags for safety

### Expected Results

**Without Strategies:**
- 40 man-days wasted (blocking)
- High risk of integration conflicts
- Late discovery of issues (Week 3-4)

**With Strategies:**
- 0 man-days wasted (all teams work from Day 1)
- Low risk (gradual integration)
- Early issue discovery (Week 1 with mocks)

### Timeline Comparison

```
Traditional Approach:
Week 1: Infrastructure (5 teams work, 8 teams idle)
Week 2: Services (13 teams work)
Week 3: Integration (conflicts discovered!)
Week 4: Bug fixing
Week 5: Deployment
Total: 30-35 days (due to rework)

Our Approach:
Week 1: All 13 teams work (with mocks)
Week 2: Gradual integration (smooth)
Week 3-4: Full integration (few conflicts)
Week 5: Deployment
Total: 25 days (as planned) ✅
```

---

## 📞 SUPPORT

### Daily Standup (15 minutes)

Each team reports:
1. What we completed yesterday
2. What we're doing today
3. Any blockers

### Integration Issues

Post in `#integration` Slack channel:
- Which service broke
- Error message
- Steps to reproduce

### Code Reviews

- Each PR reviewed within 4 hours
- Focus on: Interface compliance, shared model usage
- Merge only if tests pass

---

**Last Updated:** 2025-10-29
**Version:** 1.0 (MVP)
**Status:** ✅ Ready for Day 1 Kickoff

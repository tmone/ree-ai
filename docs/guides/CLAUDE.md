# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

REE AI is a **production-ready microservices platform** for AI-powered real estate applications. The platform features a 7-layer architecture with 18+ services, integrating LangChain, Open WebUI, RAG pipelines, and multiple LLM providers (OpenAI, Ollama).

**Key Architecture Principles:**
- Microservices communicate via REST APIs
- Feature flags enable mock→real transitions for parallel development
- Type-safe Pydantic models define API contracts across services
- BaseService class provides service registration, health checks, and logging
- Service Registry enables dynamic service discovery

## Essential Commands

### Starting Services

```bash
# Start all real services (production mode)
docker-compose --profile real up -d

# Start mock services only (Week 1 development)
docker-compose --profile mock up -d

# Start all services (mock + real)
docker-compose --profile all up -d

# View logs
docker-compose logs -f [service-name]

# Stop all services
docker-compose down

# Full cleanup (including volumes)
docker-compose down -v
```

### Testing

```bash
# Run all tests (recommended)
./scripts/run-tests.sh              # Linux/Mac
scripts\run-tests.bat               # Windows

# Run with pytest directly (requires services running)
pytest tests/ -v

# Run specific test categories
pytest tests/ -m integration -v     # Integration tests only
pytest tests/ -m unit -v             # Unit tests only
pytest tests/test_orchestrator.py -v # Single test file

# Run tests with Docker Compose
docker-compose -f docker-compose.test.yml up -d
sleep 30  # Wait for services to be healthy
docker-compose -f docker-compose.test.yml run --rm test-runner
docker-compose -f docker-compose.test.yml down -v
```

### Development

```bash
# Check service health
curl http://localhost:8000/health  # Service Registry
curl http://localhost:8080/health  # Core Gateway
curl http://localhost:8081/health  # DB Gateway
curl http://localhost:8090/health  # Orchestrator
curl http://localhost:3000         # Open WebUI

# View service API docs
open http://localhost:8090/docs    # FastAPI auto-docs for Orchestrator

# Build single service
docker-compose build [service-name]

# Run single service in standalone mode
docker-compose up [service-name]
```

### Database Operations

```bash
# Access PostgreSQL
docker exec -it ree-ai-postgres psql -U ree_ai_user -d ree_ai

# Access Redis
docker exec -it ree-ai-redis redis-cli

# Access OpenSearch
curl http://localhost:9200
```

## Architecture Overview

### 7-Layer Architecture

```
Layer 0: Frontend & Gateway
  - Open WebUI (port 3000) - Chat interface
  - API Gateway (port 8888) - Rate limiting, JWT auth
  - Auth Service (port 8085) - JWT authentication

Layer 1: Service Discovery
  - Service Registry (port 8000) - Must start first

Layer 2: Orchestration
  - Orchestrator (port 8090) - LangChain-powered routing with intent detection

Layer 3: AI Services
  - Semantic Chunking (port 8082)
  - Classification (port 8083)
  - Attribute Extraction (port 8084)
  - Completeness Check (port 8086)
  - Price Suggestion (port 8087)
  - Reranking (port 8088)

Layer 4: Storage
  - DB Gateway (port 8081) - Abstracts database operations
  - PostgreSQL (port 5432)
  - OpenSearch (port 9200) - Vector + BM25 search
  - Redis (port 6379)

Layer 5: LLM Gateway
  - Core Gateway (port 8080) - LiteLLM routing to Ollama/OpenAI

Layer 6: RAG
  - RAG Service (port 8091) - Full retrieval-augmented generation pipeline
```

### Key Design Patterns

**1. BaseService Pattern:**
All microservices inherit from `core/base_service.py`:
- Auto-registration with Service Registry on startup
- Standard health check endpoints (/, /health, /info)
- Graceful shutdown handling
- Structured logging with emoji indicators

Example:
```python
from core.base_service import BaseService

class MyService(BaseService):
    def __init__(self):
        super().__init__(
            name="my_service",
            version="1.0.0",
            capabilities=["capability1", "capability2"],
            port=8080
        )

    def setup_routes(self):
        @self.app.post("/my-endpoint")
        async def my_endpoint(request: MyRequest):
            return {"result": "data"}

if __name__ == "__main__":
    service = MyService()
    service.run()
```

**2. Feature Flags (Mock→Real Transition):**
- Set via environment variables in `.env`
- Enables parallel team development in Week 1 with mocks
- Gradual integration in Week 2+ by switching to real services
- Configured in `shared/config.py`

Environment variables:
- `USE_REAL_CORE_GATEWAY=false` (Week 1) → `true` (Week 2+)
- `USE_REAL_DB_GATEWAY=false` → `true`

**3. Shared Type-Safe Models:**
All API contracts defined in `shared/models/`:
- `core_gateway.py` - LLM requests/responses (LLMRequest, LLMResponse, Message)
- `db_gateway.py` - Database operations
- `orchestrator.py` - Orchestration requests/responses

Always import and use these models for inter-service communication to prevent contract mismatches.

**4. Service Discovery:**
- Service Registry (`services/service_registry/`) maintains live service catalog
- Services auto-register on startup via BaseService
- Orchestrator queries registry to dynamically discover services by capability
- Enables zero-configuration routing

**5. LangChain Integration:**
- Orchestrator uses LangChain for intent detection and routing
- Classification service uses PromptTemplate for structured outputs
- RAG service implements full LangChain pipeline (retrieval → context → augmentation → generation)

## Important Project Constraints

### Service Communication
- Services communicate only via HTTP REST APIs (no message queues in MVP)
- Always use `httpx.AsyncClient` for async HTTP calls in FastAPI services
- Set reasonable timeouts (30s default) to prevent hanging requests
- Services should handle downstream failures gracefully

### Logging Standards
- Use `shared/utils/logger.py` for consistent logging
- Emoji indicators: 🚀 startup, ✅ success, ❌ error, ⚠️ warning, 🤖 AI operation
- Log format: `logger.info(f"🎯 Orchestration Request: user={user_id}, query='{query}'")`

### Docker & Networking
- All services communicate via `ree-ai-network` bridge network
- Service names resolve to container names (e.g., `http://core-gateway:8080`)
- Use internal ports (8080) for inter-service communication
- Use external mapped ports for local testing (e.g., 8090:8080)

### Testing Requirements
- All new services must include health check endpoint at `/health`
- Integration tests in `tests/` use pytest with async fixtures
- Use `conftest.py` fixtures: `http_client`, `registry_client`, `cleanup_test_services`
- Tests automatically clean up registered services via fixtures

## File Organization

```
ree-ai/
├── core/                      # Shared service infrastructure
│   ├── base_service.py       # BaseService class (inherit from this)
│   └── service_registry.py   # Service registry models
├── shared/                    # Shared code across services
│   ├── config.py             # Settings and feature flags
│   ├── models/               # Pydantic API contracts
│   │   ├── core_gateway.py  # LLM models (ALWAYS use these)
│   │   ├── db_gateway.py    # Database models
│   │   └── orchestrator.py  # Orchestration models
│   └── utils/                # Shared utilities
│       ├── logger.py         # Logging setup
│       ├── cache.py          # Redis caching
│       ├── metrics.py        # Prometheus metrics
│       └── sentry.py         # Error tracking
├── services/                  # Microservices (each has own Dockerfile)
│   ├── service_registry/     # START THIS FIRST
│   ├── core_gateway/         # Layer 5: LLM routing
│   ├── db_gateway/           # Layer 4: Database abstraction
│   ├── orchestrator/         # Layer 2: LangChain routing
│   ├── rag_service/          # Layer 6: RAG pipeline
│   ├── semantic_chunking/    # Layer 3: Sample service
│   └── classification/       # Layer 3: Sample service
├── tests/                     # Pytest test suite
│   ├── conftest.py           # Shared fixtures
│   └── test_*.py             # Test files
├── docker-compose.yml         # Main service orchestration
├── docker-compose.test.yml    # Test environment
└── requirements.txt           # Python dependencies
```

## Creating a New Service

1. Copy a template service:
```bash
cp -r services/semantic_chunking services/my_new_service
```

2. Update `services/my_new_service/main.py`:
```python
from core.base_service import BaseService

class MyNewService(BaseService):
    def __init__(self):
        super().__init__(
            name="my_new_service",
            version="1.0.0",
            capabilities=["my_capability"],
            port=8080
        )

    def setup_routes(self):
        @self.app.post("/my-endpoint")
        async def my_endpoint(request: MyRequest):
            # Your logic here
            return {"result": "data"}

if __name__ == "__main__":
    service = MyNewService()
    service.run()
```

3. Update `services/my_new_service/Dockerfile` (change service name references)

4. Add to `docker-compose.yml`:
```yaml
my-new-service:
  build:
    context: .
    dockerfile: services/my_new_service/Dockerfile
  container_name: ree-ai-my-new-service
  environment:
    - USE_REAL_CORE_GATEWAY=${USE_REAL_CORE_GATEWAY:-false}
    - DEBUG=${DEBUG:-true}
  ports:
    - "8099:8080"  # Choose unused external port
  depends_on:
    - service-registry
  networks:
    - ree-ai-network
  profiles:
    - real
    - all
```

5. Build and test:
```bash
docker-compose build my-new-service
docker-compose up my-new-service
curl http://localhost:8099/health
```

## Calling Other Services

### Calling Core Gateway (LLM):
```python
from shared.models.core_gateway import LLMRequest, Message, ModelType
import httpx

async def call_llm(prompt: str) -> str:
    request = LLMRequest(
        model=ModelType.GPT4_MINI,
        messages=[
            Message(role="system", content="You are a real estate assistant"),
            Message(role="user", content=prompt)
        ],
        max_tokens=500,
        temperature=0.7
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://core-gateway:8080/chat/completions",
            json=request.dict()
        )
        response.raise_for_status()
        data = response.json()
        return data["content"]
```

### Calling DB Gateway (Search):
```python
async def search_properties(query: str, limit: int = 10):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://db-gateway:8080/search",
            json={
                "query": query,
                "filters": {},
                "limit": limit
            }
        )
        response.raise_for_status()
        return response.json()["results"]
```

## Environment Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Required environment variables:
```bash
# Must set for OpenAI (or use Ollama for free)
OPENAI_API_KEY=sk-your-key-here

# Feature flags (Week 1: false, Week 2+: true)
USE_REAL_CORE_GATEWAY=false
USE_REAL_DB_GATEWAY=false

# JWT secret (change in production)
JWT_SECRET_KEY=your-secret-key-change-in-production
```

3. Optional monitoring:
```bash
# Sentry error tracking
SENTRY_DSN=https://your-sentry-dsn
```

## Common Workflows

### Adding New LLM Model Support
Edit `shared/models/core_gateway.py` and add to `ModelType` enum:
```python
class ModelType(str, Enum):
    OLLAMA_LLAMA2 = "ollama/llama2"
    GPT4_MINI = "gpt-4o-mini"
    NEW_MODEL = "provider/model-name"  # Add here
```

### Debugging Service Communication
1. Check Service Registry for registered services:
```bash
curl http://localhost:8000/services
```

2. Check service health individually:
```bash
curl http://localhost:8080/health  # Core Gateway
curl http://localhost:8081/health  # DB Gateway
```

3. View service logs:
```bash
docker-compose logs -f orchestrator
docker-compose logs -f core-gateway
```

### Running Services Without Docker
Services can run standalone for development:
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=sk-...
export REGISTRY_URL=http://localhost:8000

# Run service
cd services/semantic_chunking
python main.py
```

## Dependencies

Key Python packages (from `requirements.txt`):
- `fastapi==0.109.0` - Web framework
- `uvicorn[standard]==0.27.0` - ASGI server
- `langchain==0.1.6` - LLM framework
- `litellm==1.17.9` - LLM gateway
- `pydantic==2.5.3` - Data validation
- `httpx==0.26.0` - Async HTTP client
- `pytest==7.4.4` - Testing
- `sentry-sdk[fastapi]==1.40.0` - Error tracking

## Monitoring & Observability

- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Dashboards (port 3001, admin/admin)
- **Sentry**: Error tracking (configure SENTRY_DSN)
- All services expose `/health` and `/metrics` endpoints

## Documentation References

- **Quick Start**: `QUICKSTART_COMPLETE.md` - 5-minute setup
- **Framework Overview**: `COMPLETE_FRAMEWORK_SUMMARY.md`
- **Testing Guide**: `TESTING.md` - Comprehensive test documentation
- **Team Collaboration**: `docs/MVP_TEAM_COLLABORATION_GUIDE.md`
- **Service Example**: `services/semantic_chunking/README.md`
- **Project Structure**: `PROJECT_STRUCTURE.md` - File organization rules (READ THIS FIRST)
- **Refactoring Guide**: `REFACTORING_RECOMMENDATIONS.md` - Code improvement suggestions

## Troubleshooting

**Service won't start:**
1. Check Service Registry is running first: `docker-compose up service-registry`
2. Check logs: `docker-compose logs [service-name]`
3. Verify no port conflicts: `netstat -ano | findstr :[port]` (Windows) or `lsof -i :[port]` (Mac/Linux)

**Tests failing:**
1. Ensure services are healthy: `./scripts/run-tests.sh` handles this automatically
2. Wait 30 seconds after starting test environment
3. Check Service Registry: `curl http://localhost:8000/health`

**Service not registering:**
1. Verify Service Registry URL is accessible from container
2. Check service inherits from BaseService correctly
3. View registration logs in service output

## Code Quality & Refactoring

### File Organization Rules
**IMPORTANT:** Read `PROJECT_STRUCTURE.md` before creating new files.

**Key Rules:**
- ✅ Each service has ONLY ONE `main.py` (no `main_v2.py`, `main_old.py`)
- ✅ Use Git branches for experiments, not versioned files
- ✅ Documentation belongs in `docs/` or service `README.md`
- ❌ NEVER commit backup files, temp files, or sensitive data
- ❌ NEVER create duplicate documentation in root directory

### Refactoring Guidelines
See `REFACTORING_RECOMMENDATIONS.md` for detailed improvements including:
- Removing versioned files (`_v2.py`, `_old.py`)
- Consolidating duplicate documentation
- Improving error handling and retry logic
- Adding structured logging and monitoring
- Implementing caching and circuit breakers

### Before Creating New Files
1. Check if file type has designated location in `PROJECT_STRUCTURE.md`
2. Verify it's not duplicate documentation
3. Use proper naming conventions (snake_case for Python, lowercase-with-dashes for markdown)
4. Ensure it's not a temp file that should be gitignored

### When Refactoring Code
1. Create a Git branch: `git checkout -b feature/your-refactor`
2. Edit files directly (don't create `_v2` versions)
3. Test thoroughly: `pytest tests/`
4. Commit with clear message: `git commit -m "refactor: improve X"`
5. Merge or discard branch based on results

# REE AI Implementation: Open WebUI + LangChain Pipelines

## Overview

REE AI đã được triển khai với kiến trúc 7-layer hoàn chỉnh, tích hợp Open WebUI và LangChain pipelines theo file `docs/reference/REE AI-architecture.drawio.xml`.

## Architecture Implementation Status

### ✅ Completed Layers

#### Layer 0: Infrastructure
- **Service Registry** (Port 8000) - Service discovery và registration
- **BaseService Class** - Base class cho tất cả microservices với auto-registration

#### Layer 5: LLM Gateway
- **Core Gateway** (Port 8080) - LLM routing với LiteLLM
  - Hỗ trợ OpenAI (GPT-4, GPT-4o-mini, GPT-3.5-turbo)
  - Hỗ trợ Ollama (llama2, mistral, codellama) - Local, FREE
  - OpenAI-compatible API (`/chat/completions`, `/embeddings`)

#### Layer 2: Orchestration
- **Orchestrator** (Port 8090) - LangChain-powered intelligent routing
  - Intent detection sử dụng LangChain
  - Automatic service routing based on intent
  - OpenAI-compatible endpoint `/v1/chat/completions` cho Open WebUI
  - Hỗ trợ các intent: SEARCH, CHAT, CLASSIFY, EXTRACT, PRICE_SUGGEST, COMPARE, RECOMMEND

### 🏗️ Shared Infrastructure

#### Core Modules (`core/`)
- `base_service.py` - Base service class với:
  - Auto-registration with Service Registry
  - Standard health check endpoints
  - Graceful shutdown handling
  - Structured logging với emoji indicators
  - CORS middleware

- `service_registry.py` - Service registry models và client
  - ServiceInfo model
  - ServiceRegistryClient for service discovery

#### Shared Modules (`shared/`)

**Configuration (`shared/config.py`)**
- Feature flags (mock → real transition)
- Service URLs configuration
- LLM provider settings
- Database settings
- Settings singleton pattern

**Models (`shared/models/`)**
- `core_gateway.py` - LLM models (LLMRequest, LLMResponse, Message, ModelType)
- `db_gateway.py` - Database models (SearchRequest, PropertyResult, ConversationMessage)
- `orchestrator.py` - Orchestration models (OrchestrationRequest, IntentType, RoutingDecision)

**Utilities (`shared/utils/`)**
- `logger.py` - Structured logging với emoji constants

## Services Architecture Flow

```
┌────────────────────────────────────────────────────────────┐
│  Open WebUI (Layer 1) - http://localhost:3000              │
│  Frontend chat interface                                    │
└──────────────────────┬─────────────────────────────────────┘
                       │ HTTP: /v1/chat/completions
                       ↓
┌────────────────────────────────────────────────────────────┐
│  Orchestrator (Layer 2) - Port 8090                        │
│  • LangChain intent detection                              │
│  • Intelligent routing                                      │
│  • OpenAI-compatible API                                    │
└──────────────────────┬─────────────────────────────────────┘
                       │
         ┌─────────────┴──────────────┬──────────────────┐
         │                            │                  │
         ↓                            ↓                  ↓
┌─────────────────┐    ┌──────────────────┐   ┌─────────────────┐
│  Core Gateway   │    │  RAG Service     │   │  AI Services    │
│  (Layer 5)      │    │  (Layer 6)       │   │  (Layer 3)      │
│  Port 8080      │    │  Port 8091       │   │  Various ports  │
│                 │    │                  │   │                 │
│  • OpenAI API   │    │  • Retrieval     │   │  • Classification│
│  • Ollama API   │    │  • Context       │   │  • Semantic     │
│  • Embeddings   │    │  • Augmentation  │   │  • Extraction   │
└─────────────────┘    └──────────────────┘   └─────────────────┘
         │                      │                       │
         └──────────────────────┴───────────────────────┘
                                │
                                ↓
                    ┌────────────────────────┐
                    │  DB Gateway (Layer 4)   │
                    │  Port 8081              │
                    │  • PostgreSQL           │
                    │  • OpenSearch           │
                    │  • Redis                │
                    └────────────────────────┘
```

## Open WebUI Integration

### Configuration

Open WebUI đã được cấu hình trong `docker-compose.yml` để kết nối với Orchestrator:

```yaml
open-webui:
  build:
    context: ./frontend/open-webui
    dockerfile: Dockerfile
  ports:
    - "3000:8080"
  environment:
    # Point to Orchestrator (OpenAI-compatible endpoint)
    - OPENAI_API_BASE_URL=http://orchestrator:8080
    - OPENAI_API_KEY=dummy-key-not-needed
    - ENABLE_OLLAMA_API=false
    - ENABLE_OPENAI_API=true
    - WEBUI_NAME=REE AI - Real Estate Assistant
```

### Communication Flow

1. **User → Open WebUI**: User sends message through chat interface
2. **Open WebUI → Orchestrator**: Sends OpenAI-format request to `/v1/chat/completions`
3. **Orchestrator → Intent Detection**: Uses LangChain to detect intent
4. **Orchestrator → Service Routing**: Routes to appropriate service
5. **Service → Response**: Service processes and returns response
6. **Orchestrator → Open WebUI**: Returns OpenAI-format response
7. **Open WebUI → User**: Displays response in chat

## LangChain Integration

### 1. Orchestrator Intent Detection

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# LangChain LLM setup
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
    openai_api_key=settings.OPENAI_API_KEY
)

# Intent detection prompt
intent_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are an intent classifier..."),
    HumanMessage(content="{query}")
])

# Execute
response = await llm.ainvoke(prompt)
```

### 2. RAG Pipeline (Coming Soon)

RAG Service sẽ sử dụng LangChain components:
- `VectorStoreRetriever` - Retrieve từ OpenSearch
- `PromptTemplate` - Context augmentation
- `LLMChain` - Generation với context

## Getting Started

### Prerequisites

```bash
# 1. Clone repository
git clone <repo-url>
cd ree-ai

# 2. Setup environment
cp .env.example .env

# 3. Edit .env - Add your OpenAI API key
OPENAI_API_KEY=sk-your-key-here
```

### Running Services

```bash
# Start all services (without Open WebUI)
docker-compose --profile real up -d

# Services will start:
# - Service Registry (8000) - MUST START FIRST
# - Core Gateway (8080)
# - Orchestrator (8090)

# Check service health
curl http://localhost:8000/services  # See registered services
curl http://localhost:8080/health    # Core Gateway
curl http://localhost:8090/health    # Orchestrator
```

### Testing Orchestrator

```bash
# Test intent detection + routing
curl -X POST http://localhost:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "query": "Tìm nhà 2 phòng ngủ ở Quận 1",
    "conversation_id": "conv_123"
  }'

# Response:
# {
#   "intent": "search",
#   "confidence": 0.95,
#   "response": "...",
#   "service_used": "rag_service",
#   "execution_time_ms": 245.67
# }
```

### Testing with Open WebUI Format

```bash
# Test OpenAI-compatible endpoint (same format Open WebUI uses)
curl -X POST http://localhost:8090/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ree-ai-orchestrator",
    "messages": [
      {"role": "user", "content": "Xin chào, tôi muốn tìm nhà"}
    ]
  }'

# Response (OpenAI format):
# {
#   "id": "chatcmpl-1234567890",
#   "object": "chat.completion",
#   "model": "ree-ai-orchestrator",
#   "choices": [{
#     "message": {
#       "role": "assistant",
#       "content": "Xin chào! Tôi có thể giúp bạn tìm nhà..."
#     },
#     "finish_reason": "stop"
#   }]
# }
```

## Next Steps

### 🚧 Remaining Implementation

1. **DB Gateway (Layer 4)**
   - PostgreSQL connection
   - OpenSearch vector + BM25 search
   - Conversation storage

2. **RAG Service (Layer 6)**
   - Full LangChain RAG pipeline
   - Retrieval from OpenSearch
   - Context augmentation
   - Response generation

3. **AI Services (Layer 3)**
   - Classification service
   - Semantic chunking service
   - Attribute extraction
   - Price suggestion
   - Reranking

4. **Open WebUI Frontend**
   - Custom build from source
   - Custom CSS/branding
   - Custom models configuration

### Development Workflow

```bash
# 1. Create new service (copy template)
cp -r services/semantic_chunking services/my_service

# 2. Implement service logic in main.py
class MyService(BaseService):
    def __init__(self):
        super().__init__(
            name="my_service",
            version="1.0.0",
            capabilities=["my_capability"],
            port=8080
        )

    def setup_routes(self):
        @self.app.post("/my-endpoint")
        async def my_endpoint(request: MyRequest):
            # Your logic here
            return {"result": "data"}

# 3. Add to docker-compose.yml

# 4. Build and run
docker-compose build my-service
docker-compose up my-service

# 5. Test
curl http://localhost:8099/health
```

## Key Design Patterns

### 1. BaseService Pattern
All services inherit from `BaseService`:
- Auto-registration with Service Registry
- Standard endpoints (`/`, `/health`, `/info`)
- Graceful shutdown
- Structured logging

### 2. Feature Flags
Environment variables control mock vs real services:
```bash
USE_REAL_CORE_GATEWAY=false  # Week 1: use mocks
USE_REAL_CORE_GATEWAY=true   # Week 2+: use real
```

### 3. Type-Safe Models
Shared Pydantic models ensure API contract consistency:
```python
from shared.models.core_gateway import LLMRequest, Message

# All services use same models → No conflicts!
```

### 4. Service Discovery
Services register automatically on startup:
```python
# BaseService handles this automatically
service_info = ServiceInfo(
    name="my_service",
    capabilities=["search", "classify"]
)
await registry_client.register(service_info)
```

## Environment Variables

```bash
# Feature Flags
USE_REAL_CORE_GATEWAY=false
USE_REAL_DB_GATEWAY=false

# Service URLs
SERVICE_REGISTRY_URL=http://service-registry:8000
CORE_GATEWAY_URL=http://core-gateway:8080
DB_GATEWAY_URL=http://db-gateway:8080

# LLM Providers
OPENAI_API_KEY=sk-your-key-here
OLLAMA_BASE_URL=http://ollama:11434

# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ree_ai
POSTGRES_USER=ree_ai_user
POSTGRES_PASSWORD=ree_ai_pass_2025

# OpenSearch
OPENSEARCH_HOST=opensearch
OPENSEARCH_PORT=9200

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# General
DEBUG=true
LOG_LEVEL=INFO
```

## Troubleshooting

### Service Won't Start
```bash
# 1. Check Service Registry is running first
docker-compose ps service-registry

# 2. Check logs
docker-compose logs service-registry
docker-compose logs core-gateway
docker-compose logs orchestrator

# 3. Verify network
docker network ls | grep ree-ai
```

### Service Not Registering
```bash
# 1. Check Service Registry health
curl http://localhost:8000/health

# 2. Check registered services
curl http://localhost:8000/services

# 3. Check service logs for registration errors
docker-compose logs my-service
```

### LangChain Errors
```bash
# Verify OpenAI API key is set
echo $OPENAI_API_KEY

# Check Orchestrator can reach OpenAI
docker-compose exec orchestrator curl https://api.openai.com
```

## Testing

### Integration Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_orchestrator.py -v

# Run with coverage
pytest tests/ --cov=services --cov-report=html
```

### Manual Testing
```bash
# 1. Start services
docker-compose --profile real up -d

# 2. Wait for registration (30s)
sleep 30

# 3. Test Service Registry
curl http://localhost:8000/services

# 4. Test Core Gateway
curl -X POST http://localhost:8080/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'

# 5. Test Orchestrator
curl -X POST http://localhost:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test",
    "query": "Tìm nhà 2 phòng ngủ"
  }'
```

## Production Considerations

### 1. Service Registry
- Replace in-memory storage with Redis
- Add service health monitoring
- Implement automatic de-registration for dead services

### 2. Core Gateway
- Add rate limiting
- Implement request caching
- Add circuit breakers for LLM providers

### 3. Orchestrator
- Cache intent detection results
- Add fallback models
- Implement request queuing

### 4. Monitoring
- Add Prometheus metrics
- Setup Grafana dashboards
- Configure Sentry error tracking

### 5. Security
- Add JWT authentication
- Implement API key management
- Enable HTTPS
- Rate limiting per user

## Summary

### ✅ What's Implemented

1. **Core Infrastructure**
   - Service Registry with auto-registration
   - BaseService class with standard patterns
   - Shared models for type-safe communication
   - Configuration management with feature flags

2. **LLM Gateway (Layer 5)**
   - OpenAI integration
   - Ollama integration (local, free)
   - OpenAI-compatible API
   - Embeddings support

3. **Orchestrator (Layer 2)**
   - LangChain intent detection
   - Intelligent service routing
   - OpenAI-compatible endpoint for Open WebUI
   - Fallback mechanisms

4. **Docker Integration**
   - All services containerized
   - Docker Compose orchestration
   - Service profiles (mock, real, all)
   - Health checks

### 🚧 Next Steps

1. Implement DB Gateway (Layer 4)
2. Implement RAG Service (Layer 6)
3. Implement AI Services (Layer 3)
4. Setup Open WebUI frontend
5. Add comprehensive testing
6. Production hardening

### 🎯 Current Capabilities

- ✅ Basic chat via Orchestrator
- ✅ Intent detection
- ✅ Service discovery
- ✅ LLM routing (OpenAI + Ollama)
- ✅ OpenAI-compatible API for Open WebUI
- 🚧 Property search (pending RAG)
- 🚧 Property classification (pending service)
- 🚧 Vector search (pending DB Gateway)

## Contact & Support

For questions or issues:
1. Check service logs: `docker-compose logs [service-name]`
2. Verify service health: `curl http://localhost:[port]/health`
3. Check Service Registry: `curl http://localhost:8000/services`

---

**Version:** 1.0.0
**Last Updated:** 2025-10-30
**Status:** ✅ Core Infrastructure Complete, 🚧 Services In Progress

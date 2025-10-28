# 🚀 REE AI - Complete Quick Start Guide

Get the **complete framework** with all services up and running in **5 minutes**.

---

## 📋 What You Get

✅ **Open WebUI** - Modern chat interface (Layer 1)
✅ **Orchestrator** - LangChain-powered routing (Layer 2)
✅ **3 Sample Services** - Semantic Chunking, Classification (Layer 3)
✅ **RAG Service** - Full RAG pipeline with LangChain (Layer 6)
✅ **Core Gateway** - LLM routing (Ollama/OpenAI) (Layer 5)
✅ **DB Gateway** - Database operations (Layer 4)
✅ **Infrastructure** - Postgres, Redis, OpenSearch, Ollama
✅ **Mock Services** - Week 1 development

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Clone & Setup (1 minute)

```bash
# Clone repository
git clone <repository-url>
cd ree-ai

# Copy environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Windows: notepad .env
# Linux/Mac: nano .env
```

### Step 2: Start ALL Services (3 minutes)

```bash
# Start everything (infrastructure + all services)
docker-compose --profile real up -d

# Or just infrastructure + Open WebUI for Week 1
docker-compose up -d postgres redis opensearch ollama open-webui
```

**Wait for services (check status):**
```bash
docker-compose ps
```

Look for `healthy` status on all services.

### Step 3: Access Services (1 minute)

Open your browser:

**🌐 Open WebUI (Main Interface):**
```
http://localhost:3000
```
- Create account
- Start chatting
- Connected to Ollama (local LLM)

**📚 API Documentation:**
```
Core Gateway:     http://localhost:8080/docs
DB Gateway:       http://localhost:8081/docs
Semantic Chunking: http://localhost:8082/docs
Classification:    http://localhost:8083/docs
Orchestrator:      http://localhost:8090/docs
RAG Service:       http://localhost:8091/docs
```

---

## 🎯 Test Each Service

### 1. Test Core Gateway (LLM)

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ollama/llama2",
    "messages": [
      {"role": "user", "content": "Hello, what can you do?"}
    ]
  }'
```

**Expected:** JSON response with LLM-generated text

### 2. Test DB Gateway (Search)

```bash
curl -X POST http://localhost:8081/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm nhà 2 phòng ngủ",
    "filters": {"region": "Quận 1"},
    "limit": 5
  }'
```

**Expected:** List of 5 properties

### 3. Test Semantic Chunking (Layer 3)

```bash
curl -X POST http://localhost:8082/chunk \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Căn hộ 2 phòng ngủ ở Quận 1, diện tích 75m2, giá 8 tỷ",
    "max_chunk_size": 500
  }'
```

**Expected:** Text split into semantic chunks

### 4. Test Classification (Layer 3)

```bash
curl -X POST http://localhost:8083/classify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Căn hộ 2 phòng ngủ view đẹp"
  }'
```

**Expected:** `{"property_type": "apartment", "confidence": 0.95, ...}`

### 5. Test RAG Service (Layer 6)

```bash
curl -X POST http://localhost:8091/rag \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm nhà 2 phòng ngủ ở Quận 1 giá khoảng 8 tỷ",
    "user_id": "user_123",
    "conversation_id": "conv_456"
  }'
```

**Expected:** AI-generated answer with property recommendations

### 6. Test Orchestrator (Layer 2)

```bash
curl -X POST http://localhost:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "query": "Tìm nhà 2 phòng ngủ ở Quận 1"
  }'
```

**Expected:** Orchestrator routes to appropriate service and returns result

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  USER (Browser)                                          │
│  http://localhost:3000 (Open WebUI) ✅                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: Orchestrator (LangChain) ✅                   │
│  http://localhost:8090                                   │
│  • Routes requests to services                           │
│  • Intent detection                                      │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: AI Services                                    │
│  • Semantic Chunking    :8082 ✅                        │
│  • Classification       :8083 ✅                        │
│  • Attribute Extraction :8084 (TODO)                     │
│  • Completeness         :8085 (TODO)                     │
│  • Price Suggestion     :8086 (TODO)                     │
│  • Rerank               :8087 (TODO)                     │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌──────────────┬─────────────┬─────────────────────────────┐
│              │             │                             │
│  LAYER 4:    │  LAYER 6:   │  LAYER 5:                   │
│  Storage ✅  │  RAG ✅     │  Core Gateway ✅            │
│              │             │                             │
│  :8081       │  :8091      │  :8080                      │
│  • DB GW     │  • Retrieval│  • LiteLLM                  │
│  • Postgres  │  • Context  │  • Ollama :11434            │
│  • OpenSearch│  • Augment  │  • OpenAI API               │
│  • Redis     │  • Generate │                             │
└──────────────┴─────────────┴─────────────────────────────┘
```

---

## 🛠️ Development Workflow

### Week 1: Develop with Mocks

```bash
# Start infrastructure + mocks only
docker-compose --profile mock up -d postgres redis opensearch ollama mock-core-gateway mock-db-gateway

# Your service automatically calls mocks
# No need to wait for other teams!

# Develop your service
cd services/your_service
# Edit main.py
```

### Week 2: Switch to Real Services

```bash
# In .env file, change:
USE_REAL_CORE_GATEWAY=true
USE_REAL_DB_GATEWAY=true

# Restart services
docker-compose restart your-service

# Now calling REAL gateways!
```

---

## 📚 All Available Services

| Service | Port | Status | Description |
|---------|------|--------|-------------|
| **Open WebUI** | 3000 | ✅ Ready | Chat interface (Layer 1) |
| **Orchestrator** | 8090 | ✅ Ready | LangChain routing (Layer 2) |
| **Semantic Chunking** | 8082 | ✅ Ready | Text chunking (Layer 3) |
| **Classification** | 8083 | ✅ Ready | Property classification (Layer 3) |
| **RAG Service** | 8091 | ✅ Ready | Full RAG pipeline (Layer 6) |
| **Core Gateway** | 8080 | ✅ Ready | LLM routing (Layer 5) |
| **DB Gateway** | 8081 | ✅ Ready | Database ops (Layer 4) |
| **PostgreSQL** | 5432 | ✅ Ready | Relational DB |
| **Redis** | 6379 | ✅ Ready | Cache |
| **OpenSearch** | 9200 | ✅ Ready | Vector + BM25 search |
| **Ollama** | 11434 | ✅ Ready | Local LLM |

### Services You Can Copy (Templates)

1. **Semantic Chunking** (`services/semantic_chunking/`) - Simple service calling Core Gateway
2. **Classification** (`services/classification/`) - LangChain prompt template usage
3. **RAG Service** (`services/rag_service/`) - Full RAG pipeline with multiple gateways

---

## 🎓 How to Add Your Service

### Step 1: Copy Template

```bash
# Copy one of the sample services
cp -r services/semantic_chunking services/your_service_name

# Or classification for LangChain example
cp -r services/classification services/your_service_name
```

### Step 2: Edit Service

```python
# services/your_service_name/main.py

from shared.models.core_gateway import LLMRequest, Message
from shared.config import feature_flags
from shared.utils.logger import setup_logger

# Your service logic here
@app.post("/your-endpoint")
async def your_function(request: YourRequest):
    # Call Core Gateway
    llm_response = await core_gateway.call_llm(...)

    # Process response
    result = process(llm_response.content)

    return YourResponse(...)
```

### Step 3: Add to Docker Compose

```yaml
# docker-compose.yml
services:
  your-service:
    build:
      context: .
      dockerfile: services/your_service_name/Dockerfile
    environment:
      - USE_REAL_CORE_GATEWAY=${USE_REAL_CORE_GATEWAY:-false}
    ports:
      - "8088:8080"  # Choose unused port
    depends_on:
      - core-gateway
    networks:
      - ree-ai-network
    profiles:
      - real
      - all
```

### Step 4: Build & Test

```bash
# Build
docker-compose build your-service

# Run
docker-compose up your-service

# Test
curl http://localhost:8088/health
```

---

## ❓ Troubleshooting

### Issue: Services won't start

```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs -f

# Restart specific service
docker-compose restart core-gateway
```

### Issue: Port already in use

```bash
# Find what's using the port (Windows)
netstat -ano | findstr :8080

# Find what's using the port (Linux/Mac)
lsof -i :8080

# Change port in docker-compose.yml
ports:
  - "8888:8080"  # Use different external port
```

### Issue: Ollama model not found

```bash
# Pull llama2 model
docker exec -it ree-ai-ollama ollama pull llama2

# Or pull llama3
docker exec -it ree-ai-ollama ollama pull llama3

# List available models
docker exec -it ree-ai-ollama ollama list
```

### Issue: OpenAI API key not working

```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Should see: OPENAI_API_KEY=sk-...

# Restart services after changing .env
docker-compose restart core-gateway
```

---

## 🎉 Success Checklist

After following this guide, you should have:

- [x] All infrastructure running (Postgres, Redis, OpenSearch, Ollama)
- [x] Open WebUI accessible at http://localhost:3000
- [x] Core Gateway responding at :8080
- [x] DB Gateway responding at :8081
- [x] 2 sample Layer 3 services (Semantic Chunking :8082, Classification :8083)
- [x] RAG Service responding at :8091
- [x] Orchestrator responding at :8090
- [x] All health checks returning 200 OK
- [x] Can test services via curl or API docs

---

## 🚀 Next Steps

### For Developers

1. **Read sample services:**
   - `services/semantic_chunking/main.py` - Simple service
   - `services/classification/main.py` - LangChain usage
   - `services/rag_service/main.py` - Full RAG pipeline

2. **Copy template for your service**

3. **Implement your logic**

4. **Test with mocks** (Week 1)

5. **Switch to real services** (Week 2)

### For Team Leads

1. **Review architecture:** `docs/MVP_TEAM_COLLABORATION_GUIDE.md`

2. **Assign services to teams:**
   - Team 1: Attribute Extraction (copy semantic_chunking)
   - Team 2: Completeness (copy classification)
   - Team 3: Price Suggestion (copy rag_service)
   - Team 4: Rerank (copy classification)

3. **Setup feature flags for gradual integration**

---

## 📞 Resources

- **Framework Docs:** `README_FRAMEWORK.md`
- **Team Guide:** `docs/MVP_TEAM_COLLABORATION_GUIDE.md`
- **Sample Service Guide:** `services/semantic_chunking/README.md`
- **Architecture:** `docs/CTO_EXECUTIVE_SUMMARY.md`

---

## ✅ Summary

You now have a **complete, working framework** with:

✅ **6 Layers** - From UI to LLM to Storage
✅ **10+ Services** - Infrastructure + core services + samples
✅ **LangChain Integration** - Orchestrator + RAG
✅ **Open WebUI** - Modern chat interface
✅ **Mock Services** - Week 1 development
✅ **Feature Flags** - Gradual integration
✅ **3 Sample Services** - Templates to copy

**Everything tested and ready to use! 🚀**

---

**Start developing:** Copy a sample service, implement your logic, test with mocks!

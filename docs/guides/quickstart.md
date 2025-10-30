# 🚀 REE AI - Quick Start Guide

Get the complete framework up and running in **5 minutes**.

---

## 📋 Prerequisites

- Docker Desktop installed and running
- Git
- Text editor (VS Code recommended)
- OpenAI API key (optional for Week 1)

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Clone & Setup (1 minute)

```bash
# Clone repository
git clone <repository-url>
cd ree-ai

# Copy environment file
cp .env.example .env

# Edit .env and add your OpenAI API key (optional for Week 1)
# nano .env  # or use your editor
```

### Step 2: Start Mock Services (2 minutes)

```bash
# Windows
docker-compose --profile mock up -d postgres redis opensearch mock-core-gateway mock-db-gateway

# Linux/Mac (or use Makefile)
make start-mock
```

**Wait for services to start (check logs):**
```bash
docker-compose logs -f
```

Look for these messages:
- ✅ `postgres` - "database system is ready to accept connections"
- ✅ `redis` - "Ready to accept connections"
- ✅ `mock-core-gateway` - "Started on port 1080"
- ✅ `mock-db-gateway` - "Started on port 1080"

### Step 3: Test Mock Services (1 minute)

```bash
# Test Mock Core Gateway
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Test Mock DB Gateway
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm nhà 2 phòng ngủ",
    "filters": {"region": "Quận 1"},
    "limit": 10
  }'
```

**Expected: Both return mock JSON responses**

### Step 4: Your First Service (1 minute)

```bash
# Start developing your service
cd services/semantic_chunking

# Read the sample implementation
cat main.py

# Build and run
cd ../..
docker-compose --profile real up semantic-chunking
```

**Boom! You're ready to develop! 🎉**

---

## 📚 What You Just Set Up

### Mock Services (Week 1)

```
┌─────────────────────────────────────┐
│   MOCK INFRASTRUCTURE READY         │
├─────────────────────────────────────┤
│ ✅ PostgreSQL       (port 5432)     │
│ ✅ Redis            (port 6379)     │
│ ✅ OpenSearch       (port 9200)     │
│ ✅ Mock Core GW     (port 8000)     │
│ ✅ Mock DB GW       (port 8001)     │
└─────────────────────────────────────┘
```

**Now ALL dev teams can work in parallel!**

---

## 🛠️ Development Workflow

### Week 1: Develop with Mocks

```bash
# Terminal 1: Keep infrastructure running
make start-mock

# Terminal 2: Develop your service
cd services/your_service
# Edit main.py
# Your service calls mock-core-gateway automatically

# Terminal 3: Test your service
curl -X POST http://localhost:YOUR_PORT/your-endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'
```

### Week 2: Switch to Real Services

```bash
# In .env, change:
USE_REAL_CORE_GATEWAY=true
USE_REAL_DB_GATEWAY=true

# Restart your service
docker-compose restart your-service

# Now your service calls REAL Core Gateway!
```

---

## 🎯 Common Tasks

### View API Documentation

```bash
# Start real services
make start-real

# Open in browser:
http://localhost:8080/docs  # Core Gateway
http://localhost:8081/docs  # DB Gateway
http://localhost:8082/docs  # Semantic Chunking (sample)
```

### Check Service Health

```bash
# Core Gateway
curl http://localhost:8080/health

# DB Gateway
curl http://localhost:8081/health

# Semantic Chunking
curl http://localhost:8082/health
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f core-gateway

# Or use Makefile
make logs
```

### Run Tests

```bash
# All tests
make test

# Specific service
make test-core      # Core Gateway
make test-db        # DB Gateway
make test-semantic  # Semantic Chunking
```

### Stop Everything

```bash
# Stop services (keep data)
make stop

# Stop and delete all data
make clean
```

---

## 🧩 Project Structure

```
ree-ai/
├── .env                    # Configuration (create from .env.example)
├── docker-compose.yml      # All services definition
├── Makefile               # Quick commands
│
├── shared/                # Shared code (ALL teams use this)
│   ├── models/           # Pydantic models
│   │   ├── core_gateway.py
│   │   ├── db_gateway.py
│   │   └── orchestrator.py
│   ├── config.py         # Settings + feature flags
│   └── utils/            # Logging, etc.
│
├── services/             # Each team's service
│   ├── core_gateway/    # Layer 5 - LLM gateway
│   ├── db_gateway/      # Layer 4 - DB gateway
│   └── semantic_chunking/  # Layer 3 - Sample service ⭐
│
├── mocks/                # Mock server configs
│   ├── core_gateway_mock.json
│   └── db_gateway_mock.json
│
└── tests/                # Integration tests
    ├── test_core_gateway.py
    ├── test_db_gateway.py
    └── test_semantic_chunking.py
```

---

## 🎓 Next Steps

### For Dev Teams

1. **Read the sample service:**
   ```bash
   cat services/semantic_chunking/README.md
   ```

2. **Copy template for your service:**
   ```bash
   cp -r services/semantic_chunking services/your_service_name
   ```

3. **Implement your logic:**
   - Edit `main.py`
   - Use `shared/models` for API contracts
   - Call Core Gateway via `CoreGatewayClient`
   - Add to `docker-compose.yml`

4. **Test:**
   ```bash
   docker-compose up your-service-name
   curl http://localhost:YOUR_PORT/health
   ```

### For Tech Leads

1. **Review architecture:**
   ```bash
   cat docs/MVP_TEAM_COLLABORATION_GUIDE.md
   ```

2. **Setup team assignments:**
   - Team 1: Core Gateway ✅ (already implemented)
   - Team 2: DB Gateway ✅ (already implemented)
   - Team 3: Orchestrator (TODO)
   - Teams 4-9: Layer 3 services (use semantic_chunking as template)

3. **Define OpenAPI contracts:**
   ```bash
   # Add contracts for each service in contracts/
   ```

---

## ❓ Troubleshooting

### Issue: Docker services won't start

```bash
# Check Docker is running
docker ps

# Check for port conflicts
netstat -an | grep 8080

# View error logs
docker-compose logs
```

### Issue: Mock services return 404

```bash
# Ensure mock profile is active
docker-compose --profile mock ps

# Restart mocks
docker-compose --profile mock restart mock-core-gateway mock-db-gateway
```

### Issue: Can't connect to Core Gateway from service

```bash
# Check network
docker network ls | grep ree-ai

# Verify all services on same network
docker network inspect ree-ai-network

# Check feature flag
echo $USE_REAL_CORE_GATEWAY  # Should be true or false
```

### Issue: Import error - "No module named 'shared'"

```bash
# Check PYTHONPATH in Dockerfile
grep PYTHONPATH services/your_service/Dockerfile

# Should have: ENV PYTHONPATH=/app

# Rebuild image
docker-compose build your-service
```

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│  USER (Browser)                                          │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Open WebUI (TODO)                             │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: Orchestrator (TODO)                           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: AI Services                                    │
│  ✅ Semantic Chunking (SAMPLE - Implemented)            │
│  ⏳ Classification (TODO - Use template)                │
│  ⏳ Attribute Extraction (TODO)                          │
│  ⏳ Completeness (TODO)                                  │
│  ⏳ Price Suggestion (TODO)                              │
│  ⏳ Rerank (TODO)                                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌──────────────┬─────────────┬─────────────────────────────┐
│              │             │                             │
│  LAYER 4:    │  LAYER 6:   │  LAYER 5:                   │
│  Storage     │  RAG        │  Core Gateway               │
│              │  (TODO)     │  ✅ Implemented             │
│  ✅ DB GW    │             │                             │
│  ✅ Postgres │             │  • LiteLLM                  │
│  ✅ OpenSrch │             │  • Ollama/OpenAI routing    │
│  ✅ Redis    │             │                             │
└──────────────┴─────────────┴─────────────────────────────┘
```

---

## ✅ Checklist

### Week 1 Setup (You Just Did This!)

- [x] Clone repository
- [x] Create .env file
- [x] Start infrastructure (Postgres, Redis, OpenSearch)
- [x] Start mock services (Mock Core Gateway, Mock DB Gateway)
- [x] Test mock endpoints
- [x] Understand project structure

### Your Next Tasks

- [ ] Read `services/semantic_chunking/README.md`
- [ ] Copy semantic_chunking template for your service
- [ ] Implement your service logic
- [ ] Add your service to docker-compose.yml
- [ ] Test your service with mocks
- [ ] Write unit tests
- [ ] Document your API

---

## 🎉 You're Ready!

All infrastructure is set up. You have:

✅ **Mock services** - No blocking, develop immediately
✅ **Sample service** - Template to copy
✅ **Shared models** - Type-safe API contracts
✅ **Feature flags** - Easy mock → real transition
✅ **Docker Compose** - One command to run everything
✅ **Tests** - Examples to follow

**Now go build amazing AI services! 🚀**

---

## 📞 Get Help

- **Sample service:** `services/semantic_chunking/README.md`
- **Team guide:** `docs/MVP_TEAM_COLLABORATION_GUIDE.md`
- **Architecture:** `docs/CTO_EXECUTIVE_SUMMARY.md`

**Happy coding! 💻**

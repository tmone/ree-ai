# GitHub Actions Deployment Strategy

## 🎯 Deployment Strategy

Chúng ta có 2 môi trường deployment tách biệt:

### 📊 Deployment Flow

```
Developer Code → main branch → WSL Test → release branch → Production Server
```

### 🏗️ Environments

| Branch | Environment | Location | Purpose | URL |
|--------|-------------|----------|---------|-----|
| `main` | WSL Test | Local WSL | Test & Debug | http://localhost:4000 |
| `release` | Production | 192.168.1.11 | Live Server | http://192.168.1.11:3000 |

---

## 🔧 Workflow Files

### 1. WSL Test Environment
**File**: `.github/workflows/deploy-test.yml`
- **Trigger**: Push to `main` branch
- **Purpose**: Test và fix lỗi trước khi deploy production
- **Location**: WSL (self-hosted runner)
- **Ports**: Test ports (4000, 9080, 9090, etc.)

### 2. Production Environment  
**File**: `.github/workflows/deploy-production.yml`
- **Trigger**: Push to `release` branch
- **Purpose**: Deploy stable code lên server chính thức
- **Location**: Remote server (192.168.1.11)
- **Ports**: Standard ports (3000, 8080, 8090, etc.)

---

## 🚀 Usage Workflow

### Step 1: Development & Testing
```bash
# Develop và commit code
git add .
git commit -m "Add new feature"
git push origin main
```
→ **Tự động deploy lên WSL** (http://localhost:4000)
→ **Test và fix bugs**

### Step 2: Production Release
```bash
# Khi code đã stable trên WSL
git checkout release
git merge main
git push origin release
```
→ **Tự động deploy lên Production** (http://192.168.1.11:3000)

---

## 🏥 Health Checks

### WSL Test Environment
```bash
# Frontend
curl http://localhost:4000

# API Services
curl http://localhost:9080/health  # Core Gateway
curl http://localhost:9090/health  # Orchestrator
curl http://localhost:9091/health  # RAG Service
```

### Production Environment
```bash
# Frontend
curl http://192.168.1.11:3000

# API Services  
curl http://192.168.1.11:8080/health  # Core Gateway
curl http://192.168.1.11:8090/health  # Orchestrator
curl http://192.168.1.11:8091/health  # RAG Service
```

---

## 🔐 Required Secrets

Cần setup trong GitHub Repository Secrets:

| Secret Name | Value | Usage |
|-------------|--------|-------|
| `PRODUCTION_SSH_KEY` | SSH private key | Connect to 192.168.1.11 |
| `OPENAI_API_KEY` | OpenAI API key | Both environments |

---

## 🎮 Manual Deployment

### Deploy to WSL (Test)
```bash
# Via GitHub UI
Actions → Deploy to WSL Test Environment → Run workflow
```

### Deploy to Production
```bash
# Via GitHub UI  
Actions → Deploy to Production Server → Run workflow
# Input "PRODUCTION" to confirm
```

---

## 📊 Port Mapping

### WSL Test Environment
```
PostgreSQL:    5433 (vs 5432 production)
Redis:         6380 (vs 6379 production) 
OpenSearch:    9201 (vs 9200 production)
Open WebUI:    4000 (vs 3000 production)
Core Gateway:  9080 (vs 8080 production)
Orchestrator:  9090 (vs 8090 production)
RAG Service:   9091 (vs 8091 production)
```

### Production Environment
```
PostgreSQL:    5432
Redis:         6379
OpenSearch:    9200
Open WebUI:    3000
Core Gateway:  8080  
Orchestrator:  8090
RAG Service:   8091
```

---

## 🔄 Branching Strategy

### main branch
- **Purpose**: Development và testing
- **Stability**: Có thể có bugs
- **Deployment**: WSL Test Environment
- **Audience**: Developers

### release branch  
- **Purpose**: Production releases
- **Stability**: Stable, tested code
- **Deployment**: Production Server
- **Audience**: End users

---

## 🛠️ Troubleshooting

### WSL Test Issues
```bash
# Check WSL services
wsl
cd /home/tmone/ree-ai-test
./status-ree-ai.sh
./logs-ree-ai.sh
```

### Production Issues
```bash
# Check production services
ssh tmone@192.168.1.11
cd ~/ree-ai
./status-ree-ai.sh
./logs-ree-ai.sh
```

### GitHub Actions Issues
1. Check Actions tab in GitHub
2. Review workflow logs
3. Check secrets configuration
4. Verify SSH connectivity

---

## ✅ Benefits

1. **Safe Testing**: Bugs được catch ở WSL trước khi lên production
2. **Zero Downtime**: Production chỉ deploy code đã stable
3. **Easy Rollback**: Có thể revert release branch nếu cần
4. **Clear Separation**: Test và production hoàn toàn tách biệt
5. **Automated Pipeline**: Push code → auto deploy

---

**🎯 Summary**: 
- Code mới → `main` → WSL test → fix bugs → `release` → Production ✅
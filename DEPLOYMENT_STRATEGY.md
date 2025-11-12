# 🚀 REE AI - GitHub Actions Deployment Strategy

## 🎯 Deployment Strategy

Chúng ta sử dụng **2-stage deployment** với 2 nhánh:

```
🔄 Developer Workflow:
Code → main branch → WSL Test → release branch → Production Server
```

### 📊 Environments

| Branch | Environment | Location | Purpose | URL |
|--------|-------------|----------|---------|-----|
| `main` | **WSL Test** | Local WSL | Test & Debug | http://localhost:4000 |
| `release` | **Production** | 192.168.1.11 | Live Server | http://192.168.1.11:3000 |

---

## 🔧 Workflow Files

### 1. WSL Test Environment
- **File**: `.github/workflows/deploy-test.yml`
- **Trigger**: Push to `main` branch  
- **Purpose**: Tự động deploy lên WSL để test
- **Ports**: 4000, 9080, 9090, 9091 (tránh conflict với production)

### 2. Production Environment
- **File**: `.github/workflows/deploy-production.yml` 
- **Trigger**: Push to `release` branch
- **Purpose**: Deploy stable code lên server chính thức
- **Ports**: 3000, 8080, 8090, 8091 (standard ports)

---

## 🚀 Usage Guide

### Step 1: Development (main branch)
```bash
# Develop new features
git add .
git commit -m "Add new feature" 
git push origin main
```
→ **Tự động deploy lên WSL** (http://localhost:4000)
→ **Test và fix bugs**

### Step 2: Production Release (release branch)  
```bash
# Khi code đã stable trên WSL
git checkout release
git merge main
git push origin release
```
→ **Tự động deploy lên Production** (http://192.168.1.11:3000)

---

## ⚡ Setup Instructions

### Bước 1: Chuẩn bị Production Server
```bash
# SSH vào server production
ssh tmone@192.168.1.11

# Download và chạy setup script
curl -sSL https://raw.githubusercontent.com/tmone/ree-ai/main/scripts/setup-production-server.sh -o setup.sh
chmod +x setup.sh
./setup.sh
```

### Bước 2: Tạo SSH Keys cho GitHub Actions
```bash
# Windows
scripts\setup-github-actions-ssh.bat

# Linux/Mac
scripts/setup-github-actions-ssh.sh
```

### Bước 3: Cấu hình GitHub Secrets
Vào: `https://github.com/tmone/ree-ai/settings/secrets/actions`

| Secret Name | Value | Description |
|-------------|--------|-------------|
| `PRODUCTION_SSH_KEY` | SSH private key | Để kết nối server 192.168.1.11 |
| `OPENAI_API_KEY` | OpenAI API key | Cho cả WSL và Production |

### Bước 4: Tạo Release Branch
```bash
git checkout -b release
git push -u origin release
```

---

## 🎮 Daily Workflow

### 🧪 Testing Phase (main branch)
```bash
# 1. Develop code
git checkout main
# ... code changes ...
git add .
git commit -m "Feature update"
git push origin main

# 2. Auto deploy to WSL
# → Check http://localhost:4000
# → Test functionality  
# → Fix any bugs

# 3. Repeat until stable
```

### 🚀 Production Release (release branch)
```bash
# 4. When WSL testing is complete
git checkout release
git merge main
git push origin release

# 5. Auto deploy to Production
# → Live at http://192.168.1.11:3000
```

---

## 🏥 Health Checks

### WSL Test Environment
```bash
curl http://localhost:4000              # Frontend
curl http://localhost:9080/health       # Core Gateway  
curl http://localhost:9090/health       # Orchestrator
curl http://localhost:9091/health       # RAG Service
```

### Production Environment
```bash
curl http://192.168.1.11:3000          # Frontend
curl http://192.168.1.11:8080/health   # Core Gateway
curl http://192.168.1.11:8090/health   # Orchestrator  
curl http://192.168.1.11:8091/health   # RAG Service
```

---

## 📊 Port Mappings

### WSL Test (main → localhost)
```
Database:      5433, 6380, 9201
Frontend:      4000  
API Gateway:   9080
Orchestrator:  9090
RAG Service:   9091
Admin:         4002
```

### Production (release → 192.168.1.11)
```
Database:      5432, 6379, 9200
Frontend:      3000
API Gateway:   8080  
Orchestrator:  8090
RAG Service:   8091
Admin:         3002
```

---

## 🔍 Troubleshooting

### WSL Issues
```bash
# Check WSL services
wsl
cd /home/tmone/ree-ai-test
docker-compose -f docker-compose.yml -f docker-compose.test.yml ps
docker-compose -f docker-compose.yml -f docker-compose.test.yml logs
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
1. Check **Actions** tab trong GitHub repository
2. Review workflow logs để tìm lỗi
3. Kiểm tra GitHub Secrets đã setup đúng chưa
4. Test SSH connection: `ssh -i ~/.ssh/github-actions-ree-ai tmone@192.168.1.11`

---

## ✅ Benefits của Strategy này

1. **🛡️ Safe Testing**: Tất cả bugs được catch ở WSL trước
2. **🚀 Zero Downtime**: Production chỉ nhận stable code
3. **🔄 Easy Rollback**: Có thể revert release branch
4. **🎯 Clear Separation**: WSL test ≠ Production 
5. **⚡ Automated**: Không cần deploy manual

---

## 🎉 Summary

**Current Setup:**
- ✅ 2 GitHub workflows created
- ✅ WSL test environment (main branch)
- ✅ Production environment (release branch)  
- ✅ Separate ports to avoid conflicts
- ✅ Automated deployment pipeline

**Next Steps:**
1. Push code to `main` → Test on WSL
2. When stable, merge `main` → `release` → Deploy Production
3. Monitor both environments
4. Iterate and improve

**🚀 Happy coding with safe deployments!**
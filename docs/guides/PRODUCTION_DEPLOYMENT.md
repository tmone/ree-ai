# REE AI - Production Deployment Guide

Hướng dẫn deploy REE AI lên server production với GitHub Actions.

## 📋 Thông tin Server

- **IP**: 192.168.1.11  
- **User**: tmone
- **Password**: 1
- **OS**: Ubuntu/Linux

## 🚀 Cài đặt nhanh (3 bước)

### Bước 1: Chuẩn bị Server Production

```bash
# 1. SSH vào server
ssh tmone@192.168.1.11

# 2. Tải script cài đặt
curl -sSL https://raw.githubusercontent.com/tmone/ree-ai/main/scripts/setup-production-server.sh -o setup.sh

# 3. Chạy script cài đặt
chmod +x setup.sh
./setup.sh
```

Script sẽ tự động:
- ✅ Cài đặt Docker & Docker Compose
- ✅ Cấu hình tường lửa
- ✅ Tạo thư mục dự án
- ✅ Clone repository
- ✅ Tạo systemd service
- ✅ Cài đặt các script quản lý

### Bước 2: Cấu hình SSH cho GitHub Actions

```bash
# Trên máy local (Windows/Linux/Mac)
# Chạy script thiết lập SSH
./scripts/setup-github-actions-ssh.sh    # Linux/Mac
# hoặc
./scripts/setup-github-actions-ssh.bat   # Windows
```

Script sẽ:
- 🔐 Tạo SSH key pair
- 📋 Hiển thị public key để copy lên server
- 📝 Hiển thị private key để thêm vào GitHub Secrets

### Bước 3: Cấu hình GitHub Secrets

1. Vào GitHub repository settings:
   ```
   https://github.com/tmone/ree-ai/settings/secrets/actions
   ```

2. Thêm các secrets sau:

   | Secret Name | Value | Mô tả |
   |-------------|--------|-------|
   | `PRODUCTION_SSH_KEY` | Private key từ script | SSH key để kết nối server |
   | `OPENAI_API_KEY` | sk-xxx... | API key của OpenAI (bắt buộc) |

## 🎯 Deploy Tự động

Sau khi cài đặt xong, mỗi khi push code lên `main` branch:

```bash
git add .
git commit -m "Update features"
git push origin main
```

GitHub Actions sẽ **tự động deploy** lên server production!

## 🌐 Truy cập Ứng dụng

Sau khi deploy thành công:

| Service | URL | Mô tả |
|---------|-----|-------|
| **Open WebUI** | http://192.168.1.11:3000 | Giao diện chat chính |
| **Core Gateway** | http://192.168.1.11:8080 | API Gateway |
| **Orchestrator** | http://192.168.1.11:8090 | AI Router |
| **RAG Service** | http://192.168.1.11:8091 | RAG Engine |
| **Admin Dashboard** | http://192.168.1.11:3002 | Quản trị hệ thống |

## 🎮 Quản lý Server

SSH vào server và sử dụng các lệnh:

```bash
# Kiểm tra trạng thái
./status-ree-ai.sh

# Khởi động dịch vụ  
./start-ree-ai.sh

# Dừng dịch vụ
./stop-ree-ai.sh

# Xem logs
./logs-ree-ai.sh

# Backup dữ liệu
./backup-data.sh
```

## 🔧 Cấu hình nâng cao

### Chỉnh sửa Environment Variables

```bash
# SSH vào server
ssh tmone@192.168.1.11
cd ~/ree-ai

# Chỉnh sửa .env
nano .env

# Restart services
./stop-ree-ai.sh
./start-ree-ai.sh
```

### Xem logs chi tiết

```bash
# Xem logs tất cả services
./logs-ree-ai.sh

# Xem logs một service cụ thể
./logs-ree-ai.sh orchestrator
./logs-ree-ai.sh open-webui
./logs-ree-ai.sh rag-service
```

### Quản lý với systemd

```bash
# Khởi động REE AI khi boot
sudo systemctl enable ree-ai

# Kiểm tra trạng thái service
sudo systemctl status ree-ai

# Khởi động/dừng service
sudo systemctl start ree-ai
sudo systemctl stop ree-ai
```

## 🔍 Troubleshooting

### 1. GitHub Actions thất bại

```bash
# Kiểm tra SSH connection
ssh -i ~/.ssh/github-actions-ree-ai tmone@192.168.1.11 'echo "SSH OK"'

# Kiểm tra Docker
ssh tmone@192.168.1.11 'docker --version'
```

### 2. Services không khởi động

```bash
# SSH vào server
ssh tmone@192.168.1.11
cd ~/ree-ai

# Xem lỗi cụ thể
docker-compose logs

# Kiểm tra ports
sudo netstat -tulpn | grep -E '(3000|8080|8090|8091)'
```

### 3. Không truy cập được web

```bash
# Kiểm tra firewall
sudo ufw status

# Kiểm tra Open WebUI
curl http://localhost:3000
```

### 4. Khởi động lại từ đầu

```bash
# SSH vào server
ssh tmone@192.168.1.11
cd ~/ree-ai

# Dọn dẹp hoàn toàn
./stop-ree-ai.sh
docker system prune -af
docker volume prune -f

# Khởi động lại
./start-ree-ai.sh
```

## 📊 Monitoring

### Kiểm tra tài nguyên hệ thống

```bash
# CPU và RAM
htop

# Disk usage
df -h

# Docker stats
docker stats

# Container health
docker-compose ps
```

### Health checks

```bash
# Frontend
curl http://192.168.1.11:3000

# API Gateway  
curl http://192.168.1.11:8080/health

# Orchestrator
curl http://192.168.1.11:8090/health

# RAG Service
curl http://192.168.1.11:8091/health
```

## 🔒 Security

### Firewall Configuration

Script tự động mở các ports sau:

```
Port 22    - SSH
Port 3000  - Open WebUI  
Port 8000  - Service Registry
Port 8080  - Core Gateway
Port 8081  - DB Gateway
Port 8090  - Orchestrator  
Port 8091  - RAG Service
Port 3002  - Admin Dashboard
Port 9200  - OpenSearch
Port 5432  - PostgreSQL
Port 6379  - Redis
```

### SSH Security

- ✅ SSH key authentication (không dùng password)
- ✅ Firewall configured
- ✅ Fail2ban installed

## 🚀 Workflow GitHub Actions

File workflow: `.github/workflows/deploy-production.yml`

**Trigger**: Push to `main` branch hoặc manual dispatch

**Các bước**:
1. Checkout code
2. Setup SSH connection
3. Deploy to production server
4. Start infrastructure (PostgreSQL, Redis, OpenSearch)  
5. Start core services
6. Start AI services
7. Start orchestrator and RAG
8. Start frontend
9. Verify deployment
10. Show summary

## 📞 Hỗ trợ

### Nếu gặp vấn đề:

1. **Kiểm tra logs**:
   ```bash
   ./logs-ree-ai.sh
   ```

2. **Restart services**:
   ```bash
   ./stop-ree-ai.sh
   ./start-ree-ai.sh
   ```

3. **Kiểm tra GitHub Actions**:
   - Vào tab "Actions" trong repository
   - Xem logs của deployment job

4. **Liên hệ support**: Tạo issue trong repository

## ✅ Checklist Deploy

- [ ] Server production đã cài đặt script setup
- [ ] SSH keys đã thiết lập
- [ ] GitHub Secrets đã cấu hình
- [ ] OPENAI_API_KEY đã thêm vào .env
- [ ] Push code lên main branch
- [ ] GitHub Actions chạy thành công  
- [ ] Truy cập được http://192.168.1.11:3000
- [ ] Tất cả health checks PASS

**🎉 Chúc mừng! REE AI đã deploy thành công!**
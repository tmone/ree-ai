# 🏗️ Setup Self-hosted Runner cho Production Server

## 🎯 Tổng quan

Thay vì dùng SSH, chúng ta sẽ cài **GitHub Actions self-hosted runner** trực tiếp trên server production (192.168.1.11).

### ✅ Lợi ích:
- **Không cần SSH keys** 
- **Deploy trực tiếp** trên server
- **Nhanh hơn** (không qua network)
- **An toàn hơn** (không expose SSH)
- **Đơn giản hơn** (ít config)

---

## 🚀 Bước 1: Setup Server Production

### SSH vào server production:
```bash
ssh tmone@192.168.1.11
```

### Chạy script setup:
```bash
# Download script setup
curl -sSL https://raw.githubusercontent.com/tmone/ree-ai/main/scripts/setup-github-runner-production.sh -o setup-runner.sh

# Chạy script
chmod +x setup-runner.sh
./setup-runner.sh
```

Script sẽ tự động:
- ✅ Download GitHub Actions runner
- ✅ Install dependencies
- ✅ Tạo helper scripts

---

## 🔧 Bước 2: Cấu hình Runner

### Lấy registration token từ GitHub:

**Cách 1: Qua GitHub UI**
1. Vào: https://github.com/tmone/ree-ai/settings/actions/runners/new
2. Chọn "Linux"
3. Copy token từ lệnh `./config.sh`

**Cách 2: Qua API (nếu có Personal Access Token)**
```bash
curl -X POST https://api.github.com/repos/tmone/ree-ai/actions/runners/registration-token \
  -H "Authorization: token YOUR_GITHUB_PAT" | jq -r .token
```

### Cấu hình runner:
```bash
cd ~/github-actions-runner

# Cấu hình với token từ GitHub
./config.sh --url https://github.com/tmone/ree-ai --token YOUR_TOKEN_HERE

# Khi được hỏi, nhập:
# Enter the name of the runner group: [press Enter for default]
# Enter the name of runner: production-server
# Enter any additional labels: production,self-hosted,linux,x64
# Enter name of work folder: [press Enter for default]
```

### Install và start service:
```bash
# Install as system service
sudo ./svc.sh install

# Start service
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
```

---

## 🧪 Bước 3: Test Setup

### Kiểm tra runner status:
```bash
cd ~/github-actions-runner
./check-runner-status.sh
```

### Verify trên GitHub:
1. Vào: https://github.com/tmone/ree-ai/settings/actions/runners
2. Xem runner "production-server" với status "Idle" (màu xanh)

---

## 🎮 Bước 4: Test Deployment

### Commit và push để test:
```bash
# Trên máy local
git add .
git commit -m "Update to self-hosted runner"
git push origin release
```

### Monitor deployment:
- **GitHub Actions**: https://github.com/tmone/ree-ai/actions
- **Production URL**: http://192.168.1.11:3000

---

## 🛠️ Quản lý Runner

### Helper scripts trên server:
```bash
cd ~/github-actions-runner

# Check status
./check-runner-status.sh

# Start runner
./start-runner.sh

# Stop runner  
./stop-runner.sh

# Restart runner
./restart-runner.sh
```

### System service commands:
```bash
# Service control
sudo systemctl status actions.runner.tmone-ree-ai.production-server.service
sudo systemctl start actions.runner.tmone-ree-ai.production-server.service
sudo systemctl stop actions.runner.tmone-ree-ai.production-server.service

# Enable auto-start
sudo systemctl enable actions.runner.tmone-ree-ai.production-server.service
```

---

## 📊 Workflow Changes

### Before (SSH):
```yaml
runs-on: ubuntu-latest  # GitHub cloud
steps:
- name: SSH Deploy
  run: ssh tmone@192.168.1.11 '...'
```

### After (Self-hosted):
```yaml
runs-on: [self-hosted, linux, x64, production]  # Production server
steps:
- name: Direct Deploy
  run: docker-compose up -d  # Direct command
```

---

## 🔍 Troubleshooting

### Runner không xuất hiện trên GitHub:
```bash
# Check runner logs
cd ~/github-actions-runner
tail -f _diag/Runner_*.log

# Restart service
sudo ./svc.sh stop
sudo ./svc.sh start
```

### Deployment fails:
```bash
# Check GitHub Actions logs trong repository
# Check local logs:
cd ~/github-actions-runner
tail -f _diag/Worker_*.log
```

### Reconfigure runner:
```bash
cd ~/github-actions-runner
sudo ./svc.sh stop
./config.sh remove
# Get new token từ GitHub
./config.sh --url https://github.com/tmone/ree-ai --token NEW_TOKEN
sudo ./svc.sh install
sudo ./svc.sh start
```

---

## ✅ Verification Checklist

- [ ] Runner hiển thị "Idle" trên GitHub
- [ ] Service đang chạy: `sudo ./svc.sh status`
- [ ] Workflow chạy trên production runner
- [ ] Deployment thành công
- [ ] Services accessible tại http://192.168.1.11:3000

---

## 🎉 Kết quả

### Workflow mới:
```
Code → Push to release → Runner trên production server → Deploy local → Done!
```

### So sánh:

| Aspect | SSH Method | Self-hosted Runner |
|--------|------------|-------------------|
| **Setup** | SSH keys + secrets | Runner installation |
| **Security** | SSH over network | Local execution |
| **Speed** | Network latency | Direct execution |
| **Debugging** | Remote logs | Local logs |
| **Complexity** | Medium | Low |
| **Maintenance** | SSH key rotation | Runner updates |

**🚀 Self-hosted runner = Đơn giản hơn, nhanh hơn, an toàn hơn!**

---

**📞 Support**: Nếu gặp vấn đề, tạo issue trong repository hoặc check GitHub runner documentation.
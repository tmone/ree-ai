# Hướng Dẫn Deploy REE AI lên Server Production

## Thông tin Server
- **IP**: 103.153.74.213
- **SSH Key**: `tmone`
- **User mặc định**: root

## Yêu cầu
- SSH key file `tmone` (file key đăng nhập server)
- File `.env` đã được cấu hình (bao gồm OPENAI_API_KEY)

## Cách 1: Deploy tự động (Khuyến nghị)

### Trên Windows (PowerShell)

```powershell
# Di chuyển vào thư mục dự án
cd d:\Crastonic\ree-ai

# Chạy script deploy
.\scripts\deploy-to-production.ps1 -SSHKey "tmone" -Server "103.153.74.213"

# Hoặc nếu key ở vị trí khác
.\scripts\deploy-to-production.ps1 -SSHKey "C:\path\to\tmone" -Server "103.153.74.213"
```

### Trên Linux/Mac (Bash)

```bash
# Di chuyển vào thư mục dự án
cd /path/to/ree-ai

# Set quyền thực thi cho script
chmod +x scripts/deploy-to-production.sh

# Chạy script deploy
./scripts/deploy-to-production.sh

# Hoặc với tham số tùy chỉnh
SSH_KEY="tmone" SSH_USER="root" ./scripts/deploy-to-production.sh
```

## Cách 2: Deploy thủ công

### Bước 1: Kết nối SSH đến server

```bash
ssh -i tmone root@103.153.74.213
```

### Bước 2: Cài đặt Docker (nếu chưa có)

```bash
# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker
systemctl start docker

# Cài Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Bước 3: Clone repository

```bash
# Tạo thư mục và clone
mkdir -p /opt
cd /opt
git clone https://github.com/tmone/ree-ai.git
cd ree-ai
```

### Bước 4: Cấu hình .env file

```bash
# Copy file mẫu
cp .env.example .env

# Chỉnh sửa file .env
nano .env
```

**Các biến môi trường quan trọng cần cấu hình:**

```bash
# BẮT BUỘC
OPENAI_API_KEY=sk-your-actual-openai-key-here

# NÊN ĐỔI (cho production)
POSTGRES_PASSWORD=your-strong-password-here
WEBUI_SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here

# TÙY CHỌN
POSTGRES_DB=ree_ai
POSTGRES_USER=ree_ai_user
DEBUG=false
LOG_LEVEL=INFO
```

Lưu file: `Ctrl+X`, sau đó `Y`, sau đó `Enter`

### Bước 5: Build và Start services

```bash
cd /opt/ree-ai

# Build Docker images
docker-compose --profile all build --parallel

# Start infrastructure services
docker-compose up -d postgres redis opensearch

# Đợi infrastructure khởi động
sleep 30

# Start service registry
docker-compose up -d service-registry
sleep 10

# Start core services
docker-compose up -d core-gateway db-gateway auth-service
sleep 15

# Start AI services
docker-compose up -d classification completeness attribute-extraction validation semantic-chunking
sleep 10

# Start orchestrator và RAG
docker-compose up -d orchestrator rag-service
sleep 15

# Start frontend
docker-compose up -d open-webui

# Kiểm tra trạng thái
docker-compose ps
```

### Bước 6: Kiểm tra services

```bash
# Xem logs
docker-compose logs -f

# Hoặc xem log từng service
docker-compose logs -f open-webui
docker-compose logs -f orchestrator
docker-compose logs -f rag-service

# Kiểm tra health
curl http://localhost:3000/health
curl http://localhost:8090/health
curl http://localhost:8000/health
```

## Truy cập ứng dụng

Sau khi deploy thành công, truy cập:

- **Open WebUI** (Giao diện chính): http://103.153.74.213:3000
- **Orchestrator API**: http://103.153.74.213:8090
- **Service Registry**: http://103.153.74.213:8000

## Cấu hình Firewall (Khuyến nghị)

```bash
# Cho phép các port cần thiết
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw allow 3000/tcp    # Open WebUI

# Enable firewall
ufw --force enable

# Kiểm tra status
ufw status
```

## Cài đặt SSL/HTTPS (Production)

### Sử dụng Nginx + Let's Encrypt

```bash
# Cài đặt Nginx
apt update
apt install -y nginx certbot python3-certbot-nginx

# Cấu hình Nginx cho REE AI
cat > /etc/nginx/sites-available/ree-ai << 'EOF'
server {
    listen 80;
    server_name your-domain.com;  # Đổi thành domain của bạn

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/ree-ai /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Cài đặt SSL certificate
certbot --nginx -d your-domain.com
```

## Quản lý Services

### Xem logs

```bash
# Tất cả services
docker-compose logs -f

# Service cụ thể
docker-compose logs -f open-webui
docker-compose logs -f orchestrator
docker-compose logs -f rag-service

# Lọc logs theo thời gian
docker-compose logs --since 30m
docker-compose logs --tail=100
```

### Restart services

```bash
# Restart tất cả
docker-compose restart

# Restart service cụ thể
docker-compose restart open-webui
docker-compose restart orchestrator
```

### Stop/Start services

```bash
# Stop tất cả
docker-compose down

# Start lại
docker-compose --profile all up -d

# Stop service cụ thể
docker-compose stop open-webui

# Start service cụ thể
docker-compose start open-webui
```

### Update code mới

```bash
cd /opt/ree-ai

# Pull code mới
git pull origin main

# Rebuild và restart
docker-compose --profile all build --parallel
docker-compose --profile all up -d --force-recreate
```

## Backup & Restore

### Backup PostgreSQL

```bash
# Backup database
docker exec ree-ai-postgres pg_dump -U ree_ai_user ree_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# Hoặc với password
docker exec ree-ai-postgres pg_dump -U ree_ai_user -W ree_ai > backup.sql
```

### Restore PostgreSQL

```bash
# Restore database
cat backup.sql | docker exec -i ree-ai-postgres psql -U ree_ai_user ree_ai
```

### Backup OpenSearch data

```bash
# Backup OpenSearch indices
docker exec ree-ai-opensearch curl -X POST "localhost:9200/_snapshot/backup/snapshot_$(date +%Y%m%d)"
```

## Monitoring

### Kiểm tra tài nguyên

```bash
# Xem CPU/Memory usage
docker stats

# Xem disk usage
df -h
docker system df

# Xem logs lỗi
docker-compose logs | grep ERROR
docker-compose logs | grep CRITICAL
```

### Health check script

```bash
# Tạo script health check
cat > /opt/ree-ai/health-check.sh << 'EOF'
#!/bin/bash
echo "=== REE AI Health Check ==="
echo ""
echo "Service Registry: $(curl -sf http://localhost:8000/health && echo 'OK' || echo 'FAILED')"
echo "Core Gateway: $(curl -sf http://localhost:8080/health && echo 'OK' || echo 'FAILED')"
echo "Orchestrator: $(curl -sf http://localhost:8090/health && echo 'OK' || echo 'FAILED')"
echo "RAG Service: $(curl -sf http://localhost:8091/health && echo 'OK' || echo 'FAILED')"
echo "Open WebUI: $(curl -sf http://localhost:3000/health && echo 'OK' || echo 'FAILED')"
EOF

chmod +x /opt/ree-ai/health-check.sh

# Chạy health check
/opt/ree-ai/health-check.sh
```

### Setup cron job cho auto health check

```bash
# Thêm vào crontab
crontab -e

# Thêm dòng này (check mỗi 5 phút)
*/5 * * * * /opt/ree-ai/health-check.sh >> /var/log/ree-ai-health.log 2>&1
```

## Troubleshooting

### Service không start được

```bash
# Kiểm tra logs
docker-compose logs service-name

# Kiểm tra container status
docker-compose ps

# Restart service
docker-compose restart service-name

# Rebuild service
docker-compose build service-name
docker-compose up -d --force-recreate service-name
```

### Port bị chiếm

```bash
# Kiểm tra port đang được sử dụng
netstat -tulpn | grep :3000
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Out of disk space

```bash
# Xóa Docker images không dùng
docker system prune -a

# Xóa volumes không dùng
docker volume prune

# Xóa logs cũ
find /var/lib/docker/containers/ -name "*.log" -delete
```

### Database connection issues

```bash
# Kiểm tra PostgreSQL
docker exec ree-ai-postgres pg_isready -U ree_ai_user

# Connect vào database
docker exec -it ree-ai-postgres psql -U ree_ai_user ree_ai

# Xem connections
docker exec ree-ai-postgres psql -U ree_ai_user ree_ai -c "SELECT count(*) FROM pg_stat_activity;"
```

## Security Checklist

- [ ] Đổi POSTGRES_PASSWORD trong .env
- [ ] Đổi WEBUI_SECRET_KEY trong .env
- [ ] Đổi JWT_SECRET_KEY trong .env
- [ ] Cấu hình firewall (ufw)
- [ ] Cài đặt SSL certificate
- [ ] Cấu hình rate limiting trong Nginx
- [ ] Backup định kỳ database
- [ ] Monitor logs thường xuyên
- [ ] Update system packages thường xuyên

## Liên hệ & Hỗ trợ

Nếu gặp vấn đề trong quá trình deploy:

1. Kiểm tra logs: `docker-compose logs -f`
2. Kiểm tra health: `/opt/ree-ai/health-check.sh`
3. Xem documentation: `/opt/ree-ai/docs/`
4. Tạo issue trên GitHub

---

**Lưu ý**: Đây là hướng dẫn deploy cho môi trường production. Đảm bảo bạn đã backup dữ liệu và test kỹ trước khi deploy.

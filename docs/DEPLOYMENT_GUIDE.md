# REE AI Frontend Deployment Guide

Complete guide for deploying REE AI custom frontend to production environments.

## Table of Contents

1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Build Optimization](#build-optimization)
6. [Monitoring & Logging](#monitoring--logging)
7. [Troubleshooting](#troubleshooting)

---

## Pre-deployment Checklist

### 1. Verify Code Quality

```bash
# Run linting
cd frontend/open-webui
npm run lint

# Type check
npm run check

# Format code
npm run format
```

### 2. Update Environment Variables

```bash
# Copy and configure production .env
cp .env.example .env

# Update these critical variables:
# - WEBUI_SECRET_KEY (MUST change from default)
# - JWT_SECRET_KEY (MUST change from default)
# - OPENAI_API_KEY (if using OpenAI)
# - DATABASE_URL (production database)
```

### 3. Security Checklist

- [ ] Changed all default secret keys
- [ ] Enabled HTTPS/TLS
- [ ] Configured CORS properly
- [ ] Set up rate limiting
- [ ] Enabled authentication
- [ ] Reviewed exposed ports
- [ ] Set up firewall rules
- [ ] Configured security headers

### 4. Performance Checklist

- [ ] Enabled production build optimizations
- [ ] Configured CDN for static assets
- [ ] Set up caching headers
- [ ] Optimized images
- [ ] Enabled compression (Gzip/Brotli)
- [ ] Set up database indexes
- [ ] Configured connection pooling

---

## Docker Deployment

### Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # Open WebUI Frontend (REE AI Custom)
  open-webui:
    build:
      context: ./frontend/open-webui
      dockerfile: Dockerfile
      args:
        - USE_CUDA=false
        - USE_SLIM=true  # Slim build for production
    container_name: ree-ai-frontend-prod
    restart: always
    ports:
      - "3000:8080"
    environment:
      # Application
      - WEBUI_NAME=REE AI - Real Estate Assistant
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}

      # Backend URLs (internal Docker network)
      - OPENAI_API_BASE_URL=http://orchestrator:8080
      - OPENAI_API_KEY=dummy

      # Database
      - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}

      # Features
      - ENABLE_OPENAI_API=true
      - ENABLE_OLLAMA_API=false

      # Security
      - WEBUI_AUTH=true

    volumes:
      - open_webui_data:/app/backend/data
    depends_on:
      - postgres
      - orchestrator
      - db-gateway
    networks:
      - ree-ai-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  # Nginx Reverse Proxy (Optional but recommended)
  nginx:
    image: nginx:alpine
    container_name: ree-ai-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/cache:/var/cache/nginx
    depends_on:
      - open-webui
    networks:
      - ree-ai-network

volumes:
  open_webui_data:
    driver: local

networks:
  ree-ai-network:
    driver: bridge
```

### Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/json application/javascript;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    # Upstream
    upstream open_webui {
        server open-webui:8080;
        keepalive 32;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # Max upload size
        client_max_body_size 50M;

        # Static files caching
        location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
            proxy_pass http://open_webui;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # API endpoints (rate limited)
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            limit_conn addr 10;

            proxy_pass http://open_webui;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;

            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # WebSocket support
        location /ws/ {
            proxy_pass http://open_webui;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 86400;
        }

        # All other requests
        location / {
            proxy_pass http://open_webui;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # Health check
        location /health {
            access_log off;
            proxy_pass http://open_webui/health;
        }
    }
}
```

### Deploy with Docker

```bash
# Build and start
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f open-webui

# Check status
docker compose -f docker-compose.prod.yml ps

# Stop
docker compose -f docker-compose.prod.yml down
```

---

## Kubernetes Deployment

### Deployment YAML

Create `k8s/frontend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ree-ai-frontend
  namespace: ree-ai
  labels:
    app: ree-ai-frontend
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ree-ai-frontend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: ree-ai-frontend
        version: v1.0.0
    spec:
      containers:
      - name: frontend
        image: registry.example.com/ree-ai/frontend:v1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: WEBUI_NAME
          value: "REE AI - Real Estate Assistant"
        - name: WEBUI_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ree-ai-secrets
              key: webui-secret-key
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ree-ai-secrets
              key: database-url
        - name: OPENAI_API_BASE_URL
          value: "http://orchestrator-service:8080"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        volumeMounts:
        - name: data
          mountPath: /app/backend/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: ree-ai-frontend-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ree-ai-frontend-service
  namespace: ree-ai
  labels:
    app: ree-ai-frontend
spec:
  type: ClusterIP
  selector:
    app: ree-ai-frontend
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ree-ai-frontend-pvc
  namespace: ree-ai
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast-ssd
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ree-ai-frontend-ingress
  namespace: ree-ai
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - ree-ai.example.com
    secretName: ree-ai-tls
  rules:
  - host: ree-ai.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ree-ai-frontend-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace ree-ai

# Create secrets
kubectl create secret generic ree-ai-secrets \
  --from-literal=webui-secret-key='your-secret-key' \
  --from-literal=database-url='postgresql://user:pass@postgres:5432/db' \
  -n ree-ai

# Apply deployment
kubectl apply -f k8s/frontend-deployment.yaml

# Check status
kubectl get pods -n ree-ai
kubectl get svc -n ree-ai
kubectl get ingress -n ree-ai

# View logs
kubectl logs -f deployment/ree-ai-frontend -n ree-ai

# Scale
kubectl scale deployment ree-ai-frontend --replicas=5 -n ree-ai
```

---

## Environment Configuration

### Production .env

```bash
# ============================================================
# PRODUCTION ENVIRONMENT VARIABLES
# ============================================================

# Application
PUBLIC_WEBUI_NAME=REE AI - Real Estate Assistant
WEBUI_SECRET_KEY=your-very-secret-production-key-change-this
JWT_SECRET_KEY=your-jwt-secret-production-key-change-this

# Database
DATABASE_URL=postgresql://ree_ai_user:strong_password@postgres:5432/ree_ai_prod

# Backend Services (internal URLs)
REE_AI_ORCHESTRATOR_URL=http://orchestrator:8080
REE_AI_DB_GATEWAY_URL=http://db-gateway:8080
REE_AI_CLASSIFICATION_URL=http://classification:8080
REE_AI_RAG_SERVICE_URL=http://rag-service:8080

# OpenAI (if using)
OPENAI_API_KEY=sk-prod-key-here

# Features
PUBLIC_FEATURE_PROPERTY_SEARCH=true
PUBLIC_FEATURE_PROPERTY_COMPARE=true
PUBLIC_FEATURE_PROPERTY_FAVORITES=true

# Performance
PUBLIC_LAZY_LOAD_IMAGES=true
PUBLIC_IMAGE_QUALITY=75
PUBLIC_ENABLE_SERVICE_WORKER=true

# Monitoring
PUBLIC_SENTRY_DSN=https://your-sentry-dsn
PUBLIC_GA_ID=G-XXXXXXXXXX

# Debug (should be false in production)
PUBLIC_DEBUG=false
PUBLIC_SHOW_DEV_TOOLS=false
PUBLIC_LOG_LEVEL=warn
```

---

## Build Optimization

### 1. Production Build

```bash
# Clean previous builds
rm -rf .svelte-kit build node_modules/.cache

# Install dependencies
npm ci --production=false

# Build with optimizations
NODE_ENV=production npm run build

# Check build size
du -sh build/*
```

### 2. Image Optimization

```bash
# Optimize images before deployment
npm install -g imagemin-cli

find public/images -name "*.jpg" -o -name "*.png" | \
  xargs -I {} imagemin {} --out-dir=public/images/optimized
```

### 3. Bundle Analysis

```bash
# Analyze bundle size
npm run build -- --mode analyze

# Check for large dependencies
npx vite-bundle-visualizer
```

---

## Monitoring & Logging

### Application Monitoring

```yaml
# Prometheus configuration
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ree-ai-frontend'
    static_configs:
      - targets: ['open-webui:8080']
    metrics_path: '/metrics'
```

### Logging Configuration

```bash
# Docker logging driver
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  ree-ai-frontend
```

### Health Checks

```bash
# Endpoint health check
curl -f http://localhost:3000/health || exit 1

# Database health
curl -f http://localhost:3000/api/health/db || exit 1

# Services health
curl -f http://localhost:3000/api/ree-ai/health || exit 1
```

---

## Troubleshooting

### Common Issues

**Issue: Build fails with memory error**
```bash
# Increase Node.js memory
export NODE_OPTIONS="--max-old-space-size=8192"
npm run build
```

**Issue: Container won't start**
```bash
# Check logs
docker logs ree-ai-frontend-prod

# Check health
docker exec ree-ai-frontend-prod curl -f http://localhost:8080/health
```

**Issue: Slow performance**
```bash
# Enable Gzip compression
# Check nginx.conf for gzip settings

# Optimize database queries
# Add indexes to frequently queried fields

# Enable caching
# Configure Redis for session/data caching
```

---

## Post-Deployment

### 1. Smoke Tests

```bash
# Homepage loads
curl -I https://your-domain.com

# API health
curl https://your-domain.com/health

# Property search
curl https://your-domain.com/properties

# Backend connectivity
curl https://your-domain.com/api/ree-ai/health
```

### 2. Performance Testing

```bash
# Load test with Apache Bench
ab -n 1000 -c 10 https://your-domain.com/

# Or with artillery
npm install -g artillery
artillery quick --count 100 --num 10 https://your-domain.com/
```

### 3. Backup Configuration

```bash
# Backup database
docker exec postgres pg_dump -U ree_ai_user ree_ai_prod > backup_$(date +%Y%m%d).sql

# Backup volumes
docker run --rm -v ree-ai_open_webui_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/data_backup_$(date +%Y%m%d).tar.gz /data
```

---

## Rollback Procedure

```bash
# Docker Compose
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --force-recreate

# Kubernetes
kubectl rollout undo deployment/ree-ai-frontend -n ree-ai
kubectl rollout status deployment/ree-ai-frontend -n ree-ai
```

---

## Support

For deployment issues:
- Check logs: `docker compose logs -f open-webui`
- Review health: `curl http://localhost:3000/health`
- Contact: devops@ree-ai.com

---

**Last Updated:** 2025-10-31
**Version:** 1.0.0

# REE AI - Production Deployment Guide

Complete guide for deploying REE AI platform to production environments.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Deployment Options](#deployment-options)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Security Configuration](#security-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────┐
│  Load Balancer / Ingress                                │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  API Gateway (Port 8888)                                │
│  ✓ Rate limiting                                        │
│  ✓ JWT authentication                                   │
│  ✓ Request routing                                      │
│  ✓ Metrics collection                                   │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  Auth Service (Port 8085)                               │
│  ✓ User registration/login                              │
│  ✓ JWT token management                                 │
│  ✓ Password hashing (bcrypt)                            │
└─────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  Business Logic Layer                                   │
│  ├─ Orchestrator (Port 8090)    - Intent detection      │
│  ├─ RAG Service (Port 8091)     - Q&A pipeline          │
│  ├─ Classification (Port 8083)  - Property classifier   │
│  └─ Semantic Chunking (8082)    - Text processing       │
└─────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  Core Services                                          │
│  ├─ Core Gateway (Port 8080)    - LLM routing           │
│  └─ DB Gateway (Port 8081)      - Database operations   │
└─────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  Infrastructure                                         │
│  ├─ PostgreSQL (Port 5432)      - User data             │
│  ├─ OpenSearch (Port 9200)      - Vector search         │
│  ├─ Redis (Port 6379)           - Cache & sessions      │
│  ├─ Ollama (Port 11434)         - Local LLM             │
│  └─ Open WebUI (Port 3000)      - Chat interface        │
└─────────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  Monitoring & Observability                             │
│  ├─ Prometheus (Port 9090)      - Metrics collection    │
│  └─ Grafana (Port 3001)         - Dashboards            │
└─────────────────────────────────────────────────────────┘
```

### Key Features

- **API Gateway**: Single entry point with rate limiting and auth
- **Authentication**: JWT-based with secure password hashing
- **Monitoring**: Prometheus metrics + Grafana dashboards
- **Scalability**: Horizontal pod autoscaling (Kubernetes)
- **High Availability**: Multi-replica deployments
- **Security**: Network policies, secrets management

---

## Deployment Options

### 1. Docker Compose (Recommended for Development/Small Production)

**Pros:**
- Simple setup
- Fast deployment
- Good for single server
- Easy development

**Cons:**
- Single point of failure
- Limited scaling
- Manual failover

### 2. Kubernetes (Recommended for Production)

**Pros:**
- Auto-scaling
- Self-healing
- Rolling updates
- High availability

**Cons:**
- Complex setup
- Requires cluster management
- Higher learning curve

---

## Docker Deployment

### Prerequisites

- Docker 24.0+
- Docker Compose v2.20+
- 8GB+ RAM
- 50GB+ disk space

### Step 1: Clone Repository

```bash
git clone <your-repo-url>
cd ree-ai
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your values
nano .env
```

**Required Variables:**

```env
# CRITICAL - MUST CHANGE IN PRODUCTION
OPENAI_API_KEY=sk-your-actual-openai-key
JWT_SECRET_KEY=use-a-long-random-string-at-least-32-chars
POSTGRES_PASSWORD=strong-database-password
WEBUI_SECRET_KEY=another-random-string

# Optional
GRAFANA_ADMIN_PASSWORD=secure-password
```

### Step 3: Start Services

```bash
# Start all services (production mode)
docker-compose --profile real up -d

# Start with monitoring
docker-compose --profile real up -d
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

### Step 4: Verify Deployment

```bash
# Check service health
curl http://localhost:8888/health  # API Gateway
curl http://localhost:8085/health  # Auth Service
curl http://localhost:8090/health  # Orchestrator
curl http://localhost:8091/health  # RAG Service

# View logs
docker-compose logs -f api-gateway
docker-compose logs -f auth-service
```

### Step 5: Access Services

```
Open WebUI:    http://localhost:3000
API Gateway:   http://localhost:8888
Auth Service:  http://localhost:8085
Grafana:       http://localhost:3001 (admin/admin)
Prometheus:    http://localhost:9090
```

### Production Hardening (Docker)

```bash
# 1. Enable firewall
sudo ufw allow 3000/tcp   # Open WebUI
sudo ufw allow 8888/tcp   # API Gateway (or use reverse proxy)
sudo ufw enable

# 2. Set up reverse proxy (nginx)
# See nginx.conf.example

# 3. Enable SSL/TLS
# Use Let's Encrypt with certbot

# 4. Set up backups
# See backup section below
```

---

## Kubernetes Deployment

See [k8s/README.md](k8s/README.md) for detailed Kubernetes deployment guide.

### Quick Start

```bash
# 1. Update secrets
kubectl create secret generic ree-ai-secrets \
  --from-literal=OPENAI_API_KEY=sk-your-key \
  --from-literal=POSTGRES_PASSWORD=your-password \
  --from-literal=JWT_SECRET_KEY=your-jwt-secret \
  -n ree-ai --dry-run=client -o yaml > k8s/base/secret.yaml

# 2. Deploy
kubectl apply -k k8s/base/

# 3. Verify
kubectl get all -n ree-ai
```

---

## Security Configuration

### 1. JWT Secret Key

```bash
# Generate secure JWT secret (32+ characters)
openssl rand -base64 32

# Add to .env
JWT_SECRET_KEY=<generated-key>
```

### 2. Database Security

```bash
# Strong PostgreSQL password
POSTGRES_PASSWORD=$(openssl rand -base64 24)

# Enable SSL for PostgreSQL (production)
# Edit postgresql.conf:
ssl = on
ssl_cert_file = '/path/to/cert.pem'
ssl_key_file = '/path/to/key.pem'
```

### 3. API Rate Limiting

Configured in API Gateway:

```python
RateLimitConfig(
    requests_per_minute=60,
    requests_per_hour=1000,
    requests_per_day=10000
)
```

### 4. Network Security

```bash
# Docker: Use internal networks
# Kubernetes: Use NetworkPolicies

# Only expose necessary ports
# API Gateway: 8888 (public)
# Everything else: internal only
```

### 5. Secrets Management

**Docker:**
```bash
# Use Docker secrets
echo "my-secret" | docker secret create jwt_secret -
```

**Kubernetes:**
```bash
# Use Kubernetes secrets
kubectl create secret generic ree-ai-secrets --from-literal=...
```

---

## Monitoring & Logging

### Prometheus Metrics

All services expose metrics at `/metrics`:

```bash
# View metrics
curl http://localhost:8888/metrics
```

**Key Metrics:**
- `http_requests_total` - Request count by endpoint
- `http_request_duration_seconds` - Request latency
- `llm_requests_total` - LLM API calls
- `llm_tokens_total` - Token usage
- `db_queries_total` - Database operations

### Grafana Dashboards

```bash
# Access Grafana
http://localhost:3001

# Default credentials
Username: admin
Password: admin (change immediately!)
```

**Pre-configured Dashboards:**
- System Overview
- API Gateway Performance
- LLM Usage & Costs
- Database Performance
- Service Health

### Application Logs

```bash
# Docker
docker-compose logs -f <service-name>

# Kubernetes
kubectl logs -f deployment/<service-name> -n ree-ai

# Filter by log level
docker-compose logs | grep ERROR
```

---

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL backup
docker exec ree-ai-postgres pg_dump -U ree_ai_user ree_ai > backup.sql

# Restore
docker exec -i ree-ai-postgres psql -U ree_ai_user ree_ai < backup.sql
```

### Automated Backups

```bash
# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

**Example backup script:**

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# PostgreSQL
docker exec ree-ai-postgres pg_dump -U ree_ai_user ree_ai | \
  gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# OpenSearch (if needed)
# Add OpenSearch backup commands

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Check dependencies
docker-compose ps

# Verify environment variables
docker-compose config
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker exec -it ree-ai-postgres psql -U ree_ai_user -d ree_ai

# Check network
docker network inspect ree-ai-network
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Limit container resources
docker-compose.yml:
  services:
    api-gateway:
      deploy:
        resources:
          limits:
            memory: 512M
```

### API Gateway Rate Limit Issues

```bash
# Check rate limit metrics
curl http://localhost:8888/metrics | grep rate_limit

# Adjust limits in services/api_gateway/main.py
```

---

## Performance Optimization

### 1. Database

```sql
-- Add indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_properties_location ON properties(location);

-- Analyze queries
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### 2. Redis Caching

```python
# Cache frequently accessed data
# Add to services as needed
```

### 3. Connection Pooling

```python
# PostgreSQL: asyncpg pool
# Already configured in services
min_size=2, max_size=10
```

### 4. Horizontal Scaling

```bash
# Docker: Scale services
docker-compose up -d --scale api-gateway=3

# Kubernetes: HPA (auto-scaling)
kubectl autoscale deployment api-gateway --min=2 --max=10 --cpu-percent=70 -n ree-ai
```

---

## Production Checklist

### Pre-Deployment

- [ ] Update all secrets (.env, k8s/base/secret.yaml)
- [ ] Configure SSL/TLS certificates
- [ ] Set up reverse proxy (nginx/traefik)
- [ ] Configure firewall rules
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation
- [ ] Set up backup strategy
- [ ] Test disaster recovery
- [ ] Review resource limits
- [ ] Configure auto-scaling

### Post-Deployment

- [ ] Verify all services are healthy
- [ ] Test authentication flow
- [ ] Test API endpoints
- [ ] Monitor resource usage
- [ ] Check logs for errors
- [ ] Verify backups are running
- [ ] Test alerting
- [ ] Document runbooks
- [ ] Train operations team

---

## Support & Resources

- **Documentation**: See `docs/` directory
- **API Docs**: http://localhost:8888/docs
- **Monitoring**: http://localhost:3001
- **Issues**: Report via GitHub issues

---

**Version:** 1.0.0
**Last Updated:** 2025-10-29
**Status:** Production Ready

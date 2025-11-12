# Production Deployment Guide

## Overview

This guide provides a complete, portable deployment solution for REE AI that works across any production environment without hard-coding server-specific configurations.

## Architecture

### Deployment Components

```
┌─────────────────────────────────────────┐
│            GitHub Repository            │
│  - Source Code                         │
│  - Deployment Scripts                  │
│  - GitHub Actions Workflows            │
└─────────────────┬───────────────────────┘
                  │
                  │ Push/Manual Trigger
                  ▼
┌─────────────────────────────────────────┐
│         GitHub Actions Runner          │
│  - Pre-deployment Validation           │
│  - Environment Setup                   │
│  - Portable Deployment Script          │
│  - Post-deployment Verification        │
└─────────────────┬───────────────────────┘
                  │
                  │ Deploy
                  ▼
┌─────────────────────────────────────────┐
│         Production Server              │
│  - Docker Compose Services             │
│  - Environment Configuration           │
│  - Health Monitoring                   │
│  - Automatic Recovery                  │
└─────────────────────────────────────────┘
```

## Features

### ✅ Portable Deployment
- **No Hard-coded IPs**: Uses dynamic server detection
- **Environment Variables**: All configuration through env vars
- **Cross-platform**: Works on any Linux server
- **Configurable**: Supports multiple environments (production, staging)

### ✅ Production-Ready
- **Pre-deployment Validation**: Checks prerequisites and environment
- **Graceful Shutdown**: Properly stops existing services
- **Health Monitoring**: Comprehensive service health checks
- **Error Handling**: Proper error reporting and recovery
- **Security**: Secrets management through GitHub Secrets

### ✅ Zero-Downtime Deployment
- **Service Dependencies**: Starts services in correct order
- **Health Checks**: Waits for services to be ready
- **Rollback Capability**: Can revert to previous version
- **Progressive Deployment**: Infrastructure → Core → AI Services → Frontend

## Quick Start

### 1. Setup GitHub Secrets

```bash
# Setup all required secrets interactively
./scripts/setup-secrets.sh setup

# Or setup specific secrets
./scripts/setup-secrets.sh set OPENAI_API_KEY
./scripts/setup-secrets.sh set JWT_SECRET_KEY

# Validate secrets
./scripts/setup-secrets.sh validate
```

### 2. Setup Production Runner

```bash
# Setup GitHub Actions runner with production label
./scripts/setup-production-runner.sh
```

### 3. Deploy

#### Auto-deployment (Recommended)
```bash
# Push to release branch triggers automatic deployment
git checkout release
git push origin release
```

#### Manual deployment
```bash
# Trigger via GitHub CLI
gh workflow run deploy-production.yml --ref release --field confirm_deployment="DEPLOY"

# Or via GitHub Web UI
# Go to Actions → Deploy to Production → Run workflow
```

## Deployment Scripts

### Core Deployment Script: `scripts/deploy-production.sh`

Portable deployment script with the following capabilities:

```bash
# Basic deployment
./scripts/deploy-production.sh

# Custom environment
./scripts/deploy-production.sh --env staging

# Custom project directory
./scripts/deploy-production.sh --project-dir /opt/ree-ai

# Full customization
./scripts/deploy-production.sh \
  --env production \
  --project-dir /opt/ree-ai \
  --log-level DEBUG
```

#### Features:
- **Prerequisites Check**: Validates Docker, docker-compose, required files
- **Environment Setup**: Creates .env file with proper production settings
- **Service Management**: Starts services in dependency order
- **Health Monitoring**: Waits for and validates service health
- **Error Recovery**: Proper error handling and cleanup

### Secrets Management: `scripts/setup-secrets.sh`

Manages GitHub Secrets for secure deployment:

```bash
# Interactive setup
./scripts/setup-secrets.sh setup

# List configured secrets
./scripts/setup-secrets.sh list

# Set individual secret
./scripts/setup-secrets.sh set OPENAI_API_KEY

# Validate all secrets
./scripts/setup-secrets.sh validate

# Create environment template
./scripts/setup-secrets.sh template
```

### Runner Setup: `scripts/setup-production-runner.sh`

Sets up GitHub Actions self-hosted runner:

- Downloads and configures latest GitHub Actions runner
- Sets up systemd service for automatic startup
- Configures proper labels for workflow targeting
- Provides management commands

## Environment Configuration

### Required Secrets

| Secret Name | Description | Required For |
|------------|-------------|--------------|
| `OPENAI_API_KEY` | OpenAI API key for LLM services | Production |
| `JWT_SECRET_KEY` | JWT token signing secret | Production |
| `WEBUI_SECRET_KEY` | WebUI session secret | Production |
| `POSTGRES_PASSWORD` | Database password | Production |
| `OPENSEARCH_PASSWORD` | Search engine password | Production |

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEPLOYMENT_ENV` | `production` | Target environment |
| `PROJECT_NAME` | `ree-ai` | Project identifier |
| `PROJECT_DIR` | `$(pwd)` | Deployment directory |
| `LOG_LEVEL` | `INFO` | Logging level |
| `PRODUCTION_MODE` | `true` | Production mode flag |

## Workflow Configuration

### GitHub Actions Workflow: `.github/workflows/deploy-production.yml`

#### Triggers
- **Push to release branch**: Automatic deployment
- **Manual trigger**: With environment selection and confirmation

#### Jobs
1. **Pre-deployment Validation**
   - Validates branch and prerequisites
   - Checks manual confirmation
   - Validates required secrets

2. **Deployment**
   - Sets up deployment environment
   - Runs portable deployment script
   - Performs post-deployment verification

#### Environment Support
- **Production**: Full production deployment
- **Staging**: Testing environment deployment
- **Development**: Local development setup

## Service Deployment Order

The deployment follows a specific order to ensure dependencies are met:

1. **Infrastructure Services** (30s wait)
   - PostgreSQL
   - Redis  
   - OpenSearch

2. **Service Registry** (15s wait)
   - Core service discovery

3. **Core Services** (15s wait)
   - Core Gateway
   - DB Gateway
   - Auth Service

4. **AI Services** (15s wait)
   - Classification
   - Attribute Extraction
   - Completeness
   - Semantic Chunking

5. **Orchestration** (15s wait)
   - Orchestrator
   - RAG Service

6. **Frontend** (10s wait)
   - Open WebUI

## Health Monitoring

### Health Check Endpoints

| Service | Endpoint | Critical |
|---------|----------|----------|
| Service Registry | `http://localhost:8000/health` | Yes |
| Core Gateway | `http://localhost:8080/health` | Yes |
| DB Gateway | `http://localhost:8081/health` | No |
| Orchestrator | `http://localhost:8090/health` | No |
| RAG Service | `http://localhost:8091/health` | No |
| Open WebUI | `http://localhost:3000` | Yes |

### Health Check Process
1. Wait for service to start (configurable timeout)
2. Perform HTTP health check
3. Classify as healthy/unhealthy
4. For critical services: fail deployment if unhealthy
5. For non-critical: log warning and continue

## Error Handling

### Deployment Failures
- **Pre-deployment**: Fails fast with clear error message
- **Infrastructure**: Rolls back and shows service logs
- **Services**: Continues with partial deployment, reports issues
- **Post-deployment**: Shows service status and troubleshooting info

### Recovery Procedures
```bash
# View deployment logs
docker-compose logs [service]

# Restart failed services
docker-compose restart [service]

# Full restart
docker-compose down && docker-compose up -d

# Emergency rollback
git checkout [previous-commit]
./scripts/deploy-production.sh
```

## Monitoring & Maintenance

### Service Management

```bash
# View all services status
docker-compose ps

# View logs for specific service
docker-compose logs -f core-gateway

# Restart service
docker-compose restart rag-service

# Update single service
docker-compose up -d --no-deps rag-service

# Full system restart
docker-compose down && docker-compose up -d
```

### System Health

```bash
# Check system resources
docker stats

# View service resource usage
docker-compose top

# Check disk usage
df -h
docker system df

# Clean up old images/containers
docker system prune -f
```

## Troubleshooting

### Common Issues

#### 1. Secret Not Found
```bash
# Error: Required environment variable 'OPENAI_API_KEY' is not set
./scripts/setup-secrets.sh validate
./scripts/setup-secrets.sh set OPENAI_API_KEY
```

#### 2. Service Won't Start
```bash
# Check logs
docker-compose logs [service]

# Check resource usage
docker stats

# Restart service
docker-compose restart [service]
```

#### 3. Health Check Failures
```bash
# Check service status
curl -f http://localhost:8080/health

# View detailed logs
docker-compose logs -f core-gateway

# Check port conflicts
netstat -tulpn | grep :8080
```

#### 4. Runner Offline
```bash
# Check runner status
sudo systemctl status actions.runner.tmone-ree-ai.production-runner

# Restart runner
sudo systemctl restart actions.runner.tmone-ree-ai.production-runner

# View runner logs
journalctl -f -u actions.runner.tmone-ree-ai.production-runner
```

### Debug Mode

```bash
# Deploy with debug logging
./scripts/deploy-production.sh --log-level DEBUG

# View detailed deployment logs
docker-compose logs -f

# Interactive debugging
docker-compose exec core-gateway bash
```

## Security Best Practices

### 1. Secrets Management
- ✅ Use GitHub Secrets for sensitive data
- ✅ Rotate secrets regularly
- ✅ Never commit secrets to repository
- ✅ Use strong, generated passwords

### 2. Network Security
- ✅ Configure firewall rules
- ✅ Use HTTPS in production
- ✅ Restrict access to internal services
- ✅ Monitor network traffic

### 3. Container Security
- ✅ Use official base images
- ✅ Regular security updates
- ✅ Run containers as non-root
- ✅ Scan images for vulnerabilities

## Performance Optimization

### 1. Resource Management
```bash
# Optimize Docker resources
docker-compose --profile production up -d

# Monitor resource usage
docker stats

# Tune container limits
# Edit docker-compose.yml with mem_limit, cpus
```

### 2. Service Scaling
```bash
# Scale specific services
docker-compose up -d --scale rag-service=3

# Load balance with nginx
# Configure nginx upstream
```

### 3. Database Optimization
- Configure PostgreSQL for production workload
- Optimize OpenSearch cluster settings
- Set up Redis clustering if needed

## Backup & Recovery

### 1. Database Backup
```bash
# PostgreSQL backup
docker-compose exec postgres pg_dump -U ree_ai_user ree_ai > backup.sql

# Restore PostgreSQL
docker-compose exec -T postgres psql -U ree_ai_user ree_ai < backup.sql
```

### 2. Configuration Backup
```bash
# Backup configuration
tar -czf ree-ai-config-$(date +%Y%m%d).tar.gz .env docker-compose.yml

# Backup OpenSearch indices
curl -X PUT "localhost:9200/_snapshot/backup/snapshot_$(date +%Y%m%d)"
```

### 3. Full System Backup
```bash
# Create complete backup
./scripts/backup-system.sh

# Restore from backup
./scripts/restore-system.sh backup-20241112.tar.gz
```

## Advanced Configuration

### Custom Environments

Create custom environment configurations:

```bash
# Create staging environment
./scripts/setup-secrets.sh setup --environment staging

# Deploy to staging
./scripts/deploy-production.sh --env staging
```

### Multi-Server Deployment

For distributed deployment across multiple servers:

1. Set up Docker Swarm or Kubernetes
2. Configure load balancer
3. Set up shared storage for persistent data
4. Configure service discovery

### CI/CD Integration

Integrate with other CI/CD tools:

```yaml
# Jenkins pipeline
pipeline {
  agent any
  stages {
    stage('Deploy') {
      steps {
        sh './scripts/deploy-production.sh'
      }
    }
  }
}

# GitLab CI
deploy:
  script:
    - ./scripts/deploy-production.sh --env production
  only:
    - release
```

## Changelog

### v1.0.0 - Initial Release
- ✅ Portable deployment scripts
- ✅ GitHub Actions integration
- ✅ Secrets management
- ✅ Health monitoring
- ✅ Error handling

### Future Enhancements
- 🔄 Blue-green deployment
- 🔄 Automated rollback
- 🔄 Multi-region deployment
- 🔄 Kubernetes support
- 🔄 Advanced monitoring with Prometheus/Grafana

---

**Need Help?**
- 📖 Check the [troubleshooting section](#troubleshooting)
- 🐛 Report issues on GitHub
- 📧 Contact the development team
- 📝 Check deployment logs: `docker-compose logs`
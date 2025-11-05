# REE AI Deployment Guide

This guide explains how to deploy REE AI using GitHub Actions with self-hosted runners.

## Prerequisites

- Self-hosted runner configured on WSL/Linux server
- Docker and Docker Compose installed
- GitHub repository with Actions enabled

## Deployment Architecture

REE AI uses **GitHub Actions with self-hosted runners** for automated deployment to your own server/WSL environment.

### Why Self-hosted Runner?

- **Full control**: Deploy to your own infrastructure
- **No usage limits**: Unlike GitHub-hosted runners
- **Direct access**: Runner has access to local Docker daemon
- **Cost-effective**: No cloud costs for simple deployments

## Setup Instructions

### 1. Configure Self-hosted Runner

If you haven't set up a runner yet, follow these steps:

```bash
# Create runner directory
mkdir -p ~/actions-runner && cd ~/actions-runner

# Download runner (Linux x64)
curl -o actions-runner-linux-x64-2.321.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.321.0/actions-runner-linux-x64-2.321.0.tar.gz

# Extract
tar xzf ./actions-runner-linux-x64-2.321.0.tar.gz

# Configure (get token from GitHub repo Settings > Actions > Runners > New runner)
./config.sh --url https://github.com/YOUR_USERNAME/ree-ai --token YOUR_TOKEN

# Install as service (auto-start on boot)
sudo ./svc.sh install
sudo ./svc.sh start

# Check status
sudo ./svc.sh status
```

### 2. Configure GitHub Secrets

Go to: `https://github.com/YOUR_USERNAME/ree-ai/settings/secrets/actions`

Add the following secrets:

#### Required Secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `OPENAI_API_KEY` | OpenAI API key for LLM access | `sk-proj-...` |
| `POSTGRES_PASSWORD` | PostgreSQL database password | `ree_ai_pass_2025` |
| `WEBUI_SECRET_KEY` | Open WebUI session secret | `random-string-here` |

#### Optional Secrets (have defaults):

| Secret Name | Description | Default Value |
|-------------|-------------|---------------|
| `POSTGRES_DB` | PostgreSQL database name | `ree_ai` |
| `POSTGRES_USER` | PostgreSQL username | `ree_ai_user` |
| `OPENSEARCH_PASSWORD` | OpenSearch admin password | `Admin123!@#` |
| `TASK_MODEL` | Ollama model for auto-generation | `llama3.2:latest` |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing | `false` |
| `LANGCHAIN_API_KEY` | LangSmith API key | (empty) |

### 3. Deployment Workflow

The deployment workflow (`.github/workflows/deploy.yml`) automatically triggers on:

- **Push to main branch** (e.g., after merging PR)
- **Manual trigger** (via GitHub Actions UI)

#### Deployment Steps:

```
1. Checkout code
2. Create .env from secrets
3. Stop existing services
4. Build Docker images
5. Start services in order:
   ├─ Infrastructure (PostgreSQL, Redis, OpenSearch, Ollama)
   ├─ Service Registry
   ├─ Core Services (Core Gateway, DB Gateway, Auth)
   ├─ AI Services (Chunking, Classification, etc.)
   ├─ Orchestrator & RAG Service
   └─ API Gateway & Open WebUI
6. Health checks for each layer
7. Pull Ollama models
8. Show deployment summary
```

### 4. Trigger Deployment

#### Automatic Deployment (Recommended):

```bash
# Merge PR to main
git checkout main
git pull origin main
git merge feature/my-feature
git push origin main
# 👆 This automatically triggers deployment
```

#### Manual Deployment:

1. Go to: `https://github.com/YOUR_USERNAME/ree-ai/actions`
2. Select **"Deploy to Production"** workflow
3. Click **"Run workflow"**
4. Select branch: `main`
5. Click **"Run workflow"**

### 5. Monitor Deployment

Watch deployment progress:

```bash
# On your WSL/server
cd ~/actions-runner/_work/ree-ai/ree-ai

# Watch logs in real-time
docker-compose logs -f

# Check specific service
docker-compose logs -f orchestrator
docker-compose logs -f core-gateway

# Check all services status
docker-compose ps
```

Or view logs in GitHub Actions UI:
- `https://github.com/YOUR_USERNAME/ree-ai/actions`

## Access Deployed Services

After successful deployment:

| Service | URL | Description |
|---------|-----|-------------|
| Open WebUI | http://localhost:3000 | Main chat interface |
| API Gateway | http://localhost:8888 | REST API endpoint |
| Service Registry | http://localhost:8000 | Service discovery |
| Orchestrator | http://localhost:8090 | AI routing layer |
| RAG Service | http://localhost:8091 | RAG pipeline |
| OpenSearch | http://localhost:9200 | Search & vector DB |
| PostgreSQL | localhost:5432 | User data DB |
| Redis | localhost:6379 | Cache layer |

## Troubleshooting

### Runner is offline

```bash
# Check runner status
sudo systemctl status actions.runner.*

# Restart runner service
sudo ./svc.sh stop
sudo ./svc.sh start
```

### Deployment failed

```bash
# View GitHub Actions logs in browser
# Or check local logs:

docker-compose logs --tail=100 service-registry
docker-compose logs --tail=100 orchestrator

# Check Service Registry
curl http://localhost:8000/health
curl http://localhost:8000/services
```

### Services not starting

```bash
# Check .env file exists
ls -la .env

# Check Docker
docker ps
docker-compose ps

# Restart specific service
docker-compose restart orchestrator

# Full restart
docker-compose down
docker-compose up -d
```

### Port conflicts

```bash
# Check what's using a port
sudo lsof -i :3000
sudo lsof -i :8090

# Kill process if needed
sudo kill -9 <PID>
```

## Rollback

If deployment fails and you need to rollback:

```bash
# 1. Find previous working commit
git log --oneline

# 2. Revert to that commit
git revert <commit-hash>
git push origin main
# This triggers automatic re-deployment

# Or manually:
cd ~/actions-runner/_work/ree-ai/ree-ai
git checkout <previous-commit>
docker-compose down
docker-compose up -d --build
```

## Manual Deployment (Without GitHub Actions)

If you prefer manual deployment:

```bash
# 1. SSH to server
ssh user@your-server

# 2. Navigate to project
cd /path/to/ree-ai

# 3. Pull latest code
git pull origin main

# 4. Create/update .env file
cp .env.example .env
nano .env  # Edit values

# 5. Deploy
docker-compose down
docker-compose build --parallel
docker-compose up -d

# 6. Check status
docker-compose ps
docker-compose logs -f
```

## Continuous Deployment Best Practices

1. **Always use feature branches**
   ```bash
   git checkout -b feature/new-feature
   # Make changes
   git commit -m "feat: add new feature"
   git push origin feature/new-feature
   # Create PR, review, then merge to main
   ```

2. **Test before merging to main**
   - Run tests locally: `./scripts/run-tests.sh`
   - CI tests run automatically on PR
   - Only merge if tests pass

3. **Monitor after deployment**
   - Check health endpoints
   - Review logs for errors
   - Test critical user flows

4. **Backup before major changes**
   ```bash
   # Backup databases
   docker exec ree-ai-postgres pg_dump -U ree_ai_user ree_ai > backup.sql

   # Backup OpenSearch data
   docker exec ree-ai-opensearch curl -X POST "localhost:9200/_snapshot/backup"
   ```

## Environment-specific Configuration

For different environments (dev, staging, production):

### Option 1: Multiple Runners

Set up separate runners with different labels:

```bash
# Dev runner
./config.sh --url ... --labels self-hosted,Linux,X64,dev

# Production runner
./config.sh --url ... --labels self-hosted,Linux,X64,production
```

Then in workflow:
```yaml
jobs:
  deploy-dev:
    runs-on: [self-hosted, dev]

  deploy-prod:
    runs-on: [self-hosted, production]
```

### Option 2: Environment Secrets

Use GitHub Environments:
1. Go to repo Settings > Environments
2. Create environments: `development`, `production`
3. Add environment-specific secrets
4. Require approval for production deployments

## Security Considerations

1. **Never commit secrets to Git**
   - Use GitHub Secrets for sensitive values
   - Add `.env` to `.gitignore` (already done)

2. **Secure your runner**
   ```bash
   # Run runner as non-root user
   # Keep runner updated
   cd ~/actions-runner
   ./config.sh remove
   # Download latest version, reconfigure
   ```

3. **Use HTTPS in production**
   - Set up reverse proxy (nginx/traefik)
   - Get SSL certificate (Let's Encrypt)
   - Update Open WebUI URL

4. **Firewall configuration**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 22/tcp    # SSH
   sudo ufw allow 80/tcp    # HTTP
   sudo ufw allow 443/tcp   # HTTPS
   sudo ufw enable
   ```

## Monitoring & Alerts

Set up monitoring for production:

1. **Health check monitoring**
   - Use Uptime Robot / Pingdom
   - Monitor: http://your-server:3000

2. **Log aggregation**
   - Set up centralized logging (e.g., ELK Stack)
   - Send logs to cloud (e.g., Papertrail, Loggly)

3. **Error tracking**
   - Configure Sentry (see `SENTRY_DSN` in config)
   - Get alerts for application errors

4. **Resource monitoring**
   ```bash
   # Install monitoring tools
   docker stats  # Real-time container stats
   htop         # CPU/Memory usage
   ```

## Support

For issues:
- Check logs: `docker-compose logs -f`
- Review docs: `/docs` directory
- Open issue: https://github.com/YOUR_USERNAME/ree-ai/issues

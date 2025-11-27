# Production Server Configuration - 103.153.74.213

## ⚠️ CRITICAL RULES - DO NOT VIOLATE

1. **NEVER stop, restart, or kill containers/images NOT belonging to `ree-ai` project**
2. **Shared server** - Multiple projects running, only manage `ree-ai-*` containers
3. **Port range**: Use 7xxx for ree-ai services to avoid conflicts

## Server Access

- **Host**: 103.153.74.213
- **SSH Key**: `C:\Users\dev\.ssh\tmone`
- **User**: root
- **Connection**: `ssh -i "C:\Users\dev\.ssh\tmone" root@103.153.74.213`

## Project Location

- **Path**: `/opt/ree-ai`
- **Note**: NOT a git repository, manual deployment via SCP

## External Dependencies (DO NOT TOUCH)

### OpenSearch Cluster (Shared - Other Projects)
- **Containers**: `opensearch-node1`, `opensearch-node2` (NOT ree-ai containers)
- **Network**: `opensearch_opensearch-net`
- **Compose File**: `/app/opensearch/docker-compose.yaml`
- **Credentials**: admin/realWorldAsset@2025
- **Ports**: 9200 (REST API), 9600 (Performance Analyzer)
- **Data Volumes**: 
  - `opensearch_opensearch-data1`
  - `opensearch_opensearch-data2`
- **Status**: Contains production data for multiple projects
- **⚠️ WARNING**: Never stop/remove these containers or volumes

### OpenSearch Dashboards (Shared)
- **Container**: `opensearch-dashboards`
- **URL**: http://103.153.74.213:5601
- **Network**: `opensearch_opensearch-net`
- **Credentials**: admin/realWorldAsset@2025

### PostgreSQL (Shared)
- **Container**: `ree-ai-postgres`
- **Password**: `ree_ai_password_2024` (NOT ree_ai_pass_2025)
- **Port**: 5433 (external) → 5432 (internal)
- **Database**: ree_ai
- **User**: ree_ai_user

## REE-AI Services

### Service Registry
| Service | Container | Port | Network |
|---------|-----------|------|---------|
| Open WebUI | ree-ai-open-webui | 3000 | ree-ai_ree-ai-network |
| Orchestrator | ree-ai-orchestrator | 8090 | ree-ai_ree-ai-network |
| Core Gateway | ree-ai-core-gateway | 7003 | ree-ai_ree-ai-network |
| DB Gateway | ree-ai-db-gateway | 7004 | ree-ai_ree-ai-network + opensearch_opensearch-net |
| RAG Service | ree-ai-rag-service | 8091 | ree-ai_ree-ai-network |
| Classification | ree-ai-classification | 7005 | ree-ai_ree-ai-network |
| Attribute Extraction | ree-ai-attribute-extraction | 8084 | ree-ai_ree-ai-network |
| Redis | ree-ai-redis | 7379 | ree-ai_ree-ai-network |
| OpenSearch (Internal) | ree-ai-opensearch | 7200, 7600 | ree-ai_ree-ai-network |

## Network Configuration

### ree-ai_ree-ai-network
- **Type**: Bridge
- **Aliases**:
  - orchestrator
  - postgres
  - classification
  - rag-service
  - attribute-extraction
  - db-gateway

### opensearch_opensearch-net
- **Purpose**: Connect to shared OpenSearch cluster
- **Connected Services**: 
  - ree-ai-db-gateway (to access opensearch-node1/node2)

## Environment Variables (.env)

### Database
```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ree_ai
POSTGRES_USER=ree_ai_user
POSTGRES_PASSWORD=ree_ai_password_2024
```

### OpenSearch (Production - Shared Cluster)
```env
OPENSEARCH_HOST=opensearch-node1
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=realWorldAsset@2025
OPENSEARCH_USE_SSL=true
OPENSEARCH_VERIFY_CERTS=false
OPENSEARCH_PROPERTIES_INDEX=properties
```

### Redis
```env
REDIS_HOST=redis
REDIS_PORT=6379  # Internal port
```

## Port Mappings (Changed from defaults)

- Redis: 6379 → **7379** (avoid conflict)
- OpenSearch: 9200 → **7200**, 9600 → **7600** (avoid conflict)
- PostgreSQL: 5432 → **5433** (shared instance)
- Open WebUI: 8080 → **3000** (configured differently)

## Deployment Process

1. **Build locally** (if needed):
   ```bash
   cd d:\Crastonic\ree-ai
   docker compose build
   ```

2. **Copy files to server**:
   ```bash
   scp -i "C:\Users\dev\.ssh\tmone" -r services/ root@103.153.74.213:/opt/ree-ai/
   scp -i "C:\Users\dev\.ssh\tmone" -r shared/ root@103.153.74.213:/opt/ree-ai/
   scp -i "C:\Users\dev\.ssh\tmone" -r core/ root@103.153.74.213:/opt/ree-ai/
   scp -i "C:\Users\dev\.ssh\tmone" docker-compose.yml root@103.153.74.213:/opt/ree-ai/
   ```

3. **Build on server**:
   ```bash
   ssh -i "C:\Users\dev\.ssh\tmone" root@103.153.74.213 "cd /opt/ree-ai && docker compose build --parallel"
   ```

4. **Start services**:
   ```bash
   ssh -i "C:\Users\dev\.ssh\tmone" root@103.153.74.213 "cd /opt/ree-ai && docker compose up -d"
   ```

## Critical Network Setup for DB Gateway

DB Gateway needs access to **both networks**:

```bash
# Connect to shared OpenSearch network
docker network connect opensearch_opensearch-net ree-ai-db-gateway

# Restart to apply
docker restart ree-ai-db-gateway
```

## Health Checks

```bash
# DB Gateway (should show property_count > 0)
curl http://localhost:7004/health

# OpenSearch Cluster
curl -u admin:realWorldAsset@2025 -k https://localhost:9200/_cluster/health

# Properties Index
curl -u admin:realWorldAsset@2025 -k https://localhost:9200/properties/_count
```

## User Access

- **Open WebUI**: http://103.153.74.213:3000
- **Model**: ree-ai-assistant
- **Test Query**: "i want to find a house in ho chi minh city"

## Troubleshooting

### Service cannot connect to OpenSearch
1. Check if opensearch-node1/node2 are running
2. Verify db-gateway is in opensearch_opensearch-net network
3. Check credentials: admin/realWorldAsset@2025

### Service cannot connect to PostgreSQL
1. Check password is `ree_ai_password_2024` (NOT ree_ai_pass_2025)
2. Verify container is connected to ree-ai_ree-ai-network with `postgres` alias

### Service DNS resolution fails
1. Check network aliases in docker-compose.yml
2. Reconnect services to network with proper aliases:
   ```bash
   docker network connect --alias <service-name> ree-ai_ree-ai-network <container>
   ```

## Data Backup

### OpenSearch Data Locations
- Volume: `opensearch_opensearch-data1`, `opensearch_opensearch-data2`
- Path: `/var/lib/docker/volumes/opensearch_opensearch-data1/_data`
- **⚠️ Contains production data for multiple projects**

### Important Files on Server
- `/opt/ree-ai/.env` - Environment variables
- `/opt/ree-ai/docker-compose.yml` - Service definitions
- `/app/opensearch/docker-compose.yaml` - Shared OpenSearch config

## Lessons Learned

1. ❌ **DO NOT** stop/remove containers not belonging to ree-ai
2. ❌ **DO NOT** assume localhost in container = host machine
3. ❌ **DO NOT** use default ports without checking conflicts
4. ✅ **DO** check network connectivity before troubleshooting
5. ✅ **DO** verify environment variables are loaded (restart may not reload .env)
6. ✅ **DO** use `docker compose up -d --no-deps <service>` to recreate single service
7. ✅ **DO** connect db-gateway to opensearch_opensearch-net for external OpenSearch access

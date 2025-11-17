# Port Externalization Implementation for REE AI

## 🎯 What Was Changed

### 1. Environment Variables Added to .env.production
```bash
# All ports are now configurable via environment variables
SERVICE_REGISTRY_PORT=7000
OPEN_WEBUI_PORT=7001
DB_GATEWAY_PORT=7002
CLASSIFICATION_PORT=7003
AUTH_SERVICE_PORT=7004
ATTRIBUTE_EXTRACTION_PORT=7005
COMPLETENESS_PORT=7006
CORE_GATEWAY_PORT=7007
RAG_SERVICE_PORT=7008
ORCHESTRATOR_PORT=7009
MONITORING_PORT=7010
INTERNAL_PORT=8080
```

### 2. Docker Compose Updated
All port mappings now use variables:
```yaml
# Before (hardcoded)
ports:
  - "8000:8080"

# After (configurable)  
ports:
  - "${SERVICE_REGISTRY_PORT:-7000}:${INTERNAL_PORT:-8080}"
```

### 3. Port Configuration Script Created
`configure-ports.sh` - Management tool for port changes:

```bash
# Apply clean 7xxx range (recommended)
./configure-ports.sh 7xxx

# Apply conflict-free 8xxx ports  
./configure-ports.sh 8xxx

# Check conflicts on server
./configure-ports.sh check 103.153.74.213 "C:\\Users\\dev\\.ssh\\tmone"

# Show current config
./configure-ports.sh show

# Generate deployment URLs
./configure-ports.sh urls 103.153.74.213
```

## 🚀 Benefits

### ✅ No Rebuild Required
Change ports by editing `.env.production` and restart containers:
```bash
# Change ports
echo "OPEN_WEBUI_PORT=8080" >> .env.production

# Restart services (no rebuild)
docker compose down && docker compose up -d
```

### ✅ Environment-Specific Configs
```bash
# Development
OPEN_WEBUI_PORT=3000

# Staging  
OPEN_WEBUI_PORT=7001

# Production
OPEN_WEBUI_PORT=80
```

### ✅ Conflict Resolution
```bash
# Check what's busy on server
./configure-ports.sh check 103.153.74.213 "C:\\Users\\dev\\.ssh\\tmone"

# Apply clean range
./configure-ports.sh 7xxx
```

### ✅ Easy Migration
```bash
# Current: Mixed ports with conflicts
SERVICE_REGISTRY_PORT=8000  # May conflict
OPEN_WEBUI_PORT=3001       # Mixed range

# Clean: Consistent range, no conflicts  
SERVICE_REGISTRY_PORT=7000  # Clean range
OPEN_WEBUI_PORT=7001       # Consistent
```

## 🔧 Implementation Details

### Default Port Mappings
| Service | Default | Range | Configurable Via |
|---------|---------|-------|------------------|
| Service Registry | 7000 | 7xxx | SERVICE_REGISTRY_PORT |
| Open WebUI | 7001 | 7xxx | OPEN_WEBUI_PORT |
| DB Gateway | 7002 | 7xxx | DB_GATEWAY_PORT |
| Classification | 7003 | 7xxx | CLASSIFICATION_PORT |
| Auth Service | 7004 | 7xxx | AUTH_SERVICE_PORT |
| Attribute Extract | 7005 | 7xxx | ATTRIBUTE_EXTRACTION_PORT |
| Completeness | 7006 | 7xxx | COMPLETENESS_PORT |
| Core Gateway | 7007 | 7xxx | CORE_GATEWAY_PORT |
| RAG Service | 7008 | 7xxx | RAG_SERVICE_PORT |
| Orchestrator | 7009 | 7xxx | ORCHESTRATOR_PORT |
| Monitoring | 7010 | 7xxx | MONITORING_PORT |

### Container Internal Port
All services use consistent internal port:
```bash
INTERNAL_PORT=8080  # All containers listen on 8080 internally
```

## 📋 Usage Examples

### Quick Setup (Clean 7xxx range)
```bash
./configure-ports.sh 7xxx
docker compose up -d
```

### Check Current Status
```bash
./configure-ports.sh show
./configure-ports.sh urls 103.153.74.213
```

### Handle Conflicts
```bash
# Check server
./configure-ports.sh check 103.153.74.213 "C:\\Users\\dev\\.ssh\\tmone"

# If conflicts found, use alternative range
./configure-ports.sh 8xxx
```

This implementation makes REE AI deployment flexible and conflict-resistant across different environments!
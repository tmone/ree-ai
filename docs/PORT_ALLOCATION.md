# REE AI Production Port Allocation

## Server Current Usage (103.153.74.213)
```
OCCUPIED PORTS:
22    - SSH
80    - Nginx HTTP
443   - Nginx HTTPS
3306  - MySQL
5432  - PostgreSQL
5601  - OpenSearch Dashboards
6379  - DragonflyDB (Redis)
8080  - Debezium UI (CONFLICT AVOIDED)
8083  - Debezium Connect (CONFLICT AVOIDED) 
9200  - OpenSearch
9600  - OpenSearch
```

## REE AI Port Assignments (Conflict-Free)
```
SERVICE                 PORT    STATUS
─────────────────────────────────────────
service-registry        8000    ✅ Available
core-gateway           8090    ✅ Available (moved from 8080)
db-gateway             8081    ✅ Available
orchestrator           8092    ✅ Available
classification         8084    ✅ Available (moved from 8083)
completeness           8089    ✅ Available
attribute-extraction   8086    ✅ Available
auth-service           8085    ✅ Available
open-webui             3001    ✅ Available (moved from 3000)
rag-service            8091    ✅ Available
monitoring-service     9998    ✅ Available (moved from 9999)
```

## Access URLs After Deployment
```
🌐 Open WebUI:         http://103.153.74.213:3001
📊 Monitoring:         http://103.153.74.213:9998
🔧 Service Registry:   http://103.153.74.213:8000
🤖 Core Gateway:       http://103.153.74.213:8090
🗄️  DB Gateway:        http://103.153.74.213:8081
🎭 Orchestrator:       http://103.153.74.213:8092
🏷️  Classification:    http://103.153.74.213:8084
✅ Completeness:       http://103.153.74.213:8089
🔍 Attribute Extract:  http://103.153.74.213:8086
🔐 Auth Service:       http://103.153.74.213:8085
📚 RAG Service:        http://103.153.74.213:8091
```

## Conflicts Resolved
- ❌ Port 8080 → ✅ Port 8090 (Core Gateway)
- ❌ Port 8083 → ✅ Port 8084 (Classification) 
- ❌ Port 3000 → ✅ Port 3001 (Open WebUI)
- ❌ Port 9999 → ✅ Port 9998 (Monitoring)

All ports are now conflict-free and ready for deployment!
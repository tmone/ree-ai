# Integrated Search Pipeline Deployment Guide

**CTO Priority 3 + 4 Integration: Hybrid Search + ML-Based Re-ranking**

## Overview

Complete deployment guide for the integrated search pipeline with:
- Hybrid Search (BM25 + Vector)
- ML-Based Re-ranking (5 features)
- Real-time Analytics Tracking
- User Personalization

## Architecture

```
User Query
    ↓
Orchestrator (8090)
    ├── Classification
    ├── Attribute Extraction
    └── Search Pipeline:
        ├── DB Gateway (8081): Hybrid Search
        ├── Reranking Service (8087): ML Scoring
        └── Analytics Tracking
    ↓
Final Ranked Results
```

## Prerequisites

1. **Docker & Docker Compose** installed
2. **PostgreSQL** with reranking Phase 2 tables
3. **OpenSearch** with properties index
4. **Environment Variables** configured

## Step 1: Database Setup

### 1.1 Run Migration

The reranking Phase 2 requires 4 new tables:

```bash
# Check if tables exist
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "\dt" | grep -E "seller_stats|property_stats|user_preferences|search_interactions"

# If tables don't exist, run migration
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -f /docker-entrypoint-initdb.d/014_reranking_phase2_tables.sql
```

### 1.2 Verify Tables

```sql
-- Connect to database
docker exec -it ree-ai-postgres psql -U ree_ai_user -d ree_ai

-- Check tables
\dt

-- Expected tables:
-- seller_stats
-- property_stats
-- user_preferences
-- search_interactions
```

### 1.3 Sample Data

The migration includes sample data for testing:
- 3 sellers (seller_123, seller_456, seller_789)
- 3 properties (prop_1, prop_2, prop_3)
- 1 test user (user_123)

## Step 2: Service Configuration

### 2.1 Environment Variables

Ensure `.env` file has:

```bash
# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ree_ai
POSTGRES_USER=ree_ai_user
POSTGRES_PASSWORD=your_secure_password

# OpenSearch
OPENSEARCH_HOST=opensearch
OPENSEARCH_PORT=9200

# Services
DEBUG=true
LOG_LEVEL=INFO
```

### 2.2 Docker Compose Services

Required services in `docker-compose.yml`:

```yaml
services:
  # Database
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    volumes:
      - ./shared/database/migrations:/docker-entrypoint-initdb.d

  # Search
  opensearch:
    image: opensearchproject/opensearch:2.11.0
    ports:
      - "9200:9200"

  # DB Gateway (Hybrid Search)
  db-gateway:
    build: ./services/db_gateway
    ports:
      - "8081:8080"
    depends_on:
      - postgres
      - opensearch

  # Reranking Service
  reranking:
    build: ./services/reranking
    ports:
      - "8087:8080"
    depends_on:
      - postgres
    environment:
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=ree_ai
      - POSTGRES_USER=ree_ai_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

  # Orchestrator
  orchestrator:
    build: ./services/orchestrator
    ports:
      - "8090:8080"
    depends_on:
      - db-gateway
      - reranking
```

## Step 3: Build & Deploy

### 3.1 Build Services

```bash
# Build all services
docker-compose build

# Or build specific services
docker-compose build orchestrator
docker-compose build db-gateway
docker-compose build reranking
```

### 3.2 Start Services

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f orchestrator
docker-compose logs -f reranking
docker-compose logs -f db-gateway
```

### 3.3 Verify Services

```bash
# Orchestrator
curl http://localhost:8090/health

# DB Gateway
curl http://localhost:8081/health

# Reranking Service
curl http://localhost:8087/health

# Expected reranking response:
# {
#   "status": "healthy",
#   "service": "reranking",
#   "version": "1.0.0-phase2",
#   "phase": "Phase 2: Real Data Integration",
#   "database_connected": true,
#   "feature_weights": {
#     "property_quality": 0.4,
#     "seller_reputation": 0.2,
#     "freshness": 0.15,
#     "engagement": 0.15,
#     "personalization": 0.1
#   }
# }
```

## Step 4: Testing

### 4.1 Run E2E Tests

```bash
# Run comprehensive E2E tests
python tests/test_search_pipeline_e2e.py

# Expected output:
# [PASS] Orchestrator is healthy
# [PASS] Hybrid search working
# [PASS] Re-ranking working
# [PASS] End-to-end search working
# [PASS] Analytics tracking operational
# [PASS] Performance test complete
```

### 4.2 Manual Testing

#### Test Hybrid Search

```bash
curl -X POST http://localhost:8081/hybrid-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "can ho quan 1",
    "filters": {},
    "limit": 5
  }' \
  -G --data-urlencode "alpha=0.3"
```

#### Test Reranking

```bash
curl -X POST http://localhost:8087/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "can ho",
    "results": [...],
    "user_id": "test_user"
  }'
```

#### Test Complete Pipeline

```bash
curl -X POST http://localhost:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm căn hộ 2 phòng ngủ ở Quận 1, giá dưới 5 tỷ",
    "user_id": "test_user_123",
    "conversation_id": "test_conv_123"
  }'
```

### 4.3 Test Analytics Tracking

```bash
# Track property view
curl -X POST http://localhost:8087/analytics/view/property_123

# Track property inquiry
curl -X POST http://localhost:8087/analytics/inquiry/property_123

# Track property favorite
curl -X POST http://localhost:8087/analytics/favorite/property_123

# Track property click (updates user preferences)
curl -X POST "http://localhost:8087/analytics/click?user_id=user_123&property_id=property_123&property_price=5000000000&property_district=District%201&property_type=apartment"
```

## Step 5: Monitoring

### 5.1 Check Logs

```bash
# Real-time logs for all services
docker-compose logs -f

# Specific service logs
docker-compose logs -f orchestrator | grep "Hybrid+Rerank"
docker-compose logs -f reranking | grep "Re-ranking"
```

### 5.2 Database Monitoring

```bash
# Check seller stats
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT * FROM seller_stats LIMIT 5;"

# Check property stats
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT property_id, views_total, inquiries_total, favorites_total FROM property_stats LIMIT 5;"

# Check user preferences
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT * FROM user_preferences LIMIT 5;"

# Check search interactions
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT COUNT(*) FROM search_interactions;"
```

### 5.3 Performance Metrics

Monitor in orchestrator logs:
- `[Hybrid Search] Found X results ... in Yms`
- `[Re-ranking] Completed in Zms`
- `[Analytics] Tracking X property views`

Target latencies:
- Hybrid Search: <100ms
- Re-ranking: <50ms
- Total Pipeline: <150ms

## Step 6: Optimization

### 6.1 Tune Hybrid Search Alpha

Adjust BM25 vs Vector weight based on query type:

```python
# In orchestrator
# filter mode: alpha=0.5 (50% BM25, 50% Vector)
# semantic mode: alpha=0.2 (20% BM25, 80% Vector)
# both mode: alpha=0.3 (30% BM25, 70% Vector)
```

Test different alpha values:
```bash
# More BM25 (keyword-heavy)
curl ... -G --data-urlencode "alpha=0.6"

# More Vector (semantic-heavy)
curl ... -G --data-urlencode "alpha=0.2"
```

### 6.2 Tune Reranking Weights

Edit `services/reranking/main.py`:

```python
FEATURE_WEIGHTS = {
    "property_quality": 0.40,    # 40%
    "seller_reputation": 0.20,   # 20%
    "freshness": 0.15,           # 15%
    "engagement": 0.15,          # 15%
    "personalization": 0.10      # 10%
}
```

After changing weights:
```bash
docker-compose restart reranking
```

### 6.3 Database Query Optimization

Add indexes for better performance:

```sql
-- Seller stats queries
CREATE INDEX IF NOT EXISTS idx_seller_stats_response_rate ON seller_stats(response_rate DESC);

-- Property stats queries
CREATE INDEX IF NOT EXISTS idx_property_stats_views_7d ON property_stats(views_7d DESC);
CREATE INDEX IF NOT EXISTS idx_property_stats_ctr ON property_stats(ctr DESC);

-- User preferences queries
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);

-- Search interactions queries
CREATE INDEX IF NOT EXISTS idx_search_interactions_user_property ON search_interactions(user_id, property_id);
CREATE INDEX IF NOT EXISTS idx_search_interactions_timestamp ON search_interactions(timestamp DESC);
```

## Troubleshooting

### Issue 1: Reranking service shows `database_connected: false`

**Solution:**
```bash
# Check PostgreSQL connection
docker logs ree-ai-reranking | grep -i "database\|postgres"

# Verify environment variables
docker exec ree-ai-reranking env | grep POSTGRES

# Restart with correct credentials
docker-compose restart reranking
```

### Issue 2: Hybrid search returns empty results

**Solution:**
```bash
# Check OpenSearch has data
curl http://localhost:9200/properties/_count

# Check vector index
curl http://localhost:9200/properties_vector/_count

# Rebuild indexes if needed
python scripts/reindex_properties.py
```

### Issue 3: Analytics tracking fails

**Solution:**
```bash
# Check tables exist
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "\dt" | grep property_stats

# Check permissions
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT has_table_privilege('ree_ai_user', 'property_stats', 'INSERT');"

# Run migration if missing
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -f /docker-entrypoint-initdb.d/014_reranking_phase2_tables.sql
```

### Issue 4: High latency (>150ms)

**Optimization steps:**
1. Add database indexes (see Section 6.3)
2. Enable database connection pooling
3. Cache frequently accessed data (Redis)
4. Use async queries where possible
5. Monitor slow queries

```bash
# Check slow queries
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
```

## Production Checklist

- [ ] Database migration 014 applied
- [ ] All 4 reranking tables created
- [ ] Sample data inserted for testing
- [ ] Services built and running
- [ ] Health checks passing
- [ ] E2E tests passing
- [ ] Analytics tracking working
- [ ] Performance within targets
- [ ] Monitoring configured
- [ ] Backup strategy for user_preferences & search_interactions

## Next Steps

1. **Monitor Production Metrics:**
   - CTR (Click-Through Rate)
   - User engagement (views, inquiries, favorites)
   - Search satisfaction scores
   - Conversion rates

2. **A/B Testing:**
   - Hybrid vs pure BM25
   - Different alpha values
   - Different reranking weights

3. **Data Collection:**
   - Collect search_interactions for ML training
   - Target: 10,000+ interactions for Phase 3

4. **Phase 3 (Future):**
   - Train LightGBM/LambdaMART model
   - Replace rule-based reranking with ML model
   - Online learning & continuous improvement

## Support

For issues or questions:
- Check logs: `docker-compose logs -f orchestrator reranking`
- Run tests: `python tests/test_search_pipeline_e2e.py`
- Review: `docs/CTO_ARCHITECTURE_IMPLEMENTATION_STATUS.md`

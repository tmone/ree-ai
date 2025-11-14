# Master Data Extraction System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you get the Master Data Extraction System up and running quickly.

## Prerequisites

- Docker Desktop installed
- docker-compose installed
- Git installed
- 4GB RAM minimum
- 10GB disk space

## Step 1: Clone and Configure (1 minute)

```bash
# Clone repository
git clone <repository-url>
cd ree-ai

# Copy environment file
cp .env.example .env

# Edit .env (set your OpenAI API key if using OpenAI)
nano .env  # or use your preferred editor
```

**Required `.env` configuration:**
```bash
# LLM Provider (choose one)
OPENAI_API_KEY=sk-your-key-here          # For OpenAI
# OR
USE_OLLAMA=true                          # For local Ollama (free)

# Database
POSTGRES_USER=ree_ai_user
POSTGRES_PASSWORD=ree_ai_password
POSTGRES_DB=ree_ai

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

## Step 2: Deploy System (3 minutes)

### Option A: Automated Deployment (Recommended)

**Linux/Mac:**
```bash
chmod +x scripts/deploy-master-data-system.sh
./scripts/deploy-master-data-system.sh
```

**Windows:**
```cmd
scripts\deploy-master-data-system.bat
```

This script will:
1. ✅ Check prerequisites
2. ✅ Start PostgreSQL and Redis
3. ✅ Run database migrations
4. ✅ Seed master data
5. ✅ Start extraction and crawler services
6. ✅ Run health checks
7. ✅ Run smoke tests

### Option B: Manual Deployment

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis

# 2. Wait for PostgreSQL
sleep 10

# 3. Run migrations
./scripts/migrate-master-data.sh up

# 4. Start services
docker-compose up -d attribute-extraction crawler-service

# 5. Verify health
./scripts/health-check.sh
```

## Step 3: Verify Installation (1 minute)

### Check Services

```bash
# Attribute Extraction Service
curl http://localhost:8084/health
# Expected: {"status": "healthy"}

# Crawler Service
curl http://localhost:8095/health
# Expected: {"status": "healthy"}
```

### API Documentation

Open in browser:
- **Extraction Service**: http://localhost:8084/docs
- **Crawler Service**: http://localhost:8095/docs

## Quick Usage Examples

### 1. Extract Attributes from Vietnamese Query

```bash
curl -X POST http://localhost:8084/extract-with-master-data \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Căn hộ 2 phòng ngủ Quận 1 có hồ bơi, gym, view sông",
    "confidence_threshold": 0.8,
    "include_suggestions": true
  }'
```

**Response:**
```json
{
  "request_language": "vi",
  "raw": {
    "bedrooms": 2
  },
  "mapped": [
    {
      "property_name": "district",
      "table": "districts",
      "id": 1,
      "value": "District 1",
      "value_translated": "Quận 1",
      "confidence": 0.95,
      "match_method": "exact"
    },
    {
      "property_name": "amenity",
      "table": "amenities",
      "id": 1,
      "value": "swimming_pool",
      "value_translated": "Hồ bơi",
      "confidence": 0.92,
      "match_method": "fuzzy"
    }
  ],
  "new": [],
  "processing_time_ms": 1234
}
```

### 2. View Available Crawlers

```bash
curl http://localhost:8095/crawlers
```

**Response:**
```json
{
  "crawlers": [
    {
      "id": "batdongsan",
      "name": "Batdongsan.com.vn",
      "url": "https://batdongsan.com.vn"
    },
    {
      "id": "mogi",
      "name": "Mogi.vn",
      "url": "https://mogi.vn"
    }
  ]
}
```

### 3. Crawl Real Estate Site (Discover New Master Data)

```bash
curl -X POST http://localhost:8095/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "site": "batdongsan",
    "max_pages": 2,
    "extract_master_data": true,
    "auto_populate": true
  }'
```

**Response:**
```json
{
  "site": "batdongsan",
  "listings_scraped": 24,
  "new_attributes_found": 5,
  "processing_time_ms": 45000,
  "sample_listings": [
    {
      "title": "Căn hộ 2PN Vinhomes Central Park",
      "price": 5500000000,
      "district": "Quận Bình Thạnh",
      "area": 80,
      "bedrooms": 2,
      "amenities": ["swimming_pool", "gym", "parking"]
    }
  ]
}
```

### 4. Review Pending Master Data Items

```bash
curl http://localhost:8084/admin/pending-items?status=pending&limit=10
```

**Response:**
```json
{
  "pending_items": [
    {
      "id": 1,
      "suggested_table": "amenities",
      "suggested_category": "luxury",
      "value_original": "infinity pool",
      "value_english": "infinity_pool",
      "frequency": 12,
      "status": "pending",
      "created_at": "2025-01-13T10:30:00Z"
    }
  ],
  "total_count": 15,
  "high_frequency_items": 3
}
```

### 5. Approve Pending Item (Admin)

```bash
curl -X POST http://localhost:8084/admin/approve-item \
  -H "Content-Type: application/json" \
  -d '{
    "pending_id": 1,
    "translations": {
      "vi": "Hồ bơi vô cực",
      "en": "Infinity pool"
    },
    "admin_user_id": "admin123"
  }'
```

## Common Tasks

### View Logs

```bash
# Extraction service logs
docker-compose logs -f attribute-extraction

# Crawler service logs
docker-compose logs -f crawler-service

# PostgreSQL logs
docker-compose logs -f postgres
```

### Check Database

```bash
# Connect to PostgreSQL
docker exec -it ree-ai-postgres psql -U ree_ai_user -d ree_ai

# Inside psql:
\dt                                # List tables
SELECT COUNT(*) FROM districts;   # Count districts
SELECT * FROM pending_master_data WHERE status='pending';  # Pending items
\q                                 # Quit
```

### Run Health Checks

```bash
./scripts/health-check.sh
```

### Run Integration Tests

```bash
pytest tests/integration/test_extraction_pipeline.py -v
```

### Create Database Backup

```bash
./scripts/migrate-master-data.sh backup my-backup
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop specific service
docker-compose stop attribute-extraction

# Stop and remove volumes (CAUTION: deletes data!)
docker-compose down -v
```

## Troubleshooting

### Issue: Services not starting

**Solution:**
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose build
docker-compose up -d
```

### Issue: Cannot connect to PostgreSQL

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Wait for PostgreSQL to be ready
docker exec ree-ai-postgres pg_isready -U ree_ai_user -d ree_ai
```

### Issue: Extraction endpoint returns 500 error

**Solution:**
```bash
# Check extraction service logs
docker-compose logs attribute-extraction

# Verify database connection
docker exec ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT COUNT(*) FROM districts;"

# Restart extraction service
docker-compose restart attribute-extraction
```

### Issue: Crawler fails to scrape

**Solution:**
```bash
# Check crawler logs
docker-compose logs crawler-service

# Verify Chromium installed
docker exec ree-ai-crawler-service which chromium

# Increase timeout
# Edit docker-compose.yml and add:
# environment:
#   - CRAWL_TIMEOUT=120000
```

### Issue: LLM translation not working

**Solution:**
```bash
# Check OpenAI API key (if using OpenAI)
echo $OPENAI_API_KEY

# Check Core Gateway connection
curl http://localhost:8080/health

# Try Ollama instead (free local LLM)
# Edit .env:
# USE_OLLAMA=true
# OLLAMA_BASE_URL=http://ollama:11434
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ User Query: "Căn hộ 2PN Quận 1 có hồ bơi"                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Language Detection → "vi" (Vietnamese)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. LLM Extraction                                           │
│    - bedrooms: 2                                            │
│    - district: "Quận 1"                                     │
│    - amenity: "hồ bơi"                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Fuzzy Matching (PostgreSQL + fuzzywuzzy)                │
│    - "Quận 1" → districts (id=1, confidence=0.95)          │
│    - "hồ bơi" → amenities (id=1, confidence=0.92)          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 3-Tier Response                                          │
│    {                                                        │
│      "raw": {"bedrooms": 2},                               │
│      "mapped": [                                            │
│        {id: 1, value: "District 1", translated: "Quận 1"}  │
│      ],                                                     │
│      "new": []                                              │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Integrate with Orchestrator**: Update your Orchestrator service to call the new extraction endpoint
2. **Schedule Crawling**: Set up cron jobs to crawl real estate sites weekly
3. **Admin Workflow**: Set up admin dashboard for reviewing pending master data
4. **Monitor Performance**: Set up Grafana dashboards for monitoring
5. **Scale**: Add more crawler sites, expand master data categories

## Documentation

- **Complete Implementation Guide**: `docs/MASTER_DATA_EXTRACTION_COMPLETE_IMPLEMENTATION.md`
- **Crawler Service Guide**: `docs/CRAWLER_SERVICE_IMPLEMENTATION.md`
- **Production Checklist**: `docs/MASTER_DATA_PRODUCTION_CHECKLIST.md`
- **API Documentation**: http://localhost:8084/docs

## Support

- **GitHub Issues**: <repository-url>/issues
- **Documentation**: `docs/`
- **Health Checks**: `./scripts/health-check.sh`

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-01-13

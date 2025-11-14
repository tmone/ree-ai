# Master Data System - Monitoring Setup Guide

## Overview

This guide explains how to set up comprehensive monitoring for the Master Data Extraction System using Prometheus and Grafana.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ Grafana Dashboard (port 3001)                                │
│ ├─ Master Data Growth Dashboard                              │
│ ├─ Extraction Performance Dashboard                          │
│ ├─ Crawler Activity Dashboard                                │
│ └─ System Health Dashboard                                   │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ Prometheus (port 9090)                                       │
│ ├─ Scrapes metrics from services every 15s                   │
│ ├─ Evaluates alert rules                                     │
│ └─ Stores time-series data                                   │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────────┐
│ Services (expose /metrics endpoints)                         │
│ ├─ Attribute Extraction Service (port 8084)                  │
│ ├─ Crawler Service (port 8095)                               │
│ ├─ PostgreSQL Exporter (port 9187)                           │
│ ├─ Redis Exporter (port 9121)                                │
│ └─ Node Exporter (port 9100)                                 │
└──────────────────────────────────────────────────────────────┘
```

## Metrics Collected

### Master Data Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `master_data_total_records{table}` | Gauge | Total records per master data table |
| `master_data_translations_count{table,lang}` | Gauge | Translation counts by table and language |
| `pending_master_data_count{status}` | Gauge | Pending items by status (pending/approved/rejected) |
| `pending_master_data_frequency{value_english,suggested_table}` | Gauge | Frequency of pending items |

### Extraction Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `extraction_requests_total{language,status}` | Counter | Total extraction requests |
| `extraction_request_duration_seconds{language}` | Histogram | Extraction request duration |
| `extraction_errors_total{error_type}` | Counter | Extraction errors by type |

### Fuzzy Matching Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `fuzzy_match_total{attribute_type,match_method}` | Counter | Total fuzzy matches |
| `fuzzy_match_confidence{attribute_type}` | Histogram | Confidence score distribution |
| `fuzzy_match_duration_seconds{attribute_type}` | Histogram | Fuzzy match duration |

### Crawler Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `crawler_listings_scraped_total{site}` | Counter | Total listings scraped per site |
| `crawler_new_attributes_discovered_total{site,attribute_type}` | Counter | New attributes discovered |
| `crawler_errors_total{site,error_type}` | Counter | Crawler errors |
| `crawler_duration_seconds{site}` | Histogram | Crawl duration per site |

### Database Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `database_query_duration_seconds{query_type}` | Histogram | Database query duration |
| `database_errors_total{error_type}` | Counter | Database errors |
| `database_connection_pool_size` | Gauge | Connection pool size |
| `database_connection_pool_available` | Gauge | Available connections |

## Step 1: Add Metrics to Services

### 1.1 Update Attribute Extraction Service

Add metrics collection to `services/attribute_extraction/main.py`:

```python
from prometheus_client import make_asgi_app
from services.attribute_extraction.metrics import (
    track_extraction_request,
    track_fuzzy_match,
    update_master_data_metrics,
    update_database_pool_metrics
)
import asyncio

class AttributeExtractionService(BaseService):
    def __init__(self):
        super().__init__(...)

        # Add background task for metrics
        self.background_tasks = set()

    def setup_routes(self):
        # ... existing routes ...

        # Add Prometheus metrics endpoint
        metrics_app = make_asgi_app()
        self.app.mount("/metrics", metrics_app)

        @self.app.post("/extract-with-master-data")
        async def extract_with_master_data(request: ExtractionRequest):
            start_time = time.time()
            try:
                response = await self.master_data_extractor.extract(request)

                # Track metrics
                duration = time.time() - start_time
                track_extraction_request(
                    language=response.request_language,
                    duration=duration,
                    success=True
                )

                return response
            except Exception as e:
                track_extraction_request(
                    language=request.language or "unknown",
                    duration=time.time() - start_time,
                    success=False
                )
                raise

        @self.app.on_event("startup")
        async def start_metrics_collection():
            """Start background task to collect metrics"""
            task = asyncio.create_task(self.collect_metrics_periodically())
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

    async def collect_metrics_periodically(self):
        """Collect metrics every 60 seconds"""
        while True:
            try:
                await update_master_data_metrics(self.master_data_extractor.db_pool)
                await update_database_pool_metrics(self.master_data_extractor.db_pool)
            except Exception as e:
                self.logger.error(f"Failed to collect metrics: {e}")

            await asyncio.sleep(60)
```

### 1.2 Update Crawler Service

Similar pattern for crawler service - add metrics endpoint and tracking.

## Step 2: Deploy Monitoring Stack

### 2.1 Update docker-compose.yml

Add monitoring services:

```yaml
# Monitoring Stack
prometheus:
  image: prom/prometheus:latest
  container_name: ree-ai-prometheus
  volumes:
    - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    - ./monitoring/prometheus/rules:/etc/prometheus/rules
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--web.console.libraries=/usr/share/prometheus/console_libraries'
    - '--web.console.templates=/usr/share/prometheus/consoles'
  ports:
    - "9090:9090"
  networks:
    - ree-ai-network
  profiles:
    - monitoring
    - all

grafana:
  image: grafana/grafana:latest
  container_name: ree-ai-grafana
  volumes:
    - grafana_data:/var/lib/grafana
    - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_USERS_ALLOW_SIGN_UP=false
  ports:
    - "3001:3000"
  networks:
    - ree-ai-network
  depends_on:
    - prometheus
  profiles:
    - monitoring
    - all

postgres-exporter:
  image: prometheuscommunity/postgres-exporter:latest
  container_name: ree-ai-postgres-exporter
  environment:
    DATA_SOURCE_NAME: "postgresql://ree_ai_user:ree_ai_password@postgres:5432/ree_ai?sslmode=disable"
  ports:
    - "9187:9187"
  networks:
    - ree-ai-network
  depends_on:
    - postgres
  profiles:
    - monitoring
    - all

redis-exporter:
  image: oliver006/redis_exporter:latest
  container_name: ree-ai-redis-exporter
  environment:
    - REDIS_ADDR=redis:6379
  ports:
    - "9121:9121"
  networks:
    - ree-ai-network
  depends_on:
    - redis
  profiles:
    - monitoring
    - all

node-exporter:
  image: prom/node-exporter:latest
  container_name: ree-ai-node-exporter
  ports:
    - "9100:9100"
  networks:
    - ree-ai-network
  profiles:
    - monitoring
    - all

volumes:
  prometheus_data:
  grafana_data:
```

### 2.2 Start Monitoring Stack

```bash
# Start monitoring services
docker-compose --profile monitoring up -d

# Or start everything including monitoring
docker-compose --profile all up -d
```

## Step 3: Configure Grafana

### 3.1 Access Grafana

Open browser: http://localhost:3001

- Username: `admin`
- Password: `admin` (change on first login)

### 3.2 Add Prometheus Data Source

1. Go to Configuration → Data Sources
2. Click "Add data source"
3. Select "Prometheus"
4. Set URL: `http://prometheus:9090`
5. Click "Save & Test"

### 3.3 Import Dashboards

Option A: **Automatic Import** (Recommended)

The dashboard JSON files in `monitoring/grafana/dashboards/` are automatically provisioned on startup.

Option B: **Manual Import**

1. Go to Dashboards → Import
2. Upload `monitoring/grafana/dashboards/master-data-growth.json`
3. Select Prometheus data source
4. Click "Import"

## Step 4: View Metrics

### Grafana Dashboards

Access dashboards at http://localhost:3001:

1. **Master Data Growth Dashboard**
   - Total master data records over time
   - Pending items queue status
   - Translation coverage
   - Top pending items by frequency

2. **Extraction Performance Dashboard**
   - Request rate and duration
   - Error rates
   - Fuzzy match confidence
   - Match method distribution

3. **Crawler Activity Dashboard**
   - Listings scraped over time
   - New attributes discovered
   - Crawler errors
   - Crawl duration

4. **System Health Dashboard**
   - CPU and memory usage
   - Disk space
   - Network I/O
   - Container status

### Prometheus Queries

Access raw metrics at http://localhost:9090:

**Master Data Growth:**
```promql
# Total districts
master_data_total_records{table="districts"}

# Master data growth rate (last 24h)
rate(master_data_total_records{table="amenities"}[24h])

# Pending items requiring review
pending_master_data_count{status="pending"}
```

**Extraction Performance:**
```promql
# Extraction requests per second
rate(extraction_requests_total[5m])

# p95 extraction time
histogram_quantile(0.95, rate(extraction_request_duration_seconds_bucket[5m]))

# Error rate
rate(extraction_errors_total[5m])
```

**Fuzzy Matching:**
```promql
# Median confidence score
histogram_quantile(0.50, rate(fuzzy_match_confidence_bucket[5m]))

# Exact vs fuzzy match ratio
sum(rate(fuzzy_match_total{match_method="exact"}[5m])) /
sum(rate(fuzzy_match_total[5m]))
```

**Crawler Activity:**
```promql
# Listings scraped per day
increase(crawler_listings_scraped_total[24h])

# New attributes discovered per day
increase(crawler_new_attributes_discovered_total[24h])
```

## Step 5: Set Up Alerts

### 5.1 View Alert Rules

Prometheus alerts are defined in:
- `monitoring/prometheus/rules/master-data-alerts.yml`

Access alerts in Prometheus UI:
- http://localhost:9090/alerts

### 5.2 Configure Alert Notifications

#### Email Notifications (SMTP)

Create `monitoring/alertmanager/alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourcompany.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

route:
  receiver: 'email-notifications'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: 'email-notifications'
    email_configs:
      - to: 'oncall-engineer@yourcompany.com'
        headers:
          Subject: '[REE AI] {{ .GroupLabels.alertname }} - {{ .GroupLabels.severity }}'
```

#### Slack Notifications

```yaml
receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#ree-ai-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

### 5.3 Test Alerts

Trigger test alert:

```bash
# Manually trigger high pending items count
curl -X POST http://localhost:8084/admin/test-alert
```

## Step 6: Monitor Production

### Daily Checks

1. **Master Data Growth**
   - Review pending items count
   - Approve/reject high-frequency items
   - Check translation coverage

2. **Performance**
   - Monitor p95 extraction time (< 2000ms target)
   - Check error rates (< 1% target)
   - Review fuzzy match confidence

3. **Crawler Health**
   - Verify scheduled crawls running
   - Check new attribute discovery rate
   - Review crawler errors

### Weekly Reviews

1. **Data Quality**
   - Review master data duplicates
   - Audit translation quality
   - Clean up rejected items

2. **Performance Optimization**
   - Identify slow queries
   - Optimize fuzzy matching thresholds
   - Review cache hit rates

3. **Capacity Planning**
   - Monitor database growth
   - Check disk space trends
   - Review connection pool usage

### Monthly Reports

Generate monthly master data growth report:

```bash
# Export metrics for last 30 days
curl 'http://localhost:9090/api/v1/query_range?query=master_data_total_records&start=...'
```

## Troubleshooting

### Issue: Metrics not appearing in Grafana

**Solution:**
1. Check Prometheus targets: http://localhost:9090/targets
2. Verify all services show as "UP"
3. Check service logs: `docker-compose logs prometheus`

### Issue: High memory usage by Prometheus

**Solution:**
```bash
# Reduce retention period in docker-compose.yml
command:
  - '--storage.tsdb.retention.time=15d'  # Default: 15 days
```

### Issue: Grafana dashboard shows "No data"

**Solution:**
1. Verify Prometheus data source configured
2. Check query syntax in dashboard
3. Verify time range selected

## Best Practices

1. **Regular Backups**
   ```bash
   # Backup Prometheus data
   docker exec ree-ai-prometheus promtool tsdb snapshot /prometheus
   ```

2. **Alert Fatigue Prevention**
   - Set appropriate thresholds
   - Use `for` duration to avoid flapping
   - Group related alerts

3. **Dashboard Organization**
   - One dashboard per domain (master data, extraction, crawler)
   - Use consistent time ranges
   - Add helpful annotations

4. **Metrics Retention**
   - Keep detailed metrics for 15-30 days
   - Aggregate older data for long-term trends

## Reference

- **Prometheus Documentation**: https://prometheus.io/docs/
- **Grafana Documentation**: https://grafana.com/docs/
- **PromQL Tutorial**: https://prometheus.io/docs/prometheus/latest/querying/basics/

---

**Version**: 1.0.0
**Last Updated**: 2025-01-13
**Status**: ✅ Production Ready

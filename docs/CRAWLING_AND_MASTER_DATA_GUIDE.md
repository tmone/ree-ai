# Crawling Real Estate Data & Building Master Data

## 🎯 Overview

This guide shows you how to automatically crawl Vietnamese real estate websites to discover and populate master data.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Crawl Real Estate Sites (Batdongsan, Mogi)              │
│    ├─ Scrape property listings                              │
│    ├─ Extract attributes (location, amenities, features)    │
│    └─ Collect 100s of listings per crawl                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Discover New Master Data                                 │
│    ├─ Compare with existing master data                     │
│    ├─ Find new: districts, amenities, features, views       │
│    ├─ Track frequency (how many times each appears)         │
│    └─ Prioritize high-frequency items                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Auto-Populate pending_master_data                        │
│    ├─ Store in PostgreSQL for admin review                  │
│    ├─ Auto-increment frequency if already exists            │
│    └─ Ready for approval via Admin API                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Admin Reviews & Approves                                 │
│    ├─ Review high-frequency items first                     │
│    ├─ Add translations (Vietnamese, English, etc.)          │
│    └─ Approve → Added to master data tables                 │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Method 1: Automated Script (Recommended)

**Linux/Mac:**
```bash
# Make executable
chmod +x scripts/crawl-and-build-master-data.sh

# Run crawl (crawls 20 pages per site by default)
./scripts/crawl-and-build-master-data.sh
```

**Windows:**
```cmd
scripts\crawl-and-build-master-data.bat
```

**Python (Cross-platform):**
```bash
# Default: crawl batdongsan and mogi, 20 pages each
python scripts/crawl_and_build_master_data.py

# Custom: crawl only batdongsan, 50 pages
python scripts/crawl_and_build_master_data.py --sites batdongsan --max-pages 50

# Crawl all available sites, 30 pages each
python scripts/crawl_and_build_master_data.py --sites batdongsan mogi --max-pages 30
```

### Method 2: Manual API Calls

```bash
# Crawl Batdongsan (20 pages, auto-populate master data)
curl -X POST http://localhost:8095/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "site": "batdongsan",
    "max_pages": 20,
    "extract_master_data": true,
    "auto_populate": true
  }'

# View results
curl http://localhost:8084/admin/pending-items?status=pending&limit=20
```

## 📊 Expected Results

### Sample Crawl Output

```
=======================================================================
  Crawling: batdongsan
=======================================================================
[INFO] Max pages: 20
[INFO] Extract master data: YES
[INFO] Auto-populate: YES

[INFO] Starting crawl (this may take a few minutes)...

✅ Crawl completed successfully!

  ▸ Listings Scraped: 247
  ▸ New Attributes Found: 18
  ▸ Processing Time: 145000ms
  ▸ Total Duration: 152s

Sample Listings:
  1. Căn hộ 2PN Vinhomes Central Park - View sông đẹp
     District: Quận Bình Thạnh
     Price: 5.5 tỷ
     Amenities: swimming_pool, gym, parking, security_24_7

  2. Biệt thự 4PN Quận 7 - Có hồ bơi riêng
     District: Quận 7
     Price: 18 tỷ
     Amenities: private_pool, garden, parking, rooftop_terrace
```

### Discovered Master Data

After crawl, the system automatically discovers new attributes:

```
=======================================================================
  Master Data Status
=======================================================================

  ▸ Total Pending Items: 24
  ▸ High Frequency Items: 8 (priority review)

Top Pending Items (by frequency):
  - infinity_pool (amenities) - Frequency: 15
  - sky_garden (amenities) - Frequency: 12
  - golf_view (view_types) - Frequency: 8
  - wine_cellar (amenities) - Frequency: 7
  - smart_home (amenities) - Frequency: 6
  - pet_park (amenities) - Frequency: 5
```

## 🔧 Configuration Options

### Crawl Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `site` | `batdongsan` | Site to crawl: `batdongsan`, `mogi`, or `all` |
| `max_pages` | `20` | Maximum pages to crawl (1 page ≈ 10-15 listings) |
| `extract_master_data` | `true` | Extract new attributes for master data |
| `auto_populate` | `true` | Auto-add to `pending_master_data` table |

### Python Script Options

```bash
# Crawl specific sites
python scripts/crawl_and_build_master_data.py \
  --sites batdongsan mogi \
  --max-pages 30 \
  --crawler-url http://localhost:8095 \
  --extraction-url http://localhost:8084
```

## 📈 Monitoring Crawl Progress

### Real-time Progress

The crawl script shows real-time progress:
- Number of listings scraped
- New attributes discovered
- Processing time
- Sample listings

### After Crawl - View Pending Items

```bash
# Get all pending items
curl http://localhost:8084/admin/pending-items?status=pending

# Get high-frequency items only
curl http://localhost:8084/admin/pending-items?status=pending&min_frequency=5

# Limit results
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
      "value_original": "hồ bơi vô cực",
      "value_english": "infinity_pool",
      "frequency": 15,
      "status": "pending",
      "created_at": "2025-01-13T10:30:00Z"
    }
  ],
  "total_count": 24,
  "high_frequency_items": 8
}
```

### Grafana Dashboard

View real-time master data growth:

http://localhost:3001/d/master-data-growth

Metrics shown:
- Master data total records over time
- Pending items queue
- Crawler activity
- New attributes discovered per day

## ✅ Admin Review & Approval

After crawling, admin needs to review and approve pending items.

### Step 1: Review Pending Items

Prioritize high-frequency items (appear many times = likely legitimate).

```bash
curl http://localhost:8084/admin/pending-items?status=pending&limit=20
```

### Step 2: Approve Item

```bash
curl -X POST http://localhost:8084/admin/approve-item \
  -H "Content-Type: application/json" \
  -d '{
    "pending_id": 1,
    "translations": {
      "vi": "Hồ bơi vô cực",
      "en": "Infinity pool",
      "zh": "无边泳池"
    },
    "admin_user_id": "admin123"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Item approved and added to master data",
  "master_data_id": 45,
  "table": "amenities"
}
```

### Step 3: Verify Addition

```bash
# Check amenities list
curl http://localhost:8084/master-data/amenities

# Run extraction test
curl -X POST http://localhost:8084/extract-with-master-data \
  -H "Content-Type: application/json" \
  -d '{"text": "Căn hộ có hồ bơi vô cực"}'
```

Now "infinity_pool" should be in the `mapped` array with ID 45!

## 🔄 Scheduled Crawling

### Manual Scheduling

**Daily Crawl (Linux/Mac - cron):**

```bash
# Edit crontab
crontab -e

# Add daily crawl at 2 AM
0 2 * * * /path/to/ree-ai/scripts/crawl-and-build-master-data.sh >> /var/log/ree-ai-crawl.log 2>&1
```

**Daily Crawl (Windows - Task Scheduler):**

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 AM
4. Action: Start a program
5. Program: `D:\Crastonic\ree-ai\scripts\crawl-and-build-master-data.bat`

**Python with Schedule:**

```bash
pip install schedule

# Create scheduled_crawl.py
import schedule
import time
from scripts.crawl_and_build_master_data import main

schedule.every().day.at("02:00").do(lambda: asyncio.run(main()))

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📊 Performance Tips

### Optimal Crawl Settings

| Scenario | Sites | Max Pages | Frequency |
|----------|-------|-----------|-----------|
| **Initial Build** | `all` | `50` | Once |
| **Daily Update** | `all` | `10` | Daily |
| **Weekly Refresh** | `all` | `20` | Weekly |
| **Testing** | `batdongsan` | `2` | Manual |

### Rate Limiting

The crawler automatically rate-limits to avoid overloading sites:
- 1 second delay between requests
- 10 second delay between sites
- Respect robots.txt

### Resource Usage

Expected resource usage per crawl:

| Pages | Duration | Listings | Memory |
|-------|----------|----------|--------|
| 5 | ~1 min | ~50 | ~200MB |
| 20 | ~3 min | ~200 | ~300MB |
| 50 | ~8 min | ~500 | ~500MB |

## 🐛 Troubleshooting

### Issue: Crawler service not running

**Solution:**
```bash
# Check service status
docker-compose ps | grep crawler

# Start crawler service
docker-compose up -d crawler-service

# Check logs
docker-compose logs -f crawler-service
```

### Issue: No new attributes discovered

**Cause:** Master data already complete, or sites have similar listings.

**Solution:**
- Crawl more pages: `--max-pages 50`
- Crawl different sites
- Check if items already in `pending_master_data` (check frequency increment)

### Issue: Crawl fails with timeout

**Cause:** Site is slow or blocking requests.

**Solution:**
```bash
# Reduce pages per crawl
python scripts/crawl_and_build_master_data.py --max-pages 10

# Try different site
python scripts/crawl_and_build_master_data.py --sites mogi
```

### Issue: Too many pending items (> 500)

**Cause:** Crawled too much without admin review.

**Solution:**
1. Review and approve high-frequency items first
2. Reject obvious duplicates/errors
3. Adjust crawl frequency

## 📚 Best Practices

### 1. Start Small, Scale Up

```bash
# Week 1: Test crawl
python scripts/crawl_and_build_master_data.py --max-pages 5

# Week 2: Medium crawl
python scripts/crawl_and_build_master_data.py --max-pages 20

# Week 3+: Full crawl
python scripts/crawl_and_build_master_data.py --max-pages 50
```

### 2. Prioritize Admin Reviews

- Review high-frequency items (> 10 occurrences) first
- Approve common amenities quickly
- Reject obvious errors/duplicates
- Normalize similar items (merge "hồ bơi" and "bể bơi")

### 3. Monitor Data Quality

```bash
# Weekly: Check for duplicates
curl http://localhost:8084/admin/pending-items?status=pending | grep -i "pool"

# Monthly: Audit approved items
psql -U ree_ai_user -d ree_ai -c "SELECT * FROM amenities ORDER BY created_at DESC LIMIT 20;"
```

### 4. Respect Crawling Ethics

- ✅ Only crawl public listings
- ✅ Respect robots.txt
- ✅ Use reasonable delays (1 sec/request)
- ✅ Crawl during off-peak hours (2-6 AM)
- ❌ Don't scrape personal data
- ❌ Don't overload servers

## 📈 Master Data Growth Tracking

### View Growth Over Time

```bash
# PostgreSQL query
psql -U ree_ai_user -d ree_ai -c "
  SELECT
    DATE(created_at) as date,
    COUNT(*) as new_items
  FROM pending_master_data
  WHERE status = 'approved'
  GROUP BY DATE(created_at)
  ORDER BY date DESC
  LIMIT 30;
"
```

### Grafana Dashboard

Metrics to track:
- Total master data records (per table)
- New items approved per day
- Pending items queue size
- Crawler success rate

## 🎯 Success Metrics

After running regular crawls, you should see:

✅ **Week 1:**
- 500+ listings crawled
- 20-50 new attributes discovered
- 10-20 high-frequency items approved
- Master data grows by ~5-10%

✅ **Week 4:**
- 2000+ listings crawled (cumulative)
- 50-100 new attributes discovered
- Master data grows by ~15-25%
- Fuzzy match accuracy improves

✅ **Month 3:**
- 10,000+ listings crawled
- Master data stabilizes (< 5 new items/week)
- 95%+ extraction accuracy
- Comprehensive coverage of HCMC properties

## 📞 Support

- **Script Issues**: Check `docker-compose logs crawler-service`
- **API Errors**: Check `docker-compose logs attribute-extraction`
- **Documentation**: `docs/CRAWLER_SERVICE_IMPLEMENTATION.md`

---

**Ready to start building master data?** 🚀

```bash
python scripts/crawl_and_build_master_data.py
```

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-01-13

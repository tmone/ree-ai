# Smart Crawler - Production Design

## Vấn đề cần giải quyết

**Challenge**: Trong production, làm sao biết page nào đã crawl để tránh lãng phí?

## Giải pháp: Multi-Layer Auto-Resume

### Layer 1: Database State Tracking

Sử dụng bảng `crawl_state` để track từng URL đã crawl:

```sql
CREATE TABLE crawl_state (
    id SERIAL PRIMARY KEY,
    site_domain VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    url_hash VARCHAR(64) NOT NULL,  -- MD5 hash for quick lookup
    status VARCHAR(50) DEFAULT 'active',
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(site_domain, url_hash)
);
```

**Benefits:**
- ✅ Track chính xác từng URL
- ✅ Detect duplicates real-time
- ✅ Support incremental crawling
- ✅ Resume từ bất kỳ điểm nào

### Layer 2: Auto-Detect Resume Point

SmartCrawler tự động tìm page để resume theo thứ tự ưu tiên:

```python
def get_resume_page(self) -> int:
    """
    Strategy:
    1. Check crawl_jobs table for last successful page
    2. Estimate from properties count (count / 20 properties per page)
    3. Default to page 1 if no data
    """
```

**Example:**
```bash
# Lần chạy đầu tiên
>>> SmartCrawler('batdongsan.com.vn').get_resume_page()
🆕 No previous crawl found, starting from page 1
>>> 1

# Sau khi crawl 10,000 properties
>>> SmartCrawler('batdongsan.com.vn').get_resume_page()
📊 Estimated last page from 10000 properties: ~500
>>> 500

# Lần chạy tiếp theo
>>> SmartCrawler('batdongsan.com.vn').get_resume_page()
📌 Found last crawled page: 505
>>> 506  # Tự động resume từ page tiếp theo
```

### Layer 3: Smart Duplicate Detection

Mỗi URL được check trước khi crawl:

```python
def is_url_crawled(self, url: str) -> bool:
    """Check database nếu URL đã crawl"""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    # Fast lookup using hash index
    return exists_in_crawl_state(url_hash)
```

**Performance:**
- O(1) lookup với hash index
- Không cần crawl lại page đã có
- Skip duplicates tự động

### Layer 4: Auto-Stop on Exhaustion

Crawler tự động dừng khi hết data mới:

```python
# Stop if 10 consecutive pages are all duplicates
if consecutive_duplicates >= 10:
    print("⏹️  Stopping: No new properties found")
    break
```

## Usage

### Basic Usage

```bash
# Crawl 10,000 new properties (tự động resume)
python services/crawler/smart_crawler.py batdongsan.com.vn 10000
```

**Output:**
```
🚀 Starting incremental crawl for batdongsan.com.vn
🎯 Target: 10000 new properties
======================================================================

📌 Found last crawled page: 505
▶️  Resuming from page 506

🔧 Initializing crawler...
✅ Crawler ready!

📄 Crawling page 506: https://batdongsan.com.vn/nha-dat-ban/p506
   ✅ Page 506: 20 total, 20 new, 0 duplicates
📄 Crawling page 507: https://batdongsan.com.vn/nha-dat-ban/p507
   ✅ Page 507: 20 total, 18 new, 2 duplicates
...
📊 Progress: 100/10000 new properties
...
🎉 Target reached! 10000 new properties crawled

======================================================================
✅ Crawl completed!
   📄 Pages crawled: 500
   🆕 New properties: 10000
   🔄 Duplicates skipped: 234
======================================================================

📊 Total properties in database: 20000
```

### Production Cron Job

```bash
# Chạy mỗi ngày để lấy data mới
0 2 * * * cd /app && python services/crawler/smart_crawler.py batdongsan.com.vn 5000
```

**Behavior:**
- Day 1: Crawl pages 1-250 → 5,000 properties
- Day 2: Auto-resume from page 251 → 5,000 more
- Day 3: Auto-resume from page 501 → 5,000 more
- ...

## Key Features

### 1. Zero Configuration
```python
crawler = SmartCrawler('batdongsan.com.vn')
crawler.crawl_incremental(target_properties=10000)  # Tự động resume!
```

### 2. Fault Tolerant
- Database transaction per batch
- Resume từ điểm dừng bất kỳ
- Không mất data khi crash

### 3. Performance Optimized
- Batch insert (20 properties/transaction)
- Hash-based duplicate detection
- Indexed lookups
- Rate limiting built-in

### 4. Production Ready
- Comprehensive logging
- Progress tracking
- Error handling
- Auto-stop when exhausted

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     SmartCrawler                             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 1. Auto-Detect Resume Point                        │    │
│  │    ├─ Check crawl_jobs (last_page metadata)       │    │
│  │    ├─ Estimate from properties count              │    │
│  │    └─ Default to page 1                           │    │
│  └────────────────────────────────────────────────────┘    │
│                         ↓                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 2. Crawl Loop                                      │    │
│  │    ├─ Fetch page HTML                              │    │
│  │    ├─ Extract properties                           │    │
│  │    └─ Check duplicates via crawl_state            │    │
│  └────────────────────────────────────────────────────┘    │
│                         ↓                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 3. Batch Insert                                    │    │
│  │    ├─ Insert into properties table                 │    │
│  │    ├─ Mark URL in crawl_state                      │    │
│  │    └─ Update job metadata                          │    │
│  └────────────────────────────────────────────────────┘    │
│                         ↓                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 4. Smart Stop                                      │    │
│  │    ├─ Check if target reached                      │    │
│  │    ├─ Check consecutive duplicates (≥10)          │    │
│  │    └─ Stop and report                              │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Database Tables                            │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │
│  │ crawl_configs│   │  properties  │   │ crawl_state  │   │
│  ├──────────────┤   ├──────────────┤   ├──────────────┤   │
│  │ Site config  │───│ Property data│───│ URL tracking │   │
│  │ Selectors    │   │ Title, price │   │ url_hash     │   │
│  │ Pagination   │   │ Location     │   │ status       │   │
│  └──────────────┘   └──────────────┘   └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### crawl_state Table
```sql
-- Track từng URL đã crawl
INSERT INTO crawl_state (site_domain, url, url_hash, status)
VALUES ('batdongsan.com.vn', 'https://...', 'abc123...', 'active')
ON CONFLICT (site_domain, url_hash)
DO UPDATE SET last_seen = CURRENT_TIMESTAMP;
```

**Indexes:**
- `idx_crawl_state_url_hash` - Fast duplicate lookup
- `idx_crawl_state_domain` - Filter by site
- `idx_crawl_state_last_seen` - Find stale URLs

## Comparison: Old vs New

### Old Approach (crawl_and_store.py)
```python
# ❌ Problems:
- Hard-coded page numbers (page 506)
- No auto-resume
- Re-crawl duplicates
- Waste bandwidth

# Example:
python crawl_from_page_506.py 506 10000  # Manual page number!
```

### New Approach (SmartCrawler)
```python
# ✅ Solutions:
- Auto-detect resume point
- Skip duplicates automatically
- Stop when no new data
- Production ready

# Example:
python services/crawler/smart_crawler.py batdongsan.com.vn 10000
# Tự động resume từ page cuối cùng!
```

## Migration Guide

### Step 1: Update existing crawl script
```bash
# Old way
python tests/crawl_and_store.py 10000

# New way
python services/crawler/smart_crawler.py batdongsan.com.vn 10000
```

### Step 2: Setup cron job
```bash
# Add to crontab
0 2 * * * cd /app && python services/crawler/smart_crawler.py batdongsan.com.vn 5000 >> /var/log/crawler.log 2>&1
```

### Step 3: Monitor
```bash
# Check crawl status
psql -c "SELECT site_domain, COUNT(*) FROM crawl_state GROUP BY site_domain;"

# Check last crawl
psql -c "SELECT site_domain, metadata->>'last_page' FROM crawl_jobs ORDER BY completed_at DESC LIMIT 5;"
```

## Future Enhancements

### 1. Distributed Crawling
```python
# Multiple workers crawl different sites in parallel
workers = [
    SmartCrawler('batdongsan.com.vn'),
    SmartCrawler('alonhadat.com.vn'),
    SmartCrawler('mogi.vn'),
]
await asyncio.gather(*[w.crawl_incremental(5000) for w in workers])
```

### 2. Delta Updates
```python
# Chỉ crawl properties updated trong 24h qua
crawler.crawl_delta(hours=24)
```

### 3. Quality Metrics
```python
# Track data quality per site
crawler.report_quality_metrics()
```

## Summary

**SmartCrawler giải quyết vấn đề production:**

✅ **Auto-Resume**: Không cần manual page number
✅ **Duplicate Detection**: Skip URLs đã crawl
✅ **Performance**: Hash-based lookup, batch insert
✅ **Fault Tolerant**: Resume từ bất kỳ điểm nào
✅ **Production Ready**: Logging, monitoring, error handling

**One-liner usage:**
```python
SmartCrawler('batdongsan.com.vn').crawl_incremental(10000)
```

Không cần biết page nào đã crawl - hệ thống tự động xử lý! 🎉

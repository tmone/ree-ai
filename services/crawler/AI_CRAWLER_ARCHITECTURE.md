# AI-Powered Adaptive Crawler Architecture

## Vấn đề của thiết kế hiện tại
❌ Hardcoded CSS selectors cho từng site
❌ Static rate limits không thích ứng
❌ Manual configuration cho mỗi site mới
❌ Không phát hiện được lỗi rate limit tự động
❌ Không có incremental crawling (cào lại toàn bộ mỗi lần)
❌ Không đánh giá chất lượng data trước khi cào

## Kiến trúc mới: 5-Layer Intelligent Crawler

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Site Discovery & Analysis (LLM-Powered)           │
│  - Auto-detect site structure using GPT-4                   │
│  - Identify pagination patterns                             │
│  - Extract data schema                                      │
│  - Evaluate data quality                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Auto-Config Generator                             │
│  - Generate optimal crawl config from analysis              │
│  - Calculate rate limits from response headers              │
│  - Determine worker count based on site capacity            │
│  - Save to config database                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Multi-Site Orchestrator                           │
│  - Manage 10+ sites in parallel                             │
│  - Load balancing across sites                              │
│  - Priority queue for urgent updates                        │
│  - Global rate limiting across all sites                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Adaptive Crawler with Error Detection             │
│  - Detect rate limit errors (429, Cloudflare, etc)          │
│  - Auto-adjust delays based on errors                       │
│  - Retry with exponential backoff                           │
│  - Switch proxies/user agents on block                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Incremental State Management                      │
│  - Track crawled URLs per site                              │
│  - Detect new properties (incremental crawl)                │
│  - Update existing properties (changes)                     │
│  - Delete removed properties (sync)                         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Site Analyzer Service (`site_analyzer.py`)

**Input:** Site URL
**Output:** SiteAnalysis object with structure, selectors, patterns

**Features:**
- Use GPT-4 Vision to analyze HTML structure
- Identify property cards, pagination, filters
- Extract data schema (price, location, bedrooms, etc)
- Evaluate data quality (completeness, accuracy)
- Suggest optimal crawl strategy

**LLM Prompt Example:**
```
Analyze this real estate website HTML and provide:
1. CSS selectors for property cards
2. Pagination pattern (URL format, max pages)
3. Data fields available (price, location, area, etc)
4. Rate limit indicators (headers, error messages)
5. Recommended crawl frequency (daily/hourly)
6. Data quality score (1-10)

Return as JSON.
```

### 2. Auto-Config Generator (`config_generator.py`)

**Input:** SiteAnalysis
**Output:** CrawlConfig saved to database

**Features:**
- Generate config from analysis
- Calculate optimal rate limits from headers
- Determine worker count based on site capacity
- Set incremental vs full crawl strategy
- Version configs for A/B testing

**Database Schema:**
```sql
CREATE TABLE crawl_configs (
    id SERIAL PRIMARY KEY,
    site_domain VARCHAR(255) UNIQUE,
    site_name VARCHAR(255),
    base_url TEXT,
    selectors JSONB,
    pagination JSONB,
    rate_limit FLOAT,
    max_workers INT,
    crawl_frequency VARCHAR(50), -- 'hourly', 'daily', 'weekly'
    enabled BOOLEAN DEFAULT true,
    last_full_crawl TIMESTAMP,
    last_incremental_crawl TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE crawl_state (
    id SERIAL PRIMARY KEY,
    site_domain VARCHAR(255),
    url TEXT,
    last_seen TIMESTAMP,
    content_hash VARCHAR(64),
    status VARCHAR(50), -- 'active', 'removed', 'updated'
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 3. Rate Limit Detector (`rate_limit_detector.py`)

**Features:**
- Detect HTTP 429 (Too Many Requests)
- Recognize Cloudflare challenges
- Identify CAPTCHA pages
- Parse Retry-After headers
- Detect IP blocks (403, soft blocks)
- Auto-adjust delays based on errors

**Error Patterns:**
```python
RATE_LIMIT_PATTERNS = {
    "http_429": r"429",
    "cloudflare": r"Checking your browser|cf-ray",
    "captcha": r"recaptcha|hcaptcha|captcha",
    "ip_block": r"Access Denied|Forbidden|blocked",
    "too_fast": r"slow down|too many requests",
}
```

### 4. Multi-Site Orchestrator (`multi_site_orchestrator.py`)

**Features:**
- Load all enabled site configs from DB
- Distribute crawl jobs across workers
- Priority queue (urgent sites first)
- Global rate limiting (don't overload system)
- Monitor health per site
- Auto-disable failing sites

**Site States:**
```python
class SiteStatus(Enum):
    ACTIVE = "active"           # Crawling normally
    RATE_LIMITED = "rate_limited"  # Temporary slow down
    BLOCKED = "blocked"         # IP blocked, use proxy
    FAILED = "failed"           # Multiple errors, pause
    DISABLED = "disabled"       # Manually disabled
```

### 5. Incremental Crawler (`incremental_crawler.py`)

**Full Crawl Mode:**
- Crawl all pages from page 1 to max
- Store all URLs + content hash
- Mark as last_full_crawl timestamp

**Incremental Crawl Mode:**
- Only crawl first N pages (new listings)
- Compare URLs with existing state
- Insert new properties
- Update changed properties (hash differs)
- Mark removed properties (not seen)

**State Tracking:**
```python
class CrawlState:
    def track_url(self, url: str, content_hash: str):
        """Track URL with content hash"""

    def is_new(self, url: str) -> bool:
        """Check if URL is new"""

    def is_updated(self, url: str, content_hash: str) -> bool:
        """Check if content changed"""

    def get_removed(self, days: int = 7) -> List[str]:
        """Get URLs not seen in N days (removed)"""
```

## Usage Flow

### Adding New Site

```python
from services.crawler.ai_crawler import AICrawlerService

# Step 1: Analyze site
crawler = AICrawlerService()
analysis = await crawler.analyze_site("https://nhatot.com/mua-ban-bat-dong-san")

# Step 2: Review & approve config
print(f"Quality Score: {analysis.quality_score}/10")
print(f"Suggested Rate Limit: {analysis.suggested_rate_limit}s")
print(f"Data Fields: {analysis.data_fields}")

# Step 3: Auto-generate & save config
config = await crawler.generate_config(analysis)
await crawler.save_config(config)

# Step 4: Start crawling
await crawler.start_site("nhatot.com")
```

### Multi-Site Crawling

```python
# Start orchestrator (crawls all enabled sites)
orchestrator = MultiSiteOrchestrator()
await orchestrator.start()

# It will:
# - Load all enabled configs from DB
# - Crawl each site with optimal settings
# - Auto-adjust based on errors
# - Save state for incremental updates
```

### Incremental Updates (Cron Job)

```bash
# Run every hour to get new listings
0 * * * * python3 -m services.crawler.incremental_crawl

# Run daily full crawl to sync deletions
0 2 * * * python3 -m services.crawler.full_crawl
```

## Supported Sites (Auto-Detected)

### Vietnam
- batdongsan.com.vn
- nhatot.com
- mogi.vn
- alonhadat.com.vn
- dothi.net
- muaban.net

### International
- zillow.com (US)
- rightmove.co.uk (UK)
- immobilienscout24.de (Germany)
- seloger.com (France)
- funda.nl (Netherlands)

## Monitoring & Alerts

**Metrics:**
- Crawl success rate per site
- Average response time
- Rate limit hits per hour
- Data quality score over time
- New properties per site per day

**Alerts:**
- Site blocked (IP ban detected)
- Config outdated (selectors not matching)
- Low quality data (missing fields)
- Crawl failures > 10% for 1 hour

## Next Steps

1. ✅ Design architecture (this document)
2. Implement Site Analyzer with GPT-4
3. Build Auto-Config Generator
4. Create Rate Limit Detector
5. Build Multi-Site Orchestrator
6. Implement Incremental Crawler
7. Add database schema
8. Create monitoring dashboard
9. Test with 10+ real sites
10. Deploy to production

## References

- [Scrapy Architecture](https://docs.scrapy.org/en/latest/topics/architecture.html)
- [Crawl4AI Documentation](https://docs.crawl4ai.com/)
- [OpenAI Vision API](https://platform.openai.com/docs/guides/vision)

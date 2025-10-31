# AI-Powered Adaptive Crawler

**Hệ thống crawler thông minh tự động phân tích và cào dữ liệu từ bất kỳ website bất động sản nào trên thế giới.**

## Tính năng

### 🤖 AI-Powered Site Analysis
- Tự động phân tích cấu trúc website bằng GPT-4
- Tìm CSS selectors tự động
- Đánh giá chất lượng dữ liệu
- Đề xuất chiến lược cào tối ưu

### 🌍 Multi-Site Support
- Cào nhiều website cùng lúc
- Hỗ trợ mọi định dạng website BĐS
- Tự động thích ứng với từng site

### 🛡️ Intelligent Rate Limiting
- Phát hiện rate limit tự động (429, Cloudflare, CAPTCHA)
- Điều chỉnh tốc độ cào thông minh
- Retry với exponential backoff

### 📊 Incremental Crawling
- Chỉ cào dữ liệu mới (tiết kiệm thời gian)
- Phát hiện thay đổi tự động
- Đồng bộ xóa properties không còn

### 📈 Monitoring & Stats
- Theo dõi tiến trình realtime
- Thống kê chi tiết mỗi site
- Log lỗi và rate limit events

## Kiến trúc

```
┌──────────────────────────────────────────────────────┐
│  Site Analyzer (GPT-4)                               │
│  - Phân tích HTML tự động                            │
│  - Tìm selectors                                     │
│  - Đánh giá quality                                  │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  Config Database                                     │
│  - Lưu cấu hình mỗi site                            │
│  - Track crawl state                                 │
│  - Monitor jobs                                      │
└──────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────┐
│  Multi-Site Orchestrator                             │
│  - Quản lý 10+ sites cùng lúc                       │
│  - Parallel crawling                                 │
│  - Error detection & recovery                        │
└──────────────────────────────────────────────────────┘
```

## Cài đặt

### 1. Cài đặt dependencies

```bash
pip install crawl4ai beautifulsoup4 psycopg2-binary httpx tabulate
```

### 2. Setup database

```bash
# Run migration
psql -U ree_ai_user -d ree_ai < database/migrations/003_crawler_configs.sql
```

### 3. Configure API key

```bash
# .env
OPENAI_API_KEY=sk-your-key-here
```

## Sử dụng

### Quick Start - Thêm Site Mới

```bash
# Phân tích và thêm site mới (AI tự động)
python3 services/crawler/ai_crawler_cli.py add https://mogi.vn

# AI sẽ:
# 1. Phân tích HTML structure
# 2. Tìm CSS selectors tự động
# 3. Đánh giá quality score
# 4. Đề xuất rate limit và workers
# 5. Lưu config vào database
```

**Output:**
```
🔍 Analyzing site: https://mogi.vn
======================================================================

✅ Analysis Complete!
Site Name: Mogi.vn
Domain: mogi.vn
Quality Score: 8.5/10
Data Completeness: 90.0%
Recommended Frequency: daily
Rate Limit: 2.5s
Max Workers: 4
Available Fields: title, price, location, area, description

Selectors:
  Card: .property-item
  Title: .property-title
  Price: .property-price
  Location: .property-location

💾 Save this configuration? (y/n): y

✅ Site configuration saved successfully!
You can now crawl with: python ai_crawler_cli.py crawl mogi.vn
```

### Xem danh sách sites

```bash
python3 services/crawler/ai_crawler_cli.py list
```

**Output:**
```
📋 Configured Sites (3 total):
┌────────────────────┬─────────────────┬─────────┬──────────┬─────────┬──────────────────┐
│ Domain             │ Name            │ Quality │ Status   │ Enabled │ Last Crawl       │
├────────────────────┼─────────────────┼─────────┼──────────┼─────────┼──────────────────┤
│ batdongsan.com.vn  │ Batdongsan      │ 9.5/10  │ active   │ ✅       │ 2025-11-01 10:30 │
│ mogi.vn            │ Mogi.vn         │ 8.5/10  │ active   │ ✅       │ 2025-11-01 09:15 │
│ nhatot.com         │ Nhatot.com      │ 7.5/10  │ active   │ ✅       │ 2025-11-01 08:00 │
└────────────────────┴─────────────────┴─────────┴──────────┴─────────┴──────────────────┘
```

### Crawl dữ liệu

```bash
# Incremental crawl tất cả sites (chỉ cào mới)
python3 services/crawler/ai_crawler_cli.py crawl

# Crawl một site cụ thể
python3 services/crawler/ai_crawler_cli.py crawl mogi.vn

# Full crawl (cào toàn bộ)
python3 services/crawler/ai_crawler_cli.py crawl mogi.vn full
```

**Output:**
```
🚀 Starting Multi-Site Orchestrator in incremental mode

ℹ️  [Batdongsan] Starting incremental crawl
ℹ️  [Mogi.vn] Starting incremental crawl
ℹ️  [Nhatot.com] Starting incremental crawl

📊 [Batdongsan] Progress: 5/10 pages, 98 properties
📊 [Mogi.vn] Progress: 5/10 pages, 85 properties
📊 [Nhatot.com] Progress: 5/10 pages, 72 properties

✅ [Batdongsan] Crawl completed: 195 total, 45 new, 12 updated, 23.4s
✅ [Mogi.vn] Crawl completed: 168 total, 38 new, 8 updated, 21.2s
✅ [Nhatot.com] Crawl completed: 142 total, 29 new, 5 updated, 19.8s

============================================================
✅ MULTI-SITE CRAWL COMPLETED
============================================================
✅ Succeeded: 3/3 sites
============================================================
```

### Xem status và thống kê

```bash
python3 services/crawler/ai_crawler_cli.py status
```

**Output:**
```
📊 Crawler Status
======================================================================
Total Sites: 3
Enabled: 3
Active: 3
Avg Quality: 8.5/10

📋 Recent Crawl Jobs:
┌───────────────────┬──────────────┬───────────┬─────┬─────────┬──────────┬─────────────┐
│ Site              │ Type         │ Status    │ New │ Updated │ Duration │ Completed   │
├───────────────────┼──────────────┼───────────┼─────┼─────────┼──────────┼─────────────┤
│ batdongsan.com.vn │ incremental  │ completed │ 45  │ 12      │ 23.4s    │ 11-01 10:30 │
│ mogi.vn           │ incremental  │ completed │ 38  │ 8       │ 21.2s    │ 11-01 09:15 │
│ nhatot.com        │ incremental  │ completed │ 29  │ 5       │ 19.8s    │ 11-01 08:00 │
└───────────────────┴──────────────┴───────────┴─────┴─────────┴──────────┴─────────────┘
```

### Enable/Disable sites

```bash
# Tắt một site
python3 services/crawler/ai_crawler_cli.py disable mogi.vn

# Bật lại
python3 services/crawler/ai_crawler_cli.py enable mogi.vn
```

## Cron Jobs (Tự động cào định kỳ)

### Incremental Crawl mỗi giờ

```bash
# Thêm vào crontab
0 * * * * cd /Users/tmone/ree-ai && python3 services/crawler/ai_crawler_cli.py crawl
```

### Full Crawl mỗi ngày

```bash
# 2:00 AM daily
0 2 * * * cd /Users/tmone/ree-ai && python3 services/crawler/ai_crawler_cli.py crawl "" full
```

## Use Cases

### 1. Thêm site BĐS Việt Nam mới

```bash
# Tự động phân tích và thêm
python3 services/crawler/ai_crawler_cli.py add https://alonhadat.com.vn

# AI sẽ tự động:
# - Tìm selectors cho property cards
# - Xác định pagination pattern
# - Đề xuất rate limit
# - Đánh giá quality

# Sau đó crawl ngay:
python3 services/crawler/ai_crawler_cli.py crawl alonhadat.com.vn
```

### 2. Thêm site BĐS quốc tế

```bash
# US - Zillow
python3 services/crawler/ai_crawler_cli.py add https://www.zillow.com/homes/for_sale/

# UK - Rightmove
python3 services/crawler/ai_crawler_cli.py add https://www.rightmove.co.uk/property-for-sale.html

# Germany - ImmobilienScout24
python3 services/crawler/ai_crawler_cli.py add https://www.immobilienscout24.de/Suche/

# France - SeLoger
python3 services/crawler/ai_crawler_cli.py add https://www.seloger.com/immobilier/achats/
```

### 3. Crawl nhiều sites cùng lúc

```bash
# Tất cả sites enabled
python3 services/crawler/ai_crawler_cli.py crawl

# Orchestrator sẽ:
# - Crawl 5 sites song song
# - Tự động phát hiện rate limit
# - Điều chỉnh tốc độ cho từng site
# - Track state incremental
```

### 4. Monitor và Debug

```bash
# Xem status realtime
watch -n 5 "python3 services/crawler/ai_crawler_cli.py status"

# Kiểm tra rate limit events
psql -U ree_ai_user -d ree_ai -c "
SELECT site_domain, event_type, COUNT(*)
FROM rate_limit_events
WHERE detected_at > NOW() - INTERVAL '1 day'
GROUP BY site_domain, event_type
ORDER BY COUNT(*) DESC;
"
```

## Advanced Features

### 1. Site Analyzer API

```python
from services.crawler.site_analyzer import SiteAnalyzer

analyzer = SiteAnalyzer()
analysis = await analyzer.analyze_site("https://example.com")

print(f"Quality: {analysis.quality_score}/10")
print(f"Selectors: {analysis.property_card_selector}")
print(f"Rate Limit: {analysis.rate_limit_seconds}s")
```

### 2. Orchestrator API

```python
from services.crawler.multi_site_orchestrator import MultiSiteOrchestrator, CrawlMode

orchestrator = MultiSiteOrchestrator(db_config)

# Crawl all sites
await orchestrator.start_all(mode=CrawlMode.INCREMENTAL)

# Crawl specific site
config = await orchestrator.load_configs()[0]
stats = await orchestrator.crawl_site(config, CrawlMode.FULL)
```

### 3. Custom Rate Limit Detection

```python
from services.crawler.multi_site_orchestrator import RateLimitDetector

# Detect from response
rate_limit_type = RateLimitDetector.detect(
    status_code=429,
    html=response_html,
    headers=response_headers
)

if rate_limit_type:
    retry_after = RateLimitDetector.get_retry_after(headers)
    await asyncio.sleep(retry_after)
```

## Database Schema

### crawl_configs
Stores AI-generated configurations for each site

### crawl_state
Tracks individual URLs for incremental crawling

### crawl_jobs
Monitors crawl job execution and performance

### rate_limit_events
Logs rate limit detections for analysis

## Troubleshooting

### Site analysis failed

```bash
# Check OpenAI API key
echo $OPENAI_API_KEY

# Try with more verbose logging
export DEBUG=true
python3 services/crawler/ai_crawler_cli.py add https://example.com
```

### Crawl too slow

```bash
# Check rate limit settings
psql -U ree_ai_user -d ree_ai -c "
SELECT site_domain, rate_limit_seconds, max_workers
FROM crawl_configs;
"

# Adjust manually if needed
psql -U ree_ai_user -d ree_ai -c "
UPDATE crawl_configs
SET rate_limit_seconds = 1.5, max_workers = 6
WHERE site_domain = 'batdongsan.com.vn';
"
```

### Rate limit detected

```bash
# Check recent rate limit events
psql -U ree_ai_user -d ree_ai -c "
SELECT * FROM rate_limit_events
WHERE site_domain = 'mogi.vn'
ORDER BY detected_at DESC
LIMIT 10;
"

# Site will auto-adjust, but you can manually slow down:
psql -U ree_ai_user -d ree_ai -c "
UPDATE crawl_configs
SET rate_limit_seconds = rate_limit_seconds * 1.5,
    max_workers = GREATEST(1, max_workers - 1)
WHERE site_domain = 'mogi.vn';
"
```

## Roadmap

- [ ] Proxy rotation support
- [ ] JavaScript rendering for SPA sites
- [ ] Auto-detect pagination end
- [ ] Smart retry strategies
- [ ] Real-time dashboard
- [ ] Webhook notifications
- [ ] Export to multiple formats
- [ ] API endpoint for external access

## So sánh với thiết kế cũ

| Feature | Old Design | New AI-Powered Design |
|---------|-----------|----------------------|
| Add new site | Manual coding selectors | AI auto-detects |
| Rate limit | Static, hardcoded | Adaptive, auto-detect |
| Multi-site | Single site only | 10+ sites parallel |
| Incremental | No, re-crawl all | Yes, only new data |
| Error handling | Basic retry | Intelligent recovery |
| Monitoring | Logs only | Database tracking |
| Config | Hardcoded in code | Database-driven |
| Quality | Unknown | AI-assessed score |

## Kết luận

Hệ thống AI Crawler mới:

✅ **Thông minh**: AI tự động phân tích mọi site
✅ **Linh hoạt**: Hỗ trợ mọi định dạng website BĐS
✅ **Mạnh mẽ**: Cào 10+ sites song song
✅ **Thích ứng**: Tự điều chỉnh rate limit
✅ **Tiết kiệm**: Incremental crawling
✅ **Monitoring**: Track mọi thứ trong database

**Không còn cần hardcode selectors cho từng site nữa!** 🎉

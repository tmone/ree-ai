# Crawler Service - Automated Master Data Collection

## 🎯 Overview

The **Crawler Service** automatically scrapes property listings from popular Vietnamese real estate websites to discover and populate master data. This enables the system to **continuously learn** from real-world data.

## 🔄 How It Works

```
┌───────────────────────────────────────────────────────────────┐
│ 1. Crawl Real Estate Websites (Crawl4AI)                      │
│    ├─ Batdongsan.com.vn                                        │
│    ├─ Mogi.vn                                                  │
│    └─ More sites can be added...                              │
└────────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────────┐
│ 2. Parse Listings & Extract Attributes                        │
│    ├─ Title, Price, Location                                  │
│    ├─ Property Type, Area, Bedrooms                           │
│    ├─ Amenities (pool, gym, parking, etc.)                    │
│    └─ Features (direction, furniture, view, etc.)             │
└────────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────────┐
│ 3. Discover New Master Data                                   │
│    ├─ Compare with existing master data                       │
│    ├─ Find new districts, amenities, features                 │
│    ├─ Track frequency (how many times each appears)           │
│    └─ Prioritize high-frequency items                         │
└────────────────────────────┬──────────────────────────────────┘
                             │
                             ▼
┌───────────────────────────────────────────────────────────────┐
│ 4. Store in pending_master_data for Admin Review              │
│    ├─ Auto-increment frequency if already exists              │
│    ├─ Store suggested table + category                        │
│    └─ Ready for admin approval via Admin API                  │
└───────────────────────────────────────────────────────────────┘
```

## 🌐 Supported Real Estate Sites

### 1. Batdongsan.com.vn
- **URL**: https://batdongsan.com.vn
- **Coverage**: Apartments, houses, land across Vietnam
- **Extracts**: Property type, location, price, area, amenities, features

### 2. Mogi.vn
- **URL**: https://mogi.vn
- **Coverage**: High-end properties, apartments in major cities
- **Extracts**: Property type, location, price, area, amenities

### 3. Extensible Design
- **Easy to add more sites**: Inherit from `BaseCrawler`
- **Consistent data format**: All crawlers return same structure
- **Plug-and-play**: Add new crawler → Auto-discovered by service

## 📊 Architecture

```
services/crawler_service/
├── main.py                          # FastAPI service
├── Dockerfile                        # Docker config
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py              # Abstract base class
│   ├── batdongsan_crawler.py        # Batdongsan.com.vn
│   └── mogi_crawler.py              # Mogi.vn
└── master_data_populator.py         # Analyzes & stores new data
```

### Key Components

#### 1. BaseCrawler (Abstract)
```python
class BaseCrawler(ABC):
    @abstractmethod
    async def get_listing_urls(self, max_pages: int) -> List[str]:
        """Get URLs of listings to scrape"""
        pass

    @abstractmethod
    async def parse_listing(self, html: str, markdown: str) -> Optional[Dict]:
        """Parse a single listing"""
        pass
```

#### 2. Site-Specific Crawlers
Each site has its own crawler implementing:
- URL pattern recognition
- HTML parsing logic
- Attribute extraction

#### 3. Master Data Populator
Analyzes scraped data and:
- Compares with existing master data
- Identifies new attributes
- Tracks frequency
- Stores in `pending_master_data`

## 🚀 API Endpoints

### POST /crawl
Crawl listings from specified site(s).

**Request:**
```json
{
  "site": "batdongsan",  // or "mogi" or "all"
  "max_pages": 5,
  "extract_master_data": true,
  "auto_populate": true
}
```

**Response:**
```json
{
  "site": "batdongsan",
  "listings_scraped": 47,
  "new_attributes_found": 12,
  "processing_time_ms": 125000,
  "sample_listings": [
    {
      "title": "Căn hộ 2PN Vinhomes Central Park",
      "price": 5500000000,
      "district": "Quận Bình Thạnh",
      "area": 80,
      "bedrooms": 2,
      "amenities": ["swimming_pool", "gym", "parking"],
      "source_url": "https://..."
    }
  ]
}
```

### GET /crawlers
List available crawlers.

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

### POST /schedule-crawl
Schedule periodic crawling (future enhancement).

## 📥 Deployment

### 1. Start Crawler Service

```bash
# Start crawler service
docker-compose up crawler-service

# Or with all services
docker-compose --profile all up -d
```

### 2. Test Crawling

```bash
# Crawl Batdongsan (5 pages, auto-populate)
curl -X POST http://localhost:8095/crawl \
  -H "Content-Type: application/json" \
  -d '{
    "site": "batdongsan",
    "max_pages": 5,
    "extract_master_data": true,
    "auto_populate": true
  }'
```

### 3. Review Discovered Data

```bash
# Check pending master data items
curl http://localhost:8084/admin/pending-items?status=pending

# Approve items via Admin API
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

## 🔍 What Gets Discovered?

### Districts & Wards
```
Discovered:
- "Quận 1" → Already in master data ✓
- "Quận Thủ Đức" → NEW (frequency: 15) ⚠️
- "Phường Tân Phú" → NEW (frequency: 8) ⚠️
```

### Amenities
```
Discovered:
- "swimming_pool" → Already in master data ✓
- "infinity_pool" → NEW (frequency: 12) ⚠️
- "sky_garden" → NEW (frequency: 7) ⚠️
- "pet_park" → NEW (frequency: 5) ⚠️
```

### View Types
```
Discovered:
- "river_view" → Already in master data ✓
- "landmark_view" → Already in master data ✓
- "golf_view" → NEW (frequency: 3) ⚠️
```

## 📈 Master Data Growth Process

```
Week 1: Start with seed data
├─ 25 districts (HCMC)
├─ 27 amenities
└─ 9 view types

Week 2: First crawl (100 listings)
├─ Discovered 15 new amenities
├─ Admin reviews and approves 12
└─ Master data grows to 39 amenities

Week 3: Second crawl (200 listings)
├─ Discovered 8 new amenities
├─ 5 are duplicates (ignored)
├─ Admin approves 3 new ones
└─ Master data grows to 42 amenities

...and so on
```

## ⚙️ Configuration

### Rate Limiting
```python
# In base_crawler.py
await asyncio.sleep(1)  # 1 second between requests
```

### Max Pages Per Crawl
```python
# Default: 5 pages per site
# Can be increased for more data
crawler.crawl(max_pages=10)
```

### Auto-Population
```python
# Enable auto-population (recommended)
{
  "auto_populate": true  // Automatically add to pending_master_data
}

# Disable for review-only mode
{
  "auto_populate": false  // Just discover, don't store
}
```

## 🛠️ Adding New Crawlers

### Step 1: Create Crawler Class

```python
# services/crawler_service/crawlers/mysite_crawler.py

from services.crawler_service.crawlers.base_crawler import BaseCrawler

class MySiteCrawler(BaseCrawler):
    def __init__(self):
        super().__init__(
            site_name="MySite.vn",
            base_url="https://mysite.vn"
        )

    async def get_listing_urls(self, max_pages: int) -> List[str]:
        # Implement: Get listing URLs from search results
        pass

    async def parse_listing(self, html: str, markdown: str) -> Optional[Dict]:
        # Implement: Parse listing HTML
        pass
```

### Step 2: Register in Service

```python
# services/crawler_service/main.py

from services.crawler_service.crawlers.mysite_crawler import MySiteCrawler

self.crawlers = {
    'batdongsan': BatdongsanCrawler(),
    'mogi': MogiCrawler(),
    'mysite': MySiteCrawler()  # ← Add here
}
```

### Step 3: Test

```bash
curl -X POST http://localhost:8095/crawl \
  -H "Content-Type: application/json" \
  -d '{"site": "mysite", "max_pages": 5}'
```

## 📊 Monitoring & Analytics

### View Crawl Statistics
```bash
# Get crawler list
curl http://localhost:8095/crawlers

# Check logs
docker logs ree-ai-crawler-service --tail 100 -f
```

### Review Discovered Data
```bash
# High-frequency items (priority review)
curl http://localhost:8084/admin/pending-items?status=pending | jq '.high_frequency_items'

# All pending items
curl http://localhost:8084/admin/pending-items?limit=100
```

## 🔒 Best Practices

### 1. Rate Limiting
- Respect website terms of service
- Use reasonable delays between requests
- Crawl during off-peak hours

### 2. Data Quality
- Review high-frequency items first
- Normalize inconsistent naming
- Merge similar attributes

### 3. Periodic Crawling
- Crawl weekly to discover new trends
- Compare month-over-month changes
- Update master data quarterly

### 4. Legal Compliance
- Only scrape public listings
- Respect robots.txt
- Don't scrape personal data
- Attribute source in documentation

## 🐛 Troubleshooting

### Issue: Crawler fails to start

**Cause**: Chromium not installed

**Solution**:
```dockerfile
# Dockerfile already includes:
RUN apt-get update && apt-get install -y chromium chromium-driver
```

### Issue: No listings found

**Cause**: Website structure changed

**Solution**: Update crawler parsing logic
```python
# Check logs for errors
docker logs ree-ai-crawler-service --tail 50

# Update selectors in crawler
soup.find('div', class_=re.compile(r'new-class-pattern'))
```

### Issue: Duplicate pending items

**Cause**: Already handled - frequency auto-increments

**Solution**: No action needed, system handles duplicates

## 📚 Related Documentation

- [Master Data Extraction Guide](./MASTER_DATA_EXTRACTION_IMPLEMENTATION_GUIDE.md)
- [Admin API Documentation](./MASTER_DATA_EXTRACTION_COMPLETE_IMPLEMENTATION.md)
- [Crawl4AI Documentation](https://crawl4ai.com/docs)

---

**Service**: Crawler Service
**Port**: 8095
**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-01-13

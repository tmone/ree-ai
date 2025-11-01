# Crawl4AI Numeric Filtering Guide

## 🎯 Problem Solved

**Before:** Crawled data had inconsistent formats (text prices "5,77 tỷ", text areas "95m²") making numeric filtering impossible.

**After:** All data is normalized and stored as NUMERIC values in OpenSearch, enabling proper filtering:
- ✅ `price > 6500000000` (filter giá > 6.5 tỷ)
- ✅ `area < 70` (filter diện tích < 70 m²)
- ✅ `bedrooms >= 3` (filter >= 3 phòng ngủ)

---

## 📊 Data Transformation

### Crawled Data (Raw)
```json
{
  "title": "Nhà mặt tiền Quận 7",
  "price": "5,77 tỷ",        // ❌ Text - cannot filter
  "area": "95m²",             // ❌ Text - cannot filter
  "location": "Quận 7, TP. Hồ Chí Minh",
  "bedrooms": "3",            // ❌ String
  "bathrooms": 2
}
```

### Normalized Data (Stored in OpenSearch)
```json
{
  "title": "Nhà mặt tiền Quận 7",
  "price": 5770000000,        // ✅ Numeric - can filter!
  "price_display": "5.77 tỷ", // For UI display
  "area": 95.0,               // ✅ Numeric - can filter!
  "area_display": "95 m²",    // For UI display
  "district": "Quận 7",       // ✅ Extracted
  "city": "Hồ Chí Minh",      // ✅ Extracted
  "bedrooms": 3,              // ✅ Integer
  "bathrooms": 2              // ✅ Integer
}
```

---

## 🚀 Setup Instructions

### Step 1: Create OpenSearch Index with Numeric Mapping

**IMPORTANT:** Run this **BEFORE** indexing any properties!

```bash
python scripts/create_opensearch_index_mapping.py
```

This creates the `properties` index with:
- `price`: **double** (numeric filtering enabled)
- `area`: **double** (numeric filtering enabled)
- `bedrooms`: **integer**
- `bathrooms`: **integer**

### Step 2: Crawl and Auto-Index Properties

```bash
# Crawl 100 properties and auto-index to OpenSearch
curl -X POST "http://localhost:8100/crawl/bulk?total=100&auto_index=true"
```

Response:
```json
{
  "success": true,
  "count": 100,
  "indexed_count": 100,
  "total_requested": 100,
  "sites": ["batdongsan", "nhatot"],
  "properties": [...]
}
```

### Step 3: Query with Numeric Filters

```bash
# Search properties with price 5-10 tỷ and area < 100 m²
curl -X POST "http://localhost:8081/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "nhà quận 7",
    "filters": {
      "min_price": 5000000000,
      "max_price": 10000000000,
      "max_area": 100,
      "min_bedrooms": 3
    },
    "limit": 20
  }'
```

---

## 📝 API Reference

### 1. Crawl with Auto-Index

**Endpoint:** `POST /crawl/bulk`

**Parameters:**
- `total` (int): Number of properties to crawl (max: 10,000)
- `sites` (string): Comma-separated sites: "batdongsan,nhatot"
- `auto_index` (bool): Auto-index to OpenSearch (default: `true`)

**Example:**
```bash
POST /crawl/bulk?total=500&sites=batdongsan&auto_index=true
```

**Response:**
```json
{
  "success": true,
  "count": 500,
  "indexed_count": 498,  // 498/500 indexed successfully
  "total_requested": 500,
  "sites": ["batdongsan"],
  "properties": [...]
}
```

---

### 2. Search with Filters

**Endpoint:** `POST /search`

**Request Body:**
```json
{
  "query": "nhà quận 7",
  "filters": {
    "property_type": "nhà phố",
    "region": "Quận 7",
    "min_price": 5000000000,    // >= 5 tỷ
    "max_price": 10000000000,   // <= 10 tỷ
    "min_area": 60,             // >= 60 m²
    "max_area": 100,            // <= 100 m²
    "min_bedrooms": 3           // >= 3 phòng ngủ
  },
  "limit": 20
}
```

**Response:**
```json
{
  "results": [
    {
      "property_id": "nha-1",
      "title": "Nhà mặt tiền Quận 7",
      "price": 5770000000,
      "price_display": "5.77 tỷ",
      "area": 95.0,
      "area_display": "95 m²",
      "district": "Quận 7",
      "city": "Hồ Chí Minh",
      "bedrooms": 3,
      "bathrooms": 2,
      "score": 8.5
    }
  ],
  "total": 15,
  "execution_time_ms": 45.2
}
```

---

### 3. Bulk Insert (Manual)

**Endpoint:** `POST /bulk-insert`

Use this if you want to manually index normalized properties:

```bash
curl -X POST "http://localhost:8081/bulk-insert" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "title": "Nhà test",
      "price": 5000000000,
      "price_display": "5 tỷ",
      "area": 100.0,
      "area_display": "100 m²",
      "district": "Quận 7",
      "city": "Hồ Chí Minh",
      "bedrooms": 3,
      "bathrooms": 2,
      "url": "https://example.com/nha-1",
      "source": "manual"
    }
  ]'
```

**Response:**
```json
{
  "indexed_count": 1,
  "failed_count": 0,
  "errors": null
}
```

---

## 🧪 Testing

### Test Normalized Data

```bash
# Run normalization tests
python shared/utils/data_normalizer.py
```

Expected output:
```
=== PRICE NORMALIZATION ===
5 tỷ                 →   5,000,000,000 VNĐ → 5.00 tỷ
5,77 tỷ              →   5,770,000,000 VNĐ → 5.77 tỷ
3.2 triệu            →       3,200,000 VNĐ → 3.2 triệu

=== AREA NORMALIZATION ===
95m²                 →       95.0 m² → 95 m²
120.5m2              →      120.5 m² → 120.5 m²

✅ ALL TESTS PASSED!
```

### Verify OpenSearch Filtering

```bash
# Create sample data and test filtering
# (See CRAWL4AI_NUMERIC_FILTERING.md for details)
```

---

## 🎨 Display in Open WebUI

Properties are displayed with formatted values:

```
🏠 Nhà mặt tiền Quận 7
💰 Giá: 5.77 tỷ                 ← from price_display
📍 Quận 7, Hồ Chí Minh           ← from district + city
🛏️ 3 phòng ngủ                  ← from bedrooms
📏 95 m²                        ← from area_display
```

Backend filtering uses numeric values:
- `price: 5770000000` (numeric)
- `area: 95.0` (numeric)

---

## ⚙️ Configuration

### Environment Variables

```bash
# .env
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_PROPERTIES_INDEX=properties
```

### Index Settings

The `properties` index has:
- **Shards:** 1
- **Replicas:** 1
- **Max Results:** 10,000
- **Dynamic Mapping:** Enabled (allows unlimited fields)

---

## 🔧 Troubleshooting

### Issue: Filters not working

**Cause:** Index created without numeric mapping

**Fix:**
```bash
# Delete and recreate index
python scripts/create_opensearch_index_mapping.py
# Re-index properties
curl -X POST "http://localhost:8100/crawl/bulk?total=100&auto_index=true"
```

### Issue: Price/area still text

**Cause:** Normalization not applied

**Fix:** Check crawler logs for normalization errors:
```bash
docker-compose logs crawler | grep "normalize"
```

### Issue: Auto-index failing

**Cause:** DB Gateway not accessible

**Fix:**
```bash
# Check DB Gateway health
curl http://localhost:8081/health

# Check network connectivity
docker-compose logs db-gateway
```

---

## 📌 Key Files

- **Normalization:** `shared/utils/data_normalizer.py`
- **Crawler Service:** `services/crawler/main.py`
- **DB Gateway:** `services/db_gateway/main.py`
- **Index Mapping:** `scripts/create_opensearch_index_mapping.py`

---

## 🎯 Example Queries

### Find cheap properties (< 3 tỷ)
```json
{
  "query": "nhà",
  "filters": {
    "max_price": 3000000000
  }
}
```

### Find small apartments (< 60 m²)
```json
{
  "query": "căn hộ",
  "filters": {
    "max_area": 60
  }
}
```

### Find family homes (3-4 bedrooms, 80-120 m²)
```json
{
  "query": "nhà gia đình",
  "filters": {
    "min_bedrooms": 3,
    "max_bedrooms": 4,
    "min_area": 80,
    "max_area": 120
  }
}
```

### Find luxury properties (> 15 tỷ, > 150 m²)
```json
{
  "query": "biệt thự cao cấp",
  "filters": {
    "min_price": 15000000000,
    "min_area": 150,
    "min_bedrooms": 4
  }
}
```

---

## ✅ Summary

**What Changed:**
1. ✅ Data normalization: text → numeric
2. ✅ Auto-indexing after crawl
3. ✅ Numeric filtering enabled
4. ✅ Display formatting preserved

**What You Can Do Now:**
- ✅ Filter by price range (VND)
- ✅ Filter by area range (m²)
- ✅ Filter by bedrooms/bathrooms (integer)
- ✅ Combine multiple filters
- ✅ Sort by price/area

**What's Maintained:**
- ✅ Flexible schema (unlimited fields)
- ✅ Full-text search (BM25)
- ✅ Nice UI display formatting
- ✅ Backward compatible

---

Need help? Check the logs:
```bash
docker-compose logs -f crawler
docker-compose logs -f db-gateway
docker-compose logs -f rag-service
```

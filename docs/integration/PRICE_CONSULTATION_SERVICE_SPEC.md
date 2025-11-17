# Price Consultation Service - API Specification

**Version:** 1.0
**Service Name:** `price-consultation-service`
**Port:** `8087`
**Purpose:** Provide real estate price consultation and market analysis

---

## 📋 Overview

Your team needs to build a **standalone microservice** that provides price consultation for real estate properties. The orchestrator will call your service when users ask about property prices.

**User queries examples:**
- "Căn hộ 2 phòng ngủ ở Quận 2 giá bao nhiêu?"
- "Giá thị trường nhà 3PN ở Quận 7?"
- "Định giá căn hộ 100m2 khu Bình Thạnh"

---

## 🎯 Service Requirements

### 1. **Core Functionality**
Your service must:
- Analyze property market prices based on input attributes
- Query similar properties from database/external sources
- Calculate price range, average, trends
- Return confidence score for the analysis
- Support Vietnamese real estate market

### 2. **Response Time**
- Target: < 3 seconds per request
- Max: < 5 seconds

### 3. **Reasoning/Iteration**
You can implement internal reasoning loop (optional):
- Analyze → Check confidence → Refine → Re-analyze
- Max 3 iterations within single request
- Exit when confidence >= 80% or max iterations reached

---

## 🔌 API Contract

### **Endpoint 1: Price Consultation** (Required)

#### `POST /api/v1/price-consultation`

**Request Format:**
```json
{
  "property_info": {
    "property_type": "apartment",          // Required: apartment, house, villa, land
    "bedrooms": 2,                         // Optional: number of bedrooms
    "bathrooms": 2,                        // Optional: number of bathrooms
    "area": 80.0,                          // Optional: area in m²
    "district": "District 2",              // Optional: district name
    "city": "Ho Chi Minh City",            // Optional: city name
    "amenities": ["pool", "gym"],          // Optional: list of amenities
    "floor": 15,                           // Optional: floor number
    "building": "Vinhomes Central Park"    // Optional: building/project name
  },
  "user_query": "Căn hộ 2PN Quận 2 giá bao nhiêu?",  // Original user query
  "language": "vi",                        // Language: vi, en, th, ja
  "options": {
    "include_trend": true,                 // Include price trend analysis
    "include_comparison": true,            // Include property comparison
    "max_samples": 20,                     // Max number of market samples
    "radius_km": 2.0                       // Search radius in km
  }
}
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "price_analysis": {
      "average_price": 5200000000,         // Average price in VND
      "min_price": 4500000000,             // Minimum price in VND
      "max_price": 6800000000,             // Maximum price in VND
      "median_price": 5100000000,          // Median price in VND
      "currency": "VND",
      "price_per_sqm": 65000000            // Price per m² (if area provided)
    },
    "market_data": {
      "sample_count": 12,                  // Number of similar properties analyzed
      "data_sources": ["opensearch", "external_api"],  // Data sources used
      "geographic_coverage": "District 2", // Geographic area covered
      "time_range": "Last 6 months"        // Time range of data
    },
    "confidence": {
      "score": 0.85,                       // Confidence score (0.0 - 1.0)
      "level": "high",                     // high, medium, low
      "reason": "Sufficient market data with recent listings"
    },
    "trend": {                             // Optional: if include_trend=true
      "direction": "increasing",           // increasing, decreasing, stable
      "percentage": 8.5,                   // Percentage change
      "period": "6 months",
      "description_vi": "Giá tăng 8.5% trong 6 tháng qua"
    },
    "insights": {                          // Market insights
      "summary_vi": "Thị trường khá ổn định với giá trung bình 5.2 tỷ",
      "summary_en": "Market is stable with average price of 5.2 billion VND",
      "notes": [
        "Có phân khúc cao cấp trong khu vực",
        "Giá dao động nhiều do vị trí"
      ]
    },
    "comparison": [                        // Optional: if include_comparison=true
      {
        "property_id": "prop_123",
        "price": 5000000000,
        "similarity_score": 0.92,
        "differences": ["Higher floor", "No pool view"]
      }
    ],
    "processing_info": {
      "iterations": 2,                     // Number of analysis iterations
      "execution_time_ms": 1850,           // Execution time in ms
      "timestamp": "2025-11-17T10:30:00Z"
    }
  },
  "message": "Price consultation completed successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "INSUFFICIENT_DATA",           // Error code
    "message": "Not enough market data for this area",
    "details": {
      "sample_count": 2,
      "min_required": 5
    }
  },
  "data": null
}
```

**Error Codes:**
- `INSUFFICIENT_DATA` - Not enough market samples (< 5)
- `INVALID_PROPERTY_INFO` - Missing or invalid property attributes
- `SERVICE_ERROR` - Internal service error
- `TIMEOUT` - Analysis timeout (> 5 seconds)
- `EXTERNAL_API_ERROR` - External data source failed

---

### **Endpoint 2: Health Check** (Required)

#### `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "price_consultation_service",
  "version": "1.0.0",
  "dependencies": {
    "opensearch": "connected",
    "external_api": "connected",
    "redis": "connected"
  }
}
```

---

### **Endpoint 3: Service Info** (Optional)

#### `GET /api/v1/info`

**Response:**
```json
{
  "service": "price_consultation_service",
  "version": "1.0.0",
  "capabilities": [
    "price_analysis",
    "trend_analysis",
    "property_comparison"
  ],
  "supported_languages": ["vi", "en", "th", "ja"],
  "max_iterations": 3,
  "avg_response_time_ms": 2200
}
```

---

## 🔗 Integration with Orchestrator

### **How Orchestrator Calls Your Service:**

1. **User sends query** → Orchestrator (:8090)
2. **Orchestrator classifies intent** → PRICE_CONSULTATION
3. **Orchestrator extracts entities** → property_type, district, bedrooms, etc.
4. **Orchestrator calls your service:**
   ```bash
   POST http://price-consultation-service:8087/api/v1/price-consultation
   Content-Type: application/json
   ```
5. **Your service analyzes & responds**
6. **Orchestrator formats response** → Returns to user

### **Network Configuration:**

All services run in Docker network: `ree-ai-network`

**Your service name in docker-compose.yml:**
```yaml
price-consultation-service:
  build: ./your-service-directory
  container_name: ree-ai-price-consultation
  ports:
    - "8087:8087"
  environment:
    - PORT=8087
    - OPENSEARCH_HOST=opensearch
    - OPENSEARCH_PORT=9200
  networks:
    - ree-ai-network
```

**Orchestrator will call:**
```
http://price-consultation-service:8087/api/v1/price-consultation
```

---

## 📊 Data Sources Available

### **1. OpenSearch** (Primary - Internal)
- **Host:** `opensearch:9200` (within Docker network)
- **Index:** `properties`
- **Authentication:** None (DISABLE_SECURITY_PLUGIN=true)

**Query similar properties:**
```bash
curl -X POST http://opensearch:9200/properties/_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"match": {"property_type": "apartment"}},
          {"match": {"district": "District 2"}}
        ],
        "filter": [
          {"range": {"bedrooms": {"gte": 1, "lte": 3}}}
        ]
      }
    },
    "size": 20
  }'
```

**Property document structure:**
```json
{
  "property_id": "prop_12345",
  "title": "Căn hộ 2PN view sông",
  "property_type": "apartment",
  "price": 5200000000,
  "bedrooms": 2,
  "bathrooms": 2,
  "area": 80,
  "district": "District 2",
  "city": "Ho Chi Minh City",
  "amenities": ["pool", "gym"],
  "created_at": "2025-11-01T10:00:00Z",
  "embedding": [0.123, 0.456, ...]  // Vector embedding
}
```

### **2. PostgreSQL** (Secondary - Optional)
- **Host:** `postgres:5432`
- **Database:** `ree_ai`
- **User/Pass:** See `.env` file

**Tables you might need:**
- `properties` - Property listings
- `price_history` - Historical price data

### **3. External APIs** (Your responsibility)
If you want to query external sources:
- Government real estate databases
- Public transaction records
- Real estate portal APIs

---

## 🧪 Testing Your Service

### **Test 1: Simple Query**
```bash
curl -X POST http://localhost:8087/api/v1/price-consultation \
  -H "Content-Type: application/json" \
  -d '{
    "property_info": {
      "property_type": "apartment",
      "bedrooms": 2,
      "district": "District 2"
    },
    "user_query": "Căn hộ 2PN Quận 2 giá bao nhiêu?",
    "language": "vi"
  }'
```

**Expected response time:** < 3 seconds
**Expected confidence:** 0.6 - 0.9 (depending on data availability)

### **Test 2: Complex Query**
```bash
curl -X POST http://localhost:8087/api/v1/price-consultation \
  -H "Content-Type: application/json" \
  -d '{
    "property_info": {
      "property_type": "apartment",
      "bedrooms": 3,
      "area": 100,
      "district": "District 7",
      "amenities": ["pool", "gym"]
    },
    "user_query": "Tôi muốn biết giá căn hộ 3PN có hồ bơi ở Q7",
    "language": "vi",
    "options": {
      "include_trend": true,
      "include_comparison": true
    }
  }'
```

### **Test 3: Health Check**
```bash
curl http://localhost:8087/health
```

---

## 📦 Service Implementation Guide

### **Recommended Tech Stack:**
- **Language:** Python 3.10+
- **Framework:** FastAPI (same as other services)
- **Base class:** Extend `core.base_service.BaseService`
- **HTTP Client:** httpx (async)
- **Dependencies:** opensearch-py, asyncpg (if using PostgreSQL)

### **Project Structure:**
```
services/price_consultation_service/
├── main.py                    # FastAPI app entry point
├── Dockerfile                 # Docker build instructions
├── requirements.txt           # Python dependencies
├── market_analyzer.py         # Market data analysis logic
├── confidence_scorer.py       # Confidence calculation
├── trend_analyzer.py          # Price trend analysis (optional)
└── external_api_client.py     # External API integration (optional)
```

### **Skeleton Code:**
```python
# services/price_consultation_service/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx

app = FastAPI(title="Price Consultation Service")

class PropertyInfo(BaseModel):
    property_type: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    district: Optional[str] = None
    city: Optional[str] = None
    amenities: Optional[List[str]] = None

class ConsultationRequest(BaseModel):
    property_info: PropertyInfo
    user_query: str
    language: str = "vi"
    options: Optional[Dict] = None

@app.post("/api/v1/price-consultation")
async def price_consultation(request: ConsultationRequest):
    """
    Main endpoint for price consultation

    Your implementation:
    1. Query OpenSearch for similar properties
    2. Calculate price statistics (avg, min, max)
    3. Score confidence based on data quality
    4. Optionally: trend analysis, comparison
    5. Return formatted response
    """

    # Step 1: Query similar properties
    market_data = await query_opensearch(request.property_info)

    # Step 2: Calculate statistics
    price_analysis = calculate_price_stats(market_data)

    # Step 3: Calculate confidence
    confidence = calculate_confidence(market_data)

    # Step 4: Optional enhancements
    trend = None
    if request.options and request.options.get("include_trend"):
        trend = analyze_trend(market_data)

    # Step 5: Return response
    return {
        "success": True,
        "data": {
            "price_analysis": price_analysis,
            "market_data": {
                "sample_count": len(market_data),
                "data_sources": ["opensearch"]
            },
            "confidence": confidence,
            "trend": trend,
            "insights": generate_insights(price_analysis, request.language)
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "price_consultation_service",
        "version": "1.0.0"
    }

async def query_opensearch(property_info: PropertyInfo):
    """Query OpenSearch for similar properties"""
    # Your implementation here
    pass

def calculate_price_stats(market_data):
    """Calculate price statistics"""
    # Your implementation here
    pass

def calculate_confidence(market_data):
    """Calculate confidence score"""
    # Your implementation here
    pass
```

---

## 🐳 Docker Integration

### **Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements
COPY services/price_consultation_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY services/price_consultation_service/ ./services/price_consultation_service/
COPY core/ ./core/
COPY shared/ ./shared/

# Expose port
EXPOSE 8087

# Run service
CMD ["uvicorn", "services.price_consultation_service.main:app", "--host", "0.0.0.0", "--port", "8087"]
```

### **Add to docker-compose.yml:**
```yaml
# Add this service to docker-compose.yml
price-consultation-service:
  build:
    context: .
    dockerfile: services/price_consultation_service/Dockerfile
  container_name: ree-ai-price-consultation
  environment:
    - OPENSEARCH_HOST=opensearch
    - OPENSEARCH_PORT=9200
    - DEBUG=${DEBUG:-false}
  ports:
    - "8087:8087"
  depends_on:
    - opensearch
  networks:
    - ree-ai-network
  profiles:
    - real
    - all
```

---

## ✅ Acceptance Criteria

Your service is ready to integrate when:

- [ ] **Endpoint `/api/v1/price-consultation` works**
  - Returns valid price analysis
  - Response time < 3 seconds
  - Includes confidence score

- [ ] **Health check `/health` returns status**

- [ ] **Error handling implemented**
  - Handles insufficient data
  - Returns proper error codes
  - Doesn't crash on invalid input

- [ ] **OpenSearch integration working**
  - Can query properties index
  - Filters by property attributes

- [ ] **Confidence scoring implemented**
  - Returns score 0.0 - 1.0
  - Score reflects data quality

- [ ] **Vietnamese language support**
  - Insights in Vietnamese
  - Handles Vietnamese property terms

- [ ] **Dockerized**
  - Dockerfile builds successfully
  - Runs in docker-compose
  - Connects to ree-ai-network

---

## 📞 Integration Meeting

Once your service is ready:

1. **Demo your API:**
   ```bash
   # Show us the request/response
   curl -X POST http://localhost:8087/api/v1/price-consultation ...
   ```

2. **Share metrics:**
   - Average response time
   - Typical confidence scores
   - Data source coverage

3. **Discuss:**
   - Error handling strategy
   - Fallback behavior (if data insufficient)
   - Rate limiting needs
   - Monitoring/logging

4. **Integration test:**
   - We'll test calling your service from orchestrator
   - Fix any issues together
   - Deploy to staging

---

## 📚 Resources

**Existing services for reference:**
- `services/classification/main.py` - FastAPI structure
- `services/attribute_extraction/main.py` - OpenSearch queries
- `core/base_service.py` - Base service class

**OpenSearch docs:**
- https://opensearch.org/docs/latest/query-dsl/

**Docker network:**
- All services communicate via `ree-ai-network`
- Use service names as hostnames (e.g., `opensearch`, `postgres`)

---

## ❓ Questions?

Contact orchestrator team:
- **Slack:** #ree-ai-orchestrator
- **GitHub Issues:** Tag `integration/price-consultation`
- **Email:** [Your team email]

---

**Good luck building! 🚀**

We're excited to see your price consultation service integrated into the REE AI platform!

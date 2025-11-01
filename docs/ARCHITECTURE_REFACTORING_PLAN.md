# Architecture Refactoring Plan - REE AI

**Created**: 2025-11-01
**Status**: 🔴 CRITICAL - Foundation architecture is incorrect
**Priority**: P0 - Must fix before any feature expansion

---

## 🎯 Executive Summary

The current implementation violates the core architectural principle of REE AI:

> **Properties have infinite, non-standardized attributes → MUST use OpenSearch flexible JSON storage**

**Current State**: ❌ Using PostgreSQL rigid schema for properties
**Target State**: ✅ OpenSearch for ALL properties, PostgreSQL ONLY for users/conversations

---

## ❌ Critical Issues Identified

### 1. DB Gateway - Wrong Data Storage (`services/db_gateway/main.py`)

**Lines 88-114**: PostgreSQL connection for properties
```python
# ❌ WRONG - Properties should NOT be in PostgreSQL
db_pool = await asyncpg.create_pool(
    host=settings.POSTGRES_HOST,
    ...
)
count = await conn.fetchval("SELECT COUNT(*) FROM properties")  # WRONG TABLE
```

**Lines 168-274**: `/search` endpoint queries PostgreSQL
```python
# ❌ WRONG - Should use OpenSearch hybrid search (vector + BM25)
query_sql = f"""
    SELECT id, title, price, location, bedrooms, bathrooms, area,
           description, property_type, url
    FROM properties  -- WRONG: rigid schema cannot capture infinite attributes
    WHERE {where_clause}
    ...
"""
```

**Why This is Wrong:**
- PostgreSQL schema forces properties into rigid columns: `bedrooms`, `bathrooms`, `area`
- **Căn hộ** needs: pool, gym, view, balcony_direction, security_level, etc.
- **Biệt thự** needs: private_garden, wine_cellar, garage_capacity, roof_terrace, etc.
- **Nhà phố** needs: street_frontage, alley_width, number_of_floors, etc.
- Cannot add new attributes without ALTER TABLE (violates core value proposition)

---

### 2. Crawl4AI Implementation - Missing LLM Extraction

**Location**: `tests/crawl_and_store.py` (based on user feedback)

**Current State**:
- Crawls raw HTML data
- Saves to PostgreSQL without attribute extraction
- Result: 20,901 properties with `bedrooms=0`, `property_type=""`

**What Should Happen**:
1. Crawl page HTML
2. **Use LLM to analyze and extract ALL attributes** (not just standard ones)
3. Generate vector embeddings for semantic search
4. **Store in OpenSearch as flexible JSON**

**Example Output Should Be:**
```json
{
  "property_id": "bds_123",
  "title": "Biệt thự Phú Mỹ Hưng cao cấp",
  "price": 15000000000,
  "district": "Quận 7",
  "property_type": "biệt thự",

  // Standard attributes (extracted by LLM)
  "bedrooms": 5,
  "bathrooms": 6,
  "area": 300,

  // Villa-specific attributes (extracted by LLM - UNLIMITED!)
  "private_garden": "200m² landscaped garden",
  "wine_cellar": "50-bottle climate controlled",
  "rooftop_terrace": "Sky garden with BBQ area",
  "smart_home": "Full Lutron system",
  "garage": "2-car covered garage",
  "swimming_pool": "15m infinity pool",
  "security": "24/7 armed guards + biometric access",

  // Vector embedding for semantic search
  "embedding": [0.123, 0.456, ...],  // 768-dim vector

  // Any other attribute LLM finds
  "anything_else": "Flexible JSON allows unlimited fields"
}
```

---

## ✅ Correct Architecture

### Data Storage Strategy

```
┌──────────────────────────────────────────────────────────┐
│  OpenSearch (PRIMARY - Property Data)                    │
│  ✅ Index: "properties"                                  │
│  ✅ Flexible JSON documents (unlimited attributes)       │
│  ✅ Vector embeddings (768-dim for semantic search)      │
│  ✅ BM25 full-text search (keyword matching)             │
│  ✅ Hybrid search combines both → best results           │
└──────────────────────────────────────────────────────────┘
                           ↑
                           │ READ/WRITE properties
                           │
           ┌───────────────┴────────────────┐
           │       DB Gateway               │
           │  (Abstracts data operations)   │
           └───────────────┬────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────┐
│  PostgreSQL (SECONDARY - Structured Data ONLY)           │
│  ✅ Table: "users" (email, password_hash, created_at)    │
│  ✅ Table: "conversations" (user_id, conversation_id)    │
│  ✅ Table: "messages" (message_id, content, timestamp)   │
│  ❌ NO "properties" table - properties belong in OpenSea │
└──────────────────────────────────────────────────────────┘
```

---

## 📋 Refactoring Tasks

### Phase 1: DB Gateway Refactoring (Priority: P0)

**File**: `services/db_gateway/main.py`

**Changes Required:**

1. **Replace PostgreSQL connection with OpenSearch client** (lines 88-114):
```python
# BEFORE (WRONG):
import asyncpg
db_pool = await asyncpg.create_pool(...)

# AFTER (CORRECT):
from opensearchpy import AsyncOpenSearch
opensearch_client = AsyncOpenSearch(
    hosts=[{'host': settings.OPENSEARCH_HOST, 'port': 9200}],
    http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD)
)
```

2. **Rewrite `/search` endpoint** (lines 168-274):
```python
# BEFORE (WRONG): PostgreSQL ILIKE pattern matching
query_sql = f"SELECT ... FROM properties WHERE title ILIKE ..."

# AFTER (CORRECT): OpenSearch hybrid search
search_body = {
    "query": {
        "bool": {
            "should": [
                # Vector semantic search
                {"knn": {"embedding": {"vector": query_embedding, "k": 10}}},
                # BM25 keyword search
                {"multi_match": {"query": request.query, "fields": ["title^3", "description"]}}
            ]
        }
    },
    "size": request.limit
}
results = await opensearch_client.search(index="properties", body=search_body)
```

3. **Remove price/area parsing utilities** (lines 23-74):
   - These are for PostgreSQL text fields
   - OpenSearch should store numeric values directly

4. **Update health check** (lines 145-165):
```python
# BEFORE: Check PostgreSQL properties count
property_count = await conn.fetchval("SELECT COUNT(*) FROM properties")

# AFTER: Check OpenSearch properties count
count_response = await opensearch_client.count(index="properties")
property_count = count_response['count']
```

---

### Phase 2: Crawl4AI Refactoring (Priority: P0)

**File**: `tests/crawl_and_store.py` (needs review)

**Changes Required:**

1. **Add LLM extraction step**:
```python
async def extract_property_attributes(html: str, basic_info: dict) -> dict:
    """Use LLM to extract ALL attributes from property page"""

    prompt = f"""Analyze this real estate listing and extract ALL attributes.

    HTML Content: {html[:5000]}  # Truncate for token limits

    Extract:
    - Standard: bedrooms, bathrooms, area, price, location
    - Property-specific: pool, garden, view, amenities, features, etc.
    - ANY OTHER relevant attribute you find

    Return as JSON with unlimited fields."""

    llm_response = await call_llm(prompt)
    attributes = json.loads(llm_response)
    return attributes
```

2. **Generate vector embeddings**:
```python
async def generate_embedding(text: str) -> List[float]:
    """Generate 768-dim vector for semantic search"""
    response = await openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding
```

3. **Store in OpenSearch** (not PostgreSQL):
```python
# BEFORE (WRONG):
await conn.execute("""
    INSERT INTO properties (title, price, bedrooms, bathrooms, ...)
    VALUES ($1, $2, $3, $4, ...)
""")

# AFTER (CORRECT):
property_doc = {
    **attributes,  # All LLM-extracted attributes (unlimited!)
    "embedding": embedding,  # Vector for semantic search
    "crawled_at": datetime.utcnow().isoformat()
}
await opensearch_client.index(
    index="properties",
    body=property_doc
)
```

---

### Phase 3: Database Schema Cleanup (Priority: P1)

**PostgreSQL** should ONLY have:
```sql
-- ✅ KEEP: User management
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ✅ KEEP: Conversation history
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ✅ KEEP: Chat messages
CREATE TABLE messages (
    message_id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(conversation_id),
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ❌ REMOVE: Properties table (move to OpenSearch)
DROP TABLE IF EXISTS properties;
```

**OpenSearch** should have:
```json
// Index: "properties"
// Mapping with flexible schema
{
  "mappings": {
    "properties": {
      "property_id": {"type": "keyword"},
      "title": {"type": "text"},
      "description": {"type": "text"},
      "price": {"type": "long"},
      "district": {"type": "keyword"},
      "city": {"type": "keyword"},
      "property_type": {"type": "keyword"},

      // Standard attributes (but optional)
      "bedrooms": {"type": "integer"},
      "bathrooms": {"type": "integer"},
      "area": {"type": "float"},

      // Vector embedding
      "embedding": {
        "type": "dense_vector",
        "dims": 768
      },

      // ✅ CRITICAL: Dynamic mapping enabled!
      // This allows ANY new field without schema changes
      "dynamic": "true"
    }
  }
}
```

---

## 🚀 Implementation Plan

### Step 1: Document Review (DONE ✅)
- [x] Update CLAUDE.md with correct architecture
- [x] Update README.md with core value proposition
- [x] Create this refactoring plan

### Step 2: DB Gateway Refactoring (NEXT)
- [ ] Add `opensearch-py` to requirements.txt
- [ ] Implement OpenSearch client initialization
- [ ] Rewrite `/search` endpoint with hybrid search
- [ ] Rewrite `/properties/{id}` endpoint
- [ ] Rewrite `/stats` endpoint
- [ ] Update health checks
- [ ] Remove PostgreSQL properties logic

### Step 3: Crawl4AI Refactoring
- [ ] Review current implementation
- [ ] Add LLM extraction function
- [ ] Add embedding generation
- [ ] Switch from PostgreSQL to OpenSearch storage
- [ ] Test with sample properties

### Step 4: Database Migration
- [ ] Export existing PostgreSQL properties to JSON
- [ ] Generate embeddings for existing data
- [ ] Bulk import to OpenSearch
- [ ] Verify data integrity
- [ ] Drop PostgreSQL properties table

### Step 5: Testing & Validation
- [ ] Test hybrid search (vector + BM25)
- [ ] Test semantic queries ("tìm nhà gần trường quốc tế")
- [ ] Test flexible attributes (villa vs apartment)
- [ ] Performance benchmarks
- [ ] Update integration tests

---

## ⚠️ Critical Notes

1. **DO NOT** add more features until this refactoring is complete
2. **DO NOT** expand Crawl4AI until LLM extraction is implemented
3. **DO NOT** create more services until foundation is solid

**Why?** Building on wrong architecture = technical debt → complete rewrite later

---

## 📊 Success Criteria

After refactoring, the system must support:

✅ **Flexible Attributes**:
```python
# Căn hộ with apartment-specific attributes
{"property_type": "căn hộ", "pool": true, "gym": true, "view": "sông Sài Gòn"}

# Biệt thự with villa-specific attributes
{"property_type": "biệt thự", "wine_cellar": "50 bottles", "private_garden": "200m²"}

# Any new attribute without code changes!
{"rooftop_helipad": true}  # ← Can add this without ALTER TABLE
```

✅ **Semantic Search**:
```python
query = "tìm nhà gần trường quốc tế có sân vườn"
# → Vector search understands intent, returns properties near international schools with gardens
# → Even if exact keywords "trường quốc tế" aren't in listing
```

✅ **Hybrid Search**:
```python
# Combines:
# - Vector search (semantic understanding)
# - BM25 (keyword matching)
# → Best of both worlds
```

---

## 🎯 Timeline Estimate

- **DB Gateway Refactoring**: 2-3 days
- **Crawl4AI Refactoring**: 2-3 days
- **Database Migration**: 1 day
- **Testing & Validation**: 1-2 days

**Total**: 6-9 days for complete architectural fix

---

**Next Step**: Start with DB Gateway refactoring → Replace PostgreSQL with OpenSearch

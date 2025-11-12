# Orchestrator Flow Documentation

**Version:** 1.0
**Last Updated:** 2025-01-12
**Author:** REE AI Team

---

## Table of Contents

1. [Overview](#overview)
2. [Case 1: Property Posting (Dang tin BDS)](#case-1-property-posting)
3. [Case 2: Property Search (Tim kiem BDS)](#case-2-property-search)
4. [Case 3: Price Consultation (Tu van gia)](#case-3-price-consultation)
5. [Case 4: General Chat (Hoi dap thuong)](#case-4-general-chat)
6. [Service Integration Map](#service-integration-map)
7. [Error Handling](#error-handling)

---

## Overview

Orchestrator is the **central routing layer** (Layer 2) that:
- Detects user intent using Classification Service
- Routes requests to appropriate handlers
- Coordinates multiple AI services
- Manages conversation memory
- Supports multimodal inputs (text + images)

### Main Classification Types

| Classification Type | Sub-Types | Intent Codes | Handler Method |
|---------------------|-----------|--------------|----------------|
| 1. Dang tin BDS | 1.1 Tin ban<br>1.2 Tin cho thue | `POST_SALE`<br>`POST_RENT` | `_handle_property_posting()` |
| 2. Tim kiem BDS | 2.1 Tim BDS ban<br>2.2 Tim BDS cho thue | `SEARCH_BUY`<br>`SEARCH_RENT` | `_handle_search()` |
| 3. Tu van gia | - | `PRICE_CONSULTATION` | **Not implemented yet** |
| 4. Hoi dap thuong | - | `CHAT` | `_handle_chat()` |

---

## Case 1: Property Posting

**Intent Codes:** `POST_SALE`, `POST_RENT`
**Handler:** `_handle_property_posting()`
**Purpose:** Help users create property listings by extracting information and providing completeness feedback

### Flow Diagram

```
User Query: "Toi co nha can ban o Q7, 2PN, 5 ty"
    |
    v
[Step 1: Attribute Extraction]
    |--- Call: POST /extract-query (Extraction Service:8084)
    |--- Input: {query, intent: "POST"}
    |--- Output: {entities: {property_type, district, bedrooms, price, area...}, confidence}
    |
    v
[Step 2: Completeness Assessment]
    |--- Call: POST /assess (Completeness Service:8086)
    |--- Input: {property_data: {transaction_type, ...entities}}
    |--- Output: {overall_score, interpretation, missing_fields, suggestions, strengths}
    |
    v
[Step 3: Feedback Generation]
    |--- Build response with:
    |    - Acknowledgment
    |    - What we understood
    |    - Completeness score
    |    - Strengths (if score >= 60)
    |    - Missing fields
    |    - Priority actions
    |--- Save to conversation memory
    |
    v
Response: "Cam on ban da muon dang tin! Toi da hieu:
          - Loai: Nha o
          - Khu vuc: Quan 7
          - Phong ngu: 2PN
          ...
          Danh gia do day du: 65/100 - Can bo sung
          De hoan thien tin dang, ban can:
          - Them dia chi cu the
          - Mo ta chi tiet..."
```

### Step Details

#### Step 1: Attribute Extraction
**Service:** Extraction Service (port 8084)
**Endpoint:** `POST /extract-query`
**Timeout:** 30s

**Input:**
```json
{
  "query": "Toi co nha can ban o Q7, 2PN, 5 ty",
  "intent": "POST"
}
```

**Output:**
```json
{
  "entities": {
    "property_type": "nha o",
    "district": "Quan 7",
    "bedrooms": 2,
    "price": 5000000000,
    "area": null
  },
  "confidence": 0.85,
  "extraction_method": "llm_based"
}
```

#### Step 2: Completeness Assessment
**Service:** Completeness Service (port 8086)
**Endpoint:** `POST /assess`
**Timeout:** 30s

**Input:**
```json
{
  "property_data": {
    "transaction_type": "ban",
    "property_type": "nha o",
    "district": "Quan 7",
    "bedrooms": 2,
    "price": 5000000000
  },
  "include_examples": false
}
```

**Output:**
```json
{
  "overall_score": 65,
  "interpretation": "Can bo sung",
  "missing_fields": ["area", "address", "description", "images"],
  "suggestions": [
    "Them dien tich chinh xac (m2)",
    "Them dia chi cu the",
    "Them mo ta chi tiet ve nha"
  ],
  "strengths": [
    "Da co gia ro rang",
    "Xac dinh duoc so phong ngu",
    "Co khu vuc cu the"
  ],
  "priority_actions": [
    "Bo sung dien tich",
    "Them hinh anh"
  ]
}
```

#### Step 3: Response Generation
**Logic:**
```python
response_parts = []
response_parts.append(f"Cam on ban da muon dang tin {transaction_type} bat dong san! 🏠\n")

# Show understood attributes
response_parts.append("**Toi da hieu ve bat dong san cua ban:**\n")
for key, value in entities.items():
    response_parts.append(f"- {format_field_name(key)}: {value}\n")

# Show completeness score
response_parts.append(f"\n**Danh gia do day du: {overall_score}/100 - {interpretation}**\n")

# Show strengths (if score >= 60)
if strengths and overall_score >= 60:
    response_parts.append("\n**Diem manh:**\n")
    for strength in strengths[:3]:
        response_parts.append(f"✓ {strength}\n")

# Show missing fields
if missing_fields:
    response_parts.append("\n**Can bo sung:**\n")
    for field in missing_fields[:5]:
        response_parts.append(f"- {format_field_name(field)}\n")

# Priority actions
if priority_actions:
    response_parts.append("\n**De hoan thien tin dang, ban nen:**\n")
    for action in priority_actions:
        response_parts.append(f"{idx}. {action}\n")

return "".join(response_parts)
```

### Example Scenarios

#### Scenario 1: Low Completeness (Score < 50)
**Input:** "Can ban nha"
**Output:**
```
Cam on ban da muon dang tin ban bat dong san! 🏠

**Toi da hieu ve bat dong san cua ban:**
- Loai: Nha o

**Danh gia do day du: 20/100 - Thieu thong tin nhieu**

**Can bo sung:**
- Khu vuc (quan/huyen)
- Gia
- Dien tich
- So phong ngu
- Dia chi cu the

**De hoan thien tin dang, ban nen:**
1. Cung cap vi tri cu the (quan, phuong, duong)
2. Cho biet gia mong muon
3. Them thong tin ve dien tich va so phong
```

#### Scenario 2: High Completeness (Score >= 80)
**Input:** "Can ban nha o 123 Nguyen Van Linh, Q7, 150m2, 3PN 2WC, gia 8 ty, nha moi xay, full noi that"
**Output:**
```
Cam on ban da muon dang tin ban bat dong san! 🏠

**Toi da hieu ve bat dong san cua ban:**
- Loai: Nha o
- Khu vuc: Quan 7
- Dia chi: 123 Nguyen Van Linh
- Dien tich: 150 m²
- Phong ngu: 3PN
- Phong tam: 2WC
- Gia: 8,000,000,000 VND

**Danh gia do day du: 85/100 - Day du thong tin**

**Diem manh:**
✓ Thong tin day du ve vi tri va dien tich
✓ Gia ca ro rang
✓ Mo ta chi tiet ve trang thai

**De hoan thien tin dang, ban nen:**
1. Them hinh anh de tang do tin cay
2. Them thong tin phap ly (so do, so hong)
```

---

## Case 2: Property Search

**Intent Codes:** `SEARCH_BUY`, `SEARCH_RENT`
**Handler:** `_handle_search()`
**Purpose:** Find properties matching user requirements using intelligent ReAct Agent pattern

### ReAct Agent Pattern

The search handler implements a **4-step iterative reasoning pattern**:

```
REASONING → ACT → EVALUATE → ITERATE (if needed)
    ^                              |
    |______________________________|
         (max 2 iterations)
```

### Flow Diagram

```
User Query: "Tim can ho 2-3PN o Q2, gia 5-7 ty"
    |
    v
[Enrich with Conversation Context]
    |--- Get conversation history (PostgreSQL or from Open WebUI)
    |--- Enrich query if context relevant
    |
    v
[ITERATION 1]
    |
    |--- [STEP 1: REASONING]
    |    |--- Analyze query requirements
    |    |--- Extract: property_type, district, bedrooms, price_range
    |    |--- Output: {requirements, search_strategy}
    |
    |--- [STEP 2: ACT]
    |    |--- Call Classification Service
    |    |--- Determine mode: "filter" | "semantic" | "both"
    |    |--- Route to appropriate search:
    |    |    - Filter: Extraction → Document search
    |    |    - Semantic: Vector search
    |    |    - Hybrid: Combine both
    |    |--- Output: List[property_results]
    |
    |--- [STEP 3: EVALUATE]
    |    |--- Check result quality:
    |    |    - Count: >= 1 result?
    |    |    - Relevance: Match requirements?
    |    |    - Diversity: Multiple property types?
    |    |--- Output: {satisfied: bool, quality_score: float, issues: list}
    |
    |--- [STEP 4: DECIDE]
    |    |--- If satisfied (quality >= 0.7):
    |    |    └─> Generate response & return
    |    |
    |    |--- If NOT satisfied:
    |    |    └─> Try progressive relaxation strategies
    |
    v
[Progressive Relaxation Strategies]
    |
    |--- Strategy 1: Location-only search
    |    |--- Remove property_type, price, bedrooms
    |    |--- Keep only district/ward filters
    |    |--- If found → Return with suggestions
    |
    |--- Strategy 2: Semantic search fallback
    |    |--- Use vector search with original query
    |    |--- If found → Return with suggestions
    |
    |--- Strategy 3: Give up gracefully
    |    └─> "Xin loi, khong tim thay..."
    |
    v
Response Generation
```

### Step Details

#### STEP 1: REASONING - Analyze Requirements
**Method:** `_analyze_query_requirements()`
**Purpose:** Extract structured search requirements from natural language

**Example:**
```python
Input: "Tim can ho 2-3PN o Q2, gia 5-7 ty"

Output:
{
  "property_type": "can ho",
  "district": "Quan 2",
  "bedrooms": {"min": 2, "max": 3},
  "price": {"min": 5000000000, "max": 7000000000},
  "search_strategy": "filter",  # Use filter search for structured query
  "confidence": 0.9
}
```

#### STEP 2: ACT - Execute Search
**Method:** `_execute_search_internal()`

**Sub-flow:**
```
1. Call Classification Service
   POST /classify
   → {mode: "filter", primary_intent: "SEARCH_BUY"}

2. Route based on mode:

   a) Filter Mode:
      - Call Extraction Service: POST /extract-query
      - Call DB Gateway: POST /search-properties
      - Filter: property_type, district, bedrooms, price_min, price_max

   b) Semantic Mode:
      - Call DB Gateway: POST /vector-search
      - Use embeddings for semantic matching

   c) Hybrid Mode (future):
      - Combine filter + semantic results
      - Re-rank with Reranking Service
```

**Example - Filter Search:**
```python
# Step 2a: Attribute Extraction
extraction_response = await http_client.post(
    f"{extraction_url}/extract-query",
    json={"query": query, "intent": "SEARCH"}
)
# Output: {property_type: "can ho", district: "Quan 2", bedrooms: 2, ...}

# Step 2b: Document Search
search_response = await http_client.post(
    f"{db_gateway_url}/search-properties",
    json={
        "filters": {
            "property_type": "can ho",
            "district": "Quan 2",
            "bedrooms": {"$gte": 2, "$lte": 3},
            "price": {"$gte": 5000000000, "$lte": 7000000000}
        },
        "limit": 10
    }
)
# Output: [{property_id: "123", title: "...", price: 6500000000}, ...]
```

#### STEP 3: EVALUATE - Check Quality
**Method:** `_evaluate_results()`

**Quality Metrics:**
```python
def _evaluate_results(results, requirements):
    quality_score = 0.0
    issues = []

    # Metric 1: Result count (40% weight)
    if len(results) == 0:
        issues.append("No results found")
    elif len(results) < 3:
        quality_score += 0.2
        issues.append("Too few results")
    else:
        quality_score += 0.4

    # Metric 2: Relevance (40% weight)
    matches = sum(1 for r in results if matches_requirements(r, requirements))
    relevance = matches / len(results) if results else 0
    quality_score += relevance * 0.4

    # Metric 3: Diversity (20% weight)
    unique_types = len(set(r.get("property_type") for r in results))
    if unique_types >= 2:
        quality_score += 0.2

    return {
        "satisfied": quality_score >= 0.7,
        "quality_score": quality_score,
        "issues": issues
    }
```

#### STEP 4: DECIDE - Next Action

**Decision Tree:**
```
Quality Score >= 0.7?
    ├─ YES: Generate response & return
    └─ NO: Try relaxation strategies
        |
        ├─ Consecutive failures >= 2?
        |   ├─ YES: Progressive relaxation
        |   |   ├─ Strategy 1: Location-only
        |   |   ├─ Strategy 2: Semantic fallback
        |   |   └─ Strategy 3: Give up
        |   └─ NO: Continue to next iteration
        |
        └─ Iteration < max_iterations?
            ├─ YES: Refine query & retry
            └─ NO: Ask clarification with alternatives
```

### Progressive Relaxation Strategies

When strict filters return 0 results, orchestrator tries **intelligent fallback strategies**:

#### Strategy 1: Location-Only Search
**Purpose:** Find ANY properties in requested area, ignore other filters

```python
async def _try_location_only_search(requirements):
    """
    Remove: property_type, price, bedrooms
    Keep: district, ward
    """
    relaxed_filters = {
        "district": requirements.get("district")
    }

    response = await http_client.post(
        f"{db_gateway_url}/search-properties",
        json={"filters": relaxed_filters, "limit": 10}
    )

    return response.json().get("results", [])
```

**Example:**
```
Original: "Tim can ho 2PN o Q2, gia 5-7 ty" → 0 results
Relaxed: "Tim bat dong san o Q2" → 15 results found

Response: "Toi khong tim thay can ho 2PN voi gia 5-7 ty o Q2.
           Tuy nhien, co 15 bat dong san khac o Q2:
           - 5 can ho (gia 3-4 ty)
           - 7 nha pho (gia 8-12 ty)
           - 3 dat nen (gia 2-3 ty)
           Ban co muon xem cac tuy chon nay khong?"
```

#### Strategy 2: Semantic Search Fallback
**Purpose:** Use vector embeddings for fuzzy matching

```python
async def _execute_semantic_search(query):
    """
    Use OpenSearch vector search with embeddings
    """
    response = await http_client.post(
        f"{db_gateway_url}/vector-search",
        json={
            "query": query,
            "limit": 10,
            "min_score": 0.7
        }
    )

    return response.json().get("results", [])
```

#### Strategy 3: Give Up Gracefully
```python
return "Xin loi, toi khong tim thay bat dong san phu hop voi yeu cau cua ban. " \
       "Ban co the cung cap them thong tin hoac mo rong tieu chi tim kiem khong?"
```

### Search Modes Comparison

| Mode | When to Use | Services Called | Response Time |
|------|-------------|-----------------|---------------|
| **Filter** | Structured queries with specific attributes | Classification → Extraction → DB Gateway | ~2-3s |
| **Semantic** | Natural language, vague requirements | Classification → DB Gateway (vector) | ~1-2s |
| **Hybrid** | Complex queries needing both precision & recall | All above + Reranking | ~3-5s |

### Example Scenarios

#### Scenario 1: Successful Filter Search
**Input:** "Tim can ho 2PN o Q2, gia 5-7 ty"

**Execution:**
```
[ITERATION 1]
  REASONING: Extract filters {type: can ho, district: Q2, bedrooms: 2, price: 5-7ty}
  ACT: Filter search → Found 8 results
  EVALUATE: Quality = 0.85 (SATISFIED)
  → Generate response & return

Response: "Toi tim thay 8 can ho phu hop:
           1. Can ho The Sun Avenue - 2PN, 70m2, 6.2 ty
           2. Can ho Masteri Thao Dien - 2PN, 65m2, 6.8 ty
           ..."
```

#### Scenario 2: Progressive Relaxation
**Input:** "Tim biet thu co ho boi o Q1, gia duoi 20 ty"

**Execution:**
```
[ITERATION 1]
  REASONING: Extract {type: biet thu, district: Q1, amenities: pool, price: <20ty}
  ACT: Filter search → Found 0 results
  EVALUATE: Quality = 0.0 (NOT SATISFIED)
  → Try relaxation

[STRATEGY 1: Location-only]
  Relaxed filters: {district: Q1}
  → Found 12 properties (no villas with pools)

Response: "Toi khong tim thay biet thu co ho boi o Q1 voi gia duoi 20 ty.
           Tuy nhien, co 12 bat dong san khac o Q1:
           - 8 can ho cao cap (10-18 ty)
           - 4 nha pho (15-25 ty)
           Ban co muon:
           1. Mo rong tim kiem sang Q2, Q7 (co nhieu biet thu hon)?
           2. Tang ngan sach len 25-30 ty?
           3. Xem cac can ho penthouse co ho boi rieng?"
```

#### Scenario 3: Semantic Fallback
**Input:** "Tim nha gan truong quoc te, thoang mat, cho gia dinh 4 nguoi"

**Execution:**
```
[ITERATION 1]
  REASONING: Vague query, use semantic
  ACT: Semantic search → Found 5 results
  EVALUATE: Quality = 0.75 (SATISFIED)
  → Generate response

Response: "Toi tim thay 5 bat dong san phu hop cho gia dinh 4 nguoi:
           1. Can ho Vista Verde Q2 - Gan SSIS, 3PN, view cong vien
           2. Nha pho Thao Dien Q2 - Gan BIS, 4PN, san vuon rong
           ..."
```

---

## Case 3: Price Consultation

**Intent Code:** `PRICE_CONSULTATION`
**Status:** ⚠️ **Not implemented yet** (proposed flow below)
**Handler:** `_handle_price_consultation()` (to be created)

### Proposed Flow

```
User Query: "Can ho 2PN o Q2 gia bao nhieu?"
    |
    v
[Step 1: Extract Property Attributes]
    |--- Call Extraction Service
    |--- Extract: property_type, district, bedrooms, area, etc.
    |
    v
[Step 2: Price Analysis]
    |--- Call Price Suggestion Service (port 8087)
    |--- Input: {property_data, market_context}
    |--- Service performs:
    |    - Historical price analysis
    |    - Comparable properties search
    |    - Market trend analysis
    |    - ML-based price prediction
    |
    v
[Step 3: Generate Consultation Response]
    |--- Price range estimate
    |--- Market insights
    |--- Factors affecting price
    |--- Recommendations
    |
    v
Response: "Gia can ho 2PN o Q2 hien tai:

          **Gia tham khao:**
          - Trung binh: 5.2 ty (74 trieu/m2)
          - Thap nhat: 4.5 ty
          - Cao nhat: 6.8 ty

          **Yeu to anh huong:**
          - Vi tri gan Metro (+10-15%)
          - Tang cao, view dep (+5-10%)
          - Noi that cao cap (+500-800 trieu)

          **Xu huong thi truong:**
          - Q2 tang 8% trong 6 thang qua
          - Nhu cau cao gan KDC Thao Dien

          **Khuyen nghi:**
          Ban co the mua voi gia 5.0-5.5 ty la hop ly."
```

### Required Implementations

To implement this case, need to:

1. **Update Classification Service** (`services/classification/`)
   ```python
   # Add to classification logic
   PRICE_CONSULTATION_KEYWORDS = [
       "gia", "bao nhieu", "dinh gia", "tu van gia",
       "gia ca", "thi truong", "estimate", "valuation"
   ]

   # Add intent type
   if contains_price_consultation_keywords(query):
       return {"primary_intent": "PRICE_CONSULTATION", ...}
   ```

2. **Update Orchestrator** (`services/orchestrator/main.py`)
   ```python
   # In setup_routes() → orchestrate()
   elif primary_intent == "PRICE_CONSULTATION":
       intent = "price_consultation"

   # Add handler
   elif intent == "price_consultation":
       response_text = await self._handle_price_consultation(
           request.query,
           history=history
       )
   ```

3. **Create Handler Method**
   ```python
   async def _handle_price_consultation(
       self,
       query: str,
       history: List[Dict] = None
   ) -> str:
       """
       Handle price consultation workflow:
       1. Extract property attributes
       2. Call Price Suggestion Service
       3. Generate consultation response with market insights
       """
       # Step 1: Extract attributes
       extraction_response = await self.http_client.post(
           f"{self.extraction_url}/extract-query",
           json={"query": query, "intent": "PRICE"}
       )

       # Step 2: Get price analysis
       price_response = await self.http_client.post(
           f"{self.price_suggestion_url}/suggest",
           json={
               "property_data": extraction_response.json().get("entities"),
               "include_market_analysis": True
           }
       )

       # Step 3: Generate response
       price_data = price_response.json()
       return self._format_price_consultation_response(price_data)
   ```

4. **Enhance Price Suggestion Service** (if needed)
   - Add market trend analysis
   - Add comparable properties search
   - Add confidence intervals

---

## Case 4: General Chat

**Intent Code:** `CHAT`
**Handler:** `_handle_chat()`
**Purpose:** Handle general conversation, questions, greetings, and multimodal analysis

### Chat Types

The chat handler supports two modes:

1. **Text-only chat** (normal conversation)
2. **Multimodal chat** (with images/files)

### Flow Diagram

```
User Query: "Xin chao" or "Can ho nay the nao?" + [image.jpg]
    |
    v
[Detect Chat Type]
    |
    ├─ Has Files? ─ YES ─> [Multimodal Chat]
    |                       |
    |                       ├─ Use vision model (gpt-4o)
    |                       ├─ Vision-specific system prompt
    |                       └─ Analyze property images
    |
    └─ NO ─> [Text-only Chat]
              |
              ├─ Context-aware system prompt
              └─ Use conversation history
    |
    v
[Build Messages]
    |--- System prompt (different for text vs multimodal)
    |--- Conversation history (last 10 messages)
    |--- Current query (+ files if present)
    |
    v
[Call Core Gateway]
    |--- POST /chat/completions
    |--- Model: gpt-4o (multimodal) or gpt-4o-mini (text)
    |--- Max tokens: 1000 (multimodal) or 500 (text)
    |
    v
[Save to Memory]
    |--- Save user message
    |--- Save assistant response
    |
    v
Response: Natural language answer
```

### Text-Only Chat

**System Prompt Strategy:**
```
Bạn là trợ lý bất động sản thông minh và chuyên nghiệp.

HƯỚNG DẪN SỬ DỤNG LỊCH SỬ HỘI THOẠI:

1. **Phân biệt loại câu hỏi:**
   - Greeting/Chào hỏi: TRẢ LỜI ĐƠN GIẢN, không reference context cũ
   - Câu hỏi mới: TRẢ LỜI TRỰC TIẾP theo câu hỏi
   - Follow-up: SỬ DỤNG context trước đó

2. **Khi nào KHÔNG sử dụng context:**
   - User nói "xin chào", "hi", "cảm ơn"
   - User bắt đầu topic hoàn toàn mới

3. **Khi nào SỬ DỤNG context:**
   - User hỏi "căn đó", "dự án đó", "khu vực đó"
   - User hỏi chi tiết về property vừa tìm

VÍ DỤ:
- User trước: "Tìm nhà ở Quận 2"
- User hiện tại: "Xin chào"
  → Response: "Xin chào! Tôi có thể giúp gì?" (KHÔNG nhắc Q2)

- User hiện tại: "Căn đó có view không?"
  → Response: "Căn hộ ở Quận 2 mà bạn vừa hỏi..." (CÓ reference)
```

**Example:**
```python
# Input
query = "Xin chao"
history = [
    {"role": "user", "content": "Tim nha o Q2"},
    {"role": "assistant", "content": "Toi tim thay 5 can ho..."}
]

# Messages sent to LLM
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Tim nha o Q2"},
    {"role": "assistant", "content": "Toi tim thay 5 can ho..."},
    {"role": "user", "content": "Xin chao"}
]

# Response (LLM understands this is greeting, not follow-up)
"Xin chào! Tôi là trợ lý bất động sản. Tôi có thể giúp gì cho bạn?"
```

### Multimodal Chat (Vision Analysis)

**Trigger:** `request.files` is not empty

**System Prompt for Vision:**
```
Bạn là trợ lý bất động sản chuyên nghiệp với khả năng phân tích hình ảnh.

NHIỆM VỤ KHI PHÂN TÍCH HÌNH ẢNH:

1. MÔ TẢ chi tiết căn hộ/nhà từ hình ảnh:
   - Loại hình: Căn hộ, biệt thự, nhà phố, đất nền
   - Phong cách thiết kế và nội thất
   - Diện tích ước tính
   - View và hướng
   - Tiện ích trong ảnh

2. ĐÁNH GIÁ chất lượng và giá trị:
   - Tình trạng bất động sản
   - Mức độ sang trọng/cao cấp
   - Ước tính giá dựa trên vị trí

3. TƯ VẤN:
   - Phù hợp với nhu cầu gì
   - Điểm mạnh/yếu
   - Khuyến nghị đầu tư
```

**Example:**
```python
# Input
query = "Can ho nay the nao?"
files = [
    {
        "name": "apartment.jpg",
        "url": "data:image/jpeg;base64,/9j/4AAQ...",
        "type": "image/jpeg"
    }
]

# Messages sent to LLM
messages = [
    {"role": "system", "content": vision_system_prompt},
    {
        "role": "user",
        "content": "Can ho nay the nao?",
        "files": [{"name": "apartment.jpg", "url": "...", "type": "image/jpeg"}]
    }
]

# Model used: gpt-4o (supports vision)
# Max tokens: 1000 (more for detailed analysis)

# Response
"Đây là một căn hộ cao cấp với những đặc điểm sau:

**Loại hình:** Căn hộ chung cư
**Diện tích:** Ước tính 80-90m²

**Mô tả:**
- Phòng khách rộng rãi với cửa sổ lớn
- Nội thất hiện đại, gam màu trắng - gỗ
- View thành phố từ ban công
- Hệ thống chiếu sáng âm trần

**Đánh giá:**
- Tình trạng: Mới, đã hoàn thiện nội thất
- Phân khúc: Trung-cao cấp
- Ước tính giá: 5-7 tỷ (tùy vị trí)

**Điểm mạnh:**
✓ Thiết kế hiện đại, sang trọng
✓ Không gian thoáng đãng
✓ View đẹp

**Phù hợp:** Gia đình trẻ, chuyên gia nước ngoài"
```

### Conversation Context Enrichment

**Method:** `_enrich_query_with_context()`
**Purpose:** Add relevant context from history to current query

```python
async def _enrich_query_with_context(query, history):
    """
    Add context from recent conversation if relevant
    """
    if not history or len(history) < 2:
        return query

    # Check if query is follow-up (uses pronouns or references)
    is_followup = any(word in query.lower() for word in [
        "căn đó", "dự án đó", "khu vực đó", "property đó",
        "cái này", "con này", "thằng này"
    ])

    if not is_followup:
        return query

    # Find last property search in history
    for msg in reversed(history):
        if msg["role"] == "assistant" and "tìm thấy" in msg["content"]:
            context = extract_property_context(msg["content"])
            enriched = f"{query} (ngữ cảnh: {context})"
            return enriched

    return query
```

### Example Scenarios

#### Scenario 1: Simple Greeting
**Input:** "Xin chao"
**Response:**
```
Xin chào! Tôi là trợ lý bất động sản của REE AI.
Tôi có thể giúp bạn:
- Tìm kiếm bất động sản mua/thuê
- Tư vấn giá
- Đăng tin bán/cho thuê
- Trả lời câu hỏi về bất động sản

Bạn cần tôi hỗ trợ gì?
```

#### Scenario 2: Follow-up Question
**Conversation:**
```
User: "Tim can ho o Q2"
Assistant: "Toi tim thay 5 can ho o Q2: 1. The Sun Avenue..."

User: "Can ho dau tien gia bao nhieu?"
Assistant: "Căn hộ The Sun Avenue có giá 6.2 tỷ, diện tích 70m2..."
```

#### Scenario 3: Image Analysis
**Input:** "Danh gia can ho nay" + [image: luxury_apartment.jpg]
**Response:**
```
Dựa trên hình ảnh bạn gửi, đây là đánh giá chi tiết:

**Loại hình:** Căn hộ penthouse cao cấp

**Mô tả:**
- Diện tích: Ước tính 120-150m²
- Nội thất: Sang trọng, phong cách Châu Âu
- View: Toàn cảnh thành phố từ tầng cao
- Tiện ích: Ban công lớn, hệ thống đèn LED cao cấp

**Đánh giá giá trị:**
- Phân khúc: Cao cấp - sang trọng
- Ước tính: 10-15 tỷ (tùy vị trí)
- Thích hợp: Đầu tư, ở cho gia đình lớn

**Điểm mạnh:**
✓ Vị trí tầng cao, view đẹp
✓ Nội thất cao cấp, thiết kế tinh tế
✓ Không gian rộng rãi

**Lưu ý:**
- Cần xác nhận vị trí cụ thể để định giá chính xác
- Nên kiểm tra tình trạng pháp lý và sổ hồng
```

---

## Service Integration Map

### Service Dependencies by Case

```
Case 1: Property Posting
    Orchestrator (8090)
        ├─> Classification Service (8083) - Intent detection
        ├─> Extraction Service (8084) - Attribute extraction
        ├─> Completeness Service (8086) - Quality assessment
        └─> DB Gateway (8081) - Save to PostgreSQL (conversation history)

Case 2: Property Search
    Orchestrator (8090)
        ├─> Classification Service (8083) - Intent + mode detection
        ├─> Extraction Service (8084) - Structured filters
        ├─> DB Gateway (8081) - Search queries
        │   └─> OpenSearch (9200) - Document/vector search
        ├─> Reranking Service (8088) - Result optimization [optional]
        └─> Core Gateway (8080) - Response generation
            └─> LLM (Ollama/OpenAI)

Case 3: Price Consultation (proposed)
    Orchestrator (8090)
        ├─> Classification Service (8083) - Intent detection
        ├─> Extraction Service (8084) - Property attributes
        ├─> Price Suggestion Service (8087) - Market analysis
        └─> Core Gateway (8080) - Consultation response

Case 4: General Chat
    Orchestrator (8090)
        ├─> Core Gateway (8080) - LLM routing
        │   └─> LLM (GPT-4o for vision, GPT-4o-mini for text)
        └─> DB Gateway (8081) - Conversation memory
            └─> PostgreSQL (5432) - History storage
```

### Port Reference

| Service | Port | Purpose |
|---------|------|---------|
| Orchestrator | 8090 | Main routing layer |
| Core Gateway | 8080 | LLM routing (LiteLLM) |
| DB Gateway | 8081 | Database abstraction |
| Semantic Chunking | 8082 | Text chunking (not used in current flows) |
| Classification | 8083 | Intent detection |
| Extraction | 8084 | Attribute extraction |
| Completeness | 8086 | Listing quality assessment |
| Price Suggestion | 8087 | Price analysis |
| Reranking | 8088 | Search result optimization |
| OpenSearch | 9200 | Document + vector search |
| PostgreSQL | 5432 | User + conversation data |
| Redis | 6379 | Caching layer |

---

## Error Handling

### Standard Error Response Pattern

All handlers follow this error handling pattern:

```python
try:
    # Main logic
    result = await execute_logic()
    return result

except httpx.HTTPError as e:
    # Network/HTTP errors (service down, timeout)
    logger.error(f"Network error: {e}")
    return "Xin lỗi, hệ thống đang gặp sự cố kết nối. Vui lòng thử lại sau."

except (ValueError, KeyError, json.JSONDecodeError) as e:
    # Data validation errors
    logger.error(f"Data validation error: {e}")
    return "Xin lỗi, đã xảy ra lỗi xử lý dữ liệu. Vui lòng thử lại."

except Exception as e:
    # Unexpected errors
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    return "Xin lỗi, đã xảy ra lỗi không xác định. Vui lòng liên hệ hỗ trợ."
```

### Timeout Configuration

**Default Timeouts:**
```python
CLASSIFICATION_TIMEOUT = 10.0  # seconds
EXTRACTION_TIMEOUT = 30.0
COMPLETENESS_TIMEOUT = 30.0
SEARCH_TIMEOUT = 30.0
LLM_TIMEOUT = 60.0  # Longer for LLM generation
```

**Configurable in:** `shared/config.py`

### Graceful Degradation

When downstream services fail, orchestrator provides fallbacks:

```python
# Example: Classification Service down
try:
    classification = await call_classification_service(query)
except Exception:
    # Fallback to simple keyword detection
    classification = {
        "primary_intent": "SEARCH_BUY" if "tìm" in query else "CHAT",
        "mode": "semantic",
        "confidence": 0.5,
        "reasoning": "Fallback (classification service unavailable)"
    }
```

### Error Response Examples

| Error Type | User-Facing Message | Internal Log |
|------------|---------------------|--------------|
| Service timeout | "Hệ thống đang xử lý chậm. Vui lòng thử lại." | `TimeoutException: Classification service timeout after 10s` |
| No results found | "Không tìm thấy BĐS phù hợp. Bạn có thể mở rộng tiêu chí không?" | `INFO: Search returned 0 results, trying relaxation strategies` |
| Invalid input | "Tôi chưa hiểu yêu cầu. Bạn có thể nói rõ hơn không?" | `ValueError: Unable to extract property_type from query` |
| Service down | "Dịch vụ đang bảo trì. Vui lòng thử lại sau." | `HTTPError: POST http://extraction:8084/extract-query failed with 503` |

---

## Appendix: Complete Flow Examples

### Complete Flow 1: Property Posting

**User Input:** "Toi can dang tin ban can ho o The Sun Avenue, Q2, 2PN 2WC, 75m2, gia 6.5 ty, nha moi"

**Execution Trace:**
```
[00:00.000] POST /orchestrate
[00:00.010] Classification: primary_intent=POST_SALE, confidence=0.95
[00:00.015] Route to: _handle_property_posting()

[00:00.020] [Step 1/3] Extraction Service
            POST http://extraction:8084/extract-query
            Request: {query: "...", intent: "POST"}
            Response: {
              entities: {
                property_type: "can ho",
                project_name: "The Sun Avenue",
                district: "Quan 2",
                bedrooms: 2,
                bathrooms: 2,
                area: 75,
                price: 6500000000,
                condition: "moi"
              },
              confidence: 0.92
            }
[00:00.850] Extraction complete (830ms)

[00:00.855] [Step 2/3] Completeness Service
            POST http://completeness:8086/assess
            Request: {
              property_data: {
                transaction_type: "ban",
                ...entities
              }
            }
            Response: {
              overall_score: 75,
              interpretation: "Day du co ban",
              missing_fields: ["address", "images", "legal_docs"],
              suggestions: [
                "Them dia chi cu the (tang, so nha)",
                "Them hinh anh de tang do tin cay",
                "Xac nhan tinh trang phap ly"
              ],
              strengths: [
                "Thong tin day du ve dien tich va phong",
                "Gia ca ro rang",
                "Co ten du an cu the"
              ]
            }
[00:01.920] Completeness check complete (1065ms)

[00:01.925] [Step 3/3] Generate response
[00:01.950] Save to conversation memory (PostgreSQL)

[00:01.980] Response returned (total: 1980ms)
```

### Complete Flow 2: Property Search (Success Case)

**User Input:** "Tim can ho 2PN o Q2, gia 5-7 ty, gan metro"

**Execution Trace:**
```
[00:00.000] POST /orchestrate
[00:00.010] Classification: primary_intent=SEARCH_BUY, confidence=0.90
[00:00.015] Route to: _handle_search()

[00:00.020] [ReAct Agent] ITERATION 1/2

[00:00.025] [STEP 1: REASONING] Analyze requirements
            - property_type: "can ho"
            - district: "Quan 2"
            - bedrooms: 2
            - price_min: 5000000000
            - price_max: 7000000000
            - keywords: ["gan metro"]
            - strategy: "filter"

[00:00.030] [STEP 2: ACT] Execute search
[00:00.035]   → Classification Service
              POST /classify → {mode: "filter"}
[00:00.250]   ← Classification complete (215ms)

[00:00.255]   → Extraction Service
              POST /extract-query
[00:00.820]   ← Extraction complete (565ms)
              Filters: {
                property_type: "can ho",
                district: "Quan 2",
                bedrooms: {"$gte": 2, "$lte": 2},
                price: {"$gte": 5000000000, "$lte": 7000000000}
              }

[00:00.825]   → DB Gateway
              POST /search-properties
[00:01.450]   ← Search complete (625ms)
              Found: 8 properties

[00:01.455] [STEP 3: EVALUATE] Check quality
            - Result count: 8 (✓)
            - Relevance: 7/8 = 87.5% (✓)
            - Diversity: 1 type (acceptable)
            - Quality score: 0.85 (SATISFIED ✓)

[00:01.460] [STEP 4: DECIDE] Quality satisfied → Generate response
[00:01.465] → Core Gateway
            POST /chat/completions
            Generate natural language response from 8 results
[00:02.120] ← Response generated (655ms)

[00:02.125] Save to conversation memory

[00:02.150] Response returned (total: 2150ms)
```

### Complete Flow 3: Search with Progressive Relaxation

**User Input:** "Tim biet thu co ho boi o Q1, gia duoi 20 ty"

**Execution Trace:**
```
[00:00.000] POST /orchestrate
[00:00.010] Classification: primary_intent=SEARCH_BUY
[00:00.015] Route to: _handle_search()

[00:00.020] [ReAct Agent] ITERATION 1/2

[00:00.025] [STEP 1: REASONING]
            - property_type: "biet thu"
            - district: "Quan 1"
            - amenities: ["ho boi"]
            - price_max: 20000000000

[00:00.030] [STEP 2: ACT] Execute search
[00:01.250] ← Found: 0 properties

[00:01.255] [STEP 3: EVALUATE]
            - Result count: 0 (✗)
            - Quality score: 0.0 (NOT SATISFIED)
            - consecutive_no_results = 1

[00:01.260] [STEP 4: DECIDE] Try next iteration

[00:01.265] [ReAct Agent] ITERATION 2/2

[00:01.270] [STEP 1: REASONING] (refined query)
[00:01.275] [STEP 2: ACT] Execute search
[00:02.380] ← Found: 0 properties

[00:02.385] [STEP 3: EVALUATE]
            - Result count: 0 (✗)
            - consecutive_no_results = 2 (TRIGGER RELAXATION)

[00:02.390] [STRATEGY 1] Location-only search
            Relaxed filters: {district: "Quan 1"}
            (Remove: property_type, amenities, price)
[00:03.120] ← Found: 12 properties (8 apartments, 4 townhouses)

[00:03.125] Generate suggestions response
            "Toi khong tim thay biet thu co ho boi o Q1...
             Tuy nhien, co 12 bat dong san khac..."

[00:03.150] Response returned (total: 3150ms)
```

### Complete Flow 4: Multimodal Chat (Image Analysis)

**User Input:** "Danh gia can ho nay giup toi" + [image: apartment_interior.jpg]

**Execution Trace:**
```
[00:00.000] POST /v1/chat/completions (Open WebUI format)
[00:00.010] Multimodal request detected: 1 file (image/jpeg)
[00:00.015] Classification: CHAT (files present)
[00:00.020] Route to: _handle_chat() with files

[00:00.025] Build multimodal messages
            - System: Vision analysis prompt
            - User: "Danh gia can ho nay giup toi"
            - Files: [{name: "apartment_interior.jpg", url: "data:image/jpeg;base64,..."}]

[00:00.030] → Core Gateway
            POST /chat/completions
            Model: gpt-4o (vision)
            Max tokens: 1000

[00:00.035] LiteLLM → OpenAI Vision API
[00:03.240] ← Vision analysis complete (3205ms)

[00:03.245] Response:
            "Đây là một căn hộ cao cấp với những đặc điểm sau:
             **Loại hình:** Căn hộ chung cư
             **Diện tích:** Ước tính 80-90m²
             ..."

[00:03.250] Save to conversation memory (with metadata: {has_files: true})

[00:03.280] Response returned (total: 3280ms)
```

---

## Document Metadata

**Document:** `ORCHESTRATOR_FLOWS.md`
**Purpose:** Technical reference for orchestrator case handling
**Audience:** Backend developers, system architects
**Related Documents:**
- `CLAUDE.md` - Project overview
- `docs/API_DOCUMENTATION.md` - API specs
- `services/orchestrator/README.md` - Service-specific docs
- `TESTING.md` - Test coverage

**Changelog:**
- 2025-01-12: Initial version covering 4 main cases
- Future: Add PRICE_CONSULTATION implementation details when completed

---

**End of Document**

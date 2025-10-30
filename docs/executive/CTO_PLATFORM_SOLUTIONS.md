# 🎯 PLATFORM SOLUTIONS - TRẢ LỜI SƠ ĐỒ CTO

> **Document này BÁM SÁT 100% sơ đồ gốc CTO** (`REE AI-architecture.drawio.xml`)
> Tìm platform MIỄN PHÍ, PHỔ BIẾN, CỘNG ĐỒNG LỚN để triển khai

---

## 📋 TÓM TẮT NHANH

### ✅ 10 Services CTO → Platform FREE

| # | Service CTO | Platform Đề Xuất | Lý Do | GitHub Stars |
|---|-------------|-------------------|-------|--------------|
| 1 | **Orchestrator** (routing message) | FastAPI + gRPC | Async, Python native, gRPC built-in | 72K⭐ |
| 2 | **Hybrid Semantic Chunking** (6 bước) | Sentence-Transformers + NLTK | HuggingFace official, đúng 6 bước CTO | 13K⭐ |
| 3 | **Attribute Extraction** (LLM-driven) | GPT-4 mini + Pydantic | Structured output JSON, validation tự động | GPT API |
| 4 | **Classification Service** (3 modes) | FastAPI + GPT-4 mini | Classify: filter / semantic / both | 72K⭐ |
| 5 | **Completeness Feedback** | GPT-4 mini | Score 0-100, re-gen if <70 | GPT API |
| 6 | **Price Suggestion** | GPT-4 mini | Market analysis + reasoning | GPT API |
| 7 | **Rerank Service** | cross-encoder (HuggingFace) | Score normalization, Top-K | HuggingFace |
| 8 | **User Account Service** | FastAPI + PostgreSQL + JWT | Auth, users, roles | Millions |
| 9 | **Core Service** (Gateway Q3) | LiteLLM + Redis | Rate limit, cost tracking, cache | 10K⭐ |
| 10 | **Real Estate Crawler** | Crawl4AI + Playwright | 73% ít code, 47% nhanh hơn Scrapy | 4K⭐ |

### ✅ TRẢ LỜI 4 CÂU HỎI CTO

| Câu Hỏi | Trả Lời | Platform | Chi Tiết |
|---------|---------|----------|----------|
| **Q1:** Context Memory - OpenAI API có quản lý không? | **KHÔNG** ❌ Phải tự quản | PostgreSQL + conversation_id | Lưu users, conversations, messages table |
| **Q2:** Mapping để OpenAI hiểu request của user nào? | **Orchestrator gen UUID** | FastAPI + UUID library | Gen conversation_id → Gửi mọi service |
| **Q3:** Có cần Core Service tập trung OpenAI? | **CÓ** ✅ Bắt buộc | LiteLLM + Redis | Rate limit, cost tracking, caching |
| **Q4:** Conversation history khi user mở lại? | **Load từ PostgreSQL** | PostgreSQL + SQLAlchemy | SELECT messages WHERE conversation_id → Inject prompt |

### 💰 Chi Phí

```
PLATFORMS: $0 (ALL FREE)
────────────────────────
✅ FastAPI: $0
✅ Sentence-Transformers: $0
✅ Crawl4AI: $0
✅ LiteLLM: $0
✅ OpenSearch: $0
✅ PostgreSQL: $0
✅ Redis: $0
✅ Pydantic: $0
✅ cross-encoder: $0

ONLY COST: OpenAI API
────────────────────────
- GPT-4 mini: $0.15/$0.60 per 1M tokens
- Embeddings: $0.02 per 1M tokens

Development: ~$100-200/month
Production: ~$300-1000/month
```

### ⏱️ Timeline

```
Week 1-2: Core (14 days)
  - PostgreSQL + Users schema
  - Orchestrator + conversation_id
  - Core Gateway (LiteLLM)

Week 3-4: AI Services (14 days)
  - Semantic Chunking
  - Attribute Extraction
  - Classification (3 modes)
  - Completeness Feedback
  - Price Suggestion
  - Rerank

Week 5: Data & Deploy (7 days)
  - Crawler (Crawl4AI)
  - OpenSearch
  - Docker Compose
  - Testing

TOTAL: 5 weeks
```

---

## 🏗️ KIẾN TRÚC CHI TIẾT

### 1. User Account Service

**Sơ đồ CTO:** User Account Service
**Platform:** FastAPI + PostgreSQL + JWT + bcrypt

```python
# Stack:
FastAPI           # Web framework
PostgreSQL        # User database
SQLAlchemy        # ORM
PyJWT             # JWT tokens
bcrypt            # Password hashing

# Features:
- Register (email, password)
- Login → JWT token
- Token refresh
- User profile management
- Role-based access (admin, user)

# API Endpoints:
POST /auth/register
POST /auth/login
POST /auth/refresh
GET  /auth/me
```

**Lý do chọn:**
- ✅ FREE (MIT License)
- ✅ 72K stars GitHub
- ✅ Python native (team dễ maintain)
- ✅ Auto OpenAPI docs
- ✅ Async performance

---

### 2. Orchestrator (Routing Service)

**Sơ đồ CTO:** Orchestrator - routing message: create RE / search RE / price suggestion
**Platform:** FastAPI + gRPC (grpcio)

```python
# Stack:
FastAPI           # HTTP interface
grpcio            # Inter-service communication
UUID              # conversation_id generation ← Q2 ANSWER

# Routing Logic:
User Request → Orchestrator
  ↓
Gen conversation_id (UUID v4)  ← Q2 ANSWER
  ↓
Route to services:
  - "create RE" → Attribute Extraction + Semantic Chunking
  - "search RE" → Classification → Search + Rerank
  - "price" → Price Suggestion

# gRPC Services:
service Orchestrator {
  rpc RouteMessage(Request) returns (Response);
  rpc CreateRE(CreateRERequest) returns (CreateREResponse);
  rpc SearchRE(SearchRERequest) returns (SearchREResponse);
}
```

**Lý do chọn gRPC:**
- ✅ Faster than REST (binary protocol)
- ✅ Built-in load balancing
- ✅ Strongly typed (Protobuf)
- ✅ Bi-directional streaming

---

### 3. Hybrid Semantic Chunking Service

**Sơ đồ CTO:** Hybrid Semantic Chunking - 6 steps (Notion doc link)
**Platform:** Sentence-Transformers + NLTK + NumPy

```python
# Stack:
sentence-transformers   # Embeddings
NLTK                    # Sentence segmentation
NumPy                   # Cosine similarity
FastAPI                 # Service wrapper

# 6 Steps ĐÚNG YÊU CẦU CTO:

Step 1: Sentence Segmentation
  → NLTK sent_tokenize()
  → Input: "Nhà 3 phòng ngủ. Giá 2 tỷ. View đẹp."
  → Output: ["Nhà 3 phòng ngủ.", "Giá 2 tỷ.", "View đẹp."]

Step 2: Generate Embedding cho từng câu
  → sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
  → Vietnamese support
  → Output: [embed1, embed2, embed3]

Step 3: Cosine Similarity Calculation
  → NumPy cosine_similarity()
  → Matrix 3x3 similarities

Step 4: Combine Sentences với threshold >0.75
  → If similarity(sent1, sent2) > 0.75 → Merge
  → "Nhà 3 phòng ngủ. Giá 2 tỷ." (if similar)

Step 5: Overlap
  → Window overlap 1-2 sentences
  → Ensure context continuity

Step 6: Create Embedding for Whole Chunk
  → sentence-transformers encode(merged_text)
  → Final chunk embedding for vector DB

# API:
POST /semantic-chunking
{
  "text": "long real estate description...",
  "threshold": 0.75,
  "overlap_sentences": 1
}
→ Returns: [{"chunk": "...", "embedding": [...]}]
```

**Lý do chọn:**
- ✅ FREE (Apache 2.0)
- ✅ 13K stars, HuggingFace official
- ✅ Đúng 6 bước CTO
- ✅ Vietnamese support
- ✅ Research paper cited 1000+ times

**Ref CTO:** https://www.notion.so/.../Chunk-size-optimation-...

---

### 4. Attribute Extraction Service (LLM-driven)

**Sơ đồ CTO:** Attribute Extraction Service - LLM-driven
**Platform:** GPT-4 mini + Pydantic (structured output)

```python
# Stack:
OpenAI GPT-4 mini   # LLM extraction
Pydantic            # Schema validation
FastAPI             # Service wrapper

# JSON Schema (Pydantic):
class RealEstateAttributes(BaseModel):
    price: Optional[float] = None
    price_unit: str = "VND"
    location: str
    district: Optional[str] = None
    city: str
    property_type: str  # "apartment", "house", "land"
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    area_unit: str = "m2"
    floor: Optional[int] = None
    direction: Optional[str] = None  # "Đông", "Tây"...
    legal_status: Optional[str] = None  # "Sổ đỏ", "Sổ hồng"
    furniture: Optional[str] = None
    description: str

# GPT-4 Prompt:
system_prompt = """
Bạn là chuyên gia bất động sản. Trích xuất thông tin từ text thành JSON.
Schema: {RealEstateAttributes.schema_json()}
"""

user_prompt = """
Text: {input_text}
Extract to JSON following schema.
"""

# API:
POST /attribute-extraction
{
  "text": "Bán nhà 3 phòng ngủ, 2WC, DT 80m2, giá 2 tỷ, Quận 1 HCM"
}
→ Returns:
{
  "price": 2000000000,
  "location": "Quận 1, HCM",
  "bedrooms": 3,
  "bathrooms": 2,
  "area": 80.0,
  ...
}
```

**Lý do chọn:**
- ✅ GPT-4 mini rẻ ($0.15 input / $0.60 output per 1M tokens)
- ✅ Pydantic FREE + auto validation
- ✅ Structured output = reliable
- ✅ Vietnamese support

---

### 5. Classification Service (3 Modes CTO)

**Sơ đồ CTO:** Classification Service → 3 modes: filter / semantic / both
**Platform:** FastAPI + GPT-4 mini

```python
# Stack:
GPT-4 mini          # Query classification
FastAPI             # Service wrapper

# 3 Modes THEO CTO:

Mode 1: FILTER (Structured Filtering)
  → Query có structured attributes rõ ràng
  → Example: "Nhà 3 phòng ngủ, giá dưới 2 tỷ, Quận 1"
  → Route: SQL WHERE bedrooms=3 AND price<2000000000 AND district='Quận 1'

Mode 2: SEMANTIC (Vector Search)
  → Query mơ hồ, semantic
  → Example: "Tìm nhà view đẹp, yên tĩnh, gần công viên"
  → Route: OpenSearch vector search với embedding

Mode 3: BOTH (Hybrid Retrieval)
  → Query kết hợp structured + semantic
  → Example: "Nhà 3 phòng ngủ, view sông, yên tĩnh"
  → Route: Hybrid (filter bedrooms=3 + semantic "view sông yên tĩnh")

# GPT-4 Prompt:
system_prompt = """
Classify query into 3 modes:
1. filter: Has clear structured attributes (price, bedrooms, location)
2. semantic: Vague, descriptive (beautiful, quiet, modern)
3. both: Mix of structured + semantic

Return JSON: {"mode": "filter|semantic|both", "reasoning": "..."}
"""

# API:
POST /classification
{
  "query": "Nhà 3 phòng ngủ view đẹp Quận 1"
}
→ Returns:
{
  "mode": "both",
  "structured": {"bedrooms": 3, "district": "Quận 1"},
  "semantic": "view đẹp"
}
```

**Lý do chọn:**
- ✅ GPT-4 mini classification chính xác
- ✅ 3 modes đúng yêu cầu CTO
- ✅ Flexible routing

---

### 6. Completeness Feedback Service

**Sơ đồ CTO:** Completeness Feedback Service
**Platform:** GPT-4 mini (completeness evaluation)

```python
# Stack:
GPT-4 mini          # Evaluate response completeness
FastAPI             # Service wrapper

# Logic:
1. User query → System generates response
2. Send (query + response) to Completeness Service
3. GPT-4 scores 0-100
4. If score < 70 → Trigger re-generation with feedback

# GPT-4 Prompt:
system_prompt = """
Bạn là chuyên gia QA. Đánh giá độ đầy đủ của câu trả lời.

Criteria:
- Trả lời đúng câu hỏi? (40 points)
- Đầy đủ thông tin? (30 points)
- Chính xác? (20 points)
- Clear & concise? (10 points)

Return JSON:
{
  "score": 0-100,
  "missing": ["what's missing"],
  "suggestion": "how to improve"
}
"""

# API:
POST /completeness-feedback
{
  "query": "Tìm nhà 3 phòng ngủ Quận 1",
  "response": "Có 5 căn nhà phù hợp: ..."
}
→ Returns:
{
  "score": 85,
  "is_complete": true,  // score >= 70
  "missing": [],
  "suggestion": "Good!"
}

# Orchestrator Logic:
if score < 70:
    re_generate_with_feedback(missing, suggestion)
```

**Lý do chọn:**
- ✅ GPT-4 mini tốt nhất cho reasoning
- ✅ Quality control tự động
- ✅ Feedback loop cải thiện response

---

### 7. Price Suggestion Service

**Sơ đồ CTO:** Price Suggestion Service
**Platform:** GPT-4 mini + Market Data

```python
# Stack:
GPT-4 mini          # Price reasoning
OpenSearch          # Similar properties
FastAPI             # Service wrapper

# Logic:
1. Get property attributes (from Attribute Extraction)
2. Search similar properties in OpenSearch
3. Send (attributes + similar_properties) to GPT-4
4. GPT-4 analyzes market → Suggest price range

# GPT-4 Prompt:
system_prompt = """
Bạn là chuyên gia định giá BĐS. Dựa vào:
1. Property attributes
2. Similar properties đã bán
3. Market trends

Suggest giá hợp lý với reasoning.

Return JSON:
{
  "suggested_price_min": float,
  "suggested_price_max": float,
  "reasoning": "...",
  "market_trend": "up|stable|down",
  "confidence": 0-1
}
"""

# API:
POST /price-suggestion
{
  "attributes": {
    "bedrooms": 3,
    "area": 80,
    "location": "Quận 1"
  }
}
→ Returns:
{
  "suggested_price_min": 1800000000,
  "suggested_price_max": 2200000000,
  "reasoning": "Based on 15 similar properties...",
  "confidence": 0.85
}
```

**Lý do chọn:**
- ✅ GPT-4 mini có market reasoning tốt
- ✅ Kết hợp similar properties = chính xác

---

### 8. Rerank Service

**Sơ đồ CTO:** Rerank Service
**Platform:** cross-encoder (HuggingFace)

```python
# Stack:
sentence-transformers   # cross-encoder model
FastAPI                 # Service wrapper

# Model:
cross-encoder/ms-marco-MiniLM-L-6-v2
  → Trained for semantic similarity ranking
  → Vietnamese support via multilingual

# Logic:
1. OpenSearch returns top 50 results
2. cross-encoder re-scores (query, doc) pairs
3. Sort by score → Return top 10

# Code:
from sentence_transformers import CrossEncoder

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

pairs = [(query, doc) for doc in search_results]
scores = model.predict(pairs)

# Sort and return top-K
ranked = sorted(zip(search_results, scores),
                key=lambda x: x[1], reverse=True)[:10]

# API:
POST /rerank
{
  "query": "Nhà view đẹp Quận 1",
  "candidates": [
    {"id": 1, "text": "..."},
    {"id": 2, "text": "..."}
  ],
  "top_k": 10
}
→ Returns: [{"id": 5, "score": 0.92}, ...]
```

**Lý do chọn:**
- ✅ FREE (HuggingFace)
- ✅ Proven research (MS MARCO dataset)
- ✅ Better than vector similarity alone

---

### 9. Core Service (OpenAI Gateway) - Q3 ANSWER

**Sơ đồ CTO:** Q3 - Có cần Core Service tập trung request lên OpenAI?
**Câu trả lời:** **CÓ** ✅ Bắt buộc
**Platform:** LiteLLM + Redis + FastAPI

```python
# Stack:
LiteLLM             # Universal LLM gateway
Redis               # Cache + rate limiting
FastAPI             # Wrapper service

# Features:

1. RATE LIMITING (protect API key)
   → Redis-based token bucket
   → 1000 requests/user/hour

2. COST TRACKING (per user/conversation)
   → Log: user_id, conversation_id, tokens, cost
   → PostgreSQL analytics table

3. RESPONSE CACHING (Redis)
   → Cache key: hash(model + prompt)
   → TTL: 1 hour
   → Save ~30% API cost

4. CENTRALIZED MONITORING
   → All OpenAI requests go through gateway
   → Track: latency, errors, usage

# Code:
from litellm import completion

async def call_gpt(prompt, user_id, conversation_id):
    # 1. Check rate limit
    if not check_rate_limit(user_id):
        raise RateLimitError()

    # 2. Check cache
    cache_key = hash(prompt)
    cached = redis.get(cache_key)
    if cached:
        return cached

    # 3. Call OpenAI via LiteLLM
    response = await completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    # 4. Track cost
    cost = calculate_cost(response.usage)
    log_usage(user_id, conversation_id, cost)

    # 5. Cache response
    redis.setex(cache_key, 3600, response)

    return response

# API:
POST /gateway/chat
{
  "user_id": "uuid",
  "conversation_id": "uuid",  ← Q2 mapping
  "messages": [...]
}
→ Returns: GPT response + cost info
```

**Lý do chọn LiteLLM:**
- ✅ FREE (MIT License) 10K⭐
- ✅ Unified API (OpenAI, Anthropic, Cohere...)
- ✅ Built-in: rate limit, retry, fallback
- ✅ Cost tracking built-in
- ✅ Easy migration to other LLMs

**Trả lời Q3 CTO:** ✅ CÓ cần Core Service - BẮTT BUỘC để:
- Protect API key (rate limiting)
- Track cost per user
- Cache expensive calls
- Centralized monitoring
- **Model routing (Ollama vs OpenAI)** ← MỚI

---

### 9.1. Model Routing Strategy - Ollama vs OpenAI

**Platform:** LiteLLM hỗ trợ cả Ollama và OpenAI
**Mục đích:** Tiết kiệm chi phí bằng cách dùng Ollama (FREE) cho tasks đơn giản

#### 📊 Phân Luồng Model:

| Task | Complexity | Model | Cost | Lý Do |
|------|-----------|-------|------|-------|
| **Attribute Extraction** | Medium | **Ollama (llama3.1:8b)** | $0 | Structured extraction, schema rõ ràng |
| **Classification (3 modes)** | Low | **Ollama (llama3.1:8b)** | $0 | Simple classification task |
| **Completeness Feedback** | High | **OpenAI (GPT-4 mini)** | $$ | Cần reasoning tốt |
| **Price Suggestion** | High | **OpenAI (GPT-4 mini)** | $$ | Market analysis phức tạp |
| **Semantic Chunking** | N/A | **Sentence-Transformers** | $0 | Không dùng LLM |
| **Rerank** | N/A | **cross-encoder** | $0 | Không dùng LLM |

#### 🎯 Chiến Lược:

```python
# Core Gateway - Model Router

TASK_MODEL_MAP = {
    "attribute_extraction": {
        "provider": "ollama",
        "model": "llama3.1:8b",
        "cost_per_1m_tokens": 0.0,
        "fallback": "gpt-4o-mini"  # Nếu Ollama fail
    },
    "classification": {
        "provider": "ollama",
        "model": "llama3.1:8b",
        "cost_per_1m_tokens": 0.0,
        "fallback": "gpt-4o-mini"
    },
    "completeness_feedback": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "cost_per_1m_tokens": 0.15,  # input
        "fallback": "ollama/llama3.1:8b"
    },
    "price_suggestion": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "cost_per_1m_tokens": 0.15,
        "fallback": "ollama/llama3.1:70b"  # Larger Ollama model
    },
    "chat": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "cost_per_1m_tokens": 0.15,
        "fallback": "ollama/llama3.1:8b"
    }
}

async def call_llm(task: str, prompt: str, user_id: str):
    config = TASK_MODEL_MAP.get(task)

    # Try primary model
    try:
        if config["provider"] == "ollama":
            response = await completion(
                model=f"ollama/{config['model']}",
                messages=[{"role": "user", "content": prompt}],
                api_base="http://ollama:11434"
            )
        else:  # openai
            response = await completion(
                model=config["model"],
                messages=[{"role": "user", "content": prompt}]
            )

        return response

    except Exception as e:
        # Fallback to secondary model
        logger.warning(f"Primary model failed: {e}, using fallback")
        response = await completion(
            model=config["fallback"],
            messages=[{"role": "user", "content": prompt}]
        )
        return response
```

#### 🐋 Docker Compose - Thêm Ollama:

```yaml
services:
  # ... existing services ...

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]  # Optional: GPU support
    command: |
      sh -c "ollama serve &
             sleep 5 &&
             ollama pull llama3.1:8b &&
             ollama pull llama3.1:70b &&
             wait"

  core_gateway:
    build: ./services/core_gateway
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OLLAMA_BASE_URL=http://ollama:11434
      - MODEL_ROUTING_ENABLED=true
    depends_on:
      - ollama
      - redis

volumes:
  ollama_models:
```

#### 💰 Cost Comparison:

```
SCENARIO: 1M tokens/month

Option 1: ALL OpenAI GPT-4 mini
────────────────────────────────
Attribute Extraction: 200K tokens × $0.15 = $30
Classification:       100K tokens × $0.15 = $15
Completeness:         300K tokens × $0.60 = $180 (output heavy)
Price Suggestion:     400K tokens × $0.60 = $240
────────────────────────────────
TOTAL: $465/month

Option 2: Hybrid (Ollama + OpenAI)
────────────────────────────────
Attribute Extraction: 200K tokens × $0    = $0   ← Ollama
Classification:       100K tokens × $0    = $0   ← Ollama
Completeness:         300K tokens × $0.60 = $180 ← OpenAI
Price Suggestion:     400K tokens × $0.60 = $240 ← OpenAI
────────────────────────────────
TOTAL: $420/month

SAVINGS: $45/month (10% reduction)

+ Ollama server cost: $20/month (DigitalOcean 8GB RAM)
────────────────────────────────
NET SAVINGS: $25/month

At scale (10M tokens/month):
- Option 1: $4,650/month
- Option 2: $4,220/month
SAVINGS: $430/month
```

#### 🎯 Quality vs Cost Trade-off:

```python
# A/B Testing Strategy

# Week 1-2: Baseline (ALL OpenAI)
config = {"default_provider": "openai"}

# Week 3-4: Hybrid Test
config = {
    "attribute_extraction": "ollama",  # Test Ollama
    "classification": "ollama",
    "others": "openai"
}

# Metrics to track:
metrics = {
    "extraction_accuracy": 0.95,  # Target: >90%
    "classification_accuracy": 0.92,  # Target: >85%
    "user_satisfaction": 4.2,  # Target: >4.0/5
    "cost_savings": 0.10  # 10% reduction
}

# Decision criteria:
if extraction_accuracy < 0.90:
    # Rollback to OpenAI
    switch_to_openai("attribute_extraction")
else:
    # Keep Ollama (save money)
    pass
```

#### 📋 Model Selection Guide:

**Dùng Ollama khi:**
- ✅ Structured output (JSON schema)
- ✅ Simple classification (2-5 classes)
- ✅ Template-based generation
- ✅ Low latency required (self-hosted = faster)
- ✅ Privacy concerns (data không ra khỏi server)

**Dùng OpenAI khi:**
- ✅ Complex reasoning (price suggestion, market analysis)
- ✅ Creative generation
- ✅ Multi-step logic
- ✅ High accuracy critical (completeness feedback)
- ✅ Vietnamese nuances important

#### 🚀 LiteLLM Router Config:

```python
# LiteLLM supports automatic routing

from litellm import Router

router = Router(
    model_list=[
        {
            "model_name": "cheap-model",
            "litellm_params": {
                "model": "ollama/llama3.1:8b",
                "api_base": "http://ollama:11434"
            }
        },
        {
            "model_name": "smart-model",
            "litellm_params": {
                "model": "gpt-4o-mini"
            }
        }
    ],
    routing_strategy="cost-based",  # Route to cheapest first
    fallbacks=[
        {"cheap-model": ["smart-model"]}  # Fallback if Ollama fails
    ]
)

# Usage:
response = await router.acompletion(
    model="cheap-model",  # Try Ollama first
    messages=[...]
)
```

#### 🔧 Implementation Steps:

```bash
Week 1: Infrastructure
  1. Deploy Ollama container
  2. Pull llama3.1:8b, llama3.1:70b models
  3. Test Ollama API connectivity

Week 2: Integration
  4. Update Core Gateway with routing logic
  5. Implement fallback mechanism
  6. Add cost tracking per model

Week 3-4: Testing
  7. A/B test: Attribute Extraction (Ollama vs OpenAI)
  8. Measure: accuracy, latency, cost
  9. Tune prompts for Ollama if needed

Week 5: Rollout
  10. Enable Ollama for attribute_extraction
  11. Enable Ollama for classification
  12. Monitor quality metrics
  13. Adjust routing if quality drops
```

#### 📊 Monitoring Dashboard:

```python
# Track per-model metrics

SELECT
    task,
    provider,
    model,
    COUNT(*) as requests,
    AVG(tokens) as avg_tokens,
    SUM(cost) as total_cost,
    AVG(latency_ms) as avg_latency,
    SUM(CASE WHEN error THEN 1 ELSE 0 END) as errors
FROM llm_usage_logs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY task, provider, model
ORDER BY total_cost DESC;

Example output:
┌─────────────────────┬──────────┬──────────────┬──────────┬────────┬───────┐
│ task                │ provider │ model        │ requests │ cost   │ errors│
├─────────────────────┼──────────┼──────────────┼──────────┼────────┼───────┤
│ price_suggestion    │ openai   │ gpt-4o-mini  │ 50,000   │ $150   │ 12    │
│ completeness        │ openai   │ gpt-4o-mini  │ 80,000   │ $120   │ 8     │
│ attribute_extract   │ ollama   │ llama3.1:8b  │ 100,000  │ $0     │ 45    │
│ classification      │ ollama   │ llama3.1:8b  │ 60,000   │ $0     │ 20    │
└─────────────────────┴──────────┴──────────────┴──────────┴────────┴───────┘

Alert if:
- Ollama error rate > 5% → Switch to OpenAI
- OpenAI cost > $500/week → Expand Ollama usage
```

---

### 10. Real Estate Crawler

**Sơ đồ CTO:** Real Estate Crawler
**Platform:** Crawl4AI + Playwright

```python
# Stack:
Crawl4AI            # AI-optimized crawler
Playwright          # JS rendering
Celery Beat         # Scheduling (every 6h)
FastAPI             # API wrapper

# Crawl Flow:
1. Crawl nhatot.vn, batdongsan.vn
2. JS render (Playwright)
3. Auto clean HTML (remove ads, scripts)
4. Extract LLM-friendly markdown
5. Send to Semantic Chunking → Attribute Extraction
6. Index to OpenSearch

# Code:
from crawl4ai import WebCrawler

crawler = WebCrawler(
    headless=True,
    browser_type="chromium",
    markdown_generator=LLMFriendlyMarkdown()
)

# Crawl property listing
result = await crawler.arun(
    url="https://nhatot.vn/mua-ban-bat-dong-san",
    css_selector=".property-item",
    extraction_strategy="JsonCssExtractionStrategy",
    schema={
        "name": "title.text",
        "price": ".price.text",
        "location": ".location.text",
        "description": ".description.text"
    }
)

# Celery Task:
@celery_app.task
def crawl_properties():
    sites = ["nhatot.vn", "batdongsan.vn", "alonhadat.com.vn"]
    for site in sites:
        properties = await crawl_site(site)
        for prop in properties:
            # Send to processing pipeline
            process_property.delay(prop)

# Schedule (every 6 hours):
celery_beat_schedule = {
    'crawl-properties': {
        'task': 'crawl_properties',
        'schedule': crontab(minute=0, hour='*/6'),
    }
}
```

**Lý do chọn Crawl4AI (thay vì Scrapy):**
- ✅ 73% ít code hơn Scrapy
- ✅ 47% nhanh hơn
- ✅ LLM-friendly markdown built-in
- ✅ Auto clean HTML (no manual parsing)
- ✅ Playwright JS rendering built-in
- ✅ 4K stars (hot, growing community)

---

### 11. Storage Layer

#### A. PostgreSQL (Context Memory - Q1, Q4)

**Sơ đồ CTO:** Q1 - Context Memory: OpenAI có quản lý không?
**Câu trả lời:** **KHÔNG** ❌ Phải tự quản PostgreSQL
**Platform:** PostgreSQL + SQLAlchemy

```sql
-- Q1 ANSWER: PostgreSQL Schema

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Conversations table ← Q1, Q4
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),  ← Q2 mapping
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages table ← Q4 (history loading)
CREATE TABLE messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(50),  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Q4: Load history when user opens conversation
SELECT role, content
FROM messages
WHERE conversation_id = $1
ORDER BY created_at ASC;

-- Inject into GPT prompt:
messages = [
    {"role": "system", "content": "You are RE assistant"},
    *[{"role": msg.role, "content": msg.content} for msg in history],
    {"role": "user", "content": new_query}
]
```

**Trả lời Q1 CTO:** ❌ OpenAI API KHÔNG có context memory built-in
**Trả lời Q4 CTO:** ✅ Load từ PostgreSQL messages table → Inject vào prompt

#### B. OpenSearch (Vector DB + BM25)

```python
# Index Schema:
{
    "properties": {
        "id": {"type": "keyword"},
        "title": {"type": "text", "analyzer": "vietnamese"},
        "description": {"type": "text", "analyzer": "vietnamese"},
        "price": {"type": "float"},
        "location": {"type": "text"},
        "bedrooms": {"type": "integer"},
        "area": {"type": "float"},
        "embedding": {
            "type": "dense_vector",
            "dims": 384  # sentence-transformers output
        }
    }
}

# Hybrid Search (vector + BM25):
{
    "query": {
        "bool": {
            "must": [
                # BM25 keyword search
                {"match": {"description": "view đẹp"}},

                # Structured filter
                {"range": {"price": {"lte": 2000000000}}},
                {"term": {"bedrooms": 3}}
            ],
            "should": [
                # Vector similarity search
                {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": embedding}
                        }
                    }
                }
            ]
        }
    }
}
```

#### C. Redis (Cache + Queue)

```python
# Use cases:
1. Response caching (Core Gateway)
2. Rate limiting (token bucket)
3. Session management
4. Celery task queue (crawling)

# Example:
redis.setex(f"rate_limit:{user_id}", 3600, 1000)  # 1000 req/hour
redis.get(f"cache:{hash(prompt)}")
```

---

## 📦 DOCKER COMPOSE

```yaml
version: '3.8'

services:
  # --- Databases ---
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ree_ai
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres_data:/var/lib/postgresql/data

  opensearch:
    image: opensearchproject/opensearch:2.11.0
    environment:
      - discovery.type=single-node
      - OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m
    volumes:
      - opensearch_data:/usr/share/opensearch/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  # --- Services (FastAPI) ---
  orchestrator:
    build: ./services/orchestrator
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://admin:secret@postgres/ree_ai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  semantic_chunking:
    build: ./services/semantic_chunking
    ports:
      - "8001:8000"

  attribute_extraction:
    build: ./services/attribute_extraction
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  classification:
    build: ./services/classification
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  completeness_feedback:
    build: ./services/completeness_feedback
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  price_suggestion:
    build: ./services/price_suggestion
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}

  rerank:
    build: ./services/rerank

  user_account:
    build: ./services/user_account
    environment:
      - DATABASE_URL=postgresql://admin:secret@postgres/ree_ai
      - JWT_SECRET=${JWT_SECRET}

  core_gateway:
    build: ./services/core_gateway
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  crawler:
    build: ./services/crawler
    environment:
      - DATABASE_URL=postgresql://admin:secret@postgres/ree_ai
      - OPENSEARCH_URL=http://opensearch:9200

  # --- Worker ---
  celery_worker:
    build: ./services/crawler
    command: celery -A tasks worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379

  celery_beat:
    build: ./services/crawler
    command: celery -A tasks beat --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379

volumes:
  postgres_data:
  opensearch_data:
  redis_data:
```

---

## 📊 SO SÁNH: SƠ ĐỒ CTO vs PLATFORM ĐỀ XUẤT

| Service CTO | Có trong platform? | Platform | Thay đổi gì? |
|-------------|-------------------|----------|--------------|
| ✅ Orchestrator | ✅ | FastAPI + gRPC | Đúng 100% |
| ✅ Hybrid Semantic Chunking | ✅ | Sentence-Transformers | Đúng 6 bước |
| ✅ Attribute Extraction | ✅ | GPT-4 mini + Pydantic | Đúng LLM-driven |
| ✅ Classification (3 modes) | ✅ | FastAPI + GPT-4 | Đúng filter/semantic/both |
| ✅ Completeness Feedback | ✅ | GPT-4 mini | Đúng |
| ✅ Price Suggestion | ✅ | GPT-4 mini | Thay "3rd pricing service" = GPT (tốt hơn) |
| ✅ Rerank | ✅ | cross-encoder | Đúng |
| ✅ User Account | ✅ | FastAPI + PostgreSQL | Đúng |
| ✅ Core/Gateway (Q3) | ✅ | LiteLLM + Redis | Đúng, TRẢ LỜI Q3 |
| ✅ Crawler | ✅ | Crawl4AI | Thay Scrapy (tốt hơn) |
| ✅ Context Memory (Q1, Q4) | ✅ | PostgreSQL | Đúng, TRẢ LỜI Q1, Q4 |
| ✅ conversation_id mapping (Q2) | ✅ | UUID trong Orchestrator | Đúng, TRẢ LỜI Q2 |

### ⚠️ Khác Biệt:

1. **Price Suggestion:**
   - CTO: "3rd pricing service" (external cloud service)
   - Platform: GPT-4 mini + market data
   - **Lý do:** GPT-4 tốt hơn, flexible, không phụ thuộc external

2. **Crawler:**
   - CTO: Không chỉ định (có thể Scrapy)
   - Platform: Crawl4AI
   - **Lý do:** 73% ít code, 47% nhanh hơn Scrapy

3. **Không có Open WebUI, LangChain:**
   - CTO không đề cập → Không dùng
   - Platform: Microservices thuần (FastAPI)

---

## ✅ KẾT LUẬN

### ĐÃ GIẢI QUYẾT:

✅ **10 Services CTO** → Tất cả có platform FREE, phổ biến
✅ **4 Câu hỏi CTO** → Đã trả lời đầy đủ (Q1, Q2, Q3, Q4)
✅ **Chi phí** → $0 tools, chỉ $100-300/month OpenAI API
✅ **Timeline** → 5 tuần (realistic)
✅ **Cộng đồng** → Tất cả platform có 4K-72K stars GitHub

### KHUYẾN NGHỊ:

1. **Review sơ đồ CTO lần cuối** để confirm
2. **Bắt đầu Week 1-2:** PostgreSQL + Orchestrator + Core Gateway
3. **Song song:** Setup Sentence-Transformers test với Vietnamese text
4. **Monitoring:** Prometheus + Grafana (optional nhưng nên có)

---

**Document này là đề xuất platform - cần CTO approve trước khi implement.**

Generated: 2025-10-29
Version: 1.0
Status: ✅ Ready for CTO review

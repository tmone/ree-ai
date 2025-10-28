# Quick Reference: PLATFORMS THEO SƠ ĐỒ CTO

## 🎯 One-Page Cheat Sheet - FREE PLATFORMS

```
┌──────────────────────────────────────────────────────────────────┐
│           PLATFORMS ĐỂ IMPLEMENT SƠ ĐỒ CTO                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🚀 FASTAPI          📦 SENTENCE-TRANS    🔍 LITELLM            │
│  Services Framework   Semantic Chunking    OpenAI Gateway       │
│  ───────────────      ──────────────────   ─────────────        │
│  • Orchestrator       • 6-step chunking    • Rate limit         │
│  • 10 services CTO    • Cosine sim >0.75   • Cost tracking     │
│  • gRPC support       • Overlap chunks     • Caching            │
│  • Auto docs          • HuggingFace       • Multi-model        │
│                                                                  │
│  ✅ FREE              ✅ FREE               ✅ FREE              │
│  72K⭐ GitHub         13K⭐ GitHub          10K⭐ GitHub          │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  🕷️  CRAWL4AI          🔎 OPENSEARCH       🐘 POSTGRESQL       │
│  Real Estate Crawler  Vector DB            Context Memory       │
│  ────────────────     ─────────────        ──────────────       │
│  • nhatot.vn          • Vector search      • Conversations     │
│  • batdongsan.vn      • BM25 keyword       • Users/Auth        │
│  • Playwright JS      • Hybrid retrieval   • SQLAlchemy ORM    │
│  • LLM-friendly       • Docker             • UUID session      │
│                                                                  │
│  ✅ FREE              ✅ FREE               ✅ FREE              │
│  4K⭐ (hot!)          8.5K⭐ GitHub         Millions users      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 Decision Matrix - THEO YÊU CẦU CTO

### CTO cần gì? → Dùng Platform nào?

#### Orchestrator (Routing message: create RE / search RE / price)
```
→ FastAPI ✅
  + gRPC (inter-service communication)

Lý do:
- Async performance
- Auto OpenAPI docs
- gRPC support built-in
- Python native (dễ team)

Platform: FastAPI (FREE)
Code: orchestrator_service.py
```

#### Hybrid Semantic Chunking (6 bước CTO)
```
→ Sentence-Transformers ✅
  + NumPy (cosine similarity)
  + NLTK (sentence segmentation)

Lý do:
- Đúng 6 bước CTO:
  1. Segment sentences (NLTK)
  2. Embed each (sentence-transformers)
  3. Cosine similarity (NumPy)
  4. Combine >0.75 threshold
  5. Overlap window
  6. Final chunk embedding
- HuggingFace official, 13K stars

Platform: Sentence-Transformers (FREE)
Code: semantic_chunking_service.py
```

#### Completeness Feedback Service
```
→ GPT-4 mini ✅
  + Custom prompt (đánh giá 0-100)

Lý do:
- LLM tốt nhất cho reasoning
- Rẻ ($0.15 input / $0.60 output per 1M)
- Nếu score <70 → re-generate

Platform: OpenAI GPT-4 mini
Code: completeness_service.py
```

#### Attribute Extraction (LLM-driven)
```
→ GPT-4 mini + Pydantic ✅

Lý do:
- Structured output (JSON schema)
- Extract: price, location, bedrooms, area
- Validation tự động (Pydantic)

Platform: GPT-4 mini + Pydantic (FREE lib)
Code: attribute_extraction_service.py
```

#### Classification Service (3 modes)
```
→ FastAPI + GPT-4 mini ✅

3 modes:
1. filter → structured filtering (SQL WHERE)
2. semantic → vector search (OpenSearch)
3. both → hybrid retrieval

Platform: FastAPI service
Code: classification_service.py
```

#### Context Memory (Q1, Q4 CTO)
```
→ PostgreSQL + SQLAlchemy ✅
  + UUID conversation_id

Q1: OpenAI không quản context → Tự lưu PostgreSQL
Q4: Load history từ DB → Inject vào prompt

Platform: PostgreSQL (FREE)
Schema:
- users (id, email, password_hash)
- conversations (id, user_id, created_at)
- messages (id, conversation_id, role, content)
```

#### Core Service/Gateway (Q3 CTO) + Model Routing
```
→ LiteLLM ✅
  + Redis (cache)
  + Ollama (self-hosted LLM)
  + FastAPI wrapper

Q3: CÓ cần gateway → CÓ!

Features:
- Rate limiting (protect API key)
- Cost tracking (theo user/conversation)
- Response caching (Redis)
- Centralized monitoring
- Model routing (Ollama vs OpenAI) ← NEW

Model Routing Strategy:
┌────────────────────────┬─────────┬─────────┐
│ Task                   │ Model   │ Cost    │
├────────────────────────┼─────────┼─────────┤
│ Attribute Extraction   │ Ollama  │ $0      │
│ Classification         │ Ollama  │ $0      │
│ Completeness Feedback  │ OpenAI  │ $$      │
│ Price Suggestion       │ OpenAI  │ $$      │
└────────────────────────┴─────────┴─────────┘

Savings: ~10% cost reduction ($25-430/month)

Platform: LiteLLM (FREE) + Ollama (FREE) + Redis
Code: core_gateway_service.py
```

#### Real Estate Crawler
```
→ Crawl4AI ✅
  + Playwright (JS rendering)

Lý do:
- 73% ít code hơn Scrapy
- 47% nhanh hơn
- LLM-friendly markdown
- Auto clean HTML

Platform: Crawl4AI (FREE)
Code: real_estate_crawler.py
```

---

## 🚦 Traffic Light Guide - THEO SƠ ĐỒ CTO

### ✅ GREEN - BẮT BUỘC (Theo sơ đồ CTO)

| Service | Platform | Cost | Stars |
|---------|----------|------|-------|
| **Orchestrator** | FastAPI + gRPC | FREE | 72K⭐ |
| **Semantic Chunking** | Sentence-Transformers | FREE | 13K⭐ |
| **Attribute Extraction** | GPT-4 mini + Pydantic | API only | GPT API |
| **Classification (3 modes)** | FastAPI + GPT-4 mini | FREE+API | 72K⭐ |
| **Completeness Feedback** | GPT-4 mini | API only | GPT API |
| **Price Suggestion** | GPT-4 mini | API only | GPT API |
| **Rerank Service** | cross-encoder (HF) | FREE | HuggingFace |
| **User Account** | FastAPI + PostgreSQL | FREE | Millions |
| **Core Gateway (Q3)** | LiteLLM + Redis + Ollama | FREE | 10K⭐ + Self-hosted |
| **RE Crawler** | Crawl4AI + Playwright | FREE | 4K⭐ |
| **Vector DB** | OpenSearch | FREE | 8.5K⭐ |
| **Context Memory (Q1,Q4)** | PostgreSQL + SQLAlchemy | FREE | Millions |

### 🟡 YELLOW - Optional Monitoring

| Tool | When | Cost |
|------|------|------|
| **Prometheus + Grafana** | Production metrics | FREE |
| **Sentry** | Error tracking | FREE tier |

### 🔴 RED - KHÔNG CẦN (Theo CTO)

| What | Why NOT | Alternative |
|------|---------|-------------|
| **LangChain** | CTO không dùng | FastAPI services |
| **LlamaIndex** | CTO không dùng | OpenSearch |
| **LangGraph** | CTO không dùng | Orchestrator |
| **Open WebUI** | CTO không dùng | Custom UI hoặc không có UI |

---

## 💡 Implementation Timeline - THEO SƠ ĐỒ CTO

### Week 1-2: Core Infrastructure
```bash
1. Setup PostgreSQL + Users schema (Q1 answer)
2. Build Orchestrator (FastAPI + gRPC)
3. Setup conversation_id mapping (Q2 answer)
4. Build Core Gateway Service (Q3 answer - LiteLLM)

Cost: $0 (all FREE tools)
Time: 10-14 days
```

### Week 3-4: AI Services
```bash
5. Hybrid Semantic Chunking (Sentence-Transformers)
6. Attribute Extraction (GPT-4 mini + Pydantic)
7. Classification Service (3 modes)
8. Completeness Feedback (GPT-4 mini)
9. Price Suggestion Service (GPT-4 mini)
10. Rerank Service (cross-encoder)

Cost: $100-200 (OpenAI API testing)
Time: 14 days
```

### Week 5: Data & Deployment
```bash
11. Real Estate Crawler (Crawl4AI)
12. OpenSearch setup (Vector + BM25)
13. Conversation history implementation (Q4 answer)
14. Docker Compose deployment
15. Integration testing

Cost: $0 (self-hosted)
Time: 7 days
```

### TOTAL: 5 weeks, $100-200 dev cost
export LANGCHAIN_API_KEY="your-key"  # Free tier

# Cost: $0
```

### Phase 2: 3-6 Months ⏸️
```bash
# IF retrieval is slow:
1. 🤔 Test LlamaIndex for retrieval
2. ✅ Keep LangChain for orchestration
3. 🔍 Monitor with LangSmith

# Cost: Still $0
```

### Phase 3: 6-12 Months 🚀
```bash
# IF need multi-agent:
1. 📊 Evaluate LangGraph
2. 💰 Upgrade LangSmith to Plus
3. 🏗️ Redesign architecture

# Cost: ~$39-239/month
```

---

## 📦 Quick Install

### LangChain
```bash
pip install langchain langchain-openai
```

### LlamaIndex
```bash
pip install llama-index
```

### LangSmith (monitoring)
```bash
# No install needed - just env vars
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_API_KEY="get-from-smith.langchain.com"
```

### LangGraph
```bash
pip install langgraph
```

---

## 🎓 5-Minute Learning Path

### 1. Understand the Ecosystem (2 min)
- LangChain = Swiss Army knife (general)
- LlamaIndex = Scalpel (specialized)
- LangSmith = Microscope (monitoring)
- LangGraph = Assembly line (workflows)

### 2. Pick Your Tool (1 min)
- Building RAG chatbot? → LangChain ✅
- Document search? → LlamaIndex
- Need monitoring? → LangSmith
- Multi-agent? → LangGraph

### 3. Add Monitoring (2 min)
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"

# That's it! All chains are now traced
```

---

## ⚡ Common Mistakes to Avoid

### ❌ DON'T:
1. Use LlamaIndex for simple RAG (overkill)
2. Skip monitoring (you'll regret in production)
3. Add LangGraph too early (complexity cost)
4. Mix everything at once (confusion)

### ✅ DO:
1. Start with LangChain for RAG
2. Add LangSmith from day 1
3. Only add LlamaIndex if needed
4. Keep it simple first

---

## 💰 Cost Reality Check

### Free Tier Setup (Đủ cho MVP)
```
LangChain:         $0
LangSmith Free:    $0 (5K traces/month)
LlamaIndex:        $0
LangGraph:         $0
────────────────────
Tools Total:       $0

OpenAI API:        ~$50-200/month
────────────────────
TOTAL:             $50-200/month
```

### Production Setup
```
LangChain:         $0
LangSmith Plus:    $39/month (100K traces)
LlamaIndex:        $0
LangGraph:         $0
────────────────────
Tools Total:       $39/month

OpenAI API:        ~$200-1000/month
────────────────────
TOTAL:             $239-1039/month
```

---

## 🔗 Essential Links

| Tool | Docs | Pricing | Sign Up |
|------|------|---------|---------|
| LangChain | [python.langchain.com](https://python.langchain.com) | FREE | - |
| LlamaIndex | [docs.llamaindex.ai](https://docs.llamaindex.ai) | FREE | - |
| LangSmith | [docs.smith.langchain.com](https://docs.smith.langchain.com) | $0-$39+ | [smith.langchain.com](https://smith.langchain.com) |
| LangGraph | [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph) | FREE | - |

---

## ✅ Checklist cho Open WebUI Project

### Now (Week 1)
- [x] Confirm LangChain in Layer 2 ✅
- [ ] Sign up LangSmith free tier
- [ ] Add tracing env vars
- [ ] Test first trace
- [ ] Monitor costs

### Later (Month 3-6)
- [ ] Benchmark retrieval speed
- [ ] Test LlamaIndex if slow
- [ ] Compare performance
- [ ] Decide on hybrid approach

### Future (Month 6-12)
- [ ] Evaluate multi-agent needs
- [ ] Test LangGraph if needed
- [ ] Upgrade LangSmith to Plus
- [ ] Production monitoring

---

## 🎯 TL;DR - Final Answer

### Cho hệ thống Open WebUI + RAG của bạn:

```
✅ DÙNG:
   - LangChain (Layer 2) - ĐÃ ĐÚNG
   - LangSmith Free - THÊM NGAY

⏸️  CHỜ:
   - LlamaIndex - Nếu retrieval chậm
   - LangGraph - Nếu cần multi-agent

💰 CHI PHÍ:
   - Hiện tại: $0
   - Sau này: $0-$39/month (tools)
   - OpenAI API: $50-1000/month (actual usage)

⏱️  THỜI GIAN:
   - Add LangSmith: 1 ngày
   - Add LlamaIndex: 1 tuần (nếu cần)
   - Add LangGraph: 2-4 tuần (nếu cần)
```

**Don't overthink it! Keep it simple.** 🎯

---

**Created:** 2025-10-28  
**For:** Open WebUI + RAG Architecture  
**Status:** ✅ Ready to use

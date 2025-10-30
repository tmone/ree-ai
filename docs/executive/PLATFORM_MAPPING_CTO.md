# 🎯 ĐỀ XUẤT PLATFORM ĐỂ TRIỂN KHAI Ý TƯỞNG CTO

> **Mục đích:** Giữ nguyên 10 services + 4 câu hỏi CTO, nhưng dùng platform MIỄN PHÍ, THÔNG DỤNG để triển khai NHANH

---

## 📊 MAPPING: YÊU CẦU CTO → PLATFORM ĐỀ XUẤT

| # | Yêu Cầu CTO | Platform Đề Xuất | Lý Do | Thời Gian Triển Khai |
|---|-------------|------------------|-------|---------------------|
| 1 | **User Account Service** | **Open WebUI** built-in | ✅ Có sẵn auth, users, roles | **0 ngày** (đã có) |
| 2 | **Orchestrator (routing)** | **LangChain Chains + RunnableRouter** | ✅ Routing logic có sẵn | **2 ngày** (config) |
| 3 | **Semantic Chunking (6 bước)** | **LangChain SemanticChunker** + custom | ✅ Base có sẵn, custom 6 bước | **3 ngày** |
| 4 | **Attribute Extraction** | **LangChain StructuredOutputParser** | ✅ JSON extraction có sẵn | **1 ngày** |
| 5 | **Classification (3 modes)** | **LangChain Classifier Chain** | ✅ Classification template có sẵn | **2 ngày** |
| 6 | **Completeness Feedback** | **LangChain Custom Chain** + GPT | ✅ Chain framework có sẵn | **2 ngày** |
| 7 | **Price Suggestion** | **LangChain Agent + Tools** | ✅ Agent framework có sẵn | **3 ngày** |
| 8 | **Rerank Service** | **LangChain Reranker** | ✅ Built-in reranking | **1 ngày** |
| 9 | **Core Gateway (Q3)** | **LiteLLM** (via LangChain) | ✅ Multi-model routing | **2 ngày** |
| 10 | **Context Memory (Q1,Q4)** | **Open WebUI** PostgreSQL + **LangChain Memory** | ✅ Conversation history có sẵn | **0 ngày** (đã có) |
| 11 | **Crawler** | **Crawl4AI** | ✅ Modern, LLM-friendly | **5 ngày** |
| 12 | **Monitoring** | **LangSmith** | ✅ Tracing, debugging | **1 ngày** setup |
| 13 | **Multi-Agent (nếu cần)** | **LangGraph** | ✅ Stateful workflows | **Optional** |

**TỔNG:** **~15-20 ngày** (thay vì 5 tuần tự code)

---

## 🏗️ KIẾN TRÚC TRIỂN KHAI

```
USER (Browser)
  ↓
┌─────────────────────────────────────────────────────┐
│ OPEN WEBUI (Layer 1)                                │
│ ✅ User Account Service (CTO #1)                    │
│ ✅ Context Memory (CTO Q1, Q4)                      │
│ • Users, Auth, JWT                                  │
│ • Conversations history (PostgreSQL)                │
│ • Load history → Auto inject to LangChain          │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│ LANGCHAIN PIPELINE (Layer 2)                        │
│ ✅ Orchestrator (CTO #2) - RunnableRouter           │
│ ✅ Semantic Chunking (CTO #3) - SemanticChunker     │
│ ✅ Attribute Extraction (CTO #4) - StructuredOutput │
│ ✅ Classification (CTO #5) - Classifier Chain       │
│ ✅ Completeness Feedback (CTO #6) - Custom Chain    │
│ ✅ Price Suggestion (CTO #7) - Agent + Tools        │
│ ✅ Rerank (CTO #8) - Reranker                       │
│                                                      │
│ File: /app/backend/data/pipelines/                  │
│       ree_ai_pipeline.py                            │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│ CORE GATEWAY (Layer 3) - Q3 ANSWER                  │
│ ✅ LiteLLM (via LangChain)                          │
│ • Rate limiting                                     │
│ • Cost tracking                                     │
│ • Model routing (Ollama/OpenAI)                     │
│ • Caching (Redis)                                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│ STORAGE (Layer 4)                                   │
│ • OpenSearch (Vector + BM25)                        │
│ • PostgreSQL (from Open WebUI) - Q1, Q4            │
│ • Redis (Cache)                                     │
└─────────────────────────────────────────────────────┘
          ↑
┌─────────────────────────────────────────────────────┐
│ CRAWLER (Layer 5)                                   │
│ • Crawl4AI (nhatot.vn, batdongsan.vn)              │
└─────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────┐
│ MONITORING (Layer 6)                                │
│ ✅ LangSmith (Tracing, Debugging)                   │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 CHI TIẾT TỪNG SERVICE

### 1️⃣ User Account Service (CTO #1)

**Yêu cầu CTO:**
- User registration, login
- Role management
- Session management

**Platform Đề Xuất:** **Open WebUI** built-in
```yaml
Tính năng có sẵn:
✅ User registration/login (email/password)
✅ JWT authentication
✅ Role-based access (admin, user)
✅ User profiles
✅ PostgreSQL backend

Setup:
docker run -d -p 3000:8080 \
  -e WEBUI_SECRET_KEY="secret" \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main

Thời gian: 0 ngày (đã có sẵn)
Code tự viết: 0 dòng
```

---

### 2️⃣ Orchestrator (CTO #2) - Q2 ANSWER

**Yêu cầu CTO:**
- Routing message: create RE / search RE / price
- Generate conversation_id

**Platform Đề Xuất:** **LangChain RunnableRouter**
```python
from langchain.chains import RunnableRouter
from langchain.prompts import ChatPromptTemplate
import uuid

# Q2 ANSWER: Gen conversation_id
conversation_id = str(uuid.uuid4())

# Routing logic
router = RunnableRouter(
    routes={
        "create_re": create_re_chain,
        "search_re": search_re_chain,
        "price_suggestion": price_chain,
    },
    route_classifier=ChatPromptTemplate.from_messages([
        ("system", "Classify user intent: create_re, search_re, or price_suggestion"),
        ("user", "{input}")
    ])
)

# Usage
result = router.invoke({
    "input": user_query,
    "conversation_id": conversation_id  # Pass to all chains
})

Thời gian: 2 ngày (setup + config)
Code tự viết: ~50 dòng (routing config)
```

**LangChain tiết kiệm:**
- ❌ Không cần tự code FastAPI routing
- ❌ Không cần tự code intent classification
- ✅ Có sẵn routing logic
- ✅ Có sẵn conversation context management

---

### 3️⃣ Semantic Chunking (CTO #3) - 6 Bước

**Yêu cầu CTO:**
1. Sentence segmentation
2. Generate embedding cho từng câu
3. Cosine similarity calculation
4. Combine sentences >0.75 threshold
5. Overlap
6. Create embedding for whole chunk

**Platform Đề Xuất:** **LangChain SemanticChunker** + custom
```python
from langchain.text_splitter import SemanticChunker
from langchain.embeddings import OpenAIEmbeddings

# Base: LangChain SemanticChunker (có sẵn bước 1-4)
chunker = SemanticChunker(
    embeddings=OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",  # Tương đương threshold 0.75
    breakpoint_threshold_amount=75
)

# Custom: Thêm bước 5-6 của CTO
class CTOSemanticChunker(SemanticChunker):
    def split_text(self, text):
        # Bước 1-4: Dùng base class
        chunks = super().split_text(text)

        # Bước 5: Overlap (custom)
        overlapped_chunks = self._add_overlap(chunks, overlap=1)

        # Bước 6: Create final embedding (custom)
        final_chunks = [
            {
                "text": chunk,
                "embedding": self.embeddings.embed_query(chunk)
            }
            for chunk in overlapped_chunks
        ]

        return final_chunks

    def _add_overlap(self, chunks, overlap=1):
        # Implement overlap logic
        pass

# Usage
custom_chunker = CTOSemanticChunker(embeddings=OpenAIEmbeddings())
result = custom_chunker.split_text(property_description)

Thời gian: 3 ngày (customize overlap + final embedding)
Code tự viết: ~100 dòng (only custom parts)
```

**LangChain tiết kiệm:**
- ✅ Bước 1-4: Có sẵn (~200 dòng code tiết kiệm)
- ✅ Embedding integration có sẵn
- ✅ Only custom bước 5-6 (~100 dòng)

---

### 4️⃣ Attribute Extraction (CTO #4)

**Yêu cầu CTO:**
- Extract structured attributes: price, location, bedrooms...
- LLM-driven
- JSON output

**Platform Đề Xuất:** **LangChain StructuredOutputParser**
```python
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from pydantic import BaseModel, Field

# Define schema
class RealEstateAttributes(BaseModel):
    price: float = Field(description="Property price in VND")
    location: str = Field(description="Full address")
    bedrooms: int = Field(description="Number of bedrooms")
    area: float = Field(description="Area in m2")
    # ... more fields

# Parser (có sẵn)
parser = PydanticOutputParser(pydantic_object=RealEstateAttributes)

# Prompt template (có sẵn)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract real estate attributes.\n{format_instructions}"),
    ("user", "{text}")
])

# Chain (có sẵn)
chain = LLMChain(
    llm=llm,
    prompt=prompt.partial(format_instructions=parser.get_format_instructions()),
    output_parser=parser
)

# Usage
result = chain.invoke({"text": property_text})
# result = RealEstateAttributes(price=2000000000, location="Quận 1", ...)

Thời gian: 1 ngày (chỉ define schema)
Code tự viết: ~30 dòng (chỉ Pydantic model)
```

**LangChain tiết kiệm:**
- ✅ Structured output parsing có sẵn (~150 dòng)
- ✅ Format instructions auto-generated
- ✅ Error handling có sẵn
- ✅ Retry logic có sẵn

---

### 5️⃣ Classification Service (CTO #5) - 3 Modes

**Yêu cầu CTO:**
- Classify query: filter / semantic / both

**Platform Đề Xuất:** **LangChain Classifier Chain**
```python
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from enum import Enum

class QueryMode(str, Enum):
    FILTER = "filter"
    SEMANTIC = "semantic"
    BOTH = "both"

# Classification prompt (template có sẵn)
classifier_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Classify the query into one of three modes:
    - filter: Has structured attributes (price, bedrooms, location)
    - semantic: Descriptive, vague (beautiful, quiet, modern)
    - both: Mix of structured + semantic

    Return JSON: {{"mode": "filter|semantic|both", "reasoning": "..."}}
    """),
    ("user", "{query}")
])

# Chain (có sẵn)
classifier_chain = LLMChain(
    llm=llm,
    prompt=classifier_prompt,
    output_parser=JsonOutputParser()
)

# Usage
result = classifier_chain.invoke({"query": "Nhà 3 phòng ngủ view đẹp Quận 1"})
# result = {"mode": "both", "reasoning": "..."}

# Route to appropriate retriever
if result["mode"] == "filter":
    retriever = structured_retriever
elif result["mode"] == "semantic":
    retriever = vector_retriever
else:
    retriever = hybrid_retriever

Thời gian: 2 ngày (prompt engineering)
Code tự viết: ~50 dòng (routing logic)
```

**LangChain tiết kiệm:**
- ✅ LLM classification có sẵn
- ✅ JSON parsing có sẵn
- ✅ Retry + error handling

---

### 6️⃣ Completeness Feedback (CTO #6)

**Yêu cầu CTO:**
- Score response 0-100
- If <70 → re-generate

**Platform Đề Xuất:** **LangChain Custom Chain**
```python
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate

# Completeness evaluator prompt
eval_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    Evaluate response completeness (0-100):
    - Answers question? (40 points)
    - Complete information? (30 points)
    - Accurate? (20 points)
    - Clear? (10 points)

    Return JSON: {{"score": int, "missing": [...], "suggestion": "..."}}
    """),
    ("user", "Query: {query}\nResponse: {response}")
])

eval_chain = LLMChain(llm=llm, prompt=eval_prompt)

# Main chain with retry logic (có sẵn trong LangChain)
from langchain.chains import SequentialChain

def generate_with_feedback(query, max_retries=3):
    for i in range(max_retries):
        # Generate response
        response = generation_chain.invoke({"query": query})

        # Evaluate
        eval_result = eval_chain.invoke({
            "query": query,
            "response": response
        })

        # Check score
        if eval_result["score"] >= 70:
            return response

        # Re-generate with feedback
        query = f"{query}\nImprove: {eval_result['suggestion']}"

    return response

Thời gian: 2 ngày (prompt + retry logic)
Code tự viết: ~80 dòng (feedback loop)
```

**LangChain tiết kiệm:**
- ✅ LLM evaluation có sẵn
- ✅ Chain composition có sẵn
- ✅ Retry framework có sẵn

---

### 7️⃣ Price Suggestion (CTO #7)

**Yêu cầu CTO:**
- Market analysis
- Similar properties
- Price range suggestion

**Platform Đề Xuất:** **LangChain Agent + Tools**
```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.tools import Tool

# Define tools
def search_similar_properties(attributes):
    # Query OpenSearch for similar properties
    pass

def get_market_trends(location):
    # Get market data
    pass

tools = [
    Tool(
        name="search_similar",
        func=search_similar_properties,
        description="Search for similar properties"
    ),
    Tool(
        name="market_trends",
        func=get_market_trends,
        description="Get market trends for location"
    )
]

# Agent (framework có sẵn)
agent = create_openai_functions_agent(
    llm=llm,
    tools=tools,
    prompt=ChatPromptTemplate.from_messages([
        ("system", "You are a real estate pricing expert. Use tools to analyze market."),
        ("user", "{input}")
    ])
)

executor = AgentExecutor(agent=agent, tools=tools)

# Usage
result = executor.invoke({
    "input": "Suggest price for 3BR apartment in District 1, 80m2"
})

Thời gian: 3 ngày (define tools + prompt)
Code tự viết: ~100 dòng (tool implementations)
```

**LangChain tiết kiệm:**
- ✅ Agent framework có sẵn (~300 dòng)
- ✅ Tool calling có sẵn
- ✅ Multi-step reasoning có sẵn

---

### 8️⃣ Rerank Service (CTO #8)

**Yêu cầu CTO:**
- Re-score search results
- Top-K selection

**Platform Đề Xuất:** **LangChain Reranker**
```python
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

# Base retriever (OpenSearch)
base_retriever = opensearch_retriever

# Reranker (có sẵn)
compressor = CohereRerank(
    model="rerank-english-v2.0",
    top_n=10
)

# Compression retriever (có sẵn)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

# Usage
results = compression_retriever.get_relevant_documents(query)

Thời gian: 1 ngày (config)
Code tự viết: ~20 dòng (wrapper)
```

**LangChain tiết kiệm:**
- ✅ Reranking có sẵn
- ✅ Multiple reranker models support
- ✅ Integration với retrievers

---

### 9️⃣ Core Gateway (CTO #9) - Q3 ANSWER

**Yêu cầu CTO:**
- Có cần Core Service tập trung OpenAI?
- Rate limiting, cost tracking, caching

**Platform Đề Xuất:** **LiteLLM** (via LangChain)
```python
from langchain.llms import LiteLLM
from langchain.cache import RedisCache
from langchain.globals import set_llm_cache
import redis

# Q3 ANSWER: CÓ - Dùng LiteLLM + Redis

# Setup caching (có sẵn)
redis_client = redis.Redis(host='localhost', port=6379)
set_llm_cache(RedisCache(redis_client))

# LiteLLM with model routing (có sẵn)
llm = LiteLLM(
    model="gpt-4o-mini",
    router_config={
        "fallbacks": ["ollama/llama3.1:8b"],  # Fallback to Ollama
        "retry_policy": {"max_retries": 3}
    },
    callbacks=[  # Cost tracking (có sẵn)
        CostTrackingCallback(),
        RateLimitCallback(max_per_hour=1000)
    ]
)

# Usage
response = llm.invoke("Extract attributes...")

Thời gian: 2 ngày (setup + callbacks)
Code tự viết: ~50 dòng (custom callbacks)
```

**LangChain tiết kiệm:**
- ✅ LiteLLM integration có sẵn
- ✅ Caching có sẵn (~100 dòng)
- ✅ Retry logic có sẵn
- ✅ Callback system có sẵn

---

### 🔟 Context Memory (CTO #10) - Q1, Q4 ANSWER

**Yêu cầu CTO:**
- Q1: Context memory - OpenAI có quản lý không?
- Q4: Conversation history khi user mở lại?

**Platform Đề Xuất:** **Open WebUI PostgreSQL** + **LangChain Memory**
```python
from langchain.memory import PostgresChatMessageHistory
from langchain.chains import ConversationChain

# Q1 ANSWER: OpenAI KHÔNG quản lý → Dùng PostgreSQL
# Open WebUI đã có PostgreSQL setup

# LangChain Memory (có sẵn)
message_history = PostgresChatMessageHistory(
    connection_string="postgresql://user:pass@postgres/openwebui",
    session_id=conversation_id  # From Q2
)

# Q4 ANSWER: Load history tự động
conversation_chain = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory(
        chat_memory=message_history,
        return_messages=True
    )
)

# Usage (history tự động load + inject)
response = conversation_chain.invoke({"input": user_query})

Thời gian: 0 ngày (Open WebUI đã có PostgreSQL + LangChain integration)
Code tự viết: ~10 dòng (config)
```

**Open WebUI + LangChain tiết kiệm:**
- ✅ PostgreSQL setup sẵn
- ✅ Users, conversations tables có sẵn
- ✅ LangChain memory integration có sẵn
- ✅ Auto load history có sẵn (~200 dòng)

---

### 1️⃣1️⃣ Crawler (CTO #11)

**Yêu cầu CTO:**
- Crawl nhatot.vn, batdongsan.vn
- JS rendering
- LLM-friendly output

**Platform Đề Xuất:** **Crawl4AI**
```python
from crawl4ai import WebCrawler

crawler = WebCrawler(
    headless=True,
    browser_type="chromium",
    markdown_generator=LLMFriendlyMarkdown()
)

# Crawl
result = await crawler.arun(
    url="https://nhatot.vn/mua-ban-bat-dong-san",
    extraction_strategy="JsonCssExtractionStrategy"
)

# Send to LangChain pipeline
for property in result:
    pipeline.invoke({"text": property})

Thời gian: 5 ngày (setup + scheduling)
Code tự viết: ~200 dòng
```

**Crawl4AI tiết kiệm:**
- ✅ JS rendering có sẵn
- ✅ LLM-friendly markdown
- ✅ 73% ít code hơn Scrapy

---

### 1️⃣2️⃣ Monitoring - LangSmith

**Yêu cầu CTO:**
- (Không có trong sơ đồ gốc, nhưng cần thiết)

**Platform Đề Xuất:** **LangSmith**
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"

# ALL LangChain chains tự động tracked!
# - Latency
# - Cost
# - Token usage
# - Errors
# - Input/output

Thời gian: 1 ngày (setup)
Code tự viết: 0 dòng (auto tracking)
```

**LangSmith tiết kiệm:**
- ✅ Tracing tự động (~500 dòng)
- ✅ Cost tracking tự động
- ✅ Dashboard có sẵn
- ✅ FREE tier: 5000 traces/month

---

### 1️⃣3️⃣ Multi-Agent (Optional) - LangGraph

**Nếu CTO muốn:**
- Complex workflows
- Multi-agent coordination

**Platform Đề Xuất:** **LangGraph**
```python
from langgraph.graph import StateGraph

# Define workflow
workflow = StateGraph()

workflow.add_node("extract", attribute_extraction_chain)
workflow.add_node("classify", classification_chain)
workflow.add_node("search", search_chain)
workflow.add_node("rerank", rerank_chain)
workflow.add_node("price", price_chain)

workflow.add_edge("extract", "classify")
workflow.add_conditional_edges(
    "classify",
    lambda x: x["mode"],
    {
        "filter": "search",
        "semantic": "search",
        "both": "search"
    }
)
workflow.add_edge("search", "rerank")
workflow.add_edge("rerank", "price")

app = workflow.compile()

# Usage
result = app.invoke({"input": user_query})

Thời gian: 5 ngày (nếu cần)
Code tự viết: ~150 dòng (workflow definition)
```

---

## 💰 SO SÁNH: TỰ CODE vs DÙNG PLATFORM

| Aspect | Tự Code (FastAPI + Custom) | Dùng Platform (Open WebUI + LangChain) |
|--------|----------------------------|----------------------------------------|
| **User Account** | 5 ngày, 500 dòng | 0 ngày, 0 dòng (Open WebUI) |
| **Orchestrator** | 3 ngày, 300 dòng | 2 ngày, 50 dòng (LangChain Router) |
| **Semantic Chunking** | 5 ngày, 400 dòng | 3 ngày, 100 dòng (LangChain base) |
| **Attribute Extraction** | 3 ngày, 200 dòng | 1 ngày, 30 dòng (StructuredOutput) |
| **Classification** | 2 ngày, 150 dòng | 2 ngày, 50 dòng (Classifier Chain) |
| **Completeness** | 3 ngày, 200 dòng | 2 ngày, 80 dòng (Custom Chain) |
| **Price Suggestion** | 5 ngày, 400 dòng | 3 ngày, 100 dòng (Agent + Tools) |
| **Rerank** | 2 ngày, 150 dòng | 1 ngày, 20 dòng (Reranker) |
| **Core Gateway** | 3 ngày, 300 dòng | 2 ngày, 50 dòng (LiteLLM) |
| **Context Memory** | 5 ngày, 400 dòng | 0 ngày, 10 dòng (Open WebUI + Memory) |
| **Crawler** | 7 ngày, 500 dòng | 5 ngày, 200 dòng (Crawl4AI) |
| **Monitoring** | 5 ngày, 500 dòng | 1 ngày, 0 dòng (LangSmith) |
| **TỔNG** | **48 ngày, 4000 dòng** | **20 ngày, 690 dòng** |

**Tiết kiệm:** **58% thời gian**, **83% code**

---

## 🎯 KẾT LUẬN - ĐỀ XUẤT CUỐI

### Stack Đề Xuất:

```yaml
Layer 1 - User Interface:
  ✅ Open WebUI

Layer 2 - Orchestration:
  ✅ LangChain (Chains, Agents, Memory)

Layer 3 - Services:
  ✅ LangChain Components:
     - RunnableRouter (Orchestrator)
     - SemanticChunker (Chunking)
     - StructuredOutputParser (Extraction)
     - Classifier Chain (Classification)
     - Custom Chains (Completeness, Price)
     - Reranker (Rerank)

Layer 4 - Gateway:
  ✅ LiteLLM (via LangChain)

Layer 5 - Storage:
  ✅ PostgreSQL (Open WebUI)
  ✅ OpenSearch
  ✅ Redis

Layer 6 - Crawler:
  ✅ Crawl4AI

Layer 7 - Monitoring:
  ✅ LangSmith

Optional:
  ⚠️ LangGraph (nếu cần multi-agent)
```

### Docker Compose:

```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - WEBUI_SECRET_KEY=secret
    volumes:
      - open-webui:/app/backend/data
      - ./pipelines:/app/backend/data/pipelines  # LangChain pipelines

  postgres:
    image: postgres:15
    # Used by Open WebUI (Q1, Q4)

  opensearch:
    image: opensearchproject/opensearch:2.11.0

  redis:
    image: redis:7-alpine

  ollama:
    image: ollama/ollama:latest
    # For LiteLLM routing

volumes:
  open-webui:
```

### Chi Phí:

```
Platforms: $0 (ALL FREE)
─────────────────────────
✅ Open WebUI: FREE
✅ LangChain: FREE
✅ LangSmith: FREE (5K traces)
✅ LangGraph: FREE
✅ Crawl4AI: FREE
✅ LiteLLM: FREE
✅ OpenSearch: FREE
✅ PostgreSQL: FREE
✅ Redis: FREE
✅ Ollama: FREE

Only Cost: OpenAI API
─────────────────────────
$100-300/month
```

### Timeline:

```
Week 1-2: Setup (5 ngày)
  - Open WebUI deployment
  - PostgreSQL + OpenSearch
  - LangChain pipeline skeleton

Week 3-4: Core Services (10 ngày)
  - 10 LangChain chains/agents
  - Integration testing

Week 5: Crawler + Polish (5 ngày)
  - Crawl4AI setup
  - LangSmith monitoring
  - End-to-end testing

TOTAL: ~20 ngày (vs 48 ngày tự code)
```

---

**Kết luận:** Dùng **Open WebUI + LangChain + LangSmith** để triển khai ý tưởng CTO → **Tiết kiệm 58% thời gian, 83% code**!

# REE AI - Implementation Plan Theo Mô Hình CTO

**Date:** 2025-10-31
**Status:** PLANNING - Cần implement đầy đủ data pipeline

---

## 🚨 Vấn Đề Hiện Tại

### Đã Có (3/10 services):
- ✅ Core Gateway (LiteLLM + failover)
- ✅ Orchestrator (routing + intent detection)
- ✅ Service Registry

### Chưa Có (7/10 services) - **CRITICAL**:
- ❌ Crawler (Crawl4AI) - Lấy data từ batdongsan.vn, nhatot.vn
- ❌ Semantic Chunking (6 steps) - Chia nhỏ document
- ❌ Attribute Extraction - Trích xuất giá, phòng ngủ, địa điểm
- ❌ Classification (3 modes) - Phân loại property
- ❌ Completeness Feedback - Kiểm tra đầy đủ
- ❌ Price Suggestion - Gợi ý giá
- ❌ Rerank - Sắp xếp kết quả

### Chưa Có Storage:
- ❌ OpenSearch setup - Vector DB
- ❌ PostgreSQL schema - Metadata storage
- ❌ RAG pipeline - Search + retrieval

---

## 📋 Implementation Roadmap

### Phase 1: Data Collection (Week 1) - CRITICAL
**Services cần implement:**

#### 1. Crawler Service (Crawl4AI)
```python
# services/crawler/main.py

from crawl4ai import AsyncWebCrawler
import asyncio

class RealEstateCrawler:
    """
    Crawl real estate data from Vietnamese websites
    """

    async def crawl_batdongsan(self):
        """Crawl batdongsan.com.vn"""
        urls = [
            "https://batdongsan.com.vn/ban-nha-rieng",
            "https://batdongsan.com.vn/ban-can-ho-chung-cu"
        ]

        async with AsyncWebCrawler() as crawler:
            for url in urls:
                result = await crawler.arun(
                    url=url,
                    word_count_threshold=10,
                    extraction_strategy=LLMExtractionStrategy(
                        provider="ollama/llama3.1:8b",
                        extraction_type="schema",
                        schema={
                            "title": str,
                            "price": str,
                            "location": str,
                            "bedrooms": int,
                            "area": str,
                            "description": str
                        }
                    )
                )

                yield result.extracted_content

    async def crawl_nhatot(self):
        """Crawl nhatot.com"""
        # Similar implementation
        pass
```

**Test cần viết:**
```python
# tests/test_crawler.py

@pytest.mark.asyncio
async def test_crawl_batdongsan_returns_properties():
    """Test crawler lấy được data từ batdongsan.com.vn"""
    crawler = RealEstateCrawler()
    results = []

    async for property in crawler.crawl_batdongsan():
        results.append(property)
        if len(results) >= 10:
            break

    # Verify data structure
    assert len(results) > 0
    assert "title" in results[0]
    assert "price" in results[0]
    assert "location" in results[0]

@pytest.mark.asyncio
async def test_crawler_extracts_correct_schema():
    """Test crawler trích xuất đúng schema"""
    # Test extraction với sample HTML
    pass

@pytest.mark.asyncio
async def test_crawler_handles_pagination():
    """Test crawler xử lý pagination"""
    # Crawl nhiều trang
    pass
```

---

#### 2. Semantic Chunking Service (6 Steps theo CTO)
```python
# services/semantic_chunking/main.py

from sentence_transformers import SentenceTransformer
import nltk
import numpy as np

class SemanticChunker:
    """
    6 Steps Semantic Chunking theo yêu cầu CTO
    """

    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        nltk.download('punkt')

    def chunk(self, text: str) -> list:
        """
        6 Steps:
        1. Sentence Segmentation
        2. Generate Embedding cho từng câu
        3. Cosine Similarity Calculation
        4. Combine với threshold >0.75
        5. Overlap window
        6. Create Embedding for whole chunk
        """

        # Step 1: Sentence Segmentation
        sentences = nltk.sent_tokenize(text, language='vietnamese')

        # Step 2: Generate Embedding
        embeddings = self.model.encode(sentences)

        # Step 3: Cosine Similarity
        similarities = self._calculate_similarities(embeddings)

        # Step 4: Combine với threshold
        chunks = self._combine_sentences(sentences, similarities, threshold=0.75)

        # Step 5: Overlap
        overlapped_chunks = self._add_overlap(chunks, window=2)

        # Step 6: Create chunk embeddings
        chunk_embeddings = [
            self.model.encode(chunk)
            for chunk in overlapped_chunks
        ]

        return [
            {
                "text": chunk,
                "embedding": emb.tolist()
            }
            for chunk, emb in zip(overlapped_chunks, chunk_embeddings)
        ]
```

**Test cần viết:**
```python
# tests/test_semantic_chunking.py

def test_step1_sentence_segmentation():
    """Test Step 1: Chia câu đúng"""
    text = "Nhà 3 phòng ngủ. Giá 5 tỷ. View đẹp ở Quận 1."
    chunker = SemanticChunker()
    sentences = chunker._segment_sentences(text)

    assert len(sentences) == 3
    assert sentences[0] == "Nhà 3 phòng ngủ."

def test_step2_generate_embeddings():
    """Test Step 2: Generate embeddings cho từng câu"""
    sentences = ["Nhà 3 phòng ngủ", "Giá 5 tỷ"]
    chunker = SemanticChunker()
    embeddings = chunker._generate_embeddings(sentences)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384  # MiniLM dimension

def test_step3_cosine_similarity():
    """Test Step 3: Tính cosine similarity"""
    # Test với 2 câu similar và 1 câu different
    pass

def test_step4_combine_threshold():
    """Test Step 4: Combine với threshold >0.75"""
    # Verify sentences with similarity >0.75 are merged
    pass

def test_step5_overlap_window():
    """Test Step 5: Overlap window"""
    # Verify overlap works correctly
    pass

def test_step6_chunk_embeddings():
    """Test Step 6: Generate embedding cho whole chunk"""
    # Verify final embeddings
    pass

def test_full_chunking_pipeline():
    """Test toàn bộ 6 steps"""
    text = """
    Bán nhà mặt tiền đường Trần Hưng Đạo, Quận 1.
    Diện tích: 80m2, 3 tầng, 4 phòng ngủ, 5 toilet.
    Giá: 15 tỷ VNĐ (có thương lượng).
    Nhà mới xây, nội thất cao cấp, view đẹp.
    Gần trường học, bệnh viện, chợ, siêu thị.
    """

    chunker = SemanticChunker()
    chunks = chunker.chunk(text)

    # Verify chunks
    assert len(chunks) > 0
    for chunk in chunks:
        assert "text" in chunk
        assert "embedding" in chunk
        assert len(chunk["embedding"]) == 384
```

---

#### 3. Attribute Extraction Service
```python
# services/attribute_extraction/main.py

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

class PropertyAttributes(BaseModel):
    price: float
    bedrooms: int
    bathrooms: int
    area: float
    location: str
    property_type: str

class AttributeExtractor:
    """
    Trích xuất attributes từ text bằng LLM
    """

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    async def extract(self, text: str) -> PropertyAttributes:
        """Extract structured attributes"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Bạn là chuyên gia trích xuất thông tin bất động sản.
Trích xuất các thông tin sau từ text:
- price: giá (VNĐ, convert sang số)
- bedrooms: số phòng ngủ
- bathrooms: số toilet
- area: diện tích (m2)
- location: địa điểm (Quận, Thành phố)
- property_type: loại (nhà, căn hộ, đất)

Trả về JSON format."""),
            ("user", "{text}")
        ])

        response = await self.llm.ainvoke(prompt.format(text=text))
        # Parse response to PropertyAttributes
        return PropertyAttributes.parse_raw(response.content)
```

**Test cần viết:**
```python
# tests/test_attribute_extraction.py

@pytest.mark.asyncio
async def test_extract_price():
    """Test trích xuất giá"""
    text = "Nhà giá 5 tỷ VNĐ"
    extractor = AttributeExtractor()
    attrs = await extractor.extract(text)

    assert attrs.price == 5_000_000_000

@pytest.mark.asyncio
async def test_extract_bedrooms():
    """Test trích xuất số phòng ngủ"""
    text = "Nhà 3 phòng ngủ, 2 toilet"
    extractor = AttributeExtractor()
    attrs = await extractor.extract(text)

    assert attrs.bedrooms == 3
    assert attrs.bathrooms == 2

@pytest.mark.asyncio
async def test_extract_location():
    """Test trích xuất địa điểm"""
    text = "Nhà ở Quận 1, TP.HCM"
    extractor = AttributeExtractor()
    attrs = await extractor.extract(text)

    assert "quận 1" in attrs.location.lower()

@pytest.mark.asyncio
async def test_extract_all_attributes():
    """Test trích xuất đầy đủ attributes"""
    text = """
    Bán nhà mặt tiền Quận 1
    Diện tích: 80m2
    3 phòng ngủ, 4 toilet
    Giá: 15 tỷ VNĐ
    """

    extractor = AttributeExtractor()
    attrs = await extractor.extract(text)

    assert attrs.price == 15_000_000_000
    assert attrs.bedrooms == 3
    assert attrs.bathrooms == 4
    assert attrs.area == 80.0
    assert "quận 1" in attrs.location.lower()
```

---

### Phase 2: Storage Setup (Week 2)

#### 4. OpenSearch Setup
```yaml
# docker-compose.yml

opensearch:
  image: opensearchproject/opensearch:latest
  environment:
    - discovery.type=single-node
    - OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m
  ports:
    - 9200:9200

# services/db_gateway/opensearch_client.py

from opensearchpy import OpenSearch

class RealEstateIndex:
    """Quản lý OpenSearch index cho real estate"""

    def __init__(self):
        self.client = OpenSearch([{'host': 'localhost', 'port': 9200}])

    def create_index(self):
        """Tạo index với mapping"""
        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "price": {"type": "float"},
                    "bedrooms": {"type": "integer"},
                    "location": {"type": "keyword"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": 384
                    }
                }
            }
        }
        self.client.indices.create(index="real_estate", body=mapping)

    async def index_property(self, property_data: dict):
        """Index một property"""
        await self.client.index(
            index="real_estate",
            body=property_data
        )

    async def search(self, query_embedding: list, filters: dict = None):
        """Vector search"""
        query = {
            "size": 10,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_embedding}
                    }
                }
            }
        }

        if filters:
            query["query"]["script_score"]["query"] = {
                "bool": {"filter": [{"term": filters}]}
            }

        return await self.client.search(index="real_estate", body=query)
```

**Test cần viết:**
```python
# tests/test_opensearch_storage.py

@pytest.mark.asyncio
async def test_create_index():
    """Test tạo index"""
    index = RealEstateIndex()
    await index.create_index()

    # Verify index exists
    assert await index.client.indices.exists("real_estate")

@pytest.mark.asyncio
async def test_index_property():
    """Test index một property"""
    property_data = {
        "title": "Nhà 3 phòng ngủ",
        "price": 5_000_000_000,
        "bedrooms": 3,
        "embedding": [0.1] * 384
    }

    index = RealEstateIndex()
    doc_id = await index.index_property(property_data)

    # Verify indexed
    doc = await index.client.get(index="real_estate", id=doc_id)
    assert doc["_source"]["title"] == "Nhà 3 phòng ngủ"

@pytest.mark.asyncio
async def test_vector_search():
    """Test vector search"""
    # Index 10 properties
    # Search with query vector
    # Verify results ranked by similarity
    pass
```

---

### Phase 3: E2E Pipeline (Week 3)

#### 5. Full Data Pipeline Test
```python
# tests/test_full_pipeline.py

@pytest.mark.e2e
@pytest.mark.slow
class TestFullDataPipeline:
    """Test toàn bộ pipeline từ crawl đến search"""

    @pytest.mark.asyncio
    async def test_crawl_to_search_pipeline(self):
        """
        Test E2E pipeline:
        1. Crawl data từ batdongsan.com.vn
        2. Semantic chunking
        3. Attribute extraction
        4. Index vào OpenSearch
        5. Search và verify kết quả
        """

        # Step 1: Crawl
        crawler = RealEstateCrawler()
        properties = []
        async for prop in crawler.crawl_batdongsan():
            properties.append(prop)
            if len(properties) >= 10:
                break

        assert len(properties) == 10

        # Step 2: Semantic Chunking
        chunker = SemanticChunker()
        chunked_properties = []
        for prop in properties:
            chunks = chunker.chunk(prop["description"])
            chunked_properties.append({
                **prop,
                "chunks": chunks
            })

        # Step 3: Attribute Extraction
        extractor = AttributeExtractor()
        extracted_properties = []
        for prop in chunked_properties:
            attrs = await extractor.extract(prop["description"])
            extracted_properties.append({
                **prop,
                "attributes": attrs.dict()
            })

        # Step 4: Index to OpenSearch
        index = RealEstateIndex()
        for prop in extracted_properties:
            await index.index_property({
                "title": prop["title"],
                "description": prop["description"],
                "price": prop["attributes"]["price"],
                "bedrooms": prop["attributes"]["bedrooms"],
                "location": prop["attributes"]["location"],
                "embedding": prop["chunks"][0]["embedding"]
            })

        # Step 5: Search
        query = "Tìm nhà 3 phòng ngủ giá dưới 6 tỷ ở Quận 1"
        query_embedding = chunker.model.encode(query).tolist()

        results = await index.search(
            query_embedding=query_embedding,
            filters={"bedrooms": 3}
        )

        # Verify results
        assert len(results["hits"]["hits"]) > 0

        # Verify filtering worked
        for hit in results["hits"]["hits"]:
            assert hit["_source"]["bedrooms"] == 3
            assert hit["_source"]["price"] < 6_000_000_000

        print(f"✅ E2E Pipeline completed: {len(results['hits']['hits'])} results found")
```

---

## 📊 Test Coverage Required

### Minimum Test Coverage:

| Component | Tests Required | Current | Status |
|-----------|---------------|---------|--------|
| Crawler | 10 tests | 0 | ❌ TODO |
| Semantic Chunking | 8 tests (6 steps + integration) | 0 | ❌ TODO |
| Attribute Extraction | 6 tests | 0 | ❌ TODO |
| Classification | 6 tests | 0 | ❌ TODO |
| Completeness | 4 tests | 0 | ❌ TODO |
| OpenSearch | 8 tests | 0 | ❌ TODO |
| PostgreSQL | 6 tests | 0 | ❌ TODO |
| RAG Pipeline | 10 tests | 0 | ❌ TODO |
| E2E Pipeline | 5 tests | 0 | ❌ TODO |
| **TOTAL** | **63 tests** | **0** | **0% coverage** |

---

## ⏱️ Implementation Timeline

### Week 1: Data Collection
- [ ] Day 1-2: Crawler Service (Crawl4AI)
- [ ] Day 3-4: Semantic Chunking (6 steps)
- [ ] Day 5: Attribute Extraction
- [ ] Day 6-7: Tests for Week 1

### Week 2: Storage & Processing
- [ ] Day 1-2: OpenSearch setup + indexing
- [ ] Day 3-4: PostgreSQL schema + storage
- [ ] Day 5: Classification Service
- [ ] Day 6-7: Tests for Week 2

### Week 3: Search & RAG
- [ ] Day 1-2: RAG Pipeline
- [ ] Day 3: Rerank Service
- [ ] Day 4: Price Suggestion
- [ ] Day 5-7: E2E tests + integration

---

## 🎯 Acceptance Criteria

### Crawler Service:
- [ ] Crawl batdongsan.com.vn successfully
- [ ] Crawl nhatot.com successfully
- [ ] Extract correct schema (title, price, location, bedrooms, area)
- [ ] Handle pagination (>100 properties)
- [ ] Error handling (network, parsing)

### Semantic Chunking:
- [ ] Step 1: Sentence segmentation works
- [ ] Step 2: Embeddings generated correctly
- [ ] Step 3: Cosine similarity calculated
- [ ] Step 4: Sentences combined with threshold >0.75
- [ ] Step 5: Overlap window applied
- [ ] Step 6: Final chunk embeddings created
- [ ] Vietnamese text support

### Storage:
- [ ] OpenSearch index created with correct mapping
- [ ] Properties indexed successfully
- [ ] Vector search works (cosine similarity)
- [ ] Filtering works (price, bedrooms, location)
- [ ] PostgreSQL stores metadata

### E2E:
- [ ] Full pipeline: Crawl → Chunk → Extract → Store → Search
- [ ] User query returns relevant results
- [ ] Results ranked by relevance
- [ ] Performance < 3s for search

---

**Status:** PLANNING
**Next Action:** Implement Crawler Service first
**Priority:** HIGH - Core data pipeline missing


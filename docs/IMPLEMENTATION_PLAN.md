# Implementation Plan - CTO Architecture Alignment

**Date:** 2025-11-17
**Status:** Approved by stakeholders

---

## ✅ Architecture Decision

**CONFIRMED:** Current architecture is correct
- **Postgres:** Master data storage (locations, amenities, translations)
- **OpenSearch:** Property storage (flexible JSON, vector + BM25 search)

**No migration needed.** Continue with current approach.

---

## 🎯 Priority Implementation

### **Priority 1: Activate Semantic Chunking**
**Timeline:** 1 week
**Owner:** [Assign]

**Tasks:**
- [ ] Integrate semantic_chunking service into orchestrator
- [ ] Add to property posting flow
- [ ] Test chunking quality with Vietnamese text
- [ ] Tune cosine similarity threshold (default 0.75)
- [ ] Measure embedding quality improvement

**Acceptance Criteria:**
- [ ] Property descriptions are chunked before embedding
- [ ] Chunks stored in OpenSearch with overlap
- [ ] Search quality improved (manual testing)

---

### **Priority 2: Enhance Attribute Extraction**
**Timeline:** 1-2 weeks
**Owner:** [Assign]

**Current Format:**
```json
{
  "bedrooms": 3,
  "property_type": "apartment"
}
```

**Target Format (CTO Spec):**
```json
{
  "value": "3 bedrooms",
  "type": "integer",
  "confidence": 0.95,
  "source_span": "text[45:55]",
  "normalized_value": 3,
  "unit": "rooms"
}
```

**Tasks:**
- [ ] Update attribute_extraction service response format
- [ ] Add confidence scoring to LLM extraction
- [ ] Track source_span in text
- [ ] Add normalized_value + unit fields
- [ ] Add validation layer (ranges, enums)
- [ ] Update orchestrator to use new format
- [ ] Update db_gateway to store confidence scores

**Files to modify:**
- `services/attribute_extraction/main.py`
- `services/orchestrator/main.py` (handler updates)
- `shared/models/properties.py` (add new fields)

**Acceptance Criteria:**
- [ ] All extractions include confidence score
- [ ] Source span tracked for debugging
- [ ] Validation prevents invalid values
- [ ] Confidence threshold configurable (default 0.7)

---

### **Priority 3: Implement Hybrid Ranking**
**Timeline:** 1-2 weeks
**Owner:** [Assign]

**CTO Formula:**
```python
final_score = α * semantic_score
            + β * attribute_match
            + γ * recency
            + δ * business_boost
```

**Tasks:**
- [ ] Implement scoring in db_gateway search
- [ ] Define default weights: α=0.4, β=0.3, γ=0.2, δ=0.1
- [ ] Make weights configurable via environment
- [ ] Add recency scoring (newer = higher)
- [ ] Add business_boost (featured properties)
- [ ] A/B testing framework (optional)

**Files to modify:**
- `services/db_gateway/main.py` (search endpoint)
- `services/db_gateway/ranking.py` (new file)

**Acceptance Criteria:**
- [ ] Search uses hybrid scoring formula
- [ ] Weights are tunable
- [ ] Recent properties ranked higher
- [ ] Featured properties get boost
- [ ] Performance < 100ms overhead

---

### **Priority 4: Implement Re-ranking Service**
**Timeline:** 2 weeks
**Owner:** [Assign]

**CTO Spec:**
- Re-rank top-50 → top-5
- Use lightweight reranker or LLM
- Apply only when scores are close

**Tasks:**
- [ ] Create `services/reranking/main.py`
- [ ] Choose approach: LLM or cross-encoder
- [ ] Implement re-rank endpoint
- [ ] Add threshold logic (re-rank if score_diff < 0.1)
- [ ] Integrate with orchestrator search flow
- [ ] Measure latency and quality impact

**Files to create:**
- `services/reranking/main.py`
- `services/reranking/Dockerfile`
- `services/reranking/requirements.txt`

**Acceptance Criteria:**
- [ ] Service running on port 8088
- [ ] Re-ranks top results effectively
- [ ] Adds < 500ms latency
- [ ] Improves relevance (manual testing)

---

## 📋 Detailed Implementation: Semantic Chunking

### **Step 1: Review Existing Service**
```bash
# Check semantic_chunking service
ls services/semantic_chunking/

# Test service independently
docker-compose up semantic-chunking
curl http://localhost:8082/health
```

### **Step 2: Integration Point**

**In orchestrator property posting flow:**

```python
# File: services/orchestrator/main.py
# Location: _handle_property_posting()

# CURRENT (around line 1500):
async def _handle_property_posting(...):
    # ... extract attributes ...

    # Save to OpenSearch
    await self._save_property_to_opensearch(property_data)

# NEW:
async def _handle_property_posting(...):
    # ... extract attributes ...

    # Semantic chunking for description
    if property_data.get("description"):
        chunks = await self._semantic_chunk_description(
            property_data["description"]
        )
        property_data["chunks"] = chunks
        property_data["embeddings"] = [chunk["embedding"] for chunk in chunks]

    # Save to OpenSearch
    await self._save_property_to_opensearch(property_data)

async def _semantic_chunk_description(self, text: str) -> List[Dict]:
    """Call semantic chunking service"""
    response = await self.http_client.post(
        "http://semantic-chunking:8080/chunk",
        json={
            "text": text,
            "language": "vi",
            "overlap_sentences": 1,
            "similarity_threshold": 0.75
        }
    )
    return response.json()["chunks"]
```

### **Step 3: Update OpenSearch Schema**

```python
# File: services/db_gateway/main.py

# Add to property document:
property_doc = {
    # ... existing fields ...
    "chunks": [
        {
            "text": "Căn hộ 2 phòng ngủ...",
            "embedding": [0.1, 0.2, ...],
            "start_offset": 0,
            "end_offset": 50
        }
    ]
}
```

### **Step 4: Test**

```python
# Create test file: tests/test_semantic_chunking_integration.py

import pytest
import httpx

@pytest.mark.asyncio
async def test_property_posting_with_chunking():
    """Test that property posting chunks description"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8090/v1/chat/completions",
            json={
                "model": "gpt-4",
                "messages": [{
                    "role": "user",
                    "content": "Tôi muốn đăng tin bán căn hộ 2PN ở Q2, view sông, gần trường học, giá 5 tỷ"
                }]
            }
        )

        # Verify property has chunks
        # ... assertions ...
```

---

## 📋 Detailed Implementation: Attribute Extraction Enhancement

### **Step 1: Update Service Response Format**

```python
# File: services/attribute_extraction/main.py

from pydantic import BaseModel
from typing import Optional

class ExtractedAttribute(BaseModel):
    """Single extracted attribute with metadata"""
    field_name: str                    # e.g., "bedrooms"
    value: str                         # Raw value: "3 phòng ngủ"
    type: str                          # "integer", "string", "float", "boolean"
    confidence: float                  # 0.0 - 1.0
    source_span: Optional[str] = None  # e.g., "text[45:55]"
    normalized_value: any              # Typed value: 3
    unit: Optional[str] = None         # e.g., "rooms"

class EnhancedExtractionResponse(BaseModel):
    """Enhanced extraction response"""
    attributes: List[ExtractedAttribute]
    overall_confidence: float
    extraction_method: str  # "llm", "regex", "hybrid"

# Update endpoint
@app.post("/extract-query", response_model=EnhancedExtractionResponse)
async def extract_query_enhanced(request: ExtractionRequest):
    """Enhanced extraction with confidence and metadata"""

    # Call LLM with enhanced prompt
    llm_response = await call_llm_extraction(request.query)

    # Parse response and add metadata
    attributes = []
    for field, value in llm_response.items():
        attr = ExtractedAttribute(
            field_name=field,
            value=str(value),
            type=infer_type(value),
            confidence=calculate_confidence(value, field),
            source_span=find_source_span(request.query, value),
            normalized_value=normalize_value(value, field),
            unit=extract_unit(value, field)
        )
        attributes.append(attr)

    return EnhancedExtractionResponse(
        attributes=attributes,
        overall_confidence=calculate_overall_confidence(attributes),
        extraction_method="llm"
    )

def calculate_confidence(value, field) -> float:
    """Calculate confidence score for extraction"""
    # Simple heuristic - can be replaced with ML model
    confidence = 1.0

    # Reduce confidence if value is ambiguous
    if field == "bedrooms" and not isinstance(value, int):
        confidence *= 0.7

    # Reduce confidence for vague location
    if field == "district" and len(value) > 50:
        confidence *= 0.6

    return max(0.1, min(1.0, confidence))

def find_source_span(text: str, value: str) -> str:
    """Find where value appears in original text"""
    try:
        start = text.lower().find(str(value).lower())
        if start >= 0:
            end = start + len(str(value))
            return f"text[{start}:{end}]"
    except:
        pass
    return None

def normalize_value(value, field):
    """Normalize value to proper type"""
    if field == "bedrooms":
        # Extract number from "3 phòng ngủ" → 3
        import re
        match = re.search(r'\d+', str(value))
        return int(match.group()) if match else None

    if field == "price":
        # "5 tỷ" → 5000000000
        return parse_price_vietnamese(value)

    return value

def extract_unit(value, field) -> Optional[str]:
    """Extract unit from value"""
    if field == "bedrooms":
        return "rooms"
    if field == "area":
        return "m²"
    if field == "price":
        return "VND"
    return None
```

### **Step 2: Update Orchestrator to Use Enhanced Format**

```python
# File: services/orchestrator/main.py

async def _extract_property_attributes(self, query: str) -> Dict:
    """Extract attributes with confidence tracking"""

    response = await self.http_client.post(
        f"{self.extraction_url}/extract-query",
        json={"query": query, "intent": "POST"}
    )

    data = response.json()

    # NEW: Filter by confidence threshold
    CONFIDENCE_THRESHOLD = 0.7

    high_confidence_attrs = {}
    low_confidence_attrs = {}

    for attr in data["attributes"]:
        if attr["confidence"] >= CONFIDENCE_THRESHOLD:
            high_confidence_attrs[attr["field_name"]] = attr["normalized_value"]
        else:
            low_confidence_attrs[attr["field_name"]] = {
                "value": attr["normalized_value"],
                "confidence": attr["confidence"],
                "needs_verification": True
            }

    # Log low confidence extractions for review
    if low_confidence_attrs:
        self.logger.warning(
            f"Low confidence extractions: {low_confidence_attrs}"
        )

    return {
        "attributes": high_confidence_attrs,
        "low_confidence": low_confidence_attrs,
        "overall_confidence": data["overall_confidence"]
    }
```

### **Step 3: Add Validation Layer**

```python
# File: services/attribute_extraction/validation.py

from typing import Dict, List, Any

class AttributeValidator:
    """Validate extracted attributes"""

    PROPERTY_TYPES = ["apartment", "house", "villa", "land", "office"]

    RANGES = {
        "bedrooms": (0, 20),
        "bathrooms": (0, 20),
        "area": (10, 10000),  # m²
        "price": (100000000, 100000000000),  # 100M - 100B VND
        "floor": (0, 100)
    }

    def validate(self, field: str, value: Any) -> Dict:
        """Validate single attribute"""
        errors = []

        # Type validation
        if field == "bedrooms" and not isinstance(value, int):
            errors.append(f"Invalid type: expected int, got {type(value)}")

        # Range validation
        if field in self.RANGES:
            min_val, max_val = self.RANGES[field]
            if not (min_val <= value <= max_val):
                errors.append(f"Out of range: {value} not in [{min_val}, {max_val}]")

        # Enum validation
        if field == "property_type" and value not in self.PROPERTY_TYPES:
            errors.append(f"Invalid property_type: {value} not in {self.PROPERTY_TYPES}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "corrected_value": self._auto_correct(field, value) if errors else value
        }

    def _auto_correct(self, field: str, value: Any) -> Any:
        """Auto-correct common mistakes"""
        if field == "property_type":
            # Fuzzy match
            value_lower = str(value).lower()
            for valid_type in self.PROPERTY_TYPES:
                if valid_type in value_lower:
                    return valid_type

        return value
```

### **Step 4: Update Models**

```python
# File: shared/models/properties.py

from pydantic import BaseModel
from typing import Optional

class PropertyAttribute(BaseModel):
    """Extracted property attribute with metadata"""
    value: Any
    confidence: float
    source_span: Optional[str] = None
    unit: Optional[str] = None
    validated: bool = True

class PropertyDocument(BaseModel):
    """Property document with enhanced attributes"""
    property_id: str
    title: str
    description: str

    # Enhanced attributes with confidence
    bedrooms: Optional[PropertyAttribute] = None
    bathrooms: Optional[PropertyAttribute] = None
    area: Optional[PropertyAttribute] = None
    price: Optional[PropertyAttribute] = None

    # For backward compatibility, also store simple values
    bedrooms_value: Optional[int] = None
    bathrooms_value: Optional[int] = None
    area_value: Optional[float] = None
    price_value: Optional[float] = None
```

---

## 🧪 Testing Strategy

### **Semantic Chunking Tests:**
```python
# Test 1: Basic chunking
description = "Căn hộ 2 phòng ngủ, view sông, gần trường học..."
chunks = await semantic_chunk(description)
assert len(chunks) > 1
assert all("embedding" in chunk for chunk in chunks)

# Test 2: Overlap
assert chunks[1]["start_offset"] < chunks[0]["end_offset"]

# Test 3: Search quality
# Manual testing: compare search results before/after
```

### **Attribute Extraction Tests:**
```python
# Test 1: Confidence scoring
result = await extract("căn hộ 2-3 phòng ngủ")  # Ambiguous
assert result.attributes[0].confidence < 0.8

# Test 2: Source span
result = await extract("Tôi có căn hộ 2 phòng ngủ")
assert "2 phòng ngủ" in result.attributes[0].source_span

# Test 3: Validation
result = await extract("100 phòng ngủ")  # Invalid
assert not result.attributes[0].validated
```

---

## 📊 Success Metrics

### **Semantic Chunking:**
- [ ] Chunking applied to 100% of property postings
- [ ] Average chunks per property: 3-5
- [ ] Search relevance improved (manual review of 50 queries)

### **Attribute Extraction:**
- [ ] Average confidence > 0.85
- [ ] Validation catches 90%+ of invalid values
- [ ] Source span tracked for 100% of extractions

### **Hybrid Ranking:**
- [ ] Search latency increase < 100ms
- [ ] Top-5 results include at least 3 highly relevant properties
- [ ] Featured properties appear in top 10

### **Re-ranking:**
- [ ] Re-ranking applied to queries with close scores
- [ ] Latency < 500ms
- [ ] Relevance improved (A/B test)

---

## 📅 Timeline

```
Week 1: Semantic Chunking
├─ Days 1-2: Code integration
├─ Days 3-4: Testing
└─ Day 5: Deploy

Week 2-3: Attribute Extraction
├─ Week 2: Implement enhanced format
└─ Week 3: Validation + testing

Week 4-5: Hybrid Ranking
├─ Week 4: Implement scoring
└─ Week 5: Tuning + testing

Week 6-7: Re-ranking Service
├─ Week 6: Build service
└─ Week 7: Integration + testing
```

**Total:** 7 weeks to complete all priorities

---

## ✅ Next Steps

1. **Today:** Assign owners to each priority
2. **This Week:** Start Semantic Chunking implementation
3. **Weekly:** Progress review meetings
4. **End of Sprint:** Demo each completed feature

---

**Document Owner:** Development Team
**Last Updated:** 2025-11-17
**Next Review:** Weekly sprint planning

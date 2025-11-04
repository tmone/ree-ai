# Deep Bug Hunter - Detailed Analysis & Fixes

**Test Date:** 2025-11-04
**Orchestrator Version:** v2 with ReAct Reasoning
**Total Bugs Found:** 8 (3 HIGH, 5 MEDIUM)

---

## 🔴 HIGH PRIORITY BUGS (Must Fix Immediately)

### Bug #1: Empty Query False Confidence
**Severity:** HIGH
**Category:** LOGIC_ERROR
**Test Case:** Empty query (`""`)

**Issue:**
Empty queries return confidence = 0.9, which incorrectly suggests the system understands a blank request.

**Expected Behavior:**
- Confidence should be 0.0 or very low (<0.1)
- Should trigger validation error or return "needs_clarification = true"

**Root Cause:**
Ambiguity detector or reasoning engine doesn't validate for empty input before processing.

**Proposed Fix:**

```python
# File: services/orchestrator/reasoning_engine.py

async def execute_react_loop(
    query: str,
    intent: str,
    history: List[Dict],
    knowledge_expansion: Optional[KnowledgeExpansion],
    ambiguity_result: Optional[AmbiguityDetectionResult]
) -> ReasoningChain:
    chain = ReasoningChain(query=query)

    # FIX: Add input validation step
    if not query or not query.strip():
        chain.add_thought(
            stage=ThinkingStage.QUERY_ANALYSIS,
            thought="Empty query detected - cannot proceed",
            data={"validation_error": "Query is empty or whitespace only"},
            confidence=0.0
        )
        chain.final_conclusion = "Please provide a property search query."
        chain.overall_confidence = 0.0
        return chain

    # Rest of the function...
```

**Files to Modify:**
- `services/orchestrator/reasoning_engine.py` - Add input validation
- `services/orchestrator/ambiguity_detector.py` - Add EMPTY_QUERY ambiguity type

**Testing:**
```bash
curl -X POST http://localhost:8090/orchestrate/v2 \
  -H "Content-Type: application/json" \
  -d '{"query": "", "user_id": "test"}'
# Expected: confidence=0.0, needs_clarification=true
```

---

### Bug #2: Whitespace-Only Query False Confidence
**Severity:** HIGH
**Category:** LOGIC_ERROR
**Test Case:** Only spaces (`"   "`)

**Issue:**
Queries with only whitespace return confidence = 0.9, same as Bug #1.

**Expected Behavior:**
- Should be treated as empty query
- Confidence = 0.0
- Trigger validation error

**Root Cause:**
Input validation uses `if not query:` which doesn't catch whitespace-only strings.

**Proposed Fix:**
Same as Bug #1 - the fix with `query.strip()` handles this case.

---

### Bug #3: Mixed Language Query Timeout
**Severity:** HIGH
**Category:** TIMEOUT
**Test Case:** `"Find nhà house maison 家"`

**Issue:**
Queries mixing multiple languages (English, Vietnamese, French, Chinese) cause request timeout (>90s).

**Expected Behavior:**
- Should handle gracefully within 5-10 seconds
- May have lower confidence, but shouldn't timeout

**Root Cause:**
Likely the LLM call in knowledge expansion or reasoning engine gets confused by multilingual input and takes too long.

**Proposed Fix:**

```python
# File: services/orchestrator/knowledge_base.py

async def expand_query(self, query: str) -> KnowledgeExpansion:
    # FIX: Detect mixed languages and simplify
    languages_detected = self._detect_languages(query)

    if len(languages_detected) > 2:
        # Too many languages - extract Vietnamese/English only
        cleaned_query = self._extract_main_languages(query)
        expansion_reason = f"Detected {len(languages_detected)} languages, simplified to: {cleaned_query}"
    else:
        cleaned_query = query
        expansion_reason = "Query language check passed"

    # Use cleaned query for LLM expansion
    prompt = f"Extract real estate terms from: {cleaned_query}"
    ...

def _detect_languages(self, query: str) -> List[str]:
    """Simple language detection based on character sets"""
    languages = set()
    if re.search(r'[a-zA-Z]', query):
        languages.add('latin')
    if re.search(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệ]', query):
        languages.add('vietnamese')
    if re.search(r'[\u4e00-\u9fff]', query):
        languages.add('chinese')
    if re.search(r'[\u0400-\u04FF]', query):
        languages.add('cyrillic')
    return list(languages)

def _extract_main_languages(self, query: str) -> str:
    """Keep only Vietnamese and Latin characters"""
    # Remove Chinese, Cyrillic, etc.
    cleaned = re.sub(r'[\u4e00-\u9fff\u0400-\u04FF]', '', query)
    return cleaned.strip()
```

**Additional Fix - Add Timeout to LLM Calls:**

```python
# File: shared/models/core_gateway.py or services/orchestrator/reasoning_engine.py

# Set shorter timeout for LLM calls in reasoning
async with httpx.AsyncClient(timeout=15.0) as client:  # Was 30.0
    response = await client.post(...)
```

**Files to Modify:**
- `services/orchestrator/knowledge_base.py` - Add language detection
- `services/orchestrator/reasoning_engine.py` - Reduce LLM timeout

---

## 🟡 MEDIUM PRIORITY BUGS (Should Fix Soon)

### Bug #4: Very Long Query Performance
**Severity:** MEDIUM
**Category:** PERFORMANCE
**Test Case:** 100x "Tìm " + "căn hộ" (very long query)

**Issue:**
Query with 500+ characters takes 9.6 seconds to process (should be <3s).

**Expected Behavior:**
- Long queries should be truncated with warning
- Response time <5s even for long input

**Root Cause:**
No input length limit. LLM processes entire 500-char string unnecessarily.

**Proposed Fix:**

```python
# File: services/orchestrator/main.py

MAX_QUERY_LENGTH = 500  # Characters

@self.app.post("/orchestrate/v2", response_model=OrchestrationResponse)
async def orchestrate_v2(request: OrchestrationRequest):
    original_query = request.query

    # FIX: Truncate very long queries
    if len(original_query) > MAX_QUERY_LENGTH:
        request.query = original_query[:MAX_QUERY_LENGTH]
        truncation_warning = f"Query truncated from {len(original_query)} to {MAX_QUERY_LENGTH} chars"
        logger.warning(f"⚠️ {truncation_warning}")

    # Continue with processing...
```

**Files to Modify:**
- `services/orchestrator/main.py` - Add query length validation

---

### Bug #5: Unicode Emoji Performance
**Severity:** MEDIUM
**Category:** PERFORMANCE
**Test Case:** `"Tìm nhà 🏠 đẹp 😍"`

**Issue:**
Queries with emoji take 7.87s (should be <3s).

**Expected Behavior:**
- Emoji should be stripped or ignored
- Performance same as non-emoji queries

**Root Cause:**
Emoji characters may confuse tokenizer or LLM encoding.

**Proposed Fix:**

```python
# File: services/orchestrator/ambiguity_detector.py or knowledge_base.py

import re

def _clean_query(self, query: str) -> str:
    """Remove emoji and special unicode characters"""
    # Remove emoji (most emoji are in these ranges)
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    cleaned = emoji_pattern.sub(r'', query)
    return cleaned.strip()

# Use in expand_query and detect_ambiguities:
async def expand_query(self, query: str) -> KnowledgeExpansion:
    query = self._clean_query(query)
    # Continue with cleaned query...
```

**Files to Modify:**
- `services/orchestrator/knowledge_base.py` - Add emoji cleaning
- `services/orchestrator/ambiguity_detector.py` - Add emoji cleaning

---

### Bug #6: Concurrent Request Performance
**Severity:** MEDIUM
**Category:** PERFORMANCE
**Test Case:** 5 concurrent requests

**Issue:**
Max response time under load: 11.7s (should be <5s even under load).

**Expected Behavior:**
- Concurrent requests should be handled efficiently
- Max response time <5s for 5 concurrent requests

**Root Cause:**
- No connection pooling for httpx clients
- Possible LLM rate limiting or queueing
- Lack of caching for similar queries

**Proposed Fix:**

1. **Add Connection Pooling:**

```python
# File: services/orchestrator/main.py

class OrchestratorService(BaseService):
    def __init__(self):
        super().__init__(...)
        # FIX: Reuse HTTP client for connection pooling
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20
            )
        )

    async def shutdown(self):
        await self.http_client.aclose()
```

2. **Add Response Caching:**

```python
# File: services/orchestrator/main.py

from functools import lru_cache
import hashlib

def _cache_key(query: str, user_id: str) -> str:
    """Generate cache key for query"""
    return hashlib.md5(f"{query}:{user_id}".encode()).hexdigest()

# Simple in-memory cache (for production, use Redis)
response_cache = {}

@self.app.post("/orchestrate/v2", response_model=OrchestrationResponse)
async def orchestrate_v2(request: OrchestrationRequest):
    cache_key = _cache_key(request.query, request.user_id)

    # Check cache (5-minute TTL)
    if cache_key in response_cache:
        cached, timestamp = response_cache[cache_key]
        if time.time() - timestamp < 300:  # 5 minutes
            logger.info(f"🎯 Cache hit for query: {request.query}")
            return cached

    # Process normally...
    response = await self._process_request(request)

    # Save to cache
    response_cache[cache_key] = (response, time.time())
    return response
```

**Files to Modify:**
- `services/orchestrator/main.py` - Add connection pooling and caching

---

### Bug #7: Knowledge Base Gap - "trường quốc tế"
**Severity:** MEDIUM
**Category:** KNOWLEDGE_GAP
**Test Case:** Term "trường quốc tế" expanded to 0 terms

**Issue:**
Important term "trường quốc tế" (international school) not expanded. This is a critical search criterion in Vietnam real estate.

**Expected Behavior:**
- Should expand to: ["international school", "AIS", "BIS", "ISHCMC", "British International School", "Australian International School"]
- Should suggest districts: Quận 2, Quận 7, Thủ Đức

**Root Cause:**
Missing in `knowledge/LOCATIONS.md` and `knowledge/PROPERTIES.md`.

**Proposed Fix:**

```markdown
# File: knowledge/LOCATIONS.md

## Trường Học Quốc Tế (International Schools)

### District 2 (Quận 2)
- **AIS** (Australian International School) - Thảo Điền
- **BIS** (British International School) - An Phú
- **ISHCMC** (International School Ho Chi Minh City) - Thảo Điền

### District 7 (Quận 7)
- **SSIS** (Saigon South International School) - Phú Mỹ Hưng
- **ILA** (International Language Academy) - Phú Mỹ Hưng

### Thu Duc City (Thủ Đức)
- **VAS** (Vietnam Australia School) - An Phú, Quận 2
- **ISHCMC American Academy** - Thảo Điền

### Query Expansion Rules
When user mentions:
- "trường quốc tế" → Expand to: international school, AIS, BIS, ISHCMC, SSIS, VAS
- "gần trường quốc tế" → Auto-filter districts: 2, 7, Thủ Đức
- Radius: 2km from school locations
```

**Files to Modify:**
- `knowledge/LOCATIONS.md` - Add international schools section

---

### Bug #8: Ambiguity Detection Miss - "Tìm nhà đẹp"
**Severity:** MEDIUM
**Category:** AMBIGUITY_MISS
**Test Case:** `"Tìm nhà đẹp"` (Find beautiful house)

**Issue:**
Query "Tìm nhà đẹp" not flagged as ambiguous, but "đẹp" (beautiful) is subjective and vague.

**Expected Behavior:**
- Should detect AMENITY_AMBIGUOUS ambiguity type
- Should ask: "Bạn muốn tìm nhà đẹp theo tiêu chí nào? (Kiến trúc hiện đại, nội thất sang trọng, view đẹp, khu vực yên tĩnh...)"

**Root Cause:**
Ambiguity detector doesn't check for vague aesthetic terms.

**Proposed Fix:**

```python
# File: services/orchestrator/ambiguity_detector.py

VAGUE_AESTHETIC_TERMS = [
    "đẹp", "beautiful", "nice", "good", "tốt",
    "sang", "luxury", "cao cấp",
    "ổn", "ok", "okay",
    "chất lượng", "quality"
]

async def detect_ambiguities(
    self,
    query: str,
    intent: str = "search"
) -> AmbiguityDetectionResult:
    ambiguities = []

    # Existing checks...

    # NEW: Check for vague aesthetic terms
    query_lower = query.lower()
    vague_terms_found = [
        term for term in VAGUE_AESTHETIC_TERMS
        if term in query_lower
    ]

    if vague_terms_found and not self._has_specific_criteria(query):
        ambiguities.append(AmbiguityItem(
            type=AmbiguityType.AMENITY_AMBIGUOUS,
            description=f"Vague aesthetic terms: {', '.join(vague_terms_found)}",
            suggestion="Please specify: modern architecture, luxury interior, good view, quiet area, etc.",
            confidence=0.8
        ))

    # Rest of function...

def _has_specific_criteria(self, query: str) -> bool:
    """Check if query has specific search criteria"""
    specific_criteria = [
        r'\d+\s*(phòng|bedroom|br)',  # "3 phòng ngủ"
        r'\d+\s*(tỷ|triệu|million|billion)',  # "5 tỷ"
        r'quận\s*\d+',  # "Quận 2"
        r'(hồ bơi|gym|ban công|view)',  # Specific amenities
    ]
    for pattern in specific_criteria:
        if re.search(pattern, query.lower()):
            return True
    return False
```

**Files to Modify:**
- `services/orchestrator/ambiguity_detector.py` - Add vague aesthetic detection

---

## 📋 Implementation Plan

### Phase 1: Critical Fixes (Priority 1 - Do Now)
1. **Bug #1 & #2**: Add input validation for empty/whitespace queries (30 mins)
2. **Bug #3**: Add language detection and timeout handling (1 hour)

### Phase 2: Performance Optimization (Priority 2 - This Week)
3. **Bug #4**: Add query length limits (15 mins)
4. **Bug #5**: Add emoji cleaning (30 mins)
5. **Bug #6**: Add connection pooling and caching (1 hour)

### Phase 3: Knowledge & Logic Improvements (Priority 3 - Next Sprint)
6. **Bug #7**: Expand knowledge base with international schools (30 mins)
7. **Bug #8**: Improve ambiguity detection for aesthetic terms (45 mins)

**Total Estimated Time:** 4-5 hours

---

## 🧪 Testing Checklist

After each fix, run:

```bash
# Quick regression test
python3 tests/quick_test.py

# Deep bug hunter
python3 tests/deep_bug_hunter.py

# Specific edge case tests
curl -X POST http://localhost:8090/orchestrate/v2 \
  -H "Content-Type: application/json" \
  -d '{"query": "", "user_id": "test"}'

curl -X POST http://localhost:8090/orchestrate/v2 \
  -H "Content-Type: application/json" \
  -d '{"query": "   ", "user_id": "test"}'

curl -X POST http://localhost:8090/orchestrate/v2 \
  -H "Content-Type: application/json" \
  -d '{"query": "Find nhà house maison 家", "user_id": "test"}'
```

---

## 📊 Success Metrics

After all fixes:
- ✅ Empty query: confidence = 0.0
- ✅ Mixed language: response time < 5s
- ✅ Long query: response time < 5s
- ✅ Emoji query: response time < 3s
- ✅ Concurrent load: max response < 5s
- ✅ "trường quốc tế": expanded to 5+ terms
- ✅ "Tìm nhà đẹp": ambiguity detected

---

**Generated by:** Deep Bug Hunter v1.0
**Next Review:** After Phase 1 implementation

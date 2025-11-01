# 🎯 Comprehensive Business Logic Test Plan
## REE AI Platform - CTO Requirements Validation

**Date:** 2025-11-01
**Status:** 🚧 In Progress
**Data Available:** 13,448 Vietnam real estate properties

---

## 📋 Executive Summary

### Test Objectives
1. ✅ **Validate CTO Requirements** - Test all 10 services against CTO diagram
2. ✅ **Verify Business Logic** - Test 8 intent types with real data
3. ✅ **Improve Prompts** - Optimize for Vietnamese real estate domain
4. ✅ **End-to-End Testing** - Full user journey from query to response

### Current Status
- **Architecture:** 7-layer implementation (CTO diagram)
- **Services:** 10/10 mapped to platforms
- **Data:** 13,448 properties from Batdongsan.com.vn
- **Prompts:** Need alignment with CTO requirements

---

## 🎨 CTO Requirements vs Current Implementation

### Gap Analysis

| CTO Requirement | Current Implementation | Status | Gap |
|----------------|------------------------|--------|-----|
| **10 Services** | 10 services implemented | ✅ | None |
| **Intent Types** | 8 intents in code vs prompts | ⚠️ | **MISMATCH** |
| **Vietnamese Support** | Prompts have Vietnamese | ✅ | None |
| **RAG Pipeline** | Implemented but untested | ⚠️ | **Need testing** |
| **Context Memory (Q1)** | PostgreSQL + Open WebUI | ✅ | None |
| **Conversation ID (Q2)** | UUID generation | ✅ | None |
| **Core Gateway (Q3)** | LiteLLM implemented | ✅ | None |
| **History Loading (Q4)** | LangChain Memory | ✅ | None |

### Critical Gap Found! 🚨

**orchestrator/main.py Intent Types:**
```python
SEARCH, CHAT, CLASSIFY, EXTRACT, PRICE_SUGGEST, COMPARE, RECOMMEND, UNKNOWN
```

**orchestrator/prompts.py Intent Types:**
```python
SEARCH, COMPARE, PRICE_ANALYSIS, INVESTMENT_ADVICE, LOCATION_INSIGHTS,
LEGAL_GUIDANCE, CHAT, UNKNOWN
```

**⚠️ Mismatch between code and prompts!**

---

## 🧪 Test Plan - 8 Intent Types

### 1. SEARCH Intent (CTO Service #8: RAG)

**Business Logic:**
- User searches for properties with specific criteria
- System uses RAG (Vector + BM25) to find matching properties
- Returns top 10 results ranked by relevance

**Test Cases:**

```python
# TC1.1: Simple search - Location only
Query: "Tìm căn hộ Quận 7"
Expected Intent: SEARCH
Expected Entities: {
    "property_type": "căn hộ",
    "location": "Quận 7"
}
Expected Service: rag_service
Expected Response: List of apartments in District 7

# TC1.2: Complex search - Multiple criteria
Query: "Tìm nhà 2 phòng ngủ Quận 2 dưới 3 tỷ gần metro"
Expected Intent: SEARCH
Expected Entities: {
    "bedrooms": 2,
    "location": "Quận 2",
    "price_range": {"max": 3000000000},
    "amenities": ["metro"]
}
Expected Service: rag_service
Expected Response: Filtered results matching all criteria

# TC1.3: Search with Vietnamese variations
Queries to test:
- "Có nhà nào giá rẻ không?" → SEARCH
- "Cần mua căn hộ gấp" → SEARCH
- "Find cheap apartments" → SEARCH (English)
```

**Success Criteria:**
- ✅ Intent detection accuracy ≥ 90%
- ✅ Entity extraction accuracy ≥ 85%
- ✅ RAG returns relevant results (P@10 ≥ 0.7)
- ✅ Response time < 2 seconds

---

### 2. COMPARE Intent (CTO Service #8: RAG + Analysis)

**Business Logic:**
- User wants to compare 2+ properties
- System retrieves properties from RAG
- LLM analyzes and creates comparison table

**Test Cases:**

```python
# TC2.1: Compare by IDs
Query: "So sánh căn hộ #123 và #456"
Expected Intent: COMPARE
Expected Entities: {
    "property_ids": ["123", "456"]
}
Expected Service: rag_service → comparison_chain
Expected Response: Comparison table with pros/cons

# TC2.2: Compare by implicit reference
Query: "So sánh 2 căn hộ Vinhomes Grand Park"
Expected Intent: COMPARE
Expected Entities: {
    "count": 2,
    "location": "Vinhomes Grand Park"
}
Expected Service: rag_service (get top 2) → comparison
Expected Response: Side-by-side comparison

# TC2.3: Multi-turn conversation context
Turn 1: "Tìm căn hộ Q7" → Returns results
Turn 2: "So sánh 2 căn đầu" → COMPARE using context
Expected: Use conversation history to identify properties
```

**Success Criteria:**
- ✅ Comparison includes: price, size, location, pros/cons
- ✅ Structured output (table format)
- ✅ Recommendations based on comparison
- ✅ Works with conversation context

---

### 3. PRICE_ANALYSIS Intent (CTO Service #7: Price Suggestion)

**Business Logic:**
- User asks if a price is reasonable
- System analyzes against market data (13K properties)
- Provides price recommendation with reasoning

**Test Cases:**

```python
# TC3.1: Price reasonability check
Query: "Giá 2.5 tỷ cho căn hộ 70m² Q7 có hợp lý không?"
Expected Intent: PRICE_ANALYSIS
Expected Entities: {
    "price": 2500000000,
    "area": 70,
    "location": "Quận 7",
    "property_type": "căn hộ"
}
Expected Service: price_suggestion
Expected Response:
- Market average price for similar properties
- "Hợp lý" or "Cao hơn thị trường X%"
- Reasoning with data

# TC3.2: Price range question
Query: "Bao nhiêu tiền mua được nhà 100m² Quận 2?"
Expected Intent: PRICE_ANALYSIS
Expected Response: Price range from market data

# TC3.3: Investment ROI
Query: "Căn này 3 tỷ, sau 5 năm bán được bao nhiêu?"
Expected Intent: PRICE_ANALYSIS (or INVESTMENT_ADVICE)
Expected Response: ROI projection based on trends
```

**Success Criteria:**
- ✅ Uses real market data from 13K properties
- ✅ Price analysis accuracy within 10% of market
- ✅ Clear reasoning with data points
- ✅ Vietnamese + English support

---

### 4. INVESTMENT_ADVICE Intent (Custom)

**Business Logic:**
- User asks for investment recommendations
- System analyzes market trends, location potential
- Provides data-driven investment advice

**Test Cases:**

```python
# TC4.1: Location comparison for investment
Query: "Nên đầu tư Q2 hay Q7 với 5 tỷ?"
Expected Intent: INVESTMENT_ADVICE
Expected Entities: {
    "locations": ["Quận 2", "Quận 7"],
    "budget": 5000000000
}
Expected Response:
- Growth trends for both districts
- Price appreciation data
- Recommendation with reasoning

# TC4.2: Investment potential question
Query: "Căn này có tiềm năng sinh lời không?"
Expected Intent: INVESTMENT_ADVICE
Expected Response:
- Location analysis
- Market trends
- Rental yield potential
- Appreciation forecast

# TC4.3: Budget optimization
Query: "5 tỷ nên mua 1 căn lớn hay 2 căn nhỏ?"
Expected Intent: INVESTMENT_ADVICE
Expected Response: Strategy comparison with ROI
```

**Success Criteria:**
- ✅ Data-driven recommendations
- ✅ Market trend analysis
- ✅ Risk assessment
- ✅ Clear reasoning

---

### 5. LOCATION_INSIGHTS Intent (Custom)

**Business Logic:**
- User asks about a specific area/district
- System provides insights: infrastructure, amenities, trends
- Uses both structured data + LLM knowledge

**Test Cases:**

```python
# TC5.1: General area question
Query: "Quận Thủ Đức có gì hay?"
Expected Intent: LOCATION_INSIGHTS
Expected Entities: {
    "location": "Quận Thủ Đức"
}
Expected Response:
- Key developments (Tech Park, universities)
- Infrastructure (Metro, highways)
- Average prices
- Growth potential

# TC5.2: Amenities question
Query: "Gần đây có trường học nào không?"
Expected Intent: LOCATION_INSIGHTS (context-dependent)
Expected Response: Schools near current context location

# TC5.3: Comparison of locations
Query: "Q7 và Q2 khác nhau thế nào?"
Expected Intent: LOCATION_INSIGHTS or COMPARE
Expected Response: Location comparison table
```

**Success Criteria:**
- ✅ Accurate location data
- ✅ Infrastructure insights
- ✅ Price trends for area
- ✅ Amenities list

---

### 6. LEGAL_GUIDANCE Intent (CTO Service: Core Gateway)

**Business Logic:**
- User asks legal/procedural questions
- System uses LLM knowledge (no RAG needed)
- Provides legal guidance with disclaimers

**Test Cases:**

```python
# TC6.1: Document question
Query: "Sổ đỏ khác sổ hồng thế nào?"
Expected Intent: LEGAL_GUIDANCE
Expected Service: core_gateway (direct LLM)
Expected Response:
- Clear explanation of differences
- Legal disclaimer
- When to use which

# TC6.2: Process question
Query: "Thủ tục mua nhà gồm những gì?"
Expected Intent: LEGAL_GUIDANCE
Expected Response:
- Step-by-step process
- Required documents
- Timeline
- Costs involved

# TC6.3: Tax question
Query: "Phải đóng thuế gì khi bán nhà?"
Expected Intent: LEGAL_GUIDANCE
Expected Response:
- Tax types (Capital gains, etc.)
- Calculation method
- Legal disclaimer
```

**Success Criteria:**
- ✅ Accurate legal information
- ✅ Clear disclaimers
- ✅ Step-by-step guidance
- ✅ Vietnamese legal context

---

### 7. CHAT Intent (CTO Service: Core Gateway)

**Business Logic:**
- General conversation, greetings, questions about system
- Uses Core Gateway for simple LLM chat
- No RAG needed

**Test Cases:**

```python
# TC7.1: Greetings
Queries:
- "Xin chào" → CHAT
- "Hello" → CHAT
- "Bạn là ai?" → CHAT
Expected Response: Friendly introduction of REE AI

# TC7.2: System capabilities
Query: "Bạn có thể làm gì?"
Expected Intent: CHAT
Expected Response: List of capabilities (search, compare, price analysis, etc.)

# TC7.3: Chitchat
Query: "Hôm nay thời tiết thế nào?"
Expected Intent: CHAT or UNKNOWN
Expected Response: Polite deflection to real estate topics
```

**Success Criteria:**
- ✅ Friendly, helpful tone
- ✅ Introduces capabilities
- ✅ Deflects off-topic gracefully
- ✅ Fast response (< 1s)

---

### 8. UNKNOWN Intent (Fallback)

**Business Logic:**
- Query doesn't match any intent
- System asks for clarification
- Suggests valid intent types

**Test Cases:**

```python
# TC8.1: Gibberish
Query: "asdf qwer zxcv"
Expected Intent: UNKNOWN
Expected Response: "Xin lỗi, tôi không hiểu. Bạn có thể hỏi về..."

# TC8.2: Off-topic
Query: "Tính 2+2 bằng mấy?"
Expected Intent: UNKNOWN
Expected Response: Redirect to real estate topics

# TC8.3: Ambiguous
Query: "Nó như thế nào?"
Expected Intent: UNKNOWN (needs context)
Expected Response: "Bạn đang hỏi về bất động sản nào?"
```

**Success Criteria:**
- ✅ Polite error handling
- ✅ Suggests valid queries
- ✅ No hallucination
- ✅ Graceful degradation

---

## 🔧 Prompt Improvement Strategy

### Current Issues

1. **Intent Mismatch:**
   - Code has: CLASSIFY, EXTRACT, RECOMMEND
   - Prompts have: PRICE_ANALYSIS, INVESTMENT_ADVICE, LOCATION_INSIGHTS
   - **Action:** Sync code with prompts (use prompts.py definitions)

2. **Prompt Quality:**
   - prompts.py has excellent Vietnamese real estate context
   - main.py has basic English prompts
   - **Action:** Replace main.py prompts with prompts.py

3. **Few-Shot Examples:**
   - prompts.py has 6 excellent examples
   - main.py has zero
   - **Action:** Import few-shot examples to improve accuracy

### Improvement Plan

#### Step 1: Sync Intent Types
```python
# Update shared/models/orchestrator.py
class IntentType(str, Enum):
    SEARCH = "search"
    COMPARE = "compare"
    PRICE_ANALYSIS = "price_analysis"      # NEW
    INVESTMENT_ADVICE = "investment_advice" # NEW
    LOCATION_INSIGHTS = "location_insights" # NEW
    LEGAL_GUIDANCE = "legal_guidance"       # NEW
    CHAT = "chat"
    UNKNOWN = "unknown"
    # REMOVE: classify, extract, recommend
```

#### Step 2: Replace Prompt in main.py
```python
# OLD (main.py line 48-73)
self.intent_prompt = ChatPromptTemplate.from_messages([...])

# NEW (use prompts.py)
from .prompts import get_intent_detection_prompt
self.intent_prompt = get_intent_detection_prompt()
```

#### Step 3: Add Few-Shot Learning
```python
# Add to intent detection
from .prompts import OrchestratorPrompts

examples_text = OrchestratorPrompts.get_few_shot_examples_text()

# Include in prompt
prompt = self.intent_prompt.format(
    query=query,
    examples=examples_text  # NEW
)
```

#### Step 4: Improve Routing Logic
```python
# Expand _decide_routing() with all 8 intents
def _decide_routing(self, intent_result: IntentDetectionResult):
    routing_map = {
        IntentType.SEARCH: ("rag_service", "/rag", True),
        IntentType.COMPARE: ("rag_service", "/compare", True),
        IntentType.PRICE_ANALYSIS: ("price_suggestion", "/analyze", False),
        IntentType.INVESTMENT_ADVICE: ("rag_service", "/investment", True),
        IntentType.LOCATION_INSIGHTS: ("rag_service", "/location", True),
        IntentType.LEGAL_GUIDANCE: ("core_gateway", "/chat/completions", False),
        IntentType.CHAT: ("core_gateway", "/chat/completions", False),
        IntentType.UNKNOWN: ("core_gateway", "/chat/completions", False),
    }

    service, endpoint, use_rag = routing_map.get(intent_result.intent)
    return RoutingDecision(...)
```

---

## 📊 Test Execution Plan

### Phase 1: Unit Tests (Intent Detection)
**Duration:** 2 hours
**Test File:** `tests/test_orchestrator_intents.py`

```python
import pytest
from services.orchestrator.main import Orchestrator

@pytest.mark.asyncio
async def test_search_intent():
    orch = Orchestrator()
    result = await orch._detect_intent("Tìm căn hộ 2PN Q7")

    assert result.intent == IntentType.SEARCH
    assert result.confidence >= 0.8
    assert "bedrooms" in result.extracted_entities
    assert result.extracted_entities["bedrooms"] == 2

# 50+ test cases for all 8 intents
```

### Phase 2: Integration Tests (End-to-End)
**Duration:** 4 hours
**Test File:** `tests/test_business_logic_e2e.py`

```python
@pytest.mark.asyncio
async def test_search_with_real_data():
    """Test SEARCH intent with 13K properties"""

    # Setup: Ensure database has 13K+ properties
    assert get_property_count() >= 10000

    # Execute: Search query
    request = OrchestrationRequest(
        user_id="test_user",
        query="Tìm căn hộ 2 phòng ngủ Quận 7 dưới 3 tỷ"
    )

    response = await orchestrator.orchestrate(request)

    # Verify: Intent detection
    assert response.intent == IntentType.SEARCH
    assert response.confidence >= 0.8

    # Verify: Response quality
    assert "căn hộ" in response.response.lower()
    assert "quận 7" in response.response.lower()

    # Verify: Performance
    assert response.execution_time_ms < 2000
```

### Phase 3: Prompt Optimization
**Duration:** 3 hours
**Method:** A/B Testing

```python
# Test old prompt vs new prompt
old_prompt_accuracy = test_with_prompt(old_prompt, test_cases)
new_prompt_accuracy = test_with_prompt(new_prompt, test_cases)

assert new_prompt_accuracy > old_prompt_accuracy + 0.05  # 5% improvement
```

### Phase 4: Load Testing
**Duration:** 2 hours
**Tool:** Locust

```python
# Simulate 100 concurrent users
# Test all 8 intent types
# Verify response times < 2s at p95
```

---

## 📈 Success Metrics

### Accuracy Metrics
- **Intent Detection:** ≥ 90% accuracy across 8 types
- **Entity Extraction:** ≥ 85% accuracy (F1 score)
- **RAG Relevance:** P@10 ≥ 0.7 (top 10 results relevant)
- **Price Analysis:** Within 10% of market average

### Performance Metrics
- **Response Time:** p95 < 2 seconds
- **Throughput:** 100 req/sec (orchestrator)
- **Availability:** 99.9% uptime

### Business Metrics
- **User Satisfaction:** Positive response to 80% queries
- **Conversation Success:** 85% complete without clarification
- **Coverage:** Handle 95% of real user queries

---

## 🎯 Test Data

### Real Estate Queries Dataset (100 samples)

**SEARCH (25 queries):**
1. "Tìm căn hộ 2 phòng ngủ Quận 7"
2. "Có nhà nào giá rẻ không?"
3. "Find apartments near metro"
4. "Cần mua biệt thự Thủ Đức"
5. "Nhà mặt tiền đường lớn Q1"
... (20 more)

**COMPARE (15 queries):**
1. "So sánh 2 căn hộ Vinhomes"
2. "Căn nào tốt hơn?"
3. "Q2 vs Q7 cho gia đình trẻ"
... (12 more)

**PRICE_ANALYSIS (15 queries):**
1. "Giá 2.5 tỷ cho 70m² Q7 hợp lý không?"
2. "Bao nhiêu tiền mua nhà Q2?"
3. "Is 3 billion too expensive?"
... (12 more)

**INVESTMENT_ADVICE (15 queries):**
1. "Nên đầu tư Q2 hay Q7?"
2. "Căn này có tiềm năng không?"
3. "5 tỷ mua 1 hay 2 căn?"
... (12 more)

**LOCATION_INSIGHTS (10 queries):**
1. "Quận Thủ Đức có gì hay?"
2. "Q7 phát triển thế nào?"
... (8 more)

**LEGAL_GUIDANCE (10 queries):**
1. "Sổ đỏ khác sổ hồng thế nào?"
2. "Thủ tục mua nhà gồm gì?"
... (8 more)

**CHAT (5 queries):**
1. "Xin chào"
2. "Bạn là ai?"
... (3 more)

**UNKNOWN (5 queries):**
1. "asdf qwer"
2. "Tính 2+2"
... (3 more)

---

## 📝 Next Steps

1. ✅ **Sync Intent Types** (main.py ← prompts.py)
2. ✅ **Replace Prompts** (use high-quality Vietnamese prompts)
3. ✅ **Create Test Suite** (100 test cases)
4. ✅ **Run Tests** (Unit → Integration → E2E)
5. ✅ **Measure Metrics** (Accuracy, Performance, Business)
6. ✅ **Generate Report** (Share with CTO)

---

## 📊 Expected Outcomes

After testing and prompt improvements:

- **Intent Accuracy:** 85% → **95%** (+10%)
- **Entity Extraction:** 75% → **90%** (+15%)
- **Response Quality:** 70% → **88%** (+18%)
- **User Satisfaction:** Unknown → **85%+**

**Timeline:** 11 hours total (1.5 days)

**Resources:**
- 13,448 real properties for testing
- CTO prompts with Vietnamese expertise
- LangChain framework for improvements

---

**Status:** 🚧 Ready to Execute
**Next:** Start with Phase 1 - Unit Tests


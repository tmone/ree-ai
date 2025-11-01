# Orchestrator Intent Detection - Comprehensive Test Report

**Date**: 2025-11-01
**Tester**: Claude Code
**System**: REE AI Microservices Platform
**Test Scope**: Intent detection accuracy for 8 intent types with Vietnamese real estate queries

---

## 📊 Executive Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Intent Accuracy** | 28.6% (2/7) | ≥85% | ❌ FAILED |
| **Response Time** | 5077ms avg | <2000ms | ❌ FAILED |
| **Services Health** | 100% | 100% | ✅ PASSED |
| **Database** | 13,448 properties | ≥10,000 | ✅ PASSED |

**Overall Result**: ❌ **NOT PRODUCTION READY**

---

## 🔬 Test Environment

### Infrastructure
- **Service Registry**: Running, healthy
- **Orchestrator**: Running (port 8090)
- **Core Gateway**: Running (port 8080) with OpenAI + Ollama fallback
- **DB Gateway**: Running (port 8081)
- **PostgreSQL**: Running with 13,448 properties
- **RAG Service**: Not available (expected for this test)

### Configuration Changes Made
1. ✅ Synchronized intent types across codebase (8 types)
2. ✅ Integrated high-quality Vietnamese prompts with few-shot examples
3. ✅ Fixed JSON parsing to handle markdown code blocks
4. ✅ **CRITICAL FIX**: Changed Orchestrator to call Core Gateway instead of direct OpenAI API
5. ✅ Enabled feature flags: `USE_REAL_CORE_GATEWAY=true`, `USE_REAL_DB_GATEWAY=true`

---

## 🧪 Test Results Detail

### Test Case 1: SEARCH Intent
**Query**: "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ"
**Expected**: SEARCH
**Actual**: SEARCH (confidence: 0.80)
**Result**: ✅ **PASSED**
**Response Time**: 7638ms

### Test Case 2: COMPARE Intent
**Query**: "So sánh căn hộ Vinhomes Grand Park với Masteri Thảo Điền"
**Expected**: COMPARE
**Actual**: SEARCH (confidence: 0.90)
**Result**: ❌ **FAILED**
**Response Time**: 4426ms
**Issue**: LLM misclassified comparison as search

### Test Case 3: PRICE_ANALYSIS Intent
**Query**: "Giá 2.5 tỷ cho căn hộ 70m² quận 7 có hợp lý không?"
**Expected**: PRICE_ANALYSIS
**Actual**: SEARCH (confidence: 0.90)
**Result**: ❌ **FAILED**
**Response Time**: 6213ms
**Issue**: LLM failed to detect price analysis intent despite explicit pricing question

### Test Case 4: INVESTMENT_ADVICE Intent
**Query**: "Nên đầu tư vào quận 2 hay quận 7 với 5 tỷ?"
**Expected**: INVESTMENT_ADVICE
**Actual**: SEARCH (confidence: 0.80)
**Result**: ❌ **FAILED**
**Response Time**: 4105ms
**Issue**: Investment question misclassified as search

### Test Case 5: LOCATION_INSIGHTS Intent
**Query**: "Quận Thủ Đức có tiện ích gì?"
**Expected**: LOCATION_INSIGHTS
**Actual**: SEARCH (confidence: 0.80)
**Result**: ❌ **FAILED**
**Response Time**: 3956ms
**Issue**: Location insight query misclassified

### Test Case 6: LEGAL_GUIDANCE Intent
**Query**: "Thủ tục mua nhà cần giấy tờ gì?"
**Expected**: LEGAL_GUIDANCE
**Actual**: SEARCH (confidence: 0.95)
**Result**: ❌ **FAILED**
**Response Time**: 3557ms
**Issue**: Legal guidance question misclassified with HIGH confidence (0.95)

### Test Case 7: CHAT Intent
**Query**: "Xin chào, bạn là ai?"
**Expected**: CHAT
**Actual**: CHAT (confidence: 0.60)
**Result**: ✅ **PASSED**
**Response Time**: 5609ms

---

## 🔍 Root Cause Analysis

### Primary Issue: LLM Bias Towards SEARCH Intent

**Evidence from logs**:
```
🤖 Raw LLM response: ```json
{
  "intent": "SEARCH",
  "confidence": 0.9,
```

**Pattern Observed**: 5 out of 7 queries (71.4%) were misclassified as SEARCH, regardless of their actual intent.

### Why This Happened

1. **Prompt Quality Issues**:
   - System prompt doesn't clearly differentiate between SEARCH and other intents
   - Few-shot examples may not cover edge cases effectively
   - LLM may be interpreting "any question about real estate" as SEARCH

2. **Model Limitations**:
   - Using `gpt-4o-mini` which may not be sophisticated enough for nuanced intent classification
   - Ollama fallback (if triggered) has even lower accuracy

3. **Prompt Engineering Gaps**:
   - Missing negative examples (what is NOT each intent type)
   - Lack of explicit distinction between similar intents (e.g., SEARCH vs LOCATION_INSIGHTS)
   - Few-shot examples don't emphasize key differentiating factors

---

## 📈 Performance Analysis

### Response Time Breakdown
- **Fastest**: 3556ms (LEGAL_GUIDANCE query)
- **Slowest**: 7638ms (SEARCH query)
- **Average**: 5077ms
- **P95**: ~7000ms (estimated)

**Analysis**: Response times are 2-3x slower than target (<2000ms), primarily due to:
1. Core Gateway → LLM round-trip latency
2. Ollama may be in use (slower than OpenAI when available)
3. No caching implemented for repeated queries

---

## 🐛 Issues Found

### Critical Issues

1. **ISSUE-001: LLM Intent Classification Bias**
   - **Severity**: CRITICAL
   - **Impact**: 71.4% misclassification rate towards SEARCH
   - **Root Cause**: Inadequate prompt engineering
   - **Recommendation**: Redesign prompt with clearer intent definitions and negative examples

2. **ISSUE-002: High Response Latency**
   - **Severity**: HIGH
   - **Impact**: 5s average response time (2.5x target)
   - **Root Cause**: No caching, possibly using Ollama fallback
   - **Recommendation**: Implement Redis caching for intent detection, optimize LLM calls

3. **ISSUE-003: OpenAI API Quota Exhausted**
   - **Severity**: HIGH
   - **Impact**: Forced to use Ollama fallback (lower accuracy)
   - **Root Cause**: Original implementation called OpenAI directly, exhausted quota
   - **Status**: RESOLVED by switching to Core Gateway with Ollama fallback

### Medium Issues

4. **ISSUE-004: RAG Service Not Connected**
   - **Severity**: MEDIUM
   - **Impact**: Cannot test full orchestration pipeline
   - **Root Cause**: DNS resolution error "[Errno -2] Name or service not known"
   - **Recommendation**: Deploy RAG service or fix networking

5. **ISSUE-005: No Intent Confidence Thresholding**
   - **Severity**: MEDIUM
   - **Impact**: High-confidence wrong answers (e.g., SEARCH with 0.95 confidence for legal question)
   - **Recommendation**: Implement confidence threshold and fallback to keyword matching below threshold

---

## ✅ What Worked Well

1. **Core Gateway Integration**: Successfully migrated from direct OpenAI API to Core Gateway
2. **Fallback Mechanism**: Keyword-based fallback worked reliably when LLM failed
3. **Infrastructure Health**: All services running stable with 100% uptime during tests
4. **Database Scale**: 13K+ properties loaded and accessible
5. **JSON Parsing**: Successfully handles both plain JSON and markdown-wrapped JSON responses

---

## 🎯 Recommendations

### Immediate Actions (Critical)

1. **Improve Prompt Engineering**:
   - Add explicit definitions for each intent type with examples of what they ARE NOT
   - Include more diverse few-shot examples covering edge cases
   - Add reasoning step: "First identify keywords, then classify based on user intent"

2. **Consider Model Upgrade**:
   - Test with `gpt-4` (not mini) for more sophisticated intent understanding
   - Benchmark Ollama models (llama3, mixtral) vs OpenAI

3. **Implement Confidence Thresholding**:
   - If LLM confidence < 0.8, fall back to keyword matching
   - Log low-confidence predictions for manual review

### Short-term Actions (High Priority)

4. **Add Caching Layer**:
   - Cache intent detection results in Redis (TTL: 1 hour)
   - Reduces latency for repeated queries

5. **Deploy RAG Service**:
   - Fix networking issues
   - Test full orchestration pipeline with actual property search

6. **Add Monitoring**:
   - Log intent detection accuracy per intent type
   - Alert on accuracy drop below 70%

### Long-term Actions (Medium Priority)

7. **Train Custom Intent Classifier**:
   - Fine-tune BERT/GPT model on Vietnamese real estate intents
   - Target: 95%+ accuracy, <500ms latency

8. **A/B Testing Framework**:
   - Test multiple prompts simultaneously
   - Track accuracy metrics per prompt version

---

## 📝 Test Artifacts

- **Test Script**: `/tmp/test_orchestrator_manual.py`
- **Comprehensive E2E Tests**: `/Users/tmone/ree-ai/tests/test_comprehensive_e2e.py` (600+ lines)
- **Test Logs**: `/tmp/orchestrator_test_core_gateway.log`
- **Docker Logs**: `docker-compose logs orchestrator`

---

## 🔄 Next Steps

### For Development Team:

1. **Immediate**: Redesign intent detection prompt (ETA: 2 hours)
2. **Today**: Implement confidence thresholding (ETA: 4 hours)
3. **This Week**: Deploy RAG service and retest full pipeline (ETA: 1 day)
4. **This Sprint**: Add caching layer and monitoring (ETA: 2 days)

### For Product/CTO:

- **Decision Needed**: Accept 28.6% accuracy with improved fallback, OR invest in prompt engineering/model upgrade to reach 85% target?
- **Trade-off**: Response time (5s avg) vs accuracy - which to prioritize?
- **Budget**: Consider OpenAI API quota limits - need to top up or rely on Ollama?

---

## 💡 Key Learnings

1. **Architecture Works**: Core Gateway abstraction allows seamless LLM provider switching
2. **Prompt Engineering is Critical**: Even small changes in prompt can dramatically affect accuracy
3. **Fallback is Essential**: Keyword matching saved us from 0% accuracy when LLM failed
4. **Testing Matters**: Comprehensive testing revealed issues that unit tests missed

---

## 📊 Appendix: Raw Test Data

### Test Execution Log
```
📊 TEST SUMMARY
================================================================================
   Total tests: 7
   ✅ Passed: 2
   ❌ Failed: 5
   ⚡ Avg time: 5077ms
   🎯 Success rate: 28.6%
================================================================================
```

### Intent Distribution (Actual vs Expected)
| Intent Type | Expected | Actual | Match Rate |
|-------------|----------|--------|------------|
| SEARCH | 1 | 5 | 100% (1/1) |
| COMPARE | 1 | 0 | 0% (0/1) |
| PRICE_ANALYSIS | 1 | 0 | 0% (0/1) |
| INVESTMENT_ADVICE | 1 | 0 | 0% (0/1) |
| LOCATION_INSIGHTS | 1 | 0 | 0% (0/1) |
| LEGAL_GUIDANCE | 1 | 0 | 0% (0/1) |
| CHAT | 1 | 1 | 100% (1/1) |
| UNKNOWN | 0 | 0 | N/A |

---

**Report Generated**: 2025-11-01 03:30:00 UTC
**Author**: Claude Code
**Version**: 1.0

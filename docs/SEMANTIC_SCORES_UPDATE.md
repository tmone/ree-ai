# Semantic Scores from OpenSearch - Implementation Update

## 📊 Overview

Updated orchestrator to use **semantic scores from OpenSearch** instead of rule-based match scores for property ranking in clarification responses.

**Date**: 2025-11-01
**Status**: ✅ Implemented & Testing

---

## 🎯 What Changed

### Before (Rule-Based Scoring)

```python
# Orchestrator calculated scores based on hard-coded rules
def _calculate_match_score(self, prop: Dict, requirements: Dict) -> int:
    score = 0
    if district_matches: score += 40
    if bedrooms_match: score += 30
    if type_matches: score += 15
    if price_ok: score += 15
    return score
```

**Problems:**
- ❌ Ignores semantic similarity from OpenSearch
- ❌ Rules can't capture nuanced meanings
- ❌ Doesn't reflect actual search relevance

### After (Semantic Scoring)

```python
# Use OpenSearch's vector similarity scores
if results_have_semantic_scores:
    max_score = max(prop.get("score") for prop in results)
    for prop in results:
        semantic_score = prop.get("score")
        normalized_score = int((semantic_score / max_score) * 100)
        scored_results.append({"property": prop, "score": normalized_score})
else:
    # Fallback to rule-based scoring if no semantic scores
    for prop in results:
        score = self._calculate_match_score(prop, requirements)
        scored_results.append({"property": prop, "score": score})
```

**Benefits:**
- ✅ Uses actual vector similarity from OpenSearch
- ✅ Reflects semantic understanding of query
- ✅ Automatically improves as embedding model improves
- ✅ Fallback to rules if semantic scores unavailable

---

## 🔧 Technical Implementation

### 1. DB Gateway Already Returns Scores

**File**: `/Users/tmone/ree-ai/services/db_gateway/main.py:419`

```python
results.append(PropertyResult(
    property_id=source.get('property_id', hit['_id']),
    title=source.get('title', ''),
    price=source.get('price', 0),
    # ... other fields ...
    score=float(hit['_score'])  # ← OpenSearch's relevance score
))
```

OpenSearch vector search returns `_score` field which represents cosine similarity or k-NN distance.

---

### 2. Orchestrator Normalization

**File**: `/Users/tmone/ree-ai/services/orchestrator/main.py:919-928`

```python
# Check if results have semantic scores from OpenSearch
has_semantic_scores = any(isinstance(prop.get("score"), (int, float)) for prop in results)

if has_semantic_scores:
    # Use semantic scores from OpenSearch and normalize to 0-100
    max_score = max((prop.get("score", 0) for prop in results), default=1.0)
    self.logger.info(f"{LogEmoji.INFO} Using OpenSearch semantic scores (max: {max_score:.2f})")

    for prop in results:
        semantic_score = prop.get("score", 0)
        # Normalize to 0-100 range based on max score in this batch
        normalized_score = int((semantic_score / max_score) * 100) if max_score > 0 else 0
        scored_results.append({"property": prop, "score": normalized_score, "type": "semantic"})
```

**Normalization Strategy:**
- Find max score in current batch
- Normalize all scores: `(score / max_score) * 100`
- Convert to integer for display: "Điểm: 85/100"
- Top result always gets 100 points

**Why Normalize?**
- OpenSearch scores are floats (e.g., 0.8537, 12.45)
- Users understand percentages (0-100) better
- Consistent with existing UI expectations

---

### 3. Best Results Tracking Fix

**File**: `/Users/tmone/ree-ai/services/orchestrator/main.py:361-377`

**Problem:** Previously, orchestrator only kept `last_results` from final iteration. If iteration 1 found 5 results but iteration 2 found 0, clarification got 0 results.

**Solution:** Track `best_results` across all iterations.

```python
best_results = []  # Keep track of BEST results across iterations
best_evaluation = None

for iteration in range(max_iterations):
    results = await self._execute_search_internal(current_query)
    evaluation = await self._evaluate_results(results, requirements)

    # Keep track of best results (prefer more results if quality is similar)
    if (not best_results and results) or (results and len(results) > len(best_results)):
        best_results = results
        best_evaluation = evaluation
        self.logger.info(f"{LogEmoji.INFO} Updated best_results: {len(best_results)} properties")

    # ... evaluation and iteration logic ...

    # Use best results from all iterations, not just last one
    return await self._ask_clarification(requirements, best_evaluation or evaluation, best_results)
```

**Benefit:** Clarification always shows best available alternatives, even if later refinement fails.

---

## 📋 Example Output

### Query
"Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế"

### Response with Semantic Scores

```
Tôi tìm thấy **150 căn hộ** ở TP.HCM, nhưng **không có căn nào ở quận 2**.

**Bạn muốn tôi:**
- 🔍 Tìm thêm ở **các quận lân cận** (Quận 9, Thủ Đức, Bình Thạnh)
- 🌍 Mở rộng tìm kiếm **toàn TP.HCM**
- 📍 Cung cấp thông tin cụ thể hơn về "gần trường quốc tế"
- 🛏️ Điều chỉnh số phòng ngủ (3 ± 1 phòng)

**Dưới đây là 5 BĐS gần nhất có thể phù hợp:**

1. 🟢 **Căn hộ The Sun Avenue 3PN** (Điểm: 100/100)  ← Normalized semantic score
   💰 Giá: 4.5 tỷ | 📐 90m² | 🛏️ 3 PN
   📍 Bình Thạnh

2. 🟡 **Căn hộ Masteri Thảo Điền** (Điểm: 87/100)
   💰 Giá: 5.2 tỷ | 📐 85m² | 🛏️ 3 PN
   📍 Quận 2

3. 🟡 **Căn hộ Vista Verde 3PN** (Điểm: 73/100)
   💰 Giá: 4.8 tỷ | 📐 88m² | 🛏️ 3 PN
   📍 Thủ Đức

4. 🟡 **Căn hộ Gateway Thảo Điền** (Điểm: 65/100)
   💰 Giá: 6.0 tỷ | 📐 95m² | 🛏️ 3 PN
   📍 Quận 2

5. 🔴 **Căn hộ Palm Heights** (Điểm: 42/100)
   💰 Giá: 5.5 tỷ | 📐 82m² | 🛏️ 2 PN
   📍 Quận 2

💬 Bạn muốn tôi hỗ trợ như thế nào?
```

---

## 🔍 Logs Analysis

### Success Case (Semantic Scores)

```
2025-11-01 12:28:14,185 - orchestrator - INFO - ✅ [ReAct-Act] Found 5 results
2025-11-01 12:28:14,185 - orchestrator - INFO - ℹ️ Updated best_results: 5 properties
2025-11-01 12:28:23,858 - orchestrator - INFO - ℹ️ Using OpenSearch semantic scores (max: 12.45)
```

- Iteration 1: Found 5 results with semantic scores
- Max score: 12.45 (OpenSearch k-NN score)
- Normalized to 0-100 range

### Fallback Case (Rule-Based)

```
2025-11-01 12:28:23,858 - orchestrator - INFO - ℹ️ Using rule-based match scores (no semantic scores found)
```

- No semantic scores in results
- Falls back to `_calculate_match_score()` method

---

## 🎯 Why Semantic Scores Matter

### 1. **Query Understanding**

**Query:** "Tìm căn hộ gần trường quốc tế"

**Semantic Search (OpenSearch):**
- Understands "gần trường quốc tế" = proximity to international schools
- Finds properties mentioning: "British International School", "Australian International School"
- Even if exact phrase "trường quốc tế" not in listing

**Rule-Based:**
- Can only match exact keywords
- Misses semantic relationships

---

### 2. **Ranking Quality**

**OpenSearch Semantic Scores:**
- Based on vector similarity (embeddings)
- Considers:
  - Semantic meaning of query
  - Context of entire listing
  - Relationships between terms

**Rule-Based Scores:**
- Fixed weights: District 40%, Bedrooms 30%, Type 15%, Price 15%
- Doesn't adapt to different query types
- Misses nuanced preferences

---

### 3. **User Intent Matching**

**Example:**

Query: "Căn hộ view đẹp yên tĩnh"

**Semantic Scores** will rank higher:
- "Căn hộ view sông Sài Gòn, thoáng mát" (Score: 95/100)
- "Căn hộ hướng công viên, không ồn" (Score: 88/100)

**Rule-Based** would ignore "view đẹp yên tĩnh" entirely because it's not a structured field (district, bedrooms, etc).

---

## 📊 Performance Considerations

### Normalization Overhead
- **Impact**: Minimal (O(n) where n = number of results)
- **Typical n**: 5-10 properties
- **Time**: < 1ms

### Memory
- **Additional data**: One float per property (`score` field)
- **Impact**: Negligible (5 properties × 8 bytes = 40 bytes)

### Accuracy Trade-off
- **Semantic scores**: Reflect actual search relevance
- **Rule-based scores**: Consistent but less accurate
- **Recommendation**: Use semantic when available

---

## 🚀 Testing

### Test Script

```bash
python3 test_semantic_scores.py
```

**Expected Output:**
```
✅ Found 5 properties with scores: [100, 87, 73, 65, 42]
✅ All scores are in 0-100 range (normalized)
✅ Scores are sorted descending (best first)

📊 Score Statistics:
  - Maximum: 100/100
  - Minimum: 42/100
  - Average: 73.4/100
  - Range: 58 points

✅ SUCCESS: Semantic scores are being used!
```

---

## 🔮 Future Improvements

### 1. Hybrid Scoring

Combine semantic + rule-based:

```python
final_score = (semantic_score * 0.7) + (rule_based_score * 0.3)
```

**Benefits:**
- Semantic for query understanding
- Rule-based for hard requirements (e.g., budget)

### 2. Score Calibration

Instead of relative normalization (max = 100), use absolute thresholds:

```python
# Calibrate based on typical score ranges
if semantic_score > 10.0:  # Excellent
    normalized_score = 90 + (semantic_score - 10) * 2
elif semantic_score > 5.0:  # Good
    normalized_score = 70 + (semantic_score - 5) * 4
else:  # Poor
    normalized_score = semantic_score * 14
```

### 3. User Feedback Learning

Collect user clicks/selections to refine scoring:

```python
# If user consistently selects properties with score < 70
# Adjust normalization to show more diversity
```

---

## ✅ Production Readiness

- [x] Semantic scores from OpenSearch
- [x] Normalization to 0-100 range
- [x] Logging for debugging
- [x] Fallback to rule-based scoring
- [x] Best results tracking across iterations
- [x] Visual indicators (🟢🟡🔴)
- [ ] Hybrid scoring (TODO)
- [ ] Score calibration (TODO)
- [ ] User feedback integration (TODO)

---

## 📚 Related Files

- **Orchestrator**: `/Users/tmone/ree-ai/services/orchestrator/main.py`
- **DB Gateway**: `/Users/tmone/ree-ai/services/db_gateway/main.py`
- **Models**: `/Users/tmone/ree-ai/shared/models/db_gateway.py`
- **Test Script**: `/Users/tmone/ree-ai/test_semantic_scores.py`
- **V2 Documentation**: `/Users/tmone/ree-ai/docs/REACT_CLARIFICATION_V2_IMPROVED.md`

---

**Last Updated**: 2025-11-01
**Implementation Status**: ✅ Complete & Testing
**Next Step**: Verify semantic scores display correctly in production

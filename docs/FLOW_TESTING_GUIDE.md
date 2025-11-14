# Flow Testing Guide - Comprehensive Architecture Validation

## Overview

This guide explains how to test all major flows in REE AI based on the architecture diagrams in `docs/diagrams/`.

## Flows Covered

### ✅ Case 1: Property Posting (POST_SALE/POST_RENT)
- **Diagram**: `docs/diagrams/case1_property_posting.drawio`
- **Key Feature**: Internal reasoning loop (1-5 iterations)
- **Services**: Classification, Extraction, Completeness
- **Exit Conditions**: Score >= 80, Max 5 iterations, No improvement

### ✅ Case 2: Property Search (SEARCH_BUY/SEARCH_RENT)
- **Diagram**: `docs/diagrams/case2_property_search.drawio`
- **Key Feature**: ReAct reasoning loop (max 2 iterations)
- **Services**: Classification, Extraction, DB Gateway → OpenSearch
- **Progressive Relaxation**: Location only → Semantic fallback → Graceful failure

### ❌ Case 3: Price Consultation (NOT IMPLEMENTED)
- **Status**: Planned but not yet implemented
- **Skip testing** until implementation is complete

### ✅ Case 4: General Chat (CHAT)
- **Diagram**: `docs/diagrams/case4_general_chat.drawio`
- **Key Feature**: No loop, simple direct LLM response
- **Services**: Classification, Core Gateway
- **Multimodal**: Supports both text and image inputs

---

## Prerequisites

### 1. Start All Services

```bash
# Start all real services
docker-compose --profile real up -d

# Wait for services to be healthy (30 seconds)
sleep 30

# Verify services are running
curl http://localhost:8000/health  # Service Registry
curl http://localhost:8090/health  # Orchestrator
curl http://localhost:8083/health  # Classification
curl http://localhost:8084/health  # Extraction
curl http://localhost:8086/health  # Completeness
curl http://localhost:8081/health  # DB Gateway
```

### 2. Verify Database

```bash
# Test PostgreSQL connection
docker exec -it ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT COUNT(*) FROM ree_common.countries;"

# Test OpenSearch connection
curl http://localhost:9200/_cat/indices?v
```

---

## Running Tests

### Option 1: Run with Docker (Recommended)

```bash
# Run comprehensive flow tests
docker run --rm --network host \
  -v "$(pwd):/app" -w /app \
  python:3.11-slim bash -c "pip install -q asyncpg httpx && python tests/test_flow_comprehensive.py"
```

### Option 2: Run Locally (if Python installed)

```bash
# Install dependencies
pip install asyncpg httpx

# Run tests
python tests/test_flow_comprehensive.py
```

### Option 3: Use Test Script

```bash
# Linux/Mac
./scripts/test-flows.sh

# Windows
scripts\test-flows.bat
```

---

## Test Coverage

### Case 1: Property Posting Tests

| Test | Input | Expected Behavior |
|------|-------|-------------------|
| **Minimal Info** | "Can ban nha Q7 2PN" | Loop 1-5 times, score < 80, request missing info (price, area, address) |
| **Complete Info** | "Can ban nha mat tien Nguyen Huu Tho, Q7, 2PN, 80m2, 5.5ty, co san vuon" | Loop exits early (score >= 80), confirmation response |

**Key Validations**:
- ✅ Intent detection: POST_SALE
- ✅ Reasoning loop iterations: 1-5
- ✅ Completeness score calculation
- ✅ Exit conditions: score >= 80 OR max iterations
- ✅ Response asks for missing fields

---

### Case 2: Property Search Tests

| Test | Input | Expected Behavior |
|------|-------|-------------------|
| **Strict Criteria** | "Tim can ho 3PN, Q2, 6-7ty, view song, co ho boi" | ReAct loop max 2 iterations, may apply progressive relaxation |
| **Location Only** | "Tim can ho o Quan 7" | Quick results (1-2 iterations), quality >= 0.7 |

**Key Validations**:
- ✅ Intent detection: SEARCH_BUY/SEARCH_RENT
- ✅ ReAct loop iterations: 1-2
- ✅ Quality score >= 0.7
- ✅ Progressive relaxation when no results
- ✅ OpenSearch integration
- ✅ Result count > 0

---

### Case 4: General Chat Tests

| Test | Input | Expected Behavior |
|------|-------|-------------------|
| **Greeting** | "Xin chao! Ban la ai?" | No loop, direct LLM response, friendly greeting |
| **Domain Question** | "Thu tuc mua nha o VN can giay to gi?" | No loop, informative response about procedures |

**Key Validations**:
- ✅ Intent detection: CHAT
- ✅ No reasoning loop (simple flow)
- ✅ LLM integration (GPT-4o-mini for text)
- ✅ Response length > 10 characters
- ✅ History saved to PostgreSQL

---

## Understanding Test Results

### Success Criteria

A test **PASSES** if:
1. ✅ Correct intent detected
2. ✅ Flow logic works (loops, exit conditions)
3. ✅ Services respond correctly
4. ✅ Response format is valid
5. ✅ Performance is acceptable (< 60s for Case 1/2, < 30s for Case 4)

### Sample Output

```
==================================================================================================
🧪 COMPREHENSIVE FLOW TESTING - Based on Architecture Diagrams
==================================================================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 CASE 1: Property Posting
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

▶ Running: Case 1: Property Posting - Minimal information...
  ✅ PASSED (3245ms)
    query: Can ban nha Q7 2PN
    intent: POST_SALE
    completeness_score: 45
    iterations: 3
    response_preview: Cảm ơn bạn! Tôi đã hiểu bạn muốn bán nhà tại Quận 7, 2 phòng ngủ. Để đăng tin chính xác hơn, bạn có thể bổ sung: - Giá bán mong muốn - Diện tích (m²) - Địa chỉ c...

▶ Running: Case 1: Property Posting - Complete information...
  ✅ PASSED (2156ms)
    query: Can ban nha mat tien duong Nguyen Huu Tho, Quan 7, 2 phong ngu, 80m2, gia 5.5 ty, co san vuon 20m2
    intent: POST_SALE
    completeness_score: 85
    iterations: 1
    response_preview: Đã nhận thông tin hoàn chỉnh! Nhà mặt tiền đường Nguyễn Hữu Thọ, Quận 7: - 2 phòng ngủ - 80m² - Giá 5.5 tỷ - Sân vườn 20m² Tin đăng của bạn đã sẵn sàng...

==================================================================================================
📊 TEST SUMMARY
==================================================================================================
Total Tests: 6
✅ Passed: 6 (100.0%)
❌ Failed: 0 (0.0%)

📁 Results saved: flow_test_results_20251114_080000.json
```

---

## Troubleshooting

### Services Not Running

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f orchestrator
docker-compose logs -f classification

# Restart services
docker-compose restart
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker exec -it ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT 1;"

# Check OpenSearch
curl http://localhost:9200
```

### Test Timeouts

If tests timeout:
1. Increase timeout in `test_flow_comprehensive.py`:
   ```python
   async with httpx.AsyncClient(timeout=120.0) as client:  # Increase from 60s
   ```
2. Check service health endpoints
3. Review service logs for errors

---

## Expected Test Duration

| Case | Tests | Expected Duration |
|------|-------|-------------------|
| Case 1 | 2 tests | ~10-15 seconds |
| Case 2 | 2 tests | ~20-30 seconds |
| Case 4 | 2 tests | ~5-10 seconds |
| **Total** | **6 tests** | **~35-55 seconds** |

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Flow Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start services
        run: docker-compose --profile real up -d
      - name: Wait for services
        run: sleep 30
      - name: Run flow tests
        run: ./scripts/test-flows.sh
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: flow-test-results
          path: flow_test_results_*.json
```

---

## Next Steps

1. ✅ Run comprehensive flow tests
2. ⚠️ Fix any failing tests
3. 📈 Monitor test coverage
4. 🔄 Add more edge case tests
5. 🚀 Integrate with CI/CD pipeline

---

## References

- **Architecture Diagrams**: `docs/diagrams/`
- **Test Suite**: `tests/test_flow_comprehensive.py`
- **Project Structure**: `PROJECT_STRUCTURE.md`
- **Testing Guide**: `TESTING.md`

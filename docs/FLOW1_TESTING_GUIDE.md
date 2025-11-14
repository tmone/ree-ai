# Flow 1: Property Posting - AI Simulator Guide

## 📋 Overview

Flow 1 tests the **Property Posting** flow với AI-generated realistic queries sử dụng Ollama. Test này validate:

1. **Intent Detection**: POST_SALE vs POST_RENT
2. **Reasoning Loop**: 1-5 iterations dựa trên completeness
3. **Completeness Scoring**: Score calculation và exit conditions
4. **Database Persistence**: Conversations và messages saved to PostgreSQL

---

## 🎯 Test Scenarios

### Scenario 1: Seller - Minimal Info (Triggers Loop)
```
Query: "Can ban nha Q7 2PN"
Expected:
  - Intent: POST_SALE ✅
  - Completeness Score: < 80 (low)
  - Iterations: 3-5 (multiple loops)
  - Response: Hỏi thêm thông tin (giá, diện tích, địa chỉ)
  - DB: Conversation + Messages saved
```

### Scenario 2: Seller - Complete Info (Early Exit)
```
Query: "Can ban nha mat tien duong Nguyen Huu Tho, Quan 7, 2 phong ngu,
       80m2, gia 5.5 ty, co san vuon 20m2, phap ly day du"
Expected:
  - Intent: POST_SALE ✅
  - Completeness Score: >= 80 (high)
  - Iterations: 1-2 (early exit)
  - Response: Xác nhận thông tin đã đủ
  - DB: Conversation + Messages saved
```

### Scenario 3: Seller - Partial Info
```
Query: "Can ban can ho 2PN o quan 7, gia khoang 5 ty"
Expected:
  - Intent: POST_SALE ✅
  - Completeness Score: 50-70 (medium)
  - Iterations: 2-3 (moderate)
  - Response: Hỏi thêm 1-2 thông tin (diện tích, địa chỉ cụ thể)
```

### Scenario 4: Landlord - Minimal Info
```
Query: "Cho thue can ho quan 2 2PN"
Expected:
  - Intent: POST_RENT ✅
  - Completeness Score: < 80
  - Iterations: 3-5
  - Response: Hỏi giá thuê, diện tích, nội thất
```

### Scenario 5: Landlord - Complete Info
```
Query: "Cho thue can ho The Sun Avenue, Quan 2, 2PN 2WC, 70m2,
       full noi that, gia 12 trieu/thang, view dep"
Expected:
  - Intent: POST_RENT ✅
  - Completeness Score: >= 80
  - Iterations: 1-2
  - Response: Xác nhận sẵn sàng đăng tin
```

---

## 🔄 Flow Diagram

```
User Query → Orchestrator
                ↓
         Classification Service (Intent: POST_SALE/POST_RENT)
                ↓
         ┌─────────────────────────────────────┐
         │  INTERNAL REASONING LOOP            │
         │  (Within single request)            │
         │                                     │
         │  Step 1: Extract Attributes         │
         │    ↓                                │
         │  Step 2: Assess Completeness        │
         │    ↓                                │
         │  Decision: Score >= 80 OR max iter? │
         │    ├─ NO → Continue Loop            │
         │    └─ YES → Exit Loop               │
         └─────────────────────────────────────┘
                ↓
         Generate Response
                ↓
         Save to PostgreSQL
                ↓
         Return to User
```

---

## 💾 Database Schema

### Table: `ree_common.conversations`

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT | Auto-increment primary key |
| `conversation_id` | VARCHAR(255) | Unique conversation ID |
| `user_id` | VARCHAR(255) | User identifier |
| `created_at` | TIMESTAMP | Conversation start time |
| `updated_at` | TIMESTAMP | Last message time |

### Table: `ree_common.messages`

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGINT | Auto-increment primary key |
| `message_id` | VARCHAR(255) | Unique message ID |
| `conversation_id` | VARCHAR(255) | FK to conversations |
| `role` | VARCHAR(50) | "user" or "assistant" |
| `content` | TEXT | Message content |
| `created_at` | TIMESTAMP | Message timestamp |
| `metadata` | JSONB | Additional data (intent, score, iterations) |

---

## 🚀 How to Run

### Step 1: Start Services

```bash
# Start Docker Desktop first!

# Start all services
cd /d/Crastonic/ree-ai
docker-compose --profile real up -d

# Wait for services to be healthy
timeout /t 30 /nobreak

# Verify services
curl http://localhost:8000/health  # Service Registry
curl http://localhost:8090/health  # Orchestrator ✅ CRITICAL
curl http://localhost:8083/health  # Classification
curl http://localhost:8084/health  # Extraction
curl http://localhost:8086/health  # Completeness
```

### Step 2: Run AI Simulator

```bash
# Option 1: With Docker (if services running locally)
docker run --rm --network host \
  -v "$(pwd):/app" -w /app \
  python:3.11-slim bash -c "pip install -q asyncpg httpx && python tests/test_flow1_ai_simulator.py"

# Option 2: With local Python (if installed)
pip install asyncpg httpx
python tests/test_flow1_ai_simulator.py
```

---

## 📊 Expected Output

```
====================================================================================================
🤖 FLOW 1: PROPERTY POSTING - AI SIMULATOR
====================================================================================================
Orchestrator: http://localhost:8090
Database: 103.153.74.213:5432/ree_ai
====================================================================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎭 SCENARIO: seller_minimal - SALE (minimal)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 Query: Can ban nha Q7 2PN
🚀 Sending to Orchestrator...

📊 Response Analysis:
  Duration: 3.24s
  Intent: POST_SALE
  Completeness Score: 45
  Iterations: 3
  Response Preview: Cảm ơn bạn! Tôi đã hiểu bạn muốn bán nhà tại Quận 7, 2 phòng ngủ.
                   Để đăng tin chính xác hơn, bạn có thể bổ sung:
                   - Giá bán mong muốn
                   - Diện tích (m²)
                   - Địa chỉ cụ thể (đường, số nhà)...

💾 Checking Database Persistence...
  Conversation Found: ✅
  Messages Saved: 2

  📜 Messages in DB:
    1. [user] Can ban nha Q7 2PN
    2. [assistant] Cảm ơn bạn! Tôi đã hiểu bạn muốn bán nhà tại Quận 7, 2 phòng ngủ...

✅ Validations:
  ✅ correct_intent
  ✅ has_iterations
  ✅ has_response
  ✅ db_saved
  ✅ messages_count_ok
  ✅ score_low_as_expected
  ✅ multiple_iterations

✅ SCENARIO PASSED

[... 4 more scenarios ...]

====================================================================================================
📊 SUMMARY
====================================================================================================

Total Scenarios: 5
✅ Passed: 5 (100.0%)
❌ Failed: 0 (0.0%)

📋 Scenario Results:
  ✅ seller_minimal        | Intent: POST_SALE    | Score:  45 | Iterations: 3
  ✅ seller_complete       | Intent: POST_SALE    | Score:  85 | Iterations: 1
  ✅ seller_partial        | Intent: POST_SALE    | Score:  60 | Iterations: 2
  ✅ landlord_minimal      | Intent: POST_RENT    | Score:  40 | Iterations: 4
  ✅ landlord_complete     | Intent: POST_RENT    | Score:  90 | Iterations: 1

📁 Results saved: flow1_simulation_results_20251114_100000.json
====================================================================================================
```

---

## 🔍 Analyzing Results

### 1. Check JSON Output

```bash
# Open results file
cat flow1_simulation_results_*.json | head -100

# Pretty print
python -m json.tool flow1_simulation_results_*.json
```

Sample JSON structure:
```json
{
  "metadata": {
    "timestamp": "2025-11-14T10:00:00",
    "orchestrator_url": "http://localhost:8090",
    "total_scenarios": 5,
    "passed": 5,
    "failed": 0
  },
  "results": [
    {
      "scenario": "seller_minimal",
      "property_type": "sale",
      "completeness_level": "minimal",
      "query": "Can ban nha Q7 2PN",
      "duration_s": 3.24,
      "response": {
        "intent": "POST_SALE",
        "completeness_score": 45,
        "iterations": 3,
        "response_text": "Cảm ơn bạn! Tôi đã hiểu..."
      },
      "database": {
        "conversation_found": true,
        "message_count": 2,
        "messages": [...]
      },
      "validations": {
        "correct_intent": true,
        "score_low_as_expected": true,
        "multiple_iterations": true,
        ...
      },
      "all_passed": true
    }
  ]
}
```

### 2. Query Database Directly

```sql
-- Check recent conversations
SELECT conversation_id, user_id, created_at
FROM ree_common.conversations
WHERE user_id LIKE 'ai_sim_%'
ORDER BY created_at DESC
LIMIT 10;

-- Check messages for a conversation
SELECT role, content, created_at
FROM ree_common.messages
WHERE conversation_id = 'conv_sale_1699999999'
ORDER BY created_at ASC;

-- Check metadata (if stored)
SELECT
    c.conversation_id,
    c.user_id,
    m.metadata->>'intent' as intent,
    m.metadata->>'completeness_score' as score,
    m.metadata->>'iterations' as iterations
FROM ree_common.conversations c
JOIN ree_common.messages m ON c.conversation_id = m.conversation_id
WHERE c.user_id LIKE 'ai_sim_%'
  AND m.role = 'assistant'
ORDER BY c.created_at DESC;
```

---

## ✅ Success Criteria

A test scenario **PASSES** if all validations succeed:

### Minimal Info Scenarios
- ✅ Correct intent detected (POST_SALE or POST_RENT)
- ✅ Completeness score < 80
- ✅ Multiple iterations (> 1)
- ✅ Response asks for missing information
- ✅ Conversation saved to database
- ✅ At least 2 messages saved (user + assistant)

### Complete Info Scenarios
- ✅ Correct intent detected
- ✅ Completeness score >= 70
- ✅ Quick exit (<= 3 iterations)
- ✅ Response confirms understanding
- ✅ Database persistence working

---

## 🐛 Troubleshooting

### Issue 1: Orchestrator Not Responding

```bash
# Check if Orchestrator is running
curl http://localhost:8090/health

# If not, check Docker
docker-compose ps

# View logs
docker-compose logs -f orchestrator

# Restart
docker-compose restart orchestrator
```

### Issue 2: Database Connection Failed

```bash
# Test PostgreSQL connection
docker exec -it ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "SELECT 1;"

# Check if tables exist
docker exec -it ree-ai-postgres psql -U ree_ai_user -d ree_ai -c "\dt ree_common.*"
```

### Issue 3: Wrong Intent Detected

**Possible causes**:
- Classification service not working
- LLM model not accurate enough
- Query too ambiguous

**Solutions**:
1. Check Classification service logs: `docker-compose logs classification`
2. Try more explicit queries: "Tôi muốn ĐĂNG TIN BÁN nhà..."
3. Verify Core Gateway is working: `curl http://localhost:8080/health`

### Issue 4: Low Completeness Score Not Improving

**Expected behavior**: With minimal info, system should loop 3-5 times

**If not looping**:
1. Check Completeness service: `docker-compose logs completeness`
2. Verify loop logic in Orchestrator
3. Check max iterations setting (should be 5)

---

## 📈 Performance Expectations

| Scenario | Expected Duration | Iterations | Completeness Score |
|----------|-------------------|------------|-------------------|
| Minimal Info | 3-5s | 3-5 | 30-60 |
| Partial Info | 2-4s | 2-3 | 50-70 |
| Complete Info | 1-3s | 1-2 | 70-95 |

**Note**: First request may be slower due to cold start (~10s).

---

## 🔄 Next Steps

After running Flow 1 tests:

1. ✅ **Validate all scenarios passed**
2. 📊 **Analyze completeness score patterns**
3. 🔍 **Inspect database data structure**
4. 📈 **Monitor performance metrics**
5. 🚀 **Proceed to Flow 2 (Property Search)**

---

## 📚 Related Files

| File | Purpose |
|------|---------|
| `tests/test_flow1_ai_simulator.py` | AI simulator implementation |
| `docs/diagrams/case1_property_posting.drawio` | Flow architecture diagram |
| `docs/FLOW_TESTING_GUIDE.md` | General flow testing guide |
| `scripts/test-flows.sh` | Run all flow tests |

---

## ✨ Summary

Flow 1 AI Simulator tests the complete Property Posting flow với:
- **5 realistic scenarios** (minimal, partial, complete info)
- **2 property types** (sale, rent)
- **Reasoning loop validation** (1-5 iterations)
- **Database persistence verification** (PostgreSQL)
- **Comprehensive reporting** (JSON + console output)

**Ready to run**: Start services → Run simulator → Analyze results! 🚀

---

Generated: 2025-11-14
Version: 1.0
Status: ✅ Ready to Test

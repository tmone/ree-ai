# How to Test ReAct Agent Yourself

This guide shows you 3 ways to test the ReAct Agent implementation.

---

## ✅ Prerequisites

Make sure orchestrator is running:
```bash
docker ps | grep orchestrator
```

Should see:
```
ree-ai-orchestrator   Up X minutes   0.0.0.0:8090->8080/tcp
```

If not running:
```bash
docker-compose up -d orchestrator
```

---

## 🎯 Method 1: Quick Test (Fastest - Recommended)

### Step 1: Run Quick Test

```bash
python3 test_react_manual.py --quick
```

**What You'll See:**
```
╔═══════════════════════════════════════════════════════════════════════════╗
║                         QUICK TEST MODE                                   ║
║  Testing the problematic query that user discovered                       ║
╚═══════════════════════════════════════════════════════════════════════════╝

🧪 TESTING QUERY
📝 Query: Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế

✅ RESPONSE RECEIVED
🎯 Intent: search
📚 Context Messages: 0

💬 SYSTEM RESPONSE:
Tôi không tìm thấy đủ bất động sản phù hợp với yêu cầu của bạn.

Tìm được 5 BDS, nhưng chỉ 0 BDS phù hợp (0%).

**Vấn đề:**
- Không đủ BDS ở quận 2
- Không đủ BDS có 3 phòng ngủ
- Thiếu: gần trường quốc tế

**Để tôi hỗ trợ tốt hơn, bạn có thể:**
- Cung cấp thêm thông tin cụ thể về "gần trường quốc tế"...
```

✅ **This is CORRECT!** System is being honest about result quality.

---

### Step 2: View ReAct Logs (See What's Happening Inside)

**In another terminal**, run:
```bash
./watch_react_logs.sh
```

Or manually:
```bash
docker logs ree-ai-orchestrator --tail 100 -f
```

**What to Look For:**
```
🤖 [ReAct Agent] Starting search with query: 'Tìm căn hộ 3 phòng ngủ...'
🤖 [ReAct-Reasoning] Analyzing query requirements...
✅ [ReAct-Reasoning] Requirements: {
    'property_type': 'căn hộ',
    'bedrooms': 3,
    'district': 'quận 2',
    'city': 'TP.HCM',
    'special_requirements': ['gần trường quốc tế']
}
ℹ️ [ReAct Agent] Iteration 1/2
🤖 [ReAct-Act] Classification
✅ [ReAct-Act] Mode: both
✅ [ReAct-Act] Found 5 results
🤖 [ReAct-Evaluate] Checking result quality...
✅ [ReAct-Evaluate] Quality: 0.0% (0/5 matches)  ← HONEST!
⚠️ [ReAct Agent] Quality not satisfied: 0.0%
🤖 [ReAct-Iterate] Refining query...
✅ [ReAct-Iterate] Refined: 'Tìm căn hộ 3 phòng ngủ ở quận 2, TP.HCM gần các trường quốc tế như Renaissance, BIS, AIS'
ℹ️ [ReAct Agent] Trying refined query
ℹ️ [ReAct Agent] Iteration 2/2
🤖 [ReAct-Act] Classification
✅ [ReAct-Act] Found 5 results
✅ [ReAct-Evaluate] Quality: 0.0% (0/5 matches)
⚠️ [ReAct Agent] Quality not satisfied: 0.0%
ℹ️ [ReAct Agent] Max iterations reached, asking clarification
```

✅ **This shows the full ReAct cycle:**
1. **REASONING**: Extracted structured requirements
2. **ACT**: Executed search
3. **EVALUATE**: Checked quality (0% match)
4. **ITERATE**: Refined query and tried again
5. **DECIDE**: Asked for clarification (honest feedback)

---

## 🎯 Method 2: Interactive Testing (Most Flexible)

### Run Interactive Mode

```bash
python3 test_react_manual.py
```

**Menu Options:**
```
1. Test pre-defined queries (recommended)
2. Test custom query
3. Multi-turn conversation test
4. Exit
```

---

### Option 1: Pre-defined Test Queries

Select `1` and you'll see:
```
1. Problematic Query (User discovered bug)
   Query: 'Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế'
   Expected: Should ask for clarification (0% match)

2. Specific District + Bedrooms
   Query: 'Tìm căn hộ 2 phòng ngủ ở quận 7'
   Expected: Should return results or ask clarification

3. Budget + Location
   Query: 'Tìm nhà dưới 5 tỷ ở Bình Thạnh'
   Expected: Should extract price_max=5 and district=Bình Thạnh

4. Vague Query
   Query: 'Tìm nhà đẹp giá tốt'
   Expected: Should ask for clarification (too vague)

5. Context-Based Follow-up
   Query: 'Có căn nào gần chợ không?'
   Expected: Should use conversation context
```

Select a number (1-5) or type `all` to test all queries.

---

### Option 2: Custom Query

Select `2` and enter your own query:
```
Enter your query: Tôi muốn mua biệt thự ở Thảo Điền dưới 20 tỷ
```

System will:
1. Extract requirements
2. Search
3. Evaluate quality
4. Return results or ask clarification

---

### Option 3: Multi-turn Conversation

Select `3` to test context awareness:
```
Turn 1 query: Tìm căn hộ 2 phòng ngủ ở quận 7
Turn 2 query: Có căn nào gần trường học không?
Turn 3 query: Giá bao nhiêu?
Turn 4 query: Khu vực đó có siêu thị không?
```

Watch how system maintains context across turns!

---

## 🎯 Method 3: Direct API Test (For Developers)

### Using curl

```bash
curl -X POST http://localhost:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "query": "Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế",
    "conversation_id": "test_session_001"
  }'
```

### Using httpx (Python)

```python
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8090/orchestrate",
            json={
                "user_id": "test_user",
                "query": "Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế",
                "conversation_id": "test_session"
            },
            timeout=120.0
        )
        print(response.json())

asyncio.run(test())
```

---

## 🧪 Recommended Test Scenarios

### 1. Test Honesty (Critical!)

**Query:**
```
Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế
```

**Expected Behavior:**
- System extracts: `district=quận 2, bedrooms=3, special_requirements=['gần trường quốc tế']`
- Search returns 5 results, but 0 match quận 2
- Quality: 0%
- **Response**: Honest clarification request (NOT "Tôi đã tìm thấy 5 BDS phù hợp")

✅ **Pass**: System says "Tôi không tìm thấy đủ BDS phù hợp"
❌ **Fail**: System says "Tôi đã tìm thấy 5 BDS phù hợp" (LYING)

---

### 2. Test Query Refinement

**Query:**
```
Tìm nhà gần trường quốc tế
```

**Expected Behavior:**
- Iteration 1: Vague query, poor results
- System refines: "Tìm nhà gần các trường quốc tế như Renaissance, BIS, AIS..."
- Iteration 2: More specific search
- If still poor → Ask clarification

**Check Logs:**
```
🤖 [ReAct-Iterate] Refining query...
✅ [ReAct-Iterate] Refined: '...'
```

---

### 3. Test Context Awareness

**Turn 1:**
```
Tìm căn hộ 2 phòng ngủ ở quận 7
```

**Turn 2:**
```
Có căn nào gần Lotte Mart không?
```

**Expected:**
- System enriches Turn 2 with context from Turn 1
- Searches for "căn hộ 2PN ở quận 7 gần Lotte Mart"

**Check Logs:**
```
ℹ️ Query enriched with context: '...' → '...'
```

---

### 4. Test Quality Threshold

**Query:**
```
Tìm căn hộ ở quận 1
```

**Expected:**
- If 3/5 results match (60%) → Return results ✅
- If 2/5 results match (40%) → Ask clarification ⚠️

**Check Logs:**
```
✅ [ReAct-Evaluate] Quality: 60.0% (3/5 matches)
✅ [ReAct Agent] Quality satisfied, returning results
```

or

```
✅ [ReAct-Evaluate] Quality: 40.0% (2/5 matches)
⚠️ [ReAct Agent] Quality not satisfied: 40.0%
🤖 [ReAct-Iterate] Refining query...
```

---

### 5. Test Iteration Limit

**Query:**
```
Tìm nhà đẹp giá rẻ
```

**Expected:**
- Iteration 1: Vague query, poor results
- Refine query
- Iteration 2: Still poor results
- **Max iterations reached** → Ask clarification

**Check Logs:**
```
ℹ️ [ReAct Agent] Iteration 1/2
...quality not satisfied...
🤖 [ReAct-Iterate] Refining query...
ℹ️ [ReAct Agent] Iteration 2/2
...quality not satisfied...
ℹ️ [ReAct Agent] Max iterations reached, asking clarification
```

---

## 📊 How to Evaluate Results

### ✅ Good Signs (ReAct Working)

1. **Honest Assessment:**
   - System says "Tìm được X BDS, nhưng chỉ Y BDS phù hợp (Z%)"
   - NOT just "Tôi đã tìm thấy X BDS phù hợp"

2. **Logs Show ReAct Steps:**
   ```
   🤖 [ReAct-Reasoning]
   🤖 [ReAct-Act]
   🤖 [ReAct-Evaluate]
   🤖 [ReAct-Iterate] or ℹ️ [ReAct Agent] Quality satisfied
   ```

3. **Quality Evaluation:**
   ```
   ✅ [ReAct-Evaluate] Quality: X% (Y/Z matches)
   ```

4. **Clarification When Needed:**
   - System asks for more info when results are poor
   - Provides specific suggestions

---

### ❌ Bad Signs (Something Wrong)

1. **No ReAct Logs:**
   - If you don't see `[ReAct` in logs → ReAct not running
   - Solution: Rebuild orchestrator (see Troubleshooting)

2. **Lying About Quality:**
   - System says "phù hợp" when results don't match
   - This was the OLD behavior (before ReAct)

3. **No Quality Check:**
   - System returns results without evaluating quality
   - No `[ReAct-Evaluate]` logs

4. **No Iteration:**
   - System gives up after first attempt
   - No `[ReAct-Iterate]` logs

---

## 🔧 Troubleshooting

### Problem: No ReAct Logs

**Symptom:**
```bash
docker logs ree-ai-orchestrator --tail 50
```

Shows NO `[ReAct` entries.

**Solution:**
```bash
# Full rebuild
docker-compose stop orchestrator
docker-compose rm -f orchestrator
docker-compose build --no-cache orchestrator
docker-compose up -d orchestrator

# Wait 10 seconds
sleep 10

# Test again
python3 test_react_manual.py --quick
```

---

### Problem: Old Behavior (Lying About Results)

**Symptom:**
System says "Tôi đã tìm thấy 5 BDS phù hợp" even when results don't match.

**Cause:**
Docker cached old code.

**Solution:**
```bash
# Nuclear option - rebuild everything
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
sleep 30

# Test
python3 test_react_manual.py --quick
```

---

### Problem: Script Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'httpx'
```

**Solution:**
```bash
pip3 install httpx
```

---

### Problem: Connection Refused

**Symptom:**
```
httpx.ConnectError: [Errno 61] Connection refused
```

**Solution:**
```bash
# Check orchestrator is running
docker ps | grep orchestrator

# If not running
docker-compose up -d orchestrator

# Check logs
docker logs ree-ai-orchestrator --tail 50
```

---

## 📝 Sample Test Session

Here's a complete test session example:

### Terminal 1: Run Test
```bash
cd /Users/tmone/ree-ai
python3 test_react_manual.py
# Select option 1 (pre-defined queries)
# Select query 1 (problematic query)
```

### Terminal 2: Watch Logs
```bash
cd /Users/tmone/ree-ai
./watch_react_logs.sh
```

**You'll see:**

**Terminal 1 Output:**
```
✅ RESPONSE RECEIVED
🎯 Intent: search
💬 SYSTEM RESPONSE:
Tôi không tìm thấy đủ bất động sản phù hợp với yêu cầu của bạn.
Tìm được 5 BDS, nhưng chỉ 0 BDS phù hợp (0%).
...
```

**Terminal 2 Logs:**
```
🤖 [ReAct Agent] Starting search...
🤖 [ReAct-Reasoning] Analyzing query requirements...
✅ [ReAct-Reasoning] Requirements: {'property_type': 'căn hộ', 'bedrooms': 3...}
ℹ️ [ReAct Agent] Iteration 1/2
🤖 [ReAct-Act] Classification
✅ [ReAct-Act] Found 5 results
🤖 [ReAct-Evaluate] Checking result quality...
✅ [ReAct-Evaluate] Quality: 0.0% (0/5 matches)
⚠️ [ReAct Agent] Quality not satisfied: 0.0%
🤖 [ReAct-Iterate] Refining query...
✅ [ReAct-Iterate] Refined: '...'
ℹ️ [ReAct Agent] Iteration 2/2
...
ℹ️ [ReAct Agent] Max iterations reached, asking clarification
```

✅ **Perfect!** This shows ReAct Agent working correctly.

---

## 🎯 Quick Checklist

Test these 5 scenarios to verify ReAct Agent:

- [ ] **Honesty Test**: Query "Tìm căn hộ 3PN ở quận 2 gần trường quốc tế" → Should admit 0% match
- [ ] **Refinement Test**: Check logs show `[ReAct-Iterate] Refining query`
- [ ] **Context Test**: Multi-turn conversation maintains context
- [ ] **Quality Threshold**: 60% match required before returning results
- [ ] **Clarification**: System asks for more info when results poor

If all 5 pass → ✅ **ReAct Agent Working Perfectly!**

---

## 📚 Additional Resources

- **Comprehensive Report**: `docs/REACT_AGENT_IMPROVEMENT_REPORT.md`
- **Code Implementation**: `services/orchestrator/main.py` (lines 322-869)
- **Architecture Guide**: `CLAUDE.md`

---

**Questions?** Check the logs first with `./watch_react_logs.sh` - they tell the full story!

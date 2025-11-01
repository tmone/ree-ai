# Testing ReAct Agent via Open WebUI

This guide shows you how to test the ReAct Agent through the Open WebUI chat interface.

---

## ✅ Step 1: Access Open WebUI

### Start Open WebUI (if not running)

```bash
cd /Users/tmone/ree-ai
docker-compose up -d open-webui
```

Wait 1-2 minutes for full startup.

### Open in Browser

Navigate to: **http://localhost:3000**

You should see the **REE AI - Real Estate Assistant** interface.

---

## 🔐 Step 2: Create Account / Login

### First Time Setup

If this is your first time:

1. Click **"Sign up"**
2. Enter:
   - Name: `Test User`
   - Email: `test@example.com`
   - Password: `password123`
3. Click **"Create Account"**

### Already Have Account

Click **"Sign in"** and use your existing credentials.

---

## 💬 Step 3: Start Testing ReAct Agent

Once logged in, you'll see the chat interface.

### Test Scenario 1: Problematic Query (Critical Test)

**Type this query:**
```
Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế
```

**Expected ReAct Behavior:**

1. **REASONING**: System extracts requirements:
   - Property type: căn hộ
   - Bedrooms: 3
   - District: Quận 2
   - City: TP.HCM
   - Special: gần trường quốc tế

2. **ACT**: Executes search

3. **EVALUATE**: Checks quality (likely 0/5 match because test data)

4. **ITERATE**:
   - Iteration 1: Refines query
   - Iteration 2: If still poor quality

5. **RESPONSE**: Honest feedback

**✅ Expected Response:**
```
Tôi không tìm thấy đủ bất động sản phù hợp với yêu cầu của bạn.

Tìm được 5 BDS, nhưng chỉ 0 BDS phù hợp (0%).

**Vấn đề:**
- Không đủ BDS ở quận 2
- Không đủ BDS có 3 phòng ngủ
- Thiếu: gần trường quốc tế

**Để tôi hỗ trợ tốt hơn, bạn có thể:**
- Cung cấp thêm thông tin cụ thể về "gần trường quốc tế" (ví dụ: tên trường, địa chỉ)
- Mở rộng khu vực tìm kiếm (các quận lân cận quận 2)
- Cho biết ngân sách cụ thể

Bạn muốn tôi hỗ trợ như thế nào?
```

**❌ Old Behavior (Before ReAct):**
```
Tôi đã tìm thấy 5 bất động sản phù hợp với yêu cầu của bạn:

1. Căn hộ cao cấp Vinhomes
   - Giá: 15 tỷ
   - Khu vực: Quận 7  ← WRONG!
   ...
```

---

### Test Scenario 2: Follow-up Query (Context Awareness)

After the first query, **continue the conversation:**

**Query 2:**
```
Vậy có căn nào ở quận 7 không?
```

**Expected Behavior:**
- System remembers context (3 bedrooms, căn hộ)
- Expands search to Quận 7
- Returns results or asks clarification

**Query 3:**
```
Giá khoảng bao nhiêu?
```

**Expected Behavior:**
- System maintains context about Quận 7, 3BR apartments
- Provides price information

---

### Test Scenario 3: Specific Requirements

**Query:**
```
Tìm nhà dưới 5 tỷ ở Bình Thạnh, có 2 phòng ngủ
```

**Expected ReAct Behavior:**

**REASONING**: Extracts
- Property type: nhà (or căn hộ if ambiguous)
- Price: < 5 tỷ
- District: Bình Thạnh
- Bedrooms: 2

**EVALUATE**: Checks if results match ALL criteria

**RESPONSE**: Either:
- ✅ "Tôi tìm thấy X/Y BDS phù hợp..." (if ≥60% match)
- ⚠️ "Tìm thấy Y BDS, nhưng chỉ X phù hợp..." (if 40-59% match)
- ❌ Clarification request (if <40% match)

---

### Test Scenario 4: Vague Query (Should Ask Clarification)

**Query:**
```
Tìm nhà đẹp giá tốt
```

**Expected Behavior:**

System should ask for clarification because:
- "đẹp" is subjective
- "giá tốt" is unclear (what budget?)
- No location specified

**Expected Response:**
```
Để tôi hỗ trợ tốt hơn, bạn có thể cung cấp thêm thông tin:

**Vấn đề:**
- Chưa có thông tin về khu vực mong muốn
- Chưa rõ ngân sách cụ thể ("giá tốt" = ?)
- Chưa có yêu cầu về loại hình (căn hộ/nhà phố/biệt thự)

**Gợi ý:**
- Bạn muốn tìm ở khu vực nào? (quận/huyện)
- Ngân sách của bạn là bao nhiêu? (ví dụ: dưới 5 tỷ, 5-10 tỷ, etc.)
- Số phòng ngủ mong muốn?
```

---

### Test Scenario 5: Chat (Non-Search)

**Query:**
```
Quy trình mua nhà cần giấy tờ gì?
```

**Expected Behavior:**
- Intent: `chat` (not search)
- System provides advisory response about legal procedures
- No ReAct Agent triggered (only for search intent)

**Expected Response:**
```
Để mua nhà, bạn cần chuẩn bị các giấy tờ sau:

1. **Giấy tờ cá nhân:**
   - CMND/CCCD
   - Hộ khẩu
   - Giấy kết hôn (nếu đã kết hôn)

2. **Giấy tờ tài chính:**
   - Sổ hộ khẩu/Giấy xác nhận thu nhập (nếu vay ngân hàng)
   ...
```

---

## 📊 How to Evaluate Results

### ✅ ReAct Agent is Working If:

1. **Honest Assessment:**
   - System admits when results don't match well
   - Shows match percentage (e.g., "3/5 BDS phù hợp (60%)")
   - NOT blindly saying "phù hợp" for all results

2. **Clarification Requests:**
   - Asks for more info when query is vague
   - Provides specific suggestions
   - Example: "Bạn có thể cho biết tên trường cụ thể?"

3. **Context Awareness:**
   - Follow-up queries use context from previous messages
   - Example: "Có căn nào gần chợ không?" remembers district and bedrooms

4. **Quality-Based Responses:**
   - Excellent match (≥80%): "Tôi đã tìm thấy X BDS **rất phù hợp**"
   - Good match (60-79%): "Tôi tìm thấy X/Y BDS phù hợp"
   - Poor match (<60%): Asks clarification or refines query

---

### ❌ Red Flags (ReAct NOT Working):

1. **Lying About Results:**
   - Claims "phù hợp" when results clearly don't match
   - Example: Query "quận 2" but shows "quận 7" properties

2. **No Clarification:**
   - Vague queries get blind responses instead of clarification requests

3. **No Context:**
   - Follow-up queries don't use previous conversation context

4. **No Quality Check:**
   - Always returns results regardless of match quality

---

## 🔍 Viewing ReAct Logs While Testing

### In Another Terminal

While you're testing in the browser, watch the ReAct logs:

```bash
cd /Users/tmone/ree-ai
./watch_react_logs.sh
```

Or manually:

```bash
docker logs ree-ai-orchestrator --tail 100 -f
```

### What to Look For

For each search query, you should see:

```
🎯 Query: 'Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế'
🤖 Intent: search
🤖 [ReAct Agent] Starting search with query: '...'
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
✅ [ReAct-Evaluate] Quality: 0.0% (0/5 matches)
⚠️ [ReAct Agent] Quality not satisfied: 0.0%
🤖 [ReAct-Iterate] Refining query...
✅ [ReAct-Iterate] Refined: 'Tìm căn hộ 3PN ở quận 2, TP.HCM gần các trường quốc tế như Renaissance, BIS, AIS'
ℹ️ [ReAct Agent] Trying refined query
ℹ️ [ReAct Agent] Iteration 2/2
...
ℹ️ [ReAct Agent] Max iterations reached, asking clarification
```

This shows the **full ReAct cycle** is working!

---

## 🎯 Quick Test Checklist

Use this checklist to verify ReAct Agent:

- [ ] **Open WebUI accessible** at http://localhost:3000
- [ ] **Logged in** successfully
- [ ] **Test 1 - Honesty**: "Tìm căn hộ 3PN quận 2 gần trường quốc tế"
      → ✅ System admits 0% match and asks clarification
      → ❌ System lies and says "phù hợp" with wrong results
- [ ] **Test 2 - Context**: Multi-turn conversation maintains context
- [ ] **Test 3 - Vague Query**: "Tìm nhà đẹp giá tốt"
      → ✅ System asks for clarification
- [ ] **Test 4 - Logs**: `watch_react_logs.sh` shows full ReAct cycle
- [ ] **Test 5 - Chat**: Non-search queries get advisory responses

If all 5 pass → ✅ **ReAct Agent Working Perfectly!**

---

## 🔧 Troubleshooting

### Problem 1: Cannot Access http://localhost:3000

**Check if container running:**
```bash
docker ps | grep open-webui
```

**If not running:**
```bash
docker-compose up -d open-webui
```

**If still not accessible:**
```bash
# Check logs
docker logs ree-ai-open-webui --tail 50

# Restart
docker-compose restart open-webui
```

---

### Problem 2: Open WebUI Shows Error

**Check dependency services:**
```bash
docker ps | grep -E "orchestrator|postgres"
```

All should be `Up`.

**If orchestrator not running:**
```bash
docker-compose up -d orchestrator
```

---

### Problem 3: Responses Don't Show ReAct Behavior

**Cause:** Orchestrator might be running old code (before ReAct).

**Solution:** Rebuild orchestrator:
```bash
docker-compose stop orchestrator
docker-compose rm -f orchestrator
docker-compose build --no-cache orchestrator
docker-compose up -d orchestrator

# Wait 10 seconds
sleep 10

# Restart Open WebUI to reconnect
docker-compose restart open-webui
```

---

### Problem 4: Open WebUI Says "API Key Required"

**This should NOT happen** because docker-compose sets `OPENAI_API_KEY=dummy-key-not-needed`.

**If it does:**

1. Check Open WebUI environment variables:
   ```bash
   docker exec ree-ai-open-webui env | grep OPENAI
   ```

   Should see:
   ```
   OPENAI_API_BASE_URL=http://orchestrator:8080
   OPENAI_API_KEY=dummy-key-not-needed
   ```

2. If not set, rebuild:
   ```bash
   docker-compose up -d --force-recreate open-webui
   ```

---

### Problem 5: Slow Responses

**Expected:** ReAct Agent takes 10-20 seconds per search query (longer than old system).

**Why:** ReAct performs multiple steps:
1. REASONING: Extract requirements (3-5s)
2. ACT: Execute search (2-5s)
3. EVALUATE: Check quality (1-2s)
4. ITERATE: Refine query + search again (5-10s)

**Total:** 10-20 seconds

This is **INTENTIONAL** - we prioritize **honest, validated results** over speed.

---

## 📊 Comparison: Testing via Open WebUI vs Script

| Aspect | Open WebUI | Python Script |
|--------|------------|---------------|
| **User Experience** | ✅ Realistic | ⚠️ Technical |
| **Visual Interface** | ✅ Full UI | ❌ Terminal only |
| **Multi-turn Context** | ✅ Easy | ⚠️ Manual conversation_id |
| **ReAct Logs** | ⚠️ Separate terminal | ✅ Same output |
| **Setup Time** | ⚠️ 2-3 min (build) | ✅ Instant |
| **Best For** | End-to-end testing | Quick validation |

**Recommendation:**
- Use **Open WebUI** for **realistic user testing**
- Use **Python script** for **quick technical validation**

---

## 🎯 Test Scenarios Summary

### Scenario 1: Problematic Query (Critical)
**Query:** `Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế`
**Pass Criteria:** System admits 0% match and asks clarification

### Scenario 2: Multi-turn Context
**Queries:**
1. `Tìm căn hộ 2 phòng ngủ ở quận 7`
2. `Có căn nào gần Lotte Mart không?`
**Pass Criteria:** Query 2 remembers "2 phòng ngủ" and "quận 7"

### Scenario 3: Specific Requirements
**Query:** `Tìm nhà dưới 5 tỷ ở Bình Thạnh, có 2 phòng ngủ`
**Pass Criteria:** Extracts all 3 requirements and validates results

### Scenario 4: Vague Query
**Query:** `Tìm nhà đẹp giá tốt`
**Pass Criteria:** Asks for clarification, not blind response

### Scenario 5: Chat Intent
**Query:** `Quy trình mua nhà cần giấy tờ gì?`
**Pass Criteria:** Provides advisory response, not search results

---

## 🚀 Quick Start

```bash
# Terminal 1: Start Open WebUI
cd /Users/tmone/ree-ai
docker-compose up -d open-webui

# Terminal 2: Watch logs
./watch_react_logs.sh

# Browser: Test
open http://localhost:3000
# Login and send query: "Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế"
```

**Expected:**
- Browser: Honest clarification request
- Logs: Full ReAct cycle (Reasoning → Act → Evaluate → Iterate)

---

## 📝 Notes

1. **First startup** takes 2-3 minutes (frontend build + database migration)
2. **Subsequent startups** take 10-20 seconds
3. **Each search query** takes 10-20 seconds (ReAct processing)
4. **Context history** is maintained per conversation (browser session)
5. **Logs are essential** to verify ReAct Agent is working

---

## 🎉 Success Criteria

You know ReAct Agent is working when:

1. ✅ **Browser** shows honest, quality-based responses
2. ✅ **Logs** show full ReAct cycle for each search
3. ✅ **System admits** when results don't match well
4. ✅ **System asks** for clarification when needed
5. ✅ **Context** is maintained across multi-turn conversations

**This is the core value proposition:** Honest, intelligent AI assistant that builds user trust through transparency.

---

**Happy Testing!** 🎯

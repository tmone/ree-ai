# Quick Start: Test ReAct Agent via Open WebUI

✅ **Status:** Open WebUI is ready at http://localhost:3000

---

## 🚀 5-Minute Test Guide

### Step 1: Open Browser

Navigate to: **http://localhost:3000**

---

### Step 2: Sign Up / Login

**First time:**
- Click **"Sign up"**
- Enter any email (e.g., `test@example.com`) and password
- Click **"Create Account"**

**Already have account:** Just sign in

---

### Step 3: Select Model

⚠️ **IMPORTANT:** You must select the model first!

1. Look for **"Select a model"** dropdown at the top of chat interface
2. Click it
3. Select **"ree-ai-assistant"**

If you don't see any model:
- Wait 30 seconds for Open WebUI to load models
- Refresh the page (F5)
- Check that orchestrator is running: `docker ps | grep orchestrator`

---

### Step 4: Send Test Query

Now you can test ReAct Agent!

**Copy and paste this query:**
```
Tìm căn hộ 3 phòng ngủ ở quận 2 gần trường quốc tế
```

Press Enter and wait ~15-20 seconds.

---

### ✅ Expected Response (ReAct Working)

You should see something like:

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

✅ **This is CORRECT!** System is being honest about result quality.

---

### ❌ Old Behavior (Before ReAct)

If you see this, ReAct is NOT working:

```
Tôi đã tìm thấy 5 bất động sản phù hợp với yêu cầu của bạn:

1. Căn hộ Quận 7 (WRONG!)
2. Căn hộ Thanh Trì (WRONG!)
...
```

**Fix:** Rebuild orchestrator:
```bash
docker-compose stop orchestrator
docker-compose rm -f orchestrator
docker-compose build --no-cache orchestrator
docker-compose up -d orchestrator
docker-compose restart open-webui
```

---

### 🔍 Watch ReAct Logs (Optional)

In another terminal:
```bash
cd /Users/tmone/ree-ai
./watch_react_logs.sh
```

You'll see the full ReAct cycle:
```
🤖 [ReAct Agent] Starting search...
🤖 [ReAct-Reasoning] Analyzing query requirements...
✅ [ReAct-Reasoning] Requirements: {'property_type': 'căn hộ', 'bedrooms': 3...}
ℹ️ [ReAct Agent] Iteration 1/2
🤖 [ReAct-Act] Classification
✅ [ReAct-Act] Found 5 results
🤖 [ReAct-Evaluate] Quality: 0.0% (0/5 matches)
⚠️ [ReAct Agent] Quality not satisfied
🤖 [ReAct-Iterate] Refining query...
ℹ️ [ReAct Agent] Iteration 2/2
...
ℹ️ [ReAct Agent] Max iterations reached, asking clarification
```

---

## 🧪 More Test Scenarios

### Test 2: Multi-turn Context

**Query 1:**
```
Tìm căn hộ 2 phòng ngủ ở quận 7
```

**Query 2:**
```
Có căn nào gần Lotte Mart không?
```

✅ **Pass:** Query 2 remembers "2 phòng ngủ" and "quận 7"

---

### Test 3: Vague Query

```
Tìm nhà đẹp giá tốt
```

✅ **Pass:** System asks for clarification instead of blind response

---

### Test 4: Chat Intent

```
Quy trình mua nhà cần giấy tờ gì?
```

✅ **Pass:** Advisory response, no property search

---

## 🔧 Troubleshooting

### Problem: "Chưa chọn Mô hình" Error

**Solution:**
1. Look for model dropdown at top
2. Select **"ree-ai-assistant"**
3. If not visible, wait 30s and refresh

---

### Problem: No Models in Dropdown

**Check orchestrator:**
```bash
docker ps | grep orchestrator
# Should show: Up X minutes

curl http://localhost:8090/v1/models
# Should return: {"object":"list","data":[{"id":"ree-ai-assistant"...}]}
```

**If orchestrator not running:**
```bash
docker-compose up -d orchestrator
docker-compose restart open-webui
```

---

### Problem: Response Too Slow

**Expected:** 15-20 seconds per search query (ReAct processing)

**Why:** ReAct Agent performs multiple steps:
- REASONING: Extract requirements (3-5s)
- ACT: Execute search (2-5s)
- EVALUATE: Check quality (1-2s)
- ITERATE: Refine + search again (5-10s)

This is **intentional** - we prioritize honest, validated results over speed.

---

## 🎯 Success Checklist

- [ ] Open WebUI accessible at http://localhost:3000
- [ ] Logged in successfully
- [ ] Model **"ree-ai-assistant"** selected
- [ ] Test query returns honest clarification
- [ ] Logs show full ReAct cycle
- [ ] Multi-turn conversation maintains context

If all pass → ✅ **ReAct Agent Working Perfectly!**

---

## 📚 Full Documentation

For detailed testing guide:
- **TEST_REACT_VIA_OPEN_WEBUI.md** - Complete testing scenarios
- **docs/REACT_AGENT_IMPROVEMENT_REPORT.md** - Technical implementation details

---

**Happy Testing!** 🎯

If you see honest, quality-based responses → ReAct Agent is working and building user trust through transparency!

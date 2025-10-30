# 🌐 Open WebUI Integration Guide

**Connect Open WebUI with REE AI Orchestrator**

---

## 📋 Current Architecture

```
┌─────────────────────────────────────────┐
│  Open WebUI (http://localhost:3000)     │
│  ❌ Currently: Calls Ollama directly    │
│  ✅ Goal: Call our Orchestrator         │
└─────────────────────────────────────────┘
```

## 🎯 Integration Methods

### Method 1: Custom Function (Recommended ⭐)

Install a custom function in Open WebUI to intercept real estate queries.

**Pros:**
- ✅ No code changes to Open WebUI
- ✅ Easy to install (copy-paste)
- ✅ Can toggle on/off
- ✅ Works with official Open WebUI image

**Cons:**
- ⚠️ Requires manual installation
- ⚠️ Limited control

---

## 🚀 Method 1: Install Custom Function (5 Minutes)

### Step 1: Start Services

```bash
# Start everything including Open WebUI
docker-compose --profile real up -d

# Wait for services to be healthy
docker-compose ps
```

### Step 2: Access Open WebUI Admin

1. Open browser: **http://localhost:3000**

2. **First time setup:**
   - Create admin account
   - Username: `admin@ree-ai.com`
   - Password: `your-secure-password`

3. **Login** with admin account

### Step 3: Navigate to Functions

```
http://localhost:3000/admin/functions
```

Or:
1. Click **⚙️ Settings** (top right)
2. Click **Admin Panel**
3. Click **Functions** tab

### Step 4: Add REE AI Function

1. Click **"+ Add Function"** button

2. **Copy content** from `services/open_webui_integration/ree_ai_function.py`

3. **Paste** into the function editor

4. **Save** (Ctrl+S or click Save button)

5. **Enable** the function (toggle switch)

### Step 5: Configure Function

1. Click **"⚙️ Valves"** button on the REE AI function

2. Configure settings:
   ```
   orchestrator_url: http://orchestrator:8080
   priority: 0
   enable_debug: true
   ```

3. **Save** configuration

### Step 6: Test Integration

1. Go to **Chat** page (http://localhost:3000)

2. **Test with real estate query:**
   ```
   Tìm nhà 2 phòng ngủ ở Quận 1
   ```

3. **Expected behavior:**
   - Function detects real estate keywords
   - Calls Orchestrator instead of Ollama
   - Returns property search results

4. **Test with non-real estate query:**
   ```
   What is the weather today?
   ```
   - Should pass through to Ollama normally

### Step 7: Check Debug Logs

```bash
# View Open WebUI logs
docker-compose logs -f open-webui

# Should see:
# [REE AI] User query: Tìm nhà 2 phòng ngủ ở Quận 1
# [REE AI] Real estate query detected! Calling Orchestrator...
# [REE AI] Orchestrator response: Tôi tìm thấy 5 căn nhà...
```

---

## 🎨 Method 2: Custom Open WebUI Fork (Advanced)

For deeper integration, fork and modify Open WebUI source code.

### Why Fork?

- ✅ Full control over routing logic
- ✅ Custom UI for property search
- ✅ Better integration with our system
- ✅ Can add REE AI-specific features

### How to Fork

1. **Fork Open WebUI:**
   ```bash
   git clone https://github.com/open-webui/open-webui.git
   cd open-webui
   ```

2. **Modify routing logic:**
   ```python
   # backend/apps/webui/routers/chats.py

   # Add import
   import requests

   # Modify completion endpoint
   @router.post("/completions")
   async def chat_completions(form_data: CompletionForm, user=Depends(get_current_user)):
       messages = form_data.messages
       last_message = messages[-1]["content"]

       # Check if real estate query
       keywords = ["nhà", "căn hộ", "tìm", "apartment"]
       if any(kw in last_message.lower() for kw in keywords):
           # Call our Orchestrator
           response = requests.post(
               "http://orchestrator:8080/orchestrate",
               json={
                   "user_id": user.id,
                   "query": last_message
               }
           )
           if response.status_code == 200:
               data = response.json()
               return {"response": data["response"]}

       # Normal flow to Ollama
       return await generate_ollama_completion(form_data, user)
   ```

3. **Build custom image:**
   ```dockerfile
   # Dockerfile.custom
   FROM ghcr.io/open-webui/open-webui:main
   COPY backend/apps/webui/routers/chats.py /app/backend/apps/webui/routers/chats.py
   ```

4. **Update docker-compose.yml:**
   ```yaml
   open-webui:
     build:
       context: ./open-webui
       dockerfile: Dockerfile.custom
   ```

---

## 🔧 Troubleshooting

### Function Not Working

**Check 1: Function is enabled**
```
Admin Panel → Functions → REE AI function → Toggle is ON
```

**Check 2: Orchestrator is running**
```bash
curl http://localhost:8090/health
# Should return: {"status": "healthy"}
```

**Check 3: Network connectivity**
```bash
# Test from Open WebUI container
docker exec -it ree-ai-open-webui curl http://orchestrator:8080/health
```

**Check 4: Debug logs**
```bash
docker-compose logs -f open-webui | grep "REE AI"
```

### Function Not Intercepting Queries

**Check 1: Keywords**
Make sure query contains real estate keywords:
- ✅ "Tìm nhà 2 phòng ngủ" (contains "Tìm" and "nhà")
- ✅ "Có căn hộ nào ở Quận 1?" (contains "căn hộ")
- ❌ "Hello" (no real estate keywords)

**Check 2: Function priority**
If multiple functions installed, check priority:
```
Valves → priority: 0 (higher = earlier execution)
```

### Orchestrator Returns Error

**Check 1: Orchestrator logs**
```bash
docker-compose logs -f orchestrator
```

**Check 2: Dependencies**
```bash
# Check if DB Gateway is running
curl http://localhost:8081/health

# Check if Core Gateway is running
curl http://localhost:8080/health
```

---

## 📊 Testing Checklist

- [ ] Open WebUI accessible at http://localhost:3000
- [ ] Can create admin account
- [ ] Can access Admin Panel → Functions
- [ ] REE AI function is installed and enabled
- [ ] Valves configured correctly
- [ ] Test query: "Tìm nhà 2 phòng ngủ" → Calls Orchestrator
- [ ] Test query: "Hello" → Calls Ollama normally
- [ ] Debug logs showing "[REE AI]" messages
- [ ] Orchestrator returning search results
- [ ] Response displayed in chat

---

## 🎯 End-to-End Flow

```
1. User types: "Tìm nhà 2 phòng ngủ ở Quận 1"
   ↓
2. Open WebUI → REE AI Function (inlet)
   ↓
3. Function detects keywords ("Tìm", "nhà")
   ↓
4. Function calls: http://orchestrator:8080/orchestrate
   ↓
5. Orchestrator → Intent detection: SEARCH
   ↓
6. Orchestrator → Calls RAG Service
   ↓
7. RAG Service → DB Gateway (search properties)
   ↓
8. RAG Service → Core Gateway (generate answer)
   ↓
9. Orchestrator → Returns response to Function
   ↓
10. Function → Injects response into Open WebUI
   ↓
11. Open WebUI → Displays: "Tôi tìm thấy 5 căn nhà..."
   ↓
12. User sees property recommendations! 🎉
```

---

## 🔍 Verification

### Test 1: Real Estate Query
```
Input: "Tìm nhà 2 phòng ngủ giá 8 tỷ"

Expected:
- Function intercepts query
- Calls Orchestrator
- Returns property list
- Shows in chat

Logs should show:
[REE AI] Real estate query detected!
[REE AI] Calling Orchestrator...
[REE AI] Orchestrator response: Tôi tìm thấy...
```

### Test 2: Normal Query
```
Input: "What is 2+2?"

Expected:
- Function passes through
- Goes to Ollama
- Returns normal answer

Logs should show:
[REE AI] Not a real estate query, passing through to Ollama
```

### Test 3: Error Handling
```
# Stop Orchestrator
docker-compose stop orchestrator

Input: "Tìm nhà 2 phòng ngủ"

Expected:
- Function detects error
- Falls back to Ollama
- Shows error message

Logs should show:
[REE AI] Exception calling Orchestrator: ...
```

---

## 📚 Documentation

- **Function Code:** `services/open_webui_integration/ree_ai_function.py`
- **Integration Guide:** `services/open_webui_integration/README.md`
- **Open WebUI Docs:** https://docs.openwebui.com/

---

## ✅ Success Criteria

After following this guide:

- [x] Open WebUI running at http://localhost:3000
- [x] REE AI function installed and enabled
- [x] Real estate queries route to Orchestrator
- [x] Normal queries route to Ollama
- [x] Debug logs visible
- [x] End-to-end flow working

**Open WebUI is now integrated with REE AI system!** 🎉

---

## 🚀 Next Steps

1. **Customize keywords** in function for better detection
2. **Add more features** (price filter, location filter)
3. **Improve UI** (show property cards instead of text)
4. **Add analytics** (track which queries go to Orchestrator)
5. **Consider forking** Open WebUI for deeper integration

---

**Status:** ✅ Integration Method Documented
**Recommended:** Method 1 (Custom Function)
**Effort:** 5 minutes to install

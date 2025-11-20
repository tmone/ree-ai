# Deployment Guide - Anti-Hallucination Fix to Dev Server

**Target Server:** 103.153.74.213
**Issue Fixed:** LLM hallucinating 4 fake properties when only 1 real property exists
**Status:** ✅ Ready for deployment

---

## 📦 What's Being Deployed

### Core Fixes
1. **`services/rag_service/openai_compliant_prompts.py`**
   - Added CRITICAL RULE #0 (anti-hallucination)
   - Updated user prompt with strict instructions

2. **`services/rag_service/main.py`**
   - Temperature: 0.7 → 0.3
   - Updated fallback prompts with Vietnamese rules

### Git Commit
- **Commit:** `4af6011`
- **Message:** "fix: Prevent LLM hallucination with strict anti-hallucination rules"

---

## 🚀 Deployment Steps

### Step 1: SSH to Dev Server

```bash
ssh user@103.153.74.213
# OR
ssh root@103.153.74.213
```

### Step 2: Navigate to Project Directory

```bash
cd /path/to/ree-ai  # Update with actual path
```

### Step 3: Pull Latest Changes

```bash
git pull origin main
# Should pull commit 4af6011
```

### Step 4: Rebuild RAG Service

```bash
# Rebuild only RAG service (faster)
docker-compose build rag_service

# Or rebuild all services (if needed)
docker-compose build
```

### Step 5: Restart Services

```bash
# Restart only RAG service
docker-compose restart rag_service

# Or restart all services
docker-compose restart

# Or full restart (if issues)
docker-compose down
docker-compose up -d
```

### Step 6: Verify Deployment

```bash
# Check RAG service logs
docker-compose logs -f rag_service | head -50

# Look for:
# - "temperature": 0.3
# - No errors on startup
```

---

## ✅ Verification Tests

### Test 1: Health Check

```bash
curl http://103.153.74.213:8090/health
# Expected: {"status": "healthy"}
```

### Test 2: Test Original Issue Query

```bash
curl -X POST http://103.153.74.213:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm nhà dưới 50 tỷ ở TP.HCM",
    "user_id": "deployment_test"
  }'
```

**Expected Result:**
- ✅ Returns ONLY 1 real property (2BR Binh Thanh, 4.5B VND)
- ✅ NO fake District 1/7/3/2 properties
- ❌ Should NOT see: "45 billion", "38 billion", "42 billion", "30 billion"

### Test 3: Impossible Search (Zero Results)

```bash
curl -X POST http://103.153.74.213:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm lâu đài 50 phòng ngủ giá 100 đồng",
    "user_id": "deployment_test"
  }'
```

**Expected Result:**
- ✅ Response contains "không tìm thấy" or "không có"
- ✅ NO fake property suggestions
- ✅ Property count = 0

### Test 4: POST Flow (Should NOT suggest properties)

```bash
curl -X POST http://103.153.74.213:8090/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tôi muốn bán nhà ở Quận 7",
    "user_id": "deployment_test"
  }'
```

**Expected Result:**
- ✅ Response asks questions (contains "?")
- ✅ NO property listings
- ✅ Guides posting process

### Test 5: Run Automated Verification Script

If you copied `tests/verify_deployment.py` to server:

```bash
python tests/verify_deployment.py --url http://103.153.74.213:8090
```

**Expected Output:**
```
TEST 1 (SEARCH): 3/3 [PASS]
TEST 2 (POST):   2/2 [PASS]
TEST 3 (CHAT):   1/1 [PASS]

TOTAL: 6/6 tests passed
Success Rate: 100.0%

[SUCCESS] All tests passed! Anti-hallucination fix is working correctly.
```

---

## 🔍 Monitoring After Deployment

### Check Logs for Hallucination Patterns

```bash
# Monitor RAG service logs
docker-compose logs -f rag_service

# Look for suspicious patterns (should NOT appear):
# - "District 1.*45.*billion"
# - "District 7.*Phu My Hung.*42.*billion"
# - Multiple properties when DB has only 1
```

### OpenSearch Query Verification

```bash
# Check actual property count
curl -u admin:realWorldAsset@2025 \
  http://103.153.74.213:9200/properties/_count

# Search for 2BR properties
curl -u admin:realWorldAsset@2025 \
  -X POST http://103.153.74.213:9200/properties/_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "match": {
        "bedrooms": 2
      }
    }
  }'
```

---

## 🐛 Troubleshooting

### Issue 1: Service Won't Start

```bash
# Check logs
docker-compose logs rag_service

# Common fixes:
docker-compose down
docker-compose up -d
```

### Issue 2: Still Seeing Fake Properties

**Possible causes:**
1. Old code still cached
2. Wrong environment variables
3. Temperature not updated

**Fix:**
```bash
# Full rebuild
docker-compose down
docker-compose build --no-cache rag_service
docker-compose up -d

# Verify temperature in logs
docker-compose logs rag_service | grep temperature
# Should show: "temperature": 0.3
```

### Issue 3: Changes Not Applied

```bash
# Verify correct commit
git log -1
# Should show: 4af6011

# Verify files updated
cat services/rag_service/main.py | grep "temperature"
# Should show: "temperature": 0.3

# Rebuild
docker-compose build rag_service
docker-compose restart rag_service
```

---

## 📊 Success Metrics

### Before Fix
- ❌ 4 fake properties when DB had 1
- ❌ Invented addresses (District 1, 7, 3, 2)
- ❌ Invented prices (45B, 38B, 42B, 30B)
- ❌ Users couldn't trust search results

### After Fix
- ✅ Returns ONLY real properties from OpenSearch
- ✅ Max 5 properties (as configured)
- ✅ 0 results → "không tìm thấy" (no fake data)
- ✅ Temperature 0.3 → deterministic output
- ✅ Comprehensive anti-hallucination rules

---

## 📝 Rollback Plan (If Needed)

If deployment causes issues:

```bash
# Rollback to previous commit
git log --oneline -5  # Find previous commit
git checkout <previous-commit-hash>

# Rebuild and restart
docker-compose build rag_service
docker-compose restart rag_service
```

---

## ✅ Deployment Checklist

- [ ] SSH to dev server (103.153.74.213)
- [ ] Navigate to project directory
- [ ] `git pull origin main`
- [ ] Verify commit 4af6011 pulled
- [ ] `docker-compose build rag_service`
- [ ] `docker-compose restart rag_service`
- [ ] Health check passes
- [ ] Test 1: Original issue query (no fake properties)
- [ ] Test 2: Impossible search (graceful fail)
- [ ] Test 3: POST flow (no suggestions)
- [ ] Run automated verification script
- [ ] Monitor logs for 10-15 minutes
- [ ] Test with real user queries
- [ ] Notify team deployment complete

---

## 📞 Support

**If issues occur:**
1. Check logs: `docker-compose logs -f rag_service`
2. Verify OpenSearch has data: `curl http://103.153.74.213:9200/properties/_count`
3. Full restart: `docker-compose down && docker-compose up -d`
4. Contact: [Your contact info]

---

**Deployment Guide Version:** 1.0
**Last Updated:** 2025-11-20
**Prepared By:** Claude AI Assistant

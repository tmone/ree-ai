# Versioned Files Review

## Files Need Decision

### 1. services/semantic_chunking/main_v2.py
**Status:** BETTER than main.py
**Why:**
- Uses BaseService (proper microservice pattern)
- Auto-registration with Service Registry
- Cleaner code (151 lines vs 228 lines)
- Better error handling

**Current:** Docker uses `main.py`
**Recommendation:** 
1. Test main_v2.py thoroughly
2. If works, replace main.py with main_v2.py
3. Delete original main.py

**Test command:**
```bash
# Temporarily update Dockerfile
sed -i '' 's/main:app/main_v2:app/' services/semantic_chunking/Dockerfile
docker-compose build semantic-chunking
docker-compose up semantic-chunking
# Test endpoint
curl http://localhost:8082/health
```

### 2. services/orchestrator/main_v2.py  
**Status:** BETTER than main.py
**Why:**
- Uses BaseService pattern
- Dynamic service discovery via Service Registry
- NO hardcoded service URLs
- Better architecture

**Current:** Docker uses `main.py`
**Recommendation:** Same as above - test and replace

### 3. docs/integration/crawl4ai-integration.md
**Status:** Renamed from crawl4ai_integration_guide_v2.md
**Action:** ✅ Already cleaned (removed _v2 suffix)

## Quick Cleanup (If you trust v2 files):

```bash
# Backup current files
cp services/semantic_chunking/main.py services/semantic_chunking/main_old_backup.py
cp services/orchestrator/main.py services/orchestrator/main_old_backup.py

# Replace with v2
mv services/semantic_chunking/main_v2.py services/semantic_chunking/main.py
mv services/orchestrator/main_v2.py services/orchestrator/main.py

# Test
docker-compose build semantic-chunking orchestrator
docker-compose up -d semantic-chunking orchestrator

# If works:
rm services/semantic_chunking/main_old_backup.py
rm services/orchestrator/main_old_backup.py

# If fails:
mv services/semantic_chunking/main_old_backup.py services/semantic_chunking/main.py
mv services/orchestrator/main_old_backup.py services/orchestrator/main.py
```

## Conservative Approach:

Keep both files for now, but document which is "canonical":
- Rename main.py -> main_legacy.py
- Rename main_v2.py -> main.py
- Update Dockerfile to use new main.py
- Test thoroughly
- Delete main_legacy.py after confirming

---

**Delete this file after making decision**

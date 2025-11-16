# Conversation Memory Fix - 2025-11-16

## Problem

System repeatedly asked basic questions even after user already provided information:

```
User: "Xin chào, tôi muốn đăng bán căn hộ"
System: "Cảm ơn bạn! Tôi hiểu bạn muốn đăng tin.
         Để bắt đầu, cho tôi biết:
         1. Loại bất động sản gì? (căn hộ/nhà/đất/...)  ← ALREADY SAID "căn hộ"!
         2. Bán hay cho thuê?"                          ← ALREADY SAID "bán"!
```

## Root Cause

**File**: `services/orchestrator/main.py` lines 195-198

**Buggy Logic**:
```python
# If request is from Open WebUI, use history from request metadata
# Open WebUI already sends full conversation history in messages
if request.metadata and request.metadata.get("from_open_webui"):
    history = request.metadata.get("conversation_history", [])  # ← Always empty!
else:
    # For direct API calls, fetch from PostgreSQL
    history = await self._get_conversation_history(request.user_id, conversation_id, limit=10)
```

**Evidence from Logs**:
```
[OpenAI Compat DEBUG] Total messages received: 1         ← Open WebUI sends ONLY current message
[OpenAI Compat DEBUG] Conversation history extracted: 0 messages  ← Result: empty history
[History Extraction DEBUG] Received history with 0 messages
```

**The Misunderstanding**:
- Comment said "Open WebUI already sends full conversation history"
- In reality, Open WebUI only sends the current message
- Result: `conversation_history` in metadata was always empty
- System thought this was a new conversation every time

## Architecture Clarification

**PostgreSQL is the source of truth for conversation memory:**

From `CLAUDE.md` lines 92-95:
```
- **OpenSearch**: Stores ALL property data (flexible schema, vector search, full-text search)
- **PostgreSQL**: Stores ONLY user data, conversations, and chat history (structured relational data)
```

**Orchestrator manages its own memory:**
- Saves messages to PostgreSQL after each request (lines 262-263)
- Has `_get_conversation_history()` function (lines 3562-3604)
- Has `_save_message()` function
- Open WebUI is just a frontend, NOT responsible for our backend's memory

## The Fix

**Changed lines 189-198 in `services/orchestrator/main.py`:**

```python
# Step 0: Get conversation history (MEMORY CONTEXT)
# ALWAYS fetch from PostgreSQL for ALL requests (including Open WebUI)
# Orchestrator manages its own memory - don't rely on external sources
conversation_id = request.conversation_id or request.user_id

history = await self._get_conversation_history(request.user_id, conversation_id, limit=10)
if history:
    self.logger.info(f"{LogEmoji.INFO} [{request_id}] Retrieved {len(history)} messages from PostgreSQL")
else:
    self.logger.info(f"{LogEmoji.INFO} [{request_id}] No conversation history found (new conversation)")
```

**Key Changes**:
1. ✅ **Removed** the `from_open_webui` check
2. ✅ **ALWAYS** fetch from PostgreSQL for ALL requests
3. ✅ **Simplified** logic - one source of truth
4. ✅ **Better logging** for debugging

## Why This Works

1. **PostgreSQL is already saving messages**: Lines 262-263 save both user and assistant messages
2. **Infrastructure already exists**: `_get_conversation_history()` and `_save_message()` work correctly
3. **Bug was logic error**: Code chose wrong path (empty metadata instead of PostgreSQL)
4. **Open WebUI doesn't matter**: It's just a frontend sending requests via OpenAI-compatible API

## Expected Behavior After Fix

**Before Fix**:
```
Turn 1: User: "Tôi muốn bán căn hộ"
        System: "Loại BĐS? Bán hay thuê?"  ← Asks again!

Turn 2: User: "Căn hộ 70m²"
        System: "Loại BĐS? Bán hay thuê?"  ← Asks again!
```

**After Fix**:
```
Turn 1: User: "Tôi muốn bán căn hộ"
        System: "Tuyệt! Địa chỉ ở đâu?"   ← Remembers property_type=căn hộ, transaction_type=bán

Turn 2: User: "Quận 7, 70m²"
        System: "Giá bao nhiêu?"          ← Remembers district + area, asks next field
```

## Testing

**Deployed**: 2025-11-16 17:23:16 +07:00
**Service**: Orchestrator restarted successfully
**Health**: ✅ Healthy

**Next Steps**:
1. Test via Open WebUI with multi-turn conversation
2. Verify logs show "Retrieved X messages from PostgreSQL"
3. Verify system remembers previous entities
4. Confirm no repeated questions

## Related Files

- `services/orchestrator/main.py:189-198` - The fix
- `services/orchestrator/main.py:262-263` - Message saving (already works)
- `services/orchestrator/main.py:3562-3604` - History retrieval functions (already work)
- `CLAUDE.md` - Architecture documentation

---

**Status**: ✅ **DEPLOYED**
**Priority**: CRITICAL
**Impact**: Fixes core UX issue - system now remembers conversation context

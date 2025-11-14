# Orchestrator Extraction Service Migration Guide

## 📋 Overview

This document tracks the migration of Orchestrator to use the new master data extraction service with multi-language support.

## ✅ Completed

### 1. **SearchHandler (Handler-based flow) - UPDATED** ✅

**File**: `services/orchestrator/handlers/search_handler.py`

**Changes**:
- Updated to call `/extract-query-enhanced` endpoint
- Uses helper functions from `services/orchestrator/utils/extraction_helpers.py`
- Handles 3-tier response structure (raw/mapped/new)
- Extracts master data IDs and passes to RAG Service

**Status**: ✅ **Complete and tested**

### 2. **Extraction Helper Utilities - CREATED** ✅

**File**: `services/orchestrator/utils/extraction_helpers.py`

**Functions**:
- `build_filters_from_extraction_response()` - Convert new response to filters
- `convert_legacy_extraction_response()` - Backward compatibility adapter
- `extract_entities_for_logging()` - Human-readable logging format

**Status**: ✅ **Complete**

## ⏳ Pending Legacy Code Migration

### Methods in `services/orchestrator/main.py` that need updates:

1. **`_execute_filter_search()`** (Line ~951)
   - Currently calls: `/extract-query` (old endpoint)
   - Expects: `{"entities": {...}}`
   - **Action needed**: Use helper functions to handle new response

2. **Other extraction calls** (Lines 1137, 1498, 1662, 1780)
   - Multiple places calling `/extract-query`
   - Need systematic refactoring

## 🔧 Migration Strategy

### Option 1: Gradual Migration (Recommended)

**Keep both old and new flows working during transition**

```python
# In orchestrator/main.py

from services.orchestrator.utils.extraction_helpers import (
    build_filters_from_extraction_response,
    convert_legacy_extraction_response
)

async def _execute_filter_search(self, query: str) -> List[Dict]:
    """Execute filter-based search (Extraction → Document search)"""
    try:
        # TRY NEW ENDPOINT FIRST
        try:
            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query-enhanced",
                json={"query": query, "intent": "SEARCH"},
                timeout=settings.EXTRACTION_TIMEOUT
            )

            if extraction_response.status_code == 200:
                extraction_result = extraction_response.json()

                # Use helper to build filters
                entities = build_filters_from_extraction_response(extraction_result)

                self.logger.info(f"{LogEmoji.SUCCESS} Using NEW extraction endpoint")

        except Exception as e:
            # FALLBACK TO OLD ENDPOINT
            self.logger.warning(f"{LogEmoji.WARNING} New endpoint failed, using legacy: {e}")

            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query",
                json={"query": query, "intent": "SEARCH"},
                timeout=settings.EXTRACTION_TIMEOUT
            )

            if extraction_response.status_code == 200:
                extraction = extraction_response.json()
                entities = extraction.get("entities", {})

        # Rest of the code continues as normal...

    except Exception as e:
        self.logger.error(f"Extraction failed: {e}")
        return []
```

### Option 2: Feature Flag (Production-safe)

```python
# In shared/config.py
USE_NEW_EXTRACTION_ENDPOINT = os.getenv("USE_NEW_EXTRACTION_ENDPOINT", "false").lower() == "true"

# In orchestrator
if settings.USE_NEW_EXTRACTION_ENDPOINT:
    # Use new endpoint
    extraction_result = await call_new_endpoint()
    entities = build_filters_from_extraction_response(extraction_result)
else:
    # Use old endpoint
    entities = await call_old_endpoint()
```

### Option 3: Clean Refactor (Breaking change)

**Replace all calls at once** - Only do this when confident

```python
# Update all 5+ locations in main.py
# Replace old extraction calls with new helper-based approach
# Remove old extraction handling code
```

## 📝 Checklist for Each Method

When migrating a method that calls extraction service:

- [ ] Identify the extraction call
- [ ] Change endpoint from `/extract-query` → `/extract-query-enhanced`
- [ ] Add intent parameter if not present
- [ ] Import helper functions
- [ ] Replace `entities = result.get("entities", {})` with:
  ```python
  entities = build_filters_from_extraction_response(result)
  ```
- [ ] Update logging to use `extract_entities_for_logging()` if needed
- [ ] Test the flow end-to-end
- [ ] Remove old code after verification

## 🔍 Finding All Extraction Calls

```bash
# Find all extraction service calls
grep -n "extract-query\|extraction_url" services/orchestrator/main.py

# Expected locations:
# Line 956:  /extract-query (in _execute_filter_search)
# Line 1137: /extract-query
# Line 1498: /extract-query
# Line 1662: /extract-query
# Line 1780: /extract-query
```

## 🧪 Testing Strategy

### 1. Unit Tests

```python
# Test helper functions
def test_build_filters_from_extraction_response():
    extraction_result = {
        "raw": {"bedrooms": 2, "area": 80},
        "mapped": [
            {
                "property_name": "district",
                "table": "districts",
                "id": 1,
                "value": "district_1",
                "value_translated": "Quận 1"
            }
        ],
        "new": []
    }

    filters = build_filters_from_extraction_response(extraction_result)

    assert filters["bedrooms"] == 2
    assert filters["district_id"] == 1
    assert filters["district"] == "district_1"
```

### 2. Integration Tests

```python
# Test SearchHandler end-to-end
async def test_search_handler_with_new_extraction():
    handler = SearchHandler(...)
    response = await handler.handle(
        request_id="test-123",
        query="Tìm căn hộ 2PN Quận 1"
    )

    assert "căn hộ" in response.lower()
    # Verify RAG was called with master data IDs
```

### 3. Manual Testing

1. Start all services with new extraction endpoint
2. Send search query via Orchestrator
3. Check logs for:
   - ✅ Extraction returns mapped master data IDs
   - ✅ Filters include `district_id`, `property_type_id`, etc.
   - ✅ RAG service receives correct filters
   - ✅ Response is accurate

## 📊 Migration Status Tracking

| Location | Method | Status | Notes |
|----------|--------|--------|-------|
| `handlers/search_handler.py` | `handle()` | ✅ Complete | Using new endpoint + helpers |
| `main.py:951` | `_execute_filter_search()` | ⏳ Pending | High priority - used in production |
| `main.py:1137` | Unknown method | ⏳ Pending | Need to identify context |
| `main.py:1498` | Unknown method | ⏳ Pending | Need to identify context |
| `main.py:1662` | Unknown method | ⏳ Pending | Need to identify context |
| `main.py:1780` | Unknown method | ⏳ Pending | Need to identify context |

## 🚀 Rollout Plan

### Phase 1: Development (Current)
- ✅ SearchHandler migrated
- ✅ Helper functions created
- ✅ Documentation complete

### Phase 2: Gradual Migration
- [ ] Add feature flag `USE_NEW_EXTRACTION_ENDPOINT`
- [ ] Migrate `_execute_filter_search()` with fallback
- [ ] Monitor logs for errors
- [ ] Enable flag for 10% of traffic

### Phase 3: Full Migration
- [ ] Migrate remaining methods
- [ ] Enable flag for 100% of traffic
- [ ] Remove old extraction handling code
- [ ] Update tests

### Phase 4: Cleanup
- [ ] Remove feature flag
- [ ] Remove legacy compatibility code
- [ ] Archive old extraction endpoint

## 🐛 Common Issues & Solutions

### Issue: "extraction_result.get() returns None"

**Cause**: Extraction service returned old format
**Solution**: Use `convert_legacy_extraction_response()` adapter

### Issue: "RAG service can't find properties with filters"

**Cause**: Filter field names don't match (e.g., `district` vs `district_id`)
**Solution**: Helper function handles both for backward compatibility

### Issue: "Extraction confidence is low"

**Cause**: Master data not matching user input
**Solution**: Check `new` array in response - items need to be added to master data

## 📚 Related Documentation

- [Master Data Extraction Implementation Guide](./MASTER_DATA_EXTRACTION_IMPLEMENTATION_GUIDE.md)
- [Database Schema](../database/migrations/001_create_master_data_schema.sql)
- [Extraction Models](../shared/models/attribute_extraction.py)

---

**Last Updated**: 2025-01-13
**Owner**: REE AI Backend Team
**Status**: In Progress - Phase 1 Complete

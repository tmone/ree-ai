# Language Detection Guide

**Auto-detect user's preferred language from multiple sources**

---

## Overview

The REE AI platform supports automatic language detection from:
1. **User profile** (from database) - highest priority
2. **HTTP Accept-Language header** (from browser)
3. **Country code** (from IP geolocation)
4. **Default fallback** (Vietnamese)

---

## Quick Start

### Option 1: Auto-Detection (Recommended)

```python
from fastapi import FastAPI, Request, Header
from shared.utils.i18n import t, auto_detect_language
from typing import Optional

app = FastAPI()

@app.post("/my-endpoint")
async def my_endpoint(
    request: Request,
    user_id: Optional[str] = None,
    accept_language: Optional[str] = Header(None)
):
    # Auto-detect language
    language = await auto_detect_language(
        user_id=user_id,
        accept_language=accept_language
    )

    # Use detected language
    response_message = t("my_service.success", language=language)

    return {"message": response_message, "language": language}
```

### Option 2: Manual Detection from Header

```python
from fastapi import Header
from shared.utils.i18n import detect_language_from_header
from typing import Optional

@app.post("/my-endpoint")
async def my_endpoint(
    accept_language: Optional[str] = Header(None)
):
    # Detect from Accept-Language header only
    language = detect_language_from_header(accept_language)

    # Use detected language
    response = t("my_service.success", language=language)

    return {"message": response}
```

### Option 3: User Profile Detection

```python
from shared.utils.i18n import detect_language_from_user_profile

@app.post("/my-endpoint")
async def my_endpoint(user_id: str):
    # Detect from user profile in database
    language = await detect_language_from_user_profile(user_id)

    # Fallback to Vietnamese if not found
    if not language:
        language = 'vi'

    response = t("my_service.success", language=language)

    return {"message": response}
```

---

## Detection Functions

### 1. `auto_detect_language()`

**Most comprehensive - detects from all sources**

```python
language = await auto_detect_language(
    user_id="user123",                    # Optional: from database
    accept_language="en-US,en;q=0.9",     # Optional: from HTTP header
    country_code="TH",                     # Optional: from IP geolocation
    db_gateway_url="http://localhost:8081", # Optional: custom DB gateway URL
    default="vi"                           # Optional: fallback language
)
```

**Priority order:**
1. User profile (database)
2. Accept-Language header
3. Country code
4. Default fallback

### 2. `detect_language_from_header()`

**Detect from HTTP Accept-Language header**

```python
from shared.utils.i18n import detect_language_from_header

language = detect_language_from_header("vi-VN,vi;q=0.9,en-US;q=0.8")
# Returns: 'vi'

language = detect_language_from_header("th-TH,th;q=0.9,en;q=0.8")
# Returns: 'th'

language = detect_language_from_header("ja-JP,ja;q=0.9")
# Returns: 'ja'
```

**Supported header formats:**
- `vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7` (with quality values)
- `en-US,en` (without quality values)
- `th` (simple format)

### 3. `detect_language_from_user_profile()`

**Fetch user's language preference from database**

```python
from shared.utils.i18n import detect_language_from_user_profile

language = await detect_language_from_user_profile(
    user_id="user123",
    db_gateway_url="http://localhost:8081"
)

if language:
    print(f"User prefers: {language}")
else:
    print("No language preference found")
```

**Requirements:**
- User must have `preferred_language` field in profile
- DB Gateway must be accessible
- Returns `None` if user not found or no preference set

### 4. `detect_language_from_country_code()`

**Map country code to language**

```python
from shared.utils.i18n import detect_language_from_country_code

language = detect_language_from_country_code('VN')  # Returns: 'vi'
language = detect_language_from_country_code('TH')  # Returns: 'th'
language = detect_language_from_country_code('JP')  # Returns: 'ja'
language = detect_language_from_country_code('US')  # Returns: 'en'
```

**Supported countries:**
- `VN` → Vietnamese (vi)
- `TH` → Thai (th)
- `JP` → Japanese (ja)
- `US`, `GB`, `AU`, `CA`, `SG` → English (en)
- Others → Vietnamese (vi) - fallback

---

## Integration Examples

### Example 1: FastAPI Service with Auto-Detection

```python
from fastapi import FastAPI, Request, Header
from shared.utils.i18n import t, auto_detect_language
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class SearchRequest(BaseModel):
    query: str
    user_id: Optional[str] = None

@app.post("/search")
async def search(
    request: SearchRequest,
    accept_language: Optional[str] = Header(None)
):
    # Auto-detect language
    language = await auto_detect_language(
        user_id=request.user_id,
        accept_language=accept_language
    )

    # Use detected language throughout
    try:
        results = perform_search(request.query)

        return {
            "message": t("search.found_properties", language=language, count=len(results)),
            "results": results,
            "language": language
        }
    except Exception as e:
        return {
            "error": t("errors.system_error", language=language),
            "language": language
        }
```

### Example 2: Orchestrator with Language Detection

```python
from fastapi import FastAPI, Header
from shared.utils.i18n import t, detect_language_from_header
from typing import Optional

app = FastAPI()

@app.post("/orchestrate")
async def orchestrate(
    query: str,
    user_id: Optional[str] = None,
    accept_language: Optional[str] = Header(None)
):
    # Detect language (header only for quick detection)
    language = detect_language_from_header(accept_language)

    # Override with explicit language if provided by user
    # (This allows users to explicitly switch language)
    if user_id:
        from shared.utils.i18n import detect_language_from_user_profile
        user_lang = await detect_language_from_user_profile(user_id)
        if user_lang:
            language = user_lang

    # Process with detected language
    response = process_query(query, language)

    return {
        "response": response,
        "language": language
    }
```

### Example 3: Validation Service with Language Detection

```python
from fastapi import FastAPI, Header
from shared.utils.i18n import t, detect_language_from_header
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class ValidationRequest(BaseModel):
    intent: str
    entities: dict
    language: Optional[str] = None  # Allow explicit override

@app.post("/validate")
async def validate(
    request: ValidationRequest,
    accept_language: Optional[str] = Header(None)
):
    # Use explicit language if provided, otherwise detect
    if request.language:
        language = request.language
    else:
        language = detect_language_from_header(accept_language)

    # Validate with detected language
    errors = []
    if not request.entities.get("price"):
        errors.append(
            t("validation.field_presence_missing_required",
              language=language,
              field="price")
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "language": language
    }
```

---

## Testing Language Detection

### Unit Tests

```python
import pytest
from shared.utils.i18n import (
    detect_language_from_header,
    detect_language_from_country_code
)

def test_detect_from_header_vietnamese():
    lang = detect_language_from_header("vi-VN,vi;q=0.9,en-US;q=0.8")
    assert lang == 'vi'

def test_detect_from_header_thai():
    lang = detect_language_from_header("th-TH,th;q=0.9")
    assert lang == 'th'

def test_detect_from_country_code():
    assert detect_language_from_country_code('VN') == 'vi'
    assert detect_language_from_country_code('TH') == 'th'
    assert detect_language_from_country_code('JP') == 'ja'
    assert detect_language_from_country_code('US') == 'en'
```

### Manual Testing with cURL

```bash
# Test with Vietnamese Accept-Language
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -H "Accept-Language: vi-VN,vi;q=0.9,en-US;q=0.8" \
  -d '{"query": "tìm nhà"}'

# Test with Thai Accept-Language
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -H "Accept-Language: th-TH,th;q=0.9,en;q=0.8" \
  -d '{"query": "หาบ้าน"}'

# Test with English Accept-Language
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -H "Accept-Language: en-US,en;q=0.9" \
  -d '{"query": "find house"}'
```

---

## Best Practices

### 1. Always Provide Fallback

```python
# ✅ CORRECT
language = detect_language_from_header(accept_language)
if not language:
    language = 'vi'  # Fallback

# ❌ WRONG
language = detect_language_from_header(accept_language)
# No fallback - could be None
```

### 2. Allow Explicit Language Override

```python
class MyRequest(BaseModel):
    query: str
    language: Optional[str] = None  # Allow explicit override

@app.post("/endpoint")
async def endpoint(
    request: MyRequest,
    accept_language: Optional[str] = Header(None)
):
    # Explicit language takes priority
    if request.language:
        language = request.language
    else:
        language = detect_language_from_header(accept_language)
```

### 3. Cache User Language Preference

```python
# Cache user's detected language for session
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_user_language(user_id: str) -> str:
    lang = await detect_language_from_user_profile(user_id)
    return lang if lang else 'vi'
```

### 4. Log Language Detection for Analytics

```python
language = await auto_detect_language(
    user_id=user_id,
    accept_language=accept_language
)

# Log for analytics
logger.info(f"Detected language: {language} for user {user_id}")
```

---

## Troubleshooting

### Issue: Language detection returns wrong language

**Check:**
1. Verify Accept-Language header format
2. Check user profile has `preferred_language` field
3. Ensure DB Gateway is accessible
4. Check country code mapping

### Issue: Language not persisting across requests

**Solution:** Store detected language in session or user profile

```python
# Update user profile with detected language
await update_user_language_preference(user_id, detected_language)
```

### Issue: Performance concerns with database lookups

**Solution:** Implement caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache for 1 hour
@lru_cache(maxsize=1000)
async def get_user_language_cached(user_id: str, cache_time: datetime) -> str:
    return await detect_language_from_user_profile(user_id)

# Usage
cache_key = datetime.now().replace(minute=0, second=0, microsecond=0)
language = await get_user_language_cached(user_id, cache_key)
```

---

## References

- **I18N Utility:** `shared/utils/i18n.py`
- **Translation Files:** `shared/data/translations/messages.*.json`
- **Quick Reference:** `docs/I18N_QUICK_REFERENCE.md`
- **Refactoring Summary:** `docs/I18N_REFACTORING_SUMMARY.md`

---

**Status:** ✅ Language detection fully implemented and tested
**Supported Languages:** Vietnamese (vi), English (en), Thai (th), Japanese (ja)
**Last Updated:** 2025-01-18

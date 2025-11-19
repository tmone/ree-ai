# I18N Quick Reference Guide

**For Developers:** Quick guide to adding i18n support to new services or features

---

## 🚀 Quick Start (5 Steps)

### Step 1: Import the i18n helper

```python
from shared.utils.i18n import t
```

### Step 2: Add language field to your request model

```python
from pydantic import BaseModel

class MyServiceRequest(BaseModel):
    query: str
    some_param: int
    language: str = "vi"  # ⭐ Add this!
```

### Step 3: Replace hardcoded strings with t() calls

```python
# ❌ BEFORE (Hardcoded)
error_message = "Không thể xử lý yêu cầu"
raise HTTPException(status_code=500, detail=error_message)

# ✅ AFTER (I18n)
error_message = t("my_service.processing_failed", language=request.language)
raise HTTPException(status_code=500, detail=error_message)
```

### Step 4: Add translation keys to translation files

**File: `shared/data/translations/messages.vi.json`**
```json
{
  "my_service": {
    "processing_failed": "Không thể xử lý yêu cầu"
  }
}
```

**File: `shared/data/translations/messages.en.json`**
```json
{
  "my_service": {
    "processing_failed": "Unable to process request"
  }
}
```

### Step 5: Pass language parameter to all functions

```python
def my_helper_function(data: Dict, language: str = 'vi') -> str:
    if not data:
        return t("my_service.no_data", language=language)
    # ...
```

---

## 📖 Common Patterns

### Pattern 1: Error Messages with Variables

```python
# Python code
error_msg = t(
    "validation.field_too_low",
    language=request.language,
    field="price",
    min_value="1000000"
)

# Translation file (messages.vi.json)
{
  "validation": {
    "field_too_low": "{field} quá thấp (tối thiểu: {min_value})"
  }
}

# Translation file (messages.en.json)
{
  "validation": {
    "field_too_low": "{field} too low (minimum: {min_value})"
  }
}

# Output (vi): "price quá thấp (tối thiểu: 1000000)"
# Output (en): "price too low (minimum: 1000000)"
```

### Pattern 2: Lists of Messages

```python
# Python code
messages = []
if missing_fields:
    for field in missing_fields:
        messages.append(
            t("validation.missing_field", language=language, field=field)
        )
```

### Pattern 3: Conditional Messages

```python
# Python code
if score >= 90:
    interpretation = t("completeness.score_excellent", language=language)
elif score >= 80:
    interpretation = t("completeness.score_good", language=language)
else:
    interpretation = t("completeness.score_poor", language=language)
```

### Pattern 4: HTTPException Messages

```python
# Python code
try:
    result = process_data()
except Exception as e:
    error_msg = t(
        "my_service.processing_error",
        language=request.language,
        error=str(e)
    )
    raise HTTPException(status_code=500, detail=error_msg)
```

---

## ✅ Checklist for New Features

When adding a new feature that interacts with users:

- [ ] Import `t` helper: `from shared.utils.i18n import t`
- [ ] Add `language: str = "vi"` field to request model
- [ ] Replace ALL hardcoded user-facing strings with `t()` calls
- [ ] Add translation keys to `messages.vi.json`
- [ ] Add English translations to `messages.en.json`
- [ ] Pass `language` parameter to all helper functions
- [ ] Test with both `language="vi"` and `language="en"`
- [ ] Update this document if you discover new patterns!

---

## 🎯 Translation Key Naming Convention

Use hierarchical naming: `<service>.<category>.<specific>`

**Examples:**
```
validation.field_presence.missing_required
validation.data_format.invalid_phone
classification.core_gateway_error
attribute_extraction.clarify_property_type
completeness.score_excellent
```

**Categories by service:**
- **validation:** field_presence, data_format, logical, spam, duplicate
- **classification:** errors, fallback
- **reranking:** errors, analytics
- **attribute_extraction:** clarify, suggestion, label, display
- **completeness:** score, missing, strength, suggestion, priority

---

## 🚫 Common Mistakes to Avoid

### ❌ Mistake 1: Hardcoding Vietnamese in code
```python
# ❌ WRONG
return "Bạn muốn tìm loại bất động sản nào?"
```

### ✅ Fix: Use t() helper
```python
# ✅ CORRECT
return t("attribute_extraction.clarify_property_type", language=language)
```

---

### ❌ Mistake 2: Forgetting to pass language parameter
```python
# ❌ WRONG
def validate_field(data):
    return t("validation.missing_field", field="price")  # No language!
```

### ✅ Fix: Always pass language
```python
# ✅ CORRECT
def validate_field(data, language='vi'):
    return t("validation.missing_field", language=language, field="price")
```

---

### ❌ Mistake 3: Using f-strings with translations
```python
# ❌ WRONG
error = t("validation.error", language=language)
return f"{error}: {details}"  # Mixing Vietnamese + English!
```

### ✅ Fix: Include variables in translation
```python
# ✅ CORRECT
return t("validation.error_with_details", language=language, details=details)

# Translation:
# "validation.error_with_details": "Lỗi: {details}"
```

---

### ❌ Mistake 4: Not adding English translation
```python
# messages.vi.json ✅
{
  "my_service": {
    "error": "Đã xảy ra lỗi"
  }
}

# messages.en.json ❌ (Missing!)
{
  "my_service": {}  # Forgot to add "error" key!
}
```

### ✅ Fix: Always add both Vietnamese and English
```python
# messages.en.json ✅
{
  "my_service": {
    "error": "An error occurred"
  }
}
```

---

## 📝 Example: Adding a New Service

Let's say you're creating a new "Property Comparison Service":

**1. Create request model with language:**
```python
# services/property_comparison/main.py

from shared.utils.i18n import t

class ComparisonRequest(BaseModel):
    property_ids: List[str]
    language: str = "vi"  # ⭐ Don't forget!
```

**2. Add translation keys:**
```json
// shared/data/translations/messages.vi.json
{
  "property_comparison": {
    "comparison_complete": "So sánh hoàn tất",
    "property_not_found": "Không tìm thấy bất động sản: {property_id}",
    "too_many_properties": "Chỉ có thể so sánh tối đa {max} bất động sản",
    "similarity_high": "Hai bất động sản rất giống nhau",
    "similarity_medium": "Hai bất động sản khá giống nhau",
    "similarity_low": "Hai bất động sản khác nhau nhiều"
  }
}

// shared/data/translations/messages.en.json
{
  "property_comparison": {
    "comparison_complete": "Comparison complete",
    "property_not_found": "Property not found: {property_id}",
    "too_many_properties": "Can only compare up to {max} properties",
    "similarity_high": "Properties are very similar",
    "similarity_medium": "Properties are moderately similar",
    "similarity_low": "Properties are quite different"
  }
}
```

**3. Use t() in your service:**
```python
@app.post("/compare", response_model=ComparisonResponse)
async def compare_properties(request: ComparisonRequest):
    try:
        # Validate
        if len(request.property_ids) > 5:
            error_msg = t(
                "property_comparison.too_many_properties",
                language=request.language,
                max=5
            )
            raise HTTPException(status_code=400, detail=error_msg)

        # Check existence
        for prop_id in request.property_ids:
            if not await property_exists(prop_id):
                error_msg = t(
                    "property_comparison.property_not_found",
                    language=request.language,
                    property_id=prop_id
                )
                raise HTTPException(status_code=404, detail=error_msg)

        # Compare
        similarity = calculate_similarity(...)

        # Return result
        if similarity > 0.8:
            interpretation = t("property_comparison.similarity_high", language=request.language)
        elif similarity > 0.5:
            interpretation = t("property_comparison.similarity_medium", language=request.language)
        else:
            interpretation = t("property_comparison.similarity_low", language=request.language)

        return ComparisonResponse(
            similarity=similarity,
            interpretation=interpretation
        )

    except Exception as e:
        # Note: Using generic error key from common namespace
        error_msg = t("errors.system_error", language=request.language)
        raise HTTPException(status_code=500, detail=error_msg)
```

**4. Test both languages:**
```bash
# Test Vietnamese
curl -X POST http://localhost:8080/compare \
  -H "Content-Type: application/json" \
  -d '{
    "property_ids": ["prop1", "prop2", "prop3", "prop4", "prop5", "prop6"],
    "language": "vi"
  }'
# Expected: "Chỉ có thể so sánh tối đa 5 bất động sản"

# Test English
curl -X POST http://localhost:8080/compare \
  -H "Content-Type: application/json" \
  -d '{
    "property_ids": ["prop1", "prop2", "prop3", "prop4", "prop5", "prop6"],
    "language": "en"
  }'
# Expected: "Can only compare up to 5 properties"
```

---

## 🔍 Finding Existing Translation Keys

To find existing keys you can reuse:

```bash
# Search for specific keywords in translation files
grep -r "property" shared/data/translations/

# View all validation keys
cat shared/data/translations/messages.vi.json | grep "validation"

# Count total translation keys
cat shared/data/translations/messages.vi.json | grep -c '":"'
```

---

## 📚 Reference Services

**Best examples to follow:**

1. **Orchestrator** - 335+ `t()` calls, perfect i18n compliance
2. **Validation Service** - Comprehensive error messages, warnings, suggestions
3. **Attribute Extraction** - Complex clarification questions with variables
4. **Completeness Service** - Extensive fallback logic with i18n

**Check these files for examples:**
- `services/orchestrator/main.py`
- `services/validation/validators/field_presence.py`
- `services/attribute_extraction/main.py` (line 1208+)
- `services/completeness/main.py` (line 177+)

---

## 🌍 Supported Languages

Currently supported:
- ✅ **Vietnamese (vi)** - Default, 100% complete (169 keys)
- ✅ **English (en)** - 100% complete (169 keys)
- ✅ **Thai (th)** - 100% complete (169 keys)
- ✅ **Japanese (ja)** - 100% complete (169 keys)

All languages have complete translations for all user-facing services!

To add a new language, copy `messages.en.json`, rename to `messages.{lang}.json`, and translate all keys.

---

## ❓ FAQ

**Q: Do internal services need i18n?**
A: No! Only user-facing services need i18n. Internal APIs (RAG Service, DB Gateway, Core Gateway) don't need it.

**Q: What if I forget to add English translation?**
A: The system will fall back to the key name. Always add both Vietnamese and English!

**Q: Can I nest variables in translations?**
A: Yes! Example: `"error": "Lỗi {type}: {details}"`

**Q: How do I test language switching?**
A: Include `"language": "vi"` or `"language": "en"` in your request JSON.

**Q: Where do I add new translation keys?**
A: `shared/data/translations/messages.vi.json` and `messages.en.json`

---

## 🔍 Auto-Detect User Language (New!)

REE AI can automatically detect the user's preferred language from multiple sources:

### Quick Usage

```python
from fastapi import Header
from shared.utils.i18n import t, auto_detect_language
from typing import Optional

@app.post("/my-endpoint")
async def my_endpoint(
    user_id: Optional[str] = None,
    accept_language: Optional[str] = Header(None)
):
    # Auto-detect language
    language = await auto_detect_language(
        user_id=user_id,
        accept_language=accept_language
    )

    # Use detected language
    response = t("my_service.success", language=language)
    return {"message": response}
```

### Detection Sources (Priority Order)

1. **User Profile** (from database) - highest priority
2. **Accept-Language Header** (from browser)
3. **Country Code** (from IP geolocation)
4. **Default** (Vietnamese) - fallback

### Available Functions

```python
from shared.utils.i18n import (
    auto_detect_language,              # Auto-detect from all sources
    detect_language_from_header,       # From HTTP Accept-Language
    detect_language_from_user_profile, # From user profile in DB
    detect_language_from_country_code  # From country code
)

# Example: Detect from header only
language = detect_language_from_header("en-US,en;q=0.9")  # Returns: 'en'
```

**Full guide:** `docs/LANGUAGE_DETECTION_GUIDE.md`

---

## 🧪 Testing Your I18N Implementation

### Automated Tests

**Run i18n integration tests:**
```bash
pytest tests/test_i18n_services.py -v
```

**Verify translation completeness:**
```bash
python tests/verify_i18n_completeness.py
```

**Expected output:**
```
[OK] Vietnamese keys: 169
[OK] English keys: 169
[OK] Thai keys: 169
[OK] Japanese keys: 169
[OK] All keys used in code are properly defined
[SUCCESS] I18N implementation is complete and correct!
```

### Before Committing

Always run the verification script to ensure:
- ✅ All 4 languages have synchronized translation keys
- ✅ All translation keys used in code are defined
- ✅ No missing translation keys

**Pre-commit hook available:** `.githooks/pre-commit-i18n.sh`

---

## 🎓 Additional Resources

- **Full documentation:** `docs/I18N_REFACTORING_SUMMARY.md`
- **Testing guide:** `tests/README_I18N_TESTS.md`
- **Helper function source:** `shared/utils/i18n.py`
- **Translation files:** `shared/data/translations/messages.*.json`
- **CLAUDE.md:** Repository coding standards and i18n policy

---

**Happy coding! 🚀 Remember: Every user-facing string deserves i18n! 🌍**

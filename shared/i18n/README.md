# REE AI Multilingual Translation System

## Overview

REE AI supports **multilingual user interactions** while maintaining **English master data** in the database.

### Core Principle

```
User Input (Any Language) → Extraction → English Master Data → Database
Database → English Data → Translation → User Language → Response
```

**Why English for Master Data?**
- ✅ **Standardization**: One canonical format across the system
- ✅ **Interoperability**: English is the universal language for tech
- ✅ **Data Quality**: Easier to validate and deduplicate
- ✅ **AI Performance**: LLMs perform better with English data
- ✅ **Global Expansion**: Easy to add new languages without changing DB schema

**Why Multilingual UI?**
- ✅ **User Experience**: Users speak Vietnamese, Chinese, etc.
- ✅ **Market Reach**: Support multiple markets
- ✅ **Natural Interaction**: Users ask in their native language

---

## Architecture

### Layer 1: User Input (Multilingual)

User queries can be in **any supported language**:

```python
# Vietnamese
"Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ"

# English
"Find apartment 2 bedrooms district 7 under 3 billion"

# Chinese
"找公寓两房第七郡低于30亿"
```

### Layer 2: Extraction Service (Language-Agnostic)

Extraction service extracts entities **in the user's language**:

```json
// Vietnamese extraction
{
  "property_type": "căn hộ",
  "bedrooms": 2,
  "district": "quận 7",
  "max_price": 3000000000
}
```

### Layer 3: Translation Mapper (Normalization)

**CRITICAL STEP**: Multilingual Mapper converts to English:

```python
from shared.i18n import get_multilingual_mapper

mapper = get_multilingual_mapper()

# Vietnamese → English
normalized = mapper.normalize_entities({
    "property_type": "căn hộ",
    "district": "q7",
    "bedrooms": 2
}, source_lang="vi")

# Output: English master data
{
    "property_type": "apartment",
    "district": "District 7",
    "bedrooms": 2
}
```

### Layer 4: Database Storage (English Only)

```json
// OpenSearch document (English)
{
  "property_id": "123",
  "property_type": "apartment",  // ✅ English
  "district": "District 7",      // ✅ English
  "bedrooms": 2,
  "price": 2500000000
}
```

### Layer 5: Response Translation (User Language)

When returning data to user, translate back:

```python
# Database → User language
translated = mapper.translate_entities({
    "property_type": "apartment",
    "district": "District 7"
}, target_lang="vi")

# Output: Vietnamese for UI
{
    "property_type": "căn hộ",
    "district": "Quận 7"
}
```

---

## Supported Languages

| Language | Code | Status | Coverage |
|----------|------|--------|----------|
| **English** | `en` | ✅ Active | Master data standard |
| **Vietnamese** | `vi` | ✅ Active | Primary market (100% coverage) |
| **Chinese** | `zh` | 🚧 Partial | Secondary market (partial coverage) |

---

## Translation Mappings

### Property Types

| English (Master) | Vietnamese | Chinese | Aliases |
|------------------|------------|---------|---------|
| `apartment` | căn hộ | 公寓 | condo, flat, chung cư |
| `villa` | biệt thự | 别墅 | detached house |
| `townhouse` | nhà phố | 联排别墅 | row house, nhà liền kề |
| `land` | đất | 土地 | vacant land, đất nền |
| `office` | văn phòng | 办公室 | office space |
| `commercial` | mặt bằng | 商铺 | shop, retail space |

### Districts (HCMC)

| English (Master) | Vietnamese | Chinese | Aliases |
|------------------|------------|---------|---------|
| `District 1` | Quận 1 | 第一郡 | Q1, D1, quan 1 |
| `District 2` | Quận 2 | 第二郡 | Q2, D2, quan 2 |
| `District 7` | Quận 7 | 第七郡 | Q7, D7, Phu My Hung |
| `Binh Thanh District` | Quận Bình Thạnh | 平盛郡 | Binh Thanh |
| `Thu Duc City` | Thành phố Thủ Đức | 守德市 | Thu Duc, Thủ Đức |

### Amenities

| English (Master) | Vietnamese | Chinese | Aliases |
|------------------|------------|---------|---------|
| `swimming_pool` | hồ bơi | 游泳池 | pool, bể bơi |
| `gym` | phòng gym | 健身房 | fitness center |
| `parking` | chỗ đậu xe | 停车场 | garage, nhà để xe |
| `elevator` | thang máy | 电梯 | lift |
| `security` | bảo vệ 24/7 | 24小时保安 | security guard |

---

## Usage Examples

### Example 1: Vietnamese → English (Extraction)

```python
from shared.i18n import get_multilingual_mapper

mapper = get_multilingual_mapper()

# User query in Vietnamese
user_query = "Tìm căn hộ 2PN quận 7 có hồ bơi"

# After extraction (Vietnamese entities)
extracted = {
    "property_type": "căn hộ",
    "bedrooms": 2,
    "district": "q7",
    "swimming_pool": True
}

# Normalize to English for DB
normalized = mapper.normalize_entities(extracted, source_lang="vi")

print(normalized)
# Output:
# {
#     "property_type": "apartment",
#     "bedrooms": 2,
#     "district": "District 7",
#     "swimming_pool": True
# }
```

### Example 2: English → Vietnamese (Display)

```python
# Data from database (English)
db_result = {
    "property_type": "apartment",
    "district": "District 7",
    "bedrooms": 2,
    "price": 2500000000
}

# Translate for Vietnamese user
translated = mapper.translate_entities(db_result, target_lang="vi")

print(translated)
# Output:
# {
#     "property_type": "căn hộ",
#     "district": "Quận 7",
#     "bedrooms": 2,
#     "price": 2500000000
# }
```

### Example 3: Integration with Extraction Service

```python
# In services/attribute_extraction/main.py

from shared.i18n import get_multilingual_mapper

class AttributeExtractionService(BaseService):
    def __init__(self):
        super().__init__(...)
        self.multilingual_mapper = get_multilingual_mapper()

    async def extract_from_query_enhanced(self, request):
        # 1. Extract entities (may be in Vietnamese)
        entities = await self._call_llm_for_extraction(prompt)

        # 2. CRITICAL: Normalize to English
        normalized_entities = self.multilingual_mapper.normalize_entities(
            entities,
            source_lang="vi"
        )

        # 3. Return English entities (ready for DB storage)
        return EnhancedExtractionResponse(
            entities=normalized_entities  # ✅ English
        )
```

### Example 4: Auto-detect Language

```python
def detect_language(text: str) -> str:
    """Simple language detection based on character set"""
    # Contains Vietnamese diacritics
    if any(c in text for c in "ăâđêôơưáàảãạấầẩẫậ"):
        return "vi"
    # Contains Chinese characters
    elif any('\u4e00' <= c <= '\u9fff' for c in text):
        return "zh"
    else:
        return "en"

# Usage
query = "Tìm căn hộ quận 7"
lang = detect_language(query)  # Returns "vi"

normalized = mapper.normalize_entities(entities, source_lang=lang)
```

---

## Adding New Languages

To add support for a new language (e.g., Korean):

### Step 1: Add Translation Entries

```python
# In shared/i18n/multilingual_mapper.py

class PropertyTypeTranslations:
    TRANSLATIONS = [
        TranslationEntry(
            english="apartment",
            vietnamese="căn hộ",
            chinese="公寓",
            korean="아파트",  # Add Korean
            aliases={
                "en": ["condo", "flat"],
                "vi": ["can ho", "chung cư"],
                "zh": ["公寓"],
                "ko": ["아파트", "콘도"]  # Add Korean aliases
            }
        ),
        # ...
    ]
```

### Step 2: Update Language Enum

```python
class Language(str, Enum):
    ENGLISH = "en"
    VIETNAMESE = "vi"
    CHINESE = "zh"
    KOREAN = "ko"  # Add Korean
```

### Step 3: Update Mapper

```python
# In MultilingualMapper._build_indices()

for entry in PropertyTypeTranslations.TRANSLATIONS:
    # Add Korean
    if entry.korean:
        self.property_type_to_english[entry.korean.lower()] = entry.english

    # Reverse index
    self.property_type_from_english[entry.english.lower()] = {
        "en": entry.english,
        "vi": entry.vietnamese,
        "zh": entry.chinese or entry.english,
        "ko": entry.korean or entry.english  # Add Korean
    }
```

---

## Testing

### Unit Tests

```bash
# Run translation tests
pytest tests/test_multilingual_mapper.py -v
```

### Manual Testing

```python
# Test script
from shared.i18n import get_multilingual_mapper

mapper = get_multilingual_mapper()

# Test Vietnamese → English
test_cases = [
    ("căn hộ", "apartment"),
    ("q7", "District 7"),
    ("hồ bơi", "swimming_pool"),
]

for vi, expected_en in test_cases:
    result = mapper.to_english("property_type", vi)
    assert result == expected_en, f"Failed: {vi} → {result} (expected {expected_en})"

print("✅ All tests passed!")
```

---

## Best Practices

### ✅ DO:
- **Always normalize** extracted entities to English before DB storage
- **Always translate** DB results to user language before display
- **Use master data mappings** for consistency
- **Add aliases** for common variations (q7, Q.7, quận 7)
- **Handle missing translations** gracefully (fallback to English)

### ❌ DON'T:
- **Don't store multilingual data** in the database (English only!)
- **Don't bypass the mapper** - always use normalize_entities()
- **Don't hardcode translations** in prompts
- **Don't assume user language** - detect or ask
- **Don't mix languages** in single field (e.g., "căn hộ in District 7")

---

## Troubleshooting

### Issue: Entities not normalized

**Problem:**
```python
# Entities still in Vietnamese after extraction
{"property_type": "căn hộ"}  # ❌ Should be "apartment"
```

**Solution:**
```python
# Make sure to call normalize_entities()
normalized = mapper.normalize_entities(entities, source_lang="vi")
```

### Issue: Translation not found

**Problem:**
```python
mapper.to_english("property_type", "penthouse")  # Returns None
```

**Solution:**
```python
# Add missing translation to PropertyTypeTranslations
TranslationEntry(
    english="penthouse",
    vietnamese="căn hộ penthouse",
    aliases={"vi": ["penthouse", "căn hộ cao cấp"]}
)
```

### Issue: Mixed language output

**Problem:**
```python
{"property_type": "apartment", "district": "Quận 7"}  # Mixed!
```

**Solution:**
```python
# Ensure ALL fields are normalized
normalized = mapper.normalize_entities(entities, source_lang="vi")
# Now: {"property_type": "apartment", "district": "District 7"}
```

---

## Performance Considerations

- **Mapper is singleton**: Initialized once, reused across requests
- **Lookup indices**: O(1) dictionary lookups for translations
- **No database calls**: All translations in-memory
- **Lazy loading**: Translation tables loaded on first use

**Benchmarks** (on standard laptop):
- Single translation: ~0.001ms
- Normalize 10 entities: ~0.01ms
- Batch translate 100 properties: ~1ms

---

## Future Enhancements

1. **Auto language detection** from query text
2. **Fuzzy matching** for typos/variations
3. **ML-based translation** for unknown terms
4. **User language preferences** stored in profile
5. **Translation caching** in Redis
6. **Dynamic translation updates** without code changes

---

## Related Documentation

- Master Data: `shared/master_data/README.md`
- Extraction Service: `services/attribute_extraction/README_ENHANCED.md`
- API Design: `docs/API_DESIGN.md`

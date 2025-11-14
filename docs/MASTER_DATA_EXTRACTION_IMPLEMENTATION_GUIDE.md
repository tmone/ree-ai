# Master Data Extraction Implementation Guide

## 🎯 Overview

This guide documents the complete implementation of **multi-language master data extraction** for REE AI. The system stores canonical data in English with multi-language translations, and returns extraction results with both master data IDs and user-language translations.

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ User Input (Any Language)                                    │
│ "Căn hộ 2PN Quận 1, hướng Đông, có hồ bơi"                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Language Detection (langdetect)                           │
│    → Detected: "vi" (Vietnamese)                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. LLM Extraction                                            │
│    → Extract raw attributes from text                        │
│    → Output: {property_type: "căn hộ", district: "Q1", ...} │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Fuzzy Match with Master Data + Translations              │
│    ┌─────────────────────────────────────────────────────┐  │
│    │ Query master_data + translations WHERE:             │  │
│    │ - Exact match: name_vi = 'căn hộ'                   │  │
│    │ - Alias match: name_variants @> 'can ho'            │  │
│    │ - Fuzzy match: similarity(name_vi, 'căn hộ') > 0.8  │  │
│    └─────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Return 3-Tier Response                                    │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ raw: {text, bedrooms: 2, area: null, price: null}    │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ mapped: [                                             │   │
│ │   {                                                   │   │
│ │     property_name: "property_type",                  │   │
│ │     table: "property_types",                         │   │
│ │     id: 1,                    ← Master data ID       │   │
│ │     value: "apartment",       ← English canonical    │   │
│ │     value_translated: "Căn hộ", ← User's language   │   │
│ │     confidence: 0.98                                 │   │
│ │   },                                                  │   │
│ │   {property_name: "district", id: 1, ...}            │   │
│ │ ]                                                     │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ new: [                                                │   │
│ │   {                                                   │   │
│ │     property_name: "amenity",                        │   │
│ │     value: "wine_cellar",     ← LLM translated to EN │   │
│ │     value_original: "hầm rượu", ← User's original   │   │
│ │     suggested_table: "amenities",                    │   │
│ │     requires_admin_review: true                      │   │
│ │   }                                                   │   │
│ │ ]                                                     │   │
│ └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Database Schema

### Master Data Tables (English Canonical)

Created in: `database/migrations/001_create_master_data_schema.sql`

Each master data table follows this pattern:

```sql
-- Master table (English canonical)
CREATE TABLE property_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,  -- English only: "apartment"
    code VARCHAR(50) NOT NULL UNIQUE,   -- "apartment"
    category VARCHAR(50),
    icon VARCHAR(50),
    description TEXT
);

-- Translation table (separate)
CREATE TABLE property_types_translations (
    id SERIAL PRIMARY KEY,
    property_type_id INT NOT NULL REFERENCES property_types(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,      -- 'vi', 'en', 'zh', 'ko', 'ja'
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(property_type_id, lang_code)
);
```

### Master Data Tables

1. **Location (Hierarchical)**
   - `cities` + `cities_translations`
   - `districts` + `districts_translations`
   - `wards` + `wards_translations`
   - `streets` + `streets_translations`

2. **Property Attributes**
   - `property_types` + `property_types_translations`
   - `amenities` + `amenities_translations`
   - `directions` + `directions_translations`
   - `furniture_types` + `furniture_types_translations`
   - `legal_statuses` + `legal_statuses_translations`
   - `view_types` + `view_types_translations`

3. **Pending Review**
   - `pending_master_data` - Stores unmatched items for admin approval

### Seed Data

Created in: `database/migrations/002_seed_master_data.sql`

- ✅ 2 cities (HCMC, Hanoi)
- ✅ 25 HCMC districts (all 22 urban + 3 suburban)
- ✅ 12 property types (apartment, villa, townhouse, etc.)
- ✅ 27 amenities (swimming pool, gym, parking, etc.)
- ✅ 8 directions (N, NE, E, SE, S, SW, W, NW)
- ✅ 4 furniture types (unfurnished, basic, full, luxury)
- ✅ 7 legal statuses (red book, pink book, etc.)
- ✅ 9 view types (river, city, park, sea, etc.)

**All with English canonical names + Vietnamese translations**

## 🔧 Pydantic Models

Created in: `shared/models/attribute_extraction.py`

### Request Models

```python
class ExtractionRequest(BaseModel):
    text: str                              # User input text
    language: Optional[LanguageCode]       # Override auto-detection
    confidence_threshold: float = 0.8      # Min confidence for auto-mapping
    include_suggestions: bool = True       # Include AI suggestions
```

### Response Models

```python
class ExtractionResponse(BaseModel):
    request_language: LanguageCode         # Auto-detected language
    raw: RawExtraction                     # Numeric + free-form data
    mapped: List[MappedAttribute]          # Successfully mapped with IDs
    new: List[NewAttribute]                # Unmatched items (admin review)
    extraction_timestamp: datetime
    processing_time_ms: float
```

### Mapped Attribute (Success Case)

```python
class MappedAttribute(BaseModel):
    property_name: str                     # "district", "amenity", etc.
    table: str                             # "districts", "amenities"
    id: int                                # Foreign key to master data
    value: str                             # English canonical name
    value_translated: str                  # Translated to user's language
    confidence: float                      # 0.0 to 1.0
    match_method: MatchMethod              # exact | alias | fuzzy | llm
```

### New Attribute (Admin Review Required)

```python
class NewAttribute(BaseModel):
    property_name: str
    value: str                             # Normalized English
    value_original: str                    # Original user input
    suggested_table: Optional[str]
    suggested_translations: Dict[str, str]  # {lang_code: translation}
    requires_admin_review: bool = True
    frequency: int                         # How many times seen
```

## 🚀 Implementation Status

### ✅ Completed

1. **Database Schema** (`database/migrations/001_create_master_data_schema.sql`)
   - All master data tables with translation tables
   - Helper views for easy querying
   - Functions for fuzzy search and translation lookups
   - Audit triggers for updated_at timestamps

2. **Seed Data** (`database/migrations/002_seed_master_data.sql`)
   - English canonical names
   - Vietnamese translations for all items
   - HCMC complete coverage (25 districts)

3. **Pydantic Models** (`shared/models/attribute_extraction.py`)
   - Complete request/response models
   - 3-tier response structure (raw/mapped/new)
   - Multi-language support
   - Admin review models

### 🔨 In Progress

4. **Language Detection Service**
   - Auto-detect user language from input text
   - Use `langdetect` library
   - Support: vi, en, zh, ko, ja

5. **Fuzzy Matching Engine**
   - Exact match (name_en or translations)
   - Alias match (name_variants if implemented)
   - Fuzzy match (PostgreSQL pg_trgm similarity)
   - Confidence scoring

6. **LLM Translation Service**
   - Translate "new" items to English via Core Gateway
   - Context-aware translation (understands real estate terms)
   - Generate suggested translations for all supported languages

### ⏳ Pending

7. **Extraction Service Refactor**
   - Integrate new models and response structure
   - Implement language detection
   - Implement fuzzy matching with translations
   - Return master data IDs + translations

8. **Admin API Endpoints**
   - `GET /admin/pending-items` - List pending master data
   - `POST /admin/approve-item` - Approve and add to master data
   - `POST /admin/reject-item` - Reject item
   - `GET /admin/master-data/:table` - Browse master data

## 📝 Example Usage

### Input

```json
POST /extract-attributes

{
  "text": "Cần bán căn hộ 2PN Vinhomes Central Park Quận Bình Thạnh, 80m2, view sông, có hồ bơi, gym, hầm rượu, full nội thất",
  "language": "vi",
  "confidence_threshold": 0.8
}
```

### Output

```json
{
  "request_language": "vi",

  "raw": {
    "text": "Cần bán căn hộ 2PN Vinhomes Central Park...",
    "bedrooms": 2,
    "bathrooms": null,
    "area": 80.0,
    "price": null,
    "title": null,
    "description": "Cần bán căn hộ 2PN Vinhomes Central Park..."
  },

  "mapped": [
    {
      "property_name": "property_type",
      "table": "property_types",
      "id": 1,
      "value": "apartment",
      "value_translated": "Căn hộ",
      "confidence": 0.98,
      "match_method": "exact",
      "original_input": "căn hộ"
    },
    {
      "property_name": "district",
      "table": "districts",
      "id": 14,
      "value": "binh_thanh",
      "value_translated": "Quận Bình Thạnh",
      "confidence": 1.0,
      "match_method": "exact",
      "original_input": "Quận Bình Thạnh"
    },
    {
      "property_name": "view_type",
      "table": "view_types",
      "id": 1,
      "value": "river_view",
      "value_translated": "View sông",
      "confidence": 0.95,
      "match_method": "fuzzy",
      "original_input": "view sông"
    },
    {
      "property_name": "amenity",
      "table": "amenities",
      "id": 1,
      "value": "swimming_pool",
      "value_translated": "Hồ bơi",
      "confidence": 1.0,
      "match_method": "exact",
      "original_input": "hồ bơi"
    },
    {
      "property_name": "amenity",
      "table": "amenities",
      "id": 2,
      "value": "gym",
      "value_translated": "Phòng gym",
      "confidence": 1.0,
      "match_method": "exact",
      "original_input": "gym"
    },
    {
      "property_name": "furniture_type",
      "table": "furniture_types",
      "id": 3,
      "value": "full",
      "value_translated": "Nội thất đầy đủ",
      "confidence": 0.92,
      "match_method": "fuzzy",
      "original_input": "full nội thất"
    }
  ],

  "new": [
    {
      "property_name": "amenity",
      "table": null,
      "id": null,
      "value": "wine_cellar",
      "value_original": "hầm rượu",
      "suggested_table": "amenities",
      "suggested_category": "private_amenity",
      "suggested_translations": {
        "vi": "Hầm rượu",
        "en": "Wine cellar",
        "zh": "酒窖"
      },
      "extraction_context": "...có hồ bơi, gym, hầm rượu, full nội thất",
      "requires_admin_review": true,
      "frequency": 1
    }
  ],

  "extraction_timestamp": "2025-01-13T10:30:00Z",
  "extractor_version": "1.0.0",
  "processing_time_ms": 1250.5
}
```

## 🔄 Data Flow

### 1. User Query → Extraction

```
User (Vietnamese): "Tìm căn hộ 2PN Quận 7 có hồ bơi"
                    ↓
              [Language Detection]
                    ↓
              Detected: "vi"
                    ↓
              [LLM Extraction]
                    ↓
Raw entities: {property_type: "căn hộ", bedrooms: 2, district: "Quận 7", swimming_pool: true}
```

### 2. Extraction → Master Data Matching

```
For each extracted attribute:
  1. Try exact match in master table (name)
  2. Try exact match in translations (translated_text WHERE lang_code='vi')
  3. Try fuzzy match (similarity > 0.8)
  4. If no match → add to "new" list

Example for "căn hộ":
  Query: SELECT pt.id, pt.name, ptt.translated_text
         FROM property_types pt
         LEFT JOIN property_types_translations ptt
           ON pt.id = ptt.property_type_id AND ptt.lang_code = 'vi'
         WHERE LOWER(ptt.translated_text) = LOWER('căn hộ')

  Result: {id: 1, name: "apartment", translated_text: "Căn hộ"}
```

### 3. Master Data Match → Response

```
Matched items → "mapped" array with:
  - id: 1
  - value: "apartment" (English)
  - value_translated: "Căn hộ" (Vietnamese)

Unmatched items → "new" array:
  - LLM translates to English
  - Suggest target table
  - Flag for admin review
```

## 🎓 Key Design Decisions

### Why English as Canonical?

1. **International standard**: Code is in English, data should be too
2. **API consistency**: External integrations expect English keys
3. **Team scalability**: Global developers can contribute
4. **Translation flexibility**: Easy to add new languages

### Why Separate Translation Tables?

1. **Normalization**: Avoid duplicate data in master tables
2. **Scalability**: Add unlimited languages without schema changes
3. **Performance**: Index on (entity_id, lang_code) for fast lookups
4. **Maintainability**: Update translations independently

### Why 3-Tier Response (raw/mapped/new)?

1. **raw**: Preserve original data for audit trail
2. **mapped**: Provide validated data with IDs for immediate use
3. **new**: Enable system to learn and grow master data

### Why Return Both ID and Translation?

1. **ID**: For database queries and relationships (foreign keys)
2. **English value**: For API consistency and logging
3. **Translated value**: For UI display in user's language

## 🚧 Next Steps

### Immediate (Week 1)

1. Run database migrations
   ```bash
   psql -U ree_ai_user -d ree_ai -f database/migrations/001_create_master_data_schema.sql
   psql -U ree_ai_user -d ree_ai -f database/migrations/002_seed_master_data.sql
   ```

2. Verify seed data
   ```sql
   SELECT COUNT(*) FROM property_types;
   SELECT COUNT(*) FROM property_types_translations;
   SELECT * FROM v_property_types_with_translations;
   ```

3. Implement language detection service

4. Implement fuzzy matching with translations

### Short-term (Week 2)

5. Refactor Extraction Service to use new models

6. Add LLM translation for "new" items

7. Create admin API for pending item review

8. Integration tests for full pipeline

### Long-term

9. Add more languages (Chinese, Korean, Japanese)

10. Implement machine learning for fuzzy matching confidence

11. Analytics dashboard for extraction accuracy

12. Automatic master data suggestions from high-frequency "new" items

## 📚 References

- Database schema: `database/migrations/001_create_master_data_schema.sql`
- Seed data: `database/migrations/002_seed_master_data.sql`
- Pydantic models: `shared/models/attribute_extraction.py`
- Current extraction service: `services/attribute_extraction/main.py`
- Current master data validator: `services/attribute_extraction/master_data_validator.py`

## 🤝 Contributing

When adding new master data:

1. Add English canonical name to master table
2. Add translations to `*_translations` table
3. Update seed data script
4. Run migration
5. Update this documentation

## ❓ FAQ

**Q: Tại sao không lưu tất cả ngôn ngữ trong 1 table?**
A: Separate translation tables cho phép thêm ngôn ngữ mới mà không cần ALTER TABLE. Scalable hơn.

**Q: Nếu user input không match master data thì sao?**
A: Đưa vào "new" array, LLM translate sang English, admin review sau.

**Q: Làm sao update translation cho item đã có?**
A: INSERT/UPDATE vào `*_translations` table. Không ảnh hưởng master table.

**Q: Có cần cache translations không?**
A: Có, nên cache bằng Redis. Key pattern: `master:{table}:{id}:{lang_code}`

---

**Last Updated**: 2025-01-13
**Status**: Design Complete, Implementation In Progress
**Author**: REE AI Team

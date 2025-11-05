# Master Data System for REE AI

## Overview

The **Master Data System** is a centralized, standardized data foundation for real estate attribute extraction and validation. Instead of hard-coding values across multiple services, all real estate domain knowledge is now consolidated in this module.

## Why Master Data?

**Problem:** Before master data, services hard-coded values like:
- ❌ District names scattered across multiple files
- ❌ Property type definitions duplicated
- ❌ Amenity lists inconsistent between services
- ❌ Price ranges hard-coded in validators
- ❌ No single source of truth

**Solution:** Master data provides:
- ✅ Single source of truth for all real estate entities
- ✅ Easy to maintain and extend
- ✅ Consistent normalization across all services
- ✅ Type-safe attribute schemas for each property type
- ✅ Validation rules based on real market data

## Architecture

```
shared/master_data/
├── __init__.py                # Module exports
├── districts.py               # District master data & normalization
├── property_types.py          # Property types + attribute schemas
├── amenities.py               # Amenity definitions & extraction
├── price_ranges.py            # Reference price ranges for validation
├── attribute_schema.py        # Unified schema interface
└── README.md                  # This file
```

## Core Components

### 1. DistrictMaster (`districts.py`)

Manages district normalization and location data.

**Features:**
- 17+ HCMC districts + Hanoi districts
- Alias support (e.g., "q7", "Q.7", "phu my hung" → "Quận 7")
- District tier classification (1=premium, 2=mid, 3=affordable)
- Popular areas within each district

**Usage:**
```python
from shared.master_data import get_district_master

master = get_district_master()

# Normalize district name
district = master.normalize("q7")  # Returns "Quận 7"

# Get district info
district_obj = master.get_district("Quận 7")
print(district_obj.tier)  # 1 (premium)
print(district_obj.popular_areas)  # ["Phú Mỹ Hưng", "Tân Phong", ...]

# Extract from text
text = "Tôi muốn mua nhà ở quận 7"
match = master.extract_from_text(text)
if match:
    matched_text, district_obj = match
    print(district_obj.standard_name)  # "Quận 7"
```

### 2. PropertyTypeMaster (`property_types.py`)

Defines property types and their specific attribute schemas.

**Features:**
- 7 property types (Apartment, Villa, Townhouse, Land, Office, Commercial, Condo)
- Type-specific attribute definitions
- Required vs optional attributes per type
- Data type validation (integer, float, string, boolean, enum)
- Min/max value ranges for numeric attributes

**Usage:**
```python
from shared.master_data import get_property_type_master

master = get_property_type_master()

# Normalize property type
prop_type = master.normalize("apartment")  # Returns "căn hộ"

# Get attribute schema for a property type
schema = master.get_attribute_schema("căn hộ")
# Returns dict of {attribute_name: AttributeDefinition}

# Get required attributes
required = master.get_required_attributes("căn hộ")
# Returns ["title", "price", "district", "bedrooms", "bathrooms", "area"]
```

**Example Schema:**
```python
# Apartment (căn hộ) has:
required_attributes = [
    "title", "price", "district",
    "bedrooms", "bathrooms", "area"
]

optional_attributes = [
    "floor", "view", "balcony_direction",
    "furniture", "project_name", ...
]

# Each attribute has definition:
AttributeDefinition(
    name="bedrooms",
    type=AttributeType.INTEGER,
    required=True,
    description="Number of bedrooms",
    aliases=["phòng ngủ", "pn", "bedroom"],
    min_value=0,  # 0 for studio
    max_value=10
)
```

### 3. AmenityMaster (`amenities.py`)

Manages property amenities and features.

**Features:**
- 30+ standardized amenities
- Category classification (building, unit, recreation, parking, security, luxury, utilities)
- Property type applicability (which amenities apply to which property types)
- Alias-based extraction from free text

**Usage:**
```python
from shared.master_data import get_amenity_master

master = get_amenity_master()

# Normalize amenity
code = master.normalize("hồ bơi")  # Returns "SWIMMING_POOL"

# Get amenity info
amenity = master.get_amenity("SWIMMING_POOL")
print(amenity.display_name)  # "Hồ bơi"
print(amenity.category)  # AmenityCategory.RECREATION

# Get amenities for property type
amenities = master.get_amenities_for_property_type("APARTMENT")
# Returns list of applicable amenities

# Extract from text
text = "Căn hộ có hồ bơi, gym và thang máy"
extracted = master.extract_from_text(text)
# Returns {"swimming_pool": True, "gym": True, "elevator": True}
```

### 4. PriceRangeMaster (`price_ranges.py`)

Provides reference price ranges for validation.

**Features:**
- District-specific price ranges (VND/m²)
- Property type-specific ranges
- Based on real 2024-2025 HCMC market data
- Total price ranges and averages

**Usage:**
```python
from shared.master_data import get_price_range_master

master = get_price_range_master()

# Get price range
price_range = master.get_price_range("Quận 7", "APARTMENT")
print(price_range.min_price_per_m2)  # 50,000,000 VND/m²
print(price_range.max_price_per_m2)  # 180,000,000 VND/m²

# Validate price
is_valid, warning = master.validate_price(
    price=3_000_000_000,      # 3 tỷ
    area=80,                   # 80m²
    district="Quận 7",
    property_type_code="APARTMENT"
)
if not is_valid:
    print(warning)
```

### 5. AttributeSchema (`attribute_schema.py`)

Unified interface combining all master data sources.

**Features:**
- Single entry point for all master data
- Comprehensive entity extraction
- Multi-source validation
- Normalization across all entity types

**Usage:**
```python
from shared.master_data import get_attribute_schema

schema = get_attribute_schema()

# Extract all entities from text
text = "Tìm căn hộ 2PN ở Q7 có hồ bơi"
entities = schema.extract_entities_from_text(text)
# Returns: {
#   "property_type": "căn hộ",
#   "district": "Quận 7",
#   "amenities": {"swimming_pool": True}
# }

# Get validation summary
input_entities = {
    "property_type": "apartment",
    "district": "q7",
    "price": 3_000_000_000,
    "area": 80
}
summary = schema.get_validation_summary(input_entities)
print(summary["normalized_entities"])  # Normalized versions
print(summary["warnings"])              # Validation warnings
print(summary["suggestions"])           # Improvement suggestions
```

## Integration with Services

### Attribute Extraction Service

The extraction service now uses master data for:
1. **NLP Pre-processing:** Uses DistrictMaster, PropertyTypeMaster, AmenityMaster
2. **Validation:** Uses PriceRangeMaster, AttributeSchema
3. **Prompt Building:** Uses schema to generate LLM prompts

**Before (Hard-coded):**
```python
DISTRICT_PATTERNS = {
    r'\bq7\b': 'Quận 7',
    r'\bq2\b': 'Quận 2',
    # ... hard-coded list
}
```

**After (Master Data):**
```python
from shared.master_data import get_district_master

district_master = get_district_master()
normalized = district_master.normalize("q7")  # "Quận 7"
```

## Extending Master Data

### Adding New Districts

Edit `districts.py`:
```python
District(
    code="HCM_NEW_DISTRICT",
    standard_name="Quận Mới",
    aliases=["quan moi", "new district"],
    city="Hồ Chí Minh",
    popular_areas=["Khu A", "Khu B"],
    tier=2
)
```

### Adding New Property Types

Edit `property_types.py`:
```python
PropertyType(
    code="NEW_TYPE",
    standard_name="loại mới",
    aliases=["new type"],
    description="Description",
    required_attributes=["title", "price", "district"],
    optional_attributes=["other_attr"]
)
```

### Adding New Amenities

Edit `amenities.py`:
```python
Amenity(
    code="NEW_AMENITY",
    standard_name="new_amenity",
    display_name="Tiện ích mới",
    aliases=["new", "amenity"],
    category=AmenityCategory.BUILDING,
    applicable_to=["APARTMENT", "VILLA"]
)
```

## Testing

Run the test suite:
```bash
python test_master_data.py
```

This tests:
- District normalization
- Property type schemas
- Amenity extraction
- Price validation
- Complete extraction workflow

## Benefits

### For Extraction Accuracy
- ✅ Consistent entity normalization
- ✅ Type-specific attribute validation
- ✅ Market-based price validation
- ✅ Comprehensive amenity coverage

### For Maintainability
- ✅ Single source of truth
- ✅ Easy to add new districts/types/amenities
- ✅ No duplicate definitions across services
- ✅ Version-controlled domain knowledge

### For Scalability
- ✅ Support for multiple cities (HCMC, Hanoi, ...)
- ✅ Property type-specific schemas
- ✅ Extensible without code changes in services
- ✅ Reusable across all AI services

## CTO Recommendation

The CTO was right: **Master data is the foundation for accurate extraction**.

Before, user queries like:
- "tìm căn hộ studio ở Thảo Điền" → ❌ Failed (unknown "studio", "Thảo Điền")
- "nhà có wine cellar" → ❌ Not recognized

After master data:
- "tìm căn hộ studio ở Thảo Điền" → ✅ Normalized to proper format
- "nhà có wine cellar" → ✅ Extracted as luxury amenity

**Result:** More accurate extraction, better user experience, easier to maintain.

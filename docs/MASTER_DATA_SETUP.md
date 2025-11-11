# Master Data Setup Guide

This guide explains how to set up and use the PostgreSQL master data system for the Attribute Extraction Service.

## Overview

The master data system provides standardized reference data for property extraction and validation:

- **Districts & Wards**: Standardized location names with aliases
- **Property Types**: Căn hộ, nhà phố, biệt thự, etc.
- **Amenities**: Swimming pool, parking, gym, etc.
- **Furniture Types**: None, basic, full, luxury
- **Directions**: East, West, North, South, etc.
- **Legal Status**: Sổ đỏ, sổ hồng, etc.
- **Price Ranges**: Statistical validation data by district and property type

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Attribute Extraction Service                   │
│                                                                  │
│  ┌──────────────┐    ┌──────────────────────────────────────┐  │
│  │ NLP Processor│───►│  Master Data Validator                │  │
│  └──────────────┘    │                                        │  │
│                      │  - Normalization (vi → en codes)      │  │
│  ┌──────────────┐    │  - Validation (price, area ranges)   │  │
│  │ RAG Enhancer │───►│  - Confidence scoring                 │  │
│  └──────────────┘    │                                        │  │
│                      └────────────┬──────────────────────────┘  │
└──────────────────────────────────┼──────────────────────────────┘
                                    │
                                    ▼
                      ┌──────────────────────────┐
                      │  PostgreSQL Master Data  │
                      │                          │
                      │  - master_districts      │
                      │  - master_property_types │
                      │  - master_amenities      │
                      │  - master_furniture_types│
                      │  - master_directions     │
                      │  - master_legal_status   │
                      │  - master_price_ranges   │
                      └──────────────────────────┘
```

## Step 1: Run Migrations

### Option A: Using Docker (Recommended)

If your PostgreSQL is running in Docker:

```bash
# Start PostgreSQL
docker-compose up postgres -d

# Wait for PostgreSQL to be ready
sleep 10

# Run migrations inside a container
docker-compose exec postgres psql -U ree_ai_user -d ree_ai -f /path/to/migrations/006_create_master_data.sql
docker-compose exec postgres psql -U ree_ai_user -d ree_ai -f /path/to/seeds/001_seed_master_data.sql
```

### Option B: Using Python Script (Easiest)

```bash
# Ensure PostgreSQL connection settings in .env
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=ree_ai
# POSTGRES_USER=ree_ai_user
# POSTGRES_PASSWORD=your_password

# Run the migration script
python scripts/run_master_data_migrations.py
```

Expected output:
```
🚀 Starting Master Data Migrations
ℹ️ Connecting to PostgreSQL at localhost:5432
✅ Connected to PostgreSQL
🤖 Running master data migration...
ℹ️ Running migration: 006_create_master_data.sql
✅ Migration completed: 006_create_master_data.sql
🤖 Found 1 seed files
ℹ️ Running seed: 001_seed_master_data.sql
✅ Seed completed: 001_seed_master_data.sql
✅ All migrations and seeds completed!
ℹ️ Verifying master data...
✅ Districts: 24
✅ Property Types: 8
✅ Amenities: 20
```

### Option C: Manual SQL Execution

```bash
# Connect to PostgreSQL
psql -h localhost -U ree_ai_user -d ree_ai

# Run migration
\i database/migrations/006_create_master_data.sql

# Run seed data
\i database/seeds/001_seed_master_data.sql

# Verify
SELECT COUNT(*) FROM master_districts;
SELECT COUNT(*) FROM master_property_types;
SELECT COUNT(*) FROM master_amenities;
```

## Step 2: Verify Installation

### Check Database Tables

```sql
-- List all master data tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name LIKE 'master_%';

-- Expected output:
-- master_amenities
-- master_directions
-- master_districts
-- master_furniture_types
-- master_legal_status
-- master_price_ranges
-- master_property_types
-- master_transaction_types
-- master_wards
```

### Check Data Counts

```sql
SELECT
    'Districts' as entity, COUNT(*) as count FROM master_districts
UNION ALL
SELECT 'Property Types', COUNT(*) FROM master_property_types
UNION ALL
SELECT 'Amenities', COUNT(*) FROM master_amenities
UNION ALL
SELECT 'Furniture Types', COUNT(*) FROM master_furniture_types
UNION ALL
SELECT 'Directions', COUNT(*) FROM master_directions
UNION ALL
SELECT 'Legal Status', COUNT(*) FROM master_legal_status;
```

Expected output:
```
entity          | count
----------------|------
Districts       | 24
Property Types  | 8
Amenities       | 20
Furniture Types | 4
Directions      | 8
Legal Status    | 5
```

## Step 3: Test the API

### Start the Attribute Extraction Service

```bash
# Using Docker
docker-compose up attribute-extraction

# Or standalone (for development)
cd services/attribute_extraction
python main.py
```

### Test Master Data Endpoints

```bash
# Get all districts
curl http://localhost:8084/master-data/districts | jq

# Expected output:
# {
#   "districts": [
#     {
#       "code": "Q1",
#       "name_vi": "Quận 1",
#       "name_en": "District 1",
#       "city": "Ho Chi Minh City"
#     },
#     ...
#   ],
#   "count": 24
# }

# Get all property types
curl http://localhost:8084/master-data/property-types | jq

# Get all amenities
curl http://localhost:8084/master-data/amenities | jq

# Get amenities by category
curl "http://localhost:8084/master-data/amenities?category=building_amenity" | jq
```

### Test Extraction with Master Data Normalization

```bash
curl -X POST http://localhost:8084/extract-query-enhanced \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ",
    "intent": "SEARCH"
  }' | jq
```

Expected output:
```json
{
  "entities": {
    "district": "Q7",
    "district_name_vi": "Quận 7",
    "district_name_en": "District 7",
    "property_type": "apartment",
    "property_type_name_vi": "Căn hộ",
    "property_type_name_en": "Apartment",
    "bedrooms": 2,
    "max_price": 3000000000
  },
  "confidence": 0.92,
  "extracted_from": "enhanced_pipeline_with_master_data",
  "warnings": [],
  "nlp_entities": {...},
  "rag_retrieved_count": 5
}
```

## Step 4: Run Tests

```bash
# Run PostgreSQL master data tests
pytest tests/test_master_data_postgres.py -v

# Run all tests
pytest tests/ -v
```

## Usage Examples

### Normalization

The master data system automatically normalizes Vietnamese input to standardized English codes:

```python
from shared.database import get_master_data_repository

repo = await get_master_data_repository()

# Normalize district (various inputs → standardized code)
result = await repo.normalize_district("quận 7")  # → "Q7"
result = await repo.normalize_district("Q.7")     # → "Q7"
result = await repo.normalize_district("quan 7")  # → "Q7"

# Normalize property type
result = await repo.normalize_property_type("căn hộ")    # → "apartment"
result = await repo.normalize_property_type("chung cư")  # → "apartment"
result = await repo.normalize_property_type("apartment") # → "apartment"

# Batch normalization
entities = {
    "district": "quận 7",
    "property_type": "căn hộ",
    "furniture": "full"
}
normalized = await repo.normalize_entities(entities)
# Returns: {
#   "district": "Q7",
#   "district_name_vi": "Quận 7",
#   "district_name_en": "District 7",
#   "property_type": "apartment",
#   "furniture": "full"
# }
```

### Validation

The system validates prices and areas against typical ranges:

```python
# Validate price
validation = await repo.validate_price(
    price=5000000000,       # 5 billion VND
    area=70,                # 70 m²
    district_code="Q7",
    property_type_code="apartment"
)

if not validation.is_valid:
    print("Warnings:", validation.warnings)
    # Example: "Price per m² 71,428,571 VND/m² is higher than typical (50-80 million)"

# Validate area
validation = await repo.validate_area(
    area=2000,              # 2000 m²
    property_type_code="apartment"
)

if not validation.is_valid:
    print("Warnings:", validation.warnings)
    # Example: "Area 2000m² is significantly larger than typical căn hộ (20-500m²)"
```

## Adding New Master Data

### Add New District

```sql
INSERT INTO master_districts (code, name_vi, name_en, city, aliases, latitude, longitude)
VALUES (
    'QXXX',
    'Quận Mới',
    'New District',
    'Ho Chi Minh City',
    ARRAY['Q.XXX', 'quận mới', 'new district'],
    10.7756,
    106.7019
);
```

### Add New Property Type

```sql
INSERT INTO master_property_types (
    code, name_vi, name_en, aliases, category,
    typical_min_area, typical_max_area,
    typical_min_bedrooms, typical_max_bedrooms
)
VALUES (
    'duplex',
    'Căn hộ duplex',
    'Duplex Apartment',
    ARRAY['duplex', 'căn hộ duplex', 'penthouse duplex'],
    'residential',
    80, 300,
    2, 5
);
```

### Add New Amenity

```sql
INSERT INTO master_amenities (code, name_vi, name_en, aliases, category, icon)
VALUES (
    'rooftop_garden',
    'Vườn sân thượng',
    'Rooftop Garden',
    ARRAY['rooftop garden', 'vườn sân thượng', 'sky garden'],
    'building_amenity',
    'local_florist'
);
```

## Updating Price Ranges

Price ranges should be updated periodically based on actual market data:

```sql
-- Update price range for District 7 apartments
UPDATE master_price_ranges
SET
    min_price_per_m2 = 60000000,
    avg_price_per_m2 = 85000000,
    max_price_per_m2 = 160000000,
    min_total_price = 2000000000,
    avg_total_price = 6000000000,
    max_total_price = 25000000000,
    sample_count = 200,
    last_updated = CURRENT_TIMESTAMP
WHERE
    district_id = (SELECT id FROM master_districts WHERE code = 'Q7')
    AND property_type_id = (SELECT id FROM master_property_types WHERE code = 'apartment');
```

## Troubleshooting

### Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection from service
docker-compose logs attribute-extraction | grep -i postgres
```

### Missing Tables

```bash
# Re-run migrations
python scripts/run_master_data_migrations.py
```

### No Data Returned

```sql
-- Check if data is present
SELECT * FROM master_districts LIMIT 5;

-- Check if records are active
SELECT * FROM master_districts WHERE active = FALSE;
```

### Normalization Not Working

```sql
-- Check aliases
SELECT code, name_vi, aliases FROM master_districts WHERE code = 'Q7';

-- Test array matching
SELECT * FROM master_districts WHERE 'quận 7' = ANY(SELECT LOWER(unnest(aliases)));
```

## Performance Optimization

### Indexes

All necessary indexes are created by the migration:

- GIN indexes on `aliases` arrays for fast fuzzy matching
- B-tree indexes on `code`, `active`, and foreign keys

### Connection Pooling

The repository uses asyncpg connection pooling (2-10 connections):

```python
self.pool = await asyncpg.create_pool(
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    min_size=2,
    max_size=10
)
```

## Next Steps

1. **Add More Districts**: Expand coverage to other cities (Hanoi, Da Nang, etc.)
2. **Update Price Ranges**: Set up automatic updates from OpenSearch property data
3. **Add Ward Data**: Populate `master_wards` table for more granular location matching
4. **Multilingual Support**: Add Chinese aliases for international users
5. **API Keys**: Add authentication for master data modification endpoints

## References

- Schema: `database/migrations/006_create_master_data.sql`
- Seed Data: `database/seeds/001_seed_master_data.sql`
- Repository: `shared/database/master_data_repository.py`
- Models: `shared/models/master_data.py`
- Service Integration: `services/attribute_extraction/master_data_validator.py`

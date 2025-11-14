-- ================================================================
-- PRODUCTION-READY MIGRATION: Rebuild Master Data Schema
-- ================================================================
-- PURPOSE: Drop and rebuild ree_common schema from scratch
-- DATE: 2025-01-14
-- SAFE FOR PRODUCTION: Can be run multiple times (idempotent)
-- ================================================================

BEGIN;

-- ================================================================
-- STEP 1: Drop existing schema (CASCADE removes all objects)
-- ================================================================

DROP SCHEMA IF EXISTS ree_common CASCADE;

-- Create clean schema
CREATE SCHEMA ree_common;

-- ================================================================
-- STEP 2: Create standard master data tables (10 tables)
-- ================================================================
-- DESIGN PRINCIPLE: Pure lookup tables - MINIMAL columns
-- - id, code, name (English), sort_order, timestamps
-- - NO active flag (master data is static)
-- - NO business logic columns
-- - NO entity attributes
-- ================================================================

-- 1. AMENITIES (tiện ích)
CREATE TABLE ree_common.amenities (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. VIEWS (loại view)
CREATE TABLE ree_common.views (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. DISTRICTS (quận/huyện)
CREATE TABLE ree_common.districts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. PROPERTY_TYPES (loại hình BĐS)
CREATE TABLE ree_common.property_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. DIRECTIONS (hướng nhà)
CREATE TABLE ree_common.directions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. FURNITURE_TYPES (tình trạng nội thất)
CREATE TABLE ree_common.furniture_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. LEGAL_STATUS (tình trạng pháp lý)
CREATE TABLE ree_common.legal_status (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. TRANSACTION_TYPES (loại giao dịch)
CREATE TABLE ree_common.transaction_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. PROPERTY_CONDITIONS (tình trạng BĐS)
CREATE TABLE ree_common.property_conditions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. UNITS (đơn vị đo)
CREATE TABLE ree_common.units (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    symbol VARCHAR(20),
    unit_type VARCHAR(50) NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================================
-- STEP 3: Create translation tables (10 tables)
-- ================================================================

CREATE TABLE ree_common.amenities_translation (
    id SERIAL PRIMARY KEY,
    amenity_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (amenity_id) REFERENCES ree_common.amenities(id) ON DELETE CASCADE,
    UNIQUE (amenity_id, lang_code)
);

CREATE TABLE ree_common.views_translation (
    id SERIAL PRIMARY KEY,
    view_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (view_id) REFERENCES ree_common.views(id) ON DELETE CASCADE,
    UNIQUE (view_id, lang_code)
);

CREATE TABLE ree_common.districts_translation (
    id SERIAL PRIMARY KEY,
    district_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (district_id) REFERENCES ree_common.districts(id) ON DELETE CASCADE,
    UNIQUE (district_id, lang_code)
);

CREATE TABLE ree_common.property_types_translation (
    id SERIAL PRIMARY KEY,
    property_type_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_type_id) REFERENCES ree_common.property_types(id) ON DELETE CASCADE,
    UNIQUE (property_type_id, lang_code)
);

CREATE TABLE ree_common.directions_translation (
    id SERIAL PRIMARY KEY,
    direction_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (direction_id) REFERENCES ree_common.directions(id) ON DELETE CASCADE,
    UNIQUE (direction_id, lang_code)
);

CREATE TABLE ree_common.furniture_types_translation (
    id SERIAL PRIMARY KEY,
    furniture_type_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (furniture_type_id) REFERENCES ree_common.furniture_types(id) ON DELETE CASCADE,
    UNIQUE (furniture_type_id, lang_code)
);

CREATE TABLE ree_common.legal_status_translation (
    id SERIAL PRIMARY KEY,
    legal_status_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (legal_status_id) REFERENCES ree_common.legal_status(id) ON DELETE CASCADE,
    UNIQUE (legal_status_id, lang_code)
);

CREATE TABLE ree_common.transaction_types_translation (
    id SERIAL PRIMARY KEY,
    transaction_type_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_type_id) REFERENCES ree_common.transaction_types(id) ON DELETE CASCADE,
    UNIQUE (transaction_type_id, lang_code)
);

CREATE TABLE ree_common.property_conditions_translation (
    id SERIAL PRIMARY KEY,
    property_condition_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_condition_id) REFERENCES ree_common.property_conditions(id) ON DELETE CASCADE,
    UNIQUE (property_condition_id, lang_code)
);

CREATE TABLE ree_common.units_translation (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES ree_common.units(id) ON DELETE CASCADE,
    UNIQUE (unit_id, lang_code)
);

-- ================================================================
-- STEP 4: Create indexes for performance
-- ================================================================

-- Main table indexes (only code - UNIQUE constraint already creates index)
-- No need for active index - no active column anymore!

CREATE INDEX idx_units_type ON ree_common.units(unit_type);

-- Translation table indexes
CREATE INDEX idx_amenities_trans_lang ON ree_common.amenities_translation(lang_code);
CREATE INDEX idx_amenities_trans_id ON ree_common.amenities_translation(amenity_id);
CREATE INDEX idx_amenities_trans_aliases ON ree_common.amenities_translation USING gin(aliases);

CREATE INDEX idx_views_trans_lang ON ree_common.views_translation(lang_code);
CREATE INDEX idx_views_trans_id ON ree_common.views_translation(view_id);
CREATE INDEX idx_views_trans_aliases ON ree_common.views_translation USING gin(aliases);

CREATE INDEX idx_districts_trans_lang ON ree_common.districts_translation(lang_code);
CREATE INDEX idx_districts_trans_id ON ree_common.districts_translation(district_id);
CREATE INDEX idx_districts_trans_aliases ON ree_common.districts_translation USING gin(aliases);

CREATE INDEX idx_property_types_trans_lang ON ree_common.property_types_translation(lang_code);
CREATE INDEX idx_property_types_trans_id ON ree_common.property_types_translation(property_type_id);
CREATE INDEX idx_property_types_trans_aliases ON ree_common.property_types_translation USING gin(aliases);

CREATE INDEX idx_directions_trans_lang ON ree_common.directions_translation(lang_code);
CREATE INDEX idx_directions_trans_id ON ree_common.directions_translation(direction_id);
CREATE INDEX idx_directions_trans_aliases ON ree_common.directions_translation USING gin(aliases);

CREATE INDEX idx_furniture_types_trans_lang ON ree_common.furniture_types_translation(lang_code);
CREATE INDEX idx_furniture_types_trans_id ON ree_common.furniture_types_translation(furniture_type_id);
CREATE INDEX idx_furniture_types_trans_aliases ON ree_common.furniture_types_translation USING gin(aliases);

CREATE INDEX idx_legal_status_trans_lang ON ree_common.legal_status_translation(lang_code);
CREATE INDEX idx_legal_status_trans_id ON ree_common.legal_status_translation(legal_status_id);
CREATE INDEX idx_legal_status_trans_aliases ON ree_common.legal_status_translation USING gin(aliases);

CREATE INDEX idx_transaction_types_trans_lang ON ree_common.transaction_types_translation(lang_code);
CREATE INDEX idx_transaction_types_trans_id ON ree_common.transaction_types_translation(transaction_type_id);
CREATE INDEX idx_transaction_types_trans_aliases ON ree_common.transaction_types_translation USING gin(aliases);

CREATE INDEX idx_property_conditions_trans_lang ON ree_common.property_conditions_translation(lang_code);
CREATE INDEX idx_property_conditions_trans_id ON ree_common.property_conditions_translation(property_condition_id);
CREATE INDEX idx_property_conditions_trans_aliases ON ree_common.property_conditions_translation USING gin(aliases);

CREATE INDEX idx_units_trans_lang ON ree_common.units_translation(lang_code);
CREATE INDEX idx_units_trans_id ON ree_common.units_translation(unit_id);
CREATE INDEX idx_units_trans_aliases ON ree_common.units_translation USING gin(aliases);

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT
    'Schema rebuilt successfully!' as status,
    COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'ree_common';

-- Show all tables
\dt ree_common.*;

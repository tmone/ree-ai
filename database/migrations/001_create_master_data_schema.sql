-- ============================================================================
-- REE AI Master Data Schema
-- ============================================================================
-- Purpose: Store canonical reference data (English) with multi-language support
-- Pattern: Each master table has a corresponding _translations table
-- ============================================================================

-- Enable UUID extension for potential future use
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. LOCATION MASTER DATA (Hierarchical)
-- ============================================================================

-- Cities (Tier 1)
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,  -- English canonical name
    code VARCHAR(20) NOT NULL UNIQUE,    -- e.g., 'hcmc', 'hanoi'
    country_code CHAR(2) DEFAULT 'VN',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE cities_translations (
    id SERIAL PRIMARY KEY,
    city_id INT NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,       -- 'vi', 'en', 'zh', 'ko', 'ja'
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(city_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_cities_translations_lookup ON cities_translations(city_id, lang_code);

-- Districts (Tier 2)
CREATE TABLE districts (
    id SERIAL PRIMARY KEY,
    city_id INT NOT NULL REFERENCES cities(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,          -- English canonical name
    code VARCHAR(20) NOT NULL,           -- e.g., 'district_1', 'district_2'
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(city_id, code)
);

CREATE TABLE districts_translations (
    id SERIAL PRIMARY KEY,
    district_id INT NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(district_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_districts_translations_lookup ON districts_translations(district_id, lang_code);
CREATE INDEX idx_districts_city ON districts(city_id);

-- Wards (Tier 3)
CREATE TABLE wards (
    id SERIAL PRIMARY KEY,
    district_id INT NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,          -- English canonical name
    code VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(district_id, code)
);

CREATE TABLE wards_translations (
    id SERIAL PRIMARY KEY,
    ward_id INT NOT NULL REFERENCES wards(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(ward_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_wards_translations_lookup ON wards_translations(ward_id, lang_code);
CREATE INDEX idx_wards_district ON wards(district_id);

-- Streets (Tier 4)
CREATE TABLE streets (
    id SERIAL PRIMARY KEY,
    ward_id INT REFERENCES wards(id) ON DELETE SET NULL,  -- Optional: some streets span multiple wards
    district_id INT REFERENCES districts(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,          -- English canonical name
    street_type VARCHAR(50),             -- 'street', 'avenue', 'boulevard', 'alley'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE streets_translations (
    id SERIAL PRIMARY KEY,
    street_id INT NOT NULL REFERENCES streets(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(street_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_streets_translations_lookup ON streets_translations(street_id, lang_code);
CREATE INDEX idx_streets_district ON streets(district_id);
CREATE INDEX idx_streets_ward ON streets(ward_id);

-- ============================================================================
-- 2. PROPERTY ATTRIBUTES MASTER DATA
-- ============================================================================

-- Property Types
CREATE TABLE property_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,   -- English canonical: 'apartment', 'villa', 'townhouse', 'land'
    code VARCHAR(50) NOT NULL UNIQUE,    -- 'apartment', 'villa', 'townhouse', 'land'
    category VARCHAR(50),                -- 'residential', 'commercial', 'industrial'
    icon VARCHAR(50),                    -- Icon identifier for UI
    description TEXT,
    attributes_schema JSONB,             -- Flexible schema for property-type-specific attributes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE property_types_translations (
    id SERIAL PRIMARY KEY,
    property_type_id INT NOT NULL REFERENCES property_types(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(property_type_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_property_types_translations_lookup ON property_types_translations(property_type_id, lang_code);

-- Amenities
CREATE TABLE amenities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,   -- English canonical: 'swimming_pool', 'gym', 'parking'
    code VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50),                -- 'shared_amenity', 'private_amenity', 'nearby_facility'
    icon VARCHAR(50),
    description TEXT,
    applicable_to JSONB,                 -- Array of property_type codes: ['apartment', 'villa']
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE amenities_translations (
    id SERIAL PRIMARY KEY,
    amenity_id INT NOT NULL REFERENCES amenities(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(amenity_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_amenities_translations_lookup ON amenities_translations(amenity_id, lang_code);

-- Directions (8 cardinal + intercardinal)
CREATE TABLE directions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL UNIQUE,    -- English: 'north', 'northeast', 'east', etc.
    code VARCHAR(5) NOT NULL UNIQUE,     -- 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'
    angle INT NOT NULL UNIQUE,           -- 0=North, 45=NE, 90=East, 135=SE, 180=South, 225=SW, 270=West, 315=NW
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE directions_translations (
    id SERIAL PRIMARY KEY,
    direction_id INT NOT NULL REFERENCES directions(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,
    translated_text VARCHAR(50) NOT NULL,
    UNIQUE(direction_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_directions_translations_lookup ON directions_translations(direction_id, lang_code);

-- Furniture Types
CREATE TABLE furniture_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,   -- English: 'unfurnished', 'basic', 'full', 'luxury'
    code VARCHAR(50) NOT NULL UNIQUE,
    level INT NOT NULL,                  -- 0=unfurnished, 1=basic, 2=full, 3=luxury
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE furniture_types_translations (
    id SERIAL PRIMARY KEY,
    furniture_type_id INT NOT NULL REFERENCES furniture_types(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(furniture_type_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_furniture_types_translations_lookup ON furniture_types_translations(furniture_type_id, lang_code);

-- Legal Statuses
CREATE TABLE legal_statuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,   -- English: 'pink_book', 'red_book', 'sales_contract', 'pending'
    code VARCHAR(50) NOT NULL UNIQUE,
    is_valid BOOLEAN DEFAULT true,       -- Is this a valid/approved legal status?
    priority INT DEFAULT 0,              -- Higher = more secure (red_book > pink_book)
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE legal_statuses_translations (
    id SERIAL PRIMARY KEY,
    legal_status_id INT NOT NULL REFERENCES legal_statuses(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(legal_status_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_legal_statuses_translations_lookup ON legal_statuses_translations(legal_status_id, lang_code);

-- View Types
CREATE TABLE view_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,   -- English: 'river_view', 'city_view', 'park_view', 'sea_view'
    code VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50),                -- 'natural', 'urban', 'landmark'
    icon VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE view_types_translations (
    id SERIAL PRIMARY KEY,
    view_type_id INT NOT NULL REFERENCES view_types(id) ON DELETE CASCADE,
    lang_code VARCHAR(5) NOT NULL,
    translated_text VARCHAR(200) NOT NULL,
    UNIQUE(view_type_id, lang_code),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_view_types_translations_lookup ON view_types_translations(view_type_id, lang_code);

-- ============================================================================
-- 3. PENDING MASTER DATA (For Admin Review)
-- ============================================================================

-- Stores new attributes extracted from text that don't match existing master data
CREATE TABLE pending_master_data (
    id SERIAL PRIMARY KEY,
    property_name VARCHAR(100) NOT NULL,     -- e.g., 'amenity', 'view_type'
    value VARCHAR(200) NOT NULL,             -- English normalized value
    value_original VARCHAR(200) NOT NULL,    -- Original user input
    suggested_table VARCHAR(100),            -- Target master data table
    suggested_category VARCHAR(100),
    suggested_translations JSONB,            -- {lang_code: translated_text}
    extraction_context TEXT,                 -- Original text snippet
    frequency INT DEFAULT 1,                 -- How many times this value appeared
    status VARCHAR(20) DEFAULT 'pending',    -- 'pending', 'approved', 'rejected'
    reviewed_by INT,                         -- Admin user ID
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pending_master_status ON pending_master_data(status);
CREATE INDEX idx_pending_master_table ON pending_master_data(suggested_table);
CREATE INDEX idx_pending_master_frequency ON pending_master_data(frequency DESC);

-- ============================================================================
-- 4. HELPER VIEWS FOR EASY QUERYING
-- ============================================================================

-- View: Get all property types with translations
CREATE OR REPLACE VIEW v_property_types_with_translations AS
SELECT
    pt.id,
    pt.name as name_en,
    pt.code,
    pt.category,
    jsonb_object_agg(
        ptt.lang_code,
        ptt.translated_text
    ) FILTER (WHERE ptt.lang_code IS NOT NULL) as translations
FROM property_types pt
LEFT JOIN property_types_translations ptt ON pt.id = ptt.property_type_id
GROUP BY pt.id, pt.name, pt.code, pt.category;

-- View: Get all amenities with translations
CREATE OR REPLACE VIEW v_amenities_with_translations AS
SELECT
    a.id,
    a.name as name_en,
    a.code,
    a.category,
    jsonb_object_agg(
        at.lang_code,
        at.translated_text
    ) FILTER (WHERE at.lang_code IS NOT NULL) as translations
FROM amenities a
LEFT JOIN amenities_translations at ON a.id = at.amenity_id
GROUP BY a.id, a.name, a.code, a.category;

-- View: Get all districts with translations for HCMC
CREATE OR REPLACE VIEW v_hcmc_districts_with_translations AS
SELECT
    d.id,
    d.name as name_en,
    d.code,
    jsonb_object_agg(
        dt.lang_code,
        dt.translated_text
    ) FILTER (WHERE dt.lang_code IS NOT NULL) as translations
FROM districts d
LEFT JOIN districts_translations dt ON d.id = dt.district_id
WHERE d.city_id = (SELECT id FROM cities WHERE code = 'hcmc')
GROUP BY d.id, d.name, d.code;

-- ============================================================================
-- 5. FUNCTIONS FOR TRANSLATION LOOKUPS
-- ============================================================================

-- Function: Get translated value for any master data entity
CREATE OR REPLACE FUNCTION get_translation(
    p_table_name VARCHAR,
    p_entity_id INT,
    p_lang_code VARCHAR DEFAULT 'en'
) RETURNS VARCHAR AS $$
DECLARE
    v_translation VARCHAR;
    v_query TEXT;
BEGIN
    -- Build dynamic query for translation table
    v_query := format(
        'SELECT translated_text FROM %I WHERE %I = $1 AND lang_code = $2',
        p_table_name || '_translations',
        regexp_replace(p_table_name, 's$', '') || '_id'  -- Remove trailing 's' for FK name
    );

    EXECUTE v_query INTO v_translation USING p_entity_id, p_lang_code;

    -- If no translation found, return English name from master table
    IF v_translation IS NULL THEN
        v_query := format('SELECT name FROM %I WHERE id = $1', p_table_name);
        EXECUTE v_query INTO v_translation USING p_entity_id;
    END IF;

    RETURN v_translation;
END;
$$ LANGUAGE plpgsql;

-- Function: Fuzzy search across master data with translations
CREATE OR REPLACE FUNCTION fuzzy_search_master_data(
    p_table_name VARCHAR,
    p_search_term VARCHAR,
    p_lang_code VARCHAR DEFAULT 'vi',
    p_threshold FLOAT DEFAULT 0.7
) RETURNS TABLE(
    id INT,
    name_en VARCHAR,
    translated_text VARCHAR,
    similarity_score FLOAT
) AS $$
DECLARE
    v_query TEXT;
BEGIN
    v_query := format($query$
        SELECT
            m.id,
            m.name as name_en,
            COALESCE(t.translated_text, m.name) as translated_text,
            GREATEST(
                similarity(LOWER(m.name), LOWER($1)),
                similarity(LOWER(COALESCE(t.translated_text, '')), LOWER($1))
            ) as similarity_score
        FROM %I m
        LEFT JOIN %I t ON m.id = t.%I AND t.lang_code = $2
        WHERE
            similarity(LOWER(m.name), LOWER($1)) > $3
            OR similarity(LOWER(COALESCE(t.translated_text, '')), LOWER($1)) > $3
        ORDER BY similarity_score DESC
        LIMIT 5
    $query$,
        p_table_name,
        p_table_name || '_translations',
        regexp_replace(p_table_name, 's$', '') || '_id'
    );

    RETURN QUERY EXECUTE v_query USING p_search_term, p_lang_code, p_threshold;
END;
$$ LANGUAGE plpgsql;

-- Enable pg_trgm for fuzzy matching
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- 6. AUDIT TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all master data tables
CREATE TRIGGER update_cities_updated_at BEFORE UPDATE ON cities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_districts_updated_at BEFORE UPDATE ON districts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wards_updated_at BEFORE UPDATE ON wards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_streets_updated_at BEFORE UPDATE ON streets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_property_types_updated_at BEFORE UPDATE ON property_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_amenities_updated_at BEFORE UPDATE ON amenities
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_furniture_types_updated_at BEFORE UPDATE ON furniture_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_legal_statuses_updated_at BEFORE UPDATE ON legal_statuses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_view_types_updated_at BEFORE UPDATE ON view_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pending_master_updated_at BEFORE UPDATE ON pending_master_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

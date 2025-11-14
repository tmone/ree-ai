-- ================================================================
-- Global Administrative Divisions Schema
-- ================================================================
-- PURPOSE: Support ALL countries worldwide (not just Vietnam)
-- DATE: 2025-11-14
-- ARCHITECTURE: Countries → Provinces/States → Districts/Cities → Wards/Neighborhoods
-- ================================================================

BEGIN;

-- ================================================================
-- STEP 1: Create Countries Table
-- ================================================================

CREATE TABLE IF NOT EXISTS ree_common.countries (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,        -- ISO 3166-1 alpha-2 (US, VN, JP, TH, UK, SG, etc.)
    name VARCHAR(255) NOT NULL,
    iso_code_3 VARCHAR(10),                  -- ISO 3166-1 alpha-3 (USA, VNM, JPN, THA, etc.)
    phone_code VARCHAR(10),                  -- +1, +84, +81, +66, etc.
    currency VARCHAR(10),                    -- USD, VND, JPY, THB, etc.
    region VARCHAR(50),                      -- Asia, Europe, Americas, Africa, Oceania
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ree_common.countries_translation (
    id SERIAL PRIMARY KEY,
    country_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES ree_common.countries(id) ON DELETE CASCADE,
    UNIQUE (country_id, lang_code)
);

-- ================================================================
-- STEP 2: Create Provinces/States Table (Level 1)
-- ================================================================

CREATE TABLE IF NOT EXISTS ree_common.provinces (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    country_id INTEGER NOT NULL REFERENCES ree_common.countries(id),
    admin_level VARCHAR(50),                 -- Province, State, Prefecture, Region, etc.
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ree_common.provinces_translation (
    id SERIAL PRIMARY KEY,
    province_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (province_id) REFERENCES ree_common.provinces(id) ON DELETE CASCADE,
    UNIQUE (province_id, lang_code)
);

-- ================================================================
-- STEP 3: Add country_id to Districts (if not exists)
-- ================================================================

DO $$
BEGIN
    -- Add country_id if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ree_common'
        AND table_name = 'districts'
        AND column_name = 'country_id'
    ) THEN
        ALTER TABLE ree_common.districts
        ADD COLUMN country_id INTEGER REFERENCES ree_common.countries(id);
    END IF;

    -- Add province_id if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ree_common'
        AND table_name = 'districts'
        AND column_name = 'province_id'
    ) THEN
        ALTER TABLE ree_common.districts
        ADD COLUMN province_id INTEGER REFERENCES ree_common.provinces(id);
    END IF;
END $$;

-- ================================================================
-- STEP 4: Create Wards/Neighborhoods Table (Level 3)
-- ================================================================

CREATE TABLE IF NOT EXISTS ree_common.wards (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    district_id INTEGER REFERENCES ree_common.districts(id),
    admin_level VARCHAR(50),                 -- Ward, Neighborhood, Subdistrict, etc.
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ree_common.wards_translation (
    id SERIAL PRIMARY KEY,
    ward_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ward_id) REFERENCES ree_common.wards(id) ON DELETE CASCADE,
    UNIQUE (ward_id, lang_code)
);

-- ================================================================
-- STEP 5: Create Streets Table (Global)
-- ================================================================

CREATE TABLE IF NOT EXISTS ree_common.streets (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    street_type VARCHAR(50),                 -- Street, Avenue, Road, Boulevard, Lane, Alley
    country_id INTEGER REFERENCES ree_common.countries(id),
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ree_common.streets_translation (
    id SERIAL PRIMARY KEY,
    street_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (street_id) REFERENCES ree_common.streets(id) ON DELETE CASCADE,
    UNIQUE (street_id, lang_code)
);

-- ================================================================
-- STEP 6: Create Indexes
-- ================================================================

-- Countries indexes
CREATE INDEX IF NOT EXISTS idx_countries_region ON ree_common.countries(region);
CREATE INDEX IF NOT EXISTS idx_countries_trans_lang ON ree_common.countries_translation(lang_code);
CREATE INDEX IF NOT EXISTS idx_countries_trans_id ON ree_common.countries_translation(country_id);
CREATE INDEX IF NOT EXISTS idx_countries_trans_aliases ON ree_common.countries_translation USING gin(aliases);

-- Provinces indexes
CREATE INDEX IF NOT EXISTS idx_provinces_country ON ree_common.provinces(country_id);
CREATE INDEX IF NOT EXISTS idx_provinces_trans_lang ON ree_common.provinces_translation(lang_code);
CREATE INDEX IF NOT EXISTS idx_provinces_trans_id ON ree_common.provinces_translation(province_id);
CREATE INDEX IF NOT EXISTS idx_provinces_trans_aliases ON ree_common.provinces_translation USING gin(aliases);

-- Districts indexes
CREATE INDEX IF NOT EXISTS idx_districts_country ON ree_common.districts(country_id);
CREATE INDEX IF NOT EXISTS idx_districts_province ON ree_common.districts(province_id);

-- Wards indexes
CREATE INDEX IF NOT EXISTS idx_wards_district ON ree_common.wards(district_id);
CREATE INDEX IF NOT EXISTS idx_wards_trans_lang ON ree_common.wards_translation(lang_code);
CREATE INDEX IF NOT EXISTS idx_wards_trans_id ON ree_common.wards_translation(ward_id);
CREATE INDEX IF NOT EXISTS idx_wards_trans_aliases ON ree_common.wards_translation USING gin(aliases);

-- Streets indexes
CREATE INDEX IF NOT EXISTS idx_streets_country ON ree_common.streets(country_id);
CREATE INDEX IF NOT EXISTS idx_streets_type ON ree_common.streets(street_type);
CREATE INDEX IF NOT EXISTS idx_streets_trans_lang ON ree_common.streets_translation(lang_code);
CREATE INDEX IF NOT EXISTS idx_streets_trans_id ON ree_common.streets_translation(street_id);
CREATE INDEX IF NOT EXISTS idx_streets_trans_aliases ON ree_common.streets_translation USING gin(aliases);

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT 'Global administrative divisions schema created!' as status;
\dt ree_common.*;

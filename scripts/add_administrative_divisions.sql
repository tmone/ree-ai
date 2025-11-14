-- ================================================================
-- Add Administrative Divisions Tables
-- ================================================================
-- PURPOSE: Add provinces, wards, and streets tables
-- DATE: 2025-11-14
-- SAFE FOR PRODUCTION: Extends existing schema without dropping
-- ================================================================

BEGIN;

-- ================================================================
-- STEP 1: Create Provinces/Cities Table
-- ================================================================

CREATE TABLE IF NOT EXISTS ree_common.provinces (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(50),                      -- North, Central, South
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
-- STEP 2: Add province_id to Districts
-- ================================================================

-- Add province_id column if not exists
DO $$
BEGIN
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
-- STEP 3: Create Wards Table
-- ================================================================

CREATE TABLE IF NOT EXISTS ree_common.wards (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    district_id INTEGER REFERENCES ree_common.districts(id),
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
-- STEP 4: Create Streets Table
-- ================================================================

CREATE TABLE IF NOT EXISTS ree_common.streets (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    street_type VARCHAR(50),                 -- Street, Avenue, Road, Lane, Alley
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
-- STEP 5: Create Indexes
-- ================================================================

-- Provinces indexes
CREATE INDEX IF NOT EXISTS idx_provinces_region ON ree_common.provinces(region);
CREATE INDEX IF NOT EXISTS idx_provinces_trans_lang ON ree_common.provinces_translation(lang_code);
CREATE INDEX IF NOT EXISTS idx_provinces_trans_id ON ree_common.provinces_translation(province_id);
CREATE INDEX IF NOT EXISTS idx_provinces_trans_aliases ON ree_common.provinces_translation USING gin(aliases);

-- Districts foreign key index
CREATE INDEX IF NOT EXISTS idx_districts_province ON ree_common.districts(province_id);

-- Wards indexes
CREATE INDEX IF NOT EXISTS idx_wards_district ON ree_common.wards(district_id);
CREATE INDEX IF NOT EXISTS idx_wards_trans_lang ON ree_common.wards_translation(lang_code);
CREATE INDEX IF NOT EXISTS idx_wards_trans_id ON ree_common.wards_translation(ward_id);
CREATE INDEX IF NOT EXISTS idx_wards_trans_aliases ON ree_common.wards_translation USING gin(aliases);

-- Streets indexes
CREATE INDEX IF NOT EXISTS idx_streets_type ON ree_common.streets(street_type);
CREATE INDEX IF NOT EXISTS idx_streets_trans_lang ON ree_common.streets_translation(lang_code);
CREATE INDEX IF NOT EXISTS idx_streets_trans_id ON ree_common.streets_translation(street_id);
CREATE INDEX IF NOT EXISTS idx_streets_trans_aliases ON ree_common.streets_translation USING gin(aliases);

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT 'Administrative divisions tables created!' as status;
\dt ree_common.*;

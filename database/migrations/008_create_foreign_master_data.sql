-- Migration 008: Foreign Master Data Tables
-- Description: Add support for international markets (Japan, China, Korea, Vietnam)
-- Purpose: Extend master data to support multiple countries and currencies

-- ============================================================
-- COUNTRY & CURRENCY MASTER DATA
-- ============================================================

-- Countries Master Data
CREATE TABLE IF NOT EXISTS master_countries (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) UNIQUE NOT NULL, -- ISO 3166-1 alpha-3 (VNM, JPN, CHN, KOR)
    code_2 VARCHAR(2) UNIQUE NOT NULL, -- ISO 3166-1 alpha-2 (VN, JP, CN, KR)
    name_en VARCHAR(100) NOT NULL,
    name_local VARCHAR(100) NOT NULL, -- Local language name
    name_vi VARCHAR(100) NOT NULL, -- Vietnamese name

    -- Alternate names for flexible matching
    aliases TEXT[], -- e.g., ["Vietnam", "Việt Nam", "VN", "越南"]

    -- Country information
    region VARCHAR(50), -- 'southeast_asia', 'east_asia', etc.
    continent VARCHAR(50), -- 'asia', 'europe', etc.
    phone_code VARCHAR(10), -- +84, +81, +86, +82

    -- Default currency
    default_currency_code VARCHAR(3), -- Will reference master_currencies

    -- Popular in system
    is_primary BOOLEAN DEFAULT FALSE, -- Main focus countries
    popularity_rank INTEGER DEFAULT 999, -- Display order

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Currencies Master Data
CREATE TABLE IF NOT EXISTS master_currencies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(3) UNIQUE NOT NULL, -- ISO 4217 (VND, JPY, CNY, KRW, USD)
    symbol VARCHAR(10) NOT NULL, -- ₫, ¥, ¥, ₩, $
    name_en VARCHAR(100) NOT NULL,
    name_vi VARCHAR(100) NOT NULL,

    -- Alternate names for flexible matching
    aliases TEXT[], -- e.g., ["VND", "dong", "đồng", "việt nam đồng"]

    -- Currency information
    decimal_places INTEGER DEFAULT 0, -- VND=0, USD=2, etc.
    exchange_rate_to_usd DECIMAL(15, 6), -- For approximate conversion

    -- Display format
    format_pattern VARCHAR(50), -- e.g., "#,##0", "#,##0.00"
    symbol_position VARCHAR(10), -- 'before' or 'after' amount

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- EXTEND EXISTING TABLES WITH COUNTRY SUPPORT
-- ============================================================

-- Add country_id to districts (cities)
ALTER TABLE master_districts ADD COLUMN IF NOT EXISTS country_id INTEGER REFERENCES master_countries(id) ON DELETE SET NULL;
ALTER TABLE master_districts ADD COLUMN IF NOT EXISTS region VARCHAR(100); -- State/Province/Prefecture

-- Add country_id to developers
ALTER TABLE master_developers ADD COLUMN IF NOT EXISTS country_id INTEGER REFERENCES master_countries(id) ON DELETE SET NULL;
ALTER TABLE master_developers ADD COLUMN IF NOT EXISTS headquarters_city VARCHAR(100);

-- Add country_id to projects
ALTER TABLE master_projects ADD COLUMN IF NOT EXISTS country_id INTEGER REFERENCES master_countries(id) ON DELETE SET NULL;
ALTER TABLE master_projects ADD COLUMN IF NOT EXISTS city VARCHAR(100); -- City name

-- Add country_id to streets
ALTER TABLE master_streets ADD COLUMN IF NOT EXISTS country_id INTEGER REFERENCES master_countries(id) ON DELETE SET NULL;

-- Add country_id to property types (some types may be country-specific)
ALTER TABLE master_property_types ADD COLUMN IF NOT EXISTS country_id INTEGER REFERENCES master_countries(id) ON DELETE SET NULL;
ALTER TABLE master_property_types ADD COLUMN IF NOT EXISTS is_global BOOLEAN DEFAULT TRUE; -- TRUE = available in all countries

-- Add country_id to legal status (very country-specific)
ALTER TABLE master_legal_status ADD COLUMN IF NOT EXISTS country_id INTEGER REFERENCES master_countries(id) ON DELETE SET NULL;

-- ============================================================
-- UNIT CONVERSION MASTER DATA
-- ============================================================

-- Unit Conversions (Area & Currency)
CREATE TABLE IF NOT EXISTS master_unit_conversions (
    id SERIAL PRIMARY KEY,
    unit_type VARCHAR(20) NOT NULL, -- 'area' or 'currency'
    from_unit VARCHAR(20) NOT NULL,
    to_unit VARCHAR(20) NOT NULL,
    conversion_factor DECIMAL(20, 10) NOT NULL,

    -- Common aliases for units
    from_aliases TEXT[], -- e.g., ["sqm", "m2", "m²", "mét vuông"]
    to_aliases TEXT[], -- e.g., ["sqft", "ft2", "ft²", "feet vuông"]

    -- Description
    description TEXT,

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_conversion UNIQUE (unit_type, from_unit, to_unit)
);

-- ============================================================
-- COUNTRY-SPECIFIC PROPERTY FEATURES
-- ============================================================

-- Property Features by Country (e.g., "tatami rooms" for Japan, "feng shui" for China)
CREATE TABLE IF NOT EXISTS master_country_features (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    name_local VARCHAR(255) NOT NULL, -- In local language
    name_vi VARCHAR(255) NOT NULL,

    -- Alternate names for NLP matching
    aliases TEXT[],

    -- Country reference
    country_id INTEGER REFERENCES master_countries(id) ON DELETE CASCADE,

    -- Feature category
    category VARCHAR(50), -- 'structure', 'cultural', 'legal', 'location'

    -- Description
    description TEXT,

    -- Value impact
    value_impact_percent INTEGER, -- Estimated impact on property value

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

-- Country indexes
CREATE INDEX IF NOT EXISTS idx_countries_code ON master_countries(code);
CREATE INDEX IF NOT EXISTS idx_countries_code_2 ON master_countries(code_2);
CREATE INDEX IF NOT EXISTS idx_countries_region ON master_countries(region);
CREATE INDEX IF NOT EXISTS idx_countries_active ON master_countries(active);
CREATE INDEX IF NOT EXISTS idx_countries_primary ON master_countries(is_primary);

-- Currency indexes
CREATE INDEX IF NOT EXISTS idx_currencies_code ON master_currencies(code);
CREATE INDEX IF NOT EXISTS idx_currencies_active ON master_currencies(active);

-- District country index
CREATE INDEX IF NOT EXISTS idx_districts_country ON master_districts(country_id);

-- Developer country index
CREATE INDEX IF NOT EXISTS idx_developers_country ON master_developers(country_id);

-- Project country index
CREATE INDEX IF NOT EXISTS idx_projects_country ON master_projects(country_id);

-- Street country index
CREATE INDEX IF NOT EXISTS idx_streets_country ON master_streets(country_id);

-- Property type country index
CREATE INDEX IF NOT EXISTS idx_property_types_country ON master_property_types(country_id);

-- Legal status country index
CREATE INDEX IF NOT EXISTS idx_legal_status_country ON master_legal_status(country_id);

-- Unit conversion indexes
CREATE INDEX IF NOT EXISTS idx_unit_conversions_type ON master_unit_conversions(unit_type);
CREATE INDEX IF NOT EXISTS idx_unit_conversions_from ON master_unit_conversions(from_unit);
CREATE INDEX IF NOT EXISTS idx_unit_conversions_to ON master_unit_conversions(to_unit);

-- Country features indexes
CREATE INDEX IF NOT EXISTS idx_country_features_code ON master_country_features(code);
CREATE INDEX IF NOT EXISTS idx_country_features_country ON master_country_features(country_id);
CREATE INDEX IF NOT EXISTS idx_country_features_category ON master_country_features(category);
CREATE INDEX IF NOT EXISTS idx_country_features_active ON master_country_features(active);

-- GIN indexes for array search (aliases)
CREATE INDEX IF NOT EXISTS idx_countries_aliases ON master_countries USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_currencies_aliases ON master_currencies USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_unit_from_aliases ON master_unit_conversions USING GIN(from_aliases);
CREATE INDEX IF NOT EXISTS idx_unit_to_aliases ON master_unit_conversions USING GIN(to_aliases);
CREATE INDEX IF NOT EXISTS idx_country_features_aliases ON master_country_features USING GIN(aliases);

-- ============================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================

COMMENT ON TABLE master_countries IS 'Master data for countries supported in the platform';
COMMENT ON TABLE master_currencies IS 'Master data for currencies and exchange rates';
COMMENT ON TABLE master_unit_conversions IS 'Unit conversion factors for area and currency';
COMMENT ON TABLE master_country_features IS 'Country-specific property features (e.g., tatami rooms, feng shui)';

COMMENT ON COLUMN master_countries.is_primary IS 'Primary focus countries for the platform';
COMMENT ON COLUMN master_countries.popularity_rank IS 'Display order in UI (lower = more prominent)';
COMMENT ON COLUMN master_currencies.exchange_rate_to_usd IS 'Approximate exchange rate to USD for rough comparisons';
COMMENT ON COLUMN master_property_types.is_global IS 'TRUE if property type exists in all countries, FALSE if country-specific';

-- Migration 006: Create Master Data Tables for Extraction Service
-- Description: Reference data for property attributes validation and standardization

-- ============================================================
-- LOCATION MASTER DATA
-- ============================================================

-- Districts/Cities in Vietnam (Top-level administrative division)
CREATE TABLE IF NOT EXISTS master_districts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,

    -- Alternate names for flexible matching
    aliases TEXT[], -- e.g., ["Q7", "Q.7", "quận 7"] for "Quận 7"

    -- Geographic data
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wards (Sub-district level)
CREATE TABLE IF NOT EXISTS master_wards (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    district_id INTEGER REFERENCES master_districts(id) ON DELETE CASCADE,

    -- Alternate names for flexible matching
    aliases TEXT[],

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PROPERTY TYPE MASTER DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS master_property_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names for NLP matching
    aliases TEXT[], -- e.g., ["căn hộ", "chung cư", "apartment"]

    -- Type classification
    category VARCHAR(50), -- residential, commercial, industrial, land

    -- Typical characteristics (for validation)
    typical_min_area DECIMAL(10, 2),
    typical_max_area DECIMAL(10, 2),
    typical_min_bedrooms INTEGER,
    typical_max_bedrooms INTEGER,

    -- Icon/UI
    icon VARCHAR(100),
    description TEXT,

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TRANSACTION TYPE MASTER DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS master_transaction_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names
    aliases TEXT[], -- e.g., ["bán", "cần bán", "đang bán", "for sale"]

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- AMENITIES & FEATURES MASTER DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS master_amenities (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names for NLP matching
    aliases TEXT[], -- e.g., ["hồ bơi", "bể bơi", "swimming pool", "pool"]

    -- Category
    category VARCHAR(50), -- building_amenity, neighborhood_amenity, feature

    -- Icon/UI
    icon VARCHAR(100),
    description TEXT,

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- FURNITURE/INTERIOR MASTER DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS master_furniture_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names
    aliases TEXT[], -- e.g., ["full", "nội thất đầy đủ", "fully furnished"]

    -- Level (for ordering)
    level INTEGER DEFAULT 0, -- 0=none, 1=basic, 2=full, 3=luxury

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- DIRECTION MASTER DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS master_directions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names
    aliases TEXT[], -- e.g., ["Đông", "East", "E"]

    -- Degrees (for calculation)
    degrees INTEGER, -- 0=N, 90=E, 180=S, 270=W

    -- Feng Shui score (optional)
    feng_shui_score INTEGER,

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- LEGAL STATUS MASTER DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS master_legal_status (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names
    aliases TEXT[], -- e.g., ["sổ đỏ", "sổ hồng", "red book", "pink book"]

    -- Trust level
    trust_level INTEGER, -- 1-5 (5 = highest legal security)

    -- Description
    description TEXT,

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- PRICE RANGES BY DISTRICT (for validation)
-- ============================================================

CREATE TABLE IF NOT EXISTS master_price_ranges (
    id SERIAL PRIMARY KEY,
    district_id INTEGER REFERENCES master_districts(id) ON DELETE CASCADE,
    property_type_id INTEGER REFERENCES master_property_types(id) ON DELETE CASCADE,

    -- Price per m2 ranges (VND)
    min_price_per_m2 BIGINT,
    avg_price_per_m2 BIGINT,
    max_price_per_m2 BIGINT,

    -- Total price ranges (VND)
    min_total_price BIGINT,
    avg_total_price BIGINT,
    max_total_price BIGINT,

    -- Sample size
    sample_count INTEGER DEFAULT 0,

    -- Last updated
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(district_id, property_type_id)
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

-- Location indexes
CREATE INDEX IF NOT EXISTS idx_districts_code ON master_districts(code);
CREATE INDEX IF NOT EXISTS idx_districts_city ON master_districts(city);
CREATE INDEX IF NOT EXISTS idx_districts_active ON master_districts(active);

CREATE INDEX IF NOT EXISTS idx_wards_code ON master_wards(code);
CREATE INDEX IF NOT EXISTS idx_wards_district ON master_wards(district_id);
CREATE INDEX IF NOT EXISTS idx_wards_active ON master_wards(active);

-- Property type indexes
CREATE INDEX IF NOT EXISTS idx_property_types_code ON master_property_types(code);
CREATE INDEX IF NOT EXISTS idx_property_types_category ON master_property_types(category);
CREATE INDEX IF NOT EXISTS idx_property_types_active ON master_property_types(active);

-- Amenities indexes
CREATE INDEX IF NOT EXISTS idx_amenities_code ON master_amenities(code);
CREATE INDEX IF NOT EXISTS idx_amenities_category ON master_amenities(category);
CREATE INDEX IF NOT EXISTS idx_amenities_active ON master_amenities(active);

-- Price ranges indexes
CREATE INDEX IF NOT EXISTS idx_price_ranges_district ON master_price_ranges(district_id);
CREATE INDEX IF NOT EXISTS idx_price_ranges_property_type ON master_price_ranges(property_type_id);

-- GIN indexes for array search (aliases)
CREATE INDEX IF NOT EXISTS idx_districts_aliases ON master_districts USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_wards_aliases ON master_wards USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_property_types_aliases ON master_property_types USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_amenities_aliases ON master_amenities USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_furniture_aliases ON master_furniture_types USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_directions_aliases ON master_directions USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_legal_status_aliases ON master_legal_status USING GIN(aliases);

-- ============================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================

COMMENT ON TABLE master_districts IS 'Master data for districts/cities in Vietnam';
COMMENT ON TABLE master_wards IS 'Master data for wards (sub-districts)';
COMMENT ON TABLE master_property_types IS 'Master data for property types (căn hộ, nhà phố, etc.)';
COMMENT ON TABLE master_transaction_types IS 'Master data for transaction types (bán, cho thuê)';
COMMENT ON TABLE master_amenities IS 'Master data for property amenities and features';
COMMENT ON TABLE master_furniture_types IS 'Master data for furniture/interior levels';
COMMENT ON TABLE master_directions IS 'Master data for property/balcony directions';
COMMENT ON TABLE master_legal_status IS 'Master data for legal documentation status';
COMMENT ON TABLE master_price_ranges IS 'Statistical price ranges by district and property type';

COMMENT ON COLUMN master_districts.aliases IS 'Alternate names for fuzzy matching (e.g., Q7, Q.7, quận 7)';
COMMENT ON COLUMN master_property_types.typical_min_area IS 'Typical minimum area for this property type (for validation)';
COMMENT ON COLUMN master_amenities.category IS 'building_amenity, neighborhood_amenity, or feature';
COMMENT ON COLUMN master_price_ranges.sample_count IS 'Number of properties used to calculate this range';

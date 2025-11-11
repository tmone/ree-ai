-- Migration 007: Extended Master Data Tables
-- Description: Additional master data tables for improved extraction accuracy
-- Purpose: Normalize projects, developers, streets, building features, views, and property conditions

-- ============================================================
-- DEVELOPER & PROJECT MASTER DATA
-- ============================================================

-- Real Estate Developers (Chủ đầu tư)
CREATE TABLE IF NOT EXISTS master_developers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names for flexible matching
    aliases TEXT[], -- e.g., ["Vinhomes", "Vingroup", "Tập đoàn Vingroup"]

    -- Developer information
    type VARCHAR(50), -- 'corporation', 'private', 'government', 'joint_venture'
    reputation_score INTEGER CHECK (reputation_score >= 1 AND reputation_score <= 5), -- 1-5 stars

    -- Contact & Legal
    website VARCHAR(255),
    hotline VARCHAR(50),
    tax_code VARCHAR(50),

    -- Description
    description TEXT,
    logo_url VARCHAR(500),

    -- Statistics
    total_projects INTEGER DEFAULT 0,
    total_units_delivered INTEGER DEFAULT 0,

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Real Estate Projects (Dự án)
CREATE TABLE IF NOT EXISTS master_projects (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names for NLP matching
    aliases TEXT[], -- e.g., ["Vinhomes Central Park", "VHCP", "VCP"]

    -- References
    developer_id INTEGER REFERENCES master_developers(id) ON DELETE SET NULL,
    district_id INTEGER REFERENCES master_districts(id) ON DELETE SET NULL,

    -- Project classification
    type VARCHAR(50), -- 'luxury', 'affordable', 'mid_range', 'landed', 'highrise', 'mixed_use'
    scale VARCHAR(50), -- 'small', 'medium', 'large', 'mega'

    -- Project details
    address TEXT,
    total_area DECIMAL(10, 2), -- Total land area in hectares
    total_units INTEGER, -- Total number of units/plots
    total_buildings INTEGER, -- Number of towers/buildings

    -- Timeline
    year_started INTEGER,
    year_completed INTEGER,
    handover_status VARCHAR(50), -- 'planning', 'under_construction', 'partially_completed', 'completed'

    -- Geographic data
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Description & Media
    description TEXT,
    features TEXT[], -- Key selling points: ["riverside", "near_metro", "green_space"]
    website VARCHAR(255),
    image_url VARCHAR(500),

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- STREET MASTER DATA
-- ============================================================

-- Streets/Roads (Đường phố)
CREATE TABLE IF NOT EXISTS master_streets (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names for flexible matching
    aliases TEXT[], -- e.g., ["Nguyễn Văn Linh", "NVL", "Đường Nguyễn Văn Linh"]

    -- Location reference
    district_id INTEGER REFERENCES master_districts(id) ON DELETE SET NULL,

    -- Street classification
    type VARCHAR(50), -- 'main_road', 'secondary_road', 'alley', 'highway', 'bridge'
    width_category VARCHAR(20), -- 'large' (>20m), 'medium' (8-20m), 'small' (<8m)
    width_meters DECIMAL(5, 2), -- Actual width in meters

    -- Importance/Popularity
    importance_score INTEGER CHECK (importance_score >= 1 AND importance_score <= 5), -- 1-5

    -- Geographic data
    length_km DECIMAL(6, 2), -- Length in kilometers
    start_point VARCHAR(255),
    end_point VARCHAR(255),

    -- Description
    description TEXT,
    notable_landmarks TEXT[], -- Nearby landmarks for reference

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- BUILDING FEATURES MASTER DATA
-- ============================================================

-- Building-level Features (Tiện ích chung tòa nhà)
CREATE TABLE IF NOT EXISTS master_building_features (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names for NLP matching
    aliases TEXT[], -- e.g., ["bảo vệ 24/7", "24/7 security", "security guard"]

    -- Feature category
    category VARCHAR(50), -- 'security', 'recreation', 'services', 'facilities', 'utilities'

    -- Importance/Premium
    premium_level INTEGER CHECK (premium_level >= 1 AND premium_level <= 3), -- 1=basic, 2=standard, 3=luxury

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
-- VIEW/OUTLOOK MASTER DATA
-- ============================================================

-- Property View/Outlook Types (Hướng view)
CREATE TABLE IF NOT EXISTS master_views (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names for NLP matching
    aliases TEXT[], -- e.g., ["view sông", "river view", "hướng sông", "nhìn ra sông"]

    -- View category
    category VARCHAR(50), -- 'natural', 'urban', 'mixed'

    -- Desirability score (affects property value)
    desirability_score INTEGER CHECK (desirability_score >= 1 AND desirability_score <= 10), -- 1-10

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
-- PROPERTY CONDITION MASTER DATA
-- ============================================================

-- Property Condition/Age (Tình trạng nhà)
CREATE TABLE IF NOT EXISTS master_property_conditions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,

    -- Alternate names for NLP matching
    aliases TEXT[], -- e.g., ["nhà mới", "brand new", "new", "chưa qua sử dụng"]

    -- Typical age range
    typical_age_min INTEGER, -- Minimum age in years
    typical_age_max INTEGER, -- Maximum age in years (NULL = unlimited)

    -- Condition level
    condition_level INTEGER CHECK (condition_level >= 1 AND condition_level <= 5), -- 1=poor, 5=excellent

    -- Description
    description TEXT,

    -- Value impact (percentage)
    value_impact_percent INTEGER, -- +10%, -20%, etc.

    -- Metadata
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

-- Developer indexes
CREATE INDEX IF NOT EXISTS idx_developers_code ON master_developers(code);
CREATE INDEX IF NOT EXISTS idx_developers_type ON master_developers(type);
CREATE INDEX IF NOT EXISTS idx_developers_active ON master_developers(active);

-- Project indexes
CREATE INDEX IF NOT EXISTS idx_projects_code ON master_projects(code);
CREATE INDEX IF NOT EXISTS idx_projects_developer ON master_projects(developer_id);
CREATE INDEX IF NOT EXISTS idx_projects_district ON master_projects(district_id);
CREATE INDEX IF NOT EXISTS idx_projects_type ON master_projects(type);
CREATE INDEX IF NOT EXISTS idx_projects_status ON master_projects(handover_status);
CREATE INDEX IF NOT EXISTS idx_projects_active ON master_projects(active);

-- Street indexes
CREATE INDEX IF NOT EXISTS idx_streets_code ON master_streets(code);
CREATE INDEX IF NOT EXISTS idx_streets_district ON master_streets(district_id);
CREATE INDEX IF NOT EXISTS idx_streets_type ON master_streets(type);
CREATE INDEX IF NOT EXISTS idx_streets_active ON master_streets(active);

-- Building features indexes
CREATE INDEX IF NOT EXISTS idx_building_features_code ON master_building_features(code);
CREATE INDEX IF NOT EXISTS idx_building_features_category ON master_building_features(category);
CREATE INDEX IF NOT EXISTS idx_building_features_active ON master_building_features(active);

-- View indexes
CREATE INDEX IF NOT EXISTS idx_views_code ON master_views(code);
CREATE INDEX IF NOT EXISTS idx_views_category ON master_views(category);
CREATE INDEX IF NOT EXISTS idx_views_active ON master_views(active);

-- Property condition indexes
CREATE INDEX IF NOT EXISTS idx_property_conditions_code ON master_property_conditions(code);
CREATE INDEX IF NOT EXISTS idx_property_conditions_level ON master_property_conditions(condition_level);
CREATE INDEX IF NOT EXISTS idx_property_conditions_active ON master_property_conditions(active);

-- GIN indexes for array search (aliases)
CREATE INDEX IF NOT EXISTS idx_developers_aliases ON master_developers USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_projects_aliases ON master_projects USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_projects_features ON master_projects USING GIN(features);
CREATE INDEX IF NOT EXISTS idx_streets_aliases ON master_streets USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_streets_landmarks ON master_streets USING GIN(notable_landmarks);
CREATE INDEX IF NOT EXISTS idx_building_features_aliases ON master_building_features USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_views_aliases ON master_views USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_property_conditions_aliases ON master_property_conditions USING GIN(aliases);

-- ============================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================

COMMENT ON TABLE master_developers IS 'Master data for real estate developers (chủ đầu tư)';
COMMENT ON TABLE master_projects IS 'Master data for real estate projects (dự án)';
COMMENT ON TABLE master_streets IS 'Master data for streets and roads';
COMMENT ON TABLE master_building_features IS 'Master data for building-level features (tiện ích chung)';
COMMENT ON TABLE master_views IS 'Master data for property view/outlook types';
COMMENT ON TABLE master_property_conditions IS 'Master data for property conditions and age categories';

COMMENT ON COLUMN master_developers.reputation_score IS '1-5 star rating based on delivery record and customer satisfaction';
COMMENT ON COLUMN master_projects.scale IS 'Project scale: small (<50 units), medium (50-500), large (500-2000), mega (>2000)';
COMMENT ON COLUMN master_streets.importance_score IS 'Street importance: 1=alley, 3=regular street, 5=major road';
COMMENT ON COLUMN master_building_features.premium_level IS 'Feature premium level: 1=basic, 2=standard, 3=luxury';
COMMENT ON COLUMN master_views.desirability_score IS 'View desirability (1-10): affects property value';
COMMENT ON COLUMN master_property_conditions.value_impact_percent IS 'Estimated impact on property value (e.g., +10% for brand new, -20% for needs renovation)';

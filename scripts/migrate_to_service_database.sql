-- ================================================================
-- MIGRATION: Separate Master Data into Service Database
-- ================================================================
-- FROM: ree_ai database with master_* tables (WRONG)
-- TO:   ai_common database with clean table names (CORRECT)
-- Date: 2025-01-14
-- ================================================================

-- ================================================================
-- STEP 1: Create new database for Master Data Service
-- ================================================================

-- Connect as superuser to create database
\c postgres

-- Create dedicated database for master data service
DROP DATABASE IF EXISTS ai_common;
CREATE DATABASE ai_common
    OWNER ree_ai_user
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TEMPLATE template0;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ai_common TO ree_ai_user;

-- Connect to new database
\c ai_common

-- ================================================================
-- STEP 2: Create clean schema (no master_ prefix)
-- ================================================================

-- Amenities table (clean name)
CREATE TABLE amenities (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,                -- English only
    category VARCHAR(50),
    icon VARCHAR(100),
    description TEXT,
    active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Amenities translations
CREATE TABLE amenities_translation (
    id SERIAL PRIMARY KEY,
    amenity_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (amenity_id) REFERENCES amenities(id) ON DELETE CASCADE,
    UNIQUE (amenity_id, lang_code)
);

-- Views table (clean name)
CREATE TABLE views (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,                -- English only
    category VARCHAR(50),
    desirability_score INTEGER CHECK (desirability_score BETWEEN 1 AND 10),
    icon VARCHAR(100),
    description TEXT,
    active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Views translations
CREATE TABLE views_translation (
    id SERIAL PRIMARY KEY,
    view_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (view_id) REFERENCES views(id) ON DELETE CASCADE,
    UNIQUE (view_id, lang_code)
);

-- Districts table
CREATE TABLE districts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100) DEFAULT 'Ho Chi Minh City',
    active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Districts translations
CREATE TABLE districts_translation (
    id SERIAL PRIMARY KEY,
    district_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (district_id) REFERENCES districts(id) ON DELETE CASCADE,
    UNIQUE (district_id, lang_code)
);

-- Property Types table
CREATE TABLE property_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Property Types translations
CREATE TABLE property_types_translation (
    id SERIAL PRIMARY KEY,
    property_type_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (property_type_id) REFERENCES property_types(id) ON DELETE CASCADE,
    UNIQUE (property_type_id, lang_code)
);

-- Transaction Types table
CREATE TABLE transaction_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Types translations
CREATE TABLE transaction_types_translation (
    id SERIAL PRIMARY KEY,
    transaction_type_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (transaction_type_id) REFERENCES transaction_types(id) ON DELETE CASCADE,
    UNIQUE (transaction_type_id, lang_code)
);

-- Directions table
CREATE TABLE directions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    degrees INTEGER,                          -- Compass degrees (0-360)
    active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Directions translations
CREATE TABLE directions_translation (
    id SERIAL PRIMARY KEY,
    direction_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (direction_id) REFERENCES directions(id) ON DELETE CASCADE,
    UNIQUE (direction_id, lang_code)
);

-- ================================================================
-- STEP 3: Create indexes for performance
-- ================================================================

-- Amenities indexes
CREATE INDEX idx_amenities_code ON amenities(code);
CREATE INDEX idx_amenities_active ON amenities(active);
CREATE INDEX idx_amenities_category ON amenities(category);

CREATE INDEX idx_amenities_trans_lang ON amenities_translation(lang_code);
CREATE INDEX idx_amenities_trans_id ON amenities_translation(amenity_id);
CREATE INDEX idx_amenities_trans_aliases ON amenities_translation USING gin(aliases);

-- Views indexes
CREATE INDEX idx_views_code ON views(code);
CREATE INDEX idx_views_active ON views(active);
CREATE INDEX idx_views_score ON views(desirability_score);

CREATE INDEX idx_views_trans_lang ON views_translation(lang_code);
CREATE INDEX idx_views_trans_id ON views_translation(view_id);
CREATE INDEX idx_views_trans_aliases ON views_translation USING gin(aliases);

-- Districts indexes
CREATE INDEX idx_districts_code ON districts(code);
CREATE INDEX idx_districts_active ON districts(active);

-- ================================================================
-- STEP 4: Migrate data from old database
-- ================================================================

-- Connect to old database to export data
\c ree_ai

-- Export amenities data to temporary table
CREATE TEMP TABLE temp_amenities_data AS
SELECT
    id,
    code,
    name,
    category,
    icon,
    description,
    active,
    sort_order,
    created_at,
    updated_at
FROM master_amenities;

-- Export amenities translations
CREATE TEMP TABLE temp_amenities_translation_data AS
SELECT
    id,
    master_amenities_id as amenity_id,
    lang_code,
    translated_text,
    aliases,
    created_at,
    updated_at
FROM master_amenities_translation;

-- Export views data
CREATE TEMP TABLE temp_views_data AS
SELECT
    id,
    code,
    name,
    category,
    desirability_score,
    icon,
    description,
    active,
    sort_order,
    created_at,
    updated_at
FROM master_views;

-- Export views translations
CREATE TEMP TABLE temp_views_translation_data AS
SELECT
    id,
    master_views_id as view_id,
    lang_code,
    translated_text,
    aliases,
    created_at,
    updated_at
FROM master_views_translation;

-- Note: For production, use pg_dump and pg_restore instead of COPY
-- This is a simplified version for development

-- ================================================================
-- STEP 5: Manual data copy instructions
-- ================================================================

-- Since we can't directly copy between databases in a single transaction,
-- we'll create SQL files for data migration

\c postgres

-- Create connection info comment
SELECT '
-- ================================================================
-- DATA MIGRATION INSTRUCTIONS
-- ================================================================
--
-- 1. Export data from ree_ai database:
--    pg_dump -h localhost -U ree_ai_user -d ree_ai \
--      -t master_amenities -t master_amenities_translation \
--      -t master_views -t master_views_translation \
--      --data-only --column-inserts > /tmp/master_data_export.sql
--
-- 2. Transform table names in the export file:
--    sed -i "s/master_amenities_translation/amenities_translation/g" /tmp/master_data_export.sql
--    sed -i "s/master_amenities/amenities/g" /tmp/master_data_export.sql
--    sed -i "s/master_views_translation/views_translation/g" /tmp/master_data_export.sql
--    sed -i "s/master_views/views/g" /tmp/master_data_export.sql
--
-- 3. Import to ai_common database:
--    psql -h localhost -U ree_ai_user -d ai_common < /tmp/master_data_export.sql
--
-- ================================================================
' as migration_instructions;

-- ================================================================
-- STEP 6: Create helper views for backward compatibility
-- ================================================================

\c ai_common

-- View with Vietnamese translations (commonly used)
CREATE OR REPLACE VIEW v_amenities_vi AS
SELECT
    a.id,
    a.code,
    a.name as name_en,
    t.translated_text as name_vi,
    t.aliases,
    a.category,
    a.icon,
    a.description,
    a.active,
    a.sort_order
FROM amenities a
LEFT JOIN amenities_translation t ON a.id = t.amenity_id AND t.lang_code = 'vi';

-- View with Vietnamese translations for views
CREATE OR REPLACE VIEW v_views_vi AS
SELECT
    v.id,
    v.code,
    v.name as name_en,
    t.translated_text as name_vi,
    t.aliases,
    v.category,
    v.desirability_score,
    v.icon,
    v.description,
    v.active,
    v.sort_order
FROM views v
LEFT JOIN views_translation t ON v.id = t.view_id AND t.lang_code = 'vi';

-- ================================================================
-- STEP 7: Grant permissions
-- ================================================================

-- Grant all privileges to service user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ree_ai_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ree_ai_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO ree_ai_user;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT '
-- ================================================================
-- VERIFICATION QUERIES
-- ================================================================
' as verification;

-- Show new database
\l ai_common

-- Show new tables (no master_ prefix)
\dt

-- Show table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||''.''||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||''.''||tablename) DESC;

-- ================================================================
-- ROLLBACK PLAN
-- ================================================================

/*
-- To rollback this migration:

\c postgres

-- Drop the new database
DROP DATABASE IF EXISTS ai_common;

-- Old data remains in ree_ai database with master_* tables
\c ree_ai

-- Verify old data is intact
SELECT COUNT(*) FROM master_amenities WHERE active = true;
SELECT COUNT(*) FROM master_views WHERE active = true;
*/

-- ================================================================
-- MIGRATION: Fix i18n Structure for Master Data Tables
-- ================================================================
-- FROM: name_vi, name_en columns (WRONG)
-- TO:   name (English) + translations table (CORRECT)
-- Date: 2025-01-14
-- ================================================================

BEGIN;

-- ================================================================
-- STEP 1: Create new translation tables
-- ================================================================

-- Translation table for amenities
CREATE TABLE IF NOT EXISTS master_amenities_translation (
    id SERIAL PRIMARY KEY,
    master_amenities_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (master_amenities_id) REFERENCES master_amenities(id) ON DELETE CASCADE,
    UNIQUE (master_amenities_id, lang_code)
);

-- Translation table for views
CREATE TABLE IF NOT EXISTS master_views_translation (
    id SERIAL PRIMARY KEY,
    master_views_id INTEGER NOT NULL,
    lang_code VARCHAR(10) NOT NULL,
    translated_text VARCHAR(255) NOT NULL,
    aliases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (master_views_id) REFERENCES master_views(id) ON DELETE CASCADE,
    UNIQUE (master_views_id, lang_code)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_amenities_trans_lang ON master_amenities_translation(lang_code);
CREATE INDEX IF NOT EXISTS idx_amenities_trans_id ON master_amenities_translation(master_amenities_id);
CREATE INDEX IF NOT EXISTS idx_amenities_trans_aliases ON master_amenities_translation USING gin(aliases);

CREATE INDEX IF NOT EXISTS idx_views_trans_lang ON master_views_translation(lang_code);
CREATE INDEX IF NOT EXISTS idx_views_trans_id ON master_views_translation(master_views_id);
CREATE INDEX IF NOT EXISTS idx_views_trans_aliases ON master_views_translation USING gin(aliases);

-- ================================================================
-- STEP 2: Migrate existing data to translation tables
-- ================================================================

-- Migrate amenities: Vietnamese translations
INSERT INTO master_amenities_translation (master_amenities_id, lang_code, translated_text, aliases)
SELECT
    id,
    'vi' as lang_code,
    name_vi as translated_text,
    aliases
FROM master_amenities
WHERE name_vi IS NOT NULL
ON CONFLICT (master_amenities_id, lang_code) DO UPDATE
SET
    translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- Migrate amenities: English translations
INSERT INTO master_amenities_translation (master_amenities_id, lang_code, translated_text, aliases)
SELECT
    id,
    'en' as lang_code,
    name_en as translated_text,
    aliases
FROM master_amenities
WHERE name_en IS NOT NULL
ON CONFLICT (master_amenities_id, lang_code) DO UPDATE
SET
    translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- Migrate views: Vietnamese translations
INSERT INTO master_views_translation (master_views_id, lang_code, translated_text, aliases)
SELECT
    id,
    'vi' as lang_code,
    name_vi as translated_text,
    aliases
FROM master_views
WHERE name_vi IS NOT NULL
ON CONFLICT (master_views_id, lang_code) DO UPDATE
SET
    translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- Migrate views: English translations
INSERT INTO master_views_translation (master_views_id, lang_code, translated_text, aliases)
SELECT
    id,
    'en' as lang_code,
    name_en as translated_text,
    aliases
FROM master_views
WHERE name_en IS NOT NULL
ON CONFLICT (master_views_id, lang_code) DO UPDATE
SET
    translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ================================================================
-- STEP 3: Add 'name' column (English only) to master tables
-- ================================================================

-- Add name column to master_amenities (use name_en as default)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_amenities' AND column_name = 'name'
    ) THEN
        ALTER TABLE master_amenities ADD COLUMN name VARCHAR(255);
        UPDATE master_amenities SET name = name_en;
        ALTER TABLE master_amenities ALTER COLUMN name SET NOT NULL;
    END IF;
END $$;

-- Add name column to master_views (use name_en as default)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'master_views' AND column_name = 'name'
    ) THEN
        ALTER TABLE master_views ADD COLUMN name VARCHAR(255);
        UPDATE master_views SET name = name_en;
        ALTER TABLE master_views ALTER COLUMN name SET NOT NULL;
    END IF;
END $$;

-- ================================================================
-- STEP 4: Drop old columns (name_vi, name_en, aliases)
-- ================================================================

-- Drop from master_amenities
ALTER TABLE master_amenities
    DROP COLUMN IF EXISTS name_vi,
    DROP COLUMN IF EXISTS name_en,
    DROP COLUMN IF EXISTS aliases;

-- Drop from master_views
ALTER TABLE master_views
    DROP COLUMN IF EXISTS name_vi,
    DROP COLUMN IF EXISTS name_en,
    DROP COLUMN IF EXISTS aliases;

-- ================================================================
-- STEP 5: Create helper views for backward compatibility
-- ================================================================

-- View with Vietnamese translations
CREATE OR REPLACE VIEW v_master_amenities_vi AS
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
    a.sort_order,
    a.created_at,
    a.updated_at
FROM master_amenities a
LEFT JOIN master_amenities_translation t
    ON a.id = t.master_amenities_id AND t.lang_code = 'vi';

-- View with Vietnamese translations for views
CREATE OR REPLACE VIEW v_master_views_vi AS
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
    v.sort_order,
    v.created_at,
    v.updated_at
FROM master_views v
LEFT JOIN master_views_translation t
    ON v.id = t.master_views_id AND t.lang_code = 'vi';

-- ================================================================
-- STEP 6: Verification queries
-- ================================================================

-- Verify amenities migration
SELECT
    'Amenities Migration Check' as check_type,
    (SELECT COUNT(*) FROM master_amenities WHERE active = true) as master_count,
    (SELECT COUNT(DISTINCT master_amenities_id) FROM master_amenities_translation WHERE lang_code = 'vi') as vi_count,
    (SELECT COUNT(DISTINCT master_amenities_id) FROM master_amenities_translation WHERE lang_code = 'en') as en_count;

-- Verify views migration
SELECT
    'Views Migration Check' as check_type,
    (SELECT COUNT(*) FROM master_views WHERE active = true) as master_count,
    (SELECT COUNT(DISTINCT master_views_id) FROM master_views_translation WHERE lang_code = 'vi') as vi_count,
    (SELECT COUNT(DISTINCT master_views_id) FROM master_views_translation WHERE lang_code = 'en') as en_count;

COMMIT;

-- ================================================================
-- USAGE EXAMPLES AFTER MIGRATION
-- ================================================================

/*
-- Get amenity with Vietnamese translation
SELECT
    a.code,
    a.name as name_en,
    t.translated_text as name_vi,
    t.aliases
FROM master_amenities a
LEFT JOIN master_amenities_translation t
    ON a.id = t.master_amenities_id AND t.lang_code = 'vi'
WHERE a.code = 'SWIMMING_POOL';

-- Get amenity with ALL translations
SELECT
    a.code,
    a.name as name_en,
    t.lang_code,
    t.translated_text,
    t.aliases
FROM master_amenities a
LEFT JOIN master_amenities_translation t ON a.id = t.master_amenities_id
WHERE a.code = 'SWIMMING_POOL'
ORDER BY t.lang_code;

-- Add new language (Chinese)
INSERT INTO master_amenities_translation (master_amenities_id, lang_code, translated_text, aliases)
SELECT
    id,
    'zh',
    '游泳池',
    ARRAY['游泳池', '泳池', '游泳场']
FROM master_amenities
WHERE code = 'SWIMMING_POOL';

-- Fuzzy search with Vietnamese
SELECT DISTINCT a.code, a.name, t.translated_text
FROM master_amenities a
JOIN master_amenities_translation t ON a.id = t.master_amenities_id
WHERE t.lang_code = 'vi'
  AND a.active = true
  AND EXISTS (
      SELECT 1 FROM unnest(t.aliases) alias
      WHERE LOWER('Căn hộ có hồ bơi') LIKE '%' || LOWER(alias) || '%'
  );
*/

-- ================================================================
-- ROLLBACK PLAN (if needed)
-- ================================================================

/*
-- To rollback this migration:

BEGIN;

-- Restore old columns
ALTER TABLE master_amenities
    ADD COLUMN IF NOT EXISTS name_vi VARCHAR(255),
    ADD COLUMN IF NOT EXISTS name_en VARCHAR(255),
    ADD COLUMN IF NOT EXISTS aliases TEXT[];

UPDATE master_amenities a
SET
    name_en = a.name,
    name_vi = (SELECT translated_text FROM master_amenities_translation
               WHERE master_amenities_id = a.id AND lang_code = 'vi' LIMIT 1),
    aliases = (SELECT aliases FROM master_amenities_translation
               WHERE master_amenities_id = a.id AND lang_code = 'vi' LIMIT 1);

-- Drop new tables
DROP TABLE IF EXISTS master_amenities_translation CASCADE;
DROP TABLE IF EXISTS master_views_translation CASCADE;

-- Drop helper views
DROP VIEW IF EXISTS v_master_amenities_vi CASCADE;
DROP VIEW IF EXISTS v_master_views_vi CASCADE;

-- Drop name column
ALTER TABLE master_amenities DROP COLUMN IF EXISTS name;
ALTER TABLE master_views DROP COLUMN IF EXISTS name;

COMMIT;
*/

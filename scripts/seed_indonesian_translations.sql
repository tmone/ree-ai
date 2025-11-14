-- ================================================================
-- SEED BAHASA INDONESIA TRANSLATIONS FOR INDONESIA PROVINCES
-- ================================================================
-- PURPOSE: Add Bahasa Indonesia translations and aliases for all 17 Indonesia provinces
-- DATE: 2025-11-14
-- COVERAGE: 17 major Indonesia provinces with Bahasa Indonesia names and aliases
-- ================================================================

BEGIN;

-- Delete existing Indonesian translations for Indonesia (if any)
DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'id'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'ID')
  );

-- Insert Bahasa Indonesia translations with comprehensive aliases
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases) VALUES

-- Special Capital Region (1)
((SELECT id FROM ree_common.provinces WHERE code = 'ID_JAKARTA'), 'id', 'DKI Jakarta',
 ARRAY['dki jakarta', 'jakarta', 'dki', 'jakarta raya', 'ibukota', 'capital', 'jkt']),

-- Java Island - Special Regions (2)
((SELECT id FROM ree_common.provinces WHERE code = 'ID_YOGYAKARTA'), 'id', 'DI Yogyakarta',
 ARRAY['di yogyakarta', 'yogyakarta', 'yogya', 'jogja', 'jogjakarta', 'diy', 'yk']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_ACEH'), 'id', 'Aceh',
 ARRAY['aceh', 'nanggroe aceh darussalam', 'nad', 'banda aceh']),

-- Java Island - Main Provinces (3)
((SELECT id FROM ree_common.provinces WHERE code = 'ID_WEST_JAVA'), 'id', 'Jawa Barat',
 ARRAY['jawa barat', 'jabar', 'west java', 'bandung', 'bogor', 'jawa barat prov']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_CENTRAL_JAVA'), 'id', 'Jawa Tengah',
 ARRAY['jawa tengah', 'jateng', 'central java', 'semarang', 'solo', 'jawa tengah prov']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_EAST_JAVA'), 'id', 'Jawa Timur',
 ARRAY['jawa timur', 'jatim', 'east java', 'surabaya', 'malang', 'jawa timur prov']),

-- Java - Banten (1)
((SELECT id FROM ree_common.provinces WHERE code = 'ID_BANTEN'), 'id', 'Banten',
 ARRAY['banten', 'serang', 'tangerang', 'banten province']),

-- Sumatra Island (6)
((SELECT id FROM ree_common.provinces WHERE code = 'ID_NORTH_SUMATRA'), 'id', 'Sumatera Utara',
 ARRAY['sumatera utara', 'sumut', 'north sumatra', 'medan', 'sumatera utara prov']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_WEST_SUMATRA'), 'id', 'Sumatera Barat',
 ARRAY['sumatera barat', 'sumbar', 'west sumatra', 'padang', 'sumatera barat prov']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_SOUTH_SUMATRA'), 'id', 'Sumatera Selatan',
 ARRAY['sumatera selatan', 'sumsel', 'south sumatra', 'palembang', 'sumatera selatan prov']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_RIAU'), 'id', 'Riau',
 ARRAY['riau', 'pekanbaru', 'riau province']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_LAMPUNG'), 'id', 'Lampung',
 ARRAY['lampung', 'bandar lampung', 'lampung province']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_BENGKULU'), 'id', 'Bengkulu',
 ARRAY['bengkulu', 'bencoolen', 'bengkulu province']),

-- Bali (Tourism Hub) (1)
((SELECT id FROM ree_common.provinces WHERE code = 'ID_BALI'), 'id', 'Bali',
 ARRAY['bali', 'denpasar', 'bali island', 'pulau bali', 'bali province']),

-- Kalimantan (Borneo) (2)
((SELECT id FROM ree_common.provinces WHERE code = 'ID_EAST_KALIMANTAN'), 'id', 'Kalimantan Timur',
 ARRAY['kalimantan timur', 'kaltim', 'east kalimantan', 'balikpapan', 'samarinda']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_SOUTH_KALIMANTAN'), 'id', 'Kalimantan Selatan',
 ARRAY['kalimantan selatan', 'kalsel', 'south kalimantan', 'banjarmasin']),

-- Sulawesi (2)
((SELECT id FROM ree_common.provinces WHERE code = 'ID_NORTH_SULAWESI'), 'id', 'Sulawesi Utara',
 ARRAY['sulawesi utara', 'sulut', 'north sulawesi', 'manado', 'sulawesi utara prov']),
((SELECT id FROM ree_common.provinces WHERE code = 'ID_SOUTH_SULAWESI'), 'id', 'Sulawesi Selatan',
 ARRAY['sulawesi selatan', 'sulsel', 'south sulawesi', 'makassar', 'sulawesi selatan prov'])

ON CONFLICT (province_id, lang_code) DO UPDATE
SET translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

-- Count Indonesian translations
SELECT
    'Indonesian translations added' as metric,
    COUNT(*) as count
FROM ree_common.provinces_translation
WHERE lang_code = 'id'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'ID')
  );

-- Show sample Indonesian provinces
SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_id,
    array_length(t.aliases, 1) as alias_count
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'id'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'ID')
ORDER BY p.sort_order
LIMIT 10;

-- ================================================================
-- SEED KHMER TRANSLATIONS FOR CAMBODIA PROVINCES
-- ================================================================
-- PURPOSE: Add Khmer language translations and aliases for all 25 Cambodia provinces
-- DATE: 2025-11-14
-- COVERAGE: 25 Cambodia provinces with Khmer names and aliases
-- ================================================================

BEGIN;

-- Delete existing Khmer translations for Cambodia (if any)
DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'km'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'KH')
  );

-- Insert Khmer translations with comprehensive aliases
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases) VALUES

-- Municipalities (3)
((SELECT id FROM ree_common.provinces WHERE code = 'KH_PHNOM_PENH'), 'km', 'ភ្នំពេញ',
 ARRAY['ភ្នំពេញ', 'phnom penh', 'phnompenh', 'pp', 'phnom pen', 'capital']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KEP'), 'km', 'កែប',
 ARRAY['កែប', 'kep', 'keb']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_PAILIN'), 'km', 'ប៉ៃលិន',
 ARRAY['ប៉ៃលិន', 'pailin', 'pai lin']),

-- Provinces - Tourism & Major Cities (22)
((SELECT id FROM ree_common.provinces WHERE code = 'KH_SIEM_REAP'), 'km', 'សៀមរាប',
 ARRAY['សៀមរាប', 'siem reap', 'siemreap', 'angkor', 'អង្គរ', 'angkor wat']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_BATTAMBANG'), 'km', 'បាត់ដំបង',
 ARRAY['បាត់ដំបង', 'battambang', 'batdambang', 'bat dambang']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_PREAH_SIHANOUK'), 'km', 'ព្រះសីហនុ',
 ARRAY['ព្រះសីហនុ', 'preah sihanouk', 'sihanoukville', 'sihanukville', 'kompong som', 'កំពង់សោម']),

-- Border provinces with Vietnam
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KAMPONG_CHAM'), 'km', 'កំពង់ចាម',
 ARRAY['កំពង់ចាម', 'kampong cham', 'kompong cham', 'kampongcham']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_SVAY_RIENG'), 'km', 'ស្វាយរៀង',
 ARRAY['ស្វាយរៀង', 'svay rieng', 'svayrieng', 'svay reng']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_PREY_VENG'), 'km', 'ព្រៃវែង',
 ARRAY['ព្រៃវែង', 'prey veng', 'preyveng', 'prey veaeng']),

-- Coastal provinces
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KOH_KONG'), 'km', 'កោះកុង',
 ARRAY['កោះកុង', 'koh kong', 'kohkong', 'kaoh kong']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KAMPOT'), 'km', 'កំពត',
 ARRAY['កំពត', 'kampot', 'kampot province']),

-- Central provinces
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KANDAL'), 'km', 'កណ្ដាល',
 ARRAY['កណ្ដាល', 'kandal', 'kandal province']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KAMPONG_SPEU'), 'km', 'កំពង់ស្ពឺ',
 ARRAY['កំពង់ស្ពឺ', 'kampong speu', 'kampong spueu', 'kompong speu']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KAMPONG_THOM'), 'km', 'កំពង់ធំ',
 ARRAY['កំពង់ធំ', 'kampong thom', 'kampongthom', 'kompong thom']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KAMPONG_CHHNANG'), 'km', 'កំពង់ឆ្នាំង',
 ARRAY['កំពង់ឆ្នាំង', 'kampong chhnang', 'kampongchhnang', 'kompong chhnang']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_TAKEO'), 'km', 'តាកែវ',
 ARRAY['តាកែវ', 'takeo', 'takev', 'ta keo']),

-- Eastern provinces
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KRATIE'), 'km', 'ក្រចេះ',
 ARRAY['ក្រចេះ', 'kratie', 'kracheh', 'kratié']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_STUNG_TRENG'), 'km', 'ស្ទឹងត្រែង',
 ARRAY['ស្ទឹងត្រែង', 'stung treng', 'stoeng treng', 'stungtreng']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_RATANAKIRI'), 'km', 'រតនគិរី',
 ARRAY['រតនគិរី', 'ratanakiri', 'ratanak kiri', 'ratanakkiri']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_MONDULKIRI'), 'km', 'មណ្ឌលគិរី',
 ARRAY['មណ្ឌលគិរី', 'mondulkiri', 'mondol kiri', 'mondolkiri']),

-- Northern provinces
((SELECT id FROM ree_common.provinces WHERE code = 'KH_BANTEAY_MEANCHEY'), 'km', 'បន្ទាយមានជ័យ',
 ARRAY['បន្ទាយមានជ័យ', 'banteay meanchey', 'banteaymeanchey', 'bantey meanchey']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_ODDAR_MEANCHEY'), 'km', 'ឧត្តរមានជ័យ',
 ARRAY['ឧត្តរមានជ័យ', 'oddar meanchey', 'oddarmeanchey', 'otdar meanchey']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_PREAH_VIHEAR'), 'km', 'ព្រះវិហារ',
 ARRAY['ព្រះវិហារ', 'preah vihear', 'preahvihear', 'preah vihea']),

-- Western provinces
((SELECT id FROM ree_common.provinces WHERE code = 'KH_PURSAT'), 'km', 'ពោធិ៍សាត់',
 ARRAY['ពោធិ៍សាត់', 'pursat', 'posat']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_TBONG_KHMUM'), 'km', 'ត្បូងឃ្មុំ',
 ARRAY['ត្បូងឃ្មុំ', 'tbong khmum', 'tboung khmum']),

-- Southern provinces
((SELECT id FROM ree_common.provinces WHERE code = 'KH_PREAH_SEIHANU'), 'km', 'ព្រះសីហនុ',
 ARRAY['ព្រះសីហនុ', 'preah seihanu', 'sihanouk']),
((SELECT id FROM ree_common.provinces WHERE code = 'KH_KOH_RONG'), 'km', 'កោះរ៉ុង',
 ARRAY['កោះរ៉ុង', 'koh rong', 'kohrong', 'koh rong island'])

ON CONFLICT (province_id, lang_code) DO UPDATE
SET translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

-- Count Khmer translations
SELECT
    'Khmer translations added' as metric,
    COUNT(*) as count
FROM ree_common.provinces_translation
WHERE lang_code = 'km'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'KH')
  );

-- Show sample Khmer provinces
SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_km,
    array_length(t.aliases, 1) as alias_count
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'km'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'KH')
ORDER BY p.sort_order
LIMIT 10;

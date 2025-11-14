-- ================================================================
-- SEED BURMESE TRANSLATIONS FOR MYANMAR REGIONS/STATES
-- ================================================================
-- PURPOSE: Add Burmese language translations and aliases for all 14 Myanmar regions/states
-- DATE: 2025-11-14
-- COVERAGE: 14 Myanmar regions/states with Burmese names and aliases
-- ================================================================

BEGIN;

-- Delete existing Burmese translations for Myanmar (if any)
DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'my'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'MM')
  );

-- Insert Burmese translations with comprehensive aliases
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases) VALUES

-- Union Territory - Capital (1)
((SELECT id FROM ree_common.provinces WHERE code = 'MM_NAYPYIDAW'), 'my', 'နေပြည်တော်',
 ARRAY['နေပြည်တော်', 'naypyidaw', 'naypyitaw', 'nay pyi taw', 'capital', 'npt']),

-- Regions (7)
((SELECT id FROM ree_common.provinces WHERE code = 'MM_YANGON'), 'my', 'ရန်ကုန်တိုင်း',
 ARRAY['ရန်ကုန်တိုင်း', 'ရန်ကုန်', 'yangon', 'rangoon', 'yangon region', 'ygn', 'yangon city']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_MANDALAY'), 'my', 'မန္တလေးတိုင်း',
 ARRAY['မန္တလေးတိုင်း', 'မန္တလေး', 'mandalay', 'mandalay region', 'mdy', 'mandalay city']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_BAGO'), 'my', 'ပဲခူးတိုင်း',
 ARRAY['ပဲခူးတိုင်း', 'bago', 'pegu', 'bago region']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_AYEYARWADY'), 'my', 'ဧရာဝတီတိုင်း',
 ARRAY['ဧရာဝတီတိုင်း', 'ayeyarwady', 'ayeyarwaddy', 'irrawaddy', 'ayeyarwady region']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_MAGWAY'), 'my', 'မကွေးတိုင်း',
 ARRAY['မကွေးတိုင်း', 'magway', 'magwe', 'magway region']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_SAGAING'), 'my', 'စစ်ကိုင်းတိုင်း',
 ARRAY['စစ်ကိုင်းတိုင်း', 'sagaing', 'sagaing region']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_TANINTHARYI'), 'my', 'တနင်္သာရီတိုင်း',
 ARRAY['တနင်္သာရီတိုင်း', 'tanintharyi', 'taninthayi', 'tenasserim', 'tanintharyi region']),

-- States (7)
((SELECT id FROM ree_common.provinces WHERE code = 'MM_SHAN'), 'my', 'ရှမ်းပြည်နယ်',
 ARRAY['ရှမ်းပြည်နယ်', 'shan', 'shan state', 'taunggyi', 'inle lake']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_KACHIN'), 'my', 'ကချင်ပြည်နယ်',
 ARRAY['ကချင်ပြည်နယ်', 'kachin', 'kachin state', 'myitkyina']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_RAKHINE'), 'my', 'ရခိုင်ပြည်နယ်',
 ARRAY['ရခိုင်ပြည်နယ်', 'rakhine', 'arakan', 'rakhine state', 'sittwe']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_KAYIN'), 'my', 'ကရင်ပြည်နယ်',
 ARRAY['ကရင်ပြည်နယ်', 'kayin', 'karen', 'kayin state', 'hpa-an']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_KAYAH'), 'my', 'ကယားပြည်နယ်',
 ARRAY['ကယားပြည်နယ်', 'kayah', 'karenni', 'kayah state', 'loikaw']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_MON'), 'my', 'မွန်ပြည်နယ်',
 ARRAY['မွန်ပြည်နယ်', 'mon', 'mon state', 'mawlamyine', 'moulmein']),
((SELECT id FROM ree_common.provinces WHERE code = 'MM_CHIN'), 'my', 'ချင်းပြည်နယ်',
 ARRAY['ချင်းပြည်နယ်', 'chin', 'chin state', 'hakha'])

ON CONFLICT (province_id, lang_code) DO UPDATE
SET translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

-- Count Burmese translations
SELECT
    'Burmese translations added' as metric,
    COUNT(*) as count
FROM ree_common.provinces_translation
WHERE lang_code = 'my'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'MM')
  );

-- Show sample Myanmar regions
SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_my,
    array_length(t.aliases, 1) as alias_count
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'my'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'MM')
ORDER BY p.sort_order
LIMIT 10;

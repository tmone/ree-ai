-- ================================================================
-- SEED LAO TRANSLATIONS FOR LAOS PROVINCES
-- ================================================================
-- PURPOSE: Add Lao language translations and aliases for all 18 Laos provinces
-- DATE: 2025-11-14
-- COVERAGE: 18 Laos provinces with Lao names and aliases
-- ================================================================

BEGIN;

-- Delete existing Lao translations for Laos (if any)
DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'lo'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'LA')
  );

-- Insert Lao translations with comprehensive aliases
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases) VALUES

-- Capital Prefecture (1)
((SELECT id FROM ree_common.provinces WHERE code = 'LA_VIENTIANE_CAPITAL'), 'lo', 'ນະຄອນຫຼວງວຽງຈັນ',
 ARRAY['ນະຄອນຫຼວງວຽງຈັນ', 'vientiane', 'viangchan', 'wiangchan', 'vte', 'capital', 'ວຽງຈັນ']),

-- UNESCO Heritage & Tourism (2)
((SELECT id FROM ree_common.provinces WHERE code = 'LA_LUANG_PRABANG'), 'lo', 'ຫຼວງພະບາງ',
 ARRAY['ຫຼວງພະບາງ', 'luang prabang', 'luangprabang', 'luang phrabang', 'lpb', 'unesco']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_VANG_VIENG'), 'lo', 'ວັງວຽງ',
 ARRAY['ວັງວຽງ', 'vang vieng', 'vangvieng', 'vang viang']),

-- Southern Provinces (4)
((SELECT id FROM ree_common.provinces WHERE code = 'LA_CHAMPASAK'), 'lo', 'ຈຳປາສັກ',
 ARRAY['ຈຳປາສັກ', 'champasak', 'champassak', 'champasack', 'pakse', 'ປາກເຊ']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_SAVANNAKHET'), 'lo', 'ສະຫວັນນະເຂດ',
 ARRAY['ສະຫວັນນະເຂດ', 'savannakhet', 'savannakhet province', 'savan']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_ATTAPEU'), 'lo', 'ອັດຕະປື',
 ARRAY['ອັດຕະປື', 'attapeu', 'attapu', 'attopu']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_SALAVAN'), 'lo', 'ສາລະວັນ',
 ARRAY['ສາລະວັນ', 'salavan', 'saravan', 'saravane']),

-- Northern Provinces (4)
((SELECT id FROM ree_common.provinces WHERE code = 'LA_PHONGSALI'), 'lo', 'ຜົ້ງສາລີ',
 ARRAY['ຜົ້ງສາລີ', 'phongsali', 'phongsaly', 'phong sali']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_LUANG_NAMTHA'), 'lo', 'ຫຼວງນໍ້າທາ',
 ARRAY['ຫຼວງນໍ້າທາ', 'luang namtha', 'luangnamtha', 'louang namtha']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_BOKEO'), 'lo', 'ບໍ່ແກ້ວ',
 ARRAY['ບໍ່ແກ້ວ', 'bokeo', 'bokèo', 'bo kaeo']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_OUDOMXAI'), 'lo', 'ອຸດົມໄຊ',
 ARRAY['ອຸດົມໄຊ', 'oudomxai', 'oudomxay', 'udomxai']),

-- Central Provinces (4)
((SELECT id FROM ree_common.provinces WHERE code = 'LA_BOLIKHAMXAI'), 'lo', 'ບໍລິຄຳໄຊ',
 ARRAY['ບໍລິຄຳໄຊ', 'bolikhamxai', 'bolikhamsai', 'boli khamxai']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_KHAMMOUANE'), 'lo', 'ຄຳມ່ວນ',
 ARRAY['ຄຳມ່ວນ', 'khammouane', 'khammouan', 'khammuan']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_VIENTIANE_PROVINCE'), 'lo', 'ແຂວງວຽງຈັນ',
 ARRAY['ແຂວງວຽງຈັນ', 'vientiane province', 'vientiane prov', 'viangchan province']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_XAISOMBOUN'), 'lo', 'ໄຊສົມບູນ',
 ARRAY['ໄຊສົມບູນ', 'xaisomboun', 'xaisombun', 'xai somboun']),

-- Mountainous Provinces (3)
((SELECT id FROM ree_common.provinces WHERE code = 'LA_HOUAPHANH'), 'lo', 'ຫົວພັນ',
 ARRAY['ຫົວພັນ', 'houaphanh', 'houaphan', 'hua phan']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_XIANGKHOUANG'), 'lo', 'ຊຽງຂວາງ',
 ARRAY['ຊຽງຂວາງ', 'xiangkhouang', 'xiangkhuang', 'xieng khouang', 'plain of jars']),
((SELECT id FROM ree_common.provinces WHERE code = 'LA_SEKONG'), 'lo', 'ເຊກອງ',
 ARRAY['ເຊກອງ', 'sekong', 'xekong', 'se kong'])

ON CONFLICT (province_id, lang_code) DO UPDATE
SET translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

-- Count Lao translations
SELECT
    'Lao translations added' as metric,
    COUNT(*) as count
FROM ree_common.provinces_translation
WHERE lang_code = 'lo'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'LA')
  );

-- Show sample Lao provinces
SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_lo,
    array_length(t.aliases, 1) as alias_count
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'lo'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'LA')
ORDER BY p.sort_order
LIMIT 10;

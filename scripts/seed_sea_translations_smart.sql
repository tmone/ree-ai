-- ================================================================
-- SMART SEA TRANSLATIONS DEPLOYMENT
-- ================================================================
-- PURPOSE: Deploy translations only for provinces that exist in database
-- DATE: 2025-11-14
-- METHOD: Use temporary tables and safe lookups
-- ================================================================

\echo '================================================================'
\echo 'SMART SEA TRANSLATIONS DEPLOYMENT'
\echo '================================================================'
\echo ''

BEGIN;

-- ================================================================
-- THAILAND - Thai Translations
-- ================================================================
\echo 'Processing Thailand (Thai)...'

CREATE TEMP TABLE thai_trans_temp (
    code VARCHAR(50),
    translated_text VARCHAR(255),
    aliases TEXT[]
);

INSERT INTO thai_trans_temp (code, translated_text, aliases) VALUES
('TH_BANGKOK', 'กรุงเทพมหานคร', ARRAY['กรุงเทพมหานคร', 'กรุงเทพ', 'bangkok', 'bkk', 'krung thep', 'กทม']),
('TH_CHIANG_MAI', 'เชียงใหม่', ARRAY['เชียงใหม่', 'chiangmai', 'chiang mai', 'เชียงใหม่จังหวัด']),
('TH_CHIANG_RAI', 'เชียงราย', ARRAY['เชียงราย', 'chiangrai', 'chiang rai', 'เชียงรายจังหวัด']),
('TH_PHUKET', 'ภูเก็ต', ARRAY['ภูเก็ต', 'phuket', 'phu ket', 'ภูเก็ตจังหวัด']),
('TH_KRABI', 'กระบี่', ARRAY['กระบี่', 'krabi', 'kra bi', 'ao nang', 'อ่าวนาง']),
('TH_SURAT_THANI', 'สุราษฎร์ธานี', ARRAY['สุราษฎร์ธานี', 'surat thani', 'suratthani', 'koh samui', 'เกาะสมุย']),
('TH_SONGKHLA', 'สงขลา', ARRAY['สงขลา', 'songkhla', 'song khla', 'hat yai', 'หาดใหญ่']),
('TH_NAKHON_RATCHASIMA', 'นครราชสีมา', ARRAY['นครราชสีมา', 'nakhon ratchasima', 'korat', 'โคราช']),
('TH_KHON_KAEN', 'ขอนแก่น', ARRAY['ขอนแก่น', 'khon kaen', 'khonkaen']),
('TH_UDON_THANI', 'อุดรธานี', ARRAY['อุดรธานี', 'udon thani', 'udonthani', 'udon']),
('TH_CHONBURI', 'ชลบุรี', ARRAY['ชลบุรี', 'chonburi', 'chon buri', 'pattaya', 'พัทยา']),
('TH_RAYONG', 'ระยอง', ARRAY['ระยอง', 'rayong', 'ra yong']),
('TH_PHRA_NAKHON_SI_AYUTTHAYA', 'พระนครศรีอยุธยา', ARRAY['พระนครศรีอยุธยา', 'อยุธยา', 'ayutthaya', 'ayudhya']);

DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'th'
  AND province_id IN (SELECT id FROM ree_common.provinces WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'TH'));

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT p.id, 'th', t.translated_text, t.aliases
FROM thai_trans_temp t
JOIN ree_common.provinces p ON p.code = t.code
WHERE p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'TH');

\echo 'Thailand: Added ' || (SELECT COUNT(*) FROM ree_common.provinces_translation WHERE lang_code = 'th') || ' translations'

-- ================================================================
-- CAMBODIA - Khmer Translations
-- ================================================================
\echo 'Processing Cambodia (Khmer)...'

CREATE TEMP TABLE khmer_trans_temp (
    code VARCHAR(50),
    translated_text VARCHAR(255),
    aliases TEXT[]
);

INSERT INTO khmer_trans_temp (code, translated_text, aliases) VALUES
('KH_PHNOM_PENH', 'ភ្នំពេញ', ARRAY['ភ្នំពេញ', 'phnom penh', 'phnompenh', 'pp', 'phnom pen', 'capital']),
('KH_SIEM_REAP', 'សៀមរាប', ARRAY['សៀមរាប', 'siem reap', 'siemreap', 'angkor', 'អង្គរ', 'angkor wat']),
('KH_BATTAMBANG', 'បាត់ដំបង', ARRAY['បាត់ដំបង', 'battambang', 'batdambang', 'bat dambang']),
('KH_PREAH_SIHANOUK', 'ព្រះសីហនុ', ARRAY['ព្រះសីហនុ', 'preah sihanouk', 'sihanoukville', 'sihanukville', 'kampong som', 'កំពង់សោម']),
('KH_SIHANOUKVILLE', 'ព្រះសីហនុ', ARRAY['ព្រះសីហនុ', 'sihanoukville', 'sihanukville', 'kompong som']),
('KH_KAMPONG_CHAM', 'កំពង់ចាម', ARRAY['កំពង់ចាម', 'kampong cham', 'kompong cham', 'kampongcham']),
('KH_SVAY_RIENG', 'ស្វាយរៀង', ARRAY['ស្វាយរៀង', 'svay rieng', 'svayrieng', 'svay reng']),
('KH_KOH_KONG', 'កោះកុង', ARRAY['កោះកុង', 'koh kong', 'kohkong', 'kaoh kong']),
('KH_KAMPOT', 'កំពត', ARRAY['កំពត', 'kampot', 'kampot province']),
('KH_KEP', 'កែប', ARRAY['កែប', 'kep', 'keb']),
('KH_PAILIN', 'ប៉ៃលិន', ARRAY['ប៉ៃលិន', 'pailin', 'pai lin']);

DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'km'
  AND province_id IN (SELECT id FROM ree_common.provinces WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'KH'));

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT p.id, 'km', t.translated_text, t.aliases
FROM khmer_trans_temp t
JOIN ree_common.provinces p ON p.code = t.code
WHERE p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'KH');

\echo 'Cambodia: Added ' || (SELECT COUNT(*) FROM ree_common.provinces_translation WHERE lang_code = 'km') || ' translations'

-- ================================================================
-- LAOS - Lao Translations
-- ================================================================
\echo 'Processing Laos (Lao)...'

CREATE TEMP TABLE lao_trans_temp (
    code VARCHAR(50),
    translated_text VARCHAR(255),
    aliases TEXT[]
);

INSERT INTO lao_trans_temp (code, translated_text, aliases) VALUES
('LA_VIENTIANE', 'ນະຄອນຫຼວງວຽງຈັນ', ARRAY['ນະຄອນຫຼວງວຽງຈັນ', 'vientiane', 'viangchan', 'wiangchan', 'vte', 'capital', 'ວຽງຈັນ']),
('LA_LUANG_PRABANG', 'ຫຼວງພະບາງ', ARRAY['ຫຼວງພະບາງ', 'luang prabang', 'luangprabang', 'luang phrabang', 'lpb', 'unesco']),
('LA_CHAMPASAK', 'ຈຳປາສັກ', ARRAY['ຈຳປາສັກ', 'champasak', 'champassak', 'champasack', 'pakse', 'ປາກເຊ']),
('LA_SAVANNAKHET', 'ສະຫວັນນະເຂດ', ARRAY['ສະຫວັນນະເຂດ', 'savannakhet', 'savannakhet province', 'savan']),
('LA_VIENTIANE_PROV', 'ແຂວງວຽງຈັນ', ARRAY['ແຂວງວຽງຈັນ', 'vientiane province', 'vientiane prov', 'viangchan province']),
('LA_BOKEO', 'ບໍ່ແກ້ວ', ARRAY['ບໍ່ແກ້ວ', 'bokeo', 'bokèo', 'bo kaeo']),
('LA_KHAMMOUANE', 'ຄຳມ່ວນ', ARRAY['ຄຳມ່ວນ', 'khammouane', 'khammouan', 'khammuan']);

DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'lo'
  AND province_id IN (SELECT id FROM ree_common.provinces WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'LA'));

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT p.id, 'lo', t.translated_text, t.aliases
FROM lao_trans_temp t
JOIN ree_common.provinces p ON p.code = t.code
WHERE p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'LA');

\echo 'Laos: Added ' || (SELECT COUNT(*) FROM ree_common.provinces_translation WHERE lang_code = 'lo') || ' translations'

-- ================================================================
-- INDONESIA - Bahasa Indonesia Translations
-- ================================================================
\echo 'Processing Indonesia (Bahasa Indonesia)...'

CREATE TEMP TABLE indonesian_trans_temp (
    code VARCHAR(50),
    translated_text VARCHAR(255),
    aliases TEXT[]
);

INSERT INTO indonesian_trans_temp (code, translated_text, aliases) VALUES
('ID_JAKARTA', 'DKI Jakarta', ARRAY['dki jakarta', 'jakarta', 'dki', 'jakarta raya', 'ibukota', 'capital', 'jkt']),
('ID_BALI', 'Bali', ARRAY['bali', 'denpasar', 'bali island', 'pulau bali', 'bali province']),
('ID_YOGYAKARTA', 'DI Yogyakarta', ARRAY['di yogyakarta', 'yogyakarta', 'yogya', 'jogja', 'jogjakarta', 'diy', 'yk']),
('ID_WEST_JAVA', 'Jawa Barat', ARRAY['jawa barat', 'jabar', 'west java', 'bandung', 'bogor']),
('ID_CENTRAL_JAVA', 'Jawa Tengah', ARRAY['jawa tengah', 'jateng', 'central java', 'semarang', 'solo']),
('ID_EAST_JAVA', 'Jawa Timur', ARRAY['jawa timur', 'jatim', 'east java', 'surabaya', 'malang']),
('ID_BANTEN', 'Banten', ARRAY['banten', 'serang', 'tangerang', 'banten province']),
('ID_NORTH_SUMATRA', 'Sumatera Utara', ARRAY['sumatera utara', 'sumut', 'north sumatra', 'medan']),
('ID_WEST_SUMATRA', 'Sumatera Barat', ARRAY['sumatera barat', 'sumbar', 'west sumatra', 'padang']),
('ID_SOUTH_SUMATRA', 'Sumatera Selatan', ARRAY['sumatera selatan', 'sumsel', 'south sumatra', 'palembang']);

DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'id'
  AND province_id IN (SELECT id FROM ree_common.provinces WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'ID'));

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT p.id, 'id', t.translated_text, t.aliases
FROM indonesian_trans_temp t
JOIN ree_common.provinces p ON p.code = t.code
WHERE p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'ID');

\echo 'Indonesia: Added ' || (SELECT COUNT(*) FROM ree_common.provinces_translation WHERE lang_code = 'id') || ' translations'

-- ================================================================
-- MYANMAR - Burmese Translations
-- ================================================================
\echo 'Processing Myanmar (Burmese)...'

CREATE TEMP TABLE burmese_trans_temp (
    code VARCHAR(50),
    translated_text VARCHAR(255),
    aliases TEXT[]
);

INSERT INTO burmese_trans_temp (code, translated_text, aliases) VALUES
('MM_YANGON', 'ရန်ကုန်တိုင်း', ARRAY['ရန်ကုန်တိုင်း', 'ရန်ကုန်', 'yangon', 'rangoon', 'yangon region', 'ygn', 'yangon city']),
('MM_MANDALAY', 'မန္တလေးတိုင်း', ARRAY['မန္တလေးတိုင်း', 'မန္တလေး', 'mandalay', 'mandalay region', 'mdy', 'mandalay city']),
('MM_NAYPYIDAW', 'နေပြည်တော်', ARRAY['နေပြည်တော်', 'naypyidaw', 'naypyitaw', 'nay pyi taw', 'capital', 'npt']),
('MM_SHAN', 'ရှမ်းပြည်နယ်', ARRAY['ရှမ်းပြည်နယ်', 'shan', 'shan state', 'taunggyi', 'inle lake']),
('MM_KACHIN', 'ကချင်ပြည်နယ်', ARRAY['ကချင်ပြည်နယ်', 'kachin', 'kachin state', 'myitkyina']),
('MM_RAKHINE', 'ရခိုင်ပြည်နယ်', ARRAY['ရခိုင်ပြည်နယ်', 'rakhine', 'arakan', 'rakhine state', 'sittwe']),
('MM_KAYIN', 'ကရင်ပြည်နယ်', ARRAY['ကရင်ပြည်နယ်', 'kayin', 'karen', 'kayin state', 'hpa-an']),
('MM_KAYAH', 'ကယားပြည်နယ်', ARRAY['ကယားပြည်နယ်', 'kayah', 'karenni', 'kayah state', 'loikaw']),
('MM_MON', 'မွန်ပြည်နယ်', ARRAY['မွန်ပြည်နယ်', 'mon', 'mon state', 'mawlamyine', 'moulmein']);

DELETE FROM ree_common.provinces_translation
WHERE lang_code = 'my'
  AND province_id IN (SELECT id FROM ree_common.provinces WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'MM'));

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT p.id, 'my', t.translated_text, t.aliases
FROM burmese_trans_temp t
JOIN ree_common.provinces p ON p.code = t.code
WHERE p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'MM');

\echo 'Myanmar: Added ' || (SELECT COUNT(*) FROM ree_common.provinces_translation WHERE lang_code = 'my') || ' translations'

COMMIT;

-- ================================================================
-- SUMMARY REPORT
-- ================================================================

\echo ''
\echo '================================================================'
\echo 'DEPLOYMENT COMPLETE - SUMMARY'
\echo '================================================================'

SELECT
    c.name as country,
    c.code,
    COUNT(DISTINCT p.id) as total_provinces,
    COUNT(DISTINCT t.province_id) as provinces_with_translation,
    COALESCE(STRING_AGG(DISTINCT t.lang_code, ', ' ORDER BY t.lang_code), 'none') as languages
FROM ree_common.countries c
LEFT JOIN ree_common.provinces p ON c.id = p.country_id
LEFT JOIN ree_common.provinces_translation t ON p.id = t.province_id AND t.lang_code IN ('th', 'km', 'lo', 'id', 'tl', 'my')
WHERE c.code IN ('TH', 'KH', 'LA', 'ID', 'PH', 'MM')
GROUP BY c.id, c.name, c.code
ORDER BY total_provinces DESC;

\echo ''
\echo 'Translations deployed successfully!'

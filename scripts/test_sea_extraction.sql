-- ================================================================
-- TEST SEA MULTI-LANGUAGE EXTRACTION
-- ================================================================
-- PURPOSE: Test location extraction with SEA local languages
-- DATE: 2025-11-14
-- COVERAGE: Thai, Khmer, Lao, Bahasa Indonesia, Filipino, Burmese
-- ================================================================

\timing on

\echo '================================================================'
\echo 'SEA MULTI-LANGUAGE LOCATION EXTRACTION TEST SUITE'
\echo '================================================================'
\echo ''

-- ================================================================
-- TEST 1: Thailand - Thai Language
-- ================================================================
\echo 'TEST 1: Thailand - Bangkok (Thai)'
\echo 'Input: "ขายคอนโด 2 ห้องนอน กรุงเทพ ใกล้ BTS"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_local,
    t.lang_code
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'th'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('ขายคอนโด 2 ห้องนอน กรุงเทพ ใกล้ BTS') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: TH_BANGKOK'
\echo ''

-- ================================================================
-- TEST 2: Thailand - Phuket (Thai)
-- ================================================================
\echo 'TEST 2: Thailand - Phuket (Thai)'
\echo 'Input: "รีสอร์ท 5 ดาว ภูเก็ต วิวทะเล"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_local
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'th'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('รีสอร์ท 5 ดาว ภูเก็ต วิวทะเล') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: TH_PHUKET'
\echo ''

-- ================================================================
-- TEST 3: Cambodia - Phnom Penh (Khmer)
-- ================================================================
\echo 'TEST 3: Cambodia - Phnom Penh (Khmer)'
\echo 'Input: "ផ្ទះលក់ ភ្នំពេញ ទីតាំងល្អ"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_local
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'km'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('ផ្ទះលក់ ភ្នំពេញ ទីតាំងល្អ') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: KH_PHNOM_PENH'
\echo ''

-- ================================================================
-- TEST 4: Cambodia - Siem Reap (English + Khmer)
-- ================================================================
\echo 'TEST 4: Cambodia - Siem Reap (English)'
\echo 'Input: "Hotel near Angkor Wat, Siem Reap"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_local
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'km'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Hotel near Angkor Wat, Siem Reap') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: KH_SIEM_REAP'
\echo ''

-- ================================================================
-- TEST 5: Laos - Vientiane (Lao)
-- ================================================================
\echo 'TEST 5: Laos - Vientiane (Lao)'
\echo 'Input: "ເຮືອນໃຫມ່ ວຽງຈັນ"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_local
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'lo'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('ເຮືອນໃຫມ່ ວຽງຈັນ') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: LA_VIENTIANE'
\echo ''

-- ================================================================
-- TEST 6: Indonesia - Jakarta (Bahasa)
-- ================================================================
\echo 'TEST 6: Indonesia - Jakarta (Bahasa Indonesia)'
\echo 'Input: "Dijual apartemen mewah Jakarta Selatan"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_local
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'id'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Dijual apartemen mewah Jakarta Selatan') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: ID_JAKARTA'
\echo ''

-- ================================================================
-- TEST 7: Indonesia - Bali (Bahasa)
-- ================================================================
\echo 'TEST 7: Indonesia - Bali (Bahasa Indonesia)'
\echo 'Input: "Villa dengan kolam renang di Bali"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_local
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'id'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Villa dengan kolam renang di Bali') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: ID_BALI'
\echo ''

-- ================================================================
-- TEST 8: Philippines - Metro Manila (Filipino)
-- ================================================================
\echo 'TEST 8: Philippines - Metro Manila (Filipino)'
\echo 'Input: "Condo for sale in Metro Manila"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_local
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'tl'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Condo for sale in Metro Manila') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: PH_NCR'
\echo ''

-- ================================================================
-- TEST 9: Myanmar - Yangon (Burmese)
-- ================================================================
\echo 'TEST 9: Myanmar - Yangon (Burmese)'
\echo 'Input: "ရန်ကုန်မြို့တွင် အိမ်ရောင်းမည်"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_local
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'my'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('ရန်ကုန်မြို့တွင် အိမ်ရောင်းမည်') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: MM_YANGON'
\echo ''

-- ================================================================
-- TEST 10: Multi-Country Search
-- ================================================================
\echo 'TEST 10: Multi-Country Search'
\echo 'Input: "Looking for property in Bangkok, Manila, or Jakarta"'

SELECT
    c.name as country,
    p.code,
    p.name as province_en,
    t.translated_text as province_local,
    t.lang_code
FROM ree_common.provinces p
JOIN ree_common.countries c ON p.country_id = c.id
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code IN ('th', 'tl', 'id')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Looking for property in Bangkok, Manila, or Jakarta') LIKE '%' || LOWER(alias) || '%'
  )
ORDER BY c.name, p.name;

\echo 'Expected: TH_BANGKOK, PH_NCR, ID_JAKARTA'
\echo ''

-- ================================================================
-- COVERAGE SUMMARY
-- ================================================================
\echo '================================================================'
\echo 'COVERAGE SUMMARY'
\echo '================================================================'

-- Total SEA translations by language
SELECT
    t.lang_code as language,
    CASE t.lang_code
        WHEN 'th' THEN 'Thai'
        WHEN 'km' THEN 'Khmer'
        WHEN 'lo' THEN 'Lao'
        WHEN 'id' THEN 'Bahasa Indonesia'
        WHEN 'tl' THEN 'Filipino/Tagalog'
        WHEN 'my' THEN 'Burmese'
        WHEN 'vi' THEN 'Vietnamese'
    END as language_name,
    COUNT(DISTINCT t.province_id) as provinces_covered,
    ROUND(AVG(array_length(t.aliases, 1))::numeric, 1) as avg_aliases
FROM ree_common.provinces_translation t
JOIN ree_common.provinces p ON t.province_id = p.id
JOIN ree_common.countries c ON p.country_id = c.id
WHERE c.code IN ('TH', 'KH', 'LA', 'ID', 'PH', 'MM', 'VN', 'SG', 'MY')
  AND t.lang_code IN ('th', 'km', 'lo', 'id', 'tl', 'my', 'vi')
GROUP BY t.lang_code
ORDER BY provinces_covered DESC;

\echo ''
\echo '================================================================'
\echo 'ALL TESTS COMPLETED'
\echo '================================================================'

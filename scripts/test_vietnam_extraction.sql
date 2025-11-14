-- ================================================================
-- TEST VIETNAM LOCATION EXTRACTION
-- ================================================================
-- PURPOSE: Test extraction accuracy with full 63 Vietnam provinces
-- METHOD: Fuzzy matching with aliases
-- ================================================================

\timing on

\echo '================================================================'
\echo 'VIETNAM LOCATION EXTRACTION TEST SUITE'
\echo '================================================================'
\echo ''

-- ================================================================
-- TEST 1: Hanoi - Capital
-- ================================================================
\echo 'TEST 1: Hanoi - Capital'
\echo 'Input: "Bán nhà 5 tầng mặt phố Hoàng Quốc Việt, Hà Nội, giá 15 tỷ"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi,
    t.aliases
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Bán nhà 5 tầng mặt phố Hoàng Quốc Việt, Hà Nội, giá 15 tỷ') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: VN_HANOI'
\echo ''

-- ================================================================
-- TEST 2: HCMC - Multiple aliases
-- ================================================================
\echo 'TEST 2: HCMC - All aliases test'
\echo 'Input: "Bán căn hộ Quận 7, TP.HCM, view sông Sài Gòn"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Bán căn hộ Quận 7, TP.HCM, view sông Sài Gòn') LIKE '%' || LOWER(alias) || '%'
  );

-- Also extract district
SELECT
    d.code,
    d.name as district_name
FROM ree_common.districts d
WHERE d.code IN ('Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12')
  AND LOWER('Bán căn hộ Quận 7, TP.HCM, view sông Sài Gòn') LIKE '%' || LOWER(REPLACE(d.code, 'Q', 'quận ')) || '%';

\echo 'Expected: VN_HCMC + Q7'
\echo ''

-- ================================================================
-- TEST 3: Quang Ninh - Ha Long
-- ================================================================
\echo 'TEST 3: Quang Ninh - Ha Long Bay'
\echo 'Input: "Bán biệt thự view vịnh Hạ Long, Quảng Ninh"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Bán biệt thự view vịnh Hạ Long, Quảng Ninh') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: VN_QUANG_NINH'
\echo ''

-- ================================================================
-- TEST 4: Da Nang - Central
-- ================================================================
\echo 'TEST 4: Da Nang - Central city'
\echo 'Input: "Bán căn hộ 2PN view biển Đà Nẵng, giá 3.5 tỷ"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Bán căn hộ 2PN view biển Đà Nẵng, giá 3.5 tỷ') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: VN_DANANG'
\echo ''

-- ================================================================
-- TEST 5: Nha Trang - Khanh Hoa
-- ================================================================
\echo 'TEST 5: Nha Trang - Beach city'
\echo 'Input: "Resort cao cấp Nha Trang, Khánh Hòa"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Resort cao cấp Nha Trang, Khánh Hòa') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: VN_KHANH_HOA'
\echo ''

-- ================================================================
-- TEST 6: Da Lat - Highland
-- ================================================================
\echo 'TEST 6: Da Lat - Highland city'
\echo 'Input: "Villa sân vườn Đà Lạt, Lâm Đồng"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Villa sân vườn Đà Lạt, Lâm Đồng') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: VN_LAM_DONG'
\echo ''

-- ================================================================
-- TEST 7: Phu Quoc - Island
-- ================================================================
\echo 'TEST 7: Phu Quoc - Island paradise'
\echo 'Input: "Resort 5 sao Phú Quốc, Kiên Giang"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Resort 5 sao Phú Quốc, Kiên Giang') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: VN_KIEN_GIANG'
\echo ''

-- ================================================================
-- TEST 8: Multiple provinces in one text
-- ================================================================
\echo 'TEST 8: Multiple provinces extraction'
\echo 'Input: "Dự án BĐS tại Hà Nội, Đà Nẵng và TP.HCM"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Dự án BĐS tại Hà Nội, Đà Nẵng và TP.HCM') LIKE '%' || LOWER(alias) || '%'
  )
ORDER BY p.code;

\echo 'Expected: VN_DANANG, VN_HANOI, VN_HCMC'
\echo ''

-- ================================================================
-- TEST 9: Sapa - Lao Cai
-- ================================================================
\echo 'TEST 9: Sapa - Mountain town'
\echo 'Input: "Homestay Sapa, Lào Cai"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi,
    t.aliases
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Homestay Sapa, Lào Cai') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: VN_LAO_CAI'
\echo ''

-- ================================================================
-- TEST 10: Vung Tau - Beach city
-- ================================================================
\echo 'TEST 10: Vung Tau - Beach city'
\echo 'Input: "Condotel Vũng Tàu view biển 180 độ"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'vi'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Condotel Vũng Tàu view biển 180 độ') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: VN_BA_RIA_VUNG_TAU'
\echo ''

-- ================================================================
-- COVERAGE SUMMARY
-- ================================================================
\echo '================================================================'
\echo 'COVERAGE SUMMARY'
\echo '================================================================'

-- Total provinces in database
SELECT
    'Total Vietnam Provinces' as metric,
    COUNT(*) as count
FROM ree_common.provinces
WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN');

-- Provinces with Vietnamese translations
SELECT
    'Provinces with Vietnamese' as metric,
    COUNT(DISTINCT province_id) as count
FROM ree_common.provinces_translation
WHERE lang_code = 'vi'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  );

-- Average aliases per province
SELECT
    'Average aliases per province' as metric,
    ROUND(AVG(array_length(aliases, 1))::numeric, 1) as count
FROM ree_common.provinces_translation
WHERE lang_code = 'vi'
  AND province_id IN (
    SELECT id FROM ree_common.provinces
    WHERE country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
  );

\echo ''
\echo '================================================================'
\echo 'ALL TESTS COMPLETED'
\echo '================================================================'

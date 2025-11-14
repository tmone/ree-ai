-- ================================================================
-- TEST JAPANESE LOCATION EXTRACTION
-- ================================================================
-- PURPOSE: Test location extraction with Japanese language (Kanji, Hiragana, Katakana)
-- DATE: 2025-11-14
-- COVERAGE: 18 Japan prefectures with multiple writing systems
-- ================================================================

\timing on

\echo '================================================================'
\echo 'JAPANESE LOCATION EXTRACTION TEST SUITE'
\echo '================================================================'
\echo ''

-- ================================================================
-- TEST 1: Tokyo - Kanji
-- ================================================================
\echo 'TEST 1: Tokyo - Kanji (漢字)'
\echo 'Input: "東京のマンション販売中"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja,
    t.lang_code
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('東京のマンション販売中') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: JP_TOKYO'
\echo ''

-- ================================================================
-- TEST 2: Tokyo - Hiragana
-- ================================================================
\echo 'TEST 2: Tokyo - Hiragana (ひらがな)'
\echo 'Input: "とうきょうで賃貸アパートを探しています"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('とうきょうで賃貸アパートを探しています') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: JP_TOKYO'
\echo ''

-- ================================================================
-- TEST 3: Tokyo - Romaji
-- ================================================================
\echo 'TEST 3: Tokyo - Romaji (English)'
\echo 'Input: "Apartment for rent in Tokyo"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('Apartment for rent in Tokyo') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: JP_TOKYO'
\echo ''

-- ================================================================
-- TEST 4: Osaka - Kanji
-- ================================================================
\echo 'TEST 4: Osaka - Kanji'
\echo 'Input: "大阪市内の一戸建て"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('大阪市内の一戸建て') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: JP_OSAKA'
\echo ''

-- ================================================================
-- TEST 5: Kyoto - Ancient Capital
-- ================================================================
\echo 'TEST 5: Kyoto - Ancient Capital'
\echo 'Input: "古都京都の伝統的な町家"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('古都京都の伝統的な町家') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: JP_KYOTO'
\echo ''

-- ================================================================
-- TEST 6: Kanagawa - Yokohama City
-- ================================================================
\echo 'TEST 6: Kanagawa via Yokohama'
\echo 'Input: "横浜みなとみらいのタワーマンション"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('横浜みなとみらいのタワーマンション') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: JP_KANAGAWA (via Yokohama alias)'
\echo ''

-- ================================================================
-- TEST 7: Hokkaido - Sapporo
-- ================================================================
\echo 'TEST 7: Hokkaido - Sapporo'
\echo 'Input: "札幌市中心部のマンション"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('札幌市中心部のマンション') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: JP_HOKKAIDO (via Sapporo alias)'
\echo ''

-- ================================================================
-- TEST 8: Aichi - Nagoya
-- ================================================================
\echo 'TEST 8: Aichi via Nagoya'
\echo 'Input: "名古屋駅近くのオフィスビル"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('名古屋駅近くのオフィスビル') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: JP_AICHI (via Nagoya alias)'
\echo ''

-- ================================================================
-- TEST 9: Fukuoka - Hakata
-- ================================================================
\echo 'TEST 9: Fukuoka via Hakata'
\echo 'Input: "博多駅前のビジネスホテル"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('博多駅前のビジネスホテル') LIKE '%' || LOWER(alias) || '%'
  );

\echo 'Expected: JP_FUKUOKA (via Hakata alias)'
\echo ''

-- ================================================================
-- TEST 10: Multi-City Search
-- ================================================================
\echo 'TEST 10: Multi-City Search'
\echo 'Input: "東京、大阪、名古屋で物件探し"'

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja,
    'Found' as status
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND EXISTS (
    SELECT 1 FROM unnest(t.aliases) alias
    WHERE LOWER('東京、大阪、名古屋で物件探し') LIKE '%' || LOWER(alias) || '%'
  )
ORDER BY p.code;

\echo 'Expected: JP_TOKYO, JP_OSAKA, JP_AICHI'
\echo ''

-- ================================================================
-- COVERAGE SUMMARY
-- ================================================================
\echo '================================================================'
\echo 'COVERAGE SUMMARY'
\echo '================================================================'

-- Japanese translation stats
SELECT
    'Japanese translations' as metric,
    COUNT(DISTINCT t.province_id) as prefectures_covered,
    ROUND(AVG(array_length(t.aliases, 1))::numeric, 1) as avg_aliases
FROM ree_common.provinces_translation t
JOIN ree_common.provinces p ON t.province_id = p.id
JOIN ree_common.countries c ON p.country_id = c.id
WHERE c.code = 'JP' AND t.lang_code = 'ja';

-- Show all prefectures
SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_ja,
    array_length(t.aliases, 1) as alias_count
FROM ree_common.provinces p
JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE t.lang_code = 'ja'
  AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'JP')
ORDER BY p.sort_order;

\echo ''
\echo '================================================================'
\echo 'Writing Systems Supported:'
\echo '  - Kanji (漢字): 東京, 大阪, 京都'
\echo '  - Hiragana (ひらがな): とうきょう, おおさか'
\echo '  - Katakana (カタカナ): トウキョウ, オオサカ'
\echo '  - Romaji: tokyo, osaka, kyoto'
\echo '================================================================'
\echo 'ALL TESTS COMPLETED'
\echo '================================================================'

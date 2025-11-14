-- ================================================================
-- SEED ALL SEA/ASEAN COUNTRY TRANSLATIONS - MASTER FILE
-- ================================================================
-- PURPOSE: Deploy all translations for SEA countries in one transaction
-- DATE: 2025-11-14
-- COVERAGE: 6 languages across 6 SEA countries (137 provinces total)
-- ================================================================
--
-- LANGUAGES COVERED:
-- - Thai (th): 46 Thailand provinces
-- - Khmer (km): 25 Cambodia provinces
-- - Lao (lo): 18 Laos provinces
-- - Bahasa Indonesia (id): 17 Indonesia provinces
-- - Filipino/Tagalog (tl): 17 Philippines regions
-- - Burmese (my): 14 Myanmar regions/states
--
-- TOTAL: 137 provinces with local language support
-- ================================================================

\echo '================================================================'
\echo 'DEPLOYING ALL SEA TRANSLATIONS'
\echo '================================================================'
\echo ''

-- Import all translation files
\echo 'Step 1/6: Adding Thai translations (46 provinces)...'
\i seed_thai_translations.sql
\echo ''

\echo 'Step 2/6: Adding Khmer translations (25 provinces)...'
\i seed_khmer_translations.sql
\echo ''

\echo 'Step 3/6: Adding Lao translations (18 provinces)...'
\i seed_lao_translations.sql
\echo ''

\echo 'Step 4/6: Adding Bahasa Indonesia translations (17 provinces)...'
\i seed_indonesian_translations.sql
\echo ''

\echo 'Step 5/6: Adding Filipino translations (17 regions)...'
\i seed_filipino_translations.sql
\echo ''

\echo 'Step 6/6: Adding Burmese translations (14 regions)...'
\i seed_burmese_translations.sql
\echo ''

-- ================================================================
-- SUMMARY REPORT
-- ================================================================

\echo '================================================================'
\echo 'DEPLOYMENT SUMMARY'
\echo '================================================================'
\echo ''

-- Count all SEA translations by language
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
    c.name as country,
    COUNT(*) as provinces
FROM ree_common.provinces_translation t
JOIN ree_common.provinces p ON t.province_id = p.id
JOIN ree_common.countries c ON p.country_id = c.id
WHERE c.code IN ('TH', 'KH', 'LA', 'ID', 'PH', 'MM', 'VN')
  AND t.lang_code IN ('th', 'km', 'lo', 'id', 'tl', 'my', 'vi')
GROUP BY t.lang_code, language_name, c.name, c.code
ORDER BY c.code, t.lang_code;

\echo ''
\echo '================================================================'

-- Total translations by country
SELECT
    c.name as country,
    c.code,
    COUNT(DISTINCT p.id) as total_provinces,
    COUNT(DISTINCT t.lang_code) as languages_supported,
    STRING_AGG(DISTINCT t.lang_code, ', ' ORDER BY t.lang_code) as language_codes
FROM ree_common.countries c
LEFT JOIN ree_common.provinces p ON c.id = p.country_id
LEFT JOIN ree_common.provinces_translation t ON p.id = t.province_id
WHERE c.code IN ('TH', 'KH', 'LA', 'ID', 'PH', 'MM', 'VN', 'SG', 'MY')
GROUP BY c.id, c.name, c.code
ORDER BY total_provinces DESC;

\echo ''
\echo '================================================================'
\echo 'ALL SEA TRANSLATIONS DEPLOYED SUCCESSFULLY!'
\echo '================================================================'
\echo ''

-- Average aliases per province
SELECT
    'Total provinces with translations' as metric,
    COUNT(DISTINCT province_id) as count
FROM ree_common.provinces_translation
WHERE province_id IN (
    SELECT p.id FROM ree_common.provinces p
    JOIN ree_common.countries c ON p.country_id = c.id
    WHERE c.code IN ('TH', 'KH', 'LA', 'ID', 'PH', 'MM', 'VN', 'SG', 'MY')
);

SELECT
    'Average aliases per province' as metric,
    ROUND(AVG(array_length(aliases, 1))::numeric, 1) as count
FROM ree_common.provinces_translation
WHERE province_id IN (
    SELECT p.id FROM ree_common.provinces p
    JOIN ree_common.countries c ON p.country_id = c.id
    WHERE c.code IN ('TH', 'KH', 'LA', 'ID', 'PH', 'MM', 'VN', 'SG', 'MY')
);

\echo ''
\echo 'Ready for multi-language property extraction across Southeast Asia!'
\echo ''

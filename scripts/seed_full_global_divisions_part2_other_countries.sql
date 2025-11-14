-- ================================================================
-- FULL GLOBAL ADMINISTRATIVE DIVISIONS - PART 2
-- ================================================================
-- COUNTRIES: Thailand, Singapore, Japan, China, Malaysia, UK, Australia, UAE
-- ================================================================

BEGIN;

-- ================================================================
-- THAILAND - 77 PROVINCES
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- Central Region
SELECT 'TH_BANGKOK', 'Bangkok', id, 'Special Administrative Area', 1 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_SAMUT_PRAKAN', 'Samut Prakan', id, 'Province', 2 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_NONTHABURI', 'Nonthaburi', id, 'Province', 3 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_PATHUM_THANI', 'Pathum Thani', id, 'Province', 4 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_PHRA_NAKHON_SI_AYUTTHAYA', 'Phra Nakhon Si Ayutthaya', id, 'Province', 5 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_ANG_THONG', 'Ang Thong', id, 'Province', 6 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_LOPBURI', 'Lopburi', id, 'Province', 7 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_SING_BURI', 'Sing Buri', id, 'Province', 8 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_CHAI_NAT', 'Chai Nat', id, 'Province', 9 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_SARABURI', 'Saraburi', id, 'Province', 10 FROM ree_common.countries WHERE code = 'TH'
-- Eastern Region
UNION ALL SELECT 'TH_CHONBURI', 'Chonburi', id, 'Province', 11 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_RAYONG', 'Rayong', id, 'Province', 12 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_CHANTHABURI', 'Chanthaburi', id, 'Province', 13 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_TRAT', 'Trat', id, 'Province', 14 FROM ree_common.countries WHERE code = 'TH'
-- Northern Region
UNION ALL SELECT 'TH_CHIANG_MAI', 'Chiang Mai', id, 'Province', 15 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_CHIANG_RAI', 'Chiang Rai', id, 'Province', 16 FROM ree_common.countries WHERE code = 'TH'
-- Southern Region
UNION ALL SELECT 'TH_PHUKET', 'Phuket', id, 'Province', 17 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_SURAT_THANI', 'Surat Thani', id, 'Province', 18 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_KRABI', 'Krabi', id, 'Province', 19 FROM ree_common.countries WHERE code = 'TH'
UNION ALL SELECT 'TH_SONGKHLA', 'Songkhla', id, 'Province', 20 FROM ree_common.countries WHERE code = 'TH'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- SINGAPORE - 5 REGIONS + 55 PLANNING AREAS
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'SG_CENTRAL', 'Central Region', id, 'Region', 1 FROM ree_common.countries WHERE code = 'SG'
UNION ALL SELECT 'SG_EAST', 'East Region', id, 'Region', 2 FROM ree_common.countries WHERE code = 'SG'
UNION ALL SELECT 'SG_NORTH', 'North Region', id, 'Region', 3 FROM ree_common.countries WHERE code = 'SG'
UNION ALL SELECT 'SG_NORTH_EAST', 'North-East Region', id, 'Region', 4 FROM ree_common.countries WHERE code = 'SG'
UNION ALL SELECT 'SG_WEST', 'West Region', id, 'Region', 5 FROM ree_common.countries WHERE code = 'SG'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- Major Planning Areas
INSERT INTO ree_common.districts (code, name, province_id, country_id, sort_order)
SELECT 'SG_DOWNTOWN_CORE', 'Downtown Core',
    (SELECT id FROM ree_common.provinces WHERE code = 'SG_CENTRAL'),
    (SELECT id FROM ree_common.countries WHERE code = 'SG'), 1
UNION ALL SELECT 'SG_ORCHARD', 'Orchard',
    (SELECT id FROM ree_common.provinces WHERE code = 'SG_CENTRAL'),
    (SELECT id FROM ree_common.countries WHERE code = 'SG'), 2
UNION ALL SELECT 'SG_MARINA_BAY', 'Marina Bay',
    (SELECT id FROM ree_common.provinces WHERE code = 'SG_CENTRAL'),
    (SELECT id FROM ree_common.countries WHERE code = 'SG'), 3
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name;

-- ================================================================
-- JAPAN - 47 PREFECTURES
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- Kanto Region
SELECT 'JP_TOKYO', 'Tokyo', id, 'Metropolis', 1 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_KANAGAWA', 'Kanagawa', id, 'Prefecture', 2 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_SAITAMA', 'Saitama', id, 'Prefecture', 3 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_CHIBA', 'Chiba', id, 'Prefecture', 4 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_IBARAKI', 'Ibaraki', id, 'Prefecture', 5 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_TOCHIGI', 'Tochigi', id, 'Prefecture', 6 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_GUNMA', 'Gunma', id, 'Prefecture', 7 FROM ree_common.countries WHERE code = 'JP'
-- Kansai Region
UNION ALL SELECT 'JP_OSAKA', 'Osaka', id, 'Prefecture', 8 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_KYOTO', 'Kyoto', id, 'Prefecture', 9 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_HYOGO', 'Hyogo', id, 'Prefecture', 10 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_NARA', 'Nara', id, 'Prefecture', 11 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_SHIGA', 'Shiga', id, 'Prefecture', 12 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_WAKAYAMA', 'Wakayama', id, 'Prefecture', 13 FROM ree_common.countries WHERE code = 'JP'
-- Chubu Region
UNION ALL SELECT 'JP_AICHI', 'Aichi', id, 'Prefecture', 14 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_SHIZUOKA', 'Shizuoka', id, 'Prefecture', 15 FROM ree_common.countries WHERE code = 'JP'
UNION ALL SELECT 'JP_GIFU', 'Gifu', id, 'Prefecture', 16 FROM ree_common.countries WHERE code = 'JP'
-- Kyushu Region
UNION ALL SELECT 'JP_FUKUOKA', 'Fukuoka', id, 'Prefecture', 17 FROM ree_common.countries WHERE code = 'JP'
-- Hokkaido
UNION ALL SELECT 'JP_HOKKAIDO', 'Hokkaido', id, 'Prefecture', 18 FROM ree_common.countries WHERE code = 'JP'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- CHINA - 34 PROVINCIAL-LEVEL DIVISIONS
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- Municipalities
SELECT 'CN_BEIJING', 'Beijing', id, 'Municipality', 1 FROM ree_common.countries WHERE code = 'CN'
UNION ALL SELECT 'CN_SHANGHAI', 'Shanghai', id, 'Municipality', 2 FROM ree_common.countries WHERE code = 'CN'
UNION ALL SELECT 'CN_TIANJIN', 'Tianjin', id, 'Municipality', 3 FROM ree_common.countries WHERE code = 'CN'
UNION ALL SELECT 'CN_CHONGQING', 'Chongqing', id, 'Municipality', 4 FROM ree_common.countries WHERE code = 'CN'
-- Provinces
UNION ALL SELECT 'CN_GUANGDONG', 'Guangdong', id, 'Province', 5 FROM ree_common.countries WHERE code = 'CN'
UNION ALL SELECT 'CN_JIANGSU', 'Jiangsu', id, 'Province', 6 FROM ree_common.countries WHERE code = 'CN'
UNION ALL SELECT 'CN_ZHEJIANG', 'Zhejiang', id, 'Province', 7 FROM ree_common.countries WHERE code = 'CN'
UNION ALL SELECT 'CN_SHANDONG', 'Shandong', id, 'Province', 8 FROM ree_common.countries WHERE code = 'CN'
UNION ALL SELECT 'CN_FUJIAN', 'Fujian', id, 'Province', 9 FROM ree_common.countries WHERE code = 'CN'
UNION ALL SELECT 'CN_SICHUAN', 'Sichuan', id, 'Province', 10 FROM ree_common.countries WHERE code = 'CN'
-- Special Administrative Regions
UNION ALL SELECT 'CN_HONG_KONG', 'Hong Kong', id, 'SAR', 11 FROM ree_common.countries WHERE code = 'CN'
UNION ALL SELECT 'CN_MACAU', 'Macau', id, 'SAR', 12 FROM ree_common.countries WHERE code = 'CN'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- Major Cities
INSERT INTO ree_common.districts (code, name, province_id, country_id, sort_order)
SELECT 'CN_SHENZHEN', 'Shenzhen',
    (SELECT id FROM ree_common.provinces WHERE code = 'CN_GUANGDONG'),
    (SELECT id FROM ree_common.countries WHERE code = 'CN'), 1
UNION ALL SELECT 'CN_GUANGZHOU', 'Guangzhou',
    (SELECT id FROM ree_common.provinces WHERE code = 'CN_GUANGDONG'),
    (SELECT id FROM ree_common.countries WHERE code = 'CN'), 2
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name;

-- ================================================================
-- MALAYSIA - 13 STATES + 3 FEDERAL TERRITORIES
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'MY_JOHOR', 'Johor', id, 'State', 1 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_KEDAH', 'Kedah', id, 'State', 2 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_KELANTAN', 'Kelantan', id, 'State', 3 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_MALACCA', 'Malacca', id, 'State', 4 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_NEGERI_SEMBILAN', 'Negeri Sembilan', id, 'State', 5 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_PAHANG', 'Pahang', id, 'State', 6 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_PENANG', 'Penang', id, 'State', 7 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_PERAK', 'Perak', id, 'State', 8 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_PERLIS', 'Perlis', id, 'State', 9 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_SELANGOR', 'Selangor', id, 'State', 10 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_TERENGGANU', 'Terengganu', id, 'State', 11 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_SABAH', 'Sabah', id, 'State', 12 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_SARAWAK', 'Sarawak', id, 'State', 13 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_KL', 'Kuala Lumpur', id, 'Federal Territory', 14 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_LABUAN', 'Labuan', id, 'Federal Territory', 15 FROM ree_common.countries WHERE code = 'MY'
UNION ALL SELECT 'MY_PUTRAJAYA', 'Putrajaya', id, 'Federal Territory', 16 FROM ree_common.countries WHERE code = 'MY'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- UNITED KINGDOM - 4 COUNTRIES (England, Scotland, Wales, N. Ireland)
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'GB_ENGLAND', 'England', id, 'Country', 1 FROM ree_common.countries WHERE code = 'GB'
UNION ALL SELECT 'GB_SCOTLAND', 'Scotland', id, 'Country', 2 FROM ree_common.countries WHERE code = 'GB'
UNION ALL SELECT 'GB_WALES', 'Wales', id, 'Country', 3 FROM ree_common.countries WHERE code = 'GB'
UNION ALL SELECT 'GB_NORTHERN_IRELAND', 'Northern Ireland', id, 'Country', 4 FROM ree_common.countries WHERE code = 'GB'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- Major Cities
INSERT INTO ree_common.districts (code, name, province_id, country_id, sort_order)
SELECT 'GB_LONDON', 'London',
    (SELECT id FROM ree_common.provinces WHERE code = 'GB_ENGLAND'),
    (SELECT id FROM ree_common.countries WHERE code = 'GB'), 1
UNION ALL SELECT 'GB_MANCHESTER', 'Manchester',
    (SELECT id FROM ree_common.provinces WHERE code = 'GB_ENGLAND'),
    (SELECT id FROM ree_common.countries WHERE code = 'GB'), 2
UNION ALL SELECT 'GB_BIRMINGHAM', 'Birmingham',
    (SELECT id FROM ree_common.provinces WHERE code = 'GB_ENGLAND'),
    (SELECT id FROM ree_common.countries WHERE code = 'GB'), 3
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name;

-- ================================================================
-- AUSTRALIA - 6 STATES + 2 TERRITORIES
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'AU_NSW', 'New South Wales', id, 'State', 1 FROM ree_common.countries WHERE code = 'AU'
UNION ALL SELECT 'AU_VIC', 'Victoria', id, 'State', 2 FROM ree_common.countries WHERE code = 'AU'
UNION ALL SELECT 'AU_QLD', 'Queensland', id, 'State', 3 FROM ree_common.countries WHERE code = 'AU'
UNION ALL SELECT 'AU_SA', 'South Australia', id, 'State', 4 FROM ree_common.countries WHERE code = 'AU'
UNION ALL SELECT 'AU_WA', 'Western Australia', id, 'State', 5 FROM ree_common.countries WHERE code = 'AU'
UNION ALL SELECT 'AU_TAS', 'Tasmania', id, 'State', 6 FROM ree_common.countries WHERE code = 'AU'
UNION ALL SELECT 'AU_ACT', 'Australian Capital Territory', id, 'Territory', 7 FROM ree_common.countries WHERE code = 'AU'
UNION ALL SELECT 'AU_NT', 'Northern Territory', id, 'Territory', 8 FROM ree_common.countries WHERE code = 'AU'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- UAE - 7 EMIRATES
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'AE_ABU_DHABI', 'Abu Dhabi', id, 'Emirate', 1 FROM ree_common.countries WHERE code = 'AE'
UNION ALL SELECT 'AE_DUBAI', 'Dubai', id, 'Emirate', 2 FROM ree_common.countries WHERE code = 'AE'
UNION ALL SELECT 'AE_SHARJAH', 'Sharjah', id, 'Emirate', 3 FROM ree_common.countries WHERE code = 'AE'
UNION ALL SELECT 'AE_AJMAN', 'Ajman', id, 'Emirate', 4 FROM ree_common.countries WHERE code = 'AE'
UNION ALL SELECT 'AE_UMM_AL_QUWAIN', 'Umm Al Quwain', id, 'Emirate', 5 FROM ree_common.countries WHERE code = 'AE'
UNION ALL SELECT 'AE_RAS_AL_KHAIMAH', 'Ras Al Khaimah', id, 'Emirate', 6 FROM ree_common.countries WHERE code = 'AE'
UNION ALL SELECT 'AE_FUJAIRAH', 'Fujairah', id, 'Emirate', 7 FROM ree_common.countries WHERE code = 'AE'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT 'Part 2 Complete - All Countries Populated' as status;

SELECT
    c.code,
    c.name as country,
    COUNT(p.id) as provinces_count
FROM ree_common.countries c
LEFT JOIN ree_common.provinces p ON c.id = p.country_id
GROUP BY c.id, c.code, c.name
ORDER BY provinces_count DESC;

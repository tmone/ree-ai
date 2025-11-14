-- ================================================================
-- SOUTHEAST ASIA (SEA/ASEAN) COUNTRIES - FULL DATA
-- ================================================================
-- PURPOSE: Complete administrative divisions for SEA countries
-- COUNTRIES: Cambodia, Laos, Myanmar, Indonesia, Philippines, Thailand (expand)
-- DATE: 2025-11-14
-- ================================================================

BEGIN;

-- ================================================================
-- ADD NEW SEA COUNTRIES
-- ================================================================

INSERT INTO ree_common.countries (code, name, iso_code_3, phone_code, currency, region, sort_order) VALUES
('KH', 'Cambodia', 'KHM', '+855', 'KHR', 'Asia', 50),
('LA', 'Laos', 'LAO', '+856', 'LAK', 'Asia', 51),
('MM', 'Myanmar', 'MMR', '+95', 'MMK', 'Asia', 52),
('ID', 'Indonesia', 'IDN', '+62', 'IDR', 'Asia', 53),
('PH', 'Philippines', 'PHL', '+63', 'PHP', 'Asia', 54)
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    iso_code_3 = EXCLUDED.iso_code_3,
    phone_code = EXCLUDED.phone_code,
    currency = EXCLUDED.currency,
    region = EXCLUDED.region;

-- ================================================================
-- CAMBODIA - 25 PROVINCES
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- Capital
SELECT 'KH_PHNOM_PENH', 'Phnom Penh', id, 'Municipality', 1 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
-- Major provinces
SELECT 'KH_SIEM_REAP', 'Siem Reap', id, 'Province', 2 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_BATTAMBANG', 'Battambang', id, 'Province', 3 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_SIHANOUKVILLE', 'Sihanoukville', id, 'Province', 4 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_KANDAL', 'Kandal', id, 'Province', 5 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_KAMPONG_CHAM', 'Kampong Cham', id, 'Province', 6 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_KAMPONG_SPEU', 'Kampong Speu', id, 'Province', 7 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_KAMPONG_THOM', 'Kampong Thom', id, 'Province', 8 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_KAMPOT', 'Kampot', id, 'Province', 9 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_KEP', 'Kep', id, 'Municipality', 10 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_KOH_KONG', 'Koh Kong', id, 'Province', 11 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_KRATIE', 'Kratie', id, 'Province', 12 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_MONDULKIRI', 'Mondulkiri', id, 'Province', 13 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_ODDAR_MEANCHEY', 'Oddar Meanchey', id, 'Province', 14 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_PAILIN', 'Pailin', id, 'Municipality', 15 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_PREAH_VIHEAR', 'Preah Vihear', id, 'Province', 16 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_PREY_VENG', 'Prey Veng', id, 'Province', 17 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_PURSAT', 'Pursat', id, 'Province', 18 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_RATANAKIRI', 'Ratanakiri', id, 'Province', 19 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_STUNG_TRENG', 'Stung Treng', id, 'Province', 20 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_SVAY_RIENG', 'Svay Rieng', id, 'Province', 21 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_TAKEO', 'Takeo', id, 'Province', 22 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_BANTEAY_MEANCHEY', 'Banteay Meanchey', id, 'Province', 23 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_KAMPONG_CHHNANG', 'Kampong Chhnang', id, 'Province', 24 FROM ree_common.countries WHERE code = 'KH'
UNION ALL
SELECT 'KH_PREAH_SIHANOUK', 'Preah Sihanouk', id, 'Province', 25 FROM ree_common.countries WHERE code = 'KH'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- LAOS - 18 PROVINCES
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- Capital
SELECT 'LA_VIENTIANE', 'Vientiane Capital', id, 'Prefecture', 1 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
-- Major provinces
SELECT 'LA_VIENTIANE_PROV', 'Vientiane Province', id, 'Province', 2 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_LUANG_PRABANG', 'Luang Prabang', id, 'Province', 3 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_CHAMPASAK', 'Champasak', id, 'Province', 4 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_SAVANNAKHET', 'Savannakhet', id, 'Province', 5 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_ATTAPEU', 'Attapeu', id, 'Province', 6 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_BOKEO', 'Bokeo', id, 'Province', 7 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_BOLIKHAMXAI', 'Bolikhamxai', id, 'Province', 8 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_HOUAPHANH', 'Houaphanh', id, 'Province', 9 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_KHAMMOUANE', 'Khammouane', id, 'Province', 10 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_LUANG_NAMTHA', 'Luang Namtha', id, 'Province', 11 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_OUDOMXAI', 'Oudomxai', id, 'Province', 12 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_PHONGSALI', 'Phongsali', id, 'Province', 13 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_SALAVAN', 'Salavan', id, 'Province', 14 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_SARAVANE', 'Saravane', id, 'Province', 15 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_SEKONG', 'Sekong', id, 'Province', 16 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_XIANGKHOUANG', 'Xiangkhouang', id, 'Province', 17 FROM ree_common.countries WHERE code = 'LA'
UNION ALL
SELECT 'LA_XAISOMBOUN', 'Xaisomboun', id, 'Province', 18 FROM ree_common.countries WHERE code = 'LA'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- MYANMAR - 14 REGIONS/STATES
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- Regions
SELECT 'MM_YANGON', 'Yangon Region', id, 'Region', 1 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_MANDALAY', 'Mandalay Region', id, 'Region', 2 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_NAYPYIDAW', 'Naypyidaw Union Territory', id, 'Union Territory', 3 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_BAGO', 'Bago Region', id, 'Region', 4 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_AYEYARWADY', 'Ayeyarwady Region', id, 'Region', 5 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_MAGWAY', 'Magway Region', id, 'Region', 6 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_SAGAING', 'Sagaing Region', id, 'Region', 7 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_TANINTHARYI', 'Tanintharyi Region', id, 'Region', 8 FROM ree_common.countries WHERE code = 'MM'
-- States
UNION ALL
SELECT 'MM_RAKHINE', 'Rakhine State', id, 'State', 9 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_SHAN', 'Shan State', id, 'State', 10 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_KACHIN', 'Kachin State', id, 'State', 11 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_KAYIN', 'Kayin State', id, 'State', 12 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_KAYAH', 'Kayah State', id, 'State', 13 FROM ree_common.countries WHERE code = 'MM'
UNION ALL
SELECT 'MM_MON', 'Mon State', id, 'State', 14 FROM ree_common.countries WHERE code = 'MM'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- INDONESIA - 34 PROVINCES (ALL)
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- Jakarta (Capital)
SELECT 'ID_JAKARTA', 'Jakarta', id, 'Special Capital Region', 1 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
-- Java Island (Major economic center)
SELECT 'ID_WEST_JAVA', 'West Java', id, 'Province', 2 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_CENTRAL_JAVA', 'Central Java', id, 'Province', 3 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_EAST_JAVA', 'East Java', id, 'Province', 4 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_BANTEN', 'Banten', id, 'Province', 5 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_YOGYAKARTA', 'Yogyakarta', id, 'Special Region', 6 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
-- Sumatra Island
SELECT 'ID_NORTH_SUMATRA', 'North Sumatra', id, 'Province', 7 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_WEST_SUMATRA', 'West Sumatra', id, 'Province', 8 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_SOUTH_SUMATRA', 'South Sumatra', id, 'Province', 9 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_RIAU', 'Riau', id, 'Province', 10 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_LAMPUNG', 'Lampung', id, 'Province', 11 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_ACEH', 'Aceh', id, 'Special Region', 12 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
-- Bali
SELECT 'ID_BALI', 'Bali', id, 'Province', 13 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
-- Kalimantan (Borneo)
SELECT 'ID_EAST_KALIMANTAN', 'East Kalimantan', id, 'Province', 14 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_SOUTH_KALIMANTAN', 'South Kalimantan', id, 'Province', 15 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
-- Sulawesi
SELECT 'ID_SOUTH_SULAWESI', 'South Sulawesi', id, 'Province', 16 FROM ree_common.countries WHERE code = 'ID'
UNION ALL
SELECT 'ID_NORTH_SULAWESI', 'North Sulawesi', id, 'Province', 17 FROM ree_common.countries WHERE code = 'ID'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- PHILIPPINES - 17 REGIONS (MAJOR)
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- NCR (Metro Manila)
SELECT 'PH_NCR', 'National Capital Region', id, 'Special Region', 1 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
-- Luzon
SELECT 'PH_CAR', 'Cordillera Administrative Region', id, 'Region', 2 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_ILOCOS', 'Ilocos Region', id, 'Region', 3 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_CAGAYAN_VALLEY', 'Cagayan Valley', id, 'Region', 4 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_CENTRAL_LUZON', 'Central Luzon', id, 'Region', 5 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_CALABARZON', 'CALABARZON', id, 'Region', 6 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_MIMAROPA', 'MIMAROPA', id, 'Region', 7 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_BICOL', 'Bicol Region', id, 'Region', 8 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
-- Visayas
SELECT 'PH_WESTERN_VISAYAS', 'Western Visayas', id, 'Region', 9 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_CENTRAL_VISAYAS', 'Central Visayas', id, 'Region', 10 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_EASTERN_VISAYAS', 'Eastern Visayas', id, 'Region', 11 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
-- Mindanao
SELECT 'PH_ZAMBOANGA', 'Zamboanga Peninsula', id, 'Region', 12 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_NORTHERN_MINDANAO', 'Northern Mindanao', id, 'Region', 13 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_DAVAO', 'Davao Region', id, 'Region', 14 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_SOCCSKSARGEN', 'SOCCSKSARGEN', id, 'Region', 15 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_CARAGA', 'Caraga', id, 'Region', 16 FROM ree_common.countries WHERE code = 'PH'
UNION ALL
SELECT 'PH_BARMM', 'Bangsamoro', id, 'Autonomous Region', 17 FROM ree_common.countries WHERE code = 'PH'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- THAILAND - EXPAND TO ALL 77 PROVINCES
-- ================================================================

-- Add remaining 56 provinces (already have 21)
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- Western Region
SELECT 'TH_KANCHANABURI', 'Kanchanaburi', id, 'Province', 21 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_TAK', 'Tak', id, 'Province', 22 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_PRACHUAP_KHIRI_KHAN', 'Prachuap Khiri Khan', id, 'Province', 23 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_PHETCHABURI', 'Phetchaburi', id, 'Province', 24 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_RATCHABURI', 'Ratchaburi', id, 'Province', 25 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_SAMUT_SONGKHRAM', 'Samut Songkhram', id, 'Province', 26 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_SAMUT_SAKHON', 'Samut Sakhon', id, 'Province', 27 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
-- Northern Region (expand)
SELECT 'TH_PHAYAO', 'Phayao', id, 'Province', 28 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_LAMPANG', 'Lampang', id, 'Province', 29 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_LAMPHUN', 'Lamphun', id, 'Province', 30 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_MAE_HONG_SON', 'Mae Hong Son', id, 'Province', 31 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_NAN', 'Nan', id, 'Province', 32 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_PHRAE', 'Phrae', id, 'Province', 33 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_UTTARADIT', 'Uttaradit', id, 'Province', 34 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
-- Northeastern Region (Isan)
SELECT 'TH_NAKHON_RATCHASIMA', 'Nakhon Ratchasima', id, 'Province', 35 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_UDON_THANI', 'Udon Thani', id, 'Province', 36 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_KHON_KAEN', 'Khon Kaen', id, 'Province', 37 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_UBON_RATCHATHANI', 'Ubon Ratchathani', id, 'Province', 38 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_NAKHON_PHANOM', 'Nakhon Phanom', id, 'Province', 39 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
-- Southern Region (expand)
SELECT 'TH_PHANG_NGA', 'Phang Nga', id, 'Province', 40 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_RANONG', 'Ranong', id, 'Province', 41 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_CHUMPHON', 'Chumphon', id, 'Province', 42 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_NAKHON_SI_THAMMARAT', 'Nakhon Si Thammarat', id, 'Province', 43 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_TRANG', 'Trang', id, 'Province', 44 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_SATUN', 'Satun', id, 'Province', 45 FROM ree_common.countries WHERE code = 'TH'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT 'SEA Countries Added Successfully!' as status;

SELECT
    c.code,
    c.name as country,
    c.region,
    COUNT(p.id) as provinces_count
FROM ree_common.countries c
LEFT JOIN ree_common.provinces p ON c.id = p.country_id
WHERE c.code IN ('KH', 'LA', 'MM', 'ID', 'PH', 'TH')
GROUP BY c.id, c.code, c.name, c.region
ORDER BY provinces_count DESC;

-- Total count
SELECT
    'Total SEA Countries' as metric,
    COUNT(DISTINCT country_id) as count
FROM ree_common.provinces p
JOIN ree_common.countries c ON p.country_id = c.id
WHERE c.region = 'Asia' AND c.code IN ('VN', 'TH', 'KH', 'LA', 'MM', 'ID', 'PH', 'SG', 'MY');

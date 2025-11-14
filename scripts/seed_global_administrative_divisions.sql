-- ================================================================
-- Seed Global Administrative Divisions
-- ================================================================
-- PURPOSE: Populate top 10 real estate markets worldwide
-- MARKETS: USA, Vietnam, Thailand, Singapore, Japan, UK, Australia, UAE, China, Malaysia
-- ================================================================

BEGIN;

-- ================================================================
-- STEP 1: Seed Countries (Top 10 Real Estate Markets)
-- ================================================================

INSERT INTO ree_common.countries (code, name, iso_code_3, phone_code, currency, region, sort_order) VALUES
-- Americas
('US', 'United States', 'USA', '+1', 'USD', 'Americas', 1),

-- Asia
('VN', 'Vietnam', 'VNM', '+84', 'VND', 'Asia', 10),
('TH', 'Thailand', 'THA', '+66', 'THB', 'Asia', 11),
('SG', 'Singapore', 'SGP', '+65', 'SGD', 'Asia', 12),
('JP', 'Japan', 'JPN', '+81', 'JPY', 'Asia', 13),
('CN', 'China', 'CHN', '+86', 'CNY', 'Asia', 14),
('MY', 'Malaysia', 'MYS', '+60', 'MYR', 'Asia', 15),

-- Europe
('GB', 'United Kingdom', 'GBR', '+44', 'GBP', 'Europe', 20),

-- Oceania
('AU', 'Australia', 'AUS', '+61', 'AUD', 'Oceania', 30),

-- Middle East
('AE', 'United Arab Emirates', 'ARE', '+971', 'AED', 'Middle East', 40)
ON CONFLICT (code) DO NOTHING;

-- ================================================================
-- STEP 2: Seed Countries Translations
-- ================================================================

-- English (default)
INSERT INTO ree_common.countries_translation (country_id, lang_code, translated_text, aliases)
SELECT id, 'en', name, ARRAY[LOWER(name), code, iso_code_3]
FROM ree_common.countries;

-- Vietnamese translations
INSERT INTO ree_common.countries_translation (country_id, lang_code, translated_text, aliases) VALUES
((SELECT id FROM ree_common.countries WHERE code = 'US'), 'vi', 'Hoa Kỳ', ARRAY['hoa kỳ', 'mỹ', 'mỹ quốc', 'usa', 'united states']),
((SELECT id FROM ree_common.countries WHERE code = 'VN'), 'vi', 'Việt Nam', ARRAY['việt nam', 'vn', 'vietnam']),
((SELECT id FROM ree_common.countries WHERE code = 'TH'), 'vi', 'Thái Lan', ARRAY['thái lan', 'thailand']),
((SELECT id FROM ree_common.countries WHERE code = 'SG'), 'vi', 'Singapore', ARRAY['singapore', 'tân gia ba']),
((SELECT id FROM ree_common.countries WHERE code = 'JP'), 'vi', 'Nhật Bản', ARRAY['nhật bản', 'nhật', 'japan']),
((SELECT id FROM ree_common.countries WHERE code = 'CN'), 'vi', 'Trung Quốc', ARRAY['trung quốc', 'china']),
((SELECT id FROM ree_common.countries WHERE code = 'MY'), 'vi', 'Malaysia', ARRAY['malaysia', 'mã lai']),
((SELECT id FROM ree_common.countries WHERE code = 'GB'), 'vi', 'Vương Quốc Anh', ARRAY['vương quốc anh', 'anh', 'uk', 'united kingdom']),
((SELECT id FROM ree_common.countries WHERE code = 'AU'), 'vi', 'Úc', ARRAY['úc', 'australia', 'úc châu']),
((SELECT id FROM ree_common.countries WHERE code = 'AE'), 'vi', 'Các Tiểu Vương Quốc Ả Rập Thống Nhất', ARRAY['uae', 'dubai', 'ả rập'])
ON CONFLICT (country_id, lang_code) DO NOTHING;

-- ================================================================
-- STEP 3: Seed Provinces/States (Major Cities)
-- ================================================================

-- USA - Major States
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'US_CA', 'California', id, 'State', 1 FROM ree_common.countries WHERE code = 'US'
UNION ALL
SELECT 'US_NY', 'New York', id, 'State', 2 FROM ree_common.countries WHERE code = 'US'
UNION ALL
SELECT 'US_TX', 'Texas', id, 'State', 3 FROM ree_common.countries WHERE code = 'US'
UNION ALL
SELECT 'US_FL', 'Florida', id, 'State', 4 FROM ree_common.countries WHERE code = 'US'
ON CONFLICT (code) DO NOTHING;

-- Vietnam - Major Cities/Provinces
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'VN_HCMC', 'Ho Chi Minh City', id, 'City', 1 FROM ree_common.countries WHERE code = 'VN'
UNION ALL
SELECT 'VN_HANOI', 'Hanoi', id, 'City', 2 FROM ree_common.countries WHERE code = 'VN'
UNION ALL
SELECT 'VN_DANANG', 'Da Nang', id, 'City', 3 FROM ree_common.countries WHERE code = 'VN'
UNION ALL
SELECT 'VN_BINH_DUONG', 'Binh Duong', id, 'Province', 4 FROM ree_common.countries WHERE code = 'VN'
UNION ALL
SELECT 'VN_DONG_NAI', 'Dong Nai', id, 'Province', 5 FROM ree_common.countries WHERE code = 'VN'
ON CONFLICT (code) DO NOTHING;

-- Thailand - Major Cities
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'TH_BANGKOK', 'Bangkok', id, 'City', 1 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_PHUKET', 'Phuket', id, 'Province', 2 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_PATTAYA', 'Pattaya', id, 'City', 3 FROM ree_common.countries WHERE code = 'TH'
ON CONFLICT (code) DO NOTHING;

-- Singapore (City-State - no provinces)
-- Japan - Major Cities
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'JP_TOKYO', 'Tokyo', id, 'Prefecture', 1 FROM ree_common.countries WHERE code = 'JP'
UNION ALL
SELECT 'JP_OSAKA', 'Osaka', id, 'Prefecture', 2 FROM ree_common.countries WHERE code = 'JP'
UNION ALL
SELECT 'JP_KYOTO', 'Kyoto', id, 'Prefecture', 3 FROM ree_common.countries WHERE code = 'JP'
ON CONFLICT (code) DO NOTHING;

-- China - Major Cities
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'CN_SHANGHAI', 'Shanghai', id, 'City', 1 FROM ree_common.countries WHERE code = 'CN'
UNION ALL
SELECT 'CN_BEIJING', 'Beijing', id, 'City', 2 FROM ree_common.countries WHERE code = 'CN'
UNION ALL
SELECT 'CN_SHENZHEN', 'Shenzhen', id, 'City', 3 FROM ree_common.countries WHERE code = 'CN'
ON CONFLICT (code) DO NOTHING;

-- Malaysia - Major Cities
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'MY_KL', 'Kuala Lumpur', id, 'City', 1 FROM ree_common.countries WHERE code = 'MY'
UNION ALL
SELECT 'MY_PENANG', 'Penang', id, 'State', 2 FROM ree_common.countries WHERE code = 'MY'
ON CONFLICT (code) DO NOTHING;

-- UK - Major Cities
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'GB_LONDON', 'London', id, 'City', 1 FROM ree_common.countries WHERE code = 'GB'
UNION ALL
SELECT 'GB_MANCHESTER', 'Manchester', id, 'City', 2 FROM ree_common.countries WHERE code = 'GB'
ON CONFLICT (code) DO NOTHING;

-- Australia - Major Cities
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'AU_SYDNEY', 'Sydney (NSW)', id, 'State', 1 FROM ree_common.countries WHERE code = 'AU'
UNION ALL
SELECT 'AU_MELBOURNE', 'Melbourne (VIC)', id, 'State', 2 FROM ree_common.countries WHERE code = 'AU'
ON CONFLICT (code) DO NOTHING;

-- UAE - Major Cities
INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'AE_DUBAI', 'Dubai', id, 'Emirate', 1 FROM ree_common.countries WHERE code = 'AE'
UNION ALL
SELECT 'AE_ABU_DHABI', 'Abu Dhabi', id, 'Emirate', 2 FROM ree_common.countries WHERE code = 'AE'
ON CONFLICT (code) DO NOTHING;

-- ================================================================
-- STEP 4: Seed Provinces Translations
-- ================================================================

-- English (all provinces)
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'en', name, ARRAY[LOWER(name), code]
FROM ree_common.provinces;

-- Vietnamese translations (Vietnam + popular cities)
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases) VALUES
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HCMC'), 'vi', 'TP. Hồ Chí Minh', ARRAY['hồ chí minh', 'sài gòn', 'hcm', 'tphcm', 'saigon']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HANOI'), 'vi', 'Hà Nội', ARRAY['hà nội', 'hanoi', 'thủ đô']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_DANANG'), 'vi', 'Đà Nẵng', ARRAY['đà nẵng', 'da nang', 'danang']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BINH_DUONG'), 'vi', 'Bình Dương', ARRAY['bình dương', 'binh duong', 'thủ dầu một']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_DONG_NAI'), 'vi', 'Đồng Nai', ARRAY['đồng nai', 'dong nai', 'biên hòa']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_BANGKOK'), 'vi', 'Bangkok', ARRAY['bangkok', 'băng cốc', 'krung thep']),
((SELECT id FROM ree_common.provinces WHERE code = 'TH_PHUKET'), 'vi', 'Phuket', ARRAY['phuket', 'phú quốc thái']),
((SELECT id FROM ree_common.provinces WHERE code = 'JP_TOKYO'), 'vi', 'Tokyo', ARRAY['tokyo', 'đông kinh']),
((SELECT id FROM ree_common.provinces WHERE code = 'AE_DUBAI'), 'vi', 'Dubai', ARRAY['dubai', 'du-bai'])
ON CONFLICT (province_id, lang_code) DO NOTHING;

-- ================================================================
-- STEP 5: Update existing Districts with country_id and province_id
-- ================================================================

-- Update HCMC districts
UPDATE ree_common.districts
SET
    country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN'),
    province_id = (SELECT id FROM ree_common.provinces WHERE code = 'VN_HCMC')
WHERE code IN ('Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12',
               'BINH_THANH', 'PHU_NHUAN', 'TAN_BINH', 'TAN_PHU', 'GO_VAP', 'BINH_TAN',
               'THU_DUC', 'CU_CHI', 'HOC_MON', 'BINH_CHANH', 'NHA_BE');

-- ================================================================
-- STEP 6: Seed Sample Streets (Multi-country)
-- ================================================================

-- USA Streets (Los Angeles, New York)
INSERT INTO ree_common.streets (code, name, street_type, country_id, sort_order)
SELECT 'US_SUNSET_BLVD', 'Sunset Boulevard', 'Boulevard', id, 1 FROM ree_common.countries WHERE code = 'US'
UNION ALL
SELECT 'US_HOLLYWOOD_BLVD', 'Hollywood Boulevard', 'Boulevard', id, 2 FROM ree_common.countries WHERE code = 'US'
UNION ALL
SELECT 'US_5TH_AVE', 'Fifth Avenue', 'Avenue', id, 3 FROM ree_common.countries WHERE code = 'US'
UNION ALL
SELECT 'US_BROADWAY', 'Broadway', 'Street', id, 4 FROM ree_common.countries WHERE code = 'US'
ON CONFLICT (code) DO NOTHING;

-- Vietnam Streets (HCMC)
INSERT INTO ree_common.streets (code, name, street_type, country_id, sort_order)
SELECT 'VN_NGUYEN_HUE', 'Nguyen Hue', 'Boulevard', id, 1 FROM ree_common.countries WHERE code = 'VN'
UNION ALL
SELECT 'VN_LE_LOI', 'Le Loi', 'Street', id, 2 FROM ree_common.countries WHERE code = 'VN'
UNION ALL
SELECT 'VN_DONG_KHOI', 'Dong Khoi', 'Street', id, 3 FROM ree_common.countries WHERE code = 'VN'
UNION ALL
SELECT 'VN_NGUYEN_VAN_LINH', 'Nguyen Van Linh', 'Avenue', id, 4 FROM ree_common.countries WHERE code = 'VN'
ON CONFLICT (code) DO NOTHING;

-- Thailand Streets (Bangkok)
INSERT INTO ree_common.streets (code, name, street_type, country_id, sort_order)
SELECT 'TH_SUKHUMVIT', 'Sukhumvit Road', 'Road', id, 1 FROM ree_common.countries WHERE code = 'TH'
UNION ALL
SELECT 'TH_SILOM', 'Silom Road', 'Road', id, 2 FROM ree_common.countries WHERE code = 'TH'
ON CONFLICT (code) DO NOTHING;

-- Singapore Streets
INSERT INTO ree_common.streets (code, name, street_type, country_id, sort_order)
SELECT 'SG_ORCHARD', 'Orchard Road', 'Road', id, 1 FROM ree_common.countries WHERE code = 'SG'
UNION ALL
SELECT 'SG_MARINA_BAY', 'Marina Bay', 'Area', id, 2 FROM ree_common.countries WHERE code = 'SG'
ON CONFLICT (code) DO NOTHING;

-- Japan Streets (Tokyo)
INSERT INTO ree_common.streets (code, name, street_type, country_id, sort_order)
SELECT 'JP_SHIBUYA', 'Shibuya Crossing', 'Intersection', id, 1 FROM ree_common.countries WHERE code = 'JP'
UNION ALL
SELECT 'JP_SHINJUKU', 'Shinjuku', 'District', id, 2 FROM ree_common.countries WHERE code = 'JP'
ON CONFLICT (code) DO NOTHING;

-- ================================================================
-- STEP 7: Seed Streets Translations
-- ================================================================

-- English (all streets)
INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'en', name, ARRAY[LOWER(name), code]
FROM ree_common.streets;

-- Vietnamese translations (Vietnam streets)
INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases) VALUES
((SELECT id FROM ree_common.streets WHERE code = 'VN_NGUYEN_HUE'), 'vi', 'Đường Nguyễn Huệ', ARRAY['nguyễn huệ', 'nguyen hue', 'phố đi bộ nguyễn huệ']),
((SELECT id FROM ree_common.streets WHERE code = 'VN_LE_LOI'), 'vi', 'Đường Lê Lợi', ARRAY['lê lợi', 'le loi']),
((SELECT id FROM ree_common.streets WHERE code = 'VN_DONG_KHOI'), 'vi', 'Đường Đồng Khởi', ARRAY['đồng khởi', 'dong khoi']),
((SELECT id FROM ree_common.streets WHERE code = 'VN_NGUYEN_VAN_LINH'), 'vi', 'Đại Lộ Nguyễn Văn Linh', ARRAY['nguyễn văn linh', 'nguyen van linh', 'nvl'])
ON CONFLICT (street_id, lang_code) DO NOTHING;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT
    'Countries' as table_name,
    COUNT(*) as records
FROM ree_common.countries
UNION ALL
SELECT 'Provinces/States', COUNT(*) FROM ree_common.provinces
UNION ALL
SELECT 'Districts', COUNT(*) FROM ree_common.districts
UNION ALL
SELECT 'Streets', COUNT(*) FROM ree_common.streets
ORDER BY table_name;

-- Show countries with counts
SELECT 'Countries with Provinces:' as info;
SELECT
    c.code as country_code,
    c.name as country,
    c.region,
    COUNT(p.id) as provinces_count
FROM ree_common.countries c
LEFT JOIN ree_common.provinces p ON c.id = p.country_id
GROUP BY c.id, c.code, c.name, c.region
ORDER BY c.sort_order;

-- Show sample data per country
SELECT 'Sample Provinces by Country:' as info;
SELECT
    c.code as country,
    p.code as province_code,
    p.name as province_name,
    p.admin_level,
    pt_vi.translated_text as name_vi,
    pt_en.translated_text as name_en
FROM ree_common.provinces p
JOIN ree_common.countries c ON p.country_id = c.id
LEFT JOIN ree_common.provinces_translation pt_vi ON p.id = pt_vi.province_id AND pt_vi.lang_code = 'vi'
LEFT JOIN ree_common.provinces_translation pt_en ON p.id = pt_en.province_id AND pt_en.lang_code = 'en'
ORDER BY c.sort_order, p.sort_order
LIMIT 15;

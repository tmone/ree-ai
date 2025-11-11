-- Seed 004: Foreign Master Data
-- Description: Seed data for Vietnam, Japan, China, and Korea markets
-- Purpose: Populate countries, currencies, cities, and country-specific data

-- ============================================================
-- SEED COUNTRIES
-- ============================================================

INSERT INTO master_countries (code, code_2, name_en, name_local, name_vi, aliases, region, continent, phone_code, default_currency_code, is_primary, popularity_rank, sort_order) VALUES
-- Vietnam (Primary)
('VNM', 'VN', 'Vietnam', 'Việt Nam', 'Việt Nam',
 ARRAY['Vietnam', 'Việt Nam', 'VN', 'VNM', '越南', 'ベトナム', '베트남'],
 'southeast_asia', 'asia', '+84', 'VND', TRUE, 1, 1),

-- Japan (Primary)
('JPN', 'JP', 'Japan', '日本', 'Nhật Bản',
 ARRAY['Japan', 'Nhật Bản', 'JP', 'JPN', '日本', 'にほん', 'にっぽん', 'Nippon', '일본'],
 'east_asia', 'asia', '+81', 'JPY', TRUE, 2, 2),

-- China (Primary)
('CHN', 'CN', 'China', '中国', 'Trung Quốc',
 ARRAY['China', 'Trung Quốc', 'CN', 'CHN', '中国', '中華', 'Zhongguo', 'PRC', '중국'],
 'east_asia', 'asia', '+86', 'CNY', TRUE, 3, 3),

-- South Korea (Primary)
('KOR', 'KR', 'South Korea', '대한민국', 'Hàn Quốc',
 ARRAY['South Korea', 'Korea', 'Hàn Quốc', 'KR', 'KOR', '韓国', '대한민국', 'ROK', 'Daehan Minguk', '한국'],
 'east_asia', 'asia', '+82', 'KRW', TRUE, 4, 4)

ON CONFLICT (code) DO UPDATE SET
    name_en = EXCLUDED.name_en,
    name_local = EXCLUDED.name_local,
    name_vi = EXCLUDED.name_vi,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- SEED CURRENCIES
-- ============================================================

INSERT INTO master_currencies (code, symbol, name_en, name_vi, aliases, decimal_places, exchange_rate_to_usd, format_pattern, symbol_position) VALUES
-- Vietnamese Dong
('VND', '₫', 'Vietnamese Dong', 'Đồng Việt Nam',
 ARRAY['VND', 'dong', 'đồng', 'việt nam đồng', 'VN dong', '₫'],
 0, 24500.00, '#,##0', 'after'),

-- Japanese Yen
('JPY', '¥', 'Japanese Yen', 'Yên Nhật',
 ARRAY['JPY', 'yen', 'yên', '円', 'えん', '¥', 'japanese yen'],
 0, 150.00, '#,##0', 'before'),

-- Chinese Yuan (Renminbi)
('CNY', '¥', 'Chinese Yuan', 'Nhân dân tệ',
 ARRAY['CNY', 'yuan', 'renminbi', 'RMB', 'nhân dân tệ', '人民币', '元', '¥', 'chinese yuan'],
 2, 7.25, '#,##0.00', 'before'),

-- South Korean Won
('KRW', '₩', 'South Korean Won', 'Won Hàn Quốc',
 ARRAY['KRW', 'won', '원', '₩', 'korean won', 'south korean won'],
 0, 1320.00, '#,##0', 'before'),

-- US Dollar (for reference)
('USD', '$', 'US Dollar', 'Đô la Mỹ',
 ARRAY['USD', 'dollar', 'đô la', 'đô', '$', 'US dollar', 'american dollar'],
 2, 1.00, '#,##0.00', 'before')

ON CONFLICT (code) DO UPDATE SET
    symbol = EXCLUDED.symbol,
    name_en = EXCLUDED.name_en,
    name_vi = EXCLUDED.name_vi,
    aliases = EXCLUDED.aliases,
    exchange_rate_to_usd = EXCLUDED.exchange_rate_to_usd,
    updated_at = CURRENT_TIMESTAMP;

-- Update country default currencies (add foreign key reference)
UPDATE master_countries SET default_currency_code = 'VND' WHERE code = 'VNM';
UPDATE master_countries SET default_currency_code = 'JPY' WHERE code = 'JPN';
UPDATE master_countries SET default_currency_code = 'CNY' WHERE code = 'CHN';
UPDATE master_countries SET default_currency_code = 'KRW' WHERE code = 'KOR';

-- ============================================================
-- SEED MAJOR CITIES - JAPAN
-- ============================================================

-- Get Japan country ID
DO $$
DECLARE
    japan_id INTEGER;
    china_id INTEGER;
    korea_id INTEGER;
    vietnam_id INTEGER;
BEGIN
    SELECT id INTO japan_id FROM master_countries WHERE code = 'JPN';
    SELECT id INTO china_id FROM master_countries WHERE code = 'CHN';
    SELECT id INTO korea_id FROM master_countries WHERE code = 'KOR';
    SELECT id INTO vietnam_id FROM master_countries WHERE code = 'VNM';

    -- JAPAN - Major Cities
    INSERT INTO master_districts (code, name_vi, name_en, city, aliases, country_id, region, latitude, longitude) VALUES
    -- Tokyo Area
    ('JP_TOKYO', 'Tokyo', 'Tokyo', 'Tokyo',
     ARRAY['Tokyo', '東京', 'とうきょう', 'Toukyou', 'Tôkyô'],
     japan_id, 'Kanto', 35.6762, 139.6503),

    ('JP_SHIBUYA', 'Shibuya', 'Shibuya', 'Tokyo',
     ARRAY['Shibuya', '渋谷', 'しぶや', 'Shibuya-ku'],
     japan_id, 'Kanto', 35.6580, 139.7016),

    ('JP_SHINJUKU', 'Shinjuku', 'Shinjuku', 'Tokyo',
     ARRAY['Shinjuku', '新宿', 'しんじゅく', 'Shinjuku-ku'],
     japan_id, 'Kanto', 35.6938, 139.7034),

    ('JP_MINATO', 'Minato', 'Minato', 'Tokyo',
     ARRAY['Minato', '港区', 'みなとく', 'Minato-ku', 'Roppongi', 'Azabu'],
     japan_id, 'Kanto', 35.6585, 139.7514),

    ('JP_CHIYODA', 'Chiyoda', 'Chiyoda', 'Tokyo',
     ARRAY['Chiyoda', '千代田', 'ちよだ', 'Chiyoda-ku'],
     japan_id, 'Kanto', 35.6940, 139.7536),

    -- Osaka Area
    ('JP_OSAKA', 'Osaka', 'Osaka', 'Osaka',
     ARRAY['Osaka', '大阪', 'おおさか', 'Oosaka', 'Ôsaka'],
     japan_id, 'Kansai', 34.6937, 135.5023),

    ('JP_KITA_OSAKA', 'Kita (Osaka)', 'Kita', 'Osaka',
     ARRAY['Kita', '北区', 'きたく', 'Kita-ku Osaka', 'Umeda'],
     japan_id, 'Kansai', 34.7062, 135.5024),

    ('JP_CHUO_OSAKA', 'Chuo (Osaka)', 'Chuo', 'Osaka',
     ARRAY['Chuo', '中央区', 'ちゅうおうく', 'Chuo-ku Osaka'],
     japan_id, 'Kansai', 34.6780, 135.5145),

    -- Kyoto
    ('JP_KYOTO', 'Kyoto', 'Kyoto', 'Kyoto',
     ARRAY['Kyoto', '京都', 'きょうと', 'Kyouto'],
     japan_id, 'Kansai', 35.0116, 135.7681),

    -- Yokohama
    ('JP_YOKOHAMA', 'Yokohama', 'Yokohama', 'Yokohama',
     ARRAY['Yokohama', '横浜', 'よこはま'],
     japan_id, 'Kanto', 35.4437, 139.6380),

    -- Nagoya
    ('JP_NAGOYA', 'Nagoya', 'Nagoya', 'Nagoya',
     ARRAY['Nagoya', '名古屋', 'なごや'],
     japan_id, 'Chubu', 35.1815, 136.9066),

    -- Fukuoka
    ('JP_FUKUOKA', 'Fukuoka', 'Fukuoka', 'Fukuoka',
     ARRAY['Fukuoka', '福岡', 'ふくおか', 'Hakata'],
     japan_id, 'Kyushu', 33.5904, 130.4017),

    -- Sapporo
    ('JP_SAPPORO', 'Sapporo', 'Sapporo', 'Sapporo',
     ARRAY['Sapporo', '札幌', 'さっぽろ'],
     japan_id, 'Hokkaido', 43.0642, 141.3469)

    ON CONFLICT (code) DO UPDATE SET
        name_en = EXCLUDED.name_en,
        aliases = EXCLUDED.aliases,
        updated_at = CURRENT_TIMESTAMP;

    -- ============================================================
    -- SEED MAJOR CITIES - CHINA
    -- ============================================================

    INSERT INTO master_districts (code, name_vi, name_en, city, aliases, country_id, region, latitude, longitude) VALUES
    -- Beijing
    ('CN_BEIJING', 'Bắc Kinh', 'Beijing', 'Beijing',
     ARRAY['Beijing', '北京', 'Bắc Kinh', 'Peking', 'Běijīng'],
     china_id, 'North China', 39.9042, 116.4074),

    ('CN_CHAOYANG', 'Triều Dương', 'Chaoyang', 'Beijing',
     ARRAY['Chaoyang', '朝阳区', 'Cháoyáng', 'Triều Dương'],
     china_id, 'North China', 39.9219, 116.4434),

    ('CN_HAIDIAN', 'Hải Điến', 'Haidian', 'Beijing',
     ARRAY['Haidian', '海淀区', 'Hǎidiàn', 'Hải Điến'],
     china_id, 'North China', 39.9590, 116.2988),

    -- Shanghai
    ('CN_SHANGHAI', 'Thượng Hải', 'Shanghai', 'Shanghai',
     ARRAY['Shanghai', '上海', 'Thượng Hải', 'Shànghǎi'],
     china_id, 'East China', 31.2304, 121.4737),

    ('CN_PUDONG', 'Phố Đông', 'Pudong', 'Shanghai',
     ARRAY['Pudong', '浦东', 'Pǔdōng', 'Phố Đông', 'Pudong New Area'],
     china_id, 'East China', 31.2231, 121.5397),

    ('CN_HUANGPU', 'Hoàng Phố', 'Huangpu', 'Shanghai',
     ARRAY['Huangpu', '黄浦区', 'Huángpǔ', 'Hoàng Phố'],
     china_id, 'East China', 31.2317, 121.4900),

    -- Guangzhou
    ('CN_GUANGZHOU', 'Quảng Châu', 'Guangzhou', 'Guangzhou',
     ARRAY['Guangzhou', '广州', 'Quảng Châu', 'Guǎngzhōu', 'Canton'],
     china_id, 'South China', 23.1291, 113.2644),

    ('CN_TIANHE', 'Thiên Hà', 'Tianhe', 'Guangzhou',
     ARRAY['Tianhe', '天河区', 'Tiānhé', 'Thiên Hà'],
     china_id, 'South China', 23.1248, 113.3613),

    -- Shenzhen
    ('CN_SHENZHEN', 'Thâm Quyến', 'Shenzhen', 'Shenzhen',
     ARRAY['Shenzhen', '深圳', 'Thâm Quyến', 'Shēnzhèn'],
     china_id, 'South China', 22.5431, 114.0579),

    ('CN_FUTIAN', 'Phúc Điền', 'Futian', 'Shenzhen',
     ARRAY['Futian', '福田区', 'Fútián', 'Phúc Điền'],
     china_id, 'South China', 22.5428, 114.0552),

    ('CN_NANSHAN', 'Nam Sơn', 'Nanshan', 'Shenzhen',
     ARRAY['Nanshan', '南山区', 'Nánshān', 'Nam Sơn'],
     china_id, 'South China', 22.5333, 113.9333),

    -- Chengdu
    ('CN_CHENGDU', 'Thành Đô', 'Chengdu', 'Chengdu',
     ARRAY['Chengdu', '成都', 'Thành Đô', 'Chéngdū'],
     china_id, 'Southwest China', 30.5728, 104.0668),

    -- Hangzhou
    ('CN_HANGZHOU', 'Hàng Châu', 'Hangzhou', 'Hangzhou',
     ARRAY['Hangzhou', '杭州', 'Hàng Châu', 'Hángzhōu'],
     china_id, 'East China', 30.2741, 120.1551),

    -- Nanjing
    ('CN_NANJING', 'Nam Kinh', 'Nanjing', 'Nanjing',
     ARRAY['Nanjing', '南京', 'Nam Kinh', 'Nánjīng', 'Nanking'],
     china_id, 'East China', 32.0603, 118.7969)

    ON CONFLICT (code) DO UPDATE SET
        name_en = EXCLUDED.name_en,
        aliases = EXCLUDED.aliases,
        updated_at = CURRENT_TIMESTAMP;

    -- ============================================================
    -- SEED MAJOR CITIES - SOUTH KOREA
    -- ============================================================

    INSERT INTO master_districts (code, name_vi, name_en, city, aliases, country_id, region, latitude, longitude) VALUES
    -- Seoul
    ('KR_SEOUL', 'Seoul', 'Seoul', 'Seoul',
     ARRAY['Seoul', '서울', 'Sơ-un', '首爾', 'ソウル'],
     korea_id, 'Seoul', 37.5665, 126.9780),

    ('KR_GANGNAM', 'Gangnam', 'Gangnam', 'Seoul',
     ARRAY['Gangnam', '강남구', 'Gangnam-gu', 'Cường Nam'],
     korea_id, 'Seoul', 37.5172, 127.0473),

    ('KR_GANGDONG', 'Gangdong', 'Gangdong', 'Seoul',
     ARRAY['Gangdong', '강동구', 'Gangdong-gu', 'Cường Đông'],
     korea_id, 'Seoul', 37.5301, 127.1238),

    ('KR_JONGNO', 'Jongno', 'Jongno', 'Seoul',
     ARRAY['Jongno', '종로구', 'Jongno-gu', 'Chung Lộ'],
     korea_id, 'Seoul', 37.5730, 126.9794),

    ('KR_MAPO', 'Mapo', 'Mapo', 'Seoul',
     ARRAY['Mapo', '마포구', 'Mapo-gu', 'Ma Po'],
     korea_id, 'Seoul', 37.5664, 126.9019),

    -- Busan
    ('KR_BUSAN', 'Busan', 'Busan', 'Busan',
     ARRAY['Busan', '부산', 'Pusan', 'Phủ Sơn', '釜山'],
     korea_id, 'Busan', 35.1796, 129.0756),

    ('KR_HAEUNDAE', 'Haeundae', 'Haeundae', 'Busan',
     ARRAY['Haeundae', '해운대구', 'Haeundae-gu', 'Hải Vân Đài'],
     korea_id, 'Busan', 35.1628, 129.1635),

    -- Incheon
    ('KR_INCHEON', 'Incheon', 'Incheon', 'Incheon',
     ARRAY['Incheon', '인천', 'Nhân Xuyên', '仁川'],
     korea_id, 'Incheon', 37.4563, 126.7052),

    -- Daegu
    ('KR_DAEGU', 'Daegu', 'Daegu', 'Daegu',
     ARRAY['Daegu', '대구', 'Taegu', 'Đại Khâu', '大邱'],
     korea_id, 'Daegu', 35.8714, 128.6014),

    -- Daejeon
    ('KR_DAEJEON', 'Daejeon', 'Daejeon', 'Daejeon',
     ARRAY['Daejeon', '대전', 'Taejon', 'Đại Điền', '大田'],
     korea_id, 'Daejeon', 36.3504, 127.3845),

    -- Gwangju
    ('KR_GWANGJU', 'Gwangju', 'Gwangju', 'Gwangju',
     ARRAY['Gwangju', '광주', 'Kwangju', 'Quang Châu', '光州'],
     korea_id, 'Gwangju', 35.1595, 126.8526),

    -- Jeju
    ('KR_JEJU', 'Jeju', 'Jeju', 'Jeju',
     ARRAY['Jeju', '제주', 'Cheju', 'Tế Châu', '濟州', 'Jeju Island'],
     korea_id, 'Jeju', 33.4996, 126.5312)

    ON CONFLICT (code) DO UPDATE SET
        name_en = EXCLUDED.name_en,
        aliases = EXCLUDED.aliases,
        updated_at = CURRENT_TIMESTAMP;

    -- ============================================================
    -- UPDATE VIETNAM CITIES WITH COUNTRY_ID
    -- ============================================================

    -- Update existing Vietnam districts with country_id
    UPDATE master_districts
    SET country_id = vietnam_id,
        region = 'Southeast Region'
    WHERE city = 'Ho Chi Minh City' OR code LIKE 'Q%' OR code = 'HCMC';

END $$;

-- ============================================================
-- SEED UNIT CONVERSIONS
-- ============================================================

INSERT INTO master_unit_conversions (unit_type, from_unit, to_unit, conversion_factor, from_aliases, to_aliases, description) VALUES
-- Area conversions
('area', 'm2', 'sqft', 10.7639,
 ARRAY['m2', 'm²', 'sqm', 'mét vuông', 'met vuong', 'square meter'],
 ARRAY['sqft', 'ft2', 'ft²', 'square feet', 'feet vuông'],
 'Square meters to square feet'),

('area', 'sqft', 'm2', 0.092903,
 ARRAY['sqft', 'ft2', 'ft²', 'square feet', 'feet vuông'],
 ARRAY['m2', 'm²', 'sqm', 'mét vuông', 'met vuong', 'square meter'],
 'Square feet to square meters'),

('area', 'm2', 'tsubo', 0.3025,
 ARRAY['m2', 'm²', 'sqm', 'mét vuông'],
 ARRAY['tsubo', '坪', 'つぼ'],
 'Square meters to tsubo (Japanese unit)'),

('area', 'tsubo', 'm2', 3.30579,
 ARRAY['tsubo', '坪', 'つぼ'],
 ARRAY['m2', 'm²', 'sqm', 'mét vuông'],
 'Tsubo to square meters'),

('area', 'm2', 'pyeong', 0.3025,
 ARRAY['m2', 'm²', 'sqm', 'mét vuông'],
 ARRAY['pyeong', '평', 'py'],
 'Square meters to pyeong (Korean unit)'),

('area', 'pyeong', 'm2', 3.30579,
 ARRAY['pyeong', '평', 'py'],
 ARRAY['m2', 'm²', 'sqm', 'mét vuông'],
 'Pyeong to square meters')

ON CONFLICT (unit_type, from_unit, to_unit) DO UPDATE SET
    conversion_factor = EXCLUDED.conversion_factor,
    from_aliases = EXCLUDED.from_aliases,
    to_aliases = EXCLUDED.to_aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- STATISTICS
-- ============================================================

-- Print summary
DO $$
DECLARE
    country_count INTEGER;
    currency_count INTEGER;
    city_count INTEGER;
    conversion_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO country_count FROM master_countries WHERE active = TRUE;
    SELECT COUNT(*) INTO currency_count FROM master_currencies WHERE active = TRUE;
    SELECT COUNT(*) INTO city_count FROM master_districts WHERE active = TRUE;
    SELECT COUNT(*) INTO conversion_count FROM master_unit_conversions WHERE active = TRUE;

    RAISE NOTICE '============================================================';
    RAISE NOTICE 'FOREIGN MASTER DATA SEEDING COMPLETE';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Countries seeded: %', country_count;
    RAISE NOTICE 'Currencies seeded: %', currency_count;
    RAISE NOTICE 'Cities/Districts seeded: %', city_count;
    RAISE NOTICE 'Unit conversions seeded: %', conversion_count;
    RAISE NOTICE '============================================================';
END $$;

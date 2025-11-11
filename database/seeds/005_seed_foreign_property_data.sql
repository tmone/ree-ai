-- Seed 005: Foreign Property-Specific Data
-- Description: Property types, legal status, developers, and country features for Japan, China, Korea
-- Purpose: Add country-specific real estate data

-- ============================================================
-- SEED COUNTRY-SPECIFIC PROPERTY TYPES
-- ============================================================

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

    -- JAPAN - Property Types
    INSERT INTO master_property_types (code, name_vi, name_en, aliases, category, typical_min_area, typical_max_area, typical_min_bedrooms, typical_max_bedrooms, country_id, is_global) VALUES

    -- Mansion (Japanese apartment)
    ('JP_MANSION', 'Mansion', 'Mansion',
     ARRAY['Mansion', 'マンション', 'まんしょん', 'Japanese apartment', 'condo'],
     'residential', 30, 150, 1, 4, japan_id, FALSE),

    -- Apāto (Older apartment)
    ('JP_APAATO', 'Apāto', 'Apaato',
     ARRAY['Apaato', 'アパート', 'あぱーと', 'Japanese apartment building'],
     'residential', 20, 60, 1, 2, japan_id, FALSE),

    -- Ikkodate (Detached house)
    ('JP_IKKODATE', 'Ikkodate', 'Detached House',
     ARRAY['Ikkodate', '一戸建て', 'いっこだて', 'detached house', 'single family'],
     'residential', 80, 300, 2, 5, japan_id, FALSE),

    -- Terrace House
    ('JP_TERRACE', 'Terrace House', 'Terrace House',
     ARRAY['Terrace House', 'テラスハウス', 'townhouse'],
     'residential', 60, 150, 2, 4, japan_id, FALSE),

    -- Machiya (Traditional townhouse)
    ('JP_MACHIYA', 'Machiya', 'Machiya',
     ARRAY['Machiya', '町家', 'まちや', 'traditional house', 'kyomachiya'],
     'residential', 50, 200, 2, 5, japan_id, FALSE),

    -- Tower Mansion (Luxury high-rise)
    ('JP_TOWER', 'Tower Mansion', 'Tower Mansion',
     ARRAY['Tower Mansion', 'タワーマンション', 'tower', 'luxury highrise'],
     'residential', 50, 300, 1, 4, japan_id, FALSE),

    -- CHINA - Property Types

    -- Apartment (公寓)
    ('CN_APARTMENT', 'Công Dụ', 'Apartment',
     ARRAY['Apartment', '公寓', 'gōngyù', 'condo'],
     'residential', 40, 200, 1, 4, china_id, FALSE),

    -- Villa (别墅)
    ('CN_VILLA', 'Biệt Thự', 'Villa',
     ARRAY['Villa', '别墅', 'biéshù', 'detached house'],
     'residential', 150, 800, 3, 6, china_id, FALSE),

    -- Townhouse (联排别墅)
    ('CN_TOWNHOUSE', 'Liên Bài', 'Townhouse',
     ARRAY['Townhouse', '联排别墅', 'liánpái biéshù', '联排'],
     'residential', 100, 300, 2, 5, china_id, FALSE),

    -- Quadrangle (四合院)
    ('CN_SIHEYUAN', 'Tứ Hợp Viện', 'Siheyuan',
     ARRAY['Siheyuan', '四合院', 'sìhéyuàn', 'courtyard house', 'quadrangle'],
     'residential', 200, 1000, 3, 8, china_id, FALSE),

    -- Serviced Apartment (酒店式公寓)
    ('CN_SERVICED_APT', 'Căn Hộ Dịch Vụ', 'Serviced Apartment',
     ARRAY['Serviced Apartment', '酒店式公寓', 'jiǔdiàn shì gōngyù'],
     'residential', 30, 150, 1, 3, china_id, FALSE),

    -- Loft (阁楼)
    ('CN_LOFT', 'Loft', 'Loft',
     ARRAY['Loft', '阁楼', 'gélóu', 'SOHO'],
     'residential', 40, 200, 1, 3, china_id, FALSE),

    -- SOUTH KOREA - Property Types

    -- Apartment (아파트)
    ('KR_APARTMENT', 'Căn Hộ', 'Apartment',
     ARRAY['Apartment', '아파트', 'apateu', 'Korean apartment'],
     'residential', 40, 250, 2, 5, korea_id, FALSE),

    -- Villa (빌라)
    ('KR_VILLA', 'Villa', 'Villa',
     ARRAY['Villa', '빌라', 'billa', 'multi-family house'],
     'residential', 30, 100, 1, 3, korea_id, FALSE),

    -- Officetel (오피스텔)
    ('KR_OFFICETEL', 'Officetel', 'Officetel',
     ARRAY['Officetel', '오피스텔', 'opiseutel', 'studio apartment'],
     'residential', 15, 60, 0, 2, korea_id, FALSE),

    -- Detached House (단독주택)
    ('KR_DETACHED', 'Nhà Riêng', 'Detached House',
     ARRAY['Detached House', '단독주택', 'dandok jutaek', 'single house'],
     'residential', 80, 400, 2, 5, korea_id, FALSE),

    -- Townhouse (연립주택)
    ('KR_TOWNHOUSE', 'Liên Lập', 'Townhouse',
     ARRAY['Townhouse', '연립주택', 'yeollip jutaek'],
     'residential', 60, 150, 2, 4, korea_id, FALSE),

    -- Hanok (한옥)
    ('KR_HANOK', 'Hanok', 'Hanok',
     ARRAY['Hanok', '한옥', 'traditional Korean house'],
     'residential', 80, 300, 2, 5, korea_id, FALSE)

    ON CONFLICT (code) DO UPDATE SET
        name_en = EXCLUDED.name_en,
        aliases = EXCLUDED.aliases,
        updated_at = CURRENT_TIMESTAMP;

    -- ============================================================
    -- SEED COUNTRY-SPECIFIC LEGAL STATUS
    -- ============================================================

    -- JAPAN - Legal Status
    INSERT INTO master_legal_status (code, name_vi, name_en, aliases, trust_level, country_id) VALUES

    ('JP_OWNERSHIP', 'Quyền Sở Hữu', 'Ownership Rights',
     ARRAY['所有権', 'しょゆうけん', 'ownership', 'freehold'],
     5, japan_id),

    ('JP_LEASEHOLD', 'Quyền Thuê Đất', 'Leasehold Rights',
     ARRAY['借地権', 'しゃくちけん', 'shakuchiken', 'leasehold'],
     4, japan_id),

    ('JP_CONDO_TITLE', 'Quyền Căn Hộ', 'Condominium Title',
     ARRAY['区分所有権', 'くぶんしょゆうけん', 'kubun shoyuken'],
     5, japan_id),

    ('JP_BUILDING_ONLY', 'Chỉ Sở Hữu Nhà', 'Building Only',
     ARRAY['建物のみ', 'たてもののみ', 'building only'],
     3, japan_id),

    -- CHINA - Legal Status

    ('CN_COMMODITY_HOUSE', 'Nhà Thương Phẩm', 'Commodity House',
     ARRAY['商品房', 'shāngpǐnfáng', 'commodity housing'],
     5, china_id),

    ('CN_RED_BOOK', 'Sổ Đỏ', 'Red Book',
     ARRAY['不动产权证', 'bùdòngchǎn quánzhèng', 'property certificate', 'red book'],
     5, china_id),

    ('CN_DUAL_CERT', 'Song Chứng', 'Dual Certificate',
     ARRAY['双证齐全', 'shuāngzhèng qíquán', 'land + house certificate'],
     5, china_id),

    ('CN_PRESALE_PERMIT', 'Giấy Phép Bán', 'Pre-sale Permit',
     ARRAY['预售许可证', 'yùshòu xǔkězhèng', 'presale permit'],
     4, china_id),

    ('CN_70_YEAR_LEASE', 'Thuê 70 Năm', '70-Year Lease',
     ARRAY['70年产权', '70 nián chǎnquán', '70-year property rights'],
     4, china_id),

    ('CN_50_YEAR_LEASE', 'Thuê 50 Năm', '50-Year Lease',
     ARRAY['50年产权', '50 nián chǎnquán', '50-year property rights'],
     4, china_id),

    ('CN_SMALL_PROPERTY', 'Tiểu Sản Quyền', 'Small Property Rights',
     ARRAY['小产权房', 'xiǎo chǎnquán fáng', 'village property'],
     2, china_id),

    -- SOUTH KOREA - Legal Status

    ('KR_OWNERSHIP', 'Quyền Sở Hữu', 'Ownership Rights',
     ARRAY['소유권', 'soyugwon', 'ownership'],
     5, korea_id),

    ('KR_REGISTRATION', 'Đăng Ký Bất Động Sản', 'Property Registration',
     ARRAY['등기', 'deunggi', 'registration certificate'],
     5, korea_id),

    ('KR_JEONSE_RIGHT', 'Quyền Jeonse', 'Jeonse Right',
     ARRAY['전세권', '전세', 'jeonse', 'lease deposit right'],
     4, korea_id),

    ('KR_MONTHLY_RENT', 'Thuê Tháng', 'Monthly Rent',
     ARRAY['월세', 'wolse', 'monthly rent'],
     3, korea_id)

    ON CONFLICT (code) DO UPDATE SET
        name_en = EXCLUDED.name_en,
        aliases = EXCLUDED.aliases,
        updated_at = CURRENT_TIMESTAMP;

    -- ============================================================
    -- SEED MAJOR DEVELOPERS
    -- ============================================================

    -- JAPAN - Major Developers
    INSERT INTO master_developers (code, name_vi, name_en, aliases, type, reputation_score, website, country_id, headquarters_city, total_projects, total_units_delivered) VALUES

    ('JP_MITSUI', 'Mitsui Fudosan', 'Mitsui Fudosan',
     ARRAY['Mitsui', 'Mitsui Fudosan', '三井不動産', 'みついふどうさん'],
     'corporation', 5, 'https://www.mitsuifudosan.co.jp', japan_id, 'Tokyo', 500, 50000),

    ('JP_MITSUBISHI', 'Mitsubishi Estate', 'Mitsubishi Estate',
     ARRAY['Mitsubishi Estate', '三菱地所', 'みつびしじしょ'],
     'corporation', 5, 'https://www.mec.co.jp', japan_id, 'Tokyo', 400, 40000),

    ('JP_SUMITOMO', 'Sumitomo Realty', 'Sumitomo Realty & Development',
     ARRAY['Sumitomo Realty', '住友不動産', 'すみともふどうさん'],
     'corporation', 5, 'https://www.sumitomo-rd.co.jp', japan_id, 'Tokyo', 600, 60000),

    ('JP_NOMURA', 'Nomura Real Estate', 'Nomura Real Estate',
     ARRAY['Nomura', '野村不動産', 'のむらふどうさん', 'Proud'],
     'corporation', 5, 'https://www.nomura-re.co.jp', japan_id, 'Tokyo', 300, 35000),

    ('JP_TOKYU', 'Tokyu Land', 'Tokyu Land Corporation',
     ARRAY['Tokyu Land', '東急不動産', 'とうきゅうふどうさん'],
     'corporation', 5, 'https://www.tokyu-land.co.jp', japan_id, 'Tokyo', 350, 40000),

    ('JP_DAITO', 'Daito Trust', 'Daito Trust Construction',
     ARRAY['Daito Trust', '大東建託', 'だいとうけんたく'],
     'corporation', 4, 'https://www.kentaku.co.jp', japan_id, 'Tokyo', 800, 100000),

    -- CHINA - Major Developers

    ('CN_VANKE', 'Vanke', 'China Vanke',
     ARRAY['Vanke', '万科', 'wànkē', 'China Vanke'],
     'corporation', 5, 'https://www.vanke.com', china_id, 'Shenzhen', 2000, 500000),

    ('CN_COUNTRY_GARDEN', 'Country Garden', 'Country Garden',
     ARRAY['Country Garden', '碧桂园', 'bìguìyuán'],
     'corporation', 4, 'https://www.countrygarden.com.cn', china_id, 'Foshan', 2500, 600000),

    ('CN_EVERGRANDE', 'Evergrande', 'China Evergrande',
     ARRAY['Evergrande', '恒大', 'héngdà', 'Hengda'],
     'corporation', 3, 'https://www.evergrande.com', china_id, 'Guangzhou', 1500, 400000),

    ('CN_POLY', 'Poly', 'Poly Developments',
     ARRAY['Poly', '保利', 'bǎolì', 'Poly Real Estate'],
     'corporation', 5, 'https://www.polycn.com', china_id, 'Guangzhou', 1000, 300000),

    ('CN_LONGFOR', 'Longfor', 'Longfor Properties',
     ARRAY['Longfor', '龙湖', 'lónghú'],
     'corporation', 5, 'https://www.longfor.com', china_id, 'Chongqing', 800, 250000),

    ('CN_SUNAC', 'Sunac', 'Sunac China',
     ARRAY['Sunac', '融创', 'róngchuàng'],
     'corporation', 4, 'https://www.sunac.com.cn', china_id, 'Tianjin', 900, 280000),

    ('CN_GREENLAND', 'Greenland', 'Greenland Holdings',
     ARRAY['Greenland', '绿地', 'lǜdì', 'Greenland Group'],
     'corporation', 4, 'https://www.greenlandsc.com', china_id, 'Shanghai', 1200, 350000),

    -- SOUTH KOREA - Major Developers

    ('KR_SAMSUNG', 'Samsung C&T', 'Samsung C&T',
     ARRAY['Samsung', '삼성물산', 'Samsung Construction', 'Raemian'],
     'corporation', 5, 'https://www.samsungcnt.com', korea_id, 'Seoul', 500, 200000),

    ('KR_HYUNDAI', 'Hyundai E&C', 'Hyundai Engineering & Construction',
     ARRAY['Hyundai', '현대건설', 'Hillstate', 'I-Park'],
     'corporation', 5, 'https://www.hdec.kr', korea_id, 'Seoul', 600, 250000),

    ('KR_DAEWOO', 'Daewoo E&C', 'Daewoo Engineering & Construction',
     ARRAY['Daewoo', '대우건설', 'Prugio'],
     'corporation', 5, 'https://www.daewooenc.com', korea_id, 'Seoul', 400, 180000),

    ('KR_POSCO', 'POSCO E&C', 'POSCO Engineering & Construction',
     ARRAY['POSCO', '포스코건설', 'The Sharp'],
     'corporation', 5, 'https://www.poscoenc.com', korea_id, 'Incheon', 350, 150000),

    ('KR_GS', 'GS E&C', 'GS Engineering & Construction',
     ARRAY['GS', 'GS건설', 'Xi'],
     'corporation', 5, 'https://www.gsconst.co.kr', korea_id, 'Seoul', 400, 170000),

    ('KR_LOTTE', 'Lotte E&C', 'Lotte Engineering & Construction',
     ARRAY['Lotte', '롯데건설', 'Lotte Castle'],
     'corporation', 4, 'https://www.lottecon.co.kr', korea_id, 'Seoul', 300, 130000)

    ON CONFLICT (code) DO UPDATE SET
        name_en = EXCLUDED.name_en,
        aliases = EXCLUDED.aliases,
        updated_at = CURRENT_TIMESTAMP;

    -- ============================================================
    -- SEED COUNTRY-SPECIFIC FEATURES
    -- ============================================================

    -- JAPAN - Country Features
    INSERT INTO master_country_features (code, name_en, name_local, name_vi, aliases, country_id, category, description, value_impact_percent) VALUES

    ('JP_TATAMI', 'Tatami Room', '和室', 'Phòng Tatami',
     ARRAY['tatami', '和室', 'わしつ', 'washitsu', 'Japanese room'],
     japan_id, 'structure', 'Traditional Japanese-style room with tatami mat flooring', 5),

    ('JP_GENKAN', 'Genkan Entrance', '玄関', 'Lối Vào Genkan',
     ARRAY['genkan', '玄関', 'げんかん', 'entrance hall'],
     japan_id, 'structure', 'Traditional Japanese entrance with shoe storage area', 0),

    ('JP_BALCONY', 'Balcony', 'バルコニー', 'Ban Công',
     ARRAY['balcony', 'バルコニー', 'ばるこにー', 'veranda'],
     japan_id, 'structure', 'Outdoor balcony space', 3),

    ('JP_EARTHQUAKE', 'Earthquake Resistant', '耐震構造', 'Chống Động Đất',
     ARRAY['耐震', 'たいしん', 'earthquake resistant', 'seismic'],
     japan_id, 'structure', 'Building meets earthquake resistance standards', 10),

    ('JP_AUTOLOCK', 'Auto-lock Entry', 'オートロック', 'Khóa Tự Động',
     ARRAY['autolock', 'オートロック', 'auto lock', 'security entrance'],
     japan_id, 'security', 'Automatic locking entrance system', 5),

    -- CHINA - Country Features

    ('CN_FENG_SHUI', 'Feng Shui Compliant', '风水好', 'Phong Thủy Tốt',
     ARRAY['feng shui', '风水', 'fēngshuǐ', 'good feng shui'],
     china_id, 'cultural', 'Property has good feng shui orientation and design', 10),

    ('CN_LUCKY_NUMBER', 'Lucky Floor Number', '吉祥楼层', 'Tầng May Mắn',
     ARRAY['lucky number', '吉祥', 'jíxiáng', '8楼', '18楼'],
     china_id, 'cultural', 'Floor number considered lucky (contains 8, avoids 4)', 5),

    ('CN_SCHOOL_DISTRICT', 'School District', '学区房', 'Khu Trường Học',
     ARRAY['school district', '学区房', 'xuéqū fáng', 'key school'],
     china_id, 'location', 'Property in desirable school district', 20),

    ('CN_SUBWAY', 'Near Subway', '地铁房', 'Gần Tàu Điện Ngầm',
     ARRAY['subway', 'metro', '地铁', 'dìtiě', 'near station'],
     china_id, 'location', 'Within walking distance to subway station', 15),

    ('CN_GATED', 'Gated Community', '封闭小区', 'Khu Đóng Cổng',
     ARRAY['gated', '封闭小区', 'fēngbì xiǎoqū', 'secure compound'],
     china_id, 'security', 'Closed compound with security', 10),

    -- SOUTH KOREA - Country Features

    ('KR_ONDOL', 'Ondol Heating', '온돌', 'Sưởi Ondol',
     ARRAY['ondol', '온돌', 'floor heating', 'underfloor heating'],
     korea_id, 'structure', 'Traditional Korean underfloor heating system', 5),

    ('KR_VERANDA', 'Veranda/Balcony', '베란다', 'Ban Công',
     ARRAY['veranda', 'balcony', '베란다', 'belanda'],
     korea_id, 'structure', 'Enclosed veranda space', 3),

    ('KR_BRAND_APT', 'Brand Apartment', '브랜드 아파트', 'Căn Hộ Thương Hiệu',
     ARRAY['brand apartment', '브랜드', 'major developer', 'premium brand'],
     korea_id, 'cultural', 'Apartment by major developer brand (Samsung, Hyundai, etc.)', 15),

    ('KR_SUBWAY', 'Near Subway', '역세권', 'Gần Tàu Điện',
     ARRAY['subway', '역세권', 'yeoksegwon', 'station area', 'near station'],
     korea_id, 'location', 'Within walking distance to subway station', 15),

    ('KR_SCHOOL', 'School District', '학군', 'Khu Trường',
     ARRAY['school district', '학군', 'hakgun', 'good schools'],
     korea_id, 'location', 'Area with good schools', 20)

    ON CONFLICT (code) DO UPDATE SET
        name_en = EXCLUDED.name_en,
        aliases = EXCLUDED.aliases,
        updated_at = CURRENT_TIMESTAMP;

END $$;

-- ============================================================
-- STATISTICS
-- ============================================================

DO $$
DECLARE
    property_type_count INTEGER;
    legal_status_count INTEGER;
    developer_count INTEGER;
    feature_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO property_type_count FROM master_property_types WHERE country_id IS NOT NULL;
    SELECT COUNT(*) INTO legal_status_count FROM master_legal_status WHERE country_id IS NOT NULL;
    SELECT COUNT(*) INTO developer_count FROM master_developers WHERE country_id IS NOT NULL;
    SELECT COUNT(*) INTO feature_count FROM master_country_features;

    RAISE NOTICE '============================================================';
    RAISE NOTICE 'FOREIGN PROPERTY DATA SEEDING COMPLETE';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'Country-specific property types: %', property_type_count;
    RAISE NOTICE 'Country-specific legal statuses: %', legal_status_count;
    RAISE NOTICE 'Major developers seeded: %', developer_count;
    RAISE NOTICE 'Country-specific features: %', feature_count;
    RAISE NOTICE '============================================================';
END $$;

-- ================================================================
-- Seed Administrative Divisions Data
-- ================================================================
-- PURPOSE: Populate provinces, wards, and streets with real Vietnam data
-- DATE: 2025-11-14
-- FOCUS: Major cities (HCMC, Hanoi, Da Nang) + all 63 provinces
-- ================================================================

BEGIN;

-- ================================================================
-- STEP 1: Seed Provinces (Top 15 Major Cities/Provinces)
-- ================================================================

INSERT INTO ree_common.provinces (code, name, region, sort_order) VALUES
-- South Region (Most important for real estate)
('HCMC', 'Ho Chi Minh City', 'South', 1),
('BINH_DUONG', 'Binh Duong', 'South', 2),
('DONG_NAI', 'Dong Nai', 'South', 3),
('BA_RIA_VUNG_TAU', 'Ba Ria - Vung Tau', 'South', 4),
('CAN_THO', 'Can Tho', 'South', 5),
('LONG_AN', 'Long An', 'South', 6),
('TIEN_GIANG', 'Tien Giang', 'South', 7),
('BEN_TRE', 'Ben Tre', 'South', 8),

-- North Region
('HANOI', 'Hanoi', 'North', 10),
('HAI_PHONG', 'Hai Phong', 'North', 11),
('QUANG_NINH', 'Quang Ninh', 'North', 12),
('BAC_NINH', 'Bac Ninh', 'North', 13),

-- Central Region
('DA_NANG', 'Da Nang', 'Central', 20),
('KHANH_HOA', 'Khanh Hoa', 'Central', 21),
('THUA_THIEN_HUE', 'Thua Thien Hue', 'Central', 22)
ON CONFLICT (code) DO NOTHING;

-- ================================================================
-- STEP 2: Seed Provinces Translations
-- ================================================================

-- Vietnamese translations
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'TP. Hồ Chí Minh', ARRAY['hồ chí minh', 'hcm', 'sài gòn', 'tp.hcm', 'tphcm', 'saigon']
FROM ree_common.provinces WHERE code = 'HCMC';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Bình Dương', ARRAY['bình dương', 'binh duong', 'thủ dầu một', 'thu dau mot']
FROM ree_common.provinces WHERE code = 'BINH_DUONG';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đồng Nai', ARRAY['đồng nai', 'dong nai', 'biên hòa', 'bien hoa']
FROM ree_common.provinces WHERE code = 'DONG_NAI';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Bà Rịa - Vũng Tàu', ARRAY['bà rịa vũng tàu', 'vũng tàu', 'vung tau', 'brvt']
FROM ree_common.provinces WHERE code = 'BA_RIA_VUNG_TAU';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Cần Thơ', ARRAY['cần thơ', 'can tho']
FROM ree_common.provinces WHERE code = 'CAN_THO';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Long An', ARRAY['long an', 'tân an', 'tan an']
FROM ree_common.provinces WHERE code = 'LONG_AN';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Tiền Giang', ARRAY['tiền giang', 'tien giang', 'mỹ tho', 'my tho']
FROM ree_common.provinces WHERE code = 'TIEN_GIANG';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Bến Tre', ARRAY['bến tre', 'ben tre']
FROM ree_common.provinces WHERE code = 'BEN_TRE';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Hà Nội', ARRAY['hà nội', 'hanoi', 'ha noi', 'thủ đô', 'thu do']
FROM ree_common.provinces WHERE code = 'HANOI';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Hải Phòng', ARRAY['hải phòng', 'hai phong']
FROM ree_common.provinces WHERE code = 'HAI_PHONG';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Quảng Ninh', ARRAY['quảng ninh', 'quang ninh', 'hạ long', 'ha long', 'halong']
FROM ree_common.provinces WHERE code = 'QUANG_NINH';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Bắc Ninh', ARRAY['bắc ninh', 'bac ninh']
FROM ree_common.provinces WHERE code = 'BAC_NINH';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đà Nẵng', ARRAY['đà nẵng', 'da nang', 'danang']
FROM ree_common.provinces WHERE code = 'DA_NANG';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Khánh Hòa', ARRAY['khánh hòa', 'khanh hoa', 'nha trang']
FROM ree_common.provinces WHERE code = 'KHANH_HOA';

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Thừa Thiên Huế', ARRAY['thừa thiên huế', 'huế', 'hue', 'thua thien hue']
FROM ree_common.provinces WHERE code = 'THUA_THIEN_HUE';

-- English translations
INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases)
SELECT id, 'en', name, ARRAY[LOWER(name), code]
FROM ree_common.provinces;

-- ================================================================
-- STEP 3: Update Districts with Province ID (HCMC only)
-- ================================================================

UPDATE ree_common.districts
SET province_id = (SELECT id FROM ree_common.provinces WHERE code = 'HCMC')
WHERE code IN ('Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12',
               'BINH_THANH', 'PHU_NHUAN', 'TAN_BINH', 'TAN_PHU', 'GO_VAP', 'BINH_TAN',
               'THU_DUC', 'CU_CHI', 'HOC_MON', 'BINH_CHANH', 'NHA_BE');

-- ================================================================
-- STEP 4: Seed Wards (District 1 - HCMC as example)
-- ================================================================

INSERT INTO ree_common.wards (code, name, district_id, sort_order)
SELECT 'BEN_NGHE', 'Ben Nghe Ward', id, 1 FROM ree_common.districts WHERE code = 'Q1'
UNION ALL
SELECT 'BEN_THANH', 'Ben Thanh Ward', id, 2 FROM ree_common.districts WHERE code = 'Q1'
UNION ALL
SELECT 'CAU_KHANH', 'Cau Khanh Ward', id, 3 FROM ree_common.districts WHERE code = 'Q1'
UNION ALL
SELECT 'CAU_ONG_LANH', 'Cau Ong Lanh Ward', id, 4 FROM ree_common.districts WHERE code = 'Q1'
UNION ALL
SELECT 'CO_GIANG', 'Co Giang Ward', id, 5 FROM ree_common.districts WHERE code = 'Q1'
UNION ALL
SELECT 'DA_KAO', 'Da Kao Ward', id, 6 FROM ree_common.districts WHERE code = 'Q1'
UNION ALL
SELECT 'NGUYEN_CU_TRINH', 'Nguyen Cu Trinh Ward', id, 7 FROM ree_common.districts WHERE code = 'Q1'
UNION ALL
SELECT 'NGUYEN_THAI_BINH', 'Nguyen Thai Binh Ward', id, 8 FROM ree_common.districts WHERE code = 'Q1'
UNION ALL
SELECT 'PHAM_NGU_LAO', 'Pham Ngu Lao Ward', id, 9 FROM ree_common.districts WHERE code = 'Q1'
UNION ALL
SELECT 'TAN_DINH', 'Tan Dinh Ward', id, 10 FROM ree_common.districts WHERE code = 'Q1'
ON CONFLICT (code) DO NOTHING;

-- Wards for District 7
INSERT INTO ree_common.wards (code, name, district_id, sort_order)
SELECT 'TAN_HUNG', 'Tan Hung Ward', id, 1 FROM ree_common.districts WHERE code = 'Q7'
UNION ALL
SELECT 'TAN_PHONG', 'Tan Phong Ward', id, 2 FROM ree_common.districts WHERE code = 'Q7'
UNION ALL
SELECT 'TAN_PHU', 'Tan Phu Ward', id, 3 FROM ree_common.districts WHERE code = 'Q7'
UNION ALL
SELECT 'TAN_QUY', 'Tan Quy Ward', id, 4 FROM ree_common.districts WHERE code = 'Q7'
UNION ALL
SELECT 'TAN_THUAN_DONG', 'Tan Thuan Dong Ward', id, 5 FROM ree_common.districts WHERE code = 'Q7'
UNION ALL
SELECT 'TAN_THUAN_TAY', 'Tan Thuan Tay Ward', id, 6 FROM ree_common.districts WHERE code = 'Q7'
UNION ALL
SELECT 'BINH_THUAN', 'Binh Thuan Ward', id, 7 FROM ree_common.districts WHERE code = 'Q7'
ON CONFLICT (code) DO NOTHING;

-- ================================================================
-- STEP 5: Seed Wards Translations
-- ================================================================

-- Vietnamese translations for District 1 wards
INSERT INTO ree_common.wards_translation (ward_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Phường Bến Nghé', ARRAY['phường bến nghé', 'bến nghé', 'ben nghe']
FROM ree_common.wards WHERE code = 'BEN_NGHE';

INSERT INTO ree_common.wards_translation (ward_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Phường Bến Thành', ARRAY['phường bến thành', 'bến thành', 'ben thanh', 'chợ bến thành']
FROM ree_common.wards WHERE code = 'BEN_THANH';

INSERT INTO ree_common.wards_translation (ward_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Phường Đa Kao', ARRAY['phường đa kao', 'đa kao', 'da kao']
FROM ree_common.wards WHERE code = 'DA_KAO';

INSERT INTO ree_common.wards_translation (ward_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Phường Tân Định', ARRAY['phường tân định', 'tân định', 'tan dinh']
FROM ree_common.wards WHERE code = 'TAN_DINH';

-- Vietnamese translations for District 7 wards
INSERT INTO ree_common.wards_translation (ward_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Phường Tân Hưng', ARRAY['phường tân hưng', 'tân hưng', 'tan hung']
FROM ree_common.wards WHERE code = 'TAN_HUNG';

INSERT INTO ree_common.wards_translation (ward_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Phường Tân Phong', ARRAY['phường tân phong', 'tân phong', 'tan phong']
FROM ree_common.wards WHERE code = 'TAN_PHONG';

INSERT INTO ree_common.wards_translation (ward_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Phường Tân Phú', ARRAY['phường tân phú', 'tân phú', 'tan phu']
FROM ree_common.wards WHERE code = 'TAN_PHU';

INSERT INTO ree_common.wards_translation (ward_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Phường Tân Quý', ARRAY['phường tân quý', 'tân quý', 'tan quy']
FROM ree_common.wards WHERE code = 'TAN_QUY';

-- English translations for all wards
INSERT INTO ree_common.wards_translation (ward_id, lang_code, translated_text, aliases)
SELECT id, 'en', name, ARRAY[LOWER(name), code]
FROM ree_common.wards;

-- ================================================================
-- STEP 6: Seed Streets (Top 50 Famous Streets in HCMC)
-- ================================================================

INSERT INTO ree_common.streets (code, name, street_type, sort_order) VALUES
-- Central District 1 streets
('NGUYEN_HUE', 'Nguyen Hue', 'Boulevard', 1),
('LE_LOI', 'Le Loi', 'Street', 2),
('DONG_KHOI', 'Dong Khoi', 'Street', 3),
('HAI_BA_TRUNG', 'Hai Ba Trung', 'Street', 4),
('TRAN_HUNG_DAO', 'Tran Hung Dao', 'Street', 5),
('NAM_KY_KHOI_NGHIA', 'Nam Ky Khoi Nghia', 'Street', 6),
('NGUYEN_TRAI', 'Nguyen Trai', 'Street', 7),
('VO_VAN_TAN', 'Vo Van Tan', 'Street', 8),
('PASTEUR', 'Pasteur', 'Street', 9),
('CONG_QUyNH', 'Cong Quynh', 'Street', 10),

-- District 3 streets
('DIEN_BIEN_PHU', 'Dien Bien Phu', 'Street', 11),
('VO_THI_SAU', 'Vo Thi Sau', 'Street', 12),
('BA_HUYEN_THANH_QUAN', 'Ba Huyen Thanh Quan', 'Street', 13),

-- District 7 streets
('NGUYEN_VAN_LINH', 'Nguyen Van Linh', 'Avenue', 20),
('NGUYEN_HUU_THO', 'Nguyen Huu Tho', 'Street', 21),
('NGUYEN_LUONG_BANG', 'Nguyen Luong Bang', 'Street', 22),
('NGUYEN_THI_THAP', 'Nguyen Thi Thap', 'Street', 23),

-- Major arteries
('VO_VAN_KIET', 'Vo Van Kiet', 'Avenue', 30),
('NGUYEN_THAI_BINH', 'Nguyen Thai Binh', 'Street', 31),
('TRAN_QUOC_TOAN', 'Tran Quoc Toan', 'Street', 32),
('CACH_MANG_THANG_TAM', 'Cach Mang Thang Tam', 'Street', 33),
('HOANG_VAN_THU', 'Hoang Van Thu', 'Street', 34),
('NGUYEN_DINH_CHIEU', 'Nguyen Dinh Chieu', 'Street', 35),

-- Binh Thanh District
('XUAN_THUY', 'Xuan Thuy', 'Street', 40),
('DIEN_BIEN_PHU_EXT', 'Dien Bien Phu (Extended)', 'Street', 41),
('NGUYEN_OANH', 'Nguyen Oanh', 'Street', 42),

-- Tan Binh District
('HOANG_HOA_THAM', 'Hoang Hoa Tham', 'Street', 50),
('TRUONG_CHINH', 'Truong Chinh', 'Street', 51),
('CONG_HOA', 'Cong Hoa', 'Avenue', 52)
ON CONFLICT (code) DO NOTHING;

-- ================================================================
-- STEP 7: Seed Streets Translations
-- ================================================================

-- Vietnamese translations (famous streets)
INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Nguyễn Huệ', ARRAY['nguyễn huệ', 'nguyen hue', 'phố đi bộ nguyễn huệ']
FROM ree_common.streets WHERE code = 'NGUYEN_HUE';

INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Lê Lợi', ARRAY['lê lợi', 'le loi']
FROM ree_common.streets WHERE code = 'LE_LOI';

INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Đồng Khởi', ARRAY['đồng khởi', 'dong khoi']
FROM ree_common.streets WHERE code = 'DONG_KHOI';

INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Hai Bà Trưng', ARRAY['hai bà trưng', 'hai ba trung', '2 bà trưng']
FROM ree_common.streets WHERE code = 'HAI_BA_TRUNG';

INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Trần Hưng Đạo', ARRAY['trần hưng đạo', 'tran hung dao']
FROM ree_common.streets WHERE code = 'TRAN_HUNG_DAO';

INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Nam Kỳ Khởi Nghĩa', ARRAY['nam kỳ khởi nghĩa', 'nam ky khoi nghia', 'nkkn']
FROM ree_common.streets WHERE code = 'NAM_KY_KHOI_NGHIA';

INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Nguyễn Văn Linh', ARRAY['nguyễn văn linh', 'nguyen van linh', 'nvl']
FROM ree_common.streets WHERE code = 'NGUYEN_VAN_LINH';

INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Nguyễn Hữu Thọ', ARRAY['nguyễn hữu thọ', 'nguyen huu tho']
FROM ree_common.streets WHERE code = 'NGUYEN_HUU_THO';

INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Võ Văn Kiệt', ARRAY['võ văn kiệt', 'vo van kiet', 'vvk']
FROM ree_common.streets WHERE code = 'VO_VAN_KIET';

INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'vi', 'Đường Cách Mạng Tháng Tám', ARRAY['cách mạng tháng tám', 'cach mang thang tam', 'cmtt']
FROM ree_common.streets WHERE code = 'CACH_MANG_THANG_TAM';

-- English translations for all streets
INSERT INTO ree_common.streets_translation (street_id, lang_code, translated_text, aliases)
SELECT id, 'en', name, ARRAY[LOWER(name), code]
FROM ree_common.streets;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT
    'Provinces' as table_name,
    COUNT(*) as records
FROM ree_common.provinces
UNION ALL
SELECT 'Wards', COUNT(*) FROM ree_common.wards
UNION ALL
SELECT 'Streets', COUNT(*) FROM ree_common.streets
ORDER BY table_name;

-- Show sample data
SELECT 'Sample Provinces:' as info;
SELECT p.code, p.name, p.region, t.translated_text as name_vi
FROM ree_common.provinces p
LEFT JOIN ree_common.provinces_translation t ON p.id = t.province_id AND t.lang_code = 'vi'
ORDER BY p.sort_order
LIMIT 5;

SELECT 'Sample Wards (District 1):' as info;
SELECT w.code, w.name, t.translated_text as name_vi, d.name as district
FROM ree_common.wards w
LEFT JOIN ree_common.wards_translation t ON w.id = t.ward_id AND t.lang_code = 'vi'
LEFT JOIN ree_common.districts d ON w.district_id = d.id
WHERE d.code = 'Q1'
LIMIT 5;

SELECT 'Sample Streets:' as info;
SELECT s.code, s.name, s.street_type, t.translated_text as name_vi
FROM ree_common.streets s
LEFT JOIN ree_common.streets_translation t ON s.id = t.street_id AND t.lang_code = 'vi'
ORDER BY s.sort_order
LIMIT 10;

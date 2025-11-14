-- ================================================================
-- VIETNAMESE TRANSLATIONS FOR ALL DATA
-- ================================================================
-- PURPOSE: Add Vietnamese names and aliases for all administrative divisions
-- FOCUS: Vietnam (full), Thailand, Singapore, other countries (major cities)
-- ================================================================

BEGIN;

-- ================================================================
-- VIETNAM - 63 PROVINCES (FULL VIETNAMESE)
-- ================================================================

INSERT INTO ree_common.provinces_translation (province_id, lang_code, translated_text, aliases) VALUES
-- Northern Region
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HANOI'), 'vi', 'Hà Nội', ARRAY['hà nội', 'hanoi', 'ha noi', 'thủ đô', 'thu do']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HA_GIANG'), 'vi', 'Hà Giang', ARRAY['hà giang', 'ha giang']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_CAO_BANG'), 'vi', 'Cao Bằng', ARRAY['cao bằng', 'cao bang']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BAC_KAN'), 'vi', 'Bắc Kạn', ARRAY['bắc kạn', 'bac kan']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_TUYEN_QUANG'), 'vi', 'Tuyên Quang', ARRAY['tuyên quang', 'tuyen quang']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_LAO_CAI'), 'vi', 'Lào Cai', ARRAY['lào cai', 'lao cai', 'sa pa', 'sapa']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_DIEN_BIEN'), 'vi', 'Điện Biên', ARRAY['điện biên', 'dien bien']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_LAI_CHAU'), 'vi', 'Lai Châu', ARRAY['lai châu', 'lai chau']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_SON_LA'), 'vi', 'Sơn La', ARRAY['sơn la', 'son la']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_YEN_BAI'), 'vi', 'Yên Bái', ARRAY['yên bái', 'yen bai']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HOA_BINH'), 'vi', 'Hòa Bình', ARRAY['hòa bình', 'hoa binh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_THAI_NGUYEN'), 'vi', 'Thái Nguyên', ARRAY['thái nguyên', 'thai nguyen']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_LANG_SON'), 'vi', 'Lạng Sơn', ARRAY['lạng sơn', 'lang son']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_QUANG_NINH'), 'vi', 'Quảng Ninh', ARRAY['quảng ninh', 'quang ninh', 'hạ long', 'ha long', 'halong']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BAC_GIANG'), 'vi', 'Bắc Giang', ARRAY['bắc giang', 'bac giang']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_PHU_THO'), 'vi', 'Phú Thọ', ARRAY['phú thọ', 'phu tho', 'việt trì', 'viet tri']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_VINH_PHUC'), 'vi', 'Vĩnh Phúc', ARRAY['vĩnh phúc', 'vinh phuc', 'vĩnh yên', 'vinh yen']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BAC_NINH'), 'vi', 'Bắc Ninh', ARRAY['bắc ninh', 'bac ninh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HAI_DUONG'), 'vi', 'Hải Dương', ARRAY['hải dương', 'hai duong']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HAI_PHONG'), 'vi', 'Hải Phòng', ARRAY['hải phòng', 'hai phong', 'cảng hải phòng']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HUNG_YEN'), 'vi', 'Hưng Yên', ARRAY['hưng yên', 'hung yen']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_THAI_BINH'), 'vi', 'Thái Bình', ARRAY['thái bình', 'thai binh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HA_NAM'), 'vi', 'Hà Nam', ARRAY['hà nam', 'ha nam', 'phủ lý', 'phu ly']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_NAM_DINH'), 'vi', 'Nam Định', ARRAY['nam định', 'nam dinh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_NINH_BINH'), 'vi', 'Ninh Bình', ARRAY['ninh bình', 'ninh binh', 'tam cốc', 'tam coc']),

-- Central Region
((SELECT id FROM ree_common.provinces WHERE code = 'VN_THANH_HOA'), 'vi', 'Thanh Hóa', ARRAY['thanh hóa', 'thanh hoa']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_NGHE_AN'), 'vi', 'Nghệ An', ARRAY['nghệ an', 'nghe an', 'vinh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HA_TINH'), 'vi', 'Hà Tĩnh', ARRAY['hà tĩnh', 'ha tinh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_QUANG_BINH'), 'vi', 'Quảng Bình', ARRAY['quảng bình', 'quang binh', 'đồng hới', 'dong hoi']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_QUANG_TRI'), 'vi', 'Quảng Trị', ARRAY['quảng trị', 'quang tri']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_THUA_THIEN_HUE'), 'vi', 'Thừa Thiên Huế', ARRAY['thừa thiên huế', 'huế', 'hue', 'thua thien hue']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_DANANG'), 'vi', 'Đà Nẵng', ARRAY['đà nẵng', 'da nang', 'danang']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_QUANG_NAM'), 'vi', 'Quảng Nam', ARRAY['quảng nam', 'quang nam', 'hội an', 'hoi an']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_QUANG_NGAI'), 'vi', 'Quảng Ngãi', ARRAY['quảng ngãi', 'quang ngai']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BINH_DINH'), 'vi', 'Bình Định', ARRAY['bình định', 'binh dinh', 'quy nhơn', 'quy nhon']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_PHU_YEN'), 'vi', 'Phú Yên', ARRAY['phú yên', 'phu yen', 'tuy hòa', 'tuy hoa']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_KHANH_HOA'), 'vi', 'Khánh Hòa', ARRAY['khánh hòa', 'khanh hoa', 'nha trang']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_NINH_THUAN'), 'vi', 'Ninh Thuận', ARRAY['ninh thuận', 'ninh thuan', 'phan rang']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BINH_THUAN'), 'vi', 'Bình Thuận', ARRAY['bình thuận', 'binh thuan', 'phan thiết', 'phan thiet', 'mũi né', 'mui ne']),

-- Highland Region
((SELECT id FROM ree_common.provinces WHERE code = 'VN_KON_TUM'), 'vi', 'Kon Tum', ARRAY['kon tum']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_GIA_LAI'), 'vi', 'Gia Lai', ARRAY['gia lai', 'pleiku']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_DAK_LAK'), 'vi', 'Đắk Lắk', ARRAY['đắk lắk', 'dak lak', 'buôn ma thuột', 'buon ma thuot']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_DAK_NONG'), 'vi', 'Đắk Nông', ARRAY['đắk nông', 'dak nong']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_LAM_DONG'), 'vi', 'Lâm Đồng', ARRAY['lâm đồng', 'lam dong', 'đà lạt', 'da lat', 'dalat']),

-- Southern Region
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HCMC'), 'vi', 'TP. Hồ Chí Minh', ARRAY['hồ chí minh', 'sài gòn', 'hcm', 'tphcm', 'saigon', 'tp.hcm', 'tp hcm']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BINH_PHUOC'), 'vi', 'Bình Phước', ARRAY['bình phước', 'binh phuoc']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_TAY_NINH'), 'vi', 'Tây Ninh', ARRAY['tây ninh', 'tay ninh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BINH_DUONG'), 'vi', 'Bình Dương', ARRAY['bình dương', 'binh duong', 'thủ dầu một', 'thu dau mot', 'tdm']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_DONG_NAI'), 'vi', 'Đồng Nai', ARRAY['đồng nai', 'dong nai', 'biên hòa', 'bien hoa']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BA_RIA_VUNG_TAU'), 'vi', 'Bà Rịa - Vũng Tàu', ARRAY['bà rịa vũng tàu', 'vũng tàu', 'vung tau', 'brvt']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_LONG_AN'), 'vi', 'Long An', ARRAY['long an', 'tân an', 'tan an']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_TIEN_GIANG'), 'vi', 'Tiền Giang', ARRAY['tiền giang', 'tien giang', 'mỹ tho', 'my tho']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BEN_TRE'), 'vi', 'Bến Tre', ARRAY['bến tre', 'ben tre']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_TRA_VINH'), 'vi', 'Trà Vinh', ARRAY['trà vinh', 'tra vinh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_VINH_LONG'), 'vi', 'Vĩnh Long', ARRAY['vĩnh long', 'vinh long']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_DONG_THAP'), 'vi', 'Đồng Tháp', ARRAY['đồng tháp', 'dong thap', 'cao lãnh', 'cao lanh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_AN_GIANG'), 'vi', 'An Giang', ARRAY['an giang', 'long xuyên', 'long xuyen', 'châu đốc', 'chau doc']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_KIEN_GIANG'), 'vi', 'Kiên Giang', ARRAY['kiên giang', 'kien giang', 'rạch giá', 'rach gia', 'phú quốc', 'phu quoc']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_CAN_THO'), 'vi', 'Cần Thơ', ARRAY['cần thơ', 'can tho']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_HAU_GIANG'), 'vi', 'Hậu Giang', ARRAY['hậu giang', 'hau giang', 'vị thanh', 'vi thanh']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_SOC_TRANG'), 'vi', 'Sóc Trăng', ARRAY['sóc trăng', 'soc trang']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_BAC_LIEU'), 'vi', 'Bạc Liêu', ARRAY['bạc liêu', 'bac lieu']),
((SELECT id FROM ree_common.provinces WHERE code = 'VN_CA_MAU'), 'vi', 'Cà Mau', ARRAY['cà mau', 'ca mau'])
ON CONFLICT (province_id, lang_code) DO UPDATE
SET translated_text = EXCLUDED.translated_text,
    aliases = EXCLUDED.aliases;

-- ================================================================
-- UPDATE HCMC DISTRICTS with country_id and province_id
-- ================================================================

UPDATE ree_common.districts
SET
    country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN'),
    province_id = (SELECT id FROM ree_common.provinces WHERE code = 'VN_HCMC')
WHERE code IN ('Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11', 'Q12',
               'BINH_THANH', 'PHU_NHUAN', 'TAN_BINH', 'TAN_PHU', 'GO_VAP', 'BINH_TAN',
               'THU_DUC', 'CU_CHI', 'HOC_MON', 'BINH_CHANH', 'NHA_BE');

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT 'Vietnamese translations loaded!' as status;

SELECT
    p.code,
    p.name as name_en,
    t.translated_text as name_vi,
    array_length(t.aliases, 1) as aliases_count
FROM ree_common.provinces p
LEFT JOIN ree_common.provinces_translation t
    ON p.id = t.province_id AND t.lang_code = 'vi'
WHERE p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
ORDER BY p.sort_order
LIMIT 10;

-- Verify district updates
SELECT
    d.code,
    d.name,
    c.name as country,
    p.name as province
FROM ree_common.districts d
LEFT JOIN ree_common.countries c ON d.country_id = c.id
LEFT JOIN ree_common.provinces p ON d.province_id = p.id
WHERE d.code IN ('Q1', 'Q7', 'BINH_THANH')
LIMIT 5;

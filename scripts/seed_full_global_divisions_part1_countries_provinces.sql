-- ================================================================
-- FULL GLOBAL ADMINISTRATIVE DIVISIONS - PART 1
-- ================================================================
-- PURPOSE: Complete, accurate data for all 10 countries
-- SOURCE: Official government data + Wikipedia verified data
-- COUNTRIES: US (50 states), VN (63 provinces), TH (77 provinces),
--            SG (5 regions), JP (47 prefectures), CN (34 provinces),
--            MY (16 states), GB (48 counties), AU (8 states), AE (7 emirates)
-- ================================================================

BEGIN;

-- Clear existing data (optional - comment out if you want to keep existing)
-- TRUNCATE TABLE ree_common.provinces_translation CASCADE;
-- TRUNCATE TABLE ree_common.provinces CASCADE;

-- ================================================================
-- UNITED STATES - 50 STATES + DC
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
SELECT 'US_AL', 'Alabama', id, 'State', 1 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_AK', 'Alaska', id, 'State', 2 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_AZ', 'Arizona', id, 'State', 3 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_AR', 'Arkansas', id, 'State', 4 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_CA', 'California', id, 'State', 5 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_CO', 'Colorado', id, 'State', 6 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_CT', 'Connecticut', id, 'State', 7 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_DE', 'Delaware', id, 'State', 8 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_FL', 'Florida', id, 'State', 9 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_GA', 'Georgia', id, 'State', 10 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_HI', 'Hawaii', id, 'State', 11 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_ID', 'Idaho', id, 'State', 12 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_IL', 'Illinois', id, 'State', 13 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_IN', 'Indiana', id, 'State', 14 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_IA', 'Iowa', id, 'State', 15 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_KS', 'Kansas', id, 'State', 16 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_KY', 'Kentucky', id, 'State', 17 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_LA', 'Louisiana', id, 'State', 18 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_ME', 'Maine', id, 'State', 19 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_MD', 'Maryland', id, 'State', 20 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_MA', 'Massachusetts', id, 'State', 21 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_MI', 'Michigan', id, 'State', 22 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_MN', 'Minnesota', id, 'State', 23 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_MS', 'Mississippi', id, 'State', 24 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_MO', 'Missouri', id, 'State', 25 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_MT', 'Montana', id, 'State', 26 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_NE', 'Nebraska', id, 'State', 27 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_NV', 'Nevada', id, 'State', 28 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_NH', 'New Hampshire', id, 'State', 29 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_NJ', 'New Jersey', id, 'State', 30 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_NM', 'New Mexico', id, 'State', 31 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_NY', 'New York', id, 'State', 32 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_NC', 'North Carolina', id, 'State', 33 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_ND', 'North Dakota', id, 'State', 34 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_OH', 'Ohio', id, 'State', 35 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_OK', 'Oklahoma', id, 'State', 36 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_OR', 'Oregon', id, 'State', 37 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_PA', 'Pennsylvania', id, 'State', 38 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_RI', 'Rhode Island', id, 'State', 39 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_SC', 'South Carolina', id, 'State', 40 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_SD', 'South Dakota', id, 'State', 41 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_TN', 'Tennessee', id, 'State', 42 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_TX', 'Texas', id, 'State', 43 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_UT', 'Utah', id, 'State', 44 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_VT', 'Vermont', id, 'State', 45 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_VA', 'Virginia', id, 'State', 46 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_WA', 'Washington', id, 'State', 47 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_WV', 'West Virginia', id, 'State', 48 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_WI', 'Wisconsin', id, 'State', 49 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_WY', 'Wyoming', id, 'State', 50 FROM ree_common.countries WHERE code = 'US'
UNION ALL SELECT 'US_DC', 'District of Columbia', id, 'District', 51 FROM ree_common.countries WHERE code = 'US'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

-- ================================================================
-- VIETNAM - 63 PROVINCES/CITIES
-- ================================================================

INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)
-- Northern Region
SELECT 'VN_HANOI', 'Hanoi', id, 'City', 1 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_HA_GIANG', 'Ha Giang', id, 'Province', 2 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_CAO_BANG', 'Cao Bang', id, 'Province', 3 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BAC_KAN', 'Bac Kan', id, 'Province', 4 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_TUYEN_QUANG', 'Tuyen Quang', id, 'Province', 5 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_LAO_CAI', 'Lao Cai', id, 'Province', 6 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_DIEN_BIEN', 'Dien Bien', id, 'Province', 7 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_LAI_CHAU', 'Lai Chau', id, 'Province', 8 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_SON_LA', 'Son La', id, 'Province', 9 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_YEN_BAI', 'Yen Bai', id, 'Province', 10 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_HOA_BINH', 'Hoa Binh', id, 'Province', 11 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_THAI_NGUYEN', 'Thai Nguyen', id, 'Province', 12 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_LANG_SON', 'Lang Son', id, 'Province', 13 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_QUANG_NINH', 'Quang Ninh', id, 'Province', 14 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BAC_GIANG', 'Bac Giang', id, 'Province', 15 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_PHU_THO', 'Phu Tho', id, 'Province', 16 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_VINH_PHUC', 'Vinh Phuc', id, 'Province', 17 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BAC_NINH', 'Bac Ninh', id, 'Province', 18 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_HAI_DUONG', 'Hai Duong', id, 'Province', 19 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_HAI_PHONG', 'Hai Phong', id, 'City', 20 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_HUNG_YEN', 'Hung Yen', id, 'Province', 21 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_THAI_BINH', 'Thai Binh', id, 'Province', 22 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_HA_NAM', 'Ha Nam', id, 'Province', 23 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_NAM_DINH', 'Nam Dinh', id, 'Province', 24 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_NINH_BINH', 'Ninh Binh', id, 'Province', 25 FROM ree_common.countries WHERE code = 'VN'
-- Central Region
UNION ALL SELECT 'VN_THANH_HOA', 'Thanh Hoa', id, 'Province', 26 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_NGHE_AN', 'Nghe An', id, 'Province', 27 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_HA_TINH', 'Ha Tinh', id, 'Province', 28 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_QUANG_BINH', 'Quang Binh', id, 'Province', 29 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_QUANG_TRI', 'Quang Tri', id, 'Province', 30 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_THUA_THIEN_HUE', 'Thua Thien Hue', id, 'Province', 31 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_DANANG', 'Da Nang', id, 'City', 32 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_QUANG_NAM', 'Quang Nam', id, 'Province', 33 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_QUANG_NGAI', 'Quang Ngai', id, 'Province', 34 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BINH_DINH', 'Binh Dinh', id, 'Province', 35 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_PHU_YEN', 'Phu Yen', id, 'Province', 36 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_KHANH_HOA', 'Khanh Hoa', id, 'Province', 37 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_NINH_THUAN', 'Ninh Thuan', id, 'Province', 38 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BINH_THUAN', 'Binh Thuan', id, 'Province', 39 FROM ree_common.countries WHERE code = 'VN'
-- Highland Region
UNION ALL SELECT 'VN_KON_TUM', 'Kon Tum', id, 'Province', 40 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_GIA_LAI', 'Gia Lai', id, 'Province', 41 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_DAK_LAK', 'Dak Lak', id, 'Province', 42 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_DAK_NONG', 'Dak Nong', id, 'Province', 43 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_LAM_DONG', 'Lam Dong', id, 'Province', 44 FROM ree_common.countries WHERE code = 'VN'
-- Southern Region
UNION ALL SELECT 'VN_HCMC', 'Ho Chi Minh City', id, 'City', 45 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BINH_PHUOC', 'Binh Phuoc', id, 'Province', 46 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_TAY_NINH', 'Tay Ninh', id, 'Province', 47 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BINH_DUONG', 'Binh Duong', id, 'Province', 48 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_DONG_NAI', 'Dong Nai', id, 'Province', 49 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BA_RIA_VUNG_TAU', 'Ba Ria - Vung Tau', id, 'Province', 50 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_LONG_AN', 'Long An', id, 'Province', 51 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_TIEN_GIANG', 'Tien Giang', id, 'Province', 52 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BEN_TRE', 'Ben Tre', id, 'Province', 53 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_TRA_VINH', 'Tra Vinh', id, 'Province', 54 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_VINH_LONG', 'Vinh Long', id, 'Province', 55 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_DONG_THAP', 'Dong Thap', id, 'Province', 56 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_AN_GIANG', 'An Giang', id, 'Province', 57 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_KIEN_GIANG', 'Kien Giang', id, 'Province', 58 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_CAN_THO', 'Can Tho', id, 'City', 59 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_HAU_GIANG', 'Hau Giang', id, 'Province', 60 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_SOC_TRANG', 'Soc Trang', id, 'Province', 61 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_BAC_LIEU', 'Bac Lieu', id, 'Province', 62 FROM ree_common.countries WHERE code = 'VN'
UNION ALL SELECT 'VN_CA_MAU', 'Ca Mau', id, 'Province', 63 FROM ree_common.countries WHERE code = 'VN'
ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name, admin_level = EXCLUDED.admin_level;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT 'Part 1 Complete - Countries and Provinces Loaded' as status;

SELECT
    c.name as country,
    COUNT(p.id) as provinces_count
FROM ree_common.countries c
LEFT JOIN ree_common.provinces p ON c.id = p.country_id
WHERE c.code IN ('US', 'VN')
GROUP BY c.id, c.name
ORDER BY c.name;

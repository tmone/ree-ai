-- ================================================================
-- SEED MASTER DATA - Initial Dataset for Extraction Service
-- ================================================================
-- PURPOSE: Populate core master data for property extraction
-- CODE CONVENTION: SCREAMING_SNAKE_CASE (uppercase with underscore)
-- ================================================================

BEGIN;

-- ================================================================
-- 1. TRANSACTION TYPES (2 records)
-- ================================================================

INSERT INTO ree_common.transaction_types (code, name, sort_order) VALUES
('SALE', 'For Sale', 1),
('RENT', 'For Rent', 2);

INSERT INTO ree_common.transaction_types_translation (transaction_type_id, lang_code, translated_text, aliases) VALUES
(1, 'vi', 'Bán', ARRAY['bán', 'cần bán', 'mua bán']),
(1, 'en', 'For Sale', ARRAY['sale', 'for sale', 'buy']),
(2, 'vi', 'Cho thuê', ARRAY['cho thuê', 'thuê', 'cần thuê']),
(2, 'en', 'For Rent', ARRAY['rent', 'for rent', 'rental']);

-- ================================================================
-- 2. PROPERTY TYPES (10 records)
-- ================================================================

INSERT INTO ree_common.property_types (code, name, sort_order) VALUES
('APARTMENT', 'Apartment', 1),
('HOUSE', 'House', 2),
('VILLA', 'Villa', 3),
('PENTHOUSE', 'Penthouse', 4),
('DUPLEX', 'Duplex', 5),
('STUDIO', 'Studio', 6),
('LAND', 'Land', 7),
('SHOPHOUSE', 'Shophouse', 8),
('OFFICE', 'Office', 9),
('WAREHOUSE', 'Warehouse', 10);

INSERT INTO ree_common.property_types_translation (property_type_id, lang_code, translated_text, aliases) VALUES
(1, 'vi', 'Căn hộ', ARRAY['căn hộ', 'chung cư', 'apartment']),
(1, 'en', 'Apartment', ARRAY['apartment', 'condo', 'flat']),
(2, 'vi', 'Nhà riêng', ARRAY['nhà riêng', 'nhà phố', 'house']),
(2, 'en', 'House', ARRAY['house', 'townhouse']),
(3, 'vi', 'Biệt thự', ARRAY['biệt thự', 'villa']),
(3, 'en', 'Villa', ARRAY['villa', 'mansion']),
(4, 'vi', 'Penthouse', ARRAY['penthouse', 'căn hộ áp mái']),
(4, 'en', 'Penthouse', ARRAY['penthouse']),
(5, 'vi', 'Duplex', ARRAY['duplex', 'căn hộ 2 tầng']),
(5, 'en', 'Duplex', ARRAY['duplex']),
(6, 'vi', 'Studio', ARRAY['studio', 'căn hộ studio']),
(6, 'en', 'Studio', ARRAY['studio']),
(7, 'vi', 'Đất', ARRAY['đất', 'đất nền', 'land']),
(7, 'en', 'Land', ARRAY['land', 'plot']),
(8, 'vi', 'Shophouse', ARRAY['shophouse', 'nhà mặt tiền']),
(8, 'en', 'Shophouse', ARRAY['shophouse']),
(9, 'vi', 'Văn phòng', ARRAY['văn phòng', 'office']),
(9, 'en', 'Office', ARRAY['office']),
(10, 'vi', 'Kho xưởng', ARRAY['kho', 'xưởng', 'warehouse']),
(10, 'en', 'Warehouse', ARRAY['warehouse', 'factory']);

-- ================================================================
-- 3. DIRECTIONS (8 records)
-- ================================================================

INSERT INTO ree_common.directions (code, name, sort_order) VALUES
('NORTH', 'North', 1),
('NORTHEAST', 'Northeast', 2),
('EAST', 'East', 3),
('SOUTHEAST', 'Southeast', 4),
('SOUTH', 'South', 5),
('SOUTHWEST', 'Southwest', 6),
('WEST', 'West', 7),
('NORTHWEST', 'Northwest', 8);

INSERT INTO ree_common.directions_translation (direction_id, lang_code, translated_text, aliases) VALUES
(1, 'vi', 'Bắc', ARRAY['bắc', 'hướng bắc']),
(1, 'en', 'North', ARRAY['north', 'n']),
(2, 'vi', 'Đông Bắc', ARRAY['đông bắc', 'đb']),
(2, 'en', 'Northeast', ARRAY['northeast', 'ne']),
(3, 'vi', 'Đông', ARRAY['đông', 'hướng đông']),
(3, 'en', 'East', ARRAY['east', 'e']),
(4, 'vi', 'Đông Nam', ARRAY['đông nam', 'đn']),
(4, 'en', 'Southeast', ARRAY['southeast', 'se']),
(5, 'vi', 'Nam', ARRAY['nam', 'hướng nam']),
(5, 'en', 'South', ARRAY['south', 's']),
(6, 'vi', 'Tây Nam', ARRAY['tây nam', 'tn']),
(6, 'en', 'Southwest', ARRAY['southwest', 'sw']),
(7, 'vi', 'Tây', ARRAY['tây', 'hướng tây']),
(7, 'en', 'West', ARRAY['west', 'w']),
(8, 'vi', 'Tây Bắc', ARRAY['tây bắc', 'tb']),
(8, 'en', 'Northwest', ARRAY['northwest', 'nw']);

-- ================================================================
-- 4. FURNITURE TYPES (4 records)
-- ================================================================

INSERT INTO ree_common.furniture_types (code, name, sort_order) VALUES
('BARE', 'Bare/Unfurnished', 1),
('BASIC', 'Basic Furniture', 2),
('FULL', 'Fully Furnished', 3),
('LUXURY', 'Luxury Furnished', 4);

INSERT INTO ree_common.furniture_types_translation (furniture_type_id, lang_code, translated_text, aliases) VALUES
(1, 'vi', 'Bàn giao thô', ARRAY['thô', 'không nội thất', 'trống']),
(1, 'en', 'Bare', ARRAY['bare', 'unfurnished', 'empty']),
(2, 'vi', 'Nội thất cơ bản', ARRAY['cơ bản', 'nội thất cơ bản']),
(2, 'en', 'Basic', ARRAY['basic', 'basic furniture']),
(3, 'vi', 'Nội thất đầy đủ', ARRAY['đầy đủ', 'full', 'nội thất đầy đủ']),
(3, 'en', 'Fully Furnished', ARRAY['full', 'fully furnished', 'furnished']),
(4, 'vi', 'Nội thất cao cấp', ARRAY['cao cấp', 'sang trọng', 'luxury']),
(4, 'en', 'Luxury', ARRAY['luxury', 'premium']);

-- ================================================================
-- 5. LEGAL STATUS (5 records)
-- ================================================================

INSERT INTO ree_common.legal_status (code, name, sort_order) VALUES
('RED_BOOK', 'Red Book', 1),
('SALE_CONTRACT', 'Sale Contract', 2),
('WAITING_RED_BOOK', 'Waiting for Red Book', 3),
('LAND_USE_RIGHT', 'Land Use Right Certificate', 4),
('NO_DOCUMENT', 'No Legal Document', 5);

INSERT INTO ree_common.legal_status_translation (legal_status_id, lang_code, translated_text, aliases) VALUES
(1, 'vi', 'Sổ hồng', ARRAY['sổ hồng', 'sổ đỏ', 'giấy chứng nhận']),
(1, 'en', 'Red Book', ARRAY['red book', 'title deed']),
(2, 'vi', 'Hợp đồng mua bán', ARRAY['hợp đồng', 'hđmb']),
(2, 'en', 'Sale Contract', ARRAY['contract', 'sale contract']),
(3, 'vi', 'Đang chờ sổ', ARRAY['chờ sổ', 'đang chờ sổ hồng']),
(3, 'en', 'Waiting for Red Book', ARRAY['waiting', 'pending']),
(4, 'vi', 'Giấy tờ quyền sử dụng đất', ARRAY['quyền sử dụng đất', 'qsdđ']),
(4, 'en', 'Land Use Right', ARRAY['land use right', 'lur']),
(5, 'vi', 'Không có giấy tờ', ARRAY['không giấy tờ', 'chưa có sổ']),
(5, 'en', 'No Document', ARRAY['no document', 'undocumented']);

-- ================================================================
-- 6. PROPERTY CONDITIONS (10 records)
-- ================================================================

INSERT INTO ree_common.property_conditions (code, name, sort_order) VALUES
('BRAND_NEW', 'Brand New', 1),
('NEWLY_BUILT', 'Newly Built (< 2 years)', 2),
('EXCELLENT', 'Excellent Condition', 3),
('WELL_MAINTAINED', 'Well Maintained', 4),
('AVERAGE', 'Average Condition', 5),
('NEEDS_COSMETIC', 'Needs Cosmetic Updates', 6),
('NEEDS_RENOVATION', 'Needs Renovation', 7),
('POOR', 'Poor Condition', 8),
('UNDER_CONSTRUCTION', 'Under Construction', 9),
('OFF_PLAN', 'Off Plan/Pre-construction', 10);

INSERT INTO ree_common.property_conditions_translation (property_condition_id, lang_code, translated_text, aliases) VALUES
(1, 'vi', 'Hoàn toàn mới', ARRAY['mới 100%', 'brand new', 'hoàn toàn mới']),
(1, 'en', 'Brand New', ARRAY['brand new', 'new']),
(2, 'vi', 'Mới xây dựng', ARRAY['mới xây', 'vừa xây xong']),
(2, 'en', 'Newly Built', ARRAY['newly built', 'new construction']),
(3, 'vi', 'Tình trạng tốt', ARRAY['tốt', 'rất tốt', 'excellent']),
(3, 'en', 'Excellent', ARRAY['excellent', 'great']),
(4, 'vi', 'Được bảo trì tốt', ARRAY['bảo trì tốt', 'được chăm sóc']),
(4, 'en', 'Well Maintained', ARRAY['well maintained', 'maintained']),
(5, 'vi', 'Tình trạng trung bình', ARRAY['trung bình', 'bình thường']),
(5, 'en', 'Average', ARRAY['average', 'normal']),
(6, 'vi', 'Cần sửa chữa nhỏ', ARRAY['cần sửa nhỏ', 'cần nâng cấp']),
(6, 'en', 'Needs Cosmetic', ARRAY['needs cosmetic', 'minor repairs']),
(7, 'vi', 'Cần cải tạo', ARRAY['cần cải tạo', 'cần sửa chữa lớn']),
(7, 'en', 'Needs Renovation', ARRAY['needs renovation', 'fixer upper']),
(8, 'vi', 'Tình trạng kém', ARRAY['kém', 'xuống cấp']),
(8, 'en', 'Poor', ARRAY['poor', 'bad condition']),
(9, 'vi', 'Đang xây dựng', ARRAY['đang xây', 'đang thi công']),
(9, 'en', 'Under Construction', ARRAY['under construction', 'building']),
(10, 'vi', 'Giai đoạn mở bán', ARRAY['mở bán', 'bán trên giấy']),
(10, 'en', 'Off Plan', ARRAY['off plan', 'pre-sale']);

-- ================================================================
-- 7. DISTRICTS - HCMC (23 records)
-- ================================================================

INSERT INTO ree_common.districts (code, name, sort_order) VALUES
('Q1', 'District 1', 1),
('Q2', 'District 2 (Thu Duc)', 2),
('Q3', 'District 3', 3),
('Q4', 'District 4', 4),
('Q5', 'District 5', 5),
('Q6', 'District 6', 6),
('Q7', 'District 7', 7),
('Q8', 'District 8', 8),
('Q9', 'District 9 (Thu Duc)', 9),
('Q10', 'District 10', 10),
('Q11', 'District 11', 11),
('Q12', 'District 12', 12),
('BINH_THANH', 'Binh Thanh', 13),
('TAN_BINH', 'Tan Binh', 14),
('TAN_PHU', 'Tan Phu', 15),
('PHU_NHUAN', 'Phu Nhuan', 16),
('GO_VAP', 'Go Vap', 17),
('BINH_TAN', 'Binh Tan', 18),
('THU_DUC', 'Thu Duc City', 19),
('HOC_MON', 'Hoc Mon', 20),
('CU_CHI', 'Cu Chi', 21),
('NHA_BE', 'Nha Be', 22),
('CAN_GIO', 'Can Gio', 23);

INSERT INTO ree_common.districts_translation (district_id, lang_code, translated_text, aliases) VALUES
(1, 'vi', 'Quận 1', ARRAY['quận 1', 'q1', 'q.1']),
(1, 'en', 'District 1', ARRAY['district 1', 'd1']),
(2, 'vi', 'Quận 2 (Thủ Đức)', ARRAY['quận 2', 'q2', 'q.2']),
(2, 'en', 'District 2', ARRAY['district 2', 'd2']),
(3, 'vi', 'Quận 3', ARRAY['quận 3', 'q3', 'q.3']),
(3, 'en', 'District 3', ARRAY['district 3', 'd3']),
(4, 'vi', 'Quận 4', ARRAY['quận 4', 'q4', 'q.4']),
(4, 'en', 'District 4', ARRAY['district 4', 'd4']),
(5, 'vi', 'Quận 5', ARRAY['quận 5', 'q5', 'q.5']),
(5, 'en', 'District 5', ARRAY['district 5', 'd5']),
(6, 'vi', 'Quận 6', ARRAY['quận 6', 'q6', 'q.6']),
(6, 'en', 'District 6', ARRAY['district 6', 'd6']),
(7, 'vi', 'Quận 7', ARRAY['quận 7', 'q7', 'q.7']),
(7, 'en', 'District 7', ARRAY['district 7', 'd7']),
(8, 'vi', 'Quận 8', ARRAY['quận 8', 'q8', 'q.8']),
(8, 'en', 'District 8', ARRAY['district 8', 'd8']),
(9, 'vi', 'Quận 9 (Thủ Đức)', ARRAY['quận 9', 'q9', 'q.9']),
(9, 'en', 'District 9', ARRAY['district 9', 'd9']),
(10, 'vi', 'Quận 10', ARRAY['quận 10', 'q10', 'q.10']),
(10, 'en', 'District 10', ARRAY['district 10', 'd10']),
(11, 'vi', 'Quận 11', ARRAY['quận 11', 'q11', 'q.11']),
(11, 'en', 'District 11', ARRAY['district 11', 'd11']),
(12, 'vi', 'Quận 12', ARRAY['quận 12', 'q12', 'q.12']),
(12, 'en', 'District 12', ARRAY['district 12', 'd12']),
(13, 'vi', 'Bình Thạnh', ARRAY['bình thạnh', 'q. bình thạnh']),
(13, 'en', 'Binh Thanh', ARRAY['binh thanh']),
(14, 'vi', 'Tân Bình', ARRAY['tân bình', 'q. tân bình']),
(14, 'en', 'Tan Binh', ARRAY['tan binh']),
(15, 'vi', 'Tân Phú', ARRAY['tân phú', 'q. tân phú']),
(15, 'en', 'Tan Phu', ARRAY['tan phu']),
(16, 'vi', 'Phú Nhuận', ARRAY['phú nhuận', 'q. phú nhuận']),
(16, 'en', 'Phu Nhuan', ARRAY['phu nhuan']),
(17, 'vi', 'Gò Vấp', ARRAY['gò vấp', 'q. gò vấp']),
(17, 'en', 'Go Vap', ARRAY['go vap']),
(18, 'vi', 'Bình Tân', ARRAY['bình tân', 'q. bình tân']),
(18, 'en', 'Binh Tan', ARRAY['binh tan']),
(19, 'vi', 'Thành phố Thủ Đức', ARRAY['thủ đức', 'tp thủ đức']),
(19, 'en', 'Thu Duc City', ARRAY['thu duc']),
(20, 'vi', 'Hóc Môn', ARRAY['hóc môn', 'h. hóc môn']),
(20, 'en', 'Hoc Mon', ARRAY['hoc mon']),
(21, 'vi', 'Củ Chi', ARRAY['củ chi', 'h. củ chi']),
(21, 'en', 'Cu Chi', ARRAY['cu chi']),
(22, 'vi', 'Nhà Bè', ARRAY['nhà bè', 'h. nhà bè']),
(22, 'en', 'Nha Be', ARRAY['nha be']),
(23, 'vi', 'Cần Giờ', ARRAY['cần giờ', 'h. cần giờ']),
(23, 'en', 'Can Gio', ARRAY['can gio']);

-- ================================================================
-- 8. UNITS (Common measurement units - 15 records)
-- ================================================================

INSERT INTO ree_common.units (code, name, symbol, unit_type, sort_order) VALUES
-- Area
('AREA_SQM', 'Square Meter', 'm²', 'area', 1),
('AREA_SQFT', 'Square Foot', 'sqft', 'area', 2),
('AREA_HECTARE', 'Hectare', 'ha', 'area', 3),
('AREA_ACRE', 'Acre', 'acre', 'area', 4),
-- Currency
('CURRENCY_VND', 'Vietnamese Dong', 'VND', 'currency', 11),
('CURRENCY_USD', 'US Dollar', 'USD', 'currency', 12),
('CURRENCY_EUR', 'Euro', 'EUR', 'currency', 13),
-- Distance
('DISTANCE_M', 'Meter', 'm', 'distance', 21),
('DISTANCE_KM', 'Kilometer', 'km', 'distance', 22),
('DISTANCE_MILE', 'Mile', 'mi', 'distance', 23),
-- Time
('TIME_MONTH', 'Month', 'month', 'time', 31),
('TIME_YEAR', 'Year', 'year', 'time', 32),
-- Price per area
('PRICE_PER_SQM', 'Price per Square Meter', 'VND/m²', 'price_density', 41),
('PRICE_PER_SQFT', 'Price per Square Foot', 'VND/sqft', 'price_density', 42),
-- Count
('COUNT_UNIT', 'Unit', 'unit', 'count', 51);

INSERT INTO ree_common.units_translation (unit_id, lang_code, translated_text, aliases) VALUES
(1, 'vi', 'Mét vuông', ARRAY['m2', 'm²', 'mét vuông', 'met vuong']),
(1, 'en', 'Square Meter', ARRAY['sqm', 'm2', 'm²', 'square meter']),
(2, 'vi', 'Foot vuông', ARRAY['sqft', 'foot vuông']),
(2, 'en', 'Square Foot', ARRAY['sqft', 'square foot']),
(3, 'vi', 'Hecta', ARRAY['ha', 'hecta']),
(3, 'en', 'Hectare', ARRAY['ha', 'hectare']),
(4, 'vi', 'Mẫu Anh', ARRAY['acre', 'mẫu anh']),
(4, 'en', 'Acre', ARRAY['acre']),
(5, 'vi', 'Đồng Việt Nam', ARRAY['vnd', 'vnđ', 'đồng', 'việt nam đồng']),
(5, 'en', 'Vietnamese Dong', ARRAY['vnd', 'dong']),
(6, 'vi', 'Đô la Mỹ', ARRAY['usd', 'đô', 'dollar']),
(6, 'en', 'US Dollar', ARRAY['usd', 'dollar', '$']),
(7, 'vi', 'Euro', ARRAY['eur', 'euro']),
(7, 'en', 'Euro', ARRAY['eur', 'euro', '€']),
(8, 'vi', 'Mét', ARRAY['m', 'mét', 'met']),
(8, 'en', 'Meter', ARRAY['m', 'meter']),
(9, 'vi', 'Kilômét', ARRAY['km', 'kilômét', 'kilomet']),
(9, 'en', 'Kilometer', ARRAY['km', 'kilometer']),
(10, 'vi', 'Dặm', ARRAY['mi', 'dặm', 'mile']),
(10, 'en', 'Mile', ARRAY['mi', 'mile']),
(11, 'vi', 'Tháng', ARRAY['tháng', 'month']),
(11, 'en', 'Month', ARRAY['month']),
(12, 'vi', 'Năm', ARRAY['năm', 'year']),
(12, 'en', 'Year', ARRAY['year']),
(13, 'vi', 'Giá mỗi m²', ARRAY['giá/m2', 'vnd/m2']),
(13, 'en', 'Price per sqm', ARRAY['price/sqm', 'vnd/m2']),
(14, 'vi', 'Giá mỗi sqft', ARRAY['giá/sqft', 'vnd/sqft']),
(14, 'en', 'Price per sqft', ARRAY['price/sqft', 'vnd/sqft']),
(15, 'vi', 'Đơn vị', ARRAY['đơn vị', 'unit']),
(15, 'en', 'Unit', ARRAY['unit']);

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT
    '✅ Seed data loaded successfully!' as status,
    '' as blank;

SELECT
    'Master Data Summary' as section,
    '===================' as line;

SELECT
    'transaction_types' as table_name,
    COUNT(*) as records
FROM ree_common.transaction_types
UNION ALL
SELECT 'property_types', COUNT(*) FROM ree_common.property_types
UNION ALL
SELECT 'directions', COUNT(*) FROM ree_common.directions
UNION ALL
SELECT 'furniture_types', COUNT(*) FROM ree_common.furniture_types
UNION ALL
SELECT 'legal_status', COUNT(*) FROM ree_common.legal_status
UNION ALL
SELECT 'property_conditions', COUNT(*) FROM ree_common.property_conditions
UNION ALL
SELECT 'districts', COUNT(*) FROM ree_common.districts
UNION ALL
SELECT 'units', COUNT(*) FROM ree_common.units;

SELECT
    '' as blank,
    'Translation Summary' as section,
    '===================' as line;

SELECT
    COUNT(DISTINCT lang_code) as languages,
    COUNT(*) as total_translations
FROM (
    SELECT lang_code FROM ree_common.transaction_types_translation
    UNION ALL
    SELECT lang_code FROM ree_common.property_types_translation
    UNION ALL
    SELECT lang_code FROM ree_common.directions_translation
    UNION ALL
    SELECT lang_code FROM ree_common.furniture_types_translation
    UNION ALL
    SELECT lang_code FROM ree_common.legal_status_translation
    UNION ALL
    SELECT lang_code FROM ree_common.property_conditions_translation
    UNION ALL
    SELECT lang_code FROM ree_common.districts_translation
    UNION ALL
    SELECT lang_code FROM ree_common.units_translation
) t;

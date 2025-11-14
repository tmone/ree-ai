-- ============================================================================
-- REE AI Master Data Seed Script
-- ============================================================================
-- Purpose: Insert initial master data (English canonical + Vietnamese translations)
-- Coverage: HCMC districts, common property types, amenities, and attributes
-- ============================================================================

-- ============================================================================
-- 1. CITIES
-- ============================================================================

INSERT INTO cities (name, code, country_code, latitude, longitude) VALUES
('Ho Chi Minh City', 'hcmc', 'VN', 10.8230989, 106.6296638),
('Hanoi', 'hanoi', 'VN', 21.0277644, 105.8341598)
ON CONFLICT (code) DO NOTHING;

-- Cities Translations (Vietnamese)
INSERT INTO cities_translations (city_id, lang_code, translated_text)
SELECT id, 'vi', translation FROM (VALUES
    ((SELECT id FROM cities WHERE code = 'hcmc'), 'Thành phố Hồ Chí Minh'),
    ((SELECT id FROM cities WHERE code = 'hanoi'), 'Hà Nội')
) AS t(id, translation)
ON CONFLICT (city_id, lang_code) DO NOTHING;

-- ============================================================================
-- 2. DISTRICTS (Ho Chi Minh City - All 22 Districts + 3 Counties)
-- ============================================================================

INSERT INTO districts (city_id, name, code) VALUES
-- Urban Districts (19)
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 1', 'district_1'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 2', 'district_2'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 3', 'district_3'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 4', 'district_4'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 5', 'district_5'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 6', 'district_6'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 7', 'district_7'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 8', 'district_8'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 9', 'district_9'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 10', 'district_10'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 11', 'district_11'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'District 12', 'district_12'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Go Vap District', 'go_vap'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Binh Thanh District', 'binh_thanh'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Tan Binh District', 'tan_binh'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Tan Phu District', 'tan_phu'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Phu Nhuan District', 'phu_nhuan'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Thu Duc City', 'thu_duc'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Binh Tan District', 'binh_tan'),
-- Suburban Districts/Counties (6)
((SELECT id FROM cities WHERE code = 'hcmc'), 'Hoc Mon District', 'hoc_mon'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Cu Chi District', 'cu_chi'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Binh Chanh District', 'binh_chanh'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Nha Be District', 'nha_be'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Can Gio District', 'can_gio'),
((SELECT id FROM cities WHERE code = 'hcmc'), 'Binh Duong Province', 'binh_duong')
ON CONFLICT (city_id, code) DO NOTHING;

-- Districts Translations (Vietnamese)
INSERT INTO districts_translations (district_id, lang_code, translated_text)
SELECT id, 'vi', translation FROM (VALUES
    ((SELECT id FROM districts WHERE code = 'district_1'), 'Quận 1'),
    ((SELECT id FROM districts WHERE code = 'district_2'), 'Quận 2'),
    ((SELECT id FROM districts WHERE code = 'district_3'), 'Quận 3'),
    ((SELECT id FROM districts WHERE code = 'district_4'), 'Quận 4'),
    ((SELECT id FROM districts WHERE code = 'district_5'), 'Quận 5'),
    ((SELECT id FROM districts WHERE code = 'district_6'), 'Quận 6'),
    ((SELECT id FROM districts WHERE code = 'district_7'), 'Quận 7'),
    ((SELECT id FROM districts WHERE code = 'district_8'), 'Quận 8'),
    ((SELECT id FROM districts WHERE code = 'district_9'), 'Quận 9'),
    ((SELECT id FROM districts WHERE code = 'district_10'), 'Quận 10'),
    ((SELECT id FROM districts WHERE code = 'district_11'), 'Quận 11'),
    ((SELECT id FROM districts WHERE code = 'district_12'), 'Quận 12'),
    ((SELECT id FROM districts WHERE code = 'go_vap'), 'Quận Gò Vấp'),
    ((SELECT id FROM districts WHERE code = 'binh_thanh'), 'Quận Bình Thạnh'),
    ((SELECT id FROM districts WHERE code = 'tan_binh'), 'Quận Tân Bình'),
    ((SELECT id FROM districts WHERE code = 'tan_phu'), 'Quận Tân Phú'),
    ((SELECT id FROM districts WHERE code = 'phu_nhuan'), 'Quận Phú Nhuận'),
    ((SELECT id FROM districts WHERE code = 'thu_duc'), 'Thành phố Thủ Đức'),
    ((SELECT id FROM districts WHERE code = 'binh_tan'), 'Quận Bình Tân'),
    ((SELECT id FROM districts WHERE code = 'hoc_mon'), 'Huyện Hóc Môn'),
    ((SELECT id FROM districts WHERE code = 'cu_chi'), 'Huyện Củ Chi'),
    ((SELECT id FROM districts WHERE code = 'binh_chanh'), 'Huyện Bình Chánh'),
    ((SELECT id FROM districts WHERE code = 'nha_be'), 'Huyện Nhà Bè'),
    ((SELECT id FROM districts WHERE code = 'can_gio'), 'Huyện Cần Giờ'),
    ((SELECT id FROM districts WHERE code = 'binh_duong'), 'Tỉnh Bình Dương')
) AS t(id, translation)
ON CONFLICT (district_id, lang_code) DO NOTHING;

-- ============================================================================
-- 3. PROPERTY TYPES
-- ============================================================================

INSERT INTO property_types (name, code, category, icon, description) VALUES
('Apartment', 'apartment', 'residential', '🏢', 'Multi-unit residential building with shared facilities'),
('Villa', 'villa', 'residential', '🏰', 'Detached luxury residential property with private garden'),
('Townhouse', 'townhouse', 'residential', '🏘️', 'Multi-story residential property in urban area'),
('Land', 'land', 'residential', '🌳', 'Vacant land for development or investment'),
('Penthouse', 'penthouse', 'residential', '🏙️', 'Luxury apartment on top floor with premium features'),
('Duplex', 'duplex', 'residential', '🏠', 'Two-level apartment or house'),
('Studio', 'studio', 'residential', '🛏️', 'Single-room apartment with combined living/sleeping area'),
('Serviced Apartment', 'serviced_apartment', 'residential', '🏨', 'Furnished apartment with hotel-like services'),
('Office', 'office', 'commercial', '🏢', 'Commercial office space'),
('Shop House', 'shop_house', 'commercial', '🏪', 'Commercial property with business on ground floor, residence above'),
('Warehouse', 'warehouse', 'commercial', '🏭', 'Storage and distribution facility'),
('Hotel', 'hotel', 'commercial', '🏨', 'Hospitality property with guest rooms')
ON CONFLICT (code) DO NOTHING;

-- Property Types Translations (Vietnamese)
INSERT INTO property_types_translations (property_type_id, lang_code, translated_text)
SELECT id, 'vi', translation FROM (VALUES
    ((SELECT id FROM property_types WHERE code = 'apartment'), 'Căn hộ'),
    ((SELECT id FROM property_types WHERE code = 'villa'), 'Biệt thự'),
    ((SELECT id FROM property_types WHERE code = 'townhouse'), 'Nhà phố'),
    ((SELECT id FROM property_types WHERE code = 'land'), 'Đất nền'),
    ((SELECT id FROM property_types WHERE code = 'penthouse'), 'Căn hộ penthouse'),
    ((SELECT id FROM property_types WHERE code = 'duplex'), 'Căn hộ duplex'),
    ((SELECT id FROM property_types WHERE code = 'studio'), 'Căn hộ studio'),
    ((SELECT id FROM property_types WHERE code = 'serviced_apartment'), 'Căn hộ dịch vụ'),
    ((SELECT id FROM property_types WHERE code = 'office'), 'Văn phòng'),
    ((SELECT id FROM property_types WHERE code = 'shop_house'), 'Nhà mặt tiền'),
    ((SELECT id FROM property_types WHERE code = 'warehouse'), 'Kho xưởng'),
    ((SELECT id FROM property_types WHERE code = 'hotel'), 'Khách sạn')
) AS t(id, translation)
ON CONFLICT (property_type_id, lang_code) DO NOTHING;

-- ============================================================================
-- 4. AMENITIES
-- ============================================================================

INSERT INTO amenities (name, code, category, icon, applicable_to) VALUES
-- Shared Amenities (Building/Complex)
('Swimming Pool', 'swimming_pool', 'shared_amenity', '🏊', '["apartment", "villa", "serviced_apartment"]'),
('Gym', 'gym', 'shared_amenity', '💪', '["apartment", "villa", "serviced_apartment"]'),
('Parking', 'parking', 'shared_amenity', '🅿️', '["apartment", "villa", "townhouse", "office"]'),
('Security 24/7', 'security_24_7', 'shared_amenity', '🔒', '["apartment", "villa", "serviced_apartment"]'),
('Elevator', 'elevator', 'shared_amenity', '🛗', '["apartment", "office"]'),
('Playground', 'playground', 'shared_amenity', '🎪', '["apartment", "villa"]'),
('Tennis Court', 'tennis_court', 'shared_amenity', '🎾', '["villa", "apartment"]'),
('BBQ Area', 'bbq_area', 'shared_amenity', '🔥', '["apartment", "villa"]'),
('Clubhouse', 'clubhouse', 'shared_amenity', '🏛️', '["apartment", "villa"]'),
('Supermarket', 'supermarket', 'shared_amenity', '🛒', '["apartment", "serviced_apartment"]'),
('Garden', 'garden', 'shared_amenity', '🌳', '["apartment", "villa"]'),
('Rooftop Terrace', 'rooftop_terrace', 'shared_amenity', '🌆', '["apartment"]'),

-- Private Amenities (Unit-specific)
('Balcony', 'balcony', 'private_amenity', '🪴', '["apartment", "penthouse"]'),
('Private Pool', 'private_pool', 'private_amenity', '🏊', '["villa", "penthouse"]'),
('Private Garden', 'private_garden', 'private_amenity', '🌺', '["villa", "townhouse"]'),
('Terrace', 'terrace', 'private_amenity', '☀️', '["apartment", "villa", "penthouse"]'),
('Wine Cellar', 'wine_cellar', 'private_amenity', '🍷', '["villa", "penthouse"]'),
('Home Theater', 'home_theater', 'private_amenity', '🎬', '["villa", "penthouse"]'),
('Maid Room', 'maid_room', 'private_amenity', '🚪', '["villa", "apartment"]'),
('Storage Room', 'storage_room', 'private_amenity', '📦', '["apartment", "villa", "townhouse"]'),
('Laundry Room', 'laundry_room', 'private_amenity', '🧺', '["villa", "apartment"]'),

-- Nearby Facilities
('School Nearby', 'school_nearby', 'nearby_facility', '🏫', '["apartment", "villa", "townhouse", "land"]'),
('Hospital Nearby', 'hospital_nearby', 'nearby_facility', '🏥', '["apartment", "villa", "townhouse", "land"]'),
('Shopping Mall Nearby', 'shopping_mall_nearby', 'nearby_facility', '🏬', '["apartment", "villa", "townhouse", "land"]'),
('Metro Station Nearby', 'metro_nearby', 'nearby_facility', '🚇', '["apartment", "villa", "townhouse", "land"]'),
('Park Nearby', 'park_nearby', 'nearby_facility', '🌳', '["apartment", "villa", "townhouse", "land"]'),
('Restaurant Nearby', 'restaurant_nearby', 'nearby_facility', '🍽️', '["apartment", "villa", "townhouse", "land"]'),
('Bank Nearby', 'bank_nearby', 'nearby_facility', '🏦', '["apartment", "villa", "townhouse", "office"]')
ON CONFLICT (code) DO NOTHING;

-- Amenities Translations (Vietnamese)
INSERT INTO amenities_translations (amenity_id, lang_code, translated_text)
SELECT id, 'vi', translation FROM (VALUES
    -- Shared
    ((SELECT id FROM amenities WHERE code = 'swimming_pool'), 'Hồ bơi'),
    ((SELECT id FROM amenities WHERE code = 'gym'), 'Phòng gym'),
    ((SELECT id FROM amenities WHERE code = 'parking'), 'Bãi đỗ xe'),
    ((SELECT id FROM amenities WHERE code = 'security_24_7'), 'Bảo vệ 24/7'),
    ((SELECT id FROM amenities WHERE code = 'elevator'), 'Thang máy'),
    ((SELECT id FROM amenities WHERE code = 'playground'), 'Khu vui chơi trẻ em'),
    ((SELECT id FROM amenities WHERE code = 'tennis_court'), 'Sân tennis'),
    ((SELECT id FROM amenities WHERE code = 'bbq_area'), 'Khu BBQ'),
    ((SELECT id FROM amenities WHERE code = 'clubhouse'), 'Câu lạc bộ'),
    ((SELECT id FROM amenities WHERE code = 'supermarket'), 'Siêu thị'),
    ((SELECT id FROM amenities WHERE code = 'garden'), 'Vườn cây'),
    ((SELECT id FROM amenities WHERE code = 'rooftop_terrace'), 'Sân thượng'),
    -- Private
    ((SELECT id FROM amenities WHERE code = 'balcony'), 'Ban công'),
    ((SELECT id FROM amenities WHERE code = 'private_pool'), 'Hồ bơi riêng'),
    ((SELECT id FROM amenities WHERE code = 'private_garden'), 'Vườn riêng'),
    ((SELECT id FROM amenities WHERE code = 'terrace'), 'Sân hiên'),
    ((SELECT id FROM amenities WHERE code = 'wine_cellar'), 'Hầm rượu'),
    ((SELECT id FROM amenities WHERE code = 'home_theater'), 'Phòng chiếu phim'),
    ((SELECT id FROM amenities WHERE code = 'maid_room'), 'Phòng giúp việc'),
    ((SELECT id FROM amenities WHERE code = 'storage_room'), 'Phòng kho'),
    ((SELECT id FROM amenities WHERE code = 'laundry_room'), 'Phòng giặt'),
    -- Nearby
    ((SELECT id FROM amenities WHERE code = 'school_nearby'), 'Gần trường học'),
    ((SELECT id FROM amenities WHERE code = 'hospital_nearby'), 'Gần bệnh viện'),
    ((SELECT id FROM amenities WHERE code = 'shopping_mall_nearby'), 'Gần trung tâm thương mại'),
    ((SELECT id FROM amenities WHERE code = 'metro_nearby'), 'Gần ga metro'),
    ((SELECT id FROM amenities WHERE code = 'park_nearby'), 'Gần công viên'),
    ((SELECT id FROM amenities WHERE code = 'restaurant_nearby'), 'Gần nhà hàng'),
    ((SELECT id FROM amenities WHERE code = 'bank_nearby'), 'Gần ngân hàng')
) AS t(id, translation)
ON CONFLICT (amenity_id, lang_code) DO NOTHING;

-- ============================================================================
-- 5. DIRECTIONS (8 Cardinal + Intercardinal)
-- ============================================================================

INSERT INTO directions (name, code, angle, description) VALUES
('North', 'N', 0, 'Facing north direction'),
('Northeast', 'NE', 45, 'Facing northeast direction'),
('East', 'E', 90, 'Facing east direction'),
('Southeast', 'SE', 135, 'Facing southeast direction'),
('South', 'S', 180, 'Facing south direction'),
('Southwest', 'SW', 225, 'Facing southwest direction'),
('West', 'W', 270, 'Facing west direction'),
('Northwest', 'NW', 315, 'Facing northwest direction')
ON CONFLICT (code) DO NOTHING;

-- Directions Translations (Vietnamese)
INSERT INTO directions_translations (direction_id, lang_code, translated_text)
SELECT id, 'vi', translation FROM (VALUES
    ((SELECT id FROM directions WHERE code = 'N'), 'Bắc'),
    ((SELECT id FROM directions WHERE code = 'NE'), 'Đông Bắc'),
    ((SELECT id FROM directions WHERE code = 'E'), 'Đông'),
    ((SELECT id FROM directions WHERE code = 'SE'), 'Đông Nam'),
    ((SELECT id FROM directions WHERE code = 'S'), 'Nam'),
    ((SELECT id FROM directions WHERE code = 'SW'), 'Tây Nam'),
    ((SELECT id FROM directions WHERE code = 'W'), 'Tây'),
    ((SELECT id FROM directions WHERE code = 'NW'), 'Tây Bắc')
) AS t(id, translation)
ON CONFLICT (direction_id, lang_code) DO NOTHING;

-- ============================================================================
-- 6. FURNITURE TYPES
-- ============================================================================

INSERT INTO furniture_types (name, code, level, description) VALUES
('Unfurnished', 'unfurnished', 0, 'No furniture provided'),
('Basic Furnished', 'basic', 1, 'Essential furniture only (bed, table, chairs)'),
('Full Furnished', 'full', 2, 'Complete furniture package including appliances'),
('Luxury Furnished', 'luxury', 3, 'High-end furniture and premium appliances')
ON CONFLICT (code) DO NOTHING;

-- Furniture Types Translations (Vietnamese)
INSERT INTO furniture_types_translations (furniture_type_id, lang_code, translated_text)
SELECT id, 'vi', translation FROM (VALUES
    ((SELECT id FROM furniture_types WHERE code = 'unfurnished'), 'Không nội thất'),
    ((SELECT id FROM furniture_types WHERE code = 'basic'), 'Nội thất cơ bản'),
    ((SELECT id FROM furniture_types WHERE code = 'full'), 'Nội thất đầy đủ'),
    ((SELECT id FROM furniture_types WHERE code = 'luxury'), 'Nội thất cao cấp')
) AS t(id, translation)
ON CONFLICT (furniture_type_id, lang_code) DO NOTHING;

-- ============================================================================
-- 7. LEGAL STATUSES
-- ============================================================================

INSERT INTO legal_statuses (name, code, is_valid, priority, description) VALUES
('Red Book', 'red_book', true, 10, 'Full legal ownership certificate (Sổ đỏ) - highest security'),
('Pink Book', 'pink_book', true, 8, 'House ownership certificate (Sổ hồng) - secure'),
('Sales Contract', 'sales_contract', true, 5, 'Signed sales agreement, pending transfer'),
('Construction Permit', 'construction_permit', true, 6, 'Legal permit for construction'),
('Land Use Right Certificate', 'land_use_right', true, 7, 'Certificate of land use rights'),
('Pending Documentation', 'pending', false, 2, 'Legal documentation in progress'),
('No Legal Documents', 'no_documents', false, 0, 'Property without legal documentation')
ON CONFLICT (code) DO NOTHING;

-- Legal Statuses Translations (Vietnamese)
INSERT INTO legal_statuses_translations (legal_status_id, lang_code, translated_text)
SELECT id, 'vi', translation FROM (VALUES
    ((SELECT id FROM legal_statuses WHERE code = 'red_book'), 'Sổ đỏ'),
    ((SELECT id FROM legal_statuses WHERE code = 'pink_book'), 'Sổ hồng'),
    ((SELECT id FROM legal_statuses WHERE code = 'sales_contract'), 'Hợp đồng mua bán'),
    ((SELECT id FROM legal_statuses WHERE code = 'construction_permit'), 'Giấy phép xây dựng'),
    ((SELECT id FROM legal_statuses WHERE code = 'land_use_right'), 'Giấy chứng nhận quyền sử dụng đất'),
    ((SELECT id FROM legal_statuses WHERE code = 'pending'), 'Đang làm giấy tờ'),
    ((SELECT id FROM legal_statuses WHERE code = 'no_documents'), 'Không có giấy tờ')
) AS t(id, translation)
ON CONFLICT (legal_status_id, lang_code) DO NOTHING;

-- ============================================================================
-- 8. VIEW TYPES
-- ============================================================================

INSERT INTO view_types (name, code, category, icon, description) VALUES
('River View', 'river_view', 'natural', '🌊', 'Overlooking river or waterway'),
('City View', 'city_view', 'urban', '🏙️', 'Overlooking city skyline'),
('Park View', 'park_view', 'natural', '🌳', 'Overlooking park or green space'),
('Sea View', 'sea_view', 'natural', '🌊', 'Overlooking ocean or sea'),
('Mountain View', 'mountain_view', 'natural', '⛰️', 'Overlooking mountains'),
('Garden View', 'garden_view', 'natural', '🌺', 'Overlooking garden or landscaped area'),
('Street View', 'street_view', 'urban', '🛣️', 'Facing main street'),
('Landmark View', 'landmark_view', 'landmark', '🗼', 'Overlooking famous landmark'),
('Pool View', 'pool_view', 'amenity', '🏊', 'Overlooking swimming pool')
ON CONFLICT (code) DO NOTHING;

-- View Types Translations (Vietnamese)
INSERT INTO view_types_translations (view_type_id, lang_code, translated_text)
SELECT id, 'vi', translation FROM (VALUES
    ((SELECT id FROM view_types WHERE code = 'river_view'), 'View sông'),
    ((SELECT id FROM view_types WHERE code = 'city_view'), 'View thành phố'),
    ((SELECT id FROM view_types WHERE code = 'park_view'), 'View công viên'),
    ((SELECT id FROM view_types WHERE code = 'sea_view'), 'View biển'),
    ((SELECT id FROM view_types WHERE code = 'mountain_view'), 'View núi'),
    ((SELECT id FROM view_types WHERE code = 'garden_view'), 'View vườn'),
    ((SELECT id FROM view_types WHERE code = 'street_view'), 'View đường'),
    ((SELECT id FROM view_types WHERE code = 'landmark_view'), 'View địa danh'),
    ((SELECT id FROM view_types WHERE code = 'pool_view'), 'View hồ bơi')
) AS t(id, translation)
ON CONFLICT (view_type_id, lang_code) DO NOTHING;

-- ============================================================================
-- SEED DATA COMPLETE
-- ============================================================================

-- Summary statistics
DO $$
DECLARE
    v_cities INT;
    v_districts INT;
    v_property_types INT;
    v_amenities INT;
    v_directions INT;
    v_furniture_types INT;
    v_legal_statuses INT;
    v_view_types INT;
BEGIN
    SELECT COUNT(*) INTO v_cities FROM cities;
    SELECT COUNT(*) INTO v_districts FROM districts;
    SELECT COUNT(*) INTO v_property_types FROM property_types;
    SELECT COUNT(*) INTO v_amenities FROM amenities;
    SELECT COUNT(*) INTO v_directions FROM directions;
    SELECT COUNT(*) INTO v_furniture_types FROM furniture_types;
    SELECT COUNT(*) INTO v_legal_statuses FROM legal_statuses;
    SELECT COUNT(*) INTO v_view_types FROM view_types;

    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Master Data Seed Summary:';
    RAISE NOTICE '- Cities: %', v_cities;
    RAISE NOTICE '- Districts: %', v_districts;
    RAISE NOTICE '- Property Types: %', v_property_types;
    RAISE NOTICE '- Amenities: %', v_amenities;
    RAISE NOTICE '- Directions: %', v_directions;
    RAISE NOTICE '- Furniture Types: %', v_furniture_types;
    RAISE NOTICE '- Legal Statuses: %', v_legal_statuses;
    RAISE NOTICE '- View Types: %', v_view_types;
    RAISE NOTICE '============================================================================';
END $$;

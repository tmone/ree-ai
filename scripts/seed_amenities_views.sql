-- ================================================================
-- SEED AMENITIES & VIEWS - Common Real Estate Data
-- ================================================================
-- PURPOSE: Populate amenities and views for extraction service
-- SOURCE: Common amenities/views found in Vietnamese real estate
-- CODE CONVENTION: SCREAMING_SNAKE_CASE
-- ================================================================

BEGIN;

-- ================================================================
-- 9. AMENITIES (50 common amenities)
-- ================================================================

INSERT INTO ree_common.amenities (code, name, sort_order) VALUES
-- Security
('SECURITY_24_7', '24/7 Security', 1),
('CCTV', 'CCTV Camera', 2),
('ACCESS_CARD', 'Access Card System', 3),
('SECURITY_GUARD', 'Security Guard', 4),
('INTERCOM', 'Intercom', 5),
-- Sports & Recreation
('SWIMMING_POOL', 'Swimming Pool', 11),
('GYM', 'Gym/Fitness Center', 12),
('PLAYGROUND', 'Children Playground', 13),
('TENNIS_COURT', 'Tennis Court', 14),
('BASKETBALL_COURT', 'Basketball Court', 15),
('BADMINTON_COURT', 'Badminton Court', 16),
('YOGA_ROOM', 'Yoga Room', 17),
('SAUNA', 'Sauna', 18),
('JACUZZI', 'Jacuzzi', 19),
('SPA', 'Spa', 20),
-- Common Areas
('GARDEN', 'Garden', 21),
('BBQ_AREA', 'BBQ Area', 22),
('ROOFTOP_GARDEN', 'Rooftop Garden', 23),
('CLUBHOUSE', 'Clubhouse', 24),
('LOUNGE', 'Lounge', 25),
('LIBRARY', 'Library', 26),
('MEETING_ROOM', 'Meeting Room', 27),
('CO_WORKING_SPACE', 'Co-working Space', 28),
-- Facilities
('PARKING', 'Parking', 31),
('ELEVATOR', 'Elevator', 32),
('BACKUP_GENERATOR', 'Backup Generator', 33),
('FIRE_ALARM', 'Fire Alarm System', 34),
('SPRINKLER', 'Fire Sprinkler', 35),
('WATER_TANK', 'Water Tank', 36),
-- Utilities
('AIR_CONDITIONING', 'Air Conditioning', 41),
('CENTRAL_AC', 'Central Air Conditioning', 42),
('HEATING', 'Heating System', 43),
('SMART_HOME', 'Smart Home System', 44),
('HIGH_SPEED_INTERNET', 'High Speed Internet', 45),
('CABLE_TV', 'Cable TV', 46),
-- Pet & Family
('PET_FRIENDLY', 'Pet Friendly', 51),
('PET_AREA', 'Pet Area', 52),
('KIDS_POOL', 'Kids Pool', 53),
('DAYCARE', 'Daycare Center', 54),
-- Commercial
('SUPERMARKET', 'Supermarket', 61),
('CONVENIENCE_STORE', 'Convenience Store', 62),
('RESTAURANT', 'Restaurant', 63),
('CAFE', 'Cafe', 64),
('ATM', 'ATM', 65),
('LAUNDRY', 'Laundry Service', 66),
('MAIL_ROOM', 'Mail Room', 67),
('CONCIERGE', 'Concierge Service', 68);

-- Vietnamese translations for amenities
INSERT INTO ree_common.amenities_translation (amenity_id, lang_code, translated_text, aliases)
SELECT id, 'vi',
    CASE code
        WHEN 'SECURITY_24_7' THEN 'Bảo vệ 24/7'
        WHEN 'CCTV' THEN 'Camera an ninh'
        WHEN 'ACCESS_CARD' THEN 'Thẻ từ'
        WHEN 'SECURITY_GUARD' THEN 'Bảo vệ'
        WHEN 'INTERCOM' THEN 'Chuông cửa'
        WHEN 'SWIMMING_POOL' THEN 'Hồ bơi'
        WHEN 'GYM' THEN 'Phòng gym'
        WHEN 'PLAYGROUND' THEN 'Sân chơi trẻ em'
        WHEN 'TENNIS_COURT' THEN 'Sân tennis'
        WHEN 'BASKETBALL_COURT' THEN 'Sân bóng rổ'
        WHEN 'BADMINTON_COURT' THEN 'Sân cầu lông'
        WHEN 'YOGA_ROOM' THEN 'Phòng yoga'
        WHEN 'SAUNA' THEN 'Phòng xông hơi'
        WHEN 'JACUZZI' THEN 'Bồn tắm massage'
        WHEN 'SPA' THEN 'Spa'
        WHEN 'GARDEN' THEN 'Vườn cây'
        WHEN 'BBQ_AREA' THEN 'Khu BBQ'
        WHEN 'ROOFTOP_GARDEN' THEN 'Vườn sân thượng'
        WHEN 'CLUBHOUSE' THEN 'Câu lạc bộ'
        WHEN 'LOUNGE' THEN 'Phòng khách chung'
        WHEN 'LIBRARY' THEN 'Thư viện'
        WHEN 'MEETING_ROOM' THEN 'Phòng họp'
        WHEN 'CO_WORKING_SPACE' THEN 'Không gian làm việc chung'
        WHEN 'PARKING' THEN 'Bãi đỗ xe'
        WHEN 'ELEVATOR' THEN 'Thang máy'
        WHEN 'BACKUP_GENERATOR' THEN 'Máy phát điện'
        WHEN 'FIRE_ALARM' THEN 'Hệ thống báo cháy'
        WHEN 'SPRINKLER' THEN 'Hệ thống chữa cháy'
        WHEN 'WATER_TANK' THEN 'Bể nước'
        WHEN 'AIR_CONDITIONING' THEN 'Máy lạnh'
        WHEN 'CENTRAL_AC' THEN 'Điều hòa trung tâm'
        WHEN 'HEATING' THEN 'Hệ thống sưởi'
        WHEN 'SMART_HOME' THEN 'Nhà thông minh'
        WHEN 'HIGH_SPEED_INTERNET' THEN 'Internet tốc độ cao'
        WHEN 'CABLE_TV' THEN 'Truyền hình cáp'
        WHEN 'PET_FRIENDLY' THEN 'Cho phép nuôi thú cưng'
        WHEN 'PET_AREA' THEN 'Khu vực thú cưng'
        WHEN 'KIDS_POOL' THEN 'Bể bơi trẻ em'
        WHEN 'DAYCARE' THEN 'Nhà trẻ'
        WHEN 'SUPERMARKET' THEN 'Siêu thị'
        WHEN 'CONVENIENCE_STORE' THEN 'Cửa hàng tiện lợi'
        WHEN 'RESTAURANT' THEN 'Nhà hàng'
        WHEN 'CAFE' THEN 'Quán cà phê'
        WHEN 'ATM' THEN 'Cây ATM'
        WHEN 'LAUNDRY' THEN 'Dịch vụ giặt ủi'
        WHEN 'MAIL_ROOM' THEN 'Phòng thư'
        WHEN 'CONCIERGE' THEN 'Dịch vụ tiếp tân'
    END,
    CASE code
        WHEN 'SECURITY_24_7' THEN ARRAY['bảo vệ 24/7', 'an ninh 24/7']
        WHEN 'CCTV' THEN ARRAY['camera', 'cctv', 'camera an ninh']
        WHEN 'ACCESS_CARD' THEN ARRAY['thẻ từ', 'thẻ căn hộ']
        WHEN 'SECURITY_GUARD' THEN ARRAY['bảo vệ', 'an ninh']
        WHEN 'INTERCOM' THEN ARRAY['chuông cửa', 'intercom']
        WHEN 'SWIMMING_POOL' THEN ARRAY['hồ bơi', 'bể bơi', 'pool']
        WHEN 'GYM' THEN ARRAY['gym', 'phòng gym', 'phòng tập']
        WHEN 'PLAYGROUND' THEN ARRAY['sân chơi', 'khu vui chơi trẻ em']
        WHEN 'TENNIS_COURT' THEN ARRAY['sân tennis', 'tennis']
        WHEN 'BASKETBALL_COURT' THEN ARRAY['sân bóng rổ', 'bóng rổ']
        WHEN 'BADMINTON_COURT' THEN ARRAY['sân cầu lông', 'cầu lông']
        WHEN 'YOGA_ROOM' THEN ARRAY['phòng yoga', 'yoga']
        WHEN 'SAUNA' THEN ARRAY['xông hơi', 'sauna']
        WHEN 'JACUZZI' THEN ARRAY['jacuzzi', 'bồn tắm massage']
        WHEN 'SPA' THEN ARRAY['spa']
        WHEN 'GARDEN' THEN ARRAY['vườn', 'vườn cây']
        WHEN 'BBQ_AREA' THEN ARRAY['bbq', 'khu bbq', 'khu nướng']
        WHEN 'ROOFTOP_GARDEN' THEN ARRAY['vườn sân thượng', 'rooftop']
        WHEN 'CLUBHOUSE' THEN ARRAY['câu lạc bộ', 'clubhouse']
        WHEN 'LOUNGE' THEN ARRAY['lounge', 'phòng khách chung']
        WHEN 'LIBRARY' THEN ARRAY['thư viện']
        WHEN 'MEETING_ROOM' THEN ARRAY['phòng họp']
        WHEN 'CO_WORKING_SPACE' THEN ARRAY['coworking', 'không gian làm việc']
        WHEN 'PARKING' THEN ARRAY['bãi đỗ xe', 'chỗ đỗ xe', 'parking']
        WHEN 'ELEVATOR' THEN ARRAY['thang máy', 'elevator']
        WHEN 'BACKUP_GENERATOR' THEN ARRAY['máy phát điện']
        WHEN 'FIRE_ALARM' THEN ARRAY['báo cháy']
        WHEN 'SPRINKLER' THEN ARRAY['chữa cháy', 'sprinkler']
        WHEN 'WATER_TANK' THEN ARRAY['bể nước']
        WHEN 'AIR_CONDITIONING' THEN ARRAY['máy lạnh', 'điều hòa', 'ac']
        WHEN 'CENTRAL_AC' THEN ARRAY['điều hòa trung tâm', 'central ac']
        WHEN 'HEATING' THEN ARRAY['sưởi', 'hệ thống sưởi']
        WHEN 'SMART_HOME' THEN ARRAY['smart home', 'nhà thông minh']
        WHEN 'HIGH_SPEED_INTERNET' THEN ARRAY['internet', 'wifi']
        WHEN 'CABLE_TV' THEN ARRAY['truyền hình', 'cable tv']
        WHEN 'PET_FRIENDLY' THEN ARRAY['pet friendly', 'nuôi thú cưng']
        WHEN 'PET_AREA' THEN ARRAY['khu thú cưng', 'pet area']
        WHEN 'KIDS_POOL' THEN ARRAY['bể bơi trẻ em']
        WHEN 'DAYCARE' THEN ARRAY['nhà trẻ', 'daycare']
        WHEN 'SUPERMARKET' THEN ARRAY['siêu thị', 'supermarket']
        WHEN 'CONVENIENCE_STORE' THEN ARRAY['cửa hàng tiện lợi', 'mini mart']
        WHEN 'RESTAURANT' THEN ARRAY['nhà hàng', 'restaurant']
        WHEN 'CAFE' THEN ARRAY['cà phê', 'cafe']
        WHEN 'ATM' THEN ARRAY['atm', 'cây atm']
        WHEN 'LAUNDRY' THEN ARRAY['giặt ủi', 'laundry']
        WHEN 'MAIL_ROOM' THEN ARRAY['phòng thư']
        WHEN 'CONCIERGE' THEN ARRAY['tiếp tân', 'concierge']
    END
FROM ree_common.amenities;

-- English translations (same as name but with aliases)
INSERT INTO ree_common.amenities_translation (amenity_id, lang_code, translated_text, aliases)
SELECT id, 'en', name,
    CASE code
        WHEN 'SECURITY_24_7' THEN ARRAY['24/7 security', 'security 24h']
        WHEN 'CCTV' THEN ARRAY['cctv', 'camera', 'surveillance']
        WHEN 'ACCESS_CARD' THEN ARRAY['access card', 'key card']
        WHEN 'SECURITY_GUARD' THEN ARRAY['security guard', 'guard']
        WHEN 'INTERCOM' THEN ARRAY['intercom', 'doorbell']
        WHEN 'SWIMMING_POOL' THEN ARRAY['swimming pool', 'pool']
        WHEN 'GYM' THEN ARRAY['gym', 'fitness', 'fitness center']
        WHEN 'PLAYGROUND' THEN ARRAY['playground', 'kids playground']
        WHEN 'TENNIS_COURT' THEN ARRAY['tennis court', 'tennis']
        WHEN 'BASKETBALL_COURT' THEN ARRAY['basketball court', 'basketball']
        WHEN 'BADMINTON_COURT' THEN ARRAY['badminton court', 'badminton']
        WHEN 'YOGA_ROOM' THEN ARRAY['yoga room', 'yoga']
        WHEN 'SAUNA' THEN ARRAY['sauna', 'steam room']
        WHEN 'JACUZZI' THEN ARRAY['jacuzzi', 'hot tub']
        WHEN 'SPA' THEN ARRAY['spa']
        WHEN 'GARDEN' THEN ARRAY['garden']
        WHEN 'BBQ_AREA' THEN ARRAY['bbq area', 'bbq', 'barbecue']
        WHEN 'ROOFTOP_GARDEN' THEN ARRAY['rooftop garden', 'rooftop']
        WHEN 'CLUBHOUSE' THEN ARRAY['clubhouse', 'club']
        WHEN 'LOUNGE' THEN ARRAY['lounge']
        WHEN 'LIBRARY' THEN ARRAY['library']
        WHEN 'MEETING_ROOM' THEN ARRAY['meeting room']
        WHEN 'CO_WORKING_SPACE' THEN ARRAY['coworking', 'co-working']
        WHEN 'PARKING' THEN ARRAY['parking', 'car park']
        WHEN 'ELEVATOR' THEN ARRAY['elevator', 'lift']
        WHEN 'BACKUP_GENERATOR' THEN ARRAY['generator', 'backup power']
        WHEN 'FIRE_ALARM' THEN ARRAY['fire alarm']
        WHEN 'SPRINKLER' THEN ARRAY['sprinkler', 'fire sprinkler']
        WHEN 'WATER_TANK' THEN ARRAY['water tank']
        WHEN 'AIR_CONDITIONING' THEN ARRAY['air conditioning', 'ac', 'aircon']
        WHEN 'CENTRAL_AC' THEN ARRAY['central ac', 'central air']
        WHEN 'HEATING' THEN ARRAY['heating']
        WHEN 'SMART_HOME' THEN ARRAY['smart home']
        WHEN 'HIGH_SPEED_INTERNET' THEN ARRAY['internet', 'wifi', 'high speed internet']
        WHEN 'CABLE_TV' THEN ARRAY['cable tv', 'tv']
        WHEN 'PET_FRIENDLY' THEN ARRAY['pet friendly', 'pets allowed']
        WHEN 'PET_AREA' THEN ARRAY['pet area']
        WHEN 'KIDS_POOL' THEN ARRAY['kids pool', 'children pool']
        WHEN 'DAYCARE' THEN ARRAY['daycare', 'childcare']
        WHEN 'SUPERMARKET' THEN ARRAY['supermarket', 'grocery']
        WHEN 'CONVENIENCE_STORE' THEN ARRAY['convenience store', 'mini mart']
        WHEN 'RESTAURANT' THEN ARRAY['restaurant']
        WHEN 'CAFE' THEN ARRAY['cafe', 'coffee shop']
        WHEN 'ATM' THEN ARRAY['atm']
        WHEN 'LAUNDRY' THEN ARRAY['laundry', 'laundry service']
        WHEN 'MAIL_ROOM' THEN ARRAY['mail room']
        WHEN 'CONCIERGE' THEN ARRAY['concierge']
    END
FROM ree_common.amenities;

-- ================================================================
-- 10. VIEWS (15 common view types)
-- ================================================================

INSERT INTO ree_common.views (code, name, sort_order) VALUES
('CITY_VIEW', 'City View', 1),
('RIVER_VIEW', 'River View', 2),
('SEA_VIEW', 'Sea View', 3),
('PARK_VIEW', 'Park View', 4),
('GARDEN_VIEW', 'Garden View', 5),
('MOUNTAIN_VIEW', 'Mountain View', 6),
('GOLF_VIEW', 'Golf Course View', 7),
('LANDMARK_VIEW', 'Landmark View', 8),
('POOL_VIEW', 'Pool View', 9),
('COURTYARD_VIEW', 'Courtyard View', 10),
('STREET_VIEW', 'Street View', 11),
('INNER_VIEW', 'Inner View', 12),
('PANORAMIC_VIEW', 'Panoramic View', 13),
('PARTIAL_VIEW', 'Partial View', 14),
('NO_VIEW', 'No Special View', 15);

-- Vietnamese translations for views
INSERT INTO ree_common.views_translation (view_id, lang_code, translated_text, aliases)
SELECT id, 'vi',
    CASE code
        WHEN 'CITY_VIEW' THEN 'View thành phố'
        WHEN 'RIVER_VIEW' THEN 'View sông'
        WHEN 'SEA_VIEW' THEN 'View biển'
        WHEN 'PARK_VIEW' THEN 'View công viên'
        WHEN 'GARDEN_VIEW' THEN 'View vườn'
        WHEN 'MOUNTAIN_VIEW' THEN 'View núi'
        WHEN 'GOLF_VIEW' THEN 'View sân golf'
        WHEN 'LANDMARK_VIEW' THEN 'View địa danh'
        WHEN 'POOL_VIEW' THEN 'View hồ bơi'
        WHEN 'COURTYARD_VIEW' THEN 'View sân trong'
        WHEN 'STREET_VIEW' THEN 'View đường phố'
        WHEN 'INNER_VIEW' THEN 'View nội khu'
        WHEN 'PANORAMIC_VIEW' THEN 'View toàn cảnh'
        WHEN 'PARTIAL_VIEW' THEN 'View một phần'
        WHEN 'NO_VIEW' THEN 'Không có view'
    END,
    CASE code
        WHEN 'CITY_VIEW' THEN ARRAY['view thành phố', 'view city', 'thành phố']
        WHEN 'RIVER_VIEW' THEN ARRAY['view sông', 'sông', 'river view']
        WHEN 'SEA_VIEW' THEN ARRAY['view biển', 'biển', 'sea view']
        WHEN 'PARK_VIEW' THEN ARRAY['view công viên', 'công viên', 'park view']
        WHEN 'GARDEN_VIEW' THEN ARRAY['view vườn', 'vườn']
        WHEN 'MOUNTAIN_VIEW' THEN ARRAY['view núi', 'núi', 'mountain view']
        WHEN 'GOLF_VIEW' THEN ARRAY['view golf', 'sân golf']
        WHEN 'LANDMARK_VIEW' THEN ARRAY['view landmark', 'view địa danh']
        WHEN 'POOL_VIEW' THEN ARRAY['view hồ bơi', 'pool view']
        WHEN 'COURTYARD_VIEW' THEN ARRAY['view sân trong']
        WHEN 'STREET_VIEW' THEN ARRAY['view đường', 'street view']
        WHEN 'INNER_VIEW' THEN ARRAY['view nội khu', 'nội khu']
        WHEN 'PANORAMIC_VIEW' THEN ARRAY['view toàn cảnh', 'panoramic']
        WHEN 'PARTIAL_VIEW' THEN ARRAY['view một phần']
        WHEN 'NO_VIEW' THEN ARRAY['không view', 'no view']
    END
FROM ree_common.views;

-- English translations
INSERT INTO ree_common.views_translation (view_id, lang_code, translated_text, aliases)
SELECT id, 'en', name,
    CASE code
        WHEN 'CITY_VIEW' THEN ARRAY['city view', 'city', 'urban view']
        WHEN 'RIVER_VIEW' THEN ARRAY['river view', 'river']
        WHEN 'SEA_VIEW' THEN ARRAY['sea view', 'ocean view', 'beach view']
        WHEN 'PARK_VIEW' THEN ARRAY['park view', 'park']
        WHEN 'GARDEN_VIEW' THEN ARRAY['garden view', 'garden']
        WHEN 'MOUNTAIN_VIEW' THEN ARRAY['mountain view', 'mountain']
        WHEN 'GOLF_VIEW' THEN ARRAY['golf view', 'golf course view']
        WHEN 'LANDMARK_VIEW' THEN ARRAY['landmark view', 'landmark']
        WHEN 'POOL_VIEW' THEN ARRAY['pool view', 'pool']
        WHEN 'COURTYARD_VIEW' THEN ARRAY['courtyard view', 'courtyard']
        WHEN 'STREET_VIEW' THEN ARRAY['street view', 'street']
        WHEN 'INNER_VIEW' THEN ARRAY['inner view', 'internal view']
        WHEN 'PANORAMIC_VIEW' THEN ARRAY['panoramic view', 'panorama']
        WHEN 'PARTIAL_VIEW' THEN ARRAY['partial view']
        WHEN 'NO_VIEW' THEN ARRAY['no view', 'blocked view']
    END
FROM ree_common.views;

COMMIT;

-- ================================================================
-- VERIFICATION
-- ================================================================

SELECT '✅ Amenities & Views loaded successfully!' as status;

SELECT
    'amenities' as table_name,
    COUNT(*) as records
FROM ree_common.amenities
UNION ALL
SELECT 'views', COUNT(*) FROM ree_common.views;

SELECT
    'Total translations (vi + en)' as description,
    (SELECT COUNT(*) FROM ree_common.amenities_translation) +
    (SELECT COUNT(*) FROM ree_common.views_translation) as count;

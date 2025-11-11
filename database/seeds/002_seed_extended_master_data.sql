-- Seed Data for Extended Master Data Tables
-- Description: Seed data for developers, projects, streets, building features, views, and property conditions

-- ============================================================
-- DEVELOPERS (Chủ đầu tư)
-- ============================================================

INSERT INTO master_developers (code, name_vi, name_en, aliases, type, reputation_score, website, hotline, total_projects, sort_order) VALUES
-- Top Tier Developers
('vingroup', 'Tập đoàn Vingroup', 'Vingroup Corporation', ARRAY['Vingroup', 'Vinhomes', 'Vin Group', 'Tập đoàn Vingroup'], 'corporation', 5, 'https://vinhomes.vn', '1900232389', 50, 1),
('capitaland', 'CapitaLand Vietnam', 'CapitaLand Vietnam', ARRAY['CapitaLand', 'Capita Land', 'Capital Land'], 'corporation', 5, 'https://www.capitaland.com', '', 15, 2),
('novaland', 'Tập đoàn Novaland', 'Novaland Group', ARRAY['Novaland', 'Nova Land', 'Tập đoàn Novaland'], 'corporation', 5, 'https://novaland.com.vn', '19006869', 30, 3),
('keppel_land', 'Keppel Land', 'Keppel Land', ARRAY['Keppel Land', 'Keppel', 'KepLand'], 'corporation', 5, 'https://www.keppelland.com.vn', '', 10, 4),
('sunwah', 'Tập đoàn Sunwah', 'Sunwah Group', ARRAY['Sunwah', 'Sun Wah', 'Tập đoàn Sunwah'], 'corporation', 4, 'https://www.sunwah.com', '', 8, 5),
('mapletree', 'Mapletree', 'Mapletree', ARRAY['Mapletree', 'Maple Tree'], 'corporation', 5, 'https://www.mapletree.com.sg', '', 5, 6),
('gamuda_land', 'Gamuda Land', 'Gamuda Land', ARRAY['Gamuda Land', 'Gamuda', 'Gamuda Việt Nam'], 'corporation', 4, 'https://gamudaland.com.vn', '1800599866', 5, 7),
('phu_my_hung', 'Phú Mỹ Hưng', 'Phu My Hung Corporation', ARRAY['Phú Mỹ Hưng', 'Phu My Hung', 'PMH'], 'corporation', 5, 'https://www.phumyhung.com.vn', '0282254 3973', 20, 8),
('dat_xanh', 'Tập đoàn Đất Xanh', 'Dat Xanh Group', ARRAY['Đất Xanh', 'Dat Xanh', 'DXG'], 'corporation', 4, 'https://www.datxanhgroup.com.vn', '1900299986', 25, 9),
('him_lam', 'Him Lam', 'Him Lam', ARRAY['Him Lam', 'Him Lâm', 'Công ty Him Lam'], 'corporation', 4, 'https://himlam.com.vn', '19001880', 20, 10),
('cotec', 'COTEC', 'COTEC Land', ARRAY['COTEC', 'Cotec Land', 'Công ty COTEC'], 'corporation', 4, '', '', 10, 11),
('van_thinh_phat', 'Vạn Thịnh Phát', 'Van Thinh Phat Group', ARRAY['Vạn Thịnh Phát', 'Van Thinh Phat', 'VTP'], 'corporation', 3, '', '', 8, 12),
('hung_thinh', 'Hưng Thịnh', 'Hung Thinh Corporation', ARRAY['Hưng Thịnh', 'Hung Thinh', 'Hung Thinh Corp'], 'corporation', 4, 'https://hungthinhcorp.com.vn', '1900299955', 30, 13),
('ldg', 'LDG Group', 'LDG Group', ARRAY['LDG', 'LDG Group', 'Long Đại Giang'], 'corporation', 3, 'https://ldggroup.vn', '', 15, 14),
('nam_long', 'Nam Long', 'Nam Long Group', ARRAY['Nam Long', 'Nam Long Group', 'Công ty Nam Long'], 'corporation', 4, 'https://www.namlong.com.vn', '19001790', 12, 15)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- PROJECTS (Dự án)
-- ============================================================

INSERT INTO master_projects (code, name_vi, name_en, aliases, developer_id, district_id, type, scale, address, total_area, total_units, total_buildings, year_started, year_completed, handover_status, features, sort_order) VALUES
-- Vinhomes Projects
('vinhomes_central_park', 'Vinhomes Central Park', 'Vinhomes Central Park',
 ARRAY['Vinhomes Central Park', 'VHCP', 'VCP', 'Landmark 81'],
 (SELECT id FROM master_developers WHERE code = 'vingroup'),
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'luxury', 'mega', 'Số 720A Điện Biên Phủ, Phường 22, Bình Thạnh', 26, 10000, 14, 2012, 2018, 'completed',
 ARRAY['riverside', 'near_metro', 'green_space', 'shopping_mall', 'international_school'],
 1),

('vinhomes_golden_river', 'Vinhomes Golden River', 'Vinhomes Golden River',
 ARRAY['Vinhomes Golden River', 'VHGR', 'VGR', 'Aqua 1', 'Aqua 2'],
 (SELECT id FROM master_developers WHERE code = 'vingroup'),
 (SELECT id FROM master_districts WHERE code = 'Q1'),
 'luxury', 'large', '02 Tôn Đức Thắng, Phường Bến Nghé, Quận 1', 5.7, 1100, 4, 2015, 2019, 'completed',
 ARRAY['riverside', 'downtown', 'luxury_facilities', 'sky_bar'],
 2),

('vinhomes_grand_park', 'Vinhomes Grand Park', 'Vinhomes Grand Park',
 ARRAY['Vinhomes Grand Park', 'VHGP', 'VGP'],
 (SELECT id FROM master_developers WHERE code = 'vingroup'),
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'mid_range', 'mega', 'Long Thạnh Mỹ, Quận 9', 271, 35000, 120, 2018, 2030, 'under_construction',
 ARRAY['mega_project', 'green_space', 'schools', 'hospitals', 'shopping_mall'],
 3),

-- Masteri Projects (Masterise Homes - part of related developers)
('masteri_thao_dien', 'Masteri Thảo Điền', 'Masteri Thao Dien',
 ARRAY['Masteri Thảo Điền', 'Masteri Thao Dien', 'MTD'],
 (SELECT id FROM master_developers WHERE code = 'novaland'),
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'luxury', 'large', '159 Xa lộ Hà Nội, Phường Thảo Điền', 5.1, 4100, 5, 2014, 2018, 'completed',
 ARRAY['near_metro', 'international_school', 'luxury_facilities', 'expat_area'],
 4),

('masteri_an_phu', 'Masteri An Phú', 'Masteri An Phu',
 ARRAY['Masteri An Phú', 'Masteri An Phu', 'MAP'],
 (SELECT id FROM master_developers WHERE code = 'novaland'),
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'luxury', 'large', '179 Xa lộ Hà Nội, Phường An Phú', 3.6, 3200, 3, 2015, 2019, 'completed',
 ARRAY['near_metro', 'shopping_mall', 'luxury_facilities'],
 5),

-- CapitaLand Projects
('the_vista', 'The Vista', 'The Vista',
 ARRAY['The Vista', 'Vista Verde', 'The Vista An Phú'],
 (SELECT id FROM master_developers WHERE code = 'capitaland'),
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'luxury', 'large', '628-632 Xa lộ Hà Nội, Phường An Phú', 9, 1400, 3, 2013, 2017, 'completed',
 ARRAY['green_space', 'international_school', 'luxury_facilities'],
 6),

('the_botanica', 'The Botanica', 'The Botanica',
 ARRAY['The Botanica', 'Botanica'],
 (SELECT id FROM master_developers WHERE code = 'novaland'),
 (SELECT id FROM master_districts WHERE code = 'QTD'),
 'mid_range', 'medium', '104B Phổ Quang, Phường 9, Phú Nhuận', 1.6, 345, 1, 2016, 2019, 'completed',
 ARRAY['near_airport', 'botanical_theme', 'sky_garden'],
 7),

-- Phú Mỹ Hưng Projects
('scenic_valley', 'Scenic Valley', 'Scenic Valley',
 ARRAY['Scenic Valley', 'Thung Lũng Xanh'],
 (SELECT id FROM master_developers WHERE code = 'phu_my_hung'),
 (SELECT id FROM master_districts WHERE code = 'Q7'),
 'luxury', 'large', 'Phú Mỹ Hưng, Quận 7', 42, 1200, 30, 2007, 2015, 'completed',
 ARRAY['green_space', 'villa_community', 'near_schools', 'secure'],
 8),

('sky_garden', 'Sky Garden', 'Sky Garden',
 ARRAY['Sky Garden', 'Sky Garden PMH'],
 (SELECT id FROM master_developers WHERE code = 'phu_my_hung'),
 (SELECT id FROM master_districts WHERE code = 'Q7'),
 'mid_range', 'large', 'Nguyễn Văn Linh, Phú Mỹ Hưng, Quận 7', 15, 2500, 3, 2012, 2016, 'completed',
 ARRAY['green_space', 'shopping_mall', 'schools'],
 9),

-- Keppel Land Projects
('empire_city', 'Empire City', 'Empire City',
 ARRAY['Empire City', 'Thành phố Đế Vương', 'Tilia Residence'],
 (SELECT id FROM master_developers WHERE code = 'keppel_land'),
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'luxury', 'mega', '88 Mai Chí Thọ, Phường An Phú', 14.5, 9000, 12, 2016, 2025, 'under_construction',
 ARRAY['riverside', 'near_metro', 'mixed_use', 'shopping_mall'],
 10),

-- Gamuda Land Projects
('celadon_city', 'Celadon City', 'Celadon City',
 ARRAY['Celadon City', 'Thành phố Celadon'],
 (SELECT id FROM master_developers WHERE code = 'gamuda_land'),
 (SELECT id FROM master_districts WHERE code = 'QTD'),
 'mid_range', 'mega', 'Tân Phú, Quận Tân Phú', 82, 16000, 50, 2012, 2022, 'partially_completed',
 ARRAY['mega_project', 'green_space', 'schools', 'shopping_mall'],
 11),

-- Dat Xanh Projects
('gem_riverside', 'Gem Riverside', 'Gem Riverside',
 ARRAY['Gem Riverside', 'GEM Riverside'],
 (SELECT id FROM master_developers WHERE code = 'dat_xanh'),
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'mid_range', 'large', 'Đường Nguyễn Duy Trinh, Quận 2', 6.1, 1800, 3, 2016, 2019, 'completed',
 ARRAY['riverside', 'green_space', 'affordable_luxury'],
 12),

-- Hung Thinh Projects
('sunshine_city', 'Sunshine City Sài Gòn', 'Sunshine City Saigon',
 ARRAY['Sunshine City', 'Sunshine City Sài Gòn'],
 (SELECT id FROM master_developers WHERE code = 'hung_thinh'),
 (SELECT id FROM master_districts WHERE code = 'Q7'),
 'mid_range', 'large', 'Đường Số 7, KDC Cityland, Quận 7', 3.6, 1800, 4, 2017, 2020, 'completed',
 ARRAY['near_phu_my_hung', 'affordable', 'green_space'],
 13),

-- Sunwah Projects
('sunwah_pearl', 'Sunwah Pearl', 'Sunwah Pearl',
 ARRAY['Sunwah Pearl', 'Ngọc trai Sunwah'],
 (SELECT id FROM master_developers WHERE code = 'sunwah'),
 (SELECT id FROM master_districts WHERE code = 'QBTh'),
 'luxury', 'large', '90 Nguyễn Hữu Cảnh, Phường 22, Bình Thạnh', 5.2, 1100, 2, 2014, 2018, 'completed',
 ARRAY['riverside', 'downtown', 'luxury_facilities', 'near_district_1'],
 14),

-- Additional Projects
('saigon_pearl', 'Saigon Pearl', 'Saigon Pearl',
 ARRAY['Saigon Pearl', 'Ngọc trai Sài Gòn'],
 (SELECT id FROM master_developers WHERE code = 'novaland'),
 (SELECT id FROM master_districts WHERE code = 'QBTh'),
 'luxury', 'large', '92 Nguyễn Hữu Cảnh, Phường 22, Bình Thạnh', 5.5, 3000, 6, 2009, 2015, 'completed',
 ARRAY['riverside', 'downtown', 'luxury_facilities'],
 15)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- STREETS (Đường phố quan trọng ở TP.HCM)
-- ============================================================

INSERT INTO master_streets (code, name_vi, name_en, aliases, district_id, type, width_category, importance_score, description, notable_landmarks, sort_order) VALUES
-- Major Roads
('nguyen_van_linh', 'Nguyễn Văn Linh', 'Nguyen Van Linh Boulevard',
 ARRAY['Nguyễn Văn Linh', 'NVL', 'Đường Nguyễn Văn Linh'],
 (SELECT id FROM master_districts WHERE code = 'Q7'),
 'main_road', 'large', 5, 'Trục đường chính nối Quận 7 với trung tâm',
 ARRAY['Phú Mỹ Hưng', 'Lotte Mart', 'Crescent Mall'],
 1),

('xa_lo_ha_noi', 'Xa lộ Hà Nội', 'Hanoi Highway',
 ARRAY['Xa lộ Hà Nội', 'XLHN', 'Xa lộ HN'],
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'highway', 'large', 5, 'Xa lộ chính nối trung tâm với Quận 2, 9, Thủ Đức',
 ARRAY['Masteri Thảo Điền', 'The Vista', 'GIGAMALL'],
 2),

('nguyen_huu_canh', 'Nguyễn Hữu Cảnh', 'Nguyen Huu Canh Street',
 ARRAY['Nguyễn Hữu Cảnh', 'NHC', 'Đường Nguyễn Hữu Cảnh'],
 (SELECT id FROM master_districts WHERE code = 'QBTh'),
 'main_road', 'large', 5, 'Đường ven sông Sài Gòn, nối Bình Thạnh với Quận 1',
 ARRAY['Saigon Pearl', 'Sunwah Pearl', 'Landmark 81'],
 3),

('le_van_luong', 'Lê Văn Lương', 'Le Van Luong Street',
 ARRAY['Lê Văn Lương', 'LVL', 'Đường Lê Văn Lương'],
 (SELECT id FROM master_districts WHERE code = 'Q7'),
 'main_road', 'large', 5, 'Đường chính trong khu đô thị Phú Mỹ Hưng',
 ARRAY['Phú Mỹ Hưng', 'Crescent Mall', 'SC VivoCity'],
 4),

('ton_duc_thang', 'Tôn Đức Thắng', 'Ton Duc Thang Street',
 ARRAY['Tôn Đức Thắng', 'TĐT', 'Đường Tôn Đức Thắng'],
 (SELECT id FROM master_districts WHERE code = 'Q1'),
 'main_road', 'large', 5, 'Đường ven sông trong trung tâm Quận 1',
 ARRAY['Vinhomes Golden River', 'Bến Bạch Đằng', 'Nhà hát'],
 5),

('vo_van_kiet', 'Võ Văn Kiệt', 'Vo Van Kiet Boulevard',
 ARRAY['Võ Văn Kiệt', 'VVK', 'Đường Võ Văn Kiệt'],
 (SELECT id FROM master_districts WHERE code = 'Q1'),
 'main_road', 'large', 5, 'Trục đường chính dọc kênh Nhiêu Lộc',
 ARRAY['Chợ Bến Thành', 'Bến xe An Sương'],
 6),

('cong_hoa', 'Cộng Hòa', 'Cong Hoa Street',
 ARRAY['Cộng Hòa', 'CH', 'Đường Cộng Hòa'],
 (SELECT id FROM master_districts WHERE code = 'QTD'),
 'main_road', 'large', 5, 'Đường chính gần sân bay Tân Sơn Nhất',
 ARRAY['Sân bay Tân Sơn Nhất', 'Plaza'],
 7),

('hoang_van_thu', 'Hoàng Văn Thụ', 'Hoang Van Thu Street',
 ARRAY['Hoàng Văn Thụ', 'HVT', 'Đường Hoàng Văn Thụ'],
 (SELECT id FROM master_districts WHERE code = 'QTD'),
 'main_road', 'medium', 4, 'Đường trung tâm Quận Tân Bình',
 ARRAY['Flemington', 'Sân bay'],
 8),

('tran_hung_dao', 'Trần Hưng Đạo', 'Tran Hung Dao Street',
 ARRAY['Trần Hưng Đạo', 'THĐ', 'Đường Trần Hưng Đạo'],
 (SELECT id FROM master_districts WHERE code = 'Q1'),
 'main_road', 'large', 5, 'Đường chính Quận 1, nối Bến Thành với Q5',
 ARRAY['Chợ Bến Thành', 'Phố đi bộ Bùi Viện'],
 9),

('nguyen_thi_minh_khai', 'Nguyễn Thị Minh Khai', 'Nguyen Thi Minh Khai Street',
 ARRAY['Nguyễn Thị Minh Khai', 'NTMK', 'Đường Nguyễn Thị Minh Khai'],
 (SELECT id FROM master_districts WHERE code = 'Q1'),
 'main_road', 'large', 4, 'Đường kết nối Quận 1 và Quận 3',
 ARRAY['Nhà thờ Đức Bà', 'Bưu điện Sài Gòn'],
 10),

('mai_chi_tho', 'Mai Chí Thọ', 'Mai Chi Tho Boulevard',
 ARRAY['Mai Chí Thọ', 'MCT', 'Đường Mai Chí Thọ'],
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'main_road', 'large', 5, 'Đại lộ kết nối Quận 2 với trung tâm',
 ARRAY['Empire City', 'The Metropole', 'Sala'],
 11),

('nguyen_duy_trinh', 'Nguyễn Duy Trinh', 'Nguyen Duy Trinh Street',
 ARRAY['Nguyễn Duy Trinh', 'NĐT', 'Đường Nguyễn Duy Trinh'],
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'secondary_road', 'medium', 4, 'Đường kết nối các khu dân cư Quận 2',
 ARRAY['Gem Riverside', 'Thảo Điền Village'],
 12),

('pham_van_dong', 'Phạm Văn Đồng', 'Pham Van Dong Boulevard',
 ARRAY['Phạm Văn Đồng', 'PVĐ', 'Đường Phạm Văn Đồng'],
 (SELECT id FROM master_districts WHERE code = 'TPTD'),
 'main_road', 'large', 5, 'Đại lộ chính kết nối Thủ Đức',
 ARRAY['KCN Thủ Đức', 'Gigamall'],
 13),

('dien_bien_phu', 'Điện Biên Phủ', 'Dien Bien Phu Street',
 ARRAY['Điện Biên Phủ', 'ĐBP', 'Đường Điện Biên Phủ'],
 (SELECT id FROM master_districts WHERE code = 'QBTh'),
 'main_road', 'large', 5, 'Đường kết nối trung tâm với Bình Thạnh',
 ARRAY['Vinhomes Central Park', 'Vincom Landmark 81'],
 14),

('tran_quang_khai', 'Trần Quang Khải', 'Tran Quang Khai Street',
 ARRAY['Trần Quang Khải', 'TQK', 'Đường Trần Quang Khải'],
 (SELECT id FROM master_districts WHERE code = 'Q1'),
 'secondary_road', 'medium', 3, 'Đường nối Quận 1 với Bình Thạnh',
 ARRAY['Chợ Tân Định'],
 15)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- BUILDING FEATURES (Tiện ích chung tòa nhà)
-- ============================================================

INSERT INTO master_building_features (code, name_vi, name_en, aliases, category, premium_level, icon, description, sort_order) VALUES
-- Security Features
('security_24_7', 'Bảo vệ 24/7', '24/7 Security Guard',
 ARRAY['bảo vệ 24/7', '24/7 security', 'security guard', 'bảo vệ'],
 'security', 1, 'security', 'Bảo vệ chuyên nghiệp túc trực 24/7', 1),

('cctv', 'Camera an ninh', 'CCTV Surveillance',
 ARRAY['camera an ninh', 'CCTV', 'camera giám sát', 'surveillance'],
 'security', 1, 'videocam', 'Hệ thống camera giám sát toàn bộ tòa nhà', 2),

('access_card', 'Thẻ từ ra vào', 'Access Card System',
 ARRAY['thẻ từ', 'access card', 'key card', 'thẻ ra vào'],
 'security', 2, 'credit_card', 'Hệ thống thẻ từ kiểm soát ra vào', 3),

('fingerprint_lock', 'Khóa vân tay', 'Fingerprint Lock',
 ARRAY['khóa vân tay', 'fingerprint', 'vân tay', 'smart lock'],
 'security', 3, 'fingerprint', 'Khóa thông minh vân tay hoặc mật mã', 4),

-- Recreation Features
('infinity_pool', 'Hồ bơi vô cực', 'Infinity Pool',
 ARRAY['hồ bơi vô cực', 'infinity pool', 'bể bơi vô cực'],
 'recreation', 3, 'pool', 'Hồ bơi vô cực cao cấp', 5),

('tennis_court', 'Sân tennis', 'Tennis Court',
 ARRAY['sân tennis', 'tennis court', 'tennis'],
 'recreation', 2, 'sports_tennis', 'Sân tennis chuyên nghiệp', 6),

('basketball_court', 'Sân bóng rổ', 'Basketball Court',
 ARRAY['sân bóng rổ', 'basketball court', 'bóng rổ'],
 'recreation', 2, 'sports_basketball', 'Sân bóng rổ', 7),

('yoga_room', 'Phòng yoga', 'Yoga Room',
 ARRAY['phòng yoga', 'yoga room', 'yoga studio'],
 'recreation', 2, 'self_improvement', 'Phòng tập yoga', 8),

('jogging_track', 'Đường chạy bộ', 'Jogging Track',
 ARRAY['đường chạy bộ', 'jogging track', 'running track'],
 'recreation', 2, 'directions_run', 'Đường chạy bộ trong khuôn viên', 9),

('golf_course', 'Sân golf', 'Golf Course',
 ARRAY['sân golf', 'golf course', 'golf'],
 'recreation', 3, 'golf_course', 'Sân golf hoặc khu luyện tập golf', 10),

-- Services
('concierge', 'Lễ tân/Concierge', 'Concierge Service',
 ARRAY['concierge', 'lễ tân', 'reception', 'front desk'],
 'services', 2, 'concierge', 'Dịch vụ lễ tân và tiện ích 24/7', 11),

('housekeeping', 'Dịch vụ vệ sinh', 'Housekeeping Service',
 ARRAY['dịch vụ vệ sinh', 'housekeeping', 'cleaning service'],
 'services', 2, 'cleaning_services', 'Dịch vụ vệ sinh định kỳ', 12),

('laundry', 'Giặt là', 'Laundry Service',
 ARRAY['giặt là', 'laundry', 'giặt ủi'],
 'services', 2, 'local_laundry_service', 'Dịch vụ giặt là', 13),

('shuttle_bus', 'Xe đưa đón', 'Shuttle Bus',
 ARRAY['xe đưa đón', 'shuttle bus', 'xe bus'],
 'services', 2, 'directions_bus', 'Xe đưa đón cư dân', 14),

('pet_care', 'Dịch vụ chăm sóc thú cưng', 'Pet Care Service',
 ARRAY['chăm sóc thú cưng', 'pet care', 'pet grooming'],
 'services', 2, 'pets', 'Dịch vụ chăm sóc thú cưng', 15),

-- Facilities
('shopping_mall', 'Trung tâm thương mại', 'Shopping Mall',
 ARRAY['trung tâm thương mại', 'shopping mall', 'TTTM', 'mall'],
 'facilities', 3, 'shopping_bag', 'Trung tâm thương mại trong dự án', 16),

('supermarket', 'Siêu thị', 'Supermarket',
 ARRAY['siêu thị', 'supermarket', 'mini mart'],
 'facilities', 2, 'local_grocery_store', 'Siêu thị tiện lợi', 17),

('restaurant', 'Nhà hàng', 'Restaurant',
 ARRAY['nhà hàng', 'restaurant', 'food court'],
 'facilities', 2, 'restaurant', 'Nhà hàng và khu ẩm thực', 18),

('coworking', 'Không gian làm việc chung', 'Co-working Space',
 ARRAY['co-working', 'không gian làm việc', 'coworking space'],
 'facilities', 2, 'work', 'Không gian làm việc chung', 19),

('library', 'Thư viện', 'Library',
 ARRAY['thư viện', 'library', 'reading room'],
 'facilities', 2, 'local_library', 'Thư viện và phòng đọc sách', 20),

-- Utilities
('backup_power', 'Máy phát điện dự phòng', 'Backup Generator',
 ARRAY['máy phát điện', 'generator', 'backup power', 'điện dự phòng'],
 'utilities', 1, 'power', 'Máy phát điện dự phòng', 21),

('water_treatment', 'Hệ thống lọc nước', 'Water Treatment System',
 ARRAY['lọc nước', 'water filter', 'water treatment'],
 'utilities', 2, 'water_drop', 'Hệ thống lọc nước tập trung', 22),

('waste_management', 'Xử lý rác thải', 'Waste Management',
 ARRAY['xử lý rác', 'waste management', 'garbage disposal'],
 'utilities', 1, 'delete', 'Hệ thống xử lý rác thải hiện đại', 23),

('solar_panel', 'Năng lượng mặt trời', 'Solar Panel',
 ARRAY['năng lượng mặt trời', 'solar panel', 'solar power'],
 'utilities', 3, 'wb_sunny', 'Hệ thống điện năng lượng mặt trời', 24),

('smart_home', 'Hệ thống nhà thông minh', 'Smart Home System',
 ARRAY['smart home', 'nhà thông minh', 'home automation'],
 'utilities', 3, 'home_automation', 'Hệ thống điều khiển nhà thông minh', 25)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- VIEWS (Hướng nhìn)
-- ============================================================

INSERT INTO master_views (code, name_vi, name_en, aliases, category, desirability_score, icon, description, sort_order) VALUES
('river_view', 'View sông', 'River View',
 ARRAY['view sông', 'river view', 'nhìn ra sông', 'hướng sông'],
 'natural', 9, 'water', 'Nhìn ra sông Sài Gòn', 1),

('city_view', 'View thành phố', 'City View',
 ARRAY['view thành phố', 'city view', 'nhìn ra thành phố', 'city skyline'],
 'urban', 8, 'location_city', 'Nhìn ra toàn cảnh thành phố', 2),

('park_view', 'View công viên', 'Park View',
 ARRAY['view công viên', 'park view', 'nhìn ra công viên', 'garden view'],
 'natural', 8, 'park', 'Nhìn ra công viên xanh mát', 3),

('sea_view', 'View biển', 'Sea View',
 ARRAY['view biển', 'sea view', 'ocean view', 'nhìn ra biển'],
 'natural', 10, 'waves', 'Nhìn ra biển (hiếm ở TP.HCM)', 4),

('pool_view', 'View hồ bơi', 'Pool View',
 ARRAY['view hồ bơi', 'pool view', 'nhìn ra hồ bơi'],
 'mixed', 6, 'pool', 'Nhìn ra hồ bơi', 5),

('golf_view', 'View sân golf', 'Golf Course View',
 ARRAY['view sân golf', 'golf view', 'nhìn ra sân golf'],
 'natural', 8, 'golf_course', 'Nhìn ra sân golf', 6),

('landmark_view', 'View landmark', 'Landmark View',
 ARRAY['view landmark', 'landmark view', 'nhìn Landmark 81'],
 'urban', 9, 'location_on', 'Nhìn ra Landmark 81 hoặc tòa nhà nổi tiếng', 7),

('inner_view', 'View nội khu', 'Inner Courtyard View',
 ARRAY['view nội khu', 'inner view', 'courtyard view'],
 'mixed', 5, 'apartment', 'Nhìn vào khuôn viên nội bộ', 8),

('street_view', 'View đường', 'Street View',
 ARRAY['view đường', 'street view', 'nhìn ra đường'],
 'urban', 4, 'road', 'Nhìn ra đường phố', 9),

('mountain_view', 'View núi', 'Mountain View',
 ARRAY['view núi', 'mountain view', 'nhìn ra núi'],
 'natural', 7, 'terrain', 'Nhìn ra núi (hiếm ở TP.HCM)', 10)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- PROPERTY CONDITIONS (Tình trạng nhà)
-- ============================================================

INSERT INTO master_property_conditions (code, name_vi, name_en, aliases, typical_age_min, typical_age_max, condition_level, description, value_impact_percent, sort_order) VALUES
('brand_new', 'Hoàn toàn mới', 'Brand New',
 ARRAY['hoàn toàn mới', 'brand new', 'chưa qua sử dụng', 'new', 'nhà mới 100%'],
 0, 1, 5, 'Nhà hoàn toàn mới, chưa qua sử dụng', 10, 1),

('newly_built', 'Mới xây', 'Newly Built',
 ARRAY['mới xây', 'newly built', 'mới hoàn thiện', 'newly completed'],
 1, 2, 5, 'Nhà mới xây trong 1-2 năm', 5, 2),

('recently_renovated', 'Mới cải tạo', 'Recently Renovated',
 ARRAY['mới cải tạo', 'renovated', 'mới sửa chữa', 'refurbished'],
 NULL, NULL, 4, 'Nhà đã được cải tạo, sửa chữa gần đây', 3, 3),

('well_maintained', 'Được bảo dưỡng tốt', 'Well Maintained',
 ARRAY['bảo dưỡng tốt', 'well maintained', 'good condition'],
 3, 10, 4, 'Nhà được chủ sở hữu bảo dưỡng tốt', 0, 4),

('good_condition', 'Tình trạng tốt', 'Good Condition',
 ARRAY['tình trạng tốt', 'good condition', 'còn tốt'],
 5, 15, 3, 'Nhà trong tình trạng tốt, có thể vào ở ngay', -5, 5),

('average_condition', 'Tình trạng trung bình', 'Average Condition',
 ARRAY['tình trạng trung bình', 'average', 'fair condition'],
 10, 20, 3, 'Nhà trong tình trạng trung bình, cần sửa chữa nhỏ', -10, 6),

('needs_renovation', 'Cần cải tạo', 'Needs Renovation',
 ARRAY['cần cải tạo', 'needs renovation', 'cần sửa chữa', 'old'],
 15, NULL, 2, 'Nhà cần cải tạo, sửa chữa đáng kể', -20, 7),

('needs_major_repair', 'Cần sửa chữa lớn', 'Needs Major Repair',
 ARRAY['cần sửa chữa lớn', 'major repair needed', 'run down'],
 20, NULL, 1, 'Nhà cần sửa chữa lớn, có thể cần xây mới', -30, 8),

('under_construction', 'Đang xây dựng', 'Under Construction',
 ARRAY['đang xây dựng', 'under construction', 'đang hoàn thiện'],
 0, 0, 3, 'Nhà đang trong quá trình xây dựng', -10, 9),

('off_plan', 'Bán giấy tờ', 'Off-Plan',
 ARRAY['bán giấy tờ', 'off-plan', 'hình thức', 'bán dự án'],
 0, 0, 3, 'Bán theo giấy tờ, chưa bàn giao', -15, 10)
ON CONFLICT (code) DO NOTHING;

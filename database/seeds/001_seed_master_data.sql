-- Seed Data for Master Data Tables
-- Description: Initial reference data for extraction service

-- ============================================================
-- DISTRICTS (Ho Chi Minh City)
-- ============================================================

INSERT INTO master_districts (code, name_vi, name_en, city, aliases, latitude, longitude, sort_order) VALUES
('Q1', 'Quận 1', 'District 1', 'Ho Chi Minh City', ARRAY['Q1', 'Q.1', 'quận 1', 'quan 1', 'District 1'], 10.7756, 106.7019, 1),
('Q2', 'Quận 2', 'District 2', 'Ho Chi Minh City', ARRAY['Q2', 'Q.2', 'quận 2', 'quan 2', 'District 2', 'Thủ Đức'], 10.7875, 106.7399, 2),
('Q3', 'Quận 3', 'District 3', 'Ho Chi Minh City', ARRAY['Q3', 'Q.3', 'quận 3', 'quan 3', 'District 3'], 10.7866, 106.6828, 3),
('Q4', 'Quận 4', 'District 4', 'Ho Chi Minh City', ARRAY['Q4', 'Q.4', 'quận 4', 'quan 4', 'District 4'], 10.7574, 106.7035, 4),
('Q5', 'Quận 5', 'District 5', 'Ho Chi Minh City', ARRAY['Q5', 'Q.5', 'quận 5', 'quan 5', 'District 5', 'Chợ Lớn'], 10.7542, 106.6665, 5),
('Q6', 'Quận 6', 'District 6', 'Ho Chi Minh City', ARRAY['Q6', 'Q.6', 'quận 6', 'quan 6', 'District 6'], 10.7476, 106.6345, 6),
('Q7', 'Quận 7', 'District 7', 'Ho Chi Minh City', ARRAY['Q7', 'Q.7', 'quận 7', 'quan 7', 'District 7', 'Phú Mỹ Hưng'], 10.7329, 106.7197, 7),
('Q8', 'Quận 8', 'District 8', 'Ho Chi Minh City', ARRAY['Q8', 'Q.8', 'quận 8', 'quan 8', 'District 8'], 10.7387, 106.6761, 8),
('Q9', 'Quận 9', 'District 9', 'Ho Chi Minh City', ARRAY['Q9', 'Q.9', 'quận 9', 'quan 9', 'District 9'], 10.8358, 106.8024, 9),
('Q10', 'Quận 10', 'District 10', 'Ho Chi Minh City', ARRAY['Q10', 'Q.10', 'quận 10', 'quan 10', 'District 10'], 10.7733, 106.6700, 10),
('Q11', 'Quận 11', 'District 11', 'Ho Chi Minh City', ARRAY['Q11', 'Q.11', 'quận 11', 'quan 11', 'District 11'], 10.7633, 106.6508, 11),
('Q12', 'Quận 12', 'District 12', 'Ho Chi Minh City', ARRAY['Q12', 'Q.12', 'quận 12', 'quan 12', 'District 12'], 10.8538, 106.6699, 12),
('QBT', 'Quận Bình Tân', 'Binh Tan District', 'Ho Chi Minh City', ARRAY['Bình Tân', 'Binh Tan', 'QBT', 'Q. Bình Tân'], 10.7403, 106.6054, 13),
('QBTh', 'Quận Bình Thạnh', 'Binh Thanh District', 'Ho Chi Minh City', ARRAY['Bình Thạnh', 'Binh Thanh', 'QBTh', 'Q. Bình Thạnh'], 10.8051, 106.7102, 14),
('QGV', 'Quận Gò Vấp', 'Go Vap District', 'Ho Chi Minh City', ARRAY['Gò Vấp', 'Go Vap', 'QGV', 'Q. Gò Vấp'], 10.8377, 106.6670, 15),
('QPN', 'Quận Phú Nhuận', 'Phu Nhuan District', 'Ho Chi Minh City', ARRAY['Phú Nhuận', 'Phu Nhuan', 'QPN', 'Q. Phú Nhuận'], 10.7990, 106.6839, 16),
('QTD', 'Quận Tân Bình', 'Tan Binh District', 'Ho Chi Minh City', ARRAY['Tân Bình', 'Tan Binh', 'QTB', 'Q. Tân Bình'], 10.8006, 106.6532, 17),
('QTP', 'Quận Tân Phú', 'Tan Phu District', 'Ho Chi Minh City', ARRAY['Tân Phú', 'Tan Phu', 'QTP', 'Q. Tân Phú'], 10.7870, 106.6256, 18),
('TPTD', 'Thành phố Thủ Đức', 'Thu Duc City', 'Ho Chi Minh City', ARRAY['Thủ Đức', 'Thu Duc', 'TPTD', 'TP. Thủ Đức', 'Q2', 'Q9', 'QTĐ'], 10.8519, 106.7637, 19),
('HBC', 'Huyện Bình Chánh', 'Binh Chanh District', 'Ho Chi Minh City', ARRAY['Bình Chánh', 'Binh Chanh', 'HBC', 'H. Bình Chánh'], 10.7178, 106.6029, 20),
('HCC', 'Huyện Củ Chi', 'Cu Chi District', 'Ho Chi Minh City', ARRAY['Củ Chi', 'Cu Chi', 'HCC', 'H. Củ Chi'], 10.9727, 106.4937, 21),
('HHM', 'Huyện Hóc Môn', 'Hoc Mon District', 'Ho Chi Minh City', ARRAY['Hóc Môn', 'Hoc Mon', 'HHM', 'H. Hóc Môn'], 10.8814, 106.5926, 22),
('HNB', 'Huyện Nhà Bè', 'Nha Be District', 'Ho Chi Minh City', ARRAY['Nhà Bè', 'Nha Be', 'HNB', 'H. Nhà Bè'], 10.6909, 106.7273, 23),
('HCG', 'Huyện Cần Giờ', 'Can Gio District', 'Ho Chi Minh City', ARRAY['Cần Giờ', 'Can Gio', 'HCG', 'H. Cần Giờ'], 10.4058, 106.9524, 24)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- PROPERTY TYPES
-- ============================================================

INSERT INTO master_property_types (code, name_vi, name_en, aliases, category, typical_min_area, typical_max_area, typical_min_bedrooms, typical_max_bedrooms, icon, description, sort_order) VALUES
('apartment', 'Căn hộ', 'Apartment', ARRAY['căn hộ', 'chung cư', 'apartment', 'condo', 'flat'], 'residential', 20, 500, 1, 5, 'building', 'Căn hộ chung cư cao tầng', 1),
('house', 'Nhà phố', 'Townhouse', ARRAY['nhà phố', 'nhà riêng', 'townhouse', 'house'], 'residential', 40, 300, 2, 8, 'home', 'Nhà phố liền kề', 2),
('villa', 'Biệt thự', 'Villa', ARRAY['biệt thự', 'villa', 'mansion'], 'residential', 100, 1000, 3, 10, 'villa', 'Biệt thự độc lập', 3),
('land', 'Đất', 'Land', ARRAY['đất', 'land', 'plot'], 'land', 50, 10000, 0, 0, 'terrain', 'Đất nền', 4),
('office', 'Văn phòng', 'Office', ARRAY['văn phòng', 'office', 'commercial space'], 'commercial', 30, 1000, 0, 0, 'business', 'Văn phòng thương mại', 5),
('shophouse', 'Nhà mặt tiền', 'Shophouse', ARRAY['nhà mặt tiền', 'shophouse', 'shop'], 'commercial', 50, 500, 0, 5, 'store', 'Nhà mặt tiền kinh doanh', 6),
('penthouse', 'Penthouse', 'Penthouse', ARRAY['penthouse', 'căn hộ cao cấp'], 'residential', 100, 800, 3, 6, 'apartment', 'Căn hộ cao cấp tầng thượng', 7),
('studio', 'Studio', 'Studio', ARRAY['studio', 'căn hộ studio'], 'residential', 20, 60, 0, 1, 'single_bed', 'Căn hộ studio', 8)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- TRANSACTION TYPES
-- ============================================================

INSERT INTO master_transaction_types (code, name_vi, name_en, aliases, sort_order) VALUES
('sale', 'Bán', 'For Sale', ARRAY['bán', 'cần bán', 'đang bán', 'for sale', 'sale'], 1),
('rent', 'Cho thuê', 'For Rent', ARRAY['cho thuê', 'cần cho thuê', 'thuê', 'for rent', 'rent', 'lease'], 2)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- AMENITIES
-- ============================================================

INSERT INTO master_amenities (code, name_vi, name_en, aliases, category, icon, description, sort_order) VALUES
-- Building Amenities
('parking', 'Chỗ đậu xe', 'Parking', ARRAY['parking', 'chỗ đậu xe', 'bãi đỗ xe', 'garage', 'car park'], 'building_amenity', 'local_parking', 'Chỗ đậu xe trong tòa nhà', 1),
('elevator', 'Thang máy', 'Elevator', ARRAY['elevator', 'thang máy', 'lift'], 'building_amenity', 'elevator', 'Thang máy', 2),
('swimming_pool', 'Hồ bơi', 'Swimming Pool', ARRAY['swimming pool', 'hồ bơi', 'bể bơi', 'pool'], 'building_amenity', 'pool', 'Hồ bơi', 3),
('gym', 'Phòng gym', 'Gym', ARRAY['gym', 'phòng gym', 'fitness', 'fitness center'], 'building_amenity', 'fitness_center', 'Phòng tập gym', 4),
('security', 'Bảo vệ 24/7', '24/7 Security', ARRAY['security', 'bảo vệ', 'an ninh', '24/7', 'guard'], 'building_amenity', 'security', 'Bảo vệ 24/7', 5),
('playground', 'Khu vui chơi trẻ em', 'Playground', ARRAY['playground', 'khu vui chơi', 'sân chơi', 'khu vui chơi trẻ em'], 'building_amenity', 'playground', 'Khu vui chơi trẻ em', 6),
('garden', 'Vườn', 'Garden', ARRAY['garden', 'vườn', 'công viên', 'park'], 'building_amenity', 'local_florist', 'Vườn/công viên', 7),
('bbq_area', 'Khu BBQ', 'BBQ Area', ARRAY['bbq', 'khu bbq', 'nướng', 'bbq area'], 'building_amenity', 'outdoor_grill', 'Khu BBQ', 8),
('clubhouse', 'Clubhouse', 'Clubhouse', ARRAY['clubhouse', 'nhà câu lạc bộ', 'community center'], 'building_amenity', 'home', 'Nhà câu lạc bộ', 9),
('sauna', 'Sauna', 'Sauna', ARRAY['sauna', 'phòng xông hơi', 'steam room'], 'building_amenity', 'spa', 'Phòng xông hơi', 10),

-- Neighborhood Amenities
('near_school', 'Gần trường học', 'Near School', ARRAY['near school', 'gần trường', 'trường học'], 'neighborhood_amenity', 'school', 'Gần trường học', 11),
('near_hospital', 'Gần bệnh viện', 'Near Hospital', ARRAY['near hospital', 'gần bệnh viện', 'bệnh viện'], 'neighborhood_amenity', 'local_hospital', 'Gần bệnh viện', 12),
('near_supermarket', 'Gần siêu thị', 'Near Supermarket', ARRAY['near supermarket', 'gần siêu thị', 'siêu thị'], 'neighborhood_amenity', 'shopping_cart', 'Gần siêu thị', 13),
('near_metro', 'Gần Metro', 'Near Metro', ARRAY['near metro', 'gần metro', 'metro', 'gần tàu điện'], 'neighborhood_amenity', 'directions_subway', 'Gần Metro', 14),
('near_bus_stop', 'Gần trạm xe buýt', 'Near Bus Stop', ARRAY['near bus stop', 'gần trạm xe buýt', 'xe buýt'], 'neighborhood_amenity', 'directions_bus', 'Gần trạm xe buýt', 15),

-- Property Features
('balcony', 'Ban công', 'Balcony', ARRAY['balcony', 'ban công'], 'feature', 'balcony', 'Ban công', 16),
('terrace', 'Sân thượng', 'Terrace', ARRAY['terrace', 'sân thượng', 'rooftop'], 'feature', 'roofing', 'Sân thượng', 17),
('air_conditioning', 'Điều hòa', 'Air Conditioning', ARRAY['air conditioning', 'điều hòa', 'AC', 'air-con'], 'feature', 'ac_unit', 'Điều hòa', 18),
('furnished', 'Nội thất', 'Furnished', ARRAY['furnished', 'nội thất', 'furniture'], 'feature', 'chair', 'Có nội thất', 19),
('pet_friendly', 'Cho phép nuôi thú cưng', 'Pet Friendly', ARRAY['pet friendly', 'cho phép thú cưng', 'nuôi chó mèo'], 'feature', 'pets', 'Cho phép nuôi thú cưng', 20)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- FURNITURE TYPES
-- ============================================================

INSERT INTO master_furniture_types (code, name_vi, name_en, aliases, level, sort_order) VALUES
('none', 'Không nội thất', 'Unfurnished', ARRAY['không', 'không nội thất', 'unfurnished', 'bare'], 0, 1),
('basic', 'Nội thất cơ bản', 'Basic Furniture', ARRAY['cơ bản', 'nội thất cơ bản', 'basic', 'partial'], 1, 2),
('full', 'Nội thất đầy đủ', 'Fully Furnished', ARRAY['full', 'đầy đủ', 'nội thất đầy đủ', 'fully furnished', 'furnished'], 2, 3),
('luxury', 'Nội thất cao cấp', 'Luxury Furniture', ARRAY['cao cấp', 'nội thất cao cấp', 'luxury', 'premium'], 3, 4)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- DIRECTIONS
-- ============================================================

INSERT INTO master_directions (code, name_vi, name_en, aliases, degrees, feng_shui_score, sort_order) VALUES
('N', 'Bắc', 'North', ARRAY['Bắc', 'North', 'N'], 0, 3, 1),
('NE', 'Đông Bắc', 'Northeast', ARRAY['Đông Bắc', 'Northeast', 'NE'], 45, 4, 2),
('E', 'Đông', 'East', ARRAY['Đông', 'East', 'E'], 90, 5, 3),
('SE', 'Đông Nam', 'Southeast', ARRAY['Đông Nam', 'Southeast', 'SE'], 135, 5, 4),
('S', 'Nam', 'South', ARRAY['Nam', 'South', 'S'], 180, 4, 5),
('SW', 'Tây Nam', 'Southwest', ARRAY['Tây Nam', 'Southwest', 'SW'], 225, 3, 6),
('W', 'Tây', 'West', ARRAY['Tây', 'West', 'W'], 270, 2, 7),
('NW', 'Tây Bắc', 'Northwest', ARRAY['Tây Bắc', 'Northwest', 'NW'], 315, 3, 8)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- LEGAL STATUS
-- ============================================================

INSERT INTO master_legal_status (code, name_vi, name_en, aliases, trust_level, description, sort_order) VALUES
('red_book', 'Sổ đỏ', 'Red Book', ARRAY['sổ đỏ', 'red book', 'sổ đỏ chính chủ'], 5, 'Giấy chứng nhận quyền sử dụng đất (cao nhất)', 1),
('pink_book', 'Sổ hồng', 'Pink Book', ARRAY['sổ hồng', 'pink book', 'sổ hồng chính chủ'], 5, 'Giấy chứng nhận quyền sở hữu nhà và quyền sử dụng đất', 2),
('sale_contract', 'Hợp đồng mua bán', 'Sale Contract', ARRAY['hợp đồng mua bán', 'sale contract', 'hợp đồng'], 3, 'Hợp đồng mua bán có công chứng', 3),
('waiting', 'Đang chờ sổ', 'Waiting for Certificate', ARRAY['đang chờ sổ', 'chờ sổ', 'waiting'], 2, 'Đang làm thủ tục xin sổ', 4),
('none', 'Chưa có sổ', 'No Certificate', ARRAY['chưa có sổ', 'không có sổ', 'no certificate'], 1, 'Chưa có giấy tờ pháp lý', 5)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- PRICE RANGES (Sample data for District 1, 7 - will be updated dynamically)
-- ============================================================

INSERT INTO master_price_ranges (district_id, property_type_id, min_price_per_m2, avg_price_per_m2, max_price_per_m2, min_total_price, avg_total_price, max_total_price, sample_count) VALUES
-- District 1 - Apartment
((SELECT id FROM master_districts WHERE code = 'Q1'), (SELECT id FROM master_property_types WHERE code = 'apartment'), 100000000, 150000000, 300000000, 2000000000, 10000000000, 50000000000, 100),
-- District 7 - Apartment
((SELECT id FROM master_districts WHERE code = 'Q7'), (SELECT id FROM master_property_types WHERE code = 'apartment'), 50000000, 80000000, 150000000, 1500000000, 5000000000, 20000000000, 150),
-- District 7 - Villa
((SELECT id FROM master_districts WHERE code = 'Q7'), (SELECT id FROM master_property_types WHERE code = 'villa'), 60000000, 100000000, 200000000, 10000000000, 30000000000, 100000000000, 50),
-- District 2 - Apartment
((SELECT id FROM master_districts WHERE code = 'Q2'), (SELECT id FROM master_property_types WHERE code = 'apartment'), 60000000, 90000000, 180000000, 2000000000, 7000000000, 30000000000, 120)
ON CONFLICT (district_id, property_type_id) DO NOTHING;

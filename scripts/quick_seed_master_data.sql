-- Quick Seed Master Data (Schema-Compatible)
-- Matches actual PostgreSQL schema from migrations 006-007

-- ============================================================
-- 1. DISTRICTS (Ho Chi Minh City)
-- ============================================================
INSERT INTO master_districts (code, name_vi, name_en, city, aliases, latitude, longitude) VALUES
('Q1', 'Quận 1', 'District 1', 'Ho Chi Minh City', ARRAY['Q1', 'Quận 1', 'District 1', 'D1'], 10.776889, 106.700806),
('Q2', 'Quận 2 (Thủ Đức)', 'District 2 (Thu Duc)', 'Ho Chi Minh City', ARRAY['Q2', 'Quận 2', 'District 2', 'Thủ Đức', 'Thu Duc', 'Thảo Điền'], 10.787932, 106.740892),
('Q3', 'Quận 3', 'District 3', 'Ho Chi Minh City', ARRAY['Q3', 'Quận 3', 'District 3'], 10.786131, 106.688087),
('Q4', 'Quận 4', 'District 4', 'Ho Chi Minh City', ARRAY['Q4', 'Quận 4', 'District 4'], 10.762252, 106.704861),
('Q5', 'Quận 5', 'District 5', 'Ho Chi Minh City', ARRAY['Q5', 'Quận 5', 'District 5', 'Chợ Lớn'], 10.756389, 106.668029),
('Q6', 'Quận 6', 'District 6', 'Ho Chi Minh City', ARRAY['Q6', 'Quận 6', 'District 6'], 10.738469, 106.638161),
('Q7', 'Quận 7', 'District 7', 'Ho Chi Minh City', ARRAY['Q7', 'Quận 7', 'District 7', 'Phú Mỹ Hưng', 'PMH'], 10.734046, 106.721332),
('Q8', 'Quận 8', 'District 8', 'Ho Chi Minh City', ARRAY['Q8', 'Quận 8', 'District 8'], 10.724512, 106.668638),
('Q9', 'Quận 9 (Thủ Đức)', 'District 9 (Thu Duc)', 'Ho Chi Minh City', ARRAY['Q9', 'Quận 9', 'District 9'], 10.838676, 106.837425),
('Q10', 'Quận 10', 'District 10', 'Ho Chi Minh City', ARRAY['Q10', 'Quận 10', 'District 10'], 10.772652, 106.668667),
('Q11', 'Quận 11', 'District 11', 'Ho Chi Minh City', ARRAY['Q11', 'Quận 11', 'District 11'], 10.762622, 106.648194),
('Q12', 'Quận 12', 'District 12', 'Ho Chi Minh City', ARRAY['Q12', 'Quận 12', 'District 12'], 10.87149, 106.698067),
('BT', 'Quận Bình Thạnh', 'Binh Thanh District', 'Ho Chi Minh City', ARRAY['BT', 'Bình Thạnh', 'Binh Thanh', 'Q Bình Thạnh'], 10.799851, 106.713701),
('TB', 'Quận Tân Bình', 'Tan Binh District', 'Ho Chi Minh City', ARRAY['TB', 'Tân Bình', 'Tan Binh', 'Q Tân Bình'], 10.799644, 106.654082),
('TP', 'Quận Tân Phú', 'Tan Phu District', 'Ho Chi Minh City', ARRAY['TP', 'Tân Phú', 'Tan Phu', 'Q Tân Phú'], 10.78375, 106.627478),
('PN', 'Quận Phú Nhuận', 'Phu Nhuan District', 'Ho Chi Minh City', ARRAY['PN', 'Phú Nhuận', 'Phu Nhuan', 'Q Phú Nhuận'], 10.79726, 106.677907),
('GV', 'Quận Gò Vấp', 'Go Vap District', 'Ho Chi Minh City', ARRAY['GV', 'Gò Vấp', 'Go Vap', 'Q Gò Vấp'], 10.837881, 106.667667),
('TD', 'Thành phố Thủ Đức', 'Thu Duc City', 'Ho Chi Minh City', ARRAY['TD', 'Thủ Đức', 'Thu Duc', 'An Phú', 'Cát Lái'], 10.850100, 106.762630),
('BC', 'Huyện Bình Chánh', 'Binh Chanh District', 'Ho Chi Minh City', ARRAY['BC', 'Bình Chánh', 'Binh Chanh'], 10.730778, 106.585000),
('HC', 'Huyện Hóc Môn', 'Hoc Mon District', 'Ho Chi Minh City', ARRAY['HC', 'Hóc Môn', 'Hoc Mon'], 10.880361, 106.599556),
('NB', 'Huyện Nhà Bè', 'Nha Be District', 'Ho Chi Minh City', ARRAY['NB', 'Nhà Bè', 'Nha Be'], 10.700000, 106.728333),
('CC', 'Huyện Củ Chi', 'Cu Chi District', 'Ho Chi Minh City', ARRAY['CC', 'Củ Chi', 'Cu Chi'], 10.974167, 106.492778),
('CG', 'Huyện Cần Giờ', 'Can Gio District', 'Ho Chi Minh City', ARRAY['CG', 'Cần Giờ', 'Can Gio'], 10.407778, 106.959167)
ON CONFLICT (code) DO UPDATE SET
    name_vi = EXCLUDED.name_vi,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 2. PROPERTY TYPES
-- ============================================================
INSERT INTO master_property_types (code, name_vi, name_en, category, aliases, typical_min_area, typical_max_area, typical_min_bedrooms, typical_max_bedrooms) VALUES
('apartment', 'Căn hộ chung cư', 'Apartment', 'residential', ARRAY['căn hộ', 'chung cư', 'apartment', 'flat', 'condo'], 30, 150, 1, 4),
('house', 'Nhà riêng', 'House', 'residential', ARRAY['nhà', 'nhà riêng', 'nhà phố', 'house', 'townhouse'], 50, 300, 2, 6),
('villa', 'Biệt thự', 'Villa', 'residential', ARRAY['biệt thự', 'villa', 'mansion'], 200, 1000, 3, 8),
('penthouse', 'Căn hộ penthouse', 'Penthouse', 'residential', ARRAY['penthouse', 'sky villa'], 150, 500, 3, 6),
('duplex', 'Căn hộ duplex', 'Duplex', 'residential', ARRAY['duplex', 'căn hộ 2 tầng'], 100, 250, 2, 4),
('studio', 'Căn hộ studio', 'Studio', 'residential', ARRAY['studio', 'studio apartment'], 20, 45, 0, 1),
('land', 'Đất nền', 'Land', 'land', ARRAY['đất', 'đất nền', 'land', 'plot'], 50, 10000, 0, 0),
('shophouse', 'Nhà mặt tiền', 'Shophouse', 'commercial', ARRAY['nhà mặt tiền', 'nhà mặt phố', 'shophouse'], 50, 200, 2, 6),
('office', 'Văn phòng', 'Office', 'commercial', ARRAY['văn phòng', 'office'], 30, 500, 0, 0),
('warehouse', 'Kho xưởng', 'Warehouse', 'commercial', ARRAY['kho', 'xưởng', 'kho xưởng', 'warehouse'], 100, 5000, 0, 0)
ON CONFLICT (code) DO UPDATE SET
    name_vi = EXCLUDED.name_vi,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 3. TRANSACTION TYPES
-- ============================================================
INSERT INTO master_transaction_types (code, name_vi, name_en, aliases) VALUES
('sale', 'Bán', 'For Sale', ARRAY['bán', 'mua', 'sale', 'buy', 'sell']),
('rent', 'Cho thuê', 'For Rent', ARRAY['cho thuê', 'thuê', 'rent', 'rental', 'lease'])
ON CONFLICT (code) DO UPDATE SET
    name_vi = EXCLUDED.name_vi,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 4. AMENITIES
-- ============================================================
INSERT INTO master_amenities (code, name_vi, name_en, category, aliases) VALUES
-- Security
('security_24_7', 'Bảo vệ 24/7', '24/7 Security', 'security', ARRAY['bảo vệ', 'security', 'an ninh', 'guard']),
('cctv', 'Camera giám sát', 'CCTV', 'security', ARRAY['camera', 'CCTV', 'surveillance', 'camera an ninh']),
('access_card', 'Thẻ từ', 'Access Card', 'security', ARRAY['thẻ từ', 'access card', 'key card']),
-- Recreation
('swimming_pool', 'Hồ bơi', 'Swimming Pool', 'recreation', ARRAY['hồ bơi', 'bể bơi', 'pool', 'swimming pool']),
('gym', 'Phòng gym', 'Gym', 'recreation', ARRAY['gym', 'phòng tập', 'fitness', 'fitness center']),
('playground', 'Khu vui chơi trẻ em', 'Playground', 'recreation', ARRAY['sân chơi', 'khu vui chơi', 'playground']),
('garden', 'Vườn', 'Garden', 'recreation', ARRAY['vườn', 'sân vườn', 'garden', 'yard']),
-- Utilities
('parking', 'Chỗ đậu xe', 'Parking', 'utilities', ARRAY['chỗ đậu xe', 'bãi đỗ xe', 'parking', 'garage']),
('elevator', 'Thang máy', 'Elevator', 'utilities', ARRAY['thang máy', 'thang', 'elevator', 'lift']),
('air_conditioning', 'Điều hòa', 'Air Conditioning', 'utilities', ARRAY['điều hòa', 'máy lạnh', 'AC', 'air con']),
('balcony', 'Ban công', 'Balcony', 'utilities', ARRAY['ban công', 'balcony', 'terrace']),
('kitchen', 'Bếp', 'Kitchen', 'utilities', ARRAY['bếp', 'nhà bếp', 'kitchen']),
('furnished', 'Nội thất đầy đủ', 'Fully Furnished', 'utilities', ARRAY['nội thất', 'furnished', 'furniture', 'full nội thất'])
ON CONFLICT (code) DO UPDATE SET
    name_vi = EXCLUDED.name_vi,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 5. DIRECTIONS
-- ============================================================
INSERT INTO master_directions (code, name_vi, name_en, aliases) VALUES
('north', 'Hướng Bắc', 'North', ARRAY['bắc', 'north', 'N']),
('northeast', 'Hướng Đông Bắc', 'Northeast', ARRAY['đông bắc', 'northeast', 'NE']),
('east', 'Hướng Đông', 'East', ARRAY['đông', 'east', 'E']),
('southeast', 'Hướng Đông Nam', 'Southeast', ARRAY['đông nam', 'southeast', 'SE']),
('south', 'Hướng Nam', 'South', ARRAY['nam', 'south', 'S']),
('southwest', 'Hướng Tây Nam', 'Southwest', ARRAY['tây nam', 'southwest', 'SW']),
('west', 'Hướng Tây', 'West', ARRAY['tây', 'west', 'W']),
('northwest', 'Hướng Tây Bắc', 'Northwest', ARRAY['tây bắc', 'northwest', 'NW'])
ON CONFLICT (code) DO UPDATE SET
    name_vi = EXCLUDED.name_vi,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 6. LEGAL STATUS
-- ============================================================
INSERT INTO master_legal_status (code, name_vi, name_en, aliases) VALUES
('red_book', 'Sổ hồng/Sổ đỏ', 'Red Book (Full Ownership)', ARRAY['sổ hồng', 'sổ đỏ', 'red book', 'pink book']),
('sale_contract', 'Hợp đồng mua bán', 'Sale Contract', ARRAY['hợp đồng', 'contract', 'sale agreement']),
('waiting_red_book', 'Đang chờ sổ', 'Waiting for Red Book', ARRAY['chờ sổ', 'waiting', 'pending']),
('land_use_right', 'Giấy chứng nhận quyền sử dụng đất', 'Land Use Right Certificate', ARRAY['GCNQSD', 'giấy tờ đất', 'land use']),
('no_document', 'Không giấy tờ', 'No Legal Document', ARRAY['không giấy tờ', 'no document'])
ON CONFLICT (code) DO UPDATE SET
    name_vi = EXCLUDED.name_vi,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 7. FURNITURE TYPES
-- ============================================================
INSERT INTO master_furniture_types (code, name_vi, name_en, aliases) VALUES
('bare', 'Bàn giao thô', 'Bare/Unfurnished', ARRAY['thô', 'bare', 'unfurnished', 'empty', 'không nội thất']),
('basic', 'Nội thất cơ bản', 'Basic Furnishing', ARRAY['cơ bản', 'basic', 'simple']),
('full', 'Nội thất đầy đủ', 'Fully Furnished', ARRAY['đầy đủ', 'full', 'furnished', 'full nội thất']),
('luxury', 'Nội thất cao cấp', 'Luxury Furnishing', ARRAY['cao cấp', 'luxury', 'premium', 'high-end', 'sang trọng'])
ON CONFLICT (code) DO UPDATE SET
    name_vi = EXCLUDED.name_vi,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 8. VIEWS
-- ============================================================
INSERT INTO master_views (code, name_vi, name_en, category, aliases) VALUES
('river_view', 'View sông', 'River View', 'natural', ARRAY['sông', 'view sông', 'river', 'riverside']),
('sea_view', 'View biển', 'Sea View', 'natural', ARRAY['biển', 'view biển', 'sea', 'ocean', 'beach']),
('city_view', 'View thành phố', 'City View', 'urban', ARRAY['thành phố', 'view thành phố', 'city', 'skyline']),
('landmark_view', 'View địa danh', 'Landmark View', 'urban', ARRAY['địa danh', 'view đẹp', 'landmark', 'monument']),
('park_view', 'View công viên', 'Park View', 'natural', ARRAY['công viên', 'view công viên', 'park', 'garden']),
('golf_view', 'View sân golf', 'Golf Course View', 'natural', ARRAY['sân golf', 'golf', 'golf course']),
('inner_view', 'View nội khu', 'Inner View', 'mixed', ARRAY['nội khu', 'trong dự án', 'inner', 'courtyard']),
('street_view', 'View đường phố', 'Street View', 'urban', ARRAY['đường', 'view đường', 'street', 'road']),
('no_view', 'Không view đặc biệt', 'No Particular View', 'none', ARRAY['không view', 'no view', 'blocked'])
ON CONFLICT (code) DO UPDATE SET
    name_vi = EXCLUDED.name_vi,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================
-- 9. PROPERTY CONDITIONS
-- ============================================================
INSERT INTO master_property_conditions (code, name_vi, name_en, aliases) VALUES
('brand_new', 'Hoàn toàn mới', 'Brand New', ARRAY['mới 100%', 'brand new', 'new', 'hoàn toàn mới']),
('newly_built', 'Mới xây', 'Newly Built', ARRAY['mới xây', 'mới', 'newly built', 'recent']),
('excellent', 'Tình trạng tốt', 'Excellent Condition', ARRAY['tốt', 'excellent', 'perfect', 'hoàn hảo']),
('well_maintained', 'Được bảo trì tốt', 'Well Maintained', ARRAY['tốt', 'đẹp', 'well maintained', 'good']),
('average', 'Tình trạng trung bình', 'Average Condition', ARRAY['trung bình', 'bình thường', 'average', 'fair']),
('needs_cosmetic', 'Cần sửa chữa nhỏ', 'Needs Cosmetic Work', ARRAY['sửa nhỏ', 'cosmetic', 'minor repairs']),
('needs_renovation', 'Cần sửa chữa lớn', 'Needs Renovation', ARRAY['cần sửa chữa', 'cần tu sửa', 'renovation', 'fixer']),
('poor', 'Tình trạng xấu', 'Poor Condition', ARRAY['xấu', 'tệ', 'poor', 'bad']),
('under_construction', 'Đang xây dựng', 'Under Construction', ARRAY['đang xây', 'construction', 'building']),
('off_plan', 'Bán trên giấy', 'Off Plan/Pre-sale', ARRAY['bán giấy', 'off plan', 'pre-sale', 'presale'])
ON CONFLICT (code) DO UPDATE SET
    name_vi = EXCLUDED.name_vi,
    name_en = EXCLUDED.name_en,
    aliases = EXCLUDED.aliases,
    updated_at = CURRENT_TIMESTAMP;

-- Verify
SELECT
    'Districts' as table_name, COUNT(*) as count FROM master_districts
UNION ALL SELECT 'Property Types', COUNT(*) FROM master_property_types
UNION ALL SELECT 'Transaction Types', COUNT(*) FROM master_transaction_types
UNION ALL SELECT 'Amenities', COUNT(*) FROM master_amenities
UNION ALL SELECT 'Directions', COUNT(*) FROM master_directions
UNION ALL SELECT 'Legal Status', COUNT(*) FROM master_legal_status
UNION ALL SELECT 'Furniture Types', COUNT(*) FROM master_furniture_types
UNION ALL SELECT 'Views', COUNT(*) FROM master_views
UNION ALL SELECT 'Property Conditions', COUNT(*) FROM master_property_conditions
ORDER BY count DESC;

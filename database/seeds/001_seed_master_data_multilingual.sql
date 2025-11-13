-- ============================================================
-- COMPREHENSIVE MULTILINGUAL MASTER DATA SEED
-- Purpose: Populate all master data tables with English base + Vietnamese mappings
-- Date: 2025-11-12
-- ============================================================

-- ============================================================
-- 1. COUNTRIES & CURRENCIES (Foundation for international support)
-- ============================================================

INSERT INTO master_countries (code, code_2, name_en, name_local, name_vi, aliases, region, continent, phone_code, default_currency_code, is_primary, popularity_rank) VALUES
('VNM', 'VN', 'Vietnam', 'Việt Nam', 'Việt Nam', ARRAY['Vietnam', 'Việt Nam', 'VN', 'VIETNAM', '越南'], 'southeast_asia', 'asia', '+84', 'VND', TRUE, 1),
('USA', 'US', 'United States', 'United States', 'Hoa Kỳ', ARRAY['USA', 'US', 'America', 'United States', '美国'], 'north_america', 'americas', '+1', 'USD', TRUE, 2),
('JPN', 'JP', 'Japan', '日本', 'Nhật Bản', ARRAY['Japan', 'JP', 'Nihon', '日本', 'Nhật'], 'east_asia', 'asia', '+81', 'JPY', TRUE, 3),
('CHN', 'CN', 'China', '中国', 'Trung Quốc', ARRAY['China', 'CN', 'PRC', '中国', 'Trung Quốc'], 'east_asia', 'asia', '+86', 'CNY', TRUE, 4),
('KOR', 'KR', 'South Korea', '대한민국', 'Hàn Quốc', ARRAY['Korea', 'KR', 'South Korea', '韩国', 'Hàn Quốc'], 'east_asia', 'asia', '+82', 'KRW', TRUE, 5)
ON CONFLICT (code) DO NOTHING;

INSERT INTO master_currencies (code, symbol, name_en, name_vi, aliases, country_code, exchange_rate_to_usd, decimal_places) VALUES
('VND', '₫', 'Vietnamese Dong', 'Đồng Việt Nam', ARRAY['VND', 'dong', 'đồng', 'việt nam đồng', 'VNĐ'], 'VNM', 0.000040, 0),
('USD', '$', 'US Dollar', 'Đô la Mỹ', ARRAY['USD', 'dollar', '$', 'đô la', 'đô'], 'USA', 1.0, 2),
('JPY', '¥', 'Japanese Yen', 'Yên Nhật', ARRAY['JPY', 'yen', '¥', '円', 'yên'], 'JPN', 0.0067, 0),
('CNY', '¥', 'Chinese Yuan', 'Nhân dân tệ', ARRAY['CNY', 'yuan', 'RMB', '元', 'tệ'], 'CHN', 0.14, 2),
('KRW', '₩', 'South Korean Won', 'Won Hàn Quốc', ARRAY['KRW', 'won', '₩', '원', 'won'], 'KOR', 0.00075, 0)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 2. VIETNAM ADMINISTRATIVE DIVISIONS (Ho Chi Minh City Focus)
-- ============================================================

INSERT INTO master_cities (code, name_vi, name_en, aliases, country_code, region, type, population, is_major) VALUES
('SGN', 'Thành phố Hồ Chí Minh', 'Ho Chi Minh City', ARRAY['HCMC', 'Sài Gòn', 'Saigon', 'HCM', 'TP HCM', 'Ho Chi Minh'], 'VNM', 'south', 'city', 9000000, TRUE),
('HAN', 'Hà Nội', 'Hanoi', ARRAY['Hanoi', 'Ha Noi', 'HN', 'Hà Nội'], 'VNM', 'north', 'city', 8000000, TRUE),
('DNA', 'Đà Nẵng', 'Da Nang', ARRAY['Da Nang', 'Danang', 'DN', 'Đà Nẵng'], 'VNM', 'central', 'city', 1200000, TRUE)
ON CONFLICT (code) DO NOTHING;

-- Ho Chi Minh City Districts (24 districts + Thủ Đức City)
INSERT INTO master_districts (code, name_vi, name_en, aliases, city_id, type, area_km2, population, avg_price_per_m2_vnd) VALUES
-- Urban Core Districts (Quận nội thành)
('Q1', 'Quận 1', 'District 1', ARRAY['Q1', 'Quận 1', 'District 1', 'D1'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 7.8, 204899, 150000000),
('Q3', 'Quận 3', 'District 3', ARRAY['Q3', 'Quận 3', 'District 3', 'D3'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 4.9, 188029, 120000000),
('Q5', 'Quận 5', 'District 5', ARRAY['Q5', 'Quận 5', 'District 5', 'D5'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 4.2, 178320, 80000000),
('Q10', 'Quận 10', 'District 10', ARRAY['Q10', 'Quận 10', 'District 10', 'D10'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 5.8, 244785, 85000000),
('Q11', 'Quận 11', 'District 11', ARRAY['Q11', 'Quận 11', 'District 11', 'D11'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 5.1, 246190, 75000000),
('PN', 'Quận Phú Nhuận', 'Phu Nhuan District', ARRAY['PN', 'Phú Nhuận', 'Phu Nhuan', 'Q Phú Nhuận'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 4.9, 179449, 100000000),

-- Suburban Districts (Quận ven)
('Q4', 'Quận 4', 'District 4', ARRAY['Q4', 'Quận 4', 'District 4', 'D4'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 4.2, 203000, 90000000),
('Q6', 'Quận 6', 'District 6', ARRAY['Q6', 'Quận 6', 'District 6', 'D6'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 7.1, 253474, 70000000),
('Q7', 'Quận 7', 'District 7', ARRAY['Q7', 'Quận 7', 'District 7', 'D7', 'Phú Mỹ Hưng'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 36.6, 387300, 95000000),
('Q8', 'Quận 8', 'District 8', ARRAY['Q8', 'Quận 8', 'District 8', 'D8'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 19.2, 489800, 65000000),
('BT', 'Quận Bình Thạnh', 'Binh Thanh District', ARRAY['BT', 'Bình Thạnh', 'Binh Thanh', 'Q Bình Thạnh'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 20.8, 495800, 88000000),
('TB', 'Quận Tân Bình', 'Tan Binh District', ARRAY['TB', 'Tân Bình', 'Tan Binh', 'Q Tân Bình'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 22.4, 498900, 92000000),
('TP', 'Quận Tân Phú', 'Tan Phu District', ARRAY['TP', 'Tân Phú', 'Tan Phu', 'Q Tân Phú'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 16.1, 439900, 75000000),
('GV', 'Quận Gò Vấp', 'Go Vap District', ARRAY['GV', 'Gò Vấp', 'Go Vap', 'Q Gò Vấp'], (SELECT id FROM master_cities WHERE code='SGN'), 'urban', 19.8, 687800, 70000000),

-- New Districts (2021+)
('TD', 'Thành phố Thủ Đức', 'Thu Duc City', ARRAY['TD', 'Thủ Đức', 'Thu Duc', 'Q2', 'Q9', 'Quận Thủ Đức', 'Thảo Điền', 'An Phú'], (SELECT id FROM master_cities WHERE code='SGN'), 'city', 211.5, 1200000, 105000000),

-- Rural Districts (Huyện)
('BC', 'Huyện Bình Chánh', 'Binh Chanh District', ARRAY['BC', 'Bình Chánh', 'Binh Chanh'], (SELECT id FROM master_cities WHERE code='SGN'), 'rural', 252.0, 559200, 45000000),
('HC', 'Huyện Hóc Môn', 'Hoc Mon District', ARRAY['HC', 'Hóc Môn', 'Hoc Mon'], (SELECT id FROM master_cities WHERE code='SGN'), 'rural', 109.0, 392600, 40000000),
('CC', 'Huyện Củ Chi', 'Cu Chi District', ARRAY['CC', 'Củ Chi', 'Cu Chi'], (SELECT id FROM master_cities WHERE code='SGN'), 'rural', 435.0, 439400, 30000000),
('NB', 'Huyện Nhà Bè', 'Nha Be District', ARRAY['NB', 'Nhà Bè', 'Nha Be'], (SELECT id FROM master_cities WHERE code='SGN'), 'rural', 100.3, 131000, 50000000),
('CG', 'Huyện Cần Giờ', 'Can Gio District', ARRAY['CG', 'Cần Giờ', 'Can Gio'], (SELECT id FROM master_cities WHERE code='SGN'), 'rural', 704.0, 73000, 25000000)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 3. PROPERTY TYPES (English base with Vietnamese mapping)
-- ============================================================

INSERT INTO master_property_types (code, name_en, name_vi, aliases, category, typical_area_min, typical_area_max, typical_price_min_vnd, typical_price_max_vnd, popularity_rank) VALUES
-- Residential
('apartment', 'Apartment', 'Căn hộ chung cư', ARRAY['apartment', 'flat', 'condo', 'căn hộ', 'chung cư', 'apartment building'], 'residential', 30, 150, 1500000000, 10000000000, 1),
('house', 'House', 'Nhà riêng', ARRAY['house', 'townhouse', 'nhà', 'nhà riêng', 'nhà phố'], 'residential', 50, 300, 3000000000, 20000000000, 2),
('villa', 'Villa', 'Biệt thự', ARRAY['villa', 'mansion', 'biệt thự', 'villa garden'], 'residential', 200, 1000, 10000000000, 100000000000, 3),
('penthouse', 'Penthouse', 'Căn hộ penthouse', ARRAY['penthouse', 'sky villa', 'penthouse apartment'], 'residential', 150, 500, 15000000000, 50000000000, 4),
('duplex', 'Duplex', 'Căn hộ duplex', ARRAY['duplex', 'maisonette', 'duplex apartment', 'căn hộ 2 tầng'], 'residential', 100, 250, 5000000000, 20000000000, 5),
('studio', 'Studio', 'Căn hộ studio', ARRAY['studio', 'studio apartment', 'efficiency', 'căn hộ studio'], 'residential', 20, 40, 800000000, 2500000000, 6),

-- Land
('land', 'Land', 'Đất nền', ARRAY['land', 'plot', 'lot', 'đất', 'đất nền', 'land plot'], 'land', 50, 10000, 1000000000, 50000000000, 7),
('agricultural_land', 'Agricultural Land', 'Đất nông nghiệp', ARRAY['farm', 'agricultural land', 'đất nông nghiệp', 'đất trồng trọt'], 'land', 500, 50000, 500000000, 20000000000, 8),

-- Commercial
('shophouse', 'Shophouse', 'Nhà mặt tiền', ARRAY['shophouse', 'shop', 'nhà mặt tiền', 'nhà mặt phố'], 'commercial', 50, 200, 5000000000, 30000000000, 9),
('office', 'Office', 'Văn phòng', ARRAY['office', 'office space', 'văn phòng', 'office building'], 'commercial', 30, 500, 2000000000, 20000000000, 10),
('warehouse', 'Warehouse', 'Kho xưởng', ARRAY['warehouse', 'factory', 'kho', 'xưởng', 'kho xưởng'], 'commercial', 100, 5000, 3000000000, 50000000000, 11),
('retail', 'Retail Space', 'Mặt bằng kinh doanh', ARRAY['retail', 'shop', 'store', 'mặt bằng', 'cửa hàng'], 'commercial', 20, 300, 1500000000, 15000000000, 12)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 4. TRANSACTION TYPES
-- ============================================================

INSERT INTO master_transaction_types (code, name_en, name_vi, aliases, requires_legal_transfer, typical_contract_duration_months) VALUES
('sale', 'For Sale', 'Bán', ARRAY['sale', 'sell', 'buy', 'bán', 'mua'], TRUE, NULL),
('rent', 'For Rent', 'Cho thuê', ARRAY['rent', 'lease', 'rental', 'cho thuê', 'thuê'], FALSE, 12),
('lease', 'Long-term Lease', 'Cho thuê dài hạn', ARRAY['lease', 'long-term', 'cho thuê dài hạn'], FALSE, 36),
('transfer', 'Transfer Rights', 'Chuyển nhượng', ARRAY['transfer', 'assignment', 'chuyển nhượng'], TRUE, NULL)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 5. AMENITIES (Building-level and Unit-level)
-- ============================================================

INSERT INTO master_amenities (code, name_en, name_vi, aliases, category, level, premium_level, value_impact_percent) VALUES
-- Security
('security_24_7', '24/7 Security', 'Bảo vệ 24/7', ARRAY['security', 'guard', 'bảo vệ', 'an ninh'], 'security', 'building', 2, 5),
('cctv', 'CCTV', 'Camera giám sát', ARRAY['CCTV', 'camera', 'surveillance', 'camera an ninh'], 'security', 'building', 2, 3),
('access_card', 'Access Card', 'Thẻ từ', ARRAY['access card', 'key card', 'thẻ từ', 'thẻ ra vào'], 'security', 'building', 2, 2),
('fingerprint_lock', 'Fingerprint Lock', 'Khóa vân tay', ARRAY['fingerprint', 'biometric', 'khóa vân tay'], 'security', 'unit', 3, 5),

-- Recreation
('swimming_pool', 'Swimming Pool', 'Hồ bơi', ARRAY['pool', 'swimming pool', 'hồ bơi', 'bể bơi'], 'recreation', 'building', 3, 8),
('gym', 'Gym', 'Phòng gym', ARRAY['gym', 'fitness', 'phòng tập', 'fitness center'], 'recreation', 'building', 2, 5),
('playground', 'Playground', 'Khu vui chơi trẻ em', ARRAY['playground', 'play area', 'khu vui chơi', 'sân chơi'], 'recreation', 'building', 2, 3),
('tennis_court', 'Tennis Court', 'Sân tennis', ARRAY['tennis', 'tennis court', 'sân tennis'], 'recreation', 'building', 3, 7),
('bbq_area', 'BBQ Area', 'Khu BBQ', ARRAY['BBQ', 'barbecue', 'khu nướng', 'BBQ area'], 'recreation', 'building', 2, 3),
('garden', 'Garden', 'Vườn', ARRAY['garden', 'yard', 'vườn', 'sân vườn'], 'recreation', 'both', 2, 5),

-- Services
('parking', 'Parking', 'Chỗ đậu xe', ARRAY['parking', 'garage', 'chỗ đậu xe', 'bãi đỗ xe'], 'services', 'building', 2, 5),
('elevator', 'Elevator', 'Thang máy', ARRAY['elevator', 'lift', 'thang máy', 'thang'], 'services', 'building', 2, 8),
('concierge', 'Concierge', 'Lễ tân', ARRAY['concierge', 'reception', 'lễ tân', 'front desk'], 'services', 'building', 3, 5),
('housekeeping', 'Housekeeping', 'Dọn dẹp', ARRAY['housekeeping', 'cleaning', 'dọn dẹp', 'vệ sinh'], 'services', 'building', 3, 7),
('laundry', 'Laundry', 'Giặt là', ARRAY['laundry', 'washing', 'giặt là', 'giặt ủi'], 'services', 'building', 2, 3),

-- Facilities
('supermarket', 'Supermarket', 'Siêu thị', ARRAY['supermarket', 'grocery', 'siêu thị', 'chợ'], 'facilities', 'building', 2, 5),
('restaurant', 'Restaurant', 'Nhà hàng', ARRAY['restaurant', 'dining', 'nhà hàng', 'quán ăn'], 'facilities', 'building', 2, 3),
('cafe', 'Cafe', 'Quán cà phê', ARRAY['cafe', 'coffee shop', 'cà phê', 'quán cà phê'], 'facilities', 'building', 2, 2),
('shopping_mall', 'Shopping Mall', 'Trung tâm thương mại', ARRAY['mall', 'shopping center', 'TTTM', 'trung tâm mua sắm'], 'facilities', 'building', 3, 8),

-- Unit Amenities
('air_conditioning', 'Air Conditioning', 'Điều hòa', ARRAY['AC', 'air con', 'điều hòa', 'máy lạnh'], 'utilities', 'unit', 1, 5),
('balcony', 'Balcony', 'Ban công', ARRAY['balcony', 'terrace', 'ban công'], 'space', 'unit', 2, 5),
('kitchen', 'Kitchen', 'Bếp', ARRAY['kitchen', 'bếp', 'nhà bếp'], 'space', 'unit', 1, 3),
('furnished', 'Fully Furnished', 'Nội thất đầy đủ', ARRAY['furnished', 'furniture', 'nội thất', 'full nội thất'], 'utilities', 'unit', 2, 10)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 6. DIRECTIONS (Feng Shui important in Vietnamese culture)
-- ============================================================

INSERT INTO master_directions (code, name_en, name_vi, aliases, angle_degrees, feng_shui_rating, preference_score) VALUES
('north', 'North', 'Hướng Bắc', ARRAY['north', 'N', 'bắc'], 0, 7, 70),
('northeast', 'Northeast', 'Hướng Đông Bắc', ARRAY['northeast', 'NE', 'đông bắc'], 45, 6, 60),
('east', 'East', 'Hướng Đông', ARRAY['east', 'E', 'đông'], 90, 9, 90),
('southeast', 'Southeast', 'Hướng Đông Nam', ARRAY['southeast', 'SE', 'đông nam'], 135, 8, 85),
('south', 'South', 'Hướng Nam', ARRAY['south', 'S', 'nam'], 180, 8, 80),
('southwest', 'Southwest', 'Hướng Tây Nam', ARRAY['southwest', 'SW', 'tây nam'], 225, 5, 50),
('west', 'West', 'Hướng Tây', ARRAY['west', 'W', 'tây'], 270, 4, 40),
('northwest', 'Northwest', 'Hướng Tây Bắc', ARRAY['northwest', 'NW', 'tây bắc'], 315, 6, 65)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 7. LEGAL STATUS
-- ============================================================

INSERT INTO master_legal_status (code, name_en, name_vi, aliases, is_transferable, requires_conversion, risk_level, value_impact_percent) VALUES
('red_book', 'Red Book (Full Ownership)', 'Sổ hồng/Sổ đỏ', ARRAY['red book', 'pink book', 'sổ hồng', 'sổ đỏ'], TRUE, FALSE, 'low', 0),
('sale_contract', 'Sale Contract', 'Hợp đồng mua bán', ARRAY['contract', 'sale agreement', 'hợp đồng'], TRUE, TRUE, 'medium', -10),
('waiting_red_book', 'Waiting for Red Book', 'Đang chờ sổ', ARRAY['waiting', 'pending', 'chờ sổ'], TRUE, TRUE, 'medium', -15),
('land_use_right', 'Land Use Right Certificate', 'Giấy chứng nhận quyền sử dụng đất', ARRAY['land use', 'GCNQSD', 'giấy tờ đất'], TRUE, FALSE, 'low', -5),
('no_document', 'No Legal Document', 'Không giấy tờ', ARRAY['no document', 'không giấy tờ'], FALSE, TRUE, 'high', -30)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 8. FURNITURE TYPES
-- ============================================================

INSERT INTO master_furniture_types (code, name_en, name_vi, aliases, level, typical_cost_vnd, value_impact_percent) VALUES
('bare', 'Bare/Unfurnished', 'Bàn giao thô', ARRAY['bare', 'unfurnished', 'empty', 'thô', 'không nội thất'], 0, 0, -15),
('basic', 'Basic Furnishing', 'Nội thất cơ bản', ARRAY['basic', 'simple', 'cơ bản'], 1, 50000000, 0),
('full', 'Fully Furnished', 'Nội thất đầy đủ', ARRAY['furnished', 'full', 'đầy đủ', 'full nội thất'], 2, 150000000, 10),
('luxury', 'Luxury Furnishing', 'Nội thất cao cấp', ARRAY['luxury', 'premium', 'high-end', 'cao cấp', 'sang trọng'], 3, 500000000, 25)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 9. VIEWS (Impact on property value)
-- ============================================================

INSERT INTO master_views (code, name_en, name_vi, aliases, category, desirability_score, value_impact_percent) VALUES
('river_view', 'River View', 'View sông', ARRAY['river', 'riverside', 'sông', 'view sông'], 'natural', 9, 15),
('sea_view', 'Sea View', 'View biển', ARRAY['sea', 'ocean', 'beach', 'biển', 'view biển'], 'natural', 10, 20),
('city_view', 'City View', 'View thành phố', ARRAY['city', 'skyline', 'thành phố', 'view thành phố'], 'urban', 8, 10),
('landmark_view', 'Landmark View', 'View địa danh', ARRAY['landmark', 'monument', 'địa danh', 'view đẹp'], 'urban', 9, 15),
('park_view', 'Park View', 'View công viên', ARRAY['park', 'garden', 'công viên', 'view công viên'], 'natural', 8, 12),
('golf_view', 'Golf Course View', 'View sân golf', ARRAY['golf', 'golf course', 'sân golf'], 'natural', 8, 12),
('inner_view', 'Inner View', 'View nội khu', ARRAY['inner', 'courtyard', 'nội khu', 'trong dự án'], 'mixed', 5, 0),
('street_view', 'Street View', 'View đường phố', ARRAY['street', 'road', 'đường', 'view đường'], 'urban', 4, -5),
('mountain_view', 'Mountain View', 'View núi', ARRAY['mountain', 'hill', 'núi', 'view núi'], 'natural', 7, 8),
('no_view', 'No Particular View', 'Không view đặc biệt', ARRAY['no view', 'blocked', 'không view'], 'none', 2, -10)
ON CONFLICT (code) DO NOTHING;

-- ============================================================
-- 10. PROPERTY CONDITIONS
-- ============================================================

INSERT INTO master_property_conditions (code, name_en, name_vi, aliases, typical_age_min, typical_age_max, condition_level, value_impact_percent, requires_renovation) VALUES
('brand_new', 'Brand New', 'Hoàn toàn mới', ARRAY['brand new', 'new', 'mới 100%', 'hoàn toàn mới'], 0, 1, 5, 10, FALSE),
('newly_built', 'Newly Built', 'Mới xây', ARRAY['newly built', 'recent', 'mới xây', 'mới'], 1, 2, 5, 5, FALSE),
('excellent', 'Excellent Condition', 'Tình trạng tốt', ARRAY['excellent', 'perfect', 'tốt', 'hoàn hảo'], 2, 5, 5, 0, FALSE),
('well_maintained', 'Well Maintained', 'Được bảo trì tốt', ARRAY['well maintained', 'good', 'tốt', 'đẹp'], 3, 10, 4, 0, FALSE),
('average', 'Average Condition', 'Tình trạng trung bình', ARRAY['average', 'fair', 'trung bình', 'bình thường'], 10, 15, 3, -5, FALSE),
('needs_cosmetic', 'Needs Cosmetic Work', 'Cần sửa chữa nhỏ', ARRAY['cosmetic', 'minor repairs', 'sửa nhỏ'], 15, 20, 2, -10, TRUE),
('needs_renovation', 'Needs Renovation', 'Cần sửa chữa lớn', ARRAY['renovation', 'fixer', 'cần sửa chữa', 'cần tu sửa'], 20, 30, 2, -20, TRUE),
('poor', 'Poor Condition', 'Tình trạng xấu', ARRAY['poor', 'bad', 'xấu', 'tệ'], 30, 50, 1, -30, TRUE),
('under_construction', 'Under Construction', 'Đang xây dựng', ARRAY['construction', 'building', 'đang xây'], 0, 0, 3, -10, FALSE),
('off_plan', 'Off Plan/Pre-sale', 'Bán trên giấy', ARRAY['off plan', 'pre-sale', 'presale', 'bán giấy'], 0, 0, 3, -15, FALSE)
ON CONFLICT (code) DO NOTHING;

-- Create indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_master_countries_aliases ON master_countries USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_master_currencies_aliases ON master_currencies USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_master_districts_aliases ON master_districts USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_master_property_types_aliases ON master_property_types USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_master_amenities_aliases ON master_amenities USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_master_directions_aliases ON master_directions USING GIN(aliases);
CREATE INDEX IF NOT EXISTS idx_master_views_aliases ON master_views USING GIN(aliases);

-- Verify data
SELECT
    'Countries' as table_name, COUNT(*) as count FROM master_countries
UNION ALL
SELECT 'Currencies', COUNT(*) FROM master_currencies
UNION ALL
SELECT 'Cities', COUNT(*) FROM master_cities
UNION ALL
SELECT 'Districts', COUNT(*) FROM master_districts
UNION ALL
SELECT 'Property Types', COUNT(*) FROM master_property_types
UNION ALL
SELECT 'Transaction Types', COUNT(*) FROM master_transaction_types
UNION ALL
SELECT 'Amenities', COUNT(*) FROM master_amenities
UNION ALL
SELECT 'Directions', COUNT(*) FROM master_directions
UNION ALL
SELECT 'Legal Status', COUNT(*) FROM master_legal_status
UNION ALL
SELECT 'Furniture Types', COUNT(*) FROM master_furniture_types
UNION ALL
SELECT 'Views', COUNT(*) FROM master_views
UNION ALL
SELECT 'Property Conditions', COUNT(*) FROM master_property_conditions;

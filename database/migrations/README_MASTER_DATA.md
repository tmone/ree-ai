# Master Data Tables Documentation

## Tổng quan

Hệ thống master data được thiết kế để chuẩn hóa và tăng độ chính xác cho service extraction, giúp chuyển đổi dữ liệu thô từ crawler4AI thành dữ liệu có cấu trúc.

## Cấu trúc Migration

### Migration 006: Base Master Data
File: `006_create_master_data.sql`

**Các bảng được tạo:**
1. **master_districts** - Quận/Huyện (24 districts seeded)
2. **master_wards** - Phường/Xã (structure only)
3. **master_property_types** - Loại BĐS (8 types)
4. **master_transaction_types** - Loại giao dịch (2 types)
5. **master_amenities** - Tiện ích (20+ amenities)
6. **master_furniture_types** - Nội thất (4 levels)
7. **master_directions** - Hướng nhà (8 directions)
8. **master_legal_status** - Giấy tờ pháp lý (5 types)
9. **master_price_ranges** - Giá tham khảo theo khu vực

### Migration 007: Extended Master Data
File: `007_create_extended_master_data.sql`

**Các bảng bổ sung:**
1. **master_developers** - Chủ đầu tư
2. **master_projects** - Dự án BĐS
3. **master_streets** - Đường phố
4. **master_building_features** - Tiện ích chung tòa nhà
5. **master_views** - Loại view/hướng nhìn
6. **master_property_conditions** - Tình trạng nhà

## Chi tiết các bảng mới

### 1. master_developers (Chủ đầu tư)

**Mục đích:** Chuẩn hóa tên chủ đầu tư, hỗ trợ nhận dạng các dự án uy tín.

**Cấu trúc chính:**
- `code`: Mã định danh (e.g., 'vingroup', 'capitaland')
- `name_vi/name_en`: Tên tiếng Việt/Anh
- `aliases`: Mảng các tên gọi khác (flexible matching)
- `type`: corporation/private/government/joint_venture
- `reputation_score`: Điểm uy tín (1-5 sao)
- `total_projects`: Số lượng dự án

**Dữ liệu seed:** 15 chủ đầu tư hàng đầu (Vingroup, CapitaLand, Novaland, etc.)

**Use cases:**
- Nhận diện project: "Masteri Thảo Điền" → developer_id = Novaland
- Filter BĐS theo độ uy tín CĐT
- Hiển thị logo/thông tin CĐT

### 2. master_projects (Dự án BĐS)

**Mục đích:** Chuẩn hóa tên dự án, liên kết với CĐT và location.

**Cấu trúc chính:**
- `code`: Mã dự án (e.g., 'vinhomes_central_park')
- `name_vi/name_en`: Tên dự án
- `aliases`: Tên viết tắt (e.g., ['VHCP', 'VCP'])
- `developer_id`: FK → master_developers
- `district_id`: FK → master_districts
- `type`: luxury/mid_range/affordable/landed/highrise
- `scale`: small/medium/large/mega
- `handover_status`: planning/under_construction/completed
- `features`: Mảng đặc điểm (e.g., ['riverside', 'near_metro'])

**Dữ liệu seed:** 15 dự án lớn nhất TP.HCM:
- Vinhomes Central Park, Golden River, Grand Park
- Masteri Thảo Điền, An Phú
- The Vista, Empire City, Celadon City, etc.

**Use cases:**
- Extraction: "căn hộ Vinhomes Central Park" → project_id
- Auto-complete địa chỉ khi user nhập tên dự án
- Filter theo scale/status/developer

### 3. master_streets (Đường phố)

**Mục đích:** Chuẩn hóa tên đường, hỗ trợ location matching.

**Cấu trúc chính:**
- `code`: Mã đường (e.g., 'nguyen_van_linh')
- `name_vi/name_en`: Tên đường
- `aliases`: Tên viết tắt (['NVL', 'Đường Nguyễn Văn Linh'])
- `district_id`: FK → master_districts
- `type`: main_road/secondary_road/alley/highway
- `width_category`: large/medium/small
- `importance_score`: 1-5 (affects property value)

**Dữ liệu seed:** 15 con đường chính TP.HCM:
- Nguyễn Văn Linh, Xa lộ Hà Nội, Nguyễn Hữu Cảnh
- Võ Văn Kiệt, Mai Chí Thọ, Điện Biên Phủ, etc.

**Use cases:**
- Extraction: "Căn hộ đường Xa lộ Hà Nội" → street_id + validation
- Tính điểm location dựa trên importance_score
- Auto-complete địa chỉ

### 4. master_building_features (Tiện ích chung tòa nhà)

**Mục đích:** Phân biệt tiện ích chung (building-level) vs tiện ích căn hộ (unit-level).

**Cấu trúc chính:**
- `code`: Mã tiện ích (e.g., 'security_24_7')
- `aliases`: Các cách gọi khác
- `category`: security/recreation/services/facilities/utilities
- `premium_level`: 1=basic, 2=standard, 3=luxury

**Dữ liệu seed:** 25 tiện ích phổ biến:
- **Security:** CCTV, access card, fingerprint lock
- **Recreation:** infinity pool, tennis court, yoga room
- **Services:** concierge, housekeeping, shuttle bus
- **Facilities:** shopping mall, supermarket, coworking
- **Utilities:** backup power, solar panel, smart home

**Use cases:**
- Extraction: Tách "hồ bơi vô cực" (building) vs "điều hòa" (unit)
- Scoring property value theo premium_level
- Filter dự án cao cấp (có nhiều premium features)

### 5. master_views (Hướng nhìn)

**Mục đích:** Chuẩn hóa loại view, ảnh hưởng đến giá trị BĐS.

**Cấu trúc chính:**
- `code`: Mã view (e.g., 'river_view')
- `category`: natural/urban/mixed
- `desirability_score`: 1-10 (tác động giá)

**Dữ liệu seed:** 10 loại view:
- **High value:** river_view (9), landmark_view (9), sea_view (10)
- **Medium value:** city_view (8), park_view (8), golf_view (8)
- **Lower value:** inner_view (5), street_view (4)

**Use cases:**
- Extraction: "view sông Sài Gòn" → river_view
- Pricing model: +15% for river_view
- Filter theo desirability

### 6. master_property_conditions (Tình trạng nhà)

**Mục đích:** Chuẩn hóa tình trạng/độ mới của BĐS.

**Cấu trúc chính:**
- `code`: Mã tình trạng (e.g., 'brand_new')
- `typical_age_min/max`: Độ tuổi tương ứng (years)
- `condition_level`: 1-5 (1=poor, 5=excellent)
- `value_impact_percent`: Ảnh hưởng giá (+10%, -20%)

**Dữ liệu seed:** 10 tình trạng:
- brand_new (0-1 years, +10%)
- newly_built (1-2 years, +5%)
- well_maintained (3-10 years, 0%)
- needs_renovation (15+ years, -20%)
- under_construction (0 years, -10%)
- off_plan (pre-sale, -15%)

**Use cases:**
- Extraction: "nhà mới 100%" → brand_new
- Pricing adjustment: Apply value_impact_percent
- Filter theo condition_level

### 7. master_wards (Phường/Xã) - SEED DATA

**Mục đích:** Bổ sung dữ liệu cho bảng ward đã có nhưng rỗng.

**Dữ liệu seed:** 150+ phường/xã cho các quận chính:
- **Quận 1:** 10 phường (Bến Nghé, Đa Kao, etc.)
- **Quận 7:** 10 phường (Tân Phú, Tân Quy, Phú Mỹ, etc.)
- **Bình Thạnh:** 20 phường
- **Thủ Đức City:** 23 phường (gộp Q2, Q9, QTĐ)
- **Tân Bình:** 14 phường
- **Phú Nhuận:** 13 phường
- **Quận 3:** 11 phường
- **Bình Chánh:** 7 xã

**Use cases:**
- Extraction: "Phường Thảo Điền, Quận 2" → ward_id + district_id
- Location hierarchy: city > district > ward > street
- Micro-location pricing

## Indexes và Performance

### GIN Indexes (Array Search)
Tất cả bảng có index GIN trên trường `aliases` để hỗ trợ tìm kiếm nhanh:

```sql
CREATE INDEX idx_developers_aliases ON master_developers USING GIN(aliases);
CREATE INDEX idx_projects_aliases ON master_projects USING GIN(aliases);
-- etc.
```

**Query example:**
```sql
-- Tìm project với alias "VHCP"
SELECT * FROM master_projects
WHERE 'VHCP' = ANY(aliases);
```

### B-tree Indexes
- `code` (UNIQUE): Primary lookup
- `district_id`, `developer_id`: Foreign key joins
- `type`, `category`: Filtering
- `active`: Soft delete

## Seed Data Files

1. **001_seed_master_data.sql** - Base master data (existing)
2. **002_seed_extended_master_data.sql** - Extended tables (NEW)
   - 15 developers
   - 15 projects
   - 15 streets
   - 25 building features
   - 10 views
   - 10 property conditions
3. **003_seed_wards.sql** - Ward data (NEW)
   - 150+ wards across 8 major districts

## Cách chạy Migrations

```bash
# 1. Kết nối PostgreSQL
psql -h localhost -U your_user -d your_database

# 2. Chạy migrations (theo thứ tự)
\i database/migrations/006_create_master_data.sql
\i database/migrations/007_create_extended_master_data.sql

# 3. Seed data
\i database/seeds/001_seed_master_data.sql
\i database/seeds/002_seed_extended_master_data.sql
\i database/seeds/003_seed_wards.sql

# 4. Verify
SELECT COUNT(*) FROM master_developers;  -- Should be 15
SELECT COUNT(*) FROM master_projects;    -- Should be 15
SELECT COUNT(*) FROM master_streets;     -- Should be 15
SELECT COUNT(*) FROM master_wards;       -- Should be 150+
```

## Integration với Extraction Service

### Before (Without Master Data)
```python
# Raw text from crawler
text = "Căn hộ Vinhomes Central Park, Quận 2, view sông"

# Extraction → Inconsistent results
{
    "project_name": "VH Central Park",  # Inconsistent
    "district": "Q2",                   # Not validated
    "view": "view song"                 # Not standardized
}
```

### After (With Master Data)
```python
# 1. NLP Pre-processing với master data lookup
project = match_project_alias("Vinhomes Central Park")
district = match_district_alias("Quận 2")
view = match_view_alias("view sông")

# 2. Validated output
{
    "project_id": 1,                    # → Vinhomes Central Park
    "project_code": "vinhomes_central_park",
    "developer_id": 1,                  # → Vingroup
    "district_id": 19,                  # → Thủ Đức City
    "view_id": 1,                       # → River View
    "view_desirability_score": 9        # → Premium view
}
```

## Maintenance

### Thêm dự án mới
```sql
INSERT INTO master_projects (code, name_vi, name_en, aliases, developer_id, district_id, type, ...)
VALUES ('new_project', 'Dự án mới', 'New Project', ARRAY['DA Mới', 'New Proj'],
        (SELECT id FROM master_developers WHERE code = 'developer_code'),
        (SELECT id FROM master_districts WHERE code = 'Q7'),
        'luxury', ...);
```

### Update aliases
```sql
UPDATE master_projects
SET aliases = array_append(aliases, 'New Alias')
WHERE code = 'vinhomes_central_park';
```

### Deactivate obsolete data
```sql
UPDATE master_projects
SET active = FALSE
WHERE code = 'old_project';
```

## Tương lai (Future Enhancements)

### Phase 2 - Expand Coverage
- [ ] Thêm 50+ projects (hiện tại: 15)
- [ ] Thêm 100+ streets (hiện tại: 15)
- [ ] Hoàn thiện 250 wards cho tất cả 24 quận (hiện tại: 150)

### Phase 3 - Advanced Features
- [ ] `master_proximity_categories` - Khoảng cách đến POI (metro, school, etc.)
- [ ] `master_price_history` - Lịch sử giá theo thời gian
- [ ] `master_property_tags` - Tags tự động (luxury, affordable, investment)

### Phase 4 - AI Integration
- [ ] Embedding vectors cho similarity search
- [ ] Auto-suggest aliases từ crawled data
- [ ] ML model training data export

## Liên hệ

Nếu có thắc mắc hoặc cần bổ sung master data:
- Tạo ticket trên Jira
- Contact: Data Team

# Property Posting Requirements - Complete Field Analysis

Based on 10K+ scraped data and master data analysis from PostgreSQL `ree_common` schema.

## Master Data Available in Database

| Table | Records | Purpose |
|-------|---------|---------|
| property_types | 10 | Apartment, House, Villa, Land, Office, etc. |
| furniture_types | 4 | Bare, Basic, Full, Luxury |
| directions | 8 | N, NE, E, SE, S, SW, W, NW |
| legal_status | 5 | Red book, Pink book, Contract, etc. |
| property_conditions | 10 | New, Old, Renovated, Under construction, etc. |
| views | 15 | River, City, Garden, Mountain, etc. |
| amenities | 47 | Pool, Gym, Parking, Security, Elevator, etc. |
| districts | 31 | All districts in HCMC |
| streets | 14 | Major streets |

## Required Fields by Priority

### TIER 1: CRITICAL (Must have for ANY property)
1. **property_type** - Loại BĐS (APARTMENT, HOUSE, VILLA, LAND, etc.)
2. **transaction_type** - SALE or RENT
3. **district** - Quận/Huyện
4. **price** - Giá bán (for SALE)
5. **price_rent** - Giá thuê (for RENT)
6. **area** - Diện tích (m²)
7. **title** - Tiêu đề tin đăng

### TIER 2: HIGHLY RECOMMENDED (90% of listings have these)
8. **bedrooms** - Số phòng ngủ (not for LAND/WAREHOUSE)
9. **bathrooms** - Số phòng tắm
10. **ward** - Phường/Xã
11. **street** - Đường
12. **furniture_type** - Nội thất (BARE, BASIC, FULL, LUXURY)
13. **direction** - Hướng nhà (NORTH, SOUTH, EAST, WEST, etc.)
14. **legal_status** - Pháp lý
15. **contact_phone** - Số điện thoại

### TIER 3: RECOMMENDED (Improves listing quality)
16. **floors** - Số tầng (for HOUSE/VILLA/SHOPHOUSE)
17. **property_condition** - Tình trạng (NEW, OLD, RENOVATED, etc.)
18. **view_type** - Tầm nhìn (RIVER, CITY, GARDEN, etc.)
19. **facade_width** - Mặt tiền (m) - important for HOUSE/SHOPHOUSE
20. **balcony_direction** - Hướng ban công (for APARTMENT)
21. **year_built** - Năm xây dựng
22. **contact_name** - Tên liên hệ
23. **contact_type** - Chính chủ/Môi giới

### TIER 4: OPTIONAL (Nice to have)
24. **project_name** - Tên dự án (for APARTMENT/VILLA in projects)
25. **amenities[]** - Tiện ích (array of codes)
26. **description** - Mô tả chi tiết
27. **images[]** - Ảnh (URLs)

## Property Type Specific Requirements

### APARTMENT / PENTHOUSE / DUPLEX / STUDIO
- **Required**: bedrooms, bathrooms, furniture_type, direction, floor (which floor)
- **Recommended**: balcony_direction, view_type, project_name, amenities (pool, gym, security, elevator)
- **Optional**: year_built

### HOUSE / VILLA
- **Required**: bedrooms, bathrooms, direction, floors, facade_width
- **Recommended**: furniture_type, legal_status, property_condition, alley_width
- **Optional**: garden_area, garage, amenities

### LAND
- **Required**: legal_status, facade_width
- **Not needed**: bedrooms, bathrooms, furniture_type, direction
- **Recommended**: alley_width (hẻm width), zoning_type
- **Optional**: utilities (water, electric connected)

### SHOPHOUSE / OFFICE / WAREHOUSE
- **Required**: floors, facade_width
- **Recommended**: parking_capacity, elevator (for OFFICE)
- **Optional**: loading_dock (for WAREHOUSE)

## Intelligent Questioning Logic

### Phase 1: Core Info (Always ask)
```
1. Property type? (show 10 options from master data)
2. Transaction type? (SALE or RENT)
3. Location? (district → ward → street)
4. Price? (or rental price)
5. Area? (m²)
```

### Phase 2: Type-Specific (Based on property_type)
```
IF property_type IN [APARTMENT, HOUSE, VILLA]:
    → Ask: bedrooms, bathrooms

IF property_type IN [APARTMENT, PENTHOUSE]:
    → Ask: floor, project_name, view_type

IF property_type IN [HOUSE, VILLA, SHOPHOUSE]:
    → Ask: floors, facade_width

IF property_type == LAND:
    → Skip: bedrooms, bathrooms, furniture
    → Focus: legal_status, facade_width
```

### Phase 3: Quality Enhancers (Always valuable)
```
→ Furniture type? (show 4 options)
→ Direction? (show 8 options)
→ Legal status? (show 5 options)
→ Property condition? (show 10 options)
→ Contact info? (phone + name)
```

### Phase 4: Premium Features (Ask if user volunteers info)
```
→ Any special amenities? (show 47 options)
→ Any special views? (show 15 options)
→ Photos? (upload URLs)
```

## Completeness Score Calculation

### Formula:
```
Score = (filled_tier1 / total_tier1) * 40%
      + (filled_tier2 / total_tier2) * 30%
      + (filled_tier3 / total_tier3) * 20%
      + (filled_tier4 / total_tier4) * 10%
```

### Minimum for "Complete" Listing:
- **75%+** = Ready to post (has Tier 1 + most of Tier 2)
- **50-74%** = Needs more info (missing key Tier 2 fields)
- **25-49%** = Incomplete (missing Tier 1 fields)
- **<25%** = Just started

## Example: Complete Apartment Listing

```json
{
  "property_type": "APARTMENT",
  "transaction_type": "RENT",
  "district": "District 7",
  "ward": "Tan Phong Ward",
  "street": "Nguyen Van Linh",
  "project_name": "Vinhomes Central Park",
  "price_rent": 15000000,
  "area": 75,
  "bedrooms": 2,
  "bathrooms": 2,
  "floor": 18,
  "furniture_type": "FULL",
  "direction": "SOUTHEAST",
  "balcony_direction": "EAST",
  "view_type": "RIVER",
  "legal_status": "PINK_BOOK",
  "property_condition": "NEW",
  "amenities": ["POOL", "GYM", "SECURITY_24_7", "ELEVATOR", "PLAYGROUND"],
  "contact_phone": "0901234567",
  "contact_name": "Mr. Nguyen",
  "contact_type": "OWNER",
  "year_built": 2020,
  "description": "Beautiful 2BR apartment with river view..."
}
```

**Completeness**: 95% (has all Tier 1, Tier 2, most of Tier 3, some Tier 4)

## Current Problem vs Solution

### ❌ Current (Only 4 fields = 100%)
```
district, bedrooms, area, price → 100% complete
```
**Problem**: Missing 90% of important info!

### ✅ Solution (15-20 fields = 100%)
```
Tier 1 (7 fields) + Tier 2 (8 fields) = 15 fields minimum
With Tier 3 (8 fields) = 23 fields for premium listings
```
**Result**: Complete, competitive listing!

## UX Improvements - Conversational Property Posting

### Current Problem

Users complain that responses are **too verbose and overwhelming**:

> "Sao bạn cứ hỏi hoài vậy? Họ đã bảo họ không có thời gian!"

### Issues:
❌ Lists ALL 9 missing fields at once
❌ 4 verbose sections (Điểm mạnh, Thông tin thiếu, Gợi ý, Hành động)
❌ No clear endpoint - keeps asking forever
❌ Not conversational - feels like filling a long form

### Required Changes:

✅ **Progressive Disclosure**: Ask 1-2 fields at a time
✅ **Clear Exit**: When score >= 60%, ask "Bạn muốn đăng tin không?"
✅ **Shorter Responses**: Max 3-4 lines per turn

### New Response Flow:

**Low score (<60%)**:
```
Để đăng tin nhanh, cho tôi biết:
1. Căn hộ ở quận nào?
2. Giá thuê bao nhiêu/tháng?
```

**Medium score (60-70%)**:
```
Tuyệt! Đã có đủ thông tin cơ bản:
- Căn hộ cho thuê, Quận 7, 70m²
- Giá: 10 triệu/tháng

Bạn muốn đăng tin ngay không? (có/không)
```

**User confirms**:
```
✅ Đã đăng tin thành công! Mã tin: #ABC123
[END CONVERSATION]
```

### Implementation Files:

1. `services/completeness/prompts.py` - Add `ready_to_post`, `next_questions` fields
2. `services/orchestrator/main.py` - Detect confirmation, end conversation
3. Response template - Short format

## Implementation Checklist

- [ ] **UX: Progressive disclosure** - Ask 1-2 fields per turn
- [ ] **UX: Confirmation flow** - Detect "có/đăng luôn" → End conversation
- [ ] **UX: Shorter responses** - Remove verbose sections
- [ ] Update Attribute Extraction Service prompts with all fields
- [ ] Update Completeness Check service with tier-based calculation
- [ ] Update Orchestrator questioning logic (intelligent based on type)
- [ ] Update mock orchestrator for testing
- [ ] Test with AI-to-AI simulator
- [ ] Update database schema if needed for new fields

# Real Estate Knowledge Base for REE AI
# Domain knowledge for Vietnamese property market

## Property Types (Loại hình bất động sản)

### Căn hộ (Apartment/Condo)
**Common attributes:**
- pool (hồ bơi)
- gym (phòng gym)
- security (an ninh 24/7)
- view (view thành phố/sông)
- balcony_direction (hướng ban công: Đông, Tây, Nam, Bắc)
- floor (tầng cao/thấp)
- parking (chỗ đậu xe)

**Keywords:**
- apartment, condo, căn hộ, chung cư
- studio, 1br, 2br, 3br (bedroom count)

**Typical price range:**
- Budget: < 2 tỷ
- Mid-range: 2-5 tỷ
- Luxury: > 5 tỷ

### Biệt thự (Villa)
**Common attributes:**
- private_garden (vườn riêng)
- wine_cellar (hầm rượu)
- home_theater (phòng chiếu phim)
- rooftop_terrace (sân thượng)
- garage (garage nhiều xe)
- smart_home (hệ thống smart home)
- land_area (diện tích đất)

**Keywords:**
- villa, biệt thự, nhà vườn
- compound (khu compound)

**Typical price range:**
- Standard: 10-30 tỷ
- Luxury: > 30 tỷ

### Nhà phố (Townhouse)
**Common attributes:**
- frontage_width (mặt tiền: 4m, 5m, 8m)
- floors (số tầng: 3 tầng, 4 tầng)
- alley_width (hẻm: 3m, 5m, 8m)
- parking_space (chỗ đậu xe)
- rooftop (sân thượng)

**Keywords:**
- townhouse, nhà phố, nhà riêng
- front house (nhà mặt tiền), alley house (nhà hẻm)

**Typical price range:**
- Alley: 3-8 tỷ
- Frontage: 8-20 tỷ

### Đất (Land)
**Common attributes:**
- zoning (quy hoạch: thổ cư, công nghiệp, thương mại)
- development_potential (tiềm năng phát triển)
- utilities (điện nước đầy đủ)
- road_width (mặt tiền đường)

**Keywords:**
- land, đất, đất nền
- residential land (đất thổ cư)

## Location Context (Ngữ cảnh địa điểm)

### Common location phrases and their meaning

**"Gần trường" (Near schools):**
- Radius: <= 2km
- Priority: International schools, bilingual schools
- Districts: Quận 2, Quận 7, Thủ Đức

**"View đẹp" (Nice view):**
- Floor: >= 10 (for apartments)
- Direction: East (Đông), South (Nam) preferred
- Keywords: river view, city view, park view

**"An ninh tốt" (Good security):**
- Gated community
- 24/7 security
- Biometric access
- Keywords: compound, security, guard

**"Yên tĩnh" (Quiet):**
- Alley width: <= 5m
- Distance from main road: > 50m
- Low traffic area

**"Tiện ích đầy đủ" (Full amenities):**
- Shopping mall: <= 1km
- Hospital: <= 3km
- Public transport: <= 500m

## Price Analysis Keywords

**Price indicators:**
- "giá tốt" → below market average
- "hời" → significantly below market
- "vị trí vàng" → prime location, premium price
- "cần bán gấp" → urgent sale, negotiable
- "chính chủ" → owner direct, no commission

**Price ranges by district (rough estimates):**
- Quận 1: 100-200 triệu/m²
- Quận 2, 7: 50-100 triệu/m²
- Thủ Đức: 30-60 triệu/m²
- Bình Thạnh: 40-80 triệu/m²

## Amenities Expansion (Mở rộng tiện nghi)

**Pool-related queries:**
- Keywords: pool, hồ bơi, swimming pool, bể bơi
- Related: infinity pool, rooftop pool, olympic pool

**Gym-related queries:**
- Keywords: gym, phòng gym, fitness, tập gym
- Related: yoga room, sauna, spa

**Parking-related queries:**
- Keywords: parking, chỗ đậu xe, bãi đỗ xe, garage
- Count: 1 car, 2 cars, multiple cars

**Garden-related queries:**
- Keywords: garden, vườn, sân vườn, vườn riêng
- Size: small (< 50m²), medium (50-100m²), large (> 100m²)

## Investment Keywords

**Investment-focused queries:**
- "tiềm năng" → growth potential
- "tăng giá" → price appreciation
- "sinh lời" → ROI, rental yield
- "đầu tư" → investment properties
- "cho thuê" → rental properties

**Investment hotspots:**
- Thủ Đức (new city center)
- Quận 9 → Thủ Đức (infrastructure development)
- Nhà Bè (southern development)

## Common Query Patterns

**Pattern: Location + Property Type**
Example: "Nhà phố Quận 2"
→ Expand: Townhouse in District 2, alley or frontage, 3-4 floors

**Pattern: Budget + Requirements**
Example: "5 tỷ có hồ bơi"
→ Expand: Apartment with pool, District 7/2, 70-90m²

**Pattern: Investment Intent**
Example: "Mua để cho thuê"
→ Expand: High rental yield, near metro, universities, offices

**Pattern: Lifestyle Requirements**
Example: "Phù hợp gia đình có con nhỏ"
→ Expand: Near schools, parks, safe area, 2-3 bedrooms

## Ambiguity Triggers

**Too broad (needs clarification):**
- "Nhà ở Quận 2" → Which area? Thảo Điền, An Phú, Cát Lái?
- "5 tỷ" → What property type? Apartment, townhouse, land?
- "Nhà đẹp" → Define "đẹp": modern, luxury, good view?

**Multiple intents:**
- "So sánh giá và tìm nhà" → Comparison + Search
- "Tư vấn đầu tư khu Thủ Đức" → Investment advice + Area analysis

## Synonyms and Variations

**Property types:**
- Căn hộ: apartment, condo, chung cư, căn hộ chung cư
- Biệt thự: villa, nhà vườn, biệt thự sân vườn
- Nhà phố: townhouse, nhà riêng, nhà phố liền kề

**Amenities:**
- Hồ bơi: pool, swimming pool, bể bơi
- Gym: fitness, phòng gym, phòng tập
- An ninh: security, bảo vệ, guard

**Locations:**
- Q2: Quận 2, District 2, D2
- Q7: Quận 7, District 7, D7, Phú Mỹ Hưng
- Thủ Đức: Thu Duc, TD, Thủ Thiêm

## Query Expansion Rules

1. **Always expand location to specific areas if missing**
2. **Add amenity synonyms to search terms**
3. **Infer property type from context if missing**
4. **Add price range filters if budget mentioned**
5. **Include related amenities (pool → gym, parking)**
6. **Expand radius for proximity searches (school: 2km)**

## Confidence Scoring

**High confidence (>= 0.9):**
- Specific property type + location + clear requirements
- Example: "Căn hộ 2PN Thảo Điền có hồ bơi"

**Medium confidence (0.6-0.9):**
- Missing some details but intent is clear
- Example: "Nhà Quận 2 giá dưới 5 tỷ"

**Low confidence (< 0.6):**
- Too vague, multiple interpretations
- Example: "Tìm nhà đẹp"

# Foreign Master Data Documentation

## Overview

This document describes the foreign master data implementation for the REE-AI platform. The system now supports multiple countries: **Vietnam, Japan, China, and South Korea**.

## Architecture

### Database Schema

The foreign master data extends the existing master data system with:

1. **Core Tables**
   - `master_countries` - Country information and metadata
   - `master_currencies` - Currency definitions and exchange rates
   - `master_unit_conversions` - Area and currency unit conversions
   - `master_country_features` - Country-specific property features

2. **Extended Tables** (with `country_id` foreign key)
   - `master_districts` - Now supports cities from all countries
   - `master_property_types` - Includes country-specific property types
   - `master_legal_status` - Country-specific legal frameworks
   - `master_developers` - Developers from all markets
   - `master_projects` - Projects across multiple countries
   - `master_streets` - Streets with country context

## Supported Countries

### 1. Vietnam (VNM) 🇻🇳
**Currency:** Vietnamese Dong (VND) - ₫
**Region:** Southeast Asia
**Cities:** Ho Chi Minh City (24 districts)

**Property Types:**
- Căn hộ (Apartment)
- Nhà phố (Townhouse)
- Biệt thự (Villa)
- Đất nền (Land)

**Legal Status:**
- Sổ đỏ (Red book)
- Sổ hồng (Pink book)
- Giấy tờ hợp lệ (Valid documents)

**Major Developers:**
- Vingroup, Novaland, CapitaLand, Keppel Land, Mapletree

---

### 2. Japan (JPN) 🇯🇵
**Currency:** Japanese Yen (JPY) - ¥
**Region:** East Asia
**Cities:** Tokyo (Shibuya, Shinjuku, Minato, Chiyoda), Osaka, Kyoto, Yokohama, Nagoya, Fukuoka, Sapporo

**Property Types:**
- **Mansion (マンション)** - Japanese apartment/condo (30-150㎡)
- **Apāto (アパート)** - Older apartment building (20-60㎡)
- **Ikkodate (一戸建て)** - Detached house (80-300㎡)
- **Terrace House (テラスハウス)** - Townhouse (60-150㎡)
- **Machiya (町家)** - Traditional townhouse (50-200㎡)
- **Tower Mansion (タワーマンション)** - Luxury high-rise (50-300㎡)

**Legal Status:**
- 所有権 (Ownership rights) - Full ownership
- 借地権 (Leasehold rights) - Land lease
- 区分所有権 (Condominium title) - Condo ownership

**Country-Specific Features:**
- **Tatami Room (和室)** - Traditional Japanese room (+5% value)
- **Genkan (玄関)** - Traditional entrance hall
- **Earthquake Resistant (耐震構造)** - Seismic compliance (+10% value)
- **Auto-lock Entry (オートロック)** - Security system (+5% value)

**Major Developers:**
- Mitsui Fudosan (三井不動産)
- Mitsubishi Estate (三菱地所)
- Sumitomo Realty (住友不動産)
- Nomura Real Estate (野村不動産)
- Tokyu Land (東急不動産)
- Daito Trust (大東建託)

**Area Units:**
- 1 tsubo (坪) = 3.306㎡
- Common sizes: 50㎡ (15 tsubo), 70㎡ (21 tsubo), 100㎡ (30 tsubo)

---

### 3. China (CHN) 🇨🇳
**Currency:** Chinese Yuan/Renminbi (CNY) - ¥
**Region:** East Asia
**Cities:** Beijing (Chaoyang, Haidian), Shanghai (Pudong, Huangpu), Guangzhou (Tianhe), Shenzhen (Futian, Nanshan), Chengdu, Hangzhou, Nanjing

**Property Types:**
- **Apartment (公寓)** - Standard apartment (40-200㎡)
- **Villa (别墅)** - Detached house (150-800㎡)
- **Townhouse (联排别墅)** - Linked villa (100-300㎡)
- **Siheyuan (四合院)** - Courtyard house (200-1000㎡)
- **Serviced Apartment (酒店式公寓)** - Hotel-style apartment (30-150㎡)
- **Loft (阁楼)** - Loft/SOHO (40-200㎡)

**Legal Status:**
- **商品房 (Commodity house)** - Full commercial property rights
- **不动产权证 (Red book)** - Property certificate
- **双证齐全 (Dual certificate)** - Land + house certificate
- **70年产权 (70-year lease)** - Residential property rights
- **50年产权 (50-year lease)** - Commercial property rights
- **小产权房 (Small property rights)** - Village property (lower trust)

**Country-Specific Features:**
- **Feng Shui (风水好)** - Good feng shui orientation (+10% value)
- **Lucky Floor Number (吉祥楼层)** - Contains 8, avoids 4 (+5% value)
- **School District (学区房)** - Desirable school zone (+20% value)
- **Near Subway (地铁房)** - Walking distance to metro (+15% value)
- **Gated Community (封闭小区)** - Secure compound (+10% value)

**Major Developers:**
- China Vanke (万科)
- Country Garden (碧桂园)
- Poly Developments (保利)
- Longfor Properties (龙湖)
- Sunac China (融创)
- Greenland Holdings (绿地)

**Cultural Notes:**
- Floor numbers with "4" (sounds like "death") are less desirable
- Floor numbers with "8" (sounds like "prosperity") are premium
- South-facing properties are most desirable (feng shui)
- School district properties command 20-30% premium

---

### 4. South Korea (KOR) 🇰🇷
**Currency:** South Korean Won (KRW) - ₩
**Region:** East Asia
**Cities:** Seoul (Gangnam, Jongno, Mapo), Busan (Haeundae), Incheon, Daegu, Daejeon, Gwangju, Jeju

**Property Types:**
- **Apartment (아파트)** - Korean apartment complex (40-250㎡)
- **Villa (빌라)** - Multi-family house (30-100㎡)
- **Officetel (오피스텔)** - Studio apartment (15-60㎡)
- **Detached House (단독주택)** - Single house (80-400㎡)
- **Townhouse (연립주택)** - Multi-unit housing (60-150㎡)
- **Hanok (한옥)** - Traditional Korean house (80-300㎡)

**Legal Status:**
- **소유권 (Ownership rights)** - Full ownership
- **등기 (Property registration)** - Registration certificate
- **전세권 (Jeonse right)** - Lease deposit system
- **월세 (Monthly rent)** - Monthly rental

**Country-Specific Features:**
- **Ondol Heating (온돌)** - Underfloor heating (+5% value)
- **Brand Apartment (브랜드 아파트)** - Major developer brand (+15% value)
- **Near Subway (역세권)** - Station area (+15% value)
- **School District (학군)** - Good school zone (+20% value)

**Major Developers:**
- Samsung C&T (삼성물산) - Raemian brand
- Hyundai E&C (현대건설) - Hillstate, I-Park brands
- Daewoo E&C (대우건설) - Prugio brand
- POSCO E&C (포스코건설) - The Sharp brand
- GS E&C (GS건설) - Xi brand
- Lotte E&C (롯데건설) - Lotte Castle brand

**Area Units:**
- 1 pyeong (평) = 3.306㎡
- Common sizes: 24평 (79㎡), 32평 (106㎡), 40평 (132㎡)

**Rental Systems:**
- **Jeonse (전세)** - Large deposit (50-80% of property value), no monthly rent
- **Wolse (월세)** - Smaller deposit + monthly rent
- **Ban-jeonse (반전세)** - Medium deposit + reduced monthly rent

---

## Unit Conversions

### Area Units

| From | To | Conversion Factor | Example |
|------|----|--------------------|---------|
| m² | sqft | × 10.7639 | 100㎡ = 1,076.39 sqft |
| sqft | m² | × 0.092903 | 1,000 sqft = 92.9㎡ |
| m² | tsubo (坪) | × 0.3025 | 100㎡ = 30.25 tsubo |
| tsubo | m² | × 3.30579 | 30 tsubo = 99.17㎡ |
| m² | pyeong (평) | × 0.3025 | 100㎡ = 30.25 pyeong |
| pyeong | m² | × 3.30579 | 32 pyeong = 105.79㎡ |

### Currency Exchange Rates (Approximate)

| Currency | Symbol | To USD | Example |
|----------|--------|--------|---------|
| VND | ₫ | ÷ 24,500 | ₫2,450,000,000 ≈ $100,000 |
| JPY | ¥ | ÷ 150 | ¥15,000,000 ≈ $100,000 |
| CNY | ¥ | ÷ 7.25 | ¥725,000 ≈ $100,000 |
| KRW | ₩ | ÷ 1,320 | ₩132,000,000 ≈ $100,000 |

**Note:** Exchange rates are approximate and for reference only. Use real-time rates for actual transactions.

---

## Database Queries

### Get All Countries

```sql
SELECT code, name_en, name_local, default_currency_code, is_primary
FROM master_countries
WHERE active = TRUE
ORDER BY popularity_rank;
```

### Get Cities by Country

```sql
-- Japan cities
SELECT d.code, d.name_en, d.city, d.region
FROM master_districts d
JOIN master_countries c ON d.country_id = c.id
WHERE c.code = 'JPN' AND d.active = TRUE
ORDER BY d.city, d.name_en;
```

### Get Property Types by Country

```sql
-- Country-specific property types
SELECT code, name_en, category, typical_min_area, typical_max_area
FROM master_property_types
WHERE country_id = (SELECT id FROM master_countries WHERE code = 'JPN')
  AND active = TRUE;

-- Global property types (available in all countries)
SELECT code, name_en, category
FROM master_property_types
WHERE is_global = TRUE AND active = TRUE;
```

### Get Developers by Country

```sql
-- Major developers in China
SELECT d.code, d.name_en, d.reputation_score, d.total_projects
FROM master_developers d
JOIN master_countries c ON d.country_id = c.id
WHERE c.code = 'CHN' AND d.active = TRUE
ORDER BY d.reputation_score DESC, d.total_projects DESC;
```

### Convert Area Units

```sql
-- Convert 100㎡ to pyeong (Korean unit)
SELECT from_unit, to_unit, 100 * conversion_factor as result
FROM master_unit_conversions
WHERE unit_type = 'area'
  AND from_unit = 'm2'
  AND to_unit = 'pyeong';
-- Result: 30.25 pyeong
```

---

## API Endpoints

### Countries

```http
GET /master-data/countries
GET /master-data/countries/{country_code}
```

**Response:**
```json
{
  "countries": [
    {
      "code": "JPN",
      "code_2": "JP",
      "name_en": "Japan",
      "name_local": "日本",
      "name_vi": "Nhật Bản",
      "default_currency": "JPY",
      "is_primary": true
    }
  ]
}
```

### Currencies

```http
GET /master-data/currencies
GET /master-data/currencies/{currency_code}
```

**Response:**
```json
{
  "currencies": [
    {
      "code": "JPY",
      "symbol": "¥",
      "name_en": "Japanese Yen",
      "decimal_places": 0,
      "exchange_rate_to_usd": 150.0
    }
  ]
}
```

### Cities by Country

```http
GET /master-data/cities?country={country_code}
```

**Response:**
```json
{
  "cities": [
    {
      "code": "JP_TOKYO",
      "name_en": "Tokyo",
      "country": "JPN",
      "region": "Kanto"
    }
  ]
}
```

### Property Types by Country

```http
GET /master-data/property-types?country={country_code}
```

**Response:**
```json
{
  "property_types": [
    {
      "code": "JP_MANSION",
      "name_en": "Mansion",
      "name_local": "マンション",
      "category": "residential",
      "typical_area": "30-150㎡"
    }
  ]
}
```

---

## Migration & Seeding

### Run Migrations

```bash
# Apply migration 008
psql -U postgres -d ree_ai_db -f database/migrations/008_create_foreign_master_data.sql
```

### Run Seeds

```bash
# Seed countries and currencies (must run first)
psql -U postgres -d ree_ai_db -f database/seeds/004_seed_foreign_master_data.sql

# Seed property data (run after 004)
psql -U postgres -d ree_ai_db -f database/seeds/005_seed_foreign_property_data.sql
```

### Verify Data

```sql
-- Check country count
SELECT COUNT(*) FROM master_countries WHERE active = TRUE;
-- Expected: 4 (Vietnam, Japan, China, Korea)

-- Check currency count
SELECT COUNT(*) FROM master_currencies WHERE active = TRUE;
-- Expected: 5 (VND, JPY, CNY, KRW, USD)

-- Check cities per country
SELECT c.name_en, COUNT(d.id) as city_count
FROM master_countries c
LEFT JOIN master_districts d ON c.id = d.country_id
WHERE c.active = TRUE
GROUP BY c.name_en
ORDER BY city_count DESC;
```

---

## Localization Support

All master data includes multilingual names:

- **name_en** - English name (for API/storage)
- **name_local** - Local language name (日本, 中国, 대한민국)
- **name_vi** - Vietnamese name (Nhật Bản, Trung Quốc, Hàn Quốc)
- **aliases** - Array of alternate names for flexible matching

### NLP Matching Examples

Users can search in any language:

```
"Tìm căn hộ ở Tokyo"        → Matches JP_TOKYO
"マンション in Shibuya"      → Matches JP_MANSION + JP_SHIBUYA
"Find apartment in 北京"     → Matches CN_APARTMENT + CN_BEIJING
"강남 아파트"                → Matches KR_GANGNAM + KR_APARTMENT
```

---

## Implementation Notes

### Foreign Key Relationships

- All existing tables extended with optional `country_id`
- Vietnam data gets `country_id` set retroactively
- New data must specify country
- Global property types (apartment, villa, etc.) have `is_global = TRUE`

### Performance Considerations

- GIN indexes on `aliases` arrays for fast text search
- B-tree indexes on `country_id` for filtering
- Partial indexes on `active = TRUE` for common queries

### Data Integrity

- Cascading deletes: country → country_features
- Set NULL on delete: country → districts, developers, projects
- Check constraints on scores, levels, and enums

---

## Future Enhancements

### Planned Countries
- Singapore (SGP)
- Thailand (THA)
- Malaysia (MYS)
- Indonesia (IDN)
- Philippines (PHL)

### Additional Features
- Historical exchange rates
- Regional price indexes
- Country-specific regulations
- Tax information
- Mortgage calculators per country

---

## References

### Japan Real Estate
- [Japan Property Central](https://japanpropertycentral.com/)
- [Real Estate Japan](https://realestate.co.jp/)
- Tsubo conversion: 1坪 = 3.306㎡

### China Real Estate
- Property rights: 70-year residential, 50-year commercial
- School district premiums: 20-30%
- Feng shui importance in pricing

### Korea Real Estate
- Jeonse system unique to Korea
- Brand apartments command premium
- Pyeong standard unit: 1평 = 3.306㎡

---

## Support

For questions or issues with foreign master data:

1. Check this documentation
2. Review seed data in `database/seeds/004_*.sql` and `005_*.sql`
3. Verify migrations in `database/migrations/008_*.sql`
4. Contact development team

**Last Updated:** 2025-01-11
**Version:** 1.0.0

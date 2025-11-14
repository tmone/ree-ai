"""
Analyze Master Data to understand what fields are needed for property posting
"""
import asyncio
import asyncpg
import sys
import io

# Fix encoding on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

async def analyze_master_data():
    conn = await asyncpg.connect(
        host='103.153.74.213',
        port=5432,
        database='ree_ai',
        user='ree_ai_user',
        password='ree_ai_pass_2025'
    )

    print('=' * 100)
    print('MASTER DATA ANALYSIS - What fields do we need for property posting?')
    print('=' * 100)

    # 1. Property Types
    print('\n1. PROPERTY TYPES (Loại BDS):')
    types = await conn.fetch('SELECT code, name_vi, name_en FROM ree_common.property_types LIMIT 15')
    for t in types:
        print(f'   - {t["code"]}: {t["name_vi"]} ({t["name_en"]})')
    type_count = await conn.fetchval('SELECT COUNT(*) FROM ree_common.property_types')
    print(f'   Total: {type_count} types')

    # 2. Furniture Types
    print('\n2. FURNITURE TYPES (Noi that):')
    furnitures = await conn.fetch('SELECT code, name_vi, name_en FROM ree_common.furniture_types')
    for f in furnitures:
        print(f'   - {f["code"]}: {f["name_vi"]} ({f["name_en"]})')

    # 3. Directions
    print('\n3. DIRECTIONS (Huong nha):')
    directions = await conn.fetch('SELECT code, name_vi, name_en FROM ree_common.directions')
    for d in directions:
        print(f'   - {d["code"]}: {d["name_vi"]} ({d["name_en"]})')

    # 4. Legal Status
    print('\n4. LEGAL STATUS (Tinh trang phap ly):')
    legal = await conn.fetch('SELECT code, name_vi, name_en FROM ree_common.legal_status')
    for l in legal:
        print(f'   - {l["code"]}: {l["name_vi"]} ({l["name_en"]})')

    # 5. Property Conditions
    print('\n5. PROPERTY CONDITIONS (Tinh trang):')
    conditions = await conn.fetch('SELECT code, name_vi, name_en FROM ree_common.property_conditions')
    for c in conditions:
        print(f'   - {c["code"]}: {c["name_vi"]} ({c["name_en"]})')

    # 6. Views
    print('\n6. VIEWS (Tam nhin):')
    views = await conn.fetch('SELECT code, name_vi, name_en FROM ree_common.views LIMIT 15')
    for v in views:
        print(f'   - {v["code"]}: {v["name_vi"]} ({v["name_en"]})')
    view_count = await conn.fetchval('SELECT COUNT(*) FROM ree_common.views')
    print(f'   Total: {view_count} views')

    # 7. Amenities
    print('\n7. AMENITIES (Tien ich):')
    amenities = await conn.fetch('SELECT code, name_vi, name_en, category FROM ree_common.amenities LIMIT 30')
    for a in amenities:
        category = a.get('category', 'N/A')
        print(f'   - {a["code"]}: {a["name_vi"]} ({a["name_en"]}) [{category}]')
    amenity_count = await conn.fetchval('SELECT COUNT(*) FROM ree_common.amenities')
    print(f'   Total: {amenity_count} amenities')

    # 8. Transaction Types
    print('\n8. TRANSACTION TYPES (Loai giao dich):')
    transactions = await conn.fetch('SELECT code, name_vi, name_en FROM ree_common.transaction_types')
    for tx in transactions:
        print(f'   - {tx["code"]}: {tx["name_vi"]} ({tx["name_en"]})')

    # Summary
    print('\n' + '=' * 100)
    print('SUMMARY - Fields needed for COMPLETE property posting:')
    print('=' * 100)
    print('''
CORE FIELDS (REQUIRED):
  1. property_type - Loại BDS (apartment, house, villa, land, commercial)
  2. transaction_type - Loại giao dịch (sale, rent, both)
  3. district - Quận/Huyện
  4. price - Giá (sale) / price_rent - Giá thuê (rent)
  5. area - Diện tích (m2)
  6. bedrooms - Số phòng ngủ (not for land)
  7. bathrooms - Số phòng tắm

LOCATION DETAILS (HIGHLY RECOMMENDED):
  8. ward - Phường/Xã
  9. street - Đường
  10. address - Địa chỉ đầy đủ
  11. project_name - Tên dự án (if any)

PROPERTY DETAILS (RECOMMENDED):
  12. direction - Hướng nhà (N/S/E/W/NE/NW/SE/SW)
  13. balcony_direction - Hướng ban công
  14. furniture_type - Nội thất (full/basic/none/luxury)
  15. legal_status - Pháp lý (red book, pink book, contract, none)
  16. property_condition - Tình trạng (new, old, under construction)
  17. view_type - Tầm nhìn (river, city, garden, mountain, etc.)
  18. floors - Số tầng
  19. facade_width - Mặt tiền (m)
  20. year_built - Năm xây dựng

AMENITIES (OPTIONAL but IMPORTANT):
  21. amenities[] - Danh sách tiện ích:
      - Swimming pool
      - Gym
      - Parking
      - Security 24/7
      - Elevator
      - Playground
      - Garden
      - etc. (30+ options available)

CONTACT INFO:
  22. contact_name - Tên liên hệ
  23. contact_phone - Số điện thoại
  24. contact_type - Chính chủ/Môi giới/Sàn

ADDITIONAL:
  25. description - Mô tả chi tiết
  26. images[] - Ảnh (URLs)
    ''')

    print('\n' + '=' * 100)
    print('CURRENT PROBLEM:')
    print('=' * 100)
    print('''
❌ Orchestrator chỉ hỏi 4 fields: district, bedrooms, area, price
✅ Nên hỏi ít nhất 15-20 fields để có tin đăng HOÀN CHỈNH
✅ Master data có sẵn 100+ options cho amenities, directions, views, etc.
✅ Cần intelligent questioning: hỏi fields quan trọng dựa trên property_type
    ''')

    await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_master_data())

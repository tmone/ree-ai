#!/usr/bin/env python3
"""Quick script to check database property data"""
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="ree_ai",
    user="ree_ai_user",
    password="ree_ai_pass_2025"
)

cursor = conn.cursor(cursor_factory=RealDictCursor)

# Check sample properties
cursor.execute("""
    SELECT property_id, title, bedrooms, bathrooms, property_type, district, price
    FROM properties
    WHERE title LIKE '%phòng ngủ%'
    LIMIT 10
""")

print("🔍 Sample properties với 'phòng ngủ' trong title:\n")
for i, row in enumerate(cursor.fetchall(), 1):
    print(f"{i}. Property ID: {row['property_id']}")
    print(f"   Title: {row['title'][:80]}...")
    print(f"   Bedrooms: {row['bedrooms']} ❌" if row['bedrooms'] == 0 else f"   Bedrooms: {row['bedrooms']} ✅")
    print(f"   Property Type: '{row['property_type']}' ❌" if not row['property_type'] else f"   Property Type: '{row['property_type']}' ✅")
    print(f"   District: {row['district']}")
    print()

# Check statistics
cursor.execute("""
    SELECT
        COUNT(*) as total,
        COUNT(*) FILTER (WHERE bedrooms > 0) as with_bedrooms,
        COUNT(*) FILTER (WHERE property_type != '' AND property_type IS NOT NULL) as with_type
    FROM properties
""")
stats = cursor.fetchone()

print("\n📊 Database Statistics:")
print(f"Total properties: {stats['total']}")
print(f"Properties with bedrooms > 0: {stats['with_bedrooms']} ({stats['with_bedrooms']/stats['total']*100:.1f}%)")
print(f"Properties with property_type: {stats['with_type']} ({stats['with_type']/stats['total']*100:.1f}%)")

cursor.close()
conn.close()

"""
Crawl additional Batdongsan categories to reach 20K+ properties
"""
import asyncio
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / '.env')

import psycopg2
from psycopg2.extras import execute_values
from services.crawler.simple_crawler import SimpleBatdongsanCrawler


async def crawl_category(base_url: str, category_name: str, target: int = 5000):
    """Crawl a specific Batdongsan category"""
    print(f"\n{'='*70}")
    print(f"🚀 Crawling {category_name}")
    print(f"📍 URL: {base_url}")
    print(f"🎯 Target: {target} properties")
    print(f"{'='*70}\n")

    # Same selectors as for-sale (perfect 10/10)
    config = {
        'card_selector': '.re__card-full',
        'title_selector': '.re__card-title',
        'price_selector': '.re__card-config-price',
        'location_selector': '.re__card-location',
        'area_selector': '.re__card-config-area',
        'link_selector': 'a',
        'pagination_pattern': '/p{page}',
        'max_pages': 500,
        'rate_limit': 3.0
    }

    crawler = SimpleBatdongsanCrawler(base_url, config)
    properties = await crawler.crawl(target_properties=target)

    print(f"\n✅ Crawled {len(properties)} properties from {category_name}")

    if len(properties) > 0:
        # Sample
        sample = properties[0]
        print(f"   Sample: {sample.get('title', '')[:60]}...")
        print(f"   Price: {sample.get('price', 'N/A')}")
        print(f"   Location: {sample.get('location', 'N/A')}")

    return properties, category_name


async def store_properties(properties, source):
    """Store properties in PostgreSQL"""
    use_local = os.getenv('USE_LOCAL_POSTGRES', 'true').lower() == 'true'
    pg_host = 'localhost' if use_local else 'postgres'
    pg_port = int(os.getenv('POSTGRES_PORT', 5432))
    pg_db = os.getenv('POSTGRES_DB', 'ree_ai')
    pg_user = os.getenv('POSTGRES_USER', 'ree_ai_user')
    pg_pass = os.getenv('POSTGRES_PASSWORD', 'ree_ai_pass_2025')

    print(f"\n💾 Storing {len(properties)} properties in PostgreSQL...")

    conn = psycopg2.connect(
        host=pg_host,
        port=pg_port,
        database=pg_db,
        user=pg_user,
        password=pg_pass
    )
    cursor = conn.cursor()

    values = []
    for prop in properties:
        values.append((
            prop.get('title', ''),
            prop.get('price', ''),
            prop.get('location', ''),
            0,  # bedrooms
            0,  # bathrooms
            prop.get('area', ''),
            prop.get('description', ''),
            prop.get('url', ''),
            source  # source
        ))

    execute_values(
        cursor,
        """
        INSERT INTO properties
        (title, price, location, bedrooms, bathrooms, area, description, url, source)
        VALUES %s
        ON CONFLICT (url) DO NOTHING
        """,
        values
    )

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM properties")
    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print(f"✅ Stored! Total properties in database: {total}")
    return total


async def main():
    """Crawl all Batdongsan categories"""
    categories = [
        ('https://batdongsan.com.vn/nha-dat-cho-thue', 'Cho Thuê', 5000),
        ('https://batdongsan.com.vn/ban-can-ho-chung-cu', 'Căn Hộ', 5000),
        ('https://batdongsan.com.vn/ban-dat-nen-du-an', 'Đất', 5000),
    ]

    for base_url, name, target in categories:
        try:
            properties, source = await crawl_category(base_url, name, target)
            if len(properties) > 0:
                await store_properties(properties, source)
        except Exception as e:
            print(f"❌ Error crawling {name}: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*70}")
    print("✅ Multi-category crawl complete!")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())

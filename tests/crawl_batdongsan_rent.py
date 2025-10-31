"""
Quick test: Crawl Batdongsan rental properties (same selectors as for-sale)
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


async def test_rental_crawl():
    """Test crawling rental category with same selectors"""
    from services.crawler.crawler import BatdongsanCrawler

    print("🏠 Testing Batdongsan RENTAL category...")
    print("=" * 70)

    # Update the config to use rental URL
    config = {
        'base_url': 'https://batdongsan.com.vn/nha-dat-cho-thue',
        'property_card_selector': '.re__card-full',
        'title_selector': '.re__card-title',
        'price_selector': '.re__card-config-price',
        'location_selector': '.re__card-location',
        'area_selector': '.re__card-config-area',
        'link_selector': 'a',
        'pagination_pattern': '/p{page}',
        'max_pages': 10,  # Test with 10 pages first
        'rate_limit': 3.0
    }

    crawler = BatdongsanCrawler(config)

    # Crawl 200 properties (10 pages × 20 props/page)
    properties = []
    for page in range(1, 11):
        url = f"{config['base_url']}/p{page}"
        print(f"📄 Crawling page {page}: {url}")

        try:
            page_props = await crawler.crawl_page(url)
            properties.extend(page_props)
            print(f"   ✅ Found {len(page_props)} properties")

            if len(page_props) > 0 and page == 1:
                print(f"   Sample: {page_props[0].get('title', '')[:60]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        await asyncio.sleep(config['rate_limit'])

    print(f"\n✅ Total crawled: {len(properties)} rental properties")

    # Store in database
    if len(properties) > 0:
        print(f"\n💾 Storing in PostgreSQL...")

        pg_host = 'localhost'
        pg_db = 'ree_ai'
        pg_user = 'ree_ai_user'
        pg_pass = 'ree_ai_pass_2025'

        conn = psycopg2.connect(host=pg_host, database=pg_db, user=pg_user, password=pg_pass)
        cursor = conn.cursor()

        values = [(
            p.get('title', ''),
            p.get('price', ''),
            p.get('location', ''),
            0, 0,
            p.get('area', ''),
            p.get('description', ''),
            p.get('url', ''),
            'batdongsan-rent'
        ) for p in properties]

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

        print(f"✅ Stored! Total in database: {total}")

        cursor.close()
        conn.close()


if __name__ == "__main__":
    asyncio.run(test_rental_crawl())

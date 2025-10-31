"""
Crawl from page 506 onwards to get NEW properties
Skip pages 1-505 that are already in database
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
from crawl4ai import WebCrawler
from bs4 import BeautifulSoup


async def crawl_from_page(start_page: int, total_properties: int):
    """Crawl starting from a specific page number"""

    print(f"🚀 Starting crawl from page {start_page} for {total_properties} properties...")

    base_url = "https://batdongsan.com.vn/nha-dat-ban"
    properties = []

    # CSS selectors (perfect 10/10 quality)
    selectors = {
        "card": ".re__card-full",
        "title": ".re__card-title",
        "price": ".re__card-config-price",
        "location": ".re__card-location",
        "area": ".re__card-config-area",
        "link": "a"
    }

    # Initialize crawler
    crawler = WebCrawler()
    crawler.warmup()

    page_num = start_page

    while len(properties) < total_properties:
        url = f"{base_url}/p{page_num}"
        print(f"📄 Crawling page {page_num}: {url}")

        try:
            result = crawler.run(url=url)

            if not result.success:
                print(f"   ❌ Failed to crawl {url}")
                page_num += 1
                continue

            # Parse HTML
            soup = BeautifulSoup(result.html, 'html.parser')
            cards = soup.select(selectors["card"])

            print(f"   ✅ Found {len(cards)} properties on page {page_num}")

            # Extract each property
            for card in cards:
                try:
                    # Extract title
                    title_elem = card.select_one(selectors["title"])
                    title = title_elem.get_text(strip=True) if title_elem else ""

                    # Extract price
                    price_elem = card.select_one(selectors["price"])
                    price = price_elem.get_text(strip=True) if price_elem else ""

                    # Extract location
                    location_elem = card.select_one(selectors["location"])
                    location = location_elem.get_text(strip=True) if location_elem else ""

                    # Extract area
                    area_elem = card.select_one(selectors["area"])
                    area = area_elem.get_text(strip=True) if area_elem else ""

                    # Extract URL
                    link_elem = card.select_one(selectors["link"])
                    url_path = link_elem.get('href', '') if link_elem else ""
                    full_url = f"https://batdongsan.com.vn{url_path}" if url_path.startswith('/') else url_path

                    if full_url:
                        properties.append({
                            'title': title,
                            'price': price,
                            'location': location,
                            'area': area,
                            'url': full_url,
                            'source': 'batdongsan'
                        })

                        if len(properties) >= total_properties:
                            break

                except Exception as e:
                    print(f"   ⚠️  Error extracting property: {e}")
                    continue

        except Exception as e:
            print(f"   ❌ Error crawling page {page_num}: {e}")

        page_num += 1

        # Rate limiting
        await asyncio.sleep(2.0)

        # Progress update every 100 properties
        if len(properties) % 100 == 0:
            print(f"📊 Progress: {len(properties)}/{total_properties} properties crawled")

    print(f"\n✅ Crawled {len(properties)} new properties")

    # Store in PostgreSQL
    print(f"\n💾 Storing in PostgreSQL...")

    use_local = os.getenv('USE_LOCAL_POSTGRES', 'true').lower() == 'true'
    pg_host = 'localhost' if use_local else 'postgres'
    pg_db = 'ree_ai'
    pg_user = 'ree_ai_user'
    pg_pass = 'ree_ai_pass_2025'

    conn = psycopg2.connect(host=pg_host, database=pg_db, user=pg_user, password=pg_pass)
    cursor = conn.cursor()

    values = [(
        p['title'],
        p['price'],
        p['location'],
        0, 0,  # bedrooms, bathrooms
        p['area'],
        '',  # description
        p['url'],
        p['source']
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

    return total


if __name__ == "__main__":
    start_page = int(sys.argv[1]) if len(sys.argv) > 1 else 506
    total = int(sys.argv[2]) if len(sys.argv) > 2 else 12000

    final_count = asyncio.run(crawl_from_page(start_page, total))

    print(f"\n{'='*70}")
    print(f"✅ CRAWL COMPLETE: {final_count} total properties in database")
    print(f"{'='*70}")

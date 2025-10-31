"""
Production-ready Smart Crawler with Auto-Resume
- Tự động phát hiện page đã crawl
- Resume từ page cuối cùng
- Track crawl state trong database
- Batch insert cho performance
"""
import asyncio
import os
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
from crawl4ai import WebCrawler
from bs4 import BeautifulSoup


class SmartCrawler:
    """Production crawler với auto-resume và state tracking"""

    def __init__(self, site_domain: str):
        self.site_domain = site_domain
        self.conn = self._get_db_connection()
        self.config = self._load_config()
        self.crawler = None

    def _get_db_connection(self):
        """Get PostgreSQL connection"""
        use_local = os.getenv('USE_LOCAL_POSTGRES', 'true').lower() == 'true'
        return psycopg2.connect(
            host='localhost' if use_local else 'postgres',
            database=os.getenv('POSTGRES_DB', 'ree_ai'),
            user=os.getenv('POSTGRES_USER', 'ree_ai_user'),
            password=os.getenv('POSTGRES_PASSWORD', 'ree_ai_pass_2025')
        )

    def _load_config(self) -> Dict:
        """Load crawler config from database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT base_url, selectors, pagination, rate_limit_seconds
            FROM crawl_configs
            WHERE site_domain = %s AND enabled = true
        """, (self.site_domain,))

        row = cursor.fetchone()
        if not row:
            raise ValueError(f"No config found for {self.site_domain}")

        base_url, selectors, pagination, rate_limit = row
        cursor.close()

        return {
            'base_url': base_url,
            'selectors': selectors,
            'pagination': pagination,
            'rate_limit': rate_limit
        }

    def get_resume_page(self) -> int:
        """
        Tự động tìm page number để resume crawl

        Strategy:
        1. Check crawl_jobs for last pages_crawled
        2. Estimate from properties count
        3. Default to page 1
        """
        cursor = self.conn.cursor()

        # Option 1: Check crawl_jobs table for last successful job
        cursor.execute("""
            SELECT pages_crawled
            FROM crawl_jobs
            WHERE site_domain = %s
              AND status = 'completed'
            ORDER BY completed_at DESC
            LIMIT 1
        """, (self.site_domain,))

        row = cursor.fetchone()
        if row and row[0]:
            last_page = int(row[0])
            cursor.close()
            print(f"📌 Found last crawled job: {last_page} pages")
            return last_page + 1

        # Option 2: Estimate from properties count
        # Batdongsan has ~20 properties/page
        cursor.execute("""
            SELECT COUNT(*) FROM properties WHERE source = %s
        """, (self.site_domain.split('.')[0],))  # 'batdongsan.com.vn' -> 'batdongsan'

        count = cursor.fetchone()[0]
        cursor.close()

        if count > 0:
            estimated_page = (count // 20) + 1
            print(f"📊 Estimated last page from {count} properties: ~{estimated_page}")
            return estimated_page

        print(f"🆕 No previous crawl found, starting from page 1")
        return 1

    def is_url_crawled(self, url: str) -> bool:
        """Check if URL đã được crawl chưa"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 1 FROM crawl_state
            WHERE site_domain = %s AND url_hash = %s
        """, (self.site_domain, url_hash))
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists

    def mark_url_crawled(self, url: str, property_id: Optional[int] = None):
        """Mark URL as crawled trong crawl_state"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO crawl_state (site_domain, url, url_hash, property_id, status)
            VALUES (%s, %s, %s, %s, 'active')
            ON CONFLICT (site_domain, url_hash)
            DO UPDATE SET last_seen = CURRENT_TIMESTAMP
        """, (self.site_domain, url, url_hash, property_id))
        self.conn.commit()
        cursor.close()

    async def crawl_page(self, page_num: int) -> Tuple[List[Dict], int, int]:
        """
        Crawl một page
        Returns: (properties, new_count, duplicate_count)
        """
        # Build URL
        base_url = self.config['base_url']
        pagination = self.config['pagination']
        url = f"{base_url}{pagination['pattern'].replace('{page}', str(page_num))}"

        print(f"📄 Crawling page {page_num}: {url}")

        # Crawl
        result = self.crawler.run(url=url)
        if not result.success:
            print(f"   ❌ Failed to crawl {url}")
            return [], 0, 0

        # Parse
        soup = BeautifulSoup(result.html, 'html.parser')
        selectors = self.config['selectors']
        cards = soup.select(selectors['card'])

        properties = []
        new_count = 0
        duplicate_count = 0

        for card in cards:
            try:
                # Extract URL first to check duplicate
                link_elem = card.select_one(selectors.get('link', 'a'))
                url_path = link_elem.get('href', '') if link_elem else ""
                full_url = f"https://{self.site_domain.split('.')[0]}.com.vn{url_path}" if url_path.startswith('/') else url_path

                if not full_url:
                    continue

                # Check if already crawled
                if self.is_url_crawled(full_url):
                    duplicate_count += 1
                    continue

                # Extract other fields
                title_elem = card.select_one(selectors.get('title', ''))
                title = title_elem.get_text(strip=True) if title_elem else ""

                price_elem = card.select_one(selectors.get('price', ''))
                price = price_elem.get_text(strip=True) if price_elem else ""

                location_elem = card.select_one(selectors.get('location', ''))
                location = location_elem.get_text(strip=True) if location_elem else ""

                area_elem = card.select_one(selectors.get('area', ''))
                area = area_elem.get_text(strip=True) if area_elem else ""

                properties.append({
                    'title': title,
                    'price': price,
                    'location': location,
                    'area': area,
                    'url': full_url,
                    'source': self.site_domain.split('.')[0]
                })
                new_count += 1

            except Exception as e:
                print(f"   ⚠️  Error extracting property: {e}")
                continue

        print(f"   ✅ Page {page_num}: {len(cards)} total, {new_count} new, {duplicate_count} duplicates")

        return properties, new_count, duplicate_count

    async def crawl_incremental(self, target_properties: int = 10000, max_pages: int = 1000):
        """
        Incremental crawl - chỉ crawl properties mới
        Tự động resume từ page cuối cùng
        """
        print(f"🚀 Starting incremental crawl for {self.site_domain}")
        print(f"🎯 Target: {target_properties} new properties")
        print(f"{'='*70}\n")

        # Auto-detect resume point
        start_page = self.get_resume_page()
        print(f"▶️  Resuming from page {start_page}\n")

        # Initialize crawler
        print(f"🔧 Initializing crawler...")
        self.crawler = WebCrawler()
        self.crawler.warmup()
        print(f"✅ Crawler ready!\n")

        # Crawl loop
        total_crawled = 0
        total_new = 0
        total_duplicates = 0
        consecutive_duplicates = 0

        for page_num in range(start_page, start_page + max_pages):
            # Crawl page
            properties, new_count, dup_count = await self.crawl_page(page_num)

            total_crawled += len(properties)
            total_new += new_count
            total_duplicates += dup_count

            # Track consecutive pages with all duplicates
            if new_count == 0 and len(properties) > 0:
                consecutive_duplicates += 1
            else:
                consecutive_duplicates = 0

            # Stop if 10 consecutive pages are all duplicates
            if consecutive_duplicates >= 10:
                print(f"\n⏹️  Stopping: 10 consecutive pages with all duplicates")
                break

            # Insert new properties
            if properties:
                self._batch_insert_properties(properties)

            # Progress
            if total_new > 0 and total_new % 100 == 0:
                print(f"📊 Progress: {total_new}/{target_properties} new properties")

            # Check target
            if total_new >= target_properties:
                print(f"\n🎉 Target reached! {total_new} new properties crawled")
                break

            # Rate limiting
            await asyncio.sleep(self.config['rate_limit'])

        # Summary
        print(f"\n{'='*70}")
        print(f"✅ Crawl completed!")
        print(f"   📄 Pages crawled: {page_num - start_page + 1}")
        print(f"   🆕 New properties: {total_new}")
        print(f"   🔄 Duplicates skipped: {total_duplicates}")
        print(f"{'='*70}\n")

        # Get total count
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM properties WHERE source = %s",
                      (self.site_domain.split('.')[0],))
        total = cursor.fetchone()[0]
        cursor.close()

        print(f"📊 Total properties in database: {total}\n")

        return total_new

    def _batch_insert_properties(self, properties: List[Dict]):
        """Batch insert properties vào database"""
        if not properties:
            return

        cursor = self.conn.cursor()

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

        # Insert properties
        execute_values(
            cursor,
            """
            INSERT INTO properties
            (title, price, location, bedrooms, bathrooms, area, description, url, source)
            VALUES %s
            ON CONFLICT (url) DO NOTHING
            RETURNING id, url
            """,
            values
        )

        # Get inserted IDs and mark as crawled
        inserted = cursor.fetchall()
        for prop_id, url in inserted:
            self.mark_url_crawled(url, prop_id)

        self.conn.commit()
        cursor.close()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


async def main():
    """Test smart crawler"""
    import sys

    site_domain = sys.argv[1] if len(sys.argv) > 1 else 'batdongsan.com.vn'
    target = int(sys.argv[2]) if len(sys.argv) > 2 else 10000

    crawler = SmartCrawler(site_domain)

    try:
        new_properties = await crawler.crawl_incremental(target_properties=target)
        print(f"✅ Successfully crawled {new_properties} new properties")
    finally:
        crawler.close()


if __name__ == "__main__":
    asyncio.run(main())

"""
Crawl Real Estate Sites and Build Master Data

This script provides an easy-to-use interface for crawling real estate
websites and building master data automatically.

Usage:
    python scripts/crawl_and_build_master_data.py
    python scripts/crawl_and_build_master_data.py --sites batdongsan mogi --max-pages 30
    python scripts/crawl_and_build_master_data.py --schedule daily
"""

import asyncio
import argparse
import httpx
import json
import time
from typing import List, Dict, Any
from datetime import datetime


# Configuration
CRAWLER_SERVICE_URL = "http://localhost:8095"
EXTRACTION_SERVICE_URL = "http://localhost:8084"
DEFAULT_MAX_PAGES = 20
DEFAULT_SITES = ["batdongsan", "mogi"]


class MasterDataCrawler:
    """
    Master Data Crawler - Automates data collection and master data building
    """

    def __init__(
        self,
        crawler_url: str = CRAWLER_SERVICE_URL,
        extraction_url: str = EXTRACTION_SERVICE_URL
    ):
        self.crawler_url = crawler_url
        self.extraction_url = extraction_url
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 minute timeout

    async def check_services(self) -> bool:
        """Check if required services are running"""
        print("\n" + "=" * 70)
        print("  Pre-Flight Checks")
        print("=" * 70)

        # Check crawler service
        try:
            response = await self.client.get(f"{self.crawler_url}/health")
            if response.status_code == 200:
                print("✓ Crawler Service is running")
            else:
                print("✗ Crawler Service returned error:", response.status_code)
                return False
        except Exception as e:
            print(f"✗ Crawler Service is not running: {e}")
            print("  Please start it with: docker-compose up -d crawler-service")
            return False

        # Check extraction service (optional)
        try:
            response = await self.client.get(f"{self.extraction_url}/health")
            if response.status_code == 200:
                print("✓ Extraction Service is running")
        except Exception:
            print("⚠ Extraction Service is not running (optional)")

        # Get available crawlers
        try:
            response = await self.client.get(f"{self.crawler_url}/crawlers")
            data = response.json()
            crawler_count = len(data.get("crawlers", []))
            print(f"✓ Found {crawler_count} crawler(s)")

            for crawler in data.get("crawlers", []):
                print(f"  - {crawler['id']}: {crawler['name']}")
        except Exception as e:
            print(f"⚠ Could not retrieve crawler list: {e}")

        return True

    async def crawl_site(
        self,
        site: str,
        max_pages: int = DEFAULT_MAX_PAGES,
        extract_master_data: bool = True,
        auto_populate: bool = True
    ) -> Dict[str, Any]:
        """
        Crawl a specific real estate site

        Args:
            site: Site to crawl ('batdongsan', 'mogi', or 'all')
            max_pages: Maximum pages to crawl
            extract_master_data: Whether to extract master data
            auto_populate: Whether to auto-populate pending_master_data

        Returns:
            Crawl results
        """
        print("\n" + "=" * 70)
        print(f"  Crawling: {site}")
        print("=" * 70)
        print(f"  ▸ Max Pages: {max_pages}")
        print(f"  ▸ Extract Master Data: {extract_master_data}")
        print(f"  ▸ Auto-Populate: {auto_populate}")
        print()

        request_data = {
            "site": site,
            "max_pages": max_pages,
            "extract_master_data": extract_master_data,
            "auto_populate": auto_populate
        }

        print("  Starting crawl (this may take a few minutes)...")

        start_time = time.time()

        try:
            response = await self.client.post(
                f"{self.crawler_url}/crawl",
                json=request_data
            )

            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                print("\n✅ Crawl completed successfully!")
                print()
                print(f"  ▸ Listings Scraped: {data['listings_scraped']}")
                print(f"  ▸ New Attributes Found: {data['new_attributes_found']}")
                print(f"  ▸ Processing Time: {data['processing_time_ms']:.0f}ms")
                print(f"  ▸ Total Duration: {duration:.1f}s")
                print()

                # Show sample listings
                if data.get('sample_listings'):
                    print("  Sample Listings:")
                    for idx, listing in enumerate(data['sample_listings'][:3], 1):
                        print(f"    {idx}. {listing.get('title', 'N/A')}")
                        print(f"       District: {listing.get('district', 'N/A')}")
                        print(f"       Price: {listing.get('price_text', 'N/A')}")
                        print(f"       Amenities: {', '.join(listing.get('amenities', []))}")
                        print()

                return data
            else:
                print(f"\n❌ Crawl failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                return None

        except Exception as e:
            print(f"\n❌ Crawl failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def get_master_data_status(self) -> Dict[str, Any]:
        """Get current master data status"""
        print("\n" + "=" * 70)
        print("  Master Data Status")
        print("=" * 70)
        print()

        try:
            response = await self.client.get(
                f"{self.extraction_url}/admin/pending-items?status=pending&limit=20"
            )

            if response.status_code == 200:
                data = response.json()

                total_pending = data.get('total_count', 0)
                high_frequency = data.get('high_frequency_items', 0)

                print(f"  ▸ Total Pending Items: {total_pending}")
                print(f"  ▸ High Frequency Items: {high_frequency} (priority review)")
                print()

                if total_pending > 0:
                    print("  Top Pending Items (by frequency):")
                    for item in data.get('pending_items', [])[:10]:
                        print(f"    - {item['value_english']} ({item['suggested_table']})")
                        print(f"      Frequency: {item['frequency']}, Status: {item['status']}")

                return data
            else:
                print(f"  ⚠ Could not retrieve pending items (status: {response.status_code})")
                return None

        except Exception as e:
            print(f"  ⚠ Could not retrieve pending items: {e}")
            return None

    async def crawl_all_sites(
        self,
        sites: List[str] = DEFAULT_SITES,
        max_pages: int = DEFAULT_MAX_PAGES
    ):
        """
        Crawl all specified sites

        Args:
            sites: List of sites to crawl
            max_pages: Maximum pages per site
        """
        print("\n" + "=" * 70)
        print("  🌐 Real Estate Data Crawler - Master Data Builder")
        print("=" * 70)
        print()
        print("  This script will crawl real estate websites and automatically")
        print("  discover new master data (amenities, features, locations, etc.)")
        print()
        print("  Settings:")
        print(f"  ├─ Sites: {', '.join(sites)}")
        print(f"  ├─ Max Pages: {max_pages} per site")
        print("  └─ Auto-Populate: Enabled")
        print()
        print("=" * 70)

        # Pre-flight checks
        if not await self.check_services():
            print("\n❌ Pre-flight checks failed. Please fix issues and try again.")
            return

        # Crawl each site
        results = []
        successful_crawls = 0

        for site in sites:
            result = await self.crawl_site(site, max_pages)

            if result:
                results.append(result)
                successful_crawls += 1

            # Wait between sites to avoid rate limiting
            if site != sites[-1]:  # Not the last site
                print(f"\n  ⏳ Waiting 10 seconds before next crawl...")
                await asyncio.sleep(10)

        # Summary
        print("\n" + "=" * 70)
        print("  Crawl Summary")
        print("=" * 70)
        print()
        print(f"  ▸ Sites Crawled: {successful_crawls}/{len(sites)}")

        total_listings = sum(r['listings_scraped'] for r in results)
        total_new_attrs = sum(r['new_attributes_found'] for r in results)

        print(f"  ▸ Total Listings: {total_listings}")
        print(f"  ▸ Total New Attributes: {total_new_attrs}")

        # Master data status
        await self.get_master_data_status()

        # Next steps
        print("\n" + "=" * 70)
        print("  Next Steps")
        print("=" * 70)
        print()
        print("  1. Review pending master data items:")
        print(f"     curl {self.extraction_url}/admin/pending-items?status=pending")
        print()
        print("  2. Approve high-frequency items (admin only):")
        print(f"     curl -X POST {self.extraction_url}/admin/approve-item \\")
        print('       -H "Content-Type: application/json" \\')
        print('       -d \'{"pending_id": 1, "translations": {...}, "admin_user_id": "admin"}\'')
        print()
        print("  3. View master data growth in Grafana:")
        print("     http://localhost:3001/d/master-data-growth")
        print()
        print("  4. Run extraction test with new master data:")
        print(f"     curl -X POST {self.extraction_url}/extract-with-master-data \\")
        print('       -H "Content-Type: application/json" \\')
        print('       -d \'{"text": "Căn hộ 2PN Quận 1 có hồ bơi"}\'')
        print()
        print("=" * 70)
        print("  ✅ Crawl completed!")
        print("=" * 70)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Crawl real estate sites and build master data"
    )

    parser.add_argument(
        '--sites',
        nargs='+',
        default=DEFAULT_SITES,
        help=f'Sites to crawl (default: {" ".join(DEFAULT_SITES)})'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f'Maximum pages per site (default: {DEFAULT_MAX_PAGES})'
    )

    parser.add_argument(
        '--crawler-url',
        default=CRAWLER_SERVICE_URL,
        help=f'Crawler service URL (default: {CRAWLER_SERVICE_URL})'
    )

    parser.add_argument(
        '--extraction-url',
        default=EXTRACTION_SERVICE_URL,
        help=f'Extraction service URL (default: {EXTRACTION_SERVICE_URL})'
    )

    parser.add_argument(
        '--schedule',
        choices=['once', 'daily', 'weekly'],
        default='once',
        help='Schedule crawling (default: once)'
    )

    args = parser.parse_args()

    # Create crawler
    crawler = MasterDataCrawler(
        crawler_url=args.crawler_url,
        extraction_url=args.extraction_url
    )

    try:
        if args.schedule == 'once':
            # Run once
            await crawler.crawl_all_sites(
                sites=args.sites,
                max_pages=args.max_pages
            )
        else:
            # Schedule periodic crawling
            print(f"\n⚠ Scheduled crawling ({args.schedule}) not yet implemented")
            print("  For now, use cron or Task Scheduler to run this script periodically")

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())

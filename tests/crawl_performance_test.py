#!/usr/bin/env python3
"""
Crawl Performance Test
Test crawl4ai effectiveness with Vietnam real estate sites
Focus on speed, success rate, and data quality
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import time
import json

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except ImportError:
    pass

from services.crawler.multi_site_orchestrator import MultiSiteOrchestrator, CrawlMode
import psycopg2
from psycopg2.extras import RealDictCursor

# Additional sites to test (manual configs)
ADDITIONAL_SITES = [
    {
        "site_domain": "mogi.vn",
        "site_name": "Mogi.vn",
        "base_url": "https://mogi.vn/mua-nha-dat",
        "selectors": {
            "card": ".prop-card",
            "title": ".prop-card__title",
            "price": ".prop-card__price",
            "location": ".prop-card__location",
            "area": ".prop-card__area",
            "description": ".prop-card__des",
            "link": "a"
        },
        "pagination": {
            "pattern": "?page={page}",
            "max_pages": 300,
            "per_page": 20
        },
        "rate_limit_seconds": 2.5,
        "max_workers": 4
    },
    {
        "site_domain": "alonhadat.com.vn",
        "site_name": "Alonhadat.com.vn",
        "base_url": "https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/1/viet-nam.html",
        "selectors": {
            "card": ".content-item",
            "title": ".text-link",
            "price": ".price",
            "location": ".address",
            "area": ".square",
            "description": ".content-info",
            "link": "a"
        },
        "pagination": {
            "pattern": "/nha-dat/can-ban/nha-dat/{page}/viet-nam.html",
            "max_pages": 200,
            "per_page": 20
        },
        "rate_limit_seconds": 2.0,
        "max_workers": 5
    },
    {
        "site_domain": "muaban.net",
        "site_name": "Muaban.net",
        "base_url": "https://muaban.net/nha-dat-cho-thue-cho-thue-can-ho-chung-cu-l35",
        "selectors": {
            "card": ".listing-card",
            "title": ".title",
            "price": ".price",
            "location": ".location",
            "area": ".area",
            "description": ".desc",
            "link": "a"
        },
        "pagination": {
            "pattern": "/nha-dat-cho-thue-cho-thue-can-ho-chung-cu-l35/p{page}",
            "max_pages": 150,
            "per_page": 20
        },
        "rate_limit_seconds": 2.0,
        "max_workers": 4
    }
]


class CrawlPerformanceTester:
    """Test crawl4ai performance across multiple sites"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'ree_ai'),
            'user': os.getenv('POSTGRES_USER', 'ree_ai_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'ree_ai_pass_2025')
        }

    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def add_test_sites(self):
        """Add additional test sites to database"""
        print(f"\n{'='*80}")
        print(f"📝 Adding {len(ADDITIONAL_SITES)} test sites to database...")
        print(f"{'='*80}\n")

        conn = self.get_db_connection()
        cursor = conn.cursor()

        added = 0
        for site in ADDITIONAL_SITES:
            try:
                cursor.execute(
                    """
                    INSERT INTO crawl_configs (
                        site_domain, site_name, base_url,
                        selectors, pagination,
                        rate_limit_seconds, max_workers,
                        quality_score, enabled
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true)
                    ON CONFLICT (site_domain) DO UPDATE SET
                        selectors = EXCLUDED.selectors,
                        pagination = EXCLUDED.pagination,
                        enabled = true
                    """,
                    (
                        site['site_domain'],
                        site['site_name'],
                        site['base_url'],
                        json.dumps(site['selectors']),
                        json.dumps(site['pagination']),
                        site['rate_limit_seconds'],
                        site['max_workers'],
                        8.0  # Default quality
                    )
                )
                print(f"   ✅ {site['site_name']}")
                added += 1
            except Exception as e:
                print(f"   ❌ {site['site_name']}: {e}")

        conn.commit()
        cursor.close()
        conn.close()

        print(f"\n✅ Added/updated {added} sites")

    async def run_crawl_test(self, properties_per_site: int = 100):
        """
        Run crawl test

        Args:
            properties_per_site: Target properties to crawl per site
        """
        print(f"\n{'='*80}")
        print(f"🚀 STARTING CRAWL PERFORMANCE TEST")
        print(f"   Target: {properties_per_site} properties per site")
        print(f"{'='*80}\n")

        orchestrator = MultiSiteOrchestrator(self.db_config)

        # Load enabled sites
        configs = await orchestrator.load_configs(enabled_only=True)

        if not configs:
            print("❌ No sites configured")
            return

        print(f"Found {len(configs)} enabled sites:\n")
        for i, config in enumerate(configs, 1):
            print(f"   {i}. {config.site_name} ({config.site_domain})")

        print(f"\n{'='*80}\n")

        # Crawl results
        results = []
        overall_start = time.time()

        for i, config in enumerate(configs, 1):
            print(f"\n[{i}/{len(configs)}] 🔍 Crawling: {config.site_name}")
            print(f"{'─'*60}")

            start_time = time.time()

            try:
                # Calculate pages needed
                pages_needed = max(1, (properties_per_site // config.pagination['per_page']) + 1)

                # Temporarily adjust config
                original_max_pages = config.pagination['max_pages']
                config.pagination['max_pages'] = min(pages_needed, 10)  # Max 10 pages for test

                # Crawl
                stats = await orchestrator.crawl_site(config, CrawlMode.INCREMENTAL)

                # Restore
                config.pagination['max_pages'] = original_max_pages

                crawl_time = time.time() - start_time
                speed = stats.get('properties_found', 0) / crawl_time if crawl_time > 0 else 0

                result = {
                    "rank": i,
                    "site": config.site_name,
                    "domain": config.site_domain,
                    "success": True,
                    "properties_found": stats.get('properties_found', 0),
                    "properties_new": stats.get('properties_new', 0),
                    "properties_updated": stats.get('properties_updated', 0),
                    "pages_crawled": stats.get('pages_crawled', 0),
                    "errors": stats.get('errors', 0),
                    "crawl_time": crawl_time,
                    "speed": speed,
                    "quality_score": config.quality_score
                }

                results.append(result)

                print(f"\n✅ Success!")
                print(f"   Properties: {result['properties_found']} ({result['properties_new']} new, {result['properties_updated']} updated)")
                print(f"   Pages: {result['pages_crawled']}")
                print(f"   Time: {crawl_time:.1f}s")
                print(f"   Speed: {speed:.1f} properties/sec")
                if result['errors'] > 0:
                    print(f"   ⚠️  Errors: {result['errors']}")

            except Exception as e:
                crawl_time = time.time() - start_time
                result = {
                    "rank": i,
                    "site": config.site_name,
                    "domain": config.site_domain,
                    "success": False,
                    "properties_found": 0,
                    "properties_new": 0,
                    "properties_updated": 0,
                    "pages_crawled": 0,
                    "errors": 1,
                    "crawl_time": crawl_time,
                    "speed": 0,
                    "quality_score": config.quality_score,
                    "error": str(e)
                }
                results.append(result)

                print(f"\n❌ Failed: {e}")

        overall_time = time.time() - overall_start

        # Print summary
        self.print_summary(results, overall_time)

        return results

    def print_summary(self, results: list, total_time: float):
        """Print test summary"""
        print(f"\n{'█'*80}")
        print(f"  CRAWL PERFORMANCE TEST RESULTS")
        print(f"{'█'*80}\n")

        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]

        print(f"✅ Successful: {len(successful)}/{len(results)} sites")
        if failed:
            print(f"❌ Failed: {len(failed)}/{len(results)} sites")

        # Detailed results table
        print(f"\n{'─'*80}")
        print(f"{'Site':<25} {'Props':<8} {'New':<6} {'Pages':<6} {'Time':<8} {'Speed':<12} {'Status':<6}")
        print(f"{'─'*80}")

        for r in results:
            status = "✅" if r['success'] else "❌"
            print(f"{r['site']:<25} {r['properties_found']:<8} {r['properties_new']:<6} "
                  f"{r['pages_crawled']:<6} {r['crawl_time']:<7.1f}s {r['speed']:<11.1f}/s {status:<6}")

        print(f"{'─'*80}\n")

        # Overall statistics
        if successful:
            total_properties = sum(r['properties_found'] for r in successful)
            total_new = sum(r['properties_new'] for r in successful)
            total_updated = sum(r['properties_updated'] for r in successful)
            total_pages = sum(r['pages_crawled'] for r in successful)
            total_errors = sum(r['errors'] for r in successful)
            avg_speed = sum(r['speed'] for r in successful) / len(successful)
            overall_speed = total_properties / total_time

            print(f"📊 Overall Statistics:")
            print(f"{'─'*80}")
            print(f"Total Properties Crawled:  {total_properties}")
            print(f"  - New:                   {total_new}")
            print(f"  - Updated:               {total_updated}")
            print(f"Total Pages:               {total_pages}")
            print(f"Total Errors:              {total_errors}")
            print(f"Total Time:                {total_time:.1f}s ({total_time/60:.1f} min)")
            print(f"Average Speed per Site:    {avg_speed:.1f} properties/sec")
            print(f"Overall Speed:             {overall_speed:.1f} properties/sec")
            print(f"Success Rate:              {len(successful)/len(results)*100:.1f}%")

            # Quality assessment
            print(f"\n🎯 crawl4ai Effectiveness:")
            print(f"{'─'*80}")

            if avg_speed >= 20:
                rating = "EXCELLENT 🌟🌟🌟"
            elif avg_speed >= 10:
                rating = "GOOD 👍"
            elif avg_speed >= 5:
                rating = "FAIR 👌"
            else:
                rating = "NEEDS IMPROVEMENT ⚠️"

            print(f"Speed Rating:              {rating}")
            print(f"Error Rate:                {total_errors/total_pages*100:.1f}% (lower is better)")

            print(f"\n💡 Recommendations:")
            if avg_speed < 10:
                print(f"   • Consider increasing max_workers for faster sites")
                print(f"   • Check if rate limits are too conservative")
            if total_errors > total_pages * 0.1:
                print(f"   • High error rate detected - check selectors and rate limits")
            if len(failed) > 0:
                print(f"   • {len(failed)} site(s) failed - check configurations")

        print(f"\n{'='*80}\n")

    async def run_full_test(self):
        """Run full performance test"""
        overall_start = time.time()

        print(f"\n{'█'*80}")
        print(f"  CRAWL4AI PERFORMANCE TEST - VIETNAM REAL ESTATE SITES")
        print(f"{'█'*80}\n")

        # Step 1: Add test sites
        self.add_test_sites()

        # Step 2: Run crawl test
        results = await self.run_crawl_test(properties_per_site=100)

        overall_time = time.time() - overall_start

        print(f"\n{'='*80}")
        print(f"✅ FULL TEST COMPLETED IN {overall_time:.1f}s ({overall_time/60:.1f} minutes)")
        print(f"{'='*80}\n")


async def main():
    """Main entry point"""
    tester = CrawlPerformanceTester()

    try:
        await tester.run_full_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

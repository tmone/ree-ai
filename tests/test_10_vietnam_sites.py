#!/usr/bin/env python3
"""
Test AI Crawler with Top 10 Vietnam Real Estate Sites
Automatically add sites and crawl data to evaluate crawl4ai effectiveness
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except ImportError:
    pass

from services.crawler.site_analyzer import SiteAnalyzer
from services.crawler.multi_site_orchestrator import MultiSiteOrchestrator, CrawlMode
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from tabulate import tabulate


# Top 10 Vietnam Real Estate Sites (by traffic)
TOP_10_SITES = [
    {
        "url": "https://batdongsan.com.vn/nha-dat-ban",
        "name": "Batdongsan.com.vn",
        "rank": 1,
        "monthly_visits": "4.2M"
    },
    {
        "url": "https://nhatot.com/mua-ban-bat-dong-san",
        "name": "Nhatot.com",
        "rank": 2,
        "monthly_visits": "~3M"
    },
    {
        "url": "https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/1/viet-nam.html",
        "name": "Alonhadat.com.vn",
        "rank": 3,
        "monthly_visits": "1.06M"
    },
    {
        "url": "https://mogi.vn/mua-nha-dat",
        "name": "Mogi.vn",
        "rank": 4,
        "monthly_visits": "593.8K"
    },
    {
        "url": "https://muaban.net/nha-dat-cho-thue-cho-thue-can-ho-chung-cu-l35",
        "name": "Muaban.net",
        "rank": 5,
        "monthly_visits": "462.4K"
    },
    {
        "url": "https://dotproperty.com.vn/en/property-for-sale",
        "name": "DotProperty.com.vn",
        "rank": 6,
        "monthly_visits": "~300K"
    },
    {
        "url": "https://www.propzy.vn/mua/nha-dat",
        "name": "Propzy.vn",
        "rank": 7,
        "monthly_visits": "~250K"
    },
    {
        "url": "https://homedy.com/mua-ban-nha-dat",
        "name": "Homedy.com",
        "rank": 8,
        "monthly_visits": "~200K"
    },
    {
        "url": "https://cafeland.vn/nha-dat/ban/",
        "name": "Cafeland.vn",
        "rank": 9,
        "monthly_visits": "~150K"
    },
    {
        "url": "https://chothuenha.net/cho-thue/nha-dat",
        "name": "Chothuenha.net",
        "rank": 10,
        "monthly_visits": "~100K"
    }
]


class VietnamSitesTester:
    """Test crawler with Vietnam's top 10 real estate sites"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'ree_ai'),
            'user': os.getenv('POSTGRES_USER', 'ree_ai_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'ree_ai_pass_2025')
        }
        self.analyzer = SiteAnalyzer()
        self.results = []

    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    async def add_site(self, site_info: dict) -> dict:
        """
        Add site using AI analyzer

        Returns:
            dict with analysis results and success status
        """
        print(f"\n{'='*80}")
        print(f"🔍 [{site_info['rank']}/10] Analyzing: {site_info['name']}")
        print(f"   URL: {site_info['url']}")
        print(f"   Traffic: {site_info['monthly_visits']}/month")
        print(f"{'='*80}")

        try:
            start_time = time.time()

            # Step 1: Analyze with AI
            analysis = await self.analyzer.analyze_site(site_info['url'], sample_pages=2)
            analysis_time = time.time() - start_time

            # Step 2: Display results
            print(f"\n✅ Analysis Complete in {analysis_time:.1f}s!")
            print(f"   Quality Score: {analysis.quality_score}/10")
            print(f"   Completeness: {analysis.data_completeness*100:.1f}%")
            print(f"   Confidence: {analysis.analysis_confidence*100:.1f}%")
            print(f"   Rate Limit: {analysis.rate_limit_seconds}s")
            print(f"   Workers: {analysis.max_workers}")
            print(f"   Fields: {', '.join(analysis.data_fields)}")

            if analysis.has_cloudflare:
                print(f"   ⚠️  Cloudflare detected")
            if analysis.requires_js:
                print(f"   ⚠️  Requires JavaScript")

            # Step 3: Save to database
            conn = self.get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO crawl_configs (
                    site_domain, site_name, base_url,
                    selectors, pagination,
                    rate_limit_seconds, max_workers,
                    has_cloudflare, requires_js,
                    quality_score, data_completeness, data_fields,
                    crawl_frequency, analysis_confidence,
                    notes, enabled
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true
                )
                ON CONFLICT (site_domain) DO UPDATE SET
                    selectors = EXCLUDED.selectors,
                    pagination = EXCLUDED.pagination,
                    quality_score = EXCLUDED.quality_score,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    analysis.site_domain,
                    analysis.site_name,
                    analysis.base_url,
                    json.dumps({
                        'card': analysis.property_card_selector,
                        'title': analysis.title_selector,
                        'price': analysis.price_selector,
                        'location': analysis.location_selector,
                        'area': analysis.area_selector,
                        'description': analysis.description_selector,
                        'link': analysis.link_selector,
                        'image': analysis.image_selector
                    }),
                    json.dumps({
                        'pattern': analysis.pagination_pattern,
                        'max_pages': analysis.max_pages_estimate,
                        'per_page': analysis.properties_per_page
                    }),
                    analysis.rate_limit_seconds,
                    analysis.max_workers,
                    analysis.has_cloudflare,
                    analysis.requires_js,
                    analysis.quality_score,
                    analysis.data_completeness,
                    json.dumps(analysis.data_fields),
                    analysis.recommended_frequency,
                    analysis.analysis_confidence,
                    f"Rank: #{site_info['rank']}, Traffic: {site_info['monthly_visits']}/month"
                )
            )

            conn.commit()
            cursor.close()
            conn.close()

            print(f"   ✅ Configuration saved to database")

            return {
                "success": True,
                "site": site_info['name'],
                "domain": analysis.site_domain,
                "quality_score": analysis.quality_score,
                "completeness": analysis.data_completeness,
                "confidence": analysis.analysis_confidence,
                "analysis_time": analysis_time,
                "error": None
            }

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                "success": False,
                "site": site_info['name'],
                "domain": None,
                "quality_score": 0,
                "completeness": 0,
                "confidence": 0,
                "analysis_time": 0,
                "error": str(e)
            }

    async def add_all_sites(self):
        """Add all 10 sites"""
        print(f"\n{'='*80}")
        print(f"🚀 ADDING TOP 10 VIETNAM REAL ESTATE SITES")
        print(f"{'='*80}\n")

        for site in TOP_10_SITES:
            result = await self.add_site(site)
            self.results.append(result)

            # Small delay to be polite
            await asyncio.sleep(2)

        # Summary
        self.print_addition_summary()

    def print_addition_summary(self):
        """Print summary of site additions"""
        print(f"\n{'='*80}")
        print(f"📊 SITE ADDITION SUMMARY")
        print(f"{'='*80}\n")

        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]

        print(f"✅ Successfully added: {len(successful)}/10 sites")
        if failed:
            print(f"❌ Failed: {len(failed)}/10 sites")

        # Table of results
        headers = ["#", "Site", "Domain", "Quality", "Complete", "Confidence", "Time", "Status"]
        rows = []

        for i, result in enumerate(self.results, 1):
            rows.append([
                i,
                result['site'][:20],
                result['domain'][:25] if result['domain'] else "N/A",
                f"{result['quality_score']:.1f}/10" if result['success'] else "N/A",
                f"{result['completeness']*100:.0f}%" if result['success'] else "N/A",
                f"{result['confidence']*100:.0f}%" if result['success'] else "N/A",
                f"{result['analysis_time']:.1f}s" if result['success'] else "N/A",
                "✅" if result['success'] else f"❌ {result['error'][:20]}"
            ])

        print(tabulate(rows, headers=headers, tablefmt="grid"))

        # Stats
        if successful:
            avg_quality = sum(r['quality_score'] for r in successful) / len(successful)
            avg_completeness = sum(r['completeness'] for r in successful) / len(successful)
            avg_time = sum(r['analysis_time'] for r in successful) / len(successful)

            print(f"\n📈 Average Metrics (successful sites):")
            print(f"   Quality Score: {avg_quality:.1f}/10")
            print(f"   Completeness: {avg_completeness*100:.1f}%")
            print(f"   Analysis Time: {avg_time:.1f}s per site")

    async def crawl_all_sites(self, sample_properties: int = 100):
        """
        Crawl sample data from all added sites

        Args:
            sample_properties: Number of properties to crawl per site (for testing)
        """
        print(f"\n{'='*80}")
        print(f"🔍 CRAWLING {sample_properties} PROPERTIES FROM EACH SITE")
        print(f"{'='*80}\n")

        orchestrator = MultiSiteOrchestrator(self.db_config)

        # Load all enabled configs
        configs = await orchestrator.load_configs(enabled_only=True)

        if not configs:
            print("❌ No sites configured!")
            return

        print(f"Found {len(configs)} enabled sites\n")

        # Crawl each site (sequential for clearer output)
        crawl_results = []

        for config in configs:
            print(f"\n🚀 Crawling: {config.site_name}")
            start_time = time.time()

            try:
                # Calculate pages needed for sample
                pages_needed = max(1, sample_properties // config.pagination['per_page'])

                # Modify config temporarily for testing
                original_max_pages = config.pagination['max_pages']
                config.pagination['max_pages'] = pages_needed

                stats = await orchestrator.crawl_site(config, CrawlMode.INCREMENTAL)

                # Restore
                config.pagination['max_pages'] = original_max_pages

                crawl_time = time.time() - start_time

                crawl_results.append({
                    "site": config.site_name,
                    "domain": config.site_domain,
                    "success": True,
                    "properties_found": stats.get('properties_found', 0),
                    "properties_new": stats.get('properties_new', 0),
                    "pages_crawled": stats.get('pages_crawled', 0),
                    "errors": stats.get('errors', 0),
                    "crawl_time": crawl_time,
                    "speed": stats.get('properties_found', 0) / crawl_time if crawl_time > 0 else 0
                })

                print(f"   ✅ Done: {stats.get('properties_found', 0)} properties in {crawl_time:.1f}s")

            except Exception as e:
                print(f"   ❌ Error: {e}")
                crawl_results.append({
                    "site": config.site_name,
                    "domain": config.site_domain,
                    "success": False,
                    "properties_found": 0,
                    "properties_new": 0,
                    "pages_crawled": 0,
                    "errors": 1,
                    "crawl_time": 0,
                    "speed": 0
                })

        # Print crawl summary
        self.print_crawl_summary(crawl_results)

    def print_crawl_summary(self, crawl_results: list):
        """Print crawl summary"""
        print(f"\n{'='*80}")
        print(f"📊 CRAWL RESULTS SUMMARY")
        print(f"{'='*80}\n")

        successful = [r for r in crawl_results if r['success']]
        failed = [r for r in crawl_results if not r['success']]

        print(f"✅ Successful crawls: {len(successful)}/{len(crawl_results)}")
        if failed:
            print(f"❌ Failed: {len(failed)}/{len(crawl_results)}")

        # Table
        headers = ["Site", "Domain", "Properties", "New", "Pages", "Time", "Speed", "Status"]
        rows = []

        for result in crawl_results:
            rows.append([
                result['site'][:20],
                result['domain'][:25],
                result['properties_found'],
                result['properties_new'],
                result['pages_crawled'],
                f"{result['crawl_time']:.1f}s",
                f"{result['speed']:.1f}/s" if result['speed'] > 0 else "N/A",
                "✅" if result['success'] else "❌"
            ])

        print(tabulate(rows, headers=headers, tablefmt="grid"))

        # Overall stats
        if successful:
            total_properties = sum(r['properties_found'] for r in successful)
            total_new = sum(r['properties_new'] for r in successful)
            total_time = sum(r['crawl_time'] for r in successful)
            avg_speed = sum(r['speed'] for r in successful) / len(successful)

            print(f"\n📈 Overall Statistics:")
            print(f"   Total Properties: {total_properties}")
            print(f"   Total New: {total_new}")
            print(f"   Total Time: {total_time:.1f}s")
            print(f"   Average Speed: {avg_speed:.1f} properties/second")
            print(f"   Overall Speed: {total_properties/total_time:.1f} properties/second")

    async def run_full_test(self):
        """Run full test: add sites + crawl data"""
        start_time = time.time()

        print(f"\n{'█'*80}")
        print(f"  AI CRAWLER TEST WITH TOP 10 VIETNAM REAL ESTATE SITES")
        print(f"{'█'*80}\n")

        # Step 1: Add all sites
        await self.add_all_sites()

        # Step 2: Crawl sample data
        await self.crawl_all_sites(sample_properties=50)

        # Final summary
        total_time = time.time() - start_time

        print(f"\n{'='*80}")
        print(f"✅ FULL TEST COMPLETED IN {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"{'='*80}\n")


async def main():
    """Main entry point"""
    tester = VietnamSitesTester()

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

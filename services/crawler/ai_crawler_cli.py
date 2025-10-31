#!/usr/bin/env python3
"""
AI Crawler CLI
Easy command-line interface for managing intelligent crawler

Commands:
    add <url>         - Analyze and add new site
    list              - List all configured sites
    enable <domain>   - Enable a site
    disable <domain>  - Disable a site
    crawl [domain]    - Start crawling (all sites or specific domain)
    status            - Show crawl status and statistics
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
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
from datetime import datetime


class AICrawlerCLI:
    """Command-line interface for AI Crawler"""

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

    async def add_site(self, url: str):
        """Analyze and add new site"""
        print(f"\n🔍 Analyzing site: {url}")
        print("="*70)

        # Step 1: Analyze site with AI
        analyzer = SiteAnalyzer()
        analysis = await analyzer.analyze_site(url)

        # Step 2: Display analysis results
        print(f"\n✅ Analysis Complete!")
        print(f"Site Name: {analysis.site_name}")
        print(f"Domain: {analysis.site_domain}")
        print(f"Quality Score: {analysis.quality_score}/10")
        print(f"Data Completeness: {analysis.data_completeness*100:.1f}%")
        print(f"Recommended Frequency: {analysis.recommended_frequency}")
        print(f"Rate Limit: {analysis.rate_limit_seconds}s")
        print(f"Max Workers: {analysis.max_workers}")
        print(f"Available Fields: {', '.join(analysis.data_fields)}")

        if analysis.has_cloudflare:
            print("⚠️  Cloudflare detected")
        if analysis.requires_js:
            print("⚠️  Requires JavaScript")

        print(f"\nSelectors:")
        print(f"  Card: {analysis.property_card_selector}")
        print(f"  Title: {analysis.title_selector}")
        print(f"  Price: {analysis.price_selector}")
        print(f"  Location: {analysis.location_selector}")

        # Step 3: Confirm
        confirm = input(f"\n💾 Save this configuration? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Cancelled")
            return

        # Step 4: Save to database
        conn = self.get_db_connection()
        cursor = conn.cursor()

        try:
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
                    site_name = EXCLUDED.site_name,
                    selectors = EXCLUDED.selectors,
                    pagination = EXCLUDED.pagination,
                    rate_limit_seconds = EXCLUDED.rate_limit_seconds,
                    max_workers = EXCLUDED.max_workers,
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
                    analysis.notes
                )
            )

            conn.commit()
            print(f"\n✅ Site configuration saved successfully!")
            print(f"You can now crawl with: python ai_crawler_cli.py crawl {analysis.site_domain}")

        except Exception as e:
            conn.rollback()
            print(f"\n❌ Error saving configuration: {e}")
        finally:
            cursor.close()
            conn.close()

    def list_sites(self):
        """List all configured sites"""
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute(
            """
            SELECT site_domain, site_name, quality_score, status, enabled,
                   last_incremental_crawl, last_full_crawl
            FROM crawl_configs
            ORDER BY quality_score DESC
            """
        )
        sites = cursor.fetchall()

        cursor.close()
        conn.close()

        if not sites:
            print("\n📭 No sites configured yet")
            print("Add a site with: python ai_crawler_cli.py add <url>")
            return

        # Format as table
        headers = ["Domain", "Name", "Quality", "Status", "Enabled", "Last Crawl"]
        rows = []

        for site in sites:
            last_crawl = site['last_incremental_crawl'] or site['last_full_crawl']
            last_crawl_str = last_crawl.strftime("%Y-%m-%d %H:%M") if last_crawl else "Never"

            rows.append([
                site['site_domain'],
                site['site_name'],
                f"{site['quality_score']}/10",
                site['status'],
                "✅" if site['enabled'] else "❌",
                last_crawl_str
            ])

        print(f"\n📋 Configured Sites ({len(sites)} total):")
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def enable_site(self, domain: str):
        """Enable a site"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE crawl_configs SET enabled = true WHERE site_domain = %s",
            (domain,)
        )

        if cursor.rowcount > 0:
            conn.commit()
            print(f"✅ Enabled: {domain}")
        else:
            print(f"❌ Site not found: {domain}")

        cursor.close()
        conn.close()

    def disable_site(self, domain: str):
        """Disable a site"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE crawl_configs SET enabled = false WHERE site_domain = %s",
            (domain,)
        )

        if cursor.rowcount > 0:
            conn.commit()
            print(f"❌ Disabled: {domain}")
        else:
            print(f"❌ Site not found: {domain}")

        cursor.close()
        conn.close()

    async def crawl(self, domain: str = None, mode: str = "incremental"):
        """Start crawling"""
        orchestrator = MultiSiteOrchestrator(self.db_config)

        crawl_mode = CrawlMode.FULL if mode == "full" else CrawlMode.INCREMENTAL

        if domain:
            # Crawl specific site
            print(f"\n🚀 Starting {mode} crawl for: {domain}")

            # Load config for this site
            configs = await orchestrator.load_configs(enabled_only=False)
            config = next((c for c in configs if c.site_domain == domain), None)

            if not config:
                print(f"❌ Site not found: {domain}")
                return

            if not config.enabled:
                print(f"⚠️  Site is disabled. Enable it first with: python ai_crawler_cli.py enable {domain}")
                return

            await orchestrator.crawl_site(config, crawl_mode)
        else:
            # Crawl all enabled sites
            print(f"\n🚀 Starting {mode} crawl for all enabled sites...")
            await orchestrator.start_all(crawl_mode)

    def status(self):
        """Show crawl status and statistics"""
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get overall stats
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_sites,
                COUNT(*) FILTER (WHERE enabled = true) as enabled_sites,
                COUNT(*) FILTER (WHERE status = 'active') as active_sites,
                COUNT(*) FILTER (WHERE status = 'rate_limited') as rate_limited_sites,
                COUNT(*) FILTER (WHERE status = 'failed') as failed_sites,
                AVG(quality_score) as avg_quality
            FROM crawl_configs
            """
        )
        stats = cursor.fetchone()

        # Get recent jobs
        cursor.execute(
            """
            SELECT site_domain, job_type, status,
                   properties_new, properties_updated,
                   duration_seconds, completed_at
            FROM crawl_jobs
            ORDER BY created_at DESC
            LIMIT 10
            """
        )
        recent_jobs = cursor.fetchall()

        cursor.close()
        conn.close()

        # Display stats
        print(f"\n📊 Crawler Status")
        print("="*70)
        print(f"Total Sites: {stats['total_sites']}")
        print(f"Enabled: {stats['enabled_sites']}")
        print(f"Active: {stats['active_sites']}")
        if stats['rate_limited_sites'] > 0:
            print(f"Rate Limited: {stats['rate_limited_sites']} ⚠️")
        if stats['failed_sites'] > 0:
            print(f"Failed: {stats['failed_sites']} ❌")
        print(f"Avg Quality: {stats['avg_quality']:.1f}/10")

        # Display recent jobs
        if recent_jobs:
            print(f"\n📋 Recent Crawl Jobs:")
            headers = ["Site", "Type", "Status", "New", "Updated", "Duration", "Completed"]
            rows = []

            for job in recent_jobs:
                duration_str = f"{job['duration_seconds']:.1f}s" if job['duration_seconds'] else "N/A"
                completed_str = job['completed_at'].strftime("%m-%d %H:%M") if job['completed_at'] else "Running"

                rows.append([
                    job['site_domain'],
                    job['job_type'],
                    job['status'],
                    job['properties_new'] or 0,
                    job['properties_updated'] or 0,
                    duration_str,
                    completed_str
                ])

            print(tabulate(rows, headers=headers, tablefmt="grid"))


def print_help():
    """Print help message"""
    print("""
🤖 AI Crawler CLI - Intelligent Real Estate Crawler

USAGE:
    python ai_crawler_cli.py <command> [args]

COMMANDS:
    add <url>              Analyze and add new site
                          Example: python ai_crawler_cli.py add https://mogi.vn

    list                   List all configured sites

    enable <domain>        Enable a site
                          Example: python ai_crawler_cli.py enable mogi.vn

    disable <domain>       Disable a site

    crawl [domain] [mode]  Start crawling
                          - No args: Crawl all enabled sites (incremental)
                          - domain: Crawl specific site
                          - mode: 'full' or 'incremental' (default: incremental)
                          Examples:
                            python ai_crawler_cli.py crawl
                            python ai_crawler_cli.py crawl batdongsan.com.vn
                            python ai_crawler_cli.py crawl batdongsan.com.vn full

    status                 Show crawl status and statistics

    help                   Show this help message

EXAMPLES:
    # Add new site (AI will analyze it)
    python ai_crawler_cli.py add https://nhatot.com/mua-ban-bat-dong-san

    # List all sites
    python ai_crawler_cli.py list

    # Crawl all enabled sites (incremental)
    python ai_crawler_cli.py crawl

    # Full crawl of specific site
    python ai_crawler_cli.py crawl batdongsan.com.vn full

    # Check status
    python ai_crawler_cli.py status
""")


async def main():
    """Main CLI entry point"""
    cli = AICrawlerCLI()

    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "add":
            if len(sys.argv) < 3:
                print("❌ Error: URL required")
                print("Usage: python ai_crawler_cli.py add <url>")
                sys.exit(1)
            await cli.add_site(sys.argv[2])

        elif command == "list":
            cli.list_sites()

        elif command == "enable":
            if len(sys.argv) < 3:
                print("❌ Error: Domain required")
                sys.exit(1)
            cli.enable_site(sys.argv[2])

        elif command == "disable":
            if len(sys.argv) < 3:
                print("❌ Error: Domain required")
                sys.exit(1)
            cli.disable_site(sys.argv[2])

        elif command == "crawl":
            domain = sys.argv[2] if len(sys.argv) > 2 else None
            mode = sys.argv[3] if len(sys.argv) > 3 else "incremental"
            await cli.crawl(domain, mode)

        elif command == "status":
            cli.status()

        elif command == "help":
            print_help()

        else:
            print(f"❌ Unknown command: {command}")
            print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

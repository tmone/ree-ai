"""
Test multi-site crawling with AI-generated configs
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.crawler.bulk_crawler import bulk_crawl_properties


async def test_sites():
    """Test crawl from multiple sites"""

    print("🚀 Testing multiple Vietnam real estate sites...")
    print("=" * 70)

    # Test with small sample from each site
    sites_to_test = ['alonhadat', 'muaban', 'nhatot']

    for site in sites_to_test:
        print(f"\n🔍 Testing {site}...")
        try:
            properties = await bulk_crawl_properties(
                total=100,  # Small test
                sites=[site],
                resume=False  # Fresh crawl
            )

            print(f"✅ {site}: Found {len(properties)} properties")

            if len(properties) > 0:
                sample = properties[0]
                print(f"   Sample: {sample.get('title', 'N/A')[:60]}...")
                print(f"   Price: {sample.get('price', 'N/A')}")
                print(f"   Location: {sample.get('location', 'N/A')}")
        except Exception as e:
            print(f"❌ {site}: Error - {str(e)}")

    print("\n" + "=" * 70)
    print("✅ Multi-site test complete!")


if __name__ == "__main__":
    asyncio.run(test_sites())

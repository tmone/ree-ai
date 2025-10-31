"""
Crawl properties and save to JSON file
Then we'll import to PostgreSQL separately
"""
import asyncio
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.crawler.bulk_crawler import bulk_crawl_properties


async def crawl_and_save(total_properties: int = 10000):
    """Crawl properties and save to JSON file"""

    print(f"🚀 Starting crawl for {total_properties} properties...")

    # Crawl properties
    properties = await bulk_crawl_properties(total=total_properties, sites=['batdongsan'])

    print(f"\n✅ Crawled {len(properties)} properties")

    # Save to JSON file
    output_file = f"/Users/tmone/ree-ai/tests/crawled_properties_{len(properties)}.json"

    print(f"\n💾 Saving to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(properties, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(properties)} properties to JSON")
    print(f"📄 File: {output_file}")

    return output_file


if __name__ == "__main__":
    # Get total from command line
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 10000

    output_file = asyncio.run(crawl_and_save(total))

    print(f"\n{'='*70}")
    print(f"✅ CRAWL COMPLETE")
    print(f"📄 Output: {output_file}")
    print(f"📊 Next: Import to PostgreSQL")
    print(f"{'='*70}")

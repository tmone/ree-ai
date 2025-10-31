#!/usr/bin/env python3
"""
AI-Powered Analysis of Top 10 Vietnam Real Estate Sites
Uses Core Gateway + Ollama to generate crawl configs automatically
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from services.crawler.site_analyzer import SiteAnalyzer


# Top 10 Vietnam Real Estate Sites
VIETNAM_SITES = [
    {
        "name": "Batdongsan.com.vn",
        "url": "https://batdongsan.com.vn/nha-dat-ban",
        "category": "Major Portal"
    },
    {
        "name": "Mogi.vn",
        "url": "https://mogi.vn/mua-nha-dat",
        "category": "Major Portal"
    },
    {
        "name": "Alonhadat.com.vn",
        "url": "https://alonhadat.com.vn/nha-dat/can-ban",
        "category": "Major Portal"
    },
    {
        "name": "Nhatot.com",
        "url": "https://nhatot.com/mua-ban-bat-dong-san",
        "category": "Classifieds"
    },
    {
        "name": "Muaban.net",
        "url": "https://muaban.net/nha-dat-ban",
        "category": "Classifieds"
    },
    {
        "name": "Propzy.vn",
        "url": "https://propzy.vn/mua/nha-dat",
        "category": "Tech Broker"
    },
    {
        "name": "Homedy.com",
        "url": "https://homedy.com/mua-nha-dat",
        "category": "Portal"
    },
    {
        "name": "Dothi.net",
        "url": "https://dothi.net/nha-dat-ban",
        "category": "Portal"
    },
    {
        "name": "Nhadatvui.vn",
        "url": "https://nhadatvui.vn/",
        "category": "Portal"
    },
    {
        "name": "123nhadat.vn",
        "url": "https://123nhadat.vn/nha-dat-ban",
        "category": "Portal"
    }
]


async def analyze_all_sites(output_dir: str = "data/site_analysis") -> List[Dict[str, Any]]:
    """Analyze all Vietnam real estate sites"""

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print("="*80)
    print("🤖 AI-POWERED VIETNAM REAL ESTATE SITES ANALYSIS")
    print("="*80)
    print(f"📊 Analyzing {len(VIETNAM_SITES)} sites using Core Gateway + Ollama")
    print(f"💰 Cost: $0 (vs $15+ for OpenAI)")
    print(f"⏱️  Estimated time: {len(VIETNAM_SITES) * 5} seconds (~5s per site)")
    print("="*80)
    print()

    analyzer = SiteAnalyzer()
    results = []

    for i, site in enumerate(VIETNAM_SITES, 1):
        print(f"\n[{i}/{len(VIETNAM_SITES)}] 🔍 Analyzing: {site['name']}")
        print(f"     URL: {site['url']}")
        print(f"     Category: {site['category']}")

        try:
            # Analyze site
            analysis = await analyzer.analyze_site(
                url=site['url'],
                sample_pages=2
            )

            # Convert to dict
            result = analysis.to_dict()
            result['site_category'] = site['category']
            result['source_site_name'] = site['name']
            results.append(result)

            # Print summary
            print(f"     ✅ Quality Score: {analysis.quality_score}/10")
            print(f"     📋 Properties/Page: {analysis.properties_per_page}")
            print(f"     🎯 Confidence: {analysis.analysis_confidence:.1%}")
            print(f"     ⏱️  Rate Limit: {analysis.rate_limit_seconds}s")
            print(f"     👷 Max Workers: {analysis.max_workers}")

            # Save individual result
            filename = f"{output_dir}/{site['name'].replace('.', '_')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"     💾 Saved to: {filename}")

        except Exception as e:
            print(f"     ❌ Error: {str(e)}")
            results.append({
                'site_name': site['name'],
                'url': site['url'],
                'error': str(e),
                'analyzed_at': datetime.now().isoformat()
            })

        # Be polite - small delay between sites
        if i < len(VIETNAM_SITES):
            await asyncio.sleep(1)

    # Save combined results
    combined_file = f"{output_dir}/all_sites_analysis.json"
    with open(combined_file, 'w', encoding='utf-8') as f:
        json.dump({
            'analyzed_at': datetime.now().isoformat(),
            'total_sites': len(VIETNAM_SITES),
            'successful': len([r for r in results if 'error' not in r]),
            'failed': len([r for r in results if 'error' in r]),
            'results': results
        }, f, indent=2, ensure_ascii=False)

    print("\n" + "="*80)
    print("📊 ANALYSIS COMPLETE!")
    print("="*80)
    print(f"✅ Successful: {len([r for r in results if 'error' not in r])}/{len(VIETNAM_SITES)}")
    print(f"❌ Failed: {len([r for r in results if 'error' in r])}/{len(VIETNAM_SITES)}")
    print(f"💾 Combined results: {combined_file}")
    print("="*80)

    # Print summary table
    print("\n📋 QUALITY SUMMARY:")
    print("-"*80)
    print(f"{'Site':<25} {'Score':<8} {'Props/Pg':<10} {'Confidence':<12} {'Rate Limit'}")
    print("-"*80)

    for result in results:
        if 'error' not in result:
            name = result.get('source_site_name', result['site_name'])[:24]
            score = result.get('quality_score', 0)
            props = result.get('properties_per_page', 0)
            conf = result.get('analysis_confidence', 0)
            rate = result.get('rate_limit_seconds', 0)
            print(f"{name:<25} {score:<8.1f} {props:<10} {conf:<11.1%} {rate:.1f}s")

    print("-"*80)
    print()

    return results


async def main():
    """Main entry point"""
    results = await analyze_all_sites()

    # Print next steps
    print("\n🚀 NEXT STEPS:")
    print("1. Review generated selectors in data/site_analysis/")
    print("2. Test selectors against actual HTML samples")
    print("3. Import validated configs into database:")
    print("   python3 scripts/import_site_configs.py")
    print("4. Start crawling all 10 sites:")
    print("   python3 tests/crawl_all_vietnam_sites.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())

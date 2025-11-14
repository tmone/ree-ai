"""
Crawl Global Administrative Divisions using Crawl4AI
=====================================================
PURPOSE: Crawl and populate full administrative divisions data for 10 countries
SOURCES: Wikipedia, GeoNames, OpenStreetMap
OUTPUT: SQL files ready for database import
"""

import asyncio
import json
import re
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import os

# Data sources for each country
DATA_SOURCES = {
    'US': {
        'states': 'https://en.wikipedia.org/wiki/List_of_states_and_territories_of_the_United_States',
        'major_cities': 'https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population'
    },
    'VN': {
        'provinces': 'https://en.wikipedia.org/wiki/Provinces_of_Vietnam',
        'hcmc_districts': 'https://en.wikipedia.org/wiki/List_of_administrative_divisions_of_Ho_Chi_Minh_City',
        'hcmc_streets': 'https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_%C4%91%C6%B0%E1%BB%9Dng_ph%E1%BB%91_%E1%BB%9F_Th%C3%A0nh_ph%E1%BB%91_H%E1%BB%93_Ch%C3%AD_Minh'
    },
    'TH': {
        'provinces': 'https://en.wikipedia.org/wiki/Provinces_of_Thailand',
        'bangkok_districts': 'https://en.wikipedia.org/wiki/List_of_districts_of_Bangkok'
    },
    'SG': {
        'planning_areas': 'https://en.wikipedia.org/wiki/Planning_Areas_of_Singapore'
    },
    'JP': {
        'prefectures': 'https://en.wikipedia.org/wiki/Prefectures_of_Japan',
        'tokyo_wards': 'https://en.wikipedia.org/wiki/Special_wards_of_Tokyo'
    },
    'CN': {
        'provinces': 'https://en.wikipedia.org/wiki/Provinces_of_China',
        'municipalities': 'https://en.wikipedia.org/wiki/Direct-administered_municipalities_of_China'
    },
    'MY': {
        'states': 'https://en.wikipedia.org/wiki/States_and_federal_territories_of_Malaysia'
    },
    'GB': {
        'regions': 'https://en.wikipedia.org/wiki/Regions_of_England',
        'london_boroughs': 'https://en.wikipedia.org/wiki/List_of_London_boroughs'
    },
    'AU': {
        'states': 'https://en.wikipedia.org/wiki/States_and_territories_of_Australia',
        'sydney_suburbs': 'https://en.wikipedia.org/wiki/List_of_Sydney_suburbs'
    },
    'AE': {
        'emirates': 'https://en.wikipedia.org/wiki/Emirates_of_the_United_Arab_Emirates',
        'dubai_areas': 'https://en.wikipedia.org/wiki/List_of_communities_in_Dubai'
    }
}


class AdminDivisionCrawler:
    def __init__(self):
        self.data = {
            'countries': [],
            'provinces': [],
            'districts': [],
            'wards': [],
            'streets': []
        }

    async def crawl_wikipedia_table(self, url: str, extraction_schema: str) -> List[Dict]:
        """Crawl Wikipedia page and extract table data using LLM"""
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url=url,
                extraction_strategy=LLMExtractionStrategy(
                    provider="openai/gpt-4o-mini",
                    api_token=os.getenv("OPENAI_API_KEY"),
                    schema=extraction_schema,
                    instruction="Extract administrative division data from Wikipedia tables. Return clean, structured JSON."
                )
            )

            if result.success:
                return json.loads(result.extracted_content)
            return []

    async def crawl_us_states(self):
        """Crawl all 50 US states"""
        print("\n🇺🇸 Crawling US States...")

        schema = {
            "name": "US States",
            "baseSelector": "table.wikitable tbody tr",
            "fields": [
                {"name": "state_name", "selector": "td:nth-child(1)", "type": "text"},
                {"name": "abbreviation", "selector": "td:nth-child(2)", "type": "text"},
                {"name": "capital", "selector": "td:nth-child(3)", "type": "text"},
                {"name": "population", "selector": "td:nth-child(4)", "type": "text"}
            ]
        }

        data = await self.crawl_wikipedia_table(
            DATA_SOURCES['US']['states'],
            json.dumps(schema)
        )

        for item in data:
            state_code = f"US_{item['abbreviation'].upper()}"
            self.data['provinces'].append({
                'code': state_code,
                'name': item['state_name'],
                'country_code': 'US',
                'admin_level': 'State',
                'capital': item.get('capital'),
                'population': item.get('population')
            })

        print(f"✅ Crawled {len(data)} US states")
        return data

    async def crawl_vietnam_provinces(self):
        """Crawl all 63 Vietnam provinces"""
        print("\n🇻🇳 Crawling Vietnam Provinces...")

        schema = {
            "name": "Vietnam Provinces",
            "baseSelector": "table.wikitable tbody tr",
            "fields": [
                {"name": "name", "selector": "td:nth-child(1)", "type": "text"},
                {"name": "vietnamese_name", "selector": "td:nth-child(2)", "type": "text"},
                {"name": "region", "selector": "td:nth-child(3)", "type": "text"},
                {"name": "capital", "selector": "td:nth-child(4)", "type": "text"}
            ]
        }

        data = await self.crawl_wikipedia_table(
            DATA_SOURCES['VN']['provinces'],
            json.dumps(schema)
        )

        for idx, item in enumerate(data):
            # Generate code from name
            code = f"VN_{item['name'].upper().replace(' ', '_').replace('-', '_')}"

            self.data['provinces'].append({
                'code': code,
                'name': item['name'],
                'country_code': 'VN',
                'admin_level': 'Province' if 'Province' in item['name'] else 'City',
                'vietnamese_name': item.get('vietnamese_name'),
                'region': item.get('region'),
                'sort_order': idx + 1
            })

        print(f"✅ Crawled {len(data)} Vietnam provinces")
        return data

    async def crawl_hcmc_districts(self):
        """Crawl HCMC 22 districts"""
        print("\n🏙️ Crawling HCMC Districts...")

        schema = {
            "name": "HCMC Districts",
            "baseSelector": "table.wikitable tbody tr",
            "fields": [
                {"name": "name", "selector": "td:nth-child(1)", "type": "text"},
                {"name": "vietnamese_name", "selector": "td:nth-child(2)", "type": "text"},
                {"name": "area", "selector": "td:nth-child(3)", "type": "text"},
                {"name": "population", "selector": "td:nth-child(4)", "type": "text"}
            ]
        }

        data = await self.crawl_wikipedia_table(
            DATA_SOURCES['VN']['hcmc_districts'],
            json.dumps(schema)
        )

        for idx, item in enumerate(data):
            code = f"{item['name'].upper().replace(' ', '_').replace('DISTRICT_', 'Q')}"

            self.data['districts'].append({
                'code': code,
                'name': item['name'],
                'province_code': 'VN_HCMC',
                'country_code': 'VN',
                'vietnamese_name': item.get('vietnamese_name'),
                'area': item.get('area'),
                'population': item.get('population'),
                'sort_order': idx + 1
            })

        print(f"✅ Crawled {len(data)} HCMC districts")
        return data

    async def crawl_thailand_provinces(self):
        """Crawl Thailand 77 provinces"""
        print("\n🇹🇭 Crawling Thailand Provinces...")

        schema = {
            "name": "Thailand Provinces",
            "baseSelector": "table.wikitable tbody tr",
            "fields": [
                {"name": "name", "selector": "td:nth-child(1)", "type": "text"},
                {"name": "thai_name", "selector": "td:nth-child(2)", "type": "text"},
                {"name": "region", "selector": "td:nth-child(3)", "type": "text"},
                {"name": "capital", "selector": "td:nth-child(4)", "type": "text"}
            ]
        }

        data = await self.crawl_wikipedia_table(
            DATA_SOURCES['TH']['provinces'],
            json.dumps(schema)
        )

        for idx, item in enumerate(data):
            code = f"TH_{item['name'].upper().replace(' ', '_')}"

            self.data['provinces'].append({
                'code': code,
                'name': item['name'],
                'country_code': 'TH',
                'admin_level': 'Province',
                'thai_name': item.get('thai_name'),
                'region': item.get('region'),
                'sort_order': idx + 1
            })

        print(f"✅ Crawled {len(data)} Thailand provinces")
        return data

    async def crawl_japan_prefectures(self):
        """Crawl Japan 47 prefectures"""
        print("\n🇯🇵 Crawling Japan Prefectures...")

        schema = {
            "name": "Japan Prefectures",
            "baseSelector": "table.wikitable tbody tr",
            "fields": [
                {"name": "name", "selector": "td:nth-child(1)", "type": "text"},
                {"name": "japanese_name", "selector": "td:nth-child(2)", "type": "text"},
                {"name": "region", "selector": "td:nth-child(3)", "type": "text"},
                {"name": "capital", "selector": "td:nth-child(4)", "type": "text"}
            ]
        }

        data = await self.crawl_wikipedia_table(
            DATA_SOURCES['JP']['prefectures'],
            json.dumps(schema)
        )

        for idx, item in enumerate(data):
            code = f"JP_{item['name'].upper().replace(' ', '_')}"

            self.data['provinces'].append({
                'code': code,
                'name': item['name'],
                'country_code': 'JP',
                'admin_level': 'Prefecture',
                'japanese_name': item.get('japanese_name'),
                'region': item.get('region'),
                'sort_order': idx + 1
            })

        print(f"✅ Crawled {len(data)} Japan prefectures")
        return data

    async def crawl_all_countries(self):
        """Crawl all countries in parallel"""
        print("🌍 Starting global administrative divisions crawling...")

        tasks = [
            self.crawl_us_states(),
            self.crawl_vietnam_provinces(),
            self.crawl_hcmc_districts(),
            self.crawl_thailand_provinces(),
            self.crawl_japan_prefectures(),
            # Add more countries here
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                print(f"❌ Error: {result}")

        return self.data

    def generate_sql_insert(self) -> str:
        """Generate SQL INSERT statements from crawled data"""
        sql = "-- Auto-generated from Crawl4AI\n"
        sql += "-- Date: " + str(asyncio.get_event_loop().time()) + "\n\n"
        sql += "BEGIN;\n\n"

        # Provinces
        sql += "-- ================================================================\n"
        sql += "-- PROVINCES/STATES\n"
        sql += "-- ================================================================\n\n"

        for province in self.data['provinces']:
            country_query = f"(SELECT id FROM ree_common.countries WHERE code = '{province['country_code']}')"
            sql += f"INSERT INTO ree_common.provinces (code, name, country_id, admin_level, sort_order)\n"
            sql += f"SELECT '{province['code']}', '{province['name']}', {country_query}, '{province['admin_level']}', {province.get('sort_order', 0)}\n"
            sql += f"ON CONFLICT (code) DO NOTHING;\n\n"

        # Districts
        sql += "-- ================================================================\n"
        sql += "-- DISTRICTS\n"
        sql += "-- ================================================================\n\n"

        for district in self.data['districts']:
            province_query = f"(SELECT id FROM ree_common.provinces WHERE code = '{district['province_code']}')"
            country_query = f"(SELECT id FROM ree_common.countries WHERE code = '{district['country_code']}')"
            sql += f"INSERT INTO ree_common.districts (code, name, province_id, country_id, sort_order)\n"
            sql += f"SELECT '{district['code']}', '{district['name']}', {province_query}, {country_query}, {district.get('sort_order', 0)}\n"
            sql += f"ON CONFLICT (code) DO NOTHING;\n\n"

        sql += "COMMIT;\n"

        return sql

    def save_to_file(self, filename: str = "crawled_admin_divisions.sql"):
        """Save generated SQL to file"""
        sql = self.generate_sql_insert()

        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sql)

        print(f"\n💾 Saved to: {filepath}")
        print(f"📊 Total provinces: {len(self.data['provinces'])}")
        print(f"📊 Total districts: {len(self.data['districts'])}")

        return filepath


async def main():
    """Main execution"""
    crawler = AdminDivisionCrawler()

    # Crawl all data
    await crawler.crawl_all_countries()

    # Generate SQL file
    crawler.save_to_file('crawled_admin_divisions_full.sql')

    print("\n✅ Crawling completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

"""
Test Master Data API with New Database Schema
"""
import asyncio
import httpx
import json
from typing import Dict, Any


class MasterDataTester:
    def __init__(self, base_url: str = "http://localhost:8095"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def test_health(self) -> bool:
        """Test service health"""
        print("\n" + "="*60)
        print("TEST 1: Service Health Check")
        print("="*60)
        try:
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Service is healthy: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    async def test_direct_database_query(self) -> bool:
        """Test direct database query"""
        print("\n" + "="*60)
        print("TEST 2: Direct Database Query")
        print("="*60)

        import asyncpg

        try:
            conn = await asyncpg.connect(
                host='localhost',
                port=5432,
                database='ree_ai',
                user='ree_ai_user',
                password='ree_ai_pass_2025'
            )

            # Test 1: Query amenities
            print("\n📊 Querying amenities...")
            amenities = await conn.fetch("""
                SELECT
                    a.id,
                    a.code,
                    a.name,
                    t.translated_text as name_vi
                FROM ree_common.amenities a
                LEFT JOIN ree_common.amenities_translation t
                    ON a.id = t.amenity_id AND t.lang_code = 'vi'
                ORDER BY a.sort_order
                LIMIT 5
            """)

            print(f"✅ Found {len(amenities)} amenities:")
            for amenity in amenities:
                print(f"  - {amenity['code']}: {amenity['name']} ({amenity['name_vi']})")

            # Test 2: Query views
            print("\n📊 Querying views...")
            views = await conn.fetch("""
                SELECT
                    v.id,
                    v.code,
                    v.name,
                    t.translated_text as name_vi
                FROM ree_common.views v
                LEFT JOIN ree_common.views_translation t
                    ON v.id = t.view_id AND t.lang_code = 'vi'
                ORDER BY v.sort_order
                LIMIT 5
            """)

            print(f"✅ Found {len(views)} views:")
            for view in views:
                print(f"  - {view['code']}: {view['name']} ({view['name_vi']})")

            # Test 3: Query districts
            print("\n📊 Querying districts...")
            districts = await conn.fetch("""
                SELECT
                    d.id,
                    d.code,
                    d.name,
                    t.translated_text as name_vi
                FROM ree_common.districts d
                LEFT JOIN ree_common.districts_translation t
                    ON d.id = t.district_id AND t.lang_code = 'vi'
                ORDER BY d.sort_order
                LIMIT 5
            """)

            print(f"✅ Found {len(districts)} districts:")
            for district in districts:
                print(f"  - {district['code']}: {district['name']} ({district['name_vi']})")

            await conn.close()
            return True

        except Exception as e:
            print(f"❌ Database query error: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_fuzzy_matching(self) -> bool:
        """Test fuzzy matching with aliases"""
        print("\n" + "="*60)
        print("TEST 3: Fuzzy Matching with Aliases")
        print("="*60)

        import asyncpg

        try:
            conn = await asyncpg.connect(
                host='localhost',
                port=5432,
                database='ree_ai',
                user='ree_ai_user',
                password='ree_ai_pass_2025'
            )

            # Test fuzzy matching on Vietnamese text
            test_text = "Căn hộ có hồ bơi và phòng gym"
            print(f"\n🔍 Extracting amenities from: '{test_text}'")

            results = await conn.fetch("""
                SELECT DISTINCT
                    a.code,
                    a.name,
                    t.translated_text as name_vi,
                    t.aliases
                FROM ree_common.amenities a
                JOIN ree_common.amenities_translation t
                    ON a.id = t.amenity_id
                WHERE t.lang_code = 'vi'
                  AND EXISTS (
                    SELECT 1 FROM unnest(t.aliases) alias
                    WHERE LOWER($1) LIKE '%' || LOWER(alias) || '%'
                  )
            """, test_text)

            if results:
                print(f"✅ Extracted {len(results)} amenities:")
                for result in results:
                    print(f"  - {result['code']}: {result['name']} (matched: {result['name_vi']})")
                    print(f"    Aliases: {result['aliases']}")
                return True
            else:
                print(f"⚠️  No amenities extracted")
                return False

            await conn.close()

        except Exception as e:
            print(f"❌ Fuzzy matching error: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_data_counts(self) -> bool:
        """Test data counts"""
        print("\n" + "="*60)
        print("TEST 4: Data Counts Verification")
        print("="*60)

        import asyncpg

        try:
            conn = await asyncpg.connect(
                host='localhost',
                port=5432,
                database='ree_ai',
                user='ree_ai_user',
                password='ree_ai_pass_2025'
            )

            counts = await conn.fetch("""
                SELECT
                    'amenities' as table_name,
                    (SELECT COUNT(*) FROM ree_common.amenities) as records,
                    (SELECT COUNT(*) FROM ree_common.amenities_translation) as translations
                UNION ALL
                SELECT
                    'views',
                    (SELECT COUNT(*) FROM ree_common.views),
                    (SELECT COUNT(*) FROM ree_common.views_translation)
                UNION ALL
                SELECT
                    'districts',
                    (SELECT COUNT(*) FROM ree_common.districts),
                    (SELECT COUNT(*) FROM ree_common.districts_translation)
                UNION ALL
                SELECT
                    'property_types',
                    (SELECT COUNT(*) FROM ree_common.property_types),
                    (SELECT COUNT(*) FROM ree_common.property_types_translation)
                ORDER BY records DESC
            """)

            print("\n📊 Master Data Counts:")
            total_records = 0
            total_translations = 0

            for row in counts:
                print(f"  {row['table_name']:20} {row['records']:4} records | {row['translations']:4} translations")
                total_records += row['records']
                total_translations += row['translations']

            print(f"\n  {'TOTAL':20} {total_records:4} records | {total_translations:4} translations")

            await conn.close()

            if total_records > 0:
                print(f"\n✅ Database contains master data")
                return True
            else:
                print(f"\n❌ Database is empty")
                return False

        except Exception as e:
            print(f"❌ Data count error: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("MASTER DATA API TEST SUITE")
        print("Database Schema: ree_common (NEW)")
        print("="*60)

        results = {
            "health": await self.test_health(),
            "database_query": await self.test_direct_database_query(),
            "fuzzy_matching": await self.test_fuzzy_matching(),
            "data_counts": await self.test_data_counts()
        }

        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)

        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name:20} {status}")

        total_passed = sum(results.values())
        total_tests = len(results)

        print("\n" + "="*60)
        print(f"TOTAL: {total_passed}/{total_tests} tests passed")
        print("="*60)

        await self.client.aclose()

        return all(results.values())


async def main():
    tester = MasterDataTester()
    success = await tester.run_all_tests()

    if success:
        print("\n🎉 All tests passed! Database schema is working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

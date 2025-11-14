"""
Test Vietnam Location Extraction Service
==========================================
PURPOSE: Test extraction accuracy with full 63 Vietnam provinces
DATE: 2025-11-14
"""

import asyncio
import asyncpg
from typing import List, Dict, Any
from dataclasses import dataclass

# Database connection
DB_CONFIG = {
    'host': '103.153.74.213',
    'port': 5432,
    'database': 'ree_ai',
    'user': 'ree_ai_user',
    'password': 'ree_ai_pass_2025'
}


@dataclass
class TestCase:
    """Test case with input text and expected results"""
    description: str
    text: str
    expected_provinces: List[str]  # Expected province codes
    expected_districts: List[str] = None  # Expected district codes


# Test cases covering different Vietnam regions
TEST_CASES = [
    # Northern Region
    TestCase(
        description="Hanoi - Capital",
        text="Bán nhà 5 tầng mặt phố Hoàng Quốc Việt, Hà Nội, giá 15 tỷ",
        expected_provinces=['VN_HANOI']
    ),
    TestCase(
        description="Hanoi - Alternative names",
        text="Cho thuê căn hộ cao cấp tại thủ đô Hà Nội",
        expected_provinces=['VN_HANOI']
    ),
    TestCase(
        description="Quang Ninh - Ha Long",
        text="Bán biệt thự view vịnh Hạ Long, Quảng Ninh",
        expected_provinces=['VN_QUANG_NINH']
    ),
    TestCase(
        description="Lao Cai - Sapa",
        text="Homestay Sapa, Lào Cai, view núi tuyệt đẹp",
        expected_provinces=['VN_LAO_CAI']
    ),

    # Central Region
    TestCase(
        description="Da Nang - Central city",
        text="Bán căn hộ 2PN view biển Đà Nẵng, giá 3.5 tỷ",
        expected_provinces=['VN_DANANG']
    ),
    TestCase(
        description="Hue - Ancient capital",
        text="Nhà vườn cổ kính Huế, Thừa Thiên Huế",
        expected_provinces=['VN_THUA_THIEN_HUE']
    ),
    TestCase(
        description="Nha Trang - Beach city",
        text="Resort cao cấp Nha Trang, Khánh Hòa, sát biển",
        expected_provinces=['VN_KHANH_HOA']
    ),
    TestCase(
        description="Phan Thiet - Mui Ne",
        text="Biệt thự biển Mũi Né, Phan Thiết, Bình Thuận",
        expected_provinces=['VN_BINH_THUAN']
    ),

    # Highland Region
    TestCase(
        description="Da Lat - Highland city",
        text="Bán villa sân vườn Đà Lạt, Lâm Đồng, view thung lũng",
        expected_provinces=['VN_LAM_DONG']
    ),
    TestCase(
        description="Pleiku - Central Highlands",
        text="Đất nền trung tâm Pleiku, Gia Lai",
        expected_provinces=['VN_GIA_LAI']
    ),
    TestCase(
        description="Buon Ma Thuot - Coffee city",
        text="Nhà vườn cà phê Buôn Ma Thuột, Đắk Lắk",
        expected_provinces=['VN_DAK_LAK']
    ),

    # Southern Region
    TestCase(
        description="HCMC - Largest city (multiple aliases)",
        text="Bán căn hộ cao cấp Quận 7, TP.HCM, view sông Sài Gòn",
        expected_provinces=['VN_HCMC'],
        expected_districts=['Q7']
    ),
    TestCase(
        description="HCMC - Saigon alias",
        text="Cho thuê văn phòng trung tâm Sài Gòn",
        expected_provinces=['VN_HCMC']
    ),
    TestCase(
        description="HCMC - TPHCM abbreviation",
        text="Mặt bằng kinh doanh TPHCM",
        expected_provinces=['VN_HCMC']
    ),
    TestCase(
        description="Binh Duong - Industrial province",
        text="Nhà xưởng 2000m2 Thủ Dầu Một, Bình Dương",
        expected_provinces=['VN_BINH_DUONG']
    ),
    TestCase(
        description="Dong Nai - Bien Hoa",
        text="Kho bãi Biên Hòa, Đồng Nai, gần KCN",
        expected_provinces=['VN_DONG_NAI']
    ),
    TestCase(
        description="Vung Tau - Beach city",
        text="Condotel Vũng Tàu, Bà Rịa Vũng Tàu, view biển 180 độ",
        expected_provinces=['VN_BA_RIA_VUNG_TAU']
    ),
    TestCase(
        description="Can Tho - Mekong Delta",
        text="Nhà vườn ven sông Cần Thơ, miệt vườn",
        expected_provinces=['VN_CAN_THO']
    ),
    TestCase(
        description="Phu Quoc - Island paradise",
        text="Resort 5 sao Phú Quốc, Kiên Giang, bãi Sao",
        expected_provinces=['VN_KIEN_GIANG']
    ),
    TestCase(
        description="My Tho - Tien Giang",
        text="Nhà vườn Mỹ Tho, Tiền Giang, ven sông",
        expected_provinces=['VN_TIEN_GIANG']
    ),

    # Complex cases
    TestCase(
        description="Multiple provinces in one text",
        text="Cần tìm nhà đầu tư dự án bất động sản tại Hà Nội, Đà Nẵng và TP.HCM",
        expected_provinces=['VN_HANOI', 'VN_DANANG', 'VN_HCMC']
    ),
    TestCase(
        description="Province with district",
        text="Bán nhà mặt tiền Quận 1, TP. Hồ Chí Minh, gần chợ Bến Thành",
        expected_provinces=['VN_HCMC'],
        expected_districts=['Q1']
    ),
    TestCase(
        description="All variations of HCMC",
        text="Tìm kiếm căn hộ tại Hồ Chí Minh, Sài Gòn, HCM, TPHCM",
        expected_provinces=['VN_HCMC']
    ),
]


class VietnamLocationExtractor:
    """Test Vietnam location extraction"""

    def __init__(self):
        self.conn = None
        self.results = []

    async def connect(self):
        """Connect to database"""
        print(f"🔗 Connecting to database at {DB_CONFIG['host']}...")
        self.conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Connected successfully")

    async def extract_provinces(self, text: str) -> List[Dict[str, Any]]:
        """Extract provinces from text using fuzzy matching"""
        query = """
            SELECT DISTINCT
                p.code,
                p.name as name_en,
                t.translated_text as name_vi,
                t.aliases
            FROM ree_common.provinces p
            JOIN ree_common.provinces_translation t
                ON p.id = t.province_id
            WHERE t.lang_code = 'vi'
              AND p.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
              AND EXISTS (
                SELECT 1 FROM unnest(t.aliases) alias
                WHERE LOWER($1) LIKE '%' || LOWER(alias) || '%'
              )
            ORDER BY p.code
        """

        results = await self.conn.fetch(query, text)
        return [dict(r) for r in results]

    async def extract_districts(self, text: str) -> List[Dict[str, Any]]:
        """Extract districts from text"""
        query = """
            SELECT DISTINCT
                d.code,
                d.name as name_en,
                dt.translated_text as name_vi
            FROM ree_common.districts d
            LEFT JOIN ree_common.districts_translation dt
                ON d.id = dt.district_id AND dt.lang_code = 'vi'
            WHERE d.country_id = (SELECT id FROM ree_common.countries WHERE code = 'VN')
              AND (
                LOWER($1) LIKE '%' || LOWER(d.name) || '%'
                OR (dt.aliases IS NOT NULL AND EXISTS (
                    SELECT 1 FROM unnest(dt.aliases) alias
                    WHERE LOWER($1) LIKE '%' || LOWER(alias) || '%'
                ))
              )
            ORDER BY d.code
        """

        results = await self.conn.fetch(query, text)
        return [dict(r) for r in results]

    async def test_case(self, test: TestCase) -> Dict[str, Any]:
        """Run single test case"""
        print(f"\n{'='*70}")
        print(f"📝 Test: {test.description}")
        print(f"{'='*70}")
        print(f"Input: {test.text}")
        print(f"Expected provinces: {test.expected_provinces}")
        if test.expected_districts:
            print(f"Expected districts: {test.expected_districts}")

        # Extract provinces
        provinces = await self.extract_provinces(test.text)
        extracted_province_codes = [p['code'] for p in provinces]

        # Extract districts
        districts = await self.extract_districts(test.text)
        extracted_district_codes = [d['code'] for d in districts]

        # Check results
        province_match = set(extracted_province_codes) == set(test.expected_provinces)
        district_match = True
        if test.expected_districts:
            district_match = set(extracted_district_codes) == set(test.expected_districts)

        success = province_match and district_match

        # Print results
        print(f"\n📍 Extracted Provinces ({len(provinces)}):")
        for p in provinces:
            print(f"  ✓ {p['code']}: {p['name_en']} ({p['name_vi']})")

        if districts:
            print(f"\n🏙️ Extracted Districts ({len(districts)}):")
            for d in districts:
                print(f"  ✓ {d['code']}: {d['name_en']}")

        # Verification
        print(f"\n{'='*70}")
        if success:
            print(f"✅ TEST PASSED")
        else:
            print(f"❌ TEST FAILED")
            if not province_match:
                print(f"  Expected provinces: {test.expected_provinces}")
                print(f"  Got: {extracted_province_codes}")
            if not district_match:
                print(f"  Expected districts: {test.expected_districts}")
                print(f"  Got: {extracted_district_codes}")

        return {
            'test': test.description,
            'input': test.text,
            'success': success,
            'provinces': provinces,
            'districts': districts,
            'province_match': province_match,
            'district_match': district_match
        }

    async def run_all_tests(self):
        """Run all test cases"""
        print("="*70)
        print("🧪 VIETNAM LOCATION EXTRACTION TEST SUITE")
        print("="*70)
        print(f"Total test cases: {len(TEST_CASES)}")
        print("="*70)

        await self.connect()

        for test in TEST_CASES:
            result = await self.test_case(test)
            self.results.append(result)
            await asyncio.sleep(0.1)  # Small delay between tests

        await self.print_summary()
        await self.conn.close()

    async def print_summary(self):
        """Print test summary"""
        print("\n\n")
        print("="*70)
        print("📊 TEST SUMMARY")
        print("="*70)

        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed

        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")

        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for r in self.results:
                if not r['success']:
                    print(f"  - {r['test']}")
                    print(f"    Input: {r['input']}")

        # Province coverage
        all_provinces = set()
        for r in self.results:
            for p in r['provinces']:
                all_provinces.add(p['code'])

        print(f"\n📍 Province Coverage:")
        print(f"  Unique provinces extracted: {len(all_provinces)}")
        print(f"  Total Vietnam provinces: 63")
        print(f"  Coverage: {len(all_provinces)/63*100:.1f}%")

        print("\n" + "="*70)

        if passed == total:
            print("🎉 ALL TESTS PASSED! Extraction service working perfectly!")
        else:
            print(f"⚠️  {failed} tests failed. Please review.")

        print("="*70)

        return passed == total


async def main():
    """Main execution"""
    tester = VietnamLocationExtractor()
    success = await tester.run_all_tests()

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

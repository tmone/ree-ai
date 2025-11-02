"""
Test Suite for Price Range Filtering
Validates that price_normalized field works correctly for range queries
"""
import asyncio
import httpx
from typing import List, Dict

class PriceFilteringTestSuite:
    def __init__(self, db_gateway_url: str = "http://localhost:8081", orchestrator_url: str = "http://localhost:8090"):
        self.db_gateway_url = db_gateway_url
        self.orchestrator_url = orchestrator_url
        self.results: List[Dict] = []

    async def test_db_gateway_price_range(self, min_price: float, max_price: float, test_name: str):
        """Test DB Gateway price range filter directly"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.db_gateway_url}/search",
                    json={
                        "query": "căn hộ",
                        "filters": {
                            "min_price": min_price,
                            "max_price": max_price
                        },
                        "limit": 20
                    }
                )

                if response.status_code != 200:
                    print(f"❌ {test_name}: HTTP {response.status_code}")
                    return False

                data = response.json()
                results = data.get("results", [])

                if not results:
                    print(f"⚠️  {test_name}: No results found")
                    return False

                # Verify ALL results are within price range
                violations = []
                for result in results:
                    # Parse price from string (e.g., "3,2 tỷ")
                    price_str = result.get("price", "")
                    price_display = price_str

                    # Try to extract numeric value for validation
                    try:
                        price_str_clean = price_str.replace(",", ".").replace(" ", "").lower()
                        import re
                        match = re.search(r'(\d+(?:\.\d+)?)', price_str_clean)
                        if match:
                            num = float(match.group(1))
                            if "tỷ" in price_str_clean:
                                price_value = num * 1_000_000_000
                            elif "triệu" in price_str_clean:
                                price_value = num * 1_000_000
                            else:
                                price_value = num

                            # Check if within range
                            if price_value < min_price or price_value > max_price:
                                violations.append({
                                    "title": result.get("title", "")[:50],
                                    "price": price_display,
                                    "price_value": price_value,
                                    "expected_range": f"{min_price/1e9:.1f}-{max_price/1e9:.1f} tỷ"
                                })
                    except:
                        pass  # Skip validation if parsing fails

                if violations:
                    print(f"❌ {test_name}: Found {len(violations)} violations")
                    for v in violations[:3]:
                        print(f"   - {v['price']} ({v['price_value']/1e9:.2f} tỷ) outside {v['expected_range']}")
                    return False

                print(f"✅ {test_name}: {len(results)} results, all within range {min_price/1e9:.1f}-{max_price/1e9:.1f} tỷ")
                return True

            except Exception as e:
                print(f"❌ {test_name}: Exception - {str(e)}")
                return False

    async def test_orchestrator_price_query(self, query: str, min_expected: float, max_expected: float, test_name: str):
        """Test Orchestrator end-to-end price query"""
        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                response = await client.post(
                    f"{self.orchestrator_url}/orchestrate",
                    json={
                        "user_id": "test_user_price",
                        "query": query,
                        "conversation_id": f"price_test_{test_name.replace(' ', '_')}"
                    }
                )

                if response.status_code != 200:
                    print(f"❌ {test_name}: HTTP {response.status_code}")
                    return False

                data = response.json()
                response_text = data.get("response", "")

                # Extract prices from response
                import re
                prices = re.findall(r'(\d+(?:,\d+)?(?:\.\d+)?)\s*tỷ', response_text)

                if not prices:
                    print(f"⚠️  {test_name}: No prices found in response")
                    return False

                # Validate prices
                violations = []
                for price_str in prices[:10]:  # Check first 10 prices
                    try:
                        price_num = float(price_str.replace(",", "."))
                        price_value = price_num * 1_000_000_000

                        if price_value < min_expected or price_value > max_expected:
                            violations.append({
                                "price": f"{price_str} tỷ",
                                "value": price_num,
                                "expected": f"{min_expected/1e9:.1f}-{max_expected/1e9:.1f} tỷ"
                            })
                    except:
                        pass

                if violations:
                    print(f"❌ {test_name}: Found {len(violations)} price violations")
                    for v in violations[:3]:
                        print(f"   - {v['price']} outside {v['expected']}")
                    return False

                print(f"✅ {test_name}: All prices within {min_expected/1e9:.1f}-{max_expected/1e9:.1f} tỷ")
                return True

            except Exception as e:
                print(f"❌ {test_name}: Exception - {str(e)}")
                return False

    async def run_all_tests(self):
        """Run complete price filtering test suite"""
        print("🧪 Starting Price Filtering Test Suite...")
        print("=" * 80)

        test_cases = [
            # (min_price, max_price, test_name)
            (2_000_000_000, 3_000_000_000, "DB Gateway - 2-3 tỷ"),
            (3_000_000_000, 5_000_000_000, "DB Gateway - 3-5 tỷ"),
            (5_000_000_000, 10_000_000_000, "DB Gateway - 5-10 tỷ"),
            (1_000_000_000, 2_000_000_000, "DB Gateway - 1-2 tỷ"),
        ]

        print("\n📍 Test Suite 1: DB Gateway Direct Price Queries")
        print("-" * 80)

        passed = 0
        failed = 0

        for min_price, max_price, test_name in test_cases:
            result = await self.test_db_gateway_price_range(min_price, max_price, test_name)
            if result:
                passed += 1
            else:
                failed += 1

        print("\n📍 Test Suite 2: Orchestrator End-to-End Price Queries")
        print("-" * 80)

        orchestrator_tests = [
            ("Tìm căn hộ giá từ 2-3 tỷ", 2_000_000_000, 3_000_000_000, "Orchestrator - 2-3 tỷ"),
            ("Căn hộ giá dưới 2 tỷ", 0, 2_000_000_000, "Orchestrator - dưới 2 tỷ"),
            ("Tìm nhà giá từ 5-7 tỷ", 5_000_000_000, 7_000_000_000, "Orchestrator - 5-7 tỷ"),
        ]

        for query, min_price, max_price, test_name in orchestrator_tests:
            result = await self.test_orchestrator_price_query(query, min_price, max_price, test_name)
            if result:
                passed += 1
            else:
                failed += 1

        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        total = passed + failed
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")

        if failed == 0:
            print("\n🎉 ALL PRICE FILTERING TESTS PASSED!")
        else:
            print(f"\n🚨 {failed} TESTS FAILED")

        print("=" * 80)


async def main():
    suite = PriceFilteringTestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

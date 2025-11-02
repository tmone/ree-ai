"""
Automated Test Suite for City Filtering
Tests both DB Gateway and Orchestrator end-to-end

Run with: python tests/test_city_filtering.py
"""
import asyncio
import httpx
import json
from typing import List, Dict, Optional
from datetime import datetime


class TestResult:
    def __init__(self, name: str, passed: bool, message: str, details: Optional[Dict] = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}


class CityFilteringTestSuite:
    def __init__(self, db_gateway_url: str = "http://localhost:8081", orchestrator_url: str = "http://localhost:8090"):
        self.db_gateway_url = db_gateway_url
        self.orchestrator_url = orchestrator_url
        self.results: List[TestResult] = []

    async def test_db_gateway_city_filter(self, city: str, expected_city: str, min_results: int = 1):
        """Test DB Gateway city filter directly"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.db_gateway_url}/search",
                    json={
                        "query": "căn hộ",
                        "filters": {"city": city},
                        "limit": 50
                    }
                )

                if response.status_code != 200:
                    return TestResult(
                        name=f"DB Gateway - City Filter: {city}",
                        passed=False,
                        message=f"HTTP {response.status_code}",
                        details={"response": response.text}
                    )

                data = response.json()
                results = data.get("results", [])
                total = data.get("total", 0)

                # Check if we got results
                if total < min_results:
                    return TestResult(
                        name=f"DB Gateway - City Filter: {city}",
                        passed=False,
                        message=f"Expected >= {min_results} results, got {total}",
                        details={"total": total}
                    )

                # Verify ALL results are from the correct city
                wrong_cities = []
                for result in results:
                    result_city = result.get("city", "")
                    if result_city != expected_city:
                        wrong_cities.append({
                            "title": result.get("title", "")[:50],
                            "city": result_city,
                            "district": result.get("district", "")
                        })

                if wrong_cities:
                    return TestResult(
                        name=f"DB Gateway - City Filter: {city}",
                        passed=False,
                        message=f"Found {len(wrong_cities)}/{len(results)} results from wrong cities",
                        details={"wrong_cities": wrong_cities[:3]}
                    )

                return TestResult(
                    name=f"DB Gateway - City Filter: {city}",
                    passed=True,
                    message=f"✅ All {len(results)} results from {expected_city} (total: {total})",
                    details={"total": total, "sample_size": len(results)}
                )

            except Exception as e:
                return TestResult(
                    name=f"DB Gateway - City Filter: {city}",
                    passed=False,
                    message=f"Exception: {str(e)}",
                    details={"error": str(e)}
                )

    async def test_orchestrator_city_query(self, query: str, expected_city: str, test_name: str):
        """Test Orchestrator end-to-end with city-specific query"""
        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                response = await client.post(
                    f"{self.orchestrator_url}/orchestrate",
                    json={
                        "user_id": "test_user",
                        "query": query,
                        "conversation_id": f"test_{datetime.now().timestamp()}"
                    }
                )

                if response.status_code != 200:
                    return TestResult(
                        name=f"Orchestrator - {test_name}",
                        passed=False,
                        message=f"HTTP {response.status_code}",
                        details={"response": response.text[:200]}
                    )

                data = response.json()
                response_text = data.get("response", "")

                # Parse property results from response
                # Look for location indicators in response
                if expected_city.lower() not in response_text.lower():
                    return TestResult(
                        name=f"Orchestrator - {test_name}",
                        passed=False,
                        message=f"Response doesn't mention {expected_city}",
                        details={"response_snippet": response_text[:300]}
                    )

                # Check for wrong cities in response
                wrong_cities = ["Hà Nội", "Đà Nẵng", "Quy Nhơn", "Cà Mau", "Bình Dương"]
                if expected_city in wrong_cities:
                    wrong_cities.remove(expected_city)

                found_wrong = []
                for wrong_city in wrong_cities:
                    if wrong_city in response_text:
                        found_wrong.append(wrong_city)

                if found_wrong:
                    return TestResult(
                        name=f"Orchestrator - {test_name}",
                        passed=False,
                        message=f"Response mentions wrong cities: {found_wrong}",
                        details={"wrong_cities": found_wrong, "response_snippet": response_text[:300]}
                    )

                return TestResult(
                    name=f"Orchestrator - {test_name}",
                    passed=True,
                    message=f"✅ Response correctly focuses on {expected_city}",
                    details={"execution_time": data.get("execution_time_ms", 0)}
                )

            except Exception as e:
                return TestResult(
                    name=f"Orchestrator - {test_name}",
                    passed=False,
                    message=f"Exception: {str(e)}",
                    details={"error": str(e)}
                )

    async def test_district_filter(self, city: str, district: str):
        """Test city + district combination"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.db_gateway_url}/search",
                    json={
                        "query": "căn hộ",
                        "filters": {"city": city, "district": district},
                        "limit": 20
                    }
                )

                if response.status_code != 200:
                    return TestResult(
                        name=f"DB Gateway - City+District: {city}/{district}",
                        passed=False,
                        message=f"HTTP {response.status_code}",
                        details={"response": response.text}
                    )

                data = response.json()
                results = data.get("results", [])
                total = data.get("total", 0)

                # Verify all results match both city AND district
                mismatches = []
                for result in results:
                    result_city = result.get("city", "")
                    result_district = result.get("district", "")
                    if result_city != city or result_district != district:
                        mismatches.append({
                            "title": result.get("title", "")[:50],
                            "city": result_city,
                            "district": result_district
                        })

                if mismatches:
                    return TestResult(
                        name=f"DB Gateway - City+District: {city}/{district}",
                        passed=False,
                        message=f"Found {len(mismatches)} results not matching {city}/{district}",
                        details={"mismatches": mismatches[:3]}
                    )

                return TestResult(
                    name=f"DB Gateway - City+District: {city}/{district}",
                    passed=True,
                    message=f"✅ All {len(results)} results match {city}/{district} (total: {total})",
                    details={"total": total}
                )

            except Exception as e:
                return TestResult(
                    name=f"DB Gateway - City+District: {city}/{district}",
                    passed=False,
                    message=f"Exception: {str(e)}",
                    details={"error": str(e)}
                )

    async def test_case_sensitivity(self):
        """Test if city filter is case-sensitive (it shouldn't be for keyword fields)"""
        test_cases = [
            ("Hồ Chí Minh", "Hồ Chí Minh"),
            ("hồ chí minh", "Hồ Chí Minh"),  # lowercase
            ("HỒ CHÍ MINH", "Hồ Chí Minh"),  # uppercase
        ]

        results = []
        for city_input, expected_city in test_cases:
            result = await self.test_db_gateway_city_filter(city_input, expected_city, min_results=1)
            results.append(result)

        return results

    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Starting Automated City Filtering Test Suite...")
        print("=" * 80)

        # Test 1: Basic city filters for different cities
        print("\n📍 Test Suite 1: Basic City Filters")
        print("-" * 80)

        city_tests = [
            ("Hồ Chí Minh", "Hồ Chí Minh", 100),
            ("Hà Nội", "Hà Nội", 10),
            ("Đà Nẵng", "Đà Nẵng", 1),
            ("Bình Dương", "Bình Dương", 1),
        ]

        for city, expected, min_results in city_tests:
            result = await self.test_db_gateway_city_filter(city, expected, min_results)
            self.results.append(result)
            self._print_result(result)

        # Test 2: City + District combinations
        print("\n📍 Test Suite 2: City + District Combinations")
        print("-" * 80)

        district_tests = [
            ("Hồ Chí Minh", "Quận 7"),
            ("Hồ Chí Minh", "Thủ Đức"),
            ("Hà Nội", "Hoàng Mai"),
            ("Hà Nội", "Bắc Từ Liêm"),
        ]

        for city, district in district_tests:
            result = await self.test_district_filter(city, district)
            self.results.append(result)
            self._print_result(result)

        # Test 3: Case sensitivity
        print("\n📍 Test Suite 3: Case Sensitivity")
        print("-" * 80)

        case_results = await self.test_case_sensitivity()
        self.results.extend(case_results)
        for result in case_results:
            self._print_result(result)

        # Test 4: Orchestrator end-to-end queries
        print("\n📍 Test Suite 4: Orchestrator End-to-End Queries")
        print("-" * 80)

        orchestrator_tests = [
            ("Tôi cần tìm mua căn hộ ở hồ chí minh", "Hồ Chí Minh", "HCM - Standard query"),
            ("Tìm căn hộ ở Hà Nội", "Hà Nội", "Hanoi - Standard query"),
            ("Có căn hộ nào ở quận 7 không?", "Hồ Chí Minh", "District mention (Q7)"),
            ("Tìm nhà ở thủ đức", "Hồ Chí Minh", "District mention (Thu Duc)"),
        ]

        for query, expected_city, test_name in orchestrator_tests:
            result = await self.test_orchestrator_city_query(query, expected_city, test_name)
            self.results.append(result)
            self._print_result(result)

        # Test 5: Edge cases
        print("\n📍 Test Suite 5: Edge Cases")
        print("-" * 80)

        # Test empty city filter
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.db_gateway_url}/search",
                    json={"query": "căn hộ", "filters": {"city": ""}, "limit": 10}
                )
                data = response.json()

                # Empty city should return results from all cities
                cities_found = set([r.get("city") for r in data.get("results", [])])

                result = TestResult(
                    name="Edge Case - Empty city filter",
                    passed=len(cities_found) > 1,
                    message=f"✅ Returns results from {len(cities_found)} different cities" if len(cities_found) > 1 else "❌ Should return multiple cities",
                    details={"cities": list(cities_found)}
                )
            except Exception as e:
                result = TestResult(
                    name="Edge Case - Empty city filter",
                    passed=False,
                    message=f"Exception: {str(e)}",
                    details={"error": str(e)}
                )

            self.results.append(result)
            self._print_result(result)

        # Summary
        self._print_summary()

    def _print_result(self, result: TestResult):
        """Print single test result"""
        icon = "✅" if result.passed else "❌"
        print(f"{icon} {result.name}")
        print(f"   {result.message}")
        if result.details and not result.passed:
            print(f"   Details: {json.dumps(result.details, indent=4, ensure_ascii=False)[:200]}")
        print()

    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)

        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"❌ Failed: {failed} ({failed/total*100:.1f}%)")

        if failed > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.message}")
        else:
            print("\n🎉 ALL TESTS PASSED!")

        print("\n" + "=" * 80)


async def main():
    suite = CityFilteringTestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())

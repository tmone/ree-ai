#!/usr/bin/env python3
"""
Continuous Testing System - REE AI Orchestrator
Runs various test scenarios continuously to find bugs
"""
import asyncio
import httpx
import time
import random
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import sys


@dataclass
class TestResult:
    scenario: str
    query: str
    success: bool
    response_time: float
    confidence: float
    error: str = None
    bug_detected: bool = False
    bug_description: str = None


class ContinuousTestScenarios:
    """
    Continuous testing with diverse real-world scenarios
    """

    def __init__(self, base_url: str = "http://localhost:8090"):
        self.base_url = base_url
        self.test_count = 0
        self.bugs_found = []
        self.results = []

    def get_test_scenarios(self) -> Dict[str, List[str]]:
        """
        Comprehensive test scenarios covering real-world use cases
        """
        return {
            "real_estate_search": [
                # Normal searches
                "Tìm căn hộ 3 phòng ngủ Quận 2",
                "Biệt thự Phú Mỹ Hưng dưới 20 tỷ",
                "Nhà phố gần trường quốc tế",
                "Căn hộ có hồ bơi và gym Thảo Điền",
                "Đất nền Thủ Đức giá 50 triệu/m²",

                # With specific amenities
                "Tìm nhà có sân vườn rộng và garage 2 xe",
                "Căn hộ view sông ban công hướng Đông",
                "Biệt thự có wine cellar và home theater",
                "Nhà phố mặt tiền 8m có rooftop",
                "Căn hộ smart home full nội thất",

                # Price-focused
                "Nhà dưới 5 tỷ gần metro",
                "Căn hộ 2-3 tỷ cho gia đình trẻ",
                "Biệt thự cao cấp 50-100 tỷ",
                "Mặt bằng kinh doanh giá tốt",

                # Location-specific
                "Nhà gần BigC Quận 7",
                "Căn hộ walking distance đến Landmark 81",
                "Biệt thự ven sông yên tĩnh",
                "Nhà gần bệnh viện FV",
            ],

            "ambiguous_queries": [
                # Vague aesthetic terms (should trigger clarification)
                "Tìm nhà đẹp",
                "Căn hộ sang trọng",
                "Nhà chất lượng tốt",
                "Biệt thự cao cấp",
                "Find a nice house",
                "Good quality apartment",
                "Luxury property",

                # Missing critical info
                "Nhà ở Sài Gòn",
                "5 tỷ",
                "3 bedrooms",
                "Có hồ bơi",
                "Near school",
            ],

            "conversational": [
                "Xin chào, tôi muốn tìm nhà",
                "Bạn có thể giúp tôi không?",
                "Tôi nên mua nhà ở đâu?",
                "So sánh Quận 2 và Quận 7",
                "Giá nhà đang như thế nào?",
                "Khu nào tốt cho gia đình có con nhỏ?",
                "What's the best area for expats?",
                "Is it a good time to buy?",
            ],

            "multilingual": [
                "Find apartment Quận 2",
                "Tìm house near AIS school",
                "Căn hộ with pool and gym",
                "Biệt thự in District 7",
                "Property gần trường quốc tế",
            ],

            "complex_criteria": [
                "Căn hộ 3PN, 2WC, có ban công, view đẹp, gần trường quốc tế, dưới 10 tỷ, Quận 2 hoặc Quận 7",
                "Biệt thự 4-5PN, có sân vườn, garage 3 xe, an ninh 24/7, Phú Mỹ Hưng, 20-30 tỷ",
                "Nhà phố mặt tiền >=6m, 4 tầng, gần chợ, giá 8-12 tỷ, hẻm xe hơi",
                "Căn hộ duplex, tầng cao, view sông, full nội thất, có hồ bơi vô cực",
            ],

            "special_characters": [
                "Nhà @Quận 2",
                "Căn hộ #ThảoDiền",
                "Biệt thự (Phú Mỹ Hưng)",
                "Nhà [3PN]",
                "Giá $100,000",
                "5,000,000,000 VNĐ",
                "100m² - 150m²",
            ],

            "numerical_variations": [
                "3 bedrooms",
                "3PN",
                "3 phòng ngủ",
                "three bedrooms",
                "ba phòng ngủ",
                "5 tỷ",
                "5000000000",
                "5,000,000,000",
                "5 billion VND",
                "$215,000",
            ],

            "typos_and_misspellings": [
                "Tim can ho Quan 2",  # No diacritics
                "Biet thu Phu My Hung",
                "Nha pho gan truong quoc te",
                "Can ho co ho boi",
                "Apartmnet District 2",
                "Vila Thao Dien",
            ],

            "edge_cases": [
                "a",
                "Nhà",
                "Find",
                "???",
                "123",
                "...",
                "Nhà nhà nhà nhà nhà",
                "QUẬN 2 QUẬN 2 QUẬN 2",
            ],

            "performance_test": [
                # These should all be fast (<5s)
                "Căn hộ Q2" * 10,
                "Tìm nhà" + " " * 50 + "Quận 2",
                "A" * 100 + "Căn hộ",
            ]
        }

    async def run_single_test(self, scenario: str, query: str) -> TestResult:
        """Run a single test and analyze results"""
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/orchestrate/v2",
                    json={"query": query, "user_id": "continuous_test"}
                )

                elapsed = time.time() - start_time

                if response.status_code != 200:
                    return TestResult(
                        scenario=scenario,
                        query=query,
                        success=False,
                        response_time=elapsed,
                        confidence=0.0,
                        error=f"HTTP {response.status_code}",
                        bug_detected=True,
                        bug_description=f"Non-200 status code: {response.status_code}"
                    )

                data = response.json()
                confidence = data.get("confidence", 0.0)

                # Bug detection logic
                bug_detected = False
                bug_description = None

                # Check 1: Response time too slow
                if elapsed > 10.0:
                    bug_detected = True
                    bug_description = f"Slow response: {elapsed:.2f}s (should be <10s)"

                # Check 2: Empty query not caught (should have been fixed)
                if not query.strip() and confidence > 0.1:
                    bug_detected = True
                    bug_description = f"Empty query has confidence {confidence} (should be ~0.0)"

                # Check 3: Vague queries should trigger ambiguity
                vague_terms = ["đẹp", "tốt", "sang", "nice", "good", "quality", "luxury"]
                has_vague = any(term in query.lower() for term in vague_terms)
                has_specific = any(c.isdigit() for c in query)  # Has numbers

                if has_vague and not has_specific and len(query) < 30:
                    needs_clarification = data.get("needs_clarification", False)
                    if not needs_clarification:
                        bug_detected = True
                        bug_description = f"Vague query '{query}' should trigger clarification"

                # Check 4: Confidence should be reasonable
                if confidence < 0.0 or confidence > 1.0:
                    bug_detected = True
                    bug_description = f"Invalid confidence: {confidence} (should be 0.0-1.0)"

                # Check 5: Response should not be empty
                response_text = data.get("response", "")
                if not response_text or len(response_text) < 10:
                    bug_detected = True
                    bug_description = "Response text too short or empty"

                return TestResult(
                    scenario=scenario,
                    query=query,
                    success=True,
                    response_time=elapsed,
                    confidence=confidence,
                    bug_detected=bug_detected,
                    bug_description=bug_description
                )

        except httpx.TimeoutException:
            elapsed = time.time() - start_time
            return TestResult(
                scenario=scenario,
                query=query,
                success=False,
                response_time=elapsed,
                confidence=0.0,
                error="Timeout",
                bug_detected=True,
                bug_description=f"Request timeout after {elapsed:.2f}s"
            )
        except Exception as e:
            elapsed = time.time() - start_time
            return TestResult(
                scenario=scenario,
                query=query,
                success=False,
                response_time=elapsed,
                confidence=0.0,
                error=str(e),
                bug_detected=True,
                bug_description=f"Exception: {str(e)}"
            )

    async def run_scenario_batch(self, scenario_name: str, queries: List[str]):
        """Run a batch of queries for one scenario"""
        print(f"\n{'='*60}")
        print(f"📋 SCENARIO: {scenario_name}")
        print(f"{'='*60}")

        results = []
        bugs_in_scenario = []

        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Testing: '{query}'")

            result = await self.run_single_test(scenario_name, query)
            results.append(result)
            self.test_count += 1

            # Print result
            status = "✅" if result.success and not result.bug_detected else "❌"
            print(f"  {status} Time: {result.response_time:.2f}s | Confidence: {result.confidence:.2f}")

            if result.bug_detected:
                print(f"  🐛 BUG: {result.bug_description}")
                bugs_in_scenario.append(result)
                self.bugs_found.append(result)

            if result.error:
                print(f"  ⚠️  ERROR: {result.error}")

            # Small delay to avoid overwhelming the server
            await asyncio.sleep(0.5)

        # Scenario summary
        print(f"\n{'='*60}")
        print(f"📊 SCENARIO SUMMARY: {scenario_name}")
        print(f"{'='*60}")
        print(f"Total tests: {len(results)}")
        print(f"✅ Successful: {sum(1 for r in results if r.success)}")
        print(f"❌ Failed: {sum(1 for r in results if not r.success)}")
        print(f"🐛 Bugs found: {len(bugs_in_scenario)}")
        print(f"⏱️  Avg time: {sum(r.response_time for r in results) / len(results):.2f}s")
        print(f"📈 Avg confidence: {sum(r.confidence for r in results if r.success) / max(sum(1 for r in results if r.success), 1):.2f}")

        if bugs_in_scenario:
            print(f"\n🐛 BUGS IN THIS SCENARIO:")
            for bug in bugs_in_scenario:
                print(f"  - Query: '{bug.query}'")
                print(f"    Issue: {bug.bug_description}")

        return results

    async def run_all_scenarios(self, iterations: int = 1):
        """Run all test scenarios"""
        print(f"╔{'='*68}╗")
        print(f"║{'CONTINUOUS TESTING SYSTEM - REE AI ORCHESTRATOR'.center(68)}║")
        print(f"║{'Running Diverse Test Scenarios'.center(68)}║")
        print(f"╚{'='*68}╝")

        scenarios = self.get_test_scenarios()

        for iteration in range(iterations):
            if iterations > 1:
                print(f"\n\n🔄 ITERATION {iteration + 1}/{iterations}")

            for scenario_name, queries in scenarios.items():
                results = await self.run_scenario_batch(scenario_name, queries)
                self.results.extend(results)

                # Short break between scenarios
                await asyncio.sleep(1)

        # Final summary
        self.print_final_summary()

    def print_final_summary(self):
        """Print comprehensive final summary"""
        print(f"\n\n╔{'='*68}╗")
        print(f"║{'FINAL TEST SUMMARY'.center(68)}║")
        print(f"╚{'='*68}╝")

        total_tests = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)
        bugs_found = len(self.bugs_found)

        print(f"\n📊 OVERALL STATISTICS:")
        print(f"  Total tests run: {total_tests}")
        print(f"  ✅ Successful: {successful} ({successful/total_tests*100:.1f}%)")
        print(f"  ❌ Failed: {failed} ({failed/total_tests*100:.1f}%)")
        print(f"  🐛 Bugs detected: {bugs_found}")

        if self.results:
            avg_time = sum(r.response_time for r in self.results) / len(self.results)
            max_time = max(r.response_time for r in self.results)
            min_time = min(r.response_time for r in self.results)

            print(f"\n⏱️  PERFORMANCE METRICS:")
            print(f"  Average response time: {avg_time:.2f}s")
            print(f"  Fastest response: {min_time:.2f}s")
            print(f"  Slowest response: {max_time:.2f}s")

            successful_results = [r for r in self.results if r.success]
            if successful_results:
                avg_conf = sum(r.confidence for r in successful_results) / len(successful_results)
                print(f"\n📈 CONFIDENCE METRICS:")
                print(f"  Average confidence: {avg_conf:.2f}")

        if self.bugs_found:
            print(f"\n🐛 BUGS FOUND ({len(self.bugs_found)}):")
            print(f"{'='*68}")

            # Group bugs by description
            bug_groups = {}
            for bug in self.bugs_found:
                desc = bug.bug_description
                if desc not in bug_groups:
                    bug_groups[desc] = []
                bug_groups[desc].append(bug)

            for i, (desc, bugs) in enumerate(bug_groups.items(), 1):
                print(f"\n[BUG #{i}] {desc}")
                print(f"  Occurrences: {len(bugs)}")
                print(f"  Example queries:")
                for bug in bugs[:3]:  # Show first 3 examples
                    print(f"    - '{bug.query}'")
                if len(bugs) > 3:
                    print(f"    ... and {len(bugs) - 3} more")
        else:
            print(f"\n✅ NO BUGS DETECTED! All tests passed.")

        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"continuous_test_report_{timestamp}.json"

        report_data = {
            "timestamp": timestamp,
            "total_tests": total_tests,
            "successful": successful,
            "failed": failed,
            "bugs_found": bugs_found,
            "results": [
                {
                    "scenario": r.scenario,
                    "query": r.query,
                    "success": r.success,
                    "response_time": r.response_time,
                    "confidence": r.confidence,
                    "bug_detected": r.bug_detected,
                    "bug_description": r.bug_description,
                    "error": r.error
                }
                for r in self.results
            ]
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Detailed report saved to: {report_file}")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Continuous Testing System for REE AI")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations to run")
    parser.add_argument("--url", type=str, default="http://localhost:8090", help="Base URL")
    parser.add_argument("--scenarios", nargs='+', help="Specific scenarios to run")

    args = parser.parse_args()

    tester = ContinuousTestScenarios(base_url=args.url)

    if args.scenarios:
        # Run only specified scenarios
        all_scenarios = tester.get_test_scenarios()
        for scenario_name in args.scenarios:
            if scenario_name in all_scenarios:
                await tester.run_scenario_batch(scenario_name, all_scenarios[scenario_name])
            else:
                print(f"⚠️  Unknown scenario: {scenario_name}")
        tester.print_final_summary()
    else:
        # Run all scenarios
        await tester.run_all_scenarios(iterations=args.iterations)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(0)

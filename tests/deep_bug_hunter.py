"""
Deep Bug Hunter - Advanced Testing
Finds subtle bugs, edge cases, performance issues, and logical errors
"""
import requests
import json
import time
import concurrent.futures
from typing import List, Dict, Any


class DeepBugHunter:
    """Advanced bug detection for edge cases and logic errors"""

    def __init__(self, base_url: str = "http://localhost:8090"):
        self.base_url = base_url
        self.bugs_found = []

    def test_edge_cases(self):
        """Test extreme edge cases"""
        print("\n" + "="*60)
        print("🔍 DEEP TEST 1: Edge Cases")
        print("="*60)

        edge_cases = [
            {"name": "Empty query", "query": ""},
            {"name": "Only spaces", "query": "   "},
            {"name": "Single character", "query": "a"},
            {"name": "Very long query", "query": "Tìm " * 100 + "căn hộ"},
            {"name": "Special characters", "query": "!@#$%^&*()"},
            {"name": "SQL injection attempt", "query": "'; DROP TABLE properties; --"},
            {"name": "XSS attempt", "query": "<script>alert('xss')</script>"},
            {"name": "Unicode emoji", "query": "Tìm nhà 🏠 đẹp 😍"},
            {"name": "Mixed languages", "query": "Find nhà house maison 家"},
            {"name": "Numbers only", "query": "123456789"},
        ]

        for test in edge_cases:
            print(f"\n[Edge] {test['name']}")
            print(f"  Query: '{test['query']}'")

            try:
                response = requests.post(
                    f"{self.base_url}/orchestrate/v2",
                    json={"user_id": "edge_test", "query": test["query"]},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    confidence = data.get("confidence", 0)

                    # Check for issues
                    if confidence > 0.5 and not test["query"].strip():
                        self.bugs_found.append({
                            "type": "LOGIC_ERROR",
                            "severity": "HIGH",
                            "test": test["name"],
                            "issue": f"Empty query has confidence {confidence} (should be low)",
                            "query": test["query"]
                        })
                        print(f"  🐛 BUG: Empty query shouldn't have high confidence")

                    if response.elapsed.total_seconds() > 5:
                        self.bugs_found.append({
                            "type": "PERFORMANCE",
                            "severity": "MEDIUM",
                            "test": test["name"],
                            "issue": f"Slow response: {response.elapsed.total_seconds():.2f}s",
                            "query": test["query"]
                        })
                        print(f"  ⚠️ SLOW: {response.elapsed.total_seconds():.2f}s")
                    else:
                        print(f"  ✅ Handled gracefully ({response.elapsed.total_seconds():.2f}s)")

                elif response.status_code == 500:
                    self.bugs_found.append({
                        "type": "CRASH",
                        "severity": "CRITICAL",
                        "test": test["name"],
                        "issue": "Server crashed with 500 error",
                        "query": test["query"]
                    })
                    print(f"  🔴 CRITICAL: Server crashed!")

                else:
                    print(f"  ⚠️ Unexpected status: {response.status_code}")

            except requests.Timeout:
                self.bugs_found.append({
                    "type": "TIMEOUT",
                    "severity": "HIGH",
                    "test": test["name"],
                    "issue": "Request timed out",
                    "query": test["query"]
                })
                print(f"  🐛 BUG: Timeout")
            except Exception as e:
                print(f"  ❌ Exception: {e}")

    def test_reasoning_consistency(self):
        """Test if reasoning chain is consistent"""
        print("\n" + "="*60)
        print("🔍 DEEP TEST 2: Reasoning Consistency")
        print("="*60)

        # Test same query multiple times - should give consistent results
        query = "Tìm căn hộ 3 phòng ngủ Quận 2"
        results = []

        for i in range(3):
            response = requests.post(
                f"{self.base_url}/orchestrate/v2",
                json={"user_id": f"consistency_{i}", "query": query},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                results.append({
                    "confidence": data.get("confidence", 0),
                    "intent": data.get("intent"),
                    "expanded_terms": len(data.get("knowledge_expansion", {}).get("expanded_terms", [])),
                    "reasoning_steps": len(data.get("reasoning_chain", {}).get("steps", []))
                })

        if len(results) == 3:
            # Check consistency
            confidences = [r["confidence"] for r in results]
            intents = [r["intent"] for r in results]
            terms = [r["expanded_terms"] for r in results]

            print(f"\nQuery: '{query}'")
            print(f"Run 1: confidence={confidences[0]:.2f}, intent={intents[0]}, terms={terms[0]}")
            print(f"Run 2: confidence={confidences[1]:.2f}, intent={intents[1]}, terms={terms[1]}")
            print(f"Run 3: confidence={confidences[2]:.2f}, intent={intents[2]}, terms={terms[2]}")

            # Check for inconsistency
            if len(set(intents)) > 1:
                self.bugs_found.append({
                    "type": "INCONSISTENCY",
                    "severity": "HIGH",
                    "test": "Reasoning consistency",
                    "issue": f"Intent varies: {intents}",
                    "query": query
                })
                print(f"🐛 BUG: Intent inconsistent!")

            if max(confidences) - min(confidences) > 0.3:
                self.bugs_found.append({
                    "type": "INCONSISTENCY",
                    "severity": "MEDIUM",
                    "test": "Reasoning consistency",
                    "issue": f"Confidence varies widely: {confidences}",
                    "query": query
                })
                print(f"⚠️ WARNING: Confidence varies widely")

            if len(set(terms)) > 1:
                print(f"ℹ️ Knowledge expansion varies: {terms} (acceptable)")

            if len(set(intents)) == 1 and max(confidences) - min(confidences) < 0.1:
                print("✅ Consistent reasoning across runs")

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        print("\n" + "="*60)
        print("🔍 DEEP TEST 3: Concurrent Request Handling")
        print("="*60)

        queries = [
            "Tìm căn hộ Quận 1",
            "Tìm nhà Quận 2",
            "Tìm đất Quận 7",
            "Tìm biệt thự Thủ Đức",
            "Tìm văn phòng Bình Thạnh"
        ]

        def make_request(query):
            start = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}/orchestrate/v2",
                    json={"user_id": "concurrent_test", "query": query},
                    timeout=30
                )
                elapsed = time.time() - start
                return {
                    "query": query,
                    "status": response.status_code,
                    "elapsed": elapsed,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "query": query,
                    "status": 0,
                    "elapsed": time.time() - start,
                    "success": False,
                    "error": str(e)
                }

        print(f"\nSending {len(queries)} concurrent requests...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, q) for q in queries]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Analyze results
        success_count = sum(1 for r in results if r["success"])
        avg_time = sum(r["elapsed"] for r in results) / len(results)
        max_time = max(r["elapsed"] for r in results)

        print(f"\nResults:")
        print(f"  Success: {success_count}/{len(queries)}")
        print(f"  Avg time: {avg_time:.2f}s")
        print(f"  Max time: {max_time:.2f}s")

        if success_count < len(queries):
            self.bugs_found.append({
                "type": "CONCURRENCY_ISSUE",
                "severity": "HIGH",
                "test": "Concurrent requests",
                "issue": f"Only {success_count}/{len(queries)} requests succeeded",
            })
            print(f"🐛 BUG: Failed to handle concurrent requests")

        if max_time > 10:
            self.bugs_found.append({
                "type": "PERFORMANCE",
                "severity": "MEDIUM",
                "test": "Concurrent requests",
                "issue": f"Max response time: {max_time:.2f}s",
            })
            print(f"⚠️ WARNING: Slow under load")

        if success_count == len(queries) and max_time < 5:
            print("✅ Handles concurrent requests well")

    def test_knowledge_base_coverage(self):
        """Test knowledge base expansion coverage"""
        print("\n" + "="*60)
        print("🔍 DEEP TEST 4: Knowledge Base Coverage")
        print("="*60)

        test_terms = [
            {"term": "hồ bơi", "should_expand": True, "expected_min": 2},
            {"term": "gym", "should_expand": True, "expected_min": 2},
            {"term": "trường quốc tế", "should_expand": True, "expected_min": 2},
            {"term": "biệt thự", "should_expand": True, "expected_min": 2},
            {"term": "căn hộ", "should_expand": True, "expected_min": 2},
            {"term": "quận 2", "should_expand": True, "expected_min": 2},
            {"term": "random_gibberish_xyz", "should_expand": False, "expected_min": 0},
        ]

        for test in test_terms:
            query = f"Tìm nhà có {test['term']}"

            response = requests.post(
                f"{self.base_url}/orchestrate/v2",
                json={"user_id": "kb_test", "query": query},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                expansion = data.get("knowledge_expansion", {})
                expanded_terms = expansion.get("expanded_terms", [])

                print(f"\nTerm: '{test['term']}'")
                print(f"  Expanded: {len(expanded_terms)} terms")

                if test["should_expand"]:
                    if len(expanded_terms) >= test["expected_min"]:
                        print(f"  ✅ Good expansion: {expanded_terms[:3]}...")
                    else:
                        self.bugs_found.append({
                            "type": "KNOWLEDGE_GAP",
                            "severity": "MEDIUM",
                            "test": "Knowledge base coverage",
                            "issue": f"Term '{test['term']}' only expanded to {len(expanded_terms)} terms (expected >= {test['expected_min']})",
                        })
                        print(f"  🐛 BUG: Poor expansion")
                else:
                    if len(expanded_terms) == 0:
                        print(f"  ✅ Correctly ignored unknown term")
                    else:
                        print(f"  ℹ️ Unexpectedly expanded: {expanded_terms}")

    def test_ambiguity_detection_accuracy(self):
        """Test ambiguity detection logic"""
        print("\n" + "="*60)
        print("🔍 DEEP TEST 5: Ambiguity Detection Accuracy")
        print("="*60)

        test_cases = [
            {"query": "Nhà ở Quận 2", "should_detect": True, "reason": "Location broad + type missing"},
            {"query": "5 tỷ", "should_detect": True, "reason": "Property type missing"},
            {"query": "Tìm nhà đẹp", "should_detect": True, "reason": "Vague aesthetic"},
            {"query": "Căn hộ 3PN Thảo Điền có hồ bơi", "should_detect": False, "reason": "Specific and clear"},
            {"query": "Biệt thự Phú Mỹ Hưng", "should_detect": False, "reason": "Clear type and location"},
        ]

        for test in test_cases:
            response = requests.post(
                f"{self.base_url}/orchestrate/v2",
                json={"user_id": "ambiguity_test", "query": test["query"]},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                needs_clarification = data.get("needs_clarification", False)

                print(f"\nQuery: '{test['query']}'")
                print(f"  Expected: {test['should_detect']}")
                print(f"  Detected: {needs_clarification}")

                if test["should_detect"] and not needs_clarification:
                    self.bugs_found.append({
                        "type": "AMBIGUITY_MISS",
                        "severity": "MEDIUM",
                        "test": "Ambiguity detection",
                        "issue": f"Failed to detect ambiguity: {test['reason']}",
                        "query": test["query"]
                    })
                    print(f"  🐛 BUG: Missed ambiguity ({test['reason']})")

                elif not test["should_detect"] and needs_clarification:
                    self.bugs_found.append({
                        "type": "FALSE_AMBIGUITY",
                        "severity": "LOW",
                        "test": "Ambiguity detection",
                        "issue": f"False positive: flagged clear query as ambiguous",
                        "query": test["query"]
                    })
                    print(f"  ⚠️ WARNING: False positive")

                else:
                    print(f"  ✅ Correct")

    def test_streaming_endpoint(self):
        """Test streaming endpoint"""
        print("\n" + "="*60)
        print("🔍 DEEP TEST 6: Streaming Endpoint")
        print("="*60)

        try:
            response = requests.post(
                f"{self.base_url}/orchestrate/v2/stream",
                json={"user_id": "stream_test", "query": "Tìm căn hộ"},
                stream=True,
                timeout=30
            )

            if response.status_code == 200:
                events = []
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith("data: "):
                            try:
                                event = json.loads(line_str[6:])
                                events.append(event)
                            except:
                                pass

                print(f"\nReceived {len(events)} events")

                event_types = [e.get("type") for e in events]
                print(f"Event types: {set(event_types)}")

                required_events = ["start", "intent", "response", "complete"]
                missing_events = [e for e in required_events if e not in event_types]

                if missing_events:
                    self.bugs_found.append({
                        "type": "STREAMING_INCOMPLETE",
                        "severity": "HIGH",
                        "test": "Streaming endpoint",
                        "issue": f"Missing events: {missing_events}",
                    })
                    print(f"  🐛 BUG: Missing events: {missing_events}")
                else:
                    print(f"  ✅ All required events present")

            else:
                self.bugs_found.append({
                    "type": "STREAMING_FAILED",
                    "severity": "HIGH",
                    "test": "Streaming endpoint",
                    "issue": f"Status {response.status_code}",
                })
                print(f"  🐛 BUG: Streaming failed with {response.status_code}")

        except Exception as e:
            self.bugs_found.append({
                "type": "STREAMING_ERROR",
                "severity": "HIGH",
                "test": "Streaming endpoint",
                "issue": str(e),
            })
            print(f"  ❌ Exception: {e}")

    def test_memory_leak(self):
        """Test for potential memory leaks"""
        print("\n" + "="*60)
        print("🔍 DEEP TEST 7: Memory Leak Detection")
        print("="*60)

        print("\nMaking 10 rapid requests to check for memory issues...")

        times = []
        for i in range(10):
            start = time.time()
            response = requests.post(
                f"{self.base_url}/orchestrate/v2",
                json={"user_id": f"memory_test_{i}", "query": f"Test {i}"},
                timeout=30
            )
            elapsed = time.time() - start
            times.append(elapsed)

            if i % 3 == 0:
                print(f"  Request {i+1}: {elapsed:.2f}s")

        # Check if times are increasing (potential memory leak)
        first_half_avg = sum(times[:5]) / 5
        second_half_avg = sum(times[5:]) / 5

        print(f"\nFirst 5 requests avg: {first_half_avg:.2f}s")
        print(f"Last 5 requests avg: {second_half_avg:.2f}s")

        if second_half_avg > first_half_avg * 1.5:
            self.bugs_found.append({
                "type": "MEMORY_LEAK_SUSPECTED",
                "severity": "MEDIUM",
                "test": "Memory leak",
                "issue": f"Response time increased from {first_half_avg:.2f}s to {second_half_avg:.2f}s",
            })
            print(f"⚠️ WARNING: Possible memory leak (times increasing)")
        else:
            print("✅ No obvious memory leak detected")

    def generate_report(self):
        """Generate comprehensive bug report"""
        print("\n" + "="*60)
        print("📊 DEEP BUG HUNTER - FINAL REPORT")
        print("="*60)

        # Group bugs by severity
        by_severity = {}
        for bug in self.bugs_found:
            severity = bug["severity"]
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(bug)

        print(f"\nTotal Bugs Found: {len(self.bugs_found)}")

        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity in by_severity:
                print(f"  {severity}: {len(by_severity[severity])}")

        if self.bugs_found:
            print("\n🐛 DETAILED BUG LIST:")
            for i, bug in enumerate(self.bugs_found, 1):
                print(f"\n{i}. [{bug['severity']}] {bug['type']}")
                print(f"   Test: {bug['test']}")
                print(f"   Issue: {bug['issue']}")
                if 'query' in bug:
                    print(f"   Query: '{bug['query']}'")

        else:
            print("\n✅ NO BUGS FOUND! System is robust.")

        return self.bugs_found


def main():
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║              DEEP BUG HUNTER - ADVANCED TESTING                ║")
    print("║   Edge Cases | Logic Errors | Performance | Concurrency       ║")
    print("╚════════════════════════════════════════════════════════════════╝")

    hunter = DeepBugHunter()

    hunter.test_edge_cases()
    hunter.test_reasoning_consistency()
    hunter.test_concurrent_requests()
    hunter.test_knowledge_base_coverage()
    hunter.test_ambiguity_detection_accuracy()
    hunter.test_streaming_endpoint()
    hunter.test_memory_leak()

    bugs = hunter.generate_report()

    # Save report
    with open("deep_bug_report.txt", "w") as f:
        f.write("DEEP BUG HUNTER REPORT\n")
        f.write("="*60 + "\n\n")
        for bug in bugs:
            f.write(f"{bug}\n\n")

    print(f"\n💾 Report saved to: deep_bug_report.txt")

    if not bugs:
        print("\n🎉 EXCELLENT! No bugs found in deep testing!")
    elif len(bugs) < 5:
        print(f"\n✅ GOOD! Only {len(bugs)} minor issues found.")
    else:
        print(f"\n⚠️ ATTENTION! {len(bugs)} issues need review.")


if __name__ == "__main__":
    main()

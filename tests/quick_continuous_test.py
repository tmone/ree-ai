#!/usr/bin/env python3
"""
Quick Continuous Test - Faster version with key scenarios
"""
import requests
import time
import json
from typing import Dict, List

BASE_URL = "http://localhost:8090/orchestrate/v2"

# Test scenarios
SCENARIOS = {
    "Normal Searches": [
        "Tìm căn hộ 3 phòng ngủ Quận 2",
        "Biệt thự Phú Mỹ Hưng dưới 20 tỷ",
        "Nhà phố gần trường quốc tế",
    ],
    "Ambiguous Queries (Should Trigger Clarification)": [
        "Tìm nhà đẹp",
        "Căn hộ sang trọng",
        "Find a nice house",
    ],
    "Conversational": [
        "Xin chào, tôi muốn tìm nhà",
        "So sánh Quận 2 và Quận 7",
        "What's the best area for expats?",
    ],
    "Multilingual": [
        "Find apartment Quận 2",
        "Căn hộ with pool and gym",
    ],
    "Complex Criteria": [
        "Căn hộ 3PN, có ban công, view đẹp, gần trường quốc tế, dưới 10 tỷ, Quận 2",
    ],
    "Edge Cases": [
        "a",
        "Nhà",
        "???",
    ],
    "Special Characters": [
        "Nhà @Quận 2",
        "Giá $100,000",
    ],
}

def test_query(query: str) -> Dict:
    """Test a single query"""
    try:
        start = time.time()
        response = requests.post(
            BASE_URL,
            json={"query": query, "user_id": "quick_test"},
            timeout=30
        )
        elapsed = time.time() - start

        if response.status_code != 200:
            return {
                "status": "❌ FAIL",
                "time": elapsed,
                "error": f"HTTP {response.status_code}",
                "bug": f"Non-200 status: {response.status_code}"
            }

        data = response.json()
        confidence = data.get("confidence", 0.0)
        needs_clarification = data.get("needs_clarification", False)

        # Bug detection
        bugs = []

        # Check 1: Slow response
        if elapsed > 10.0:
            bugs.append(f"SLOW: {elapsed:.1f}s")

        # Check 2: Vague queries should trigger clarification
        vague_terms = ["đẹp", "sang", "nice", "good", "quality", "luxury"]
        has_vague = any(term in query.lower() for term in vague_terms)
        has_specific = any(c.isdigit() for c in query)

        if has_vague and not has_specific and len(query) < 40:
            if not needs_clarification:
                bugs.append(f"AMBIGUITY MISS: '{query}' should ask clarification")

        # Check 3: Confidence range
        if confidence < 0.0 or confidence > 1.0:
            bugs.append(f"BAD CONFIDENCE: {confidence}")

        # Check 4: Empty response
        response_text = data.get("response", "")
        if not response_text or len(response_text) < 10:
            bugs.append("EMPTY RESPONSE")

        return {
            "status": "✅ PASS" if not bugs else "🐛 BUG",
            "time": elapsed,
            "confidence": confidence,
            "needs_clarification": needs_clarification,
            "bugs": bugs if bugs else None
        }

    except requests.Timeout:
        return {
            "status": "❌ TIMEOUT",
            "time": 30.0,
            "error": "Request timeout",
            "bug": "TIMEOUT >30s"
        }
    except Exception as e:
        return {
            "status": "❌ ERROR",
            "time": 0,
            "error": str(e),
            "bug": f"EXCEPTION: {str(e)}"
        }

def main():
    print("╔" + "="*68 + "╗")
    print("║" + "QUICK CONTINUOUS TEST - REE AI ORCHESTRATOR".center(68) + "║")
    print("╚" + "="*68 + "╝\n")

    total_tests = 0
    total_pass = 0
    total_bugs = 0
    all_bugs = []

    for scenario, queries in SCENARIOS.items():
        print(f"\n{'='*70}")
        print(f"📋 SCENARIO: {scenario}")
        print(f"{'='*70}")

        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] '{query}'")

            result = test_query(query)
            total_tests += 1

            print(f"  {result['status']} | {result['time']:.1f}s | Conf: {result.get('confidence', 0):.2f}", end="")

            if result.get('needs_clarification'):
                print(" | 🔔 Clarification", end="")

            print()

            if result.get('bugs'):
                for bug in result['bugs']:
                    print(f"    🐛 {bug}")
                    all_bugs.append({"query": query, "bug": bug})
                    total_bugs += 1
            elif result['status'] == "✅ PASS":
                total_pass += 1

            if result.get('error'):
                print(f"    ⚠️  {result['error']}")

    # Summary
    print(f"\n\n╔{'='*68}╗")
    print(f"║{'FINAL SUMMARY'.center(68)}║")
    print(f"╚{'='*68}╝")

    print(f"\n📊 Statistics:")
    print(f"  Total tests: {total_tests}")
    print(f"  ✅ Passed: {total_pass} ({total_pass/total_tests*100:.1f}%)")
    print(f"  🐛 Bugs found: {total_bugs}")

    if all_bugs:
        print(f"\n🐛 ALL BUGS DETECTED:")
        for i, bug_info in enumerate(all_bugs, 1):
            print(f"  [{i}] {bug_info['bug']}")
            print(f"      Query: '{bug_info['query']}'")
    else:
        print("\n✅ NO BUGS DETECTED!")

if __name__ == "__main__":
    main()

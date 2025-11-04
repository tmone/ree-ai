"""
Quick Manual Test Script
Tests the new ReAct endpoints and identifies bugs
"""
import requests
import json
from typing import List, Dict, Any


def test_orchestrate_v2():
    """Test the new /orchestrate/v2 endpoint"""
    print("\n" + "="*60)
    print("TESTING: /orchestrate/v2 Endpoint")
    print("="*60)

    test_cases = [
        {
            "name": "Simple apartment search",
            "query": "Tìm căn hộ 2 phòng ngủ Quận 2",
            "expected": "Should search for apartments in District 2"
        },
        {
            "name": "Ambiguous query",
            "query": "Nhà ở Quận 2",
            "expected": "Should detect ambiguity (property type missing, location broad)"
        },
        {
            "name": "Pool amenity search",
            "query": "Căn hộ có hồ bơi gần trường quốc tế",
            "expected": "Should expand 'hồ bơi' to pool synonyms and filter D2/D7"
        },
        {
            "name": "Price-based search",
            "query": "Nhà phố giá dưới 5 tỷ",
            "expected": "Should add price filter"
        },
        {
            "name": "Vague aesthetic query",
            "query": "Tìm nhà đẹp",
            "expected": "Should detect AMENITY_AMBIGUOUS"
        }
    ]

    results = []
    bugs_found = []

    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}/{len(test_cases)}] {test['name']}")
        print(f"Query: '{test['query']}'")
        print(f"Expected: {test['expected']}")

        try:
            response = requests.post(
                "http://localhost:8090/orchestrate/v2",
                json={
                    "user_id": f"test_user_{i}",
                    "query": test["query"],
                    "conversation_id": None
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # Extract key metrics
                intent = data.get("intent")
                confidence = data.get("confidence", 0)
                reasoning_steps = len(data.get("reasoning_chain", {}).get("steps", []))
                has_ambiguity = data.get("needs_clarification", False)
                expanded_terms = len(data.get("knowledge_expansion", {}).get("expanded_terms", []))

                print(f"✅ SUCCESS")
                print(f"  Intent: {intent}")
                print(f"  Confidence: {confidence:.2f}")
                print(f"  Reasoning steps: {reasoning_steps}")
                print(f"  Needs clarification: {has_ambiguity}")
                print(f"  Expanded terms: {expanded_terms}")

                # Check for potential issues
                if confidence < 0.5:
                    bugs_found.append({
                        "test": test["name"],
                        "issue": "LOW_CONFIDENCE",
                        "details": f"Confidence {confidence} is below 0.5"
                    })
                    print(f"  ⚠️ BUG: Low confidence ({confidence})")

                if reasoning_steps == 0:
                    bugs_found.append({
                        "test": test["name"],
                        "issue": "NO_REASONING_STEPS",
                        "details": "ReasoningChain has no steps"
                    })
                    print(f"  ⚠️ BUG: No reasoning steps")

                results.append({
                    "test": test["name"],
                    "status": "PASS",
                    "confidence": confidence,
                    "reasoning_steps": reasoning_steps
                })

            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"  Error: {response.text[:200]}")
                bugs_found.append({
                    "test": test["name"],
                    "issue": "HTTP_ERROR",
                    "details": f"Status {response.status_code}: {response.text[:100]}"
                })
                results.append({
                    "test": test["name"],
                    "status": "FAIL",
                    "error": response.text[:100]
                })

        except Exception as e:
            print(f"❌ EXCEPTION: {e}")
            bugs_found.append({
                "test": test["name"],
                "issue": "EXCEPTION",
                "details": str(e)
            })
            results.append({
                "test": test["name"],
                "status": "FAIL",
                "error": str(e)
            })

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    print(f"Total: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(results) - passed}")
    print(f"Bugs Found: {len(bugs_found)}")

    if bugs_found:
        print("\n🐛 BUGS DETECTED:")
        for i, bug in enumerate(bugs_found, 1):
            print(f"\n{i}. Test: {bug['test']}")
            print(f"   Issue: {bug['issue']}")
            print(f"   Details: {bug['details']}")

    return results, bugs_found


def test_knowledge_expansion():
    """Test knowledge expansion specifically"""
    print("\n" + "="*60)
    print("TESTING: Knowledge Expansion")
    print("="*60)

    test_queries = [
        "Căn hộ có hồ bơi",
        "Nhà gần trường quốc tế",
        "Biệt thự Quận 7",
        "Đất nền Thủ Đức"
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")

        try:
            response = requests.post(
                "http://localhost:8090/orchestrate/v2",
                json={
                    "user_id": "test_expansion",
                    "query": query,
                    "conversation_id": None
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                expansion = data.get("knowledge_expansion", {})

                if expansion:
                    print(f"  ✅ Expanded terms: {expansion.get('expanded_terms', [])}")
                    print(f"  ✅ Filters: {expansion.get('filters', {})}")
                    print(f"  ✅ Reasoning: {expansion.get('reasoning', '')}")
                else:
                    print(f"  ⚠️ No knowledge expansion occurred")

        except Exception as e:
            print(f"  ❌ Error: {e}")


def test_ambiguity_detection():
    """Test ambiguity detection"""
    print("\n" + "="*60)
    print("TESTING: Ambiguity Detection")
    print("="*60)

    ambiguous_queries = [
        "Nhà ở Quận 2",  # Location too broad + property type missing
        "5 tỷ",  # Property type missing
        "Tìm nhà đẹp",  # Vague aesthetic
        "Nhà giá tốt"  # Price unclear
    ]

    for query in ambiguous_queries:
        print(f"\nQuery: '{query}'")

        try:
            response = requests.post(
                "http://localhost:8090/orchestrate/v2",
                json={
                    "user_id": "test_ambiguity",
                    "query": query,
                    "conversation_id": None
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                needs_clarification = data.get("needs_clarification", False)
                ambiguity_result = data.get("ambiguity_result", {})

                if needs_clarification:
                    clarifications = ambiguity_result.get("clarifications", [])
                    print(f"  ✅ Ambiguity detected: {len(clarifications)} questions")
                    for i, clarif in enumerate(clarifications, 1):
                        print(f"     {i}. {clarif.get('question', '')}")
                else:
                    print(f"  ⚠️ No ambiguity detected (should have been flagged)")

        except Exception as e:
            print(f"  ❌ Error: {e}")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║         QUICK TEST SUITE - REE AI ORCHESTRATOR v2             ║
╚════════════════════════════════════════════════════════════════╝
""")

    # Run all tests
    results, bugs = test_orchestrate_v2()
    test_knowledge_expansion()
    test_ambiguity_detection()

    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)

    if bugs:
        print(f"\n⚠️ {len(bugs)} bugs found. Review above for details.")
    else:
        print("\n✅ No critical bugs detected!")

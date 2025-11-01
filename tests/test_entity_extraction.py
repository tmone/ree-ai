#!/usr/bin/env python3
"""Test entity extraction and structured filtering in Orchestrator"""
import httpx
import json

def test_orchestrator_with_entity_extraction():
    """Test that Orchestrator now extracts entities before calling DB Gateway"""

    print("="*80)
    print("Testing Architectural Fix: Entity Extraction Before DB Gateway")
    print("="*80)

    # Test query with clear entities
    test_query = "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ"
    print(f"\n📝 Test Query: {test_query}")
    print("\nExpected entities:")
    print("  - property_type: 'căn hộ'")
    print("  - bedrooms: 2")
    print("  - region: 'quận 7'")
    print("  - max_price: 3000000000 (3 tỷ)")

    # Call Orchestrator
    try:
        response = httpx.post(
            "http://localhost:8090/orchestrate",
            json={
                "user_id": "test_user",
                "query": test_query
            },
            timeout=60.0
        )

        print(f"\n✅ Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n🎯 Intent: {data.get('intent')}")
            print(f"🔍 Confidence: {data.get('confidence')}")
            print(f"⚙️  Service Used: {data.get('service_used')}")
            print(f"⏱️  Execution Time: {data.get('execution_time_ms'):.2f}ms")

            if 'metadata' in data:
                print(f"\n📊 Metadata:")
                print(json.dumps(data['metadata'], indent=2, ensure_ascii=False))

            print(f"\n💬 Response:")
            print(data.get('response', 'No response'))
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Error calling Orchestrator: {e}")

    print("\n" + "="*80)
    print("Now check Orchestrator logs for entity extraction:")
    print("docker-compose logs orchestrator --tail=50 | grep 'Extracted search filters'")
    print("="*80)

if __name__ == "__main__":
    test_orchestrator_with_entity_extraction()

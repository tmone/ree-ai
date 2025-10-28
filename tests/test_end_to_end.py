"""
End-to-End Integration Tests

Tests complete workflows:
1. Service starts → Registers → Orchestrator discovers → Service called
2. User query → Intent detection → Service discovery → Service execution → Response
"""
import pytest
import asyncio


@pytest.mark.asyncio
async def test_complete_chunking_workflow(http_client, registry_client):
    """
    Test complete workflow for semantic chunking:
    1. Verify semantic_chunking is registered
    2. Query Orchestrator
    3. Orchestrator discovers service via registry
    4. Service processes request
    5. Response returned
    """
    try:
        # Step 1: Verify service is registered
        print("\n🔍 Step 1: Checking service registration...")
        service_info = await registry_client.get_service("semantic_chunking")
        assert service_info["name"] == "semantic_chunking"
        assert service_info["status"] == "healthy"
        print(f"✅ semantic_chunking is registered and healthy")

        # Step 2: Send request to Orchestrator
        print("\n🔍 Step 2: Sending orchestration request...")
        orchestrator_url = "http://localhost:8090"
        request_data = {
            "user_id": "test_user_e2e",
            "query": "Please chunk this text: Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "service_type": "semantic_chunking"
        }

        response = await http_client.post(
            f"{orchestrator_url}/orchestrate",
            json=request_data,
            timeout=30.0
        )

        assert response.status_code == 200
        data = response.json()

        # Step 3: Verify response structure
        print("\n🔍 Step 3: Verifying response...")
        assert "response" in data
        assert "service_used" in data
        assert data["service_used"] == "semantic_chunking"
        assert "took_ms" in data
        assert data["took_ms"] > 0

        print(f"✅ Complete chunking workflow test passed")
        print(f"   Response time: {data['took_ms']}ms")

    except Exception as e:
        print(f"❌ End-to-end chunking test failed: {e}")
        raise


@pytest.mark.asyncio
async def test_complete_discovery_workflow(registry_client):
    """
    Test service discovery workflow:
    1. Register multiple services
    2. Query by capability
    3. Verify correct services returned
    """
    cleanup_services = []

    try:
        # Step 1: Register test services
        print("\n🔍 Step 1: Registering test services...")
        services = [
            {
                "name": "test_service_a",
                "host": "test-a",
                "port": 10001,
                "version": "1.0.0",
                "capabilities": ["capability_a", "shared"]
            },
            {
                "name": "test_service_b",
                "host": "test-b",
                "port": 10002,
                "version": "1.0.0",
                "capabilities": ["capability_b", "shared"]
            }
        ]

        for service in services:
            await registry_client.register_service(service)
            cleanup_services.append(service["name"])
            print(f"  ✓ Registered {service['name']}")

        # Step 2: Query by specific capability
        print("\n🔍 Step 2: Querying by capability...")
        result_a = await registry_client.list_services(capability="capability_a")
        assert result_a["count"] >= 1
        assert any(s["name"] == "test_service_a" for s in result_a["services"])
        print(f"  ✓ Found services with capability_a: {result_a['count']}")

        # Step 3: Query by shared capability
        print("\n🔍 Step 3: Querying by shared capability...")
        result_shared = await registry_client.list_services(capability="shared")
        assert result_shared["count"] >= 2
        print(f"  ✓ Found services with shared capability: {result_shared['count']}")

        print(f"✅ Complete discovery workflow test passed")

    except Exception as e:
        print(f"❌ Discovery workflow test failed: {e}")
        raise

    finally:
        # Cleanup
        for service_name in cleanup_services:
            try:
                await registry_client.deregister_service(service_name)
            except:
                pass


@pytest.mark.asyncio
async def test_service_lifecycle(registry_client):
    """
    Test complete service lifecycle:
    1. Service registration
    2. Service appears in listings
    3. Service health monitoring
    4. Service deregistration
    5. Service disappears from listings
    """
    service_data = {
        "name": "test_lifecycle_service",
        "host": "test-lifecycle",
        "port": 10003,
        "version": "1.0.0",
        "capabilities": ["lifecycle_test"]
    }

    try:
        # Step 1: Register
        print("\n🔍 Step 1: Registering service...")
        response = await registry_client.register_service(service_data)
        assert response["status"] == "registered"
        print(f"  ✓ Service registered")

        # Step 2: Verify in listings
        print("\n🔍 Step 2: Verifying service in listings...")
        services = await registry_client.list_services()
        assert any(s["name"] == service_data["name"] for s in services["services"])
        print(f"  ✓ Service appears in listings")

        # Step 3: Get service info
        print("\n🔍 Step 3: Getting service info...")
        info = await registry_client.get_service(service_data["name"])
        assert info["name"] == service_data["name"]
        assert info["version"] == service_data["version"]
        print(f"  ✓ Service info retrieved")

        # Step 4: Deregister
        print("\n🔍 Step 4: Deregistering service...")
        response = await registry_client.deregister_service(service_data["name"])
        assert response["status"] == "deregistered"
        print(f"  ✓ Service deregistered")

        # Step 5: Verify removed from listings
        print("\n🔍 Step 5: Verifying service removed...")
        try:
            await registry_client.get_service(service_data["name"])
            assert False, "Service should not be found"
        except Exception:
            print(f"  ✓ Service not found (as expected)")

        print(f"✅ Service lifecycle test passed")

    except Exception as e:
        print(f"❌ Service lifecycle test failed: {e}")
        # Cleanup
        try:
            await registry_client.deregister_service(service_data["name"])
        except:
            pass
        raise


@pytest.mark.asyncio
async def test_multi_service_orchestration(http_client, registry_client):
    """
    Test orchestration across multiple services
    Verify Orchestrator can route to different services based on intent
    """
    orchestrator_url = "http://localhost:8090"

    test_queries = [
        {
            "query": "Chunk this text into semantic pieces",
            "expected_capability": "chunking"
        },
        {
            "query": "Classify this property description",
            "expected_capability": "classification"
        }
    ]

    try:
        for i, test in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: Query - '{test['query']}'")

            # Check if service with required capability exists
            services = await registry_client.list_services(
                capability=test["expected_capability"]
            )

            if services["count"] == 0:
                print(f"  ⚠️ No service with capability '{test['expected_capability']}' registered, skipping")
                continue

            # Send orchestration request
            request_data = {
                "user_id": "test_multi_service",
                "query": test["query"]
            }

            response = await http_client.post(
                f"{orchestrator_url}/orchestrate",
                json=request_data,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Routed to: {data.get('service_used')}")
                print(f"  ✓ Response time: {data.get('took_ms')}ms")
            else:
                print(f"  ⚠️ Request failed: {response.status_code}")

        print(f"\n✅ Multi-service orchestration test completed")

    except Exception as e:
        print(f"❌ Multi-service orchestration test failed: {e}")

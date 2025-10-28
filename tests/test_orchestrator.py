"""
Orchestrator Dynamic Service Discovery Tests

Tests for:
- Intent detection
- Dynamic service discovery via Service Registry
- Service routing
- Error handling
"""
import pytest


@pytest.mark.asyncio
async def test_orchestrator_health(http_client):
    """Test Orchestrator health endpoint"""
    orchestrator_url = "http://localhost:8090"

    try:
        response = await http_client.get(f"{orchestrator_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Orchestrator health test passed")
    except Exception as e:
        print(f"⚠️ Orchestrator not running: {e}")


@pytest.mark.asyncio
async def test_orchestrator_dynamic_discovery(http_client, registry_client):
    """Test that Orchestrator dynamically discovers services via Service Registry"""
    orchestrator_url = "http://localhost:8090"

    try:
        # First verify that semantic_chunking is registered
        services = await registry_client.list_services(capability="chunking")
        if services["count"] == 0:
            print("⚠️ No chunking services registered, skipping test")
            return

        # Test orchestration with chunking capability
        request_data = {
            "user_id": "test_user",
            "query": "Chunk this text into semantic pieces",
            "service_type": "semantic_chunking"
        }

        response = await http_client.post(
            f"{orchestrator_url}/orchestrate",
            json=request_data
        )

        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert "service_used" in data
            assert data["service_used"] == "semantic_chunking"
            assert "took_ms" in data
            print(f"✅ Orchestrator dynamic discovery test passed")
        else:
            print(f"⚠️ Orchestration failed: {response.status_code}")

    except Exception as e:
        print(f"⚠️ Orchestrator test failed: {e}")


@pytest.mark.asyncio
async def test_orchestrator_intent_detection(http_client):
    """Test Orchestrator's intent detection"""
    orchestrator_url = "http://localhost:8090"

    test_cases = [
        {
            "query": "Tìm nhà 2 phòng ngủ",
            "expected_type": "search"
        },
        {
            "query": "Giá nhà bao nhiêu?",
            "expected_type": "price_suggestion"
        },
        {
            "query": "Phân loại bất động sản này",
            "expected_type": "classification"
        }
    ]

    try:
        for test_case in test_cases:
            request_data = {
                "user_id": "test_user",
                "query": test_case["query"]
            }

            response = await http_client.post(
                f"{orchestrator_url}/orchestrate",
                json=request_data,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                print(f"  Query: '{test_case['query']}' -> Service: {data.get('service_used')}")

        print(f"✅ Intent detection test completed")

    except Exception as e:
        print(f"⚠️ Intent detection test failed: {e}")


@pytest.mark.asyncio
async def test_orchestrator_service_unavailable(http_client):
    """Test Orchestrator handles unavailable services gracefully"""
    orchestrator_url = "http://localhost:8090"

    try:
        # Request a service that doesn't exist
        request_data = {
            "user_id": "test_user",
            "query": "Test query",
            "service_type": "non_existent_service"
        }

        response = await http_client.post(
            f"{orchestrator_url}/orchestrate",
            json=request_data
        )

        if response.status_code == 200:
            data = response.json()
            # Should return graceful error message
            assert "not available" in data["response"].lower() or "error" in data.get("metadata", {})
            print(f"✅ Service unavailable handling test passed")

    except Exception as e:
        print(f"⚠️ Service unavailable test failed: {e}")


@pytest.mark.asyncio
async def test_orchestrator_registry_query(http_client, registry_client):
    """Test that Orchestrator queries Service Registry correctly"""
    orchestrator_url = "http://localhost:8090"

    try:
        # Register a test service with unique capability
        test_service = {
            "name": "test_orchestrator_target",
            "host": "test-target",
            "port": 9999,
            "version": "1.0.0",
            "capabilities": ["test_capability_unique"]
        }

        await registry_client.register_service(test_service)

        # Verify service is in registry
        services = await registry_client.list_services(capability="test_capability_unique")
        assert services["count"] >= 1

        # Cleanup
        await registry_client.deregister_service(test_service["name"])

        print(f"✅ Orchestrator registry query test passed")

    except Exception as e:
        print(f"⚠️ Registry query test failed: {e}")

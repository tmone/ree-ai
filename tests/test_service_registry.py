"""
Service Registry Integration Tests

Tests for:
- Service registration
- Service deregistration
- Service discovery
- Health monitoring
- Stats tracking
"""
import pytest
import asyncio


@pytest.mark.asyncio
async def test_service_registry_health(wait_for_service_registry, registry_client):
    """Test that Service Registry is healthy"""
    response = await registry_client.health_check()

    assert response["status"] == "healthy"
    print(f"✅ Service Registry health check passed")


@pytest.mark.asyncio
async def test_register_service(registry_client, sample_service_data, cleanup_test_services):
    """Test service registration"""
    # Register service
    response = await registry_client.register_service(sample_service_data)
    cleanup_test_services.append(sample_service_data["name"])

    assert response["status"] == "registered"
    assert response["service"]["name"] == sample_service_data["name"]

    # Verify service is in registry
    service_info = await registry_client.get_service(sample_service_data["name"])
    assert service_info["name"] == sample_service_data["name"]
    assert service_info["version"] == sample_service_data["version"]
    assert set(service_info["capabilities"]) == set(sample_service_data["capabilities"])

    print(f"✅ Service registration test passed")


@pytest.mark.asyncio
async def test_deregister_service(registry_client, sample_service_data, cleanup_test_services):
    """Test service deregistration"""
    # Register service
    await registry_client.register_service(sample_service_data)
    cleanup_test_services.append(sample_service_data["name"])

    # Deregister service
    response = await registry_client.deregister_service(sample_service_data["name"])
    assert response["status"] == "deregistered"

    # Verify service is removed
    try:
        await registry_client.get_service(sample_service_data["name"])
        assert False, "Service should not be found"
    except Exception as e:
        assert "404" in str(e) or "not found" in str(e).lower()

    print(f"✅ Service deregistration test passed")


@pytest.mark.asyncio
async def test_list_services(registry_client, cleanup_test_services):
    """Test listing services"""
    # Register multiple test services
    services = [
        {
            "name": "test_chunking",
            "host": "test-chunking",
            "port": 8081,
            "version": "1.0.0",
            "capabilities": ["chunking", "text_processing"]
        },
        {
            "name": "test_classification",
            "host": "test-classification",
            "port": 8082,
            "version": "1.0.0",
            "capabilities": ["classification", "text_processing"]
        }
    ]

    for service_data in services:
        await registry_client.register_service(service_data)
        cleanup_test_services.append(service_data["name"])

    # List all services
    response = await registry_client.list_services()
    assert response["count"] >= 2
    service_names = [s["name"] for s in response["services"]]
    assert "test_chunking" in service_names
    assert "test_classification" in service_names

    # Filter by capability
    response = await registry_client.list_services(capability="chunking")
    assert response["count"] >= 1
    assert any(s["name"] == "test_chunking" for s in response["services"])

    print(f"✅ List services test passed")


@pytest.mark.asyncio
async def test_service_capabilities_filter(registry_client, cleanup_test_services):
    """Test filtering services by capabilities"""
    # Register services with different capabilities
    services = [
        {
            "name": "test_rag",
            "host": "test-rag",
            "port": 8091,
            "version": "1.0.0",
            "capabilities": ["rag", "search"]
        },
        {
            "name": "test_embedding",
            "host": "test-embedding",
            "port": 8092,
            "version": "1.0.0",
            "capabilities": ["embedding", "vector"]
        }
    ]

    for service_data in services:
        await registry_client.register_service(service_data)
        cleanup_test_services.append(service_data["name"])

    # Filter by 'rag' capability
    response = await registry_client.list_services(capability="rag")
    assert response["count"] >= 1
    assert any(s["name"] == "test_rag" for s in response["services"])

    # Filter by 'embedding' capability
    response = await registry_client.list_services(capability="embedding")
    assert response["count"] >= 1
    assert any(s["name"] == "test_embedding" for s in response["services"])

    print(f"✅ Capability filtering test passed")


@pytest.mark.asyncio
async def test_registry_stats(registry_client, sample_service_data, cleanup_test_services):
    """Test registry statistics"""
    # Get initial stats
    initial_stats = await registry_client.get_stats()
    initial_count = initial_stats["total_services"]

    # Register a service
    await registry_client.register_service(sample_service_data)
    cleanup_test_services.append(sample_service_data["name"])

    # Check stats increased
    new_stats = await registry_client.get_stats()
    assert new_stats["total_services"] >= initial_count + 1

    print(f"✅ Registry stats test passed")


@pytest.mark.asyncio
async def test_duplicate_registration(registry_client, sample_service_data, cleanup_test_services):
    """Test that re-registering the same service updates it"""
    # Register service
    await registry_client.register_service(sample_service_data)
    cleanup_test_services.append(sample_service_data["name"])

    # Re-register with updated data
    updated_data = sample_service_data.copy()
    updated_data["version"] = "2.0.0"

    response = await registry_client.register_service(updated_data)
    assert response["status"] == "registered"

    # Verify version was updated
    service_info = await registry_client.get_service(sample_service_data["name"])
    assert service_info["version"] == "2.0.0"

    print(f"✅ Duplicate registration test passed")


@pytest.mark.asyncio
async def test_service_url_format(registry_client, sample_service_data, cleanup_test_services):
    """Test that service URL is correctly formatted"""
    await registry_client.register_service(sample_service_data)
    cleanup_test_services.append(sample_service_data["name"])

    service_info = await registry_client.get_service(sample_service_data["name"])

    # URL should be http://host:port
    expected_url = f"http://{sample_service_data['host']}:{sample_service_data['port']}"
    assert service_info["url"] == expected_url

    print(f"✅ Service URL format test passed")

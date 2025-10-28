"""
Pytest Configuration and Fixtures
Shared test utilities and fixtures
"""
import pytest
import httpx
import asyncio
import time
from typing import Generator, AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def service_registry_url() -> str:
    """Service Registry URL"""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
async def wait_for_service_registry(service_registry_url: str):
    """Wait for Service Registry to be healthy"""
    max_retries = 30
    retry_delay = 2

    async with httpx.AsyncClient() as client:
        for i in range(max_retries):
            try:
                response = await client.get(f"{service_registry_url}/health", timeout=5.0)
                if response.status_code == 200:
                    print(f"\n✅ Service Registry is healthy")
                    return True
            except Exception as e:
                if i < max_retries - 1:
                    print(f"⏳ Waiting for Service Registry... ({i+1}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                else:
                    raise Exception(f"Service Registry failed to start: {e}")

    raise Exception("Service Registry failed to start")


@pytest.fixture
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for tests"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
async def registry_client(service_registry_url: str, http_client: httpx.AsyncClient):
    """Client specifically for Service Registry operations"""

    class RegistryClient:
        def __init__(self, base_url: str, client: httpx.AsyncClient):
            self.base_url = base_url
            self.client = client

        async def register_service(self, service_data: dict) -> dict:
            """Register a service"""
            response = await self.client.post(
                f"{self.base_url}/register",
                json=service_data
            )
            response.raise_for_status()
            return response.json()

        async def deregister_service(self, service_name: str) -> dict:
            """Deregister a service"""
            response = await self.client.post(
                f"{self.base_url}/deregister",
                json={"name": service_name}
            )
            response.raise_for_status()
            return response.json()

        async def get_service(self, service_name: str) -> dict:
            """Get service info"""
            response = await self.client.get(f"{self.base_url}/services/{service_name}")
            response.raise_for_status()
            return response.json()

        async def list_services(self, capability: str = None, status: str = None) -> dict:
            """List services with optional filters"""
            params = {}
            if capability:
                params["capability"] = capability
            if status:
                params["status"] = status

            response = await self.client.get(
                f"{self.base_url}/services",
                params=params
            )
            response.raise_for_status()
            return response.json()

        async def get_stats(self) -> dict:
            """Get registry stats"""
            response = await self.client.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()

        async def health_check(self) -> dict:
            """Check registry health"""
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    return RegistryClient(service_registry_url, http_client)


@pytest.fixture
def sample_service_data() -> dict:
    """Sample service registration data"""
    return {
        "name": "test_service",
        "host": "test-service",
        "port": 8080,
        "version": "1.0.0",
        "capabilities": ["testing", "sample"],
        "metadata": {"test": True}
    }


@pytest.fixture
async def cleanup_test_services(registry_client):
    """Cleanup test services after each test"""
    test_service_names = []

    yield test_service_names

    # Cleanup
    for service_name in test_service_names:
        try:
            await registry_client.deregister_service(service_name)
            print(f"🧹 Cleaned up test service: {service_name}")
        except Exception as e:
            print(f"⚠️ Failed to cleanup {service_name}: {e}")


def wait_for_condition(condition_fn, timeout: int = 10, interval: float = 0.5) -> bool:
    """Wait for a condition to become true"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if condition_fn():
            return True
        time.sleep(interval)
    return False

"""
Pytest configuration and shared fixtures for REE AI Platform tests.
"""
import asyncio
import os
from typing import AsyncGenerator, Dict, Any

import pytest
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Service URLs
CORE_GATEWAY_URL = os.getenv("CORE_GATEWAY_URL", "http://localhost:8080")
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8090")
SERVICE_REGISTRY_URL = os.getenv("SERVICE_REGISTRY_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Provide a shared HTTP client for all tests."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
async def core_gateway_client(http_client: httpx.AsyncClient):
    """HTTP client pre-configured for Core Gateway."""
    class CoreGatewayClient:
        def __init__(self, client: httpx.AsyncClient):
            self.client = client
            self.base_url = CORE_GATEWAY_URL

        async def health_check(self):
            response = await self.client.get(f"{self.base_url}/health")
            return response.json()

        async def chat_completion(self, model: str, messages: list, **kwargs):
            payload = {
                "model": model,
                "messages": messages,
                **kwargs
            }
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            return response

        async def create_embedding(self, text: str, model: str = "text-embedding-ada-002"):
            payload = {
                "input": text,
                "model": model
            }
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                json=payload
            )
            return response

    return CoreGatewayClient(http_client)


@pytest.fixture
async def orchestrator_client(http_client: httpx.AsyncClient):
    """HTTP client pre-configured for Orchestrator."""
    class OrchestratorClient:
        def __init__(self, client: httpx.AsyncClient):
            self.client = client
            self.base_url = ORCHESTRATOR_URL

        async def health_check(self):
            response = await self.client.get(f"{self.base_url}/health")
            return response.json()

        async def chat_completion(self, model: str, messages: list, **kwargs):
            payload = {
                "model": model,
                "messages": messages,
                **kwargs
            }
            response = await self.client.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload
            )
            return response

    return OrchestratorClient(http_client)


@pytest.fixture
def sample_messages() -> Dict[str, list]:
    """Provide sample message sets for testing."""
    return {
        "simple": [
            {"role": "user", "content": "Hello"}
        ],
        "math": [
            {"role": "user", "content": "What is 2+2?"}
        ],
        "context": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain AI in one sentence."}
        ],
        "multi_turn": [
            {"role": "user", "content": "What is Python?"},
            {"role": "assistant", "content": "Python is a programming language."},
            {"role": "user", "content": "What is it used for?"}
        ],
        "long": [
            {"role": "user", "content": "Explain machine learning " * 50}
        ]
    }


@pytest.fixture
def ai_test_cases():
    """Provide AI-specific test cases with expected behaviors."""
    return [
        {
            "name": "Basic Math",
            "messages": [{"role": "user", "content": "Calculate 15 + 27"}],
            "expected_keywords": ["42", "forty", "sum"],
            "max_tokens": 50
        },
        {
            "name": "Factual Question",
            "messages": [{"role": "user", "content": "What is the capital of France?"}],
            "expected_keywords": ["Paris"],
            "max_tokens": 50
        },
        {
            "name": "Creative Task",
            "messages": [{"role": "user", "content": "Write a haiku about AI"}],
            "expected_keywords": ["AI", "machine", "code", "silicon"],
            "min_words": 10,
            "max_tokens": 100
        },
        {
            "name": "Reasoning",
            "messages": [{"role": "user", "content": "If all A are B, and all B are C, then are all A also C?"}],
            "expected_keywords": ["yes", "correct", "true", "syllogism"],
            "max_tokens": 100
        },
        {
            "name": "Code Generation",
            "messages": [{"role": "user", "content": "Write a Python function to reverse a string"}],
            "expected_keywords": ["def", "return", "[::-1]", "reverse"],
            "max_tokens": 200
        }
    ]


@pytest.fixture
def failover_scenarios():
    """Provide scenarios for testing failover mechanism."""
    return [
        {
            "name": "Rate Limit Trigger",
            "description": "Trigger OpenAI rate limit to test failover",
            "model": "gpt-4o-mini",
            "expected_fallback": "ollama",
            "verify_id_prefix": "ollama-"
        },
        {
            "name": "Direct Ollama",
            "description": "Direct call to Ollama without failover",
            "model": "ollama/llama2",
            "expected_fallback": None,
            "verify_id_prefix": "ollama-"
        }
    ]


@pytest.fixture(autouse=True)
async def check_services_running(http_client: httpx.AsyncClient):
    """Auto-fixture to ensure services are running before each test."""
    services = {
        "Core Gateway": CORE_GATEWAY_URL,
        "Orchestrator": ORCHESTRATOR_URL,
        "Service Registry": SERVICE_REGISTRY_URL
    }

    for name, url in services.items():
        try:
            response = await http_client.get(f"{url}/health", timeout=5.0)
            if response.status_code != 200:
                pytest.skip(f"{name} is not healthy (status: {response.status_code})")
        except Exception as e:
            pytest.skip(f"{name} is not accessible: {e}")


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o-mini",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a test response."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "total_tokens": 20
        }
    }


@pytest.fixture
def performance_config():
    """Configuration for performance tests."""
    return {
        "concurrent_users": 10,
        "requests_per_user": 5,
        "timeout": 30,
        "acceptable_failure_rate": 0.05,  # 5%
        "max_response_time": 5.0,  # seconds
        "p95_response_time": 2.0   # 95th percentile
    }


# Hooks for pytest
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers",
        "requires_openai: mark test as requiring OpenAI API key"
    )
    config.addinivalue_line(
        "markers",
        "requires_ollama: mark test as requiring Ollama service"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add 'ai' marker to all tests in test_ai_*.py files
        if "test_ai_" in item.nodeid:
            item.add_marker(pytest.mark.ai)

        # Add 'failover' marker to failover tests
        if "failover" in item.nodeid.lower():
            item.add_marker(pytest.mark.failover)

        # Add 'performance' marker to performance tests
        if "performance" in item.nodeid.lower() or "load" in item.nodeid.lower():
            item.add_marker(pytest.mark.performance)

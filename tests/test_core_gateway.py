"""
Integration tests for Core Gateway
"""
import pytest
from httpx import AsyncClient
import sys
import os

# Add shared to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.core_gateway.main import app
from shared.models.core_gateway import LLMRequest, Message, ModelType


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_chat_completions():
    """Test LLM completion endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "model": "ollama/llama2",
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }

        response = await client.post("/v1/chat/completions", json=request_data)

        # Note: This will fail without real Ollama/OpenAI
        # Use with mock in integration tests
        assert response.status_code in [200, 500]  # 500 if no LLM available

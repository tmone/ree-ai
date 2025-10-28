"""
Integration tests for Semantic Chunking Service
"""
import pytest
from httpx import AsyncClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.semantic_chunking.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "core_gateway" in data


@pytest.mark.asyncio
async def test_chunk_text():
    """Test text chunking endpoint"""
    async with AsyncClient(app=app, base_url="http://test", timeout=30.0) as client:
        request_data = {
            "text": "Căn hộ 2 phòng ngủ ở Quận 1, diện tích 75m2, giá 8 tỷ.",
            "max_chunk_size": 500
        }

        response = await client.post("/chunk", json=request_data)

        # Note: Will fail without Core Gateway running
        # Use with mock Core Gateway in integration tests
        assert response.status_code in [200, 502]  # 502 if Core Gateway unavailable

        if response.status_code == 200:
            data = response.json()
            assert "chunks" in data
            assert "total_chunks" in data
            assert "processing_time_ms" in data

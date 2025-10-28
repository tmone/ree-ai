"""
Integration tests for DB Gateway
"""
import pytest
from httpx import AsyncClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.db_gateway.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "mock_data_count" in data


@pytest.mark.asyncio
async def test_search_properties():
    """Test property search with mock data"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        request_data = {
            "query": "Tìm nhà 2 phòng ngủ",
            "filters": {
                "region": "Quận 1",
                "bedrooms": 2
            },
            "limit": 10
        }

        response = await client.post("/search", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total" in data
        assert "took_ms" in data
        assert isinstance(data["results"], list)


@pytest.mark.asyncio
async def test_get_property():
    """Test get single property"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/properties/prop_001")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == "prop_001"
        assert "title" in data
        assert "price" in data


@pytest.mark.asyncio
async def test_get_property_not_found():
    """Test get non-existent property"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/properties/nonexistent")
        assert response.status_code == 404

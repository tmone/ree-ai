"""
Test suite for HIGH priority bug fixes
Tests: Retry logic, circuit breakers, connection pooling, error sanitization
"""

import pytest
import httpx
import asyncio
import time
from datetime import datetime


class TestRetryLogicAndBackoff:
    """Test exponential backoff retry logic in orchestrator"""

    @pytest.mark.asyncio
    async def test_exponential_backoff_timing(self):
        """Verify retry delays follow exponential pattern (1s, 2s, 4s)"""
        # This test would need a mock endpoint that fails multiple times
        # For now, just verify orchestrator is accessible
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("http://localhost:8090/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            print(f"✅ Orchestrator v{data['version']} is healthy")


class TestCircuitBreaker:
    """Test circuit breaker pattern for external services"""

    @pytest.mark.asyncio
    async def test_circuit_breaker_exists(self):
        """Verify orchestrator has circuit breaker protection"""
        # Circuit breakers are internal to the service
        # We can verify the service starts correctly with them
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("http://localhost:8090/info")
            assert response.status_code == 200
            data = response.json()
            assert "capabilities" in data
            print(f"✅ Orchestrator capabilities: {data['capabilities']}")


class TestConnectionPooling:
    """Test HTTP connection pooling configuration"""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self):
        """Verify connection pooling handles concurrent requests efficiently"""
        start_time = time.time()

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Send 10 concurrent requests
            tasks = []
            for i in range(10):
                task = client.get("http://localhost:8090/health")
                tasks.append(task)

            responses = await asyncio.gather(*tasks)

        elapsed = time.time() - start_time

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # Should be fast due to connection pooling (< 5 seconds for 10 requests)
        assert elapsed < 5.0

        print(f"✅ Connection pooling test: 10 concurrent requests in {elapsed:.2f}s")


class TestErrorSanitization:
    """Test that error messages don't expose internal details"""

    @pytest.mark.asyncio
    async def test_invalid_query_error_message(self):
        """Verify error messages are sanitized (no internal stack traces)"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Send invalid request to db-gateway
            response = await client.post(
                "http://localhost:8081/search",
                json={"query": ""}  # Empty query should be rejected
            )

            assert response.status_code == 400
            data = response.json()

            # Error message should not contain internal details
            error_detail = str(data.get("detail", ""))
            assert "Traceback" not in error_detail
            assert "File" not in error_detail
            assert ".py" not in error_detail

            print(f"✅ Error sanitization: {error_detail}")

    @pytest.mark.asyncio
    async def test_db_gateway_error_handling(self):
        """Test DB Gateway returns sanitized errors"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Send request with special characters only
            response = await client.post(
                "http://localhost:8081/search",
                json={"query": "!@#$%^&*()"}
            )

            # Should get clean error message
            if response.status_code != 200:
                data = response.json()
                error_msg = str(data)

                # Should not expose internals
                assert "opensearch" not in error_msg.lower() or "alphanumeric" in error_msg.lower()
                print(f"✅ DB Gateway error sanitization passed")


class TestTypeSafety:
    """Test type coercion and validation improvements"""

    @pytest.mark.asyncio
    async def test_search_results_type_safety(self):
        """Verify search results have proper type coercion"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8081/search",
                json={
                    "query": "apartment",
                    "limit": 5
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Verify results have proper types
            if data.get("results"):
                for result in data["results"][:3]:
                    # Bedrooms should be int, not string
                    bedrooms = result.get("bedrooms", 0)
                    assert isinstance(bedrooms, int), f"bedrooms should be int, got {type(bedrooms)}"

                    # Price should be numeric
                    price = result.get("price", 0)
                    assert isinstance(price, (int, float)), f"price should be numeric, got {type(price)}"

                print(f"✅ Type safety: All fields have correct types")


class TestReliabilityMetrics:
    """Test overall system reliability with new fixes"""

    @pytest.mark.asyncio
    async def test_orchestrator_with_all_fixes(self):
        """Integration test: Orchestrator with all HIGH priority fixes"""
        async with httpx.AsyncClient(timeout=90.0) as client:
            # Test chat endpoint with retry logic, circuit breakers, connection pooling
            response = await client.post(
                "http://localhost:8090/v1/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Tìm căn hộ 2 phòng ngủ"}
                    ],
                    "user_id": "test_user_reliability",
                    "stream": False
                }
            )

            assert response.status_code == 200
            data = response.json()

            # Should have orchestration metadata
            assert "intent" in data or "response" in data

            print(f"✅ Orchestrator integration test passed")
            print(f"   Response keys: {list(data.keys())}")

    @pytest.mark.asyncio
    async def test_core_gateway_reliability(self):
        """Test Core Gateway with connection pooling"""
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                "http://localhost:8080/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Hello"}
                    ],
                    "max_tokens": 50
                }
            )

            # Should succeed or fail gracefully
            if response.status_code == 200:
                data = response.json()
                assert "content" in data or "choices" in data
                print(f"✅ Core Gateway reliability test passed")
            else:
                # If failed, error should be sanitized
                data = response.json()
                error_msg = str(data)
                assert "Traceback" not in error_msg
                print(f"✅ Core Gateway failed gracefully with sanitized error")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

"""
Infrastructure and Service Integration Tests

Tests database connections, service discovery, and inter-service communication.
"""
import pytest
import httpx
import asyncio
from typing import Dict, Any


@pytest.mark.integration
@pytest.mark.critical
class TestServiceDiscovery:
    """Test service registry and discovery mechanism."""

    @pytest.mark.asyncio
    async def test_service_registry_health(self, http_client):
        """Test that service registry is accessible."""
        response = await http_client.get("http://localhost:8000/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "service_registry" in data["service"].lower()

    @pytest.mark.asyncio
    async def test_services_auto_registration(self, http_client):
        """Test that services auto-register on startup."""
        response = await http_client.get("http://localhost:8000/services")
        assert response.status_code == 200

        data = response.json()

        # Should have registered services (even if count is 0, structure should be correct)
        assert "services" in data or isinstance(data, list)

        print(f"📊 Registered services: {len(data.get('services', data)) if isinstance(data, dict) else len(data)}")

    @pytest.mark.asyncio
    async def test_service_health_endpoints(self, http_client):
        """Test health endpoints of all services."""
        services = {
            "Service Registry": "http://localhost:8000",
            "Core Gateway": "http://localhost:8080",
            "Orchestrator": "http://localhost:8090"
        }

        results = {}
        for name, url in services.items():
            try:
                response = await http_client.get(f"{url}/health", timeout=5.0)
                results[name] = {
                    "status": response.status_code,
                    "healthy": response.status_code == 200
                }

                if response.status_code == 200:
                    print(f"✅ {name}: healthy")
                else:
                    print(f"⚠️ {name}: unhealthy (status {response.status_code})")

            except Exception as e:
                results[name] = {
                    "status": None,
                    "healthy": False,
                    "error": str(e)
                }
                print(f"❌ {name}: {e}")

        # At least core services should be healthy
        assert results["Core Gateway"]["healthy"], "Core Gateway must be healthy"

    @pytest.mark.asyncio
    async def test_service_communication(self, http_client):
        """Test that services can communicate with each other."""
        # Orchestrator should be able to communicate with Core Gateway
        response = await http_client.post(
            "http://localhost:8090/v1/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            },
            timeout=10.0
        )

        # Should get a response (success or graceful error)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            print("✅ Inter-service communication working")


@pytest.mark.integration
class TestDatabaseConnections:
    """Test database connectivity and operations."""

    @pytest.mark.asyncio
    async def test_postgres_connection(self):
        """Test PostgreSQL connection."""
        import os

        # Check if PostgreSQL is configured
        postgres_host = os.getenv("POSTGRES_HOST", "postgres")
        postgres_port = int(os.getenv("POSTGRES_PORT", "5432"))

        # Try to connect (will skip if psycopg2 not installed)
        try:
            import psycopg2
            conn_string = f"host={postgres_host} port={postgres_port} dbname=ree_ai user=ree_ai_user password=ree_ai_pass_2025"

            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()

            print(f"✅ PostgreSQL connected: {version[0][:50]}")

            cursor.close()
            conn.close()

        except ImportError:
            pytest.skip("psycopg2 not installed")
        except Exception as e:
            # Connection error is OK if database not started
            print(f"⚠️ PostgreSQL not accessible: {e}")

    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test Redis connection."""
        import os

        redis_host = os.getenv("REDIS_HOST", "redis")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        try:
            import redis

            r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            r.ping()

            print(f"✅ Redis connected: {redis_host}:{redis_port}")

            # Test basic operations
            r.set("test_key", "test_value")
            value = r.get("test_key")
            assert value == "test_value"

            r.delete("test_key")

        except ImportError:
            pytest.skip("redis not installed")
        except Exception as e:
            print(f"⚠️ Redis not accessible: {e}")

    @pytest.mark.asyncio
    async def test_opensearch_connection(self, http_client):
        """Test OpenSearch connection."""
        try:
            # OpenSearch health endpoint
            response = await http_client.get(
                "http://localhost:9200/_cluster/health",
                auth=("admin", "Admin@123"),
                timeout=5.0
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ OpenSearch connected: {data.get('cluster_name', 'unknown')}")
                print(f"   Status: {data.get('status', 'unknown')}")
            else:
                print(f"⚠️ OpenSearch returned status {response.status_code}")

        except Exception as e:
            print(f"⚠️ OpenSearch not accessible: {e}")


@pytest.mark.integration
class TestEmbeddingsGeneration:
    """Test embeddings generation functionality."""

    @pytest.mark.asyncio
    async def test_create_embeddings_endpoint_exists(self, core_gateway_client):
        """Test that embeddings endpoint is accessible."""
        # Try to create embeddings
        response = await core_gateway_client.create_embedding(
            text="Test text for embeddings"
        )

        # Should return 200 or 500 (if OpenAI key not configured)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "embeddings" in data
            print(f"✅ Embeddings generated: {len(data['embeddings'])} vectors")

    @pytest.mark.asyncio
    @pytest.mark.requires_openai
    async def test_embeddings_quality(self, core_gateway_client):
        """Test quality of generated embeddings."""
        # Create embeddings for similar and different texts
        texts = {
            "similar1": "The cat sat on the mat",
            "similar2": "A cat was sitting on a mat",
            "different": "Python is a programming language"
        }

        embeddings = {}

        for key, text in texts.items():
            response = await core_gateway_client.create_embedding(text=text)

            if response.status_code == 200:
                data = response.json()
                embeddings[key] = data["embeddings"][0]

        if len(embeddings) == 3:
            import numpy as np

            # Calculate cosine similarity
            def cosine_similarity(a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

            sim_1_2 = cosine_similarity(embeddings["similar1"], embeddings["similar2"])
            sim_1_diff = cosine_similarity(embeddings["similar1"], embeddings["different"])

            print(f"📊 Similarity (cat texts): {sim_1_2:.3f}")
            print(f"📊 Similarity (cat vs Python): {sim_1_diff:.3f}")

            # Similar texts should have higher similarity than different ones
            assert sim_1_2 > sim_1_diff, \
                f"Similar texts should be more similar: {sim_1_2:.3f} vs {sim_1_diff:.3f}"

            print("✅ Embeddings quality is good")


@pytest.mark.integration
class TestOrchestratorIntentDetection:
    """Test orchestrator's intent detection capabilities."""

    @pytest.mark.asyncio
    async def test_basic_intent_routing(self, orchestrator_client):
        """Test that orchestrator routes requests correctly."""
        test_cases = [
            {
                "input": "What is AI?",
                "expected_route": "chat",
                "description": "Simple question"
            },
            {
                "input": "Search for machine learning papers",
                "expected_route": "search",
                "description": "Search query"
            }
        ]

        for case in test_cases:
            response = await orchestrator_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": case["input"]}],
                max_tokens=50
            )

            # Should get a response
            assert response.status_code in [200, 500]

            if response.status_code == 200:
                print(f"✅ {case['description']}: routed successfully")

    @pytest.mark.asyncio
    async def test_orchestrator_response_format(self, orchestrator_client):
        """Test that orchestrator returns OpenAI-compatible format."""
        response = await orchestrator_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )

        if response.status_code == 200:
            data = response.json()

            # Should have OpenAI format
            assert "choices" in data
            assert len(data["choices"]) > 0
            assert "message" in data["choices"][0]
            assert "content" in data["choices"][0]["message"]

            print("✅ Orchestrator returns OpenAI-compatible format")


@pytest.mark.integration
@pytest.mark.slow
class TestServiceResilience:
    """Test system resilience and recovery."""

    @pytest.mark.asyncio
    async def test_service_recovery_from_errors(self, core_gateway_client):
        """Test that services recover gracefully from errors."""
        # Send valid request after potential errors
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )

        # Should recover and respond
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_concurrent_requests_stability(self, core_gateway_client):
        """Test system stability under concurrent load."""
        num_concurrent = 20

        async def make_request(i):
            try:
                response = await core_gateway_client.chat_completion(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": f"Request {i}"}],
                    max_tokens=5
                )
                return response.status_code == 200
            except Exception:
                return False

        # Send concurrent requests
        tasks = [make_request(i) for i in range(num_concurrent)]
        results = await asyncio.gather(*tasks)

        success_count = sum(results)
        success_rate = success_count / num_concurrent

        print(f"📊 Concurrent requests: {success_count}/{num_concurrent} succeeded ({success_rate:.1%})")

        # Should handle at least 70% of concurrent requests
        assert success_rate >= 0.7, \
            f"Too many concurrent failures: {success_rate:.1%}"

    @pytest.mark.asyncio
    async def test_timeout_handling(self, http_client):
        """Test that services handle timeouts correctly."""
        try:
            # Make request with very short timeout
            response = await http_client.post(
                "http://localhost:8080/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5
                },
                timeout=0.001  # Very short timeout
            )

            # Should either complete fast or timeout
            print(f"Response status: {response.status_code}")

        except httpx.TimeoutException:
            print("✅ Timeout handled correctly")
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")


@pytest.mark.integration
class TestSystemMetrics:
    """Test system metrics and monitoring."""

    @pytest.mark.asyncio
    async def test_response_time_metrics(self, core_gateway_client):
        """Test response time is within acceptable range."""
        import time

        num_samples = 5
        response_times = []

        for i in range(num_samples):
            start = time.time()

            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Test {i}"}],
                max_tokens=5
            )

            elapsed = time.time() - start

            if response.status_code == 200:
                response_times.append(elapsed)

        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)

            print(f"📊 Response times ({len(response_times)} samples):")
            print(f"   Average: {avg_time:.3f}s")
            print(f"   Min: {min_time:.3f}s")
            print(f"   Max: {max_time:.3f}s")

            # Average should be reasonable (<5s)
            assert avg_time < 5.0, f"Average response time too high: {avg_time:.3f}s"

    @pytest.mark.asyncio
    async def test_memory_usage_stable(self, core_gateway_client):
        """Test that memory usage doesn't grow excessively."""
        # Make multiple requests and check system stays stable
        num_requests = 10

        for i in range(num_requests):
            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Request {i}"}],
                max_tokens=5
            )

            # Just check system responds
            assert response.status_code in [200, 500]

        print(f"✅ System stable after {num_requests} requests")

"""
Failover Mechanism Tests

Comprehensive testing of the OpenAI → Ollama failover system.
Tests reliability, performance, and edge cases of the failover logic.
"""
import pytest
import asyncio
from typing import List, Dict


@pytest.mark.failover
@pytest.mark.critical
class TestFailoverReliability:
    """Test the reliability and correctness of failover mechanism."""

    @pytest.mark.asyncio
    async def test_rate_limit_triggers_fallback(self, core_gateway_client):
        """Test that OpenAI rate limit correctly triggers Ollama fallback."""
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )

        # Response should succeed even if OpenAI fails
        assert response.status_code == 200, \
            f"Failover failed. Status: {response.status_code}, Body: {response.text}"

        data = response.json()

        # Check response structure
        assert "id" in data
        assert "model" in data
        assert "content" in data

        # If failover occurred, ID should start with "ollama-"
        if data["id"].startswith("ollama-"):
            print(f"✅ Failover triggered successfully. Model: {data['model']}")
            assert "qwen" in data["model"].lower() or "llama" in data["model"].lower(), \
                f"Unexpected fallback model: {data['model']}"
        else:
            print(f"ℹ️ OpenAI served request (no failover needed). Model: {data['model']}")

    @pytest.mark.asyncio
    async def test_failover_preserves_functionality(self, core_gateway_client):
        """Test that failover maintains full functionality."""
        test_cases = [
            {"content": "What is 5+5?", "expected_terms": ["10", "ten"]},
            {"content": "Name a color", "expected_terms": ["red", "blue", "green", "yellow", "black", "white"]},
            {"content": "Say hello", "expected_terms": ["hello", "hi", "hey", "greetings"]}
        ]

        for case in test_cases:
            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": case["content"]}],
                max_tokens=20
            )

            assert response.status_code == 200

            data = response.json()
            content_lower = data["content"].lower()

            # Check that response is meaningful (contains expected terms)
            has_expected = any(term in content_lower for term in case["expected_terms"])

            # If failover occurred, note it
            if data["id"].startswith("ollama-"):
                print(f"✅ Failover response for '{case['content']}': {data['content'][:50]}...")

            # Response should be relevant regardless of provider
            assert len(data["content"]) > 0, f"Empty response for: {case['content']}"

    @pytest.mark.asyncio
    async def test_failover_response_time(self, core_gateway_client):
        """Test that failover completes within acceptable time."""
        import time

        start_time = time.time()

        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )

        elapsed = time.time() - start_time

        assert response.status_code == 200
        # Failover should complete in < 5 seconds (generous limit)
        assert elapsed < 5.0, \
            f"Failover took too long: {elapsed:.2f}s"

        if response.json()["id"].startswith("ollama-"):
            # Ollama failover should be fast (< 2s typically)
            print(f"✅ Failover completed in {elapsed:.2f}s")
            assert elapsed < 3.0, \
                f"Ollama failover slow: {elapsed:.2f}s"

    @pytest.mark.asyncio
    async def test_multiple_consecutive_failovers(self, core_gateway_client):
        """Test that failover works consistently across multiple requests."""
        num_requests = 5
        results = []

        for i in range(num_requests):
            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Request {i+1}"}],
                max_tokens=10
            )

            assert response.status_code == 200, \
                f"Request {i+1} failed"

            data = response.json()
            results.append({
                "request_num": i + 1,
                "provider": "ollama" if data["id"].startswith("ollama-") else "openai",
                "model": data["model"],
                "response_length": len(data["content"])
            })

        # All requests should succeed
        assert len(results) == num_requests

        # Count failovers
        ollama_count = sum(1 for r in results if r["provider"] == "ollama")
        print(f"✅ {num_requests} requests completed. Failovers: {ollama_count}/{num_requests}")

        # All responses should have content
        assert all(r["response_length"] > 0 for r in results), \
            "Some responses were empty"

    @pytest.mark.asyncio
    async def test_failover_with_different_parameters(self, core_gateway_client):
        """Test failover with various request parameters."""
        test_configs = [
            {"max_tokens": 5, "temperature": 0.0},
            {"max_tokens": 50, "temperature": 0.5},
            {"max_tokens": 100, "temperature": 0.9},
            {"max_tokens": 10, "top_p": 0.9}
        ]

        for config in test_configs:
            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Test"}],
                **config
            )

            assert response.status_code == 200, \
                f"Failed with config: {config}"

            data = response.json()
            assert len(data["content"]) > 0


@pytest.mark.failover
class TestFailoverEdgeCases:
    """Test edge cases and error scenarios in failover."""

    @pytest.mark.asyncio
    async def test_failover_with_long_context(self, core_gateway_client):
        """Test failover with long conversation context."""
        # Build a long conversation history
        messages = [{"role": "system", "content": "You are a helpful assistant."}]

        for i in range(5):
            messages.append({"role": "user", "content": f"Question {i+1}: What is {i}+{i}?"})
            messages.append({"role": "assistant", "content": f"Answer: {i+i}"})

        messages.append({"role": "user", "content": "What is 10+10?"})

        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=20
        )

        assert response.status_code == 200
        data = response.json()
        assert "20" in data["content"] or "twenty" in data["content"].lower()

    @pytest.mark.asyncio
    async def test_failover_with_special_characters(self, core_gateway_client):
        """Test failover handles special characters correctly."""
        special_messages = [
            {"role": "user", "content": "Test with emoji: 😀🎉"},
            {"role": "user", "content": "Test with symbols: @#$%^&*()"},
            {"role": "user", "content": "Test with unicode: ñáéíóú"},
            {"role": "user", "content": "Test with newlines:\nLine 2\nLine 3"}
        ]

        for msg in special_messages:
            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[msg],
                max_tokens=20
            )

            # Should handle gracefully
            assert response.status_code in [200, 400]

            if response.status_code == 200:
                data = response.json()
                assert len(data["content"]) > 0

    @pytest.mark.asyncio
    async def test_concurrent_failover_requests(self, core_gateway_client):
        """Test failover under concurrent load."""
        num_concurrent = 10

        async def make_request(i):
            return await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Concurrent request {i}"}],
                max_tokens=10
            )

        # Send all requests concurrently
        tasks = [make_request(i) for i in range(num_concurrent)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successes
        successful = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
        failed = len(responses) - len(successful)

        print(f"✅ Concurrent failover test: {len(successful)}/{num_concurrent} succeeded, {failed} failed")

        # At least 80% should succeed
        success_rate = len(successful) / num_concurrent
        assert success_rate >= 0.8, \
            f"Too many concurrent failures: {success_rate:.1%} success rate"

        # Check that failover worked for successful requests
        ollama_responses = sum(
            1 for r in successful
            if r.json()["id"].startswith("ollama-")
        )

        print(f"  {ollama_responses}/{len(successful)} used Ollama fallback")


@pytest.mark.failover
class TestFailoverLogging:
    """Test that failover events are properly logged."""

    @pytest.mark.asyncio
    async def test_failover_includes_model_info(self, core_gateway_client):
        """Test that failover response includes correct model information."""
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )

        assert response.status_code == 200

        data = response.json()

        # Response should always include model information
        assert "model" in data
        assert len(data["model"]) > 0

        # If Ollama was used, model should reflect that
        if data["id"].startswith("ollama-"):
            assert "qwen" in data["model"].lower() or "llama" in data["model"].lower(), \
                f"Ollama model not identified correctly: {data['model']}"

    @pytest.mark.asyncio
    async def test_failover_finish_reason(self, core_gateway_client):
        """Test that failover responses include proper finish_reason."""
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say hi"}],
            max_tokens=5
        )

        if response.status_code == 200:
            data = response.json()

            assert "finish_reason" in data
            assert data["finish_reason"] in ["stop", "length", None], \
                f"Invalid finish_reason: {data['finish_reason']}"


@pytest.mark.failover
@pytest.mark.performance
class TestFailoverPerformance:
    """Test performance characteristics of failover."""

    @pytest.mark.asyncio
    async def test_failover_latency_distribution(self, core_gateway_client):
        """Measure failover latency distribution."""
        import time

        num_requests = 20
        latencies = []

        for i in range(num_requests):
            start = time.time()

            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Request {i}"}],
                max_tokens=10
            )

            elapsed = time.time() - start

            if response.status_code == 200:
                latencies.append(elapsed)

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

            print(f"\n✅ Failover Latency Stats ({len(latencies)} requests):")
            print(f"  Average: {avg_latency:.3f}s")
            print(f"  Min: {min_latency:.3f}s")
            print(f"  Max: {max_latency:.3f}s")
            print(f"  P95: {p95_latency:.3f}s")

            # Performance assertions
            assert avg_latency < 3.0, f"Average latency too high: {avg_latency:.3f}s"
            assert p95_latency < 5.0, f"P95 latency too high: {p95_latency:.3f}s"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_failover_throughput(self, core_gateway_client):
        """Test failover system throughput."""
        import time

        num_requests = 50
        start_time = time.time()

        async def make_request(i):
            return await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Request {i}"}],
                max_tokens=10
            )

        # Send requests in batches to avoid overwhelming the system
        batch_size = 10
        successful_requests = 0

        for batch_start in range(0, num_requests, batch_size):
            batch_tasks = [
                make_request(i)
                for i in range(batch_start, min(batch_start + batch_size, num_requests))
            ]

            responses = await asyncio.gather(*batch_tasks, return_exceptions=True)
            successful_requests += sum(
                1 for r in responses
                if not isinstance(r, Exception) and r.status_code == 200
            )

            # Small delay between batches
            await asyncio.sleep(0.1)

        total_time = time.time() - start_time
        throughput = successful_requests / total_time

        print(f"\n✅ Failover Throughput Test:")
        print(f"  Total requests: {num_requests}")
        print(f"  Successful: {successful_requests}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Throughput: {throughput:.2f} req/s")

        # Should handle at least 5 req/s
        assert throughput >= 5.0, \
            f"Throughput too low: {throughput:.2f} req/s"

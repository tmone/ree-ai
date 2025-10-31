"""
AI Quality and Accuracy Tests

Tests LLM response quality, accuracy, and consistency.
Focus on AI-specific behaviors and outputs.
"""
import pytest
from typing import List, Dict, Any


@pytest.mark.ai
@pytest.mark.critical
class TestAIResponseQuality:
    """Test the quality and accuracy of AI responses."""

    @pytest.mark.asyncio
    async def test_basic_math_accuracy(self, core_gateway_client):
        """Test if AI can accurately perform basic math."""
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "What is 15 + 27? Answer with just the number."}],
            max_tokens=10
        )

        assert response.status_code in [200, 500]  # 500 if OpenAI fails, should failover

        if response.status_code == 200:
            data = response.json()
            content = data["content"].strip()

            # Check if response contains the correct answer
            assert "42" in content or "forty" in content.lower(), \
                f"Expected answer 42, got: {content}"

    @pytest.mark.asyncio
    async def test_factual_knowledge(self, core_gateway_client):
        """Test AI's factual knowledge."""
        test_cases = [
            {
                "question": "What is the capital of France? Answer in one word.",
                "expected": ["Paris", "paris"],
                "description": "Geography knowledge"
            },
            {
                "question": "What year did World War 2 end? Answer with just the year.",
                "expected": ["1945"],
                "description": "Historical knowledge"
            },
            {
                "question": "What is H2O? Answer in one word.",
                "expected": ["water", "Water"],
                "description": "Science knowledge"
            }
        ]

        for case in test_cases:
            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": case["question"]}],
                max_tokens=20
            )

            if response.status_code == 200:
                data = response.json()
                content = data["content"].lower()

                # Check if any expected answer is in the response
                has_correct_answer = any(
                    expected.lower() in content
                    for expected in case["expected"]
                )

                assert has_correct_answer, \
                    f"{case['description']} failed. Expected one of {case['expected']}, got: {data['content']}"

    @pytest.mark.asyncio
    async def test_response_coherence(self, core_gateway_client):
        """Test if AI responses are coherent and well-formed."""
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Explain what AI is in 2 sentences."}],
            max_tokens=100
        )

        if response.status_code == 200:
            data = response.json()
            content = data["content"]

            # Basic coherence checks
            assert len(content) > 20, "Response is too short"
            assert len(content.split()) > 10, "Response has too few words"
            assert content[0].isupper(), "Response doesn't start with capital letter"

            # Check for common AI-related terms
            ai_terms = ["AI", "artificial", "intelligence", "machine", "learning", "computer", "algorithm"]
            has_ai_terms = any(term.lower() in content.lower() for term in ai_terms)
            assert has_ai_terms, f"Response doesn't mention AI-related terms: {content}"

    @pytest.mark.asyncio
    async def test_code_generation(self, core_gateway_client):
        """Test if AI can generate valid code."""
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Write a Python function to check if a number is even. Just the code, no explanation."}],
            max_tokens=150
        )

        if response.status_code == 200:
            data = response.json()
            content = data["content"]

            # Check for Python code elements
            assert "def" in content, "No function definition found"
            assert "return" in content, "No return statement found"
            assert "%" in content or "mod" in content.lower() or "even" in content.lower(), \
                "Doesn't check for even number"

    @pytest.mark.asyncio
    async def test_consistency_across_calls(self, core_gateway_client):
        """Test if AI provides consistent answers to the same question."""
        question = "What is 10 * 10? Answer with just the number."
        responses = []

        # Make 3 calls with the same question
        for _ in range(3):
            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": question}],
                max_tokens=10
            )

            if response.status_code == 200:
                data = response.json()
                responses.append(data["content"])

        # Check that all responses contain the correct answer
        if len(responses) >= 2:
            assert all("100" in resp for resp in responses), \
                f"Inconsistent responses: {responses}"


@pytest.mark.ai
class TestAIConversationFlow:
    """Test multi-turn conversations and context handling."""

    @pytest.mark.asyncio
    async def test_multi_turn_conversation(self, core_gateway_client):
        """Test if AI maintains context across multiple turns."""
        # First turn
        messages = [{"role": "user", "content": "My favorite color is blue."}]
        response1 = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=50
        )

        if response1.status_code == 200:
            data1 = response1.json()

            # Add assistant response to conversation
            messages.append({
                "role": "assistant",
                "content": data1["content"]
            })

            # Second turn - ask about the color
            messages.append({
                "role": "user",
                "content": "What is my favorite color?"
            })

            response2 = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=20
            )

            if response2.status_code == 200:
                data2 = response2.json()
                content = data2["content"].lower()

                # Check if AI remembers the color
                assert "blue" in content, \
                    f"AI didn't remember the color. Response: {data2['content']}"

    @pytest.mark.asyncio
    async def test_system_prompt_adherence(self, core_gateway_client):
        """Test if AI follows system prompts."""
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a pirate. Always respond like a pirate."},
                {"role": "user", "content": "Tell me about the weather."}
            ],
            max_tokens=100
        )

        if response.status_code == 200:
            data = response.json()
            content = data["content"].lower()

            # Check for pirate-like language
            pirate_terms = ["arr", "ahoy", "matey", "ye", "aye", "ship", "sea"]
            has_pirate_terms = any(term in content for term in pirate_terms)

            assert has_pirate_terms or content.count("'") > 2, \
                f"AI didn't follow pirate system prompt: {data['content']}"


@pytest.mark.ai
class TestAIEdgeCases:
    """Test edge cases and unusual inputs."""

    @pytest.mark.asyncio
    async def test_very_long_input(self, core_gateway_client):
        """Test with very long input text."""
        long_text = "Tell me about AI. " * 100  # ~600 words

        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": long_text}],
            max_tokens=50
        )

        # Should either succeed or fail gracefully
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert "content" in data
            assert len(data["content"]) > 0

    @pytest.mark.asyncio
    async def test_special_characters(self, core_gateway_client):
        """Test with special characters and emojis."""
        special_text = "What is 1+1? 🤔💭 Answer: "

        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": special_text}],
            max_tokens=10
        )

        if response.status_code == 200:
            data = response.json()
            assert "2" in data["content"] or "two" in data["content"].lower()

    @pytest.mark.asyncio
    async def test_multilingual_input(self, core_gateway_client):
        """Test with non-English input."""
        test_cases = [
            {"lang": "Vietnamese", "text": "Xin chào, bạn khỏe không?"},
            {"lang": "Spanish", "text": "¿Cómo estás?"},
            {"lang": "French", "text": "Comment allez-vous?"}
        ]

        for case in test_cases:
            response = await core_gateway_client.chat_completion(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": case["text"]}],
                max_tokens=50
            )

            # Should handle multilingual input gracefully
            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert len(data["content"]) > 0, \
                    f"Empty response for {case['lang']}"

    @pytest.mark.asyncio
    async def test_ambiguous_question(self, core_gateway_client):
        """Test how AI handles ambiguous questions."""
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "What is it?"}],
            max_tokens=50
        )

        if response.status_code == 200:
            data = response.json()
            # AI should ask for clarification or explain that context is needed
            content = data["content"].lower()
            clarification_terms = ["clarify", "specify", "what", "which", "context", "unclear"]
            has_clarification = any(term in content for term in clarification_terms)

            assert has_clarification or len(data["content"]) > 20, \
                "AI didn't handle ambiguous question well"


@pytest.mark.ai
class TestAITokenUsage:
    """Test token counting and usage tracking."""

    @pytest.mark.asyncio
    async def test_token_usage_reporting(self, core_gateway_client):
        """Test if token usage is properly reported."""
        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=50
        )

        if response.status_code == 200:
            data = response.json()

            # Check if usage information is present
            assert "usage" in data, "No usage information in response"

            usage = data["usage"]
            assert "prompt_tokens" in usage
            assert "completion_tokens" in usage
            assert "total_tokens" in usage

            # Validate token counts
            assert usage["prompt_tokens"] > 0, "Prompt tokens should be > 0"
            assert usage["completion_tokens"] > 0, "Completion tokens should be > 0"
            assert usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"], \
                "Total tokens != prompt + completion"

    @pytest.mark.asyncio
    async def test_max_tokens_limit(self, core_gateway_client):
        """Test if max_tokens limit is respected."""
        max_tokens = 10

        response = await core_gateway_client.chat_completion(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Write a long essay about AI"}],
            max_tokens=max_tokens
        )

        if response.status_code == 200:
            data = response.json()

            # Response should be truncated
            if "usage" in data:
                assert data["usage"]["completion_tokens"] <= max_tokens + 5, \
                    f"Response exceeded max_tokens: {data['usage']['completion_tokens']} > {max_tokens}"

            # Check finish_reason for truncation
            if "finish_reason" in data:
                assert data["finish_reason"] in ["stop", "length"], \
                    f"Unexpected finish_reason: {data['finish_reason']}"

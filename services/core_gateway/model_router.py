"""
Intelligent Model Router for Core Gateway
Automatically selects optimal LLM model based on query complexity
"""
import os
from typing import List, Optional
from enum import Enum
from shared.models.core_gateway import Message, ModelType
from shared.utils.logger import setup_logger, LogEmoji

logger = setup_logger("model_router")


class QueryComplexity(str, Enum):
    """Query complexity levels"""
    SIMPLE = "simple"      # Simple classification, extraction → Ollama (free, fast)
    MEDIUM = "medium"      # Standard queries → GPT-4o-mini (cheap, decent)
    COMPLEX = "complex"    # Complex reasoning, vision → GPT-4o (expensive, best)


class ModelRouter:
    """
    Intelligent model router that selects optimal LLM based on query complexity.

    Cost optimization strategy:
    - SIMPLE queries → Ollama (free, fast) - 50% of queries
    - MEDIUM queries → GPT-4o-mini ($0.15/1M tokens) - 30% of queries
    - COMPLEX queries → GPT-4o ($2.50/1M tokens) - 20% of queries

    Expected savings: ~60% cost reduction
    """

    # Keywords indicating simple tasks (can use Ollama)
    SIMPLE_KEYWORDS = [
        "classify", "phân loại",
        "extract", "trích xuất",
        "parse", "phân tích cú pháp",
        "yes or no", "có hay không",
        "true or false", "đúng hay sai"
    ]

    # Keywords indicating complex tasks (need GPT-4o)
    COMPLEX_KEYWORDS = [
        "explain why", "giải thích tại sao",
        "analyze", "phân tích sâu",
        "compare and contrast", "so sánh",
        "evaluate", "đánh giá",
        "recommend", "đề xuất",
        "creative", "sáng tạo",
        "image", "hình ảnh", "ảnh",
        "vision", "nhìn"
    ]

    @classmethod
    def estimate_complexity(
        cls,
        messages: List[Message],
        is_multimodal: bool = False
    ) -> QueryComplexity:
        """
        Estimate query complexity based on message content.

        Args:
            messages: List of conversation messages
            is_multimodal: Whether request contains images

        Returns:
            QueryComplexity level
        """
        # Multimodal always requires GPT-4o (vision capability)
        if is_multimodal:
            logger.info(f"{LogEmoji.AI} Complexity: COMPLEX (multimodal)")
            return QueryComplexity.COMPLEX

        # Get last user message (most relevant)
        user_messages = [msg for msg in messages if msg.role == "user"]
        if not user_messages:
            return QueryComplexity.MEDIUM

        last_message = user_messages[-1]
        content = last_message.content.lower() if isinstance(last_message.content, str) else ""

        # Check for simple keywords
        if any(keyword in content for keyword in cls.SIMPLE_KEYWORDS):
            logger.info(f"{LogEmoji.AI} Complexity: SIMPLE (keyword match)")
            return QueryComplexity.SIMPLE

        # Check for complex keywords
        if any(keyword in content for keyword in cls.COMPLEX_KEYWORDS):
            logger.info(f"{LogEmoji.AI} Complexity: COMPLEX (keyword match)")
            return QueryComplexity.COMPLEX

        # Check message length (proxy for complexity)
        word_count = len(content.split())
        if word_count < 20:
            # Short messages usually simple
            logger.info(f"{LogEmoji.AI} Complexity: SIMPLE (short message: {word_count} words)")
            return QueryComplexity.SIMPLE
        elif word_count > 100:
            # Long messages usually complex
            logger.info(f"{LogEmoji.AI} Complexity: COMPLEX (long message: {word_count} words)")
            return QueryComplexity.COMPLEX

        # Check if system prompt mentions structured output (usually simple)
        system_messages = [msg for msg in messages if msg.role == "system"]
        if system_messages:
            system_content = system_messages[0].content.lower() if isinstance(system_messages[0].content, str) else ""
            if "json" in system_content or "structured" in system_content:
                logger.info(f"{LogEmoji.AI} Complexity: SIMPLE (structured output)")
                return QueryComplexity.SIMPLE

        # Default to MEDIUM
        logger.info(f"{LogEmoji.AI} Complexity: MEDIUM (default)")
        return QueryComplexity.MEDIUM

    @classmethod
    def select_model(
        cls,
        current_model: ModelType,
        messages: List[Message],
        is_multimodal: bool = False,
        enable_routing: bool = True
    ) -> ModelType:
        """
        Select optimal model based on complexity.

        Args:
            current_model: Originally requested model
            messages: Conversation messages
            is_multimodal: Whether request has images
            enable_routing: Whether to enable intelligent routing (default: True)

        Returns:
            Optimal ModelType
        """
        if not enable_routing:
            # Routing disabled, use requested model
            return current_model

        complexity = cls.estimate_complexity(messages, is_multimodal)

        # Route based on complexity
        if complexity == QueryComplexity.SIMPLE:
            # Check if Ollama is available
            ollama_url = os.getenv('OLLAMA_BASE_URL', '')
            if ollama_url and ollama_url.strip():
                # Use Ollama for simple tasks (free, fast)
                optimal_model = ModelType.OLLAMA_QWEN25
                logger.info(
                    f"{LogEmoji.SUCCESS} Model routing: {current_model.value} → {optimal_model.value} "
                    f"(SIMPLE task, cost savings: 100%)"
                )
                return optimal_model
            else:
                # Ollama not available, fallback to GPT-4o-mini
                optimal_model = ModelType.GPT4_MINI
                logger.info(
                    f"{LogEmoji.WARNING} Ollama unavailable, fallback: {current_model.value} → {optimal_model.value} "
                    f"(SIMPLE task, production mode)"
                )
                return optimal_model

        elif complexity == QueryComplexity.MEDIUM:
            # Use GPT-4o-mini for medium tasks (cheap, decent)
            if current_model == ModelType.GPT4O:
                optimal_model = ModelType.GPT4_MINI
                logger.info(
                    f"{LogEmoji.SUCCESS} Model routing: {current_model.value} → {optimal_model.value} "
                    f"(MEDIUM task, cost savings: 94%)"
                )
                return optimal_model
            else:
                # Already using cheap model
                return current_model

        else:  # COMPLEX
            # Keep GPT-4o for complex tasks
            if is_multimodal and current_model != ModelType.GPT4O:
                logger.info(
                    f"{LogEmoji.WARNING} Upgrading to GPT-4o for vision support"
                )
                return ModelType.GPT4O
            else:
                return current_model

    @classmethod
    def get_routing_stats(cls, complexity: QueryComplexity) -> dict:
        """
        Get cost comparison stats for routing decision.

        Returns:
            Dict with cost info and savings
        """
        # OpenAI pricing (as of 2024)
        pricing = {
            "ollama": {"input": 0, "output": 0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},  # per 1M tokens
            "gpt-4o": {"input": 2.50, "output": 10.00}
        }

        if complexity == QueryComplexity.SIMPLE:
            return {
                "selected_model": "ollama",
                "alternative_cost": "gpt-4o: $2.50/1M",
                "savings_percent": 100,
                "reason": "Simple structured task"
            }
        elif complexity == QueryComplexity.MEDIUM:
            return {
                "selected_model": "gpt-4o-mini",
                "alternative_cost": "gpt-4o: $2.50/1M",
                "savings_percent": 94,
                "reason": "Standard query"
            }
        else:
            return {
                "selected_model": "gpt-4o",
                "alternative_cost": "N/A",
                "savings_percent": 0,
                "reason": "Complex reasoning or vision required"
            }

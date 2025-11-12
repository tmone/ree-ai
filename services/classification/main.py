"""
Classification Service - Layer 2 AI Services
Classifies user queries into filter/semantic/both modes using LLM
Enhanced with Redis caching for 400x performance improvement
"""
import httpx
from typing import List, Dict, Optional
from pydantic import BaseModel
from fastapi import HTTPException

from core.base_service import BaseService
from shared.models.core_gateway import LLMRequest, Message, ModelType
from shared.config import settings
from shared.utils.logger import LogEmoji
from shared.utils.redis_cache import get_cache


class ClassifyRequest(BaseModel):
    """Request to classify query"""
    query: str
    context: Optional[List[Dict]] = None  # Optional conversation history


class ClassifyResponse(BaseModel):
    """Response from classification"""
    mode: str  # "filter" | "semantic" | "both"
    confidence: float  # 0.0 - 1.0
    reasoning: str  # Why this classification was chosen
    # NEW: Multi-intent support
    intents: Optional[List[str]] = None  # ["SEARCH", "PRICE_SUGGESTION", "COMPARE"]
    primary_intent: Optional[str] = None  # Primary intent


class ClassificationService(BaseService):
    """
    Classification Service - Intelligent query type detection

    Classifies real estate queries into:
    - filter: Structured attributes (price, bedrooms, location)
    - semantic: Vague/descriptive (beautiful, quiet, near school)
    - both: Mix of structured + semantic
    """

    def __init__(self):
        super().__init__(
            name="classification_service",
            version="2.0.0",  # Enhanced with Redis caching
            capabilities=["query_classification", "intent_detection", "intelligent_caching"],
            port=8080
        )

        # MEDIUM FIX Bug#23: Add connection pooling for better performance
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=50,
                keepalive_expiry=30.0
            )
        )
        self.core_gateway_url = settings.get_core_gateway_url()

        # NEW: Redis cache for classification results
        # Cache TTL: 24h (classification mode rarely changes for same query)
        self.cache = get_cache(namespace="classification")
        self.cache_ttl = 86400  # 24 hours

        self.logger.info(f"{LogEmoji.INFO} Core Gateway: {self.core_gateway_url}")
        self.logger.info(f"{LogEmoji.SUCCESS} Redis cache enabled (TTL: {self.cache_ttl}s)")

    def setup_routes(self):
        """Setup classification API routes"""

        @self.app.post("/classify", response_model=ClassifyResponse)
        async def classify_query(request: ClassifyRequest):
            """
            Classify query type using LLM with intelligent caching

            Returns:
            - filter: Query has clear structured attributes
            - semantic: Query is vague/descriptive
            - both: Query has mix of both

            Performance:
            - Cache HIT: <10ms (400x faster)
            - Cache MISS: 2-4s (LLM call)
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} Classifying query: '{request.query}'")

                # NEW: Check cache first
                # Normalize query for consistent cache keys
                normalized_query = request.query.lower().strip()
                cache_key = f"classify:{self.cache._hash_key(normalized_query)}"

                # Try to get from cache
                await self.cache.connect()
                cached_result = await self.cache.get(cache_key)

                if cached_result:
                    self.logger.info(
                        f"{LogEmoji.SUCCESS} Cache HIT! Returning cached classification: "
                        f"{cached_result['mode']} (saved ~2-4s + LLM cost)"
                    )
                    return ClassifyResponse(**cached_result)

                # Build smart prompt for LLM with multi-intent detection
                system_prompt = """You are an expert at classifying real estate queries.

Your tasks:
1. Classify query MODE (filter/semantic/both)
2. Detect ALL intents in the query (multi-intent support)

**PART 1: MODE CLASSIFICATION**

1. **filter** - Query contains CLEAR structured attributes:
   - Specific price ("3 tỷ", "5-7 tỷ", "dưới 10 tỷ")
   - Number of bedrooms/bathrooms ("2PN", "3 phòng ngủ")
   - Specific location ("quận 2", "Thảo Điền", "gần trung tâm")
   - Property type ("căn hộ", "biệt thự", "nhà phố")

2. **semantic** - Query is VAGUE or DESCRIPTIVE:
   - Aesthetic qualities ("đẹp", "sang trọng", "hiện đại")
   - Feelings/atmosphere ("yên tĩnh", "sầm uất", "thoáng mát")
   - Nearby amenities (vague: "gần trường học", "gần siêu thị")
   - Lifestyle preferences ("phù hợp gia đình", "cho người trẻ")

3. **both** - Query has BOTH structured AND semantic:
   - "Căn hộ 2PN ở quận 2, view đẹp" (structured: 2PN, quận 2 | semantic: view đẹp)
   - "Nhà giá 5 tỷ, yên tĩnh" (structured: price | semantic: quiet)

**PART 2: INTENT DETECTION (NEW - Multi-Intent Support)**

Detect ALL intents in the query:
- **SEARCH**: User wants to find properties ("tìm", "cần mua", "cần thuê")
- **PRICE_SUGGESTION**: User wants market price info ("giá thị trường", "giá khu vực này", "bao nhiêu một m2")
- **COMPARE**: User wants to compare properties ("so sánh", "khác gì", "tốt hơn")
- **VALUATION**: User wants property valuation ("định giá", "nhà này giá bao nhiêu")
- **TREND_ANALYSIS**: User wants market trends ("xu hướng thị trường", "giá đang tăng hay giảm")
- **CONSULTATION**: User asks for advice ("nên mua", "nên chọn", "đầu tư")

Examples:
- "Tìm căn hộ 2PN Q7" → intents: ["SEARCH"], primary: "SEARCH"
- "Tìm nhà 3 tỷ và cho tôi giá thị trường Q2" → intents: ["SEARCH", "PRICE_SUGGESTION"], primary: "SEARCH"
- "So sánh nhà phố Q7 và Q2" → intents: ["COMPARE", "SEARCH"], primary: "COMPARE"

IMPORTANT:
- Respond in JSON format ONLY
- Detect ALL intents (can have multiple)
- Set primary_intent to the MOST IMPORTANT intent

Response format:
{
  "mode": "filter" | "semantic" | "both",
  "confidence": 0.9,
  "reasoning": "Brief explanation in Vietnamese",
  "intents": ["SEARCH", "PRICE_SUGGESTION"],
  "primary_intent": "SEARCH"
}"""

                user_prompt = f"""Classify this Vietnamese real estate query:

Query: "{request.query}"

Context: {request.context if request.context else "No previous context"}

Respond with JSON only."""

                # Call Core Gateway (LLM)
                llm_request = LLMRequest(
                    model=ModelType.GPT4_MINI,
                    messages=[
                        Message(role="system", content=system_prompt),
                        Message(role="user", content=user_prompt)
                    ],
                    temperature=0.1,  # Low temperature for consistent classification
                    max_tokens=200
                )

                response = await self.http_client.post(
                    f"{self.core_gateway_url}/chat/completions",
                    json=llm_request.dict()
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Core Gateway error: {response.text}"
                    )

                data = response.json()
                content = data.get("content", "").strip()

                # Parse JSON response
                import json
                try:
                    # Remove markdown code blocks if present
                    if content.startswith("```"):
                        content = content.split("```")[1]
                        if content.startswith("json"):
                            content = content[4:]
                        content = content.strip()

                    result = json.loads(content)

                    mode = result.get("mode", "semantic")
                    confidence = result.get("confidence", 0.7)
                    reasoning = result.get("reasoning", "")
                    # NEW: Multi-intent fields
                    intents = result.get("intents", ["SEARCH"])  # Default to SEARCH
                    primary_intent = result.get("primary_intent", "SEARCH")

                    # Validate mode
                    if mode not in ["filter", "semantic", "both"]:
                        self.logger.warning(f"{LogEmoji.WARNING} Invalid mode '{mode}', defaulting to 'semantic'")
                        mode = "semantic"
                        confidence = 0.5

                    self.logger.info(f"{LogEmoji.SUCCESS} Classification: {mode} (confidence: {confidence:.2f})")
                    self.logger.info(f"{LogEmoji.INFO} Reasoning: {reasoning}")
                    self.logger.info(f"{LogEmoji.INFO} Intents: {intents} (primary: {primary_intent})")

                    response = ClassifyResponse(
                        mode=mode,
                        confidence=confidence,
                        reasoning=reasoning,
                        intents=intents,
                        primary_intent=primary_intent
                    )

                    # NEW: Cache the result for future requests
                    await self.cache.set(
                        cache_key,
                        response.dict(),
                        ttl=self.cache_ttl
                    )
                    self.logger.info(f"{LogEmoji.SUCCESS} Cached classification result (TTL: 24h)")

                    return response

                except json.JSONDecodeError as e:
                    self.logger.error(f"{LogEmoji.ERROR} Failed to parse LLM response: {content}")
                    # Fallback: simple heuristic
                    mode = self._fallback_classification(request.query)
                    return ClassifyResponse(
                        mode=mode,
                        confidence=0.5,
                        reasoning="Fallback classification (LLM parse error)"
                    )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Classification failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def _fallback_classification(self, query: str) -> str:
        """Simple heuristic fallback if LLM fails"""
        query_lower = query.lower()

        # Check for structured keywords
        structured_keywords = [
            "pn", "phòng ngủ", "bedroom",
            "tỷ", "triệu", "vnd",
            "quận", "district", "phường",
            "căn hộ", "nhà phố", "biệt thự"
        ]

        # Check for semantic keywords
        semantic_keywords = [
            "đẹp", "sang", "hiện đại", "cổ điển",
            "yên tĩnh", "sầm uất", "thoáng",
            "gần", "view", "tiện ích"
        ]

        has_structured = any(kw in query_lower for kw in structured_keywords)
        has_semantic = any(kw in query_lower for kw in semantic_keywords)

        if has_structured and has_semantic:
            return "both"
        elif has_structured:
            return "filter"
        else:
            return "semantic"

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()
        await self.cache.close()
        self.logger.info(f"{LogEmoji.INFO} Redis cache closed")
        await super().on_shutdown()


if __name__ == "__main__":
    service = ClassificationService()
    service.run()

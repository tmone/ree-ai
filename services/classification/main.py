"""
Classification Service - Layer 2 AI Services
Classifies user queries into filter/semantic/both modes using LLM
Enhanced with Redis caching for 400x performance improvement
UPDATED 2025-11-16: Added CHAT intent detection for general conversations
UPDATED 2025-11-16 v2: Fixed CHAT vs ACTION intent priority (actions take precedence)
UPDATED 2025-11-16 v3: Refactored to use language-agnostic English prompts (i18n ready)
UPDATED 2025-11-21: CRITICAL i18n compliance - load keywords from master data
"""
import httpx
import os
from typing import List, Dict, Optional
from pydantic import BaseModel
from fastapi import HTTPException

from core.base_service import BaseService
from shared.models.core_gateway import LLMRequest, Message, ModelType
from shared.config import settings
from shared.utils.logger import LogEmoji
from shared.utils.redis_cache import get_cache
from shared.utils.i18n import t
from shared.utils.i18n_loader import get_i18n_loader

# Load master data - NEVER hardcode keywords!
i18n_loader = get_i18n_loader()


def load_prompt(filename: str) -> str:
    """Load prompt template from file"""
    prompt_path = os.path.join(os.path.dirname(__file__), '../../shared/prompts', filename)
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to inline if file not found
        return None


class ClassifyRequest(BaseModel):
    """Request to classify query"""
    query: str
    context: Optional[List[Dict]] = None  # Optional conversation history
    language: str = "vi"  # User's preferred language (vi, en, th, ja)


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
        # Cache TTL: Reduced to 1h during debugging (was 24h)
        # TODO: Restore to 86400 after classification bug is confirmed fixed
        self.cache = get_cache(namespace="classification")
        self.cache_ttl = 3600  # 1 hour (TEMPORARY - was 24 hours)

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

                # NEW: Check cache first (ONLY if no context)
                # When context is provided, skip cache to ensure context-aware classification
                cached_result = None
                cache_key = None  # Initialize cache_key to avoid UnboundLocalError
                if not request.context:
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
                else:
                    self.logger.info(f"{LogEmoji.INFO} Context provided ({len(request.context)} messages) - skipping cache for context-aware classification")

                # Build smart prompt for LLM with multi-intent detection
                # Load language-agnostic English prompt (works with all languages)
                system_prompt = load_prompt('classification_prompt_en.txt')

                # Fallback to inline if file not found
                if not system_prompt:
                    system_prompt = """You are an expert at classifying real estate queries in ANY language.

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

Detect ALL intents in the query. **CRITICAL**: Distinguish between POSTING vs SEARCHING:

**PRIMARY INTENTS (Transaction Type + Listing Type):**
- **POST_SALE**: User wants to post property FOR SALE ("đăng tin bán", "tôi có nhà bán", "cần bán nhà", "muốn đăng bán")
- **POST_RENT**: User wants to post property FOR RENT ("đăng tin cho thuê", "tôi có nhà cho thuê", "cần cho thuê", "muốn đăng cho thuê")
- **SEARCH_BUY**: User wants to FIND properties to BUY ("tìm nhà mua", "cần mua nhà", "muốn mua căn hộ", "tìm mua")
- **SEARCH_RENT**: User wants to FIND properties to RENT ("tìm nhà thuê", "cần thuê nhà", "muốn thuê căn hộ", "tìm thuê")

**GENERAL CHAT INTENT (Use with caution - don't over-classify as CHAT):**
- **CHAT**: General conversation, greetings, questions NOT about real estate transactions
  - Greetings: "xin chào", "hi", "hello", "chào bạn", "cảm ơn", "tạm biệt"
  - General questions: "hôm nay thứ mấy", "mấy giờ rồi", "bạn là ai", "bạn có thể giúp gì"
  - Non-real-estate topics: "thời tiết thế nào", "ăn gì ngon", "đi đâu chơi"
  - General real estate knowledge (NOT specific actions): "định nghĩa bất động sản là gì", "phân loại loại hình BĐS"

  **IMPORTANT**: Questions about HOW TO post/rent/sell properties should be classified as the ACTION intent (POST_SALE/POST_RENT/SEARCH_*), NOT CHAT:
  - ❌ "Làm thế nào để cho thuê nhà?" → POST_RENT (NOT CHAT - this is action intent!)
  - ❌ "Cho thuê nhà như thế nào?" → POST_RENT (NOT CHAT!)
  - ✅ "Thị trường BĐS hiện tại thế nào?" → CHAT (general knowledge)

**SECONDARY INTENTS (Can combine with primary):**
- **PRICE_CONSULTATION**: User wants market price info or property valuation ("giá thị trường", "giá khu vực này", "bao nhiêu một m2", "định giá nhà", "ước tính giá")
- **COMPARE**: User wants to compare properties ("so sánh", "khác gì", "tốt hơn")
- **TREND_ANALYSIS**: User wants market trends ("xu hướng thị trường", "giá đang tăng hay giảm")
- **CONSULTATION**: User asks for advice about specific property transactions ("nên mua", "nên chọn", "đầu tư")

**DETECTION RULES (Priority Order):**
1. **Check for ACTION keywords FIRST** (posting/searching):
   - "đăng tin", "cho thuê", "cần bán", "muốn cho thuê", "làm thế nào để cho thuê" → POST_SALE/POST_RENT
   - "tìm nhà", "cần mua", "muốn thuê", "tìm kiếm" → SEARCH_BUY/SEARCH_RENT

2. **Then check CHAT intent** (only if NOT an action):
   - Greetings: "xin chào", "hi", "hello", "chào", "cảm ơn" → CHAT
   - General questions: "hôm nay", "thứ mấy", "mấy giờ", "bạn là ai" → CHAT
   - Non-real-estate: "thời tiết", "ăn gì", topics not about properties → CHAT
   - General knowledge (not specific actions): "thị trường BĐS thế nào", "xu hướng đầu tư" → CHAT

3. Determine transaction type:
   - "bán" → SALE, "cho thuê/thuê" → RENT

4. Combine to form final intent:
   - POST + SALE = POST_SALE
   - POST + RENT = POST_RENT
   - SEARCH + BUY = SEARCH_BUY
   - SEARCH + RENT = SEARCH_RENT

Examples:
- "Xin chào!" → intents: ["CHAT"], primary: "CHAT"
- "Hôm nay là thứ mấy?" → intents: ["CHAT"], primary: "CHAT"
- "Thị trường BĐS hiện tại thế nào?" → intents: ["CHAT"], primary: "CHAT"
- "Làm thế nào để cho thuê nhà?" → intents: ["POST_RENT"], primary: "POST_RENT" (NOT CHAT!)
- "Cho thuê nhà như thế nào?" → intents: ["POST_RENT"], primary: "POST_RENT" (NOT CHAT!)
- "Tôi có nhà cần bán ở Q7" → intents: ["POST_SALE"], primary: "POST_SALE"
- "Đăng tin cho thuê căn hộ 2PN" → intents: ["POST_RENT"], primary: "POST_RENT"
- "Tìm căn hộ 2PN Q7 để mua" → intents: ["SEARCH_BUY"], primary: "SEARCH_BUY"
- "Cần thuê nhà Q2" → intents: ["SEARCH_RENT"], primary: "SEARCH_RENT"
- "Tìm nhà 3 tỷ và cho tôi giá thị trường Q2" → intents: ["SEARCH_BUY", "PRICE_CONSULTATION"], primary: "SEARCH_BUY"

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

                # Language-agnostic user prompt (works with any language)
                user_prompt = f"""Classify this real estate query (language: auto-detect):

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
                        detail=t(
                            "classification.core_gateway_error",
                            language=request.language,
                            detail=response.text
                        )
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
                    intents = result.get("intents", ["SEARCH_BUY"])  # Default to SEARCH_BUY
                    primary_intent = result.get("primary_intent", "SEARCH_BUY")

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

                    # NEW: Cache the result for future requests (only if cache_key was created)
                    if cache_key:
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
                    fallback_result = self._fallback_classification(request.query, request.language)
                    return ClassifyResponse(**fallback_result)

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Classification failed: {e}")
                error_msg = t(
                    "classification.classification_failed",
                    language=request.language if hasattr(request, 'language') else 'vi',
                    error=str(e)
                )
                raise HTTPException(status_code=500, detail=error_msg)

    def _fallback_classification(self, query: str, language: str = 'vi') -> Dict:
        """
        Simple heuristic fallback if LLM fails
        Returns dict with mode, confidence, reasoning, intents, primary_intent

        Args:
            query: Query to classify
            language: User's preferred language
        """
        query_lower = query.lower()

        # Log fallback trigger for debugging
        self.logger.warning(f"{LogEmoji.WARNING} FALLBACK HEURISTIC TRIGGERED for query: '{query}'")
        self.logger.warning(f"{LogEmoji.INFO} This means LLM classification failed - investigate why!")

        # PRIORITY 1: Check for CHAT intent first (greetings, general questions)
        chat_keywords = [
            "xin chào", "hi", "hello", "chào bạn", "cảm ơn", "tạm biệt", "bye",
            "hôm nay", "thứ mấy", "mấy giờ", "bạn là ai", "bạn có thể",
            "thời tiết", "để xây nhà", "thủ tục", "cách đầu tư", "làm thế nào"
        ]

        if any(kw in query_lower for kw in chat_keywords):
            # Check if it's REALLY about property transaction
            # If query mentions specific property search/posting, NOT chat
            if not any(kw in query_lower for kw in ["tìm nhà", "tìm căn hộ", "mua nhà", "thuê nhà", "đăng tin"]):
                return {
                    "mode": "semantic",
                    "confidence": 0.8,
                    "reasoning": t("classification.fallback_chat_reasoning", language=language),
                    "intents": ["CHAT"],
                    "primary_intent": "CHAT"
                }

        # PRIORITY 2: Detect intent (POST vs SEARCH, SALE vs RENT)
        # FIX Bug#24: Add missing posting keywords for "muốn bán", "muốn cho thuê"
        posting_keywords = [
            # Original keywords
            "đăng tin", "tôi có", "nhà của tôi", "cần bán", "cần cho thuê", "muốn đăng",
            # ADDED: Common variations for "want to sell/rent"
            "muốn bán",         # "want to sell" - FIX for "Tôi muốn bán nhà"
            "muốn cho thuê",    # "want to rent out"
            "có nhà bán",       # "have house to sell"
            "có nhà cho thuê",  # "have house for rent"
            "định bán",         # "planning to sell"
            "sắp bán",          # "about to sell"
        ]

        search_keywords = [
            # Original keywords
            "tìm", "cần mua", "cần thuê", "muốn mua", "muốn thuê", "tìm kiếm",
            # ADDED: Common variations
            "đang tìm",         # "currently looking for"
            "muốn tìm",         # "want to find"
        ]

        # Load transaction type keywords from master data
        sale_keywords_vi = i18n_loader.get_listing_type_keywords('sale', 'vi')
        rent_keywords_vi = i18n_loader.get_listing_type_keywords('rent', 'vi')

        is_posting = any(kw in query_lower for kw in posting_keywords)
        is_searching = any(kw in query_lower for kw in search_keywords) or not is_posting  # Default to search

        is_sale = any(kw in query_lower for kw in sale_keywords_vi)
        is_rent = any(kw in query_lower for kw in rent_keywords_vi)

        # Determine primary intent
        if is_posting and is_sale:
            primary_intent = "POST_SALE"
        elif is_posting and is_rent:
            primary_intent = "POST_RENT"
        elif is_searching and is_sale:
            primary_intent = "SEARCH_BUY"
        elif is_searching and is_rent:
            primary_intent = "SEARCH_RENT"
        elif is_posting:
            primary_intent = "POST_SALE"  # Default posting to sale
        else:
            primary_intent = "SEARCH_BUY"  # Default to search buy

        # Check for structured keywords (for mode classification)
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
            mode = "both"
        elif has_structured:
            mode = "filter"
        else:
            mode = "semantic"

        # Log matching keywords for debugging
        matched_posting = [kw for kw in posting_keywords if kw in query_lower]
        matched_search = [kw for kw in search_keywords if kw in query_lower]
        self.logger.info(f"{LogEmoji.INFO} Fallback result: {primary_intent}")
        self.logger.info(f"{LogEmoji.INFO} Matched posting keywords: {matched_posting}")
        self.logger.info(f"{LogEmoji.INFO} Matched search keywords: {matched_search}")
        self.logger.info(f"{LogEmoji.INFO} is_posting={is_posting}, is_sale={is_sale}, is_rent={is_rent}")

        return {
            "mode": mode,
            "confidence": 0.5,
            "reasoning": t("classification.fallback_heuristic_reasoning", language=language),
            "intents": [primary_intent],
            "primary_intent": primary_intent
        }

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()
        await self.cache.close()
        self.logger.info(f"{LogEmoji.INFO} Redis cache closed")
        await super().on_shutdown()


if __name__ == "__main__":
    service = ClassificationService()
    service.run()

"""Orchestrator - Intelligent request routing with Core Gateway-powered intent detection."""
import time
from typing import Dict, Any, List, Optional
import httpx

from core.base_service import BaseService
from shared.models.orchestrator import (
    OrchestrationRequest, OrchestrationResponse, IntentType,
    IntentDetectionResult, RoutingDecision
)
from shared.models.core_gateway import LLMRequest, Message, ModelType
from shared.utils.logger import LogEmoji
from shared.config import settings
from services.orchestrator.prompts import get_intent_detection_prompt, OrchestratorPrompts


class Orchestrator(BaseService):
    """
    Orchestrator Service - Layer 2
    Uses LangChain for intelligent request routing and intent detection.
    """

    def __init__(self):
        super().__init__(
            name="orchestrator",
            version="1.0.0",
            capabilities=["orchestration", "routing", "intent_detection"],
            port=8080
        )

        # HTTP client for service calls
        self.http_client = httpx.AsyncClient(timeout=60.0)

        # Core Gateway URL for LLM calls
        self.core_gateway_url = settings.get_core_gateway_url()
        self.logger.info(f"{LogEmoji.INFO} Using Core Gateway at: {self.core_gateway_url}")

        # Intent detection prompt - Using high-quality Vietnamese prompts
        self.intent_prompt_system = OrchestratorPrompts.INTENT_DETECTION_SYSTEM

        # Pre-generate few-shot examples text for efficiency
        self.few_shot_examples = OrchestratorPrompts.get_few_shot_examples_text()

    def setup_routes(self):
        """Setup Orchestrator API routes."""

        @self.app.post("/orchestrate", response_model=OrchestrationResponse)
        async def orchestrate(request: OrchestrationRequest):
            """
            Main orchestration endpoint.
            Detects intent and routes to appropriate service.
            """
            try:
                start_time = time.time()

                self.logger.info(
                    f"{LogEmoji.TARGET} Orchestration request: "
                    f"user={request.user_id}, query='{request.query}'"
                )

                # Step 1: Detect intent
                intent_result = await self._detect_intent(request.query)

                self.logger.info(
                    f"{LogEmoji.AI} Intent detected: {intent_result.intent.value} "
                    f"(confidence: {intent_result.confidence:.2f})"
                )

                # Step 2: Route to appropriate service
                routing_decision = self._decide_routing(intent_result)

                # Step 3: Execute routing
                response_text = await self._execute_routing(
                    routing_decision,
                    request,
                    intent_result
                )

                execution_time = (time.time() - start_time) * 1000

                self.logger.info(
                    f"{LogEmoji.SUCCESS} Orchestration completed: "
                    f"intent={intent_result.intent.value}, time={execution_time:.2f}ms"
                )

                return OrchestrationResponse(
                    intent=intent_result.intent,
                    confidence=intent_result.confidence,
                    response=response_text,
                    service_used=routing_decision.target_service,
                    execution_time_ms=execution_time,
                    metadata={
                        "entities": intent_result.extracted_entities,
                        "routing": routing_decision.dict()
                    }
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Orchestration failed: {e}")
                # Return fallback response
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response=f"Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn: {str(e)}",
                    service_used="none",
                    execution_time_ms=0.0
                )

        @self.app.post("/v1/chat/completions")
        async def openai_compatible_chat(request: Dict[str, Any]):
            """
            OpenAI-compatible endpoint for Open WebUI integration.
            This allows Open WebUI to communicate with Orchestrator.
            """
            try:
                # Extract messages from request
                messages = request.get("messages", [])
                if not messages:
                    return {"error": "No messages provided"}

                # Get last user message
                user_message = ""
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        user_message = msg.get("content", "")
                        break

                if not user_message:
                    return {"error": "No user message found"}

                # Create orchestration request
                orch_request = OrchestrationRequest(
                    user_id=request.get("user", "anonymous"),
                    query=user_message,
                    conversation_id=None,
                    metadata={"messages": messages}
                )

                # Orchestrate
                orch_response = await orchestrate(orch_request)

                # Return OpenAI-compatible response
                return {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "ree-ai-orchestrator",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": orch_response.response
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": len(user_message) // 4,
                        "completion_tokens": len(orch_response.response) // 4,
                        "total_tokens": (len(user_message) + len(orch_response.response)) // 4
                    }
                }

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} OpenAI-compatible chat failed: {e}")
                return {
                    "error": str(e),
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": f"Xin lỗi, tôi gặp lỗi: {str(e)}"
                        }
                    }]
                }

    async def _detect_intent(self, query: str) -> IntentDetectionResult:
        """Detect user intent using Core Gateway with improved prompt and thinking model."""
        try:
            # Build prompt for intent detection
            user_prompt = f"Phân loại câu hỏi sau:\n\n{query}\n\nDựa vào few-shot examples:\n{self.few_shot_examples}"

            # Call Core Gateway
            llm_request = {
                "model": "gpt-4o-mini",  # Core Gateway will handle fallback to Ollama if needed
                "messages": [
                    {"role": "system", "content": self.intent_prompt_system},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json=llm_request,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "").strip()

                self.logger.info(f"{LogEmoji.AI} Raw LLM response: {content[:200]}...")

                # Parse response - Clean up markdown code blocks first
                import json
                import re

                # Remove markdown code blocks if present
                content = re.sub(r'^```(?:json)?\s*\n?', '', content)
                content = re.sub(r'\n?```\s*$', '', content)
                content = content.strip()

                # Parse JSON
                result = json.loads(content)

                return IntentDetectionResult(
                    intent=IntentType(result["intent"].lower()),
                    confidence=result.get("confidence", 0.9),
                    extracted_entities=result.get("entities", {})
                )
            else:
                self.logger.warning(f"{LogEmoji.WARNING} Core Gateway returned {response.status_code}")

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Core Gateway intent detection failed: {e}")

        # Fallback: Simple keyword-based intent detection (aligned with new intents)
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in ["tìm", "find", "search", "tìm kiếm", "có", "cần"]):
            return IntentDetectionResult(
                intent=IntentType.SEARCH,
                confidence=0.8,
                extracted_entities={}
            )
        elif any(keyword in query_lower for keyword in ["so sánh", "compare", "khác gì", "tốt hơn"]):
            return IntentDetectionResult(
                intent=IntentType.COMPARE,
                confidence=0.75,
                extracted_entities={}
            )
        elif any(keyword in query_lower for keyword in ["giá", "price", "bao nhiêu", "hợp lý", "đánh giá giá"]):
            return IntentDetectionResult(
                intent=IntentType.PRICE_ANALYSIS,
                confidence=0.7,
                extracted_entities={}
            )
        elif any(keyword in query_lower for keyword in ["đầu tư", "investment", "nên mua"]):
            return IntentDetectionResult(
                intent=IntentType.INVESTMENT_ADVICE,
                confidence=0.7,
                extracted_entities={}
            )
        elif any(keyword in query_lower for keyword in ["khu vực", "tiện ích", "có gì", "location"]):
            return IntentDetectionResult(
                intent=IntentType.LOCATION_INSIGHTS,
                confidence=0.7,
                extracted_entities={}
            )
        elif any(keyword in query_lower for keyword in ["pháp lý", "thủ tục", "legal", "giấy tờ"]):
            return IntentDetectionResult(
                intent=IntentType.LEGAL_GUIDANCE,
                confidence=0.7,
                extracted_entities={}
            )
        else:
            return IntentDetectionResult(
                intent=IntentType.CHAT,
                confidence=0.6,
                extracted_entities={}
            )

    def _extract_search_filters(self, query: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured search filters from query and entities.
        This is the critical entity extraction layer that prevents raw queries from going to DB Gateway!
        """
        filters = {}

        # Extract from entities (already parsed by intent detection LLM)
        if entities:
            # Property type
            if "property_type" in entities:
                filters["property_type"] = entities["property_type"]

            # Bedrooms
            if "bedrooms" in entities:
                filters["min_bedrooms"] = entities["bedrooms"]

            # Location/Region
            if "location" in entities:
                filters["region"] = entities["location"]
            elif "district" in entities:
                filters["region"] = entities["district"]

            # Price range - handle multiple formats
            if "price_range" in entities:
                if "min" in entities["price_range"]:
                    filters["min_price"] = entities["price_range"]["min"]
                if "max" in entities["price_range"]:
                    filters["max_price"] = entities["price_range"]["max"]
            elif "price" in entities:
                filters["max_price"] = entities["price"]  # Assume "price" means "up to this price"
            else:
                # Handle direct min_price/max_price fields from Attribute Extraction Service
                if "min_price" in entities:
                    filters["min_price"] = entities["min_price"]
                if "max_price" in entities:
                    filters["max_price"] = entities["max_price"]

            # Area - handle multiple formats
            if "area" in entities:
                filters["min_area"] = entities["area"]
            else:
                # Handle direct min_area/max_area fields
                if "min_area" in entities:
                    filters["min_area"] = entities["min_area"]
                if "max_area" in entities:
                    filters["max_area"] = entities["max_area"]

        # Build search request with structured filters
        search_request = {
            "query": query,  # Still include query for text matching
            "filters": filters if filters else None,
            "limit": 5
        }

        self.logger.info(f"{LogEmoji.AI} Extracted search filters: {filters}")
        return search_request

    def _decide_routing(self, intent_result: IntentDetectionResult) -> RoutingDecision:
        """
        Decide which service to route to based on intent.
        Aligned with Vietnamese real estate domain requirements.
        """
        if intent_result.intent == IntentType.SEARCH:
            # Tìm kiếm bất động sản → DB Gateway (direct search)
            return RoutingDecision(
                intent=intent_result.intent,
                target_service="db_gateway",
                endpoint="/search",
                should_use_rag=True,  # Uses database search
                extracted_params=intent_result.extracted_entities
            )
        elif intent_result.intent == IntentType.COMPARE:
            # So sánh bất động sản → RAG Service + Analysis
            return RoutingDecision(
                intent=intent_result.intent,
                target_service="rag_service",
                endpoint="/compare",
                should_use_rag=True,
                extracted_params=intent_result.extracted_entities
            )
        elif intent_result.intent == IntentType.PRICE_ANALYSIS:
            # Phân tích giá → Price Suggestion Service
            return RoutingDecision(
                intent=intent_result.intent,
                target_service="price_suggestion",
                endpoint="/analyze",
                should_use_rag=False,
                extracted_params=intent_result.extracted_entities
            )
        elif intent_result.intent == IntentType.INVESTMENT_ADVICE:
            # Tư vấn đầu tư → RAG Service + Investment Analysis
            return RoutingDecision(
                intent=intent_result.intent,
                target_service="rag_service",
                endpoint="/investment",
                should_use_rag=True,
                extracted_params=intent_result.extracted_entities
            )
        elif intent_result.intent == IntentType.LOCATION_INSIGHTS:
            # Phân tích khu vực → RAG Service (area data)
            return RoutingDecision(
                intent=intent_result.intent,
                target_service="rag_service",
                endpoint="/location",
                should_use_rag=True,
                extracted_params=intent_result.extracted_entities
            )
        elif intent_result.intent == IntentType.LEGAL_GUIDANCE:
            # Tư vấn pháp lý → Core Gateway (LLM knowledge base)
            return RoutingDecision(
                intent=intent_result.intent,
                target_service="core_gateway",
                endpoint="/chat/completions",
                should_use_rag=False,
                extracted_params=intent_result.extracted_entities
            )
        else:
            # Default: CHAT or UNKNOWN → Core Gateway
            return RoutingDecision(
                intent=intent_result.intent,
                target_service="core_gateway",
                endpoint="/chat/completions",
                should_use_rag=False,
                extracted_params=intent_result.extracted_entities
            )

    async def _execute_routing(
        self,
        routing: RoutingDecision,
        request: OrchestrationRequest,
        intent_result: IntentDetectionResult
    ) -> str:
        """Execute the routing decision."""
        if routing.should_use_rag and routing.target_service == "db_gateway":
            # CORRECT CTO ARCHITECTURE: Route to RAG Service (Layer 6)
            # RAG Service handles full pipeline: Retrieve → Augment → Generate
            # Orchestrator should NOT call DB Gateway directly!
            try:
                # Step 1: Call Attribute Extraction Service (Layer 3) to extract entities from raw query
                self.logger.info(f"{LogEmoji.AI} Calling Attribute Extraction Service for entity extraction...")

                attr_extraction_url = "http://attribute-extraction:8084"
                attr_response = await self.http_client.post(
                    f"{attr_extraction_url}/extract-query",
                    json={
                        "query": request.query,
                        "intent": intent_result.intent.value
                    },
                    timeout=30.0
                )

                extracted_entities = {}
                if attr_response.status_code == 200:
                    attr_data = attr_response.json()
                    extracted_entities = attr_data.get("entities", {})
                    confidence = attr_data.get("confidence", 0.0)
                    self.logger.info(f"{LogEmoji.SUCCESS} Extracted entities (confidence={confidence:.2f}): {extracted_entities}")
                else:
                    self.logger.warning(f"{LogEmoji.WARNING} Attribute Extraction Service returned {attr_response.status_code}")
                    # Continue with empty entities as fallback

                # Step 2: Build filters from extracted entities
                search_filters = self._extract_search_filters(
                    request.query,
                    extracted_entities
                ).get("filters", {})

                self.logger.info(f"{LogEmoji.AI} Calling RAG Service with filters: {search_filters}")

                # Step 3: Call RAG Service (Layer 6) - handles full RAG pipeline internally
                # RAG Service will:
                # - Retrieve relevant properties from DB Gateway
                # - Augment context with retrieved data
                # - Generate natural language response using Core Gateway (LLM)
                rag_service_url = "http://rag-service:8080"
                rag_response = await self.http_client.post(
                    f"{rag_service_url}/query",
                    json={
                        "query": request.query,
                        "filters": search_filters,
                        "limit": 5
                    },
                    timeout=90.0  # RAG needs more time for full pipeline
                )

                if rag_response.status_code == 200:
                    rag_data = rag_response.json()
                    generated_response = rag_data.get("response", "")
                    retrieved_count = rag_data.get("retrieved_count", 0)
                    confidence = rag_data.get("confidence", 0.0)

                    self.logger.info(f"{LogEmoji.SUCCESS} RAG response (retrieved={retrieved_count}, confidence={confidence:.2f})")
                    return generated_response
                else:
                    self.logger.warning(f"{LogEmoji.WARNING} RAG Service returned {rag_response.status_code}")
                    return "Xin lỗi, tôi không thể xử lý yêu cầu tìm kiếm của bạn lúc này. Vui lòng thử lại sau."

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} RAG Service call failed: {e}")
                return "Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau."

        # Fallback: Use Core Gateway for simple chat
        try:
            core_gateway_url = settings.get_core_gateway_url()
            llm_request = LLMRequest(
                model=ModelType.GPT4_MINI,
                messages=[
                    Message(role="system", content="Bạn là trợ lý AI cho bất động sản REE AI. Hãy trả lời một cách thân thiện và hữu ích."),
                    Message(role="user", content=request.query)
                ],
                max_tokens=500,
                temperature=0.7
            )

            response = await self.http_client.post(
                f"{core_gateway_url}/chat/completions",
                json=llm_request.dict(),
                timeout=60.0
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("content", "Xin lỗi, tôi không thể trả lời câu hỏi này.")

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Core Gateway call failed: {e}")

        return "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau."

    async def on_shutdown(self):
        """Cleanup on shutdown."""
        await self.http_client.aclose()
        await super().on_shutdown()


if __name__ == "__main__":
    service = Orchestrator()
    service.run()

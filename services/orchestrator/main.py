"""Orchestrator - LangChain-powered request routing with intent detection."""
import time
from typing import Dict, Any, List
import httpx
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from core.base_service import BaseService
from shared.models.orchestrator import (
    OrchestrationRequest, OrchestrationResponse, IntentType,
    IntentDetectionResult, RoutingDecision
)
from shared.models.core_gateway import LLMRequest, Message, ModelType
from shared.utils.logger import LogEmoji
from shared.config import settings


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

        # LangChain LLM for intent detection
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            self.llm = None
            self.logger.warning(f"{LogEmoji.WARNING} OpenAI API key not set, using fallback intent detection")

        # Intent detection prompt
        self.intent_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an intent classifier for a real estate AI assistant.
Classify the user's query into one of these intents:
- SEARCH: User wants to search for properties (e.g., "Tìm nhà 2 phòng ngủ", "Find apartments")
- CHAT: General conversation or questions (e.g., "Hello", "How are you?")
- CLASSIFY: User wants to classify a property type (e.g., "This is a villa")
- EXTRACT: User wants to extract property attributes
- PRICE_SUGGEST: User wants price suggestion
- COMPARE: User wants to compare properties
- RECOMMEND: User wants property recommendations
- UNKNOWN: Cannot determine intent

Extract any relevant entities like:
- bedrooms: number of bedrooms
- price_range: price range
- location: district or city
- property_type: apartment, house, villa, etc.

Respond with JSON format:
{{
  "intent": "INTENT_NAME",
  "confidence": 0.95,
  "entities": {{}}
}}"""),
            HumanMessage(content="{query}")
        ])

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
        """Detect user intent using LangChain."""
        if self.llm:
            try:
                # Use LangChain for intent detection
                prompt = self.intent_prompt.format(query=query)
                response = await self.llm.ainvoke(prompt)

                # Parse response
                import json
                result = json.loads(response.content)

                return IntentDetectionResult(
                    intent=IntentType(result["intent"].lower()),
                    confidence=result.get("confidence", 0.9),
                    extracted_entities=result.get("entities", {})
                )

            except Exception as e:
                self.logger.warning(f"{LogEmoji.WARNING} LangChain intent detection failed: {e}")

        # Fallback: Simple keyword-based intent detection
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in ["tìm", "find", "search", "tìm kiếm"]):
            return IntentDetectionResult(
                intent=IntentType.SEARCH,
                confidence=0.8,
                extracted_entities={}
            )
        elif any(keyword in query_lower for keyword in ["giá", "price", "bao nhiêu", "how much"]):
            return IntentDetectionResult(
                intent=IntentType.PRICE_SUGGEST,
                confidence=0.7,
                extracted_entities={}
            )
        else:
            return IntentDetectionResult(
                intent=IntentType.CHAT,
                confidence=0.6,
                extracted_entities={}
            )

    def _decide_routing(self, intent_result: IntentDetectionResult) -> RoutingDecision:
        """Decide which service to route to based on intent."""
        if intent_result.intent == IntentType.SEARCH:
            return RoutingDecision(
                intent=intent_result.intent,
                target_service="rag_service",
                endpoint="/rag",
                should_use_rag=True,
                extracted_params=intent_result.extracted_entities
            )
        elif intent_result.intent == IntentType.CLASSIFY:
            return RoutingDecision(
                intent=intent_result.intent,
                target_service="classification",
                endpoint="/classify",
                should_use_rag=False,
                extracted_params=intent_result.extracted_entities
            )
        else:
            # Default: use Core Gateway for chat
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
        if routing.should_use_rag:
            # Route to RAG service
            try:
                rag_url = f"{settings.get_db_gateway_url().replace('db-gateway', 'rag-service')}/rag"
                response = await self.http_client.post(
                    rag_url,
                    json={
                        "query": request.query,
                        "user_id": request.user_id,
                        "conversation_id": request.conversation_id
                    },
                    timeout=60.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("response", "")
            except Exception as e:
                self.logger.warning(f"{LogEmoji.WARNING} RAG service unavailable: {e}")

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

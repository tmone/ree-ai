"""
Classification Service - REFACTORED with New Utilities

Intent classification using LLM
"""
import uuid
import time
from typing import Dict, Any
from fastapi import HTTPException
from pydantic import BaseModel

from core.base_service import BaseService
from shared.config import settings
from shared.utils.logger import StructuredLogger, setup_logger
from shared.utils.http_client import HTTPClientFactory
from shared.utils.retry import retry_on_http_error
from shared.exceptions import ClassificationError, ServiceUnavailableError
from shared.models.base import QueryRequest


class ClassificationRequest(QueryRequest):
    """Classification request - inherits query validation"""
    pass


class ClassificationResponse(BaseModel):
    """Classification response"""
    intent: str
    confidence: float
    reasoning: str


class ClassificationService(BaseService):
    """
    Classification Service - Intent Detection with LLM

    REFACTORED with:
    - ✅ Shared HTTP Client Factory
    - ✅ Structured Logging with Request IDs
    - ✅ Retry Logic on failures
    - ✅ Custom Exceptions
    - ✅ Pydantic Validators
    """

    def __init__(self):
        super().__init__(
            name="classification",
            version="2.0.0",  # Refactored version
            capabilities=["intent_classification", "llm_classification"],
            port=8080
        )

        # REFACTORED: Use shared HTTP client factory
        self.http_client = HTTPClientFactory.create_classification_client()

        # REFACTORED: Structured logging
        raw_logger = setup_logger(self.name, level=settings.LOG_LEVEL)
        self.structured_logger = StructuredLogger(raw_logger, "CLASS")

        # Service URLs
        self.core_gateway_url = settings.get_core_gateway_url()

        self.logger.info(f"✅ Classification Service initialized (refactored)")
        self.logger.info(f"ℹ️  Core Gateway: {self.core_gateway_url}")

    def setup_routes(self):
        @self.app.post("/classify", response_model=ClassificationResponse)
        async def classify(request: ClassificationRequest):
            """Classify user intent with LLM"""
            # REFACTORED: Generate request ID for tracing
            request_id = str(uuid.uuid4())[:8]

            # REFACTORED: Structured logging
            self.structured_logger.log_request(
                request_id,
                "CLASSIFY",
                {"query": request.query}
            )

            start_time = time.time()

            try:
                # Call LLM for classification
                result = await self._classify_with_llm(request_id, request.query)

                duration_ms = (time.time() - start_time) * 1000

                # REFACTORED: Log performance
                self.structured_logger.log_performance(
                    request_id,
                    "classification",
                    duration_ms,
                    threshold_ms=1000
                )

                # REFACTORED: Log success
                self.structured_logger.log_success(
                    request_id,
                    "Classification complete",
                    {"intent": result["intent"], "confidence": result["confidence"]}
                )

                return ClassificationResponse(**result)

            except ClassificationError as e:
                # REFACTORED: Structured error logging
                self.structured_logger.log_error(request_id, e, {"query": request.query})
                raise HTTPException(status_code=e.status_code, detail=e.to_dict())

            except Exception as e:
                # REFACTORED: Log unexpected errors
                self.structured_logger.log_error(request_id, e, {"query": request.query})
                raise HTTPException(status_code=500, detail=str(e))

    @retry_on_http_error  # REFACTORED: Automatic retry
    async def _classify_with_llm(self, request_id: str, query: str) -> Dict[str, Any]:
        """
        Classify intent using LLM

        Automatically retries on network errors (via @retry_on_http_error)
        """
        import httpx

        system_prompt = """You are an intent classifier for a real estate platform.
Classify the user query into one of these intents:
- SEARCH: User wants to find/search for properties
- CHAT: General conversation, questions, greetings
- LISTING: User wants to create a property listing

Respond in JSON format:
{
    "intent": "SEARCH" | "CHAT" | "LISTING",
    "confidence": 0.0-1.0,
    "reasoning": "explanation"
}"""

        user_prompt = f"Classify this query: '{query}'"

        self.structured_logger.log_external_call(
            request_id, "CORE_GATEWAY", "/chat/completions"
        )

        try:
            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 200,
                    "temperature": 0.3
                }
            )
            response.raise_for_status()

            llm_response = response.json()
            content = llm_response.get("content", "")

            # Parse JSON response
            import json
            result = json.loads(content)

            return {
                "intent": result.get("intent", "CHAT").lower(),
                "confidence": result.get("confidence", 0.5),
                "reasoning": result.get("reasoning", "")
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                self.structured_logger.log_retry(
                    request_id, 1, 3, e, 2.0
                )
                raise  # Retry on 5xx
            else:
                raise ClassificationError(query, f"LLM returned {e.response.status_code}")

        except httpx.RequestError as e:
            raise ServiceUnavailableError("core_gateway", {"error": str(e)})

        except (json.JSONDecodeError, KeyError) as e:
            raise ClassificationError(query, f"Invalid LLM response: {e}")

    async def on_shutdown(self):
        await self.http_client.aclose()
        await super().on_shutdown()


# Create service instance
service = ClassificationService()
app = service.app

if __name__ == "__main__":
    service.run()

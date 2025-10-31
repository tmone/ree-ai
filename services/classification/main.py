"""
Classification Service - CTO Service #5
3 modes: filter / semantic / both
"""
from typing import Dict, Any, List
from enum import Enum
from pydantic import BaseModel
import httpx

from core.base_service import BaseService
from shared.models.core_gateway import LLMRequest, Message, ModelType
from shared.utils.logger import LogEmoji


class ClassificationMode(str, Enum):
    FILTER = "filter"
    SEMANTIC = "semantic"
    BOTH = "both"


class PropertyType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    VILLA = "villa"
    LAND = "land"
    COMMERCIAL = "commercial"
    UNKNOWN = "unknown"


class ClassificationRequest(BaseModel):
    text: str
    mode: ClassificationMode = ClassificationMode.BOTH


class ClassificationResult(BaseModel):
    property_type: PropertyType
    confidence: float
    mode_used: ClassificationMode
    filter_result: PropertyType = None
    semantic_result: PropertyType = None


class ClassificationService(BaseService):
    """
    Classification Service - CTO Service #5

    3 Modes:
    - filter: Rule-based keyword matching
    - semantic: LLM-based semantic understanding
    - both: Combine filter + semantic
    """

    def __init__(self):
        super().__init__(
            name="classification",
            version="1.0.0",
            capabilities=["property_classification", "filter", "semantic"],
            port=8102
        )

        self.http_client = httpx.AsyncClient(timeout=30.0)

        # Keyword filters for each property type
        self.keywords = {
            PropertyType.HOUSE: ["nhà", "nhà riêng", "nhà phố", "house"],
            PropertyType.APARTMENT: ["căn hộ", "chung cư", "apartment", "condo"],
            PropertyType.VILLA: ["biệt thự", "villa"],
            PropertyType.LAND: ["đất", "land", "lô đất"],
            PropertyType.COMMERCIAL: ["văn phòng", "office", "commercial", "mặt bằng kinh doanh"]
        }

    def setup_routes(self):
        """Setup Classification API routes"""

        @self.app.post("/classify", response_model=ClassificationResult)
        async def classify(request: ClassificationRequest):
            """
            Classify property type using 3 modes

            Modes:
            - filter: Fast keyword-based classification
            - semantic: LLM-based semantic classification
            - both: Combine both methods (recommended)
            """
            result = await self.classify_property(request.text, request.mode)
            return result

    async def classify_property(
        self,
        text: str,
        mode: ClassificationMode = ClassificationMode.BOTH
    ) -> ClassificationResult:
        """
        Classify property type

        Args:
            text: Property description
            mode: Classification mode (filter/semantic/both)

        Returns:
            ClassificationResult with property type and confidence
        """

        if mode == ClassificationMode.FILTER:
            # Mode 1: Filter only
            property_type = self._classify_by_filter(text)
            return ClassificationResult(
                property_type=property_type,
                confidence=0.7 if property_type != PropertyType.UNKNOWN else 0.3,
                mode_used=ClassificationMode.FILTER,
                filter_result=property_type
            )

        elif mode == ClassificationMode.SEMANTIC:
            # Mode 2: Semantic only
            property_type, confidence = await self._classify_by_semantic(text)
            return ClassificationResult(
                property_type=property_type,
                confidence=confidence,
                mode_used=ClassificationMode.SEMANTIC,
                semantic_result=property_type
            )

        else:  # Mode 3: BOTH
            # Combine filter and semantic
            filter_result = self._classify_by_filter(text)
            semantic_result, semantic_confidence = await self._classify_by_semantic(text)

            # Decision logic: Trust semantic if confidence high, else use filter
            if semantic_confidence > 0.8:
                final_type = semantic_result
                final_confidence = semantic_confidence
            elif filter_result != PropertyType.UNKNOWN:
                final_type = filter_result
                final_confidence = 0.75
            else:
                final_type = semantic_result
                final_confidence = semantic_confidence

            return ClassificationResult(
                property_type=final_type,
                confidence=final_confidence,
                mode_used=ClassificationMode.BOTH,
                filter_result=filter_result,
                semantic_result=semantic_result
            )

    def _classify_by_filter(self, text: str) -> PropertyType:
        """
        Mode 1: Filter - Rule-based keyword matching

        Fast but less accurate for ambiguous cases
        """
        text_lower = text.lower()

        # Count keyword matches for each type
        scores = {}
        for prop_type, keywords in self.keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[prop_type] = score

        # Return type with highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        else:
            return PropertyType.UNKNOWN

    async def _classify_by_semantic(self, text: str) -> tuple[PropertyType, float]:
        """
        Mode 2: Semantic - LLM-based semantic understanding

        More accurate but slower
        """
        try:
            # Call Core Gateway for LLM classification
            llm_request = LLMRequest(
                model=ModelType.GPT4_MINI,
                messages=[
                    Message(
                        role="system",
                        content="""Bạn là chuyên gia phân loại bất động sản.
Phân loại property vào 1 trong các loại sau:
- house: Nhà riêng, nhà phố
- apartment: Căn hộ, chung cư
- villa: Biệt thự
- land: Đất, lô đất
- commercial: Văn phòng, mặt bằng kinh doanh

Trả về JSON: {"type": "...", "confidence": 0.95}"""
                    ),
                    Message(role="user", content=f"Phân loại: {text}")
                ],
                max_tokens=50,
                temperature=0.3
            )

            # Make request to Core Gateway
            response = await self.http_client.post(
                "http://localhost:8080/chat/completions",
                json=llm_request.dict()
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")

                # Parse JSON response
                import json
                try:
                    result = json.loads(content)
                    prop_type = PropertyType(result.get("type", "unknown"))
                    confidence = float(result.get("confidence", 0.5))
                    return prop_type, confidence
                except:
                    pass

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Semantic classification error: {e}")

        # Fallback
        return PropertyType.UNKNOWN, 0.5

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()
        await super().on_shutdown()


if __name__ == "__main__":
    service = ClassificationService()
    service.run()

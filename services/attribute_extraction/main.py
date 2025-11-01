"""
Attribute Extraction Service - CTO Service #4 (Layer 3)
Extracts structured entities from raw user queries using LLM
"""
import httpx
import json
import re
from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from core.base_service import BaseService
from services.attribute_extraction.prompts import AttributeExtractionPrompts, PropertyAttributes
from shared.config import settings
from shared.utils.logger import LogEmoji


class QueryExtractionRequest(BaseModel):
    """Request to extract entities from user query"""
    query: str
    intent: Optional[str] = None  # SEARCH, COMPARE, etc.


class QueryExtractionResponse(BaseModel):
    """Response with extracted entities"""
    entities: Dict[str, Any]
    confidence: float
    extracted_from: str  # "query"


class AttributeExtractionService(BaseService):
    """
    Attribute Extraction Service - Layer 3
    Extracts structured entities from raw queries and property descriptions
    """

    def __init__(self):
        super().__init__(
            name="attribute_extraction",
            version="1.0.0",
            capabilities=["entity_extraction", "attribute_extraction", "query_parsing"],
            port=8080
        )

        self.http_client = httpx.AsyncClient(timeout=60.0)
        self.core_gateway_url = settings.get_core_gateway_url()
        self.logger.info(f"{LogEmoji.INFO} Using Core Gateway at: {self.core_gateway_url}")

    def setup_routes(self):
        """Setup API routes"""

        @self.app.post("/extract-query", response_model=QueryExtractionResponse)
        async def extract_from_query(request: QueryExtractionRequest):
            """
            Extract entities from user search query
            This is what Orchestrator should call for SEARCH intent!
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} Extracting entities from query: '{request.query}'")

                # Build specialized prompt for query extraction (not full property description)
                prompt = self._build_query_extraction_prompt(request.query, request.intent)

                # Call LLM via Core Gateway
                entities = await self._call_llm_for_extraction(prompt)

                confidence = self._calculate_confidence(entities)

                self.logger.info(f"{LogEmoji.SUCCESS} Extracted entities: {entities}")

                return QueryExtractionResponse(
                    entities=entities,
                    confidence=confidence,
                    extracted_from="query"
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Entity extraction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/extract-property", response_model=QueryExtractionResponse)
        async def extract_from_property_description(request: QueryExtractionRequest):
            """
            Extract full property attributes from property description/listing
            Used for data enrichment, not for user queries
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} Extracting from property description (length: {len(request.query)})")

                # Use full extraction prompt for property descriptions
                prompt = AttributeExtractionPrompts.build_extraction_prompt(request.query, include_examples=True)

                entities = await self._call_llm_for_extraction(prompt)
                confidence = self._calculate_confidence(entities)

                return QueryExtractionResponse(
                    entities=entities,
                    confidence=confidence,
                    extracted_from="property_description"
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Property extraction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def _build_query_extraction_prompt(self, query: str, intent: Optional[str] = None) -> str:
        """
        Build specialized prompt for extracting entities from USER QUERIES
        Simpler than full property extraction - focuses on search criteria
        """
        return f"""Bạn là chuyên gia trích xuất thông tin tìm kiếm bất động sản từ câu hỏi của người dùng.

🎯 NHIỆM VỤ:
Đọc câu hỏi của user và trích xuất CÁC TIÊU CHÍ TÌM KIẾM thành JSON.

📊 ENTITIES CẦN TRÍCH XUẤT (chỉ trích xuất những gì có trong câu hỏi):

**1. PROPERTY TYPE**
- property_type: căn hộ | nhà phố | biệt thự | đất | chung cư | commercial

**2. LOCATION**
- district: Quận/Huyện (chuẩn hóa)
  * "Q7", "Q.7", "quận 7" → "Quận 7"
  * "Q2" → "Quận 2"
  * "Bình Thạnh" → "Quận Bình Thạnh"
  * "Thủ Đức" → "Quận Thủ Đức"
- ward: Phường (nếu có)
- project_name: Tên dự án (Vinhomes, Masteri, etc.)

**3. PHYSICAL ATTRIBUTES**
- bedrooms: Số phòng ngủ
  * "2PN" → 2
  * "3 phòng ngủ" → 3
  * "2 phòng" → 2
- bathrooms: Số phòng tắm/WC
- area: Diện tích (m²)
- min_area: Diện tích tối thiểu
- max_area: Diện tích tối đa

**4. PRICE**
- price: Giá cụ thể (VND)
- min_price: Giá tối thiểu (VND)
- max_price: Giá tối đa (VND)

CHUẨN HÓA GIÁ:
  * "dưới 3 tỷ" → max_price: 3000000000
  * "từ 2 đến 5 tỷ" → min_price: 2000000000, max_price: 5000000000
  * "khoảng 3 tỷ" → price: 3000000000
  * "25 triệu/tháng" → price: 25000000

**5. FEATURES**
- furniture: full | cơ bản | không
- direction: Đông | Tây | Nam | Bắc | etc.

**6. AMENITIES**
- parking: true nếu có yêu cầu chỗ đậu xe
- elevator: true nếu có yêu cầu thang máy
- swimming_pool: true nếu có yêu cầu hồ bơi
- gym: true nếu có yêu cầu gym

🔍 EXTRACTION RULES:

1. **Chỉ trích xuất thông tin CÓ TRONG CÂU HỎI** - đừng bịa thêm
2. **Chuẩn hóa địa danh** về format chuẩn
3. **Chuẩn hóa giá** về số VND
4. **Nếu không có thông tin** → không đưa vào JSON (not null, just omit)
5. **Ưu tiên từ khóa rõ ràng** hơn từ khóa mơ hồ

📝 FEW-SHOT EXAMPLES:

Example 1:
Input: "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ"
Output: {{"property_type": "căn hộ", "bedrooms": 2, "district": "Quận 7", "max_price": 3000000000}}

Example 2:
Input: "Cần mua nhà phố Bình Thạnh khoảng 100m2"
Output: {{"property_type": "nhà phố", "district": "Quận Bình Thạnh", "area": 100}}

Example 3:
Input: "Tìm chung cư Vinhomes có hồ bơi"
Output: {{"property_type": "chung cư", "project_name": "Vinhomes", "swimming_pool": true}}

Example 4:
Input: "Biệt thự Q2 từ 10 đến 20 tỷ, có garage"
Output: {{"property_type": "biệt thự", "district": "Quận 2", "min_price": 10000000000, "max_price": 20000000000, "parking": true}}

📥 USER QUERY:
{query}

Intent: {intent or "SEARCH"}

📤 OUTPUT (chỉ JSON, không giải thích):
"""

    async def _call_llm_for_extraction(self, prompt: str) -> Dict[str, Any]:
        """Call LLM via Core Gateway to extract entities"""
        try:
            llm_request = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a structured data extraction expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.2  # Low temperature for consistent extraction
            }

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json=llm_request,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "").strip()

                # Clean up markdown code blocks
                content = re.sub(r'^```(?:json)?\s*\n?', '', content)
                content = re.sub(r'\n?```\s*$', '', content)
                content = content.strip()

                # Parse JSON
                entities = json.loads(content)
                return entities
            else:
                self.logger.warning(f"{LogEmoji.WARNING} Core Gateway returned {response.status_code}")
                return {}

        except json.JSONDecodeError as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to parse JSON: {e}")
            self.logger.error(f"Raw content: {content}")
            return {}
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} LLM call failed: {e}")
            return {}

    def _calculate_confidence(self, entities: Dict[str, Any]) -> float:
        """Calculate confidence score based on extracted entities"""
        if not entities:
            return 0.0

        # Simple confidence based on number of entities extracted
        num_entities = len(entities)
        if num_entities >= 4:
            return 0.95
        elif num_entities >= 3:
            return 0.85
        elif num_entities >= 2:
            return 0.75
        else:
            return 0.65

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()
        await super().on_shutdown()


# Create service instance at module level for uvicorn
service = AttributeExtractionService()
app = service.app

if __name__ == "__main__":
    service.run()

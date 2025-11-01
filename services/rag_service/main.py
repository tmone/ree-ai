"""
RAG Service - Layer 6
Retrieval-Augmented Generation for Real Estate Queries

Architecture Flow:
1. RETRIEVE: Get relevant properties from DB Gateway (via search)
2. AUGMENT: Build rich context from retrieved data
3. GENERATE: Use Core Gateway (LLM) to generate natural language response with context
"""
import httpx
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from core.base_service import BaseService
from shared.config import settings
from shared.utils.logger import LogEmoji


class RAGQueryRequest(BaseModel):
    """Request for RAG query"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 5


class RAGQueryResponse(BaseModel):
    """Response from RAG query"""
    response: str
    retrieved_count: int
    confidence: float
    sources: List[Dict[str, Any]] = []


class RAGService(BaseService):
    """
    RAG Service - Layer 6 (CTO Architecture)

    Implements full Retrieval-Augmented Generation pipeline:
    - Retrieve relevant properties from DB Gateway
    - Augment context with property data
    - Generate natural language response with Core Gateway
    """

    def __init__(self):
        super().__init__(
            name="rag_service",
            version="1.0.0",
            capabilities=["retrieval_augmented_generation", "context_building", "semantic_search"],
            port=8091
        )

        self.http_client = httpx.AsyncClient(timeout=60.0)
        self.db_gateway_url = settings.get_db_gateway_url()
        self.core_gateway_url = settings.get_core_gateway_url()

        self.logger.info(f"{LogEmoji.INFO} DB Gateway: {self.db_gateway_url}")
        self.logger.info(f"{LogEmoji.INFO} Core Gateway: {self.core_gateway_url}")

    def setup_routes(self):
        """Setup RAG API routes"""

        @self.app.post("/query", response_model=RAGQueryResponse)
        async def rag_query(request: RAGQueryRequest):
            """
            Main RAG endpoint - Full Retrieval-Augmented Generation

            This is what Orchestrator should call for SEARCH intent!
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} RAG Query: '{request.query}'")
                self.logger.info(f"{LogEmoji.INFO} Filters: {request.filters}")

                # STEP 1: RETRIEVE - Get relevant properties from DB Gateway
                retrieved_properties = await self._retrieve(request.query, request.filters, request.limit)

                self.logger.info(f"{LogEmoji.SUCCESS} Retrieved {len(retrieved_properties)} properties")

                if not retrieved_properties:
                    return RAGQueryResponse(
                        response="Xin lỗi, tôi không tìm thấy bất động sản phù hợp với yêu cầu của bạn.",
                        retrieved_count=0,
                        confidence=0.0,
                        sources=[]
                    )

                # STEP 2: AUGMENT - Build rich context from retrieved data
                context = self._build_context(retrieved_properties, request.query)

                self.logger.info(f"{LogEmoji.AI} Built context (length: {len(context)} chars)")

                # STEP 3: GENERATE - Use LLM to generate natural language response
                generated_response = await self._generate_response(
                    query=request.query,
                    context=context,
                    retrieved_properties=retrieved_properties
                )

                return RAGQueryResponse(
                    response=generated_response,
                    retrieved_count=len(retrieved_properties),
                    confidence=0.9,  # High confidence since we have retrieved data
                    sources=[
                        {
                            "property_id": prop.get("property_id"),
                            "title": prop.get("title"),
                            "price": prop.get("price")
                        }
                        for prop in retrieved_properties[:3]  # Top 3 sources
                    ]
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} RAG query failed: {e}")
                raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

    async def _retrieve(self, query: str, filters: Optional[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """
        STEP 1: RETRIEVE
        Get relevant properties from DB Gateway using search
        """
        try:
            search_request = {
                "query": query,
                "filters": filters or {},
                "limit": limit
            }

            self.logger.info(f"{LogEmoji.TARGET} Calling DB Gateway /search with filters: {filters}")

            response = await self.http_client.post(
                f"{self.db_gateway_url}/search",
                json=search_request,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                self.logger.info(f"{LogEmoji.SUCCESS} DB Gateway returned {len(results)} results")
                return results
            else:
                self.logger.warning(f"{LogEmoji.WARNING} DB Gateway returned {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Retrieval failed: {e}")
            return []

    def _build_context(self, properties: List[Dict[str, Any]], query: str) -> str:
        """
        STEP 2: AUGMENT
        Build rich context from retrieved properties
        """
        if not properties:
            return "Không có dữ liệu bất động sản phù hợp."

        context_parts = [
            "# DỮ LIỆU BẤT ĐỘNG SẢN TÌM ĐƯỢC\n",
            f"Tìm thấy {len(properties)} bất động sản phù hợp với yêu cầu: '{query}'\n\n"
        ]

        for i, prop in enumerate(properties, 1):
            context_parts.append(f"## BẤT ĐỘNG SẢN #{i}\n")
            context_parts.append(f"- **Tiêu đề**: {prop.get('title', 'N/A')}\n")

            # Price
            price = prop.get('price', 0)
            if price > 0:
                price_str = f"{price/1_000_000_000:.1f} tỷ VNĐ" if price >= 1_000_000_000 else f"{price/1_000_000:.0f} triệu VNĐ"
                context_parts.append(f"- **Giá**: {price_str}\n")

            # Location
            district = prop.get('district', 'N/A')
            ward = prop.get('ward', '')
            location_str = f"{ward}, {district}" if ward else district
            context_parts.append(f"- **Vị trí**: {location_str}\n")

            # Attributes
            if prop.get('bedrooms'):
                context_parts.append(f"- **Phòng ngủ**: {prop['bedrooms']}\n")
            if prop.get('bathrooms'):
                context_parts.append(f"- **Phòng tắm**: {prop['bathrooms']}\n")
            if prop.get('area'):
                context_parts.append(f"- **Diện tích**: {prop['area']} m²\n")

            # Description excerpt
            if prop.get('description'):
                desc = prop['description'][:200]
                context_parts.append(f"- **Mô tả**: {desc}...\n")

            context_parts.append("\n")

        return "".join(context_parts)

    async def _generate_response(self, query: str, context: str, retrieved_properties: List[Dict[str, Any]]) -> str:
        """
        STEP 3: GENERATE
        Use Core Gateway (LLM) to generate natural language response with augmented context
        """
        try:
            # Build prompt for LLM with retrieved context
            system_prompt = """Bạn là chuyên gia tư vấn bất động sản REE AI.

NHIỆM VỤ:
Dựa vào dữ liệu bất động sản được cung cấp, hãy tạo câu trả lời tự nhiên, hữu ích cho khách hàng.

QUY TẮC:
1. Giới thiệu ngắn gọn số lượng bất động sản tìm thấy
2. Nêu bật 2-3 bất động sản phù hợp nhất
3. Cung cấp thông tin chi tiết: giá, vị trí, diện tích, số phòng
4. Tư vấn thêm nếu phù hợp (xu hướng giá, tiện ích khu vực)
5. Kết thúc với câu hỏi hoặc lời mời hành động

PHONG CÁCH:
- Thân thiện, chuyên nghiệp
- Sử dụng tiếng Việt tự nhiên
- Không copy nguyên văn dữ liệu, hãy diễn đạt lại"""

            user_prompt = f"""Câu hỏi của khách hàng: {query}

{context}

Hãy tạo câu trả lời tự nhiên, hữu ích cho khách hàng dựa trên dữ liệu trên."""

            llm_request = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 800,
                "temperature": 0.7
            }

            self.logger.info(f"{LogEmoji.AI} Calling Core Gateway for generation...")

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json=llm_request,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("content", "").strip()
                self.logger.info(f"{LogEmoji.SUCCESS} Generated response (length: {len(generated_text)} chars)")
                return generated_text
            else:
                self.logger.warning(f"{LogEmoji.WARNING} Core Gateway returned {response.status_code}")
                # Fallback to simple formatting
                return self._format_simple_response(retrieved_properties)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Generation failed: {e}")
            # Fallback to simple formatting
            return self._format_simple_response(retrieved_properties)

    def _format_simple_response(self, properties: List[Dict[str, Any]]) -> str:
        """Fallback: Simple formatting without LLM generation"""
        if not properties:
            return "Xin lỗi, tôi không tìm thấy bất động sản phù hợp với yêu cầu của bạn."

        response_parts = [f"Tôi đã tìm thấy {len(properties)} bất động sản phù hợp:\n\n"]

        for i, prop in enumerate(properties, 1):
            price = prop.get('price', 0)
            price_str = f"{price/1_000_000_000:.1f} tỷ" if price > 0 else "Giá thỏa thuận"

            response_parts.append(f"{i}. **{prop.get('title', 'N/A')}**\n")
            response_parts.append(f"   - 💰 Giá: {price_str}\n")
            response_parts.append(f"   - 📍 Vị trí: {prop.get('district', 'N/A')}\n")

            if prop.get('bedrooms'):
                response_parts.append(f"   - 🛏️ {prop['bedrooms']} phòng ngủ\n")
            if prop.get('area'):
                response_parts.append(f"   - 📏 Diện tích: {prop['area']} m²\n")

            response_parts.append("\n")

        return "".join(response_parts)

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()
        await super().on_shutdown()


# Create service instance at module level for uvicorn
service = RAGService()
app = service.app

if __name__ == "__main__":
    service.run()

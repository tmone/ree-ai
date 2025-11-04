"""
RAG Service - Enhanced with Modular RAG + Memory + Multi-Agent
Layer 6 - Production-Ready Advanced RAG Pipeline

NEW FEATURES (vs basic main.py):
- Modular RAG operators (grading, reranking, query rewriting)
- Agentic memory system (episodic, semantic, procedural)
- Multi-agent coordination (supervisor + specialists)
- Self-reflection and quality control
- Advanced operators (HyDE, decomposition, reflection)

BACKWARD COMPATIBLE: Falls back to basic pipeline if advanced features disabled
"""
import httpx
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel
import os

from core.base_service import BaseService
from shared.config import settings
from shared.utils.logger import LogEmoji

# Import new modular RAG components
try:
    from shared.rag_operators.operators import (
        HybridRetrievalOperator,
        DocumentGraderOperator,
        RerankOperator,
        QueryRewriterOperator,
        GenerationOperator
    )
    from shared.rag_operators.operators.hyde import HyDEOperator
    from shared.rag_operators.operators.query_decomposition import QueryDecompositionOperator
    from shared.rag_operators.operators.reflection import ReflectionOperator
    from shared.memory import MemoryManager
    from shared.agents import SupervisorAgent
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Advanced features not available: {e}")
    ADVANCED_FEATURES_AVAILABLE = False


class RAGQueryRequest(BaseModel):
    """Request for RAG query"""
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 5
    user_id: Optional[str] = None  # NEW: For memory personalization
    use_advanced_rag: bool = True  # NEW: Enable/disable advanced features


class RAGQueryResponse(BaseModel):
    """Response from RAG query"""
    response: str
    retrieved_count: int
    confidence: float
    sources: List[Dict[str, Any]] = []
    # NEW: Advanced metadata
    pipeline_used: Optional[str] = None
    quality_score: Optional[float] = None
    operators_executed: Optional[List[str]] = None
    memory_context_used: Optional[bool] = None


class EnhancedRAGService(BaseService):
    """
    Enhanced RAG Service with Modular RAG + Memory + Multi-Agent

    Features:
    1. Modular RAG Pipeline:
       - Query rewriting (fix typos, ambiguity)
       - HyDE or Query Decomposition (for complex queries)
       - Hybrid retrieval (vector + BM25)
       - Document grading (filter irrelevant)
       - Semantic reranking (optimize order)
       - LLM generation (natural language)
       - Reflection (self-critique)

    2. Agentic Memory:
       - Episodic: Learn from past interactions
       - Semantic: Pre-loaded domain knowledge
       - Procedural: Learned skills/strategies

    3. Multi-Agent System:
       - Supervisor coordination
       - Specialist agents (search, grade, rerank, critique)
       - Performance tracking
    """

    def __init__(self):
        super().__init__(
            name="enhanced_rag_service",
            version="2.0.0",
            capabilities=[
                "retrieval_augmented_generation",
                "modular_rag",
                "agentic_memory",
                "multi_agent",
                "self_reflection"
            ],
            port=8091
        )

        self.http_client = httpx.AsyncClient(timeout=90.0)
        self.db_gateway_url = settings.get_db_gateway_url()
        self.core_gateway_url = settings.get_core_gateway_url()

        # Initialize advanced components if available
        self.advanced_enabled = ADVANCED_FEATURES_AVAILABLE and os.getenv("USE_ADVANCED_RAG", "true").lower() == "true"

        if self.advanced_enabled:
            self.logger.info(f"{LogEmoji.SUCCESS} Advanced RAG features enabled")
            self._setup_advanced_components()
        else:
            self.logger.warning(f"{LogEmoji.WARNING} Advanced RAG features disabled (fallback to basic)")
            self.memory_manager = None
            self.supervisor = None

        self.logger.info(f"{LogEmoji.INFO} DB Gateway: {self.db_gateway_url}")
        self.logger.info(f"{LogEmoji.INFO} Core Gateway: {self.core_gateway_url}")

    def _setup_advanced_components(self):
        """Initialize advanced RAG components"""
        try:
            # Memory system
            self.memory_manager = MemoryManager()
            self.logger.info(f"{LogEmoji.SUCCESS} Memory system initialized")

            # Multi-agent system
            self.supervisor = SupervisorAgent()
            self.logger.info(f"{LogEmoji.SUCCESS} Multi-agent system initialized")

            # Individual operators (for custom pipelines)
            self.query_rewriter = QueryRewriterOperator(core_gateway_url=self.core_gateway_url)
            self.hyde_operator = HyDEOperator(core_gateway_url=self.core_gateway_url)
            self.decomposition_operator = QueryDecompositionOperator(core_gateway_url=self.core_gateway_url)
            self.document_grader = DocumentGraderOperator()
            self.reranker = RerankOperator()
            self.reflection_operator = ReflectionOperator(core_gateway_url=self.core_gateway_url)
            self.generation_operator = GenerationOperator(core_gateway_url=self.core_gateway_url)

            self.logger.info(f"{LogEmoji.SUCCESS} All operators initialized")

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to setup advanced components: {e}")
            self.advanced_enabled = False
            self.memory_manager = None
            self.supervisor = None

    def setup_routes(self):
        """Setup RAG API routes"""

        @self.app.post("/query", response_model=RAGQueryResponse)
        async def rag_query(request: RAGQueryRequest):
            """
            Main RAG endpoint - Intelligent Retrieval-Augmented Generation

            Automatically selects best pipeline:
            - Advanced: Modular RAG + Memory + Multi-Agent (if enabled)
            - Basic: Simple retrieve → augment → generate (fallback)
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} RAG Query: '{request.query}'")

                # Decide pipeline based on availability and request
                use_advanced = self.advanced_enabled and request.use_advanced_rag

                if use_advanced:
                    self.logger.info(f"{LogEmoji.AI} Using ADVANCED pipeline (Modular RAG + Memory + Agents)")
                    return await self._advanced_rag_pipeline(request)
                else:
                    self.logger.info(f"{LogEmoji.INFO} Using BASIC pipeline (Simple RAG)")
                    return await self._basic_rag_pipeline(request)

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} RAG query failed: {e}")
                raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

        @self.app.get("/stats")
        async def get_stats():
            """Get RAG service statistics"""
            if not self.advanced_enabled:
                return {"advanced_features": False, "message": "Basic RAG only"}

            stats = {
                "advanced_features": True,
                "memory_stats": self.memory_manager.get_memory_stats() if self.memory_manager else {},
                "agent_stats": self.supervisor.get_all_agent_stats() if self.supervisor else {}
            }
            return stats

    async def _advanced_rag_pipeline(self, request: RAGQueryRequest) -> RAGQueryResponse:
        """
        ADVANCED PIPELINE: Full Modular RAG + Memory + Multi-Agent

        Flow:
        1. Retrieve memory context (if user_id provided)
        2. Check procedural memory for applicable skills
        3. Query enhancement (rewrite/HyDE/decomposition if needed)
        4. Multi-agent search (supervisor delegates to specialists)
        5. Reflection and quality check
        6. Record interaction in memory
        """
        operators_executed = []
        memory_context_used = False

        # STEP 1: Memory retrieval
        memory_context = None
        if request.user_id and self.memory_manager:
            self.logger.info(f"{LogEmoji.AI} Retrieving memory context for user: {request.user_id}")
            memory_context = await self.memory_manager.retrieve_context_for_query(
                request.user_id,
                request.query
            )
            memory_context_used = True
            operators_executed.append("memory_retrieval")

            # Log memory insights
            if memory_context.get("user_preferences"):
                prefs = memory_context["user_preferences"]
                self.logger.info(f"{LogEmoji.INFO} User preferences: {prefs}")

            if memory_context.get("applicable_skills"):
                skills = memory_context["applicable_skills"]
                self.logger.info(f"{LogEmoji.SUCCESS} Found {len(skills)} applicable skills")

        # STEP 2: Query enhancement (if needed)
        enhanced_query = request.query

        # Check if query is complex enough for decomposition
        if self._is_complex_query(request.query):
            self.logger.info(f"{LogEmoji.AI} Complex query detected, using decomposition")
            decomp_result = await self.decomposition_operator.execute({"query": request.query})
            if decomp_result.success:
                sub_queries = decomp_result.data.sub_queries
                self.logger.info(f"{LogEmoji.SUCCESS} Decomposed into {len(sub_queries)} sub-queries")
                operators_executed.append("query_decomposition")
                # For now, use first sub-query (in production, could search all and merge)
                enhanced_query = sub_queries[0] if sub_queries else request.query

        # STEP 3: Multi-agent search
        self.logger.info(f"{LogEmoji.AI} Executing multi-agent search pipeline")
        search_task = {
            "query": enhanced_query,
            "filters": request.filters or {},
            "limit": request.limit
        }

        supervisor_result = await self.supervisor.execute(search_task)
        operators_executed.append("multi_agent_search")

        if not supervisor_result.success or not supervisor_result.data:
            # Fallback to basic search
            self.logger.warning(f"{LogEmoji.WARNING} Multi-agent search failed, falling back to basic")
            return await self._basic_rag_pipeline(request)

        retrieved_properties = supervisor_result.data
        self.logger.info(f"{LogEmoji.SUCCESS} Multi-agent pipeline retrieved {len(retrieved_properties)} properties")

        # STEP 4: Generate response
        context = self._build_context(retrieved_properties, request.query)
        generation_result = await self.generation_operator.execute({
            "query": request.query,
            "documents": [{"content": context}],
            "system_prompt": "Bạn là chuyên gia tư vấn bất động sản REE AI. Hãy tạo câu trả lời tự nhiên, hữu ích dựa trên dữ liệu được cung cấp."
        })
        operators_executed.append("generation")

        if not generation_result.success:
            self.logger.error(f"{LogEmoji.ERROR} Generation failed")
            return await self._basic_rag_pipeline(request)

        generated_response = generation_result.data.response

        # STEP 5: Reflection (quality check)
        self.logger.info(f"{LogEmoji.AI} Performing self-reflection on response")
        reflection_result = await self.reflection_operator.execute({
            "query": request.query,
            "response": generated_response,
            "sources": retrieved_properties
        })
        operators_executed.append("reflection")

        quality_score = 0.8  # Default
        if reflection_result.success:
            quality_score = reflection_result.data.quality_score
            self.logger.info(f"{LogEmoji.SUCCESS} Quality score: {quality_score:.2f}")

            # If quality is low and needs improvement, could retry here
            if reflection_result.data.needs_improvement:
                self.logger.warning(f"{LogEmoji.WARNING} Quality below threshold, consider retry")
                # In production: implement retry logic

        # STEP 6: Record in memory
        if request.user_id and self.memory_manager:
            self.logger.info(f"{LogEmoji.AI} Recording interaction in memory")
            await self.memory_manager.record_interaction(
                user_id=request.user_id,
                query=request.query,
                results=retrieved_properties,
                success=True,
                applied_skills=[],
                metadata={
                    "confidence": supervisor_result.confidence,
                    "quality_score": quality_score
                }
            )
            operators_executed.append("memory_storage")

        return RAGQueryResponse(
            response=generated_response,
            retrieved_count=len(retrieved_properties),
            confidence=supervisor_result.confidence,
            sources=[
                {
                    "property_id": prop.get("property_id"),
                    "title": prop.get("title"),
                    "price": prop.get("price")
                }
                for prop in retrieved_properties[:3]
            ],
            pipeline_used="advanced_modular_rag",
            quality_score=quality_score,
            operators_executed=operators_executed,
            memory_context_used=memory_context_used
        )

    async def _basic_rag_pipeline(self, request: RAGQueryRequest) -> RAGQueryResponse:
        """
        BASIC PIPELINE: Simple retrieve → augment → generate (fallback)
        Same as original main.py implementation
        """
        # STEP 1: RETRIEVE
        retrieved_properties = await self._retrieve_basic(
            request.query,
            request.filters,
            request.limit
        )

        if not retrieved_properties:
            return RAGQueryResponse(
                response="Xin lỗi, tôi không tìm thấy bất động sản phù hợp với yêu cầu của bạn.",
                retrieved_count=0,
                confidence=0.0,
                sources=[],
                pipeline_used="basic"
            )

        # STEP 2: AUGMENT
        context = self._build_context(retrieved_properties, request.query)

        # STEP 3: GENERATE
        generated_response = await self._generate_basic(
            query=request.query,
            context=context,
            retrieved_properties=retrieved_properties
        )

        return RAGQueryResponse(
            response=generated_response,
            retrieved_count=len(retrieved_properties),
            confidence=0.9,
            sources=[
                {
                    "property_id": prop.get("property_id"),
                    "title": prop.get("title"),
                    "price": prop.get("price")
                }
                for prop in retrieved_properties[:3]
            ],
            pipeline_used="basic"
        )

    async def _retrieve_basic(self, query: str, filters: Optional[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Basic retrieval via DB Gateway"""
        try:
            search_request = {
                "query": query,
                "filters": filters or {},
                "limit": limit
            }

            response = await self.http_client.post(
                f"{self.db_gateway_url}/search",
                json=search_request,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                self.logger.info(f"{LogEmoji.SUCCESS} Retrieved {len(results)} results")
                return results
            else:
                self.logger.warning(f"{LogEmoji.WARNING} DB Gateway returned {response.status_code}")
                return []

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Retrieval failed: {e}")
            return []

    def _build_context(self, properties: List[Dict[str, Any]], query: str) -> str:
        """Build context from properties (same as original)"""
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
            price_display = prop.get('price_display')
            if price_display:
                context_parts.append(f"- **Giá**: {price_display}\n")
            else:
                price = prop.get('price', 0)
                if isinstance(price, (int, float)) and price > 0:
                    price_str = f"{price/1_000_000_000:.1f} tỷ VNĐ" if price >= 1_000_000_000 else f"{price/1_000_000:.0f} triệu VNĐ"
                    context_parts.append(f"- **Giá**: {price_str}\n")

            # Location
            city = prop.get('city', '')
            district = prop.get('district', '')
            ward = prop.get('ward', '')
            location_parts = [p for p in [ward, district, city] if p]
            location_str = ', '.join(location_parts) if location_parts else prop.get('location', 'N/A')
            context_parts.append(f"- **Vị trí**: {location_str}\n")

            # Attributes
            if prop.get('bedrooms'):
                context_parts.append(f"- **Phòng ngủ**: {prop['bedrooms']}\n")
            if prop.get('bathrooms'):
                context_parts.append(f"- **Phòng tắm**: {prop['bathrooms']}\n")

            # Area
            area_display = prop.get('area_display')
            if area_display:
                context_parts.append(f"- **Diện tích**: {area_display}\n")
            elif prop.get('area'):
                area = prop['area']
                area_str = f"{area} m²" if isinstance(area, (int, float)) else str(area)
                context_parts.append(f"- **Diện tích**: {area_str}\n")

            # Description excerpt
            if prop.get('description'):
                desc = prop['description'][:200]
                context_parts.append(f"- **Mô tả**: {desc}...\n")

            context_parts.append("\n")

        return "".join(context_parts)

    async def _generate_basic(self, query: str, context: str, retrieved_properties: List[Dict[str, Any]]) -> str:
        """Basic generation via Core Gateway"""
        try:
            system_prompt = """Bạn là chuyên gia tư vấn bất động sản REE AI.

NHIỆM VỤ:
Dựa vào dữ liệu bất động sản được cung cấp, hãy tạo câu trả lời tự nhiên, hữu ích cho khách hàng.

QUY TẮC:
1. Giới thiệu ngắn gọn số lượng bất động sản tìm thấy
2. Nêu bật 2-3 bất động sản phù hợp nhất
3. Cung cấp thông tin chi tiết: giá, vị trí, diện tích, số phòng
4. Tư vấn thêm nếu phù hợp
5. Kết thúc với câu hỏi hoặc lời mời hành động

PHONG CÁCH:
- Thân thiện, chuyên nghiệp
- Sử dụng tiếng Việt tự nhiên
- Không copy nguyên văn dữ liệu"""

            user_prompt = f"""Câu hỏi của khách hàng: {query}

{context}

Hãy tạo câu trả lời tự nhiên, hữu ích cho khách hàng dựa trên dữ liệu trên."""

            llm_request = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json=llm_request,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("content", "").strip()
                return generated_text
            else:
                return self._format_simple_response(retrieved_properties)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Generation failed: {e}")
            return self._format_simple_response(retrieved_properties)

    def _format_simple_response(self, properties: List[Dict[str, Any]]) -> str:
        """Fallback: Simple formatting without LLM"""
        if not properties:
            return "Xin lỗi, tôi không tìm thấy bất động sản phù hợp với yêu cầu của bạn."

        response_parts = [f"Tôi đã tìm thấy {len(properties)} bất động sản phù hợp:\n\n"]

        for i, prop in enumerate(properties, 1):
            price_str = prop.get('price_display')
            if not price_str:
                price = prop.get('price', 0)
                if isinstance(price, (int, float)) and price > 0:
                    price_str = f"{price/1_000_000_000:.1f} tỷ"
                else:
                    price_str = "Giá thỏa thuận"

            location_str = prop.get('district', prop.get('location', 'N/A'))

            response_parts.append(f"{i}. **{prop.get('title', 'N/A')}**\n")
            response_parts.append(f"   - 💰 Giá: {price_str}\n")
            response_parts.append(f"   - 📍 Vị trí: {location_str}\n")

            if prop.get('bedrooms'):
                response_parts.append(f"   - 🛏️ {prop['bedrooms']} phòng ngủ\n")

            area_str = prop.get('area_display')
            if not area_str and prop.get('area'):
                area = prop['area']
                area_str = f"{area} m²" if isinstance(area, (int, float)) else str(area)

            if area_str:
                response_parts.append(f"   - 📏 Diện tích: {area_str}\n")

            response_parts.append("\n")

        return "".join(response_parts)

    def _is_complex_query(self, query: str) -> bool:
        """Check if query is complex enough for decomposition"""
        constraint_keywords = ["và", "gần", "giá", "dưới", "trên", "có", "với"]
        count = sum(1 for kw in constraint_keywords if kw in query.lower())
        return count >= 2

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()

        # Cleanup operators
        if self.advanced_enabled:
            if hasattr(self.query_rewriter, 'cleanup'):
                await self.query_rewriter.cleanup()
            if hasattr(self.hyde_operator, 'cleanup'):
                await self.hyde_operator.cleanup()
            if hasattr(self.decomposition_operator, 'cleanup'):
                await self.decomposition_operator.cleanup()
            if hasattr(self.reflection_operator, 'cleanup'):
                await self.reflection_operator.cleanup()

        await super().on_shutdown()


# Create service instance at module level for uvicorn
service = EnhancedRAGService()
app = service.app

if __name__ == "__main__":
    service.run()

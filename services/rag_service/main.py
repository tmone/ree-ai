"""
RAG Service - Unified Basic + Advanced Pipeline
Layer 6 - Production-Ready with Feature Flag

FEATURES:
- BASIC Mode: Simple retrieve → augment → generate (default)
- ADVANCED Mode: Modular RAG + Memory + Multi-Agent (via USE_ADVANCED_RAG=true)

BACKWARD COMPATIBLE: Falls back to basic pipeline if advanced components unavailable
"""
import os
import uuid
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field

from core.base_service import BaseService
from shared.config import settings
from shared.utils.logger import LogEmoji, StructuredLogger, setup_logger
from shared.utils.http_client import HTTPClientFactory
from shared.utils.retry import retry_on_http_error
from shared.exceptions import ServiceUnavailableError, RAGPipelineError
from shared.utils.i18n_loader import get_i18n_loader

# Load master data using i18n_loader - NEVER hardcode display names or field labels!
i18n_loader = get_i18n_loader()
LISTING_TYPE_DISPLAY = i18n_loader.get_listing_type_display('vi')
FIELD_LABELS = i18n_loader.get_field_labels('vi')

# Try importing advanced RAG components
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
    user_id: Optional[str] = None  # For memory personalization
    use_advanced_rag: bool = True  # Enable/disable advanced features per request


class RAGQueryResponse(BaseModel):
    """Response from RAG query"""
    response: str
    retrieved_count: int
    confidence: float
    sources: List[Dict[str, Any]] = []
    # Advanced metadata (populated only in advanced mode)
    pipeline_used: Optional[str] = None
    quality_score: Optional[float] = None
    operators_executed: Optional[List[str]] = None
    memory_context_used: Optional[bool] = None
    # NEW: Full property data for frontend rendering (Structured Response Format)
    properties: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Full property data for frontend components (property cards, etc.)"
    )


class RAGService(BaseService):
    """
    RAG Service - Unified Basic + Advanced Pipeline

    BASIC Pipeline (default):
        1. RETRIEVE: Get relevant properties from DB Gateway
        2. AUGMENT: Build rich context from retrieved data
        3. GENERATE: Use Core Gateway (LLM) to generate natural language response

    ADVANCED Pipeline (USE_ADVANCED_RAG=true):
        1. Memory retrieval (episodic, semantic, procedural)
        2. Query enhancement (rewriting, HyDE, decomposition)
        3. Multi-agent search (supervisor + specialists)
        4. Document grading and reranking
        5. LLM generation with reflection
        6. Memory storage for future personalization
    """

    def __init__(self):
        super().__init__(
            name="rag_service",
            version="2.0.0",  # Unified version
            capabilities=[
                "retrieval_augmented_generation",
                "basic_rag",
                "modular_rag",
                "agentic_memory",
                "multi_agent"
            ],
            port=8080
        )

        # REFACTORED: Use shared HTTP client factory with RAG-optimized timeout
        self.http_client = HTTPClientFactory.create_rag_client()

        # Service URLs
        self.db_gateway_url = settings.get_db_gateway_url()
        self.core_gateway_url = settings.get_core_gateway_url()

        # REFACTORED: Use structured logging
        raw_logger = setup_logger("rag_service", level=settings.LOG_LEVEL)
        self.structured_logger = StructuredLogger(raw_logger, "RAG")

        # Feature flag: Enable advanced features based on env var
        self.advanced_enabled = (
            ADVANCED_FEATURES_AVAILABLE and
            os.getenv("USE_ADVANCED_RAG", "false").lower() == "true"
        )

        if self.advanced_enabled:
            self.logger.info(f"{LogEmoji.SUCCESS} Advanced RAG mode enabled")
            self._init_advanced_components()
        else:
            self.logger.info(f"{LogEmoji.INFO} Basic RAG mode (set USE_ADVANCED_RAG=true for advanced)")
            self.memory_manager = None
            self.supervisor = None

        self.logger.info(f"{LogEmoji.INFO} DB Gateway: {self.db_gateway_url}")
        self.logger.info(f"{LogEmoji.INFO} Core Gateway: {self.core_gateway_url}")

    def _init_advanced_components(self):
        """Initialize advanced RAG components (modular operators, memory, agents)"""
        try:
            # Memory system
            self.memory_manager = MemoryManager()
            self.logger.info(f"{LogEmoji.SUCCESS} Memory system initialized")

            # Multi-agent system
            self.supervisor = SupervisorAgent()
            self.logger.info(f"{LogEmoji.SUCCESS} Multi-agent system initialized")

            # Individual operators for custom pipelines
            self.query_rewriter = QueryRewriterOperator(core_gateway_url=self.core_gateway_url)
            self.hyde_operator = HyDEOperator(core_gateway_url=self.core_gateway_url)
            self.decomposition_operator = QueryDecompositionOperator(core_gateway_url=self.core_gateway_url)
            self.document_grader = DocumentGraderOperator()
            self.reranker = RerankOperator()
            self.reflection_operator = ReflectionOperator(core_gateway_url=self.core_gateway_url)
            self.generation_operator = GenerationOperator(core_gateway_url=self.core_gateway_url)

            self.logger.info(f"{LogEmoji.SUCCESS} All modular operators initialized")

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
                    return await self._advanced_pipeline(request)
                else:
                    self.logger.info(f"{LogEmoji.INFO} Using BASIC pipeline (Simple RAG)")
                    return await self._basic_pipeline(request)

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} RAG query failed: {e}")
                raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

        @self.app.get("/stats")
        async def get_stats():
            """Get RAG service statistics"""
            if not self.advanced_enabled:
                return {
                    "advanced_features": False,
                    "pipeline": "basic",
                    "message": "Set USE_ADVANCED_RAG=true to enable advanced features"
                }

            stats = {
                "advanced_features": True,
                "pipeline": "advanced",
                "memory_stats": self.memory_manager.get_memory_stats() if self.memory_manager else {},
                "agent_stats": self.supervisor.get_all_agent_stats() if self.supervisor else {}
            }
            return stats

    # ==================== ADVANCED PIPELINE ====================

    async def _advanced_pipeline(self, request: RAGQueryRequest) -> RAGQueryResponse:
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
                self.logger.info(f"{LogEmoji.INFO} User preferences: {memory_context['user_preferences']}")
            if memory_context.get("applicable_skills"):
                self.logger.info(f"{LogEmoji.SUCCESS} Found {len(memory_context['applicable_skills'])} applicable skills")

        # STEP 2: Query enhancement
        enhanced_query = request.query

        if self._is_complex_query(request.query):
            self.logger.info(f"{LogEmoji.AI} Complex query detected, using decomposition")
            decomp_result = await self.decomposition_operator.execute({"query": request.query})
            if decomp_result.success:
                sub_queries = decomp_result.data.sub_queries
                self.logger.info(f"{LogEmoji.SUCCESS} Decomposed into {len(sub_queries)} sub-queries")
                operators_executed.append("query_decomposition")
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
            self.logger.warning(f"{LogEmoji.WARNING} Multi-agent search failed, falling back to basic")
            return await self._basic_pipeline(request)

        retrieved_properties = supervisor_result.data
        self.logger.info(f"{LogEmoji.SUCCESS} Retrieved {len(retrieved_properties)} properties")

        # STEP 4: Generate response
        context = self._build_context(retrieved_properties, request.query)
        generation_result = await self.generation_operator.execute({
            "query": request.query,
            "documents": [{"content": context}],
            "system_prompt": "Bạn là chuyên gia tư vấn bất động sản REE AI. Hãy tạo câu trả lời tự nhiên, hữu ích."
        })
        operators_executed.append("generation")

        if not generation_result.success:
            self.logger.error(f"{LogEmoji.ERROR} Generation failed")
            return await self._basic_pipeline(request)

        generated_response = generation_result.data.response

        # STEP 5: Reflection (quality check)
        self.logger.info(f"{LogEmoji.AI} Performing self-reflection")
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

        # STEP 6: Record in memory
        if request.user_id and self.memory_manager:
            await self.memory_manager.record_interaction(
                user_id=request.user_id,
                query=request.query,
                results=retrieved_properties,
                success=True,
                applied_skills=[],
                metadata={"confidence": supervisor_result.confidence, "quality_score": quality_score}
            )
            operators_executed.append("memory_storage")

        # DEBUG: Log properties before returning
        self.logger.info(f"{LogEmoji.INFO} Advanced pipeline returning {len(retrieved_properties)} properties")
        self.logger.info(f"{LogEmoji.INFO} First property sample: {retrieved_properties[0] if retrieved_properties else 'None'}")

        # NEW: Return properties data for Structured Response Format
        # Frontend will handle rendering, backend just provides data
        response_obj = RAGQueryResponse(
            response=generated_response,  # Clean text response without embedded HTML
            retrieved_count=len(retrieved_properties),
            confidence=supervisor_result.confidence,
            sources=[
                {"property_id": p.get("property_id"), "title": p.get("title"), "price": p.get("price")}
                for p in retrieved_properties[:3]
            ],
            pipeline_used="advanced",
            quality_score=quality_score,
            properties=retrieved_properties,  # Full property data for frontend
            operators_executed=operators_executed,
            memory_context_used=memory_context_used
        )

        # DEBUG: Log response dict to see if properties is included
        response_dict = response_obj.dict()
        self.logger.info(f"{LogEmoji.INFO} Response dict keys: {response_dict.keys()}")
        self.logger.info(f"{LogEmoji.INFO} Properties in response dict: {len(response_dict.get('properties', [])) if response_dict.get('properties') else 0}")

        return response_obj

    # ==================== BASIC PIPELINE ====================

    async def _basic_pipeline(self, request: RAGQueryRequest) -> RAGQueryResponse:
        """
        BASIC PIPELINE: Simple retrieve → augment → generate

        This is the default fallback pipeline that always works.
        No dependencies on advanced components.
        """
        # STEP 1: RETRIEVE
        retrieved_properties = await self._retrieve(
            request.query,
            request.filters,
            request.limit
        )

        if not retrieved_properties:
            no_results_msg = i18n_loader.get_ui_message('no_results', 'vi')
            return RAGQueryResponse(
                response=no_results_msg,
                retrieved_count=0,
                confidence=0.0,
                sources=[],
                pipeline_used="basic"
            )

        self.logger.info(f"{LogEmoji.SUCCESS} Retrieved {len(retrieved_properties)} properties")

        # STEP 2: AUGMENT - Build rich context
        context = self._build_context(retrieved_properties, request.query)

        # STEP 3: GENERATE - Use LLM to create natural response
        generated_response = await self._generate(
            query=request.query,
            context=context,
            retrieved_properties=retrieved_properties
        )

        # NEW: Return properties data for Structured Response Format
        # Frontend will handle rendering, backend just provides data
        return RAGQueryResponse(
            response=generated_response,  # Clean text response without embedded HTML
            retrieved_count=len(retrieved_properties),
            confidence=0.9,
            sources=[
                {"property_id": p.get("property_id"), "title": p.get("title"), "price": p.get("price")}
                for p in retrieved_properties[:3]
            ],
            pipeline_used="basic",
            properties=retrieved_properties  # Full property data for frontend
        )

    # ==================== SHARED UTILITIES ====================

    @retry_on_http_error  # REFACTORED: Automatic retry on network errors
    async def _retrieve(self, query: str, filters: Optional[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """
        STEP 1: RETRIEVE
        Get relevant properties from DB Gateway using search

        Automatically retries on network errors and 5xx responses (via @retry_on_http_error)
        """
        import httpx  # Import for exception handling

        search_request = {
            "query": query,
            "filters": filters or {},
            "limit": limit
        }

        self.logger.info(f"{LogEmoji.TARGET} Calling DB Gateway /search")

        try:
            response = await self.http_client.post(
                f"{self.db_gateway_url}/search",
                json=search_request,
                timeout=30.0
            )
            response.raise_for_status()  # Raise on 4xx/5xx

            data = response.json()
            results = data.get("results", [])
            return results

        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                # 5xx errors will be retried by decorator
                self.logger.warning(f"{LogEmoji.WARNING} DB Gateway returned {e.response.status_code}, will retry")
                raise  # Re-raise for retry
            else:
                # 4xx errors should not be retried
                self.logger.warning(f"{LogEmoji.WARNING} DB Gateway returned {e.response.status_code} (client error)")
                return []

        except httpx.RequestError as e:
            # Network errors will be retried by decorator
            self.logger.error(f"{LogEmoji.ERROR} Network error: {e}, will retry")
            raise ServiceUnavailableError("db_gateway", {"original_error": str(e)})

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
            # Use i18n field labels from master data
            context_parts.append(f"- **{FIELD_LABELS['title']}**: {prop.get('title', 'N/A')}\n")

            # Listing Type - CRITICAL: Show sale/rent info using master data
            listing_type = prop.get('listing_type', 'N/A')
            if listing_type != 'N/A':
                # Get display name from master data (never hardcode!)
                listing_type_display = LISTING_TYPE_DISPLAY.get(listing_type, listing_type)
                context_parts.append(f"- **{FIELD_LABELS['listing_type']}**: {listing_type_display}\n")

            # Price - use price_display if available (normalized format)
            price_display = prop.get('price_display')
            if price_display:
                context_parts.append(f"- **{FIELD_LABELS['price']}**: {price_display}\n")
            else:
                price = prop.get('price', 0)
                if isinstance(price, (int, float)) and price > 0:
                    price_str = f"{price/1_000_000_000:.1f} tỷ VNĐ" if price >= 1_000_000_000 else f"{price/1_000_000:.0f} triệu VNĐ"
                    context_parts.append(f"- **{FIELD_LABELS['price']}**: {price_str}\n")

            # Location - use city/district if available
            city = prop.get('city', '')
            district = prop.get('district', '')
            ward = prop.get('ward', '')
            location_parts = [p for p in [ward, district, city] if p]
            location_str = ', '.join(location_parts) if location_parts else prop.get('location', 'N/A')
            context_parts.append(f"- **{FIELD_LABELS['location']}**: {location_str}\n")

            # Attributes
            if prop.get('bedrooms'):
                context_parts.append(f"- **{FIELD_LABELS['bedrooms']}**: {prop['bedrooms']}\n")
            if prop.get('bathrooms'):
                context_parts.append(f"- **{FIELD_LABELS['bathrooms']}**: {prop['bathrooms']}\n")

            # Area - use area_display if available (normalized format)
            area_display = prop.get('area_display')
            if area_display:
                context_parts.append(f"- **{FIELD_LABELS['area']}**: {area_display}\n")
            elif prop.get('area'):
                area = prop['area']
                area_str = f"{area} m²" if isinstance(area, (int, float)) else str(area)
                context_parts.append(f"- **{FIELD_LABELS['area']}**: {area_str}\n")

            # Description excerpt
            if prop.get('description'):
                desc = prop['description'][:200]
                context_parts.append(f"- **{FIELD_LABELS['description']}**: {desc}...\n")

            context_parts.append("\n")

        return "".join(context_parts)

    async def _generate(self, query: str, context: str, retrieved_properties: List[Dict[str, Any]]) -> str:
        """
        STEP 3: GENERATE
        Use Core Gateway (LLM) to generate natural language response with augmented context
        """
        try:
            # Import OpenAI-compliant prompts (if available)
            try:
                from services.rag_service.openai_compliant_prompts import (
                    SYSTEM_PROMPT_OPENAI_COMPLIANT,
                    build_user_prompt_openai_compliant
                )
            except ImportError:
                # Fallback to inline prompts
                SYSTEM_PROMPT_OPENAI_COMPLIANT = """Bạn là chuyên gia tư vấn bất động sản REE AI.

⛔ QUY TẮC TỐI QUAN TRỌNG: KHÔNG ĐƯỢC TỰ TẠO DỮ LIỆU GIẢ
- CHỈ sử dụng bất động sản có trong dữ liệu được cung cấp
- Nếu có 1 BĐS, chỉ giới thiệu 1 BĐS
- Nếu không có BĐS nào, nói rõ "Tôi không tìm thấy bất động sản phù hợp"
- TUYỆT ĐỐI KHÔNG tự tạo thêm địa chỉ, giá, hoặc thông tin BĐS

NHIỆM VỤ:
Dựa vào dữ liệu bất động sản được cung cấp, hãy tạo câu trả lời tự nhiên, hữu ích cho khách hàng.

QUY TẮC:
1. Đếm chính xác số lượng bất động sản trong dữ liệu
2. Giới thiệu TẤT CẢ bất động sản có trong dữ liệu (không tự tạo thêm)
3. Cung cấp thông tin chi tiết: giá, vị trí, diện tích, số phòng (từ dữ liệu thật)
4. Tư vấn dựa trên dữ liệu có sẵn, không bịa đặt
5. Kết thúc với câu hỏi hoặc lời mời hành động

PHONG CÁCH:
- Thân thiện, chuyên nghiệp
- Sử dụng tiếng Việt tự nhiên
- Chỉ dùng thông tin có trong dữ liệu"""

                def build_user_prompt_openai_compliant(q, c):
                    return f"""Câu hỏi của khách hàng: {q}

{c}

⛔ CHỈ sử dụng dữ liệu ở trên, KHÔNG tự tạo thêm bất động sản.
Hãy tạo câu trả lời tự nhiên, hữu ích dựa CHÍNH XÁC trên dữ liệu trên."""

            # Build prompt for LLM with retrieved context
            system_prompt = SYSTEM_PROMPT_OPENAI_COMPLIANT
            user_prompt = build_user_prompt_openai_compliant(query, context)

            llm_request = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.3  # Reduced from 0.7 to prevent hallucination
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
                self.logger.info(f"{LogEmoji.SUCCESS} Generated response ({len(generated_text)} chars)")
                return generated_text
            else:
                self.logger.warning(f"{LogEmoji.WARNING} Core Gateway returned {response.status_code}")
                return self._format_simple_response(retrieved_properties)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Generation failed: {e}")
            return self._format_simple_response(retrieved_properties)

    def _format_simple_response(self, properties: List[Dict[str, Any]]) -> str:
        """Fallback: Simple formatting without LLM generation"""
        if not properties:
            return i18n_loader.get_ui_message('no_results', 'vi')

        response_parts = [f"Tôi đã tìm thấy {len(properties)} bất động sản phù hợp:\n\n"]

        for i, prop in enumerate(properties, 1):
            # Use price_display if available (normalized format)
            price_str = prop.get('price_display')
            if not price_str:
                price = prop.get('price', 0)
                if isinstance(price, (int, float)) and price > 0:
                    # Format price using i18n_loader
                    price_str = i18n_loader.format_price(price, 'vi')
                else:
                    price_str = i18n_loader.get_price_format('negotiable', 'vi')

            # Use district/city if available
            location_str = prop.get('district', prop.get('location', 'N/A'))

            response_parts.append(f"{i}. **{prop.get('title', 'N/A')}**\n")
            response_parts.append(f"   - 💰 Giá: {price_str}\n")
            response_parts.append(f"   - 📍 Vị trí: {location_str}\n")

            if prop.get('bedrooms'):
                response_parts.append(f"   - 🛏️ {prop['bedrooms']} phòng ngủ\n")

            # Use area_display if available (normalized format)
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

    def _format_properties_for_frontend(self, properties: List[Dict[str, Any]]) -> str:
        """
        Format property data as URL-encoded JSON for frontend PropertySearchResults component
        (OpenAI Apps SDK Design Guidelines)
        """
        import json
        from urllib.parse import quote

        if not properties:
            return ""

        # Format properties for PropertyCard component
        formatted_properties = []
        for prop in properties[:6]:  # Limit to 6 for carousel
            # Format price display
            price_display = prop.get('price_display', '')
            if not price_display:
                price = prop.get('price', 0)
                if isinstance(price, (int, float)) and price > 0:
                    if price >= 1_000_000_000:
                        price_display = f"{price/1_000_000_000:.1f} tỷ"
                    else:
                        price_display = f"{price/1_000_000:.0f} triệu"
                else:
                    price_display = "Thỏa thuận"

            # Format area display
            area_display = prop.get('area_display', '')
            if not area_display and prop.get('area'):
                area = prop['area']
                area_display = str(area) if isinstance(area, (int, float)) else area

            # Build location string
            district = prop.get('district', '')
            city = prop.get('city', '')
            location_parts = [p for p in [district, city] if p]
            address = ', '.join(location_parts) if location_parts else prop.get('location', '')

            # Get first image or placeholder
            images = prop.get('images', [])
            image_url = images[0] if images else prop.get('image_url', 'https://via.placeholder.com/400x300?text=No+Image')

            formatted_properties.append({
                "id": prop.get('property_id', prop.get('id', '')),
                "title": prop.get('title', 'N/A'),
                "address": address,
                "price": price_display,
                "priceUnit": "VNĐ",
                "area": area_display,
                "areaUnit": "m²",
                "bedrooms": prop.get('bedrooms', 0),
                "bathrooms": prop.get('bathrooms', 0),
                "imageUrl": image_url,
                "propertyType": prop.get('property_type', ''),
                "transactionType": prop.get('transaction_type', 'sale')
            })

        # URL encode the JSON
        json_str = json.dumps(formatted_properties, ensure_ascii=False)
        return quote(json_str)

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()

        # Cleanup advanced operators if initialized
        if self.advanced_enabled:
            for operator_name in ['query_rewriter', 'hyde_operator', 'decomposition_operator', 'reflection_operator']:
                if hasattr(self, operator_name):
                    operator = getattr(self, operator_name)
                    if hasattr(operator, 'cleanup'):
                        await operator.cleanup()

        await super().on_shutdown()


# Create service instance at module level for uvicorn
service = RAGService()
app = service.app

if __name__ == "__main__":
    service.run()

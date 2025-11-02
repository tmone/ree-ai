"""
Orchestrator - CTO Architecture Implementation
Intelligent agent with Classification-based routing and ReAct loop
WITH CONVERSATION MEMORY CONTEXT
"""
import time
import json
import uuid
from typing import Dict, Any, List, Optional
import httpx
import asyncpg
from datetime import datetime

from core.base_service import BaseService
from shared.models.orchestrator import (
    OrchestrationRequest, OrchestrationResponse, IntentType,
    IntentDetectionResult, RoutingDecision
)
from shared.models.core_gateway import LLMRequest, Message, ModelType, FileAttachment
from shared.utils.logger import LogEmoji
from shared.config import settings


class Orchestrator(BaseService):
    """
    Orchestrator Service - CTO Architecture
    80% of system intelligence - ReAct agent pattern
    """

    def __init__(self):
        super().__init__(
            name="orchestrator",
            version="3.0.0",  # v3 with conversation memory
            capabilities=["orchestration", "classification_routing", "react_agent", "conversation_memory"],
            port=8080
        )

        self.http_client = httpx.AsyncClient(timeout=60.0)

        # Service URLs
        self.core_gateway_url = settings.get_core_gateway_url()
        self.classification_url = "http://classification:8080"
        self.extraction_url = "http://attribute-extraction:8080"
        self.db_gateway_url = "http://db-gateway:8080"

        # PostgreSQL connection pool for conversation memory
        self.db_pool = None

        self.logger.info(f"{LogEmoji.INFO} CTO Architecture Mode Enabled")
        self.logger.info(f"{LogEmoji.INFO} Conversation Memory: PostgreSQL")

        # UUID v5 namespace for generating deterministic UUIDs from string IDs
        self.uuid_namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace

    def _string_to_uuid(self, string_id: str) -> uuid.UUID:
        """Convert string ID to deterministic UUID using UUID v5"""
        return uuid.uuid5(self.uuid_namespace, string_id)

    def _parse_data_uri(self, data_uri: str) -> Optional[FileAttachment]:
        """
        Parse data URI to FileAttachment.

        Format: data:image/jpeg;base64,<base64_data>
        """
        try:
            if not data_uri.startswith("data:"):
                return None

            # Split data URI
            parts = data_uri.split(",", 1)
            if len(parts) != 2:
                return None

            # Parse header: data:image/jpeg;base64
            header = parts[0]
            base64_data = parts[1]

            # Extract MIME type
            mime_parts = header.split(";")
            mime_type = mime_parts[0].replace("data:", "")

            # Generate file ID and filename
            file_id = str(uuid.uuid4())
            extension = mime_type.split("/")[-1]  # e.g., "jpeg" from "image/jpeg"
            filename = f"upload_{file_id[:8]}.{extension}"

            # Estimate size (base64 is ~33% larger than original)
            size_bytes = len(base64_data) * 3 // 4

            return FileAttachment(
                file_id=file_id,
                filename=filename,
                mime_type=mime_type,
                size_bytes=size_bytes,
                base64_data=base64_data,
                upload_time=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to parse data URI: {e}")
            return None

    async def on_startup(self):
        """Initialize resources on startup"""
        await super().on_startup()
        await self._init_db_pool()

    def setup_routes(self):
        """Setup Orchestrator API routes."""

        @self.app.post("/orchestrate", response_model=OrchestrationResponse)
        async def orchestrate(request: OrchestrationRequest):
            """Main orchestration with Classification routing + Conversation Memory + Multimodal support"""
            try:
                start_time = time.time()

                # Log multimodal request
                if request.has_files():
                    self.logger.info(
                        f"{LogEmoji.AI} Multimodal Query: '{request.query}' + {len(request.files)} file(s)"
                    )
                else:
                    self.logger.info(
                        f"{LogEmoji.TARGET} Query: '{request.query}'"
                    )

                # Step 0: Get conversation history (MEMORY CONTEXT)
                conversation_id = request.conversation_id or request.user_id
                history = await self._get_conversation_history(request.user_id, conversation_id, limit=10)

                if history:
                    self.logger.info(f"{LogEmoji.INFO} Retrieved {len(history)} messages from conversation history")

                # Step 1: Detect intent (simple keyword-based for now, files → chat for analysis)
                if request.has_files():
                    # Images/documents → Use vision model for analysis
                    intent = "chat"  # Vision analysis goes through chat path
                    self.logger.info(f"{LogEmoji.AI} Intent: {intent} (multimodal analysis)")
                else:
                    intent = self._detect_intent_simple(request.query)
                    self.logger.info(f"{LogEmoji.AI} Intent: {intent}")

                # Step 2: Route based on intent (with history context + files)
                if intent == "search":
                    response_text = await self._handle_search(request.query, history=history, files=request.files)
                else:
                    response_text = await self._handle_chat(request.query, history=history, files=request.files)

                # Step 3: Save conversation to memory
                await self._save_message(request.user_id, conversation_id, "user", request.query)
                await self._save_message(request.user_id, conversation_id, "assistant", response_text, metadata={"intent": intent, "has_files": request.has_files()})

                execution_time = (time.time() - start_time) * 1000

                return OrchestrationResponse(
                    intent=IntentType.SEARCH if intent == "search" else IntentType.CHAT,
                    confidence=0.9,
                    response=response_text,
                    service_used="classification_routing_with_memory_multimodal",
                    execution_time_ms=execution_time,
                    metadata={
                        "flow": "cto_architecture",
                        "history_messages": len(history),
                        "multimodal": request.has_files(),
                        "files_count": len(request.files) if request.files else 0
                    }
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Orchestration failed: {e}")
                import traceback
                traceback.print_exc()
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response=f"Xin lỗi, đã xảy ra lỗi: {str(e)}",
                    service_used="none",
                    execution_time_ms=0.0
                )

        @self.app.get("/v1/models")
        async def list_models():
            """OpenAI-compatible models endpoint for Open WebUI"""
            return {
                "object": "list",
                "data": [
                    {
                        "id": "ree-ai-assistant",
                        "object": "model",
                        "created": 1677610602,
                        "owned_by": "ree-ai",
                        "permission": [],
                        "root": "ree-ai-assistant",
                        "parent": None
                    }
                ]
            }

        @self.app.post("/v1/chat/completions")
        async def openai_compatible_chat(request: Dict[str, Any]):
            """
            OpenAI-compatible endpoint with multimodal support.
            Handles file uploads from Open WebUI.
            """
            try:
                messages = request.get("messages", [])
                user_message = ""
                files = []

                # Extract last user message and any files
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        content = msg.get("content", "")

                        # Handle multimodal content (Open WebUI format)
                        if isinstance(content, list):
                            # Content is array of blocks: [{"type": "text", "text": "..."}, {"type": "image_url", ...}]
                            text_parts = []
                            for block in content:
                                if block.get("type") == "text":
                                    text_parts.append(block.get("text", ""))
                                elif block.get("type") == "image_url":
                                    # Extract image
                                    image_url = block.get("image_url", {})
                                    url = image_url.get("url", "")
                                    if url.startswith("data:"):
                                        # Parse data URI: data:image/jpeg;base64,<base64_data>
                                        file_attachment = self._parse_data_uri(url)
                                        if file_attachment:
                                            files.append(file_attachment)
                            user_message = " ".join(text_parts)
                        else:
                            # Text-only content
                            user_message = content
                        break

                if not user_message and not files:
                    return {"error": "No user message or files found"}

                # If only files, add default prompt
                if files and not user_message:
                    user_message = "Phân tích hình ảnh này và cho tôi biết về bất động sản trong ảnh."

                # Log multimodal request
                if files:
                    self.logger.info(
                        f"{LogEmoji.AI} Multimodal request: {len(files)} file(s) attached"
                    )

                orch_request = OrchestrationRequest(
                    user_id=request.get("user", "anonymous"),
                    query=user_message,
                    conversation_id=None,
                    metadata={
                        "messages": messages,
                        "has_files": len(files) > 0,
                        "files": [f.filename for f in files]
                    },
                    files=files if files else None
                )

                orch_response = await orchestrate(orch_request)

                return {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "ree-ai-orchestrator-v3-multimodal",
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
                self.logger.error(f"{LogEmoji.ERROR} OpenAI chat failed: {e}")
                import traceback
                traceback.print_exc()
                return {
                    "error": str(e),
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": f"Xin lỗi, đã xảy ra lỗi: {str(e)}"
                        }
                    }]
                }

    def _detect_intent_simple(self, query: str) -> str:
        """
        Improved intent detection - distinguishes advisory from search

        Returns:
        - "chat": Advisory/consultation questions (giá hợp lý?, ROI?, nên mua?)
        - "search": Property search queries (tìm căn hộ, có view không?)
        """
        query_lower = query.lower()

        # PRIORITY 1: Advisory/Consultation patterns (CHAT intent)
        # These should be answered with advice, not property listings
        advisory_patterns = [
            "bao nhiêu là hợp lý",
            "chịu được bao nhiêu",
            "giá hợp lý",
            "có hợp lý không",
            "có đáng",
            "có nên",
            "nên mua",
            "nên chọn",
            "nên không",
            "roi",
            "lợi nhuận",
            "phân tích",
            "đánh giá",
            "xu hướng",
            "thị trường",
            "dự kiến",
            "ước tính",
            "so sánh",
            "thủ tục",
            "giấy tờ",
            "pháp lý",
            "quy hoạch",
            "tiềm năng",
            "rủi ro",
            "lời khuyên",
            "tư vấn"
        ]

        # Check advisory patterns first (higher priority)
        if any(pattern in query_lower for pattern in advisory_patterns):
            return "chat"

        # PRIORITY 2: Search patterns (SEARCH intent)
        # These indicate user wants to find specific properties
        search_patterns = [
            "tìm",
            "find",
            "search",
            "cho xem",
            "xem",
            "cần tìm",
            "muốn tìm",
            "muốn mua",
            "muốn thuê",
            "cần mua",
            "cần thuê"
        ]

        # Check explicit search keywords
        if any(pattern in query_lower for pattern in search_patterns):
            return "search"

        # PRIORITY 3: Contextual questions (depends on context)
        # These are follow-up questions that reference previous context
        contextual_indicators = [
            "có không",
            "có ... không",
            "căn đó",
            "căn này",
            "dự án đó",
            "khu vực đó",
            "tòa đó",
            "chỗ đó"
        ]

        # If asking about specific property features → SEARCH
        if any(indicator in query_lower for indicator in contextual_indicators):
            return "search"

        # PRIORITY 4: Greeting/General conversation
        greeting_patterns = ["xin chào", "hello", "hi", "cảm ơn", "thank"]
        if any(pattern in query_lower for pattern in greeting_patterns):
            return "chat"

        # DEFAULT: If unclear, default to CHAT (safer - won't return wrong properties)
        # Better to give advice than wrong property listings
        return "chat"

    async def _enrich_query_with_context(self, query: str, history: List[Dict]) -> str:
        """Enrich query with context from conversation history using LLM"""
        if not history or len(history) == 0:
            return query

        try:
            # Build context string from history
            context_parts = []
            for msg in history[-4:]:  # Use last 4 messages for context
                role = msg.get('role', '')
                content = msg.get('content', '')
                if role == 'user':
                    context_parts.append(f"User: {content}")
                elif role == 'assistant':
                    # Only include first 200 chars of assistant response
                    context_parts.append(f"Assistant: {content[:200]}...")

            context_str = "\n".join(context_parts)

            # Use LLM to rewrite query with full context
            prompt = f"""Given this conversation history:
{context_str}

Current user query: "{query}"

If the query contains references to previous context (e.g., "căn đó", "dự án đó", "khu vực đó"), rewrite it as a standalone query with full context. Otherwise, return the original query unchanged.

Standalone query:"""

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150,
                    "temperature": 0.3
                },
                timeout=15.0
            )

            if response.status_code == 200:
                data = response.json()
                enriched_query = data.get("content", query).strip()

                if enriched_query and enriched_query != query:
                    self.logger.info(f"{LogEmoji.INFO} Query enriched with context: '{query}' → '{enriched_query}'")
                    return enriched_query

            return query

        except Exception as e:
            self.logger.warning(f"{LogEmoji.WARNING} Failed to enrich query with context: {e}")
            return query

    async def _handle_search(self, query: str, history: List[Dict] = None, files: Optional[List[FileAttachment]] = None) -> str:
        """
        ReAct Agent Pattern for Search:
        1. REASONING: Analyze query requirements
        2. ACT: Execute search (classify + route)
        3. EVALUATE: Check result quality
        4. ITERATE: Refine query or ask clarification if quality is poor

        Max 2 iterations to balance quality vs response time
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [ReAct Agent] Starting search with query: '{query}'")

            # STEP 1: REASONING - Analyze query requirements
            requirements = await self._analyze_query_requirements(query, history)

            # Enrich query with conversation context if available
            enriched_query = await self._enrich_query_with_context(query, history or [])

            max_iterations = 2  # Balance quality vs speed
            current_query = enriched_query
            best_results = []  # Keep track of BEST results across iterations for clarification
            best_evaluation = None

            for iteration in range(max_iterations):
                self.logger.info(f"{LogEmoji.INFO} [ReAct Agent] Iteration {iteration + 1}/{max_iterations}")

                # STEP 2: ACT - Execute search
                results = await self._execute_search_internal(current_query)

                # STEP 3: EVALUATE - Check result quality
                evaluation = await self._evaluate_results(results, requirements)

                # Keep track of best results (prefer more results if quality is similar)
                if (not best_results and results) or (results and len(results) > len(best_results)):
                    best_results = results
                    best_evaluation = evaluation
                    self.logger.info(f"{LogEmoji.INFO} Updated best_results: {len(best_results)} properties")

                # STEP 4: DECIDE based on evaluation
                if evaluation["satisfied"]:
                    # Quality is good → Return to user
                    self.logger.info(f"{LogEmoji.SUCCESS} [ReAct Agent] Quality satisfied, returning results")
                    return await self._generate_quality_response(query, results, requirements, evaluation)

                else:
                    # Quality is poor
                    self.logger.warning(f"{LogEmoji.WARNING} [ReAct Agent] Quality not satisfied: {evaluation['quality_score']:.1%}")

                    if iteration < max_iterations - 1:
                        # Try to refine query for next iteration
                        current_query = await self._refine_query(current_query, requirements, evaluation)
                        self.logger.info(f"{LogEmoji.INFO} [ReAct Agent] Trying refined query: '{current_query}'")
                    else:
                        # Last iteration and still not satisfied → Ask user for clarification with alternatives
                        self.logger.info(f"{LogEmoji.INFO} [ReAct Agent] Max iterations reached, asking clarification with alternatives")
                        # Use best results from all iterations, not just last one
                        return await self._ask_clarification(requirements, best_evaluation or evaluation, best_results)

            # Fallback (should not reach here)
            return "Xin lỗi, tôi không tìm thấy bất động sản phù hợp. Bạn có thể cung cấp thêm thông tin không?"

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [ReAct Agent] Search failed: {e}")
            return f"Xin lỗi, đã xảy ra lỗi khi tìm kiếm: {str(e)}"

    async def _execute_search_internal(self, query: str) -> List[Dict]:
        """
        Internal method: Execute actual search (Classification → Routing → Search)
        Used by ReAct agent in ACT step

        Returns list of property results
        """
        try:
            # Step 1: Classification
            self.logger.info(f"{LogEmoji.AI} [ReAct-Act] Classification")

            classification_response = await self.http_client.post(
                f"{self.classification_url}/classify",
                json={"query": query, "context": None},
                timeout=30.0
            )

            if classification_response.status_code != 200:
                raise Exception(f"Classification failed: {classification_response.text}")

            classification = classification_response.json()
            mode = classification.get("mode", "semantic")

            self.logger.info(f"{LogEmoji.SUCCESS} [ReAct-Act] Mode: {mode}")

            # Step 2: Route based on mode
            if mode == "filter":
                results = await self._execute_filter_search(query)
            elif mode == "semantic":
                results = await self._execute_semantic_search(query)
            else:  # both
                results = await self._execute_filter_search(query)  # Use filter for now

            self.logger.info(f"{LogEmoji.SUCCESS} [ReAct-Act] Found {len(results)} results")
            return results

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [ReAct-Act] Search execution failed: {e}")
            return []

    async def _execute_filter_search(self, query: str) -> List[Dict]:
        """Execute filter-based search (Extraction → Document search)"""
        try:
            # Step 1: Attribute Extraction
            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query",
                json={"query": query, "intent": "SEARCH"},
                timeout=30.0
            )

            if extraction_response.status_code != 200:
                return []

            extraction = extraction_response.json()
            entities = extraction.get("entities", {})

            # Step 2: Document Search
            search_response = await self.http_client.post(
                f"{self.db_gateway_url}/search",
                json={
                    "query": query,
                    "filters": entities,
                    "limit": 5
                },
                timeout=30.0
            )

            if search_response.status_code != 200:
                return []

            search_results = search_response.json()
            return search_results.get("results", [])

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Filter search failed: {e}")
            return []

    async def _execute_semantic_search(self, query: str) -> List[Dict]:
        """Execute semantic search (Vector search)"""
        try:
            search_response = await self.http_client.post(
                f"{self.db_gateway_url}/vector-search",
                json={
                    "query": query,
                    "limit": 5
                },
                timeout=30.0
            )

            if search_response.status_code != 200:
                return []

            search_results = search_response.json()
            return search_results.get("results", [])

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Semantic search failed: {e}")
            return []

    async def _handle_filter_search(self, query: str) -> str:
        """Filter mode: Extraction → Document search"""
        try:
            # Step 2a: Attribute Extraction
            self.logger.info(f"{LogEmoji.AI} Step 2a: Attribute Extraction")

            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query",
                json={"query": query, "intent": "SEARCH"},
                timeout=30.0
            )

            if extraction_response.status_code != 200:
                raise Exception(f"Extraction failed: {extraction_response.text}")

            extraction = extraction_response.json()
            entities = extraction.get("entities", {})

            self.logger.info(f"{LogEmoji.SUCCESS} Extracted: {entities}")

            # Step 2b: Document Search
            self.logger.info(f"{LogEmoji.AI} Step 2b: Document Search")

            search_response = await self.http_client.post(
                f"{self.db_gateway_url}/search",
                json={
                    "query": query,
                    "filters": entities,
                    "limit": 5
                },
                timeout=30.0
            )

            if search_response.status_code != 200:
                raise Exception(f"Search failed: {search_response.text}")

            search_results = search_response.json()
            results = search_results.get("results", [])

            self.logger.info(f"{LogEmoji.SUCCESS} Found {len(results)} properties")

            # Step 3: Generate response
            return await self._generate_search_response(query, results, "filter")

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Filter search failed: {e}")
            return f"Xin lỗi, không tìm thấy bất động sản phù hợp. Chi tiết lỗi: {str(e)}"

    async def _handle_semantic_search(self, query: str) -> str:
        """Semantic mode: Use vector search with embeddings"""
        try:
            self.logger.info(f"{LogEmoji.AI} Step 2: Vector Search (Semantic)")

            # Call DB Gateway vector search endpoint
            search_response = await self.http_client.post(
                f"{self.db_gateway_url}/vector-search",
                json={
                    "query": query,
                    "limit": 5
                },
                timeout=30.0
            )

            search_results = search_response.json()
            results = search_results.get("results", [])

            self.logger.info(f"{LogEmoji.SUCCESS} Vector search found {len(results)} properties")

            # Generate response from search results
            return await self._generate_search_response(query, results, "semantic")

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Vector search failed: {e}")
            return f"Xin lỗi, tìm kiếm ngữ nghĩa gặp lỗi: {str(e)}"

    async def _handle_hybrid_search(self, query: str) -> str:
        """Both mode: Hybrid search (simplified - use filter for now)"""
        self.logger.info(f"{LogEmoji.AI} Hybrid search → using filter path")
        return await self._handle_filter_search(query)

    async def _generate_search_response(self, query: str, results: List[Dict], mode: str) -> str:
        """Generate natural language response from search results"""
        if not results or len(results) == 0:
            return f"Tôi không tìm thấy bất động sản nào phù hợp với yêu cầu '{query}'. Bạn có thể mô tả cụ thể hơn về giá, số phòng ngủ, hoặc khu vực không?"

        # Build response with property details
        response_parts = [f"Tôi đã tìm thấy {len(results)} bất động sản phù hợp:\n"]

        for i, prop in enumerate(results[:3], 1):  # Top 3
            title = prop.get("title", "Không có tiêu đề")
            price = prop.get("price_display", prop.get("price", "Liên hệ"))
            area = prop.get("area", "N/A")
            location = prop.get("district", prop.get("region", "N/A"))

            response_parts.append(
                f"\n{i}. **{title}**\n"
                f"   - Giá: {price}\n"
                f"   - Diện tích: {area} m²\n"
                f"   - Khu vực: {location}"
            )

        if len(results) > 3:
            response_parts.append(f"\n\n...và {len(results) - 3} bất động sản khác.")

        return "".join(response_parts)

    async def _handle_chat(self, query: str, history: List[Dict] = None, files: Optional[List[FileAttachment]] = None) -> str:
        """Handle general chat (non-search) with conversation context and multimodal support"""
        try:
            # Build messages with history context
            if files and len(files) > 0:
                # Multimodal prompt (vision analysis)
                system_prompt = """Bạn là trợ lý bất động sản chuyên nghiệp với khả năng phân tích hình ảnh.

NHIỆM VỤ KHI PHÂN TÍCH HÌNH ẢNH BẤT ĐỘNG SẢN:
1. MÔ TẢ chi tiết căn hộ/nhà từ hình ảnh:
   - Loại hình: Căn hộ, biệt thự, nhà phố, đất nền
   - Phong cách thiết kế và nội thất
   - Diện tích ước tính
   - View và hướng (nếu nhìn thấy)
   - Tiện ích trong ảnh (hồ bơi, gym, ban công...)

2. ĐÁNH GIÁ chất lượng và giá trị:
   - Tình trạng bất động sản
   - Mức độ sang trọng/cao cấp
   - Ước tính giá dựa trên vị trí và đặc điểm

3. TƯ VẤN nếu người dùng hỏi:
   - Phù hợp với nhu cầu gì
   - Điểm mạnh/yếu của BĐS
   - Khuyến nghị đầu tư

LUÔN trả lời bằng tiếng Việt, chi tiết và chuyên nghiệp."""
            else:
                # Text-only prompt
                system_prompt = """Bạn là trợ lý bất động sản thông minh và chuyên nghiệp.

QUAN TRỌNG - Sử dụng lịch sử hội thoại:
1. LUÔN LUÔN đọc kỹ toàn bộ cuộc trò chuyện trước đó
2. REFERENCE cụ thể những gì người dùng đã hỏi/nói trước đó
3. KẾT NỐI câu trả lời hiện tại với ngữ cảnh cuộc trò chuyện

VÍ DỤ TỐT:
- User trước: "Tìm nhà trọ gần đại học"
- User hiện tại: "Giá thuê bao nhiêu?"
- Response: "Dựa trên yêu cầu trước của bạn về NHÀ TRỌ GẦN ĐẠI HỌC, giá thuê phổ biến là..."

VÍ DỤ XẤU (TRÁNH):
- Response: "Giá thuê bao nhiêu tùy thuộc vào khu vực..." (KHÔNG đề cập context)

LUÔN thể hiện rằng bạn NHỚ và HIỂU cuộc trò chuyện trước đó."""

            messages_data = [
                {"role": "system", "content": system_prompt}
            ]

            # Add history for context (text-only)
            if history:
                messages_data.extend(history)

            # Add current query with files if present
            if files:
                # Multimodal message
                messages_data.append({
                    "role": "user",
                    "content": query,
                    "files": [f.dict() for f in files]
                })
            else:
                # Text-only message
                messages_data.append({"role": "user", "content": query})

            # Choose model based on multimodal
            model = "gpt-4o" if files else "gpt-4o-mini"

            if files:
                self.logger.info(f"{LogEmoji.AI} Using vision model {model} for {len(files)} file(s)")

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": model,
                    "messages": messages_data,
                    "max_tokens": 1000 if files else 500,
                    "temperature": 0.7
                },
                timeout=60.0 if files else 30.0  # More time for vision
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("content", "Xin lỗi, tôi không hiểu câu hỏi.")
            else:
                self.logger.error(f"{LogEmoji.ERROR} Core Gateway error: {response.status_code}")
                return "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu."

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Chat failed: {e}")
            import traceback
            traceback.print_exc()
            return f"Xin lỗi, đã xảy ra lỗi: {str(e)}"

    # ========================================
    # ReAct Agent Pattern Methods
    # ========================================

    async def _analyze_query_requirements(self, query: str, history: List[Dict] = None) -> Dict:
        """
        REASONING Step: Extract structured requirements from user query

        Returns:
            {
                "property_type": str,  # "căn hộ", "nhà phố", "biệt thự", etc.
                "bedrooms": int or None,
                "district": str or None,
                "city": str or None,
                "price_min": float or None,
                "price_max": float or None,
                "special_requirements": List[str]  # ["gần trường quốc tế", "view sông", etc.]
            }
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [ReAct-Reasoning] Analyzing query requirements...")

            analysis_prompt = f"""Phân tích yêu cầu tìm kiếm bất động sản từ người dùng.

Query: "{query}"

Trích xuất thông tin theo format JSON:
{{
    "property_type": "căn hộ/nhà phố/biệt thự/đất/etc hoặc null",
    "bedrooms": số phòng ngủ (số nguyên) hoặc null,
    "district": "quận X/huyện Y hoặc null",
    "city": "TP.HCM/Hà Nội/Đà Nẵng/etc hoặc null",
    "price_min": giá tối thiểu (tỷ VND) hoặc null,
    "price_max": giá tối đa (tỷ VND) hoặc null,
    "special_requirements": ["gần trường quốc tế", "view sông", "yên tĩnh", etc]
}}

CHÚ Ý:
- Nếu query nói "quận 2" thì city mặc định là "TP.HCM"
- Nếu query nói "Cầu Giấy" thì city mặc định là "Hà Nội"
- Trích xuất TẤT CẢ yêu cầu đặc biệt (gần trường, view đẹp, yên tĩnh, etc.)
- Chỉ trả về JSON, không giải thích thêm.

JSON:"""

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": analysis_prompt}],
                    "max_tokens": 300,
                    "temperature": 0.1
                },
                timeout=15.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "{}")

                # Parse JSON from response
                try:
                    requirements = json.loads(content)
                    self.logger.info(f"{LogEmoji.SUCCESS} [ReAct-Reasoning] Requirements: {requirements}")
                    return requirements
                except json.JSONDecodeError:
                    self.logger.warning(f"{LogEmoji.WARNING} Failed to parse requirements JSON")
                    return {}
            else:
                return {}

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Query analysis failed: {e}")
            return {}

    async def _evaluate_results(self, results: List[Dict], requirements: Dict) -> Dict:
        """
        EVALUATE Step: Check if search results match requirements

        Returns:
            {
                "satisfied": bool,  # Overall satisfaction
                "match_count": int,  # Number of results matching requirements
                "total_count": int,  # Total results
                "match_rate": float,  # Percentage (0-1)
                "missing_criteria": List[str],  # What's not matching
                "quality_score": float  # 0-1 score
            }
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [ReAct-Evaluate] Checking result quality...")

            if not results:
                return {
                    "satisfied": False,
                    "match_count": 0,
                    "total_count": 0,
                    "match_rate": 0.0,
                    "missing_criteria": ["No results found"],
                    "quality_score": 0.0
                }

            match_count = 0
            missing_criteria = []

            # Check each result against requirements
            for prop in results:
                matches = True

                # Check district (CRITICAL)
                if requirements.get("district"):
                    required_district = requirements["district"].lower()
                    prop_district = str(prop.get("district", "")).lower()

                    # Extract district number (e.g., "quận 2" → "2")
                    import re
                    required_num = re.search(r'\d+', required_district)
                    prop_num = re.search(r'\d+', prop_district)

                    if required_num and prop_num:
                        if required_num.group() != prop_num.group():
                            matches = False
                    elif required_district not in prop_district and prop_district not in required_district:
                        matches = False

                # Check bedrooms (IMPORTANT)
                if requirements.get("bedrooms"):
                    prop_bedrooms = prop.get("bedrooms") or prop.get("bedroom")
                    if prop_bedrooms:
                        try:
                            if int(prop_bedrooms) != int(requirements["bedrooms"]):
                                matches = False
                        except:
                            pass

                # Check property type
                if requirements.get("property_type"):
                    required_type = requirements["property_type"].lower()
                    prop_title = str(prop.get("title", "")).lower()
                    if required_type not in prop_title:
                        # Don't fail on property type, just lower score
                        pass

                # Check price range
                if requirements.get("price_max"):
                    prop_price = prop.get("price")
                    if prop_price:
                        try:
                            price_val = float(prop_price)
                            if price_val > requirements["price_max"] * 1e9:  # Convert tỷ to VND
                                matches = False
                        except:
                            pass

                if matches:
                    match_count += 1

            match_rate = match_count / len(results) if results else 0.0

            # Determine missing criteria
            if match_rate < 0.6:
                if requirements.get("district"):
                    missing_criteria.append(f"Không đủ BDS ở {requirements['district']}")
                if requirements.get("bedrooms"):
                    missing_criteria.append(f"Không đủ BDS có {requirements['bedrooms']} phòng ngủ")
                if requirements.get("special_requirements"):
                    missing_criteria.extend([f"Thiếu: {req}" for req in requirements["special_requirements"]])

            # Quality score based on match rate
            quality_score = match_rate
            satisfied = quality_score >= 0.6  # At least 60% match

            evaluation = {
                "satisfied": satisfied,
                "match_count": match_count,
                "total_count": len(results),
                "match_rate": match_rate,
                "missing_criteria": missing_criteria,
                "quality_score": quality_score
            }

            self.logger.info(f"{LogEmoji.SUCCESS} [ReAct-Evaluate] Quality: {quality_score:.1%} ({match_count}/{len(results)} matches)")

            return evaluation

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Evaluation failed: {e}")
            return {
                "satisfied": False,
                "match_count": 0,
                "total_count": len(results) if results else 0,
                "match_rate": 0.0,
                "missing_criteria": [str(e)],
                "quality_score": 0.0
            }

    async def _refine_query(self, original_query: str, requirements: Dict, evaluation: Dict) -> str:
        """
        ITERATE Step: Refine query based on evaluation feedback

        Returns refined query string
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [ReAct-Iterate] Refining query...")

            # Build refinement context
            missing = evaluation.get("missing_criteria", [])

            refine_prompt = f"""Query gốc: "{original_query}"

Yêu cầu đã phân tích: {json.dumps(requirements, ensure_ascii=False)}

Vấn đề: Tìm được {evaluation['match_count']}/{evaluation['total_count']} BDS phù hợp.
Thiếu: {', '.join(missing)}

Hãy tạo query mới CỤ THỂ HƠN để cải thiện kết quả.
Chỉ trả về query mới, không giải thích.

Query mới:"""

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": refine_prompt}],
                    "max_tokens": 100,
                    "temperature": 0.3
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                refined = data.get("content", original_query).strip().strip('"')
                self.logger.info(f"{LogEmoji.SUCCESS} [ReAct-Iterate] Refined: '{refined}'")
                return refined
            else:
                return original_query

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Query refinement failed: {e}")
            return original_query

    async def _ask_clarification(self, requirements: Dict, evaluation: Dict, results: List[Dict] = None) -> str:
        """
        ITERATE Alternative: Intelligent clarification with alternatives and statistics

        Returns clarification message with:
        - Data-driven insights (statistics)
        - Proactive suggestions
        - Top alternatives with scoring (using OpenSearch semantic scores)
        """
        try:
            # Get statistics from DB Gateway
            stats = await self._get_property_statistics(requirements)

            # Use semantic scores from OpenSearch (if available) or calculate match scores
            scored_results = []
            if results:
                # Check if results have semantic scores from OpenSearch
                has_semantic_scores = any(isinstance(prop.get("score"), (int, float)) for prop in results)

                if has_semantic_scores:
                    # Use semantic scores from OpenSearch and normalize to 0-100
                    max_score = max((prop.get("score", 0) for prop in results), default=1.0)
                    self.logger.info(f"{LogEmoji.INFO} Using OpenSearch semantic scores (max: {max_score:.2f})")

                    for prop in results:
                        semantic_score = prop.get("score", 0)
                        # Normalize to 0-100 range based on max score in this batch
                        normalized_score = int((semantic_score / max_score) * 100) if max_score > 0 else 0
                        scored_results.append({"property": prop, "score": normalized_score, "type": "semantic"})
                else:
                    # Fallback: Calculate rule-based match scores
                    self.logger.info(f"{LogEmoji.INFO} Using rule-based match scores (no semantic scores found)")
                    for prop in results:
                        score = self._calculate_match_score(prop, requirements)
                        scored_results.append({"property": prop, "score": score, "type": "match"})

                # Sort by score descending
                scored_results.sort(key=lambda x: x["score"], reverse=True)

            # Build intelligent response
            clarification_parts = []

            # Part 1: Statistics & Context
            property_type = requirements.get("property_type", "bất động sản")
            city = requirements.get("city", "TP.HCM")
            district = requirements.get("district")
            bedrooms = requirements.get("bedrooms")

            if stats.get("total_in_city", 0) > 0:
                clarification_parts.append(
                    f"Tôi tìm thấy **{stats['total_in_city']} {property_type}** ở {city}"
                )

                if district and stats.get("total_in_district", 0) == 0:
                    clarification_parts.append(
                        f", nhưng **không có căn nào ở {district}**."
                    )
                elif district:
                    clarification_parts.append(
                        f", trong đó có **{stats['total_in_district']} căn** ở {district}."
                    )
                else:
                    clarification_parts.append(".")
            else:
                clarification_parts.append(
                    f"Hiện tại không có {property_type} nào phù hợp với yêu cầu của bạn trong hệ thống."
                )

            # Part 2: Proactive Options
            clarification_parts.append("\n\n**Bạn muốn tôi:**\n")

            if district:
                # Suggest expanding to nearby districts
                nearby_districts = self._get_nearby_districts(district)
                if nearby_districts:
                    clarification_parts.append(
                        f"- 🔍 Tìm thêm ở **các quận lân cận** ({', '.join(nearby_districts[:3])})\n"
                    )

                clarification_parts.append(
                    f"- 🌍 Mở rộng tìm kiếm **toàn {city}**\n"
                )

            if requirements.get("special_requirements"):
                spec_req = requirements["special_requirements"][0]
                clarification_parts.append(
                    f"- 📍 Cung cấp thông tin cụ thể hơn về \"{spec_req}\"\n"
                )

            if bedrooms:
                clarification_parts.append(
                    f"- 🛏️ Điều chỉnh số phòng ngủ ({bedrooms} ± 1 phòng)\n"
                )

            # Part 3: Show Top 5 Alternatives
            if scored_results and len(scored_results) > 0:
                clarification_parts.append(
                    f"\n**Dưới đây là {min(5, len(scored_results))} BĐS gần nhất có thể phù hợp:**\n"
                )

                for i, item in enumerate(scored_results[:5]):
                    prop = item["property"]
                    score = item["score"]

                    title = prop.get("title", "Không có tiêu đề")
                    price = prop.get("price_display", prop.get("price", "Liên hệ"))
                    area = prop.get("area", "N/A")
                    location = prop.get("district", prop.get("region", "N/A"))
                    prop_bedrooms = prop.get("bedrooms") or prop.get("bedroom", "N/A")

                    # Match indicator
                    match_indicator = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"

                    clarification_parts.append(
                        f"\n{i + 1}. {match_indicator} **{title}** (Điểm: {score}/100)\n"
                        f"   💰 Giá: {price} | 📐 {area}m² | 🛏️ {prop_bedrooms} PN\n"
                        f"   📍 {location}\n"
                    )

            # Part 4: Call to Action
            clarification_parts.append("\n💬 Bạn muốn tôi hỗ trợ như thế nào?")

            return "".join(clarification_parts)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Clarification generation failed: {e}")
            return "Xin lỗi, tôi không tìm thấy bất động sản phù hợp chính xác. Bạn có thể cung cấp thêm thông tin để tôi tìm kiếm tốt hơn không?"

    def _calculate_match_score(self, prop: Dict, requirements: Dict) -> int:
        """
        Calculate match score (0-100) for a property against requirements

        Scoring:
        - District match: 40 points
        - Bedrooms match: 30 points
        - Property type match: 15 points
        - Price in range: 15 points
        """
        score = 0

        # District match (40 points)
        if requirements.get("district"):
            required_district = requirements["district"].lower()
            prop_district = str(prop.get("district", "")).lower()

            import re
            required_num = re.search(r'\d+', required_district)
            prop_num = re.search(r'\d+', prop_district)

            if required_num and prop_num and required_num.group() == prop_num.group():
                score += 40
            elif required_district in prop_district or prop_district in required_district:
                score += 20  # Partial match

        # Bedrooms match (30 points)
        if requirements.get("bedrooms"):
            prop_bedrooms = prop.get("bedrooms") or prop.get("bedroom")
            if prop_bedrooms:
                try:
                    required_br = int(requirements["bedrooms"])
                    prop_br = int(prop_bedrooms)

                    if required_br == prop_br:
                        score += 30
                    elif abs(required_br - prop_br) == 1:
                        score += 15  # ±1 bedroom
                except:
                    pass

        # Property type match (15 points)
        if requirements.get("property_type"):
            required_type = requirements["property_type"].lower()
            prop_title = str(prop.get("title", "")).lower()

            if required_type in prop_title:
                score += 15

        # Price in range (15 points)
        if requirements.get("price_max"):
            prop_price = prop.get("price")
            if prop_price:
                try:
                    price_val = float(prop_price)
                    price_max = requirements["price_max"] * 1e9

                    if price_val <= price_max:
                        score += 15
                    elif price_val <= price_max * 1.2:  # Within 20% over budget
                        score += 7
                except:
                    pass

        return min(100, score)

    async def _get_property_statistics(self, requirements: Dict) -> Dict:
        """
        Get statistics from DB Gateway about available properties

        Returns:
        - total_in_city: Total properties in the city
        - total_in_district: Total properties in the district (if specified)
        """
        try:
            # TODO: Call DB Gateway to get real statistics
            # For now, return mock data
            return {
                "total_in_city": 150,  # Mock: 150 căn hộ ở TP.HCM
                "total_in_district": 0 if requirements.get("district") == "quận 2" else 50
            }
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to get statistics: {e}")
            return {
                "total_in_city": 0,
                "total_in_district": 0
            }

    def _get_nearby_districts(self, district: str) -> List[str]:
        """
        Get nearby districts for expansion suggestions

        Simple mapping for now, can be improved with geographic data
        """
        nearby_map = {
            "quận 1": ["Quận 3", "Quận 4", "Quận 5"],
            "quận 2": ["Quận 9", "Thủ Đức", "Bình Thạnh"],
            "quận 3": ["Quận 1", "Quận 10", "Bình Thạnh"],
            "quận 4": ["Quận 1", "Quận 7", "Quận 8"],
            "quận 5": ["Quận 6", "Quận 8", "Quận 11"],
            "quận 6": ["Quận 5", "Quận 8", "Quận 11"],
            "quận 7": ["Quận 4", "Nhà Bè", "Bình Chánh"],
            "quận 8": ["Quận 5", "Quận 6", "Bình Tân"],
            "quận 9": ["Quận 2", "Thủ Đức"],
            "quận 10": ["Quận 3", "Quận 6", "Quận 11"],
            "quận 11": ["Quận 5", "Quận 6", "Quận 10"],
            "quận 12": ["Gò Vấp", "Tân Bình", "Bình Thạnh"],
            "bình thạnh": ["Quận 2", "Quận 3", "Quận 12"],
            "gò vấp": ["Quận 12", "Tân Bình", "Bình Thạnh"],
            "tân bình": ["Quận 10", "Quận 11", "Gò Vấp"],
            "tân phú": ["Quận 6", "Quận 12", "Bình Tân"],
            "thủ đức": ["Quận 2", "Quận 9", "Bình Thạnh"],
            "bình tân": ["Quận 8", "Tân Phú", "Bình Chánh"],
        }

        district_lower = district.lower()
        return nearby_map.get(district_lower, ["Quận 1", "Quận 7", "Thủ Đức"])

    async def _generate_quality_response(self, query: str, results: List[Dict], requirements: Dict, evaluation: Dict) -> str:
        """
        Generate response with quality assessment and honest feedback
        """
        try:
            if evaluation["quality_score"] >= 0.8:
                # Excellent match
                intro = f"Tôi đã tìm thấy {evaluation['match_count']} bất động sản **rất phù hợp** với yêu cầu của bạn:\n"
            elif evaluation["quality_score"] >= 0.6:
                # Good match
                intro = f"Tôi tìm thấy {evaluation['match_count']}/{evaluation['total_count']} bất động sản phù hợp với yêu cầu của bạn:\n"
            else:
                # Poor match - should have asked clarification instead
                intro = f"Tìm thấy {evaluation['total_count']} BDS, nhưng chỉ {evaluation['match_count']} BDS phù hợp một phần:\n"

            response_parts = [intro]

            # Show matching results first
            shown = 0
            for i, prop in enumerate(results):
                if shown >= 3:
                    break

                # Quick match check
                matches_district = True
                if requirements.get("district"):
                    prop_district = str(prop.get("district", "")).lower()
                    required_district = requirements["district"].lower()
                    import re
                    required_num = re.search(r'\d+', required_district)
                    prop_num = re.search(r'\d+', prop_district)
                    if required_num and prop_num:
                        matches_district = (required_num.group() == prop_num.group())

                # Prioritize matching properties
                if matches_district or shown < 2:
                    title = prop.get("title", "Không có tiêu đề")
                    price = prop.get("price_display", prop.get("price", "Liên hệ"))
                    area = prop.get("area", "N/A")
                    location = prop.get("district", prop.get("region", "N/A"))

                    response_parts.append(
                        f"\n{shown + 1}. **{title}**\n"
                        f"   - Giá: {price}\n"
                        f"   - Diện tích: {area} m²\n"
                        f"   - Khu vực: {location}"
                    )
                    shown += 1

            if evaluation["total_count"] > shown:
                response_parts.append(f"\n\n...và {evaluation['total_count'] - shown} BDS khác.")

            # Add honest feedback if quality is not perfect
            if evaluation["quality_score"] < 0.8 and evaluation.get("missing_criteria"):
                response_parts.append(f"\n\n**Lưu ý:** {evaluation['missing_criteria'][0]}")
                response_parts.append(f"\nBạn có thể cung cấp thêm thông tin để tôi tìm chính xác hơn không?")

            return "".join(response_parts)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Response generation failed: {e}")
            return await self._generate_search_response(query, results, "search")

    async def _init_db_pool(self):
        """Initialize PostgreSQL connection pool for conversation memory"""
        try:
            self.db_pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=2,
                max_size=10
            )
            self.logger.info(f"{LogEmoji.SUCCESS} PostgreSQL pool initialized for conversation memory")
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to initialize PostgreSQL pool: {e}")
            self.logger.warning(f"{LogEmoji.WARNING} Conversation memory will not be available")

    async def _get_conversation_history(self, user_id: str, conversation_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Retrieve conversation history from PostgreSQL"""
        if not self.db_pool:
            return []

        try:
            # Use conversation_id if provided, otherwise use user_id for latest conversation
            if not conversation_id:
                conversation_id = user_id  # Use user_id as conversation_id for simplicity

            # Convert string IDs to deterministic UUIDs
            conv_uuid = self._string_to_uuid(conversation_id)

            async with self.db_pool.acquire() as conn:
                # Get last N messages from conversation
                rows = await conn.fetch(
                    """
                    SELECT role, content, created_at
                    FROM messages
                    WHERE conversation_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    conv_uuid,
                    limit
                )

                # Reverse to chronological order
                messages = []
                for row in reversed(rows):
                    messages.append({
                        "role": row['role'],
                        "content": row['content']
                    })

                return messages

        except Exception as e:
            self.logger.warning(f"{LogEmoji.WARNING} Failed to retrieve conversation history: {e}")
            return []

    async def _save_message(self, user_id: str, conversation_id: str, role: str, content: str, metadata: Dict = None):
        """Save message to PostgreSQL conversation history"""
        if not self.db_pool:
            return

        try:
            # Convert string IDs to deterministic UUIDs
            user_uuid = self._string_to_uuid(user_id)
            conv_uuid = self._string_to_uuid(conversation_id)

            async with self.db_pool.acquire() as conn:
                # Ensure user exists first (required for foreign key constraint)
                await conn.execute(
                    """
                    INSERT INTO users (user_id, email, created_at)
                    VALUES ($1, $2, NOW())
                    ON CONFLICT (user_id) DO NOTHING
                    """,
                    user_uuid,
                    f"{user_id}@system.local"  # Placeholder email for system-generated users
                )

                # Ensure conversation exists (idempotent)
                await conn.execute(
                    """
                    INSERT INTO conversations (conversation_id, user_id, created_at, updated_at)
                    VALUES ($1, $2, NOW(), NOW())
                    ON CONFLICT (conversation_id) DO NOTHING
                    """,
                    conv_uuid,
                    user_uuid
                )

                # Insert message
                await conn.execute(
                    """
                    INSERT INTO messages (conversation_id, role, content, metadata, created_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    """,
                    conv_uuid,
                    role,
                    content,
                    json.dumps(metadata or {})
                )

        except Exception as e:
            self.logger.warning(f"{LogEmoji.WARNING} Failed to save message: {e}")

    async def on_shutdown(self):
        """Cleanup"""
        if self.db_pool:
            await self.db_pool.close()
        await self.http_client.aclose()
        await super().on_shutdown()


if __name__ == "__main__":
    service = Orchestrator()
    service.run()

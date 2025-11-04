"""
Orchestrator - CTO Architecture Implementation
Intelligent agent with Classification-based routing and ReAct loop
WITH CONVERSATION MEMORY CONTEXT
"""
import time
import json
import uuid
import os  # MEDIUM FIX Bug#25: Needed for environment variable access
import asyncio  # CRITICAL FIX: Missing import for asyncio.sleep in retry logic
from typing import Dict, Any, List, Optional
import httpx
import asyncpg
from datetime import datetime
from fastapi.responses import StreamingResponse

# HIGH PRIORITY FIX: Add retry logic and circuit breaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pybreaker import CircuitBreaker, CircuitBreakerError

from core.base_service import BaseService
from shared.models.orchestrator import (
    OrchestrationRequest, OrchestrationResponse, IntentType,
    IntentDetectionResult, RoutingDecision
)
from shared.models.core_gateway import LLMRequest, Message, ModelType, FileAttachment
from shared.utils.logger import LogEmoji
from shared.config import settings

# NEW: Import ReAct components (Phase 1-3)
# FIX BUG#2+#4: Add project root to path for module imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from services.orchestrator.knowledge_base import KnowledgeBase
from services.orchestrator.ambiguity_detector import AmbiguityDetector
from services.orchestrator.reasoning_engine import ReasoningEngine


class Orchestrator(BaseService):
    """
    Orchestrator Service - CTO Architecture
    80% of system intelligence - ReAct agent pattern
    """

    def __init__(self):
        super().__init__(
            name="orchestrator",
            version="3.1.0",  # v3.1 with retry logic, connection pooling, circuit breakers
            capabilities=["orchestration", "classification_routing", "react_agent", "conversation_memory", "circuit_breaker", "retry_logic"],
            port=8080
        )

        # HIGH PRIORITY FIX: Configure HTTP client with connection pooling
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            limits=httpx.Limits(
                max_keepalive_connections=20,  # Reuse connections
                max_connections=100,  # Total connection pool size
                keepalive_expiry=30.0  # Keep connections alive for 30s
            )
        )

        # Service URLs
        self.core_gateway_url = settings.get_core_gateway_url()
        self.classification_url = "http://classification:8080"
        self.extraction_url = "http://attribute-extraction:8080"
        self.db_gateway_url = "http://db-gateway:8080"

        # HIGH PRIORITY FIX: Circuit breakers for external services
        self.core_gateway_breaker = CircuitBreaker(
            fail_max=5,  # Open circuit after 5 failures
            reset_timeout=60  # Try again after 60 seconds
        )
        self.db_gateway_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

        # PostgreSQL connection pool for conversation memory
        self.db_pool = None

        self.logger.info(f"{LogEmoji.INFO} CTO Architecture Mode Enabled")
        self.logger.info(f"{LogEmoji.INFO} Conversation Memory: PostgreSQL")
        self.logger.info(f"{LogEmoji.INFO} Connection Pooling: Enabled (max=100, keepalive=20)")
        self.logger.info(f"{LogEmoji.INFO} Circuit Breakers: Enabled (fail_max=5, timeout=60s)")

        # UUID v5 namespace for generating deterministic UUIDs from string IDs
        self.uuid_namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace

        # NEW: Phase 1-3 components (Codex-inspired reasoning)
        self.knowledge_base = KnowledgeBase(knowledge_dir="knowledge")
        self.ambiguity_detector = AmbiguityDetector()
        self.reasoning_engine = ReasoningEngine(
            core_gateway_url=self.core_gateway_url,
            rag_service_url="http://rag-service:8080",
            db_gateway_url=self.db_gateway_url,
            http_client=self.http_client,
            logger=self.logger
        )

        self.logger.info(f"{LogEmoji.SUCCESS} ReAct Reasoning Engine Initialized (Codex-style)")
        self.logger.info(f"{LogEmoji.SUCCESS} Knowledge Base Loaded: PROPERTIES.md + LOCATIONS.md")
        self.logger.info(f"{LogEmoji.SUCCESS} Ambiguity Detector Ready")

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

                # MEDIUM FIX Bug#1: Generate request ID for distributed tracing
                request_id = str(uuid.uuid4())[:8]  # Short ID for readability

                # Log multimodal request with request ID
                if request.has_files():
                    self.logger.info(
                        f"{LogEmoji.AI} [{request_id}] Multimodal Query: '{request.query}' + {len(request.files)} file(s), user={request.user_id}"
                    )
                else:
                    self.logger.info(
                        f"{LogEmoji.TARGET} [{request_id}] Query: '{request.query}', user={request.user_id}"
                    )

                # Step 0: Get conversation history (MEMORY CONTEXT)
                # FIX BUG: Define conversation_id before conditional blocks
                conversation_id = request.conversation_id or request.user_id

                # If request is from Open WebUI, use history from request metadata
                # Open WebUI already sends full conversation history in messages
                if request.metadata and request.metadata.get("from_open_webui"):
                    history = request.metadata.get("conversation_history", [])
                    if history:
                        self.logger.info(f"{LogEmoji.INFO} [{request_id}] Using {len(history)} messages from Open WebUI request")
                else:
                    # For direct API calls, fetch from PostgreSQL
                    history = await self._get_conversation_history(request.user_id, conversation_id, limit=10)
                    if history:
                        self.logger.info(f"{LogEmoji.INFO} [{request_id}] Retrieved {len(history)} messages from PostgreSQL")

                # Step 1: Detect intent (simple keyword-based for now, files → chat for analysis)
                if request.has_files():
                    # Images/documents → Use vision model for analysis
                    intent = "chat"  # Vision analysis goes through chat path
                    self.logger.info(f"{LogEmoji.AI} [{request_id}] Intent: {intent} (multimodal analysis)")
                else:
                    intent = self._detect_intent_simple(request.query)
                    self.logger.info(f"{LogEmoji.AI} [{request_id}] Intent: {intent}")

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
                        "files_count": len(request.files) if request.files else 0,
                        "request_id": request_id  # MEDIUM FIX Bug#1: Include request ID for tracing
                    }
                )

            except (httpx.HTTPError, httpx.TimeoutException) as e:
                # CRITICAL FIX: Handle expected network errors
                self.logger.error(f"{LogEmoji.ERROR} Network error during orchestration: {e}", exc_info=True)
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response="Xin lỗi, hệ thống đang gặp sự cố kết nối. Vui lòng thử lại sau.",
                    service_used="none",
                    execution_time_ms=0.0
                )
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                # CRITICAL FIX: Handle data validation errors
                self.logger.error(f"{LogEmoji.ERROR} Data validation error: {e}", exc_info=True)
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response="Xin lỗi, đã xảy ra lỗi xử lý dữ liệu. Vui lòng thử lại.",
                    service_used="none",
                    execution_time_ms=0.0
                )
            except Exception as e:
                # CRITICAL FIX: Log unexpected errors but don't expose details to users
                self.logger.critical(f"{LogEmoji.ERROR} Unexpected orchestration error: {e}", exc_info=True)
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response="Xin lỗi, đã xảy ra lỗi không xác định. Vui lòng liên hệ hỗ trợ.",
                    service_used="none",
                    execution_time_ms=0.0
                )

        @self.app.post("/orchestrate/v2", response_model=OrchestrationResponse)
        async def orchestrate_v2(request: OrchestrationRequest):
            """
            NEW: Enhanced orchestration with full ReAct reasoning (Codex-inspired)
            Phase 1-3: Reasoning + Knowledge + Ambiguity Detection
            """
            try:
                start_time = time.time()
                request_id = str(uuid.uuid4())[:8]

                self.logger.info(f"{LogEmoji.AI} [ReAct-v2] [{request_id}] Query: '{request.query}'")

                # FIX BUG #4: Validate and truncate very long queries
                MAX_QUERY_LENGTH = 500
                original_query = request.query
                if len(original_query) > MAX_QUERY_LENGTH:
                    request.query = original_query[:MAX_QUERY_LENGTH]
                    truncation_warning = f"Query truncated from {len(original_query)} to {MAX_QUERY_LENGTH} chars"
                    self.logger.warning(f"{LogEmoji.WARNING} [ReAct-v2] {truncation_warning}")

                # Step 0: Get conversation history
                conversation_id = request.conversation_id or request.user_id
                if request.metadata and request.metadata.get("from_open_webui"):
                    history = request.metadata.get("conversation_history", [])
                else:
                    history = await self._get_conversation_history(request.user_id, conversation_id, limit=10)

                # Step 1: Detect intent
                intent = "chat" if request.has_files() else self._detect_intent_simple(request.query)
                self.logger.info(f"{LogEmoji.AI} [ReAct-v2] Intent: {intent}")

                # Step 2: Knowledge Expansion (Phase 2)
                knowledge_expansion = await self.knowledge_base.expand_query(request.query)
                if knowledge_expansion.expanded_terms:
                    self.logger.info(
                        f"{LogEmoji.INFO} [ReAct-v2] Expanded with domain knowledge: "
                        f"{len(knowledge_expansion.expanded_terms)} terms, "
                        f"{len(knowledge_expansion.filters)} filters"
                    )

                # Step 3: Ambiguity Detection (Phase 1)
                ambiguity_result = await self.ambiguity_detector.detect_ambiguities(request.query)
                if ambiguity_result.has_ambiguity:
                    self.logger.warning(
                        f"{LogEmoji.WARNING} [ReAct-v2] Ambiguities detected: "
                        f"{len(ambiguity_result.clarifications)} questions"
                    )

                # Step 4: Execute ReAct Loop (Phase 3)
                reasoning_chain = await self.reasoning_engine.execute_react_loop(
                    query=request.query,
                    intent=intent,
                    history=history,
                    knowledge_expansion=knowledge_expansion,
                    ambiguity_result=ambiguity_result,
                    files=request.files
                )

                # Step 5: Synthesize final response
                response_text = await self.reasoning_engine.synthesize_response(reasoning_chain)

                # Step 6: Save to conversation memory
                await self._save_message(request.user_id, conversation_id, "user", request.query)
                await self._save_message(
                    request.user_id,
                    conversation_id,
                    "assistant",
                    response_text,
                    metadata={
                        "intent": intent,
                        "reasoning_steps": len(reasoning_chain.steps),
                        "confidence": reasoning_chain.overall_confidence
                    }
                )

                execution_time = (time.time() - start_time) * 1000

                # Determine if clarification needed
                needs_clarification = (
                    ambiguity_result.has_ambiguity and
                    self.ambiguity_detector.should_clarify(ambiguity_result)
                )

                return OrchestrationResponse(
                    intent=IntentType.SEARCH if intent == "search" else IntentType.CHAT,
                    confidence=reasoning_chain.overall_confidence,
                    response=response_text,
                    service_used="react_reasoning_engine_v2",
                    execution_time_ms=execution_time,
                    metadata={
                        "flow": "react_codex_inspired",
                        "request_id": request_id,
                        "reasoning_steps": len(reasoning_chain.steps),
                        "expanded_terms": len(knowledge_expansion.expanded_terms),
                        "has_ambiguity": ambiguity_result.has_ambiguity
                    },
                    # NEW FIELDS (Phase 1-3)
                    reasoning_chain=reasoning_chain,
                    needs_clarification=needs_clarification,
                    ambiguity_result=ambiguity_result if needs_clarification else None,
                    knowledge_expansion=knowledge_expansion
                )

            except Exception as e:
                self.logger.critical(f"{LogEmoji.ERROR} [ReAct-v2] Error: {e}", exc_info=True)
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response="Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại.",
                    service_used="react_v2_error",
                    execution_time_ms=0.0
                )

        @self.app.post("/orchestrate/v2/stream")
        async def orchestrate_v2_stream(request: OrchestrationRequest):
            """
            NEW: Streaming version of ReAct reasoning
            Returns Server-Sent Events (SSE) for real-time reasoning transparency
            """
            async def event_generator():
                try:
                    request_id = str(uuid.uuid4())[:8]

                    # Send initial event
                    yield f"data: {json.dumps({'type': 'start', 'request_id': request_id})}\n\n"

                    # Get history
                    conversation_id = request.conversation_id or request.user_id
                    if request.metadata and request.metadata.get("from_open_webui"):
                        history = request.metadata.get("conversation_history", [])
                    else:
                        history = await self._get_conversation_history(request.user_id, conversation_id, limit=10)

                    # Detect intent
                    intent = "chat" if request.has_files() else self._detect_intent_simple(request.query)
                    yield f"data: {json.dumps({'type': 'intent', 'intent': intent})}\n\n"

                    # Knowledge expansion
                    yield f"data: {json.dumps({'type': 'thinking', 'stage': 'knowledge_expansion', 'message': 'Expanding query with domain knowledge...'})}\n\n"
                    knowledge_expansion = await self.knowledge_base.expand_query(request.query)

                    if knowledge_expansion.expanded_terms:
                        yield f"data: {json.dumps({'type': 'knowledge', 'expanded_terms': knowledge_expansion.expanded_terms, 'filters': knowledge_expansion.filters})}\n\n"

                    # Ambiguity detection
                    yield f"data: {json.dumps({'type': 'thinking', 'stage': 'ambiguity_check', 'message': 'Checking for ambiguities...'})}\n\n"
                    ambiguity_result = await self.ambiguity_detector.detect_ambiguities(request.query)

                    if ambiguity_result.has_ambiguity:
                        clarifications = [{"question": c.question, "options": c.options} for c in ambiguity_result.clarifications]
                        yield f"data: {json.dumps({'type': 'ambiguity', 'clarifications': clarifications})}\n\n"

                    # Execute ReAct loop
                    yield f"data: {json.dumps({'type': 'thinking', 'stage': 'react_execution', 'message': 'Executing ReAct reasoning loop...'})}\n\n"

                    reasoning_chain = await self.reasoning_engine.execute_react_loop(
                        query=request.query,
                        intent=intent,
                        history=history,
                        knowledge_expansion=knowledge_expansion,
                        ambiguity_result=ambiguity_result,
                        files=request.files
                    )

                    # Stream reasoning steps
                    for i, step in enumerate(reasoning_chain.steps):
                        step_data = {
                            'type': 'reasoning_step',
                            'step_number': i + 1,
                            'thought': step.thought.thought,
                            'stage': step.thought.stage,
                            'confidence': step.thought.confidence
                        }

                        if step.action:
                            step_data['action'] = {
                                'tool': step.action.tool_name,
                                'reason': step.action.reason
                            }

                        if step.observation:
                            step_data['observation'] = {
                                'success': step.observation.success,
                                'insight': step.observation.insight
                            }

                        yield f"data: {json.dumps(step_data)}\n\n"
                        await asyncio.sleep(0.1)  # Small delay for better UX

                    # Final response
                    response_text = await self.reasoning_engine.synthesize_response(reasoning_chain)

                    yield f"data: {json.dumps({'type': 'response', 'content': response_text, 'confidence': reasoning_chain.overall_confidence})}\n\n"

                    # Summary
                    summary = {
                        'type': 'complete',
                        'total_steps': len(reasoning_chain.steps),
                        'confidence': reasoning_chain.overall_confidence,
                        'expanded_terms': len(knowledge_expansion.expanded_terms),
                        'has_ambiguity': ambiguity_result.has_ambiguity
                    }
                    yield f"data: {json.dumps(summary)}\n\n"

                    # Save to memory
                    await self._save_message(request.user_id, conversation_id, "user", request.query)
                    await self._save_message(request.user_id, conversation_id, "assistant", response_text)

                except Exception as e:
                    self.logger.error(f"{LogEmoji.ERROR} Streaming error: {e}", exc_info=True)
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no"
                }
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
                        "parent": None,
                        "description": "REE AI Assistant - Trợ lý bất động sản thông minh"
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

                # FIX BUG: Open WebUI sends FULL messages history
                # Don't fetch from PostgreSQL again - use messages from request
                # Extract conversation history (exclude system messages and last user message)
                conversation_history = []
                for msg in messages:
                    # Skip system messages and the current user message (already in user_message)
                    if msg.get("role") != "system" and msg.get("content", "") != user_message:
                        conversation_history.append({
                            "role": msg.get("role"),
                            "content": msg.get("content", "")
                        })

                orch_request = OrchestrationRequest(
                    user_id=request.get("user", "anonymous"),
                    query=user_message,
                    conversation_id=None,
                    metadata={
                        "messages": messages,
                        "has_files": len(files) > 0,
                        "files": [f.filename for f in files],
                        "from_open_webui": True,  # Flag to indicate this is from Open WebUI
                        "conversation_history": conversation_history  # Pass history from Open WebUI
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
                # CRITICAL FIX: Don't expose internal error details to API consumers
                self.logger.error(f"{LogEmoji.ERROR} OpenAI chat failed: {e}", exc_info=True)
                return {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "ree-ai-orchestrator-v3-multimodal",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Xin lỗi, hệ thống đang gặp sự cố. Vui lòng thử lại sau."
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
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
            self.logger.info(f"{LogEmoji.AI} [ReAct Agent] Starting INTELLIGENT search with query: '{query}'")

            # Enrich query with conversation context if available
            enriched_query = await self._enrich_query_with_context(query, history or [])

            # MEDIUM FIX Bug#15: Use configurable max iterations
            max_iterations = settings.MAX_REACT_ITERATIONS  # Default: 2 (1 original + 1 refine)
            current_query = enriched_query
            best_results = []  # Keep track of BEST results across iterations for clarification
            best_evaluation = None
            requirements = None  # Will be extracted in each iteration
            consecutive_no_results = 0  # Track consecutive iterations with 0 results for early stop

            for iteration in range(max_iterations):
                self.logger.info(f"{LogEmoji.INFO} [ReAct Agent] ========== Iteration {iteration + 1}/{max_iterations} ==========")

                # STEP 1: REASONING - Extract requirements using AI service (fresh each iteration)
                requirements = await self._analyze_query_requirements(current_query, history, iteration=iteration+1)

                # STEP 2: ACT - Execute search
                results = await self._execute_search_internal(current_query)

                # STEP 3: EVALUATE - Check result quality
                evaluation = await self._evaluate_results(results, requirements)

                # Track consecutive no results for early stop
                if not results:
                    consecutive_no_results += 1
                    self.logger.warning(f"{LogEmoji.WARNING} [ReAct Agent] No results found ({consecutive_no_results} consecutive)")

                    # INTELLIGENT BEHAVIOR: Progressive filter relaxation
                    if consecutive_no_results >= 2:
                        self.logger.info(f"{LogEmoji.INFO} [ReAct Agent] Investigating... Trying relaxed search strategies")

                        # Strategy 1: Try with ONLY location filters (remove property_type, price, bedrooms)
                        self.logger.info(f"{LogEmoji.INFO} [ReAct Strategy 1] Search with location only...")
                        relaxed_results = await self._try_location_only_search(requirements)

                        if relaxed_results:
                            self.logger.info(f"{LogEmoji.SUCCESS} [ReAct Strategy 1] Found {len(relaxed_results)} properties in requested area")
                            # Return suggestions with disclaimer
                            return await self._generate_suggestions_response(query, relaxed_results, requirements)

                        # Strategy 2: Semantic search fallback
                        self.logger.info(f"{LogEmoji.INFO} [ReAct Strategy 2] Trying semantic search...")
                        semantic_results = await self._execute_semantic_search(query)

                        if semantic_results:
                            self.logger.info(f"{LogEmoji.SUCCESS} [ReAct Strategy 2] Semantic search found {len(semantic_results)} results")
                            return await self._generate_suggestions_response(query, semantic_results, requirements)

                        # Strategy 3: Give up gracefully
                        self.logger.warning(f"{LogEmoji.WARNING} [ReAct Agent] All strategies failed")
                        return "Xin lỗi, tôi không tìm thấy bất động sản phù hợp với yêu cầu của bạn. Bạn có thể cung cấp thêm thông tin hoặc mở rộng tiêu chí tìm kiếm không?"
                else:
                    consecutive_no_results = 0  # Reset counter when results found

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

            # MEDIUM FIX Bug#14: Use configurable timeout
            classification_response = await self.http_client.post(
                f"{self.classification_url}/classify",
                json={"query": query, "context": None},
                timeout=settings.CLASSIFICATION_TIMEOUT
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
                timeout=settings.EXTRACTION_TIMEOUT  # MEDIUM FIX Bug#14
            )

            if extraction_response.status_code != 200:
                return []

            extraction = extraction_response.json()
            entities = extraction.get("entities", {})

            # FIX BUG #4: Normalize district to match OpenSearch data format
            # District filtering: KEEP ORIGINAL FORMAT (OpenSearch has "Quận 7", not "7")
            # DB Gateway uses term query requiring exact match
            # FIX: Don't strip "Quận " prefix - keep as-is
            if "district" in entities and entities["district"]:
                district = entities["district"]
                self.logger.info(f"{LogEmoji.INFO} [Filter] District: '{district}' (no normalization - exact match required)")

            # FIX PRICE FILTER BUG: Normalize price field names to match SearchFilters model
            # Attribute Extraction returns "price_min"/"price_max" but SearchFilters expects "min_price"/"max_price"
            if "price_min" in entities:
                entities["min_price"] = entities.pop("price_min")
                self.logger.info(f"{LogEmoji.INFO} [Filter Normalization] Renamed price_min → min_price: {entities['min_price']}")
            if "price_max" in entities:
                entities["max_price"] = entities.pop("price_max")
                self.logger.info(f"{LogEmoji.INFO} [Filter Normalization] Renamed price_max → max_price: {entities['max_price']}")

            # FIX EMPTY PROPERTY_TYPE BUG: Remove vague property_type filters
            # Database has empty property_type="" for most properties, so vague terms cause 0 results
            if "property_type" in entities:
                vague_terms = ["nhà", "bds", "bất động sản", "property", "real estate", ""]
                property_type_lower = entities["property_type"].lower().strip()
                if property_type_lower in vague_terms or not property_type_lower:
                    self.logger.info(f"{LogEmoji.WARNING} [Filter Normalization] Removing vague property_type='{entities['property_type']}' (DB has empty property_type field)")
                    del entities["property_type"]

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

    async def _try_location_only_search(self, requirements: Dict) -> List[Dict]:
        """
        INTELLIGENT STRATEGY: Search with location filters ONLY
        Remove property_type, price, bedrooms to get broader results
        Used when strict filters return 0 results
        """
        try:
            # Extract ONLY location filters from requirements
            location_filters = {}

            if requirements.get("district"):
                district = requirements["district"]
                # KEEP ORIGINAL FORMAT - don't strip "Quận " prefix (OpenSearch has "Quận 7")
                location_filters["district"] = district

            if requirements.get("city"):
                location_filters["city"] = requirements["city"]

            if not location_filters:
                self.logger.warning(f"{LogEmoji.WARNING} No location filters found in requirements")
                return []

            self.logger.info(f"{LogEmoji.INFO} [Location-Only Search] Filters: {location_filters}")

            # Search with location ONLY
            search_response = await self.http_client.post(
                f"{self.db_gateway_url}/search",
                json={
                    "query": "",  # Empty query, rely on filters
                    "filters": location_filters,
                    "limit": 10  # Get more results for suggestions
                },
                timeout=30.0
            )

            if search_response.status_code != 200:
                return []

            search_results = search_response.json()
            results = search_results.get("results", [])

            self.logger.info(f"{LogEmoji.SUCCESS} [Location-Only Search] Found {len(results)} properties")
            return results

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Location-only search failed: {e}")
            return []

    async def _generate_suggestions_response(self, query: str, results: List[Dict], requirements: Dict) -> str:
        """
        Generate response with suggestions and disclaimer
        Used when relaxed search found results but query was incomplete
        """
        try:
            # Build context about what filters were relaxed
            location = requirements.get("district", "khu vực này")

            # Build property list
            properties_text = []
            for idx, prop in enumerate(results[:5], 1):  # Top 5 only
                title = prop.get("title", "Bất động sản")
                price = prop.get("price", "Liên hệ")
                area = prop.get("area", "")
                bedrooms = prop.get("bedrooms")

                prop_desc = f"{idx}. {title}\n"
                prop_desc += f"   💰 Giá: {price}"
                if bedrooms:
                    prop_desc += f" | 🛏️ {bedrooms} phòng ngủ"
                if area:
                    prop_desc += f" | 📐 {area}"

                properties_text.append(prop_desc)

            properties_str = "\n\n".join(properties_text)

            # Generate response với disclaimer
            response = f"""📍 Tôi tìm thấy {len(results)} bất động sản ở {location}. Đây là một số gợi ý:

{properties_str}

💡 **Gợi ý:** Để tôi tìm chính xác hơn, bạn có thể cho biết thêm:
- Loại hình: căn hộ, nhà phố, biệt thự?
- Ngân sách: khoảng bao nhiêu tỷ?
- Diện tích hoặc số phòng ngủ mong muốn?

Bạn quan tâm căn nào? Hoặc muốn tìm với tiêu chí cụ thể hơn?"""

            return response

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to generate suggestions response: {e}")
            return "Tôi tìm thấy một số bất động sản phù hợp. Bạn có thể cung cấp thêm thông tin để tôi tìm chính xác hơn?"

    async def _handle_filter_search(self, query: str) -> str:
        """Filter mode: Extraction → Document search"""
        try:
            # Step 2a: Attribute Extraction
            self.logger.info(f"{LogEmoji.AI} Step 2a: Attribute Extraction")

            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query",
                json={"query": query, "intent": "SEARCH"},
                timeout=settings.EXTRACTION_TIMEOUT  # MEDIUM FIX Bug#14
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
                f"   - Diện tích: {self._format_area(area)}\n"
                f"   - Khu vực: {location}"
            )

        if len(results) > 3:
            response_parts.append(f"\n\n...và {len(results) - 3} bất động sản khác.")

        return "".join(response_parts)

    async def _handle_chat(self, query: str, history: List[Dict] = None, files: Optional[List[FileAttachment]] = None) -> str:
        """
        Handle general chat (non-search) with conversation context and multimodal support

        HIGH PRIORITY FIX: Added type hints for better IDE support
        """
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

HƯỚNG DẪN SỬ DỤNG LỊCH SỬ HỘI THOẠI:

1. **Phân biệt loại câu hỏi:**
   - Greeting/Chào hỏi (xin chào, hi, cảm ơn): TRẢ LỜI ĐƠN GIẢN, không reference context cũ
   - Câu hỏi mới (tìm nhà ở X, giá bao nhiêu): TRẢ LỜI TRỰC TIẾP theo câu hỏi
   - Câu hỏi follow-up (căn đó như thế nào?, còn view không?): SỬ DỤNG context trước đó

2. **Khi nào KHÔNG sử dụng context:**
   - User nói "xin chào", "hi", "hello", "cảm ơn"
   - User bắt đầu topic hoàn toàn mới
   - User hỏi về thứ không liên quan context cũ

3. **Khi nào SỬ DỤNG context:**
   - User hỏi "căn đó", "dự án đó", "khu vực đó"
   - User hỏi chi tiết về property vừa tìm
   - User hỏi follow-up rõ ràng

VÍ DỤ TỐT:
- User trước: "Tìm nhà ở Quận 2"
- User hiện tại: "Xin chào" → Response: "Xin chào! Tôi là trợ lý bất động sản. Tôi có thể giúp gì cho bạn?" (KHÔNG nhắc Quận 2)
- User hiện tại: "Căn đó có view không?" → Response: "Căn hộ ở Quận 2 mà bạn vừa hỏi..." (CÓ reference)

LUÔN trả lời phù hợp với ngữ cảnh câu hỏi hiện tại."""

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

            # FIX BUG #7: Add retry logic and better error logging
            max_retries = 2
            for attempt in range(max_retries):
                try:
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
                        # Log detailed error response
                        error_body = response.text
                        self.logger.error(
                            f"{LogEmoji.ERROR} Core Gateway error (attempt {attempt+1}/{max_retries}): "
                            f"status={response.status_code}, body={error_body[:200]}"
                        )

                        # HIGH PRIORITY FIX: Exponential backoff for retries
                        if attempt < max_retries - 1 and response.status_code >= 500:
                            backoff_time = 2 ** attempt  # 1s, 2s, 4s...
                            self.logger.info(f"{LogEmoji.WARNING} Retrying after {backoff_time}s...")
                            await asyncio.sleep(backoff_time)
                            continue

                        # Give up after retries
                        return "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu."

                except httpx.TimeoutException:
                    self.logger.error(f"{LogEmoji.ERROR} Core Gateway timeout (attempt {attempt+1}/{max_retries})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    return "Xin lỗi, tôi gặp sự cố khi xử lý yêu cầu (timeout)."

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Chat failed: {e}")
            import traceback
            traceback.print_exc()
            return f"Xin lỗi, đã xảy ra lỗi: {str(e)}"

    # ========================================
    # ReAct Agent Pattern Methods
    # ========================================

    async def _analyze_query_requirements(self, query: str, history: List[Dict] = None, iteration: int = 1) -> Dict:
        """
        REASONING Step: Extract structured requirements using ATTRIBUTE EXTRACTION SERVICE

        NO MORE REGEX! Use AI service for intelligent extraction.

        Args:
            query: User query
            history: Conversation history (for context)
            iteration: Current iteration number (for progressive refinement)

        Returns:
            {
                "property_type": str,
                "bedrooms": int or None,
                "district": str or None,
                "city": str or None,
                "price_min": float or None,
                "price_max": float or None,
                "special_requirements": List[str],
                "raw_entities": Dict  # Raw extraction from service
            }
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [ReAct-Reasoning] Iteration {iteration}: Calling Attribute Extraction service...")

            # Call Attribute Extraction service
            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query",
                json={
                    "query": query,
                    "intent": "SEARCH"
                },
                timeout=30.0
            )

            if extraction_response.status_code != 200:
                self.logger.warning(f"{LogEmoji.WARNING} Attribute extraction failed, using fallback LLM")
                return await self._fallback_llm_extraction(query)

            extraction_data = extraction_response.json()
            entities = extraction_data.get("entities", {})
            confidence = extraction_data.get("confidence", 0.0)

            self.logger.info(f"{LogEmoji.SUCCESS} [ReAct-Reasoning] Extracted entities (confidence: {confidence:.1%}): {entities}")

            # Infer city from district if city not provided (must await since it's async)
            city = entities.get("city") or entities.get("thanh_pho")
            district = entities.get("district") or entities.get("quan_huyen")

            # FIX: Attribute Extraction sometimes misclassifies city as district
            # If "district" looks like a city name (contains "Thành phố", "TP"), treat it as city
            # ALSO FIX: Handle case where district is a list (multi-district queries)
            if not city and district:
                # Handle both string and list cases
                district_for_check = district if isinstance(district, str) else (district[0] if isinstance(district, list) and len(district) > 0 else "")

                if district_for_check and any(keyword in district_for_check.lower() for keyword in ["thành phố", "tp.", "tp ", "city"]):
                    # This is actually a city, not a district!
                    city = district_for_check.replace("Thành phố", "").replace("TP.", "").replace("TP", "").strip()
                    district = None  # Clear the wrongly classified district
                else:
                    # Infer city from actual district (use first district if it's a list)
                    city = await self._infer_city_from_district(district_for_check)

            # Normalize extracted entities to standard format
            # FIX PRICE FILTER BUG: Use correct field names that match SearchFilters model
            # SearchFilters expects: min_price, max_price (not price_min, price_max)
            requirements = {
                "property_type": entities.get("property_type") or entities.get("loai_hinh"),
                "bedrooms": self._parse_int(entities.get("bedrooms") or entities.get("so_phong_ngu")),
                "district": district,  # Use corrected district (may be None if it was actually a city)
                "city": city,
                "min_price": self._parse_price(entities.get("price_min") or entities.get("gia_min")),
                "max_price": self._parse_price(entities.get("price_max") or entities.get("gia_max")),
                "special_requirements": entities.get("special_requirements", []),
                "raw_entities": entities,
                "extraction_confidence": confidence
            }

            # Log warnings for missing critical fields
            if not requirements.get("city"):
                self.logger.warning(f"{LogEmoji.WARNING} [ReAct-Reasoning] CRITICAL: No city extracted from query!")
            if not requirements.get("property_type"):
                self.logger.warning(f"{LogEmoji.WARNING} [ReAct-Reasoning] No property_type extracted")

            return requirements

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Attribute extraction failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to simple LLM extraction
            return await self._fallback_llm_extraction(query)

    async def _fallback_llm_extraction(self, query: str) -> Dict:
        """Fallback: Simple LLM extraction if Attribute Extraction service fails"""
        try:
            analysis_prompt = f"""Extract real estate search requirements from this Vietnamese query.

Query: "{query}"

Return JSON with these fields:
{{
    "property_type": "căn hộ/nhà phố/biệt thự/đất/shophouse/etc",
    "bedrooms": integer or null,
    "district": "Quận X/Huyện Y" or null,
    "city": "Hồ Chí Minh/Hà Nội/Đà Nẵng/etc" or null,
    "price_min": float (billion VND) or null,
    "price_max": float (billion VND) or null,
    "special_requirements": ["requirement1", "requirement2"]
}}

CRITICAL RULES:
- If query mentions "quận 2/7/9" or "Thủ Đức" → city = "Hồ Chí Minh"
- If query mentions "Cầu Giấy/Đống Đa/Hoàn Kiếm" → city = "Hà Nội"
- Extract city explicitly, do NOT leave null if inferable
- Return ONLY JSON, no explanation

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
                requirements = json.loads(content)
                requirements["extraction_confidence"] = 0.5  # Lower confidence for fallback
                return requirements
            else:
                return {"extraction_confidence": 0.0}

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Fallback LLM extraction failed: {e}")
            return {"extraction_confidence": 0.0}

    def _parse_int(self, value) -> Optional[int]:
        """Safely parse integer from various formats"""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            # MEDIUM FIX Bug#7: Catch specific exceptions and log for debugging
            self.logger.warning(f"{LogEmoji.WARNING} Failed to parse int '{value}': {e}")
            return None

    def _parse_price(self, value) -> Optional[float]:
        """Safely parse price from various formats"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            # MEDIUM FIX Bug#7: Catch specific exceptions and log for debugging
            self.logger.warning(f"{LogEmoji.WARNING} Failed to parse price '{value}': {e}")
            return None

    async def _infer_city_from_district(self, district: Optional[str]) -> Optional[str]:
        """
        INTELLIGENT city inference using LLM geographic knowledge

        NO HARDCODING! Works for ANY location globally:
        - "Quận 2" → "Hồ Chí Minh"
        - "Cầu Giấy" → "Hà Nội"
        - "Sukhumvit" → "Bangkok"
        - "Orchard Road" → "Singapore"

        Uses LLM's built-in geographic knowledge + web search fallback
        """
        if not district:
            return None

        try:
            # Use LLM to infer city from district (works globally!)
            geo_prompt = f"""What city is "{district}" located in?

RULES:
- Return ONLY the city name, nothing else
- Use local language for city name (e.g., "Hồ Chí Minh" not "Ho Chi Minh City")
- If uncertain, return "UNKNOWN"
- Examples:
  * "Quận 2" → "Hồ Chí Minh"
  * "Cầu Giấy" → "Hà Nội"
  * "Sukhumvit" → "Bangkok"
  * "Brooklyn" → "New York"

City name:"""

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": geo_prompt}],
                    "max_tokens": 20,
                    "temperature": 0.0  # Deterministic for geo facts
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                city = data.get("content", "").strip()

                if city and city != "UNKNOWN":
                    self.logger.info(f"{LogEmoji.SUCCESS} [Geo Inference] '{district}' → '{city}'")
                    return city
                else:
                    self.logger.warning(f"{LogEmoji.WARNING} [Geo Inference] Could not infer city for '{district}'")
                    return None
            else:
                return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} City inference failed: {e}")
            return None

    async def _evaluate_results(self, results: List[Dict], requirements: Dict) -> Dict:
        """
        EVALUATE Step: INTELLIGENT evaluation using LLM + rule-based validation

        TWO-LAYER VALIDATION:
        1. CRITICAL CHECKS (instant rejection):
           - City mismatch (HCM vs Hà Nội/Quy Nhơn)
           - Property type semantic mismatch (căn hộ vs shophouse/đất)

        2. SOFT CHECKS (score reduction):
           - District, bedrooms, price, area variations

        Returns:
            {
                "satisfied": bool,
                "match_count": int,
                "total_count": int,
                "match_rate": float,
                "missing_criteria": List[str],
                "quality_score": float,
                "critical_failures": List[str]  # NEW: Critical mismatches
            }
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [ReAct-Evaluate] Intelligent evaluation with LLM...")

            if not results:
                return {
                    "satisfied": False,
                    "match_count": 0,
                    "total_count": 0,
                    "match_rate": 0.0,
                    "missing_criteria": ["No results found"],
                    "quality_score": 0.0,
                    "critical_failures": []
                }

            # LAYER 1: LLM-based semantic validation (CRITICAL)
            semantic_validation = await self._validate_results_with_llm(results, requirements)

            if not semantic_validation["semantically_valid"]:
                # REJECT immediately if semantic mismatch
                self.logger.warning(f"{LogEmoji.WARNING} [ReAct-Evaluate] CRITICAL: Semantic mismatch detected!")
                return {
                    "satisfied": False,
                    "match_count": 0,
                    "total_count": len(results),
                    "match_rate": 0.0,
                    "missing_criteria": semantic_validation["issues"],
                    "quality_score": 0.0,
                    "critical_failures": semantic_validation["issues"]
                }

            # LAYER 2: Rule-based field validation (if semantic passes)
            match_count = 0
            missing_criteria = []

            for prop in results:
                matches = True

                # Check city (CRITICAL - must match)
                if requirements.get("city"):
                    required_city = requirements["city"].lower()
                    prop_city = str(prop.get("city", "")).lower()

                    # Normalize city names
                    city_aliases = {
                        "hồ chí minh": ["hcm", "sài gòn", "saigon", "tp.hcm", "tphcm"],
                        "hà nội": ["hanoi", "hn"],
                        "đà nẵng": ["da nang", "danang"]
                    }

                    city_match = False
                    for canonical, aliases in city_aliases.items():
                        if canonical in required_city or any(alias in required_city for alias in aliases):
                            if canonical in prop_city or any(alias in prop_city for alias in aliases):
                                city_match = True
                                break

                    if not city_match and required_city not in prop_city and prop_city not in required_city:
                        matches = False
                        self.logger.info(f"{LogEmoji.WARNING} City mismatch: required '{required_city}' but got '{prop_city}'")

                # Check district (IMPORTANT but not critical)
                if requirements.get("district"):
                    required_district = requirements["district"].lower()
                    prop_district = str(prop.get("district", "")).lower()

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

                # Check property type (use LLM semantic validation above)
                # Skip rule-based property type check since LLM handles it better

                # Check price range
                if requirements.get("price_max"):
                    prop_price = prop.get("price")
                    if prop_price:
                        try:
                            price_val = float(prop_price)
                            if price_val > requirements["price_max"] * 1e9:
                                matches = False
                        except:
                            pass

                if matches:
                    match_count += 1

            match_rate = match_count / len(results) if results else 0.0

            # Determine missing criteria
            if match_rate < 0.6:
                if requirements.get("city"):
                    missing_criteria.append(f"Không đủ BDS ở {requirements['city']}")
                if requirements.get("district"):
                    missing_criteria.append(f"Không đủ BDS ở {requirements['district']}")
                if requirements.get("bedrooms"):
                    missing_criteria.append(f"Không đủ BDS có {requirements['bedrooms']} phòng ngủ")
                if requirements.get("special_requirements"):
                    missing_criteria.extend([f"Thiếu: {req}" for req in requirements["special_requirements"]])

            # Quality score: weighted average of semantic + field match
            quality_score = (semantic_validation["confidence"] * 0.4) + (match_rate * 0.6)
            satisfied = quality_score >= 0.6

            evaluation = {
                "satisfied": satisfied,
                "match_count": match_count,
                "total_count": len(results),
                "match_rate": match_rate,
                "missing_criteria": missing_criteria,
                "quality_score": quality_score,
                "critical_failures": []
            }

            self.logger.info(f"{LogEmoji.SUCCESS} [ReAct-Evaluate] Quality: {quality_score:.1%} (semantic: {semantic_validation['confidence']:.1%}, field: {match_rate:.1%})")

            return evaluation

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Evaluation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "satisfied": False,
                "match_count": 0,
                "total_count": len(results) if results else 0,
                "match_rate": 0.0,
                "missing_criteria": [str(e)],
                "quality_score": 0.0,
                "critical_failures": []
            }

    async def _validate_results_with_llm(self, results: List[Dict], requirements: Dict) -> Dict:
        """
        LLM-based semantic validation: "Do these results match what user asked for?"

        This is the INTELLIGENCE layer that prevents:
        - Returning "Quy Nhơn" properties when user asked for "Hồ Chí Minh"
        - Returning "shophouse/đất" when user asked for "căn hộ"
        - Returning "3 bedrooms" when user specifically asked for "2 bedrooms"

        Returns:
            {
                "semantically_valid": bool,  # True if results match requirements
                "confidence": float,  # 0-1 confidence score
                "issues": List[str]  # Critical mismatches found
            }
        """
        try:
            if not results or not requirements:
                return {
                    "semantically_valid": True,
                    "confidence": 0.5,
                    "issues": []
                }

            # Build validation prompt with top 3 results
            validation_prompt = f"""Bạn là trợ lý đánh giá chất lượng kết quả tìm kiếm bất động sản.

**YÊU CẦU CỦA NGƯỜI DÙNG:**
{json.dumps(requirements, ensure_ascii=False, indent=2)}

**KẾT QUẢ TÌM ĐƯỢC (Top 3):**
"""

            for i, prop in enumerate(results[:3], 1):
                validation_prompt += f"""
{i}. Tiêu đề: {prop.get('title', 'N/A')}
   - Loại: {prop.get('property_type', 'N/A')}
   - Khu vực: {prop.get('district', 'N/A')}, {prop.get('city', 'N/A')}
   - Phòng ngủ: {prop.get('bedrooms', 'N/A')}
   - Giá: {prop.get('price', 'N/A')}
"""

            validation_prompt += """

**NHIỆM VỤ:**
Đánh giá xem kết quả có PHÙHỢP NGỮ NGHĨA với yêu cầu không?

**KIỂM TRA CÁC LỖI NGHIÊM TRỌNG:**
1. **City mismatch**: User yêu cầu "Hồ Chí Minh/TP.HCM" nhưng kết quả là "Hà Nội/Quy Nhơn/Đà Nẵng" → LỖI NGHIÊM TRỌNG
2. **Property type mismatch**: User yêu cầu "căn hộ" nhưng kết quả là "shophouse/đất/nhà phố/biệt thự" → LỖI NGHIÊM TRỌNG
3. **Complete irrelevance**: Kết quả hoàn toàn không liên quan đến yêu cầu

**TRƯỜNG HỢP CHẤP NHẬN:**
- User yêu cầu "quận 2" nhưng kết quả là "quận 9" (cùng thành phố) → CHẤP NHẬN (district flexibility)
- User yêu cầu "2 phòng ngủ" nhưng có kết quả "3 phòng ngủ" → CHẤP NHẬN (bedroom flexibility)
- User yêu cầu "căn hộ" và kết quả là "căn hộ/chung cư" → CHẤP NHẬN (synonyms)

**TRẢ LỜI FORMAT JSON:**
{
    "semantically_valid": true/false,
    "confidence": 0.0-1.0,
    "issues": ["Lỗi 1", "Lỗi 2", ...]
}

Chỉ trả về JSON, không giải thích thêm.

JSON:"""

            # Call LLM for semantic validation
            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": validation_prompt}],
                    "max_tokens": 300,
                    "temperature": 0.1  # Low temperature for consistent judgment
                },
                timeout=20.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "{}")

                # Parse JSON response
                try:
                    validation_result = json.loads(content)
                    self.logger.info(
                        f"{LogEmoji.INFO} [LLM Validation] Valid: {validation_result.get('semantically_valid')}, "
                        f"Confidence: {validation_result.get('confidence', 0):.1%}"
                    )

                    if validation_result.get("issues"):
                        for issue in validation_result["issues"]:
                            self.logger.warning(f"{LogEmoji.WARNING} Issue: {issue}")

                    return validation_result

                except json.JSONDecodeError as e:
                    self.logger.warning(f"{LogEmoji.WARNING} Failed to parse LLM validation JSON: {e}")
                    # Fallback: assume valid if can't parse
                    return {
                        "semantically_valid": True,
                        "confidence": 0.5,
                        "issues": []
                    }
            else:
                # LLM failed, use fallback
                return {
                    "semantically_valid": True,
                    "confidence": 0.5,
                    "issues": []
                }

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} LLM validation failed: {e}")
            # Fail-safe: assume valid to not block searches
            return {
                "semantically_valid": True,
                "confidence": 0.5,
                "issues": []
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

            # FIX BUG #6: Handle None city value
            if city is None:
                city = "Hồ Chí Minh"

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
                nearby_districts = await self._get_nearby_districts(district, requirements.get("city"))
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
                        f"   💰 Giá: {price} | 📐 {self._format_area(area)} | 🛏️ {prop_bedrooms} PN\n"
                        f"   📍 {location}\n"
                    )

            # Part 4: Call to Action
            clarification_parts.append("\n💬 Bạn muốn tôi hỗ trợ như thế nào?")

            return "".join(clarification_parts)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Clarification generation failed: {e}")
            return "Xin lỗi, tôi không tìm thấy bất động sản phù hợp chính xác. Bạn có thể cung cấp thêm thông tin để tôi tìm kiếm tốt hơn không?"

    def _format_area(self, area) -> str:
        """
        Format area value to avoid duplicate units.

        Examples:
        - "78" → "78 m²"
        - "78 m²" → "78 m²"
        - "78m²" → "78 m²"
        - 78 → "78 m²"
        """
        if not area or area == "N/A":
            return "N/A"

        # Convert to string
        area_str = str(area).strip()

        # Remove existing m² variations
        area_str = area_str.replace("m²", "").replace("m2", "").strip()

        # Return with proper unit
        return f"{area_str} m²" if area_str else "N/A"

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
            # MEDIUM FIX Bug#17: Use configurable mock statistics
            return {
                "total_in_city": settings.MOCK_PROPERTIES_IN_CITY,
                "total_in_district": 0 if requirements.get("district") == "quận 2" else settings.MOCK_PROPERTIES_IN_DISTRICT
            }
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to get statistics: {e}")
            return {
                "total_in_city": 0,
                "total_in_district": 0
            }

    async def _get_nearby_districts(self, district: str, city: Optional[str] = None) -> List[str]:
        """
        INTELLIGENT nearby districts using LLM geographic knowledge

        NO HARDCODING! Works globally:
        - "Quận 2" (HCM) → ["Quận 9", "Thủ Đức", "Bình Thạnh"]
        - "Brooklyn" (NYC) → ["Queens", "Manhattan"]
        - "Shibuya" (Tokyo) → ["Shinjuku", "Minato"]

        Uses LLM's built-in geographic intelligence
        """
        try:
            location = f"{district}, {city}" if city else district

            nearby_prompt = f"""What are the 3-4 neighboring districts/areas closest to "{location}"?

RULES:
- Return ONLY a comma-separated list of district names
- Use local language names
- Order by proximity (closest first)
- If uncertain, return "UNKNOWN"
- Examples:
  * "Quận 2, Hồ Chí Minh" → "Quận 9, Thủ Đức, Bình Thạnh"
  * "Brooklyn, New York" → "Queens, Manhattan, Staten Island"
  * "Shibuya, Tokyo" → "Shinjuku, Minato, Meguro"

Nearby districts:"""

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": nearby_prompt}],
                    "max_tokens": 50,
                    "temperature": 0.0  # Deterministic for geo facts
                },
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                nearby_str = data.get("content", "").strip()

                if nearby_str and nearby_str != "UNKNOWN":
                    # Parse comma-separated list
                    nearby_list = [d.strip() for d in nearby_str.split(",") if d.strip()]
                    self.logger.info(f"{LogEmoji.SUCCESS} [Nearby Districts] '{district}' → {nearby_list[:3]}")
                    return nearby_list[:3]  # Top 3
                else:
                    return []
            else:
                return []

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Nearby districts inference failed: {e}")
            return []

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
                        f"   - Diện tích: {self._format_area(area)}\n"
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
            # MEDIUM FIX Bug#25: Make connection pool size configurable
            pool_min = int(os.getenv("POSTGRES_POOL_MIN", "2"))
            pool_max = int(os.getenv("POSTGRES_POOL_MAX", "20"))  # Increased default for better concurrency

            self.db_pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=pool_min,
                max_size=pool_max
            )
            self.logger.info(f"{LogEmoji.SUCCESS} DB pool initialized: min={pool_min}, max={pool_max}")
            self.logger.info(f"{LogEmoji.SUCCESS} PostgreSQL pool initialized for conversation memory")
        except Exception as e:
            # CRITICAL FIX: Cleanup partial connections on failure
            self.logger.error(f"{LogEmoji.ERROR} Failed to initialize PostgreSQL pool: {e}", exc_info=True)
            self.logger.warning(f"{LogEmoji.WARNING} Conversation memory will not be available")
            if self.db_pool:
                try:
                    await self.db_pool.close()
                except Exception as cleanup_error:
                    self.logger.error(f"{LogEmoji.ERROR} Pool cleanup failed: {cleanup_error}")
                finally:
                    self.db_pool = None

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
        """Cleanup resources on shutdown"""
        # CRITICAL FIX: Ensure all resources are properly closed even on errors
        try:
            if self.db_pool:
                await self.db_pool.close()
                self.logger.info(f"{LogEmoji.SUCCESS} Database pool closed")
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to close database pool: {e}")

        try:
            await self.http_client.aclose()
            self.logger.info(f"{LogEmoji.SUCCESS} HTTP client closed")
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to close HTTP client: {e}")

        await super().on_shutdown()


if __name__ == "__main__":
    service = Orchestrator()
    service.run()

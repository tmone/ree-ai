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
from langdetect import detect, LangDetectException

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



def load_prompt(filename: str) -> str:
    """Load prompt template from shared/prompts directory"""
    prompt_path = os.path.join(os.path.dirname(__file__), '../../shared/prompts', filename)
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None

# NEW: Import ReAct components (Phase 1-3)
# FIX BUG#2+#4: Add project root to path for module imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# REMOVED: knowledge_base.py - switched to master data approach (shared/data/multilingual_keywords.json)
# from services.orchestrator.knowledge_base import KnowledgeBase
from services.orchestrator.ambiguity_detector import AmbiguityDetector
from services.orchestrator.reasoning_engine import ReasoningEngine
from shared.utils.multilingual_keywords import get_confirmation_keywords, get_frustration_keywords
from shared.utils.i18n import t, auto_detect_language, detect_language_from_header

# ITERATION 1 IMPROVEMENT: Query normalization for better attribute extraction
from shared.utils.query_normalizer import QueryNormalizer


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
        self.classification_url = "http://ree-ai-classification:8080"
        self.extraction_url = "http://ree-ai-attribute-extraction:8080"
        self.completeness_url = "http://ree-ai-completeness:8080"
        self.validation_url = "http://ree-ai-validation:8080"
        self.db_gateway_url = "http://ree-ai-db-gateway:8080"
        self.reranking_url = "http://ree-ai-reranking:8080"  # CTO Priority 4: Re-ranking Service

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
        # REMOVED: knowledge_base - switched to master data approach
        # self.knowledge_base = KnowledgeBase(knowledge_dir="knowledge")
        self.ambiguity_detector = AmbiguityDetector()
        self.reasoning_engine = ReasoningEngine(
            core_gateway_url=self.core_gateway_url,
            rag_service_url="http://rag-service:8080",
            db_gateway_url=self.db_gateway_url,
            http_client=self.http_client,
            logger=self.logger
        )

        # ITERATION 1 IMPROVEMENT: Query normalizer for better attribute extraction
        self.query_normalizer = QueryNormalizer()

        self.logger.info(f"{LogEmoji.SUCCESS} ReAct Reasoning Engine Initialized (Codex-style)")
        self.logger.info(f"{LogEmoji.SUCCESS} Knowledge Base Loaded: PROPERTIES.md + LOCATIONS.md")
        self.logger.info(f"{LogEmoji.SUCCESS} Ambiguity Detector Ready")
        self.logger.info(f"{LogEmoji.SUCCESS} Query Normalizer Ready (handles abbreviations & mixed languages)")

    def _string_to_uuid(self, string_id: str) -> str:
        """Convert string ID to deterministic UUID string using UUID v5"""
        return str(uuid.uuid5(self.uuid_namespace, string_id))

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

                # Step 0: Auto-detect language if not specified
                if not request.language or request.language == "vi":
                    # Try to detect language from query or user profile
                    try:
                        detected_lang = await auto_detect_language(
                            user_id=request.user_id,
                            accept_language=None,  # Not available in this context
                            default=request.language or "vi"
                        )
                        if detected_lang != request.language:
                            request.language = detected_lang
                            self.logger.info(f"{LogEmoji.INFO} [{request_id}] Auto-detected language: {request.language}")
                    except Exception as e:
                        self.logger.warning(f"{LogEmoji.WARNING} [{request_id}] Language detection failed: {e}")
                        request.language = request.language or "vi"
                else:
                    self.logger.info(f"{LogEmoji.INFO} [{request_id}] Using specified language: {request.language}")

                # Step 1: Get conversation history (MEMORY CONTEXT)
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

                # Step 1: Enhanced intent detection using classification service
                if request.has_files():
                    # Images/documents → Use vision model for analysis
                    intent = "chat"  # Vision analysis goes through chat path
                    primary_intent = "CHAT"
                    self.logger.info(f"{LogEmoji.AI} [{request_id}] Intent: {intent} (multimodal analysis)")
                else:
                    # Use classification service for intelligent intent detection with conversation context
                    classification_result = await self._classify_query(request.query, history=history)
                    primary_intent = classification_result.get("primary_intent", "SEARCH_BUY")
                    all_intents = classification_result.get("intents", [primary_intent])

                    self.logger.info(f"{LogEmoji.AI} [{request_id}] Primary Intent: {primary_intent}, All: {all_intents}")

                    # Map primary intent to routing decision
                    if primary_intent in ["POST_SALE", "POST_RENT"]:
                        intent = "post_property"
                    elif primary_intent in ["SEARCH_BUY", "SEARCH_RENT"]:
                        intent = "search"
                    elif primary_intent == "PRICE_CONSULTATION":
                        intent = "price_consultation"
                    elif primary_intent == "PROPERTY_DETAIL":
                        intent = "property_detail"
                    else:
                        intent = "chat"

                # Step 2: Route based on intent (with history context + files)
                if intent == "post_property":
                    # Case 1: Handle property posting workflow with reasoning loop
                    response_text = await self._handle_property_posting(
                        request.query,
                        primary_intent=primary_intent,
                        history=history,
                        user_id=request.user_id,
                        language=request.language,
                        files=request.files  # NEW: Pass images to POST flow
                    )
                elif intent == "search":
                    # Case 2: Handle search with ReAct agent
                    response_text = await self._handle_search(request.query, history=history, files=request.files, language=request.language)
                elif intent == "price_consultation":
                    # Case 3: Handle price consultation with reasoning loop
                    response_text = await self._handle_price_consultation(
                        request.query,
                        history=history,
                        language=request.language
                    )
                elif intent == "property_detail":
                    # NEW Case 4: Handle property detail view by ID or keyword
                    response_text = await self._handle_property_detail(
                        request.query,
                        history=history,
                        language=request.language
                    )
                else:
                    # Case 5: General chat (multimodal or text)
                    response_text = await self._handle_chat(request.query, history=history, files=request.files, language=request.language)

                # Step 3: Save conversation to memory
                await self._save_message(request.user_id, conversation_id, "user", request.query)
                await self._save_message(request.user_id, conversation_id, "assistant", response_text, metadata={"intent": intent, "has_files": request.has_files()})

                execution_time = (time.time() - start_time) * 1000

                # Map intent to IntentType enum
                if intent == "search":
                    intent_type = IntentType.SEARCH
                elif intent == "post_property":
                    intent_type = IntentType.POST
                elif intent == "price_consultation":
                    intent_type = IntentType.PRICE_CONSULTATION
                elif intent == "property_detail":
                    intent_type = IntentType.PROPERTY_DETAIL
                else:
                    intent_type = IntentType.CHAT

                return OrchestrationResponse(
                    intent=intent_type,
                    confidence=0.9,
                    response=response_text,
                    service_used="classification_routing_with_memory_multimodal",
                    execution_time_ms=execution_time,
                    metadata={
                        "flow": "cto_architecture",
                        "history_messages": len(history),
                        "multimodal": request.has_files(),
                        "files_count": len(request.files) if request.files else 0,
                        "request_id": request_id,  # MEDIUM FIX Bug#1: Include request ID for tracing
                        "reasoning_loops": 1  # All cases use reasoning loops now
                    }
                )

            except (httpx.HTTPError, httpx.TimeoutException) as e:
                # CRITICAL FIX: Handle expected network errors
                self.logger.error(f"{LogEmoji.ERROR} Network error during orchestration: {e}", exc_info=True)
                # Detect language from request history
                lang = self._detect_language(history) if history else 'vi'
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response=t('errors.connection_error', language=lang),
                    service_used="none",
                    execution_time_ms=0.0
                )
            except (ValueError, KeyError, json.JSONDecodeError) as e:
                # CRITICAL FIX: Handle data validation errors
                self.logger.error(f"{LogEmoji.ERROR} Data validation error: {e}", exc_info=True)
                lang = self._detect_language(history) if history else 'vi'
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response=t('errors.data_error', language=lang),
                    service_used="none",
                    execution_time_ms=0.0
                )
            except Exception as e:
                # CRITICAL FIX: Log unexpected errors but don't expose details to users
                self.logger.critical(f"{LogEmoji.ERROR} Unexpected orchestration error: {e}", exc_info=True)
                lang = self._detect_language(history) if history else 'vi'
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response=t('errors.unknown_error', language=lang),
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

                # Step 2: Knowledge Expansion (Phase 2) - REMOVED
                # REMOVED: Switched to master data approach in multilingual_keywords.json
                # knowledge_expansion = await self.knowledge_base.expand_query(request.query)
                # if knowledge_expansion.expanded_terms:
                #     self.logger.info(
                #         f"{LogEmoji.INFO} [ReAct-v2] Expanded with domain knowledge: "
                #         f"{len(knowledge_expansion.expanded_terms)} terms, "
                #         f"{len(knowledge_expansion.filters)} filters"
                #     )
                knowledge_expansion = None  # Placeholder for compatibility

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
                lang = self._detect_language(history) if history else 'vi'
                return OrchestrationResponse(
                    intent=IntentType.UNKNOWN,
                    confidence=0.0,
                    response=t('errors.retry_error', language=lang),
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

                    # Knowledge expansion - REMOVED
                    # REMOVED: Switched to master data approach
                    # yield f"data: {json.dumps({'type': 'thinking', 'stage': 'knowledge_expansion', 'message': 'Expanding query with domain knowledge...'})}\n\n"
                    # knowledge_expansion = await self.knowledge_base.expand_query(request.query)
                    # if knowledge_expansion.expanded_terms:
                    #     yield f"data: {json.dumps({'type': 'knowledge', 'expanded_terms': knowledge_expansion.expanded_terms, 'filters': knowledge_expansion.filters})}\n\n"
                    knowledge_expansion = None  # Placeholder for compatibility

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

        @self.app.post("/chat/completions")
        @self.app.post("/v1/chat/completions")  # OpenAI-compatible alias for Open WebUI
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
                # Detect language from messages
                history = [{"role": msg.get("role"), "content": str(msg.get("content", ""))} for msg in messages]
                lang = self._detect_language(history) if history else 'vi'
                return {
                    "id": f"chatcmpl-{int(time.time())}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "ree-ai-orchestrator-v3-multimodal",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": t('errors.system_error', language=lang)
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

    async def _handle_search(self, query: str, history: List[Dict] = None, files: Optional[List[FileAttachment]] = None, language: str = "vi") -> str:
        """
        ReAct Agent Pattern for Search:
        1. REASONING: Analyze query requirements
        2. ACT: Execute search (classify + route)
        3. EVALUATE: Check result quality
        4. ITERATE: Refine query or ask clarification if quality is poor

        Max 2 iterations to balance quality vs response time

        Args:
            query: User search query
            history: Conversation history
            files: Attached files
            language: User's preferred language (vi, en, th, ja)
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
                            return await self._generate_suggestions_response(query, relaxed_results, requirements, language)

                        # Strategy 2: Semantic search fallback
                        self.logger.info(f"{LogEmoji.INFO} [ReAct Strategy 2] Trying semantic search...")
                        semantic_results = await self._execute_semantic_search(query)

                        if semantic_results:
                            self.logger.info(f"{LogEmoji.SUCCESS} [ReAct Strategy 2] Semantic search found {len(semantic_results)} results")
                            return await self._generate_suggestions_response(query, semantic_results, requirements, language)

                        # Strategy 3: Give up gracefully
                        self.logger.warning(f"{LogEmoji.WARNING} [ReAct Agent] All strategies failed")
                        return t('search.no_results', language=language)
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
                    return await self._generate_quality_response(query, results, requirements, evaluation, language)

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
                        return await self._ask_clarification(requirements, best_evaluation or evaluation, best_results, language)

            # Fallback (should not reach here)
            return t('search.no_results_expand', language=language)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [ReAct Agent] Search failed: {e}")
            return t('errors.retry_error', language=language)

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
            # CTO Priority 3+4: Use hybrid search + reranking for all modes
            if mode == "filter":
                # Use hybrid search with more BM25 weight for filter-heavy queries
                results = await self._execute_hybrid_search_with_reranking(query, alpha=0.5)
            elif mode == "semantic":
                # Use hybrid search with more vector weight for semantic queries
                results = await self._execute_hybrid_search_with_reranking(query, alpha=0.2)
            else:  # both
                # Balanced hybrid search
                results = await self._execute_hybrid_search_with_reranking(query, alpha=0.3)

            self.logger.info(f"{LogEmoji.SUCCESS} [ReAct-Act] Found {len(results)} results")
            return results

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [ReAct-Act] Search execution failed: {e}")
            return []

    async def _execute_filter_search(self, query: str) -> List[Dict]:
        """Execute filter-based search (Extraction → Document search)"""
        try:
            # ITERATION 1 IMPROVEMENT: Normalize query before extraction
            # Expands abbreviations (Q1 → Quận 1, 2BR → 2 phòng ngủ)
            # Handles mixed languages, multiple values
            normalized_query = self.query_normalizer.normalize(query)
            self.logger.info(f"{LogEmoji.INFO} [Query Normalization] '{query}' → '{normalized_query}'")

            # Step 1: Attribute Extraction (with normalized query)
            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query",
                json={"query": normalized_query, "intent": "SEARCH"},
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
        """Execute semantic search (Vector search)

        NOW WITH ATTRIBUTE EXTRACTION: Extract property_type, listing_type, etc. to improve results
        """
        try:
            # ITERATION 1 IMPROVEMENT: Normalize query before extraction
            normalized_query = self.query_normalizer.normalize(query)

            # FIX: Extract attributes to pass as filters for better semantic search
            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query",
                json={"query": normalized_query, "intent": "SEARCH"},
                timeout=settings.EXTRACTION_TIMEOUT
            )

            filters = {}
            if extraction_response.status_code == 200:
                extraction = extraction_response.json()
                entities = extraction.get("entities", {})

                # Pass extracted attributes as filters
                if "property_type" in entities and entities["property_type"]:
                    filters["property_type"] = entities["property_type"]
                if "listing_type" in entities and entities["listing_type"]:
                    filters["listing_type"] = entities["listing_type"]
                if "district" in entities and entities["district"]:
                    filters["district"] = entities["district"]
                if "city" in entities and entities["city"]:
                    filters["city"] = entities["city"]
                if "bedrooms" in entities and entities["bedrooms"]:
                    filters["bedrooms"] = entities["bedrooms"]
                if "min_price" in entities:
                    filters["min_price"] = entities["min_price"]
                if "max_price" in entities:
                    filters["max_price"] = entities["max_price"]

                self.logger.info(f"{LogEmoji.INFO} [Semantic Search] Extracted filters: {filters}")

            search_response = await self.http_client.post(
                f"{self.db_gateway_url}/vector-search",
                json={
                    "query": query,
                    "filters": filters if filters else {},
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

    async def _execute_hybrid_search_with_reranking(
        self,
        query: str,
        user_id: Optional[str] = None,
        alpha: float = 0.3
    ) -> List[Dict]:
        """
        Execute hybrid search (BM25 + Vector) with ML-based re-ranking

        CTO Priority 3 + 4 Integration:
        1. Hybrid Search: Combines BM25 (keyword) + Vector (semantic) search
        2. Re-ranking: Applies 5-feature scoring (quality, seller, freshness, engagement, personalization)

        Args:
            query: Search query text
            user_id: User ID for personalization (optional)
            alpha: BM25 weight (default: 0.3 = 30% BM25, 70% Vector)

        Returns:
            List of re-ranked property results with final scores
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [Hybrid+Rerank] Starting integrated search pipeline")

            # ITERATION 1 IMPROVEMENT: Normalize query before extraction
            normalized_query = self.query_normalizer.normalize(query)
            if normalized_query != query:
                self.logger.info(f"{LogEmoji.INFO} [Hybrid+Rerank] Normalized: '{query}' → '{normalized_query}'")

            # Step 1: Extract attributes for filters
            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query",
                json={"query": normalized_query, "intent": "SEARCH"},
                timeout=settings.EXTRACTION_TIMEOUT
            )

            filters = {}
            if extraction_response.status_code == 200:
                extraction = extraction_response.json()
                entities = extraction.get("entities", {})

                # Build filters for hybrid search
                if "district" in entities and entities["district"]:
                    filters["district"] = entities["district"]
                if "city" in entities and entities["city"]:
                    filters["city"] = entities["city"]
                if "property_type" in entities and entities["property_type"]:
                    # Remove vague terms
                    vague_terms = ["nhà", "bds", "bất động sản", "property", "real estate", ""]
                    prop_type = entities["property_type"].lower().strip()
                    if prop_type not in vague_terms and prop_type:
                        filters["property_type"] = entities["property_type"]
                if "listing_type" in entities and entities["listing_type"]:
                    filters["listing_type"] = entities["listing_type"]
                if "min_price" in entities:
                    filters["min_price"] = entities["min_price"]
                if "max_price" in entities:
                    filters["max_price"] = entities["max_price"]
                if "min_area" in entities:
                    filters["min_area"] = entities["min_area"]
                if "max_area" in entities:
                    filters["max_area"] = entities["max_area"]

                self.logger.info(f"{LogEmoji.INFO} [Hybrid Search] Extracted filters: {filters}")

            # Step 2: Execute hybrid search (BM25 + Vector)
            hybrid_response = await self.http_client.post(
                f"{self.db_gateway_url}/hybrid-search",
                json={
                    "query": query,
                    "filters": filters,
                    "limit": 10  # Get more candidates for reranking
                },
                params={"alpha": alpha},
                timeout=30.0
            )

            if hybrid_response.status_code != 200:
                self.logger.warning(f"{LogEmoji.WARNING} Hybrid search failed: {hybrid_response.status_code}")
                return []

            hybrid_results = hybrid_response.json()
            results = hybrid_results.get("results", [])
            metadata = hybrid_results.get("metadata", {})

            if not results:
                self.logger.info(f"{LogEmoji.INFO} [Hybrid Search] No results found")
                return []

            self.logger.info(
                f"{LogEmoji.SUCCESS} [Hybrid Search] Found {len(results)} results "
                f"(BM25: {metadata.get('bm25_count', 0)}, Vector: {metadata.get('vector_count', 0)}) "
                f"in {metadata.get('execution_time_ms', 0):.2f}ms"
            )

            # Step 3: Re-rank with ML-based scoring
            rerank_response = await self.http_client.post(
                f"{self.reranking_url}/rerank",
                json={
                    "query": query,
                    "results": results,
                    "user_id": user_id or "anonymous"
                },
                timeout=30.0
            )

            if rerank_response.status_code != 200:
                self.logger.warning(f"{LogEmoji.WARNING} Re-ranking failed, using hybrid results")
                return results[:5]  # Return top 5 from hybrid search

            reranked_data = rerank_response.json()
            reranked_results = reranked_data.get("results", [])
            rerank_metadata = reranked_data.get("rerank_metadata", {})

            self.logger.info(
                f"{LogEmoji.SUCCESS} [Re-ranking] Completed in {rerank_metadata.get('processing_time_ms', 0):.2f}ms, "
                f"model={rerank_metadata.get('model_version', 'unknown')}"
            )

            # Log top 3 for debugging
            for i, result in enumerate(reranked_results[:3], 1):
                features = result.get("rerank_features", {})
                self.logger.info(
                    f"{LogEmoji.INFO} [Top {i}] {result.get('title', 'N/A')[:40]}... | "
                    f"Final={result.get('final_score', 0):.3f} | "
                    f"Quality={features.get('completeness', 0):.2f} | "
                    f"Seller={features.get('seller_reputation', 0):.2f} | "
                    f"Fresh={features.get('freshness', 0):.2f} | "
                    f"Engage={features.get('engagement', 0):.2f} | "
                    f"Personal={features.get('personalization', 0):.2f}"
                )

            # Return top 5 results
            return reranked_results[:5]

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Hybrid+Rerank pipeline failed: {e}", exc_info=True)
            # Fallback to filter search
            return await self._execute_filter_search(query)

    async def _track_property_views(self, property_ids: List[str]) -> None:
        """
        Track property views for analytics

        CTO Priority 4: Analytics tracking for engagement metrics
        Sends view events to reranking service for property_stats updates

        Args:
            property_ids: List of property IDs that were shown to user
        """
        try:
            if not property_ids:
                return

            self.logger.info(f"{LogEmoji.INFO} [Analytics] Tracking {len(property_ids)} property views")

            # Track each property view asynchronously (fire and forget)
            for prop_id in property_ids:
                try:
                    # Fire and forget - don't await to avoid blocking response
                    await self.http_client.post(
                        f"{self.reranking_url}/analytics/view/{prop_id}",
                        timeout=5.0
                    )
                except Exception as e:
                    # Log error but don't fail the request
                    self.logger.warning(f"{LogEmoji.WARNING} Failed to track view for {prop_id}: {e}")

            self.logger.info(f"{LogEmoji.SUCCESS} [Analytics] View tracking completed")

        except Exception as e:
            # Analytics should never break the main flow
            self.logger.warning(f"{LogEmoji.WARNING} Analytics tracking failed: {e}")

    async def _track_property_click(
        self,
        user_id: str,
        property_id: str,
        property_price: Optional[float] = None,
        property_district: Optional[str] = None,
        property_type: Optional[str] = None
    ) -> None:
        """
        Track property click and update user preferences

        CTO Priority 4: Analytics tracking for user personalization
        Updates user_preferences table based on clicked properties

        Args:
            user_id: User ID
            property_id: Property ID that was clicked
            property_price: Property price (for preference learning)
            property_district: Property district (for preference learning)
            property_type: Property type (for preference learning)
        """
        try:
            self.logger.info(f"{LogEmoji.INFO} [Analytics] Tracking click: user={user_id}, property={property_id}")

            # Build click tracking request
            params = {
                "user_id": user_id,
                "property_id": property_id
            }

            if property_price:
                params["property_price"] = property_price
            if property_district:
                params["property_district"] = property_district
            if property_type:
                params["property_type"] = property_type

            # Fire and forget
            await self.http_client.post(
                f"{self.reranking_url}/analytics/click",
                params=params,
                timeout=5.0
            )

            self.logger.info(f"{LogEmoji.SUCCESS} [Analytics] Click tracking completed")

        except Exception as e:
            # Analytics should never break the main flow
            self.logger.warning(f"{LogEmoji.WARNING} Click tracking failed: {e}")

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

    async def _generate_suggestions_response(self, query: str, results: List[Dict], requirements: Dict, language: str = "vi") -> str:
        """
        Generate response with suggestions and disclaimer
        Used when relaxed search found results but query was incomplete

        Args:
            query: User query
            results: Search results
            requirements: Extracted requirements
            language: User's preferred language
        """
        try:
            # CTO Priority 4: Track property views for analytics
            if results:
                property_ids = [p.get("property_id") for p in results if p.get("property_id")]
                await self._track_property_views(property_ids)

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
            return t('search.found_some_provide_more_info', language=language)

    async def _handle_filter_search(self, query: str) -> str:
        """Filter mode: Extraction → Document search"""
        try:
            # ITERATION 1 IMPROVEMENT: Normalize query
            normalized_query = self.query_normalizer.normalize(query)

            # Step 2a: Attribute Extraction
            self.logger.info(f"{LogEmoji.AI} Step 2a: Attribute Extraction")

            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-query",
                json={"query": normalized_query, "intent": "SEARCH"},
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
            return t('errors.retry_error', language='vi')

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
            return t('errors.retry_error', language='vi')

    async def _handle_hybrid_search(self, query: str) -> str:
        """Both mode: Hybrid search (simplified - use filter for now)"""
        self.logger.info(f"{LogEmoji.AI} Hybrid search → using filter path")
        return await self._handle_filter_search(query)

    async def _generate_search_response(self, query: str, results: List[Dict], mode: str, language: str = 'vi') -> str:
        """Generate natural language response from search results"""
        if not results or len(results) == 0:
            return t('search.no_results_expand', language=language)

        # Build response with property details
        response_parts = [t('search.found_properties', language=language, count=len(results)) + ":\n"]

        for i, prop in enumerate(results[:3], 1):  # Top 3
            title = prop.get("title", "Không có tiêu đề")
            price = prop.get("price_display", prop.get("price", "Liên hệ"))
            area = prop.get("area", "N/A")
            location = prop.get("district", prop.get("region", "N/A"))

            # NEW: Add listing_type badge
            listing_type = prop.get("listing_type", "")
            if listing_type == "sale":
                listing_badge = "🏷️ Bán"
            elif listing_type == "rent":
                listing_badge = "🏷️ Cho thuê"
            else:
                listing_badge = ""

            # NEW: Add property_id
            property_id = prop.get("property_id", "N/A")

            # NEW: Add first image
            images = prop.get("images", [])
            first_image = images[0] if images else None

            response_parts.append(
                f"\n{i}. **{title}** {listing_badge}\n"
                f"   - ID: `{property_id}`\n"
                f"   - Giá: {price}\n"
                f"   - Diện tích: {self._format_area(area)}\n"
                f"   - Khu vực: {location}"
            )

            # Add image if available
            if first_image:
                response_parts.append(f"\n   - Hình ảnh: {first_image}")

        if len(results) > 3:
            response_parts.append(f"\n\n...và {len(results) - 3} bất động sản khác. Gõ 'xem thêm' để hiển thị.")

        return "".join(response_parts)

    async def _handle_chat(self, query: str, history: List[Dict] = None, files: Optional[List[FileAttachment]] = None, language: str = "vi") -> str:
        """
        Handle general chat (non-search) with conversation context and multimodal support

        Args:
            query: User chat message
            history: Conversation history
            files: Attached files
            language: User's preferred language (vi, en, th, ja)
        """
        try:
            # Build messages with history context
            if files and len(files) > 0:
                # Load vision analysis prompt
                system_prompt = load_prompt('vision_analysis_en.txt')
                if not system_prompt:
                    # Fallback to inline English prompt
                    system_prompt = """You are a professional real estate assistant with image analysis capabilities.

**CRITICAL - LANGUAGE:**
Respond in the SAME language the user uses (Vietnamese→Vietnamese, English→English)

Analyze real estate images and provide detailed descriptions of property type, design style, amenities, and value estimates."""
            else:
                # Load language-agnostic English prompt
                system_prompt = load_prompt('chat_handler_prompt_en.txt')
                if not system_prompt:
                    # Fallback to inline English prompt
                    system_prompt = """You are a friendly, enthusiastic AI assistant with expertise in real estate.

IMPORTANT - RESPOND NATURALLY AND FLEXIBLY:

**CRITICAL - LANGUAGE:**
Respond in the SAME language the user uses:
- If user writes in Vietnamese → Respond in Vietnamese
- If user writes in English → Respond in English
Auto-detect the user's language and match it

1. **For greetings/emotions:**
   - Show empathy, comfort naturally like a friend
   - Greet warmly, ask how they're doing
   - Respond politely, ask if you can help with anything else

2. **For general questions:**
   - Be honest about limitations (e.g., real-time info)
   - Introduce yourself naturally and friendly
   - Give helpful advice about real estate processes

3. **For real estate questions:**
   - Answer specifically, in detail, helpfully
   - Encourage them to provide criteria for property search
   - Give professional recommendations

GUIDING PRINCIPLES:
- EMPATHETIC and care about user emotions
- NATURAL like chatting with friends
- HELPFUL and professional when discussing real estate
- FLEXIBLE, not rigid templates

Respond like a real person, not a mechanical chatbot!"""

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
                        return data.get("content", t('errors.no_request', language=language))
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
                        return t('errors.retry_error', language=language)

                except httpx.TimeoutException:
                    self.logger.error(f"{LogEmoji.ERROR} Core Gateway timeout (attempt {attempt+1}/{max_retries})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    return t('errors.retry_error', language=language)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Chat failed: {e}")
            import traceback
            traceback.print_exc()
            return t('errors.retry_error', language=language)

    # ========================================
    # Classification & Property Posting Methods
    # ========================================

    async def _classify_query(self, query: str, history: Optional[List[Dict]] = None) -> Dict:
        """
        Call classification service for intelligent intent detection

        Args:
            query: Current user query
            history: Conversation history for context-aware classification

        Returns dict with:
        - mode: "filter" | "semantic" | "both"
        - primary_intent: "POST_SALE" | "POST_RENT" | "SEARCH_BUY" | "SEARCH_RENT" | etc.
        - intents: List of all detected intents
        - confidence: float
        - reasoning: str
        """
        try:
            self.logger.info(f"{LogEmoji.AI} Calling classification service...")

            # Format conversation history as context for classification
            # This allows the classifier to maintain state across turns
            context = None
            if history:
                # Pass last 5 messages as list (classification service expects List[Dict])
                context = history[-5:]
                self.logger.info(f"{LogEmoji.INFO} Classification context: {len(context)} messages")

            response = await self.http_client.post(
                f"{self.classification_url}/classify",
                json={"query": query, "context": context},
                timeout=10.0
            )

            if response.status_code != 200:
                self.logger.warning(f"{LogEmoji.WARNING} Classification service error: {response.text}")
                # Fallback to simple detection
                return {
                    "mode": "semantic",
                    "primary_intent": "SEARCH_BUY",
                    "intents": ["SEARCH_BUY"],
                    "confidence": 0.5,
                    "reasoning": "Fallback (classification service unavailable)"
                }

            result = response.json()
            self.logger.info(
                f"{LogEmoji.SUCCESS} Classification: {result.get('primary_intent')} "
                f"(mode: {result.get('mode')}, confidence: {result.get('confidence', 0):.2f})"
            )
            return result

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Classification failed: {e}")
            # Fallback
            return {
                "mode": "semantic",
                "primary_intent": "SEARCH_BUY",
                "intents": ["SEARCH_BUY"],
                "confidence": 0.5,
                "reasoning": f"Fallback (error: {str(e)})"
            }

    async def _handle_property_posting(
        self,
        query: str,
        primary_intent: str,
        history: List[Dict] = None,
        user_id: str = None,
        language: str = "vi",
        files: Optional[List[FileAttachment]] = None  # NEW: Support image uploads
    ) -> str:
        """
        Handle property posting workflow with INTERNAL REASONING LOOP:
        Loop 1-5 times within single request:
        1. Extract property attributes from query (with context)
        2. Assess completeness
        3. Decision: Score >= 80? Exit : Continue
        4. Re-extract with improved context

        Exit conditions:
        - Score >= 80 (satisfied)
        - Max 5 iterations
        - No improvement between iterations

        Args:
            query: User query (e.g., "Tôi có nhà cần bán ở Q7, 2PN, 5 tỷ")
            primary_intent: "POST_SALE" or "POST_RENT"
            history: Conversation history
            user_id: User ID
            language: User's preferred language (vi, en, th, ja)

        Returns:
            Response text with completeness feedback
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [Property Posting] Intent: {primary_intent}")

            # Determine transaction type from intent
            transaction_type = "bán" if primary_intent == "POST_SALE" else "cho thuê"

            # INTERNAL REASONING LOOP CONFIGURATION
            MAX_ITERATIONS = 5
            COMPLETENESS_THRESHOLD = 80

            # Initialize loop variables
            entities = {}
            completeness_data = {}
            overall_score = 0
            previous_score = 0
            image_urls = []  # NEW: Store uploaded image URLs

            # NEW: Extract attributes from images FIRST (if provided)
            if files and len(files) > 0:
                self.logger.info(f"{LogEmoji.AI} [Property Posting] Extracting from {len(files)} image(s)...")

                image_entities = await self._extract_from_images(files, query)

                if image_entities:
                    entities.update(image_entities)
                    self.logger.info(f"{LogEmoji.SUCCESS} [Property Posting] Extracted {len(image_entities)} attributes from images: {list(image_entities.keys())}")

                # Upload images to GCS (will be added to property later)
                self.logger.info(f"{LogEmoji.AI} [Property Posting] Preparing {len(files)} image(s) for upload...")
                # Note: Images will be uploaded when property is saved (in _save_property_to_db)

            # Build conversation context from history once
            conversation_context = await self._build_conversation_context(history or [])

            self.logger.info(f"{LogEmoji.INFO} [Property Posting Loop] Starting reasoning loop (max {MAX_ITERATIONS} iterations)")

            # REASONING LOOP: Extract → Assess → Decide → Re-extract
            for iteration in range(1, MAX_ITERATIONS + 1):
                self.logger.info(f"{LogEmoji.AI} [Loop {iteration}/{MAX_ITERATIONS}] ========== ITERATION {iteration} ==========")

                # STEP 1: Extract attributes (with enriched context in later iterations)
                self.logger.info(f"{LogEmoji.AI} [Loop {iteration}] Step 1: Extracting attributes...")

                # Build extraction prompt with context
                if iteration == 1:
                    # First iteration: use original query + conversation context
                    extraction_prompt = query
                    if conversation_context:
                        extraction_prompt = f"{conversation_context}\n\nCurrent query: {query}"
                else:
                    # Later iterations: enrich with previous extraction results
                    extraction_prompt = f"""Conversation context: {conversation_context}

Original query: {query}

Previous extraction (iteration {iteration-1}):
{json.dumps(entities, ensure_ascii=False, indent=2)}

Previous completeness score: {previous_score}/100

Re-extract property attributes with improved understanding. Focus on filling missing fields and improving accuracy."""

                extraction_response = await self.http_client.post(
                    f"{self.extraction_url}/extract-query",
                    json={
                        "query": extraction_prompt,
                        "intent": "POST",
                        "iteration": iteration
                    },
                    timeout=30.0
                )

                if extraction_response.status_code != 200:
                    self.logger.warning(f"{LogEmoji.WARNING} [Loop {iteration}] Extraction failed")
                    if iteration == 1:
                        return self._generate_simple_fallback_feedback({}, 0, ["extraction_error"], language)
                    else:
                        # Use previous iteration's data
                        break

                extraction_data = extraction_response.json()
                entities = extraction_data.get("entities", {})
                confidence = extraction_data.get("confidence", 0.0)

                self.logger.info(f"{LogEmoji.SUCCESS} [Loop {iteration}] Step 1: Extracted {len(entities)} attributes (confidence: {confidence:.1%})")

                # STEP 2: Assess completeness
                self.logger.info(f"{LogEmoji.AI} [Loop {iteration}] Step 2: Assessing completeness...")

                property_data = {
                    "transaction_type": transaction_type,
                    **entities
                }

                completeness_response = await self.http_client.post(
                    f"{self.completeness_url}/assess",
                    json={"property_data": property_data, "language": language, "include_examples": False},
                    timeout=30.0
                )

                if completeness_response.status_code != 200:
                    self.logger.warning(f"{LogEmoji.WARNING} [Loop {iteration}] Completeness assessment failed")
                    if iteration == 1:
                        return self._generate_simple_fallback_feedback({}, 0, ["completeness_error"], language)
                    else:
                        break

                completeness_data = completeness_response.json()
                overall_score = completeness_data.get("overall_score", 0)
                interpretation = completeness_data.get("interpretation", "")

                self.logger.info(f"{LogEmoji.SUCCESS} [Loop {iteration}] Step 2: Score: {overall_score}/100 ({interpretation})")

                # STEP 3: DECISION - Exit loop?
                # Exit condition 1: Score >= threshold (SATISFIED)
                if overall_score >= COMPLETENESS_THRESHOLD:
                    self.logger.info(f"{LogEmoji.SUCCESS} [Loop {iteration}] ✅ SATISFIED (score {overall_score} >= {COMPLETENESS_THRESHOLD})")
                    self.logger.info(f"{LogEmoji.SUCCESS} [Property Posting Loop] Exiting loop after {iteration} iteration(s)")
                    break

                # Exit condition 2: Max iterations reached
                if iteration == MAX_ITERATIONS:
                    self.logger.info(f"{LogEmoji.WARNING} [Loop {iteration}] ⚠️ MAX ITERATIONS reached")
                    self.logger.info(f"{LogEmoji.INFO} [Property Posting Loop] Final score: {overall_score}/100")
                    break

                # Exit condition 3: No improvement
                if iteration > 1:
                    improvement = overall_score - previous_score
                    self.logger.info(f"{LogEmoji.INFO} [Loop {iteration}] Improvement: +{improvement:.1f} points")

                    if improvement <= 0:
                        self.logger.info(f"{LogEmoji.WARNING} [Loop {iteration}] ⚠️ NO IMPROVEMENT, stopping early")
                        self.logger.info(f"{LogEmoji.INFO} [Property Posting Loop] Exiting loop after {iteration} iteration(s)")
                        break

                # Continue loop: Save score for next iteration comparison
                previous_score = overall_score
                self.logger.info(f"{LogEmoji.INFO} [Loop {iteration}] → Continuing to iteration {iteration + 1}")

            # STEP 4: Generate response based on final results
            self.logger.info(f"{LogEmoji.AI} [Property Posting] Step 3: Generating response...")

            # Check if user confirms completion (conversation ending logic)
            is_user_confirming = self._detect_completion_confirmation(query, history)

            # Ending Condition: High completeness + User confirmation
            if overall_score >= 75 and is_user_confirming:
                self.logger.info(f"{LogEmoji.SUCCESS} [Property Posting] ✅ Conversation ending: Score {overall_score}/100 + User confirmed")

                # VALIDATE PROPERTY ATTRIBUTES (CTO Priority 2)
                self.logger.info(f"{LogEmoji.AI} [Property Posting] Running validation checks...")

                validation_request = {
                    "intent": primary_intent,
                    "entities": entities,
                    "user_id": user_id or "anonymous",
                    "confidence_threshold": 0.8
                }

                try:
                    validation_response = await self.http_client.post(
                        f"{self.validation_url}/validate",
                        json=validation_request,
                        timeout=10.0
                    )

                    if validation_response.status_code == 200:
                        validation_data = validation_response.json()
                        can_save = validation_data.get("can_save", False)
                        total_errors = validation_data.get("total_errors", 0)
                        total_warnings = validation_data.get("total_warnings", 0)

                        self.logger.info(f"{LogEmoji.INFO} [Validation] Can save: {can_save}, Errors: {total_errors}, Warnings: {total_warnings}")

                        # If validation fails, return error message
                        if not can_save:
                            summary = validation_data.get("summary", "Validation failed")
                            next_steps = validation_data.get("next_steps", [])

                            error_message = f"{summary}\n\n"
                            if next_steps:
                                error_message += "Vui lòng:\n" + "\n".join(f"• {step}" for step in next_steps)

                            self.logger.warning(f"{LogEmoji.WARNING} [Validation] Property validation failed: {summary}")
                            return error_message

                        # Log warnings but continue
                        if total_warnings > 0:
                            self.logger.info(f"{LogEmoji.INFO} [Validation] Property has {total_warnings} warnings but can proceed")
                    else:
                        # Validation service unavailable - log warning but continue
                        self.logger.warning(f"{LogEmoji.WARNING} [Validation] Service unavailable, skipping validation")

                except Exception as e:
                    # Validation error - log but don't block save
                    self.logger.error(f"{LogEmoji.ERROR} [Validation] Error: {e}")
                    self.logger.info(f"{LogEmoji.INFO} [Validation] Continuing without validation due to error")

                # SAVE PROPERTY TO DATABASE
                save_result = await self._save_property_to_db(
                    entities=entities,
                    user_id=user_id or "anonymous",
                    transaction_type=transaction_type,
                    files=files  # NEW: Pass images for upload
                )

                # Log save result for debugging
                property_id = None
                if save_result:
                    property_id = save_result.get('property_id')
                    self.logger.info(f"{LogEmoji.SUCCESS} [Property Posting] Property saved with ID: {property_id}")
                else:
                    self.logger.warning(f"{LogEmoji.WARNING} [Property Posting] Failed to save property, but continuing with response")

                return await self._generate_completion_message(
                    entities=entities,
                    overall_score=overall_score,
                    property_id=property_id,
                    history=history,
                    query=query,
                    language=language
                )

            # Otherwise: Generate regular feedback with improvement suggestions
            self.logger.info(f"{LogEmoji.AI} [Property Posting] Generating feedback (Score: {overall_score}/100, Confirmed: {is_user_confirming})")
            return await self._generate_posting_feedback(
                entities=entities,
                completeness_data=completeness_data,
                transaction_type=transaction_type,
                iterations=iteration,
                history=history,
                query=query,
                language=language
            )

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Property Posting] Failed: {e}")
            import traceback
            traceback.print_exc()
            # Use fallback with user's preferred language
            return self._generate_simple_fallback_feedback({}, 0, [], language)

    async def _handle_price_consultation(
        self,
        query: str,
        history: List[Dict] = None,
        language: str = "vi"
    ) -> str:
        """
        Handle price consultation workflow with REASONING LOOP:
        Loop 1-3 times within single request:
        1. Extract property info from query
        2. Market analysis: Query similar properties
        3. Compare & Validate confidence
        4. Refine if needed

        Exit conditions:
        - Confidence >= 0.8 (high confidence)
        - Max 3 iterations
        - Sufficient market data (>= 5 similar properties)

        Args:
            query: User query (e.g., "Căn hộ 2PN Quận 2 giá bao nhiêu?")
            history: Conversation history
            language: User's preferred language (vi, en, th, ja)

        Returns:
            Price consultation response with range and insights
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [Price Consultation] Starting price analysis...")

            # REASONING LOOP CONFIGURATION
            MAX_ITERATIONS = 3
            CONFIDENCE_THRESHOLD = 0.8
            MIN_MARKET_SAMPLES = 5

            # Initialize loop variables
            property_info = {}
            market_data = []
            confidence = 0.0
            previous_confidence = 0.0

            # Build conversation context from history once
            conversation_context = await self._build_conversation_context(history or [])

            self.logger.info(f"{LogEmoji.INFO} [Price Consultation Loop] Starting reasoning loop (max {MAX_ITERATIONS} iterations)")

            # REASONING LOOP: Extract → Analyze → Validate → Refine
            for iteration in range(1, MAX_ITERATIONS + 1):
                self.logger.info(f"{LogEmoji.AI} [Loop {iteration}/{MAX_ITERATIONS}] ========== ITERATION {iteration} ==========")

                # STEP 1: Extract property information
                self.logger.info(f"{LogEmoji.AI} [Loop {iteration}] Step 1: Extracting property info...")

                # Build extraction prompt with context
                if iteration == 1:
                    extraction_prompt = query
                    if conversation_context:
                        extraction_prompt = f"{conversation_context}\n\nCurrent query: {query}"
                else:
                    # Later iterations: enrich with previous results
                    extraction_prompt = f"""Conversation context: {conversation_context}

Original query: {query}

Previous extraction (iteration {iteration-1}):
{json.dumps(property_info, ensure_ascii=False, indent=2)}

Previous market data: {len(market_data)} similar properties found
Previous confidence: {previous_confidence:.1%}

Re-extract property info with improved understanding. Be more specific about location, property type, and features."""

                extraction_response = await self.http_client.post(
                    f"{self.extraction_url}/extract-query",
                    json={
                        "query": extraction_prompt,
                        "intent": "PRICE_CONSULTATION",
                        "iteration": iteration
                    },
                    timeout=30.0
                )

                if extraction_response.status_code != 200:
                    self.logger.warning(f"{LogEmoji.WARNING} [Loop {iteration}] Extraction failed")
                    if iteration == 1:
                        return t('property_posting.extraction_error_detail', language=language)
                    else:
                        break

                extraction_data = extraction_response.json()
                property_info = extraction_data.get("entities", {})

                self.logger.info(f"{LogEmoji.SUCCESS} [Loop {iteration}] Step 1: Extracted info: {list(property_info.keys())}")

                # STEP 2: Market Analysis - Query similar properties
                self.logger.info(f"{LogEmoji.AI} [Loop {iteration}] Step 2: Analyzing market data...")

                market_data = await self._query_similar_properties(property_info)

                self.logger.info(f"{LogEmoji.SUCCESS} [Loop {iteration}] Step 2: Found {len(market_data)} similar properties")

                # STEP 3: Compare & Validate - Calculate confidence
                self.logger.info(f"{LogEmoji.AI} [Loop {iteration}] Step 3: Validating data quality...")

                validation = self._validate_market_data(property_info, market_data)
                confidence = validation["confidence"]
                data_quality = validation["data_quality"]

                self.logger.info(f"{LogEmoji.SUCCESS} [Loop {iteration}] Step 3: Confidence: {confidence:.1%}, Quality: {data_quality}")

                # DECISION: Exit loop?
                # Exit condition 1: High confidence
                if confidence >= CONFIDENCE_THRESHOLD:
                    self.logger.info(f"{LogEmoji.SUCCESS} [Loop {iteration}] ✅ HIGH CONFIDENCE (>= {CONFIDENCE_THRESHOLD:.0%})")
                    self.logger.info(f"{LogEmoji.SUCCESS} [Price Consultation Loop] Exiting loop after {iteration} iteration(s)")
                    break

                # Exit condition 2: Sufficient market samples
                if len(market_data) >= MIN_MARKET_SAMPLES and confidence >= 0.6:
                    self.logger.info(f"{LogEmoji.SUCCESS} [Loop {iteration}] ✅ SUFFICIENT DATA ({len(market_data)} samples, confidence {confidence:.1%})")
                    self.logger.info(f"{LogEmoji.SUCCESS} [Price Consultation Loop] Exiting loop after {iteration} iteration(s)")
                    break

                # Exit condition 3: Max iterations
                if iteration == MAX_ITERATIONS:
                    self.logger.info(f"{LogEmoji.WARNING} [Loop {iteration}] ⚠️ MAX ITERATIONS reached")
                    self.logger.info(f"{LogEmoji.INFO} [Price Consultation Loop] Final confidence: {confidence:.1%}")
                    break

                # Exit condition 4: No improvement
                if iteration > 1:
                    improvement = confidence - previous_confidence
                    self.logger.info(f"{LogEmoji.INFO} [Loop {iteration}] Improvement: +{improvement:.1%}")

                    if improvement <= 0.05:  # Less than 5% improvement
                        self.logger.info(f"{LogEmoji.WARNING} [Loop {iteration}] ⚠️ MINIMAL IMPROVEMENT, stopping")
                        self.logger.info(f"{LogEmoji.INFO} [Price Consultation Loop] Exiting loop after {iteration} iteration(s)")
                        break

                # Continue loop
                previous_confidence = confidence
                self.logger.info(f"{LogEmoji.INFO} [Loop {iteration}] → Continuing to iteration {iteration + 1}")

            # STEP 4: Generate consultation response
            self.logger.info(f"{LogEmoji.AI} [Price Consultation] Step 4: Generating consultation...")

            return await self._generate_price_consultation_response(
                property_info=property_info,
                market_data=market_data,
                confidence=confidence,
                iterations=iteration,
                language=language
            )

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Price Consultation] Failed: {e}")
            import traceback
            traceback.print_exc()
            return t('errors.retry_error', language=language)

    async def _handle_property_detail(
        self,
        query: str,
        history: List[Dict] = None,
        language: str = "vi"
    ) -> str:
        """
        Handle property detail view request.

        Supports 3 methods:
        1. By ID: "Cho tôi xem chi tiết ID prop_abc123"
        2. By position: "Xem thông tin căn số 2"
        3. By keyword: "Thông tin về Vinhomes Central Park"

        Args:
            query: User query
            history: Conversation history
            language: User's preferred language

        Returns:
            Formatted property details or error message
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [Property Detail] Processing request...")

            # STEP 1: Extract property_id or position or keyword
            property_id, position, keyword = self._extract_property_reference(query)

            self.logger.info(
                f"{LogEmoji.INFO} [Property Detail] Extracted - "
                f"ID: {property_id}, Position: {position}, Keyword: {keyword}"
            )

            # STEP 2: If position (e.g., "căn số 2"), get property_id from recent search history
            if position and not property_id:
                property_id = await self._get_property_id_from_history(history, position)

                if not property_id:
                    return t('property_detail.position_not_found', language=language, position=position)

            # STEP 3: If keyword, search for matching property
            if keyword and not property_id:
                property_id = await self._search_property_by_keyword(keyword, history)

                if not property_id:
                    return t('property_detail.keyword_not_found', language=language, keyword=keyword)

            # STEP 4: If still no property_id, return error
            if not property_id:
                return t('property_detail.id_not_found', language=language)

            # STEP 5: Fetch property details from DB Gateway
            self.logger.info(f"{LogEmoji.AI} [Property Detail] Fetching details for {property_id}...")

            try:
                detail_response = await self.http_client.get(
                    f"{self.db_gateway_url}/properties/{property_id}",
                    timeout=10.0
                )

                if detail_response.status_code == 404:
                    return t('property_detail.not_found', language=language, property_id=property_id)

                if detail_response.status_code != 200:
                    self.logger.warning(
                        f"{LogEmoji.WARNING} [Property Detail] Failed: {detail_response.status_code}"
                    )
                    return t('property_detail.error', language=language)

                property_data = detail_response.json()

                self.logger.info(f"{LogEmoji.SUCCESS} [Property Detail] Fetched successfully")

                # STEP 6: Format detailed response
                return self._format_property_detail(property_data, language)

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} [Property Detail] Fetch failed: {e}")
                return t('property_detail.error', language=language)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Property Detail] Failed: {e}")
            import traceback
            traceback.print_exc()
            return t('property_detail.error', language=language)

    def _extract_property_reference(self, query: str) -> tuple:
        """
        Extract property ID, position, or keyword from query.

        Returns:
            (property_id, position, keyword)
        """
        query_lower = query.lower()

        # Pattern 1: Extract property_id (e.g., "ID prop_abc123", "property_id: prop_xyz")
        id_patterns = [
            r"(?:id|property[_\s]id)[:\s]+([a-z0-9_-]{8,})",  # "ID prop_abc123"
            r"(?:mã|ma)\s*(?:số|so)?[:\s]+([a-z0-9_-]{8,})",  # "mã số prop_abc123"
            r"([a-z]+_[a-z0-9_-]{7,})",  # Direct "prop_abc123"
        ]

        for pattern in id_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return (match.group(1), None, None)

        # Pattern 2: Extract position (e.g., "căn số 2", "số 3", "item 1")
        position_patterns = [
            r"(?:căn|can)\s+(?:số|so)\s+(\d+)",  # "căn số 2"
            r"(?:số|so)\s+(\d+)",  # "số 2"
            r"(?:item|property)\s+(?:#)?(\d+)",  # "item 2" or "property #2"
            r"(?:thứ|thu)\s+(\d+)",  # "thứ 2"
        ]

        for pattern in position_patterns:
            match = re.search(pattern, query_lower)
            if match:
                position = int(match.group(1))
                return (None, position, None)

        # Pattern 3: Extract keyword (anything after "xem", "thông tin", etc.)
        keyword_patterns = [
            r"(?:xem|thông tin|thong tin|chi tiết|chi tiet|info about|details about)[:\s]+(.+)",
            r"(?:cho tôi|cho toi|show me|tell me about)[:\s]+(.+)",
        ]

        for pattern in keyword_patterns:
            match = re.search(pattern, query_lower)
            if match:
                keyword = match.group(1).strip()
                # Remove common words
                keyword = re.sub(r"\b(về|ve|của|cua|the|of)\b", "", keyword).strip()
                if len(keyword) > 3:  # Minimum keyword length
                    return (None, None, keyword)

        # No match found
        return (None, None, None)

    async def _get_property_id_from_history(
        self,
        history: List[Dict],
        position: int
    ) -> Optional[str]:
        """
        Get property_id from recent search results in conversation history.

        Args:
            history: Conversation history
            position: Position in search results (1-indexed)

        Returns:
            property_id or None
        """
        try:
            # Look for recent assistant messages with search results
            for msg in reversed(history or []):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")

                    # Check if this message contains search results with IDs
                    # Pattern: "ID: `prop_abc123`"
                    id_matches = re.findall(r"ID:\s*`([a-z0-9_-]+)`", content)

                    if id_matches and len(id_matches) >= position:
                        property_id = id_matches[position - 1]  # Convert to 0-indexed
                        self.logger.info(
                            f"{LogEmoji.SUCCESS} [Property Detail] Found ID from history position {position}: {property_id}"
                        )
                        return property_id

            self.logger.warning(
                f"{LogEmoji.WARNING} [Property Detail] No property found at position {position} in history"
            )
            return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Property Detail] History lookup failed: {e}")
            return None

    async def _search_property_by_keyword(
        self,
        keyword: str,
        history: List[Dict]
    ) -> Optional[str]:
        """
        Search for property by keyword in recent search results or via new search.

        Strategy:
        1. Check recent search results in history for keyword match
        2. If not found, trigger new search with keyword

        Args:
            keyword: Search keyword
            history: Conversation history

        Returns:
            property_id or None
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [Property Detail] Searching by keyword: {keyword}")

            # Strategy 1: Check recent history for keyword match
            for msg in reversed(history or []):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")

                    # Find all properties in this message
                    # Pattern: "1. **Title** 🏷️ Badge\n   - ID: `prop_abc`"
                    property_blocks = re.findall(
                        r"\d+\.\s+\*\*(.+?)\*\*.*?ID:\s*`([a-z0-9_-]+)`",
                        content,
                        re.DOTALL
                    )

                    # Search for keyword match in titles
                    for title, prop_id in property_blocks:
                        if keyword.lower() in title.lower():
                            self.logger.info(
                                f"{LogEmoji.SUCCESS} [Property Detail] Found match in history: {title} → {prop_id}"
                            )
                            return prop_id

            # Strategy 2: Trigger new search (fallback)
            self.logger.info(f"{LogEmoji.AI} [Property Detail] No match in history, triggering search...")

            search_response = await self.http_client.post(
                f"{self.db_gateway_url}/hybrid-search",
                json={
                    "query": keyword,
                    "filters": {},
                    "limit": 1
                },
                params={"alpha": 0.3},
                timeout=10.0
            )

            if search_response.status_code == 200:
                data = search_response.json()
                results = data.get("results", [])

                if results:
                    property_id = results[0].get("property_id")
                    self.logger.info(
                        f"{LogEmoji.SUCCESS} [Property Detail] Found via search: {property_id}"
                    )
                    return property_id

            self.logger.warning(f"{LogEmoji.WARNING} [Property Detail] No property found for keyword: {keyword}")
            return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Property Detail] Keyword search failed: {e}")
            return None

    def _format_property_detail(
        self,
        property_data: Dict,
        language: str
    ) -> str:
        """
        Format property details in user's language.

        Args:
            property_data: Property document from DB
            language: User's preferred language

        Returns:
            Formatted detail message
        """
        # Listing type badge
        listing_type = property_data.get("listing_type", "")
        if listing_type == "sale":
            listing_badge = "🏷️ Bán" if language == "vi" else "🏷️ Sale"
        elif listing_type == "rent":
            listing_badge = "🏷️ Cho thuê" if language == "vi" else "🏷️ Rent"
        else:
            listing_badge = ""

        # Build detail text
        title = property_data.get("title", "N/A")

        if language == "vi":
            detail_text = f"""
🏠 **{title}** {listing_badge}

📍 **Địa chỉ:**
   - Quận/Huyện: {property_data.get('district', 'N/A')}
   - Phường/Xã: {property_data.get('ward', 'N/A')}
   - Đường: {property_data.get('street', 'N/A')}
   - Thành phố: {property_data.get('city', 'N/A')}

💰 **Giá:** {property_data.get('price_display', property_data.get('price', 'N/A'))}

📐 **Thông tin kỹ thuật:**
   - Diện tích: {property_data.get('area', 'N/A')} m²
   - Phòng ngủ: {property_data.get('bedrooms', 'N/A')}
   - Phòng tắm: {property_data.get('bathrooms', 'N/A')}
   - Số tầng: {property_data.get('floors', 'N/A')}
"""
        else:
            detail_text = f"""
🏠 **{title}** {listing_badge}

📍 **Location:**
   - District: {property_data.get('district', 'N/A')}
   - Ward: {property_data.get('ward', 'N/A')}
   - Street: {property_data.get('street', 'N/A')}
   - City: {property_data.get('city', 'N/A')}

💰 **Price:** {property_data.get('price_display', property_data.get('price', 'N/A'))}

📐 **Specifications:**
   - Area: {property_data.get('area', 'N/A')} m²
   - Bedrooms: {property_data.get('bedrooms', 'N/A')}
   - Bathrooms: {property_data.get('bathrooms', 'N/A')}
   - Floors: {property_data.get('floors', 'N/A')}
"""

        # Add dimensions if available (for townhouse/villa)
        if property_data.get('width') or property_data.get('depth'):
            width = property_data.get('width', '?')
            depth = property_data.get('depth', '?')
            if language == "vi":
                detail_text += f"   - Kích thước: {width}m x {depth}m (ngang x dài)\n"
            else:
                detail_text += f"   - Dimensions: {width}m x {depth}m (width x depth)\n"

        # Add description
        description = property_data.get('description', '')
        if description:
            desc_preview = description[:300] + "..." if len(description) > 300 else description
            if language == "vi":
                detail_text += f"\n📝 **Mô tả:**\n{desc_preview}\n"
            else:
                detail_text += f"\n📝 **Description:**\n{desc_preview}\n"

        # Add images
        images = property_data.get('images', [])
        if images:
            if language == "vi":
                detail_text += f"\n📷 **Hình ảnh:** {len(images)} ảnh\n"
            else:
                detail_text += f"\n📷 **Images:** {len(images)} photos\n"

            for i, img in enumerate(images[:3], 1):  # Show first 3 URLs
                detail_text += f"   {i}. {img}\n"

            if len(images) > 3:
                if language == "vi":
                    detail_text += f"   ... và {len(images) - 3} ảnh khác\n"
                else:
                    detail_text += f"   ... and {len(images) - 3} more\n"

        # Add features/amenities
        amenities = []
        if property_data.get('parking'):
            amenities.append("🅿️ Parking" if language == "en" else "🅿️ Chỗ đậu xe")
        if property_data.get('elevator'):
            amenities.append("🛗 Elevator" if language == "en" else "🛗 Thang máy")
        if property_data.get('swimming_pool'):
            amenities.append("🏊 Pool" if language == "en" else "🏊 Hồ bơi")
        if property_data.get('gym'):
            amenities.append("🏋️ Gym" if language == "en" else "🏋️ Phòng gym")
        if property_data.get('security'):
            amenities.append("🔒 Security" if language == "en" else "🔒 An ninh 24/7")

        if amenities:
            if language == "vi":
                detail_text += f"\n✨ **Tiện ích:** {', '.join(amenities)}\n"
            else:
                detail_text += f"\n✨ **Amenities:** {', '.join(amenities)}\n"

        # Add contact information
        if property_data.get('contact_phone'):
            if language == "vi":
                detail_text += f"\n📞 **Liên hệ:**\n"
            else:
                detail_text += f"\n📞 **Contact:**\n"

            detail_text += f"   - {property_data.get('contact_phone')}\n"

            if property_data.get('contact_name'):
                detail_text += f"   - {property_data.get('contact_name')}\n"

        # Add property ID at the end
        property_id = property_data.get('property_id', 'N/A')
        detail_text += f"\n---\n🆔 Property ID: `{property_id}`"

        return detail_text

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
            validation_prompt = f"""{t('chat.system_prompt_quality_evaluator', language='vi')}

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

    async def _ask_clarification(self, requirements: Dict, evaluation: Dict, results: List[Dict] = None, language: str = "vi") -> str:
        """
        ITERATE Alternative: Intelligent clarification with alternatives and statistics

        Returns clarification message with:
        - Data-driven insights (statistics)
        - Proactive suggestions
        - Top alternatives with scoring (using OpenSearch semantic scores)

        Args:
            requirements: Extracted requirements
            evaluation: Quality evaluation
            results: Search results
            language: User's preferred language
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
                        t('search.no_units_in_district', language=language, district=district)
                    )
                elif district:
                    clarification_parts.append(
                        f", trong đó có **{stats['total_in_district']} căn** ở {district}."
                    )
                else:
                    clarification_parts.append(".")
            else:
                clarification_parts.append(
                    t('search.no_property_type', language=language, property_type=property_type)
                )

            # Part 2: Proactive Options
            clarification_parts.append("\n\n**" + t('search.clarification_header', language=language) + "**\n")

            if district:
                # Suggest expanding to nearby districts
                nearby_districts = await self._get_nearby_districts(district, requirements.get("city"))
                if nearby_districts:
                    clarification_parts.append(
                        f"- 🔍 {t('search.search_nearby_districts', language=language, districts=', '.join(nearby_districts[:3]))}\n"
                    )

                clarification_parts.append(
                    f"- 🌍 {t('search.expand_search_city', language=language, city=city)}\n"
                )

            if requirements.get("special_requirements"):
                spec_req = requirements["special_requirements"][0]
                clarification_parts.append(
                    f"- 📍 {t('search.provide_details', language=language, requirement=spec_req)}\n"
                )

            if bedrooms:
                clarification_parts.append(
                    f"- 🛏️ {t('search.adjust_bedrooms', language=language, bedrooms=bedrooms)}\n"
                )

            # Part 3: Show Top 5 Alternatives
            if scored_results and len(scored_results) > 0:
                count = min(5, len(scored_results))
                clarification_parts.append(
                    f"\n**{t('search.nearby_alternatives', language=language, count=count)}**\n"
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
            clarification_parts.append(f"\n💬 {t('search.how_can_help', language=language)}")

            return "".join(clarification_parts)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Clarification generation failed: {e}")
            return t('search.no_results_expand', language=language)

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
            # FIX: Get REAL statistics from DB Gateway instead of mock data
            property_type = requirements.get("property_type")
            city = requirements.get("city")
            district = requirements.get("district")

            # Query 1: Total in city (if city is specified)
            total_in_city = 0
            if city:
                city_response = await self.http_client.post(
                    f"{self.db_gateway_url}/search",
                    json={
                        "query": "",
                        "filters": {
                            "city": city,
                            "property_type": property_type if property_type else None
                        },
                        "limit": 1  # We only need the total count
                    },
                    timeout=10.0
                )
                if city_response.status_code == 200:
                    city_results = city_response.json()
                    total_in_city = city_results.get("total", 0)

            # Query 2: Total in district (if district is specified)
            total_in_district = 0
            if district:
                district_response = await self.http_client.post(
                    f"{self.db_gateway_url}/search",
                    json={
                        "query": "",
                        "filters": {
                            "district": district,
                            "property_type": property_type if property_type else None
                        },
                        "limit": 1  # We only need the total count
                    },
                    timeout=10.0
                )
                if district_response.status_code == 200:
                    district_results = district_response.json()
                    total_in_district = district_results.get("total", 0)

            self.logger.info(f"{LogEmoji.INFO} [Statistics] City: {total_in_city}, District: {total_in_district}")

            return {
                "total_in_city": total_in_city,
                "total_in_district": total_in_district
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

    # ========================================
    # Property Posting Helper Methods
    # ========================================

    async def _extract_from_images(
        self,
        files: List[FileAttachment],
        text_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract property attributes from images using GPT-4o Vision.

        Args:
            files: List of image attachments
            text_context: Optional text context to enhance extraction

        Returns:
            Extracted entities dict
        """
        try:
            # Prepare images for extraction service
            images_base64 = []
            for file in files[:10]:  # Max 10 images
                if file.mime_type and file.mime_type.startswith('image/'):
                    images_base64.append(file.base64_data)

            if not images_base64:
                self.logger.warning(f"{LogEmoji.WARNING} [Image Extraction] No valid images found")
                return {}

            # Call attribute extraction service
            extraction_response = await self.http_client.post(
                f"{self.extraction_url}/extract-from-images",
                json={
                    "images": images_base64,
                    "text_context": text_context
                },
                timeout=60.0
            )

            if extraction_response.status_code == 200:
                data = extraction_response.json()
                entities = data.get("entities", {})
                confidence = data.get("confidence", 0.0)

                self.logger.info(
                    f"{LogEmoji.SUCCESS} [Image Extraction] Extracted {len(entities)} attributes "
                    f"(confidence: {confidence:.1%})"
                )
                return entities
            else:
                self.logger.warning(
                    f"{LogEmoji.WARNING} [Image Extraction] Failed: {extraction_response.status_code}"
                )
                return {}

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Image Extraction] Failed: {e}")
            return {}

    async def _upload_property_images(
        self,
        property_id: str,
        files: List[FileAttachment],
        auth_token: str
    ) -> bool:
        """
        Upload images to GCS via DB Gateway for a property.

        Args:
            property_id: Property ID
            files: Image file attachments
            auth_token: JWT auth token

        Returns:
            True if successful
        """
        try:
            from io import BytesIO
            import base64

            self.logger.info(f"{LogEmoji.AI} [Image Upload] Uploading {len(files)} image(s) to GCS...")

            # Prepare multipart form data
            form_files = []
            for i, file in enumerate(files[:10]):  # Max 10 images
                if file.mime_type and file.mime_type.startswith('image/'):
                    # Decode base64 to bytes
                    image_bytes = base64.b64decode(file.base64_data)

                    # Generate filename
                    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
                    filename = f"property_{property_id}_image_{i+1}.{ext}"

                    form_files.append(('files', (filename, BytesIO(image_bytes), file.mime_type)))

            if not form_files:
                self.logger.warning(f"{LogEmoji.WARNING} [Image Upload] No valid images to upload")
                return False

            # Upload via DB Gateway
            upload_response = await self.http_client.post(
                f"{self.db_gateway_url}/properties/{property_id}/images/upload-files",
                files=form_files,
                headers={"Authorization": auth_token},
                timeout=60.0
            )

            if upload_response.status_code == 200:
                result = upload_response.json()
                uploaded_count = result.get('uploaded_count', 0)
                self.logger.info(
                    f"{LogEmoji.SUCCESS} [Image Upload] ✅ Uploaded {uploaded_count} images to GCS"
                )
                return True
            else:
                self.logger.warning(
                    f"{LogEmoji.WARNING} [Image Upload] Failed: {upload_response.status_code} - {upload_response.text}"
                )
                return False

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Image Upload] Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _get_district_center_coordinates(self, district: str) -> Optional[Dict[str, float]]:
        """
        Get approximate center coordinates for HCMC districts.

        Args:
            district: District name (e.g., "Quận 1", "Quận 7")

        Returns:
            Dict with lat/lng or None
        """
        # Mapping of HCMC districts to approximate center coordinates
        DISTRICT_COORDINATES = {
            "Quận 1": {"lat": 10.7756, "lng": 106.7019},
            "Quận 2": {"lat": 10.7860, "lng": 106.7431},
            "Quận 3": {"lat": 10.7846, "lng": 106.6878},
            "Quận 4": {"lat": 10.7574, "lng": 106.7028},
            "Quận 5": {"lat": 10.7538, "lng": 106.6639},
            "Quận 6": {"lat": 10.7470, "lng": 106.6345},
            "Quận 7": {"lat": 10.7316, "lng": 106.7196},
            "Quận 8": {"lat": 10.7356, "lng": 106.6758},
            "Quận 9": {"lat": 10.8503, "lng": 106.7896},
            "Quận 10": {"lat": 10.7722, "lng": 106.6681},
            "Quận 11": {"lat": 10.7626, "lng": 106.6504},
            "Quận 12": {"lat": 10.8634, "lng": 106.6711},
            "Quận Bình Thạnh": {"lat": 10.8099, "lng": 106.7103},
            "Quận Gò Vấp": {"lat": 10.8368, "lng": 106.6706},
            "Quận Phú Nhuận": {"lat": 10.7981, "lng": 106.6811},
            "Quận Tân Bình": {"lat": 10.7991, "lng": 106.6527},
            "Quận Tân Phú": {"lat": 10.7875, "lng": 106.6281},
            "Quận Thủ Đức": {"lat": 10.8521, "lng": 106.7644},
            "Quận Bình Tân": {"lat": 10.7407, "lng": 106.6067},
            "Huyện Bình Chánh": {"lat": 10.6834, "lng": 106.5942},
            "Huyện Cần Giờ": {"lat": 10.4090, "lng": 106.9502},
            "Huyện Củ Chi": {"lat": 11.0091, "lng": 106.4922},
            "Huyện Hóc Môn": {"lat": 10.8804, "lng": 106.5926},
            "Huyện Nhà Bè": {"lat": 10.6904, "lng": 106.7285},
        }

        # Normalize district name
        normalized = district.strip()

        return DISTRICT_COORDINATES.get(normalized)

    def _add_map_suggestion_to_feedback(
        self,
        feedback: str,
        district: str,
        language: str
    ) -> str:
        """
        Add map location suggestion to feedback message.

        Args:
            feedback: Generated feedback message
            district: District name
            language: User's preferred language

        Returns:
            Feedback with map suggestion appended
        """
        try:
            # Get approximate coordinates
            coords = self._get_district_center_coordinates(district)

            if not coords:
                self.logger.warning(f"{LogEmoji.WARNING} No coordinates found for district: {district}")
                return feedback

            # Multilingual map suggestion messages
            MAP_SUGGESTIONS = {
                "vi": f"\n\n📍 **Chọn vị trí chính xác trên bản đồ**\n\nTôi đã xác định khu vực của bạn là **{district}**. Bạn có muốn chọn vị trí chính xác trên bản đồ không? (Tùy chọn, giúp người mua dễ tìm thấy hơn)",
                "en": f"\n\n📍 **Select Exact Location on Map**\n\nI've identified your area as **{district}**. Would you like to select the exact location on the map? (Optional, helps buyers find it easier)",
                "th": f"\n\n📍 **เลือกตำแหน่งที่แน่นอนบนแผนที่**\n\nฉันระบุพื้นที่ของคุณเป็น **{district}** คุณต้องการเลือกตำแหน่งที่แน่นอนบนแผนที่หรือไม่? (ทางเลือก ช่วยให้ผู้ซื้อค้นหาได้ง่ายขึ้น)",
                "ja": f"\n\n📍 **地図で正確な場所を選択**\n\nあなたのエリアを **{district}** として特定しました。地図で正確な場所を選択しますか？ (オプション、買い手が見つけやすくなります)"
            }

            suggestion = MAP_SUGGESTIONS.get(language, MAP_SUGGESTIONS["en"])

            # Append metadata for frontend (hidden HTML comment)
            location_meta = {
                "action": "MAP_SUGGESTION",
                "district": district,
                "latitude": coords["lat"],
                "longitude": coords["lng"]
            }

            suggestion += f"\n\n<!--MAP_SUGGESTION:{json.dumps(location_meta)}-->"

            return feedback + suggestion

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to add map suggestion: {e}")
            return feedback

    async def _build_conversation_context(self, history: List[Dict]) -> str:
        """
        Build conversation context string from history for property posting.

        Args:
            history: List of conversation messages

        Returns:
            Formatted context string
        """
        if not history or len(history) == 0:
            return ""

        try:
            context_parts = []
            # Use last 4 messages for context
            for msg in history[-4:]:
                role = msg.get('role', '')
                content = msg.get('content', '')
                if role == 'user':
                    context_parts.append(f"User: {content[:200]}")
                elif role == 'assistant':
                    # Only include first 150 chars of assistant response
                    context_parts.append(f"Assistant: {content[:150]}")

            if context_parts:
                return "Conversation history:\n" + "\n".join(context_parts)
            return ""

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to build conversation context: {e}")
            return ""

    def _detect_user_frustration(self, query: str, history: List[Dict] = None) -> bool:
        """
        Detect if user is showing frustration signals.

        Args:
            query: Current user query
            history: Conversation history

        Returns:
            True if user shows frustration, False otherwise
        """
        try:
            query_lower = query.lower()

            # Load frustration signals from master data (supports all languages)
            frustration_signals = get_frustration_keywords()

            # Check for frustration signals
            if any(signal in query_lower for signal in frustration_signals):
                return True

            return False

        except Exception as e:
            self.logger.warning(f"{LogEmoji.WARNING} Frustration detection failed: {e}")
            return False

    def _detect_completion_confirmation(self, query: str, history: List[Dict] = None) -> bool:
        """
        Detect if user is confirming completion or wants to end conversation.
        Uses master data for multilingual keywords.

        Args:
            query: Current user query
            history: Conversation history

        Returns:
            True if user confirms completion, False otherwise
        """
        try:
            query_lower = query.lower()

            # Load confirmation keywords from master data (supports all languages)
            confirmation_keywords = get_confirmation_keywords()

            # Check if user confirms
            if any(keyword in query_lower for keyword in confirmation_keywords):
                return True

            return False

        except Exception as e:
            self.logger.warning(f"{LogEmoji.WARNING} Completion confirmation detection failed: {e}")
            return False

    def _detect_language(self, history: List[Dict] = None, entities: Dict = None, current_query: str = None) -> str:
        """
        Detect user's language from conversation history or current query using AI langdetect library.

        Args:
            history: Conversation history
            entities: Extracted entities
            current_query: Current user query (used when history is empty)

        Returns:
            Language code: 'vi', 'en', 'th', 'ja', 'zh', 'ko'
        """
        try:
            text_to_detect = None

            # Priority 1: Extract text from recent user messages in history
            if history:
                recent_text = " ".join([msg.get("content", "") for msg in history[-3:] if msg.get("role") == "user"])
                if recent_text and len(recent_text.strip()) > 0:
                    text_to_detect = recent_text

            # Priority 2: If no history, use current query
            if not text_to_detect and current_query and len(current_query.strip()) > 0:
                text_to_detect = current_query
                self.logger.info(f"{LogEmoji.INFO} No history available, detecting language from current query")

            # Perform language detection if we have text
            if text_to_detect:
                # Use langdetect AI library for accurate detection
                detected = detect(text_to_detect)

                # Map langdetect codes to our supported codes
                lang_mapping = {
                    'vi': 'vi',
                    'en': 'en',
                    'th': 'th',
                    'ja': 'ja',
                    'zh-cn': 'zh',
                    'zh-tw': 'zh',
                    'ko': 'ko'
                }

                result = lang_mapping.get(detected, 'en')
                self.logger.info(f"{LogEmoji.SUCCESS} Detected language: {result} (raw: {detected})")
                return result

            # Fallback to Vietnamese for this Vietnamese real estate system
            self.logger.warning(f"{LogEmoji.WARNING} No text to detect language, defaulting to 'vi' (primary market)")
            return "vi"

        except LangDetectException as e:
            self.logger.warning(f"{LogEmoji.WARNING} Language detection failed: {e}, defaulting to 'vi'")
            return "vi"
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Unexpected error in language detection: {e}, defaulting to 'vi'")
            return "vi"

    async def _semantic_chunk_description(self, text: str) -> List[Dict]:
        """
        Call semantic chunking service to chunk property description.

        Uses 6-step semantic chunking pipeline:
        1. Sentence segmentation
        2. Generate embeddings per sentence
        3. Calculate cosine similarity
        4. Combine sentences (threshold 0.75)
        5. Add overlap
        6. Create chunk embeddings

        Args:
            text: Property description text

        Returns:
            List of chunks with text and embeddings
        """
        try:
            if not text or len(text) < 20:
                # Too short to chunk
                return []

            self.logger.info(f"{LogEmoji.AI} [Semantic Chunking] Chunking description ({len(text)} chars)...")

            response = await self.http_client.post(
                "http://semantic-chunking:8080/chunk",  # Internal port, not external 8082
                json={
                    "text": text,
                    "threshold": 0.75,  # CTO spec: cosine similarity >= 0.75
                    "overlap": 1  # 1 sentence overlap
                },
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                chunks = result.get("chunks", [])
                self.logger.info(
                    f"{LogEmoji.SUCCESS} [Semantic Chunking] Created {len(chunks)} chunks"
                )
                return chunks
            else:
                self.logger.warning(
                    f"{LogEmoji.WARNING} [Semantic Chunking] Service error: {response.status_code}"
                )
                return []

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Semantic Chunking] Failed: {e}")
            # Fallback: no chunking
            return []

    async def _save_property_to_db(
        self,
        entities: Dict,
        user_id: str,
        transaction_type: str,
        files: Optional[List[FileAttachment]] = None  # NEW: Image files to upload
    ) -> Optional[Dict]:
        """
        Save extracted property to OpenSearch via DB Gateway.

        Args:
            entities: Extracted property attributes
            user_id: User identifier
            transaction_type: "bán" or "cho thuê"
            files: Optional image files to upload to GCS

        Returns:
            Save result dict or None if failed
        """
        try:
            self.logger.info(f"{LogEmoji.INFO} [Save Property] Preparing to save property for user {user_id}")

            # Map Vietnamese transaction type to ListingType enum
            listing_type = "sale" if transaction_type == "bán" else "rent"

            # Build fallback title and description if not provided
            fallback_title = f"{entities.get('property_type', 'Property').title()} in {entities.get('district', 'Unknown')}"
            if entities.get('bedrooms'):
                fallback_title = f"{entities.get('bedrooms')}BR {fallback_title}"

            # Create detailed fallback description (minimum 50 chars required)
            fallback_description_parts = [
                f"{entities.get('property_type', 'Property').title()} for {listing_type}",
                f"located in {entities.get('district', 'Unknown')}, {entities.get('city', 'Ho Chi Minh City')}."
            ]
            if entities.get('area'):
                fallback_description_parts.append(f"Area: {entities.get('area')} m².")
            if entities.get('bedrooms'):
                fallback_description_parts.append(f"Bedrooms: {entities.get('bedrooms')}.")
            if entities.get('price'):
                fallback_description_parts.append(f"Price: {entities.get('price'):,.0f} VND.")

            fallback_description = " ".join(fallback_description_parts)

            # 🔧 NEW: Semantic Chunking for description
            description_text = entities.get("description", fallback_description)
            chunks = await self._semantic_chunk_description(description_text)

            # Build property data from entities (map to PropertyCreate format)
            property_data = {
                "title": entities.get("title", fallback_title),
                "description": description_text,
                "property_type": entities.get("property_type", "apartment"),
                "listing_type": listing_type,

                # 🔧 NEW: Add chunks and embeddings
                "chunks": chunks,
                "chunk_count": len(chunks),

                # Location
                "district": entities.get("district", "Unknown"),
                "ward": entities.get("ward"),
                "street": entities.get("street"),
                "city": entities.get("city", "Ho Chi Minh City"),

                # Price
                "price": float(entities.get("price", 0)),

                # Attributes
                "bedrooms": entities.get("bedrooms"),
                "bathrooms": entities.get("bathrooms"),
                "area": float(entities.get("area")) if entities.get("area") else None,
                "floor": entities.get("floor"),

                # Dimensions (for townhouse, land)
                "width": float(entities.get("width")) if entities.get("width") else None,
                "depth": float(entities.get("depth")) if entities.get("depth") else None,
                "land_area": float(entities.get("land_area")) if entities.get("land_area") else None,

                # Geolocation (for map - optional, set by user later)
                "latitude": float(entities.get("latitude")) if entities.get("latitude") else None,
                "longitude": float(entities.get("longitude")) if entities.get("longitude") else None,

                # Contact (use dummy for now)
                "contact_phone": entities.get("contact_phone", "0901234567"),
                "contact_email": entities.get("contact_email"),
                "show_contact_info": True,

                # Save as draft initially
                "publish_immediately": False,

                # Flexible attributes (store all other extracted data)
                "attributes": {k: v for k, v in entities.items() if k not in [
                    "title", "description", "property_type", "district", "ward",
                    "street", "city", "price", "bedrooms", "bathrooms", "area", "floor",
                    "width", "depth", "land_area", "latitude", "longitude"
                ]}
            }

            # Create JWT auth token for DB Gateway
            from jose import jwt
            from datetime import datetime, timedelta

            jwt_payload = {
                "sub": user_id,  # user_id as subject
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=1)
            }
            jwt_token = jwt.encode(jwt_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
            auth_token = f"Bearer {jwt_token}"

            # Call DB Gateway to save property
            save_response = await self.http_client.post(
                f"{self.db_gateway_url}/properties",
                json=property_data,
                headers={"Authorization": auth_token},
                timeout=30.0
            )

            if save_response.status_code in [200, 201]:
                result = save_response.json()
                property_id = result.get('property_id')
                self.logger.info(f"{LogEmoji.SUCCESS} [Save Property] ✅ Property saved: {property_id}")

                # NEW: Upload images to GCS if provided
                if files and len(files) > 0 and property_id:
                    await self._upload_property_images(property_id, files, auth_token)

                return result
            else:
                self.logger.warning(f"{LogEmoji.WARNING} [Save Property] Failed: {save_response.status_code} - {save_response.text}")
                return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Save Property] Exception: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _generate_completion_message(
        self,
        entities: Dict,
        overall_score: float,
        property_id: str = None,
        history: List[Dict] = None,
        query: str = "",
        language: str = "vi"
    ) -> str:
        """
        Generate completion/closing message when posting is ready.

        Args:
            entities: Final extracted entities
            overall_score: Final completeness score
            property_id: ID of the saved property (for map picker trigger)
            history: Conversation history
            query: Current user query
            language: User's preferred language

        Returns:
            Completion message in user's language
        """
        try:
            # Build entity summary
            entity_summary = []
            if entities.get("property_type"):
                entity_summary.append(f"Property Type: {entities['property_type']}")
            if entities.get("district"):
                entity_summary.append(f"Location: {entities['district']}")
            if entities.get("bedrooms"):
                entity_summary.append(f"Bedrooms: {entities['bedrooms']}")
            if entities.get("area"):
                entity_summary.append(f"Area: {entities['area']} m²")
            if entities.get("price"):
                entity_summary.append(f"Price: {entities['price']:,.0f} VND")

            entities_text = "\n".join(entity_summary) if entity_summary else "Property details provided"

            # Build prompt for completion message
            prompt = f"""You are a helpful real estate assistant. The user has provided all necessary information for their property posting.

**USER LANGUAGE**: {language} (CRITICAL: Respond ONLY in this language!)

**PROPERTY INFORMATION**:
{entities_text}

**COMPLETENESS SCORE**: {overall_score}/100 (Complete!)

**YOUR TASK**:
Generate a warm, congratulatory closing message in **{language} language** that:
1. Congratulates user on providing complete information ✅
2. Briefly summarizes the key property details
3. Informs them the posting is ready to be published
4. Thanks them for using the service
5. Offers to help with anything else if needed

**FORMAT REQUIREMENTS**:
- Be warm and encouraging
- Use emojis appropriately: ✅ 🎉 🏠 💚
- Keep it concise (3-4 sentences max)
- CRITICAL: Write EVERYTHING in {language} language!

**OUTPUT** (in {language} language):"""

            # Call LLM
            self.logger.info(f"{LogEmoji.INFO} Generating completion message in '{language}'...")

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300,
                    "temperature": 0.8
                },
                timeout=15.0
            )

            if response.status_code == 200:
                data = response.json()
                message = data.get("content", "").strip()
                if message:
                    # Check if location selection is needed (has district but no coordinates)
                    needs_location = (
                        property_id and
                        entities.get("district") and
                        not entities.get("latitude")
                    )

                    if needs_location:
                        # Append location selection trigger for frontend
                        location_trigger = {
                            "action": "LOCATION_SELECTION",
                            "propertyId": property_id,
                            "address": entities.get("address", "") or entities.get("district", ""),
                            "latitude": 10.7769,  # Default to Ho Chi Minh City
                            "longitude": 106.7009
                        }

                        # Add suggestion text based on language
                        location_suggestions = {
                            "vi": "\n\n📍 **Gợi ý:** Chọn vị trí chính xác trên bản đồ để người mua dễ dàng tìm đến!",
                            "en": "\n\n📍 **Suggestion:** Select the exact location on the map to help buyers find it easily!",
                            "th": "\n\n📍 **คำแนะนำ:** เลือกตำแหน่งที่ถูกต้องบนแผนที่เพื่อให้ผู้ซื้อค้นหาได้ง่าย!",
                            "ja": "\n\n📍 **提案:** 購入者が見つけやすいように地図上で正確な場所を選択してください！"
                        }
                        message += location_suggestions.get(language, location_suggestions["en"])
                        message += f"\n\n<!--LOCATION_SELECTION:{json.dumps(location_trigger)}-->"

                    return message

            # Fallback
            fallback_templates = {
                "vi": f"✅ Hoàn tất! Thông tin đăng tin đã đầy đủ ({overall_score:.0f}/100). 🎉 Tin của bạn đã sẵn sàng đăng tải!",
                "en": f"✅ Complete! Your posting information is ready ({overall_score:.0f}/100). 🎉 Your property is ready to be published!",
                "th": f"✅ เสร็จสิ้น! ข้อมูลของคุณครบถ้วน ({overall_score:.0f}/100). 🎉 พร้อมเผยแพร่แล้ว!",
                "ja": f"✅ 完了！情報は完全です ({overall_score:.0f}/100). 🎉 投稿の準備ができました！"
            }
            fallback_message = fallback_templates.get(language, fallback_templates["en"])

            # Also add location trigger to fallback
            needs_location = (
                property_id and
                entities.get("district") and
                not entities.get("latitude")
            )

            if needs_location:
                location_trigger = {
                    "action": "LOCATION_SELECTION",
                    "propertyId": property_id,
                    "address": entities.get("address", "") or entities.get("district", ""),
                    "latitude": 10.7769,
                    "longitude": 106.7009
                }
                location_suggestions = {
                    "vi": "\n\n📍 **Gợi ý:** Chọn vị trí chính xác trên bản đồ!",
                    "en": "\n\n📍 **Suggestion:** Select exact location on map!",
                    "th": "\n\n📍 **คำแนะนำ:** เลือกตำแหน่งบนแผนที่!",
                    "ja": "\n\n📍 **提案:** 地図で正確な場所を選択！"
                }
                fallback_message += location_suggestions.get(language, location_suggestions["en"])
                fallback_message += f"\n\n<!--LOCATION_SELECTION:{json.dumps(location_trigger)}-->"

            return fallback_message

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to generate completion message: {e}")
            return "✅ Complete! Your property posting is ready."

    async def _generate_posting_feedback(
        self,
        entities: Dict,
        completeness_data: Dict,
        transaction_type: str,
        iterations: int,
        history: List[Dict] = None,
        query: str = "",
        language: str = "vi"
    ) -> str:
        """
        Generate multilingual feedback response for property posting using LLM.

        Args:
            entities: Extracted property attributes
            completeness_data: Completeness assessment data
            transaction_type: "bán"/"sale" or "cho thuê"/"rent"
            iterations: Number of reasoning loop iterations
            history: Conversation history
            query: Current user query for frustration detection
            language: User's preferred language

        Returns:
            Formatted feedback response in user's language
        """
        try:
            # Detect user frustration
            is_frustrated = self._detect_user_frustration(query, history) if query else False

            if is_frustrated:
                self.logger.info(f"{LogEmoji.WARNING} User frustration detected - adjusting response tone")

            # Prepare data for LLM
            overall_score = completeness_data.get("overall_score", 0)
            interpretation = completeness_data.get("interpretation", "")
            missing_fields = completeness_data.get("missing_fields", [])
            suggestions = completeness_data.get("suggestions", [])
            strengths = completeness_data.get("strengths", [])
            priority_actions = completeness_data.get("priority_actions", [])

            # Build structured data summary
            entities_summary = []
            if entities.get("property_type"):
                entities_summary.append(f"Property Type: {entities['property_type']}")
            if entities.get("district"):
                entities_summary.append(f"Location: {entities['district']}")
            if entities.get("bedrooms"):
                entities_summary.append(f"Bedrooms: {entities['bedrooms']}")
            if entities.get("area"):
                entities_summary.append(f"Area: {entities['area']} m²")
            if entities.get("price"):
                entities_summary.append(f"Price: {entities['price']:,.0f} VND")

            entities_text = "\n".join(entities_summary) if entities_summary else "No specific details yet"

            # Determine assistant mode based on score
            if overall_score < 30:
                mode = "INITIAL_ASSISTANT"  # Conversational, no formal evaluation
            elif overall_score < 60:
                mode = "GUIDING_ASSISTANT"  # Light guidance, minimal scoring
            else:
                mode = "DETAILED_REVIEW"  # Full evaluation with scoring

            self.logger.info(f"{LogEmoji.INFO} [Posting Feedback] Mode: {mode} (score: {overall_score}/100)")

            # Build LLM prompt based on assistant mode
            frustration_note = ""
            if is_frustrated:
                frustration_note = f"""
**⚠️ USER FRUSTRATION DETECTED**:
The user appears frustrated or confused. Adjust your response to:
- Start with an apology and acknowledgment: "Sorry for any confusion!"
- Clearly show what data you currently have recorded
- Ask them to correct any incorrect information
- Be extra patient and helpful
- Use reassuring tone"""

            # MODE 1: INITIAL ASSISTANT (score < 30) - Conversational, no formal evaluation
            if mode == "INITIAL_ASSISTANT":
                prompt = f"""You are a friendly real estate assistant helping a user post their property.

**USER LANGUAGE**: {language} (CRITICAL: Respond ONLY in this language!)

**TRANSACTION TYPE**: {transaction_type}

**CURRENT INFORMATION**:
{entities_text}
{frustration_note}

**YOUR TASK**:
Act as a helpful secretary (NOT as an evaluator). Generate a warm, conversational response in **{language} language**:

1. **Greeting**: Welcome them warmly with a friendly greeting
2. **Acknowledgment**: Thank them for wanting to post their property for {transaction_type}
3. **Current Info**: If they provided any details, acknowledge them briefly
4. **Helpful Questions**: Ask for 2-3 basic information in a friendly way:
   - What type of property? (Apartment/House/Land/Villa)
   - Where is it located? (District/Area)
   - What's the price range?
5. **Closing**: Encourage them to share information comfortably

**CRITICAL RULES**:
- DO NOT mention scores, completeness, or evaluation
- DO NOT show ❌ missing fields or formal assessment
- BE conversational like a friendly helper, NOT like a form validator
- Use emojis sparingly: 👋 🏠 😊 💬
- Keep it SHORT and friendly (max 5-6 lines)

**OUTPUT** (in {language} language):"""

            # MODE 2: GUIDING ASSISTANT (score 30-60) - Light guidance, minimal scoring
            elif mode == "GUIDING_ASSISTANT":
                prompt = f"""You are a helpful real estate assistant guiding a user to complete their property posting.

**USER LANGUAGE**: {language} (CRITICAL: Respond ONLY in this language!)

**TRANSACTION TYPE**: {transaction_type}

**INFORMATION PROVIDED**:
{entities_text}

**MISSING INFO**: {', '.join(missing_fields[:5]) if missing_fields else 'None'}
{frustration_note}

**YOUR TASK**:
Generate a supportive response in **{language} language**:

1. **Thanks**: Thank them for providing information
2. **Summary**: Show what you've recorded in 1 line with all the details they provided
3. **Gentle Guidance**: Suggest 2-3 important missing details with 💡 emoji:
   - Focus on high-impact fields (location, price, area, property type)
   - Be encouraging, not demanding
4. **Closing**: Ask if they can provide more details

**CRITICAL RULES**:
- DO NOT show formal score/interpretation
- Use ✅ for provided info, 💡 for suggestions (NOT ❌ for missing)
- Keep tone supportive and encouraging
- Keep it SHORT (max 6-8 lines)
- ONLY ask for information NOT already in "INFORMATION PROVIDED" section

**OUTPUT** (in {language} language):"""

            # MODE 3: DETAILED REVIEW (score >= 60) - Full evaluation with scoring
            else:  # DETAILED_REVIEW
                prompt = f"""You are a professional real estate assistant providing detailed feedback on a property posting.

**USER LANGUAGE**: {language} (CRITICAL: Respond ONLY in this language!)

**TRANSACTION TYPE**: {transaction_type}

**EXTRACTED INFORMATION**:
{entities_text}

**COMPLETENESS ASSESSMENT**:
- Overall Score: {overall_score}/100
- Interpretation: {interpretation}
- Missing Fields ({len(missing_fields)}): {', '.join(missing_fields) if missing_fields else 'None'}
- Strengths ({len(strengths)}): {', '.join(strengths) if strengths else 'None'}
- Suggestions ({len(suggestions)}): {', '.join(suggestions) if suggestions else 'None'}
- Priority Actions ({len(priority_actions)}): {', '.join(priority_actions) if priority_actions else 'None'}
{frustration_note}

**YOUR TASK**:
Generate a detailed review response in **{language} language**:

1. **Acknowledgment**: Congratulate them on providing good information
2. **Score**: Display the score (X/100) and interpretation
3. **Strengths**: List 2-3 strong points with ✅ emoji
4. **Missing Info**: List missing fields with ❌ emoji (ONLY fields NOT in "EXTRACTED INFORMATION")
5. **Suggestions**: Provide 2-3 improvement tips with 💡 emoji
6. **Closing**:
   - If score >= 80: Encourage final touches before publishing
   - If score 60-79: Ask for important missing details

**CRITICAL RULES**:
- In "Missing Info" section, ONLY list fields NOT in "EXTRACTED INFORMATION" above
- Be professional but warm and encouraging
- Use emojis: 🎉 ✅ ❌ 💡 🏠

**OUTPUT** (in {language} language):"""

            # Call Core Gateway LLM
            self.logger.info(f"{LogEmoji.INFO} Generating multilingual feedback in '{language}'...")

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.7
                },
                timeout=20.0
            )

            if response.status_code == 200:
                data = response.json()
                feedback = data.get("content", "").strip()

                if feedback:
                    self.logger.info(f"{LogEmoji.SUCCESS} Multilingual feedback generated successfully in '{language}'")

                    # NEW: Add map suggestion if district extracted but no coordinates
                    if entities.get("district") and not entities.get("latitude"):
                        feedback = self._add_map_suggestion_to_feedback(feedback, entities.get("district"), language)

                    return feedback

            # Fallback if LLM fails
            self.logger.warning(f"{LogEmoji.WARNING} LLM feedback generation failed, using simple fallback")
            return self._generate_simple_fallback_feedback(entities, overall_score, missing_fields, language)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to generate posting feedback: {e}")
            return self._generate_simple_fallback_feedback(entities, 0, [], "en")

    def _generate_simple_fallback_feedback(
        self,
        entities: Dict,
        score: float,
        missing_fields: List[str],
        language: str
    ) -> str:
        """
        Simple fallback feedback when LLM generation fails.

        Args:
            entities: Extracted entities
            score: Completeness score
            missing_fields: List of missing fields
            language: Target language

        Returns:
            Simple feedback message
        """
        try:
            # Build message using i18n
            message = t('property_posting.fallback_completeness', language=language, score=int(score))

            if missing_fields:
                missing_str = ', '.join(missing_fields[:3])
                message += " " + t('property_posting.fallback_please_add', language=language, missing_fields=missing_str)
            else:
                message += " " + t('property_posting.fallback_complete', language=language)

            return message

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Fallback feedback generation failed: {e}")
            return "Thank you for your information. Please provide more details about the property."

    # ========================================
    # Price Consultation Helper Methods
    # ========================================

    async def _query_similar_properties(self, property_info: Dict) -> List[Dict]:
        """
        Query database for similar properties to analyze market prices.

        Args:
            property_info: Property attributes (district, property_type, bedrooms, area)

        Returns:
            List of similar properties with prices
        """
        try:
            # Build search filters from property info
            filters = {}

            # Required: Location
            if property_info.get("district"):
                filters["district"] = property_info["district"]
            else:
                # Cannot analyze without location
                self.logger.warning(f"{LogEmoji.WARNING} No district specified, cannot query market data")
                return []

            # Optional: Property type
            if property_info.get("property_type"):
                filters["property_type"] = property_info["property_type"]

            # Optional: Bedrooms (with ±1 tolerance)
            if property_info.get("bedrooms"):
                bedrooms = property_info["bedrooms"]
                filters["bedrooms_min"] = max(1, bedrooms - 1)
                filters["bedrooms_max"] = bedrooms + 1

            # Optional: Area (with ±20% tolerance)
            if property_info.get("area"):
                area = property_info["area"]
                filters["area_min"] = area * 0.8
                filters["area_max"] = area * 1.2

            self.logger.info(f"{LogEmoji.INFO} Querying market data with filters: {filters}")

            # Query DB Gateway for similar properties
            response = await self.http_client.post(
                f"{self.db_gateway_url}/search",
                json={
                    "filters": filters,
                    "limit": 50,  # Get more samples for better analysis
                    "sort_by": "created_at",
                    "sort_order": "desc"
                },
                timeout=30.0
            )

            if response.status_code != 200:
                self.logger.warning(f"{LogEmoji.WARNING} Market data query failed: {response.status_code}")
                return []

            data = response.json()
            properties = data.get("results", [])

            # Filter out properties without price
            properties_with_price = [p for p in properties if p.get("price") and p["price"] > 0]

            self.logger.info(f"{LogEmoji.SUCCESS} Found {len(properties_with_price)} properties with prices")

            return properties_with_price

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to query similar properties: {e}")
            return []

    def _validate_market_data(self, property_info: Dict, market_data: List[Dict]) -> Dict:
        """
        Validate market data quality and calculate confidence score.

        Args:
            property_info: Target property attributes
            market_data: List of similar properties

        Returns:
            Validation result with confidence score and quality metrics
        """
        try:
            # Calculate confidence based on multiple factors
            confidence = 0.0
            quality_factors = []

            # Factor 1: Sample size (0-40 points)
            sample_count = len(market_data)
            if sample_count >= 20:
                sample_score = 0.4
                quality_factors.append("Excellent sample size (20+)")
            elif sample_count >= 10:
                sample_score = 0.3
                quality_factors.append("Good sample size (10+)")
            elif sample_count >= 5:
                sample_score = 0.2
                quality_factors.append("Acceptable sample size (5+)")
            else:
                sample_score = 0.1
                quality_factors.append("Small sample size (<5)")

            confidence += sample_score

            # Factor 2: Location match (0-30 points)
            if property_info.get("district"):
                district_matches = sum(1 for p in market_data if p.get("district") == property_info["district"])
                location_score = min(0.3, district_matches / max(sample_count, 1) * 0.3)
                confidence += location_score

                if location_score >= 0.25:
                    quality_factors.append("Excellent location match")
                elif location_score >= 0.15:
                    quality_factors.append("Good location match")

            # Factor 3: Property type match (0-20 points)
            if property_info.get("property_type"):
                type_matches = sum(1 for p in market_data if p.get("property_type") == property_info["property_type"])
                type_score = min(0.2, type_matches / max(sample_count, 1) * 0.2)
                confidence += type_score

                if type_score >= 0.15:
                    quality_factors.append("Good property type match")

            # Factor 4: Bedrooms match (0-10 points)
            if property_info.get("bedrooms"):
                target_bedrooms = property_info["bedrooms"]
                bedroom_matches = sum(1 for p in market_data
                                     if p.get("bedrooms") and abs(p["bedrooms"] - target_bedrooms) <= 1)
                bedroom_score = min(0.1, bedroom_matches / max(sample_count, 1) * 0.1)
                confidence += bedroom_score

            # Quality assessment
            if confidence >= 0.8:
                data_quality = "Excellent"
            elif confidence >= 0.6:
                data_quality = "Good"
            elif confidence >= 0.4:
                data_quality = "Fair"
            else:
                data_quality = "Poor"

            return {
                "confidence": confidence,
                "data_quality": data_quality,
                "sample_count": sample_count,
                "quality_factors": quality_factors
            }

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to validate market data: {e}")
            return {
                "confidence": 0.0,
                "data_quality": "Unknown",
                "sample_count": 0,
                "quality_factors": []
            }

    async def _generate_price_consultation_response(
        self,
        property_info: Dict,
        market_data: List[Dict],
        confidence: float,
        iterations: int,
        language: str = "vi"
    ) -> str:
        """
        Generate price consultation response with insights.

        Args:
            property_info: Target property attributes
            market_data: Similar properties data
            confidence: Confidence score
            iterations: Number of reasoning iterations
            language: User's preferred language

        Returns:
            Formatted consultation response
        """
        try:
            # Calculate statistics
            has_data = bool(market_data)
            stats_summary = ""

            if market_data:
                prices = [p["price"] for p in market_data if p.get("price")]
                if prices:
                    avg_price = sum(prices) / len(prices)
                    min_price = min(prices)
                    max_price = max(prices)
                    median_price = sorted(prices)[len(prices) // 2]
                    price_per_sqm = avg_price / property_info["area"] if property_info.get("area") else None

                    stats_summary = f"""
Sample Size: {len(prices)} similar properties
Average Price: {avg_price:,.0f} VND ({avg_price/1_000_000_000:.2f} billion)
Price Range: {min_price:,.0f} - {max_price:,.0f} VND
Median Price: {median_price:,.0f} VND ({median_price/1_000_000_000:.2f} billion)
Price per sqm: {price_per_sqm:,.0f} VND/m² (if area provided)
Confidence Level: {confidence:.0%}
"""

            # Build LLM prompt
            property_summary = f"""
Property Type: {property_info.get('property_type', 'Not specified')}
Location: {property_info.get('district', 'Not specified')}
Bedrooms: {property_info.get('bedrooms', 'Not specified')}
Area: {property_info.get('area', 'Not specified')} m²
"""

            prompt = f"""You are a professional real estate price consultant.

**USER LANGUAGE**: {language} (CRITICAL: Respond ONLY in this language!)

**PROPERTY TO CONSULT:**
{property_summary}

**MARKET DATA:**
{stats_summary if has_data else "No similar properties found in the market."}

**YOUR TASK:**
Generate a professional price consultation report in **{language} language** that includes:

1. **Greeting** (📊 icon)
2. **Property Summary**: Show what property they're asking about
3. **Market Analysis**:
   - If data available: Show price statistics, confidence level, price/m², insights
   - If no data: Apologize and suggest providing more details
4. **Recommendations** (if applicable)
5. **Call to Action**: Ask if they need more information

**FORMATTING**:
- Use emojis: 📊 💰 ✅ ⚠️ 📈 💬
- Use markdown bold (**text**) for headers
- Keep professional but friendly tone
- CRITICAL: Write EVERYTHING in {language} language!

**OUTPUT** (in {language} language):"""

            # Call LLM
            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.7
                },
                timeout=20.0
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("content", "").strip()

            # Fallback if LLM fails
            fallback = {
                "vi": f"📊 Tư vấn giá: {'Có dữ liệu thị trường' if has_data else 'Không có dữ liệu'}. Phân tích {iterations} lần.",
                "en": f"📊 Price consultation: {'Market data available' if has_data else 'No market data'}. Analyzed {iterations} times.",
                "th": f"📊 การปรึกษาราคา: {'มีข้อมูลตลาด' if has_data else 'ไม่มีข้อมูลตลาด'}",
                "ja": f"📊 価格相談: {'市場データあり' if has_data else '市場データなし'}"
            }
            return fallback.get(language, fallback["en"])

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to generate price consultation response: {e}")
            return t('errors.retry_error', language=language)

    # ========================================
    # Search Quality & Response Generation
    # ========================================

    async def _generate_quality_response(self, query: str, results: List[Dict], requirements: Dict, evaluation: Dict, language: str = "vi") -> str:
        """
        Generate response with quality assessment and honest feedback

        Args:
            query: User query
            results: Search results
            requirements: Extracted requirements
            evaluation: Quality evaluation
            language: User's preferred language
        """
        try:
            # CTO Priority 4: Track property views for analytics
            if results:
                property_ids = [p.get("property_id") for p in results if p.get("property_id")]
                await self._track_property_views(property_ids)

            if evaluation["quality_score"] >= 0.8:
                # Excellent match
                intro = t('search.found_exact', language=language, count=evaluation['match_count']) + "\n"
            elif evaluation["quality_score"] >= 0.6:
                # Good match
                intro = t('search.found_good', language=language,
                         match_count=evaluation['match_count'],
                         total_count=evaluation['total_count']) + "\n"
            else:
                # Poor match - should have asked clarification instead
                intro = t('search.found_partial', language=language,
                         match_count=evaluation['match_count'],
                         total_count=evaluation['total_count']) + "\n"

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
                # Note: message.data is JSON containing role info
                rows = await conn.fetch(
                    """
                    SELECT data->>'role' as role, content, created_at
                    FROM message
                    WHERE channel_id = $1
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

            # Using current Unix timestamp in milliseconds
            current_time = int(time.time() * 1000)

            async with self.db_pool.acquire() as conn:
                # Ensure user exists first (required for foreign key constraint)
                await conn.execute(
                    """
                    INSERT INTO "user" (id, name, email, role, profile_image_url, created_at, updated_at, last_active_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (id) DO UPDATE SET last_active_at = $8
                    """,
                    user_uuid,
                    user_id,  # name
                    f"{user_id}@system.local",  # email
                    "user",  # role
                    "",  # profile_image_url
                    current_time,
                    current_time,
                    current_time
                )

                # Ensure chat exists (idempotent)
                await conn.execute(
                    """
                    INSERT INTO chat (id, user_id, title, archived, created_at, updated_at, meta)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (id) DO UPDATE SET updated_at = $6
                    """,
                    conv_uuid,
                    user_uuid,
                    "Property Posting",  # Default title
                    False,  # archived
                    current_time,
                    current_time,
                    json.dumps({})
                )

                # Insert message with proper schema
                # Generate unique message ID
                msg_id = str(uuid.uuid4())

                await conn.execute(
                    """
                    INSERT INTO message (id, user_id, channel_id, content, data, meta, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    msg_id,
                    user_uuid,
                    conv_uuid,  # channel_id links to chat.id
                    content,
                    json.dumps({"role": role}),  # Store role in data field
                    json.dumps(metadata or {}),
                    current_time,
                    current_time
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

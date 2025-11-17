"""
Search Handler - Property Search Flow

Handles SEARCH intent:
1. Extract attributes from query
2. Call RAG Service for property search
3. Return natural language response
"""
import time
from typing import Dict, Any, List, Optional
from services.orchestrator.handlers.base_handler import BaseHandler
from services.orchestrator.utils.extraction_helpers import (
    build_filters_from_extraction_response,
    extract_entities_for_logging
)
from shared.utils.logger import LogEmoji
from shared.utils.i18n import t


class SearchHandler(BaseHandler):
    """
    Handles property search requests

    Flow:
    1. Extract search attributes (bedrooms, location, price, etc.)
    2. Query RAG Service with extracted attributes
    3. Return AI-generated response with property results
    """

    async def handle(
        self,
        request_id: str,
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List] = None
    ) -> str:
        """
        Execute search flow

        Args:
            request_id: Request ID for tracing
            query: User search query
            history: Conversation history (optional)
            files: Attached files (optional)

        Returns:
            Natural language response with search results
        """
        start_time = time.time()
        self.log_handler_start(request_id, "SearchHandler", query)

        # STEP 1: Extract attributes from query using enhanced pipeline
        self.logger.info(f"{LogEmoji.AI} [{request_id}] Extracting search attributes with master data...")

        try:
            extraction_result = await self.call_service(
                "attribute_extraction",
                "/extract-query-enhanced",
                json_data={
                    "query": query,
                    "intent": "SEARCH"
                }
            )

            # NEW: Extract from 3-tier response structure (raw/mapped/new)
            raw_attrs = extraction_result.get("raw", {})
            mapped_attrs = extraction_result.get("mapped", [])
            new_attrs = extraction_result.get("new", [])
            confidence = extraction_result.get("confidence", 0.0)

            self.logger.info(
                f"{LogEmoji.SUCCESS} [{request_id}] Extraction complete: "
                f"{len(mapped_attrs)} mapped, {len(new_attrs)} new, confidence: {confidence:.2f}"
            )

            # Build filters using helper function
            extracted_attrs = build_filters_from_extraction_response(extraction_result)

            # Log in human-readable format
            entities_log = extract_entities_for_logging(extraction_result)
            self.logger.info(
                f"{LogEmoji.INFO} [{request_id}] Extracted entities: {entities_log}"
            )
            self.logger.info(
                f"{LogEmoji.INFO} [{request_id}] Built filters: {extracted_attrs}"
            )

        except Exception as e:
            self.logger.warning(
                f"{LogEmoji.WARNING} [{request_id}] Attribute extraction failed: {e}, proceeding without filters"
            )
            extracted_attrs = {}

        # STEP 2: Query RAG Service with extracted attributes
        self.logger.info(f"{LogEmoji.SEARCH} [{request_id}] Querying RAG Service...")

        try:
            rag_result = await self.call_service(
                "rag_service",
                "/query",
                json_data={
                    "query": query,
                    "filters": extracted_attrs,
                    "limit": 5,
                    "use_advanced_rag": True  # Use advanced pipeline if available
                },
                timeout=90.0  # RAG can be slow
            )

            response_text = rag_result.get("response", "")
            retrieved_count = rag_result.get("retrieved_count", 0)
            pipeline_used = rag_result.get("pipeline_used", "unknown")

            self.logger.info(
                f"{LogEmoji.SUCCESS} [{request_id}] RAG returned {retrieved_count} properties "
                f"(pipeline: {pipeline_used})"
            )

            duration_ms = (time.time() - start_time) * 1000
            self.log_handler_complete(request_id, "SearchHandler", duration_ms)

            return response_text

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [{request_id}] RAG Service failed: {e}")
            duration_ms = (time.time() - start_time) * 1000
            self.log_handler_complete(request_id, "SearchHandler", duration_ms)

            # Fallback response
            return t('search.service_unavailable', language='vi')

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
from shared.utils.logger import LogEmoji


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

        # STEP 1: Extract attributes from query
        self.logger.info(f"{LogEmoji.AI} [{request_id}] Extracting search attributes...")

        try:
            extraction_result = await self.call_service(
                "attribute_extraction",
                "/extract",
                json_data={"query": query}
            )

            extracted_attrs = extraction_result.get("attributes", {})
            self.logger.info(
                f"{LogEmoji.SUCCESS} [{request_id}] Extracted attributes: {extracted_attrs}"
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
            return "Xin lỗi, tôi không thể tìm kiếm bất động sản lúc này. Vui lòng thử lại sau."

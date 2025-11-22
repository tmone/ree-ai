"""
Search Handler - Property Search Flow

Handles SEARCH intent:
1. Extract attributes from query
2. Call RAG Service for property search
3. Return structured response with PropertyListComponent
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
from shared.models.ui_components import PropertyListComponent, UIComponent


class SearchHandler(BaseHandler):
    """
    Handles property search requests

    Flow:
    1. Extract search attributes (bedrooms, location, price, etc.)
    2. Query RAG Service with extracted attributes
    3. Return AI-generated response with PropertyListComponent
    """

    async def handle(
        self,
        request_id: str,
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List] = None,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """
        Execute search flow

        Args:
            request_id: Request ID for tracing
            query: User search query
            history: Conversation history (optional)
            files: Attached files (optional)
            language: User's preferred language (vi, en, th, ja)

        Returns:
            Dict with 'message' (str) and 'components' (List[UIComponent])
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
            properties = rag_result.get("properties", [])  # NEW: Get properties data

            self.logger.info(
                f"{LogEmoji.SUCCESS} [{request_id}] RAG returned {retrieved_count} properties "
                f"(pipeline: {pipeline_used})"
            )

            # STEP 3: Create UI components from properties data
            components = []
            if properties:
                property_list_component = PropertyListComponent.create(
                    properties=self._format_properties_for_frontend(properties),
                    total=retrieved_count
                )
                components.append(property_list_component.dict())
                self.logger.info(f"{LogEmoji.SUCCESS} [{request_id}] Created PropertyListComponent with {len(properties)} items")

            duration_ms = (time.time() - start_time) * 1000
            self.log_handler_complete(request_id, "SearchHandler", duration_ms)

            # Return structured response
            return {
                "message": response_text,
                "components": components
            }

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [{request_id}] RAG Service failed: {e}")
            duration_ms = (time.time() - start_time) * 1000
            self.log_handler_complete(request_id, "SearchHandler", duration_ms)

            # Fallback response
            return {
                "message": t('search.service_unavailable', language=language),
                "components": []
            }

    def _format_properties_for_frontend(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format property data for frontend PropertyCard component

        Args:
            properties: Raw property data from database

        Returns:
            List of formatted properties for PropertyCard
        """
        formatted_properties = []

        for prop in properties:
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
            image_url = images[0] if images else ''

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
                "transactionType": prop.get('listing_type', 'sale')  # 'sale' or 'rent'
            })

        return formatted_properties

"""
Property Detail Handler - Show property detail in Inspector modal

Handles PROPERTY_DETAIL intent:
1. Extract property reference (ID, position, keyword)
2. Fetch property data from DB Gateway
3. Return structured response with PropertyInspectorComponent
"""
import re
import time
from typing import Dict, Any, List, Optional
from services.orchestrator.handlers.base_handler import BaseHandler
from shared.utils.logger import LogEmoji
from shared.utils.i18n import t
from shared.models.ui_components import PropertyInspectorComponent, UIComponent


class PropertyDetailHandler(BaseHandler):
    """
    Handles property detail view requests

    Flow:
    1. Extract property reference (ID/position/keyword)
    2. Fetch full property data from DB Gateway
    3. Return PropertyInspectorComponent for modal display
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
        Execute property detail flow

        Args:
            request_id: Request ID for tracing
            query: User query
            history: Conversation history (for position/keyword lookup)
            files: Attached files (unused)
            language: User's preferred language (vi, en, th, ja)

        Returns:
            Dict with 'message' (str) and 'components' (List[UIComponent])
        """
        start_time = time.time()
        self.log_handler_start(request_id, "PropertyDetailHandler", query)

        # STEP 1: Extract property reference
        property_id, position, keyword = self._extract_property_reference(query)

        self.logger.info(
            f"{LogEmoji.INFO} [{request_id}] Extracted - "
            f"ID: {property_id}, Position: {position}, Keyword: {keyword}"
        )

        # STEP 2: Resolve to property_id if needed
        if position and not property_id:
            property_id = await self._get_property_id_from_history(history, position)
            if not property_id:
                return {
                    "message": t('property_detail.position_not_found', language=language, position=position),
                    "components": []
                }

        if keyword and not property_id:
            property_id = await self._search_property_by_keyword(keyword, history)
            if not property_id:
                return {
                    "message": t('property_detail.keyword_not_found', language=language, keyword=keyword),
                    "components": []
                }

        if not property_id:
            return {
                "message": t('property_detail.id_not_found', language=language),
                "components": []
            }

        # STEP 3: Fetch property details from DB Gateway
        self.logger.info(f"{LogEmoji.AI} [{request_id}] Fetching details for {property_id}...")

        try:
            detail_response = await self.call_service(
                "db_gateway",
                f"/properties/{property_id}",
                method="GET",
                timeout=10.0
            )

            if not detail_response:
                return {
                    "message": t('property_detail.not_found', language=language, property_id=property_id),
                    "components": []
                }

            property_data = detail_response

            self.logger.info(f"{LogEmoji.SUCCESS} [{request_id}] Fetched property details")

            # STEP 4: Create PropertyInspectorComponent
            inspector_component = PropertyInspectorComponent.create(
                property_data=property_data
            )

            duration_ms = (time.time() - start_time) * 1000
            self.log_handler_complete(request_id, "PropertyDetailHandler", duration_ms)

            # Return structured response
            return {
                "message": t('property_detail.showing_details', language=language, title=property_data.get('title', 'N/A')),
                "components": [inspector_component.dict()]
            }

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [{request_id}] Fetch failed: {e}")
            duration_ms = (time.time() - start_time) * 1000
            self.log_handler_complete(request_id, "PropertyDetailHandler", duration_ms)

            return {
                "message": t('property_detail.error', language=language),
                "components": []
            }

    def _extract_property_reference(self, query: str) -> tuple:
        """
        Extract property ID, position, or keyword from query.

        Returns:
            (property_id, position, keyword)
        """
        query_lower = query.lower()

        # Pattern 1: Extract property_id (e.g., "ID prop_abc123")
        id_patterns = [
            r"(?:id|property[_\s]id)[:\s]+([a-z0-9_-]{8,})",
            r"(?:mã|ma)\s*(?:số|so)?[:\s]+([a-z0-9_-]{8,})",
            r"([a-z]+_[a-z0-9_-]{7,})",
        ]

        for pattern in id_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return (match.group(1), None, None)

        # Pattern 2: Extract position (e.g., "căn số 2")
        position_patterns = [
            r"(?:căn|can)\s+(?:số|so)\s+(\d+)",
            r"(?:số|so)\s+(\d+)",
            r"(?:item|property)\s+(?:#)?(\d+)",
            r"(?:thứ|thu)\s+(\d+)",
        ]

        for pattern in position_patterns:
            match = re.search(pattern, query_lower)
            if match:
                position = int(match.group(1))
                return (None, position, None)

        # Pattern 3: Extract keyword
        keyword_patterns = [
            r"(?:xem|thông tin|thong tin|chi tiết|chi tiet|info about|details about)[:\s]+(.+)",
            r"(?:cho tôi|cho toi|show me|tell me about)[:\s]+(.+)",
        ]

        for pattern in keyword_patterns:
            match = re.search(pattern, query_lower)
            if match:
                keyword = match.group(1).strip()
                keyword = re.sub(r"\b(về|ve|của|cua|the|of)\b", "", keyword).strip()
                if len(keyword) > 3:
                    return (None, None, keyword)

        return (None, None, None)

    async def _get_property_id_from_history(
        self,
        history: List[Dict],
        position: int
    ) -> Optional[str]:
        """Get property_id from recent search results in conversation history."""
        try:
            for msg in reversed(history or []):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    id_matches = re.findall(r"ID:\s*`([a-z0-9_-]+)`", content)

                    if id_matches and len(id_matches) >= position:
                        property_id = id_matches[position - 1]
                        self.logger.info(
                            f"{LogEmoji.SUCCESS} Found ID from history position {position}: {property_id}"
                        )
                        return property_id

            self.logger.warning(f"{LogEmoji.WARNING} No property found at position {position}")
            return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} History lookup failed: {e}")
            return None

    async def _search_property_by_keyword(
        self,
        keyword: str,
        history: List[Dict]
    ) -> Optional[str]:
        """Search for property by keyword."""
        try:
            self.logger.info(f"{LogEmoji.AI} Searching by keyword: {keyword}")

            # Strategy 1: Check recent history
            for msg in reversed(history or []):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    property_blocks = re.findall(
                        r"\d+\.\s+\*\*(.+?)\*\*.*?ID:\s*`([a-z0-9_-]+)`",
                        content,
                        re.DOTALL
                    )

                    for title, prop_id in property_blocks:
                        if keyword.lower() in title.lower():
                            self.logger.info(f"{LogEmoji.SUCCESS} Found match: {title} → {prop_id}")
                            return prop_id

            # Strategy 2: Trigger new search
            self.logger.info(f"{LogEmoji.AI} No match in history, searching...")

            search_response = await self.call_service(
                "db_gateway",
                "/hybrid-search",
                json_data={
                    "query": keyword,
                    "filters": {},
                    "limit": 1
                },
                timeout=10.0
            )

            if search_response:
                results = search_response.get("results", [])
                if results:
                    property_id = results[0].get("property_id")
                    self.logger.info(f"{LogEmoji.SUCCESS} Found via search: {property_id}")
                    return property_id

            self.logger.warning(f"{LogEmoji.WARNING} No property found for: {keyword}")
            return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Keyword search failed: {e}")
            return None

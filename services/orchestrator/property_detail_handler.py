"""
Property Detail View Handler - CTO Requirement: Detail View by ID/Keyword
"""
import re
from typing import Dict, List, Optional
from shared.utils.logger import LogEmoji
from shared.utils.i18n import t


async def handle_property_detail(
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
        property_id, position, keyword = _extract_property_reference(query)

        self.logger.info(
            f"{LogEmoji.INFO} [Property Detail] Extracted - "
            f"ID: {property_id}, Position: {position}, Keyword: {keyword}"
        )

        # STEP 2: If position (e.g., "căn số 2"), get property_id from recent search history
        if position and not property_id:
            property_id = await _get_property_id_from_history(self, history, position)

            if not property_id:
                return t('property_detail.position_not_found', language=language, position=position)

        # STEP 3: If keyword, search for matching property
        if keyword and not property_id:
            property_id = await _search_property_by_keyword(self, keyword, history)

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
            return _format_property_detail(property_data, language)

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [Property Detail] Fetch failed: {e}")
            return t('property_detail.error', language=language)

    except Exception as e:
        self.logger.error(f"{LogEmoji.ERROR} [Property Detail] Failed: {e}")
        import traceback
        traceback.print_exc()
        return t('property_detail.error', language=language)


def _extract_property_reference(query: str) -> tuple:
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

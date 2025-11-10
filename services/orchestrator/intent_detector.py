"""
Intent Detector Module

Detects user intent from query:
- SEARCH: Property search queries
- CHAT: General conversation, questions, greetings
- LISTING: Property listing creation (future)
"""
from typing import Dict, Any
# Note: Using simple strings instead of IntentType enum to avoid Pydantic dependency


class IntentDetector:
    """
    Simple keyword-based intent detection

    Future: Can be enhanced with:
    - ML-based classification
    - LLM-powered intent detection
    - Multi-label intent support
    """

    # Intent keywords mapping
    SEARCH_KEYWORDS = [
        "tìm", "cần", "mua", "bán", "thuê", "cho thuê",
        "căn hộ", "nhà", "đất", "biệt thự", "phòng",
        "quận", "huyện", "phường", "đường",
        "giá", "triệu", "tỷ", "m2", "m²",
        "phòng ngủ", "wc", "toilet"
    ]

    CHAT_KEYWORDS = [
        "hi", "hello", "chào", "xin chào",
        "là gì", "thế nào", "như thế nào",
        "tại sao", "vì sao", "làm sao",
        "có thể", "nên", "không nên",
        "tư vấn", "hỏi", "giải thích"
    ]

    def detect(self, query: str, has_files: bool = False) -> str:
        """
        Detect intent from user query

        Args:
            query: User query text
            has_files: Whether request includes files (images, docs)

        Returns:
            Intent string ("search", "chat", or "listing")

        Logic:
        - If has files (images) → "chat" (for vision analysis)
        - If contains search keywords → "search"
        - Otherwise → "chat"
        """
        # Files (especially images) → chat for analysis
        if has_files:
            return "chat"

        query_lower = query.lower()

        # Count search vs chat keywords
        search_score = sum(1 for kw in self.SEARCH_KEYWORDS if kw in query_lower)
        chat_score = sum(1 for kw in self.CHAT_KEYWORDS if kw in query_lower)

        # Search if has search keywords and no chat keywords dominate
        if search_score > 0 and search_score >= chat_score:
            return "search"

        # Default to chat
        return "chat"

    def detect_with_confidence(self, query: str, has_files: bool = False) -> Dict[str, Any]:
        """
        Detect intent with confidence score

        Returns:
            {
                "intent": "search" | "chat" | "listing",
                "confidence": 0.0 - 1.0,
                "scores": {"search": int, "chat": int}
            }
        """
        intent = self.detect(query, has_files)

        query_lower = query.lower()
        search_score = sum(1 for kw in self.SEARCH_KEYWORDS if kw in query_lower)
        chat_score = sum(1 for kw in self.CHAT_KEYWORDS if kw in query_lower)

        total_score = search_score + chat_score
        confidence = 0.9 if total_score > 0 else 0.5  # High confidence if keywords found

        return {
            "intent": intent,
            "confidence": confidence,
            "scores": {"search": search_score, "chat": chat_score},
            "has_files": has_files
        }

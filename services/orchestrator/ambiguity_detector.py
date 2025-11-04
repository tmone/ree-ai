"""
Ambiguity Detector - Phase 1
Detects vague queries and suggests clarifications
"""
import re
from typing import List, Optional
from shared.models.reasoning import (
    AmbiguityDetectionResult,
    ClarificationQuestion,
    AmbiguityType
)


class AmbiguityDetector:
    """
    Detects ambiguous queries and generates clarification questions
    Inspired by Codex's clarification pattern
    """

    def __init__(self):
        # Thresholds
        self.min_query_length = 10  # Very short queries are likely ambiguous
        self.max_broad_location_query = 30  # "Nhà ở Quận 2" is too broad if query is short

    async def detect_ambiguities(self, query: str) -> AmbiguityDetectionResult:
        """
        Main method to detect all ambiguities in a query
        """
        clarifications = []

        # Check 1: Location too broad
        location_ambiguity = self._check_location_too_broad(query)
        if location_ambiguity:
            clarifications.append(location_ambiguity)

        # Check 2: Property type missing
        property_type_ambiguity = self._check_property_type_missing(query)
        if property_type_ambiguity:
            clarifications.append(property_type_ambiguity)

        # Check 3: Price range unclear
        price_ambiguity = self._check_price_unclear(query)
        if price_ambiguity:
            clarifications.append(price_ambiguity)

        # Check 4: Amenity ambiguous
        amenity_ambiguity = self._check_amenity_ambiguous(query)
        if amenity_ambiguity:
            clarifications.append(amenity_ambiguity)

        # Check 5: Multiple intents
        multiple_intents = self._check_multiple_intents(query)
        if multiple_intents:
            clarifications.append(multiple_intents)

        has_ambiguity = len(clarifications) > 0
        confidence = 1.0 - (len(clarifications) * 0.2)  # More ambiguities = lower confidence

        return AmbiguityDetectionResult(
            has_ambiguity=has_ambiguity,
            clarifications=clarifications,
            confidence=max(0.0, confidence)
        )

    def _check_location_too_broad(self, query: str) -> Optional[ClarificationQuestion]:
        """
        Detect if location mentioned is too broad
        Example: "Nhà ở Quận 2" without specific area
        """
        query_lower = query.lower()

        # District 2 is very large, needs area specification
        if "quận 2" in query_lower or "district 2" in query_lower or "q2" in query_lower:
            # Check if specific area already mentioned
            specific_areas = ["thảo điền", "an phú", "cát lái", "thủ thiêm", "thao dien", "an phu", "cat lai", "thu thiem"]
            if not any(area in query_lower for area in specific_areas):
                # Query is short and only mentions district
                if len(query) < self.max_broad_location_query:
                    return ClarificationQuestion(
                        type=AmbiguityType.LOCATION_TOO_BROAD,
                        question="Quận 2 rất rộng. Bạn muốn khu vực nào cụ thể?",
                        options=["Thảo Điền (expat area)", "An Phú (near schools)", "Cát Lái (affordable)", "Thủ Thiêm (new urban)"],
                        default="An Phú"
                    )

        # District 7 check
        if "quận 7" in query_lower or "district 7" in query_lower or "q7" in query_lower:
            specific_areas = ["phú mỹ hưng", "pmh", "tân phú", "tân quy", "phu my hung"]
            if not any(area in query_lower for area in specific_areas):
                if len(query) < self.max_broad_location_query:
                    return ClarificationQuestion(
                        type=AmbiguityType.LOCATION_TOO_BROAD,
                        question="Quận 7 có nhiều khu vực khác nhau. Bạn quan tâm khu nào?",
                        options=["Phú Mỹ Hưng (high-end)", "Tân Phú (affordable)", "Tân Quy (mixed)"],
                        default="Phú Mỹ Hưng"
                    )

        return None

    def _check_property_type_missing(self, query: str) -> Optional[ClarificationQuestion]:
        """
        Detect if property type is not specified
        Example: "5 tỷ ở Quận 2" - what type?
        """
        query_lower = query.lower()

        # Check if property type keywords exist
        property_types = [
            "căn hộ", "apartment", "condo", "chung cư",
            "biệt thự", "villa", "nhà vườn",
            "nhà phố", "townhouse", "nhà riêng",
            "đất", "land", "đất nền"
        ]

        has_property_type = any(ptype in query_lower for ptype in property_types)

        # Check if price or location mentioned (indicates search intent)
        has_price = any(keyword in query_lower for keyword in ["tỷ", "triệu", "billion", "million"])
        has_location = any(keyword in query_lower for keyword in ["quận", "district", "q"])

        # If price/location mentioned but no property type → ambiguous
        if (has_price or has_location) and not has_property_type:
            return ClarificationQuestion(
                type=AmbiguityType.PROPERTY_TYPE_MISSING,
                question="Bạn đang tìm loại hình bất động sản nào?",
                options=["Căn hộ/Chung cư", "Biệt thự", "Nhà phố", "Đất nền"],
                default="Căn hộ/Chung cư"
            )

        return None

    def _check_price_unclear(self, query: str) -> Optional[ClarificationQuestion]:
        """
        Detect if price range is ambiguous
        Example: "Nhà giá tốt" - define "good price"?
        """
        query_lower = query.lower()

        # Subjective price terms without specific numbers
        subjective_price_terms = ["giá tốt", "giá rẻ", "hời", "phải chăng", "affordable", "cheap", "good price"]

        has_subjective_price = any(term in query_lower for term in subjective_price_terms)

        # Check if specific price NOT mentioned
        has_specific_price = bool(re.search(r'\d+\s*(tỷ|triệu|billion|million)', query_lower))

        if has_subjective_price and not has_specific_price:
            return ClarificationQuestion(
                type=AmbiguityType.PRICE_RANGE_UNCLEAR,
                question="'Giá tốt' có nghĩa là khoảng bao nhiêu đối với bạn?",
                options=["< 2 tỷ (budget)", "2-5 tỷ (mid-range)", "5-10 tỷ (comfortable)", "> 10 tỷ (luxury)"],
                default="2-5 tỷ"
            )

        return None

    def _check_amenity_ambiguous(self, query: str) -> Optional[ClarificationQuestion]:
        """
        Detect ambiguous amenity descriptions
        Example: "Nhà đẹp" - what does "beautiful" mean?
        """
        query_lower = query.lower()

        # FIX BUG #8: Expanded vague aesthetic terms list
        vague_terms = {
            "đẹp": {
                "question": "Bạn muốn 'đẹp' theo nghĩa nào?",
                "options": ["Hiện đại (modern design)", "View đẹp (nice view)", "Nội thất cao cấp (luxury interior)", "Kiến trúc độc đáo (unique architecture)"],
                "default": "Hiện đại"
            },
            "beautiful": {
                "question": "What makes a property 'beautiful' for you?",
                "options": ["Modern architecture", "Nice view", "Luxury interior", "Unique design"],
                "default": "Modern architecture"
            },
            "nice": {
                "question": "What specific features are you looking for in a 'nice' property?",
                "options": ["Good location", "Modern amenities", "Spacious", "Well-maintained"],
                "default": "Good location"
            },
            "good": {
                "question": "What qualities matter most in a 'good' property?",
                "options": ["Location", "Price", "Amenities", "Size"],
                "default": "Location"
            },
            "tốt": {
                "question": "'Tốt' theo tiêu chí nào?",
                "options": ["Vị trí tốt", "Giá tốt", "Tiện nghi đầy đủ", "Diện tích rộng"],
                "default": "Vị trí tốt"
            },
            "sang": {
                "question": "'Sang trọng' bạn mong đợi những tiện nghi gì?",
                "options": ["Hồ bơi + Gym", "Nội thất luxury", "Smart home", "Vị trí đẹp"],
                "default": "Hồ bơi + Gym"
            },
            "luxury": {
                "question": "What luxury features are you looking for?",
                "options": ["Pool + Gym", "High-end interior", "Smart home", "Premium location"],
                "default": "Pool + Gym"
            },
            "cao cấp": {
                "question": "'Cao cấp' bạn quan tâm đến?",
                "options": ["Nội thất sang", "Vị trí đắc địa", "Tiện ích 5 sao", "Thương hiệu uy tín"],
                "default": "Tiện ích 5 sao"
            },
            "tiện nghi": {
                "question": "Tiện nghi nào quan trọng nhất với bạn?",
                "options": ["Hồ bơi", "Gym", "Gần trường", "Gần siêu thị"],
                "default": "Gần trường"
            },
            "ổn": {
                "question": "'Ổn' theo bạn là như thế nào?",
                "options": ["Giá phải chăng", "Vị trí tiện", "Đủ tiện nghi cơ bản", "Diện tích hợp lý"],
                "default": "Giá phải chăng"
            },
            "okay": {
                "question": "What makes a property 'okay' for you?",
                "options": ["Affordable price", "Convenient location", "Basic amenities", "Reasonable size"],
                "default": "Affordable price"
            },
            "chất lượng": {
                "question": "'Chất lượng' bạn đánh giá theo?",
                "options": ["Vật liệu xây dựng", "Tiện ích", "Vị trí", "Thiết kế"],
                "default": "Vật liệu xây dựng"
            },
            "quality": {
                "question": "What quality aspects matter most?",
                "options": ["Construction materials", "Amenities", "Location", "Design"],
                "default": "Construction materials"
            }
        }

        for term, config in vague_terms.items():
            if term in query_lower:
                # FIX BUG #8: Flag ambiguity if:
                # 1. Short query (< 30 chars) OR
                # 2. No specific criteria even in longer query
                if len(query) < 30 or not self._has_specific_criteria(query_lower):
                    return ClarificationQuestion(
                        type=AmbiguityType.AMENITY_AMBIGUOUS,
                        question=config["question"],
                        options=config["options"],
                        default=config["default"]
                    )

        return None

    def _has_specific_criteria(self, query: str) -> bool:
        """
        FIX BUG #8: Check if query has specific search criteria
        If query has specific criteria, vague terms are less problematic
        """
        specific_criteria = [
            r'\d+\s*(phòng|bedroom|br|pn)',  # "3 phòng ngủ"
            r'\d+\s*(tỷ|triệu|million|billion)',  # "5 tỷ"
            r'quận\s*\d+',  # "Quận 2"
            r'district\s*\d+',  # "District 2"
            r'(hồ bơi|pool|gym|ban công|balcony|view|parking|garden)',  # Specific amenities
            r'(thảo điền|an phú|phú mỹ hưng|pmh|bình thạnh)',  # Specific areas
            r'\d+\s*m[²2]',  # "100m²"
        ]

        for pattern in specific_criteria:
            if re.search(pattern, query.lower()):
                return True

        return False

    def _check_multiple_intents(self, query: str) -> Optional[ClarificationQuestion]:
        """
        Detect if query has multiple intents
        Example: "So sánh giá và tìm nhà" - comparison + search
        """
        query_lower = query.lower()

        # Intent keywords
        intent_keywords = {
            "search": ["tìm", "search", "find", "có", "cho tôi"],
            "compare": ["so sánh", "compare", "khác nhau", "difference"],
            "analysis": ["phân tích", "analyze", "đánh giá", "review"],
            "advice": ["tư vấn", "advise", "nên", "should"]
        }

        # Count how many intents are present
        detected_intents = []
        for intent, keywords in intent_keywords.items():
            if any(kw in query_lower for kw in keywords):
                detected_intents.append(intent)

        # If multiple intents detected
        if len(detected_intents) >= 2:
            return ClarificationQuestion(
                type=AmbiguityType.MULTIPLE_INTENTS,
                question="Câu hỏi của bạn có nhiều mục đích. Bạn muốn làm gì trước?",
                options=[
                    f"Tìm kiếm bất động sản (search)" if "search" in detected_intents else None,
                    f"So sánh các lựa chọn (compare)" if "compare" in detected_intents else None,
                    f"Phân tích chi tiết (analysis)" if "analysis" in detected_intents else None,
                    f"Tư vấn đầu tư (advice)" if "advice" in detected_intents else None
                ],
                default="Tìm kiếm bất động sản"
            )

        return None

    def should_clarify(self, ambiguity_result: AmbiguityDetectionResult) -> bool:
        """
        Determine if we should ask for clarification or proceed
        """
        # If confidence is very low, definitely clarify
        if ambiguity_result.confidence < 0.5:
            return True

        # If multiple ambiguities, clarify
        if len(ambiguity_result.clarifications) >= 2:
            return True

        # FIX BUG #8: Expand critical ambiguity types
        # If single ambiguity of critical type, clarify
        if len(ambiguity_result.clarifications) == 1:
            critical_types = [
                AmbiguityType.PROPERTY_TYPE_MISSING,
                AmbiguityType.MULTIPLE_INTENTS,
                AmbiguityType.AMENITY_AMBIGUOUS,  # NEW: Vague aesthetic terms need clarification
                AmbiguityType.PRICE_RANGE_UNCLEAR  # NEW: Subjective price terms need clarification
            ]
            if ambiguity_result.clarifications[0].type in critical_types:
                return True

        # Otherwise, proceed with best guess
        return False

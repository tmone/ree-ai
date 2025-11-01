"""
ConversationContext Service - User Preference Tracking

OpenAI Intelligent Design: Track user behavior to anticipate needs

This service learns from user queries and interactions to:
1. Extract and remember budget preferences
2. Track preferred locations
3. Identify property type interests
4. Detect must-have features
5. Generate contextual proactive suggestions (OpenAI compliant)

Storage: Redis with user session
Integration: Orchestrator → ConversationContext → RAG Service
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json


class ConversationContext:
    """
    Track user preferences across property search sessions

    OpenAI Principle: "Intelligent - Tools remain aware of discussion context
    and anticipate user needs"
    """

    def __init__(self, user_id: str, redis_client=None):
        """
        Initialize conversation context for a user

        Args:
            user_id: Unique user identifier
            redis_client: Redis client for persistence (optional, uses in-memory if None)
        """
        self.user_id = user_id
        self.redis_client = redis_client
        self.redis_key = f"conversation_context:{user_id}"

        # Load existing preferences or initialize new
        self.preferences = self._load_preferences()

    def _load_preferences(self) -> Dict:
        """Load preferences from Redis or return defaults"""
        if self.redis_client:
            try:
                data = self.redis_client.get(self.redis_key)
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"Failed to load preferences from Redis: {e}")

        # Default preferences structure
        return {
            "budget_range": None,           # (min, max) in VND
            "preferred_locations": [],      # List of districts/areas
            "property_types": [],           # apartment, house, villa, etc.
            "key_features": [],             # pool, gym, garden, etc.
            "bedrooms_range": None,         # (min, max)
            "area_range": None,             # (min, max) in m²
            "last_search_date": None,       # ISO datetime
            "search_history": [],           # Last 10 queries
            "clicked_properties": [],       # Last 10 property_ids
            "session_count": 0              # Number of search sessions
        }

    def _save_preferences(self):
        """Persist preferences to Redis"""
        if self.redis_client:
            try:
                data = json.dumps(self.preferences)
                # Expire after 30 days of inactivity
                self.redis_client.setex(self.redis_key, 30 * 24 * 60 * 60, data)
            except Exception as e:
                print(f"Failed to save preferences to Redis: {e}")

    def learn_from_query(self, query: str, clicked_property_ids: List[str] = None):
        """
        Extract and update preferences from user query

        Args:
            query: User's search query (Vietnamese)
            clicked_property_ids: IDs of properties user clicked on

        Examples:
            "tìm căn hộ 2 phòng ngủ dưới 5 tỷ quận 1"
            → budget: (0, 5_000_000_000)
            → location: ["Quận 1"]
            → bedrooms: (2, 2)
            → property_type: ["apartment"]
        """
        query_lower = query.lower()

        # 1. Extract budget range
        budget = self._extract_budget(query_lower)
        if budget:
            self.preferences["budget_range"] = budget

        # 2. Extract locations (Vietnamese districts)
        locations = self._extract_locations(query_lower)
        if locations:
            for loc in locations:
                if loc not in self.preferences["preferred_locations"]:
                    self.preferences["preferred_locations"].append(loc)
                    # Keep only last 5 locations
                    if len(self.preferences["preferred_locations"]) > 5:
                        self.preferences["preferred_locations"].pop(0)

        # 3. Extract property types
        property_types = self._extract_property_types(query_lower)
        if property_types:
            for ptype in property_types:
                if ptype not in self.preferences["property_types"]:
                    self.preferences["property_types"].append(ptype)

        # 4. Extract bedrooms
        bedrooms = self._extract_bedrooms(query_lower)
        if bedrooms:
            self.preferences["bedrooms_range"] = bedrooms

        # 5. Extract area range
        area = self._extract_area(query_lower)
        if area:
            self.preferences["area_range"] = area

        # 6. Extract key features
        features = self._extract_features(query_lower)
        if features:
            for feature in features:
                if feature not in self.preferences["key_features"]:
                    self.preferences["key_features"].append(feature)

        # 7. Update search history
        self.preferences["search_history"].append({
            "query": query,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.preferences["search_history"]) > 10:
            self.preferences["search_history"].pop(0)

        # 8. Track clicked properties
        if clicked_property_ids:
            self.preferences["clicked_properties"].extend(clicked_property_ids)
            if len(self.preferences["clicked_properties"]) > 10:
                self.preferences["clicked_properties"] = self.preferences["clicked_properties"][-10:]

        # 9. Update metadata
        self.preferences["last_search_date"] = datetime.now().isoformat()
        self.preferences["session_count"] += 1

        # Save to Redis
        self._save_preferences()

    def _extract_budget(self, query: str) -> Optional[Tuple[int, int]]:
        """
        Extract budget range from query

        Patterns:
        - "dưới 5 tỷ" → (0, 5_000_000_000)
        - "từ 3 đến 5 tỷ" → (3_000_000_000, 5_000_000_000)
        - "dưới 500 triệu" → (0, 500_000_000)
        - "khoảng 3 tỷ" → (2_500_000_000, 3_500_000_000) ±500M
        """
        # Pattern: "dưới X tỷ/triệu"
        under_pattern = r'dưới\s+(\d+(?:[.,]\d+)?)\s*(tỷ|triệu)'
        match = re.search(under_pattern, query)
        if match:
            amount = float(match.group(1).replace(',', '.'))
            unit = match.group(2)
            max_price = int(amount * 1_000_000_000) if unit == 'tỷ' else int(amount * 1_000_000)
            return (0, max_price)

        # Pattern: "từ X đến Y tỷ/triệu"
        range_pattern = r'từ\s+(\d+(?:[.,]\d+)?)\s*đến\s+(\d+(?:[.,]\d+)?)\s*(tỷ|triệu)'
        match = re.search(range_pattern, query)
        if match:
            min_amount = float(match.group(1).replace(',', '.'))
            max_amount = float(match.group(2).replace(',', '.'))
            unit = match.group(3)
            multiplier = 1_000_000_000 if unit == 'tỷ' else 1_000_000
            return (int(min_amount * multiplier), int(max_amount * multiplier))

        # Pattern: "khoảng X tỷ/triệu" (±20%)
        around_pattern = r'khoảng\s+(\d+(?:[.,]\d+)?)\s*(tỷ|triệu)'
        match = re.search(around_pattern, query)
        if match:
            amount = float(match.group(1).replace(',', '.'))
            unit = match.group(2)
            center = int(amount * 1_000_000_000) if unit == 'tỷ' else int(amount * 1_000_000)
            margin = int(center * 0.2)
            return (center - margin, center + margin)

        return None

    def _extract_locations(self, query: str) -> List[str]:
        """
        Extract location names from query

        Patterns:
        - "quận 1", "quận 7"
        - "thủ đức", "bình thạnh"
        - "tp.hcm", "hà nội"
        """
        locations = []

        # Districts
        district_patterns = [
            r'quận\s+(\d+)',
            r'quận\s+([a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]+)',
        ]

        for pattern in district_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                location = f"Quận {match}" if match.isdigit() else f"Quận {match.strip().title()}"
                locations.append(location)

        # Cities
        city_keywords = ['tp.hcm', 'hà nội', 'đà nẵng', 'cần thơ', 'hải phòng']
        for city in city_keywords:
            if city in query:
                locations.append(city.upper() if city == 'tp.hcm' else city.title())

        return locations

    def _extract_property_types(self, query: str) -> List[str]:
        """
        Extract property types from query

        Mappings:
        - "căn hộ", "chung cư" → apartment
        - "nhà riêng", "nhà phố" → house
        - "biệt thự", "villa" → villa
        - "đất nền", "đất" → land
        """
        type_mapping = {
            'apartment': ['căn hộ', 'chung cư', 'apartment'],
            'house': ['nhà riêng', 'nhà phố', 'house'],
            'villa': ['biệt thự', 'villa'],
            'land': ['đất nền', 'đất'],
            'townhouse': ['nhà liền kề', 'townhouse'],
            'office': ['văn phòng', 'office']
        }

        found_types = []
        for ptype, keywords in type_mapping.items():
            for keyword in keywords:
                if keyword in query:
                    found_types.append(ptype)
                    break

        return found_types

    def _extract_bedrooms(self, query: str) -> Optional[Tuple[int, int]]:
        """
        Extract bedroom count from query

        Patterns:
        - "2 phòng ngủ", "2pn" → (2, 2)
        - "từ 2 đến 3 phòng ngủ" → (2, 3)
        """
        # Exact count: "2 phòng ngủ", "2pn"
        exact_pattern = r'(\d+)\s*(?:phòng\s*ngủ|pn)'
        match = re.search(exact_pattern, query)
        if match:
            count = int(match.group(1))
            return (count, count)

        # Range: "từ 2 đến 3 phòng ngủ"
        range_pattern = r'từ\s+(\d+)\s*đến\s+(\d+)\s*(?:phòng\s*ngủ|pn)'
        match = re.search(range_pattern, query)
        if match:
            min_count = int(match.group(1))
            max_count = int(match.group(2))
            return (min_count, max_count)

        return None

    def _extract_area(self, query: str) -> Optional[Tuple[float, float]]:
        """
        Extract area range from query

        Patterns:
        - "70m2", "70 m²" → (70, 70)
        - "từ 70 đến 100m2" → (70, 100)
        - "trên 100m2" → (100, None)
        """
        # Exact area: "70m2", "70 m²"
        exact_pattern = r'(\d+(?:[.,]\d+)?)\s*m[²2]'
        match = re.search(exact_pattern, query)
        if match and 'từ' not in query[:match.start()]:
            area = float(match.group(1).replace(',', '.'))
            return (area, area)

        # Range: "từ 70 đến 100m2"
        range_pattern = r'từ\s+(\d+(?:[.,]\d+)?)\s*đến\s+(\d+(?:[.,]\d+)?)\s*m[²2]'
        match = re.search(range_pattern, query)
        if match:
            min_area = float(match.group(1).replace(',', '.'))
            max_area = float(match.group(2).replace(',', '.'))
            return (min_area, max_area)

        # Above: "trên 100m2"
        above_pattern = r'trên\s+(\d+(?:[.,]\d+)?)\s*m[²2]'
        match = re.search(above_pattern, query)
        if match:
            min_area = float(match.group(1).replace(',', '.'))
            return (min_area, 999999)  # Large number

        return None

    def _extract_features(self, query: str) -> List[str]:
        """
        Extract key features from query

        Features: pool, gym, garden, parking, security, view
        """
        feature_keywords = {
            'pool': ['hồ bơi', 'bể bơi', 'pool'],
            'gym': ['gym', 'phòng gym', 'thể dục'],
            'garden': ['vườn', 'sân vườn', 'garden'],
            'parking': ['chỗ đỗ xe', 'garage', 'parking'],
            'security': ['bảo vệ 24/7', 'an ninh', 'security'],
            'balcony': ['ban công', 'balcony'],
            'view': ['view đẹp', 'view sông', 'view thành phố']
        }

        found_features = []
        for feature, keywords in feature_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    found_features.append(feature)
                    break

        return found_features

    def generate_proactive_suggestion(self) -> Optional[str]:
        """
        Generate contextual proactive suggestion (OpenAI compliant)

        OpenAI Rule: "Only surface contextual nudges tied to user intent"

        Returns:
            Suggestion string or None if not contextually relevant
        """
        # Check if we have enough context
        if not self.preferences.get("budget_range") or not self.preferences.get("preferred_locations"):
            return None

        # Check recency (only suggest if last search was recent)
        if self.preferences.get("last_search_date"):
            last_search = datetime.fromisoformat(self.preferences["last_search_date"])
            if datetime.now() - last_search > timedelta(days=7):
                return None  # Too old, don't suggest

        # Build contextual suggestion
        location = self.preferences["preferred_locations"][0] if self.preferences["preferred_locations"] else "khu vực bạn quan tâm"

        budget_max = self.preferences["budget_range"][1]
        if budget_max >= 1_000_000_000:
            budget_str = f"dưới {budget_max / 1_000_000_000:.1f} tỷ"
        else:
            budget_str = f"dưới {budget_max / 1_000_000:.0f} triệu"

        # ✅ ALLOWED: Contextual nudge based on user behavior
        suggestion = (
            f"Dựa trên lịch sử tìm kiếm của bạn ({location}, {budget_str}), "
            f"tôi có thể gợi ý thêm các bất động sản mới đăng trong 7 ngày qua."
        )

        return suggestion

    def get_search_filters(self) -> Dict:
        """
        Convert preferences to search filters for RAG/DB queries

        Returns:
            Dictionary of filters compatible with property search API
        """
        filters = {}

        if self.preferences.get("budget_range"):
            min_price, max_price = self.preferences["budget_range"]
            if min_price > 0:
                filters["min_price"] = min_price
            if max_price < 999999999999:
                filters["max_price"] = max_price

        if self.preferences.get("preferred_locations"):
            filters["locations"] = self.preferences["preferred_locations"]

        if self.preferences.get("property_types"):
            filters["property_types"] = self.preferences["property_types"]

        if self.preferences.get("bedrooms_range"):
            min_bed, max_bed = self.preferences["bedrooms_range"]
            filters["min_bedrooms"] = min_bed
            filters["max_bedrooms"] = max_bed

        if self.preferences.get("area_range"):
            min_area, max_area = self.preferences["area_range"]
            filters["min_area"] = min_area
            if max_area < 999999:
                filters["max_area"] = max_area

        if self.preferences.get("key_features"):
            filters["features"] = self.preferences["key_features"]

        return filters

    def to_dict(self) -> Dict:
        """Export preferences as dictionary"""
        return self.preferences.copy()

    def reset(self):
        """Clear all preferences"""
        self.preferences = self._load_preferences()
        if self.redis_client:
            self.redis_client.delete(self.redis_key)


# Example usage
if __name__ == "__main__":
    # Simulate user conversation
    context = ConversationContext("user_123")

    # First query
    context.learn_from_query("tìm căn hộ 2 phòng ngủ dưới 5 tỷ quận 1 có hồ bơi")
    print("After query 1:", json.dumps(context.to_dict(), indent=2, ensure_ascii=False))

    # Second query (refine search)
    context.learn_from_query("có view đẹp không")
    print("\nAfter query 2:", json.dumps(context.to_dict(), indent=2, ensure_ascii=False))

    # Generate suggestion
    suggestion = context.generate_proactive_suggestion()
    print(f"\nProactive suggestion: {suggestion}")

    # Get filters for search
    filters = context.get_search_filters()
    print(f"\nSearch filters: {json.dumps(filters, indent=2, ensure_ascii=False)}")

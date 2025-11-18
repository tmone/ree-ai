"""
Simple Regex Extractor with Hardcoded Patterns
NO PostgreSQL dependency - uses patterns from multilingual_keywords.json
Provides guaranteed baseline extraction for common patterns
"""
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional


class SimpleRegexExtractor:
    """
    Regex-based attribute extractor with hardcoded patterns.
    Serves as Layer 1 baseline extraction before LLM.
    """

    def __init__(self):
        """Initialize with hardcoded patterns from master data"""
        self._load_patterns()

    def _load_patterns(self):
        """Load patterns from multilingual_keywords.json"""
        # Load keywords file
        keywords_path = Path(__file__).parent.parent.parent / "shared" / "data" / "multilingual_keywords.json"
        with open(keywords_path, 'r', encoding='utf-8') as f:
            keywords = json.load(f)

        # Build district patterns
        self.district_patterns = []
        district_config = keywords.get("district_abbreviations", {}).get("patterns", {})
        for abbr in district_config.keys():
            # Prevent matching digits before abbreviation (e.g., "10Q1" shouldn't match)
            if re.match(r'^[QD]\d+$', abbr):
                self.district_patterns.append(f'(?<![0-9])\\b{re.escape(abbr)}\\b')
            else:
                self.district_patterns.append(f'\\b{re.escape(abbr)}\\b')

        # Hardcoded property type patterns
        self.property_type_patterns = [
            (r'\b(apartment|căn hộ|can ho|condo)\b', 'apartment'),
            (r'\b(villa|biệt thự|biet thu)\b', 'villa'),
            (r'\b(townhouse|nhà phố|nha pho|shophouse)\b', 'townhouse'),
            (r'\b(house|nhà|nha)\b', 'house'),
            (r'\b(land|đất|dat)\b', 'land'),
            (r'\b(office|văn phòng|van phong)\b', 'office'),
        ]

        # Listing type patterns
        self.listing_type_patterns = [
            (r'\b(cho thuê|cho thue|thuê|thue|rent|rental|for rent)\b', 'rent'),
            (r'\b(bán|ban|cần bán|can ban|sale|sell|for sale)\b', 'sale'),
        ]

        # Price patterns
        self.price_patterns = [
            # Zero price
            (r'\b(price|giá|gia)\s*:?\s*0\b', 0),
            # Price with "tỷ" (billion VND)
            (r'(\d+(?:\.\d+)?)\s*(?:tỷ|ty|B|billion)', lambda m: float(m.group(1)) * 1_000_000_000),
            # Price with "triệu" (million VND)
            (r'(\d+(?:\.\d+)?)\s*(?:triệu|trieu|M|million)', lambda m: float(m.group(1)) * 1_000_000),
            # Price range - under
            (r'(?:under|dưới|duoi|below)\s*(\d+(?:\.\d+)?)\s*(?:tỷ|ty|B|billion)',
             lambda m: {'max_price': float(m.group(1)) * 1_000_000_000}),
            (r'(?:under|dưới|duoi|below)\s*(\d+(?:\.\d+)?)\s*(?:triệu|trieu|M|million)',
             lambda m: {'max_price': float(m.group(1)) * 1_000_000}),
            # Price range - over
            (r'(?:over|trên|tren|above)\s*(\d+(?:\.\d+)?)\s*(?:tỷ|ty|B|billion)',
             lambda m: {'min_price': float(m.group(1)) * 1_000_000_000}),
            (r'(?:over|trên|tren|above)\s*(\d+(?:\.\d+)?)\s*(?:triệu|trieu|M|million)',
             lambda m: {'min_price': float(m.group(1)) * 1_000_000}),
        ]

        # Bedroom patterns
        self.bedroom_patterns = [
            (r'(\d+)\s*(?:BR|bedroom|bedrooms|phòng ngủ|phong ngu|PN)\b', lambda m: int(m.group(1))),
        ]

        # Bathroom patterns
        self.bathroom_patterns = [
            (r'(\d+)\s*(?:bathroom|bathrooms|phòng tắm|phong tam|WC|toilet)\b', lambda m: int(m.group(1))),
        ]

        # Area patterns
        self.area_patterns = [
            (r'(\d+(?:\.\d+)?)\s*(?:m2|m²|sqm|square meter)', lambda m: float(m.group(1))),
        ]

    def extract(self, query: str) -> Dict[str, Any]:
        """
        Extract entities using regex patterns

        Returns:
            Dict with extracted entities
        """
        entities = {}

        # Extract district
        district = self._extract_district(query)
        if district:
            entities['district'] = district

        # Extract property type
        property_type = self._extract_property_type(query)
        if property_type:
            entities['property_type'] = property_type

        # Extract listing type
        listing_type = self._extract_listing_type(query)
        if listing_type:
            entities['listing_type'] = listing_type

        # Extract price
        price_info = self._extract_price(query)
        if price_info:
            entities.update(price_info)

        # Extract bedrooms
        bedrooms = self._extract_bedrooms(query)
        if bedrooms:
            entities['bedrooms'] = bedrooms

        # Extract bathrooms
        bathrooms = self._extract_bathrooms(query)
        if bathrooms:
            entities['bathrooms'] = bathrooms

        # Extract area
        area = self._extract_area(query)
        if area:
            entities['area'] = area

        return entities

    def _extract_district(self, query: str) -> Optional[str]:
        """Extract district from query"""
        for pattern in self.district_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                matched_text = match.group(0)
                # Normalize: Q7 -> District 7, Quận 7 -> District 7
                if re.match(r'^[QD](\d+)$', matched_text, re.IGNORECASE):
                    num = re.search(r'\d+', matched_text).group()
                    return f"District {num}"
                elif 'quận' in matched_text.lower() or 'quan' in matched_text.lower():
                    num = re.search(r'\d+', matched_text)
                    if num:
                        return f"District {num.group()}"
                return matched_text.title()
        return None

    def _extract_property_type(self, query: str) -> Optional[str]:
        """Extract property type from query"""
        for pattern, prop_type in self.property_type_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return prop_type
        return None

    def _extract_listing_type(self, query: str) -> Optional[str]:
        """Extract listing type (rent/sale) from query"""
        for pattern, listing_type in self.listing_type_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return listing_type
        return None

    def _extract_price(self, query: str) -> Dict[str, Any]:
        """Extract price information from query"""
        price_info = {}

        for pattern, handler in self.price_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if callable(handler):
                    result = handler(match)
                    if isinstance(result, dict):
                        price_info.update(result)
                    else:
                        price_info['price'] = result
                else:
                    price_info['price'] = handler
                break  # Take first match

        return price_info

    def _extract_bedrooms(self, query: str) -> Optional[int]:
        """Extract number of bedrooms"""
        for pattern, handler in self.bedroom_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return handler(match)
        return None

    def _extract_bathrooms(self, query: str) -> Optional[int]:
        """Extract number of bathrooms"""
        for pattern, handler in self.bathroom_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return handler(match)
        return None

    def _extract_area(self, query: str) -> Optional[float]:
        """Extract area in square meters"""
        for pattern, handler in self.area_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return handler(match)
        return None

    def get_confidence(self, entities: Dict[str, Any]) -> float:
        """
        Calculate extraction confidence based on number of entities

        Args:
            entities: Extracted entities dict

        Returns:
            Confidence score 0.0-1.0
        """
        if not entities:
            return 0.0

        # Base confidence on number of entities extracted
        entity_count = len(entities)

        if entity_count >= 4:
            return 0.95
        elif entity_count == 3:
            return 0.85
        elif entity_count == 2:
            return 0.75
        elif entity_count == 1:
            return 0.65
        else:
            return 0.5

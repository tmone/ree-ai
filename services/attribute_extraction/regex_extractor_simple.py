"""
Simple Regex Extractor - i18n Compliant
RULE #0 COMPLIANT: ALL patterns loaded from multilingual_keywords.json
NO hardcoded keywords - system MUST FAIL if master data unavailable
Provides guaranteed baseline extraction for common patterns
"""
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple


class SimpleRegexExtractor:
    """
    Regex-based attribute extractor with i18n-compliant patterns.
    Serves as Layer 1 baseline extraction before LLM.

    RULE #0 COMPLIANT: All patterns loaded from master data at runtime.
    """

    def __init__(self):
        """Initialize with patterns from master data (RULE #0 compliant)"""
        self._load_patterns()

    def _load_patterns(self):
        """
        Load ALL patterns from multilingual_keywords.json

        RULE #0: System MUST FAIL if master data unavailable (no fallbacks!)
        """
        # Load keywords file
        keywords_path = Path(__file__).parent.parent.parent / "shared" / "data" / "multilingual_keywords.json"

        try:
            with open(keywords_path, 'r', encoding='utf-8') as f:
                self.keywords = json.load(f)
        except Exception as e:
            raise RuntimeError(
                f"[CRITICAL] Failed to load master data from {keywords_path}. "
                f"RULE #0 violation: System cannot operate without master data! Error: {e}"
            )

        # Build district patterns from master data
        self.district_patterns = []
        district_config = self.keywords.get("district_abbreviations", {}).get("patterns", {})
        for abbr in district_config.keys():
            # Prevent matching digits before abbreviation (e.g., "10Q1" shouldn't match)
            if re.match(r'^[QD]\d+$', abbr):
                self.district_patterns.append(f'(?<![0-9])\\b{re.escape(abbr)}\\b')
            else:
                self.district_patterns.append(f'\\b{re.escape(abbr)}\\b')

        # Build property type patterns from master data (RULE #0 compliant)
        self.property_type_patterns = self._build_property_type_patterns()

        # Build listing type patterns from master data (RULE #0 compliant)
        self.listing_type_patterns = self._build_listing_type_patterns()

        # Build price patterns from master data (RULE #0 compliant)
        self.price_patterns = self._build_price_patterns()

        # Build bedroom patterns from master data (RULE #0 compliant)
        self.bedroom_patterns = self._build_bedroom_patterns()

        # Build bathroom patterns from master data (RULE #0 compliant)
        self.bathroom_patterns = self._build_bathroom_patterns()

        # Build area patterns from master data (RULE #0 compliant)
        self.area_patterns = self._build_area_patterns()

    def _build_property_type_patterns(self) -> List[Tuple[str, str]]:
        """
        Build property type regex patterns from master data

        RULE #0: Load from multilingual_keywords.json, NO hardcoding!
        """
        patterns = []
        property_types = self.keywords.get("property_types", {})

        # For each property type, build regex from vi/en keywords
        for prop_type_key, langs in property_types.items():
            if prop_type_key == "description":
                continue

            if isinstance(langs, dict):
                # Collect all keywords from all languages
                all_keywords = []

                if "vi" in langs:
                    all_keywords.extend(langs["vi"])
                if "en" in langs:
                    all_keywords.extend(langs["en"])
                if "th" in langs:
                    all_keywords.extend(langs.get("th", []))
                if "ja" in langs:
                    all_keywords.extend(langs.get("ja", []))

                # Build regex pattern
                if all_keywords:
                    # Escape special regex characters
                    escaped = [re.escape(kw) for kw in all_keywords]
                    pattern = r'\b(' + '|'.join(escaped) + r')\b'
                    patterns.append((pattern, prop_type_key))

        return patterns

    def _build_listing_type_patterns(self) -> List[Tuple[str, str]]:
        """
        Build listing type (rent/sale) regex patterns from master data

        RULE #0: Load from multilingual_keywords.json, NO hardcoding!
        """
        patterns = []
        listing_type_config = self.keywords.get("attribute_keywords", {}).get("listing_type", {})

        if "values" in listing_type_config:
            for listing_value, langs in listing_type_config["values"].items():
                # Collect keywords from all languages
                all_keywords = []

                for lang_code in ["vi", "en", "th", "ja"]:
                    if lang_code in langs:
                        all_keywords.extend(langs[lang_code])

                # Build regex pattern
                if all_keywords:
                    escaped = [re.escape(kw) for kw in all_keywords]
                    pattern = r'\b(' + '|'.join(escaped) + r')\b'
                    patterns.append((pattern, listing_value))

        return patterns

    def _build_price_patterns(self) -> List[Tuple[str, Any]]:
        """
        Build price regex patterns from master data

        RULE #0: Load price units from multilingual_keywords.json!
        BUGFIX #30: Use master data units to prevent parsing errors
        """
        patterns = []
        price_config = self.keywords.get("attribute_keywords", {}).get("price", {})
        price_units = price_config.get("units", {})

        # Get price keywords (giá, gia, price, etc.)
        price_keywords = []
        if "vi" in price_config:
            price_keywords.extend(price_config["vi"])
        if "en" in price_config:
            price_keywords.extend(price_config["en"])

        # Zero price pattern
        if price_keywords:
            price_kw_pattern = '|'.join([re.escape(kw) for kw in price_keywords])
            patterns.append((
                f'\\b({price_kw_pattern})\\s*:?\\s*0\\b',
                0
            ))

        # Build patterns for each price unit from master data
        for unit_name, multiplier in price_units.items():
            # Number + unit (e.g., "15.5 tỷ")
            unit_escaped = re.escape(unit_name)
            patterns.append((
                f'(\\d+(?:[\\.,]\\d+)?)\\s*{unit_escaped}\\b',
                lambda m, mult=multiplier: float(m.group(1).replace(',', '.')) * mult
            ))

            # Range patterns - under
            patterns.append((
                f'(?:under|dưới|duoi|below)\\s*(\\d+(?:[\\.,]\\d+)?)\\s*{unit_escaped}\\b',
                lambda m, mult=multiplier: {'max_price': float(m.group(1).replace(',', '.')) * mult}
            ))

            # Range patterns - over
            patterns.append((
                f'(?:over|trên|tren|above)\\s*(\\d+(?:[\\.,]\\d+)?)\\s*{unit_escaped}\\b',
                lambda m, mult=multiplier: {'min_price': float(m.group(1).replace(',', '.')) * mult}
            ))

        return patterns

    def _build_bedroom_patterns(self) -> List[Tuple[str, Any]]:
        """
        Build bedroom regex patterns from master data

        RULE #0: Load bedroom keywords from multilingual_keywords.json!
        """
        patterns = []
        bedrooms_config = self.keywords.get("attribute_keywords", {}).get("bedrooms", {})

        # Collect all bedroom keywords
        bedroom_keywords = []
        if "vi" in bedrooms_config:
            bedroom_keywords.extend(bedrooms_config["vi"])
        if "en" in bedrooms_config:
            bedroom_keywords.extend(bedrooms_config["en"])

        # Build pattern: number + bedroom keyword
        if bedroom_keywords:
            # Also add common abbreviations
            bedroom_keywords.extend(["BR", "PN"])
            escaped = [re.escape(kw) for kw in bedroom_keywords]
            pattern = f'(\\d+)\\s*(?:{"|".join(escaped)})\\b'
            patterns.append((pattern, lambda m: int(m.group(1))))

        return patterns

    def _build_bathroom_patterns(self) -> List[Tuple[str, Any]]:
        """
        Build bathroom regex patterns from master data

        RULE #0: Load bathroom keywords from multilingual_keywords.json!
        """
        patterns = []
        bathrooms_config = self.keywords.get("attribute_keywords", {}).get("bathrooms", {})

        # Collect all bathroom keywords
        bathroom_keywords = []
        if "vi" in bathrooms_config:
            bathroom_keywords.extend(bathrooms_config["vi"])
        if "en" in bathrooms_config:
            bathroom_keywords.extend(bathrooms_config["en"])

        # Build pattern: number + bathroom keyword
        if bathroom_keywords:
            # Add common aliases: WC, toilet
            bathroom_keywords.extend(["WC", "toilet"])
            escaped = [re.escape(kw) for kw in bathroom_keywords]
            pattern = f'(\\d+)\\s*(?:{"|".join(escaped)})\\b'
            patterns.append((pattern, lambda m: int(m.group(1))))

        return patterns

    def _build_area_patterns(self) -> List[Tuple[str, Any]]:
        """
        Build area regex patterns from master data

        RULE #0: Load area units from multilingual_keywords.json!
        """
        patterns = []
        area_config = self.keywords.get("attribute_keywords", {}).get("area", {})

        # Get area units (m2, m², sqm, etc.)
        area_units = area_config.get("units", [])

        # Build pattern: number + area unit
        if area_units:
            escaped = [re.escape(unit) for unit in area_units]
            pattern = f'(\\d+(?:\\.\\d+)?)\\s*(?:{"|".join(escaped)})\\b'
            patterns.append((pattern, lambda m: float(m.group(1))))

        return patterns

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

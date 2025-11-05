"""
Vietnamese NLP Pre-processing for Property Attribute Extraction
Uses rule-based extraction + regex patterns + MASTER DATA for high-accuracy entity detection

UPDATED: Now uses centralized master data instead of hard-coded values
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from shared.utils.logger import setup_logger, LogEmoji
from shared.master_data import get_district_master, get_property_type_master, get_amenity_master

logger = setup_logger(__name__)


class VietnameseNLPProcessor:
    """
    Pre-process Vietnamese property queries with rule-based extraction.

    NOW USES MASTER DATA for:
    - District normalization (from DistrictMaster)
    - Property type normalization (from PropertyTypeMaster)
    - Amenity extraction (from AmenityMaster)

    This layer extracts obvious entities using regex patterns and normalization rules,
    providing high-confidence hints to the LLM layer.
    """

    def __init__(self):
        """Initialize NLP processor with master data"""
        # Load master data
        self.district_master = get_district_master()
        self.property_type_master = get_property_type_master()
        self.amenity_master = get_amenity_master()

        logger.info(f"{LogEmoji.INFO} Initialized Vietnamese NLP Processor with Master Data")
        logger.info(f"{LogEmoji.INFO} Loaded {len(self.district_master.districts)} districts")
        logger.info(f"{LogEmoji.INFO} Loaded {len(self.property_type_master.PROPERTY_TYPES)} property types")
        logger.info(f"{LogEmoji.INFO} Loaded {len(self.amenity_master.AMENITIES)} amenities")

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text using rule-based NLP.

        Args:
            text: Input query or property description

        Returns:
            Dictionary of extracted entities with confidence scores
        """
        text_lower = text.lower()
        entities = {}

        # Extract different entity types
        entities.update(self._extract_location(text, text_lower))
        entities.update(self._extract_property_type(text_lower))
        entities.update(self._extract_numbers(text, text_lower))
        entities.update(self._extract_price(text, text_lower))
        entities.update(self._extract_amenities(text_lower))
        entities.update(self._extract_project_name(text, text_lower))
        entities.update(self._extract_direction(text_lower))

        logger.info(f"{LogEmoji.SUCCESS} NLP extracted {len(entities)} entities")
        logger.debug(f"NLP entities: {entities}")

        return entities

    def _extract_location(self, text: str, text_lower: str) -> Dict[str, Any]:
        """Extract and normalize location entities using DistrictMaster"""
        location = {}

        # Use DistrictMaster for extraction
        district_match = self.district_master.extract_from_text(text)
        if district_match:
            matched_text, district_obj = district_match
            location['district'] = district_obj.standard_name
            logger.debug(f"Extracted district: {district_obj.standard_name} (from: {matched_text})")

            # Also extract popular area if mentioned
            for popular_area in district_obj.popular_areas:
                if popular_area.lower() in text_lower:
                    location['area'] = popular_area
                    logger.debug(f"Extracted popular area: {popular_area}")
                    break

        # Extract ward (phường)
        ward_patterns = [
            r'phường\s+(\d+)',
            r'p\.?\s*(\d+)',
            r'phường\s+([\w\s]+?)(?:\s+quận|\s+q\.|\s*,|$)',
        ]
        for pattern in ward_patterns:
            match = re.search(pattern, text_lower)
            if match:
                location['ward'] = match.group(1).strip().title()
                break

        # Extract street (đường)
        street_patterns = [
            r'đường\s+([\w\s]+?)(?:\s+quận|\s+q\.|\s*,|$)',
            r'đ\.?\s+([\w\s]+?)(?:\s+quận|\s+q\.|\s*,|$)',
        ]
        for pattern in street_patterns:
            match = re.search(pattern, text_lower)
            if match:
                street = match.group(1).strip().title()
                if len(street) > 2:  # Avoid single letters
                    location['street'] = street
                    break

        return location

    def _extract_property_type(self, text_lower: str) -> Dict[str, str]:
        """Extract property type using PropertyTypeMaster"""
        # Try each property type from master data
        for prop_type_obj in self.property_type_master.PROPERTY_TYPES:
            # Check standard name
            if prop_type_obj.standard_name in text_lower:
                logger.debug(f"Extracted property_type: {prop_type_obj.standard_name}")
                return {'property_type': prop_type_obj.standard_name}

            # Check aliases
            for alias in prop_type_obj.aliases:
                if re.search(rf'\b{re.escape(alias)}\b', text_lower):
                    logger.debug(f"Extracted property_type: {prop_type_obj.standard_name} (from alias: {alias})")
                    return {'property_type': prop_type_obj.standard_name}

        return {}

    def _extract_numbers(self, text: str, text_lower: str) -> Dict[str, Any]:
        """Extract numeric attributes (bedrooms, bathrooms, area, floors)"""
        numbers = {}

        # Bedrooms
        bedroom_patterns = [
            (r'(\d+)\s*(?:phòng\s+ngủ|pn|bedroom)', 'bedrooms'),
            (r'(\d+)\s*pn\b', 'bedrooms'),
        ]
        for pattern, key in bedroom_patterns:
            match = re.search(pattern, text_lower)
            if match:
                numbers[key] = int(match.group(1))
                logger.debug(f"Extracted {key}: {numbers[key]}")
                break

        # Bathrooms
        bathroom_patterns = [
            (r'(\d+)\s*(?:phòng\s+tắm|wc|toilet|bathroom)', 'bathrooms'),
            (r'(\d+)\s*wc\b', 'bathrooms'),
        ]
        for pattern, key in bathroom_patterns:
            match = re.search(pattern, text_lower)
            if match:
                numbers[key] = int(match.group(1))
                logger.debug(f"Extracted {key}: {numbers[key]}")
                break

        # Area (diện tích)
        area_patterns = [
            r'(\d+(?:\.\d+)?)\s*m[²2]',
            r'diện\s+tích[:\s]+(\d+(?:\.\d+)?)',
            r'dt[:\s]+(\d+(?:\.\d+)?)',
            r'(\d+)\s*x\s*(\d+)',  # Width x depth
        ]

        for pattern in area_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if len(match.groups()) == 2:
                    # Width x depth - calculate area
                    width = float(match.group(1))
                    depth = float(match.group(2))
                    numbers['area'] = width * depth
                    numbers['facade_width'] = width
                    logger.debug(f"Extracted area: {numbers['area']} (from {width}x{depth})")
                else:
                    numbers['area'] = float(match.group(1))
                    logger.debug(f"Extracted area: {numbers['area']}")
                break

        # Floors (số tầng)
        floor_patterns = [
            r'(\d+)\s*tầng',
            r'(\d+)\s*lầu',
        ]
        for pattern in floor_patterns:
            match = re.search(pattern, text_lower)
            if match:
                numbers['floors'] = int(match.group(1))
                logger.debug(f"Extracted floors: {numbers['floors']}")
                break

        return numbers

    def _extract_price(self, text: str, text_lower: str) -> Dict[str, Any]:
        """Extract price with normalization to VND"""
        price_info = {}

        # Price patterns with units
        price_patterns = [
            # "dưới X tỷ", "dưới X triệu"
            (r'dưới\s+(\d+(?:\.\d+)?)\s*tỷ', 'max_price', 1_000_000_000),
            (r'dưới\s+(\d+(?:\.\d+)?)\s*triệu', 'max_price', 1_000_000),

            # "trên X tỷ", "trên X triệu"
            (r'trên\s+(\d+(?:\.\d+)?)\s*tỷ', 'min_price', 1_000_000_000),
            (r'trên\s+(\d+(?:\.\d+)?)\s*triệu', 'min_price', 1_000_000),

            # "từ X đến Y tỷ"
            (r'từ\s+(\d+(?:\.\d+)?)\s*đến\s+(\d+(?:\.\d+)?)\s*tỷ', 'range', 1_000_000_000),
            (r'từ\s+(\d+(?:\.\d+)?)\s*đến\s+(\d+(?:\.\d+)?)\s*triệu', 'range', 1_000_000),

            # "khoảng X tỷ", "khoảng X triệu"
            (r'khoảng\s+(\d+(?:\.\d+)?)\s*tỷ', 'price', 1_000_000_000),
            (r'khoảng\s+(\d+(?:\.\d+)?)\s*triệu', 'price', 1_000_000),

            # "X tỷ", "X triệu"
            (r'(\d+(?:\.\d+)?)\s*tỷ', 'price', 1_000_000_000),
            (r'(\d+(?:\.\d+)?)\s*triệu(?:/tháng)?', 'price', 1_000_000),
        ]

        for pattern, price_type, multiplier in price_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if price_type == 'range':
                    # From X to Y
                    min_val = float(match.group(1)) * multiplier
                    max_val = float(match.group(2)) * multiplier
                    price_info['min_price'] = min_val
                    price_info['max_price'] = max_val
                    logger.debug(f"Extracted price range: {min_val:,.0f} - {max_val:,.0f} VND")
                else:
                    # Single price or min/max
                    value = float(match.group(1)) * multiplier
                    price_info[price_type] = value
                    logger.debug(f"Extracted {price_type}: {value:,.0f} VND")
                break

        return price_info

    def _extract_amenities(self, text_lower: str) -> Dict[str, bool]:
        """Extract boolean amenities using AmenityMaster"""
        # Use AmenityMaster's extract_from_text method
        amenities = self.amenity_master.extract_from_text(text_lower)

        if amenities:
            logger.debug(f"Extracted amenities: {list(amenities.keys())}")

        return amenities

    def _extract_project_name(self, text: str, text_lower: str) -> Dict[str, str]:
        """Extract known project names"""
        for project in self.KNOWN_PROJECTS:
            if project in text_lower:
                # Get the original case from text
                match = re.search(re.escape(project), text, re.IGNORECASE)
                if match:
                    project_name = match.group(0).title()
                    logger.debug(f"Extracted project: {project_name}")
                    return {'project_name': project_name}
        return {}

    def _extract_direction(self, text_lower: str) -> Dict[str, str]:
        """Extract house/balcony direction"""
        directions = {
            'đông': 'Đông',
            'tây': 'Tây',
            'nam': 'Nam',
            'bắc': 'Bắc',
            'đông nam': 'Đông Nam',
            'đông bắc': 'Đông Bắc',
            'tây nam': 'Tây Nam',
            'tây bắc': 'Tây Bắc',
        }

        # Extract main direction
        for direction_vn, direction_standard in directions.items():
            pattern = rf'\bhướng\s+{direction_vn}\b'
            if re.search(pattern, text_lower):
                logger.debug(f"Extracted direction: {direction_standard}")
                return {'direction': direction_standard}

        return {}

    def get_extraction_confidence(self, entities: Dict[str, Any]) -> float:
        """
        Calculate confidence score for NLP extraction.

        Higher confidence for more entities and more specific entities.
        """
        if not entities:
            return 0.0

        # Weight different entity types
        weights = {
            'district': 0.2,
            'property_type': 0.15,
            'price': 0.15,
            'min_price': 0.1,
            'max_price': 0.1,
            'bedrooms': 0.1,
            'area': 0.1,
            'project_name': 0.1,
        }

        confidence = 0.0
        for entity, weight in weights.items():
            if entity in entities:
                confidence += weight

        # Bonus for having multiple entities
        if len(entities) >= 5:
            confidence += 0.1
        elif len(entities) >= 3:
            confidence += 0.05

        return min(confidence, 1.0)


# Convenience function
def extract_entities(text: str) -> Tuple[Dict[str, Any], float]:
    """
    Extract entities from text and return with confidence score.

    Returns:
        Tuple of (entities dict, confidence score)
    """
    processor = VietnameseNLPProcessor()
    entities = processor.extract_entities(text)
    confidence = processor.get_extraction_confidence(entities)
    return entities, confidence

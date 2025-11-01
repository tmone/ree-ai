"""
Vietnamese NLP Pre-processing for Property Attribute Extraction
Uses rule-based extraction + regex patterns for high-accuracy entity detection
"""
import re
from typing import Dict, Any, List, Optional, Tuple
from shared.utils.logger import setup_logger, LogEmoji

logger = setup_logger(__name__)


class VietnameseNLPProcessor:
    """
    Pre-process Vietnamese property queries with rule-based extraction.

    This layer extracts obvious entities using regex patterns and normalization rules,
    providing high-confidence hints to the LLM layer.
    """

    # Location normalization mappings
    DISTRICT_PATTERNS = {
        r'\bq\.?\s*(\d+)\b': r'Quận \1',
        r'\bquận\s*(\d+)\b': r'Quận \1',
        r'\bquận\s+bình\s+thạnh\b': 'Quận Bình Thạnh',
        r'\bbình\s+thạnh\b': 'Quận Bình Thạnh',
        r'\bthủ\s+đức\b': 'Thành phố Thủ Đức',
        r'\btân\s+bình\b': 'Quận Tân Bình',
        r'\btân\s+phú\b': 'Quận Tân Phú',
        r'\bgò\s+vấp\b': 'Quận Gò Vấp',
        r'\bphú\s+nhuận\b': 'Quận Phú Nhuận',
    }

    # Property type mappings
    PROPERTY_TYPES = {
        r'\bcăn\s+hộ\b': 'căn hộ',
        r'\bchung\s+cư\b': 'chung cư',
        r'\bapartment\b': 'căn hộ',
        r'\bnhà\s+phố\b': 'nhà phố',
        r'\btownhouse\b': 'nhà phố',
        r'\bbiệt\s+thự\b': 'biệt thự',
        r'\bvilla\b': 'biệt thự',
        r'\bđất\b': 'đất',
        r'\bđất\s+nền\b': 'đất',
        r'\boffice\b': 'văn phòng',
        r'\bvăn\s+phòng\b': 'văn phòng',
        r'\bmặt\s+bằng\b': 'mặt bằng',
    }

    # Project name patterns
    KNOWN_PROJECTS = [
        'vinhomes', 'masteri', 'the manor', 'the sun avenue',
        'estella heights', 'gateway', 'sala', 'sarimi',
        'park riverside', 'diamond island', 'vista verde',
        'feliz en vista', 'palm heights', 'eco green'
    ]

    def __init__(self):
        """Initialize NLP processor"""
        logger.info(f"{LogEmoji.INFO} Initialized Vietnamese NLP Processor")

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
        """Extract and normalize location entities (district, ward, street)"""
        location = {}

        # Extract district with normalization
        for pattern, replacement in self.DISTRICT_PATTERNS.items():
            match = re.search(pattern, text_lower)
            if match:
                if '\\1' in replacement:
                    # Pattern with capture group
                    district = re.sub(pattern, replacement, match.group(0))
                else:
                    # Direct replacement
                    district = replacement
                location['district'] = district
                logger.debug(f"Extracted district: {district}")
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
        """Extract property type"""
        for pattern, prop_type in self.PROPERTY_TYPES.items():
            if re.search(pattern, text_lower):
                logger.debug(f"Extracted property_type: {prop_type}")
                return {'property_type': prop_type}
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
        """Extract boolean amenities"""
        amenities = {}

        amenity_patterns = {
            'parking': [r'chỗ\s+đậu\s+xe', r'garage', r'bãi\s+xe', r'parking'],
            'elevator': [r'thang\s+máy', r'elevator', r'lift'],
            'swimming_pool': [r'hồ\s+bơi', r'pool', r'bể\s+bơi'],
            'gym': [r'phòng\s+gym', r'gym', r'fitness'],
            'security': [r'bảo\s+vệ\s+24/7', r'security', r'an\s+ninh'],
            'balcony': [r'ban\s+công', r'balcony'],
            'garden': [r'sân\s+vườn', r'vườn', r'garden'],
        }

        for amenity, patterns in amenity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    amenities[amenity] = True
                    logger.debug(f"Extracted amenity: {amenity}")
                    break

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

"""
Multilingual Translation Mapper for REE AI

This module provides bidirectional translation between user languages (Vietnamese, Chinese, etc.)
and English master data standard.

CRITICAL DESIGN PRINCIPLE:
- Master data stored in English (database standard)
- User interaction in any language (vi, en, zh)
- Extraction service maps user language → English master data
- Response layer maps English → user language

Example Flow:
  User (Vietnamese): "Tìm căn hộ 2PN quận 7"
  → Extraction: {property_type: "căn hộ", district: "Quận 7"}
  → Mapper: {property_type: "apartment", district: "District 7"}
  → Database: Stored in English
  → Response: Translated back to Vietnamese for user
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class Language(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    VIETNAMESE = "vi"
    CHINESE = "zh"


@dataclass
class TranslationEntry:
    """
    Single translation entry for an entity.

    Example:
        TranslationEntry(
            english="apartment",
            vietnamese="căn hộ",
            chinese="公寓",
            aliases={
                "en": ["condo", "flat"],
                "vi": ["can ho", "chung cư"],
                "zh": ["公寓"]
            }
        )
    """
    english: str  # English standard name (MASTER DATA KEY)
    vietnamese: str  # Vietnamese translation
    chinese: Optional[str] = None  # Chinese translation
    aliases: Dict[str, List[str]] = None  # Additional aliases per language


class PropertyTypeTranslations:
    """Property type translations across languages"""

    TRANSLATIONS = [
        TranslationEntry(
            english="apartment",
            vietnamese="căn hộ",
            chinese="公寓",
            aliases={
                "en": ["condo", "flat", "condominium"],
                "vi": ["can ho", "chung cư", "chung cu"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="villa",
            vietnamese="biệt thự",
            chinese="别墅",
            aliases={
                "en": ["detached house", "standalone house"],
                "vi": ["biet thu", "nhà biệt lập"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="townhouse",
            vietnamese="nhà phố",
            chinese="联排别墅",
            aliases={
                "en": ["row house", "terrace house"],
                "vi": ["nha pho", "nhà liền kề"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="land",
            vietnamese="đất",
            chinese="土地",
            aliases={
                "en": ["vacant land", "plot"],
                "vi": ["dat", "đất nền", "dat nen"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="office",
            vietnamese="văn phòng",
            chinese="办公室",
            aliases={
                "en": ["office space"],
                "vi": ["van phong", "vp"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="commercial",
            vietnamese="mặt bằng",
            chinese="商铺",
            aliases={
                "en": ["commercial space", "shop", "retail space"],
                "vi": ["mat bang", "cửa hàng", "cua hang"],
                "zh": []
            }
        ),
    ]


class DistrictTranslations:
    """District translations for HCMC"""

    TRANSLATIONS = [
        TranslationEntry(
            english="District 1",
            vietnamese="Quận 1",
            chinese="第一郡",
            aliases={
                "en": ["D1", "Dist 1"],
                "vi": ["q1", "q.1", "quan 1"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 2",
            vietnamese="Quận 2",
            chinese="第二郡",
            aliases={
                "en": ["D2", "Dist 2"],
                "vi": ["q2", "q.2", "quan 2"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 3",
            vietnamese="Quận 3",
            chinese="第三郡",
            aliases={
                "en": ["D3", "Dist 3"],
                "vi": ["q3", "q.3", "quan 3"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 4",
            vietnamese="Quận 4",
            chinese="第四郡",
            aliases={
                "en": ["D4"],
                "vi": ["q4", "q.4", "quan 4"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 5",
            vietnamese="Quận 5",
            chinese="第五郡",
            aliases={
                "en": ["D5", "Chinatown"],
                "vi": ["q5", "q.5", "quan 5", "chợ lớn", "cho lon"],
                "zh": ["堤岸"]
            }
        ),
        TranslationEntry(
            english="District 6",
            vietnamese="Quận 6",
            chinese="第六郡",
            aliases={
                "en": ["D6"],
                "vi": ["q6", "q.6", "quan 6"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 7",
            vietnamese="Quận 7",
            chinese="第七郡",
            aliases={
                "en": ["D7", "Phu My Hung"],
                "vi": ["q7", "q.7", "quan 7", "phú mỹ hưng", "phu my hung"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 8",
            vietnamese="Quận 8",
            chinese="第八郡",
            aliases={
                "en": ["D8"],
                "vi": ["q8", "q.8", "quan 8"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 9",
            vietnamese="Quận 9",
            chinese="第九郡",
            aliases={
                "en": ["D9"],
                "vi": ["q9", "q.9", "quan 9"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 10",
            vietnamese="Quận 10",
            chinese="第十郡",
            aliases={
                "en": ["D10"],
                "vi": ["q10", "q.10", "quan 10"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 11",
            vietnamese="Quận 11",
            chinese="第十一郡",
            aliases={
                "en": ["D11"],
                "vi": ["q11", "q.11", "quan 11"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="District 12",
            vietnamese="Quận 12",
            chinese="第十二郡",
            aliases={
                "en": ["D12"],
                "vi": ["q12", "q.12", "quan 12"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="Binh Thanh District",
            vietnamese="Quận Bình Thạnh",
            chinese="平盛郡",
            aliases={
                "en": ["Binh Thanh"],
                "vi": ["bình thạnh", "binh thanh", "quận bình thạnh"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="Tan Binh District",
            vietnamese="Quận Tân Bình",
            chinese="新平郡",
            aliases={
                "en": ["Tan Binh"],
                "vi": ["tân bình", "tan binh", "quận tân bình"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="Phu Nhuan District",
            vietnamese="Quận Phú Nhuận",
            chinese="富润郡",
            aliases={
                "en": ["Phu Nhuan"],
                "vi": ["phú nhuận", "phu nhuan", "quận phú nhuận"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="Thu Duc City",
            vietnamese="Thành phố Thủ Đức",
            chinese="守德市",
            aliases={
                "en": ["Thu Duc", "Thủ Đức"],
                "vi": ["thủ đức", "thu duc", "tp thủ đức", "quận thủ đức"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="Go Vap District",
            vietnamese="Quận Gò Vấp",
            chinese="嘉瓦郡",
            aliases={
                "en": ["Go Vap"],
                "vi": ["gò vấp", "go vap", "quận gò vấp"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="Tan Phu District",
            vietnamese="Quận Tân Phú",
            chinese="新富郡",
            aliases={
                "en": ["Tan Phu"],
                "vi": ["tân phú", "tan phu", "quận tân phú"],
                "zh": []
            }
        ),
    ]


class AmenityTranslations:
    """Common amenity translations"""

    TRANSLATIONS = [
        TranslationEntry(
            english="swimming_pool",
            vietnamese="hồ bơi",
            chinese="游泳池",
            aliases={
                "en": ["pool", "swimming pool"],
                "vi": ["ho boi", "bể bơi", "be boi"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="gym",
            vietnamese="phòng gym",
            chinese="健身房",
            aliases={
                "en": ["fitness center", "gymnasium"],
                "vi": ["gym", "phòng tập gym", "fitness"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="parking",
            vietnamese="chỗ đậu xe",
            chinese="停车场",
            aliases={
                "en": ["garage", "parking space", "car park"],
                "vi": ["bãi đậu xe", "nhà để xe", "garage"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="elevator",
            vietnamese="thang máy",
            chinese="电梯",
            aliases={
                "en": ["lift"],
                "vi": ["thang may", "thang bộ"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="security",
            vietnamese="bảo vệ 24/7",
            chinese="24小时保安",
            aliases={
                "en": ["24/7 security", "security guard"],
                "vi": ["bảo vệ", "bao ve", "an ninh"],
                "zh": []
            }
        ),
        TranslationEntry(
            english="balcony",
            vietnamese="ban công",
            chinese="阳台",
            aliases={
                "en": ["terrace"],
                "vi": ["ban cong", "sân"],
                "zh": []
            }
        ),
    ]


class MultilingualMapper:
    """
    Bidirectional translation mapper between user languages and English master data.

    Usage:
        mapper = MultilingualMapper()

        # Vietnamese → English (for database storage)
        english_type = mapper.to_english("property_type", "căn hộ", source_lang="vi")
        # Returns: "apartment"

        # English → Vietnamese (for user display)
        vietnamese_type = mapper.from_english("property_type", "apartment", target_lang="vi")
        # Returns: "căn hộ"

        # Normalize extracted entities
        normalized = mapper.normalize_entities({
            "property_type": "căn hộ",
            "district": "q7",
            "bedrooms": 2
        }, source_lang="vi")
        # Returns: {
        #   "property_type": "apartment",
        #   "district": "District 7",
        #   "bedrooms": 2
        # }
    """

    def __init__(self):
        """Initialize translation indices"""
        self._build_indices()

    def _build_indices(self):
        """Build lookup indices for fast translation"""
        # Property types
        self.property_type_to_english: Dict[str, str] = {}
        self.property_type_from_english: Dict[str, Dict[str, str]] = {}

        for entry in PropertyTypeTranslations.TRANSLATIONS:
            # Add standard translations
            self.property_type_to_english[entry.english.lower()] = entry.english
            self.property_type_to_english[entry.vietnamese.lower()] = entry.english
            if entry.chinese:
                self.property_type_to_english[entry.chinese.lower()] = entry.english

            # Add aliases
            if entry.aliases:
                for lang, aliases in entry.aliases.items():
                    for alias in aliases:
                        self.property_type_to_english[alias.lower()] = entry.english

            # Build reverse index (English → other languages)
            self.property_type_from_english[entry.english.lower()] = {
                "en": entry.english,
                "vi": entry.vietnamese,
                "zh": entry.chinese or entry.english
            }

        # Districts
        self.district_to_english: Dict[str, str] = {}
        self.district_from_english: Dict[str, Dict[str, str]] = {}

        for entry in DistrictTranslations.TRANSLATIONS:
            # Add standard translations
            self.district_to_english[entry.english.lower()] = entry.english
            self.district_to_english[entry.vietnamese.lower()] = entry.english
            if entry.chinese:
                self.district_to_english[entry.chinese.lower()] = entry.english

            # Add aliases
            if entry.aliases:
                for lang, aliases in entry.aliases.items():
                    for alias in aliases:
                        self.district_to_english[alias.lower()] = entry.english

            # Reverse index
            self.district_from_english[entry.english.lower()] = {
                "en": entry.english,
                "vi": entry.vietnamese,
                "zh": entry.chinese or entry.english
            }

        # Amenities
        self.amenity_to_english: Dict[str, str] = {}
        self.amenity_from_english: Dict[str, Dict[str, str]] = {}

        for entry in AmenityTranslations.TRANSLATIONS:
            self.amenity_to_english[entry.english.lower()] = entry.english
            self.amenity_to_english[entry.vietnamese.lower()] = entry.english
            if entry.chinese:
                self.amenity_to_english[entry.chinese.lower()] = entry.english

            if entry.aliases:
                for lang, aliases in entry.aliases.items():
                    for alias in aliases:
                        self.amenity_to_english[alias.lower()] = entry.english

            self.amenity_from_english[entry.english.lower()] = {
                "en": entry.english,
                "vi": entry.vietnamese,
                "zh": entry.chinese or entry.english
            }

    def to_english(
        self,
        entity_type: str,
        value: str,
        source_lang: Optional[str] = None
    ) -> Optional[str]:
        """
        Convert any language value to English master data standard.

        Args:
            entity_type: Type of entity ("property_type", "district", "amenity")
            value: Value in any language
            source_lang: Source language (optional, auto-detected if not provided)

        Returns:
            English standard name, or None if not found

        Examples:
            to_english("property_type", "căn hộ") → "apartment"
            to_english("district", "q7") → "District 7"
            to_english("amenity", "hồ bơi") → "swimming_pool"
        """
        value_lower = value.lower().strip()

        if entity_type == "property_type":
            return self.property_type_to_english.get(value_lower)
        elif entity_type == "district":
            return self.district_to_english.get(value_lower)
        elif entity_type == "amenity":
            return self.amenity_to_english.get(value_lower)

        return None

    def from_english(
        self,
        entity_type: str,
        value: str,
        target_lang: str = "vi"
    ) -> Optional[str]:
        """
        Convert English master data to target language.

        Args:
            entity_type: Type of entity
            value: English value
            target_lang: Target language ("vi", "zh", "en")

        Returns:
            Translated value

        Examples:
            from_english("property_type", "apartment", "vi") → "căn hộ"
            from_english("district", "District 7", "vi") → "Quận 7"
        """
        value_lower = value.lower().strip()

        if entity_type == "property_type":
            entry = self.property_type_from_english.get(value_lower)
        elif entity_type == "district":
            entry = self.district_from_english.get(value_lower)
        elif entity_type == "amenity":
            entry = self.amenity_from_english.get(value_lower)
        else:
            return None

        if entry:
            return entry.get(target_lang, entry.get("en"))

        return None

    def normalize_entities(
        self,
        entities: Dict,
        source_lang: str = "vi"
    ) -> Dict:
        """
        Normalize all entities to English master data standard.

        This is the MAIN function to call after extraction!

        Args:
            entities: Extracted entities (may contain multilingual values)
            source_lang: Source language of extraction

        Returns:
            Normalized entities with English values

        Example:
            Input (Vietnamese):
                {
                    "property_type": "căn hộ",
                    "district": "q7",
                    "bedrooms": 2,
                    "swimming_pool": true
                }

            Output (English):
                {
                    "property_type": "apartment",
                    "district": "District 7",
                    "bedrooms": 2,
                    "swimming_pool": true
                }
        """
        normalized = {}

        for key, value in entities.items():
            # Skip null/None values
            if value is None:
                continue

            # Only translate string values
            if not isinstance(value, str):
                normalized[key] = value
                continue

            # Try to translate based on key name
            english_value = None

            if "property_type" in key or "type" in key:
                english_value = self.to_english("property_type", value, source_lang)
            elif "district" in key or "area" in key:
                english_value = self.to_english("district", value, source_lang)
            elif key in ["swimming_pool", "gym", "parking", "elevator", "security", "balcony"]:
                # For boolean amenities, check if the Vietnamese text mentions them
                if isinstance(value, bool):
                    normalized[key] = value
                    continue
                english_value = self.to_english("amenity", value, source_lang)

            # Use translated value if found, otherwise keep original
            normalized[key] = english_value if english_value else value

        return normalized

    def translate_entities(
        self,
        entities: Dict,
        target_lang: str = "vi"
    ) -> Dict:
        """
        Translate English entities to target language (for user display).

        Args:
            entities: Entities with English values (from database)
            target_lang: Target language for user display

        Returns:
            Translated entities

        Example:
            Input (English from DB):
                {
                    "property_type": "apartment",
                    "district": "District 7",
                    "bedrooms": 2
                }

            Output (Vietnamese for user):
                {
                    "property_type": "căn hộ",
                    "district": "Quận 7",
                    "bedrooms": 2
                }
        """
        translated = {}

        for key, value in entities.items():
            if not isinstance(value, str):
                translated[key] = value
                continue

            translated_value = None

            if "property_type" in key or "type" in key:
                translated_value = self.from_english("property_type", value, target_lang)
            elif "district" in key:
                translated_value = self.from_english("district", value, target_lang)
            elif key in ["swimming_pool", "gym", "parking", "elevator", "security"]:
                if isinstance(value, bool):
                    translated[key] = value
                    continue
                translated_value = self.from_english("amenity", value, target_lang)

            translated[key] = translated_value if translated_value else value

        return translated


# Singleton instance
_instance: Optional[MultilingualMapper] = None

def get_multilingual_mapper() -> MultilingualMapper:
    """Get singleton instance of MultilingualMapper"""
    global _instance
    if _instance is None:
        _instance = MultilingualMapper()
    return _instance

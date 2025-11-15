"""
Master Data Extraction Service
Complete extraction pipeline with master data integration
"""
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from services.attribute_extraction.language_detector import LanguageDetector
from services.attribute_extraction.fuzzy_matcher import FuzzyMatcher
from services.attribute_extraction.llm_translator import LLMTranslator
from shared.models.attribute_extraction import (
    ExtractionRequest,
    ExtractionResponse,
    RawExtraction,
    MappedAttribute,
    NewAttribute,
    MatchMethod,
    LanguageCode
)
from shared.utils.logger import setup_logger, LogEmoji


class MasterDataExtractor:
    """
    Complete extraction pipeline:
    1. Detect language
    2. Extract attributes with LLM
    3. Match against master data with fuzzy matching
    4. Translate new items to English
    5. Return 3-tier response (raw/mapped/new)
    """

    def __init__(self, core_gateway_url: str, llm_extractor):
        """
        Args:
            core_gateway_url: URL for Core Gateway (for LLM calls)
            llm_extractor: Existing LLM extraction function from main.py
        """
        self.core_gateway_url = core_gateway_url
        self.llm_extractor = llm_extractor  # Reuse existing extraction logic

        # Initialize components
        self.language_detector = LanguageDetector()
        self.fuzzy_matcher = FuzzyMatcher()
        self.llm_translator = LLMTranslator(core_gateway_url)

        self.logger = setup_logger("master_data_extractor")

    async def initialize(self):
        """Initialize all components"""
        await self.fuzzy_matcher.initialize()
        self.logger.info(f"{LogEmoji.SUCCESS} Master data extractor initialized")

    async def extract(self, request: ExtractionRequest) -> ExtractionResponse:
        """
        Main extraction method

        Args:
            request: ExtractionRequest with text and optional language

        Returns:
            ExtractionResponse with raw/mapped/new structure
        """
        start_time = time.time()

        # STEP 1: Detect language
        if request.language:
            detected_lang = self.language_detector.normalize_language_code(request.language)
        else:
            detected_lang = self.language_detector.detect_language(request.text)

        self.logger.info(f"{LogEmoji.INFO} Detected language: {detected_lang}")

        # STEP 2: Extract raw attributes using existing LLM extraction
        raw_entities = await self.llm_extractor(request.text)

        self.logger.info(f"{LogEmoji.SUCCESS} LLM extracted {len(raw_entities)} entities")

        # STEP 3: Separate numeric vs text attributes
        raw_extraction = self._build_raw_extraction(request.text, raw_entities)

        # STEP 4: Match text attributes against master data
        mapped_attrs = []
        new_attrs = []

        for key, value in raw_entities.items():
            if value is None or value == "":
                continue

            # Skip numeric fields (already in raw)
            if key in ["bedrooms", "bathrooms", "area", "price", "min_price", "max_price", "floor", "total_floors"]:
                continue

            # Match against master data
            match_result = await self._match_attribute(
                key, str(value), detected_lang, request.confidence_threshold
            )

            if match_result:
                # Successfully matched
                mapped_attrs.append(match_result)
            else:
                # No match - create new attribute
                new_attr = await self._create_new_attribute(
                    key, str(value), detected_lang, request.text, request.include_suggestions
                )
                new_attrs.append(new_attr)

        # STEP 5: Build response
        processing_time = (time.time() - start_time) * 1000

        response = ExtractionResponse(
            request_language=LanguageCode(detected_lang),
            raw=raw_extraction,
            mapped=mapped_attrs,
            new=new_attrs,
            extraction_timestamp=datetime.now(),
            extractor_version="2.0.0",
            processing_time_ms=processing_time
        )

        self.logger.info(
            f"{LogEmoji.SUCCESS} Extraction complete: "
            f"{len(mapped_attrs)} mapped, {len(new_attrs)} new ({processing_time:.0f}ms)"
        )

        return response

    def _build_raw_extraction(self, text: str, entities: Dict[str, Any]) -> RawExtraction:
        """Build raw extraction from LLM output"""
        raw = RawExtraction(
            text=text,
            bedrooms=entities.get("bedrooms"),
            bathrooms=entities.get("bathrooms"),
            area=entities.get("area"),
            price=entities.get("price"),
            floor=entities.get("floor"),
            total_floors=entities.get("total_floors"),
            title=entities.get("title"),
            description=entities.get("description")
        )
        return raw

    async def _match_attribute(
        self,
        property_name: str,
        value: str,
        source_language: str,
        threshold: float
    ) -> Optional[MappedAttribute]:
        """
        Match an attribute against master data

        Args:
            property_name: Type of attribute (district, property_type, amenity, etc.)
            value: User input value
            source_language: Language code
            threshold: Minimum confidence

        Returns:
            MappedAttribute if match found, None otherwise
        """
        match = None

        # Route to appropriate matcher based on property_name
        if property_name == "district":
            match = await self.fuzzy_matcher.match_district(value, source_language, threshold)
            table = "districts"

        elif property_name == "property_type":
            match = await self.fuzzy_matcher.match_property_type(value, source_language, threshold)
            table = "property_types"

        elif property_name == "amenity":
            match = await self.fuzzy_matcher.match_amenity(value, source_language, threshold)
            table = "amenities"

        elif property_name == "direction":
            match = await self.fuzzy_matcher.match_generic("directions", value, source_language, threshold)
            table = "directions"

        elif property_name == "furniture" or property_name == "furniture_type":
            match = await self.fuzzy_matcher.match_generic("furniture_types", value, source_language, threshold)
            table = "furniture_types"
            property_name = "furniture_type"  # Normalize

        elif property_name == "legal_status":
            match = await self.fuzzy_matcher.match_generic("legal_statuses", value, source_language, threshold)
            table = "legal_statuses"

        elif property_name == "view" or property_name == "view_type":
            match = await self.fuzzy_matcher.match_generic("view_types", value, source_language, threshold)
            table = "view_types"
            property_name = "view_type"  # Normalize

        else:
            # Unknown property type - no matching
            return None

        if not match:
            return None

        # Build MappedAttribute
        mapped_attr = MappedAttribute(
            property_name=property_name,
            table=table,
            id=match["id"],
            value=match["name_en"],  # English canonical
            value_translated=match["name_translated"],  # User's language
            confidence=match["confidence"],
            match_method=MatchMethod(match["match_method"]),
            original_input=value
        )

        return mapped_attr

    async def _create_new_attribute(
        self,
        property_name: str,
        value: str,
        source_language: str,
        context: str,
        include_suggestions: bool
    ) -> NewAttribute:
        """
        Create NewAttribute for unmatched item

        Args:
            property_name: Attribute type
            value: Original value
            source_language: Language code
            context: Full text for context
            include_suggestions: Whether to generate AI suggestions

        Returns:
            NewAttribute
        """
        # Translate to English if not already English
        if source_language != 'en':
            translation = await self.llm_translator.translate_to_english(
                value=value,
                source_language=source_language,
                context=context,
                property_name=property_name
            )
            english_value = translation.get("english", value)
            suggested_translations = translation.get("suggested_translations", {})
            suggested_category = translation.get("category", "unknown")
        else:
            english_value = value
            suggested_translations = {"en": value}
            suggested_category = "unknown"

        # Guess suggested table
        table_mapping = {
            "district": "districts",
            "ward": "wards",
            "property_type": "property_types",
            "amenity": "amenities",
            "direction": "directions",
            "furniture": "furniture_types",
            "furniture_type": "furniture_types",
            "legal_status": "legal_statuses",
            "view": "view_types",
            "view_type": "view_types"
        }
        suggested_table = table_mapping.get(property_name)

        new_attr = NewAttribute(
            property_name=property_name,
            table=None,
            id=None,
            value=english_value,
            value_original=value,
            suggested_table=suggested_table,
            suggested_category=suggested_category if include_suggestions else None,
            suggested_translations=suggested_translations if include_suggestions else {},
            extraction_context=context[:200] if len(context) > 200 else context,  # Truncate
            requires_admin_review=True,
            frequency=1
        )

        return new_attr

    async def close(self):
        """Cleanup resources"""
        await self.fuzzy_matcher.close()
        await self.llm_translator.close()

"""
REE AI Internationalization (i18n) Module

Provides multilingual support for the platform:
1. Multilingual Mapper: User language → English master data (for storage)
2. Translation Layer: English → User language (for display)

Usage:
    from shared.i18n import get_multilingual_mapper

    mapper = get_multilingual_mapper()

    # Normalize extracted entities to English (for DB storage)
    normalized = mapper.normalize_entities({
        "property_type": "căn hộ",
        "district": "q7"
    }, source_lang="vi")

    # Translate English back to user language (for display)
    translated = mapper.translate_entities({
        "property_type": "apartment",
        "district": "District 7"
    }, target_lang="vi")
"""

from shared.i18n.multilingual_mapper import (
    MultilingualMapper,
    get_multilingual_mapper,
    Language,
    TranslationEntry,
    PropertyTypeTranslations,
    DistrictTranslations,
    AmenityTranslations,
)

__all__ = [
    "MultilingualMapper",
    "get_multilingual_mapper",
    "Language",
    "TranslationEntry",
    "PropertyTypeTranslations",
    "DistrictTranslations",
    "AmenityTranslations",
]

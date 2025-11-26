"""
Extraction Response Helpers
Utilities for handling new extraction service response structure
"""
from typing import Dict, Any, List


def build_filters_from_extraction_response(extraction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert extraction response to filters dict

    Supports both formats:
    1. New format: {"raw": {...}, "mapped": [...], "new": [...]}
    2. Legacy format: {"entities": {"bedrooms": 2, "district": "district_7", ...}}

    Returns:
        Filters dict compatible with RAG/DB Gateway
    """
    filters = {}

    # FIRST: Check for direct "entities" format (from enhanced extraction)
    entities = extraction_result.get("entities", {})
    if entities:
        # Direct extraction from entities - already normalized
        numeric_fields = ["bedrooms", "bathrooms", "area", "min_area", "max_area",
                        "price", "min_price", "max_price", "floor", "total_floors"]
        text_fields = ["district", "property_type", "listing_type", "direction", "furniture"]

        for field in numeric_fields:
            if field in entities and entities[field] is not None:
                filters[field] = entities[field]

        for field in text_fields:
            if field in entities and entities[field]:
                value = entities[field]
                # Normalize district format: "district_7" -> "District 7"
                if field == "district" and value.startswith("district_"):
                    value = "District " + value.replace("district_", "")
                filters[field] = value

        return filters

    # FALLBACK: Old format with raw/mapped/new structure
    raw_attrs = extraction_result.get("raw", {})
    mapped_attrs = extraction_result.get("mapped", [])
    new_attrs = extraction_result.get("new", [])

    # 1. Copy numeric fields from raw
    numeric_fields = [
        "bedrooms", "bathrooms", "area", "min_area", "max_area",
        "price", "min_price", "max_price", "floor", "total_floors"
    ]
    for field in numeric_fields:
        if field in raw_attrs and raw_attrs[field] is not None:
            filters[field] = raw_attrs[field]

    # 2. Extract master data attributes from mapped
    for mapped_item in mapped_attrs:
        prop_name = mapped_item.get("property_name")
        master_id = mapped_item.get("id")
        canonical_value = mapped_item.get("value")  # English canonical

        if not prop_name or not master_id:
            continue

        # Map to filter field names
        if prop_name == "district":
            filters["district_id"] = master_id
            filters["district"] = canonical_value

        elif prop_name == "property_type":
            filters["property_type_id"] = master_id
            filters["property_type"] = canonical_value

        elif prop_name == "amenity":
            # Multiple amenities - collect in array
            if "amenity_ids" not in filters:
                filters["amenity_ids"] = []
            filters["amenity_ids"].append(master_id)

        elif prop_name == "view_type":
            if "view_type_ids" not in filters:
                filters["view_type_ids"] = []
            filters["view_type_ids"].append(master_id)

        elif prop_name == "direction":
            filters["direction_id"] = master_id
            filters["direction"] = canonical_value

        elif prop_name == "furniture_type":
            filters["furniture_type_id"] = master_id
            filters["furniture"] = canonical_value

        elif prop_name == "legal_status":
            filters["legal_status_id"] = master_id
            filters["legal_status"] = canonical_value

        else:
            # Generic - use canonical English value
            filters[prop_name] = canonical_value

    return filters


def convert_legacy_extraction_response(legacy_response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert old extraction response format to new format for backward compatibility

    Old format:
        {
            "entities": {
                "bedrooms": 2,
                "district": "Quận 1",
                "property_type": "căn hộ"
            },
            "confidence": 0.85
        }

    New format:
        {
            "raw": {
                "text": "...",
                "bedrooms": 2
            },
            "mapped": [],
            "new": [],
            "confidence": 0.85
        }

    Args:
        legacy_response: Old-format extraction response

    Returns:
        New-format extraction response
    """
    entities = legacy_response.get("entities", {})
    confidence = legacy_response.get("confidence", 0.0)

    # Separate numeric and text attributes
    raw = {}
    unmapped_text_attrs = {}

    numeric_fields = [
        "bedrooms", "bathrooms", "area", "min_area", "max_area",
        "price", "min_price", "max_price", "floor", "total_floors"
    ]

    for key, value in entities.items():
        if key in numeric_fields:
            raw[key] = value
        else:
            # Text attributes go to "unmapped" since we don't have master data IDs
            unmapped_text_attrs[key] = value

    # Create new-format response
    # Note: Legacy responses don't have master data IDs, so everything goes to "raw" or "new"
    new_response = {
        "raw": raw,
        "mapped": [],  # Empty - no master data mapping in legacy
        "new": [
            {
                "property_name": key,
                "value": value,
                "value_original": value,
                "suggested_table": _guess_table_name(key),
                "requires_admin_review": False  # Already extracted, assume valid
            }
            for key, value in unmapped_text_attrs.items()
        ],
        "confidence": confidence,
        "extraction_timestamp": legacy_response.get("extraction_timestamp"),
        "extractor_version": "legacy"
    }

    return new_response


def _guess_table_name(attribute_name: str) -> str:
    """Guess master data table name from attribute name"""
    mapping = {
        "district": "districts",
        "ward": "wards",
        "property_type": "property_types",
        "furniture": "furniture_types",
        "direction": "directions",
        "legal_status": "legal_statuses",
        "view": "view_types"
    }
    return mapping.get(attribute_name, "unknown")


def extract_entities_for_logging(extraction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract a simplified entities dict for logging (backward compatible)

    Useful for logs that expect old format: {"bedrooms": 2, "district": "Quận 1"}

    Args:
        extraction_result: Extraction response (supports both formats)

    Returns:
        Simple entities dict
    """
    # FIRST: Check for direct entities format
    direct_entities = extraction_result.get("entities", {})
    if direct_entities:
        # Return relevant fields for logging
        log_entities = {}
        for key in ["bedrooms", "bathrooms", "area", "price", "district", "property_type"]:
            if key in direct_entities and direct_entities[key]:
                log_entities[key] = direct_entities[key]
        return log_entities

    # FALLBACK: Old raw/mapped format
    entities = {}

    # Add raw numeric fields
    raw = extraction_result.get("raw", {})
    for key in ["bedrooms", "bathrooms", "area", "price", "min_price", "max_price"]:
        if key in raw and raw[key] is not None:
            entities[key] = raw[key]

    # Add mapped attributes (use translated value for readability)
    mapped = extraction_result.get("mapped", [])
    for item in mapped:
        prop_name = item.get("property_name")
        # Use translated value for logs (more readable)
        value = item.get("value_translated") or item.get("value")
        if prop_name and value:
            entities[prop_name] = value

    return entities

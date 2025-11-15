"""
Master Data Validator for Attribute Extraction Service
Uses PostgreSQL master data for normalization and validation
"""
from typing import Dict, Any, List
from shared.database import get_master_data_repository
from shared.models.master_data import ValidationResult
from shared.utils.logger import setup_logger, LogEmoji


class MasterDataValidator:
    """
    Validates and normalizes extracted entities using PostgreSQL master data
    """

    def __init__(self):
        self.repo = None
        self.logger = setup_logger("master_data_validator")

    async def initialize(self):
        """Initialize repository connection"""
        self.repo = await get_master_data_repository()
        self.logger.info(f"{LogEmoji.SUCCESS} Master data validator initialized")

    async def normalize_and_validate(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate all entities using master data

        Returns:
            {
                "normalized_entities": {...},  # Standardized entities
                "validation_results": [...],   # List of validation results
                "warnings": [...],             # List of warnings
                "confidence": 0.85             # Overall confidence
            }
        """
        if not self.repo:
            await self.initialize()

        normalized_entities = {}
        validation_results = []
        warnings = []

        # 1. Normalize district
        if "district" in entities and entities["district"]:
            district_norm = await self.repo.normalize_district(entities["district"])
            if district_norm:
                normalized_entities["district"] = district_norm.normalized_code
                normalized_entities["district_name_vi"] = district_norm.normalized_name_vi
                normalized_entities["district_name_en"] = district_norm.normalized_name_en

                if district_norm.confidence < 1.0:
                    warnings.append(
                        f"District '{entities['district']}' normalized to '{district_norm.normalized_name_vi}' "
                        f"(confidence: {district_norm.confidence:.2f}, match: {district_norm.match_type})"
                    )

                self.logger.info(
                    f"{LogEmoji.SUCCESS} Normalized district: '{entities['district']}' → "
                    f"'{district_norm.normalized_name_vi}' ({district_norm.match_type})"
                )
            else:
                warnings.append(f"District '{entities['district']}' not found in master data")
                normalized_entities["district"] = entities["district"]
                self.logger.warning(
                    f"{LogEmoji.WARNING} District not found: '{entities['district']}'"
                )

        # 2. Normalize property_type
        if "property_type" in entities and entities["property_type"]:
            prop_type_norm = await self.repo.normalize_property_type(entities["property_type"])
            if prop_type_norm:
                normalized_entities["property_type"] = prop_type_norm.normalized_code
                normalized_entities["property_type_name_vi"] = prop_type_norm.normalized_name_vi
                normalized_entities["property_type_name_en"] = prop_type_norm.normalized_name_en

                if prop_type_norm.confidence < 1.0:
                    warnings.append(
                        f"Property type '{entities['property_type']}' normalized to "
                        f"'{prop_type_norm.normalized_name_vi}' (confidence: {prop_type_norm.confidence:.2f})"
                    )

                self.logger.info(
                    f"{LogEmoji.SUCCESS} Normalized property type: '{entities['property_type']}' → "
                    f"'{prop_type_norm.normalized_name_vi}'"
                )
            else:
                warnings.append(f"Property type '{entities['property_type']}' not found in master data")
                normalized_entities["property_type"] = entities["property_type"]
                self.logger.warning(
                    f"{LogEmoji.WARNING} Property type not found: '{entities['property_type']}'"
                )

        # 3. Normalize furniture
        if "furniture" in entities and entities["furniture"]:
            furniture_norm = await self.repo.normalize_furniture(entities["furniture"])
            if furniture_norm:
                normalized_entities["furniture"] = furniture_norm.normalized_code
                self.logger.info(
                    f"{LogEmoji.SUCCESS} Normalized furniture: '{entities['furniture']}' → "
                    f"'{furniture_norm.normalized_code}'"
                )
            else:
                normalized_entities["furniture"] = entities["furniture"]

        # 4. Normalize direction
        if "direction" in entities and entities["direction"]:
            direction_norm = await self.repo.normalize_direction(entities["direction"])
            if direction_norm:
                normalized_entities["direction"] = direction_norm.normalized_code
                self.logger.info(
                    f"{LogEmoji.SUCCESS} Normalized direction: '{entities['direction']}' → "
                    f"'{direction_norm.normalized_code}'"
                )
            else:
                normalized_entities["direction"] = entities["direction"]

        # 5. Normalize legal_status
        if "legal_status" in entities and entities["legal_status"]:
            legal_norm = await self.repo.normalize_legal_status(entities["legal_status"])
            if legal_norm:
                normalized_entities["legal_status"] = legal_norm.normalized_code
                self.logger.info(
                    f"{LogEmoji.SUCCESS} Normalized legal status: '{entities['legal_status']}' → "
                    f"'{legal_norm.normalized_code}'"
                )
            else:
                normalized_entities["legal_status"] = entities["legal_status"]

        # 6. Validate area (if property_type available)
        if "area" in entities and entities["area"] and normalized_entities.get("property_type"):
            area_validation = await self.repo.validate_area(
                entities["area"],
                normalized_entities["property_type"]
            )
            validation_results.append(area_validation)
            warnings.extend(area_validation.warnings)

        # 7. Validate price (if district, property_type, and price available)
        if (
            "price" in entities
            and entities["price"]
            and normalized_entities.get("district")
            and normalized_entities.get("property_type")
        ):
            price_validation = await self.repo.validate_price(
                entities["price"],
                entities.get("area"),
                normalized_entities["district"],
                normalized_entities["property_type"]
            )
            validation_results.append(price_validation)
            warnings.extend(price_validation.warnings)

        # Copy other fields as-is
        for key, value in entities.items():
            if key not in normalized_entities:
                normalized_entities[key] = value

        # Calculate overall confidence
        confidence = self._calculate_confidence(normalized_entities, warnings)

        return {
            "normalized_entities": normalized_entities,
            "validation_results": validation_results,
            "warnings": warnings,
            "confidence": confidence
        }

    def _calculate_confidence(self, normalized_entities: Dict[str, Any], warnings: List[str]) -> float:
        """Calculate overall confidence score"""
        # Start with base confidence
        confidence = 1.0

        # Reduce confidence for each warning
        confidence -= len(warnings) * 0.05

        # Boost confidence if key fields are normalized
        key_fields = ["district", "property_type", "price", "area"]
        normalized_count = sum(1 for field in key_fields if field in normalized_entities)
        confidence += (normalized_count / len(key_fields)) * 0.1

        # Clamp between 0.0 and 1.0
        return max(0.0, min(1.0, confidence))

    async def get_districts_list(self) -> List[Dict[str, str]]:
        """Get list of all districts for UI/autocomplete"""
        if not self.repo:
            await self.initialize()

        districts = await self.repo.get_all_districts()
        return [
            {
                "code": d.code,
                "name_vi": d.name_vi,
                "name_en": d.name_en,
                "city": d.city
            }
            for d in districts
        ]

    async def get_property_types_list(self) -> List[Dict[str, str]]:
        """Get list of all property types for UI/autocomplete"""
        if not self.repo:
            await self.initialize()

        property_types = await self.repo.get_all_property_types()
        return [
            {
                "code": pt.code,
                "name_vi": pt.name_vi,
                "name_en": pt.name_en,
                "category": pt.category
            }
            for pt in property_types
        ]

    async def get_amenities_list(self, category: str = None) -> List[Dict[str, str]]:
        """Get list of all amenities for UI/autocomplete"""
        if not self.repo:
            await self.initialize()

        amenities = await self.repo.get_all_amenities(category=category)
        return [
            {
                "code": a.code,
                "name_vi": a.name_vi,
                "name_en": a.name_en,
                "category": a.category
            }
            for a in amenities
        ]

    async def close(self):
        """Close repository connection"""
        if self.repo:
            await self.repo.disconnect()

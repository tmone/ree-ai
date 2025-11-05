"""
Attribute Validation Module
Validates extracted entities against real-world patterns and logical consistency

UPDATED: Now uses centralized master data for validation
"""
from typing import Dict, Any, List, Tuple, Optional
from shared.utils.logger import setup_logger, LogEmoji
from shared.master_data import (
    get_district_master,
    get_property_type_master,
    get_price_range_master,
    get_attribute_schema
)

logger = setup_logger(__name__)


class AttributeValidator:
    """
    Validate extracted attributes using MASTER DATA.

    NOW USES:
    - DistrictMaster for district validation
    - PropertyTypeMaster for property type and area validation
    - PriceRangeMaster for price validation
    - AttributeSchema for comprehensive validation

    This layer ensures:
    1. Extracted values are within reasonable ranges (from master data)
    2. Logical consistency between attributes
    3. Conformity with known patterns from RAG context
    """

    def __init__(self):
        """Initialize validator with master data"""
        # Load master data
        self.district_master = get_district_master()
        self.property_type_master = get_property_type_master()
        self.price_range_master = get_price_range_master()
        self.schema = get_attribute_schema()

        logger.info(f"{LogEmoji.INFO} Attribute Validator initialized with Master Data")
        logger.info(f"{LogEmoji.INFO} Using centralized validation rules from master data")

    def validate(
        self,
        entities: Dict[str, Any],
        nlp_entities: Dict[str, Any],
        rag_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate extracted entities and calculate confidence score.

        Args:
            entities: Entities extracted by LLM
            nlp_entities: Entities extracted by NLP (for cross-validation)
            rag_context: Context from RAG retrieval

        Returns:
            Dictionary with:
            - validated_entities: Cleaned and validated entities
            - warnings: List of validation warnings
            - errors: List of validation errors
            - confidence: Overall confidence score (0-1)
            - validation_details: Detailed validation results
        """
        logger.info(f"{LogEmoji.TARGET} Validating extracted entities")

        warnings = []
        errors = []
        validation_details = {}

        # 1. Cross-validate with NLP entities
        nlp_warnings = self._cross_validate_with_nlp(entities, nlp_entities)
        warnings.extend(nlp_warnings)

        # 2. Validate against RAG patterns
        rag_warnings = self._validate_against_rag_patterns(entities, rag_context)
        warnings.extend(rag_warnings)

        # 3. Validate price reasonableness
        price_warnings = self._validate_price(entities, rag_context)
        warnings.extend(price_warnings)

        # 4. Validate area reasonableness
        area_warnings = self._validate_area(entities)
        warnings.extend(area_warnings)

        # 5. Validate logical consistency
        logic_warnings = self._validate_logical_consistency(entities)
        warnings.extend(logic_warnings)

        # 6. Validate required fields
        required_warnings = self._validate_required_fields(entities)
        warnings.extend(required_warnings)

        # Calculate confidence score
        confidence = self._calculate_confidence(entities, warnings, errors, rag_context)

        validation_details = {
            "total_warnings": len(warnings),
            "total_errors": len(errors),
            "validated_attributes": len(entities),
        }

        logger.info(f"{LogEmoji.SUCCESS} Validation complete: {len(warnings)} warnings, {len(errors)} errors, confidence={confidence:.2f}")

        return {
            "validated_entities": entities,
            "warnings": warnings,
            "errors": errors,
            "confidence": confidence,
            "validation_details": validation_details
        }

    def _cross_validate_with_nlp(
        self,
        llm_entities: Dict[str, Any],
        nlp_entities: Dict[str, Any]
    ) -> List[str]:
        """
        Cross-validate LLM entities with NLP entities.

        If NLP extracted something but LLM didn't, that's a warning.
        If they disagree significantly, that's a warning.
        """
        warnings = []

        # Check for missing entities that NLP found
        for key in ["district", "property_type", "bedrooms", "area"]:
            if key in nlp_entities and key not in llm_entities:
                warnings.append(f"NLP found '{key}': {nlp_entities[key]}, but LLM did not extract it")

        # Check for disagreements
        for key in ["bedrooms", "bathrooms", "area"]:
            if key in nlp_entities and key in llm_entities:
                nlp_val = nlp_entities[key]
                llm_val = llm_entities[key]
                if isinstance(nlp_val, (int, float)) and isinstance(llm_val, (int, float)):
                    # Allow 10% tolerance
                    if abs(nlp_val - llm_val) / max(nlp_val, 1) > 0.1:
                        warnings.append(
                            f"NLP-LLM mismatch for '{key}': NLP={nlp_val}, LLM={llm_val}"
                        )

        return warnings

    def _validate_against_rag_patterns(
        self,
        entities: Dict[str, Any],
        rag_context: Dict[str, Any]
    ) -> List[str]:
        """Validate entities against patterns from similar properties"""
        warnings = []
        patterns = rag_context.get("patterns", {})

        # Validate district against common districts
        if "district" in entities:
            common_districts = patterns.get("common_districts", [])
            if common_districts:
                district_values = [d["value"] for d in common_districts]
                if entities["district"] not in district_values:
                    warnings.append(
                        f"District '{entities['district']}' not found in similar properties. "
                        f"Common districts: {', '.join(district_values[:3])}"
                    )

        # Validate property type against common types
        if "property_type" in entities:
            common_types = patterns.get("common_property_types", [])
            if common_types:
                type_values = [t["value"] for t in common_types]
                if entities["property_type"] not in type_values:
                    warnings.append(
                        f"Property type '{entities['property_type']}' uncommon. "
                        f"Similar properties are: {', '.join(type_values)}"
                    )

        return warnings

    def _validate_price(
        self,
        entities: Dict[str, Any],
        rag_context: Dict[str, Any]
    ) -> List[str]:
        """Validate price reasonableness using PriceRangeMaster"""
        warnings = []

        price = entities.get("price")
        if not price:
            return warnings

        # Check against RAG value ranges first (if available)
        value_ranges = rag_context.get("value_ranges", {})
        if "price" in value_ranges:
            price_range = value_ranges["price"]
            min_price = price_range["min"]
            max_price = price_range["max"]
            avg_price = price_range["avg"]

            # Warning if price is 2x outside the range
            if price < min_price * 0.5:
                warnings.append(
                    f"Price {price:,.0f} VND unusually low. "
                    f"Similar properties: {min_price:,.0f} - {max_price:,.0f} VND (avg: {avg_price:,.0f})"
                )
            elif price > max_price * 2:
                warnings.append(
                    f"Price {price:,.0f} VND unusually high. "
                    f"Similar properties: {min_price:,.0f} - {max_price:,.0f} VND (avg: {avg_price:,.0f})"
                )

        # Use PriceRangeMaster for validation
        area = entities.get("area") or entities.get("land_area")
        district = entities.get("district")
        property_type = entities.get("property_type")

        if district and property_type:
            # Get property type code
            prop_type_obj = self.property_type_master.get_property_type(property_type)
            if prop_type_obj:
                # Validate using master data
                is_valid, warning = self.price_range_master.validate_price(
                    price=price,
                    area=area,
                    district=district,
                    property_type_code=prop_type_obj.code,
                    tolerance=2.0
                )

                if not is_valid and warning:
                    warnings.append(warning)

        return warnings

    def _validate_area(self, entities: Dict[str, Any]) -> List[str]:
        """Validate area reasonableness using PropertyTypeMaster"""
        warnings = []

        area = entities.get("area") or entities.get("land_area")
        property_type = entities.get("property_type")

        if not area or not property_type:
            return warnings

        # Use AttributeSchema for validation
        is_valid, warning = self.schema.validate_area(area, property_type)

        if not is_valid and warning:
            warnings.append(warning)

        return warnings

    def _validate_logical_consistency(self, entities: Dict[str, Any]) -> List[str]:
        """Validate logical relationships between attributes"""
        warnings = []

        # Bedrooms vs Bathrooms
        bedrooms = entities.get("bedrooms")
        bathrooms = entities.get("bathrooms")

        if bedrooms and bathrooms:
            # Bathrooms should not exceed bedrooms + 2 (unusual for residential)
            if bathrooms > bedrooms + 2:
                warnings.append(
                    f"Bathrooms ({bathrooms}) > Bedrooms ({bedrooms}) + 2 is unusual"
                )

            # Bathrooms should be at least 1 if bedrooms exist
            if bathrooms == 0:
                warnings.append(
                    f"Property with {bedrooms} bedrooms should have at least 1 bathroom"
                )

        # Bedrooms range check
        if bedrooms:
            if bedrooms < 1:
                warnings.append(f"Bedrooms cannot be less than 1 (got {bedrooms})")
            elif bedrooms > 20:
                warnings.append(f"Bedrooms {bedrooms} unusually high for residential property")

        # Floors range check
        floors = entities.get("floors")
        if floors:
            if floors < 1:
                warnings.append(f"Floors cannot be less than 1 (got {floors})")
            elif floors > 50:
                warnings.append(f"Floors {floors} unusually high")

        # Area vs Bedrooms consistency
        area = entities.get("area")
        if area and bedrooms:
            area_per_bedroom = area / bedrooms
            if area_per_bedroom < 10:
                warnings.append(
                    f"Area per bedroom ({area_per_bedroom:.1f}m²) very small. "
                    f"Total area: {area}m², Bedrooms: {bedrooms}"
                )

        return warnings

    def _validate_required_fields(self, entities: Dict[str, Any]) -> List[str]:
        """Check for recommended required fields"""
        warnings = []

        # For sale/rent listings, these are typically required
        recommended_fields = ["property_type", "district"]

        for field in recommended_fields:
            if field not in entities or entities[field] is None:
                warnings.append(f"Recommended field '{field}' is missing")

        return warnings

    def _calculate_confidence(
        self,
        entities: Dict[str, Any],
        warnings: List[str],
        errors: List[str],
        rag_context: Dict[str, Any]
    ) -> float:
        """
        Calculate overall confidence score for extraction.

        Factors:
        - Number of entities extracted (more = higher confidence)
        - Number of warnings (more = lower confidence)
        - Number of errors (more = much lower confidence)
        - RAG context availability (with context = higher confidence)
        - NLP cross-validation (agreement = higher confidence)
        """
        # Base score from number of entities
        num_entities = len([v for v in entities.values() if v is not None])
        base_score = min(num_entities * 0.1, 0.6)  # Max 0.6 from entities

        # Bonus for having RAG context
        rag_bonus = 0.0
        if rag_context.get("retrieved_count", 0) > 0:
            rag_bonus = 0.15

        # Bonus for key entities
        key_entities = ["property_type", "district", "price", "area"]
        key_bonus = sum(0.05 for key in key_entities if key in entities) * 0.25  # Max 0.2

        # Penalty for warnings
        warning_penalty = min(len(warnings) * 0.05, 0.3)  # Max -0.3

        # Severe penalty for errors
        error_penalty = min(len(errors) * 0.2, 0.6)  # Max -0.6

        # Calculate final confidence
        confidence = base_score + rag_bonus + key_bonus - warning_penalty - error_penalty
        confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]

        logger.debug(
            f"Confidence calculation: base={base_score:.2f}, rag={rag_bonus:.2f}, "
            f"key={key_bonus:.2f}, warnings=-{warning_penalty:.2f}, errors=-{error_penalty:.2f}, "
            f"final={confidence:.2f}"
        )

        return confidence


# Convenience function
def validate_attributes(
    entities: Dict[str, Any],
    nlp_entities: Dict[str, Any] = None,
    rag_context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Validate extracted attributes.

    Args:
        entities: Entities extracted by LLM
        nlp_entities: Entities from NLP layer (optional)
        rag_context: Context from RAG retrieval (optional)

    Returns:
        Validation result dictionary
    """
    validator = AttributeValidator()
    return validator.validate(
        entities,
        nlp_entities or {},
        rag_context or {}
    )

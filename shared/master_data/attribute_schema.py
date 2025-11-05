"""
Attribute Schema Module

Unified schema combining all master data sources.
Provides comprehensive schema for extraction and validation.

This is the main entry point for extraction services to query master data.
"""

from typing import Dict, List, Optional, Any, Set
from .cities import CityMaster, get_city_master
from .provinces import ProvinceMaster, get_province_master
from .districts import DistrictMaster, get_district_master
from .property_types import PropertyTypeMaster, get_property_type_master, AttributeDefinition
from .amenities import AmenityMaster, get_amenity_master
from .price_ranges import PriceRangeMaster, get_price_range_master
from .units import UnitMaster, get_unit_master


class AttributeSchema:
    """
    Unified attribute schema system combining all master data.

    This is the primary interface for extraction services to:
    1. Get complete attribute schema for any property type
    2. Normalize entities (cities, provinces, districts, property types, amenities, units)
    3. Validate extracted data
    4. Get extraction hints and patterns
    5. Parse values with units

    Usage:
        schema = AttributeSchema()

        # Get schema for extraction
        attrs = schema.get_attributes_for_property_type("căn hộ")

        # Normalize entities
        city = schema.normalize_city("sài gòn")  # -> "Hồ Chí Minh"
        province = schema.normalize_province("tphcm")  # -> "Hồ Chí Minh"
        district = schema.normalize_district("q7")  # -> "Quận 7"
        prop_type = schema.normalize_property_type("apartment")  # -> "căn hộ"

        # Parse units
        value, unit = schema.parse_value_with_unit("100m²")  # -> (100.0, Unit(m²))

        # Validate
        is_valid, warning = schema.validate_price(3000000000, 80, "Quận 7", "APARTMENT")
    """

    def __init__(self):
        """Initialize with all master data sources"""
        self.cities = get_city_master()
        self.provinces = get_province_master()
        self.districts = get_district_master()
        self.property_types = get_property_type_master()
        self.amenities = get_amenity_master()
        self.price_ranges = get_price_range_master()
        self.units = get_unit_master()

    # ===== Property Type Schema Methods =====

    def get_attributes_for_property_type(
        self,
        property_type_name: str
    ) -> Dict[str, AttributeDefinition]:
        """
        Get complete attribute schema for a property type.

        Args:
            property_type_name: Property type (accepts aliases)

        Returns:
            Dictionary of {attribute_name: AttributeDefinition}

        Example:
            schema.get_attributes_for_property_type("căn hộ")
            # Returns all attributes: title, price, bedrooms, bathrooms, etc.
        """
        return self.property_types.get_attribute_schema(property_type_name)

    def get_required_attributes(self, property_type_name: str) -> List[str]:
        """Get list of required attribute names for a property type"""
        return self.property_types.get_required_attributes(property_type_name)

    def get_all_property_types(self) -> List[str]:
        """Get list of all property type names"""
        return self.property_types.get_all_property_types()

    # ===== Normalization Methods =====

    def normalize_district(self, text: str) -> Optional[str]:
        """
        Normalize district name to standard format.

        Examples:
            "q7" -> "Quận 7"
            "phu my hung" -> "Quận 7"
        """
        return self.districts.normalize(text)

    def normalize_property_type(self, text: str) -> Optional[str]:
        """
        Normalize property type to standard format.

        Examples:
            "apartment" -> "căn hộ"
            "villa" -> "biệt thự"
        """
        return self.property_types.normalize(text)

    def normalize_amenity(self, text: str) -> Optional[str]:
        """
        Normalize amenity to standard code.

        Examples:
            "hồ bơi" -> "SWIMMING_POOL"
            "gym" -> "GYM"
        """
        return self.amenities.normalize(text)

    def normalize_city(self, text: str) -> Optional[str]:
        """
        Normalize city name to standard format.

        Examples:
            "sài gòn" -> "Hồ Chí Minh"
            "tphcm" -> "Hồ Chí Minh"
            "hanoi" -> "Hà Nội"
        """
        return self.cities.normalize(text)

    def normalize_province(self, text: str) -> Optional[str]:
        """
        Normalize province name to standard format.

        Examples:
            "tphcm" -> "Hồ Chí Minh"
            "da nang" -> "Đà Nẵng"
        """
        return self.provinces.normalize(text)

    def normalize_unit(self, text: str) -> Optional[Any]:
        """
        Normalize unit text to Unit object.

        Examples:
            "m2" -> Unit(m²)
            "ty" -> Unit(tỷ)
        """
        return self.units.normalize_unit(text)

    def parse_value_with_unit(self, text: str) -> Optional[tuple]:
        """
        Parse text containing value and unit.

        Examples:
            "100m²" -> (100.0, Unit(m²))
            "3 tỷ" -> (3.0, Unit(tỷ))
        """
        return self.units.parse_value_with_unit(text)

    # ===== Validation Methods =====

    def validate_price(
        self,
        price: float,
        area: Optional[float],
        district: str,
        property_type_code: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if price is reasonable.

        Returns:
            (is_valid, warning_message)
        """
        return self.price_ranges.validate_price(price, area, district, property_type_code)

    def validate_area(
        self,
        area: float,
        property_type_name: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate if area is reasonable for property type.

        Returns:
            (is_valid, warning_message)
        """
        prop_type = self.property_types.get_property_type(property_type_name)
        if not prop_type:
            return True, None

        # Get area attribute definition
        area_attr = prop_type.all_attributes.get("area") or prop_type.all_attributes.get("land_area")
        if not area_attr:
            return True, None

        min_val = area_attr.min_value
        max_val = area_attr.max_value

        if min_val and area < min_val:
            return False, f"Area {area}m² is below minimum {min_val}m² for {property_type_name}"

        if max_val and area > max_val:
            return False, f"Area {area}m² exceeds maximum {max_val}m² for {property_type_name}"

        return True, None

    # ===== Query & Lookup Methods =====

    def get_district_info(self, district_name: str) -> Optional[Any]:
        """Get full district information"""
        return self.districts.get_district(district_name)

    def get_property_type_info(self, property_type_name: str) -> Optional[Any]:
        """Get full property type information"""
        return self.property_types.get_property_type(property_type_name)

    def get_amenities_for_property_type(self, property_type_code: str) -> List[Any]:
        """Get list of applicable amenities for a property type"""
        return self.amenities.get_amenities_for_property_type(property_type_code)

    def get_price_range(self, district: str, property_type_code: str) -> Optional[Any]:
        """Get reference price range"""
        return self.price_ranges.get_price_range(district, property_type_code)

    # ===== Extraction Helper Methods =====

    def extract_entities_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract all recognizable entities from free text.

        This is a comprehensive extraction that finds:
        - Districts
        - Property types
        - Amenities

        Args:
            text: Free text

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        # Extract district
        district_match = self.districts.extract_from_text(text)
        if district_match:
            matched_text, district_obj = district_match
            entities["district"] = district_obj.standard_name

        # Extract property type (simple keyword match)
        text_lower = text.lower()
        for prop_type in self.property_types.PROPERTY_TYPES:
            if prop_type.standard_name in text_lower:
                entities["property_type"] = prop_type.standard_name
                break
            for alias in prop_type.aliases:
                if alias in text_lower:
                    entities["property_type"] = prop_type.standard_name
                    break

        # Extract amenities
        amenities_found = self.amenities.extract_from_text(text)
        if amenities_found:
            entities["amenities"] = amenities_found

        return entities

    def build_extraction_prompt(
        self,
        query: str,
        property_type: Optional[str] = None
    ) -> str:
        """
        Build enhanced extraction prompt with master data context.

        This generates a prompt that includes:
        - Valid property types
        - Valid districts
        - Expected attributes for the property type
        - Valid amenities

        Args:
            query: User query
            property_type: Property type if known (optional)

        Returns:
            Enhanced extraction prompt string
        """
        # Get valid values from master data
        valid_property_types = self.get_all_property_types()
        valid_districts = self.districts.get_all_standard_names("Hồ Chí Minh")

        # Get attributes if property type is known
        attribute_schema = {}
        if property_type:
            attribute_schema = self.get_attributes_for_property_type(property_type)

        # Build prompt
        prompt = f"""Bạn là chuyên gia trích xuất thông tin bất động sản.

🎯 NHIỆM VỤ: Trích xuất thông tin từ query thành JSON chuẩn.

📊 MASTER DATA (sử dụng các giá trị CHUẨN sau):

**Property Types (chỉ dùng các loại sau):**
{', '.join(valid_property_types)}

**Districts in HCMC (chuẩn hóa về format sau):**
{', '.join(valid_districts[:10])}... (và các quận khác)

"""

        if attribute_schema:
            prompt += f"""
**Expected Attributes for {property_type}:**
"""
            for attr_name, attr_def in attribute_schema.items():
                if attr_def.required:
                    prompt += f"- {attr_name} ({attr_def.type.value}) - REQUIRED: {attr_def.description}\n"

            prompt += "\n**Optional Attributes:**\n"
            for attr_name, attr_def in attribute_schema.items():
                if not attr_def.required:
                    prompt += f"- {attr_name} ({attr_def.type.value}): {attr_def.description}\n"

        prompt += f"""

🔍 EXTRACTION RULES:
1. Chỉ trích xuất thông tin CÓ TRONG QUERY
2. Chuẩn hóa district về format chuẩn từ master data
3. Chuẩn hóa property_type về tên chuẩn
4. Không bịa thêm thông tin

📥 USER QUERY:
{query}

📤 OUTPUT (JSON only, no explanation):
"""
        return prompt

    def get_validation_summary(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive validation summary for extracted entities.

        Args:
            entities: Extracted entities dictionary

        Returns:
            Validation summary with warnings and suggestions
        """
        summary = {
            "valid": True,
            "warnings": [],
            "suggestions": [],
            "normalized_entities": {}
        }

        # Normalize district
        if "district" in entities:
            normalized_district = self.normalize_district(entities["district"])
            if normalized_district:
                summary["normalized_entities"]["district"] = normalized_district
                if normalized_district != entities["district"]:
                    summary["suggestions"].append(
                        f"District normalized: '{entities['district']}' -> '{normalized_district}'"
                    )
            else:
                summary["warnings"].append(f"Unknown district: '{entities['district']}'")
                summary["valid"] = False

        # Normalize property type
        if "property_type" in entities:
            normalized_type = self.normalize_property_type(entities["property_type"])
            if normalized_type:
                summary["normalized_entities"]["property_type"] = normalized_type
                if normalized_type != entities["property_type"]:
                    summary["suggestions"].append(
                        f"Property type normalized: '{entities['property_type']}' -> '{normalized_type}'"
                    )
            else:
                summary["warnings"].append(f"Unknown property type: '{entities['property_type']}'")
                summary["valid"] = False

        # Validate price if available
        if "price" in entities and "area" in entities and "district" in summary["normalized_entities"]:
            prop_type = summary["normalized_entities"].get("property_type", "APARTMENT")
            prop_type_obj = self.property_types.get_property_type(prop_type)
            prop_type_code = prop_type_obj.code if prop_type_obj else "APARTMENT"

            is_valid, warning = self.validate_price(
                entities["price"],
                entities["area"],
                summary["normalized_entities"]["district"],
                prop_type_code
            )
            if not is_valid:
                summary["warnings"].append(warning)

        # Validate area if available
        if "area" in entities and "property_type" in summary["normalized_entities"]:
            is_valid, warning = self.validate_area(
                entities["area"],
                summary["normalized_entities"]["property_type"]
            )
            if not is_valid:
                summary["warnings"].append(warning)

        return summary


# Singleton instance
_instance: Optional[AttributeSchema] = None

def get_attribute_schema() -> AttributeSchema:
    """Get singleton instance of AttributeSchema"""
    global _instance
    if _instance is None:
        _instance = AttributeSchema()
    return _instance

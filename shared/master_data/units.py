"""
Units Master Data for Vietnam Real Estate

Provides standardized measurement units with normalization and conversion.
Covers area, price, distance, and count units used in Vietnamese real estate.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class UnitCategory(str, Enum):
    """Categories of measurement units"""
    AREA = "area"  # Area measurements (m², ha, etc.)
    PRICE = "price"  # Price/currency (VND, tỷ, triệu, etc.)
    DISTANCE = "distance"  # Distance/length (m, km, etc.)
    COUNT = "count"  # Countable items (phòng, tầng, etc.)
    TIME = "time"  # Time-based (tháng, năm for rent)


@dataclass
class Unit:
    """Definition of a measurement unit"""
    code: str  # Unique code (e.g., "SQUARE_METER", "BILLION_VND")
    standard_name: str  # Standard name (e.g., "m²", "tỷ")
    display_name: str  # Display name (e.g., "mét vuông", "tỷ đồng")
    aliases: List[str]  # Alternative representations
    category: UnitCategory  # Unit category
    base_multiplier: float  # Multiplier to convert to base unit
    base_unit: str  # Base unit for this category
    description: str = ""


class UnitMaster:
    """
    Master data for measurement units in real estate.

    Usage:
        master = UnitMaster()

        # Normalize unit
        unit = master.normalize_unit("m2")  # Returns Unit object for "m²"

        # Parse value with unit
        value, unit = master.parse_value_with_unit("100m²")  # (100, m² Unit)

        # Convert value
        converted = master.convert(100, "m²", "ha")  # Convert 100 m² to hectares
    """

    UNITS = [
        # ===== AREA UNITS =====
        Unit(
            code="SQUARE_METER",
            standard_name="m²",
            display_name="mét vuông",
            aliases=["m2", "m²", "mét vuông", "met vuong", "mét2", "m^2", "sq m", "sqm"],
            category=UnitCategory.AREA,
            base_multiplier=1.0,
            base_unit="m²",
            description="Square meter (base unit for area)"
        ),
        Unit(
            code="HECTARE",
            standard_name="ha",
            display_name="héc-ta",
            aliases=["ha", "hectare", "hec-ta", "héc-ta", "hec ta"],
            category=UnitCategory.AREA,
            base_multiplier=10000.0,  # 1 ha = 10,000 m²
            base_unit="m²",
            description="Hectare (10,000 m²)"
        ),
        Unit(
            code="SAO",
            standard_name="sào",
            display_name="sào",
            aliases=["sào", "sao"],
            category=UnitCategory.AREA,
            base_multiplier=360.0,  # 1 sào (Northern) = 360 m²
            base_unit="m²",
            description="Sào (traditional Vietnamese unit, ~360 m²)"
        ),
        Unit(
            code="SAO_SOUTHERN",
            standard_name="sào Nam Bộ",
            display_name="sào Nam Bộ",
            aliases=["sào nam bộ", "sao nam bo"],
            category=UnitCategory.AREA,
            base_multiplier=500.0,  # 1 sào (Southern) = 500 m²
            base_unit="m²",
            description="Sào Nam Bộ (Southern Vietnam, ~500 m²)"
        ),
        Unit(
            code="MAU",
            standard_name="mẫu",
            display_name="mẫu",
            aliases=["mẫu", "mau"],
            category=UnitCategory.AREA,
            base_multiplier=3600.0,  # 1 mẫu (Northern) = 3,600 m²
            base_unit="m²",
            description="Mẫu (traditional Vietnamese unit, ~3,600 m²)"
        ),
        Unit(
            code="MAU_SOUTHERN",
            standard_name="mẫu Tây",
            display_name="mẫu Tây",
            aliases=["mẫu tây", "mau tay"],
            category=UnitCategory.AREA,
            base_multiplier=10000.0,  # 1 mẫu Tây = 10,000 m²
            base_unit="m²",
            description="Mẫu Tây (Southern Vietnam, 10,000 m²)"
        ),

        # ===== PRICE UNITS (VND) =====
        Unit(
            code="VND",
            standard_name="đồng",
            display_name="đồng",
            aliases=["đồng", "dong", "vnd", "₫", "d"],
            category=UnitCategory.PRICE,
            base_multiplier=1.0,
            base_unit="VND",
            description="Vietnamese Dong (base currency unit)"
        ),
        Unit(
            code="THOUSAND_VND",
            standard_name="nghìn",
            display_name="nghìn đồng",
            aliases=["nghìn", "nghin", "k", "1000"],
            category=UnitCategory.PRICE,
            base_multiplier=1_000.0,
            base_unit="VND",
            description="Thousand VND (1,000 đồng)"
        ),
        Unit(
            code="MILLION_VND",
            standard_name="triệu",
            display_name="triệu đồng",
            aliases=["triệu", "trieu", "tr", "million", "m", "1000000"],
            category=UnitCategory.PRICE,
            base_multiplier=1_000_000.0,
            base_unit="VND",
            description="Million VND (1,000,000 đồng)"
        ),
        Unit(
            code="BILLION_VND",
            standard_name="tỷ",
            display_name="tỷ đồng",
            aliases=["tỷ", "ty", "tỷ đồng", "ty dong", "billion", "b", "1000000000"],
            category=UnitCategory.PRICE,
            base_multiplier=1_000_000_000.0,
            base_unit="VND",
            description="Billion VND (1,000,000,000 đồng)"
        ),

        # ===== DISTANCE/LENGTH UNITS =====
        Unit(
            code="METER",
            standard_name="m",
            display_name="mét",
            aliases=["m", "mét", "met", "meter"],
            category=UnitCategory.DISTANCE,
            base_multiplier=1.0,
            base_unit="m",
            description="Meter (base unit for distance)"
        ),
        Unit(
            code="KILOMETER",
            standard_name="km",
            display_name="ki-lô-mét",
            aliases=["km", "ki-lô-mét", "kilo met", "kilometer"],
            category=UnitCategory.DISTANCE,
            base_multiplier=1000.0,
            base_unit="m",
            description="Kilometer (1,000 m)"
        ),
        Unit(
            code="CENTIMETER",
            standard_name="cm",
            display_name="xăng-ti-mét",
            aliases=["cm", "xăng-ti-mét", "centimeter"],
            category=UnitCategory.DISTANCE,
            base_multiplier=0.01,
            base_unit="m",
            description="Centimeter (0.01 m)"
        ),

        # ===== COUNT UNITS =====
        Unit(
            code="ROOM",
            standard_name="phòng",
            display_name="phòng",
            aliases=["phòng", "phong", "pn", "room"],
            category=UnitCategory.COUNT,
            base_multiplier=1.0,
            base_unit="phòng",
            description="Room (bedroom, bathroom)"
        ),
        Unit(
            code="FLOOR",
            standard_name="tầng",
            display_name="tầng",
            aliases=["tầng", "tang", "lầu", "lau", "floor"],
            category=UnitCategory.COUNT,
            base_multiplier=1.0,
            base_unit="tầng",
            description="Floor/Story"
        ),
        Unit(
            code="UNIT",
            standard_name="căn",
            display_name="căn",
            aliases=["căn", "can", "unit"],
            category=UnitCategory.COUNT,
            base_multiplier=1.0,
            base_unit="căn",
            description="Unit (apartment, house)"
        ),

        # ===== TIME UNITS (for rent) =====
        Unit(
            code="MONTH",
            standard_name="tháng",
            display_name="tháng",
            aliases=["tháng", "thang", "month", "/tháng", "/thang", "/month"],
            category=UnitCategory.TIME,
            base_multiplier=1.0,
            base_unit="tháng",
            description="Month (rental period)"
        ),
        Unit(
            code="YEAR",
            standard_name="năm",
            display_name="năm",
            aliases=["năm", "nam", "year", "/năm", "/nam", "/year"],
            category=UnitCategory.TIME,
            base_multiplier=12.0,
            base_unit="tháng",
            description="Year (rental period)"
        ),
    ]

    def __init__(self):
        """Initialize unit master"""
        self.units = self.UNITS
        self._build_indices()

    def _build_indices(self):
        """Build lookup indices for fast search"""
        # Code -> Unit
        self.by_code: Dict[str, Unit] = {
            u.code: u for u in self.units
        }

        # Standard name -> Unit
        self.by_standard_name: Dict[str, Unit] = {
            u.standard_name: u for u in self.units
        }

        # Alias -> Unit (for normalization)
        self.alias_to_unit: Dict[str, Unit] = {}
        for unit in self.units:
            # Add standard name
            self.alias_to_unit[unit.standard_name.lower()] = unit
            # Add all aliases
            for alias in unit.aliases:
                self.alias_to_unit[alias.lower()] = unit

        # Category -> Units
        self.by_category: Dict[UnitCategory, List[Unit]] = {}
        for unit in self.units:
            if unit.category not in self.by_category:
                self.by_category[unit.category] = []
            self.by_category[unit.category].append(unit)

    def normalize_unit(self, text: str) -> Optional[Unit]:
        """
        Normalize unit text to Unit object.

        Examples:
            "m2" -> Unit(m²)
            "ty" -> Unit(tỷ)
            "tr" -> Unit(triệu)

        Args:
            text: Unit text

        Returns:
            Unit object or None
        """
        text_lower = text.lower().strip()
        return self.alias_to_unit.get(text_lower)

    def parse_value_with_unit(self, text: str) -> Optional[Tuple[float, Unit]]:
        """
        Parse text containing value and unit.

        Examples:
            "100m²" -> (100.0, Unit(m²))
            "3 tỷ" -> (3.0, Unit(tỷ))
            "2.5 triệu" -> (2.5, Unit(triệu))
            "80m2" -> (80.0, Unit(m²))

        Args:
            text: Text with value and unit

        Returns:
            Tuple of (value, Unit) or None if parsing fails
        """
        import re

        text = text.strip()

        # Pattern: number (integer or decimal) followed by optional space and unit
        # Examples: "100m²", "3 tỷ", "2.5 triệu", "80m2"
        pattern = r'([\d,\.]+)\s*([^\d\s,\.]+)'
        match = re.search(pattern, text)

        if match:
            # Extract value
            value_str = match.group(1).replace(',', '')  # Remove thousand separators
            try:
                value = float(value_str)
            except ValueError:
                return None

            # Extract unit
            unit_str = match.group(2)
            unit = self.normalize_unit(unit_str)

            if unit:
                return (value, unit)

        return None

    def convert(self, value: float, from_unit_text: str, to_unit_text: str) -> Optional[float]:
        """
        Convert value from one unit to another (within same category).

        Examples:
            convert(100, "m²", "ha") -> 0.01
            convert(3, "tỷ", "triệu") -> 3000.0
            convert(1, "ha", "m²") -> 10000.0

        Args:
            value: Numeric value
            from_unit_text: Source unit
            to_unit_text: Target unit

        Returns:
            Converted value or None if conversion not possible
        """
        from_unit = self.normalize_unit(from_unit_text)
        to_unit = self.normalize_unit(to_unit_text)

        if not from_unit or not to_unit:
            return None

        # Can only convert within same category
        if from_unit.category != to_unit.category:
            return None

        # Convert to base unit, then to target unit
        base_value = value * from_unit.base_multiplier
        target_value = base_value / to_unit.base_multiplier

        return target_value

    def get_units_by_category(self, category: UnitCategory) -> List[Unit]:
        """Get all units in a category"""
        return self.by_category.get(category, [])

    def format_value(self, value: float, unit_text: str) -> str:
        """
        Format value with unit for display.

        Examples:
            format_value(100, "m²") -> "100 m²"
            format_value(3000000000, "VND") -> "3 tỷ"
            format_value(5.77, "tỷ") -> "5.77 tỷ"

        Args:
            value: Numeric value
            unit_text: Unit

        Returns:
            Formatted string
        """
        unit = self.normalize_unit(unit_text)
        if not unit:
            return f"{value:,.0f}"

        # Special formatting for currency
        if unit.category == UnitCategory.PRICE and unit.code == "VND":
            # Auto-convert to appropriate unit
            if value >= 1_000_000_000:
                converted_value = value / 1_000_000_000
                return f"{converted_value:,.2f} tỷ"
            elif value >= 1_000_000:
                converted_value = value / 1_000_000
                return f"{converted_value:,.0f} triệu"
            elif value >= 1_000:
                converted_value = value / 1_000
                return f"{converted_value:,.0f} nghìn"
            else:
                return f"{value:,.0f} đồng"

        # For other units, use standard format
        if value >= 1_000:
            return f"{value:,.0f} {unit.standard_name}"
        elif value == int(value):
            return f"{int(value)} {unit.standard_name}"
        else:
            return f"{value:.2f} {unit.standard_name}"

    def extract_units_from_text(self, text: str) -> List[Tuple[float, Unit]]:
        """
        Extract all values with units from text.

        Example:
            "Căn hộ 80m² giá 3 tỷ" -> [(80.0, m² Unit), (3.0, tỷ Unit)]

        Args:
            text: Input text

        Returns:
            List of (value, Unit) tuples
        """
        import re

        results = []

        # Find all number + unit patterns
        pattern = r'([\d,\.]+)\s*([^\d\s,\.]+)'
        matches = re.finditer(pattern, text)

        for match in matches:
            parsed = self.parse_value_with_unit(match.group(0))
            if parsed:
                results.append(parsed)

        return results


# Singleton instance
_instance: Optional[UnitMaster] = None

def get_unit_master() -> UnitMaster:
    """Get singleton instance of UnitMaster"""
    global _instance
    if _instance is None:
        _instance = UnitMaster()
    return _instance

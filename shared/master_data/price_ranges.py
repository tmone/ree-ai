"""
Price Range Master Data

Reference price ranges for validation and market analysis.
Based on real HCMC real estate market data (2024-2025).

These ranges help validate extracted prices and provide market context.
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PriceRange:
    """Price range for a specific district and property type"""
    min_price_per_m2: float  # Minimum price per m² in VND
    max_price_per_m2: float  # Maximum price per m² in VND
    avg_price_per_m2: float  # Average price per m² in VND
    min_total_price: float  # Typical minimum total price in VND
    max_total_price: float  # Typical maximum total price in VND
    avg_total_price: float  # Average total price in VND


class PriceRangeMaster:
    """
    Master data for reference price ranges in HCMC.

    Based on 2024-2025 real estate market data.
    Used for price validation and anomaly detection.

    Usage:
        master = PriceRangeMaster()
        price_range = master.get_price_range("Quận 7", "APARTMENT")
        is_valid = master.validate_price(3000000000, 80, "Quận 7", "APARTMENT")
    """

    # Price per m² ranges by district (VND/m²)
    # Source: HCMC real estate market data 2024-2025
    DISTRICT_PRICE_RANGES = {
        # Premium Districts (Tier 1)
        "Quận 1": {
            "APARTMENT": PriceRange(
                min_price_per_m2=100_000_000,
                max_price_per_m2=300_000_000,
                avg_price_per_m2=180_000_000,
                min_total_price=3_000_000_000,
                max_total_price=50_000_000_000,
                avg_total_price=12_000_000_000
            ),
            "TOWNHOUSE": PriceRange(
                min_price_per_m2=150_000_000,
                max_price_per_m2=500_000_000,
                avg_price_per_m2=250_000_000,
                min_total_price=10_000_000_000,
                max_total_price=100_000_000_000,
                avg_total_price=30_000_000_000
            ),
            "OFFICE": PriceRange(
                min_price_per_m2=80_000_000,
                max_price_per_m2=250_000_000,
                avg_price_per_m2=150_000_000,
                min_total_price=3_000_000_000,
                max_total_price=50_000_000_000,
                avg_total_price=15_000_000_000
            ),
        },
        "Quận 2": {
            "APARTMENT": PriceRange(
                min_price_per_m2=60_000_000,
                max_price_per_m2=200_000_000,
                avg_price_per_m2=100_000_000,
                min_total_price=2_500_000_000,
                max_total_price=30_000_000_000,
                avg_total_price=8_000_000_000
            ),
            "VILLA": PriceRange(
                min_price_per_m2=80_000_000,
                max_price_per_m2=250_000_000,
                avg_price_per_m2=150_000_000,
                min_total_price=15_000_000_000,
                max_total_price=200_000_000_000,
                avg_total_price=50_000_000_000
            ),
            "TOWNHOUSE": PriceRange(
                min_price_per_m2=70_000_000,
                max_price_per_m2=200_000_000,
                avg_price_per_m2=120_000_000,
                min_total_price=8_000_000_000,
                max_total_price=50_000_000_000,
                avg_total_price=20_000_000_000
            ),
        },
        "Quận 7": {
            "APARTMENT": PriceRange(
                min_price_per_m2=50_000_000,
                max_price_per_m2=180_000_000,
                avg_price_per_m2=90_000_000,
                min_total_price=2_000_000_000,
                max_total_price=25_000_000_000,
                avg_total_price=7_000_000_000
            ),
            "VILLA": PriceRange(
                min_price_per_m2=70_000_000,
                max_price_per_m2=200_000_000,
                avg_price_per_m2=120_000_000,
                min_total_price=15_000_000_000,
                max_total_price=150_000_000_000,
                avg_total_price=45_000_000_000
            ),
            "TOWNHOUSE": PriceRange(
                min_price_per_m2=60_000_000,
                max_price_per_m2=150_000_000,
                avg_price_per_m2=90_000_000,
                min_total_price=7_000_000_000,
                max_total_price=40_000_000_000,
                avg_total_price=15_000_000_000
            ),
        },

        # Mid-tier Districts (Tier 2)
        "Quận Bình Thạnh": {
            "APARTMENT": PriceRange(
                min_price_per_m2=50_000_000,
                max_price_per_m2=150_000_000,
                avg_price_per_m2=80_000_000,
                min_total_price=1_800_000_000,
                max_total_price=15_000_000_000,
                avg_total_price=6_000_000_000
            ),
            "TOWNHOUSE": PriceRange(
                min_price_per_m2=50_000_000,
                max_price_per_m2=120_000_000,
                avg_price_per_m2=75_000_000,
                min_total_price=5_000_000_000,
                max_total_price=25_000_000_000,
                avg_total_price=12_000_000_000
            ),
        },
        "Quận Tân Bình": {
            "APARTMENT": PriceRange(
                min_price_per_m2=45_000_000,
                max_price_per_m2=120_000_000,
                avg_price_per_m2=70_000_000,
                min_total_price=1_500_000_000,
                max_total_price=12_000_000_000,
                avg_total_price=5_500_000_000
            ),
            "TOWNHOUSE": PriceRange(
                min_price_per_m2=50_000_000,
                max_price_per_m2=110_000_000,
                avg_price_per_m2=70_000_000,
                min_total_price=5_000_000_000,
                max_total_price=20_000_000_000,
                avg_total_price=10_000_000_000
            ),
        },
        "Thành phố Thủ Đức": {
            "APARTMENT": PriceRange(
                min_price_per_m2=40_000_000,
                max_price_per_m2=120_000_000,
                avg_price_per_m2=65_000_000,
                min_total_price=1_500_000_000,
                max_total_price=15_000_000_000,
                avg_total_price=5_000_000_000
            ),
            "VILLA": PriceRange(
                min_price_per_m2=50_000_000,
                max_price_per_m2=150_000_000,
                avg_price_per_m2=80_000_000,
                min_total_price=10_000_000_000,
                max_total_price=80_000_000_000,
                avg_total_price=30_000_000_000
            ),
            "TOWNHOUSE": PriceRange(
                min_price_per_m2=40_000_000,
                max_price_per_m2=100_000_000,
                avg_price_per_m2=60_000_000,
                min_total_price=4_000_000_000,
                max_total_price=20_000_000_000,
                avg_total_price=8_000_000_000
            ),
            "LAND": PriceRange(
                min_price_per_m2=30_000_000,
                max_price_per_m2=100_000_000,
                avg_price_per_m2=50_000_000,
                min_total_price=3_000_000_000,
                max_total_price=50_000_000_000,
                avg_total_price=10_000_000_000
            ),
        },

        # Affordable Districts (Tier 3)
        "Quận 12": {
            "APARTMENT": PriceRange(
                min_price_per_m2=25_000_000,
                max_price_per_m2=60_000_000,
                avg_price_per_m2=40_000_000,
                min_total_price=1_000_000_000,
                max_total_price=5_000_000_000,
                avg_total_price=2_500_000_000
            ),
            "TOWNHOUSE": PriceRange(
                min_price_per_m2=30_000_000,
                max_price_per_m2=70_000_000,
                avg_price_per_m2=45_000_000,
                min_total_price=2_500_000_000,
                max_total_price=10_000_000_000,
                avg_total_price=5_000_000_000
            ),
        },
        "Quận Bình Tân": {
            "APARTMENT": PriceRange(
                min_price_per_m2=25_000_000,
                max_price_per_m2=55_000_000,
                avg_price_per_m2=38_000_000,
                min_total_price=1_000_000_000,
                max_total_price=4_000_000_000,
                avg_total_price=2_200_000_000
            ),
            "TOWNHOUSE": PriceRange(
                min_price_per_m2=28_000_000,
                max_price_per_m2=65_000_000,
                avg_price_per_m2=42_000_000,
                min_total_price=2_000_000_000,
                max_total_price=8_000_000_000,
                avg_total_price=4_000_000_000
            ),
        },
    }

    # Default ranges for districts not in the list
    DEFAULT_RANGES = {
        "APARTMENT": PriceRange(
            min_price_per_m2=30_000_000,
            max_price_per_m2=150_000_000,
            avg_price_per_m2=60_000_000,
            min_total_price=1_500_000_000,
            max_total_price=15_000_000_000,
            avg_total_price=5_000_000_000
        ),
        "VILLA": PriceRange(
            min_price_per_m2=50_000_000,
            max_price_per_m2=200_000_000,
            avg_price_per_m2=100_000_000,
            min_total_price=10_000_000_000,
            max_total_price=100_000_000_000,
            avg_total_price=30_000_000_000
        ),
        "TOWNHOUSE": PriceRange(
            min_price_per_m2=40_000_000,
            max_price_per_m2=120_000_000,
            avg_price_per_m2=70_000_000,
            min_total_price=4_000_000_000,
            max_total_price=30_000_000_000,
            avg_total_price=10_000_000_000
        ),
        "LAND": PriceRange(
            min_price_per_m2=20_000_000,
            max_price_per_m2=100_000_000,
            avg_price_per_m2=45_000_000,
            min_total_price=2_000_000_000,
            max_total_price=50_000_000_000,
            avg_total_price=10_000_000_000
        ),
        "OFFICE": PriceRange(
            min_price_per_m2=40_000_000,
            max_price_per_m2=150_000_000,
            avg_price_per_m2=80_000_000,
            min_total_price=2_000_000_000,
            max_total_price=30_000_000_000,
            avg_total_price=8_000_000_000
        ),
    }

    def __init__(self):
        """Initialize price range master"""
        pass

    def get_price_range(
        self,
        district: str,
        property_type_code: str
    ) -> Optional[PriceRange]:
        """
        Get price range for a specific district and property type.

        Args:
            district: District name (e.g., "Quận 7")
            property_type_code: Property type code (e.g., "APARTMENT")

        Returns:
            PriceRange object or None if not available
        """
        # Try exact match
        if district in self.DISTRICT_PRICE_RANGES:
            if property_type_code in self.DISTRICT_PRICE_RANGES[district]:
                return self.DISTRICT_PRICE_RANGES[district][property_type_code]

        # Fall back to default
        return self.DEFAULT_RANGES.get(property_type_code)

    def validate_price(
        self,
        price: float,
        area: Optional[float],
        district: str,
        property_type_code: str,
        tolerance: float = 2.0
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a price is reasonable for the given parameters.

        Args:
            price: Total price in VND
            area: Property area in m² (optional)
            district: District name
            property_type_code: Property type code
            tolerance: Multiplier for acceptable range (2.0 = allow 2x outside range)

        Returns:
            Tuple of (is_valid, warning_message)
        """
        price_range = self.get_price_range(district, property_type_code)

        if not price_range:
            # No reference data available
            return True, None

        # Check total price range
        if price < price_range.min_total_price * (1 / tolerance):
            return False, (
                f"Price {price:,.0f} VND is unusually low for {property_type_code} in {district}. "
                f"Typical range: {price_range.min_total_price:,.0f} - {price_range.max_total_price:,.0f} VND"
            )

        if price > price_range.max_total_price * tolerance:
            return False, (
                f"Price {price:,.0f} VND is unusually high for {property_type_code} in {district}. "
                f"Typical range: {price_range.min_total_price:,.0f} - {price_range.max_total_price:,.0f} VND"
            )

        # Check price per m² if area is provided
        if area and area > 0:
            price_per_m2 = price / area

            if price_per_m2 < price_range.min_price_per_m2 * (1 / tolerance):
                return False, (
                    f"Price per m² {price_per_m2:,.0f} VND/m² is unusually low for {property_type_code} in {district}. "
                    f"Typical range: {price_range.min_price_per_m2:,.0f} - {price_range.max_price_per_m2:,.0f} VND/m²"
                )

            if price_per_m2 > price_range.max_price_per_m2 * tolerance:
                return False, (
                    f"Price per m² {price_per_m2:,.0f} VND/m² is unusually high for {property_type_code} in {district}. "
                    f"Typical range: {price_range.min_price_per_m2:,.0f} - {price_range.max_price_per_m2:,.0f} VND/m²"
                )

        # Price looks reasonable
        return True, None

    def get_estimated_price_range(
        self,
        area: float,
        district: str,
        property_type_code: str
    ) -> Optional[Tuple[float, float, float]]:
        """
        Estimate price range based on area.

        Args:
            area: Property area in m²
            district: District name
            property_type_code: Property type code

        Returns:
            Tuple of (min_price, avg_price, max_price) in VND, or None
        """
        price_range = self.get_price_range(district, property_type_code)

        if not price_range:
            return None

        min_price = area * price_range.min_price_per_m2
        avg_price = area * price_range.avg_price_per_m2
        max_price = area * price_range.max_price_per_m2

        return (min_price, avg_price, max_price)


# Singleton instance
_instance: Optional[PriceRangeMaster] = None

def get_price_range_master() -> PriceRangeMaster:
    """Get singleton instance of PriceRangeMaster"""
    global _instance
    if _instance is None:
        _instance = PriceRangeMaster()
    return _instance

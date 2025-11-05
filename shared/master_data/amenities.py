"""
Amenities Master Data

Standardized list of property amenities with normalization.
Different property types have different relevant amenities.

Example:
- Apartment: parking, elevator, swimming_pool, gym, security
- Villa: private_pool, wine_cellar, home_theater, rooftop_terrace
- Land: utilities (water, electricity), zoning
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class AmenityCategory(str, Enum):
    """Categories of amenities"""
    BUILDING = "building"  # Building-level (elevator, security, lobby)
    UNIT = "unit"  # Unit-level (balcony, storage, etc.)
    RECREATION = "recreation"  # Recreation (pool, gym, playground)
    PARKING = "parking"  # Parking related
    SECURITY = "security"  # Security features
    LUXURY = "luxury"  # Luxury features (wine cellar, home theater)
    UTILITIES = "utilities"  # Basic utilities (water, electricity)


@dataclass
class Amenity:
    """Definition of a single amenity"""
    code: str  # Unique code (e.g., "PARKING", "SWIMMING_POOL")
    standard_name: str  # Standard name (e.g., "parking", "swimming_pool")
    display_name: str  # Display name (e.g., "Chỗ đậu xe", "Hồ bơi")
    aliases: List[str]  # Alternative names for extraction
    category: AmenityCategory  # Amenity category
    applicable_to: List[str]  # Property types this applies to (codes)
    description: str = ""  # Description


class AmenityMaster:
    """
    Master data for property amenities.

    Usage:
        master = AmenityMaster()
        amenity = master.get_amenity("hồ bơi")  # Returns SWIMMING_POOL
        amenities_for_apartment = master.get_amenities_for_property_type("APARTMENT")
    """

    AMENITIES = [
        # Parking
        Amenity(
            code="PARKING",
            standard_name="parking",
            display_name="Chỗ đậu xe",
            aliases=["chỗ đậu xe", "bãi xe", "parking", "garage", "nhà để xe"],
            category=AmenityCategory.PARKING,
            applicable_to=["APARTMENT", "CONDO", "VILLA", "TOWNHOUSE", "OFFICE", "COMMERCIAL"],
            description="Parking space or garage"
        ),
        Amenity(
            code="COVERED_PARKING",
            standard_name="covered_parking",
            display_name="Chỗ đậu xe có mái che",
            aliases=["bãi xe có mái", "parking có mái"],
            category=AmenityCategory.PARKING,
            applicable_to=["APARTMENT", "CONDO", "OFFICE"],
        ),
        Amenity(
            code="UNDERGROUND_PARKING",
            standard_name="underground_parking",
            display_name="Bãi xe hầm",
            aliases=["bãi xe hầm", "hầm xe", "underground parking"],
            category=AmenityCategory.PARKING,
            applicable_to=["APARTMENT", "CONDO", "OFFICE"],
        ),

        # Building amenities
        Amenity(
            code="ELEVATOR",
            standard_name="elevator",
            display_name="Thang máy",
            aliases=["thang máy", "elevator", "lift"],
            category=AmenityCategory.BUILDING,
            applicable_to=["APARTMENT", "CONDO", "OFFICE", "COMMERCIAL"],
            description="Elevator in building"
        ),
        Amenity(
            code="LOBBY",
            standard_name="lobby",
            display_name="Sảnh chính",
            aliases=["sảnh", "lobby", "reception"],
            category=AmenityCategory.BUILDING,
            applicable_to=["APARTMENT", "CONDO", "OFFICE"],
        ),

        # Recreation - Community
        Amenity(
            code="SWIMMING_POOL",
            standard_name="swimming_pool",
            display_name="Hồ bơi",
            aliases=["hồ bơi", "bể bơi", "pool", "swimming pool"],
            category=AmenityCategory.RECREATION,
            applicable_to=["APARTMENT", "CONDO", "VILLA"],
            description="Swimming pool (shared or private)"
        ),
        Amenity(
            code="GYM",
            standard_name="gym",
            display_name="Phòng gym",
            aliases=["gym", "phòng gym", "fitness", "fitness center", "phòng tập"],
            category=AmenityCategory.RECREATION,
            applicable_to=["APARTMENT", "CONDO", "OFFICE"],
            description="Gym/fitness center"
        ),
        Amenity(
            code="PLAYGROUND",
            standard_name="playground",
            display_name="Khu vui chơi trẻ em",
            aliases=["khu vui chơi", "khu vui chơi trẻ em", "playground"],
            category=AmenityCategory.RECREATION,
            applicable_to=["APARTMENT", "CONDO"],
        ),
        Amenity(
            code="TENNIS_COURT",
            standard_name="tennis_court",
            display_name="Sân tennis",
            aliases=["sân tennis", "tennis court"],
            category=AmenityCategory.RECREATION,
            applicable_to=["APARTMENT", "CONDO", "VILLA"],
        ),
        Amenity(
            code="BASKETBALL_COURT",
            standard_name="basketball_court",
            display_name="Sân bóng rổ",
            aliases=["sân bóng rổ", "basketball court"],
            category=AmenityCategory.RECREATION,
            applicable_to=["APARTMENT", "CONDO"],
        ),
        Amenity(
            code="BBQ_AREA",
            standard_name="bbq_area",
            display_name="Khu BBQ",
            aliases=["khu bbq", "khu nướng", "bbq area", "barbecue"],
            category=AmenityCategory.RECREATION,
            applicable_to=["APARTMENT", "CONDO", "VILLA"],
        ),
        Amenity(
            code="CLUBHOUSE",
            standard_name="clubhouse",
            display_name="Clubhouse",
            aliases=["clubhouse", "khu sinh hoạt cộng đồng"],
            category=AmenityCategory.RECREATION,
            applicable_to=["APARTMENT", "CONDO"],
        ),

        # Security
        Amenity(
            code="SECURITY_24_7",
            standard_name="security_24_7",
            display_name="Bảo vệ 24/7",
            aliases=["bảo vệ 24/7", "security 24/7", "an ninh 24/7", "bảo vệ"],
            category=AmenityCategory.SECURITY,
            applicable_to=["APARTMENT", "CONDO", "VILLA", "OFFICE"],
            description="24/7 security guard"
        ),
        Amenity(
            code="CCTV",
            standard_name="cctv",
            display_name="Camera an ninh",
            aliases=["camera an ninh", "cctv", "camera giám sát"],
            category=AmenityCategory.SECURITY,
            applicable_to=["APARTMENT", "CONDO", "VILLA", "TOWNHOUSE", "OFFICE"],
        ),
        Amenity(
            code="ACCESS_CARD",
            standard_name="access_card",
            display_name="Thẻ từ ra vào",
            aliases=["thẻ từ", "access card", "key card"],
            category=AmenityCategory.SECURITY,
            applicable_to=["APARTMENT", "CONDO", "OFFICE"],
        ),
        Amenity(
            code="FINGERPRINT_LOCK",
            standard_name="fingerprint_lock",
            display_name="Khóa vân tay",
            aliases=["khóa vân tay", "fingerprint lock", "vân tay"],
            category=AmenityCategory.SECURITY,
            applicable_to=["APARTMENT", "CONDO", "VILLA", "TOWNHOUSE"],
        ),

        # Unit amenities
        Amenity(
            code="BALCONY",
            standard_name="balcony",
            display_name="Ban công",
            aliases=["ban công", "balcony"],
            category=AmenityCategory.UNIT,
            applicable_to=["APARTMENT", "CONDO"],
        ),
        Amenity(
            code="TERRACE",
            standard_name="terrace",
            display_name="Sân thượng",
            aliases=["sân thượng", "terrace", "rooftop"],
            category=AmenityCategory.UNIT,
            applicable_to=["APARTMENT", "CONDO", "VILLA", "TOWNHOUSE"],
        ),
        Amenity(
            code="STORAGE",
            standard_name="storage",
            display_name="Kho chứa",
            aliases=["kho", "kho chứa", "storage"],
            category=AmenityCategory.UNIT,
            applicable_to=["APARTMENT", "CONDO", "OFFICE"],
        ),

        # Villa-specific luxury amenities
        Amenity(
            code="PRIVATE_POOL",
            standard_name="private_pool",
            display_name="Hồ bơi riêng",
            aliases=["hồ bơi riêng", "bể bơi riêng", "private pool"],
            category=AmenityCategory.LUXURY,
            applicable_to=["VILLA"],
            description="Private swimming pool"
        ),
        Amenity(
            code="WINE_CELLAR",
            standard_name="wine_cellar",
            display_name="Hầm rượu",
            aliases=["hầm rượu", "wine cellar"],
            category=AmenityCategory.LUXURY,
            applicable_to=["VILLA"],
        ),
        Amenity(
            code="HOME_THEATER",
            standard_name="home_theater",
            display_name="Phòng chiếu phim",
            aliases=["phòng chiếu phim", "home theater", "rạp phim riêng"],
            category=AmenityCategory.LUXURY,
            applicable_to=["VILLA"],
        ),
        Amenity(
            code="SAUNA",
            standard_name="sauna",
            display_name="Phòng xông hơi",
            aliases=["phòng xông hơi", "sauna"],
            category=AmenityCategory.LUXURY,
            applicable_to=["VILLA", "APARTMENT", "CONDO"],
        ),
        Amenity(
            code="GARDEN",
            standard_name="garden",
            display_name="Sân vườn",
            aliases=["sân vườn", "vườn", "garden"],
            category=AmenityCategory.UNIT,
            applicable_to=["VILLA", "TOWNHOUSE"],
        ),
        Amenity(
            code="SMART_HOME",
            standard_name="smart_home",
            display_name="Nhà thông minh",
            aliases=["smart home", "nhà thông minh", "home automation"],
            category=AmenityCategory.LUXURY,
            applicable_to=["VILLA", "APARTMENT", "CONDO"],
        ),

        # Utilities (for land)
        Amenity(
            code="WATER_CONNECTION",
            standard_name="water_connection",
            display_name="Có nước máy",
            aliases=["nước máy", "water", "cấp nước"],
            category=AmenityCategory.UTILITIES,
            applicable_to=["LAND", "VILLA", "TOWNHOUSE"],
        ),
        Amenity(
            code="ELECTRICITY_CONNECTION",
            standard_name="electricity_connection",
            display_name="Có điện",
            aliases=["điện", "electricity", "cấp điện"],
            category=AmenityCategory.UTILITIES,
            applicable_to=["LAND", "VILLA", "TOWNHOUSE"],
        ),
        Amenity(
            code="ROAD_ACCESS",
            standard_name="road_access",
            display_name="Có đường vào",
            aliases=["đường vào", "road access", "lộ giới"],
            category=AmenityCategory.UTILITIES,
            applicable_to=["LAND"],
        ),
    ]

    def __init__(self):
        """Initialize amenity master"""
        # Build lookup indices
        self._build_indices()

    def _build_indices(self):
        """Build lookup indices for fast search"""
        # Code -> Amenity
        self.by_code: Dict[str, Amenity] = {
            a.code: a for a in self.AMENITIES
        }

        # Standard name -> Amenity
        self.by_standard_name: Dict[str, Amenity] = {
            a.standard_name: a for a in self.AMENITIES
        }

        # Alias -> Amenity code (for normalization)
        self.alias_to_code: Dict[str, str] = {}
        for amenity in self.AMENITIES:
            # Add standard name
            self.alias_to_code[amenity.standard_name.lower()] = amenity.code
            # Add display name
            self.alias_to_code[amenity.display_name.lower()] = amenity.code
            # Add aliases
            for alias in amenity.aliases:
                self.alias_to_code[alias.lower()] = amenity.code

        # Property type -> Amenities
        self.by_property_type: Dict[str, List[Amenity]] = {}
        for amenity in self.AMENITIES:
            for prop_type in amenity.applicable_to:
                if prop_type not in self.by_property_type:
                    self.by_property_type[prop_type] = []
                self.by_property_type[prop_type].append(amenity)

    def normalize(self, text: str) -> Optional[str]:
        """
        Normalize amenity name to standard code.

        Examples:
            "hồ bơi" -> "SWIMMING_POOL"
            "gym" -> "GYM"
            "thang máy" -> "ELEVATOR"

        Returns:
            Amenity code or None
        """
        text_lower = text.lower().strip()
        return self.alias_to_code.get(text_lower)

    def get_amenity(self, name_or_code: str) -> Optional[Amenity]:
        """
        Get amenity object by name or code.

        Args:
            name_or_code: Amenity name (any alias) or code

        Returns:
            Amenity object or None
        """
        # Try as code first
        if name_or_code.upper() in self.by_code:
            return self.by_code[name_or_code.upper()]

        # Try normalization
        code = self.normalize(name_or_code)
        if code:
            return self.by_code.get(code)

        return None

    def get_amenities_for_property_type(self, property_type_code: str) -> List[Amenity]:
        """
        Get all relevant amenities for a property type.

        Args:
            property_type_code: Property type code (e.g., "APARTMENT", "VILLA")

        Returns:
            List of applicable amenities
        """
        return self.by_property_type.get(property_type_code, [])

    def get_amenities_by_category(self, category: AmenityCategory) -> List[Amenity]:
        """Get all amenities in a category"""
        return [a for a in self.AMENITIES if a.category == category]

    def extract_from_text(self, text: str) -> Dict[str, bool]:
        """
        Extract amenities from free text.

        Args:
            text: Free text (e.g., "có hồ bơi và gym")

        Returns:
            Dictionary of {amenity_standard_name: True} for found amenities
        """
        text_lower = text.lower()
        found_amenities = {}

        for amenity in self.AMENITIES:
            # Check if any alias appears in text
            for alias in [amenity.display_name] + amenity.aliases:
                if alias.lower() in text_lower:
                    found_amenities[amenity.standard_name] = True
                    break

        return found_amenities

    def get_all_amenity_codes(self) -> List[str]:
        """Get list of all amenity codes"""
        return [a.code for a in self.AMENITIES]

    def get_all_standard_names(self) -> List[str]:
        """Get list of all standard names"""
        return [a.standard_name for a in self.AMENITIES]


# Singleton instance
_instance: Optional[AmenityMaster] = None

def get_amenity_master() -> AmenityMaster:
    """Get singleton instance of AmenityMaster"""
    global _instance
    if _instance is None:
        _instance = AmenityMaster()
    return _instance

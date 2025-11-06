"""
Cities Master Data for Vietnam Real Estate

Provides standardized city names and metadata for major Vietnamese cities.
Supports normalization and hierarchical relationship with provinces.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CityTier(str, Enum):
    """City classification by economic development"""
    TIER_1 = "tier_1"  # Major cities: HCMC, Hanoi
    TIER_2 = "tier_2"  # Provincial cities: Da Nang, Can Tho, Hai Phong
    TIER_3 = "tier_3"  # Smaller provincial cities


@dataclass
class City:
    """Standardized city information"""
    code: str  # Unique code (e.g., "HCM", "HN", "DN")
    standard_name: str  # Standard Vietnamese name (e.g., "Hồ Chí Minh")
    full_name: str  # Full official name (e.g., "Thành phố Hồ Chí Minh")
    aliases: List[str]  # Alternative names (e.g., ["Sài Gòn", "TPHCM", "HCM", "Saigon"])
    english_name: str  # English name (e.g., "Ho Chi Minh City")
    province_code: str  # Parent province code
    tier: CityTier  # City tier
    region: str  # Geographic region (Nam Bộ, Bắc Bộ, Trung Bộ)
    population: int  # Population (approximate)
    major_districts: List[str]  # List of major districts


class CityMaster:
    """
    Master data for Vietnamese cities with normalization capabilities.

    Usage:
        master = CityMaster()
        normalized = master.normalize("sài gòn")  # Returns "Hồ Chí Minh"
        city_info = master.get_city("Hồ Chí Minh")
    """

    CITIES = [
        # Tier 1 Cities (Thành phố trực thuộc TW)
        City(
            code="HCM",
            standard_name="Hồ Chí Minh",
            full_name="Thành phố Hồ Chí Minh",
            aliases=[
                "hồ chí minh", "ho chi minh", "hcm", "tphcm", "tp hcm", "tp.hcm",
                "sài gòn", "saigon", "sai gon", "sài gòn", "sg",
                "thành phố hồ chí minh", "thanh pho ho chi minh"
            ],
            english_name="Ho Chi Minh City",
            province_code="79",
            tier=CityTier.TIER_1,
            region="Nam Bộ",
            population=9_000_000,
            major_districts=[
                "Quận 1", "Quận 2", "Quận 3", "Quận 4", "Quận 5",
                "Quận 7", "Quận Bình Thạnh", "Quận Tân Bình",
                "Thành phố Thủ Đức"
            ]
        ),
        City(
            code="HN",
            standard_name="Hà Nội",
            full_name="Thành phố Hà Nội",
            aliases=[
                "hà nội", "ha noi", "hn", "tphn", "tp hà nội", "tp.hà nội",
                "thủ đô", "thu do", "hanoi",
                "thành phố hà nội", "thanh pho ha noi"
            ],
            english_name="Hanoi",
            province_code="01",
            tier=CityTier.TIER_1,
            region="Bắc Bộ",
            population=8_000_000,
            major_districts=[
                "Quận Hoàn Kiếm", "Quận Ba Đình", "Quận Đống Đa",
                "Quận Hai Bà Trưng", "Quận Tây Hồ", "Quận Cầu Giấy",
                "Quận Thanh Xuân", "Quận Long Biên"
            ]
        ),

        # Tier 2 Cities (Thành phố lớn)
        City(
            code="DN",
            standard_name="Đà Nẵng",
            full_name="Thành phố Đà Nẵng",
            aliases=[
                "đà nẵng", "da nang", "dn", "tpdn", "tp đà nẵng",
                "danang", "da nang city",
                "thành phố đà nẵng"
            ],
            english_name="Da Nang",
            province_code="48",
            tier=CityTier.TIER_2,
            region="Trung Bộ",
            population=1_200_000,
            major_districts=[
                "Quận Hải Châu", "Quận Thanh Khê", "Quận Sơn Trà",
                "Quận Ngũ Hành Sơn", "Quận Liên Chiểu", "Quận Cẩm Lệ"
            ]
        ),
        City(
            code="HP",
            standard_name="Hải Phòng",
            full_name="Thành phố Hải Phòng",
            aliases=[
                "hải phòng", "hai phong", "hp", "tphp", "tp hải phòng",
                "haiphong", "hai phong city",
                "thành phố hải phòng"
            ],
            english_name="Hai Phong",
            province_code="31",
            tier=CityTier.TIER_2,
            region="Bắc Bộ",
            population=2_000_000,
            major_districts=[
                "Quận Hồng Bàng", "Quận Ngô Quyền", "Quận Lê Chân",
                "Quận Hải An", "Quận Kiến An", "Quận Đồ Sơn"
            ]
        ),
        City(
            code="CT",
            standard_name="Cần Thơ",
            full_name="Thành phố Cần Thơ",
            aliases=[
                "cần thơ", "can tho", "ct", "tpct", "tp cần thơ",
                "cantho", "can tho city",
                "thành phố cần thơ"
            ],
            english_name="Can Tho",
            province_code="92",
            tier=CityTier.TIER_2,
            region="Nam Bộ",
            population=1_200_000,
            major_districts=[
                "Quận Ninh Kiều", "Quận Bình Thủy", "Quận Cái Răng",
                "Quận Ô Môn", "Quận Thốt Nốt"
            ]
        ),

        # Tier 3 Cities (Thành phố tỉnh)
        City(
            code="BD",
            standard_name="Biên Hòa",
            full_name="Thành phố Biên Hòa",
            aliases=["biên hòa", "bien hoa", "bd", "tp biên hòa"],
            english_name="Bien Hoa",
            province_code="75",  # Đồng Nai
            tier=CityTier.TIER_3,
            region="Nam Bộ",
            population=1_000_000,
            major_districts=["Quận Tân Phong", "Quận Trảng Dài", "Quận Tân Biên"]
        ),
        City(
            code="VT",
            standard_name="Vũng Tàu",
            full_name="Thành phố Vũng Tàu",
            aliases=["vũng tàu", "vung tau", "vt", "tp vũng tàu"],
            english_name="Vung Tau",
            province_code="77",  # Bà Rịa - Vũng Tàu
            tier=CityTier.TIER_3,
            region="Nam Bộ",
            population=500_000,
            major_districts=["Phường 1", "Phường 2", "Phường 3"]
        ),
        City(
            code="NHA_TRANG",
            standard_name="Nha Trang",
            full_name="Thành phố Nha Trang",
            aliases=["nha trang", "nhatrang", "nt", "tp nha trang"],
            english_name="Nha Trang",
            province_code="56",  # Khánh Hòa
            tier=CityTier.TIER_3,
            region="Trung Bộ",
            population=500_000,
            major_districts=["Phường Vĩnh Hải", "Phường Vĩnh Hòa", "Phường Phương Sài"]
        ),
        City(
            code="DA_LAT",
            standard_name="Đà Lạt",
            full_name="Thành phố Đà Lạt",
            aliases=["đà lạt", "da lat", "dalat", "tp đà lạt"],
            english_name="Da Lat",
            province_code="68",  # Lâm Đồng
            tier=CityTier.TIER_3,
            region="Trung Bộ",
            population=300_000,
            major_districts=["Phường 1", "Phường 2", "Phường 3"]
        ),
        City(
            code="HUE",
            standard_name="Huế",
            full_name="Thành phố Huế",
            aliases=["huế", "hue", "tp huế", "thành phố huế"],
            english_name="Hue",
            province_code="46",  # Thừa Thiên Huế
            tier=CityTier.TIER_3,
            region="Trung Bộ",
            population=400_000,
            major_districts=["Phường Vĩnh Ninh", "Phường Phú Hội", "Phường Thuận Hòa"]
        ),
        City(
            code="VIET_TRI",
            standard_name="Việt Trì",
            full_name="Thành phố Việt Trì",
            aliases=["việt trì", "viet tri", "tp việt trì"],
            english_name="Viet Tri",
            province_code="25",  # Phú Thọ
            tier=CityTier.TIER_3,
            region="Bắc Bộ",
            population=300_000,
            major_districts=["Phường Tiên Cát", "Phường Bến Gót"]
        ),
        City(
            code="BMT",
            standard_name="Buôn Ma Thuột",
            full_name="Thành phố Buôn Ma Thuột",
            aliases=["buôn ma thuột", "buon ma thuot", "bmt", "tp buôn ma thuột"],
            english_name="Buon Ma Thuot",
            province_code="66",  # Đắk Lắk
            tier=CityTier.TIER_3,
            region="Trung Bộ",
            population=400_000,
            major_districts=["Phường Tân Lập", "Phường Tân Hòa"]
        ),
    ]

    def __init__(self):
        """Initialize city master with all cities"""
        self.cities = self.CITIES

        # Build lookup indices for fast search
        self._build_indices()

    def _build_indices(self):
        """Build lookup indices for fast normalization"""
        # Standard name -> City
        self.by_standard_name: Dict[str, City] = {
            c.standard_name: c for c in self.cities
        }

        # Code -> City
        self.by_code: Dict[str, City] = {
            c.code: c for c in self.cities
        }

        # Alias -> Standard name (for normalization)
        self.alias_to_standard: Dict[str, str] = {}
        for city in self.cities:
            # Add standard name itself
            self.alias_to_standard[city.standard_name.lower()] = city.standard_name
            # Add full name
            self.alias_to_standard[city.full_name.lower()] = city.standard_name
            # Add all aliases
            for alias in city.aliases:
                self.alias_to_standard[alias.lower()] = city.standard_name

    def normalize(self, text: str) -> Optional[str]:
        """
        Normalize city name from any format to standard format.

        Examples:
            "sài gòn" -> "Hồ Chí Minh"
            "TPHCM" -> "Hồ Chí Minh"
            "hanoi" -> "Hà Nội"
            "da nang" -> "Đà Nẵng"

        Args:
            text: Input text (can be messy)

        Returns:
            Standard city name, or None if not found
        """
        text_lower = text.lower().strip()

        # Direct lookup
        if text_lower in self.alias_to_standard:
            return self.alias_to_standard[text_lower]

        return None

    def get_city(self, name: str) -> Optional[City]:
        """
        Get city object by name (accepts both standard and alias).

        Args:
            name: City name (any format)

        Returns:
            City object or None
        """
        standard_name = self.normalize(name)
        if standard_name:
            return self.by_standard_name.get(standard_name)
        return None

    def get_cities_by_tier(self, tier: CityTier) -> List[City]:
        """Get all cities in a tier"""
        return [c for c in self.cities if c.tier == tier]

    def get_cities_by_region(self, region: str) -> List[City]:
        """
        Get all cities in a region.

        Args:
            region: "Nam Bộ", "Bắc Bộ", or "Trung Bộ"
        """
        return [c for c in self.cities if c.region == region]

    def get_all_standard_names(self) -> List[str]:
        """Get list of all standard city names"""
        return [c.standard_name for c in self.cities]

    def extract_from_text(self, text: str) -> Optional[Tuple[str, City]]:
        """
        Extract city from free text.

        Args:
            text: Free text (e.g., "Tôi muốn mua nhà ở Sài Gòn")

        Returns:
            Tuple of (matched_text, City) or None
        """
        text_lower = text.lower()

        # Try to match each city's patterns
        # Sort by alias length (longest first) to match more specific terms first
        matches = []
        for city in self.cities:
            # Check all aliases
            for alias in [city.full_name, city.standard_name] + city.aliases:
                if alias.lower() in text_lower:
                    matches.append((alias, city, len(alias)))

        # Return the longest match (most specific)
        if matches:
            matches.sort(key=lambda x: x[2], reverse=True)
            return (matches[0][0], matches[0][1])

        return None

    def get_tier_1_cities(self) -> List[City]:
        """Get Tier 1 cities (HCMC, Hanoi)"""
        return self.get_cities_by_tier(CityTier.TIER_1)

    def get_tier_2_cities(self) -> List[City]:
        """Get Tier 2 cities (Da Nang, Hai Phong, Can Tho)"""
        return self.get_cities_by_tier(CityTier.TIER_2)

    def is_major_city(self, city_name: str) -> bool:
        """
        Check if a city is a major city (Tier 1 or 2).

        Args:
            city_name: City name (any format)

        Returns:
            True if Tier 1 or 2, False otherwise
        """
        city = self.get_city(city_name)
        if city:
            return city.tier in [CityTier.TIER_1, CityTier.TIER_2]
        return False


# Singleton instance
_instance: Optional[CityMaster] = None

def get_city_master() -> CityMaster:
    """Get singleton instance of CityMaster"""
    global _instance
    if _instance is None:
        _instance = CityMaster()
    return _instance

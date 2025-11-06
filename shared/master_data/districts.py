"""
District Master Data for Vietnam Real Estate

Provides standardized district names, normalization patterns, and location data.
Supports HCMC (Quận 1-12, Thủ Đức, etc.) and can be extended to Hanoi, Da Nang.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class District:
    """Standardized district information"""
    code: str  # Unique code (e.g., "HCM_Q1", "HCM_Q7")
    standard_name: str  # Standard name (e.g., "Quận 1", "Quận 7")
    aliases: List[str]  # Alternative names (e.g., ["Q1", "Q.1", "quận 1"])
    city: str  # City (e.g., "Hồ Chí Minh", "Hà Nội")
    popular_areas: List[str]  # Popular wards/areas in this district
    tier: int  # District tier (1=premium, 2=mid, 3=affordable)


class DistrictMaster:
    """
    Master data for Vietnamese districts with normalization capabilities.

    Usage:
        master = DistrictMaster()
        normalized = master.normalize("q7")  # Returns "Quận 7"
        district_info = master.get_district("Quận 7")
    """

    # HCMC Districts
    HCMC_DISTRICTS = [
        # Premium Districts (Tier 1)
        District(
            code="HCM_Q1",
            standard_name="Quận 1",
            aliases=["q1", "q.1", "quận 1", "quan 1", "district 1"],
            city="Hồ Chí Minh",
            popular_areas=["Bến Nghé", "Bến Thành", "Đa Kao", "Nguyễn Thái Bình"],
            tier=1
        ),
        District(
            code="HCM_Q2",
            standard_name="Quận 2",
            aliases=["q2", "q.2", "quận 2", "quan 2", "district 2"],
            city="Hồ Chí Minh",
            popular_areas=["Thảo Điền", "An Phú", "Bình An", "Thủ Thiêm"],
            tier=1
        ),
        District(
            code="HCM_Q3",
            standard_name="Quận 3",
            aliases=["q3", "q.3", "quận 3", "quan 3", "district 3"],
            city="Hồ Chí Minh",
            popular_areas=["Võ Thị Sáu", "Phường 1", "Phường 6"],
            tier=1
        ),
        District(
            code="HCM_Q7",
            standard_name="Quận 7",
            aliases=["q7", "q.7", "quận 7", "quan 7", "district 7", "phu my hung", "phú mỹ hưng"],
            city="Hồ Chí Minh",
            popular_areas=["Phú Mỹ Hưng", "Tân Phong", "Tân Hưng", "Tân Quy"],
            tier=1
        ),
        District(
            code="HCM_PHU_NHUAN",
            standard_name="Quận Phú Nhuận",
            aliases=["phú nhuận", "phu nhuan", "quận phú nhuận"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 15", "Phường 13", "Phường 11"],
            tier=1
        ),

        # Mid-tier Districts (Tier 2)
        District(
            code="HCM_Q4",
            standard_name="Quận 4",
            aliases=["q4", "q.4", "quận 4", "quan 4"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 1", "Phường 3", "Phường 6"],
            tier=2
        ),
        District(
            code="HCM_Q5",
            standard_name="Quận 5",
            aliases=["q5", "q.5", "quận 5", "quan 5", "chợ lớn", "cho lon"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 1", "Phường 4", "Phường 5"],
            tier=2
        ),
        District(
            code="HCM_Q6",
            standard_name="Quận 6",
            aliases=["q6", "q.6", "quận 6", "quan 6"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 1", "Phường 4", "Phường 5"],
            tier=2
        ),
        District(
            code="HCM_Q8",
            standard_name="Quận 8",
            aliases=["q8", "q.8", "quận 8", "quan 8"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 1", "Phường 4", "Phường 5"],
            tier=2
        ),
        District(
            code="HCM_Q10",
            standard_name="Quận 10",
            aliases=["q10", "q.10", "quận 10", "quan 10"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 1", "Phường 4", "Phường 5"],
            tier=2
        ),
        District(
            code="HCM_Q11",
            standard_name="Quận 11",
            aliases=["q11", "q.11", "quận 11", "quan 11"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 1", "Phường 4", "Phường 5"],
            tier=2
        ),
        District(
            code="HCM_BINH_THANH",
            standard_name="Quận Bình Thạnh",
            aliases=["bình thạnh", "binh thanh", "quận bình thạnh"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 1", "Phường 2", "Phường 3"],
            tier=2
        ),
        District(
            code="HCM_TAN_BINH",
            standard_name="Quận Tân Bình",
            aliases=["tân bình", "tan binh", "quận tân bình"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 1", "Phường 2", "Phường 3"],
            tier=2
        ),
        District(
            code="HCM_GO_VAP",
            standard_name="Quận Gò Vấp",
            aliases=["gò vấp", "go vap", "quận gò vấp"],
            city="Hồ Chí Minh",
            popular_areas=["Phường 1", "Phường 3", "Phường 6"],
            tier=2
        ),

        # Thủ Đức (New city)
        District(
            code="HCM_THU_DUC",
            standard_name="Thành phố Thủ Đức",
            aliases=["thủ đức", "thu duc", "tp thủ đức", "quận 9", "q9", "q.9", "quận thủ đức"],
            city="Hồ Chí Minh",
            popular_areas=["Thảo Điền", "An Phú", "Cát Lái", "Phước Long B"],
            tier=2
        ),

        # Affordable Districts (Tier 3)
        District(
            code="HCM_Q12",
            standard_name="Quận 12",
            aliases=["q12", "q.12", "quận 12", "quan 12"],
            city="Hồ Chí Minh",
            popular_areas=["Thới An", "Tân Chánh Hiệp"],
            tier=3
        ),
        District(
            code="HCM_TAN_PHU",
            standard_name="Quận Tân Phú",
            aliases=["tân phú", "tan phu", "quận tân phú"],
            city="Hồ Chí Minh",
            popular_areas=["Tân Sơn Nhì", "Phú Thọ Hòa"],
            tier=3
        ),
        District(
            code="HCM_BINH_TAN",
            standard_name="Quận Bình Tân",
            aliases=["bình tân", "binh tan", "quận bình tân"],
            city="Hồ Chí Minh",
            popular_areas=["Bình Hưng Hòa", "Bình Trị Đông"],
            tier=3
        ),
    ]

    # Hanoi Districts (can be extended)
    HANOI_DISTRICTS = [
        District(
            code="HN_HOAN_KIEM",
            standard_name="Quận Hoàn Kiếm",
            aliases=["hoàn kiếm", "hoan kiem", "quận hoàn kiếm"],
            city="Hà Nội",
            popular_areas=["Hàng Bạc", "Hàng Bông", "Hàng Gai"],
            tier=1
        ),
        District(
            code="HN_TAY_HO",
            standard_name="Quận Tây Hồ",
            aliases=["tây hồ", "tay ho", "quận tây hồ"],
            city="Hà Nội",
            popular_areas=["Nhật Tân", "Quảng An", "Yên Phụ"],
            tier=1
        ),
        District(
            code="HN_CAU_GIAY",
            standard_name="Quận Cầu Giấy",
            aliases=["cầu giấy", "cau giay", "quận cầu giấy"],
            city="Hà Nội",
            popular_areas=["Trung Hòa", "Nhân Chính", "Yên Hòa"],
            tier=2
        ),
    ]

    def __init__(self):
        """Initialize district master with all districts"""
        self.districts = self.HCMC_DISTRICTS + self.HANOI_DISTRICTS

        # Build lookup indices for fast search
        self._build_indices()

    def _build_indices(self):
        """Build lookup indices for fast normalization"""
        # Standard name -> District
        self.by_standard_name: Dict[str, District] = {
            d.standard_name: d for d in self.districts
        }

        # Code -> District
        self.by_code: Dict[str, District] = {
            d.code: d for d in self.districts
        }

        # Alias -> Standard name (for normalization)
        self.alias_to_standard: Dict[str, str] = {}
        for district in self.districts:
            # Add standard name itself
            self.alias_to_standard[district.standard_name.lower()] = district.standard_name
            # Add all aliases
            for alias in district.aliases:
                self.alias_to_standard[alias.lower()] = district.standard_name

    def normalize(self, text: str) -> Optional[str]:
        """
        Normalize district name from any format to standard format.

        Examples:
            "q7" -> "Quận 7"
            "Q.7" -> "Quận 7"
            "phu my hung" -> "Quận 7"
            "thủ đức" -> "Thành phố Thủ Đức"

        Args:
            text: Input text (can be messy)

        Returns:
            Standard district name, or None if not found
        """
        text_lower = text.lower().strip()

        # Direct lookup
        if text_lower in self.alias_to_standard:
            return self.alias_to_standard[text_lower]

        # Pattern-based normalization for numbered districts
        # "q 7", "q7", "q.7" -> "Quận 7"
        match = re.search(r'\bq\.?\s*(\d+)\b', text_lower)
        if match:
            number = match.group(1)
            candidate = f"quận {number}"
            if candidate in self.alias_to_standard:
                return self.alias_to_standard[candidate]

        # Pattern for "quận X"
        match = re.search(r'\bquận\s*(\d+)\b', text_lower)
        if match:
            number = match.group(1)
            candidate = f"quận {number}"
            if candidate in self.alias_to_standard:
                return self.alias_to_standard[candidate]

        return None

    def get_district(self, name: str) -> Optional[District]:
        """
        Get district object by name (accepts both standard and alias).

        Args:
            name: District name (any format)

        Returns:
            District object or None
        """
        standard_name = self.normalize(name)
        if standard_name:
            return self.by_standard_name.get(standard_name)
        return None

    def get_districts_by_city(self, city: str) -> List[District]:
        """Get all districts in a city"""
        return [d for d in self.districts if d.city == city]

    def get_districts_by_tier(self, tier: int) -> List[District]:
        """Get all districts in a tier (1=premium, 2=mid, 3=affordable)"""
        return [d for d in self.districts if d.tier == tier]

    def get_all_standard_names(self, city: Optional[str] = None) -> List[str]:
        """Get list of all standard district names"""
        if city:
            return [d.standard_name for d in self.districts if d.city == city]
        return [d.standard_name for d in self.districts]

    def extract_from_text(self, text: str) -> Optional[Tuple[str, District]]:
        """
        Extract district from free text.

        Args:
            text: Free text (e.g., "Tôi muốn mua nhà ở quận 7")

        Returns:
            Tuple of (matched_text, District) or None
        """
        text_lower = text.lower()

        # Try to match each district's patterns
        for district in self.districts:
            # Check standard name
            if district.standard_name.lower() in text_lower:
                return (district.standard_name, district)

            # Check aliases
            for alias in district.aliases:
                if alias in text_lower:
                    return (alias, district)

        # Try regex patterns for numbered districts
        match = re.search(r'\bq\.?\s*(\d+)\b', text_lower)
        if match:
            normalized = self.normalize(match.group(0))
            if normalized:
                district = self.by_standard_name.get(normalized)
                if district:
                    return (match.group(0), district)

        return None


# Singleton instance
_instance: Optional[DistrictMaster] = None

def get_district_master() -> DistrictMaster:
    """Get singleton instance of DistrictMaster"""
    global _instance
    if _instance is None:
        _instance = DistrictMaster()
    return _instance

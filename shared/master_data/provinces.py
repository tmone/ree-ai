"""
Provinces Master Data for Vietnam Real Estate

Provides standardized province names and metadata for all 63 provinces/cities of Vietnam.
Supports normalization and hierarchical relationships.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Province:
    """Standardized province information"""
    code: str  # Official province code (e.g., "01", "79")
    standard_name: str  # Standard Vietnamese name (e.g., "Hà Nội")
    full_name: str  # Full official name (e.g., "Thành phố Hà Nội")
    aliases: List[str]  # Alternative names
    region: str  # Geographic region (Nam Bộ, Bắc Bộ, Trung Bộ)
    sub_region: str  # Sub-region (Đông Nam Bộ, Đồng bằng Sông Hồng, etc.)


class ProvinceMaster:
    """
    Master data for Vietnamese provinces with normalization capabilities.

    Usage:
        master = ProvinceMaster()
        normalized = master.normalize("tp hcm")  # Returns "Hồ Chí Minh"
        province_info = master.get_province("Hồ Chí Minh")
    """

    # 63 provinces/cities of Vietnam
    PROVINCES = [
        # Bắc Bộ - Đồng bằng Sông Hồng
        Province("01", "Hà Nội", "Thành phố Hà Nội", ["hà nội", "ha noi", "hanoi", "hn"], "Bắc Bộ", "Đồng bằng Sông Hồng"),
        Province("26", "Vĩnh Phúc", "Tỉnh Vĩnh Phúc", ["vĩnh phúc", "vinh phuc"], "Bắc Bộ", "Đồng bằng Sông Hồng"),
        Province("27", "Bắc Ninh", "Tỉnh Bắc Ninh", ["bắc ninh", "bac ninh"], "Bắc Bộ", "Đồng bằng Sông Hồng"),
        Province("30", "Hải Dương", "Tỉnh Hải Dương", ["hải dương", "hai duong"], "Bắc Bộ", "Đồng bằng Sông Hồng"),
        Province("31", "Hải Phòng", "Thành phố Hải Phòng", ["hải phòng", "hai phong", "hp"], "Bắc Bộ", "Đồng bằng Sông Hồng"),
        Province("33", "Hưng Yên", "Tỉnh Hưng Yên", ["hưng yên", "hung yen"], "Bắc Bộ", "Đồng bằng Sông Hồng"),
        Province("34", "Thái Bình", "Tỉnh Thái Bình", ["thái bình", "thai binh"], "Bắc Bộ", "Đồng bằng Sông Hồng"),
        Province("35", "Hà Nam", "Tỉnh Hà Nam", ["hà nam", "ha nam"], "Bắc Bộ", "Đồng bằng Sông Hồng"),
        Province("36", "Nam Định", "Tỉnh Nam Định", ["nam định", "nam dinh"], "Bắc Bộ", "Đồng bằng Sông Hồng"),
        Province("37", "Ninh Bình", "Tỉnh Ninh Bình", ["ninh bình", "ninh binh"], "Bắc Bộ", "Đồng bằng Sông Hồng"),

        # Bắc Bộ - Vùng núi phía Bắc
        Province("02", "Hà Giang", "Tỉnh Hà Giang", ["hà giang", "ha giang"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("04", "Cao Bằng", "Tỉnh Cao Bằng", ["cao bằng", "cao bang"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("06", "Bắc Kạn", "Tỉnh Bắc Kạn", ["bắc kạn", "bac kan"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("08", "Tuyên Quang", "Tỉnh Tuyên Quang", ["tuyên quang", "tuyen quang"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("10", "Lào Cai", "Tỉnh Lào Cai", ["lào cai", "lao cai"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("11", "Điện Biên", "Tỉnh Điện Biên", ["điện biên", "dien bien"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("12", "Lai Châu", "Tỉnh Lai Châu", ["lai châu", "lai chau"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("14", "Sơn La", "Tỉnh Sơn La", ["sơn la", "son la"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("15", "Yên Bái", "Tỉnh Yên Bái", ["yên bái", "yen bai"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("17", "Hòa Bình", "Tỉnh Hòa Bình", ["hòa bình", "hoa binh"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("19", "Thái Nguyên", "Tỉnh Thái Nguyên", ["thái nguyên", "thai nguyen"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("20", "Lạng Sơn", "Tỉnh Lạng Sơn", ["lạng sơn", "lang son"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("22", "Quảng Ninh", "Tỉnh Quảng Ninh", ["quảng ninh", "quang ninh"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("24", "Bắc Giang", "Tỉnh Bắc Giang", ["bắc giang", "bac giang"], "Bắc Bộ", "Vùng núi phía Bắc"),
        Province("25", "Phú Thọ", "Tỉnh Phú Thọ", ["phú thọ", "phu tho"], "Bắc Bộ", "Vùng núi phía Bắc"),

        # Trung Bộ - Bắc Trung Bộ
        Province("38", "Thanh Hóa", "Tỉnh Thanh Hóa", ["thanh hóa", "thanh hoa"], "Trung Bộ", "Bắc Trung Bộ"),
        Province("40", "Nghệ An", "Tỉnh Nghệ An", ["nghệ an", "nghe an"], "Trung Bộ", "Bắc Trung Bộ"),
        Province("42", "Hà Tĩnh", "Tỉnh Hà Tĩnh", ["hà tĩnh", "ha tinh"], "Trung Bộ", "Bắc Trung Bộ"),
        Province("44", "Quảng Bình", "Tỉnh Quảng Bình", ["quảng bình", "quang binh"], "Trung Bộ", "Bắc Trung Bộ"),
        Province("45", "Quảng Trị", "Tỉnh Quảng Trị", ["quảng trị", "quang tri"], "Trung Bộ", "Bắc Trung Bộ"),
        Province("46", "Thừa Thiên Huế", "Tỉnh Thừa Thiên Huế", ["thừa thiên huế", "thua thien hue", "huế", "hue"], "Trung Bộ", "Bắc Trung Bộ"),

        # Trung Bộ - Duyên hải Nam Trung Bộ
        Province("48", "Đà Nẵng", "Thành phố Đà Nẵng", ["đà nẵng", "da nang", "danang", "dn"], "Trung Bộ", "Duyên hải Nam Trung Bộ"),
        Province("49", "Quảng Nam", "Tỉnh Quảng Nam", ["quảng nam", "quang nam"], "Trung Bộ", "Duyên hải Nam Trung Bộ"),
        Province("51", "Quảng Ngãi", "Tỉnh Quảng Ngãi", ["quảng ngãi", "quang ngai"], "Trung Bộ", "Duyên hải Nam Trung Bộ"),
        Province("52", "Bình Định", "Tỉnh Bình Định", ["bình định", "binh dinh"], "Trung Bộ", "Duyên hải Nam Trung Bộ"),
        Province("54", "Phú Yên", "Tỉnh Phú Yên", ["phú yên", "phu yen"], "Trung Bộ", "Duyên hải Nam Trung Bộ"),
        Province("56", "Khánh Hòa", "Tỉnh Khánh Hòa", ["khánh hòa", "khanh hoa", "nha trang"], "Trung Bộ", "Duyên hải Nam Trung Bộ"),
        Province("58", "Ninh Thuận", "Tỉnh Ninh Thuận", ["ninh thuận", "ninh thuan"], "Trung Bộ", "Duyên hải Nam Trung Bộ"),
        Province("60", "Bình Thuận", "Tỉnh Bình Thuận", ["bình thuận", "binh thuan"], "Trung Bộ", "Duyên hải Nam Trung Bộ"),

        # Trung Bộ - Tây Nguyên
        Province("62", "Kon Tum", "Tỉnh Kon Tum", ["kon tum"], "Trung Bộ", "Tây Nguyên"),
        Province("64", "Gia Lai", "Tỉnh Gia Lai", ["gia lai"], "Trung Bộ", "Tây Nguyên"),
        Province("66", "Đắk Lắk", "Tỉnh Đắk Lắk", ["đắk lắk", "dak lak", "daklak"], "Trung Bộ", "Tây Nguyên"),
        Province("67", "Đắk Nông", "Tỉnh Đắk Nông", ["đắk nông", "dak nong"], "Trung Bộ", "Tây Nguyên"),
        Province("68", "Lâm Đồng", "Tỉnh Lâm Đồng", ["lâm đồng", "lam dong", "đà lạt", "da lat"], "Trung Bộ", "Tây Nguyên"),

        # Nam Bộ - Đông Nam Bộ
        Province("70", "Bình Phước", "Tỉnh Bình Phước", ["bình phước", "binh phuoc"], "Nam Bộ", "Đông Nam Bộ"),
        Province("72", "Tây Ninh", "Tỉnh Tây Ninh", ["tây ninh", "tay ninh"], "Nam Bộ", "Đông Nam Bộ"),
        Province("74", "Bình Dương", "Tỉnh Bình Dương", ["bình dương", "binh duong"], "Nam Bộ", "Đông Nam Bộ"),
        Province("75", "Đồng Nai", "Tỉnh Đồng Nai", ["đồng nai", "dong nai", "biên hòa", "bien hoa"], "Nam Bộ", "Đông Nam Bộ"),
        Province("77", "Bà Rịa - Vũng Tàu", "Tỉnh Bà Rịa - Vũng Tàu", ["bà rịa vũng tàu", "ba ria vung tau", "vũng tàu", "vung tau"], "Nam Bộ", "Đông Nam Bộ"),
        Province("79", "Hồ Chí Minh", "Thành phố Hồ Chí Minh", ["hồ chí minh", "ho chi minh", "hcm", "tphcm", "tp hcm", "tp.hcm", "sài gòn", "saigon"], "Nam Bộ", "Đông Nam Bộ"),

        # Nam Bộ - Đồng bằng Sông Cửu Long
        Province("80", "Long An", "Tỉnh Long An", ["long an"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("82", "Tiền Giang", "Tỉnh Tiền Giang", ["tiền giang", "tien giang"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("83", "Bến Tre", "Tỉnh Bến Tre", ["bến tre", "ben tre"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("84", "Trà Vinh", "Tỉnh Trà Vinh", ["trà vinh", "tra vinh"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("86", "Vĩnh Long", "Tỉnh Vĩnh Long", ["vĩnh long", "vinh long"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("87", "Đồng Tháp", "Tỉnh Đồng Tháp", ["đồng tháp", "dong thap"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("89", "An Giang", "Tỉnh An Giang", ["an giang"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("91", "Kiên Giang", "Tỉnh Kiên Giang", ["kiên giang", "kien giang"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("92", "Cần Thơ", "Thành phố Cần Thơ", ["cần thơ", "can tho", "cantho", "ct"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("93", "Hậu Giang", "Tỉnh Hậu Giang", ["hậu giang", "hau giang"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("94", "Sóc Trăng", "Tỉnh Sóc Trăng", ["sóc trăng", "soc trang"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("95", "Bạc Liêu", "Tỉnh Bạc Liêu", ["bạc liêu", "bac lieu"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
        Province("96", "Cà Mau", "Tỉnh Cà Mau", ["cà mau", "ca mau"], "Nam Bộ", "Đồng bằng Sông Cửu Long"),
    ]

    def __init__(self):
        """Initialize province master with all provinces"""
        self.provinces = self.PROVINCES

        # Build lookup indices for fast search
        self._build_indices()

    def _build_indices(self):
        """Build lookup indices for fast normalization"""
        # Standard name -> Province
        self.by_standard_name: Dict[str, Province] = {
            p.standard_name: p for p in self.provinces
        }

        # Code -> Province
        self.by_code: Dict[str, Province] = {
            p.code: p for p in self.provinces
        }

        # Alias -> Standard name (for normalization)
        self.alias_to_standard: Dict[str, str] = {}
        for province in self.provinces:
            # Add standard name itself
            self.alias_to_standard[province.standard_name.lower()] = province.standard_name
            # Add full name
            self.alias_to_standard[province.full_name.lower()] = province.standard_name
            # Add all aliases
            for alias in province.aliases:
                self.alias_to_standard[alias.lower()] = province.standard_name

    def normalize(self, text: str) -> Optional[str]:
        """
        Normalize province name from any format to standard format.

        Examples:
            "tphcm" -> "Hồ Chí Minh"
            "ha noi" -> "Hà Nội"
            "da nang" -> "Đà Nẵng"

        Args:
            text: Input text (can be messy)

        Returns:
            Standard province name, or None if not found
        """
        text_lower = text.lower().strip()

        # Direct lookup
        if text_lower in self.alias_to_standard:
            return self.alias_to_standard[text_lower]

        return None

    def get_province(self, name: str) -> Optional[Province]:
        """
        Get province object by name (accepts both standard and alias).

        Args:
            name: Province name (any format)

        Returns:
            Province object or None
        """
        standard_name = self.normalize(name)
        if standard_name:
            return self.by_standard_name.get(standard_name)
        return None

    def get_provinces_by_region(self, region: str) -> List[Province]:
        """
        Get all provinces in a region.

        Args:
            region: "Nam Bộ", "Bắc Bộ", or "Trung Bộ"
        """
        return [p for p in self.provinces if p.region == region]

    def get_provinces_by_sub_region(self, sub_region: str) -> List[Province]:
        """Get all provinces in a sub-region"""
        return [p for p in self.provinces if p.sub_region == sub_region]

    def get_all_standard_names(self) -> List[str]:
        """Get list of all standard province names"""
        return [p.standard_name for p in self.provinces]

    def extract_from_text(self, text: str) -> Optional[Tuple[str, Province]]:
        """
        Extract province from free text.

        Args:
            text: Free text

        Returns:
            Tuple of (matched_text, Province) or None
        """
        text_lower = text.lower()

        # Try to match each province's patterns
        # Sort by alias length (longest first) to match more specific terms first
        matches = []
        for province in self.provinces:
            # Check all aliases
            for alias in [province.full_name, province.standard_name] + province.aliases:
                if alias.lower() in text_lower:
                    matches.append((alias, province, len(alias)))

        # Return the longest match (most specific)
        if matches:
            matches.sort(key=lambda x: x[2], reverse=True)
            return (matches[0][0], matches[0][1])

        return None

    def get_major_provinces(self) -> List[Province]:
        """
        Get list of major provinces (5 central cities).

        Returns provinces: Hà Nội, Hồ Chí Minh, Đà Nẵng, Hải Phòng, Cần Thơ
        """
        major_codes = ["01", "79", "48", "31", "92"]
        return [self.by_code[code] for code in major_codes if code in self.by_code]


# Singleton instance
_instance: Optional[ProvinceMaster] = None

def get_province_master() -> ProvinceMaster:
    """Get singleton instance of ProvinceMaster"""
    global _instance
    if _instance is None:
        _instance = ProvinceMaster()
    return _instance

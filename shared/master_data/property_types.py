"""
Property Type Master Data with Attribute Schemas

Defines all property types and their specific attributes.
This is CRITICAL for extraction accuracy - each property type has different attributes!

Example:
- Căn hộ: bedrooms, bathrooms, view, balcony_direction
- Biệt thự: bedrooms, bathrooms, land_area, building_area, garden, wine_cellar
- Đất: land_area, zoning, street_frontage, alley_width
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum


class AttributeType(str, Enum):
    """Data types for attributes"""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    ENUM = "enum"
    LIST_STRING = "list_string"


@dataclass
class AttributeDefinition:
    """
    Definition of a single attribute.

    Example:
        AttributeDefinition(
            name="bedrooms",
            type=AttributeType.INTEGER,
            required=True,
            description="Number of bedrooms",
            aliases=["phòng ngủ", "pn", "bedroom"],
            min_value=1,
            max_value=10
        )
    """
    name: str  # Standard attribute name (e.g., "bedrooms")
    type: AttributeType  # Data type
    required: bool = False  # Is this attribute required?
    description: str = ""  # Human-readable description
    aliases: List[str] = field(default_factory=list)  # Alternative names
    enum_values: Optional[List[str]] = None  # For ENUM type
    min_value: Optional[float] = None  # For INTEGER/FLOAT
    max_value: Optional[float] = None  # For INTEGER/FLOAT
    default_value: Any = None  # Default value if not extracted
    examples: List[str] = field(default_factory=list)  # Example values


@dataclass
class PropertyType:
    """
    Definition of a property type with its specific attributes.
    """
    code: str  # Unique code (e.g., "APARTMENT", "VILLA")
    standard_name: str  # Standard Vietnamese name (e.g., "căn hộ", "biệt thự")
    aliases: List[str]  # Alternative names
    description: str  # Description
    required_attributes: List[str]  # Required attribute names
    optional_attributes: List[str]  # Optional attribute names
    all_attributes: Dict[str, AttributeDefinition] = field(default_factory=dict)  # All attributes with definitions


class PropertyTypeMaster:
    """
    Master data for property types with complete attribute schemas.

    Usage:
        master = PropertyTypeMaster()
        prop_type = master.get_property_type("căn hộ")
        required_attrs = prop_type.required_attributes
        schema = master.get_attribute_schema("APARTMENT")
    """

    # Common attributes shared across all property types
    COMMON_ATTRIBUTES = {
        "title": AttributeDefinition(
            name="title",
            type=AttributeType.STRING,
            required=True,
            description="Property title/name",
            aliases=["tiêu đề", "tên"],
            examples=["Căn hộ 2PN quận 7", "Biệt thự Phú Mỹ Hưng"]
        ),
        "description": AttributeDefinition(
            name="description",
            type=AttributeType.STRING,
            required=True,
            description="Full property description",
            aliases=["mô tả", "thông tin"],
        ),
        "price": AttributeDefinition(
            name="price",
            type=AttributeType.FLOAT,
            required=True,
            description="Price in VND",
            aliases=["giá", "giá bán", "giá cho thuê"],
            min_value=0,
            examples=["3000000000", "5.5 tỷ", "25 triệu/tháng"]
        ),
        "district": AttributeDefinition(
            name="district",
            type=AttributeType.STRING,
            required=True,
            description="District/Area",
            aliases=["quận", "khu vực", "địa điểm"],
            examples=["Quận 7", "Quận 2", "Thành phố Thủ Đức"]
        ),
        "ward": AttributeDefinition(
            name="ward",
            type=AttributeType.STRING,
            required=False,
            description="Ward (Phường)",
            aliases=["phường", "p"],
            examples=["Phường 1", "Tân Phong"]
        ),
        "street": AttributeDefinition(
            name="street",
            type=AttributeType.STRING,
            required=False,
            description="Street name",
            aliases=["đường", "đ"],
            examples=["Nguyễn Văn Linh", "Huỳnh Tấn Phát"]
        ),
        "project_name": AttributeDefinition(
            name="project_name",
            type=AttributeType.STRING,
            required=False,
            description="Project/Building name",
            aliases=["dự án", "tòa nhà", "chung cư"],
            examples=["Vinhomes Central Park", "Masteri Thảo Điền"]
        ),
        "latitude": AttributeDefinition(
            name="latitude",
            type=AttributeType.FLOAT,
            required=False,
            description="Latitude coordinate for map",
            aliases=["vĩ độ", "lat"],
            min_value=-90,
            max_value=90,
            examples=["10.7769", "10.8231"]
        ),
        "longitude": AttributeDefinition(
            name="longitude",
            type=AttributeType.FLOAT,
            required=False,
            description="Longitude coordinate for map",
            aliases=["kinh độ", "lng", "long"],
            min_value=-180,
            max_value=180,
            examples=["106.7009", "106.6297"]
        ),
    }

    # Apartment/Condo specific attributes
    APARTMENT_SPECIFIC = {
        "bedrooms": AttributeDefinition(
            name="bedrooms",
            type=AttributeType.INTEGER,
            required=True,
            description="Number of bedrooms",
            aliases=["phòng ngủ", "pn", "bedroom"],
            min_value=0,  # Studio = 0
            max_value=10,
            examples=["0 (studio)", "2PN", "3 phòng ngủ"]
        ),
        "bathrooms": AttributeDefinition(
            name="bathrooms",
            type=AttributeType.INTEGER,
            required=True,
            description="Number of bathrooms",
            aliases=["phòng tắm", "wc", "toilet"],
            min_value=1,
            max_value=10,
            examples=["1WC", "2 phòng tắm"]
        ),
        "area": AttributeDefinition(
            name="area",
            type=AttributeType.FLOAT,
            required=True,
            description="Floor area in m²",
            aliases=["diện tích", "dt", "m2"],
            min_value=20,
            max_value=500,
            examples=["50m²", "95m²", "150m2"]
        ),
        "floor": AttributeDefinition(
            name="floor",
            type=AttributeType.INTEGER,
            required=False,
            description="Floor number",
            aliases=["tầng", "lầu"],
            min_value=1,
            max_value=100,
            examples=["Tầng 15", "Lầu 20"]
        ),
        "view": AttributeDefinition(
            name="view",
            type=AttributeType.ENUM,
            required=False,
            description="View from apartment",
            aliases=["hướng view", "tầm nhìn"],
            enum_values=["city_view", "river_view", "park_view", "pool_view", "no_view"],
            examples=["View sông", "View thành phố", "View công viên"]
        ),
        "balcony_direction": AttributeDefinition(
            name="balcony_direction",
            type=AttributeType.ENUM,
            required=False,
            description="Balcony direction",
            aliases=["hướng ban công", "hướng"],
            enum_values=["Đông", "Tây", "Nam", "Bắc", "Đông Nam", "Đông Bắc", "Tây Nam", "Tây Bắc"],
            examples=["Hướng Đông", "Ban công hướng Nam"]
        ),
        "furniture": AttributeDefinition(
            name="furniture",
            type=AttributeType.ENUM,
            required=False,
            description="Furniture status",
            aliases=["nội thất"],
            enum_values=["full", "partial", "empty", "negotiable"],
            examples=["Full nội thất", "Nội thất cơ bản", "Không nội thất"]
        ),
    }

    # Villa specific attributes
    VILLA_SPECIFIC = {
        "bedrooms": AttributeDefinition(
            name="bedrooms",
            type=AttributeType.INTEGER,
            required=True,
            description="Number of bedrooms",
            aliases=["phòng ngủ", "pn"],
            min_value=2,
            max_value=20,
        ),
        "bathrooms": AttributeDefinition(
            name="bathrooms",
            type=AttributeType.INTEGER,
            required=True,
            description="Number of bathrooms",
            aliases=["phòng tắm", "wc"],
            min_value=2,
            max_value=20,
        ),
        "land_area": AttributeDefinition(
            name="land_area",
            type=AttributeType.FLOAT,
            required=True,
            description="Total land area in m²",
            aliases=["diện tích đất", "dt đất"],
            min_value=100,
            max_value=5000,
            examples=["200m²", "300m² đất"]
        ),
        "building_area": AttributeDefinition(
            name="building_area",
            type=AttributeType.FLOAT,
            required=True,
            description="Building floor area in m²",
            aliases=["diện tích xây dựng", "dt xây dựng"],
            min_value=80,
            max_value=3000,
            examples=["150m² xây dựng"]
        ),
        "floors": AttributeDefinition(
            name="floors",
            type=AttributeType.INTEGER,
            required=True,
            description="Number of floors",
            aliases=["số tầng", "tầng"],
            min_value=1,
            max_value=10,
            examples=["2 tầng", "3 lầu"]
        ),
        "garden": AttributeDefinition(
            name="garden",
            type=AttributeType.BOOLEAN,
            required=False,
            description="Has private garden",
            aliases=["sân vườn", "vườn"],
            examples=["Có vườn", "Sân vườn rộng"]
        ),
        "garden_area": AttributeDefinition(
            name="garden_area",
            type=AttributeType.FLOAT,
            required=False,
            description="Garden area in m²",
            aliases=["diện tích vườn"],
            min_value=10,
            max_value=1000,
            examples=["50m² vườn", "Vườn 100m²"]
        ),
        "swimming_pool": AttributeDefinition(
            name="swimming_pool",
            type=AttributeType.BOOLEAN,
            required=False,
            description="Has private swimming pool",
            aliases=["hồ bơi riêng", "bể bơi"],
        ),
        "garage": AttributeDefinition(
            name="garage",
            type=AttributeType.BOOLEAN,
            required=False,
            description="Has garage",
            aliases=["nhà để xe", "garage"],
        ),
        "garage_capacity": AttributeDefinition(
            name="garage_capacity",
            type=AttributeType.INTEGER,
            required=False,
            description="Number of cars garage can hold",
            aliases=["chỗ đậu xe"],
            min_value=1,
            max_value=10,
            examples=["Garage 2 xe", "Chỗ đậu 4 ô tô"]
        ),
        "wine_cellar": AttributeDefinition(
            name="wine_cellar",
            type=AttributeType.BOOLEAN,
            required=False,
            description="Has wine cellar",
            aliases=["hầm rượu"],
        ),
        "rooftop_terrace": AttributeDefinition(
            name="rooftop_terrace",
            type=AttributeType.BOOLEAN,
            required=False,
            description="Has rooftop terrace",
            aliases=["sân thượng", "rooftop"],
        ),
    }

    # Townhouse (Nhà phố) specific attributes
    TOWNHOUSE_SPECIFIC = {
        "bedrooms": AttributeDefinition(
            name="bedrooms",
            type=AttributeType.INTEGER,
            required=True,
            description="Number of bedrooms",
            aliases=["phòng ngủ", "pn"],
            min_value=2,
            max_value=10,
        ),
        "bathrooms": AttributeDefinition(
            name="bathrooms",
            type=AttributeType.INTEGER,
            required=True,
            description="Number of bathrooms",
            aliases=["phòng tắm", "wc"],
            min_value=1,
            max_value=10,
        ),
        "land_area": AttributeDefinition(
            name="land_area",
            type=AttributeType.FLOAT,
            required=True,
            description="Total land area in m²",
            aliases=["diện tích đất", "dt đất"],
            min_value=40,
            max_value=500,
        ),
        "building_area": AttributeDefinition(
            name="building_area",
            type=AttributeType.FLOAT,
            required=False,
            description="Building floor area in m²",
            aliases=["diện tích xây dựng", "dt xây dựng"],
            min_value=40,
            max_value=500,
        ),
        "facade_width": AttributeDefinition(
            name="facade_width",
            type=AttributeType.FLOAT,
            required=False,
            description="Street frontage width in meters",
            aliases=["mặt tiền"],
            min_value=3,
            max_value=30,
            examples=["Mặt tiền 4m"]
        ),
        "width": AttributeDefinition(
            name="width",
            type=AttributeType.FLOAT,
            required=False,
            description="Lot width in meters",
            aliases=["ngang", "chiều ngang", "rộng", "chiều rộng"],
            min_value=3,
            max_value=30,
            examples=["Ngang 5m", "Rộng 4m", "Chiều rộng 6m"]
        ),
        "depth": AttributeDefinition(
            name="depth",
            type=AttributeType.FLOAT,
            required=False,
            description="Lot depth in meters",
            aliases=["chiều sâu", "dài", "chiều dài"],
            min_value=5,
            max_value=50,
            examples=["Dài 20m", "Chiều sâu 15m", "Chiều dài 18m"]
        ),
        "floors": AttributeDefinition(
            name="floors",
            type=AttributeType.INTEGER,
            required=True,
            description="Number of floors",
            aliases=["số tầng", "tầng", "lầu"],
            min_value=1,
            max_value=10,
            examples=["3 tầng", "1 trệt 2 lầu"]
        ),
        "alley_width": AttributeDefinition(
            name="alley_width",
            type=AttributeType.FLOAT,
            required=False,
            description="Alley width in meters (if in alley)",
            aliases=["hẻm", "hẻm xe hơi"],
            min_value=1,
            max_value=20,
            examples=["Hẻm 4m", "Hẻm xe hơi"]
        ),
        "street_access": AttributeDefinition(
            name="street_access",
            type=AttributeType.BOOLEAN,
            required=False,
            description="Direct street access (not in alley)",
            aliases=["mặt tiền đường", "đường lớn"],
            default_value=False,
        ),
    }

    # Land (Đất) specific attributes
    LAND_SPECIFIC = {
        "land_area": AttributeDefinition(
            name="land_area",
            type=AttributeType.FLOAT,
            required=True,
            description="Land area in m²",
            aliases=["diện tích", "dt"],
            min_value=50,
            max_value=100000,
        ),
        "facade_width": AttributeDefinition(
            name="facade_width",
            type=AttributeType.FLOAT,
            required=False,
            description="Street frontage width in meters",
            aliases=["mặt tiền"],
            min_value=3,
            max_value=100,
        ),
        "width": AttributeDefinition(
            name="width",
            type=AttributeType.FLOAT,
            required=False,
            description="Lot width in meters",
            aliases=["ngang", "chiều ngang", "rộng", "chiều rộng"],
            min_value=3,
            max_value=100,
            examples=["Ngang 10m", "Rộng 8m"]
        ),
        "depth": AttributeDefinition(
            name="depth",
            type=AttributeType.FLOAT,
            required=False,
            description="Lot depth in meters",
            aliases=["chiều sâu", "dài", "chiều dài"],
            min_value=5,
            max_value=500,
        ),
        "zoning": AttributeDefinition(
            name="zoning",
            type=AttributeType.ENUM,
            required=False,
            description="Land zoning classification",
            aliases=["phân vùng", "loại đất"],
            enum_values=["residential", "commercial", "industrial", "agricultural", "mixed"],
            examples=["Đất thổ cư", "Đất thương mại", "Đất nông nghiệp"]
        ),
        "street_access": AttributeDefinition(
            name="street_access",
            type=AttributeType.BOOLEAN,
            required=False,
            description="Direct street access",
            aliases=["mặt tiền đường"],
        ),
        "corner_lot": AttributeDefinition(
            name="corner_lot",
            type=AttributeType.BOOLEAN,
            required=False,
            description="Corner lot (2 street frontages)",
            aliases=["đất góc", "2 mặt tiền"],
        ),
    }

    # Commercial (Văn phòng, mặt bằng) specific attributes
    COMMERCIAL_SPECIFIC = {
        "area": AttributeDefinition(
            name="area",
            type=AttributeType.FLOAT,
            required=True,
            description="Floor area in m²",
            aliases=["diện tích", "dt"],
            min_value=30,
            max_value=5000,
        ),
        "floor": AttributeDefinition(
            name="floor",
            type=AttributeType.INTEGER,
            required=False,
            description="Floor number",
            aliases=["tầng"],
            min_value=1,
            max_value=100,
        ),
        "office_layout": AttributeDefinition(
            name="office_layout",
            type=AttributeType.ENUM,
            required=False,
            description="Office layout type",
            aliases=["kiểu văn phòng"],
            enum_values=["open_space", "partitioned", "private_rooms", "mixed"],
            examples=["Văn phòng trống", "Đã chia phòng"]
        ),
        "meeting_rooms": AttributeDefinition(
            name="meeting_rooms",
            type=AttributeType.INTEGER,
            required=False,
            description="Number of meeting rooms",
            aliases=["phòng họp"],
            min_value=0,
            max_value=20,
        ),
    }

    # Property type definitions
    PROPERTY_TYPES = [
        PropertyType(
            code="APARTMENT",
            standard_name="căn hộ",
            aliases=["can ho", "apartment", "condo", "flat"],
            description="Apartment in a building (căn hộ trong chung cư)",
            required_attributes=["title", "price", "district", "bedrooms", "bathrooms", "area"],
            optional_attributes=["ward", "street", "project_name", "floor", "view", "balcony_direction", "furniture"],
        ),
        PropertyType(
            code="CONDO",
            standard_name="chung cư",
            aliases=["chung cu", "condominium"],
            description="Condominium (same as apartment in Vietnamese context)",
            required_attributes=["title", "price", "district", "bedrooms", "bathrooms", "area"],
            optional_attributes=["ward", "street", "project_name", "floor", "view", "balcony_direction", "furniture"],
        ),
        PropertyType(
            code="VILLA",
            standard_name="biệt thự",
            aliases=["biet thu", "villa"],
            description="Villa (standalone house with land)",
            required_attributes=["title", "price", "district", "bedrooms", "bathrooms", "land_area", "building_area", "floors"],
            optional_attributes=["ward", "street", "project_name", "garden", "garden_area", "swimming_pool", "garage", "garage_capacity", "wine_cellar", "rooftop_terrace"],
        ),
        PropertyType(
            code="TOWNHOUSE",
            standard_name="nhà phố",
            aliases=["nha pho", "townhouse", "row house"],
            description="Townhouse (narrow urban house)",
            required_attributes=["title", "price", "district", "bedrooms", "bathrooms", "land_area", "floors"],
            optional_attributes=["ward", "street", "building_area", "facade_width", "width", "depth", "alley_width", "street_access", "latitude", "longitude"],
        ),
        PropertyType(
            code="LAND",
            standard_name="đất",
            aliases=["dat", "dat nen", "land"],
            description="Land (vacant land for development)",
            required_attributes=["title", "price", "district", "land_area"],
            optional_attributes=["ward", "street", "facade_width", "width", "depth", "zoning", "street_access", "corner_lot", "latitude", "longitude"],
        ),
        PropertyType(
            code="OFFICE",
            standard_name="văn phòng",
            aliases=["van phong", "office"],
            description="Office space (văn phòng)",
            required_attributes=["title", "price", "district", "area"],
            optional_attributes=["ward", "street", "project_name", "floor", "office_layout", "meeting_rooms"],
        ),
        PropertyType(
            code="COMMERCIAL",
            standard_name="mặt bằng",
            aliases=["mat bang", "commercial space", "shop"],
            description="Commercial space/shop (mặt bằng kinh doanh)",
            required_attributes=["title", "price", "district", "area"],
            optional_attributes=["ward", "street", "floor", "facade_width"],
        ),
    ]

    def __init__(self):
        """Initialize property type master"""
        # Build attribute definitions for each property type
        self._build_property_schemas()

        # Build lookup indices
        self._build_indices()

    def _build_property_schemas(self):
        """Build complete attribute schemas for each property type"""
        for prop_type in self.PROPERTY_TYPES:
            # Start with common attributes
            all_attrs = self.COMMON_ATTRIBUTES.copy()

            # Add type-specific attributes
            if prop_type.code in ["APARTMENT", "CONDO"]:
                all_attrs.update(self.APARTMENT_SPECIFIC)
            elif prop_type.code == "VILLA":
                all_attrs.update(self.VILLA_SPECIFIC)
            elif prop_type.code == "TOWNHOUSE":
                all_attrs.update(self.TOWNHOUSE_SPECIFIC)
            elif prop_type.code == "LAND":
                all_attrs.update(self.LAND_SPECIFIC)
            elif prop_type.code in ["OFFICE", "COMMERCIAL"]:
                all_attrs.update(self.COMMERCIAL_SPECIFIC)

            prop_type.all_attributes = all_attrs

    def _build_indices(self):
        """Build lookup indices"""
        # Standard name -> PropertyType
        self.by_standard_name: Dict[str, PropertyType] = {
            pt.standard_name: pt for pt in self.PROPERTY_TYPES
        }

        # Code -> PropertyType
        self.by_code: Dict[str, PropertyType] = {
            pt.code: pt for pt in self.PROPERTY_TYPES
        }

        # Alias -> Standard name
        self.alias_to_standard: Dict[str, str] = {}
        for pt in self.PROPERTY_TYPES:
            # Add standard name
            self.alias_to_standard[pt.standard_name.lower()] = pt.standard_name
            # Add aliases
            for alias in pt.aliases:
                self.alias_to_standard[alias.lower()] = pt.standard_name

    def normalize(self, text: str) -> Optional[str]:
        """
        Normalize property type name to standard format.

        Examples:
            "can ho" -> "căn hộ"
            "apartment" -> "căn hộ"
            "villa" -> "biệt thự"
        """
        text_lower = text.lower().strip()
        return self.alias_to_standard.get(text_lower)

    def get_property_type(self, name: str) -> Optional[PropertyType]:
        """
        Get property type object by name (accepts both standard and alias).
        """
        standard_name = self.normalize(name)
        if standard_name:
            return self.by_standard_name.get(standard_name)
        return None

    def get_attribute_schema(self, property_type_name: str) -> Dict[str, AttributeDefinition]:
        """
        Get complete attribute schema for a property type.

        Returns all attributes (required + optional) with their definitions.
        """
        prop_type = self.get_property_type(property_type_name)
        if prop_type:
            return prop_type.all_attributes
        return {}

    def get_required_attributes(self, property_type_name: str) -> List[str]:
        """Get list of required attribute names"""
        prop_type = self.get_property_type(property_type_name)
        if prop_type:
            return prop_type.required_attributes
        return []

    def get_all_property_types(self) -> List[str]:
        """Get list of all standard property type names"""
        return [pt.standard_name for pt in self.PROPERTY_TYPES]


# Singleton instance
_instance: Optional[PropertyTypeMaster] = None

def get_property_type_master() -> PropertyTypeMaster:
    """Get singleton instance of PropertyTypeMaster"""
    global _instance
    if _instance is None:
        _instance = PropertyTypeMaster()
    return _instance

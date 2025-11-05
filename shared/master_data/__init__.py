"""
Master Data Module for Real Estate Domain

This module provides centralized, standardized master data for:
- Cities and provinces (Vietnam's administrative divisions)
- Districts and locations (HCMC + other cities)
- Property types with their specific attributes
- Amenities and features
- Price ranges and validation rules
- Units of measurement (area, price, distance, count)

All extraction services should use this master data instead of hard-coding values.
"""

from .cities import CityMaster, get_city_master
from .provinces import ProvinceMaster, get_province_master
from .districts import DistrictMaster, get_district_master
from .property_types import PropertyTypeMaster, get_property_type_master
from .amenities import AmenityMaster, get_amenity_master
from .price_ranges import PriceRangeMaster, get_price_range_master
from .units import UnitMaster, get_unit_master
from .attribute_schema import AttributeSchema, get_attribute_schema

__all__ = [
    # Masters
    "CityMaster",
    "ProvinceMaster",
    "DistrictMaster",
    "PropertyTypeMaster",
    "AmenityMaster",
    "PriceRangeMaster",
    "UnitMaster",
    "AttributeSchema",
    # Singleton getters
    "get_city_master",
    "get_province_master",
    "get_district_master",
    "get_property_type_master",
    "get_amenity_master",
    "get_price_range_master",
    "get_unit_master",
    "get_attribute_schema",
]

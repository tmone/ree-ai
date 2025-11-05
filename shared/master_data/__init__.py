"""
Master Data Module for Real Estate Domain

This module provides centralized, standardized master data for:
- Districts and locations (HCMC + other cities)
- Property types with their specific attributes
- Amenities and features
- Price ranges and validation rules

All extraction services should use this master data instead of hard-coding values.
"""

from .districts import DistrictMaster, get_district_master
from .property_types import PropertyTypeMaster, get_property_type_master
from .amenities import AmenityMaster, get_amenity_master
from .price_ranges import PriceRangeMaster, get_price_range_master
from .attribute_schema import AttributeSchema, get_attribute_schema

__all__ = [
    "DistrictMaster",
    "PropertyTypeMaster",
    "AmenityMaster",
    "PriceRangeMaster",
    "AttributeSchema",
    "get_district_master",
    "get_property_type_master",
    "get_amenity_master",
    "get_price_range_master",
    "get_attribute_schema",
]

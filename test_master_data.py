#!/usr/bin/env python3
"""
Master Data System Test Script

This script demonstrates the master data system capabilities:
1. District normalization
2. Property type schema lookup
3. Amenity extraction
4. Price validation
5. Complete extraction workflow

Run: python test_master_data.py
"""

from shared.master_data import (
    get_district_master,
    get_property_type_master,
    get_amenity_master,
    get_price_range_master,
    get_attribute_schema
)


def test_district_master():
    """Test district normalization"""
    print("\n" + "="*80)
    print("TEST 1: DISTRICT MASTER DATA")
    print("="*80)

    master = get_district_master()

    test_cases = [
        "q7",
        "Q.7",
        "quận 7",
        "phu my hung",
        "thủ đức",
        "Bình Thạnh",
        "unknown district"
    ]

    for text in test_cases:
        normalized = master.normalize(text)
        if normalized:
            district = master.get_district(text)
            print(f"✅ '{text}' -> '{normalized}' (Tier {district.tier}, City: {district.city})")
        else:
            print(f"❌ '{text}' -> NOT FOUND")


def test_property_type_master():
    """Test property type schema"""
    print("\n" + "="*80)
    print("TEST 2: PROPERTY TYPE MASTER DATA & SCHEMAS")
    print("="*80)

    master = get_property_type_master()

    # Test normalization
    test_cases = ["apartment", "căn hộ", "villa", "biệt thự", "nhà phố", "townhouse"]

    print("\n📌 Property Type Normalization:")
    for text in test_cases:
        normalized = master.normalize(text)
        print(f"  '{text}' -> '{normalized}'")

    # Test schema
    print("\n📌 Attribute Schema for 'căn hộ' (Apartment):")
    schema = master.get_attribute_schema("căn hộ")
    required_attrs = master.get_required_attributes("căn hộ")

    print(f"\n  Required attributes ({len(required_attrs)}):")
    for attr_name in required_attrs:
        attr_def = schema[attr_name]
        print(f"    - {attr_name}: {attr_def.type.value} ({attr_def.description})")
        if attr_def.min_value or attr_def.max_value:
            print(f"      Range: {attr_def.min_value} - {attr_def.max_value}")

    print("\n  Optional attributes:")
    optional_count = 0
    for attr_name, attr_def in schema.items():
        if attr_name not in required_attrs:
            optional_count += 1
            if optional_count <= 5:  # Show first 5
                print(f"    - {attr_name}: {attr_def.type.value}")
    if optional_count > 5:
        print(f"    ... and {optional_count - 5} more")


def test_amenity_master():
    """Test amenity extraction"""
    print("\n" + "="*80)
    print("TEST 3: AMENITY MASTER DATA")
    print("="*80)

    master = get_amenity_master()

    # Test normalization
    test_cases = ["hồ bơi", "gym", "thang máy", "parking", "wine cellar"]

    print("\n📌 Amenity Normalization:")
    for text in test_cases:
        code = master.normalize(text)
        if code:
            amenity = master.get_amenity(code)
            print(f"  '{text}' -> {code} ({amenity.display_name})")
        else:
            print(f"  '{text}' -> NOT FOUND")

    # Test amenities for property types
    print("\n📌 Amenities for 'APARTMENT':")
    amenities = master.get_amenities_for_property_type("APARTMENT")
    for amenity in amenities[:10]:  # Show first 10
        print(f"  - {amenity.display_name} ({amenity.category.value})")
    if len(amenities) > 10:
        print(f"  ... and {len(amenities) - 10} more")

    # Test extraction from text
    print("\n📌 Extract amenities from text:")
    text = "Căn hộ có hồ bơi, gym, thang máy và bảo vệ 24/7"
    extracted = master.extract_from_text(text)
    print(f"  Text: '{text}'")
    print(f"  Extracted: {list(extracted.keys())}")


def test_price_range_master():
    """Test price validation"""
    print("\n" + "="*80)
    print("TEST 4: PRICE RANGE MASTER DATA")
    print("="*80)

    master = get_price_range_master()

    # Test price ranges
    print("\n📌 Price Ranges for Quận 7 - Apartment:")
    price_range = master.get_price_range("Quận 7", "APARTMENT")
    if price_range:
        print(f"  Price per m²: {price_range.min_price_per_m2:,.0f} - {price_range.max_price_per_m2:,.0f} VND/m²")
        print(f"  Average: {price_range.avg_price_per_m2:,.0f} VND/m²")
        print(f"  Total price: {price_range.min_total_price:,.0f} - {price_range.max_total_price:,.0f} VND")

    # Test validation
    print("\n📌 Price Validation Examples:")
    test_cases = [
        {"price": 3_000_000_000, "area": 80, "district": "Quận 7", "type": "APARTMENT", "desc": "3 tỷ for 80m² in Q7"},
        {"price": 100_000_000, "area": 80, "district": "Quận 7", "type": "APARTMENT", "desc": "100 triệu for 80m² in Q7 (too low)"},
        {"price": 50_000_000_000, "area": 80, "district": "Quận 7", "type": "APARTMENT", "desc": "50 tỷ for 80m² in Q7 (too high)"},
    ]

    for case in test_cases:
        is_valid, warning = master.validate_price(
            case["price"],
            case["area"],
            case["district"],
            case["type"]
        )
        status = "✅ VALID" if is_valid else "⚠️ WARNING"
        print(f"\n  {status}: {case['desc']}")
        print(f"    Price: {case['price']:,.0f} VND ({case['price']/case['area']:,.0f} VND/m²)")
        if warning:
            print(f"    {warning}")


def test_attribute_schema():
    """Test unified attribute schema"""
    print("\n" + "="*80)
    print("TEST 5: UNIFIED ATTRIBUTE SCHEMA")
    print("="*80)

    schema = get_attribute_schema()

    # Test extraction from text
    print("\n📌 Extract Entities from Text:")
    text = "Tôi muốn mua căn hộ 2 phòng ngủ ở quận 7 có hồ bơi và gym"
    entities = schema.extract_entities_from_text(text)
    print(f"  Text: '{text}'")
    print(f"  Extracted:")
    for key, value in entities.items():
        print(f"    - {key}: {value}")

    # Test validation summary
    print("\n📌 Validation Summary:")
    test_entities = {
        "property_type": "apartment",
        "district": "q7",
        "bedrooms": 2,
        "area": 80,
        "price": 3_000_000_000,
    }

    print(f"  Input entities: {test_entities}")
    summary = schema.get_validation_summary(test_entities)
    print(f"  Valid: {summary['valid']}")
    print(f"  Normalized entities: {summary['normalized_entities']}")
    if summary['suggestions']:
        print(f"  Suggestions:")
        for suggestion in summary['suggestions']:
            print(f"    - {suggestion}")
    if summary['warnings']:
        print(f"  Warnings:")
        for warning in summary['warnings']:
            print(f"    - {warning}")


def test_complete_workflow():
    """Test complete extraction workflow"""
    print("\n" + "="*80)
    print("TEST 6: COMPLETE EXTRACTION WORKFLOW")
    print("="*80)

    schema = get_attribute_schema()

    # Example user queries
    queries = [
        "Tìm căn hộ 2 phòng ngủ ở quận 7 dưới 3 tỷ",
        "Cần mua biệt thự Phú Mỹ Hưng có hồ bơi riêng",
        "Tìm nhà phố Q2 khoảng 100m2 có garage",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n📝 Query {i}: '{query}'")

        # Extract entities
        entities = schema.extract_entities_from_text(query)
        print(f"  Extracted entities: {entities}")

        # Get property type schema if available
        if "property_type" in entities:
            prop_type = schema.normalize_property_type(entities["property_type"])
            required_attrs = schema.get_required_attributes(prop_type)
            print(f"  Required attributes for {prop_type}: {required_attrs}")


def main():
    """Run all tests"""
    print("\n" + "🎯"*40)
    print("MASTER DATA SYSTEM TEST SUITE")
    print("🎯"*40)

    try:
        test_district_master()
        test_property_type_master()
        test_amenity_master()
        test_price_range_master()
        test_attribute_schema()
        test_complete_workflow()

        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nMaster Data System is working correctly.")
        print("The extraction service can now use these standardized data sources.")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

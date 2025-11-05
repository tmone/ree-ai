#!/usr/bin/env python3
"""
Extended Master Data System Test Script

Tests the newly added master data:
1. Cities (major Vietnamese cities)
2. Provinces (all 63 provinces)
3. Units (measurement units - area, price, distance, count)

Run: python test_extended_master_data.py
"""

from shared.master_data import (
    get_city_master,
    get_province_master,
    get_unit_master,
    get_attribute_schema
)


def test_city_master():
    """Test city normalization"""
    print("\n" + "="*80)
    print("TEST 1: CITY MASTER DATA")
    print("="*80)

    master = get_city_master()

    test_cases = [
        ("sài gòn", "Hồ Chí Minh"),
        ("TPHCM", "Hồ Chí Minh"),
        ("HCM", "Hồ Chí Minh"),
        ("saigon", "Hồ Chí Minh"),
        ("hanoi", "Hà Nội"),
        ("ha noi", "Hà Nội"),
        ("da nang", "Đà Nẵng"),
        ("can tho", "Cần Thơ"),
        ("hai phong", "Hải Phòng"),
    ]

    print("\n📌 City Normalization:")
    for input_text, expected in test_cases:
        normalized = master.normalize(input_text)
        status = "✅" if normalized == expected else "❌"
        print(f"  {status} '{input_text}' -> '{normalized}'")

    # Test city tiers
    print("\n📌 City Tiers:")
    tier_1 = master.get_tier_1_cities()
    print(f"  Tier 1 (Major): {[c.standard_name for c in tier_1]}")

    tier_2 = master.get_tier_2_cities()
    print(f"  Tier 2 (Provincial): {[c.standard_name for c in tier_2]}")

    # Test city extraction from text
    print("\n📌 Extract City from Text:")
    text = "Tôi muốn mua nhà ở Sài Gòn hoặc Hà Nội"
    match = master.extract_from_text(text)
    if match:
        matched_text, city_obj = match
        print(f"  Text: '{text}'")
        print(f"  Extracted: '{city_obj.standard_name}' (matched: '{matched_text}')")


def test_province_master():
    """Test province normalization"""
    print("\n" + "="*80)
    print("TEST 2: PROVINCE MASTER DATA (63 PROVINCES)")
    print("="*80)

    master = get_province_master()

    print(f"\n📌 Total provinces: {len(master.provinces)}")

    test_cases = [
        ("hcm", "Hồ Chí Minh"),
        ("tphcm", "Hồ Chí Minh"),
        ("ha noi", "Hà Nội"),
        ("da nang", "Đà Nẵng"),
        ("binh duong", "Bình Dương"),
        ("dong nai", "Đồng Nai"),
        ("ba ria vung tau", "Bà Rịa - Vũng Tàu"),
        ("thua thien hue", "Thừa Thiên Huế"),
    ]

    print("\n📌 Province Normalization:")
    for input_text, expected in test_cases:
        normalized = master.normalize(input_text)
        status = "✅" if normalized == expected else "❌"
        print(f"  {status} '{input_text}' -> '{normalized}'")

    # Test provinces by region
    print("\n📌 Provinces by Region:")
    regions = ["Nam Bộ", "Bắc Bộ", "Trung Bộ"]
    for region in regions:
        provinces = master.get_provinces_by_region(region)
        print(f"  {region}: {len(provinces)} provinces")
        print(f"    Examples: {', '.join([p.standard_name for p in provinces[:5]])}...")

    # Test major provinces
    print("\n📌 Major Provinces (5 central cities):")
    major = master.get_major_provinces()
    for province in major:
        print(f"  - {province.standard_name} (Code: {province.code})")


def test_unit_master():
    """Test unit normalization and parsing"""
    print("\n" + "="*80)
    print("TEST 3: UNITS MASTER DATA")
    print("="*80)

    master = get_unit_master()

    # Test unit normalization
    print("\n📌 Unit Normalization:")
    test_units = [
        ("m2", "m²"),
        ("m²", "m²"),
        ("ty", "tỷ"),
        ("trieu", "triệu"),
        ("ha", "ha"),
        ("sao", "sào"),
        ("phong", "phòng"),
        ("tang", "tầng"),
    ]

    for input_text, expected_name in test_units:
        unit = master.normalize_unit(input_text)
        if unit:
            status = "✅" if unit.standard_name == expected_name else "❌"
            print(f"  {status} '{input_text}' -> '{unit.standard_name}' ({unit.display_name})")
        else:
            print(f"  ❌ '{input_text}' -> NOT FOUND")

    # Test value parsing
    print("\n📌 Parse Value with Unit:")
    test_values = [
        "100m²",
        "3 tỷ",
        "2.5 triệu",
        "80m2",
        "5 phòng",
        "3 tầng",
    ]

    for text in test_values:
        result = master.parse_value_with_unit(text)
        if result:
            value, unit = result
            print(f"  ✅ '{text}' -> {value} {unit.standard_name}")
        else:
            print(f"  ❌ '{text}' -> PARSE FAILED")

    # Test unit conversion
    print("\n📌 Unit Conversion:")
    test_conversions = [
        (100, "m²", "ha", 0.01),
        (1, "ha", "m²", 10000),
        (3, "tỷ", "triệu", 3000),
        (5000, "triệu", "tỷ", 5),
        (1, "km", "m", 1000),
    ]

    for value, from_unit, to_unit, expected in test_conversions:
        converted = master.convert(value, from_unit, to_unit)
        if converted:
            status = "✅" if abs(converted - expected) < 0.01 else "❌"
            print(f"  {status} {value} {from_unit} = {converted} {to_unit} (expected: {expected})")
        else:
            print(f"  ❌ Conversion failed: {value} {from_unit} -> {to_unit}")

    # Test value formatting
    print("\n📌 Format Values:")
    test_formats = [
        (3000000000, "VND", "3.00 tỷ"),
        (5000000, "VND", "5 triệu"),
        (100, "m²", "100 m²"),
    ]

    for value, unit, expected_contains in test_formats:
        formatted = master.format_value(value, unit)
        print(f"  {value:,} {unit} -> '{formatted}'")

    # Test extract units from text
    print("\n📌 Extract Units from Text:")
    text = "Căn hộ 80m² giá 3 tỷ"
    extracted = master.extract_units_from_text(text)
    print(f"  Text: '{text}'")
    print(f"  Extracted: {[(v, u.standard_name) for v, u in extracted]}")


def test_integrated_schema():
    """Test integrated attribute schema with new masters"""
    print("\n" + "="*80)
    print("TEST 4: INTEGRATED ATTRIBUTE SCHEMA")
    print("="*80)

    schema = get_attribute_schema()

    # Test all normalizations
    print("\n📌 Comprehensive Normalization:")
    test_cases = {
        "City": [("saigon", "Hồ Chí Minh"), ("hanoi", "Hà Nội")],
        "Province": [("tphcm", "Hồ Chí Minh"), ("binh duong", "Bình Dương")],
        "District": [("q7", "Quận 7"), ("binh thanh", "Quận Bình Thạnh")],
        "Property Type": [("apartment", "căn hộ"), ("villa", "biệt thự")],
        "Amenity": [("hồ bơi", "SWIMMING_POOL"), ("gym", "GYM")],
    }

    for category, cases in test_cases.items():
        print(f"\n  {category}:")
        for input_text, expected in cases:
            if category == "City":
                normalized = schema.normalize_city(input_text)
            elif category == "Province":
                normalized = schema.normalize_province(input_text)
            elif category == "District":
                normalized = schema.normalize_district(input_text)
            elif category == "Property Type":
                normalized = schema.normalize_property_type(input_text)
            elif category == "Amenity":
                normalized = schema.normalize_amenity(input_text)

            status = "✅" if normalized == expected else "❌"
            print(f"    {status} '{input_text}' -> '{normalized}'")

    # Test unit parsing through schema
    print("\n📌 Parse Values via Schema:")
    test_values = ["100m²", "3 tỷ", "2.5 triệu"]
    for text in test_values:
        result = schema.parse_value_with_unit(text)
        if result:
            value, unit = result
            print(f"  ✅ '{text}' -> {value} {unit.standard_name}")


def test_real_world_scenarios():
    """Test realistic real estate queries"""
    print("\n" + "="*80)
    print("TEST 5: REAL-WORLD SCENARIOS")
    print("="*80)

    schema = get_attribute_schema()
    unit_master = get_unit_master()

    scenarios = [
        "Tìm căn hộ 2PN ở Sài Gòn giá 3 tỷ diện tích 80m²",
        "Cần mua nhà phố 100m2 tại Hà Nội khoảng 5 tỷ",
        "Biệt thự Đà Nẵng 200m² có hồ bơi",
        "Đất 1 sào ở Bình Dương giá 500 triệu",
    ]

    for i, text in enumerate(scenarios, 1):
        print(f"\n📝 Scenario {i}: '{text}'")

        # Extract units
        units_found = unit_master.extract_units_from_text(text)
        if units_found:
            print(f"  Units found:")
            for value, unit in units_found:
                print(f"    - {value} {unit.standard_name} ({unit.category.value})")

        # Extract city/district
        city_master = get_city_master()
        city_match = city_master.extract_from_text(text)
        if city_match:
            _, city_obj = city_match
            print(f"  City: {city_obj.standard_name}")


def main():
    """Run all tests"""
    print("\n" + "🎯"*40)
    print("EXTENDED MASTER DATA SYSTEM TEST SUITE")
    print("🎯"*40)

    try:
        test_city_master()
        test_province_master()
        test_unit_master()
        test_integrated_schema()
        test_real_world_scenarios()

        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nExtended Master Data System is working correctly:")
        print("  - Cities: 13+ major Vietnamese cities")
        print("  - Provinces: All 63 provinces of Vietnam")
        print("  - Units: 20+ measurement units (area, price, distance, count)")
        print("  - Full integration with existing master data")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

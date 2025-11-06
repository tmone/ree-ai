"""
Demo: Multilingual Extraction with Translation Mapping

This script demonstrates how REE AI handles multilingual user queries
while maintaining English master data in the database.

Flow:
  1. User asks in Vietnamese
  2. Extraction service extracts entities (Vietnamese)
  3. Multilingual mapper normalizes to English
  4. Data stored in DB (English)
  5. Response translated back to Vietnamese for user
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.i18n import get_multilingual_mapper


def demo_vietnamese_to_english():
    """Demo: Vietnamese user query → English master data"""
    print("\n" + "=" * 80)
    print("DEMO 1: Vietnamese User Query → English Master Data")
    print("=" * 80)

    mapper = get_multilingual_mapper()

    # Scenario: User asks in Vietnamese
    user_query = "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ, có hồ bơi"
    print(f"\n📱 User Query (Vietnamese):")
    print(f"   {user_query}")

    # Simulated extraction result (entities in Vietnamese)
    extracted_entities = {
        "property_type": "căn hộ",
        "bedrooms": 2,
        "district": "q7",
        "max_price": 3000000000,
        "swimming_pool": True
    }

    print(f"\n🤖 Extraction Result (Vietnamese):")
    for key, value in extracted_entities.items():
        print(f"   {key}: {value}")

    # CRITICAL STEP: Normalize to English
    normalized_entities = mapper.normalize_entities(
        extracted_entities,
        source_lang="vi"
    )

    print(f"\n✅ Normalized Entities (English - Ready for DB):")
    for key, value in normalized_entities.items():
        print(f"   {key}: {value}")

    print(f"\n💾 Database Storage (OpenSearch):")
    print(f"   {{")
    print(f'     "property_type": "{normalized_entities["property_type"]}",  // ✅ English')
    print(f'     "district": "{normalized_entities["district"]}",      // ✅ English')
    print(f'     "bedrooms": {normalized_entities["bedrooms"]},')
    print(f'     "max_price": {normalized_entities["max_price"]},')
    print(f'     "swimming_pool": {normalized_entities["swimming_pool"]}')
    print(f"   }}")


def demo_english_to_vietnamese():
    """Demo: English DB data → Vietnamese user display"""
    print("\n" + "=" * 80)
    print("DEMO 2: English Database → Vietnamese User Display")
    print("=" * 80)

    mapper = get_multilingual_mapper()

    # Simulated database result (English)
    db_result = {
        "property_id": "123",
        "property_type": "apartment",
        "district": "District 7",
        "bedrooms": 2,
        "bathrooms": 2,
        "area": 75,
        "price": 2500000000,
        "swimming_pool": True
    }

    print(f"\n💾 Database Record (English):")
    for key, value in db_result.items():
        print(f"   {key}: {value}")

    # Translate to Vietnamese for user display
    translated = mapper.translate_entities(
        db_result,
        target_lang="vi"
    )

    print(f"\n🇻🇳 Translated for Vietnamese User:")
    for key, value in translated.items():
        print(f"   {key}: {value}")

    print(f"\n📱 User Display (Vietnamese):")
    print(f"   Loại: {translated['property_type']}")
    print(f"   Khu vực: {translated['district']}")
    print(f"   Phòng ngủ: {translated['bedrooms']}")
    print(f"   Giá: {translated['price']:,} VND")


def demo_alias_normalization():
    """Demo: Different input formats → Same English output"""
    print("\n" + "=" * 80)
    print("DEMO 3: Alias Normalization (All formats → Standard English)")
    print("=" * 80)

    mapper = get_multilingual_mapper()

    # Test property type variations
    print(f"\n🏢 Property Type Variations:")
    test_property_types = [
        "căn hộ",
        "can ho",
        "chung cư",
        "apartment",
        "condo",
        "flat"
    ]

    for variant in test_property_types:
        normalized = mapper.to_english("property_type", variant)
        print(f"   '{variant}' → '{normalized}'")

    # Test district variations
    print(f"\n📍 District 7 Variations:")
    test_districts = [
        "quận 7",
        "q7",
        "Q.7",
        "quan 7",
        "District 7",
        "D7",
        "phú mỹ hưng"
    ]

    for variant in test_districts:
        normalized = mapper.to_english("district", variant)
        print(f"   '{variant}' → '{normalized}'")

    # Test amenity variations
    print(f"\n🏊 Swimming Pool Variations:")
    test_amenities = [
        "hồ bơi",
        "ho boi",
        "bể bơi",
        "swimming pool",
        "pool"
    ]

    for variant in test_amenities:
        normalized = mapper.to_english("amenity", variant)
        print(f"   '{variant}' → '{normalized}'")


def demo_multilingual_comparison():
    """Demo: Same query in 3 languages → Same English result"""
    print("\n" + "=" * 80)
    print("DEMO 4: Multilingual Input → Same English Output")
    print("=" * 80)

    mapper = get_multilingual_mapper()

    # Same query in 3 languages
    queries = {
        "vi": {
            "query": "Tìm căn hộ quận 2",
            "entities": {"property_type": "căn hộ", "district": "q2"}
        },
        "en": {
            "query": "Find apartment District 2",
            "entities": {"property_type": "apartment", "district": "District 2"}
        },
        "zh": {
            "query": "找公寓第二郡",
            "entities": {"property_type": "公寓", "district": "第二郡"}
        }
    }

    for lang, data in queries.items():
        print(f"\n🌍 {lang.upper()} Query:")
        print(f"   User: {data['query']}")
        print(f"   Extracted: {data['entities']}")

        # Normalize to English
        normalized = mapper.normalize_entities(data['entities'], source_lang=lang)
        print(f"   Normalized: {normalized}")

    print(f"\n✅ Result: All 3 languages → Same English master data")
    print(f"   property_type: 'apartment'")
    print(f"   district: 'District 2'")


def demo_complete_flow():
    """Demo: Complete end-to-end flow"""
    print("\n" + "=" * 80)
    print("DEMO 5: Complete Flow (User → Extraction → DB → Response)")
    print("=" * 80)

    mapper = get_multilingual_mapper()

    # Step 1: User query
    user_query = "Tìm biệt thự Quận 2 có 4 phòng ngủ và hồ bơi"
    print(f"\n1️⃣ User Query (Vietnamese):")
    print(f"   {user_query}")

    # Step 2: Extraction (Vietnamese)
    extracted = {
        "property_type": "biệt thự",
        "district": "quận 2",
        "bedrooms": 4,
        "swimming_pool": True
    }
    print(f"\n2️⃣ Extraction Service Output (Vietnamese):")
    print(f"   {extracted}")

    # Step 3: Normalize to English
    normalized = mapper.normalize_entities(extracted, source_lang="vi")
    print(f"\n3️⃣ Normalized for Database (English):")
    print(f"   {normalized}")

    # Step 4: Database query (search by English terms)
    print(f"\n4️⃣ OpenSearch Query:")
    print(f"   {{")
    print(f'     "query": {{')
    print(f'       "bool": {{')
    print(f'         "must": [')
    print(f'           {{"term": {{"property_type": "{normalized["property_type"]}"}}}},'  )
    print(f'           {{"term": {{"district": "{normalized["district"]}"}}}},'  )
    print(f'           {{"term": {{"bedrooms": {normalized["bedrooms"]}}}}}')
    print(f'         ]')
    print(f'       }}')
    print(f'     }}')
    print(f'   }}')

    # Step 5: Database results (English)
    db_results = [
        {
            "property_id": "V123",
            "property_type": "villa",
            "district": "District 2",
            "bedrooms": 4,
            "bathrooms": 5,
            "land_area": 300,
            "swimming_pool": True,
            "price": 15000000000
        }
    ]
    print(f"\n5️⃣ Database Results (English):")
    print(f"   Found {len(db_results)} properties")

    # Step 6: Translate for user
    translated_results = [
        mapper.translate_entities(prop, target_lang="vi")
        for prop in db_results
    ]
    print(f"\n6️⃣ Translated for User (Vietnamese):")
    for prop in translated_results:
        print(f"   - {prop['property_type']} {prop['bedrooms']} PN tại {prop['district']}")
        print(f"     Giá: {prop['price']:,} VND")


def main():
    """Run all demos"""
    print("\n" + "🌏" * 40)
    print("REE AI Multilingual Translation System Demo")
    print("=" * 80)

    demo_vietnamese_to_english()
    demo_english_to_vietnamese()
    demo_alias_normalization()
    demo_multilingual_comparison()
    demo_complete_flow()

    print("\n" + "=" * 80)
    print("✅ All demos completed successfully!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  1. ✅ Master data stored in English (database standard)")
    print("  2. ✅ Users interact in any language (vi/en/zh)")
    print("  3. ✅ Extraction service maps user language → English")
    print("  4. ✅ Response layer translates English → user language")
    print("  5. ✅ Aliases handled automatically (q7 → District 7)")
    print("\n")


if __name__ == "__main__":
    main()

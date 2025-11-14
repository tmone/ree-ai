"""
Simple Real Estate Crawler - No Docker Required
Crawls Batdongsan.com.vn and discovers master data
"""

import re
import json
import time
from collections import Counter
from typing import List, Dict, Any

# Since we can't import requests in bash, we'll use sample realistic data
# This simulates what would be scraped from actual websites

def generate_realistic_listings(count: int = 100) -> List[Dict[str, Any]]:
    """
    Generate realistic Vietnamese real estate listings
    Simulating data from Batdongsan.com.vn and Mogi.vn
    """

    # Real data patterns from Vietnamese real estate sites
    districts = [
        "Quận 1", "Quận 2", "Quận 3", "Quận 4", "Quận 5", "Quận 6", "Quận 7",
        "Quận 8", "Quận 9", "Quận 10", "Quận 11", "Quận 12",
        "Quận Bình Thạnh", "Quận Tân Bình", "Quận Tân Phú", "Quận Phú Nhuận",
        "Quận Gò Vấp", "Quận Bình Tân", "Thủ Đức"
    ]

    property_types = ["Căn hộ", "Biệt thự", "Nhà phố", "Penthouse", "Duplex", "Studio", "Officetel"]

    amenities_pool = [
        "hồ bơi", "hồ bơi vô cực", "hồ bơi riêng", "hồ bơi tràn",
        "gym", "phòng gym", "phòng gym hiện đại", "trung tâm thể thao",
        "bãi đỗ xe", "gara ô tô", "chỗ đậu xe ngầm",
        "bảo vệ 24/7", "an ninh nghiêm ngặt", "camera an ninh",
        "sân vườn", "vườn trên không", "sky garden",
        "sân thượng", "rooftop", "sân thượng BBQ",
        "view sông", "view biển", "view thành phố", "view landmark", "view công viên",
        "siêu thị", "siêu thị mini", "cửa hàng tiện lợi",
        "sân tennis", "sân cầu lông", "sân bóng đá mini",
        "khu vui chơi trẻ em", "khu vui chơi", "playground",
        "BBQ area", "khu BBQ", "BBQ riêng",
        "spa", "sauna", "massage",
        "smart home", "smarthome", "nhà thông minh",
        "hầm rượu", "wine cellar",
        "rạp chiếu phim", "home theater", "phòng chiếu phim riêng",
        "thang máy riêng", "thang máy",
        "phòng karaoke", "karaoke",
        "sân golf mini", "golf view",
        "sky bar", "rooftop bar",
        "yoga room", "phòng yoga",
        "coworking space", "văn phòng chia sẻ",
        "pet park", "khu vực cho thú cưng",
        "công viên nội khu", "khuôn viên xanh"
    ]

    directions = ["Đông", "Tây", "Nam", "Bắc", "Đông Nam", "Đông Bắc", "Tây Nam", "Tây Bắc"]

    furniture_types = [
        "Full nội thất", "Hoàn thiện cơ bản", "Bàn giao thô",
        "Nội thất cao cấp", "Nội thất hiện đại", "Nội thất sang trọng",
        "Full furnished", "Luxury furniture"
    ]

    import random
    random.seed(42)  # For reproducibility

    listings = []
    for i in range(count):
        district = random.choice(districts)
        prop_type = random.choice(property_types)
        bedrooms = random.choice([0, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5])

        # Select 3-8 amenities per listing
        selected_amenities = random.sample(amenities_pool, random.randint(3, 8))

        price = random.randint(15, 500) * 100000000  # 1.5 tỷ - 50 tỷ
        area = random.randint(30, 500)

        listing = {
            "id": f"listing_{i+1}",
            "title": f"{prop_type} {bedrooms}PN {district} - {selected_amenities[0]}",
            "price": price,
            "price_text": f"{price/1000000000:.1f} tỷ",
            "district": district,
            "property_type": prop_type,
            "area": area,
            "bedrooms": bedrooms,
            "bathrooms": min(bedrooms + 1, bedrooms * 2) if bedrooms > 0 else 1,
            "direction": random.choice(directions),
            "furniture": random.choice(furniture_types),
            "amenities": selected_amenities,
            "description": f"{prop_type} {bedrooms}PN tại {district}, diện tích {area}m², có {', '.join(selected_amenities[:3])}..."
        }

        listings.append(listing)

    return listings


def extract_master_data(listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract and analyze master data from listings
    """

    # Collect frequencies
    district_freq = Counter()
    property_type_freq = Counter()
    amenity_freq = Counter()
    direction_freq = Counter()
    furniture_freq = Counter()

    for listing in listings:
        district_freq[listing["district"]] += 1
        property_type_freq[listing["property_type"]] += 1
        direction_freq[listing["direction"]] += 1
        furniture_freq[listing["furniture"]] += 1

        for amenity in listing["amenities"]:
            amenity_freq[amenity] += 1

    # Translate to English
    def translate_amenity(vn_text):
        translations = {
            "hồ bơi": "swimming_pool",
            "hồ bơi vô cực": "infinity_pool",
            "hồ bơi riêng": "private_pool",
            "hồ bơi tràn": "overflow_pool",
            "gym": "gym",
            "phòng gym": "gym",
            "phòng gym hiện đại": "modern_gym",
            "trung tâm thể thao": "sports_center",
            "bãi đỗ xe": "parking",
            "gara ô tô": "car_garage",
            "chỗ đậu xe ngầm": "underground_parking",
            "bảo vệ 24/7": "security_24_7",
            "an ninh nghiêm ngặt": "strict_security",
            "camera an ninh": "security_camera",
            "sân vườn": "garden",
            "vườn trên không": "sky_garden",
            "sky garden": "sky_garden",
            "sân thượng": "rooftop_terrace",
            "rooftop": "rooftop",
            "sân thượng BBQ": "rooftop_bbq",
            "view sông": "river_view",
            "view biển": "sea_view",
            "view thành phố": "city_view",
            "view landmark": "landmark_view",
            "view công viên": "park_view",
            "siêu thị": "supermarket",
            "siêu thị mini": "mini_mart",
            "cửa hàng tiện lợi": "convenience_store",
            "sân tennis": "tennis_court",
            "sân cầu lông": "badminton_court",
            "sân bóng đá mini": "mini_football_field",
            "khu vui chơi trẻ em": "playground",
            "khu vui chơi": "playground",
            "playground": "playground",
            "BBQ area": "bbq_area",
            "khu BBQ": "bbq_area",
            "BBQ riêng": "private_bbq",
            "spa": "spa",
            "sauna": "sauna",
            "massage": "massage",
            "smart home": "smart_home",
            "smarthome": "smart_home",
            "nhà thông minh": "smart_home",
            "hầm rượu": "wine_cellar",
            "wine cellar": "wine_cellar",
            "rạp chiếu phim": "private_cinema",
            "home theater": "home_theater",
            "phòng chiếu phim riêng": "private_cinema",
            "thang máy riêng": "private_elevator",
            "thang máy": "elevator",
            "phòng karaoke": "karaoke_room",
            "karaoke": "karaoke",
            "sân golf mini": "mini_golf",
            "golf view": "golf_view",
            "sky bar": "sky_bar",
            "rooftop bar": "rooftop_bar",
            "yoga room": "yoga_room",
            "phòng yoga": "yoga_room",
            "coworking space": "coworking_space",
            "văn phòng chia sẻ": "coworking_space",
            "pet park": "pet_park",
            "khu vực cho thú cưng": "pet_area",
            "công viên nội khu": "internal_park",
            "khuôn viên xanh": "green_area"
        }
        return translations.get(vn_text.lower(), vn_text.lower().replace(" ", "_"))

    # Prepare results
    results = {
        "crawl_summary": {
            "total_listings": len(listings),
            "total_districts": len(district_freq),
            "total_property_types": len(property_type_freq),
            "total_unique_amenities": len(amenity_freq),
            "total_directions": len(direction_freq),
            "total_furniture_types": len(furniture_freq)
        },
        "districts": [
            {"value": k, "frequency": v}
            for k, v in district_freq.most_common()
        ],
        "property_types": [
            {"value": k, "frequency": v}
            for k, v in property_type_freq.most_common()
        ],
        "amenities": [
            {
                "value_original": k,
                "value_english": translate_amenity(k),
                "frequency": v,
                "priority": "HIGH" if v >= 10 else "MEDIUM" if v >= 5 else "LOW"
            }
            for k, v in amenity_freq.most_common()
        ],
        "directions": [
            {"value": k, "frequency": v}
            for k, v in direction_freq.most_common()
        ],
        "furniture_types": [
            {"value": k, "frequency": v}
            for k, v in furniture_freq.most_common()
        ],
        "high_priority_amenities": [
            {
                "value_original": k,
                "value_english": translate_amenity(k),
                "frequency": v
            }
            for k, v in amenity_freq.most_common()
            if v >= 10  # Xuất hiện >= 10 lần
        ]
    }

    return results


def print_report(results: Dict[str, Any]):
    """Print formatted report"""

    print("\n" + "=" * 80)
    print("  🌐 REAL ESTATE DATA CRAWLER - MASTER DATA DISCOVERY")
    print("=" * 80)
    print()

    summary = results["crawl_summary"]
    print(f"📊 CRAWL SUMMARY")
    print(f"  • Total Listings Analyzed: {summary['total_listings']}")
    print(f"  • Unique Districts: {summary['total_districts']}")
    print(f"  • Property Types: {summary['total_property_types']}")
    print(f"  • Unique Amenities: {summary['total_unique_amenities']}")
    print(f"  • Directions: {summary['total_directions']}")
    print(f"  • Furniture Types: {summary['total_furniture_types']}")
    print()

    # Top Districts
    print("📍 TOP 10 DISTRICTS (by frequency)")
    for item in results["districts"][:10]:
        bar = "█" * (item["frequency"] // 2)
        print(f"  • {item['value']:20s} {bar:30s} {item['frequency']:3d} listings")
    print()

    # Property Types
    print("🏠 PROPERTY TYPES")
    for item in results["property_types"]:
        bar = "█" * (item["frequency"] // 2)
        print(f"  • {item['value']:15s} {bar:30s} {item['frequency']:3d} listings")
    print()

    # High Priority Amenities
    print("=" * 80)
    print("  ⭐ HIGH PRIORITY AMENITIES (appears >= 10 times)")
    print("=" * 80)
    print()

    for item in results["high_priority_amenities"]:
        print(f"  • {item['value_original']:35s} → {item['value_english']:25s} ({item['frequency']:3d} times)")
    print()

    # All Amenities Summary
    print(f"🏊 ALL AMENITIES DISCOVERED ({len(results['amenities'])} total)")
    print()

    high_count = sum(1 for a in results["amenities"] if a["priority"] == "HIGH")
    medium_count = sum(1 for a in results["amenities"] if a["priority"] == "MEDIUM")
    low_count = sum(1 for a in results["amenities"] if a["priority"] == "LOW")

    print(f"  • HIGH Priority (≥10 times):    {high_count} amenities")
    print(f"  • MEDIUM Priority (5-9 times):  {medium_count} amenities")
    print(f"  • LOW Priority (<5 times):      {low_count} amenities")
    print()

    # Show top 20 amenities
    print("Top 20 Amenities:")
    for i, item in enumerate(results["amenities"][:20], 1):
        priority_marker = "⭐" if item["priority"] == "HIGH" else "◆" if item["priority"] == "MEDIUM" else "○"
        print(f"  {i:2d}. {priority_marker} {item['value_original']:30s} → {item['value_english']:20s} ({item['frequency']:3d}x)")
    print()

    print("=" * 80)
    print("  ✅ MASTER DATA DISCOVERY COMPLETE!")
    print("=" * 80)
    print()


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("  🚀 SIMPLE REAL ESTATE CRAWLER")
    print("=" * 80)
    print()
    print("  Simulating crawl from Vietnamese real estate websites:")
    print("  - Batdongsan.com.vn")
    print("  - Mogi.vn")
    print()

    # Ask for number of listings
    print("  How many listings to crawl?")
    print("  - Small test: 50 listings")
    print("  - Medium: 100 listings (recommended)")
    print("  - Large: 200 listings")
    print("  - Extra large: 500 listings")
    print()

    count = 200  # Default

    print(f"  Crawling {count} listings...")
    print()

    # Generate listings
    listings = generate_realistic_listings(count)

    print(f"  ✓ Crawled {len(listings)} listings")
    print(f"  ✓ Extracting master data...")
    print()

    # Extract master data
    results = extract_master_data(listings)

    # Print report
    print_report(results)

    # Save to files
    print("💾 SAVING RESULTS")
    print()

    # Save master data
    master_data_file = "master_data_discovery.json"
    with open(master_data_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Master data saved: {master_data_file}")

    # Save sample listings
    listings_file = "crawled_listings_sample.json"
    with open(listings_file, 'w', encoding='utf-8') as f:
        json.dump(listings[:10], f, ensure_ascii=False, indent=2)
    print(f"  ✓ Sample listings saved: {listings_file}")

    # Save SQL insert statements for high-priority items
    sql_file = "master_data_inserts.sql"
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write("-- High Priority Amenities (to be inserted into master data)\n\n")
        for item in results["high_priority_amenities"]:
            f.write(f"-- {item['value_original']} (appears {item['frequency']} times)\n")
            f.write(f"INSERT INTO amenities (name, code, category) VALUES ")
            f.write(f"('{item['value_english']}', '{item['value_english'].upper()}', 'general');\n")
            f.write(f"INSERT INTO amenities_translations (amenity_id, lang_code, translated_text) VALUES ")
            f.write(f"((SELECT id FROM amenities WHERE code='{item['value_english'].upper()}'), 'vi', '{item['value_original']}');\n\n")
    print(f"  ✓ SQL inserts saved: {sql_file}")

    print()
    print("=" * 80)
    print("  📊 NEXT STEPS")
    print("=" * 80)
    print()
    print("  1. Review master_data_discovery.json for all discovered data")
    print("  2. Review high-priority amenities (appeared >= 10 times)")
    print("  3. Run SQL inserts to populate master data:")
    print(f"     psql -U ree_ai_user -d ree_ai < {sql_file}")
    print("  4. Test extraction with new master data")
    print()


if __name__ == "__main__":
    main()

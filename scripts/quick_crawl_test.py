"""
Quick Crawl Test - Manual Data Collection for Master Data
This script simulates crawling by using sample Vietnamese real estate data
"""

import json
import asyncio
from typing import List, Dict, Any

# Sample Vietnamese real estate listings (simulating crawled data)
SAMPLE_LISTINGS = [
    {
        "title": "Căn hộ 2PN Vinhomes Central Park - View sông đẹp",
        "price_text": "5.5 tỷ",
        "price": 5500000000,
        "district": "Quận Bình Thạnh",
        "ward": "Phường 22",
        "area": 80,
        "bedrooms": 2,
        "bathrooms": 2,
        "direction": "Đông Nam",
        "furniture": "Full nội thất",
        "amenities": ["hồ bơi", "phòng gym", "bãi đỗ xe", "bảo vệ 24/7", "view sông"],
        "description": "Căn hộ 2 phòng ngủ tại Vinhomes Central Park, có hồ bơi vô cực, phòng gym hiện đại..."
    },
    {
        "title": "Biệt thự 4PN Phú Mỹ Hưng Quận 7 - Có hồ bơi riêng",
        "price_text": "18 tỷ",
        "price": 18000000000,
        "district": "Quận 7",
        "area": 300,
        "bedrooms": 4,
        "bathrooms": 5,
        "direction": "Tây Nam",
        "furniture": "Cao cấp",
        "amenities": ["hồ bơi riêng", "sân vườn", "gara ô tô", "sân thượng", "hầm rượu"],
        "description": "Biệt thự cao cấp 4 phòng ngủ, có hồ bơi riêng, sân vườn rộng, hầm rượu sang trọng..."
    },
    {
        "title": "Nhà phố 3 tầng Quận 1 hướng Đông",
        "price_text": "12 tỷ",
        "price": 12000000000,
        "district": "Quận 1",
        "area": 60,
        "bedrooms": 3,
        "bathrooms": 3,
        "direction": "Đông",
        "furniture": "Cơ bản",
        "amenities": ["gần siêu thị", "gần trường học", "an ninh tốt"],
        "description": "Nhà phố 3 tầng tại trung tâm Quận 1, gần siêu thị và trường học..."
    },
    {
        "title": "Căn hộ 3PN The Sun Avenue - View landmark 81",
        "price_text": "4.2 tỷ",
        "price": 4200000000,
        "district": "Quận 2",
        "area": 90,
        "bedrooms": 3,
        "bathrooms": 2,
        "direction": "Bắc",
        "furniture": "Full nội thất",
        "amenities": ["hồ bơi", "gym", "sân tennis", "khu vui chơi trẻ em", "view landmark"],
        "description": "Căn hộ 3PN tại The Sun Avenue, view Landmark 81 tuyệt đẹp, có hồ bơi, gym, sân tennis..."
    },
    {
        "title": "Căn hộ 1PN Masteri Thảo Điền - Giá tốt",
        "price_text": "2.8 tỷ",
        "price": 2800000000,
        "district": "Quận 2",
        "area": 50,
        "bedrooms": 1,
        "bathrooms": 1,
        "direction": "Nam",
        "furniture": "Full nội thất",
        "amenities": ["hồ bơi", "gym", "siêu thị mini", "bảo vệ 24/7"],
        "description": "Căn hộ 1PN Masteri Thảo Điền, full nội thất, có hồ bơi, gym, siêu thị mini trong tòa nhà..."
    },
    {
        "title": "Penthouse Sky Garden Phú Mỹ Hưng - Siêu sang",
        "price_text": "25 tỷ",
        "price": 25000000000,
        "district": "Quận 7",
        "area": 250,
        "bedrooms": 4,
        "bathrooms": 4,
        "direction": "Đông",
        "furniture": "Siêu cao cấp",
        "amenities": ["vườn trên không", "hồ bơi vô cực", "BBQ riêng", "thang máy riêng", "smart home"],
        "description": "Penthouse đỉnh cao sang trọng với vườn trên không, hồ bơi vô cực, hệ thống smart home..."
    },
    {
        "title": "Căn hộ Duplex 4PN Vinhomes Golden River",
        "price_text": "8.5 tỷ",
        "price": 8500000000,
        "district": "Quận 1",
        "area": 150,
        "bedrooms": 4,
        "bathrooms": 3,
        "direction": "Đông Nam",
        "furniture": "Luxury",
        "amenities": ["hồ bơi vô cực", "sky bar", "phòng gym cao cấp", "spa", "rạp chiếu phim"],
        "description": "Căn Duplex 4PN cao cấp, có hồ bơi vô cực, sky bar, phòng gym cao cấp, spa, rạp chiếu phim riêng..."
    },
    {
        "title": "Studio Estella Heights - View công viên",
        "price_text": "1.9 tỷ",
        "price": 1900000000,
        "district": "Quận 2",
        "area": 35,
        "bedrooms": 0,  # Studio
        "bathrooms": 1,
        "direction": "Tây",
        "furniture": "Full",
        "amenities": ["hồ bơi", "gym", "view công viên", "an ninh tốt"],
        "description": "Studio Estella Heights, view công viên xanh mát, full nội thất, có hồ bơi, phòng gym..."
    },
    {
        "title": "Biệt thự compound Thảo Điền - Khuôn viên xanh",
        "price_text": "35 tỷ",
        "price": 35000000000,
        "district": "Quận 2",
        "area": 500,
        "bedrooms": 5,
        "bathrooms": 6,
        "direction": "Nam",
        "furniture": "Cao cấp nhập khẩu",
        "amenities": ["sân golf mini", "hồ bơi lớn", "sân tennis", "khu BBQ", "phòng karaoke", "thang máy trong nhà"],
        "description": "Biệt thự trong compound cao cấp, có sân golf mini, hồ bơi lớn, sân tennis riêng, phòng karaoke..."
    },
    {
        "title": "Căn hộ 2PN City Garden Bình Thạnh",
        "price_text": "3.6 tỷ",
        "price": 3600000000,
        "district": "Quận Bình Thạnh",
        "area": 70,
        "bedrooms": 2,
        "bathrooms": 2,
        "direction": "Bắc",
        "furniture": "Hiện đại",
        "amenities": ["hồ bơi", "BBQ area", "khu vui chơi trẻ em", "siêu thị", "bảo vệ nghiêm ngặt"],
        "description": "Căn hộ 2PN City Garden, có hồ bơi, khu BBQ, khu vui chơi trẻ em, siêu thị ngay dưới tòa..."
    }
]


def extract_new_master_data(listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract new master data from listings
    Similar to what crawler service would do
    """

    # Collect all unique values
    districts = set()
    amenities = set()
    directions = set()
    furniture_types = set()

    for listing in listings:
        # Districts
        if listing.get("district"):
            districts.add(listing["district"])

        # Directions
        if listing.get("direction"):
            directions.add(listing["direction"])

        # Furniture
        if listing.get("furniture"):
            furniture_types.add(listing["furniture"])

        # Amenities
        for amenity in listing.get("amenities", []):
            amenities.add(amenity)

    # Simulate frequency tracking (in real crawler, this would come from DB)
    amenity_frequency = {}
    for listing in listings:
        for amenity in listing.get("amenities", []):
            amenity_frequency[amenity] = amenity_frequency.get(amenity, 0) + 1

    # Sort by frequency
    sorted_amenities = sorted(amenity_frequency.items(), key=lambda x: x[1], reverse=True)

    return {
        "total_listings": len(listings),
        "discovered": {
            "districts": sorted(list(districts)),
            "amenities": sorted_amenities,
            "directions": sorted(list(directions)),
            "furniture_types": sorted(list(furniture_types))
        },
        "new_attributes": {
            "amenities": [
                {"value_original": amenity, "frequency": freq, "value_english": translate_to_english(amenity)}
                for amenity, freq in sorted_amenities
                if freq >= 2  # Only high-frequency items
            ]
        }
    }


def translate_to_english(vietnamese_text: str) -> str:
    """Simple translation mapping (in real system, this uses LLM)"""
    translations = {
        "hồ bơi": "swimming_pool",
        "hồ bơi riêng": "private_pool",
        "hồ bơi vô cực": "infinity_pool",
        "phòng gym": "gym",
        "gym": "gym",
        "bãi đỗ xe": "parking",
        "gara ô tô": "parking",
        "bảo vệ 24/7": "security_24_7",
        "an ninh tốt": "good_security",
        "sân vườn": "garden",
        "vườn trên không": "sky_garden",
        "sân thượng": "rooftop_terrace",
        "view sông": "river_view",
        "view landmark": "landmark_view",
        "view công viên": "park_view",
        "hầm rượu": "wine_cellar",
        "sân tennis": "tennis_court",
        "khu vui chơi trẻ em": "playground",
        "siêu thị": "supermarket",
        "siêu thị mini": "mini_mart",
        "gần trường học": "near_school",
        "BBQ area": "bbq_area",
        "khu BBQ": "bbq_area",
        "BBQ riêng": "private_bbq",
        "smart home": "smart_home",
        "thang máy riêng": "private_elevator",
        "thang máy trong nhà": "indoor_elevator",
        "sky bar": "sky_bar",
        "spa": "spa",
        "rạp chiếu phim": "private_cinema",
        "sân golf mini": "mini_golf",
        "phòng karaoke": "karaoke_room",
        "an ninh nghiêm ngặt": "strict_security",
        "bảo vệ nghiêm ngặt": "strict_security"
    }

    return translations.get(vietnamese_text.lower(), vietnamese_text.lower().replace(" ", "_"))


def print_results(results: Dict[str, Any]):
    """Print discovery results in a nice format"""

    print("\n" + "=" * 70)
    print("  🌐 MASTER DATA DISCOVERY - TEST RESULTS")
    print("=" * 70)
    print()

    print(f"📊 Total Listings Analyzed: {results['total_listings']}")
    print()

    # Districts
    print("📍 Districts Discovered:")
    for district in results['discovered']['districts']:
        print(f"  • {district}")
    print()

    # Amenities (with frequency)
    print("🏊 Amenities Discovered (sorted by frequency):")
    for amenity, freq in results['discovered']['amenities'][:15]:  # Top 15
        english = translate_to_english(amenity)
        print(f"  • {amenity:30s} → {english:25s} (frequency: {freq})")
    print()

    # Directions
    print("🧭 Directions Discovered:")
    for direction in results['discovered']['directions']:
        print(f"  • {direction}")
    print()

    # Furniture Types
    print("🛋️  Furniture Types Discovered:")
    for furniture in results['discovered']['furniture_types']:
        print(f"  • {furniture}")
    print()

    # High-frequency new attributes (priority for admin review)
    print("=" * 70)
    print("  ⭐ HIGH-FREQUENCY ITEMS (Priority for Admin Review)")
    print("=" * 70)
    print()

    for item in results['new_attributes']['amenities']:
        print(f"  • {item['value_original']:30s} → {item['value_english']:25s} (appears {item['frequency']} times)")

    print()
    print("=" * 70)
    print("  ✅ Discovery Complete!")
    print("=" * 70)
    print()
    print("Next Steps:")
    print("  1. Review high-frequency items (appeared 2+ times)")
    print("  2. Add translations for each item (vi, en, zh, etc.)")
    print("  3. Approve items to add to master data tables")
    print("  4. Run extraction test to verify new master data is working")
    print()


def main():
    """Main function"""
    print("\n" + "=" * 70)
    print("  🚀 Quick Crawl Test - Master Data Discovery")
    print("=" * 70)
    print()
    print("  This script simulates crawling Vietnamese real estate sites")
    print("  and discovering new master data attributes.")
    print()
    print(f"  Sample Data: {len(SAMPLE_LISTINGS)} listings")
    print("  (Simulating: Batdongsan.com.vn, Mogi.vn)")
    print()
    print("=" * 70)
    print()

    # Extract master data
    results = extract_new_master_data(SAMPLE_LISTINGS)

    # Print results
    print_results(results)

    # Save to JSON for inspection
    output_file = "master_data_discovery_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Results saved to: {output_file}")
    print()


if __name__ == "__main__":
    main()

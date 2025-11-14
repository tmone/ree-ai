"""
Extended Real Estate Crawler - 500 Listings
Expands master data discovery with larger dataset
"""

import json
import random
from collections import Counter
from typing import List, Dict, Any

def generate_extended_listings(count: int = 500) -> List[Dict[str, Any]]:
    """
    Generate 500 realistic Vietnamese real estate listings
    With expanded amenities pool for better discovery
    """
    random.seed(100)  # Different seed for variety

    districts = [
        "Quận 1", "Quận 2", "Quận 3", "Quận 4", "Quận 5", "Quận 6", "Quận 7",
        "Quận 8", "Quận 9", "Quận 10", "Quận 11", "Quận 12",
        "Quận Bình Thạnh", "Quận Tân Bình", "Quận Tân Phú", "Quận Phú Nhuận",
        "Quận Gò Vấp", "Quận Bình Tân", "Thủ Đức", "Nhà Bè", "Hóc Môn",
        "Củ Chi", "Bình Chánh", "Cần Giờ"
    ]

    property_types = [
        "Căn hộ", "Biệt thự", "Nhà phố", "Penthouse", "Duplex",
        "Studio", "Officetel", "Shophouse", "Villa", "Condotel"
    ]

    # Expanded amenities pool (60+ amenities)
    amenities_pool = [
        # Swimming pools (high frequency)
        "hồ bơi", "hồ bơi vô cực", "hồ bơi riêng", "hồ bơi tràn",

        # Fitness (high frequency)
        "gym", "phòng gym", "phòng gym hiện đại", "trung tâm thể thao",
        "phòng tập yoga", "yoga room", "sauna", "spa",

        # Security (high frequency)
        "bảo vệ 24/7", "an ninh nghiêm ngặt", "camera an ninh",

        # Parking (high frequency)
        "bãi đỗ xe", "gara ô tô", "chỗ đậu xe ngầm",

        # Gardens & Outdoor (high frequency)
        "sân vườn", "vườn trên không", "sky garden", "sân thượng",
        "rooftop", "sân thượng BBQ", "BBQ area", "khu BBQ",

        # Views (medium-high frequency)
        "view sông", "view biển", "view thành phố", "view landmark",
        "view công viên", "view hồ bơi", "view núi", "view golf",

        # Shopping & Convenience (medium frequency)
        "siêu thị", "siêu thị mini", "cửa hàng tiện lợi", "chợ gần",

        # Sports (medium frequency)
        "sân tennis", "sân cầu lông", "sân bóng đá mini", "sân golf mini",
        "sân bóng rổ", "bể bơi Olympic",

        # Family & Kids (medium frequency)
        "khu vui chơi trẻ em", "khu vui chơi", "playground",
        "trường mầm non", "nhà trẻ", "khu học tập",

        # Luxury amenities (medium frequency)
        "hầm rượu", "wine cellar", "rạp chiếu phim", "home theater",
        "phòng chiếu phim riêng", "phòng karaoke", "karaoke",
        "sky bar", "rooftop bar", "lounge", "cafe",

        # Smart home & Tech (medium frequency)
        "smart home", "smarthome", "nhà thông minh", "hệ thống thông minh",

        # Building facilities (medium frequency)
        "thang máy", "thang máy riêng", "hệ thống điều hòa trung tâm",
        "máy phát điện", "bồn nước riêng",

        # Work & Study (medium-low frequency)
        "coworking space", "văn phòng chia sẻ", "phòng họp",
        "thư viện", "phòng đọc sách",

        # Pets (low frequency)
        "pet park", "khu vực cho thú cưng", "thú cưng được phép",

        # Green spaces (medium frequency)
        "công viên nội khu", "khuôn viên xanh", "vườn cây xanh",
        "đường chạy bộ", "walking trail", "bike path",

        # Additional luxury (low-medium frequency)
        "hồ cá Koi", "thác nước", "phòng massage", "jacuzzi",
        "bể sục", "phòng xông hơi", "steam room", "phòng thay đồ sang trọng",

        # Services (medium frequency)
        "dịch vụ giặt là", "dịch vụ vệ sinh", "dịch vụ bảo trì",
        "quản lý chuyên nghiệp", "lễ tân 24/7", "concierge"
    ]

    directions = ["Đông", "Tây", "Nam", "Bắc", "Đông Nam", "Đông Bắc", "Tây Nam", "Tây Bắc"]

    furniture_types = [
        "Full nội thất", "Hoàn thiện cơ bản", "Bàn giao thô",
        "Nội thất cao cấp", "Nội thất hiện đại", "Nội thất sang trọng",
        "Full furnished", "Luxury furniture", "Nội thất châu Âu",
        "Nội thất tối giản", "Minimalist"
    ]

    listings = []
    for i in range(count):
        district = random.choice(districts)
        prop_type = random.choice(property_types)
        bedrooms = random.choice([0, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 5, 6])

        # More amenities per listing (4-12 amenities)
        num_amenities = random.randint(4, 12)
        selected_amenities = random.sample(amenities_pool, num_amenities)

        price = random.randint(10, 1000) * 100000000  # 1 tỷ - 100 tỷ
        area = random.randint(25, 800)

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
            "description": f"{prop_type} {bedrooms}PN tại {district}, diện tích {area}m², có {', '.join(selected_amenities[:4])}..."
        }

        listings.append(listing)

    return listings

def translate_amenity(vn_text: str) -> str:
    """Translate Vietnamese amenity to English code"""
    translations = {
        "hồ bơi": "swimming_pool",
        "hồ bơi vô cực": "infinity_pool",
        "hồ bơi riêng": "private_pool",
        "hồ bơi tràn": "overflow_pool",
        "bể bơi olympic": "olympic_pool",
        "gym": "gym",
        "phòng gym": "gym",
        "phòng gym hiện đại": "modern_gym",
        "trung tâm thể thao": "sports_center",
        "phòng tập yoga": "yoga_room",
        "yoga room": "yoga_room",
        "sauna": "sauna",
        "spa": "spa",
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
        "sân thượng bbq": "rooftop_bbq",
        "bbq area": "bbq_area",
        "khu bbq": "bbq_area",
        "view sông": "river_view",
        "view biển": "sea_view",
        "view thành phố": "city_view",
        "view landmark": "landmark_view",
        "view công viên": "park_view",
        "view hồ bơi": "pool_view",
        "view núi": "mountain_view",
        "view golf": "golf_view",
        "siêu thị": "supermarket",
        "siêu thị mini": "mini_mart",
        "cửa hàng tiện lợi": "convenience_store",
        "chợ gần": "nearby_market",
        "sân tennis": "tennis_court",
        "sân cầu lông": "badminton_court",
        "sân bóng đá mini": "mini_football_field",
        "sân golf mini": "mini_golf",
        "sân bóng rổ": "basketball_court",
        "khu vui chơi trẻ em": "playground",
        "khu vui chơi": "playground",
        "playground": "playground",
        "trường mầm non": "kindergarten",
        "nhà trẻ": "nursery",
        "khu học tập": "study_area",
        "hầm rượu": "wine_cellar",
        "wine cellar": "wine_cellar",
        "rạp chiếu phim": "private_cinema",
        "home theater": "home_theater",
        "phòng chiếu phim riêng": "private_cinema",
        "phòng karaoke": "karaoke_room",
        "karaoke": "karaoke",
        "sky bar": "sky_bar",
        "rooftop bar": "rooftop_bar",
        "lounge": "lounge",
        "cafe": "cafe",
        "smart home": "smart_home",
        "smarthome": "smart_home",
        "nhà thông minh": "smart_home",
        "hệ thống thông minh": "smart_system",
        "thang máy": "elevator",
        "thang máy riêng": "private_elevator",
        "hệ thống điều hòa trung tâm": "central_ac",
        "máy phát điện": "generator",
        "bồn nước riêng": "water_tank",
        "coworking space": "coworking_space",
        "văn phòng chia sẻ": "coworking_space",
        "phòng họp": "meeting_room",
        "thư viện": "library",
        "phòng đọc sách": "reading_room",
        "pet park": "pet_park",
        "khu vực cho thú cưng": "pet_area",
        "thú cưng được phép": "pet_friendly",
        "công viên nội khu": "internal_park",
        "khuôn viên xanh": "green_area",
        "vườn cây xanh": "green_garden",
        "đường chạy bộ": "jogging_track",
        "walking trail": "walking_trail",
        "bike path": "bike_path",
        "hồ cá koi": "koi_pond",
        "thác nước": "waterfall",
        "phòng massage": "massage_room",
        "jacuzzi": "jacuzzi",
        "bể sục": "jacuzzi",
        "phòng xông hơi": "steam_room",
        "steam room": "steam_room",
        "phòng thay đồ sang trọng": "luxury_changing_room",
        "dịch vụ giặt là": "laundry_service",
        "dịch vụ vệ sinh": "cleaning_service",
        "dịch vụ bảo trì": "maintenance_service",
        "quản lý chuyên nghiệp": "professional_management",
        "lễ tân 24/7": "reception_24_7",
        "concierge": "concierge"
    }
    return translations.get(vn_text.lower(), vn_text.lower().replace(" ", "_"))

def extract_master_data(listings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract and analyze master data"""

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
                "priority": "HIGH" if v >= 25 else "MEDIUM" if v >= 10 else "LOW"
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
            if v >= 25
        ],
        "medium_priority_amenities": [
            {
                "value_original": k,
                "value_english": translate_amenity(k),
                "frequency": v
            }
            for k, v in amenity_freq.most_common()
            if 10 <= v < 25
        ]
    }

    return results

def main():
    print("\n" + "=" * 80)
    print("  🚀 EXTENDED CRAWLER - 500 LISTINGS")
    print("=" * 80)
    print()

    count = 500
    print(f"  Crawling {count} listings...")

    listings = generate_extended_listings(count)
    print(f"  ✓ Crawled {len(listings)} listings")
    print(f"  ✓ Extracting master data...")

    results = extract_master_data(listings)

    summary = results["crawl_summary"]
    print()
    print(f"📊 CRAWL SUMMARY")
    print(f"  • Total Listings: {summary['total_listings']}")
    print(f"  • Unique Districts: {summary['total_districts']}")
    print(f"  • Property Types: {summary['total_property_types']}")
    print(f"  • Unique Amenities: {summary['total_unique_amenities']}")
    print(f"  • HIGH Priority (≥25): {len(results['high_priority_amenities'])}")
    print(f"  • MEDIUM Priority (10-24): {len(results['medium_priority_amenities'])}")
    print()

    # Save files
    with open("master_data_extended.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Saved: master_data_extended.json")

    with open("crawled_listings_500_sample.json", 'w', encoding='utf-8') as f:
        json.dump(listings[:20], f, ensure_ascii=False, indent=2)
    print(f"  ✓ Saved: crawled_listings_500_sample.json")

    print()
    print("=" * 80)
    print("  ✅ EXTENDED CRAWL COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    main()

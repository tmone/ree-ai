"""
Data Normalization Utilities for Crawl4AI Property Data

Normalizes inconsistent crawled data into structured formats:
- Price: "5 tỷ" → 5000000000, "3.2 triệu" → 3200000
- Area: "95m²" → 95, "95 m²" → 95
- Location: "Quận 7, TP. Hồ Chí Minh" → {district: "Quận 7", city: "Hồ Chí Minh"}
"""
import re
from typing import Dict, Any, Optional, Tuple


def normalize_price(price_text: str) -> Optional[float]:
    """
    Normalize Vietnamese price text to numeric value

    Examples:
        "5 tỷ" → 5000000000.0
        "5,77 tỷ" → 5770000000.0
        "3.2 triệu" → 3200000.0
        "500 triệu" → 500000000.0
        "12.5 tỷ VNĐ" → 12500000000.0
        "Thỏa thuận" → None

    Args:
        price_text: Price string from crawled data

    Returns:
        Numeric price value or None if cannot parse
    """
    if not price_text or not isinstance(price_text, str):
        return None

    # Clean text
    text = price_text.strip().lower()

    # Handle special cases
    if any(keyword in text for keyword in ['thỏa thuận', 'liên hệ', 'n/a', 'contact']):
        return None

    # Extract number and unit
    # Pattern: number (with . or , as decimal) + optional space + unit (tỷ/triệu)
    pattern = r'([\d,\.]+)\s*(tỷ|triệu|ty|trieu)'
    match = re.search(pattern, text)

    if not match:
        return None

    number_str = match.group(1)
    unit = match.group(2)

    # Normalize number string (handle both . and , as decimal separator)
    # Vietnamese uses both: "5,77" and "5.77"
    number_str = number_str.replace(',', '.')

    try:
        number = float(number_str)
    except ValueError:
        return None

    # Convert to VND
    if unit in ['tỷ', 'ty']:
        # 1 tỷ = 1,000,000,000 VND
        return number * 1_000_000_000
    elif unit in ['triệu', 'trieu']:
        # 1 triệu = 1,000,000 VND
        return number * 1_000_000

    return None


def normalize_area(area_text: str) -> Optional[float]:
    """
    Normalize area text to numeric value in m²

    Examples:
        "95m²" → 95.0
        "95 m²" → 95.0
        "120.5m2" → 120.5
        "N/A" → None

    Args:
        area_text: Area string from crawled data

    Returns:
        Numeric area value or None if cannot parse
    """
    if not area_text or not isinstance(area_text, str):
        return None

    # Clean text
    text = area_text.strip().lower()

    # Handle special cases
    if any(keyword in text for keyword in ['n/a', 'liên hệ', 'contact']):
        return None

    # Extract number (with . or , as decimal)
    # Pattern: number + optional space + m² or m2
    pattern = r'([\d,\.]+)\s*(?:m²|m2|mét vuông)'
    match = re.search(pattern, text)

    if not match:
        return None

    number_str = match.group(1)

    # Normalize decimal separator
    number_str = number_str.replace(',', '.')

    try:
        return float(number_str)
    except ValueError:
        return None


def extract_location_parts(location_text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract district and city from Vietnamese location text

    Examples:
        "Quận 7, TP. Hồ Chí Minh" → ("Quận 7", "Hồ Chí Minh")
        "Quận Bình Thạnh, TP. Hồ Chí Minh" → ("Quận Bình Thạnh", "Hồ Chí Minh")
        "Hà Nội" → (None, "Hà Nội")

    Args:
        location_text: Location string from crawled data

    Returns:
        Tuple of (district, city) or (None, None)
    """
    if not location_text or not isinstance(location_text, str):
        return None, None

    text = location_text.strip()

    # Split by comma
    parts = [p.strip() for p in text.split(',')]

    if len(parts) == 0:
        return None, None

    district = None
    city = None

    # Identify district (Quận X, Huyện Y, District Z)
    for part in parts:
        if any(prefix in part for prefix in ['Quận', 'Huyện', 'District', 'Phường']):
            district = part
            break

    # Identify city (last part usually, or look for TP/Thành phố keywords)
    for part in reversed(parts):
        # Clean city name
        clean_part = part
        # Remove "TP." prefix
        clean_part = re.sub(r'^TP\.\s*', '', clean_part)
        # Remove "Thành phố" prefix
        clean_part = re.sub(r'^Thành phố\s*', '', clean_part, flags=re.IGNORECASE)

        if clean_part:
            city = clean_part
            break

    return district, city


def format_price_display(price: float) -> str:
    """
    Format numeric price to Vietnamese display format

    Examples:
        5000000000 → "5 tỷ"
        5770000000 → "5.77 tỷ"
        3200000 → "3.2 triệu"
        500000000 → "500 triệu"

    Args:
        price: Numeric price value

    Returns:
        Formatted price string
    """
    if not price or price <= 0:
        return "Giá thỏa thuận"

    # Convert to tỷ if >= 1 billion
    if price >= 1_000_000_000:
        value = price / 1_000_000_000
        # Format with appropriate decimal places
        if value >= 100:
            return f"{value:.0f} tỷ"
        elif value >= 10:
            return f"{value:.1f} tỷ"
        else:
            return f"{value:.2f} tỷ"

    # Convert to triệu if >= 1 million
    elif price >= 1_000_000:
        value = price / 1_000_000
        if value >= 100:
            return f"{value:.0f} triệu"
        else:
            return f"{value:.1f} triệu"

    # Small values
    else:
        return f"{price:,.0f} VNĐ"


def format_area_display(area: float) -> str:
    """
    Format numeric area to display format

    Examples:
        95.0 → "95 m²"
        120.5 → "120.5 m²"

    Args:
        area: Numeric area value

    Returns:
        Formatted area string
    """
    if not area or area <= 0:
        return "N/A"

    # Remove .0 for whole numbers
    if area == int(area):
        return f"{int(area)} m²"
    else:
        return f"{area:.1f} m²"


def normalize_property_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize complete property data from Crawl4AI

    Converts:
    - price: text → number (and keeps formatted text for display)
    - area: text → number (and keeps formatted text for display)
    - location: text → {district, city}
    - bedrooms/bathrooms: ensure int type

    Args:
        raw_data: Raw property data from crawler

    Returns:
        Normalized property data with both numeric and display formats
    """
    normalized = raw_data.copy()

    # Normalize price
    if 'price' in raw_data:
        price_raw = raw_data['price']

        if isinstance(price_raw, str):
            # Extract numeric price
            price_numeric = normalize_price(price_raw)

            if price_numeric:
                normalized['price'] = price_numeric
                normalized['price_display'] = format_price_display(price_numeric)
            else:
                normalized['price'] = 0
                normalized['price_display'] = price_raw  # Keep original text

        elif isinstance(price_raw, (int, float)):
            # Already numeric
            normalized['price'] = float(price_raw)
            normalized['price_display'] = format_price_display(price_raw)

    # Normalize area
    if 'area' in raw_data:
        area_raw = raw_data['area']

        if isinstance(area_raw, str):
            # Extract numeric area
            area_numeric = normalize_area(area_raw)

            if area_numeric:
                normalized['area'] = area_numeric
                normalized['area_display'] = format_area_display(area_numeric)
            else:
                normalized['area'] = 0
                normalized['area_display'] = area_raw  # Keep original text

        elif isinstance(area_raw, (int, float)):
            # Already numeric
            normalized['area'] = float(area_raw)
            normalized['area_display'] = format_area_display(area_raw)

    # Extract district and city from location
    if 'location' in raw_data:
        district, city = extract_location_parts(raw_data['location'])

        if district:
            normalized['district'] = district
        if city:
            normalized['city'] = city

    # Ensure bedrooms/bathrooms are integers
    for field in ['bedrooms', 'bathrooms']:
        if field in raw_data:
            value = raw_data[field]

            if isinstance(value, str):
                try:
                    normalized[field] = int(value)
                except (ValueError, TypeError):
                    normalized[field] = 0
            elif isinstance(value, (int, float)):
                normalized[field] = int(value)
            else:
                normalized[field] = 0

    return normalized


# Quick test
if __name__ == "__main__":
    # Test price normalization
    test_prices = [
        "5 tỷ",
        "5,77 tỷ",
        "3.2 triệu",
        "500 triệu",
        "12.5 tỷ VNĐ",
        "Thỏa thuận"
    ]

    print("=== PRICE NORMALIZATION ===")
    for price_text in test_prices:
        numeric = normalize_price(price_text)
        if numeric:
            display = format_price_display(numeric)
            print(f"{price_text:20} → {numeric:15,.0f} VNĐ → {display}")
        else:
            print(f"{price_text:20} → None")

    print("\n=== AREA NORMALIZATION ===")
    test_areas = ["95m²", "95 m²", "120.5m2", "N/A"]
    for area_text in test_areas:
        numeric = normalize_area(area_text)
        if numeric:
            display = format_area_display(numeric)
            print(f"{area_text:20} → {numeric:10} m² → {display}")
        else:
            print(f"{area_text:20} → None")

    print("\n=== LOCATION EXTRACTION ===")
    test_locations = [
        "Quận 7, TP. Hồ Chí Minh",
        "Quận Bình Thạnh, TP. Hồ Chí Minh",
        "Hà Nội"
    ]
    for location in test_locations:
        district, city = extract_location_parts(location)
        print(f"{location:35} → district={district}, city={city}")

    print("\n=== FULL NORMALIZATION ===")
    test_property = {
        "title": "Nhà mặt tiền Quận 7",
        "price": "5,77 tỷ",
        "location": "Quận 7, TP. Hồ Chí Minh",
        "bedrooms": "3",
        "bathrooms": 2,
        "area": "95m²",
        "description": "Nhà đẹp 3 phòng ngủ",
        "url": "https://example.com",
        "source": "batdongsan.com.vn"
    }

    normalized = normalize_property_data(test_property)
    print("\nOriginal:")
    for k, v in test_property.items():
        print(f"  {k:15} = {v}")

    print("\nNormalized:")
    for k, v in normalized.items():
        print(f"  {k:15} = {v}")

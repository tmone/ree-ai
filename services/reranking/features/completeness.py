"""
Property Completeness Feature Calculator
Measures information richness of property listing

CTO Priority 4: Re-ranking Service
Feature Category: Property Quality (10% of 40%)
"""

from typing import Dict, List, Any


def calculate_completeness(property_data: Dict[str, Any]) -> float:
    """
    Calculate completeness score based on information richness

    Args:
        property_data: Property dictionary

    Returns:
        float: Completeness score [0.0, 1.0]
    """
    # Required fields (70% weight)
    required_fields = [
        'title',
        'description',
        'price',
        'area',
        'district',
        'property_type',
        'listing_type'
    ]

    # Optional/recommended fields (30% weight)
    optional_fields = [
        'images',
        'videos',
        'virtual_tour_url',
        'contact_phone',
        'contact_email',
        'bedrooms',
        'bathrooms',
        'ward',
        'street_address',
        'amenities'
    ]

    # Check required fields
    required_count = 0
    for field in required_fields:
        value = property_data.get(field)
        if value is not None and value != "" and value != []:
            required_count += 1

    required_score = required_count / len(required_fields)

    # Check optional fields
    optional_count = 0
    for field in optional_fields:
        value = property_data.get(field)
        if value is not None and value != "" and value != []:
            optional_count += 1

    optional_score = optional_count / len(optional_fields)

    # Weighted combination (70% required, 30% optional)
    completeness_score = 0.7 * required_score + 0.3 * optional_score

    return min(max(completeness_score, 0.0), 1.0)


def calculate_image_quality(property_data: Dict[str, Any]) -> float:
    """
    Calculate image quality score

    Args:
        property_data: Property dictionary

    Returns:
        float: Image quality score [0.0, 1.0]
    """
    images = property_data.get('images', [])
    videos = property_data.get('videos', [])
    virtual_tour = property_data.get('virtual_tour_url')

    # Number of images (normalized to 0-10 images)
    num_images = len(images) if isinstance(images, list) else 0
    image_score = min(num_images / 10.0, 1.0)

    # Bonus for videos
    video_bonus = 0.1 if videos and len(videos) > 0 else 0.0

    # Bonus for virtual tour
    vr_bonus = 0.2 if virtual_tour else 0.0

    # Combine (max 1.0)
    quality_score = min(image_score + video_bonus + vr_bonus, 1.0)

    return quality_score


def calculate_description_quality(property_data: Dict[str, Any]) -> float:
    """
    Calculate description quality score

    Args:
        property_data: Property dictionary

    Returns:
        float: Description quality score [0.0, 1.0]
    """
    description = property_data.get('description', '')

    if not description:
        return 0.0

    # Length score (optimal: 200-500 chars)
    desc_len = len(description)
    if desc_len < 50:
        length_score = desc_len / 50.0  # Too short
    elif desc_len <= 500:
        length_score = 1.0  # Optimal range
    else:
        # Decay for too long descriptions (max 1000 chars)
        length_score = max(1.0 - (desc_len - 500) / 500.0, 0.5)

    # Keywords presence (simple check)
    keywords = [
        'giá', 'diện tích', 'phòng', 'vị trí', 'tiện ích',
        'gần', 'view', 'mặt tiền', 'hẻm', 'đường'
    ]

    keyword_count = sum(1 for kw in keywords if kw in description.lower())
    keyword_score = min(keyword_count / 5.0, 1.0)  # At least 5 keywords = 1.0

    # Professional language check (no excessive caps/emojis)
    # Simple heuristic: less than 10% uppercase
    if desc_len > 0:
        uppercase_ratio = sum(1 for c in description if c.isupper()) / desc_len
        professional_score = 1.0 if uppercase_ratio < 0.1 else 0.7
    else:
        professional_score = 0.5

    # Weighted combination
    quality_score = (
        0.4 * length_score +
        0.4 * keyword_score +
        0.2 * professional_score
    )

    return min(max(quality_score, 0.0), 1.0)


def calculate_verification_score(property_data: Dict[str, Any]) -> float:
    """
    Calculate verification status score

    Args:
        property_data: Property dictionary

    Returns:
        float: Verification score [0.0, 1.0]
    """
    verified = property_data.get('verified', False)

    if verified:
        return 1.0
    else:
        # Unverified properties get 0.5 (not penalized too heavily)
        return 0.5


def calculate_property_quality_score(property_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate overall property quality score (40% of total)

    Returns dictionary with individual scores and weighted total

    Args:
        property_data: Property dictionary

    Returns:
        dict: Individual scores and total property quality score
    """
    # Individual scores
    completeness = calculate_completeness(property_data)
    image_quality = calculate_image_quality(property_data)
    description_quality = calculate_description_quality(property_data)
    verification = calculate_verification_score(property_data)

    # Weighted combination (each 10% of total, so 40% combined)
    # Normalized to [0, 1] range
    property_quality = (
        0.25 * completeness +      # 10% of 40%
        0.25 * image_quality +     # 10% of 40%
        0.25 * description_quality + # 10% of 40%
        0.25 * verification         # 10% of 40%
    )

    return {
        'completeness': completeness,
        'image_quality': image_quality,
        'description_quality': description_quality,
        'verification': verification,
        'property_quality_total': property_quality
    }

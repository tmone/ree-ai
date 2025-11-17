"""
Engagement Feature Calculator
Measures user interaction signals with property listing

CTO Priority 4: Re-ranking Service
Feature Category: Engagement (15% of total)

Phase 2: Queries real analytics data from database
"""

from typing import Dict, Any


async def calculate_user_behavior_score(
    property_id: str,
    time_window_days: int = 7,
    db = None
) -> float:
    """
    Calculate engagement score based on recent user behavior from database

    Args:
        property_id: Property ID
        time_window_days: Time window for aggregation (default: 7 days)
        db: Database connection (RerankingDB instance)

    Returns:
        float: Engagement score [0.0, 1.0]
    """
    if not db:
        # Fallback to Phase 1 default score
        return 0.6

    try:
        stats = await db.get_property_stats(property_id, time_window_days)

        if not stats:
            # New property or no stats: return low score
            return 0.3

        # Extract metrics
        views = stats.get('views', 0)
        inquiries = stats.get('inquiries', 0)
        favorites = stats.get('favorites', 0)

        # Calculate per-day averages
        views_per_day = views / time_window_days if time_window_days > 0 else 0
        inquiries_per_day = inquiries / time_window_days if time_window_days > 0 else 0
        favorites_per_day = favorites / time_window_days if time_window_days > 0 else 0

        # Weighted combination with caps
        # High engagement property: 10 views/day, 2 inquiries/day, 1 favorite/day
        engagement_score = (
            0.3 * min(views_per_day / 10.0, 1.0) +      # Cap at 10 views/day
            0.4 * min(inquiries_per_day / 2.0, 1.0) +   # Cap at 2 inquiries/day
            0.3 * min(favorites_per_day / 1.0, 1.0)     # Cap at 1 favorite/day
        )

        return min(max(engagement_score, 0.0), 1.0)

    except Exception as e:
        # On error, return moderate default score
        return 0.6


async def calculate_ctr_score(property_id: str, db = None) -> float:
    """
    Calculate Click-Through Rate score from search results

    CTR = (clicks on property in search) / (times shown in search)

    Args:
        property_id: Property ID
        db: Database connection (RerankingDB instance)

    Returns:
        float: CTR score [0.0, 1.0]
    """
    if not db:
        # Fallback to Phase 1 default score
        return 0.5

    try:
        stats = await db.get_property_stats(property_id, time_window_days=30)

        if not stats:
            # New property or no stats: return moderate score
            return 0.5

        # Extract CTR (already calculated by database trigger)
        ctr = stats.get('ctr', 0.0)

        # CTR is already in [0, 1] range
        # But normalize it: typical good CTR is 0.1 (10%)
        # Scale so 0.1 CTR = 1.0 score
        normalized_ctr = min(ctr / 0.1, 1.0)

        return normalized_ctr

    except Exception as e:
        # On error, return moderate default score
        return 0.5


async def calculate_engagement_score(
    property_data: Dict[str, Any],
    db = None
) -> Dict[str, float]:
    """
    Calculate overall engagement score (15% of total)

    Args:
        property_data: Property dictionary
        db: Database connection (RerankingDB instance)

    Returns:
        dict: Individual scores and total engagement score
    """
    property_id = property_data.get('property_id', '')

    # User behavior signals (10% of total -> 66.7% of this category)
    user_behavior = await calculate_user_behavior_score(property_id, time_window_days=7, db=db)

    # CTR from search (5% of total -> 33.3% of this category)
    ctr = await calculate_ctr_score(property_id, db=db)

    # Weighted combination
    # 66.7% user behavior + 33.3% CTR
    engagement_total = 0.667 * user_behavior + 0.333 * ctr

    return {
        'user_behavior': user_behavior,
        'ctr': ctr,
        'engagement_total': engagement_total
    }

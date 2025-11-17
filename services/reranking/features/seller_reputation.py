"""
Seller Reputation Feature Calculator
Measures seller's track record and trustworthiness

CTO Priority 4: Re-ranking Service
Feature Category: Seller Reputation (20% of total)

NOTE: Phase 1 uses placeholder/mock data
Phase 2 will integrate with seller analytics database
"""

from typing import Dict, Any
from datetime import datetime, timezone


def calculate_seller_performance(owner_id: str) -> float:
    """
    Calculate seller's historical performance score

    NOTE: Phase 1 placeholder - returns default score
    Phase 2 will query seller_stats database

    Args:
        owner_id: Seller's user ID

    Returns:
        float: Performance score [0.0, 1.0]
    """
    # TODO Phase 2: Query actual seller statistics
    # seller_stats = db.get_seller_stats(owner_id)
    # response_rate = seller_stats['responses'] / seller_stats['inquiries']
    # avg_response_time = seller_stats['avg_response_time_hours']
    # closure_rate = seller_stats['closed_deals'] / seller_stats['total_listings']

    # Phase 1: Return moderate default score
    # This assumes average seller performance until we have data
    default_score = 0.7

    return default_score


def calculate_account_age_score(property_data: Dict[str, Any]) -> float:
    """
    Calculate score based on seller's account age

    NOTE: Phase 1 estimates from property created_at
    Phase 2 will use actual account creation date

    Args:
        property_data: Property dictionary

    Returns:
        float: Account age score [0.0, 1.0]
    """
    created_at = property_data.get('created_at', '')

    if not created_at:
        return 0.5  # Default for missing data

    try:
        # Estimate account age from property posting
        # In reality, we'd query user.created_at
        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        days_old = (now - created_date).days

        if days_old < 30:
            # New seller (<1 month)
            return 0.5
        elif days_old < 180:
            # Established (1-6 months)
            return 0.75
        else:
            # Veteran (>6 months)
            return 1.0

    except:
        return 0.5


def calculate_seller_reputation_score(property_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate overall seller reputation score (20% of total)

    Args:
        property_data: Property dictionary

    Returns:
        dict: Individual scores and total seller reputation score
    """
    owner_id = property_data.get('owner_id', 'unknown')

    # Historical performance (15% of total -> 75% of this category)
    performance = calculate_seller_performance(owner_id)

    # Account age (5% of total -> 25% of this category)
    account_age = calculate_account_age_score(property_data)

    # Weighted combination
    # 75% performance + 25% account age
    seller_reputation_total = 0.75 * performance + 0.25 * account_age

    return {
        'seller_performance': performance,
        'account_age': account_age,
        'seller_reputation_total': seller_reputation_total
    }

"""
Seller Reputation Feature Calculator
Measures seller's track record and trustworthiness

CTO Priority 4: Re-ranking Service
Feature Category: Seller Reputation (20% of total)

Phase 2: Queries real seller analytics from database
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone


async def calculate_seller_performance(
    owner_id: str,
    db = None
) -> float:
    """
    Calculate seller's historical performance score based on database statistics

    Args:
        owner_id: Seller's user ID
        db: Database connection (RerankingDB instance)

    Returns:
        float: Performance score [0.0, 1.0]
    """
    if not db:
        # Fallback to Phase 1 default score if no DB
        return 0.7

    try:
        seller_stats = await db.get_seller_stats(owner_id)

        if not seller_stats:
            # New seller or no stats: return moderate score
            return 0.5

        # Extract metrics
        response_rate = seller_stats.get('response_rate', 0.0)
        closure_rate = seller_stats.get('closure_rate', 0.0)
        avg_response_time = seller_stats.get('avg_response_time_hours', 24.0)

        # Calculate response time score (1.0 / (1 + hours/24))
        # Fast response = high score
        response_time_score = 1.0 / (1.0 + avg_response_time / 24.0)

        # Weighted combination:
        # 40% response rate + 30% response time + 30% closure rate
        performance_score = (
            0.4 * response_rate +
            0.3 * response_time_score +
            0.3 * closure_rate
        )

        return min(max(performance_score, 0.0), 1.0)

    except Exception as e:
        # On error, return moderate default score
        return 0.7


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


async def calculate_seller_reputation_score(
    property_data: Dict[str, Any],
    db = None
) -> Dict[str, float]:
    """
    Calculate overall seller reputation score (20% of total)

    Args:
        property_data: Property dictionary
        db: Database connection (RerankingDB instance)

    Returns:
        dict: Individual scores and total seller reputation score
    """
    owner_id = property_data.get('owner_id', 'unknown')

    # Historical performance (15% of total -> 75% of this category)
    performance = await calculate_seller_performance(owner_id, db)

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

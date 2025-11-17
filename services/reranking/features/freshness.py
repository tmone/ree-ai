"""
Freshness Feature Calculator
Measures listing recency and update frequency

CTO Priority 4: Re-ranking Service
Feature Category: Freshness (15% of total)
"""

from typing import Dict, Any
from datetime import datetime, timezone
import math


def calculate_days_since_posted(created_at: str) -> int:
    """
    Calculate days since property was posted

    Args:
        created_at: ISO format timestamp string

    Returns:
        int: Days since posted
    """
    if not created_at:
        return 365  # Default to 1 year for missing data

    try:
        # Parse ISO format timestamp
        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        delta = now - created_date
        return max(delta.days, 0)
    except:
        # If parsing fails, assume old listing
        return 365


def calculate_freshness_decay(days_since_posted: int) -> float:
    """
    Calculate freshness score using exponential decay

    Args:
        days_since_posted: Days since property was posted

    Returns:
        float: Freshness score [0.0, 1.0]
    """
    # Half-life: Property loses half relevance after 30 days
    half_life_days = 30.0

    # Exponential decay: score = 2^(-days / half_life)
    freshness_score = math.pow(2, -days_since_posted / half_life_days)

    return min(max(freshness_score, 0.0), 1.0)


def calculate_recent_update_bonus(property_data: Dict[str, Any]) -> float:
    """
    Calculate bonus for recent updates

    Args:
        property_data: Property dictionary

    Returns:
        float: Update bonus [0.0, 0.3]
    """
    created_at = property_data.get('created_at')
    updated_at = property_data.get('updated_at')

    if not created_at or not updated_at:
        return 0.0

    try:
        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)

        # Days since last update
        days_since_update = (now - updated_date).days

        # Property was updated (not just created)
        was_updated = (updated_date - created_date).days > 0

        if was_updated and days_since_update <= 7:
            # Updated within 7 days: +0.2 bonus
            return 0.2
        elif was_updated and days_since_update <= 30:
            # Updated within 30 days: +0.1 bonus
            return 0.1
        else:
            return 0.0

    except:
        return 0.0


def calculate_freshness_score(property_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate overall freshness score (15% of total)

    Args:
        property_data: Property dictionary

    Returns:
        dict: Individual scores and total freshness score
    """
    created_at = property_data.get('created_at', '')

    # Calculate days since posted
    days_since_posted = calculate_days_since_posted(created_at)

    # Listing age decay (10% of total)
    age_decay = calculate_freshness_decay(days_since_posted)

    # Recent update bonus (5% of total)
    update_bonus = calculate_recent_update_bonus(property_data)

    # Combine (age_decay is base, update_bonus is additive)
    # Normalized to [0, 1] range
    # 66.7% age decay + 33.3% update bonus
    freshness_total = min(0.667 * age_decay + 0.333 * update_bonus, 1.0)

    return {
        'days_since_posted': days_since_posted,
        'age_decay': age_decay,
        'update_bonus': update_bonus,
        'freshness_total': freshness_total
    }

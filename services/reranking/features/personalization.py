"""
Personalization Feature Calculator
Matches property with user preferences and history

CTO Priority 4: Re-ranking Service
Feature Category: Personalization (10% of total)

Phase 2: Queries real user preferences and interaction history from database
"""

from typing import Dict, Any, Optional


async def calculate_preference_match(
    user_id: Optional[str],
    property_data: Dict[str, Any],
    db = None
) -> float:
    """
    Calculate how well property matches user's preferences based on database

    Args:
        user_id: User ID (None for anonymous users)
        property_data: Property dictionary
        db: Database connection (RerankingDB instance)

    Returns:
        float: Preference match score [0.0, 1.0]
    """
    if not user_id:
        # Anonymous user: return neutral score
        return 0.5

    if not db:
        # Fallback to Phase 1 default score
        return 0.7

    try:
        user_prefs = await db.get_user_preferences(user_id)

        if not user_prefs:
            # New user or no preferences: return neutral score
            return 0.5

        # Extract property attributes
        price = property_data.get('price', 0)
        district = property_data.get('district', '')
        property_type = property_data.get('property_type', '')

        # Price range affinity
        min_price = user_prefs.get('min_price')
        max_price = user_prefs.get('max_price')

        if min_price and max_price:
            if min_price <= price <= max_price:
                price_match = 1.0
            else:
                # Partial match if close to range
                if price < min_price:
                    ratio = price / min_price if min_price > 0 else 0
                else:
                    ratio = max_price / price if price > 0 else 0
                price_match = max(ratio, 0.3)  # At least 0.3
        else:
            price_match = 0.7  # No preference set

        # District preference
        preferred_districts = user_prefs.get('preferred_districts', [])
        if preferred_districts:
            district_match = 1.0 if district in preferred_districts else 0.5
        else:
            district_match = 0.7  # No preference set

        # Property type preference
        preferred_types = user_prefs.get('preferred_property_types', [])
        if preferred_types:
            type_match = 1.0 if property_type in preferred_types else 0.6
        else:
            type_match = 0.7  # No preference set

        # Weighted combination
        # 40% price + 30% district + 30% type
        preference_score = (
            0.4 * price_match +
            0.3 * district_match +
            0.3 * type_match
        )

        return min(max(preference_score, 0.0), 1.0)

    except Exception as e:
        # On error, return moderate default score
        return 0.7


async def calculate_interaction_history(
    user_id: Optional[str],
    property_id: str,
    db = None
) -> float:
    """
    Calculate score based on user's previous interactions with this property

    Uses search_interactions table to check if user has:
    - Clicked this property before
    - Favorited this property
    - Sent inquiry about this property

    Args:
        user_id: User ID (None for anonymous users)
        property_id: Property ID
        db: Database connection (RerankingDB instance)

    Returns:
        float: Interaction history score [0.0, 1.0]
    """
    if not user_id:
        # Anonymous user: no history
        return 0.5

    if not db or not db.pool:
        # Fallback to Phase 1 default score
        return 0.5

    try:
        # Query search_interactions for this user + property
        row = await db.pool.fetchrow(
            """
            SELECT
                MAX(CASE WHEN clicked THEN 1 ELSE 0 END) as has_clicked,
                MAX(CASE WHEN favorited THEN 1 ELSE 0 END) as has_favorited,
                MAX(CASE WHEN inquiry_sent THEN 1 ELSE 0 END) as has_inquired
            FROM search_interactions
            WHERE user_id = $1 AND property_id = $2
            """,
            user_id,
            property_id
        )

        if not row:
            # No previous interaction: neutral score
            return 0.5

        has_clicked = row['has_clicked']
        has_favorited = row['has_favorited']
        has_inquired = row['has_inquired']

        # Scoring logic
        if has_inquired:
            # User already contacted seller: penalize to avoid duplicates
            return 0.0
        elif has_favorited:
            # User favorited: strong positive signal
            return 1.0
        elif has_clicked:
            # User viewed before: moderate positive signal
            return 0.7
        else:
            # No interaction: neutral
            return 0.5

    except Exception as e:
        # On error, return neutral default score
        return 0.5


async def calculate_personalization_score(
    property_data: Dict[str, Any],
    user_id: Optional[str] = None,
    db = None
) -> Dict[str, float]:
    """
    Calculate overall personalization score (10% of total)

    Args:
        property_data: Property dictionary
        user_id: User ID (None for anonymous users)
        db: Database connection (RerankingDB instance)

    Returns:
        dict: Individual scores and total personalization score
    """
    property_id = property_data.get('property_id', '')

    # User preference matching (7% of total -> 70% of this category)
    preference_match = await calculate_preference_match(user_id, property_data, db)

    # Previous interactions (3% of total -> 30% of this category)
    interaction_history = await calculate_interaction_history(user_id, property_id, db)

    # Weighted combination
    # 70% preference + 30% interaction history
    personalization_total = 0.7 * preference_match + 0.3 * interaction_history

    return {
        'preference_match': preference_match,
        'interaction_history': interaction_history,
        'personalization_total': personalization_total
    }

"""
Personalization Feature Calculator
Matches property with user preferences and history

CTO Priority 4: Re-ranking Service
Feature Category: Personalization (10% of total)

NOTE: Phase 1 uses basic heuristics
Phase 2 will integrate with user preference tracking database
"""

from typing import Dict, Any, Optional


def calculate_preference_match(user_id: Optional[str], property_data: Dict[str, Any]) -> float:
    """
    Calculate how well property matches user's preferences

    NOTE: Phase 1 uses basic heuristics without user profile
    Phase 2 will query user_preferences table for:
    - Preferred price range
    - Preferred districts
    - Preferred property types

    Args:
        user_id: User ID (None for anonymous users)
        property_data: Property dictionary

    Returns:
        float: Preference match score [0.0, 1.0]
    """
    if not user_id:
        # Anonymous user: return neutral score
        return 0.5

    # TODO Phase 2: Query actual user preferences
    # user_prefs = db.get_user_preferences(user_id)
    #
    # # Price range affinity
    # price = property_data.get('price', 0)
    # price_match = 1.0 if user_prefs['min_price'] <= price <= user_prefs['max_price'] else 0.5
    #
    # # District preference
    # district = property_data.get('district', '')
    # district_match = 1.0 if district in user_prefs['preferred_districts'] else 0.7
    #
    # # Property type preference
    # prop_type = property_data.get('property_type', '')
    # type_match = 1.0 if prop_type in user_prefs['preferred_types'] else 0.8
    #
    # return 0.4 * price_match + 0.3 * district_match + 0.3 * type_match

    # Phase 1: Return moderate default score
    # This assumes average preference match until we have user profiles
    default_score = 0.7

    return default_score


def calculate_interaction_history(user_id: Optional[str], property_id: str) -> float:
    """
    Calculate score based on user's previous interactions with this property

    NOTE: Phase 1 placeholder - returns default score
    Phase 2 will query user_interactions table for:
    - Previous views
    - Favorited status
    - Contact attempts

    Args:
        user_id: User ID (None for anonymous users)
        property_id: Property ID

    Returns:
        float: Interaction history score [0.0, 1.0]
    """
    if not user_id:
        # Anonymous user: no history
        return 0.5

    # TODO Phase 2: Query actual interaction history
    # interactions = db.get_user_property_interactions(user_id, property_id)
    #
    # if interactions.get('contacted'):
    #     # User already contacted seller: penalize to avoid duplicates
    #     return 0.0
    # elif interactions.get('favorited'):
    #     # User favorited: strong positive signal
    #     return 1.0
    # elif interactions.get('viewed'):
    #     # User viewed before: moderate positive signal
    #     return 0.7
    # else:
    #     # No previous interaction: neutral
    #     return 0.5

    # Phase 1: Return neutral default score
    default_score = 0.5

    return default_score


def calculate_personalization_score(
    property_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> Dict[str, float]:
    """
    Calculate overall personalization score (10% of total)

    Args:
        property_data: Property dictionary
        user_id: User ID (None for anonymous users)

    Returns:
        dict: Individual scores and total personalization score
    """
    property_id = property_data.get('property_id', '')

    # User preference matching (7% of total -> 70% of this category)
    preference_match = calculate_preference_match(user_id, property_data)

    # Previous interactions (3% of total -> 30% of this category)
    interaction_history = calculate_interaction_history(user_id, property_id)

    # Weighted combination
    # 70% preference + 30% interaction history
    personalization_total = 0.7 * preference_match + 0.3 * interaction_history

    return {
        'preference_match': preference_match,
        'interaction_history': interaction_history,
        'personalization_total': personalization_total
    }

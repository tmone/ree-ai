"""
Database connection and queries for Re-ranking Service Phase 2
CTO Priority 4 - Phase 2
"""

import os
import logging
from typing import Optional, Dict, Any, List
import asyncpg
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RerankingDB:
    """Database connection for reranking service"""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", 5432)),
                database=os.getenv("POSTGRES_DB", "ree_ai"),
                user=os.getenv("POSTGRES_USER", "ree_ai_user"),
                password=os.getenv("POSTGRES_PASSWORD", "ree_ai_pass_2025"),
                min_size=2,
                max_size=10
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.pool = None

    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    # ========================================================================
    # Seller Stats Queries
    # ========================================================================

    async def get_seller_stats(self, seller_id: str) -> Optional[Dict[str, Any]]:
        """Get seller performance statistics"""
        if not self.pool:
            return None

        try:
            row = await self.pool.fetchrow(
                """
                SELECT
                    seller_id,
                    total_listings,
                    active_listings,
                    closed_deals,
                    total_inquiries,
                    total_responses,
                    avg_response_time_hours,
                    response_rate,
                    closure_rate,
                    account_created_at
                FROM seller_stats
                WHERE seller_id = $1
                """,
                seller_id
            )

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Error getting seller stats for {seller_id}: {e}")
            return None

    # ========================================================================
    # Property Stats Queries
    # ========================================================================

    async def get_property_stats(
        self,
        property_id: str,
        time_window_days: int = 7
    ) -> Optional[Dict[str, Any]]:
        """Get property engagement statistics"""
        if not self.pool:
            return None

        try:
            # Select time window columns based on parameter
            if time_window_days == 7:
                views_col = "views_7d"
                inquiries_col = "inquiries_7d"
                favorites_col = "favorites_7d"
            elif time_window_days == 30:
                views_col = "views_30d"
                inquiries_col = "inquiries_30d"
                favorites_col = "favorites_30d"
            else:
                views_col = "views_total"
                inquiries_col = "inquiries_total"
                favorites_col = "favorites_total"

            row = await self.pool.fetchrow(
                f"""
                SELECT
                    property_id,
                    {views_col} as views,
                    {inquiries_col} as inquiries,
                    {favorites_col} as favorites,
                    search_impressions,
                    search_clicks,
                    ctr
                FROM property_stats
                WHERE property_id = $1
                """,
                property_id
            )

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Error getting property stats for {property_id}: {e}")
            return None

    async def increment_property_view(self, property_id: str):
        """Increment property view counters"""
        if not self.pool:
            return

        try:
            await self.pool.execute(
                """
                INSERT INTO property_stats (property_id, views_total, views_7d, views_30d, last_viewed_at)
                VALUES ($1, 1, 1, 1, $2)
                ON CONFLICT (property_id) DO UPDATE SET
                    views_total = property_stats.views_total + 1,
                    views_7d = property_stats.views_7d + 1,
                    views_30d = property_stats.views_30d + 1,
                    last_viewed_at = $2,
                    updated_at = $2
                """,
                property_id,
                datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error incrementing view for {property_id}: {e}")

    async def increment_property_inquiry(self, property_id: str):
        """Increment property inquiry counters"""
        if not self.pool:
            return

        try:
            await self.pool.execute(
                """
                INSERT INTO property_stats (property_id, inquiries_total, inquiries_7d, inquiries_30d, last_inquiry_at)
                VALUES ($1, 1, 1, 1, $2)
                ON CONFLICT (property_id) DO UPDATE SET
                    inquiries_total = property_stats.inquiries_total + 1,
                    inquiries_7d = property_stats.inquiries_7d + 1,
                    inquiries_30d = property_stats.inquiries_30d + 1,
                    last_inquiry_at = $2,
                    updated_at = $2
                """,
                property_id,
                datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error incrementing inquiry for {property_id}: {e}")

    async def increment_property_favorite(self, property_id: str):
        """Increment property favorite counters"""
        if not self.pool:
            return

        try:
            await self.pool.execute(
                """
                INSERT INTO property_stats (property_id, favorites_total, favorites_7d, favorites_30d, last_favorited_at)
                VALUES ($1, 1, 1, 1, $2)
                ON CONFLICT (property_id) DO UPDATE SET
                    favorites_total = property_stats.favorites_total + 1,
                    favorites_7d = property_stats.favorites_7d + 1,
                    favorites_30d = property_stats.favorites_30d + 1,
                    last_favorited_at = $2,
                    updated_at = $2
                """,
                property_id,
                datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error incrementing favorite for {property_id}: {e}")

    # ========================================================================
    # User Preferences Queries
    # ========================================================================

    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user search preferences"""
        if not self.pool:
            return None

        try:
            row = await self.pool.fetchrow(
                """
                SELECT
                    user_id,
                    min_price,
                    max_price,
                    avg_clicked_price,
                    preferred_districts,
                    preferred_cities,
                    preferred_property_types,
                    preferred_bedrooms,
                    preferred_bathrooms,
                    preferred_area_min,
                    preferred_area_max,
                    total_searches,
                    total_clicks,
                    total_inquiries,
                    total_favorites
                FROM user_preferences
                WHERE user_id = $1
                """,
                user_id
            )

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Error getting user preferences for {user_id}: {e}")
            return None

    async def update_user_preferences_from_click(
        self,
        user_id: str,
        property_price: float,
        property_district: str,
        property_type: str
    ):
        """Update user preferences based on clicked property"""
        if not self.pool:
            return

        try:
            await self.pool.execute(
                """
                INSERT INTO user_preferences (
                    user_id,
                    preferred_districts,
                    preferred_property_types,
                    total_clicks,
                    last_search_at
                )
                VALUES (
                    $1,
                    $2::JSONB,
                    $3::JSONB,
                    1,
                    $4
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    preferred_districts = CASE
                        WHEN NOT user_preferences.preferred_districts @> $2::JSONB
                        THEN user_preferences.preferred_districts || $2::JSONB
                        ELSE user_preferences.preferred_districts
                    END,
                    preferred_property_types = CASE
                        WHEN NOT user_preferences.preferred_property_types @> $3::JSONB
                        THEN user_preferences.preferred_property_types || $3::JSONB
                        ELSE user_preferences.preferred_property_types
                    END,
                    total_clicks = user_preferences.total_clicks + 1,
                    last_search_at = $4,
                    updated_at = $4
                """,
                user_id,
                f'["{property_district}"]',
                f'["{property_type}"]',
                datetime.utcnow()
            )
        except Exception as e:
            logger.error(f"Error updating user preferences for {user_id}: {e}")

    # ========================================================================
    # Search Interactions Queries
    # ========================================================================

    async def log_search_interaction(
        self,
        user_id: Optional[str],
        query: str,
        property_id: str,
        rank_position: int,
        hybrid_score: Optional[float] = None,
        rerank_score: Optional[float] = None,
        final_score: Optional[float] = None
    ) -> Optional[str]:
        """Log search interaction for ML training"""
        if not self.pool:
            return None

        try:
            row = await self.pool.fetchrow(
                """
                INSERT INTO search_interactions (
                    user_id,
                    query,
                    property_id,
                    rank_position,
                    hybrid_score,
                    rerank_score,
                    final_score
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id
                """,
                user_id,
                query,
                property_id,
                rank_position,
                hybrid_score,
                rerank_score,
                final_score
            )

            return str(row['id']) if row else None

        except Exception as e:
            logger.error(f"Error logging search interaction: {e}")
            return None

    async def update_search_interaction(
        self,
        interaction_id: str,
        clicked: Optional[bool] = None,
        inquiry_sent: Optional[bool] = None,
        favorited: Optional[bool] = None
    ):
        """Update search interaction (e.g., mark as clicked)"""
        if not self.pool:
            return

        try:
            updates = []
            params = []
            param_count = 1

            if clicked is not None:
                updates.append(f"clicked = ${param_count}")
                params.append(clicked)
                param_count += 1

            if inquiry_sent is not None:
                updates.append(f"inquiry_sent = ${param_count}")
                params.append(inquiry_sent)
                param_count += 1

            if favorited is not None:
                updates.append(f"favorited = ${param_count}")
                params.append(favorited)
                param_count += 1

            if updates:
                params.append(interaction_id)
                await self.pool.execute(
                    f"""
                    UPDATE search_interactions
                    SET {', '.join(updates)}
                    WHERE id = ${param_count}::UUID
                    """,
                    *params
                )

        except Exception as e:
            logger.error(f"Error updating search interaction {interaction_id}: {e}")


# Global database instance
db = RerankingDB()

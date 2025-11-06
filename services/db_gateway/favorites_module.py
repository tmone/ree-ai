"""
Favorites Module for DB Gateway

Handles user favorite properties:
- Add to favorites
- Remove from favorites
- Get user's favorites
- Update favorite notes
"""

from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException
import asyncpg

from shared.models.favorites import (
    FavoriteCreate,
    FavoriteUpdate,
    Favorite,
    FavoriteWithProperty,
    FavoriteListResponse
)
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


async def add_favorite(
    favorite_data: FavoriteCreate,
    user_id: str,
    db_pool: asyncpg.Pool
):
    """
    Add property to user's favorites.

    Returns existing favorite if already exists.
    """
    async with db_pool.acquire() as conn:
        try:
            # Check if already favorited
            existing = await conn.fetchrow(
                'SELECT id, created_at FROM favorites WHERE user_id = $1 AND property_id = $2',
                user_id, favorite_data.property_id
            )

            if existing:
                return {
                    "id": existing['id'],
                    "message": "Property already in favorites",
                    "already_exists": True
                }

            # Insert new favorite
            favorite_id = await conn.fetchval(
                '''
                INSERT INTO favorites (user_id, property_id, notes, created_at)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                ''',
                user_id,
                favorite_data.property_id,
                favorite_data.notes,
                datetime.utcnow()
            )

            logger.info(f"✅ Added to favorites: user={user_id}, property={favorite_data.property_id}")

            return {
                "id": favorite_id,
                "message": "Added to favorites",
                "already_exists": False
            }

        except Exception as e:
            logger.error(f"❌ Failed to add favorite: {e}")
            raise HTTPException(status_code=500, detail="Failed to add to favorites")


async def remove_favorite(
    property_id: str,
    user_id: str,
    db_pool: asyncpg.Pool
):
    """Remove property from user's favorites"""
    async with db_pool.acquire() as conn:
        try:
            result = await conn.execute(
                'DELETE FROM favorites WHERE user_id = $1 AND property_id = $2',
                user_id, property_id
            )

            # Check if anything was deleted
            if result == 'DELETE 0':
                raise HTTPException(status_code=404, detail="Favorite not found")

            logger.info(f"✅ Removed from favorites: user={user_id}, property={property_id}")

            return {"message": "Removed from favorites"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to remove favorite: {e}")
            raise HTTPException(status_code=500, detail="Failed to remove from favorites")


async def get_favorites(
    user_id: str,
    db_pool: asyncpg.Pool,
    opensearch_client,
    properties_index: str,
    page: int = 1,
    page_size: int = 20
):
    """
    Get user's favorite properties with property details.

    Fetches from PostgreSQL, then enriches with property data from OpenSearch.
    """
    async with db_pool.acquire() as conn:
        try:
            # Calculate pagination
            offset = (page - 1) * page_size

            # Get favorites from PostgreSQL
            favorites = await conn.fetch(
                '''
                SELECT id, user_id, property_id, notes, created_at
                FROM favorites
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                ''',
                user_id, page_size, offset
            )

            # Get total count
            total = await conn.fetchval(
                'SELECT COUNT(*) FROM favorites WHERE user_id = $1',
                user_id
            )

            # Enrich with property details from OpenSearch
            favorites_with_properties = []

            for fav in favorites:
                # Fetch property from OpenSearch
                try:
                    property_doc = await opensearch_client.get(
                        index=properties_index,
                        id=fav['property_id']
                    )
                    property_data = property_doc['_source']
                except:
                    # Property might have been deleted
                    property_data = None

                favorites_with_properties.append(
                    FavoriteWithProperty(
                        id=fav['id'],
                        user_id=fav['user_id'],
                        property_id=fav['property_id'],
                        notes=fav['notes'],
                        created_at=fav['created_at'],
                        property=property_data
                    )
                )

            logger.info(f"✅ Retrieved {len(favorites)} favorites for user={user_id}")

            return FavoriteListResponse(
                favorites=favorites_with_properties,
                total=total,
                page=page,
                page_size=page_size
            )

        except Exception as e:
            logger.error(f"❌ Failed to get favorites: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve favorites")


async def update_favorite_notes(
    property_id: str,
    update_data: FavoriteUpdate,
    user_id: str,
    db_pool: asyncpg.Pool
):
    """Update notes on a favorite property"""
    async with db_pool.acquire() as conn:
        try:
            result = await conn.execute(
                '''
                UPDATE favorites
                SET notes = $1
                WHERE user_id = $2 AND property_id = $3
                ''',
                update_data.notes,
                user_id,
                property_id
            )

            if result == 'UPDATE 0':
                raise HTTPException(status_code=404, detail="Favorite not found")

            logger.info(f"✅ Updated favorite notes: user={user_id}, property={property_id}")

            return {"message": "Notes updated"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to update notes: {e}")
            raise HTTPException(status_code=500, detail="Failed to update notes")


async def is_favorited(
    property_id: str,
    user_id: str,
    db_pool: asyncpg.Pool
) -> bool:
    """Check if property is in user's favorites"""
    async with db_pool.acquire() as conn:
        try:
            result = await conn.fetchval(
                'SELECT EXISTS(SELECT 1 FROM favorites WHERE user_id = $1 AND property_id = $2)',
                user_id, property_id
            )
            return result
        except:
            return False


async def get_favorites_count(
    user_id: str,
    db_pool: asyncpg.Pool
) -> int:
    """Get total number of favorites for user"""
    async with db_pool.acquire() as conn:
        try:
            count = await conn.fetchval(
                'SELECT COUNT(*) FROM favorites WHERE user_id = $1',
                user_id
            )
            return count or 0
        except:
            return 0


async def track_favorite_action(
    user_id: str,
    property_id: str,
    action: str,  # 'favorite' or 'unfavorite'
    db_pool: asyncpg.Pool
):
    """
    Track favorite/unfavorite action in user_actions table for analytics.
    """
    async with db_pool.acquire() as conn:
        try:
            await conn.execute(
                '''
                INSERT INTO user_actions (user_id, action_type, property_id, created_at)
                VALUES ($1, $2, $3, $4)
                ''',
                user_id,
                action,
                property_id,
                datetime.utcnow()
            )
        except Exception as e:
            logger.warning(f"⚠️  Failed to track action: {e}")
            # Don't fail the main operation if tracking fails

"""
Saved Searches Module for DB Gateway

Handles user saved searches:
- Create saved search
- Get user's saved searches
- Update saved search
- Delete saved search
- Find new matches for saved searches
"""

from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException
import asyncpg

from shared.models.saved_searches import (
    SavedSearchCreate,
    SavedSearchUpdate,
    SavedSearch,
    SavedSearchListResponse
)
from shared.models.db_gateway import SearchFilters
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


async def create_saved_search(
    search_data: SavedSearchCreate,
    user_id: str,
    db_pool: asyncpg.Pool
):
    """
    Create new saved search for user.

    User will receive notifications when new properties match this search.
    """
    async with db_pool.acquire() as conn:
        try:
            # Convert filters to JSON
            import json
            filters_json = json.dumps(search_data.filters.dict() if search_data.filters else {})

            # Insert saved search
            search_id = await conn.fetchval(
                '''
                INSERT INTO saved_searches (
                    user_id, search_name, query, filters,
                    notify_new_listings, notify_price_drops,
                    created_at, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                ''',
                user_id,
                search_data.search_name,
                search_data.query,
                filters_json,
                search_data.notify_new_listings,
                search_data.notify_price_drops,
                datetime.utcnow(),
                datetime.utcnow()
            )

            logger.info(f"✅ Saved search created: id={search_id}, user={user_id}")

            return {
                "id": search_id,
                "message": "Search saved successfully"
            }

        except Exception as e:
            logger.error(f"❌ Failed to create saved search: {e}")
            raise HTTPException(status_code=500, detail="Failed to save search")


async def get_saved_searches(
    user_id: str,
    db_pool: asyncpg.Pool
):
    """Get all saved searches for user"""
    async with db_pool.acquire() as conn:
        try:
            searches = await conn.fetch(
                '''
                SELECT id, user_id, search_name, query, filters,
                       notify_new_listings, notify_price_drops,
                       created_at, updated_at, last_notified_at
                FROM saved_searches
                WHERE user_id = $1
                ORDER BY created_at DESC
                ''',
                user_id
            )

            # Convert to response model
            saved_searches = []
            for search in searches:
                import json
                filters_dict = json.loads(search['filters']) if search['filters'] else {}

                saved_searches.append(
                    SavedSearch(
                        id=search['id'],
                        user_id=search['user_id'],
                        search_name=search['search_name'],
                        query=search['query'],
                        filters=filters_dict,
                        notify_new_listings=search['notify_new_listings'],
                        notify_price_drops=search['notify_price_drops'],
                        created_at=search['created_at'],
                        updated_at=search['updated_at'],
                        last_notified_at=search['last_notified_at'],
                        new_matches_count=0  # TODO: Calculate from OpenSearch
                    )
                )

            logger.info(f"✅ Retrieved {len(saved_searches)} saved searches for user={user_id}")

            return SavedSearchListResponse(
                saved_searches=saved_searches,
                total=len(saved_searches)
            )

        except Exception as e:
            logger.error(f"❌ Failed to get saved searches: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve saved searches")


async def update_saved_search(
    search_id: int,
    update_data: SavedSearchUpdate,
    user_id: str,
    db_pool: asyncpg.Pool
):
    """Update saved search"""
    async with db_pool.acquire() as conn:
        try:
            # Build update query dynamically
            update_fields = []
            values = []
            param_count = 1

            if update_data.search_name is not None:
                update_fields.append(f"search_name = ${param_count}")
                values.append(update_data.search_name)
                param_count += 1

            if update_data.query is not None:
                update_fields.append(f"query = ${param_count}")
                values.append(update_data.query)
                param_count += 1

            if update_data.filters is not None:
                import json
                update_fields.append(f"filters = ${param_count}")
                values.append(json.dumps(update_data.filters.dict()))
                param_count += 1

            if update_data.notify_new_listings is not None:
                update_fields.append(f"notify_new_listings = ${param_count}")
                values.append(update_data.notify_new_listings)
                param_count += 1

            if update_data.notify_price_drops is not None:
                update_fields.append(f"notify_price_drops = ${param_count}")
                values.append(update_data.notify_price_drops)
                param_count += 1

            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update")

            # Add updated_at
            update_fields.append(f"updated_at = ${param_count}")
            values.append(datetime.utcnow())
            param_count += 1

            # Add WHERE clause parameters
            values.append(search_id)
            values.append(user_id)

            query = f'''
            UPDATE saved_searches
            SET {", ".join(update_fields)}
            WHERE id = ${param_count} AND user_id = ${param_count + 1}
            '''

            result = await conn.execute(query, *values)

            if result == 'UPDATE 0':
                raise HTTPException(status_code=404, detail="Saved search not found")

            logger.info(f"✅ Saved search updated: id={search_id}")

            return {"message": "Saved search updated"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to update saved search: {e}")
            raise HTTPException(status_code=500, detail="Failed to update saved search")


async def delete_saved_search(
    search_id: int,
    user_id: str,
    db_pool: asyncpg.Pool
):
    """Delete saved search"""
    async with db_pool.acquire() as conn:
        try:
            result = await conn.execute(
                'DELETE FROM saved_searches WHERE id = $1 AND user_id = $2',
                search_id, user_id
            )

            if result == 'DELETE 0':
                raise HTTPException(status_code=404, detail="Saved search not found")

            logger.info(f"✅ Saved search deleted: id={search_id}")

            return {"message": "Saved search deleted"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to delete saved search: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete saved search")


async def find_new_matches(
    search_id: int,
    user_id: str,
    db_pool: asyncpg.Pool,
    opensearch_client,
    properties_index: str
):
    """
    Find new properties matching a saved search.

    Used for notifications - finds properties added since last_notified_at.
    """
    async with db_pool.acquire() as conn:
        try:
            # Get saved search
            search = await conn.fetchrow(
                '''
                SELECT query, filters, last_notified_at
                FROM saved_searches
                WHERE id = $1 AND user_id = $2
                ''',
                search_id, user_id
            )

            if not search:
                raise HTTPException(status_code=404, detail="Saved search not found")

            # Parse filters
            import json
            filters_dict = json.loads(search['filters']) if search['filters'] else {}

            # Build OpenSearch query
            # TODO: Use actual search logic from main.py
            # For now, simple keyword search with date filter

            must_clauses = []

            # Text search
            if search['query']:
                must_clauses.append({
                    "multi_match": {
                        "query": search['query'],
                        "fields": ["title^3", "description", "location^2"]
                    }
                })

            # Date filter - only properties created since last notification
            if search['last_notified_at']:
                must_clauses.append({
                    "range": {
                        "created_at": {
                            "gt": search['last_notified_at'].isoformat()
                        }
                    }
                })

            # Apply saved filters
            # TODO: Add district, property_type, price filters from filters_dict

            query = {"bool": {"must": must_clauses}} if must_clauses else {"match_all": {}}

            # Search OpenSearch
            response = await opensearch_client.search(
                index=properties_index,
                body={
                    "query": query,
                    "size": 50,  # Max 50 new matches
                    "sort": [{"created_at": {"order": "desc"}}]
                }
            )

            new_matches = []
            for hit in response['hits']['hits']:
                new_matches.append(hit['_source'])

            # Update last_notified_at
            await conn.execute(
                'UPDATE saved_searches SET last_notified_at = $1 WHERE id = $2',
                datetime.utcnow(), search_id
            )

            logger.info(f"✅ Found {len(new_matches)} new matches for search={search_id}")

            return {
                "search_id": search_id,
                "new_matches_count": len(new_matches),
                "new_matches": new_matches
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to find new matches: {e}")
            raise HTTPException(status_code=500, detail="Failed to find new matches")

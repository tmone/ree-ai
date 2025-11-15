"""
Admin API Routes for Master Data Management
Endpoints for reviewing and approving pending master data items
"""
from typing import List, Optional
from fastapi import HTTPException, Query
import asyncpg
from shared.utils.logger import setup_logger, LogEmoji
from shared.config import settings
from shared.models.attribute_extraction import (
    PendingMasterDataApproval,
    PendingMasterDataListResponse,
    NewAttribute
)


class AdminRoutes:
    """
    Admin routes for master data management
    """

    def __init__(self):
        self.logger = setup_logger("admin_routes")
        self.db_pool: Optional[asyncpg.Pool] = None

    async def initialize(self):
        """Initialize database connection"""
        try:
            self.db_pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                min_size=2,
                max_size=10
            )
            self.logger.info(f"{LogEmoji.SUCCESS} Admin routes connected to PostgreSQL")
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to connect to PostgreSQL: {e}")
            raise

    async def close(self):
        """Close database connection"""
        if self.db_pool:
            await self.db_pool.close()

    async def get_pending_items(
        self,
        status: str = 'pending',
        limit: int = 50,
        offset: int = 0
    ) -> PendingMasterDataListResponse:
        """
        Get list of pending master data items for review

        Args:
            status: Filter by status ('pending', 'approved', 'rejected')
            limit: Max items to return
            offset: Pagination offset

        Returns:
            List of pending items with metadata
        """
        if not self.db_pool:
            await self.initialize()

        try:
            async with self.db_pool.acquire() as conn:
                # Get total count
                count_query = """
                    SELECT COUNT(*) as total
                    FROM pending_master_data
                    WHERE status = $1
                """
                total_row = await conn.fetchrow(count_query, status)
                total_count = total_row['total']

                # Get items
                query = """
                    SELECT
                        id,
                        property_name,
                        value,
                        value_original,
                        suggested_table,
                        suggested_category,
                        suggested_translations,
                        extraction_context,
                        frequency,
                        status,
                        created_at
                    FROM pending_master_data
                    WHERE status = $1
                    ORDER BY frequency DESC, created_at DESC
                    LIMIT $2 OFFSET $3
                """

                rows = await conn.fetch(query, status, limit, offset)

                items = []
                for row in rows:
                    item = NewAttribute(
                        property_name=row['property_name'],
                        table=None,
                        id=None,
                        value=row['value'],
                        value_original=row['value_original'],
                        suggested_table=row['suggested_table'],
                        suggested_category=row['suggested_category'],
                        suggested_translations=row['suggested_translations'] or {},
                        extraction_context=row['extraction_context'],
                        requires_admin_review=True,
                        frequency=row['frequency']
                    )
                    items.append(item)

                # Get high-frequency items (frequency >= 3)
                high_freq_query = """
                    SELECT
                        id,
                        property_name,
                        value,
                        value_original,
                        suggested_table,
                        suggested_category,
                        suggested_translations,
                        extraction_context,
                        frequency
                    FROM pending_master_data
                    WHERE status = 'pending' AND frequency >= 3
                    ORDER BY frequency DESC
                    LIMIT 10
                """

                high_freq_rows = await conn.fetch(high_freq_query)
                high_freq_items = []
                for row in high_freq_rows:
                    item = NewAttribute(
                        property_name=row['property_name'],
                        table=None,
                        id=None,
                        value=row['value'],
                        value_original=row['value_original'],
                        suggested_table=row['suggested_table'],
                        suggested_category=row['suggested_category'],
                        suggested_translations=row['suggested_translations'] or {},
                        extraction_context=row['extraction_context'],
                        requires_admin_review=True,
                        frequency=row['frequency']
                    )
                    high_freq_items.append(item)

                return PendingMasterDataListResponse(
                    items=items,
                    total_count=total_count,
                    high_frequency_items=high_freq_items
                )

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to get pending items: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def approve_pending_item(
        self,
        pending_id: int,
        translations: dict,
        admin_user_id: str,
        admin_notes: Optional[str] = None
    ) -> dict:
        """
        Approve a pending item and add to master data

        Args:
            pending_id: ID in pending_master_data table
            translations: Dict of {lang_code: translated_text}
            admin_user_id: Admin who approved
            admin_notes: Optional notes

        Returns:
            Success response with new master data ID
        """
        if not self.db_pool:
            await self.initialize()

        try:
            async with self.db_pool.acquire() as conn:
                # Start transaction
                async with conn.transaction():
                    # Get pending item
                    pending_item = await conn.fetchrow(
                        """
                        SELECT * FROM pending_master_data WHERE id = $1 AND status = 'pending'
                        """,
                        pending_id
                    )

                    if not pending_item:
                        raise HTTPException(status_code=404, detail="Pending item not found")

                    # Insert into master data table
                    table_name = pending_item['suggested_table']
                    if not table_name:
                        raise HTTPException(status_code=400, detail="No suggested table")

                    # Insert into master table
                    insert_query = f"""
                        INSERT INTO {table_name} (name, code, category)
                        VALUES ($1, $2, $3)
                        RETURNING id
                    """

                    code = pending_item['value'].lower().replace(' ', '_')
                    category = pending_item['suggested_category'] or 'general'

                    new_id = await conn.fetchval(
                        insert_query,
                        pending_item['value'],  # English name
                        code,
                        category
                    )

                    # Insert translations
                    translation_table = f"{table_name}_translations"
                    fk_field = f"{table_name.rstrip('s')}_id"  # Remove trailing 's'

                    for lang_code, translated_text in translations.items():
                        await conn.execute(
                            f"""
                            INSERT INTO {translation_table} ({fk_field}, lang_code, translated_text)
                            VALUES ($1, $2, $3)
                            ON CONFLICT ({fk_field}, lang_code) DO UPDATE
                            SET translated_text = EXCLUDED.translated_text
                            """,
                            new_id,
                            lang_code,
                            translated_text
                        )

                    # Update pending_master_data status
                    await conn.execute(
                        """
                        UPDATE pending_master_data
                        SET status = 'approved',
                            reviewed_by = $1,
                            reviewed_at = NOW(),
                            updated_at = NOW()
                        WHERE id = $2
                        """,
                        admin_user_id,
                        pending_id
                    )

                    self.logger.info(
                        f"{LogEmoji.SUCCESS} Approved item {pending_id} → "
                        f"{table_name} ID {new_id}"
                    )

                    return {
                        "success": True,
                        "master_data_id": new_id,
                        "table": table_name,
                        "message": f"Successfully added to {table_name}"
                    }

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to approve item: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def reject_pending_item(
        self,
        pending_id: int,
        admin_user_id: str,
        admin_notes: Optional[str] = None
    ) -> dict:
        """
        Reject a pending item

        Args:
            pending_id: ID in pending_master_data table
            admin_user_id: Admin who rejected
            admin_notes: Reason for rejection

        Returns:
            Success response
        """
        if not self.db_pool:
            await self.initialize()

        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.execute(
                    """
                    UPDATE pending_master_data
                    SET status = 'rejected',
                        reviewed_by = $1,
                        reviewed_at = NOW(),
                        updated_at = NOW()
                    WHERE id = $2 AND status = 'pending'
                    """,
                    admin_user_id,
                    pending_id
                )

                if result == "UPDATE 0":
                    raise HTTPException(status_code=404, detail="Pending item not found")

                self.logger.info(f"{LogEmoji.INFO} Rejected item {pending_id}")

                return {
                    "success": True,
                    "message": "Item rejected successfully"
                }

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to reject item: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def store_new_attribute(
        self,
        new_attr: NewAttribute
    ) -> int:
        """
        Store a new attribute to pending_master_data for admin review

        Args:
            new_attr: NewAttribute from extraction

        Returns:
            ID of inserted row
        """
        if not self.db_pool:
            await self.initialize()

        try:
            async with self.db_pool.acquire() as conn:
                # Check if already exists
                existing = await conn.fetchrow(
                    """
                    SELECT id, frequency
                    FROM pending_master_data
                    WHERE value = $1 AND property_name = $2 AND status = 'pending'
                    """,
                    new_attr.value,
                    new_attr.property_name
                )

                if existing:
                    # Increment frequency
                    await conn.execute(
                        """
                        UPDATE pending_master_data
                        SET frequency = frequency + 1,
                            updated_at = NOW()
                        WHERE id = $1
                        """,
                        existing['id']
                    )
                    return existing['id']
                else:
                    # Insert new
                    new_id = await conn.fetchval(
                        """
                        INSERT INTO pending_master_data (
                            property_name,
                            value,
                            value_original,
                            suggested_table,
                            suggested_category,
                            suggested_translations,
                            extraction_context,
                            frequency,
                            status
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'pending')
                        RETURNING id
                        """,
                        new_attr.property_name,
                        new_attr.value,
                        new_attr.value_original,
                        new_attr.suggested_table,
                        new_attr.suggested_category,
                        new_attr.suggested_translations,
                        new_attr.extraction_context,
                        new_attr.frequency
                    )

                    return new_id

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to store new attribute: {e}")
            return -1

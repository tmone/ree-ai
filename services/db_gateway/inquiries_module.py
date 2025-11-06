"""
Inquiries Module for DB Gateway

Handles buyer-seller communication:
- Send inquiry (buyer → seller)
- Get sent inquiries (buyer)
- Get received inquiries (seller)
- Respond to inquiry (seller)
- Update inquiry status
- Get inquiry statistics
"""

from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException
import asyncpg
import uuid

from shared.models.inquiries import (
    InquiryCreate,
    InquiryResponse,
    InquiryStatusUpdate,
    Inquiry,
    InquiryWithDetails,
    InquiryListResponse,
    InquiryStats,
    InquiryStatus
)
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


async def send_inquiry(
    inquiry_data: InquiryCreate,
    sender_id: str,
    db_pool: asyncpg.Pool,
    opensearch_client,
    properties_index: str
):
    """
    Send inquiry from buyer to seller.

    Finds property owner and creates inquiry record.
    """
    # Get property to find owner
    try:
        property_doc = await opensearch_client.get(
            index=properties_index,
            id=inquiry_data.property_id
        )
        receiver_id = property_doc['_source'].get('owner_id')

        if not receiver_id:
            raise HTTPException(status_code=400, detail="Property has no owner")

        # Don't allow sending inquiry to self
        if receiver_id == sender_id:
            raise HTTPException(status_code=400, detail="Cannot send inquiry to yourself")

    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=404, detail="Property not found")

    async with db_pool.acquire() as conn:
        try:
            # Create inquiry
            inquiry_id = str(uuid.uuid4())

            await conn.execute(
                '''
                INSERT INTO inquiries (
                    id, property_id, sender_id, receiver_id,
                    message, contact_phone, contact_email,
                    status, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ''',
                inquiry_id,
                inquiry_data.property_id,
                sender_id,
                receiver_id,
                inquiry_data.message,
                inquiry_data.contact_phone,
                inquiry_data.contact_email,
                InquiryStatus.PENDING.value,
                datetime.utcnow()
            )

            # Track action in analytics
            await conn.execute(
                '''
                INSERT INTO user_actions (user_id, action_type, property_id, created_at)
                VALUES ($1, $2, $3, $4)
                ''',
                sender_id,
                'contact',
                inquiry_data.property_id,
                datetime.utcnow()
            )

            # Increment inquiries count on property
            try:
                current_count = property_doc['_source'].get('inquiries_count', 0)
                await opensearch_client.update(
                    index=properties_index,
                    id=inquiry_data.property_id,
                    body={"doc": {"inquiries_count": current_count + 1}}
                )
            except:
                pass  # Don't fail if count update fails

            logger.info(f"✅ Inquiry sent: id={inquiry_id}, from={sender_id}, to={receiver_id}")

            return {
                "id": inquiry_id,
                "message": "Inquiry sent successfully"
            }

        except Exception as e:
            logger.error(f"❌ Failed to send inquiry: {e}")
            raise HTTPException(status_code=500, detail="Failed to send inquiry")


async def get_sent_inquiries(
    sender_id: str,
    db_pool: asyncpg.Pool,
    opensearch_client,
    properties_index: str,
    page: int = 1,
    page_size: int = 20
):
    """Get inquiries sent by buyer"""
    async with db_pool.acquire() as conn:
        try:
            offset = (page - 1) * page_size

            inquiries = await conn.fetch(
                '''
                SELECT id, property_id, sender_id, receiver_id,
                       message, contact_phone, contact_email, response,
                       status, created_at, responded_at
                FROM inquiries
                WHERE sender_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                ''',
                sender_id, page_size, offset
            )

            total = await conn.fetchval(
                'SELECT COUNT(*) FROM inquiries WHERE sender_id = $1',
                sender_id
            )

            # Enrich with property and user details
            inquiries_with_details = await _enrich_inquiries(
                inquiries, conn, opensearch_client, properties_index
            )

            return InquiryListResponse(
                inquiries=inquiries_with_details,
                total=total,
                page=page,
                page_size=page_size
            )

        except Exception as e:
            logger.error(f"❌ Failed to get sent inquiries: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve inquiries")


async def get_received_inquiries(
    receiver_id: str,
    db_pool: asyncpg.Pool,
    opensearch_client,
    properties_index: str,
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Get inquiries received by seller"""
    async with db_pool.acquire() as conn:
        try:
            offset = (page - 1) * page_size

            # Build query
            if status_filter:
                query = '''
                SELECT id, property_id, sender_id, receiver_id,
                       message, contact_phone, contact_email, response,
                       status, created_at, responded_at
                FROM inquiries
                WHERE receiver_id = $1 AND status = $2
                ORDER BY created_at DESC
                LIMIT $3 OFFSET $4
                '''
                inquiries = await conn.fetch(query, receiver_id, status_filter, page_size, offset)
                total = await conn.fetchval(
                    'SELECT COUNT(*) FROM inquiries WHERE receiver_id = $1 AND status = $2',
                    receiver_id, status_filter
                )
            else:
                query = '''
                SELECT id, property_id, sender_id, receiver_id,
                       message, contact_phone, contact_email, response,
                       status, created_at, responded_at
                FROM inquiries
                WHERE receiver_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                '''
                inquiries = await conn.fetch(query, receiver_id, page_size, offset)
                total = await conn.fetchval(
                    'SELECT COUNT(*) FROM inquiries WHERE receiver_id = $1',
                    receiver_id
                )

            # Enrich with details
            inquiries_with_details = await _enrich_inquiries(
                inquiries, conn, opensearch_client, properties_index
            )

            return InquiryListResponse(
                inquiries=inquiries_with_details,
                total=total,
                page=page,
                page_size=page_size
            )

        except Exception as e:
            logger.error(f"❌ Failed to get received inquiries: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve inquiries")


async def respond_to_inquiry(
    inquiry_id: str,
    response_data: InquiryResponse,
    receiver_id: str,
    db_pool: asyncpg.Pool
):
    """Seller responds to inquiry"""
    async with db_pool.acquire() as conn:
        try:
            result = await conn.execute(
                '''
                UPDATE inquiries
                SET response = $1, status = $2, responded_at = $3
                WHERE id = $4 AND receiver_id = $5
                ''',
                response_data.message,
                InquiryStatus.RESPONDED.value,
                datetime.utcnow(),
                inquiry_id,
                receiver_id
            )

            if result == 'UPDATE 0':
                raise HTTPException(status_code=404, detail="Inquiry not found or not authorized")

            logger.info(f"✅ Responded to inquiry: id={inquiry_id}")

            return {"message": "Response sent successfully"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to respond: {e}")
            raise HTTPException(status_code=500, detail="Failed to send response")


async def update_inquiry_status(
    inquiry_id: str,
    status_update: InquiryStatusUpdate,
    user_id: str,
    db_pool: asyncpg.Pool
):
    """Update inquiry status"""
    async with db_pool.acquire() as conn:
        try:
            # Verify user is sender or receiver
            inquiry = await conn.fetchrow(
                'SELECT sender_id, receiver_id FROM inquiries WHERE id = $1',
                inquiry_id
            )

            if not inquiry:
                raise HTTPException(status_code=404, detail="Inquiry not found")

            if user_id not in [inquiry['sender_id'], inquiry['receiver_id']]:
                raise HTTPException(status_code=403, detail="Not authorized")

            result = await conn.execute(
                'UPDATE inquiries SET status = $1 WHERE id = $2',
                status_update.status.value,
                inquiry_id
            )

            logger.info(f"✅ Inquiry status updated: id={inquiry_id} -> {status_update.status.value}")

            return {"message": "Status updated"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Failed to update status: {e}")
            raise HTTPException(status_code=500, detail="Failed to update status")


async def get_inquiry_stats(
    receiver_id: str,
    db_pool: asyncpg.Pool
):
    """Get inquiry statistics for seller"""
    async with db_pool.acquire() as conn:
        try:
            # Get counts by status
            stats = await conn.fetchrow(
                '''
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending,
                    COUNT(*) FILTER (WHERE status = 'responded') as responded,
                    AVG(EXTRACT(EPOCH FROM (responded_at - created_at))) as avg_response_time_seconds
                FROM inquiries
                WHERE receiver_id = $1
                ''',
                receiver_id
            )

            total = stats['total'] or 0
            pending = stats['pending'] or 0
            responded = stats['responded'] or 0

            response_rate = responded / total if total > 0 else 0.0

            # Format avg response time
            avg_seconds = stats['avg_response_time_seconds'] or 0
            if avg_seconds > 3600:
                avg_time_str = f"{int(avg_seconds / 3600)}h {int((avg_seconds % 3600) / 60)}m"
            elif avg_seconds > 60:
                avg_time_str = f"{int(avg_seconds / 60)}m"
            else:
                avg_time_str = f"{int(avg_seconds)}s"

            return InquiryStats(
                total_inquiries=total,
                pending_inquiries=pending,
                responded_inquiries=responded,
                response_rate=response_rate,
                avg_response_time=avg_time_str
            )

        except Exception as e:
            logger.error(f"❌ Failed to get inquiry stats: {e}")
            raise HTTPException(status_code=500, detail="Failed to get statistics")


async def _enrich_inquiries(
    inquiries: List,
    conn: asyncpg.Connection,
    opensearch_client,
    properties_index: str
) -> List[InquiryWithDetails]:
    """
    Enrich inquiries with property and user details.

    Internal helper function.
    """
    enriched = []

    for inquiry in inquiries:
        # Fetch property details
        try:
            property_doc = await opensearch_client.get(
                index=properties_index,
                id=inquiry['property_id']
            )
            property_data = property_doc['_source']
        except:
            property_data = None

        # Fetch sender details
        try:
            sender = await conn.fetchrow(
                'SELECT id, email, full_name, user_type FROM "user" WHERE id = $1',
                inquiry['sender_id']
            )
            sender_data = dict(sender) if sender else None
        except:
            sender_data = None

        # Fetch receiver details
        try:
            receiver = await conn.fetchrow(
                'SELECT id, email, full_name, user_type, company_name FROM "user" WHERE id = $1',
                inquiry['receiver_id']
            )
            receiver_data = dict(receiver) if receiver else None
        except:
            receiver_data = None

        enriched.append(
            InquiryWithDetails(
                id=inquiry['id'],
                property_id=inquiry['property_id'],
                sender_id=inquiry['sender_id'],
                receiver_id=inquiry['receiver_id'],
                message=inquiry['message'],
                contact_phone=inquiry['contact_phone'],
                contact_email=inquiry['contact_email'],
                response=inquiry['response'],
                status=InquiryStatus(inquiry['status']),
                created_at=inquiry['created_at'],
                responded_at=inquiry['responded_at'],
                property=property_data,
                sender=sender_data,
                receiver=receiver_data
            )
        )

    return enriched

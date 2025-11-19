"""
Property Management Module for DB Gateway

Handles seller-side property CRUD operations:
- Create property (draft or publish)
- Update property
- Delete property
- Publish/pause/reactivate listings
- Upload images
- Get seller's properties
- Property analytics
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Header
import uuid

from shared.models.properties import (
    PropertyCreate,
    PropertyUpdate,
    PropertyStatus,
    PropertyStatusUpdate,
    PropertyListResponse,
    PropertyAnalytics,
    ImageUploadRequest,
    PropertyDocument
)
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)


async def create_property(
    property_data: PropertyCreate,
    authorization: str,
    opensearch_client,
    properties_index: str
):
    """
    Create new property (draft or published).

    Seller must be authenticated. Property saved to OpenSearch.
    """
    # Extract user_id from auth token
    # TODO: Verify token with User Management Service
    user_id = _extract_user_id_from_token(authorization)

    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Generate property ID
    property_id = str(uuid.uuid4())

    # Determine status
    status = PropertyStatus.ACTIVE if property_data.publish_immediately else PropertyStatus.DRAFT

    # Build property document
    now = datetime.utcnow()
    property_doc = {
        "property_id": property_id,
        "owner_id": user_id,

        # Basic info
        "title": property_data.title,
        "description": property_data.description,
        "property_type": property_data.property_type,
        "listing_type": property_data.listing_type.value,

        # Location
        "district": property_data.district,
        "ward": property_data.ward,
        "street": property_data.street,
        "city": property_data.city,

        # Price & attributes
        "price": property_data.price,
        "bedrooms": property_data.bedrooms,
        "bathrooms": property_data.bathrooms,
        "area": property_data.area,
        "floor": property_data.floor,

        # Dimensions (for townhouse, land)
        "width": property_data.width,
        "depth": property_data.depth,
        "land_area": property_data.land_area,

        # Geolocation (for map)
        "latitude": property_data.latitude,
        "longitude": property_data.longitude,

        # Flexible attributes
        "attributes": property_data.attributes or {},

        # Images (empty initially)
        "images": [],
        "videos": [],

        # Status
        "status": status.value,
        "verification_status": "unverified",

        # Analytics
        "views_count": 0,
        "favorites_count": 0,
        "inquiries_count": 0,

        # Contact info
        "contact_phone": property_data.contact_phone,
        "contact_email": property_data.contact_email,
        "show_contact_info": property_data.show_contact_info,

        # Timestamps
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "published_at": now.isoformat() if status == PropertyStatus.ACTIVE else None,
        "expires_at": (now + timedelta(days=90)).isoformat(),  # Auto-expire after 90 days

        # Semantic chunking (CTO Architecture Priority 1)
        "chunks": property_data.chunks or [],
        "chunk_count": property_data.chunk_count or 0,
    }

    # Index in OpenSearch
    try:
        response = await opensearch_client.index(
            index=properties_index,
            id=property_id,
            body=property_doc,
            refresh=True
        )

        logger.info(f"✅ Property created: {property_id} (status: {status.value})")

        return {
            "property_id": property_id,
            "status": status.value,
            "message": "Property created successfully" if status == PropertyStatus.DRAFT else "Property published successfully"
        }

    except Exception as e:
        logger.error(f"❌ Failed to create property: {e}")
        raise HTTPException(status_code=500, detail="Failed to create property")


async def get_my_properties(
    authorization: str,
    opensearch_client,
    properties_index: str,
    status_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    Get seller's own properties.

    Supports filtering by status (draft, active, sold, etc.)
    """
    user_id = _extract_user_id_from_token(authorization)

    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Build query
    must_clauses = [{"term": {"owner_id": user_id}}]

    if status_filter:
        must_clauses.append({"term": {"status": status_filter}})

    query = {
        "bool": {
            "must": must_clauses
        }
    }

    # Calculate pagination
    from_index = (page - 1) * page_size

    try:
        response = await opensearch_client.search(
            index=properties_index,
            body={
                "query": query,
                "from": from_index,
                "size": page_size,
                "sort": [{"created_at": {"order": "desc"}}]
            }
        )

        properties = []
        for hit in response['hits']['hits']:
            properties.append(PropertyDocument(**hit['_source']))

        total = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']

        return PropertyListResponse(
            properties=properties,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"❌ Failed to get properties: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve properties")


async def update_property(
    property_id: str,
    update_data: PropertyUpdate,
    authorization: str,
    opensearch_client,
    properties_index: str
):
    """
    Update property details.

    Only owner can update. Cannot update if status is sold/rented.
    """
    user_id = _extract_user_id_from_token(authorization)

    # Get existing property
    try:
        property_doc = await opensearch_client.get(
            index=properties_index,
            id=property_id
        )
    except:
        raise HTTPException(status_code=404, detail="Property not found")

    # Verify ownership
    if property_doc['_source']['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this property")

    # Check status
    current_status = property_doc['_source']['status']
    if current_status in ['sold', 'rented']:
        raise HTTPException(status_code=400, detail="Cannot update sold/rented property")

    # Build update document
    update_doc = {"updated_at": datetime.utcnow().isoformat()}

    if update_data.title: update_doc['title'] = update_data.title
    if update_data.description: update_doc['description'] = update_data.description
    if update_data.price: update_doc['price'] = update_data.price
    if update_data.bedrooms is not None: update_doc['bedrooms'] = update_data.bedrooms
    if update_data.bathrooms is not None: update_doc['bathrooms'] = update_data.bathrooms
    if update_data.area: update_doc['area'] = update_data.area
    if update_data.floor is not None: update_doc['floor'] = update_data.floor
    # Dimensions
    if update_data.width is not None: update_doc['width'] = update_data.width
    if update_data.depth is not None: update_doc['depth'] = update_data.depth
    if update_data.land_area is not None: update_doc['land_area'] = update_data.land_area
    # Geolocation
    if update_data.latitude is not None: update_doc['latitude'] = update_data.latitude
    if update_data.longitude is not None: update_doc['longitude'] = update_data.longitude
    if update_data.attributes: update_doc['attributes'] = update_data.attributes
    if update_data.contact_phone: update_doc['contact_phone'] = update_data.contact_phone
    if update_data.contact_email: update_doc['contact_email'] = update_data.contact_email
    if update_data.show_contact_info is not None: update_doc['show_contact_info'] = update_data.show_contact_info

    # Update in OpenSearch
    try:
        await opensearch_client.update(
            index=properties_index,
            id=property_id,
            body={"doc": update_doc},
            refresh=True
        )

        logger.info(f"✅ Property updated: {property_id}")

        return {"message": "Property updated successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to update property: {e}")
        raise HTTPException(status_code=500, detail="Failed to update property")


async def update_property_status(
    property_id: str,
    status_update: PropertyStatusUpdate,
    authorization: str,
    opensearch_client,
    properties_index: str
):
    """
    Update property status (publish, pause, mark as sold, etc.)
    """
    user_id = _extract_user_id_from_token(authorization)

    # Get existing property
    try:
        property_doc = await opensearch_client.get(
            index=properties_index,
            id=property_id
        )
    except:
        raise HTTPException(status_code=404, detail="Property not found")

    # Verify ownership
    if property_doc['_source']['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this property")

    # Build update
    update_doc = {
        "status": status_update.status.value,
        "updated_at": datetime.utcnow().isoformat()
    }

    # Set published_at if publishing for first time
    if status_update.status == PropertyStatus.ACTIVE and not property_doc['_source'].get('published_at'):
        update_doc['published_at'] = datetime.utcnow().isoformat()

    # Update
    try:
        await opensearch_client.update(
            index=properties_index,
            id=property_id,
            body={"doc": update_doc},
            refresh=True
        )

        logger.info(f"✅ Property status updated: {property_id} -> {status_update.status.value}")

        return {"message": f"Property status updated to {status_update.status.value}"}

    except Exception as e:
        logger.error(f"❌ Failed to update status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update status")


async def delete_property(
    property_id: str,
    authorization: str,
    opensearch_client,
    properties_index: str
):
    """Delete property (only drafts and owner's properties)"""
    user_id = _extract_user_id_from_token(authorization)

    # Get existing property
    try:
        property_doc = await opensearch_client.get(
            index=properties_index,
            id=property_id
        )
    except:
        raise HTTPException(status_code=404, detail="Property not found")

    # Verify ownership
    if property_doc['_source']['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this property")

    # Delete from OpenSearch
    try:
        await opensearch_client.delete(
            index=properties_index,
            id=property_id,
            refresh=True
        )

        logger.info(f"✅ Property deleted: {property_id}")

        return {"message": "Property deleted successfully"}

    except Exception as e:
        logger.error(f"❌ Failed to delete property: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete property")


async def upload_images(
    upload_request: ImageUploadRequest,
    authorization: str,
    opensearch_client,
    properties_index: str
):
    """
    Upload images to property.

    Images are URLs (already uploaded to CDN/S3).
    """
    user_id = _extract_user_id_from_token(authorization)

    # Get existing property
    try:
        property_doc = await opensearch_client.get(
            index=properties_index,
            id=upload_request.property_id
        )
    except:
        raise HTTPException(status_code=404, detail="Property not found")

    # Verify ownership
    if property_doc['_source']['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update images
    current_images = property_doc['_source'].get('images', [])
    new_images = current_images + upload_request.image_urls

    # Limit to 10 images
    if len(new_images) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images allowed")

    update_doc = {
        "images": new_images,
        "updated_at": datetime.utcnow().isoformat()
    }

    try:
        await opensearch_client.update(
            index=properties_index,
            id=upload_request.property_id,
            body={"doc": update_doc},
            refresh=True
        )

        logger.info(f"✅ Images uploaded: {upload_request.property_id}")

        return {
            "message": "Images uploaded successfully",
            "total_images": len(new_images)
        }

    except Exception as e:
        logger.error(f"❌ Failed to upload images: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload images")


async def upload_image_files(
    property_id: str,
    files: list,  # List of UploadFile
    authorization: str,
    opensearch_client,
    properties_index: str
):
    """
    Upload image files directly to Google Cloud Storage.

    Accepts multipart form data with multiple image files.
    Images are uploaded to GCS and URLs stored in property document.
    """
    from shared.utils.gcs_storage import get_gcs_client

    user_id = _extract_user_id_from_token(authorization)

    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Get existing property
    try:
        property_doc = await opensearch_client.get(
            index=properties_index,
            id=property_id
        )
    except:
        raise HTTPException(status_code=404, detail="Property not found")

    # Verify ownership
    if property_doc['_source']['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check current image count
    current_images = property_doc['_source'].get('images', [])
    if len(current_images) + len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum 10 images allowed. Current: {len(current_images)}, Uploading: {len(files)}"
        )

    # Get GCS client
    gcs_client = get_gcs_client()

    # Prepare files for upload
    upload_files = []
    for file in files:
        content = await file.read()
        upload_files.append((content, file.filename, file.content_type))

    # Upload to GCS
    uploaded_urls = await gcs_client.upload_images(property_id, upload_files)

    if not uploaded_urls:
        raise HTTPException(status_code=500, detail="Failed to upload images to storage")

    # Update property with new image URLs
    new_images = current_images + uploaded_urls

    update_doc = {
        "images": new_images,
        "updated_at": datetime.utcnow().isoformat()
    }

    try:
        await opensearch_client.update(
            index=properties_index,
            id=property_id,
            body={"doc": update_doc},
            refresh=True
        )

        logger.info(f"✅ Images uploaded to GCS for property {property_id}: {len(uploaded_urls)} files")

        return {
            "message": "Images uploaded successfully",
            "uploaded_count": len(uploaded_urls),
            "total_images": len(new_images),
            "image_urls": uploaded_urls
        }

    except Exception as e:
        logger.error(f"❌ Failed to update property with images: {e}")
        raise HTTPException(status_code=500, detail="Failed to update property with images")


async def update_property_coordinates(
    property_id: str,
    latitude: float,
    longitude: float,
    authorization: str,
    opensearch_client,
    properties_index: str
):
    """
    Update property coordinates from map selection.

    Called after user selects location on map.
    """
    user_id = _extract_user_id_from_token(authorization)

    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Get existing property
    try:
        property_doc = await opensearch_client.get(
            index=properties_index,
            id=property_id
        )
    except:
        raise HTTPException(status_code=404, detail="Property not found")

    # Verify ownership
    if property_doc['_source']['owner_id'] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate coordinates
    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Invalid coordinates")

    # Update coordinates
    update_doc = {
        "latitude": latitude,
        "longitude": longitude,
        "location_geo": {"lat": latitude, "lon": longitude},  # For geo queries
        "updated_at": datetime.utcnow().isoformat()
    }

    try:
        await opensearch_client.update(
            index=properties_index,
            id=property_id,
            body={"doc": update_doc},
            refresh=True
        )

        logger.info(f"✅ Coordinates updated for property {property_id}: ({latitude}, {longitude})")

        return {
            "message": "Coordinates updated successfully",
            "latitude": latitude,
            "longitude": longitude
        }

    except Exception as e:
        logger.error(f"❌ Failed to update coordinates: {e}")
        raise HTTPException(status_code=500, detail="Failed to update coordinates")


def _extract_user_id_from_token(authorization: Optional[str]) -> Optional[str]:
    """
    Extract user_id from JWT token.

    TODO: Verify token with User Management Service.
    For now, extracting from Bearer token.
    """
    if not authorization:
        return None

    try:
        import jwt
        from shared.config import settings

        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")  # user_id
    except:
        return None

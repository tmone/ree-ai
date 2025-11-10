# REE AI - User Areas API Documentation

**Version**: 1.0.0
**Base URLs**:
- User Management: `http://localhost:8085`
- DB Gateway: `http://localhost:8081`

**Authentication**: JWT Bearer Token (except `/register` and `/login`)

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Management API](#user-management-api)
3. [Property Management API](#property-management-api)
4. [Favorites API](#favorites-api)
5. [Saved Searches API](#saved-searches-api)
6. [Inquiries API](#inquiries-api)
7. [Search API](#search-api)
8. [Error Codes](#error-codes)
9. [Rate Limiting](#rate-limiting)

---

## Authentication

### Overview

All API endpoints (except `/register` and `/login`) require JWT authentication.

**How to authenticate**:
1. Register or login to get access token
2. Include token in `Authorization` header: `Bearer <token>`
3. Token expires after 7 days (configurable)

**Example**:
```bash
curl -X GET http://localhost:8081/favorites \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## User Management API

Base URL: `http://localhost:8085`

### POST /register

Register a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "user_type": "seller",              // "seller" | "buyer" | "both"
  "phone_number": "0901234567",       // Optional
  "company_name": "John Real Estate"  // Optional (for sellers)
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_type": "seller",
    "role": "user",
    "phone_number": "0901234567",
    "company_name": "John Real Estate",
    "verified": false,
    "created_at": "2025-11-10T10:30:00Z"
  }
}
```

**Errors**:
- `400 Bad Request`: Invalid input (email already exists, password too short)
- `422 Unprocessable Entity`: Validation error

**Validation Rules**:
- `email`: Valid email format, unique
- `password`: Minimum 8 characters
- `full_name`: Required, non-empty
- `user_type`: Must be "seller", "buyer", or "both"

**Example**:
```bash
curl -X POST http://localhost:8085/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "MyPassword123",
    "full_name": "Jane Seller",
    "user_type": "seller",
    "phone_number": "0909999999"
  }'
```

---

### POST /login

Login with email and password.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_type": "seller",
    "role": "user",
    "verified": false,
    "created_at": "2025-11-10T10:30:00Z"
  }
}
```

**Errors**:
- `401 Unauthorized`: Invalid email or password
- `404 Not Found`: User does not exist

**Example**:
```bash
curl -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "MyPassword123"
  }'
```

---

### GET /users/me

Get current user profile.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "user_type": "seller",
  "role": "user",
  "phone_number": "0901234567",
  "company_name": "John Real Estate",
  "license_number": null,
  "verified": false,
  "created_at": "2025-11-10T10:30:00Z",
  "updated_at": "2025-11-10T10:30:00Z"
}
```

**Errors**:
- `401 Unauthorized`: Invalid or expired token

---

### PUT /users/me

Update current user profile.

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "full_name": "John Updated",
  "phone_number": "0909999999",
  "company_name": "New Company Name"
}
```

**Response** (200 OK):
```json
{
  "message": "Profile updated successfully",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Updated",
    "phone_number": "0909999999",
    "company_name": "New Company Name",
    ...
  }
}
```

**Errors**:
- `401 Unauthorized`: Invalid token
- `400 Bad Request`: Invalid data

---

### POST /logout

Logout user (client-side token removal recommended).

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

## Property Management API

Base URL: `http://localhost:8081`

### POST /properties

Create a new property listing (Seller only).

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "title": "Modern 2BR Apartment in District 7",
  "description": "Beautiful apartment with city view, fully furnished, near schools and shopping centers. Modern design with high-quality finishes.",
  "property_type": "apartment",      // apartment | house | villa | land | commercial
  "listing_type": "sale",            // sale | rent
  "address": "123 Nguyen Van Linh",
  "district": "Quận 7",
  "city": "Hồ Chí Minh",
  "price": 5000000000,               // VND (numeric)
  "area": 80,                        // m² (numeric)
  "bedrooms": 2,
  "bathrooms": 2,
  "floors": 1,                       // Optional
  "publish_immediately": true        // Optional (default: false = save as draft)
}
```

**Response** (200 OK):
```json
{
  "property_id": "prop_abc123xyz",
  "owner_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Modern 2BR Apartment in District 7",
  "description": "Beautiful apartment with city view...",
  "property_type": "apartment",
  "listing_type": "sale",
  "address": "123 Nguyen Van Linh",
  "district": "Quận 7",
  "city": "Hồ Chí Minh",
  "price": 5000000000,
  "price_display": "5 tỷ",
  "area": 80,
  "area_display": "80 m²",
  "bedrooms": 2,
  "bathrooms": 2,
  "floors": 1,
  "status": "active",                // active | draft
  "verification_status": "unverified",
  "views_count": 0,
  "favorites_count": 0,
  "inquiries_count": 0,
  "images": [],
  "created_at": "2025-11-10T10:30:00Z",
  "updated_at": "2025-11-10T10:30:00Z",
  "published_at": "2025-11-10T10:30:00Z"
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated or not a seller
- `400 Bad Request`: Invalid data (missing required fields)
- `503 Service Unavailable`: OpenSearch not available

**Validation Rules**:
- `title`: Required, min 10 characters
- `description`: Required, min 50 characters
- `price`: Required, > 0
- `area`: Required, > 0
- `bedrooms`, `bathrooms`: Required, >= 0

**Example**:
```bash
TOKEN="your-jwt-token"

curl -X POST http://localhost:8081/properties \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Luxury Villa with Pool",
    "description": "Stunning 4-bedroom villa with private pool and garden. Located in quiet area with 24/7 security.",
    "property_type": "villa",
    "listing_type": "sale",
    "city": "Hồ Chí Minh",
    "district": "Quận 2",
    "price": 15000000000,
    "area": 300,
    "bedrooms": 4,
    "bathrooms": 5,
    "publish_immediately": true
  }'
```

---

### GET /properties/my-listings

Get seller's own property listings.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `status_filter` (optional): Filter by status (active, draft, sold, rented, paused)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Response** (200 OK):
```json
{
  "items": [
    {
      "property_id": "prop_abc123",
      "title": "Modern 2BR Apartment",
      "price": 5000000000,
      "status": "active",
      "views_count": 45,
      "favorites_count": 8,
      "inquiries_count": 3,
      "created_at": "2025-11-10T10:30:00Z",
      ...
    },
    ...
  ],
  "total": 15,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated

**Example**:
```bash
curl -X GET "http://localhost:8081/properties/my-listings?status_filter=active&page=1&page_size=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

### PUT /properties/{property_id}

Update property details (Owner only).

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "price": 5500000000,
  "bedrooms": 3
}
```

**Response** (200 OK):
```json
{
  "message": "Property updated successfully",
  "property": {
    "property_id": "prop_abc123",
    "title": "Updated Title",
    "price": 5500000000,
    "bedrooms": 3,
    "updated_at": "2025-11-10T11:00:00Z",
    ...
  }
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not the property owner
- `404 Not Found`: Property does not exist
- `400 Bad Request`: Cannot update sold/rented properties

---

### PUT /properties/{property_id}/status

Update property status (publish, pause, mark as sold, etc.).

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "status": "sold",               // draft | pending | active | sold | rented | paused
  "reason": "Property sold today" // Optional
}
```

**Response** (200 OK):
```json
{
  "message": "Property status updated to sold",
  "property": {
    "property_id": "prop_abc123",
    "status": "sold",
    "updated_at": "2025-11-10T11:00:00Z",
    ...
  }
}
```

**Status Transitions**:
- `draft` → `active`: Publish property
- `active` → `paused`: Temporarily hide property
- `active` → `sold`: Mark as sold
- `active` → `rented`: Mark as rented
- `paused` → `active`: Resume listing

**Errors**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not the property owner
- `400 Bad Request`: Invalid status transition

---

### DELETE /properties/{property_id}

Delete property (Owner only).

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "message": "Property deleted successfully"
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not the property owner
- `404 Not Found`: Property does not exist

**Note**: This is a hard delete. Consider implementing soft delete (marking as deleted) for audit purposes.

---

### POST /properties/{property_id}/images

Upload images to property.

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
  ]
}
```

**Response** (200 OK):
```json
{
  "message": "Images uploaded successfully",
  "property": {
    "property_id": "prop_abc123",
    "images": [
      "https://example.com/image1.jpg",
      "https://example.com/image2.jpg",
      "https://example.com/image3.jpg"
    ],
    "thumbnail": "https://example.com/image1.jpg",
    ...
  }
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not the property owner

**Note**: This endpoint accepts image URLs. For actual image upload, implement file upload endpoint with multipart/form-data.

---

## Favorites API

Base URL: `http://localhost:8081`

### POST /favorites

Add property to favorites (Buyer).

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "property_id": "prop_abc123",
  "notes": "Nice location near school, good for family"
}
```

**Response** (200 OK):
```json
{
  "message": "Added to favorites",
  "favorite_id": 42
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `400 Bad Request`: Property already in favorites
- `404 Not Found`: Property does not exist

---

### GET /favorites

Get user's favorite properties.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 42,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "property_id": "prop_abc123",
      "notes": "Nice location near school",
      "created_at": "2025-11-10T10:30:00Z",
      "property": {
        "property_id": "prop_abc123",
        "title": "Modern 2BR Apartment",
        "price": 5000000000,
        "district": "Quận 7",
        "city": "Hồ Chí Minh",
        "area": 80,
        "bedrooms": 2,
        "bathrooms": 2,
        "images": ["https://..."],
        ...
      }
    },
    ...
  ],
  "total": 8,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated

---

### DELETE /favorites/{property_id}

Remove property from favorites.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "message": "Removed from favorites"
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Favorite not found

---

### PUT /favorites/{property_id}

Update notes on a favorite property.

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "notes": "Updated notes about this property"
}
```

**Response** (200 OK):
```json
{
  "message": "Favorite updated successfully"
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Favorite not found

---

## Saved Searches API

Base URL: `http://localhost:8081`

### POST /saved-searches

Save search criteria for notifications.

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "name": "2BR in District 7 under 6B",
  "query": "apartment district 7",
  "filters": {
    "property_type": "apartment",
    "city": "Hồ Chí Minh",
    "district": "Quận 7",
    "min_price": 4000000000,
    "max_price": 6000000000,
    "min_bedrooms": 2
  },
  "notify_email": true,
  "notify_frequency": "daily"    // instant | daily | weekly
}
```

**Response** (200 OK):
```json
{
  "id": 123,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "2BR in District 7 under 6B",
  "query": "apartment district 7",
  "filters": { ... },
  "notify_email": true,
  "notify_frequency": "daily",
  "active": true,
  "created_at": "2025-11-10T10:30:00Z",
  "last_notified_at": null
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `400 Bad Request`: Invalid filters

---

### GET /saved-searches

Get user's saved searches.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": 123,
      "name": "2BR in District 7 under 6B",
      "query": "apartment district 7",
      "filters": { ... },
      "notify_email": true,
      "notify_frequency": "daily",
      "active": true,
      "created_at": "2025-11-10T10:30:00Z",
      "last_notified_at": "2025-11-11T08:00:00Z"
    },
    ...
  ],
  "total": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

### GET /saved-searches/{search_id}/new-matches

Find new properties matching saved search.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "new_matches": [
    {
      "property_id": "prop_new123",
      "title": "New Apartment Listing",
      "price": 5500000000,
      ...
    },
    ...
  ],
  "count": 3
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Saved search not found

**Note**: This endpoint updates `last_notified_at` timestamp.

---

### PUT /saved-searches/{search_id}

Update saved search.

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "name": "Updated Search Name",
  "notify_frequency": "weekly",
  "active": false
}
```

**Response** (200 OK):
```json
{
  "message": "Saved search updated successfully",
  "saved_search": { ... }
}
```

---

### DELETE /saved-searches/{search_id}

Delete saved search.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "message": "Saved search deleted successfully"
}
```

---

## Inquiries API

Base URL: `http://localhost:8081`

### POST /inquiries

Send inquiry to seller (Buyer).

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "property_id": "prop_abc123",
  "message": "I'm interested in this property. Is it still available? Can I schedule a viewing this weekend?",
  "contact_email": "buyer@example.com",
  "contact_phone": "0901234567",
  "preferred_contact_time": "evening"  // morning | afternoon | evening | anytime
}
```

**Response** (200 OK):
```json
{
  "message": "Inquiry sent successfully",
  "inquiry_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `404 Not Found`: Property does not exist
- `400 Bad Request`: Invalid message (too short)

**Side Effects**:
- Increments `inquiries_count` on property
- Tracks action in `user_actions` table
- Sends email notification to seller (if enabled)

---

### GET /inquiries/sent

Get inquiries sent by buyer.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Response** (200 OK):
```json
{
  "items": [
    {
      "inquiry_id": "550e8400-e29b-41d4-a716-446655440001",
      "property_id": "prop_abc123",
      "sender_id": "user123",
      "receiver_id": "seller456",
      "message": "I'm interested in this property...",
      "contact_email": "buyer@example.com",
      "contact_phone": "0901234567",
      "preferred_contact_time": "evening",
      "status": "responded",
      "response_message": "Thank you for your interest. The property is still available...",
      "responded_at": "2025-11-10T15:00:00Z",
      "created_at": "2025-11-10T10:30:00Z",
      "property": {
        "property_id": "prop_abc123",
        "title": "Modern 2BR Apartment",
        ...
      },
      "sender": {
        "user_id": "user123",
        "full_name": "John Buyer",
        ...
      },
      "receiver": {
        "user_id": "seller456",
        "full_name": "Jane Seller",
        ...
      }
    },
    ...
  ],
  "total": 12,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

### GET /inquiries/received

Get inquiries received by seller.

**Headers**:
```
Authorization: Bearer <token>
```

**Query Parameters**:
- `status_filter` (optional): Filter by status (pending, responded, closed)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)

**Response** (200 OK):
```json
{
  "items": [
    {
      "inquiry_id": "550e8400-e29b-41d4-a716-446655440001",
      "property_id": "prop_abc123",
      "sender_id": "buyer123",
      "receiver_id": "seller456",
      "message": "I'm interested in this property...",
      "contact_email": "buyer@example.com",
      "contact_phone": "0901234567",
      "status": "pending",
      "created_at": "2025-11-10T10:30:00Z",
      "property": { ... },
      "sender": {
        "user_id": "buyer123",
        "full_name": "John Buyer",
        "email": "buyer@example.com"
      }
    },
    ...
  ],
  "total": 8,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

---

### PUT /inquiries/{inquiry_id}/respond

Respond to inquiry (Seller).

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "response_message": "Thank you for your interest! The property is still available. I can arrange a viewing this Saturday at 2pm. Please let me know if this works for you."
}
```

**Response** (200 OK):
```json
{
  "message": "Response sent successfully"
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Not the inquiry receiver
- `404 Not Found`: Inquiry does not exist
- `400 Bad Request`: Inquiry already responded

**Side Effects**:
- Updates `status` to "responded"
- Sets `responded_at` timestamp
- Sends email notification to buyer (if enabled)

---

### PUT /inquiries/{inquiry_id}/status

Update inquiry status.

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```json
{
  "status": "closed"  // pending | responded | closed
}
```

**Response** (200 OK):
```json
{
  "message": "Inquiry status updated successfully"
}
```

---

### GET /inquiries/stats

Get inquiry statistics for seller.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "total_inquiries": 45,
  "pending_count": 3,
  "responded_count": 38,
  "closed_count": 4,
  "response_rate": 84.44,
  "avg_response_time_hours": 4.2
}
```

**Errors**:
- `401 Unauthorized`: Not authenticated

---

## Search API

Base URL: `http://localhost:8081`

### POST /search

Search properties using BM25 full-text search.

**Request**:
```json
{
  "query": "apartment district 7 near school",
  "filters": {
    "property_type": "apartment",
    "listing_type": "sale",
    "city": "Hồ Chí Minh",
    "district": "Quận 7",
    "min_price": 3000000000,
    "max_price": 7000000000,
    "min_area": 60,
    "max_area": 100,
    "min_bedrooms": 2,
    "max_bedrooms": 3
  },
  "limit": 20
}
```

**Response** (200 OK):
```json
{
  "results": [
    {
      "property_id": "prop_abc123",
      "title": "Modern 2BR Apartment in District 7",
      "price": 5000000000,
      "price_display": "5 tỷ",
      "description": "Beautiful apartment...",
      "property_type": "apartment",
      "bedrooms": 2,
      "bathrooms": 2,
      "area": 80,
      "district": "Quận 7",
      "city": "Hồ Chí Minh",
      "score": 12.345  // Relevance score
    },
    ...
  ],
  "total": 45,
  "execution_time_ms": 23.5
}
```

**Errors**:
- `400 Bad Request`: Invalid query or filters
- `503 Service Unavailable`: OpenSearch not available

**Note**: This endpoint does NOT require authentication (public search).

---

### POST /vector-search

Semantic search using vector embeddings.

**Request**:
```json
{
  "query": "quiet apartment near international school",
  "filters": { ... },
  "limit": 20
}
```

**Response**: Same format as `/search`

**Note**: Requires embedding model to be loaded. Currently disabled by default for faster startup.

---

### GET /stats

Get database statistics.

**Response** (200 OK):
```json
{
  "total_properties": 1523,
  "by_type": {
    "apartment": 845,
    "house": 432,
    "villa": 156,
    "land": 90
  },
  "by_district": {
    "Quận 7": 234,
    "Quận 2": 189,
    "Thủ Đức": 156,
    ...
  },
  "by_city": {
    "Hồ Chí Minh": 1234,
    "Hà Nội": 189,
    "Đà Nẵng": 100
  }
}
```

---

## Error Codes

### HTTP Status Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input, validation error |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 422 | Unprocessable Entity | Validation error (Pydantic) |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Database not available |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400
}
```

### Common Errors

**1. Authentication Errors**:
```json
{
  "detail": "Invalid or expired token",
  "status_code": 401
}
```

**2. Validation Errors**:
```json
{
  "detail": "price: ensure this value is greater than 0",
  "status_code": 422
}
```

**3. Permission Errors**:
```json
{
  "detail": "You are not the owner of this property",
  "status_code": 403
}
```

**4. Not Found Errors**:
```json
{
  "detail": "Property not found",
  "status_code": 404
}
```

---

## Rate Limiting

**Status**: Not implemented yet

**Recommended Configuration**:
- 100 requests per minute per IP
- 1000 requests per hour per user
- Use Redis for distributed rate limiting

**Implementation** (TODO):
```python
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/properties", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_property(...):
    ...
```

---

## Pagination

All list endpoints support pagination:

**Query Parameters**:
- `page`: Page number (starts at 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response Format**:
```json
{
  "items": [ ... ],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

---

## Postman Collection

Import this collection for easy API testing:

```json
{
  "info": {
    "name": "REE AI - User Areas API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url_user",
      "value": "http://localhost:8085"
    },
    {
      "key": "base_url_gateway",
      "value": "http://localhost:8081"
    },
    {
      "key": "token",
      "value": ""
    }
  ],
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": "{{base_url_user}}/register",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"Test123456\",\n  \"full_name\": \"Test User\",\n  \"user_type\": \"both\"\n}"
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{base_url_user}}/login",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"Test123456\"\n}"
            }
          }
        }
      ]
    }
  ]
}
```

---

## OpenAPI Specification

Auto-generated API documentation available at:
- User Management: http://localhost:8085/docs
- DB Gateway: http://localhost:8081/docs

Interactive Swagger UI with "Try it out" functionality.

---

## Changelog

### Version 1.0.0 (2025-11-10)

**Initial Release**:
- 29 API endpoints
- User Management (5 endpoints)
- Property Management (6 endpoints)
- Favorites (4 endpoints)
- Saved Searches (5 endpoints)
- Inquiries (6 endpoints)
- Search (3 endpoints)
- JWT authentication
- Pagination support
- Error handling

---

**For more information, see**:
- Feature Documentation: `docs/FEATURE_USER_AREAS.md`
- User Guide: `docs/USER_GUIDE.md`
- Developer Guide: `docs/DEVELOPER_GUIDE.md`

# User Areas Feature Documentation

## Overview

The User Areas feature enables REE AI platform to support **two distinct user types**: Sellers (property owners/landlords) and Buyers (property seekers/tenants). This feature transforms the platform from a search-only system into a complete real estate marketplace with property management, favorites, saved searches, and buyer-seller communication.

**Version**: 1.0.0
**Date**: November 2025
**Status**: ✅ Production Ready

---

## Table of Contents

1. [Feature Overview](#feature-overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [Backend Services](#backend-services)
5. [Frontend Components](#frontend-components)
6. [User Workflows](#user-workflows)
7. [API Endpoints](#api-endpoints)
8. [Setup Guide](#setup-guide)
9. [Testing Guide](#testing-guide)
10. [Security Considerations](#security-considerations)

---

## Feature Overview

### Problem Statement

Traditional real estate platforms have two critical limitations:
1. **No property posting capability** - Only admins can add properties via data scraping
2. **No seller-buyer interaction** - No communication channel between parties

### Solution

The User Areas feature provides:

**For Sellers (Property Owners/Landlords):**
- Create, edit, and manage property listings
- Track engagement metrics (views, favorites, inquiries)
- Receive and respond to buyer inquiries
- View performance analytics
- Publish/unpublish properties
- Mark properties as sold/rented

**For Buyers (Property Seekers/Tenants):**
- Save favorite properties with personal notes
- Save search criteria for notifications
- Contact sellers directly via inquiry forms
- Track inquiry status
- Get notified when new matching properties appear

**For Both:**
- Dual-role support (users can be both seller and buyer)
- Secure JWT authentication
- Role-based access control

### Key Benefits

1. **User Empowerment**: Sellers can post properties without admin intervention
2. **Direct Communication**: Buyers can contact sellers directly
3. **Personalization**: Save favorites and searches for better UX
4. **Analytics**: Sellers see engagement data to optimize listings
5. **Scalability**: Unlimited properties without manual data entry

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                      │
│  - Seller Dashboard    - Property Form    - Favorites List      │
│  - Buyer Dashboard     - Inquiry Form     - Search Interface    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS/REST
┌────────────────────────────┴────────────────────────────────────┐
│                    Backend Microservices                        │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ User Management  │  │   DB Gateway     │                   │
│  │  (Port 8085)     │  │  (Port 8081)     │                   │
│  │                  │  │                  │                   │
│  │ - Registration   │  │ - Properties     │                   │
│  │ - Authentication │  │ - Favorites      │                   │
│  │ - JWT Tokens     │  │ - Saved Searches │                   │
│  │ - User CRUD      │  │ - Inquiries      │                   │
│  └──────────────────┘  └──────────────────┘                   │
│           │                      │                              │
└───────────┼──────────────────────┼──────────────────────────────┘
            │                      │
            ▼                      ▼
┌────────────────────┐  ┌────────────────────┐
│    PostgreSQL      │  │    OpenSearch      │
│   (Port 5432)      │  │   (Port 9200)      │
│                    │  │                    │
│ - users            │  │ - properties       │
│ - favorites        │  │   (flexible JSON)  │
│ - saved_searches   │  │                    │
│ - inquiries        │  │                    │
│ - user_actions     │  │                    │
└────────────────────┘  └────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI 0.109.0 - Web framework
- asyncpg 0.29.0 - PostgreSQL async driver
- OpenSearch-py 2.4.2 - OpenSearch client
- PyJWT 2.8.0 - JWT authentication
- Bcrypt 4.1.2 - Password hashing

**Frontend:**
- Next.js 14 - React framework
- TypeScript 5.3.3 - Type safety
- TailwindCSS 3.4.0 - Styling
- React Hook Form 7.49.2 - Form validation
- Axios 1.6.2 - HTTP client
- SWR 2.2.4 - Data fetching

**Databases:**
- PostgreSQL 15+ - User data, relationships
- OpenSearch 2.11+ - Property documents
- Redis 7+ - Caching (optional)

### Data Storage Strategy

**Why Two Databases?**

1. **OpenSearch (PRIMARY for Properties)**:
   - **Flexible schema**: Properties have infinite variations (apartment vs villa vs land)
   - **Semantic search**: Vector embeddings for "find quiet apartment near school"
   - **BM25 full-text**: Keyword search with relevance scoring
   - **No migrations needed**: Add new fields without schema changes

2. **PostgreSQL (SECONDARY for Users)**:
   - **Relational integrity**: Foreign keys, ACID transactions
   - **User authentication**: Passwords, tokens, sessions
   - **Structured queries**: JOIN operations for favorites, inquiries
   - **Data consistency**: Critical user data needs strict validation

**Example Property (OpenSearch)**:
```json
{
  "property_id": "abc123",
  "owner_id": "user456",
  "title": "Luxury Villa in District 7",
  "price": 15000000000,
  "area": 300,
  "bedrooms": 5,
  "pool": true,
  "wine_cellar": true,
  "smart_home": "Full Lutron system",
  "any_new_field": "Can be added without migration"
}
```

---

## Database Schema

### PostgreSQL Tables

#### 1. users
```sql
CREATE TABLE users (
    user_id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    user_type VARCHAR(50) NOT NULL DEFAULT 'buyer',  -- seller/buyer/both
    role VARCHAR(50) NOT NULL DEFAULT 'user',        -- user/admin
    phone_number VARCHAR(50),
    company_name VARCHAR(255),
    license_number VARCHAR(100),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_user_type ON users(user_type);
```

**Purpose**: Store user accounts with type distinction
**Key Fields**:
- `user_type`: Determines user capabilities (seller/buyer/both)
- `verified`: Email/phone verification status
- `license_number`: For professional sellers

#### 2. favorites
```sql
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    property_id VARCHAR(255) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (user_id, property_id)
);

CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_favorites_property_id ON favorites(property_id);
```

**Purpose**: Track user's favorite properties
**Key Fields**:
- `notes`: Personal notes about the property
- `UNIQUE constraint`: Prevent duplicate favorites

#### 3. saved_searches
```sql
CREATE TABLE saved_searches (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    query TEXT NOT NULL,
    filters JSONB,
    notify_email BOOLEAN DEFAULT TRUE,
    notify_frequency VARCHAR(50) DEFAULT 'instant',  -- instant/daily/weekly
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_notified_at TIMESTAMP
);

CREATE INDEX idx_saved_searches_user_id ON saved_searches(user_id);
CREATE INDEX idx_saved_searches_active ON saved_searches(active);
```

**Purpose**: Store search criteria for automatic notifications
**Key Fields**:
- `filters`: JSONB for flexible search parameters
- `notify_frequency`: How often to send notifications
- `last_notified_at`: Track when last notification was sent

#### 4. inquiries
```sql
CREATE TABLE inquiries (
    inquiry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    property_id VARCHAR(255) NOT NULL,
    sender_id VARCHAR(255) NOT NULL REFERENCES users(user_id),
    receiver_id VARCHAR(255) NOT NULL REFERENCES users(user_id),
    message TEXT NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    preferred_contact_time VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',  -- pending/responded/closed
    response_message TEXT,
    responded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    CHECK (status IN ('pending', 'responded', 'closed'))
);

CREATE INDEX idx_inquiries_sender_id ON inquiries(sender_id);
CREATE INDEX idx_inquiries_receiver_id ON inquiries(receiver_id);
CREATE INDEX idx_inquiries_property_id ON inquiries(property_id);
CREATE INDEX idx_inquiries_status ON inquiries(status);
```

**Purpose**: Buyer-seller communication
**Key Fields**:
- `status`: Track inquiry lifecycle
- `response_message`: Seller's reply
- `responded_at`: For calculating response time

#### 5. user_actions
```sql
CREATE TABLE user_actions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id),
    action_type VARCHAR(100) NOT NULL,  -- view/favorite/contact/search/share
    property_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX idx_user_actions_action_type ON user_actions(action_type);
CREATE INDEX idx_user_actions_created_at ON user_actions(created_at);
```

**Purpose**: Analytics and activity tracking
**Key Fields**:
- `action_type`: Type of user activity
- `metadata`: Additional context (search query, filters, etc.)
- `created_at`: For time-series analysis

### OpenSearch Schema

#### properties Index
```json
{
  "mappings": {
    "properties": {
      "property_id": { "type": "keyword" },
      "owner_id": { "type": "keyword" },
      "title": { "type": "text" },
      "description": { "type": "text" },
      "property_type": { "type": "keyword" },
      "listing_type": { "type": "keyword" },

      "price": { "type": "double" },
      "area": { "type": "double" },
      "bedrooms": { "type": "integer" },
      "bathrooms": { "type": "integer" },

      "district": { "type": "keyword" },
      "city": { "type": "keyword" },
      "location": { "type": "text" },

      "status": { "type": "keyword" },
      "verification_status": { "type": "keyword" },

      "views_count": { "type": "integer" },
      "favorites_count": { "type": "integer" },
      "inquiries_count": { "type": "integer" },

      "images": { "type": "keyword" },
      "embedding": { "type": "knn_vector", "dimension": 384 },

      "created_at": { "type": "date" },
      "updated_at": { "type": "date" },
      "published_at": { "type": "date" }
    }
  }
}
```

**Key Features**:
- **Flexible schema**: Can add unlimited fields without migration
- **Numeric fields**: For range filtering (price, area)
- **Keyword fields**: For exact matching (district, city)
- **Text fields**: For full-text search (title, description)
- **Vector field**: For semantic search

---

## Backend Services

### 1. User Management Service

**Location**: `services/user_management/main.py`
**Port**: 8085
**Purpose**: Handle user registration, authentication, and profile management

**Key Features**:
- User registration with email/password
- JWT token generation and validation
- User type assignment (seller/buyer/both)
- Password hashing with bcrypt
- User profile CRUD operations

**Endpoints**:
```
POST   /register         - Register new user
POST   /login            - Login and get JWT token
GET    /users/me         - Get current user profile
PUT    /users/me         - Update user profile
POST   /logout           - Logout user
```

**Dependencies**:
- PostgreSQL (user data)
- PyJWT (token generation)
- Bcrypt (password hashing)

### 2. DB Gateway Service

**Location**: `services/db_gateway/main.py`
**Port**: 8081
**Purpose**: Central gateway for all database operations

**Modules**:
1. **property_management.py** - Seller property operations
2. **favorites_module.py** - Buyer favorites management
3. **saved_searches_module.py** - Search criteria management
4. **inquiries_module.py** - Buyer-seller communication

**Key Features**:
- Dual database support (PostgreSQL + OpenSearch)
- Connection pooling for performance
- JWT authentication on all protected endpoints
- Ownership verification for property operations
- Transaction management

**Endpoints**: 24 total (see API Documentation section)

---

## Frontend Components

### Component Architecture

```
frontend/ree-ai-app/src/
├── components/
│   ├── seller/
│   │   ├── SellerDashboard.tsx      (425 lines)
│   │   ├── PropertyForm.tsx         (362 lines)
│   │   └── PropertyList.tsx         (planned)
│   ├── buyer/
│   │   ├── FavoritesList.tsx        (188 lines)
│   │   ├── InquiryForm.tsx          (163 lines)
│   │   └── SavedSearchesList.tsx    (planned)
│   └── shared/
│       ├── PropertyCard.tsx         (130 lines)
│       └── SearchBar.tsx            (planned)
├── services/
│   └── api.ts                       (445 lines - API client)
└── types/
    └── index.ts                     (280 lines - TypeScript types)
```

### Component Details

#### 1. SellerDashboard (425 lines)

**Purpose**: Main dashboard for sellers showing overview and analytics

**Features**:
- Statistics cards (total properties, views, favorites, inquiries)
- Inquiry performance metrics (response rate, avg response time)
- Recent properties list with engagement data
- Status breakdown (active/draft/sold)
- Visual charts and progress bars

**Props**: None (fetches data via API)

**State**:
- `stats`: Dashboard statistics
- `inquiryStats`: Inquiry performance data
- `recentProperties`: Latest 5 properties
- `loading`: Loading state
- `error`: Error message

**API Calls**:
```typescript
api.property.getMyListings()
api.inquiries.getStats()
```

#### 2. PropertyForm (362 lines)

**Purpose**: Form for creating and editing property listings

**Features**:
- All property fields with validation
- Save as draft or publish immediately
- Edit mode for existing properties
- Real-time validation
- Success/error feedback
- Loading states

**Props**:
```typescript
{
  property?: Property;        // For edit mode
  onSuccess?: (property) => void;
  onCancel?: () => void;
}
```

**Fields**:
- Basic: title, description, property_type, listing_type
- Location: city, district, address
- Pricing: price
- Specifications: area, bedrooms, bathrooms, floors

**Validation Rules**:
- Title: Required, min 10 characters
- Description: Required, min 50 characters
- Price: Required, > 0
- Area: Required, > 0
- Bedrooms/Bathrooms: Required, >= 0

#### 3. FavoritesList (188 lines)

**Purpose**: Display and manage user's favorite properties

**Features**:
- Grid layout of favorite properties
- Inline note editing
- Remove from favorites
- Link to property details
- Empty state with CTA

**Props**: None

**State**:
- `favorites`: Array of favorites with property data
- `editingNotes`: Map of property_id to note text
- `loading`: Loading state
- `error`: Error message

**API Calls**:
```typescript
api.favorites.getAll()
api.favorites.remove(propertyId)
api.favorites.updateNotes(propertyId, notes)
```

#### 4. InquiryForm (163 lines)

**Purpose**: Form for buyers to contact sellers

**Features**:
- Message text area
- Contact information fields
- Preferred contact time
- Form validation
- Success feedback

**Props**:
```typescript
{
  propertyId: string;
  propertyTitle: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}
```

**Fields**:
- message: Required, min 10 characters
- contact_email: Optional, valid email
- contact_phone: Optional, 10-11 digits
- preferred_contact_time: Optional dropdown

#### 5. PropertyCard (130 lines)

**Purpose**: Reusable card component for displaying properties

**Features**:
- Property image with fallback
- Favorite toggle button
- Listing type badge (Sale/Rent)
- Status badge (Active/Sold/Draft)
- Property specs display
- Engagement metrics
- Hover effects
- Responsive design

**Props**:
```typescript
{
  property: Property;
  onFavoriteToggle?: (propertyId) => void;
  isFavorited?: boolean;
  showEngagementMetrics?: boolean;
  onClick?: (propertyId) => void;
}
```

---

## User Workflows

### Seller Workflow

```
1. Registration
   User registers → Select "seller" or "both" type → Email verification (optional)

2. Create Property Listing
   Dashboard → "New Property" → Fill form → Save draft OR Publish

3. Manage Properties
   Dashboard → View properties → Edit/Update status/Delete

4. Handle Inquiries
   Dashboard → View inquiries → Read message → Respond

5. Track Performance
   Dashboard → View stats → Analyze engagement → Optimize listings
```

**Detailed Steps**:

**Step 1: Registration**
```
POST /register
{
  "email": "seller@example.com",
  "password": "SecurePass123",
  "full_name": "John Seller",
  "user_type": "seller",
  "phone_number": "0901234567",
  "company_name": "John Real Estate"
}

Response: {
  "access_token": "eyJ...",
  "user": { "user_id": "...", "user_type": "seller", ... }
}
```

**Step 2: Create Property**
```
POST /properties
Authorization: Bearer eyJ...
{
  "title": "Modern 2BR Apartment in District 7",
  "description": "Beautiful apartment with city view...",
  "property_type": "apartment",
  "listing_type": "sale",
  "city": "Hồ Chí Minh",
  "district": "Quận 7",
  "price": 5000000000,
  "area": 80,
  "bedrooms": 2,
  "bathrooms": 2,
  "publish_immediately": true
}

Response: {
  "property_id": "abc123",
  "status": "active",
  "owner_id": "...",
  ...
}
```

**Step 3: Respond to Inquiry**
```
PUT /inquiries/{inquiry_id}/respond
Authorization: Bearer eyJ...
{
  "response_message": "Thank you for your interest! The property is still available. Would you like to schedule a viewing?"
}

Response: {
  "message": "Response sent successfully"
}
```

### Buyer Workflow

```
1. Registration
   User registers → Select "buyer" type → Browse properties

2. Search Properties
   Search page → Enter query + filters → View results

3. Save Favorites
   Property details → Click "Add to Favorites" → Add notes

4. Contact Seller
   Property details → Click "Contact" → Fill inquiry form → Submit

5. Track Inquiries
   Dashboard → View sent inquiries → Check responses
```

**Detailed Steps**:

**Step 1: Search Properties**
```
POST /search
{
  "query": "apartment district 7",
  "filters": {
    "city": "Hồ Chí Minh",
    "district": "Quận 7",
    "min_price": 3000000000,
    "max_price": 7000000000,
    "min_bedrooms": 2
  },
  "limit": 20
}

Response: {
  "results": [ {...}, {...}, ... ],
  "total": 45,
  "execution_time_ms": 23.5
}
```

**Step 2: Add to Favorites**
```
POST /favorites
Authorization: Bearer eyJ...
{
  "property_id": "abc123",
  "notes": "Nice location near school, good for family"
}

Response: {
  "message": "Added to favorites",
  "favorite_id": 42
}
```

**Step 3: Send Inquiry**
```
POST /inquiries
Authorization: Bearer eyJ...
{
  "property_id": "abc123",
  "message": "I'm interested in this property. Is it still available? Can I schedule a viewing this weekend?",
  "contact_email": "buyer@example.com",
  "contact_phone": "0901234567",
  "preferred_contact_time": "evening"
}

Response: {
  "message": "Inquiry sent successfully",
  "inquiry_id": "uuid-..."
}
```

---

## API Endpoints

### Summary

| Module | Endpoints | Description |
|--------|-----------|-------------|
| User Management | 5 | Authentication & user profiles |
| Property Management | 6 | Seller property CRUD |
| Favorites | 4 | Buyer favorites management |
| Saved Searches | 5 | Search criteria management |
| Inquiries | 6 | Buyer-seller communication |
| Search | 3 | Property search & stats |
| **Total** | **29** | |

### Authentication Endpoints

All endpoints except `/register` and `/login` require JWT authentication via `Authorization: Bearer <token>` header.

**Detailed API documentation**: See `docs/API_DOCUMENTATION.md`

---

## Setup Guide

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- OpenSearch 2.11+
- Docker & Docker Compose (recommended)

### Backend Setup

**1. Run Database Migrations**:
```bash
cd /home/user/ree-ai
chmod +x scripts/run-migrations.sh
./scripts/run-migrations.sh
```

This creates all 5 tables:
- users (with user_type)
- favorites
- saved_searches
- inquiries
- user_actions

**2. Start Backend Services**:
```bash
docker-compose --profile all up -d
```

Services running:
- User Management: http://localhost:8085
- DB Gateway: http://localhost:8081
- PostgreSQL: localhost:5432
- OpenSearch: localhost:9200

**3. Verify Health**:
```bash
curl http://localhost:8085/health
curl http://localhost:8081/health
```

### Frontend Setup

**1. Install Dependencies**:
```bash
cd frontend/ree-ai-app
npm install
```

**2. Configure Environment**:
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_DB_GATEWAY_URL=http://localhost:8081
NEXT_PUBLIC_USER_MANAGEMENT_URL=http://localhost:8085
```

**3. Start Dev Server**:
```bash
npm run dev
```

Frontend running: http://localhost:3001

---

## Testing Guide

### Manual Testing

**Test 1: User Registration & Login**
```bash
# Register seller
curl -X POST http://localhost:8085/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@test.com",
    "password": "Test123456",
    "full_name": "Test Seller",
    "user_type": "seller"
  }'

# Save the access_token from response

# Login
curl -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@test.com",
    "password": "Test123456"
  }'
```

**Test 2: Create Property**
```bash
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8081/properties \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Property",
    "description": "This is a test property for verification",
    "property_type": "apartment",
    "listing_type": "sale",
    "city": "Hồ Chí Minh",
    "district": "Quận 7",
    "price": 5000000000,
    "area": 80,
    "bedrooms": 2,
    "bathrooms": 2,
    "publish_immediately": true
  }'
```

**Test 3: Add to Favorites (register buyer first)**
```bash
# Register buyer
curl -X POST http://localhost:8085/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "buyer@test.com",
    "password": "Test123456",
    "full_name": "Test Buyer",
    "user_type": "buyer"
  }'

BUYER_TOKEN="buyer-jwt-token-here"
PROPERTY_ID="property-id-from-above"

curl -X POST http://localhost:8081/favorites \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "'$PROPERTY_ID'",
    "notes": "Test favorite"
  }'
```

**Test 4: Send Inquiry**
```bash
curl -X POST http://localhost:8081/inquiries \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": "'$PROPERTY_ID'",
    "message": "I am interested in this property",
    "contact_email": "buyer@test.com",
    "contact_phone": "0901234567"
  }'
```

### Automated Testing

Create test script `tests/test_user_areas.py`:

```python
import pytest
from services.user_management.main import app as user_app
from services.db_gateway.main import app as gateway_app
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_workflow():
    # Test user registration
    async with AsyncClient(app=user_app, base_url="http://test") as client:
        response = await client.post("/register", json={
            "email": "test@example.com",
            "password": "Test123456",
            "full_name": "Test User",
            "user_type": "both"
        })
        assert response.status_code == 200
        token = response.json()["access_token"]

    # Test property creation
    async with AsyncClient(app=gateway_app, base_url="http://test") as client:
        response = await client.post(
            "/properties",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Test Property",
                "description": "Test description",
                "property_type": "apartment",
                "listing_type": "sale",
                "city": "HCM",
                "district": "Q7",
                "price": 5000000000,
                "area": 80,
                "bedrooms": 2,
                "bathrooms": 2
            }
        )
        assert response.status_code == 200
        property_id = response.json()["property_id"]

    # Test add to favorites
    async with AsyncClient(app=gateway_app, base_url="http://test") as client:
        response = await client.post(
            "/favorites",
            headers={"Authorization": f"Bearer {token}"},
            json={"property_id": property_id, "notes": "Test"}
        )
        assert response.status_code == 200
```

Run tests:
```bash
pytest tests/test_user_areas.py -v
```

---

## Security Considerations

### Authentication

1. **JWT Tokens**:
   - HS256 algorithm
   - Secret key stored in environment variable
   - Token expiration: 7 days (configurable)
   - Token refresh not implemented (logout/login required)

2. **Password Security**:
   - Bcrypt hashing with salt
   - Minimum length: 8 characters
   - No plaintext passwords stored

3. **Authorization**:
   - Owner-only operations for property management
   - Sender/receiver validation for inquiries
   - User ID extracted from JWT token (not from request body)

### Data Validation

1. **Input Sanitization**:
   - Pydantic models validate all inputs
   - SQL injection prevented by parameterized queries
   - XSS prevented by not rendering raw HTML

2. **Rate Limiting** (TODO):
   - Not implemented yet
   - Recommend: 100 requests/minute per IP
   - Redis-based rate limiting

3. **CORS**:
   - Configured in DB Gateway
   - Default: localhost:3000, localhost:8888
   - Production: Set ALLOWED_ORIGINS env var

### Data Privacy

1. **Personal Data**:
   - Email, phone stored encrypted (TODO)
   - GDPR compliance required for EU users
   - Data retention policy needed

2. **Property Data**:
   - Owner ID not exposed in public API
   - Contact info only shared via inquiries
   - Soft delete recommended (mark as deleted, not DROP)

### Recommendations

1. **Enable HTTPS**: Use TLS/SSL in production
2. **Add Rate Limiting**: Prevent abuse
3. **Implement Refresh Tokens**: For better UX
4. **Add Email Verification**: Prevent fake accounts
5. **Enable Audit Logging**: Track all modifications
6. **Add CAPTCHA**: On registration/inquiry forms
7. **Implement 2FA**: For seller accounts (optional)

---

## Performance Optimization

### Database Optimization

1. **PostgreSQL**:
   - Indexes on frequently queried columns (✅ Already added)
   - Connection pooling (✅ Configured: min=5, max=20)
   - Query optimization with EXPLAIN ANALYZE

2. **OpenSearch**:
   - Bulk indexing for large datasets
   - Query result caching
   - Shard configuration for scale

### Caching Strategy

**Recommended Redis Usage**:

```python
# Cache user profile for 5 minutes
cache_key = f"user:{user_id}"
cached = await redis.get(cache_key)
if cached:
    return json.loads(cached)

user = await db.fetch_user(user_id)
await redis.setex(cache_key, 300, json.dumps(user))
return user
```

**Cache Invalidation**:
- Clear user cache on profile update
- Clear property cache on edit
- Use TTL for automatic expiration

### Frontend Optimization

1. **SWR Configuration**:
```typescript
// Automatic revalidation and caching
const { data, error } = useSWR('/api/properties', fetcher, {
  revalidateOnFocus: false,
  revalidateOnReconnect: true,
  refreshInterval: 60000 // 1 minute
});
```

2. **Image Optimization**:
- Use Next.js Image component
- Lazy loading for property images
- WebP format with fallback

3. **Code Splitting**:
- Dynamic imports for heavy components
- Route-based code splitting (built-in with Next.js)

---

## Troubleshooting

### Common Issues

**Issue 1: "Database not available" error**
```
Solution:
1. Check PostgreSQL is running: docker ps | grep postgres
2. Verify connection: psql -U ree_ai_user -d ree_ai -h localhost
3. Check migrations: ./scripts/run-migrations.sh
```

**Issue 2: "OpenSearch not available" error**
```
Solution:
1. Check OpenSearch is running: curl http://localhost:9200
2. Verify index exists: curl http://localhost:9200/_cat/indices
3. Create index if missing (auto-created on first insert)
```

**Issue 3: "401 Unauthorized" on API calls**
```
Solution:
1. Check token is valid: jwt.decode(token, verify=False)
2. Verify Authorization header: "Bearer <token>" (not "Token <token>")
3. Re-login if token expired
```

**Issue 4: Frontend can't connect to backend**
```
Solution:
1. Check CORS configuration in services/db_gateway/main.py
2. Verify API URLs in .env.local
3. Check browser console for CORS errors
4. Add frontend URL to ALLOWED_ORIGINS
```

---

## Migration Guide

### Upgrading from Search-Only System

**Step 1: Backup Database**
```bash
pg_dump -U ree_ai_user ree_ai > backup_before_migration.sql
```

**Step 2: Run New Migrations**
```bash
./scripts/run-migrations.sh
```

**Step 3: Migrate Existing Users** (if any)
```sql
-- Add user_type to existing users
UPDATE users SET user_type = 'buyer' WHERE user_type IS NULL;
```

**Step 4: Update Properties with owner_id**
```python
# Script to assign owner_id to existing properties
# Run once during migration
for property in existing_properties:
    property['owner_id'] = 'admin'  # or appropriate user
    opensearch_client.update(...)
```

**Step 5: Test All Endpoints**
- Use test script in Testing Guide
- Verify all 29 endpoints work

**Step 6: Deploy Frontend**
```bash
cd frontend/ree-ai-app
npm run build
npm start
```

---

## Future Enhancements

### Phase 2 Features

1. **Payment Integration**:
   - Deposit payments via Stripe/VNPay
   - Transaction history
   - Escrow service

2. **Advanced Search**:
   - Map-based search
   - Polygon drawing for area selection
   - Price prediction ML model

3. **Notifications**:
   - Email notifications for inquiries
   - Push notifications (FCM)
   - SMS alerts for saved search matches

4. **Property Verification**:
   - Admin approval workflow
   - Document upload (ownership proof)
   - Background checks

5. **Analytics Dashboard**:
   - Seller performance metrics
   - Market trend analysis
   - Competitor analysis

### Phase 3 Features

1. **Mobile App**:
   - React Native app
   - Offline mode
   - Camera integration for photos

2. **Virtual Tours**:
   - 360° photo integration
   - Video tours
   - Live video calls with sellers

3. **AI Recommendations**:
   - Personalized property suggestions
   - Price optimization for sellers
   - Chatbot for instant answers

---

## Support & Contact

**Documentation**: `/docs`
**API Docs**: `http://localhost:8081/docs` (FastAPI auto-docs)
**Issues**: GitHub Issues
**Version**: 1.0.0
**Last Updated**: November 2025

---

## Appendix

### A. Environment Variables

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=ree_ai_user
POSTGRES_PASSWORD=ree_ai_password
POSTGRES_DB=ree_ai

# OpenSearch
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_PROPERTIES_INDEX=properties

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# Frontend
NEXT_PUBLIC_DB_GATEWAY_URL=http://localhost:8081
NEXT_PUBLIC_USER_MANAGEMENT_URL=http://localhost:8085

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### B. File Structure

```
ree-ai/
├── services/
│   ├── user_management/
│   │   ├── main.py                (564 lines)
│   │   └── requirements.txt
│   └── db_gateway/
│       ├── main.py                (1,242 lines)
│       ├── property_management.py (429 lines)
│       ├── favorites_module.py    (274 lines)
│       ├── saved_searches_module.py (301 lines)
│       ├── inquiries_module.py    (423 lines)
│       └── requirements.txt
├── shared/
│   └── models/
│       ├── users.py
│       ├── properties.py
│       ├── favorites.py
│       ├── saved_searches.py
│       └── inquiries.py
├── database/
│   └── migrations/
│       ├── 001_add_user_types.sql
│       ├── 002_create_favorites.sql
│       ├── 003_create_saved_searches.sql
│       ├── 004_create_inquiries.sql
│       └── 005_create_user_actions.sql
├── frontend/
│   └── ree-ai-app/
│       ├── src/
│       │   ├── components/
│       │   │   ├── seller/
│       │   │   ├── buyer/
│       │   │   └── shared/
│       │   ├── services/
│       │   └── types/
│       └── package.json
└── docs/
    ├── FEATURE_USER_AREAS.md (this file)
    ├── API_DOCUMENTATION.md
    ├── USER_GUIDE.md
    └── DEVELOPER_GUIDE.md
```

### C. Glossary

- **Seller**: User who posts/manages property listings
- **Buyer**: User who searches/saves properties and contacts sellers
- **Property**: Real estate listing (apartment, house, villa, land, commercial)
- **Favorite**: Saved property with optional personal notes
- **Saved Search**: Stored search criteria for automatic notifications
- **Inquiry**: Message from buyer to seller about a property
- **Listing Type**: Sale or Rent
- **Property Status**: draft/pending/active/sold/rented/paused
- **User Type**: seller/buyer/both

---

**End of Documentation**

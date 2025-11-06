# REE AI User Types Architecture

## Overview

REE AI supports **two primary user personas** with distinct workflows:

1. **Seller/Landlord** - Posts and manages property listings
2. **Buyer/Tenant** - Searches and discovers properties

## User Types

### 1. Seller/Landlord (Property Provider)

**Goals:**
- Post property listings quickly
- Manage listings (edit, delete, pause)
- Track performance (views, contacts, inquiries)
- Respond to buyer inquiries

**User Journey:**
```
Register → Verify Account → Post Property → AI Extraction → Review & Edit → Publish → Manage
```

**Key Features:**
- Property posting form with AI assistance
- Draft management
- Performance analytics
- Inquiry management
- Bulk upload (for agencies)

---

### 2. Buyer/Tenant (Property Seeker)

**Goals:**
- Find properties matching criteria
- Save favorite properties
- Compare options
- Contact sellers

**User Journey:**
```
Browse → Search → Filter → Compare → Save Favorites → Contact Seller → Negotiate
```

**Key Features:**
- Advanced search (text + filters)
- Saved searches
- Favorite properties
- Property comparison
- Contact sellers
- View history

---

## Database Schema Updates

### User Table (PostgreSQL)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255),

    -- User type
    user_type VARCHAR(20) NOT NULL,  -- 'seller', 'buyer', 'both'
    role VARCHAR(20) DEFAULT 'user',  -- 'user', 'admin' (system role)

    -- Profile
    full_name VARCHAR(255),
    phone_number VARCHAR(20),
    avatar_url TEXT,
    bio TEXT,

    -- Seller-specific fields
    company_name VARCHAR(255),  -- For agencies
    license_number VARCHAR(100),  -- Real estate license
    verified BOOLEAN DEFAULT FALSE,  -- Email/phone verified

    -- Preferences (JSON)
    preferences JSONB,  -- Search preferences, notification settings

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_verified ON users(verified);
```

### Property Listings Table (OpenSearch)

```json
{
  "property_id": "uuid",
  "owner_id": "uuid",  // ✅ NEW: User who posted

  // Basic info (English master data)
  "title": "string",
  "description": "string",
  "property_type": "apartment|villa|townhouse|land|office|commercial",
  "listing_type": "sale|rent",  // ✅ NEW

  // Location
  "district": "District 7",
  "ward": "Tan Phong",
  "street": "Nguyen Van Linh",
  "city": "Ho Chi Minh City",

  // Attributes (flexible schema)
  "price": 2500000000,
  "bedrooms": 2,
  "bathrooms": 2,
  "area": 75,
  "floor": 15,
  "swimming_pool": true,
  // ... unlimited additional fields

  // Media
  "images": ["url1", "url2"],
  "videos": ["url1"],
  "virtual_tour_url": "string",

  // Status & Moderation
  "status": "draft|pending|active|sold|rented|paused",  // ✅ NEW
  "verification_status": "unverified|verified|rejected",  // ✅ NEW
  "rejection_reason": "string",

  // SEO & Metadata
  "slug": "apartment-2br-district-7-phu-my-hung",
  "seo_title": "string",
  "seo_description": "string",

  // Analytics
  "views_count": 0,  // ✅ NEW
  "favorites_count": 0,  // ✅ NEW
  "inquiries_count": 0,  // ✅ NEW

  // Timestamps
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z",
  "published_at": "2025-01-15T12:00:00Z",  // ✅ NEW
  "expires_at": "2025-04-15T12:00:00Z"  // ✅ NEW: Auto-expire after 90 days
}
```

### User Actions Table (PostgreSQL)

Track user interactions for analytics and recommendations:

```sql
CREATE TABLE user_actions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    action_type VARCHAR(50) NOT NULL,  -- 'view', 'favorite', 'unfavorite', 'contact', 'search'
    property_id UUID,  -- NULL for search actions

    -- Action metadata (JSON)
    metadata JSONB,  -- Search query, filters, etc.

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX idx_user_actions_property_id ON user_actions(property_id);
CREATE INDEX idx_user_actions_type ON user_actions(action_type);
CREATE INDEX idx_user_actions_created_at ON user_actions(created_at DESC);
```

### Favorite Properties Table (PostgreSQL)

```sql
CREATE TABLE favorites (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    property_id UUID NOT NULL,

    -- Metadata
    notes TEXT,  -- User's private notes
    created_at TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, property_id)
);

CREATE INDEX idx_favorites_user_id ON favorites(user_id);
```

### Saved Searches Table (PostgreSQL)

```sql
CREATE TABLE saved_searches (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,

    -- Search criteria
    search_name VARCHAR(255) NOT NULL,
    query TEXT,
    filters JSONB,  -- SearchFilters JSON

    -- Notifications
    notify_new_listings BOOLEAN DEFAULT TRUE,
    notify_price_drops BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_notified_at TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_saved_searches_user_id ON saved_searches(user_id);
```

### Inquiries Table (PostgreSQL)

Track buyer inquiries to sellers:

```sql
CREATE TABLE inquiries (
    id UUID PRIMARY KEY,
    property_id UUID NOT NULL,
    sender_id UUID NOT NULL,  -- Buyer
    receiver_id UUID NOT NULL,  -- Seller (property owner)

    -- Message
    message TEXT NOT NULL,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),

    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'responded', 'closed'

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    responded_at TIMESTAMP
);

CREATE INDEX idx_inquiries_property_id ON inquiries(property_id);
CREATE INDEX idx_inquiries_sender_id ON inquiries(sender_id);
CREATE INDEX idx_inquiries_receiver_id ON inquiries(receiver_id);
```

---

## API Endpoints

### User Management

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/users/me
PUT    /api/v1/users/me
PUT    /api/v1/users/me/preferences
```

### Property Management (Seller)

```
POST   /api/v1/properties                    # Create property (draft)
GET    /api/v1/properties/my-listings        # Get seller's properties
GET    /api/v1/properties/:id                # Get single property
PUT    /api/v1/properties/:id                # Update property
DELETE /api/v1/properties/:id                # Delete property
POST   /api/v1/properties/:id/publish        # Publish draft → active
POST   /api/v1/properties/:id/pause          # Pause active listing
POST   /api/v1/properties/:id/reactivate     # Reactivate paused listing
POST   /api/v1/properties/:id/upload-images  # Upload property images
GET    /api/v1/properties/:id/analytics      # Get property analytics
```

### Property Search (Buyer)

```
POST   /api/v1/search                        # Search properties
GET    /api/v1/properties/:id                # View property details
POST   /api/v1/properties/:id/view           # Track property view
```

### Favorites (Buyer)

```
GET    /api/v1/favorites                     # Get user's favorites
POST   /api/v1/favorites                     # Add to favorites
DELETE /api/v1/favorites/:propertyId         # Remove from favorites
```

### Saved Searches (Buyer)

```
GET    /api/v1/saved-searches                # Get user's saved searches
POST   /api/v1/saved-searches                # Create saved search
PUT    /api/v1/saved-searches/:id            # Update saved search
DELETE /api/v1/saved-searches/:id            # Delete saved search
```

### Inquiries

```
POST   /api/v1/inquiries                     # Send inquiry (buyer → seller)
GET    /api/v1/inquiries/sent                # Get sent inquiries (buyer)
GET    /api/v1/inquiries/received            # Get received inquiries (seller)
PUT    /api/v1/inquiries/:id                 # Update inquiry status
```

---

## Frontend Components

### Seller Components

```
components/seller/
├── PropertyPostingForm.svelte          # Main posting form with AI extraction
├── PropertyDraftList.svelte            # List of draft properties
├── PropertyManagementDashboard.svelte  # Seller dashboard
├── PropertyEditor.svelte               # Edit existing property
├── PropertyAnalytics.svelte            # Views, favorites, inquiries stats
├── InquiryList.svelte                  # Received inquiries
└── BulkPropertyUpload.svelte           # For agencies
```

### Buyer Components

```
components/buyer/
├── PropertySearch.svelte               # ✅ Already exists
├── PropertyCard.svelte                 # ✅ Already exists
├── PropertyDetails.svelte              # ✅ Already exists
├── PropertyComparison.svelte           # ✅ Already exists
├── FavoritesList.svelte                # ❌ NEW
├── SavedSearchesList.svelte            # ❌ NEW
├── InquiryForm.svelte                  # ❌ NEW - Contact seller
└── ViewHistory.svelte                  # ❌ NEW
```

---

## User Workflows

### Seller Workflow: Post New Property

```
1. Navigate to "Post Property"
2. Choose listing type (Sale/Rent)
3. Choose property type (Apartment/Villa/etc.)
4. Enter property description (natural language)
   "Căn hộ 2PN quận 7 Phú Mỹ Hưng, 75m², full nội thất, view sông"
5. AI Extraction Service automatically extracts:
   - property_type: "apartment"
   - bedrooms: 2
   - district: "District 7"
   - area: 75
   - furniture: "full"
   - view: "river_view"
6. Review AI-extracted data
7. Upload images (3-10 photos)
8. Add contact info (phone/email)
9. Preview listing
10. Save as draft OR Publish immediately
```

### Buyer Workflow: Find Property

```
1. Land on homepage with search bar
2. Enter natural language query:
   "Tìm căn hộ 2PN quận 7 dưới 3 tỷ có hồ bơi"
3. AI understands and applies filters automatically
4. Browse results (PropertyCard grid)
5. Click property → PropertyDetails
6. Actions:
   - ❤️ Add to Favorites
   - 📞 Contact Seller (InquiryForm)
   - 📊 Compare with others
   - 💾 Save search for notifications
7. Receive email when new matching properties posted
```

---

## Permission Matrix

| Feature | Anonymous | Buyer | Seller | Admin |
|---------|-----------|-------|--------|-------|
| **Search properties** | ✅ | ✅ | ✅ | ✅ |
| **View property details** | ✅ | ✅ | ✅ | ✅ |
| **Add to favorites** | ❌ | ✅ | ✅ | ✅ |
| **Save searches** | ❌ | ✅ | ✅ | ✅ |
| **Contact seller** | ❌ | ✅ | ❌ | ✅ |
| **Post property** | ❌ | ❌ | ✅ | ✅ |
| **Edit own property** | ❌ | ❌ | ✅ (own) | ✅ (all) |
| **Delete own property** | ❌ | ❌ | ✅ (own) | ✅ (all) |
| **View analytics** | ❌ | ❌ | ✅ (own) | ✅ (all) |
| **Moderate listings** | ❌ | ❌ | ❌ | ✅ |

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Update User schema with `user_type`
- [ ] Add `owner_id`, `status` to Property schema
- [ ] Create Favorites table
- [ ] Create User Actions tracking

### Phase 2: Seller Features (Week 3-4)
- [ ] PropertyPostingForm component
- [ ] POST /properties endpoint
- [ ] Draft management
- [ ] Image upload
- [ ] Seller dashboard

### Phase 3: Buyer Features (Week 5-6)
- [ ] Favorites system
- [ ] Saved searches
- [ ] Inquiry system (contact seller)
- [ ] View history

### Phase 4: Analytics & Optimization (Week 7-8)
- [ ] Property analytics
- [ ] Email notifications
- [ ] Search recommendations
- [ ] Performance optimization

---

## Security Considerations

### Property Posting
- **Verification**: New sellers require email/phone verification
- **Rate limiting**: Max 5 properties per day for new users
- **Image validation**: Max 10 images, 5MB each, JPG/PNG only
- **Content moderation**: AI check for inappropriate content
- **Spam prevention**: Duplicate detection

### User Data
- **Authentication**: JWT tokens with expiration
- **Authorization**: Role-based access control (RBAC)
- **Privacy**: Sellers choose which contact info to show
- **Data encryption**: Sensitive data encrypted at rest

### Anti-Scraping
- **Rate limiting**: Max 100 searches per hour for anonymous
- **CAPTCHA**: After suspicious activity
- **API keys**: Required for bulk operations
- **Watermarking**: Optional for property images

---

## Analytics & Tracking

### Seller Analytics (per property)
```json
{
  "property_id": "uuid",
  "period": "last_30_days",
  "views": 1250,
  "unique_views": 980,
  "favorites": 45,
  "inquiries": 12,
  "inquiry_response_rate": 0.83,
  "avg_time_on_page": "2m 35s",
  "traffic_sources": {
    "search": 850,
    "direct": 200,
    "saved_search_alert": 150,
    "social": 50
  }
}
```

### Platform Analytics (Admin)
```json
{
  "period": "last_30_days",
  "total_users": 15000,
  "new_users": 1200,
  "sellers": 3500,
  "buyers": 11500,
  "active_listings": 8900,
  "new_listings": 850,
  "searches_count": 45000,
  "avg_searches_per_user": 12.5,
  "top_search_terms": ["căn hộ quận 7", "biệt thự quận 2", "nhà phố bình thạnh"]
}
```

---

## Notification System

### Seller Notifications
- New inquiry received
- Property view milestone (100, 500, 1000 views)
- Listing expiring soon (7 days before)
- Verification status changed

### Buyer Notifications
- New properties matching saved search
- Price drop on favorited property
- Seller responded to inquiry
- Property status changed (sold/rented)

### Notification Channels
- **Email**: For important events
- **In-app**: Real-time toast notifications
- **SMS** (optional): Critical alerts only
- **Push** (mobile app): Future enhancement

---

## Future Enhancements

1. **Seller Tiers**
   - Free: 5 listings, basic analytics
   - Premium: Unlimited listings, advanced analytics, featured placement
   - Agency: Bulk upload, team management, API access

2. **Buyer Premium**
   - Unlimited saved searches
   - Price drop alerts
   - Exclusive early access to new listings
   - AI-powered recommendations

3. **Social Features**
   - Share listings to social media
   - Property reviews/ratings
   - Neighborhood guides
   - Q&A forums

4. **AI Enhancements**
   - Auto-price suggestions
   - Property quality scoring
   - Photo enhancement
   - Virtual staging

---

## Migration Strategy

### From Current State → Full User Types

**Step 1: Schema Updates (Non-breaking)**
```sql
-- Add new columns to users table
ALTER TABLE users ADD COLUMN user_type VARCHAR(20) DEFAULT 'buyer';
ALTER TABLE users ADD COLUMN verified BOOLEAN DEFAULT FALSE;

-- Add new columns to properties (OpenSearch mapping update)
-- owner_id, status, verification_status, analytics
```

**Step 2: Create New Tables**
```sql
-- Create in order (respect foreign keys)
CREATE TABLE favorites;
CREATE TABLE saved_searches;
CREATE TABLE user_actions;
CREATE TABLE inquiries;
```

**Step 3: Migrate Existing Data**
```sql
-- Mark all existing users as buyers (they were only searching)
UPDATE users SET user_type = 'buyer' WHERE user_type IS NULL;

-- Mark all existing properties as "active" with no owner
-- (migrated from crawler data)
```

**Step 4: Deploy New Features**
- Deploy seller posting flow
- Deploy favorites/saved searches
- Deploy inquiry system

**Step 5: User Communication**
- Email existing users about new features
- Onboarding flow for posting first property
- Tutorial videos

---

## Testing Strategy

### Unit Tests
- User type validation
- Property status transitions
- Permission checks
- AI extraction for posting

### Integration Tests
- End-to-end posting flow
- Search → Favorite → Inquiry flow
- Email notifications
- Image upload

### Load Tests
- 1000 concurrent searches
- 100 simultaneous property posts
- Bulk upload (1000 properties)

### User Acceptance Tests
- Seller posts first property (5 min)
- Buyer finds and contacts seller (3 min)
- Admin moderates listing (2 min)

---

## Success Metrics

### Seller Success
- Time to first listing: <10 minutes
- Listing completion rate: >80%
- Average inquiries per listing: >5
- Seller retention (30 days): >60%

### Buyer Success
- Search success rate: >70%
- Favorite conversion rate: >15%
- Inquiry response rate: >50%
- Buyer retention (30 days): >70%

### Platform Health
- Daily active users (DAU): Target 10K
- Monthly active listings: Target 50K
- Search → Contact conversion: >5%
- User satisfaction (NPS): >50

---

This architecture provides a complete foundation for supporting both seller and buyer user types with clear separation of concerns, scalability, and excellent user experience.

# Quick Start Guide - User Areas Feature

Get up and running with REE AI's seller and buyer features in 5 minutes!

---

## For End Users

### As a Seller (Property Owner/Landlord)

**1. Create Account**
- Go to http://localhost:3001/register
- Fill in your details
- Select "Seller" as user type
- Click "Register"

**2. Post Your First Property**
- Login to your dashboard
- Click "New Property" button
- Fill in property details:
  - Title (e.g., "Modern 2BR Apartment in District 7")
  - Description (minimum 50 characters)
  - Property type (Apartment, House, Villa, Land, Commercial)
  - Listing type (For Sale or For Rent)
  - Location (City, District, Address)
  - Price (in VND)
  - Area (in m²)
  - Bedrooms & Bathrooms
- Click "Publish" or "Save as Draft"

**3. Manage Your Listings**
- View all your properties on the dashboard
- See engagement metrics (views, favorites, inquiries)
- Edit, pause, or mark properties as sold
- Respond to buyer inquiries

**4. Track Performance**
- Dashboard shows total views, favorites, inquiries
- See response rate and average response time
- Analyze which properties get the most attention

---

### As a Buyer (Property Seeker)

**1. Create Account**
- Go to http://localhost:3001/register
- Fill in your details
- Select "Buyer" as user type
- Click "Register"

**2. Search for Properties**
- Use the search bar on homepage
- Apply filters:
  - Property type
  - Location (City, District)
  - Price range
  - Area range
  - Number of bedrooms
- Browse results

**3. Save Favorites**
- Click the heart icon on any property
- Add personal notes (e.g., "Good location near school")
- View all favorites in your dashboard

**4. Contact Sellers**
- Click "Contact" button on property details page
- Fill in inquiry form:
  - Your message
  - Contact email (optional)
  - Contact phone (optional)
  - Preferred contact time
- Click "Send"
- Track inquiry status in your dashboard

**5. Save Searches**
- After searching, click "Save this search"
- Name your search (e.g., "2BR in Q7 under 6B")
- Enable email notifications
- Choose frequency (instant, daily, weekly)
- Get notified when new matching properties appear

---

## For Developers

### Quick Setup (5 minutes)

**1. Start Backend Services**
```bash
cd /home/user/ree-ai

# Run database migrations
chmod +x scripts/run-migrations.sh
./scripts/run-migrations.sh

# Start all services
docker-compose --profile all up -d

# Verify health
curl http://localhost:8085/health  # User Management
curl http://localhost:8081/health  # DB Gateway
```

**2. Start Frontend**
```bash
cd frontend/ree-ai-app

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local if needed (defaults to localhost)

# Start dev server
npm run dev
```

**3. Open Browser**
- Frontend: http://localhost:3001
- API Docs: http://localhost:8081/docs
- User Management Docs: http://localhost:8085/docs

**4. Create Test User**
```bash
curl -X POST http://localhost:8085/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123456",
    "full_name": "Test User",
    "user_type": "both"
  }'
```

**5. Test API**
```bash
# Login and get token
TOKEN=$(curl -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123456"}' \
  | jq -r '.access_token')

# Create property
curl -X POST http://localhost:8081/properties \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Property",
    "description": "This is a test property for verification purposes",
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

# Get my listings
curl -X GET http://localhost:8081/properties/my-listings \
  -H "Authorization: Bearer $TOKEN"
```

Done! 🎉

---

## Testing Workflows

### Seller Workflow Test

```bash
# 1. Register seller
curl -X POST http://localhost:8085/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@test.com",
    "password": "Seller123",
    "full_name": "Test Seller",
    "user_type": "seller",
    "company_name": "Test Real Estate"
  }'

# 2. Login
SELLER_TOKEN=$(curl -s -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{"email":"seller@test.com","password":"Seller123"}' \
  | jq -r '.access_token')

# 3. Create property
PROPERTY_ID=$(curl -s -X POST http://localhost:8081/properties \
  -H "Authorization: Bearer $SELLER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Beautiful Villa with Pool",
    "description": "Luxurious 4-bedroom villa with private pool and garden in quiet area",
    "property_type": "villa",
    "listing_type": "sale",
    "city": "Hồ Chí Minh",
    "district": "Quận 2",
    "price": 15000000000,
    "area": 300,
    "bedrooms": 4,
    "bathrooms": 5,
    "publish_immediately": true
  }' | jq -r '.property_id')

echo "Property created: $PROPERTY_ID"

# 4. View my listings
curl -X GET http://localhost:8081/properties/my-listings \
  -H "Authorization: Bearer $SELLER_TOKEN" | jq

# 5. Get inquiry stats
curl -X GET http://localhost:8081/inquiries/stats \
  -H "Authorization: Bearer $SELLER_TOKEN" | jq
```

### Buyer Workflow Test

```bash
# 1. Register buyer
curl -X POST http://localhost:8085/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "buyer@test.com",
    "password": "Buyer123",
    "full_name": "Test Buyer",
    "user_type": "buyer"
  }'

# 2. Login
BUYER_TOKEN=$(curl -s -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{"email":"buyer@test.com","password":"Buyer123"}' \
  | jq -r '.access_token')

# 3. Search properties
curl -X POST http://localhost:8081/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "villa",
    "limit": 10
  }' | jq

# 4. Add to favorites (use PROPERTY_ID from above)
curl -X POST http://localhost:8081/favorites \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"property_id\": \"$PROPERTY_ID\",
    \"notes\": \"Interested in this villa for my family\"
  }"

# 5. Get favorites
curl -X GET http://localhost:8081/favorites \
  -H "Authorization: Bearer $BUYER_TOKEN" | jq

# 6. Send inquiry
curl -X POST http://localhost:8081/inquiries \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"property_id\": \"$PROPERTY_ID\",
    \"message\": \"I am very interested in this villa. Is it still available? Can I schedule a viewing this weekend?\",
    \"contact_email\": \"buyer@test.com\",
    \"contact_phone\": \"0901234567\",
    \"preferred_contact_time\": \"weekend\"
  }"

# 7. Get sent inquiries
curl -X GET http://localhost:8081/inquiries/sent \
  -H "Authorization: Bearer $BUYER_TOKEN" | jq
```

### Seller Respond to Inquiry

```bash
# 1. Seller checks received inquiries
curl -X GET http://localhost:8081/inquiries/received \
  -H "Authorization: Bearer $SELLER_TOKEN" | jq

# 2. Get inquiry ID from above response
INQUIRY_ID="<inquiry-id-from-response>"

# 3. Respond to inquiry
curl -X PUT "http://localhost:8081/inquiries/$INQUIRY_ID/respond" \
  -H "Authorization: Bearer $SELLER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response_message": "Thank you for your interest! The villa is still available. I can arrange a viewing this Saturday at 2pm. Please let me know if this works for you."
  }'

# 4. Buyer checks inquiry status
curl -X GET http://localhost:8081/inquiries/sent \
  -H "Authorization: Bearer $BUYER_TOKEN" | jq
```

---

## Common Issues & Solutions

### Issue: "Database not available"
**Solution**: Ensure PostgreSQL and OpenSearch are running
```bash
docker ps | grep -E 'postgres|opensearch'
```

### Issue: "401 Unauthorized"
**Solution**: Token may be expired, login again
```bash
curl -X POST http://localhost:8085/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}'
```

### Issue: Frontend can't connect to backend
**Solution**: Check CORS configuration and .env.local
```bash
# In frontend/ree-ai-app/.env.local
NEXT_PUBLIC_DB_GATEWAY_URL=http://localhost:8081
NEXT_PUBLIC_USER_MANAGEMENT_URL=http://localhost:8085
```

### Issue: Migrations not applied
**Solution**: Run migration script
```bash
cd /home/user/ree-ai
./scripts/run-migrations.sh
```

---

## Next Steps

1. **Read Full Documentation**:
   - Feature Overview: `docs/FEATURE_USER_AREAS.md`
   - API Reference: `docs/API_DOCUMENTATION.md`

2. **Explore Examples**:
   - Test scripts: `tests/test_user_areas.py`
   - Frontend components: `frontend/ree-ai-app/src/components/`

3. **Customize**:
   - Add custom property fields (OpenSearch flexible schema)
   - Modify frontend styling (TailwindCSS)
   - Implement notifications (email/SMS)

4. **Deploy**:
   - See deployment guide for production setup
   - Configure SSL/TLS
   - Set up monitoring

---

## API Endpoints Summary

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/register` | POST | Register user | ❌ |
| `/login` | POST | Login | ❌ |
| `/users/me` | GET | Get profile | ✅ |
| `/properties` | POST | Create property | ✅ |
| `/properties/my-listings` | GET | Get my properties | ✅ |
| `/properties/:id` | PUT | Update property | ✅ |
| `/properties/:id/status` | PUT | Change status | ✅ |
| `/properties/:id` | DELETE | Delete property | ✅ |
| `/favorites` | POST | Add favorite | ✅ |
| `/favorites` | GET | Get favorites | ✅ |
| `/favorites/:id` | DELETE | Remove favorite | ✅ |
| `/inquiries` | POST | Send inquiry | ✅ |
| `/inquiries/sent` | GET | Get sent inquiries | ✅ |
| `/inquiries/received` | GET | Get received inquiries | ✅ |
| `/inquiries/:id/respond` | PUT | Respond to inquiry | ✅ |
| `/inquiries/stats` | GET | Get inquiry stats | ✅ |
| `/search` | POST | Search properties | ❌ |

**Total**: 29 endpoints (see full API docs for details)

---

## Support

- **Documentation**: `/docs` directory
- **API Docs**: http://localhost:8081/docs (Swagger UI)
- **Issues**: GitHub Issues
- **Version**: 1.0.0

---

**Ready to build amazing real estate applications!** 🏡

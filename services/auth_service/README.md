# User Management Service

Authentication and user CRUD service for REE AI platform.

## Features

- **User Registration**: Register as seller or buyer
- **Authentication**: JWT-based login/logout
- **Profile Management**: Update user profile
- **Seller Verification**: Special verification flow for sellers

## API Endpoints

### Authentication

```
POST /register
POST /login
GET  /users/me
PUT  /users/me
```

### Register User

```bash
curl -X POST http://localhost:8089/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "securepass123",
    "full_name": "John Doe",
    "user_type": "seller",
    "phone_number": "+84901234567",
    "company_name": "ABC Real Estate"
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "seller@example.com",
    "user_type": "seller",
    "role": "pending",
    "full_name": "John Doe",
    "verified": false
  }
}
```

### Login

```bash
curl -X POST http://localhost:8089/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "securepass123"
  }'
```

### Get Current User

```bash
curl -X GET http://localhost:8089/users/me \
  -H "Authorization: Bearer eyJ..."
```

### Update Profile

```bash
curl -X PUT http://localhost:8089/users/me \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated",
    "bio": "Professional real estate agent"
  }'
```

## User Types

### Seller
- Can post and manage property listings
- Requires email/phone verification
- Optional: company_name, license_number

### Buyer
- Can search and save properties
- Can contact sellers
- Simpler registration process

### Both
- Can both post and search properties

## Security

- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: 1 hour expiration
- **HTTPS Only**: In production
- **Rate Limiting**: 100 requests/minute per IP

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=ree_ai_user
export POSTGRES_PASSWORD=your_password
export POSTGRES_DB=ree_ai
export JWT_SECRET_KEY=your_secret_key

# Run service
python main.py
```

## Running with Docker

```bash
# Build image
docker build -t ree-ai-user-management .

# Run container
docker run -p 8089:8080 \
  -e POSTGRES_HOST=postgres \
  -e JWT_SECRET_KEY=your_secret \
  ree-ai-user-management
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| POSTGRES_HOST | Yes | localhost | PostgreSQL host |
| POSTGRES_PORT | No | 5432 | PostgreSQL port |
| POSTGRES_USER | Yes | - | PostgreSQL user |
| POSTGRES_PASSWORD | Yes | - | PostgreSQL password |
| POSTGRES_DB | Yes | ree_ai | Database name |
| JWT_SECRET_KEY | Yes | - | JWT signing secret |
| JWT_ALGORITHM | No | HS256 | JWT algorithm |

## TODO

- [ ] Email verification flow
- [ ] Password reset functionality
- [ ] OAuth integration (Google, Facebook)
- [ ] Two-factor authentication
- [ ] Seller verification with documents
- [ ] User suspension/ban functionality

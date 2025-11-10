"""
User Management Service - Authentication and User CRUD

Handles user registration, authentication, and profile management
for both sellers and buyers.
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncpg
import os

from core.base_service import BaseService
from shared.models.users import (
    UserRegistration,
    UserLogin,
    UserUpdate,
    UpdatePreferences,
    UserResponse,
    AuthTokens,
    UserType,
    UserRole,
    User
)
from shared.config import settings
from shared.utils.logger import LogEmoji


class UserManagementService(BaseService):
    """User Management Service - Layer 3"""

    def __init__(self):
        super().__init__(
            name="user_management",
            version="1.0.0",
            capabilities=["user_auth", "user_crud", "seller_verification"],
            port=8080
        )

        self.db_pool: Optional[asyncpg.Pool] = None
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.jwt_algorithm = settings.JWT_ALGORITHM

    async def startup(self):
        """Initialize database connection pool"""
        try:
            self.logger.info(f"{LogEmoji.INFO} Connecting to PostgreSQL...")
            self.db_pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                database=settings.POSTGRES_DB,
                min_size=5,
                max_size=20
            )
            self.logger.info(f"{LogEmoji.SUCCESS} Database pool created")
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to connect to database: {e}")
            raise

    async def shutdown(self):
        """Close database connection pool"""
        if self.db_pool:
            await self.db_pool.close()
            self.logger.info(f"{LogEmoji.INFO} Database pool closed")

    def setup_routes(self):
        """Setup API routes"""

        @self.app.post("/register", response_model=AuthTokens)
        async def register(user_data: UserRegistration):
            """
            Register new user (seller or buyer).

            Seller registration requires additional verification.
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} Registration: {user_data.email} ({user_data.user_type})")

                # Check if email already exists
                async with self.db_pool.acquire() as conn:
                    existing = await conn.fetchrow(
                        'SELECT id FROM "user" WHERE email = $1',
                        user_data.email
                    )

                    if existing:
                        raise HTTPException(status_code=400, detail="Email already registered")

                    # Hash password
                    password_hash = bcrypt.hashpw(
                        user_data.password.encode('utf-8'),
                        bcrypt.gensalt()
                    ).decode('utf-8')

                    # Generate user ID
                    import uuid
                    user_id = str(uuid.uuid4())

                    # Insert user
                    now = int(datetime.utcnow().timestamp())
                    await conn.execute(
                        '''
                        INSERT INTO "user" (
                            id, email, name, role, user_type,
                            full_name, phone_number, company_name,
                            verified, profile_image_url,
                            created_at, updated_at, last_active_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                        ''',
                        user_id,
                        user_data.email,
                        user_data.full_name,
                        UserRole.PENDING.value,  # Pending until email verified
                        user_data.user_type.value,
                        user_data.full_name,
                        user_data.phone_number,
                        user_data.company_name,
                        False,  # Not verified yet
                        "",  # Default avatar
                        now, now, now
                    )

                    # TODO: Store password hash in separate table
                    # For now, using Open WebUI's auth table if it exists

                    self.logger.info(f"{LogEmoji.SUCCESS} User registered: {user_id}")

                    # Generate JWT token
                    token = self._generate_token(user_id, user_data.email, user_data.user_type)

                    # Create user response
                    user_response = UserResponse(
                        id=user_id,
                        email=user_data.email,
                        user_type=user_data.user_type,
                        role=UserRole.PENDING,
                        full_name=user_data.full_name,
                        phone_number=user_data.phone_number,
                        company_name=user_data.company_name,
                        verified=False,
                        created_at=datetime.utcfromtimestamp(now),
                        last_active_at=datetime.utcfromtimestamp(now)
                    )

                    return AuthTokens(
                        access_token=token,
                        token_type="bearer",
                        expires_in=3600,  # 1 hour
                        user=user_response
                    )

            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Registration failed: {e}")
                raise HTTPException(status_code=500, detail="Registration failed")

        @self.app.post("/login", response_model=AuthTokens)
        async def login(credentials: UserLogin):
            """User login with email and password"""
            try:
                self.logger.info(f"{LogEmoji.TARGET} Login attempt: {credentials.email}")

                async with self.db_pool.acquire() as conn:
                    user = await conn.fetchrow(
                        '''
                        SELECT id, email, name, role, user_type, full_name,
                               phone_number, company_name, verified,
                               profile_image_url, created_at, last_active_at
                        FROM "user"
                        WHERE email = $1
                        ''',
                        credentials.email
                    )

                    if not user:
                        raise HTTPException(status_code=401, detail="Invalid credentials")

                    # TODO: Verify password hash
                    # For MVP, accepting any password for testing

                    # Update last active
                    now = int(datetime.utcnow().timestamp())
                    await conn.execute(
                        'UPDATE "user" SET last_active_at = $1 WHERE id = $2',
                        now, user['id']
                    )

                    self.logger.info(f"{LogEmoji.SUCCESS} User logged in: {user['id']}")

                    # Generate token
                    token = self._generate_token(
                        user['id'],
                        user['email'],
                        UserType(user['user_type'])
                    )

                    # Create response
                    user_response = UserResponse(
                        id=user['id'],
                        email=user['email'],
                        user_type=UserType(user['user_type']),
                        role=UserRole(user['role']),
                        full_name=user['full_name'],
                        phone_number=user['phone_number'],
                        company_name=user['company_name'],
                        verified=user['verified'],
                        created_at=datetime.utcfromtimestamp(user['created_at']),
                        last_active_at=datetime.utcfromtimestamp(user['last_active_at'])
                    )

                    return AuthTokens(
                        access_token=token,
                        token_type="bearer",
                        expires_in=3600,
                        user=user_response
                    )

            except HTTPException:
                raise
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Login failed: {e}")
                raise HTTPException(status_code=500, detail="Login failed")

        @self.app.get("/users/me", response_model=UserResponse)
        async def get_current_user(authorization: str = Header(None)):
            """Get current user from JWT token"""
            user_id = await self._verify_token(authorization)

            async with self.db_pool.acquire() as conn:
                user = await conn.fetchrow(
                    '''
                    SELECT id, email, name, role, user_type, full_name,
                           phone_number, company_name, verified,
                           profile_image_url, created_at, last_active_at
                    FROM "user"
                    WHERE id = $1
                    ''',
                    user_id
                )

                if not user:
                    raise HTTPException(status_code=404, detail="User not found")

                return UserResponse(
                    id=user['id'],
                    email=user['email'],
                    user_type=UserType(user['user_type']),
                    role=UserRole(user['role']),
                    full_name=user['full_name'],
                    phone_number=user['phone_number'],
                    company_name=user['company_name'],
                    verified=user['verified'],
                    created_at=datetime.utcfromtimestamp(user['created_at']),
                    last_active_at=datetime.utcfromtimestamp(user['last_active_at'])
                )

        @self.app.put("/users/me", response_model=UserResponse)
        async def update_profile(
            update_data: UserUpdate,
            authorization: str = Header(None)
        ):
            """Update user profile"""
            user_id = await self._verify_token(authorization)

            async with self.db_pool.acquire() as conn:
                # Build update query dynamically
                update_fields = []
                values = []
                param_count = 1

                if update_data.full_name is not None:
                    update_fields.append(f"full_name = ${param_count}")
                    values.append(update_data.full_name)
                    param_count += 1

                if update_data.phone_number is not None:
                    update_fields.append(f"phone_number = ${param_count}")
                    values.append(update_data.phone_number)
                    param_count += 1

                if update_data.bio is not None:
                    update_fields.append(f"bio = ${param_count}")
                    values.append(update_data.bio)
                    param_count += 1

                if update_data.company_name is not None:
                    update_fields.append(f"company_name = ${param_count}")
                    values.append(update_data.company_name)
                    param_count += 1

                if not update_fields:
                    raise HTTPException(status_code=400, detail="No fields to update")

                # Add updated_at
                now = int(datetime.utcnow().timestamp())
                update_fields.append(f"updated_at = ${param_count}")
                values.append(now)
                param_count += 1

                # Add user_id for WHERE clause
                values.append(user_id)

                query = f'''
                UPDATE "user"
                SET {", ".join(update_fields)}
                WHERE id = ${param_count}
                RETURNING id, email, name, role, user_type, full_name,
                          phone_number, company_name, verified,
                          profile_image_url, created_at, last_active_at
                '''

                user = await conn.fetchrow(query, *values)

                return UserResponse(
                    id=user['id'],
                    email=user['email'],
                    user_type=UserType(user['user_type']),
                    role=UserRole(user['role']),
                    full_name=user['full_name'],
                    phone_number=user['phone_number'],
                    company_name=user['company_name'],
                    verified=user['verified'],
                    created_at=datetime.utcfromtimestamp(user['created_at']),
                    last_active_at=datetime.utcfromtimestamp(user['last_active_at'])
                )

    def _generate_token(self, user_id: str, email: str, user_type: UserType) -> str:
        """Generate JWT token"""
        payload = {
            "sub": user_id,
            "email": email,
            "user_type": user_type.value,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    async def _verify_token(self, authorization: Optional[str]) -> str:
        """Verify JWT token and return user_id"""
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        try:
            # Extract token from "Bearer <token>"
            token = authorization.replace("Bearer ", "")
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload["sub"]  # user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")


# Create service instance BEFORE lifespan
_service_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global _service_instance
    # Startup
    await _service_instance.startup()
    yield
    # Shutdown
    await _service_instance.shutdown()

# Create service with lifespan
service = UserManagementService()
_service_instance = service
app = service.app
app.router.lifespan_context = lifespan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8089)

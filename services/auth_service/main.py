"""
Authentication Service
- User registration
- Login with JWT tokens
- Token refresh
- Password hashing
- User management
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import jwt, JWTError
import asyncpg

from shared.utils.logger import get_logger
from shared.config import get_settings

# Logger & Settings
logger = get_logger(__name__)
settings = get_settings()

# App
app = FastAPI(
    title="REE AI - Authentication Service",
    description="User authentication and authorization",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database pool
db_pool: Optional[asyncpg.Pool] = None


# ============================================================
# MODELS
# ============================================================

class UserCreate(BaseModel):
    """User registration model"""
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response model"""
    user_id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str
    role: str = "user"


# ============================================================
# DATABASE
# ============================================================

async def init_db():
    """Initialize database connection"""
    global db_pool

    try:
        db_pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            min_size=2,
            max_size=10
        )

        # Create users table if not exists
        async with db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    role VARCHAR(50) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create index on email
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
            """)

        logger.info("✅ Database initialized")

    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {str(e)}")
        raise


async def close_db():
    """Close database connection"""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("✅ Database connection closed")


# ============================================================
# PASSWORD UTILITIES
# ============================================================

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# JWT UTILITIES
# ============================================================

def create_access_token(
    user_id: str,
    email: str,
    role: str = "user",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role", "user")

        if user_id is None or email is None:
            raise credentials_exception

        return TokenData(user_id=user_id, email=email, role=role)

    except JWTError:
        raise credentials_exception


# ============================================================
# USER CRUD
# ============================================================

async def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM users WHERE email = $1",
            email
        )
        return dict(row) if row else None


async def create_user(user_data: UserCreate) -> dict:
    """Create a new user"""
    # Check if user exists
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    password_hash = hash_password(user_data.password)

    # Insert user
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO users (email, password_hash, full_name)
            VALUES ($1, $2, $3)
            RETURNING user_id, email, full_name, role, is_active, created_at
        """, user_data.email, password_hash, user_data.full_name)

        return dict(row)


async def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user with email and password"""
    user = await get_user_by_email(email)
    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    if not user["is_active"]:
        return None

    return user


# ============================================================
# ENDPOINTS
# ============================================================

@app.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        logger.info(f"📝 Registering user: {user_data.email}")

        user = await create_user(user_data)

        logger.info(f"✅ User registered: {user['email']}")

        return UserResponse(
            user_id=str(user["user_id"]),
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Registration failed"
        )


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email and password"""
    try:
        logger.info(f"🔐 Login attempt: {form_data.username}")

        user = await authenticate_user(form_data.username, form_data.password)

        if not user:
            logger.warning(f"⚠️ Invalid credentials: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token = create_access_token(
            user_id=str(user["user_id"]),
            email=user["email"],
            role=user["role"]
        )

        logger.info(f"✅ Login successful: {user['email']}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )


@app.post("/login", response_model=Token)
async def login_json(email: EmailStr, password: str):
    """Login with JSON body (alternative to form)"""
    try:
        logger.info(f"🔐 Login attempt (JSON): {email}")

        user = await authenticate_user(email, password)

        if not user:
            logger.warning(f"⚠️ Invalid credentials: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Create access token
        access_token = create_access_token(
            user_id=str(user["user_id"]),
            email=user["email"],
            role=user["role"]
        )

        logger.info(f"✅ Login successful: {email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )


@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user information"""
    try:
        user = await get_user_by_email(current_user.email)

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return UserResponse(
            user_id=str(user["user_id"]),
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get user info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get user information"
        )


@app.post("/refresh", response_model=Token)
async def refresh_token(current_user: TokenData = Depends(get_current_user)):
    """Refresh access token"""
    try:
        # Create new access token
        access_token = create_access_token(
            user_id=current_user.user_id,
            email=current_user.email,
            role=current_user.role
        )

        logger.info(f"🔄 Token refreshed for: {current_user.email}")

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except Exception as e:
        logger.error(f"❌ Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Token refresh failed"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "healthy" if db_pool else "unavailable"

    return {
        "status": "healthy",
        "service": "auth_service",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }


# ============================================================
# STARTUP & SHUTDOWN
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info("🚀 Auth Service starting...")
    await init_db()
    logger.info("✅ Auth Service ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("👋 Auth Service shutting down...")
    await close_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

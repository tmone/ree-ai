"""Configuration and feature flags for REE AI platform."""
import os
from typing import Optional
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with feature flags."""

    model_config = ConfigDict(
        extra='ignore',
        env_file='.env',
        case_sensitive=True
    )

    # Feature Flags (Mock → Real transition)
    USE_REAL_CORE_GATEWAY: bool = os.getenv("USE_REAL_CORE_GATEWAY", "false").lower() == "true"
    USE_REAL_DB_GATEWAY: bool = os.getenv("USE_REAL_DB_GATEWAY", "false").lower() == "true"

    # Service URLs
    SERVICE_REGISTRY_URL: str = os.getenv("SERVICE_REGISTRY_URL", "http://service-registry:8000")
    CORE_GATEWAY_URL: str = os.getenv("CORE_GATEWAY_URL", "http://core-gateway:8080")
    DB_GATEWAY_URL: str = os.getenv("DB_GATEWAY_URL", "http://db-gateway:8080")

    # Mock Service URLs (for Week 1 development)
    MOCK_CORE_GATEWAY_URL: str = os.getenv("MOCK_CORE_GATEWAY_URL", "http://mock-core-gateway:1080")
    MOCK_DB_GATEWAY_URL: str = os.getenv("MOCK_DB_GATEWAY_URL", "http://mock-db-gateway:1080")

    # LLM Provider Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

    # Database Settings
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ree_ai")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "ree_ai_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "ree_ai_pass_2025")

    # OpenSearch Settings
    OPENSEARCH_HOST: str = os.getenv("OPENSEARCH_HOST", "opensearch")
    OPENSEARCH_PORT: int = int(os.getenv("OPENSEARCH_PORT", "9200"))

    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    # Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")

    # General Settings
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def opensearch_url(self) -> str:
        """Get OpenSearch connection URL."""
        return f"http://{self.OPENSEARCH_HOST}:{self.OPENSEARCH_PORT}"

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    def get_core_gateway_url(self) -> str:
        """Get Core Gateway URL based on feature flag."""
        return self.CORE_GATEWAY_URL if self.USE_REAL_CORE_GATEWAY else self.MOCK_CORE_GATEWAY_URL

    def get_db_gateway_url(self) -> str:
        """Get DB Gateway URL based on feature flag."""
        return self.DB_GATEWAY_URL if self.USE_REAL_DB_GATEWAY else self.MOCK_DB_GATEWAY_URL


# Global settings instance
settings = Settings()

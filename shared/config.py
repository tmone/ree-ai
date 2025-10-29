"""
Shared configuration and feature flags
"""
from pydantic_settings import BaseSettings
from typing import Dict
from enum import Enum


class ServiceMode(str, Enum):
    """Service mode: mock or real"""
    MOCK = "mock"
    REAL = "real"


class Settings(BaseSettings):
    """Application settings"""
    # OpenAI
    OPENAI_API_KEY: str = "sk-dummy-key"

    # Ollama
    OLLAMA_BASE_URL: str = "http://ollama:11434"

    # PostgreSQL
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "ree_ai"
    POSTGRES_USER: str = "ree_ai_user"
    POSTGRES_PASSWORD: str = "ree_ai_pass_2025"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""

    # OpenSearch
    OPENSEARCH_HOST: str = "opensearch"
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USER: str = "admin"
    OPENSEARCH_PASSWORD: str = "Admin@123"

    # Feature Flags
    USE_REAL_CORE_GATEWAY: bool = False
    USE_REAL_DB_GATEWAY: bool = False
    USE_REAL_ORCHESTRATOR: bool = False

    # Service Modes
    SERVICE_SEMANTIC_CHUNKING: ServiceMode = ServiceMode.MOCK
    SERVICE_CLASSIFICATION: ServiceMode = ServiceMode.MOCK
    SERVICE_ATTRIBUTE_EXTRACTION: ServiceMode = ServiceMode.MOCK
    SERVICE_COMPLETENESS: ServiceMode = ServiceMode.MOCK
    SERVICE_PRICE_SUGGESTION: ServiceMode = ServiceMode.MOCK
    SERVICE_RERANK: ServiceMode = ServiceMode.MOCK
    SERVICE_RAG: ServiceMode = ServiceMode.MOCK

    # Development
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # JWT Authentication
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def opensearch_url(self) -> str:
        """Get OpenSearch connection URL"""
        return f"http://{self.OPENSEARCH_USER}:{self.OPENSEARCH_PASSWORD}@{self.OPENSEARCH_HOST}:{self.OPENSEARCH_PORT}"

    def is_service_real(self, service_name: str) -> bool:
        """Check if service is using real implementation"""
        service_mode = getattr(self, f"SERVICE_{service_name.upper()}", ServiceMode.MOCK)
        return service_mode == ServiceMode.REAL


# Global settings instance
settings = Settings()


class FeatureFlags:
    """Feature flags for gradual integration"""

    def __init__(self):
        self.settings = settings

    def use_real_core_gateway(self) -> bool:
        return self.settings.USE_REAL_CORE_GATEWAY

    def use_real_db_gateway(self) -> bool:
        return self.settings.USE_REAL_DB_GATEWAY

    def use_real_orchestrator(self) -> bool:
        return self.settings.USE_REAL_ORCHESTRATOR

    def is_service_real(self, service_name: str) -> bool:
        return self.settings.is_service_real(service_name)

    def get_service_url(self, service_name: str) -> str:
        """Get service URL based on mode (mock or real)"""
        if self.is_service_real(service_name):
            return f"http://{service_name.lower().replace('_', '-')}:8080"
        else:
            return f"http://mock-{service_name.lower().replace('_', '-')}:1080"


# Global feature flags instance
feature_flags = FeatureFlags()

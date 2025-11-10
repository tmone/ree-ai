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
    # SECURITY FIX: No default password - must be provided via environment variable
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")

    # OpenSearch Settings (PRIMARY for property data)
    OPENSEARCH_HOST: str = os.getenv("OPENSEARCH_HOST", "opensearch")
    OPENSEARCH_PORT: int = int(os.getenv("OPENSEARCH_PORT", "9200"))
    # SECURITY FIX: No default credentials - must be provided via environment variable
    OPENSEARCH_USER: Optional[str] = os.getenv("OPENSEARCH_USER", "")
    OPENSEARCH_PASSWORD: Optional[str] = os.getenv("OPENSEARCH_PASSWORD", "")
    OPENSEARCH_PROPERTIES_INDEX: str = os.getenv("OPENSEARCH_PROPERTIES_INDEX", "properties")
    OPENSEARCH_USE_SSL: bool = os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true"
    OPENSEARCH_VERIFY_CERTS: bool = os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true"

    # Redis Settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    # Authentication
    # SECURITY FIX: No default JWT secret - must be provided via environment variable
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")

    # General Settings
    # SECURITY FIX: DEBUG disabled by default for production safety
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # MEDIUM FIX Bug#13: Configurable Embedding Model
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")

    # MEDIUM FIX Bug#14: Configurable Timeout Values (in seconds)
    CLASSIFICATION_TIMEOUT: int = int(os.getenv("CLASSIFICATION_TIMEOUT", "30"))
    EXTRACTION_TIMEOUT: int = int(os.getenv("EXTRACTION_TIMEOUT", "30"))
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))
    HEALTH_CHECK_TIMEOUT: int = int(os.getenv("HEALTH_CHECK_TIMEOUT", "10"))

    # MEDIUM FIX Bug#15: Configurable ReAct Loop Iterations
    MAX_REACT_ITERATIONS: int = int(os.getenv("MAX_REACT_ITERATIONS", "2"))

    # MEDIUM FIX Bug#16: Configurable Vision Models
    OLLAMA_VISION_MODELS: str = os.getenv("OLLAMA_VISION_MODELS", "qwen2-vl,llava,moondream,llama3.2-vision")
    OLLAMA_FALLBACK_VISION: str = os.getenv("OLLAMA_FALLBACK_VISION", "qwen2-vl:7b")

    # MEDIUM FIX Bug#17: Configurable Mock Statistics
    MOCK_PROPERTIES_IN_CITY: int = int(os.getenv("MOCK_PROPERTIES_IN_CITY", "150"))
    MOCK_PROPERTIES_IN_DISTRICT: int = int(os.getenv("MOCK_PROPERTIES_IN_DISTRICT", "50"))

    # MEDIUM FIX Bug#18: Configurable Chunk Similarity Threshold
    CHUNK_SIMILARITY_THRESHOLD: float = float(os.getenv("CHUNK_SIMILARITY_THRESHOLD", "0.75"))

    # HTTP Client Configuration (for shared/utils/http_client.py)
    HTTP_TIMEOUT_DEFAULT: int = int(os.getenv("HTTP_TIMEOUT_DEFAULT", "60"))
    HTTP_TIMEOUT_RAG: int = int(os.getenv("HTTP_TIMEOUT_RAG", "90"))
    HTTP_TIMEOUT_CLASSIFICATION: int = int(os.getenv("HTTP_TIMEOUT_CLASSIFICATION", "30"))
    HTTP_MAX_CONNECTIONS: int = int(os.getenv("HTTP_MAX_CONNECTIONS", "100"))
    HTTP_MAX_KEEPALIVE: int = int(os.getenv("HTTP_MAX_KEEPALIVE", "20"))

    # Query/Search Limits
    CONVERSATION_HISTORY_LIMIT: int = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "10"))
    SEARCH_RESULTS_DEFAULT_LIMIT: int = int(os.getenv("SEARCH_RESULTS_DEFAULT_LIMIT", "5"))
    TOP_SOURCES_LIMIT: int = int(os.getenv("TOP_SOURCES_LIMIT", "3"))

    # Retry Configuration
    RETRY_MAX_ATTEMPTS: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    RETRY_BACKOFF_MULTIPLIER: float = float(os.getenv("RETRY_BACKOFF_MULTIPLIER", "2.0"))

    # Circuit Breaker Configuration
    CIRCUIT_BREAKER_FAIL_MAX: int = int(os.getenv("CIRCUIT_BREAKER_FAIL_MAX", "5"))
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "60"))

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

    def __init__(self, **kwargs):
        """Validate critical security settings on initialization."""
        super().__init__(**kwargs)

        # SECURITY VALIDATION: Ensure critical credentials are provided
        if not self.POSTGRES_PASSWORD:
            raise ValueError(
                "POSTGRES_PASSWORD environment variable is required. "
                "Never use default passwords in production."
            )

        if not self.JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is required. "
                "Generate a secure random key: openssl rand -hex 32"
            )

        # Warn if using empty OpenSearch credentials (for development only)
        if not self.OPENSEARCH_PASSWORD and os.getenv("ENV", "development") == "production":
            raise ValueError(
                "OPENSEARCH_PASSWORD must be set in production environment."
            )


# Global settings instance
settings = Settings()

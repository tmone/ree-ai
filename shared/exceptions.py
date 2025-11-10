"""
Centralized exception handling for REE AI platform

This module provides a hierarchical exception structure for consistent
error handling across all microservices.

Usage:
    from shared.exceptions import ServiceUnavailableError, PropertyNotFoundError

    # Raise domain-specific exceptions
    raise PropertyNotFoundError(property_id="abc123")

    # In FastAPI exception handlers
    @app.exception_handler(REEAIException)
    async def ree_exception_handler(request: Request, exc: REEAIException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        )
"""
from typing import Optional, Dict, Any


class REEAIException(Exception):
    """
    Base exception for REE AI platform

    All custom exceptions should inherit from this class to enable
    centralized error handling and logging.

    Attributes:
        message: Human-readable error message
        error_code: Machine-readable error code (e.g., "PROPERTY_NOT_FOUND")
        status_code: HTTP status code (e.g., 404, 500)
        details: Additional context for debugging
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to JSON-serializable dict for API responses"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }


# ==================== SERVICE-LEVEL EXCEPTIONS ====================

class ServiceUnavailableError(REEAIException):
    """
    Downstream service is unavailable or not responding

    Use when a dependent service (DB Gateway, Core Gateway, etc.) fails to respond
    """

    def __init__(self, service_name: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Service '{service_name}' is currently unavailable",
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details={"service": service_name, **(details or {})}
        )


class ServiceTimeoutError(REEAIException):
    """
    Service request timed out

    Use when a downstream service takes too long to respond
    """

    def __init__(self, service_name: str, timeout_seconds: float, details: Optional[Dict] = None):
        super().__init__(
            message=f"Service '{service_name}' did not respond within {timeout_seconds}s",
            error_code="SERVICE_TIMEOUT",
            status_code=504,
            details={"service": service_name, "timeout": timeout_seconds, **(details or {})}
        )


class CircuitBreakerOpenError(REEAIException):
    """
    Circuit breaker is open (too many failures)

    Use when circuit breaker prevents calls to failing service
    """

    def __init__(self, service_name: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Circuit breaker is open for '{service_name}' (too many recent failures)",
            error_code="CIRCUIT_BREAKER_OPEN",
            status_code=503,
            details={"service": service_name, **(details or {})}
        )


# ==================== DATA/DOMAIN EXCEPTIONS ====================

class PropertyNotFoundError(REEAIException):
    """
    Property not found in database

    Use when querying for a specific property that doesn't exist
    """

    def __init__(self, property_id: str):
        super().__init__(
            message=f"Property with ID '{property_id}' not found",
            error_code="PROPERTY_NOT_FOUND",
            status_code=404,
            details={"property_id": property_id}
        )


class UserNotFoundError(REEAIException):
    """
    User not found in database

    Use when querying for a specific user that doesn't exist
    """

    def __init__(self, user_id: str):
        super().__init__(
            message=f"User with ID '{user_id}' not found",
            error_code="USER_NOT_FOUND",
            status_code=404,
            details={"user_id": user_id}
        )


class ConversationNotFoundError(REEAIException):
    """
    Conversation not found in database

    Use when querying for a specific conversation that doesn't exist
    """

    def __init__(self, conversation_id: str):
        super().__init__(
            message=f"Conversation with ID '{conversation_id}' not found",
            error_code="CONVERSATION_NOT_FOUND",
            status_code=404,
            details={"conversation_id": conversation_id}
        )


# ==================== VALIDATION EXCEPTIONS ====================

class InvalidQueryError(REEAIException):
    """
    Invalid user query

    Use when user input fails validation (too short, malformed, etc.)
    """

    def __init__(self, query: str, reason: str):
        super().__init__(
            message=f"Invalid query: {reason}",
            error_code="INVALID_QUERY",
            status_code=400,
            details={"query": query, "reason": reason}
        )


class InvalidFiltersError(REEAIException):
    """
    Invalid search filters

    Use when search filter parameters are malformed or invalid
    """

    def __init__(self, filters: Dict[str, Any], reason: str):
        super().__init__(
            message=f"Invalid filters: {reason}",
            error_code="INVALID_FILTERS",
            status_code=400,
            details={"filters": filters, "reason": reason}
        )


class MissingRequiredFieldError(REEAIException):
    """
    Required field is missing from request

    Use when mandatory fields are not provided
    """

    def __init__(self, field_name: str, context: Optional[str] = None):
        ctx_msg = f" in {context}" if context else ""
        super().__init__(
            message=f"Required field '{field_name}' is missing{ctx_msg}",
            error_code="MISSING_REQUIRED_FIELD",
            status_code=400,
            details={"field_name": field_name, "context": context}
        )


# ==================== LLM/AI EXCEPTIONS ====================

class LLMGenerationError(REEAIException):
    """
    LLM failed to generate response

    Use when Core Gateway or LLM provider returns an error
    """

    def __init__(self, model: str, reason: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"LLM generation failed for model '{model}': {reason}",
            error_code="LLM_GENERATION_ERROR",
            status_code=500,
            details={"model": model, "reason": reason, **(details or {})}
        )


class ClassificationError(REEAIException):
    """
    Intent classification failed

    Use when Classification service fails to detect intent
    """

    def __init__(self, query: str, reason: str):
        super().__init__(
            message=f"Failed to classify query: {reason}",
            error_code="CLASSIFICATION_ERROR",
            status_code=500,
            details={"query": query, "reason": reason}
        )


class AttributeExtractionError(REEAIException):
    """
    Attribute extraction failed

    Use when Attribute Extraction service fails to parse query
    """

    def __init__(self, query: str, reason: str):
        super().__init__(
            message=f"Failed to extract attributes: {reason}",
            error_code="ATTRIBUTE_EXTRACTION_ERROR",
            status_code=500,
            details={"query": query, "reason": reason}
        )


class RAGPipelineError(REEAIException):
    """
    RAG pipeline failed

    Use when RAG Service encounters an error during retrieval/augmentation/generation
    """

    def __init__(self, stage: str, reason: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"RAG pipeline failed at stage '{stage}': {reason}",
            error_code="RAG_PIPELINE_ERROR",
            status_code=500,
            details={"stage": stage, "reason": reason, **(details or {})}
        )


# ==================== DATABASE EXCEPTIONS ====================

class DatabaseError(REEAIException):
    """
    Database operation failed

    Use when PostgreSQL or OpenSearch operations fail
    """

    def __init__(self, operation: str, reason: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Database operation '{operation}' failed: {reason}",
            error_code="DATABASE_ERROR",
            status_code=500,
            details={"operation": operation, "reason": reason, **(details or {})}
        )


class SearchError(REEAIException):
    """
    Search operation failed

    Use when OpenSearch or vector search fails
    """

    def __init__(self, query: str, reason: str, details: Optional[Dict] = None):
        super().__init__(
            message=f"Search failed: {reason}",
            error_code="SEARCH_ERROR",
            status_code=500,
            details={"query": query, "reason": reason, **(details or {})}
        )


# ==================== AUTHENTICATION/AUTHORIZATION ====================

class AuthenticationError(REEAIException):
    """
    Authentication failed

    Use when JWT validation or credentials are invalid
    """

    def __init__(self, reason: str):
        super().__init__(
            message=f"Authentication failed: {reason}",
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details={"reason": reason}
        )


class AuthorizationError(REEAIException):
    """
    Authorization failed (insufficient permissions)

    Use when user doesn't have permission for requested action
    """

    def __init__(self, user_id: str, action: str):
        super().__init__(
            message=f"User '{user_id}' is not authorized to perform '{action}'",
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details={"user_id": user_id, "action": action}
        )


# ==================== RATE LIMITING ====================

class RateLimitExceededError(REEAIException):
    """
    Rate limit exceeded

    Use when user exceeds API rate limits
    """

    def __init__(self, limit: int, window_seconds: int, details: Optional[Dict] = None):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window_seconds}s",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details={"limit": limit, "window_seconds": window_seconds, **(details or {})}
        )


# ==================== CONFIGURATION ERRORS ====================

class ConfigurationError(REEAIException):
    """
    Service configuration error

    Use when required environment variables or settings are missing/invalid
    """

    def __init__(self, setting_name: str, reason: str):
        super().__init__(
            message=f"Configuration error for '{setting_name}': {reason}",
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details={"setting_name": setting_name, "reason": reason}
        )

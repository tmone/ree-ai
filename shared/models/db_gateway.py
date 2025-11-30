"""Pydantic models for DB Gateway service communication."""
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    """Filters for property search."""
    property_type: Optional[str] = None
    property_types: Optional[List[str]] = None  # Multiple property types (synonyms) for OR search
    listing_type: Optional[str] = None  # "sale" or "rent"
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    bedrooms: Optional[int] = None  # Exact bedrooms count
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[int] = None
    min_area: Optional[float] = None
    max_area: Optional[float] = None
    region: Optional[str] = None  # For Vietnamese real estate (e.g., "Quận 7", "Hà Nội")
    district: Optional[str] = None
    city: Optional[str] = None


class SearchRequest(BaseModel):
    """Request format for vector + BM25 search."""
    query: str = Field(..., description="Search query text")
    filters: Optional[SearchFilters] = Field(None, description="Optional filters")
    limit: int = Field(10, description="Maximum number of results")
    use_vector: bool = Field(True, description="Use vector similarity search")
    use_bm25: bool = Field(True, description="Use BM25 keyword search")
    alpha: float = Field(0.5, description="Weight for vector vs BM25 (0=BM25 only, 1=vector only)")


class PropertyResult(BaseModel):
    """Property search result with flexible OpenSearch types."""
    property_id: str
    title: str
    description: str
    price: Union[str, float, int] = Field(..., description="Price (flexible: can be string '5,77 tỷ' or number)")
    property_type: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Union[str, float, int, None] = Field(None, description="Area (flexible: can be string '95m²' or number)")
    district: Optional[str] = None
    city: Optional[str] = None
    images: Optional[List[str]] = Field(default_factory=list, description="Property image URLs")
    score: float = Field(..., description="Relevance score")
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Response format for search operations."""
    results: List[PropertyResult]
    total: int  # Backward compat
    total_found: int = 0  # Will be populated from total
    execution_time_ms: float = 0.0  # Backward compat
    query_time_ms: float = 0.0  # Will be populated from execution_time_ms

    def __init__(self, **data):
        # Auto-populate for backward compatibility
        if 'total' in data and 'total_found' not in data:
            data['total_found'] = data['total']
        if 'execution_time_ms' in data and 'query_time_ms' not in data:
            data['query_time_ms'] = data['execution_time_ms']
        super().__init__(**data)


class ConversationMessage(BaseModel):
    """Single message in a conversation."""
    message_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class SaveConversationRequest(BaseModel):
    """Request to save a conversation turn."""
    conversation_id: str
    user_id: str
    user_message: str
    assistant_message: str
    metadata: Optional[Dict[str, Any]] = None


class GetConversationRequest(BaseModel):
    """Request to retrieve conversation history."""
    conversation_id: str
    limit: Optional[int] = Field(50, description="Maximum number of messages to retrieve")


class ConversationResponse(BaseModel):
    """Response containing conversation history."""
    conversation_id: str
    messages: List[ConversationMessage]
    total_messages: int


class PropertyDocument(BaseModel):
    """Property document for indexing."""
    property_id: str
    title: str
    description: str
    price: float
    property_type: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    area: Optional[float] = None
    district: Optional[str] = None
    city: Optional[str] = None
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    embedding: Optional[List[float]] = None  # Pre-computed embedding


class IndexDocumentRequest(BaseModel):
    """Request to index a property document."""
    documents: List[PropertyDocument]


class IndexDocumentResponse(BaseModel):
    """Response from document indexing."""
    indexed_count: int
    failed_count: int
    errors: Optional[List[str]] = None

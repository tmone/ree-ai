"""
UI Components Models for Structured Response Format

This module defines the schema for UI components that can be rendered by Open WebUI frontend.
Orchestration Service returns structured data, and frontend decides how to render.
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    """Types of UI components that can be rendered by frontend"""

    # Property-related components
    PROPERTY_LIST = "property-list"  # List/carousel of property cards
    PROPERTY_DETAIL = "property-detail"  # Single property detail modal

    # Future component types
    PROPERTY_COMPARISON = "property-comparison"  # Side-by-side comparison
    MAP_VIEW = "map-view"  # Map with property markers
    PRICE_CHART = "price-chart"  # Price trends chart

    # Generic components
    TEXT = "text"  # Plain text message (fallback)
    ERROR = "error"  # Error message
    LOADING = "loading"  # Loading indicator


class UIComponent(BaseModel):
    """
    A UI component to be rendered by frontend.

    Backend (Orchestration) only provides data and component type.
    Frontend (Open WebUI) decides how to render based on component type.
    """
    type: ComponentType = Field(..., description="Type of component to render")
    data: Dict[str, Any] = Field(..., description="Component-specific data")

    # Optional metadata
    id: Optional[str] = Field(None, description="Unique component ID for interaction")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PropertyListComponent(UIComponent):
    """
    Property list component - displays search results as cards/carousel

    Frontend renders as PropertySearchResults component
    """
    type: ComponentType = ComponentType.PROPERTY_LIST
    data: Dict[str, Any] = Field(
        ...,
        description="Must contain 'properties' (list) and 'total' (int)"
    )

    @classmethod
    def create(cls, properties: List[Dict[str, Any]], total: int, **kwargs):
        """Factory method to create PropertyListComponent"""
        return cls(
            data={
                "properties": properties,
                "total": total
            },
            **kwargs
        )


class PropertyDetailComponent(UIComponent):
    """
    Property detail component - displays single property in modal/popup

    Frontend renders as PropertyDetailModal with PropertyInspector
    """
    type: ComponentType = ComponentType.PROPERTY_DETAIL
    data: Dict[str, Any] = Field(
        ...,
        description="Must contain 'property' (dict)"
    )

    @classmethod
    def create(cls, property_data: Dict[str, Any], **kwargs):
        """Factory method to create PropertyDetailComponent"""
        return cls(
            data={
                "property": property_data
            },
            **kwargs
        )


# Export all
__all__ = [
    'ComponentType',
    'UIComponent',
    'PropertyListComponent',
    'PropertyDetailComponent'
]

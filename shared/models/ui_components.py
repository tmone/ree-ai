"""
UI Components Models for Structured Response Format

This module defines the schema for UI components that can be rendered by Open WebUI frontend.
Follows OpenAI Apps SDK Design Guidelines from Figma.

Component types align with OpenAI Apps SDK:
- Inline Carousel (property-carousel)
- Inspector (property-inspector)
- Full screen modals
- PiP (Picture-in-Picture)
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ComponentType(str, Enum):
    """
    Types of UI components - Following OpenAI Apps SDK Design Guidelines

    Based on Figma: Apps in ChatGPT • Components & Templates
    FileKey: 4JSHQqDBBms4mAvprmbN2b
    """

    # OpenAI Apps SDK Component Types (REE AI specific)
    PROPERTY_CAROUSEL = "property-carousel"  # 🎠 Inline Carousel: List of property cards
    PROPERTY_INSPECTOR = "property-inspector"  # 🔎 Inspector: Single property detail view

    # Future OpenAI Apps SDK components
    PROPERTY_COMPARISON = "property-comparison"  # Side-by-side comparison
    PROPERTY_FULLSCREEN = "property-fullscreen"  # ↕ Full screen browser
    PROPERTY_MAP = "property-map"  # Map with property markers
    PROPERTY_PIP = "property-pip"  # 🔲 PiP: Picture-in-Picture

    # Generic components
    TEXT = "text"  # Plain text message (fallback)
    ERROR = "error"  # Error message
    LOADING = "loading"  # Loading indicator


class UIComponent(BaseModel):
    """
    A UI component to be rendered by frontend.

    Backend (Orchestration) only provides data and component type.
    Frontend (Open WebUI) decides how to render based on component type.

    Follows OpenAI Apps SDK Design Guidelines.
    """
    type: ComponentType = Field(..., description="Type of component to render")
    data: Dict[str, Any] = Field(..., description="Component-specific data")

    # Optional metadata
    id: Optional[str] = Field(None, description="Unique component ID for interaction")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PropertyCarouselComponent(UIComponent):
    """
    Property Carousel Component - OpenAI Apps SDK: 🎠 Inline Carousel

    Displays search results as horizontal carousel of property cards.
    Frontend renders as PropertySearchResults component (uses Carousel).

    Design: Inline display, scrollable, shows 2-3 cards at once
    """
    type: ComponentType = ComponentType.PROPERTY_CAROUSEL
    data: Dict[str, Any] = Field(
        ...,
        description="Must contain 'properties' (list) and 'total' (int)"
    )

    @classmethod
    def create(cls, properties: List[Dict[str, Any]], total: int, **kwargs):
        """Factory method to create PropertyCarouselComponent"""
        return cls(
            data={
                "properties": properties,
                "total": total
            },
            **kwargs
        )


class PropertyInspectorComponent(UIComponent):
    """
    Property Inspector Component - OpenAI Apps SDK: 🔎 Inspector

    Displays single property detail in inspector view (modal/sidebar).
    Frontend renders as PropertyInspector component.

    Design: Full detail view with images, specs, amenities, contact info
    """
    type: ComponentType = ComponentType.PROPERTY_INSPECTOR
    data: Dict[str, Any] = Field(
        ...,
        description="Must contain 'property' (dict) with full property data"
    )

    @classmethod
    def create(cls, property_data: Dict[str, Any], **kwargs):
        """Factory method to create PropertyInspectorComponent"""
        return cls(
            data={
                "property": property_data
            },
            **kwargs
        )


# Backward compatibility aliases
PropertyListComponent = PropertyCarouselComponent  # Legacy name
PropertyDetailComponent = PropertyInspectorComponent  # Legacy name


# Export all
__all__ = [
    'ComponentType',
    'UIComponent',
    'PropertyCarouselComponent',
    'PropertyInspectorComponent',
    # Legacy exports for backward compatibility
    'PropertyListComponent',
    'PropertyDetailComponent'
]

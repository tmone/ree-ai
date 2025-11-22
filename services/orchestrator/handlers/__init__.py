"""
Orchestrator Handlers - Structured Response Pattern

All handlers follow BaseHandler pattern and return Dict[str, Any]:
{
    "message": str,  # Text response for user  
    "components": List[UIComponent]  # UI components to render
}
"""

from services.orchestrator.handlers.search_handler import SearchHandler
from services.orchestrator.handlers.property_detail_handler import PropertyDetailHandler

__all__ = [
    'SearchHandler',
    'PropertyDetailHandler'
]

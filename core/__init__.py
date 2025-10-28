"""
Core Library for REE AI Microservices

This is the foundation library that ALL services use.
Provides:
- BaseService class
- Service Registry
- Common utilities
"""
from .base_service import BaseService
from .service_registry import ServiceRegistry, ServiceInfo, registry

__version__ = "1.0.0"

__all__ = [
    "BaseService",
    "ServiceRegistry",
    "ServiceInfo",
    "registry"
]

"""
REE AI Router
Proxy endpoints for REE AI microservices integration
"""

import logging
import httpx
from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from open_webui.utils.auth import get_verified_user

log = logging.getLogger(__name__)

router = APIRouter()

# REE AI Service URLs (can be configured via environment variables)
ORCHESTRATOR_URL = "http://orchestrator:8080"
DB_GATEWAY_URL = "http://db-gateway:8080"
RAG_SERVICE_URL = "http://rag-service:8080"
CLASSIFICATION_URL = "http://classification:8080"


# ============================================================
# Request/Response Models
# ============================================================

class OrchestratorRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class PropertySearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0


class ClassificationRequest(BaseModel):
    text: str
    options: Optional[Dict[str, Any]] = None


class RAGQueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = 5


# ============================================================
# Orchestrator Endpoints
# ============================================================

@router.post("/orchestrator/query")
async def orchestrator_query(
    request: OrchestratorRequest,
    user=Depends(get_verified_user)
):
    """
    Send query to Orchestrator for AI-powered routing and intent detection
    """
    try:
        # Add user_id from authenticated user if not provided
        if not request.user_id:
            request.user_id = user.id

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ORCHESTRATOR_URL}/query",
                json=request.dict(),
            )
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        log.error(f"Orchestrator timeout for user {user.id}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Orchestrator service timeout"
        )
    except httpx.HTTPStatusError as e:
        log.error(f"Orchestrator error: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Orchestrator error: {e.response.text}"
        )
    except Exception as e:
        log.error(f"Orchestrator unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/orchestrator/health")
async def orchestrator_health(user=Depends(get_verified_user)):
    """
    Check Orchestrator service health
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ORCHESTRATOR_URL}/health")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Orchestrator unavailable: {str(e)}"
        )


# ============================================================
# Storage/Search Endpoints (DB Gateway)
# ============================================================

@router.post("/storage/search")
async def storage_search(
    request: PropertySearchRequest,
    user=Depends(get_verified_user)
):
    """
    Search properties using semantic search and filters
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{DB_GATEWAY_URL}/search",
                json=request.dict(),
            )
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        log.error(f"Storage search timeout for user {user.id}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Storage service timeout"
        )
    except httpx.HTTPStatusError as e:
        log.error(f"Storage error: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Storage error: {e.response.text}"
        )
    except Exception as e:
        log.error(f"Storage unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/storage/properties/{property_id}")
async def get_property_by_id(
    property_id: str,
    user=Depends(get_verified_user)
):
    """
    Get property details by ID
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{DB_GATEWAY_URL}/properties/{property_id}"
            )
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Property not found"
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Storage error: {e.response.text}"
        )
    except Exception as e:
        log.error(f"Get property error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/storage/suggestions")
async def get_property_suggestions(
    user_id: Optional[str] = None,
    limit: int = 5,
    user=Depends(get_verified_user)
):
    """
    Get property suggestions based on user preferences
    """
    try:
        # Use authenticated user if user_id not provided
        target_user_id = user_id or user.id

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{DB_GATEWAY_URL}/suggestions",
                params={"user_id": target_user_id, "limit": limit}
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        log.error(f"Get suggestions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


# ============================================================
# Classification Endpoints
# ============================================================

@router.post("/classification/classify")
async def classify_property(
    request: ClassificationRequest,
    user=Depends(get_verified_user)
):
    """
    Classify property text and extract attributes
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{CLASSIFICATION_URL}/classify",
                json=request.dict(),
            )
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        log.error(f"Classification timeout for user {user.id}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Classification service timeout"
        )
    except httpx.HTTPStatusError as e:
        log.error(f"Classification error: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Classification error: {e.response.text}"
        )
    except Exception as e:
        log.error(f"Classification unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@router.post("/classification/extract")
async def extract_attributes(
    text: str,
    user=Depends(get_verified_user)
):
    """
    Extract attributes from property description
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{CLASSIFICATION_URL}/extract",
                json={"text": text},
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        log.error(f"Extract attributes error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


# ============================================================
# RAG Endpoints
# ============================================================

@router.post("/rag/query")
async def rag_query(
    request: RAGQueryRequest,
    user=Depends(get_verified_user)
):
    """
    Query RAG service for context-aware responses
    """
    try:
        # Add user_id from authenticated user if not provided
        if not request.user_id:
            request.user_id = user.id

        async with httpx.AsyncClient(timeout=60.0) as client:  # RAG may take longer
            response = await client.post(
                f"{RAG_SERVICE_URL}/query",
                json=request.dict(),
            )
            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        log.error(f"RAG query timeout for user {user.id}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="RAG service timeout"
        )
    except httpx.HTTPStatusError as e:
        log.error(f"RAG error: {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"RAG error: {e.response.text}"
        )
    except Exception as e:
        log.error(f"RAG unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


@router.post("/rag/index")
async def index_property(
    property_data: Dict[str, Any],
    user=Depends(get_verified_user)
):
    """
    Index a new property document for RAG
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{RAG_SERVICE_URL}/index",
                json=property_data,
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        log.error(f"RAG index error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error: {str(e)}"
        )


# ============================================================
# Health Check
# ============================================================

@router.get("/health")
async def health_check():
    """
    Check health of all REE AI services
    """
    services = {
        "orchestrator": ORCHESTRATOR_URL,
        "db_gateway": DB_GATEWAY_URL,
        "rag_service": RAG_SERVICE_URL,
        "classification": CLASSIFICATION_URL,
    }

    status_dict = {}

    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in services.items():
            try:
                response = await client.get(f"{service_url}/health")
                status_dict[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code
                }
            except Exception as e:
                status_dict[service_name] = {
                    "status": "unavailable",
                    "error": str(e)
                }

    # Determine overall health
    all_healthy = all(
        s.get("status") == "healthy" for s in status_dict.values()
    )

    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": status_dict
    }

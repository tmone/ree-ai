"""
Orchestrator Service - REFACTORED
Uses Service Registry for dynamic service discovery

NO MORE HARDCODED URLS!
"""
import sys
sys.path.insert(0, '/app')

import httpx
import time
from typing import Optional

from core import BaseService
from shared.models.orchestrator import (
    OrchestrationRequest,
    OrchestrationResponse,
    ServiceType
)


class OrchestratorService(BaseService):
    """
    Orchestrator Service

    Responsibilities:
    - Detect user intent
    - Query Service Registry for available services
    - Route requests to appropriate services
    - Handle service failures
    """

    def __init__(self):
        super().__init__(
            name="orchestrator",
            version="1.0.0",
            capabilities=["orchestration", "routing", "intent_detection"],
            port=8080
        )

        self.registry_url = "http://service-registry:8000"

    def setup_routes(self):
        """Setup orchestration routes"""

        @self.app.post("/orchestrate", response_model=OrchestrationResponse)
        async def orchestrate(request: OrchestrationRequest):
            """
            Main orchestration endpoint

            1. Detect intent (if not specified)
            2. Query Service Registry for available services
            3. Route to appropriate service
            4. Return response
            """
            start_time = time.time()

            try:
                self.logger.info(f"🎯 Orchestration: user={request.user_id}, query='{request.query}'")

                # Step 1: Detect intent
                if request.service_type is None:
                    service_type = await self._detect_intent(request.query)
                    self.logger.info(f"🤖 Detected intent: {service_type}")
                else:
                    service_type = request.service_type

                # Step 2: Get service from registry
                service_url = await self._get_service_url(service_type)

                if not service_url:
                    elapsed_ms = int((time.time() - start_time) * 1000)
                    return OrchestrationResponse(
                        response=f"Service {service_type} is not available",
                        service_used=service_type,
                        metadata={"error": "service_unavailable"},
                        took_ms=elapsed_ms
                    )

                # Step 3: Route to service
                response_text, metadata = await self._call_service(
                    service_type,
                    service_url,
                    request
                )

                elapsed_ms = int((time.time() - start_time) * 1000)
                self.logger.info(f"✅ Orchestration complete: {elapsed_ms}ms")

                return OrchestrationResponse(
                    response=response_text,
                    service_used=service_type,
                    metadata=metadata,
                    took_ms=elapsed_ms
                )

            except Exception as e:
                elapsed_ms = int((time.time() - start_time) * 1000)
                self.logger.error(f"❌ Error: {str(e)} ({elapsed_ms}ms)")
                raise

    async def _detect_intent(self, query: str) -> ServiceType:
        """Detect user intent from query"""
        query_lower = query.lower()

        # Simple keyword-based detection
        if any(kw in query_lower for kw in ["tìm", "search", "có", "list"]):
            return ServiceType.SEARCH

        if any(kw in query_lower for kw in ["giá", "price", "bao nhiêu"]):
            return ServiceType.PRICE_SUGGESTION

        if any(kw in query_lower for kw in ["loại", "classify", "phân loại"]):
            return ServiceType.CLASSIFICATION

        # Default: RAG for complex queries
        return ServiceType.RAG

    async def _get_service_url(self, service_type: ServiceType) -> Optional[str]:
        """
        Get service URL from Service Registry

        This is the KEY difference from hardcoded approach!
        """
        try:
            # Map service type to capability
            capability_map = {
                ServiceType.SEMANTIC_CHUNKING: "chunking",
                ServiceType.CLASSIFICATION: "classification",
                ServiceType.RAG: "rag",
                ServiceType.SEARCH: "search"
            }

            capability = capability_map.get(service_type)

            if not capability:
                self.logger.warning(f"No capability mapping for {service_type}")
                return None

            # Query Service Registry
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.registry_url}/services",
                    params={"capability": capability, "status": "healthy"}
                )

                if response.status_code == 200:
                    data = response.json()
                    services = data.get("services", [])

                    if services:
                        # Use first available service
                        service = services[0]
                        service_url = service["url"]
                        self.logger.info(f"📍 Found service: {service['name']} at {service_url}")
                        return service_url
                    else:
                        self.logger.warning(f"⚠️ No services available for capability: {capability}")
                        return None

        except Exception as e:
            self.logger.error(f"❌ Error querying Service Registry: {e}")
            return None

    async def _call_service(
        self,
        service_type: ServiceType,
        service_url: str,
        request: OrchestrationRequest
    ) -> tuple[str, dict]:
        """Call the actual service"""

        # Different service types have different endpoints
        endpoint_map = {
            ServiceType.SEARCH: "/search",
            ServiceType.RAG: "/rag",
            ServiceType.CLASSIFICATION: "/classify",
            ServiceType.SEMANTIC_CHUNKING: "/chunk"
        }

        endpoint = endpoint_map.get(service_type, "/")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Build request based on service type
                if service_type == ServiceType.SEARCH:
                    payload = {
                        "query": request.query,
                        "filters": {},
                        "limit": 10
                    }
                elif service_type == ServiceType.RAG:
                    payload = {
                        "query": request.query,
                        "user_id": request.user_id,
                        "conversation_id": request.conversation_id or "default"
                    }
                else:
                    payload = {"query": request.query}

                response = await client.post(
                    f"{service_url}{endpoint}",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                # Extract response based on service type
                if service_type == ServiceType.SEARCH:
                    results = data.get("results", [])
                    response_text = f"Tìm thấy {len(results)} bất động sản:\n\n"
                    for i, prop in enumerate(results[:5], 1):
                        response_text += f"{i}. {prop['title']} - {prop['price']:,.0f} VNĐ\n"
                    metadata = {"properties_count": len(results)}

                elif service_type == ServiceType.RAG:
                    response_text = data.get("answer", "")
                    metadata = data.get("metadata", {})

                else:
                    response_text = str(data)
                    metadata = {}

                return response_text, metadata

        except Exception as e:
            self.logger.error(f"❌ Error calling service: {e}")
            return f"Error calling {service_type}: {str(e)}", {"error": str(e)}


if __name__ == "__main__":
    service = OrchestratorService()
    service.run()

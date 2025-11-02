"""
AI Test Agent Service

This service simulates real users using AI (Ollama) to generate test queries
and conversations. It provides multiple user personas with realistic behaviors.

Port: 8095
"""

import sys
import os
from typing import List, Dict, Optional
from fastapi import HTTPException
import httpx

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.base_service import BaseService
from pydantic import BaseModel

from personas import PersonaType, get_persona, get_all_personas, get_persona_names
from query_generator import QueryGenerator, GeneratedQuery, get_fallback_query


class GenerateQueryRequest(BaseModel):
    """Request to generate a single query"""
    persona_type: PersonaType
    intent: str
    context: Optional[str] = None


class GenerateQueriesRequest(BaseModel):
    """Request to generate multiple queries"""
    persona_type: PersonaType
    intent: str
    count: int = 10
    context: Optional[str] = None


class GenerateConversationRequest(BaseModel):
    """Request to generate a multi-turn conversation"""
    persona_type: PersonaType
    turns: int = 5


class SimulateSessionRequest(BaseModel):
    """Request to simulate a full user session"""
    persona_type: PersonaType
    duration_minutes: int = 10  # How long session should last
    query_interval_seconds: int = 30  # Time between queries


class AITestAgentService(BaseService):
    """AI Test Agent Service - Simulates real users for testing"""

    def __init__(self):
        super().__init__(
            name="ai_test_agent",
            version="1.0.0",
            capabilities=["query_generation", "persona_simulation", "conversation_generation"],
            port=8080  # Internal port, mapped to 8095 externally
        )

        # Initialize query generator
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        self.query_generator = QueryGenerator(ollama_base_url=ollama_url)

        # Track active sessions
        self.active_sessions = {}

    def setup_routes(self):
        """Setup API routes"""

        @self.app.get("/personas")
        async def list_personas():
            """List all available personas"""
            personas = get_all_personas()
            return {
                "personas": [
                    {
                        "type": p.type,
                        "name": p.name,
                        "description": p.description,
                        "knowledge_level": p.knowledge_level,
                        "typical_queries": p.typical_queries[:3]  # Show 3 examples
                    }
                    for p in personas.values()
                ]
            }

        @self.app.get("/personas/{persona_type}")
        async def get_persona_details(persona_type: PersonaType):
            """Get detailed information about a persona"""
            try:
                persona = get_persona(persona_type)
                return {
                    "persona": persona.dict()
                }
            except KeyError:
                raise HTTPException(status_code=404, detail=f"Persona {persona_type} not found")

        @self.app.post("/generate-query")
        async def generate_query(request: GenerateQueryRequest) -> Dict:
            """
            Generate a single query for a persona and intent

            Example:
            ```
            POST /generate-query
            {
                "persona_type": "first_time_buyer",
                "intent": "search",
                "context": null
            }
            ```

            Returns:
            ```
            {
                "query": "Tìm căn hộ 2 phòng ngủ giá dưới 3 tỷ Quận 7",
                "persona_type": "first_time_buyer",
                "intent": "search",
                "expected_entities": {
                    "bedrooms": 2,
                    "price_max": 3000000000,
                    "location": "quận 7",
                    "property_type": "apartment"
                },
                "difficulty": "medium",
                "tags": ["search", "beginner", "price"]
            }
            ```
            """
            self.logger.info(f"🎭 Generating query for {request.persona_type} - {request.intent}")

            try:
                # Try Ollama first
                query = await self.query_generator.generate_query(
                    persona_type=request.persona_type,
                    intent=request.intent,
                    context=request.context
                )
                self.logger.info(f"✅ Generated query: {query.query}")
                return {"query": query.dict()}

            except Exception as e:
                self.logger.warning(f"⚠️ Ollama unavailable, using fallback: {e}")
                # Fallback to template
                fallback_query = get_fallback_query(request.persona_type, request.intent)
                return {
                    "query": {
                        "query": fallback_query,
                        "persona_type": request.persona_type,
                        "intent": request.intent,
                        "expected_entities": {},
                        "difficulty": "medium",
                        "tags": [request.intent, "fallback"],
                        "fallback": True
                    }
                }

        @self.app.post("/generate-queries")
        async def generate_queries(request: GenerateQueriesRequest) -> Dict:
            """
            Generate multiple queries for a persona and intent

            Example:
            ```
            POST /generate-queries
            {
                "persona_type": "experienced_investor",
                "intent": "investment_advice",
                "count": 5
            }
            ```

            Returns list of 5 generated queries
            """
            self.logger.info(f"🎭 Generating {request.count} queries for {request.persona_type} - {request.intent}")

            try:
                queries = await self.query_generator.generate_queries(
                    persona_type=request.persona_type,
                    intent=request.intent,
                    count=request.count,
                    context=request.context
                )
                self.logger.info(f"✅ Generated {len(queries)} queries")
                return {
                    "queries": [q.dict() for q in queries],
                    "count": len(queries)
                }

            except Exception as e:
                self.logger.error(f"❌ Failed to generate queries: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/generate-conversation")
        async def generate_conversation(request: GenerateConversationRequest) -> Dict:
            """
            Generate a multi-turn conversation

            Example:
            ```
            POST /generate-conversation
            {
                "persona_type": "first_time_buyer",
                "turns": 5
            }
            ```

            Returns conversation with 5 turns (search → clarification → compare → price → decision)
            """
            self.logger.info(f"🎭 Generating {request.turns}-turn conversation for {request.persona_type}")

            try:
                conversation = await self.query_generator.generate_conversation(
                    persona_type=request.persona_type,
                    turns=request.turns
                )
                self.logger.info(f"✅ Generated conversation with {len(conversation)} turns")
                return {
                    "conversation": [q.dict() for q in conversation],
                    "turns": len(conversation),
                    "persona_type": request.persona_type
                }

            except Exception as e:
                self.logger.error(f"❌ Failed to generate conversation: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/simulate-user-session")
        async def simulate_user_session(request: SimulateSessionRequest) -> Dict:
            """
            Simulate a full user session with realistic timing

            This endpoint starts a background session that generates queries
            at specified intervals, simulating a real user browsing the site.

            Example:
            ```
            POST /simulate-user-session
            {
                "persona_type": "young_professional",
                "duration_minutes": 10,
                "query_interval_seconds": 30
            }
            ```

            Returns session_id to track the simulation
            """
            self.logger.info(f"🎭 Starting user session simulation for {request.persona_type}")

            import uuid
            session_id = str(uuid.uuid4())

            # Store session info
            self.active_sessions[session_id] = {
                "persona_type": request.persona_type,
                "duration_minutes": request.duration_minutes,
                "query_interval_seconds": request.query_interval_seconds,
                "status": "running",
                "queries_generated": 0,
                "start_time": None  # Will be set when background task starts
            }

            # TODO: Implement background task for continuous query generation
            # For now, just return session info

            return {
                "session_id": session_id,
                "status": "running",
                "persona_type": request.persona_type,
                "message": "Session simulation started (background task not yet implemented)"
            }

        @self.app.get("/sessions/{session_id}")
        async def get_session_status(session_id: str) -> Dict:
            """Get status of a simulated session"""
            if session_id not in self.active_sessions:
                raise HTTPException(status_code=404, detail="Session not found")

            return {"session": self.active_sessions[session_id]}

        @self.app.get("/test-ollama")
        async def test_ollama_connection():
            """Test connection to Ollama"""
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{self.query_generator.ollama_base_url}/api/tags")
                    response.raise_for_status()
                    models = response.json()
                    return {
                        "status": "connected",
                        "ollama_url": self.query_generator.ollama_base_url,
                        "models": models
                    }
            except Exception as e:
                return {
                    "status": "disconnected",
                    "ollama_url": self.query_generator.ollama_base_url,
                    "error": str(e),
                    "fallback_mode": "Templates will be used instead"
                }


if __name__ == "__main__":
    service = AITestAgentService()
    service.run()

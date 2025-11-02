"""
Query Generator using Ollama

This module uses Ollama LLM to generate realistic Vietnamese queries
based on user personas and scenarios.
"""

import httpx
import random
from typing import List, Dict, Optional
from pydantic import BaseModel

from personas import Persona, PersonaType, get_persona


class QueryGenerationRequest(BaseModel):
    """Request for query generation"""
    persona_type: PersonaType
    intent: str  # search, compare, price_analysis, investment_advice, etc.
    context: Optional[str] = None
    count: int = 1


class GeneratedQuery(BaseModel):
    """Generated query with metadata"""
    query: str
    persona_type: PersonaType
    intent: str
    expected_entities: Dict[str, any]
    difficulty: str  # "easy", "medium", "hard"
    tags: List[str]


class QueryGenerator:
    """Generate test queries using Ollama"""

    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.ollama_base_url = ollama_base_url
        self.model = "llama2"

    async def generate_query(
        self,
        persona_type: PersonaType,
        intent: str,
        context: Optional[str] = None
    ) -> GeneratedQuery:
        """Generate a single query for a persona and intent"""

        persona = get_persona(persona_type)

        # Build prompt for Ollama
        prompt = self._build_prompt(persona, intent, context)

        # Call Ollama
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,  # More creative
                        "top_p": 0.9
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            generated_text = result["response"]

        # Parse generated query
        query = self._parse_generated_query(generated_text)

        # Extract expected entities based on persona and query
        expected_entities = self._extract_expected_entities(query, persona, intent)

        # Determine difficulty
        difficulty = self._determine_difficulty(query, intent)

        # Generate tags
        tags = self._generate_tags(query, persona, intent)

        return GeneratedQuery(
            query=query,
            persona_type=persona_type,
            intent=intent,
            expected_entities=expected_entities,
            difficulty=difficulty,
            tags=tags
        )

    async def generate_queries(
        self,
        persona_type: PersonaType,
        intent: str,
        count: int = 10,
        context: Optional[str] = None
    ) -> List[GeneratedQuery]:
        """Generate multiple queries"""
        queries = []
        for _ in range(count):
            query = await self.generate_query(persona_type, intent, context)
            queries.append(query)
        return queries

    async def generate_conversation(
        self,
        persona_type: PersonaType,
        turns: int = 5
    ) -> List[GeneratedQuery]:
        """Generate a multi-turn conversation"""
        conversation = []
        context = ""

        # Define conversation flow for typical property search
        intents_flow = ["search", "clarification", "compare", "price_analysis", "decision"]

        for turn in range(min(turns, len(intents_flow))):
            intent = intents_flow[turn]
            query = await self.generate_query(persona_type, intent, context)
            conversation.append(query)
            context += f"\nUser: {query.query}"

        return conversation

    def _build_prompt(self, persona: Persona, intent: str, context: Optional[str]) -> str:
        """Build prompt for Ollama"""

        # Intent-specific instructions
        intent_instructions = {
            "search": "Generate a Vietnamese query asking to search for properties. Include specific requirements like location, price, number of bedrooms, or features.",
            "compare": "Generate a Vietnamese query asking to compare 2 or more properties. Reference specific property features or ask for comparison criteria.",
            "price_analysis": "Generate a Vietnamese query asking about property prices, market value, or price trends.",
            "investment_advice": "Generate a Vietnamese query asking for investment advice, ROI, or market potential.",
            "location_insights": "Generate a Vietnamese query asking about a specific area, neighborhood, or location benefits.",
            "legal_guidance": "Generate a Vietnamese query asking about legal aspects, documents, or regulations.",
            "chat": "Generate a Vietnamese conversational query or greeting.",
            "clarification": "Generate a Vietnamese follow-up question asking for more details or clarification."
        }

        prompt = f"""You are a Vietnamese real estate customer with the following profile:

**Persona**: {persona.name}
**Description**: {persona.description}
**Knowledge Level**: {persona.knowledge_level}
**Language Style**: {persona.language_style}
**Budget**: {persona.budget_range['min']:,} - {persona.budget_range['max']:,} VND
**Typical Interests**: {', '.join(persona.preferences['keywords'])}

**Task**: {intent_instructions.get(intent, "Generate a Vietnamese query related to real estate.")}

**Requirements**:
1. Write ONLY in Vietnamese (tiếng Việt)
2. Use {persona.language_style} language style
3. Keep query natural and realistic (like a real person would ask)
4. Include specific details relevant to this persona
5. Query length: 1-2 sentences

**Example queries from this persona**:
{chr(10).join([f"- {q}" for q in random.sample(persona.typical_queries, min(3, len(persona.typical_queries)))])}
"""

        if context:
            prompt += f"\n**Conversation Context**:\n{context}\n"

        prompt += "\n**Generate ONE query now** (Vietnamese only, no explanations):"

        return prompt

    def _parse_generated_query(self, generated_text: str) -> str:
        """Parse and clean generated query from Ollama response"""
        # Remove common prefixes
        query = generated_text.strip()
        prefixes = ["Query:", "Câu hỏi:", "User:", "Customer:", "-", "*"]
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()

        # Take first line only
        query = query.split("\n")[0].strip()

        # Remove quotes if present
        if query.startswith('"') and query.endswith('"'):
            query = query[1:-1]
        if query.startswith("'") and query.endswith("'"):
            query = query[1:-1]

        return query

    def _extract_expected_entities(self, query: str, persona: Persona, intent: str) -> Dict[str, any]:
        """Extract expected entities from query"""
        entities = {}
        query_lower = query.lower()

        # Location extraction
        districts = [
            "quận 1", "quận 2", "quận 3", "quận 4", "quận 5", "quận 6", "quận 7",
            "quận 8", "quận 9", "quận 10", "quận 11", "quận 12",
            "bình thạnh", "tân bình", "phú nhuận", "gò vấp",
            "thủ đức", "bình tân", "tân phú", "nhà bè", "bình chánh"
        ]
        for district in districts:
            if district in query_lower:
                entities["location"] = district
                break

        # Bedroom extraction
        bedroom_patterns = [
            ("1 phòng ngủ", 1), ("1 pn", 1), ("1pn", 1),
            ("2 phòng ngủ", 2), ("2 pn", 2), ("2pn", 2),
            ("3 phòng ngủ", 3), ("3 pn", 3), ("3pn", 3),
            ("4 phòng ngủ", 4), ("4 pn", 4), ("4pn", 4),
            ("studio", 0)
        ]
        for pattern, bedroom_count in bedroom_patterns:
            if pattern in query_lower:
                entities["bedrooms"] = bedroom_count
                break

        # Price extraction (basic patterns)
        if "dưới" in query_lower or "duoi" in query_lower:
            if "tỷ" in query_lower or "ty" in query_lower:
                # Extract number before tỷ
                import re
                match = re.search(r"(\d+)\s*(tỷ|ty)", query_lower)
                if match:
                    entities["price_max"] = int(match.group(1)) * 1_000_000_000

        # Property type
        if "căn hộ" in query_lower or "chung cư" in query_lower:
            entities["property_type"] = "apartment"
        elif "nhà phố" in query_lower:
            entities["property_type"] = "house"
        elif "biệt thự" in query_lower:
            entities["property_type"] = "villa"
        elif "đất" in query_lower:
            entities["property_type"] = "land"

        return entities

    def _determine_difficulty(self, query: str, intent: str) -> str:
        """Determine query difficulty level"""
        query_lower = query.lower()

        # Complex intents are harder
        complex_intents = ["compare", "investment_advice", "price_analysis"]
        if intent in complex_intents:
            return "hard"

        # Multiple requirements = harder
        requirement_keywords = ["và", "hoặc", "gần", "có", "không có"]
        requirement_count = sum(1 for kw in requirement_keywords if kw in query_lower)
        if requirement_count >= 3:
            return "hard"
        elif requirement_count >= 1:
            return "medium"

        return "easy"

    def _generate_tags(self, query: str, persona: Persona, intent: str) -> List[str]:
        """Generate tags for query"""
        tags = [intent, persona.knowledge_level]

        query_lower = query.lower()

        # Add feature tags
        if any(kw in query_lower for kw in ["gym", "hồ bơi", "pool"]):
            tags.append("amenities")
        if any(kw in query_lower for kw in ["trường", "school"]):
            tags.append("education")
        if any(kw in query_lower for kw in ["metro", "mrt", "giao thông"]):
            tags.append("transport")
        if any(kw in query_lower for kw in ["đầu tư", "roi", "lợi nhuận"]):
            tags.append("investment")
        if any(kw in query_lower for kw in ["pháp lý", "legal", "giấy tờ"]):
            tags.append("legal")

        return tags


# Fallback query templates for when Ollama is unavailable
FALLBACK_TEMPLATES = {
    "search": {
        PersonaType.FIRST_TIME_BUYER: [
            "Tìm căn hộ giá rẻ {location}",
            "Có căn hộ {bedrooms} phòng ngủ dưới {price} tỷ không?",
            "Căn hộ giá bao nhiêu ở {location}?"
        ],
        PersonaType.EXPERIENCED_INVESTOR: [
            "Tìm căn hộ có tiềm năng đầu tư {location}",
            "Dự án nào ở {location} có ROI tốt?",
            "Phân tích thị trường bất động sản {location}"
        ],
        PersonaType.YOUNG_PROFESSIONAL: [
            "Tìm căn hộ gần metro {location}",
            "Chung cư hiện đại có gym {location}",
            "Studio apartment {location} giá bao nhiêu?"
        ],
        PersonaType.FAMILY_BUYER: [
            "Tìm nhà {bedrooms} phòng ngủ gần trường {location}",
            "Khu nào an toàn cho trẻ em {location}?",
            "Chung cư có sân chơi trẻ em {location}"
        ],
        PersonaType.REAL_ESTATE_AGENT: [
            "Thông tin chi tiết dự án {location}",
            "Mức giá trung bình căn hộ {bedrooms}PN {location}",
            "Danh sách căn hộ chủ đầu tư bán {location}"
        ]
    }
}


def get_fallback_query(persona_type: PersonaType, intent: str) -> str:
    """Get a fallback query when Ollama is unavailable"""
    templates = FALLBACK_TEMPLATES.get(intent, {}).get(persona_type, [])
    if not templates:
        return "Tìm căn hộ 2 phòng ngủ Quận 7"

    template = random.choice(templates)

    # Fill in placeholders
    locations = ["Quận 7", "Quận 2", "Thủ Đức", "Bình Thạnh"]
    bedrooms = random.choice([1, 2, 3])
    price = random.choice([2, 3, 4, 5])

    query = template.format(
        location=random.choice(locations),
        bedrooms=bedrooms,
        price=price
    )

    return query

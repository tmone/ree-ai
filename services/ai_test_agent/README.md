# AI Test Agent Service

## Overview

AI Test Agent Service simulates real users using AI (Ollama) to generate realistic test queries and conversations. It provides multiple user personas with different characteristics, knowledge levels, and behaviors.

**Port**: 8095 (external) / 8080 (internal)

## Features

- **5 User Personas**: First-time buyer, Experienced investor, Young professional, Family buyer, Real estate agent
- **AI-Powered Query Generation**: Uses Ollama to generate natural Vietnamese queries
- **Multi-Turn Conversations**: Simulate realistic property search conversations
- **Fallback Templates**: Works even when Ollama is unavailable
- **Entity Extraction**: Automatically extracts expected entities from queries

## User Personas

### 1. First-Time Buyer (first_time_buyer)
- **Knowledge**: Beginner
- **Language**: Simple
- **Budget**: 1-3 billion VND
- **Typical Queries**: "Tìm căn hộ giá rẻ", "Mua nhà cần giấy tờ gì?"

### 2. Experienced Investor (experienced_investor)
- **Knowledge**: Expert
- **Language**: Professional
- **Budget**: 10-50 billion VND
- **Typical Queries**: "Phân tích tiềm năng đầu tư khu vực Thủ Thiêm", "So sánh ROI giữa Quận 2 và Quận 7"

### 3. Young Professional (young_professional)
- **Knowledge**: Intermediate
- **Language**: Moderate
- **Budget**: 2-5 billion VND
- **Typical Queries**: "Tìm căn hộ gần metro Quận 2", "Chung cư có gym và hồ bơi"

### 4. Family Buyer (family_buyer)
- **Knowledge**: Intermediate
- **Language**: Moderate
- **Budget**: 4-8 billion VND
- **Typical Queries**: "Tìm nhà 3 phòng ngủ gần trường quốc tế", "Khu nào an toàn cho trẻ em?"

### 5. Real Estate Agent (real_estate_agent)
- **Knowledge**: Expert
- **Language**: Professional
- **Budget**: No limit
- **Typical Queries**: "So sánh 3 căn hộ này theo diện tích và giá", "Thông tin chi tiết về dự án Vinhomes Grand Park"

## API Endpoints

### List Personas
```bash
GET http://localhost:8095/personas
```

Returns list of all available personas with examples.

### Get Persona Details
```bash
GET http://localhost:8095/personas/{persona_type}
```

Returns detailed information about a specific persona.

### Generate Single Query
```bash
POST http://localhost:8095/generate-query
Content-Type: application/json

{
  "persona_type": "first_time_buyer",
  "intent": "search",
  "context": null
}
```

Returns:
```json
{
  "query": {
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
    "tags": ["search", "beginner"]
  }
}
```

### Generate Multiple Queries
```bash
POST http://localhost:8095/generate-queries
Content-Type: application/json

{
  "persona_type": "experienced_investor",
  "intent": "investment_advice",
  "count": 5
}
```

Returns list of 5 generated queries.

### Generate Conversation
```bash
POST http://localhost:8095/generate-conversation
Content-Type: application/json

{
  "persona_type": "first_time_buyer",
  "turns": 5
}
```

Returns multi-turn conversation with 5 turns (search → clarification → compare → price → decision).

### Test Ollama Connection
```bash
GET http://localhost:8095/test-ollama
```

Returns Ollama connection status and available models.

## Available Intents

- `search`: Search for properties
- `compare`: Compare multiple properties
- `price_analysis`: Ask about prices or market value
- `investment_advice`: Ask for investment advice
- `location_insights`: Ask about specific locations
- `legal_guidance`: Ask about legal aspects
- `chat`: General conversation
- `clarification`: Follow-up questions

## Environment Variables

- `OLLAMA_BASE_URL`: Ollama API URL (default: `http://host.docker.internal:11434`)
- `DEBUG`: Enable debug mode (default: `true`)
- `LOG_LEVEL`: Logging level (default: `INFO`)
- `SERVICE_REGISTRY_URL`: Service Registry URL (default: `http://service-registry:8000`)

## Usage Examples

### Example 1: Generate Search Queries for Testing

```python
import httpx
import asyncio

async def generate_test_queries():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8095/generate-queries",
            json={
                "persona_type": "first_time_buyer",
                "intent": "search",
                "count": 10
            }
        )
        queries = response.json()["queries"]

        for q in queries:
            print(f"Query: {q['query']}")
            print(f"Expected entities: {q['expected_entities']}")
            print(f"Difficulty: {q['difficulty']}")
            print()

asyncio.run(generate_test_queries())
```

### Example 2: Simulate Conversation Flow

```python
import httpx
import asyncio

async def simulate_conversation():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8095/generate-conversation",
            json={
                "persona_type": "young_professional",
                "turns": 5
            }
        )
        conversation = response.json()["conversation"]

        for i, turn in enumerate(conversation, 1):
            print(f"Turn {i} ({turn['intent']}): {turn['query']}")

asyncio.run(simulate_conversation())
```

### Example 3: Test All Personas

```python
import httpx
import asyncio

async def test_all_personas():
    async with httpx.AsyncClient() as client:
        # Get all personas
        response = await client.get("http://localhost:8095/personas")
        personas = response.json()["personas"]

        for persona in personas:
            print(f"\n=== {persona['name']} ===")

            # Generate query for this persona
            response = await client.post(
                "http://localhost:8095/generate-query",
                json={
                    "persona_type": persona["type"],
                    "intent": "search"
                }
            )
            query = response.json()["query"]
            print(f"Generated: {query['query']}")

asyncio.run(test_all_personas())
```

## Fallback Mode

If Ollama is unavailable, the service automatically falls back to using predefined query templates. This ensures the service remains functional even without AI generation.

## Testing

```bash
# Test Ollama connection
curl http://localhost:8095/test-ollama

# List personas
curl http://localhost:8095/personas

# Generate a query
curl -X POST http://localhost:8095/generate-query \
  -H "Content-Type: application/json" \
  -d '{"persona_type": "first_time_buyer", "intent": "search"}'

# Health check
curl http://localhost:8095/health
```

## Integration with Test System

This service is designed to be integrated with:

1. **Test Orchestrator Service**: Coordinate test execution
2. **Response Evaluator Service**: Evaluate system responses
3. **Learning Service**: Track failures and patterns

## Future Enhancements

- [ ] Background session simulation
- [ ] Real-time query streaming
- [ ] Multi-language support (English + Vietnamese)
- [ ] Custom persona creation
- [ ] Query variation generation (paraphrasing)
- [ ] Adversarial query generation
- [ ] Voice query simulation

## Dependencies

- `fastapi`: Web framework
- `httpx`: HTTP client for Ollama
- `pydantic`: Data validation
- Python 3.11+

## Architecture

```
┌─────────────────────────────────────────┐
│       AI Test Agent Service             │
│            (Port 8095)                  │
└─────────────────────────────────────────┘
                  │
                  ├─→ Personas Module
                  │   (5 user personas)
                  │
                  ├─→ Query Generator
                  │   ├─ Ollama Integration
                  │   └─ Fallback Templates
                  │
                  └─→ BaseService
                      └─ Service Registry
```

## Related Documentation

- Main System: `/docs/AI_AUTOMATION_TEST_SYSTEM.md`
- Personas: `personas.py`
- Query Generator: `query_generator.py`

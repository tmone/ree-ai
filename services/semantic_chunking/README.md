# Semantic Chunking Service - Sample Implementation

This is a **sample Layer 3 service** showing best practices for implementing REE AI services.

## 📋 What This Service Does

Breaks text into semantic chunks using LLM. For example:

**Input:**
```
Căn hộ 2 phòng ngủ ở Quận 1, diện tích 75m2, giá 8 tỷ. Nội thất cao cấp, view đẹp.
```

**Output:**
```json
{
  "chunks": [
    {"index": 0, "content": "Căn hộ 2 phòng ngủ ở Quận 1", "token_count": 15},
    {"index": 1, "content": "diện tích 75m2, giá 8 tỷ", "token_count": 12},
    {"index": 2, "content": "Nội thất cao cấp, view đẹp", "token_count": 10}
  ],
  "total_chunks": 3,
  "processing_time_ms": 350
}
```

## 🏗️ Architecture Patterns

### 1. Use Shared Models

```python
# ✅ CORRECT: Import from shared/models
from shared.models.core_gateway import LLMRequest, LLMResponse, Message

# ❌ WRONG: Define your own models
class MyLLMRequest(BaseModel):  # Don't do this!
    ...
```

### 2. Core Gateway Client

```python
class CoreGatewayClient:
    def __init__(self):
        # Use feature flags to switch mock/real
        if feature_flags.use_real_core_gateway():
            self.base_url = "http://core-gateway:8080"
        else:
            self.base_url = "http://mock-core-gateway:1080"

    async def call_llm(self, request: LLMRequest) -> LLMResponse:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=request.dict()
            )
            return LLMResponse(**response.json())
```

### 3. Error Handling

```python
try:
    # Call Core Gateway
    response = await core_gateway.call_llm(request)
except httpx.HTTPStatusError as e:
    # Gateway is down or returned error
    raise HTTPException(status_code=502, detail="Gateway error")
except Exception as e:
    # Service logic error
    raise HTTPException(status_code=500, detail=str(e))
```

### 4. Logging

```python
from shared.utils.logger import setup_logger

logger = setup_logger(__name__)

# Use emoji for easy scanning
logger.info("🚀 Service starting...")
logger.info("📝 Request received...")
logger.info("✅ Success!")
logger.error("❌ Error occurred")
```

## 🚀 How to Implement Your Service

### Step 1: Copy This Template

```bash
cp -r services/semantic_chunking services/your_service_name
```

### Step 2: Update Files

1. **main.py**: Implement your service logic
2. **requirements.txt**: Add service-specific dependencies
3. **Dockerfile**: Usually no changes needed
4. **README.md**: Document what your service does

### Step 3: Define Your Models

```python
# your_service_name/main.py

class YourServiceRequest(BaseModel):
    """Request for your service"""
    input_data: str
    # ... your fields

class YourServiceResponse(BaseModel):
    """Response from your service"""
    output_data: str
    # ... your fields
```

### Step 4: Implement Endpoint

```python
@app.post("/your-endpoint", response_model=YourServiceResponse)
async def your_endpoint(request: YourServiceRequest):
    start_time = time.time()

    try:
        logger.info(f"📝 Request: {request.input_data}")

        # Call Core Gateway if needed
        llm_response = await core_gateway.call_llm(...)

        # Your service logic here
        result = process_data(llm_response.content)

        elapsed_ms = int((time.time() - start_time) * 1000)
        logger.info(f"✅ Success: {elapsed_ms}ms")

        return YourServiceResponse(...)

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 5: Add to Docker Compose

```yaml
# docker-compose.yml
services:
  your-service-name:
    build:
      context: .
      dockerfile: services/your_service_name/Dockerfile
    environment:
      - USE_REAL_CORE_GATEWAY=${USE_REAL_CORE_GATEWAY}
    depends_on:
      - core-gateway
    ports:
      - "8083:8080"  # Choose unused port
```

### Step 6: Test

```bash
# Start services
docker-compose up your-service-name

# Test endpoint
curl -X POST http://localhost:8083/your-endpoint \
  -H "Content-Type: application/json" \
  -d '{"input_data": "test"}'
```

## 📚 Best Practices

### Do's ✅

1. **Use shared models** - Import from `shared/models`
2. **Handle errors properly** - Return appropriate HTTP codes
3. **Log everything** - Use emoji for easy scanning
4. **Use feature flags** - Support mock/real mode
5. **Write tests** - Unit + integration tests
6. **Document API** - Use FastAPI's OpenAPI docs

### Don'ts ❌

1. **Don't hardcode URLs** - Use feature flags
2. **Don't create duplicate models** - Use shared models
3. **Don't skip error handling** - Always use try/except
4. **Don't forget logging** - Log request/response
5. **Don't block** - Use async/await
6. **Don't skip health checks** - Implement `/health` endpoint

## 🧪 Testing

### Unit Test Example

```python
# tests/test_semantic_chunking.py
import pytest
from httpx import AsyncClient
from services.semantic_chunking.main import app

@pytest.mark.asyncio
async def test_chunk_text():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/chunk", json={
            "text": "Test text to chunk",
            "max_chunk_size": 500
        })
        assert response.status_code == 200
        data = response.json()
        assert "chunks" in data
        assert data["total_chunks"] > 0
```

### Integration Test

```bash
# Start mock Core Gateway first
docker-compose up mock-core-gateway

# Test with curl
curl -X POST http://localhost:8082/chunk \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Căn hộ 2 phòng ngủ ở Quận 1, giá 8 tỷ",
    "max_chunk_size": 500
  }'
```

## 🔧 Troubleshooting

### Issue: "Core Gateway connection refused"

**Solution:**
```bash
# Check Core Gateway is running
docker ps | grep core-gateway

# Check feature flag
echo $USE_REAL_CORE_GATEWAY  # Should be true or false

# Check network
docker network ls
```

### Issue: "Import error: No module named 'shared'"

**Solution:**
```bash
# Check PYTHONPATH in Dockerfile
ENV PYTHONPATH=/app

# Ensure shared/ is copied
COPY shared /app/shared
```

### Issue: "Validation error on request"

**Solution:**
```python
# Check your request matches the model
# Use FastAPI's /docs to see expected format
# Example: http://localhost:8082/docs
```

## 📝 Summary

This sample service demonstrates:

- ✅ Using shared models
- ✅ Calling Core Gateway
- ✅ Error handling
- ✅ Logging
- ✅ Feature flags
- ✅ FastAPI best practices

**Use this as a template for all Layer 3 services!**

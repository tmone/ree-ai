# LM Studio Failover Configuration

## Overview

REE AI Core Gateway đã được cấu hình để tự động failover từ OpenAI sang LM Studio khi gặp rate limit hoặc quota errors.

## Failover Chain

```
OpenAI API
    ↓ (on 429 / rate limit / quota error)
LM Studio (Local)
    ↓ (on connection error)
Ollama (Final fallback)
```

## Configuration

### 1. Setup LM Studio

1. **Cài đặt LM Studio:**
   - Download từ: https://lmstudio.ai/
   - Install và launch application

2. **Load Model:**
   - Chọn model (VD: Llama 2, Mistral, etc.)
   - Click "Load Model"

3. **Start Server:**
   - Go to "Local Server" tab
   - Click "Start Server"
   - Default endpoint: `http://localhost:1234`
   - Note: Nếu chạy trên máy khác, dùng IP: `http://192.168.1.19:1234`

### 2. Configure REE AI

Edit `.env` file:

```bash
# LM Studio Settings (local failover)
LMSTUDIO_BASE_URL=http://192.168.1.19:1234  # Your LM Studio IP
LMSTUDIO_MODEL=local-model                   # Model name in LM Studio
```

### 3. Update docker-compose.test.yml

Add environment variable:

```yaml
core-gateway:
  environment:
    - LMSTUDIO_BASE_URL=${LMSTUDIO_BASE_URL}
    - LMSTUDIO_MODEL=${LMSTUDIO_MODEL}
```

### 4. Restart Service

```bash
# Rebuild image
docker build -t ree-ai-core-gateway -f services/core_gateway/Dockerfile .

# Restart service
docker-compose -f docker-compose.test.yml restart core-gateway
```

## Testing Failover

### Manual Test

```bash
# This will trigger OpenAI rate limit and failover to LM Studio
curl -X POST http://localhost:8080/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 50
  }'
```

### Check Logs

```bash
# Watch for failover messages
docker logs -f ree-ai-core-gateway | grep -i "failover\|lm studio"
```

Expected log output when failover works:
```
⚠️ OpenAI rate limit/quota exceeded, failing over to LM Studio
✅ Using LM Studio (failover)
✅ LLM request completed: model=gpt-4o-mini, time=1234ms
```

## Implementation Details

### Code Location

File: `services/core_gateway/main.py`

### Failover Logic

```python
try:
    # Try OpenAI first
    response = await self._call_openai(request)
except HTTPStatusError as error:
    if error.response.status_code == 429:
        # Failover to LM Studio
        response = await self._call_lmstudio(request)
```

### Error Detection

The failover is triggered on:
- HTTP Status Code 429 (Too Many Requests)
- Error messages containing "rate_limit"
- Error messages containing "quota"

## Troubleshooting

### LM Studio Not Responding

**Problem:** Failover to LM Studio fails with connection error

**Solutions:**
1. Check LM Studio server is running:
   ```bash
   curl http://192.168.1.19:1234/v1/models
   ```

2. Check firewall allows connections

3. Verify IP address in `.env` is correct

4. Check LM Studio logs for errors

### Model Not Found

**Problem:** LM Studio returns "model not found" error

**Solution:**
1. Check loaded model name in LM Studio
2. Update `LMSTUDIO_MODEL` in `.env` to match
3. Restart Core Gateway

### Slow Response

**Problem:** LM Studio responses are very slow

**Solutions:**
1. Use smaller model (faster inference)
2. Enable GPU acceleration in LM Studio
3. Adjust max_tokens to lower value
4. Check CPU/RAM usage

## Performance Comparison

| Provider | Avg Response Time | Cost | Availability |
|----------|-------------------|------|--------------|
| OpenAI API | 500-1000ms | $$ | High (with quota) |
| LM Studio | 2000-5000ms | Free | 100% (local) |
| Ollama | 3000-8000ms | Free | 100% (local) |

## Best Practices

### 1. Development Setup
- Use LM Studio as primary (free, no quota)
- OpenAI as backup for better quality

### 2. Production Setup
- Use OpenAI as primary (faster, better quality)
- LM Studio as failover (avoid quota issues)
- Ollama as final fallback

### 3. Cost Optimization
- Set lower max_tokens for OpenAI calls
- Cache responses when possible
- Use LM Studio for development/testing

## Advanced Configuration

### Custom Failover Order

Edit `services/core_gateway/main.py`:

```python
# Change failover priority
1. Try LM Studio first (free)
2. Failover to OpenAI (quality)
3. Final fallback to Ollama (always available)
```

### Retry Logic

Add retry before failover:

```python
for attempt in range(3):
    try:
        return await self._call_openai(request)
    except HTTPStatusError as e:
        if e.response.status_code == 429 and attempt < 2:
            await asyncio.sleep(1)  # Wait 1 second
            continue
        # Failover to LM Studio
```

### Health Checks

Add LM Studio health check:

```python
async def check_lmstudio_health():
    try:
        response = await http_client.get(
            f"{settings.LMSTUDIO_BASE_URL}/v1/models"
        )
        return response.status_code == 200
    except:
        return False
```

## Network Configuration

### Docker Network Access

If LM Studio runs on host machine:

```yaml
core-gateway:
  extra_hosts:
    - "host.docker.internal:host-gateway"
  environment:
    - LMSTUDIO_BASE_URL=http://host.docker.internal:1234
```

### Kubernetes Setup

```yaml
env:
  - name: LMSTUDIO_BASE_URL
    value: "http://lmstudio-service.default.svc.cluster.local:1234"
```

## Monitoring

### Metrics to Track

1. **Failover Rate:**
   - How often failover happens
   - Success rate of each provider

2. **Response Times:**
   - Compare OpenAI vs LM Studio
   - Identify slow models

3. **Error Rates:**
   - Track 429 errors from OpenAI
   - Connection errors to LM Studio

### Logging

Current implementation logs:
- ✅ Provider used (OpenAI/LM Studio/Ollama)
- ⚠️ Failover events
- ❌ Errors and failures
- ⏱️ Execution time

## FAQ

**Q: Can I use LM Studio as primary provider?**
A: Yes! Just change model to start with "lmstudio/" or modify routing logic.

**Q: Does failover work with streaming?**
A: Not yet. Currently only supports non-streaming requests.

**Q: Can I add more fallback providers?**
A: Yes! Add new methods like `_call_anthropic()` and update failover chain.

**Q: How to disable failover?**
A: Set `LMSTUDIO_BASE_URL=""` in .env to skip LM Studio.

## Next Steps

1. ✅ LM Studio failover implemented
2. 🚧 Add caching to reduce API calls
3. 🚧 Add request queuing for rate limiting
4. 🚧 Add automatic retry with exponential backoff
5. 🚧 Add health checks for all providers

---

**Last Updated:** 2025-10-31
**Status:** Implemented, Needs Testing
**Related Files:**
- `services/core_gateway/main.py`
- `shared/config.py`
- `.env`

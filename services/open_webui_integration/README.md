# Open WebUI Integration with REE AI

## Overview

Open WebUI cần được tích hợp với Orchestrator qua **Functions** (như MCP servers).

## Integration Strategy

### Option 1: Open WebUI Functions (Recommended)

Open WebUI hỗ trợ custom functions để extend functionality.

```python
# open_webui_functions/ree_ai.py
"""
title: REE AI Property Search
author: REE AI Team
version: 1.0.0
"""

from pydantic import BaseModel, Field
import requests


class Filter:
    class Valves(BaseModel):
        orchestrator_url: str = Field(
            default="http://orchestrator:8080",
            description="Orchestrator service URL"
        )

    def __init__(self):
        self.valves = self.Valves()

    def inlet(self, body: dict, user: dict) -> dict:
        """
        Intercept user messages and route to REE AI Orchestrator
        """
        messages = body.get("messages", [])
        if not messages:
            return body

        last_message = messages[-1]
        user_query = last_message.get("content", "")

        # Check if this is a real estate query
        keywords = ["nhà", "căn hộ", "apartment", "tìm", "search", "giá"]
        if any(kw in user_query.lower() for kw in keywords):
            # Call Orchestrator
            try:
                response = requests.post(
                    f"{self.valves.orchestrator_url}/orchestrate",
                    json={
                        "user_id": user.get("id", "anonymous"),
                        "conversation_id": body.get("chat_id", "default"),
                        "query": user_query
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    # Replace message with orchestrator response
                    last_message["content"] = data.get("response", user_query)

            except Exception as e:
                print(f"Orchestrator error: {e}")

        return body
```

### Option 2: Direct Ollama Proxy (Current Setup)

Open WebUI hiện đang kết nối trực tiếp với Ollama:

```yaml
open-webui:
  image: ghcr.io/open-webui/open-webui:main
  environment:
    - OLLAMA_BASE_URL=http://ollama:11434
```

**Vấn đề:** Bỏ qua Orchestrator và các AI services của chúng ta!

## Recommended Architecture

```
┌─────────────────────────────────────────┐
│  User Browser                            │
│  http://localhost:3000                   │
└────────────────┬────────────────────────┘
                 ↓
┌─────────────────────────────────────────┐
│  Open WebUI                              │
│  • Chat interface                        │
│  • User authentication                   │
│  • ✅ Custom Function installed          │
└────────────────┬────────────────────────┘
                 ↓
         [Function detects]
         [real estate query]
                 ↓
┌─────────────────────────────────────────┐
│  Orchestrator (Our System)               │
│  http://orchestrator:8080                │
│  • Intent detection                      │
│  • Route to AI services                  │
└────────────────┬────────────────────────┘
                 ↓
         [RAG, Classification, etc.]
```

## How to Install Function

1. **Access Open WebUI Admin:**
   ```
   http://localhost:3000/admin/functions
   ```

2. **Create New Function:**
   - Click "+ Add Function"
   - Paste `ree_ai.py` content
   - Save & Enable

3. **Configure Valves:**
   - Set `orchestrator_url: http://orchestrator:8080`

4. **Test:**
   - Chat: "Tìm nhà 2 phòng ngủ ở Quận 1"
   - Should call Orchestrator → RAG → Return results

## Alternative: Custom Open WebUI Fork

For deeper integration, fork Open WebUI and modify:

```python
# backend/apps/webui/routers/chats.py

@router.post("/completions")
async def chat_completions(request: CompletionRequest):
    # Instead of calling Ollama directly
    # Call our Orchestrator
    response = await orchestrator_client.post(
        "/orchestrate",
        json={
            "user_id": request.user_id,
            "query": request.messages[-1]["content"]
        }
    )
    return response.json()
```

## Current Status

❌ Open WebUI calls Ollama directly (bypasses our system)
✅ Open WebUI running at http://localhost:3000
⏳ Need to install custom function to integrate with Orchestrator

## Next Steps

1. Install Function (Option 1) - Quick
2. OR Fork Open WebUI (Option 2) - Better control
3. Test end-to-end: User → Open WebUI → Orchestrator → RAG → Response

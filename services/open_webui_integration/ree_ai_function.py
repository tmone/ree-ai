"""
title: REE AI Property Search & Assistant
author: REE AI Team
version: 1.0.0
required_open_webui_version: 0.3.0
"""

from pydantic import BaseModel, Field
from typing import Optional
import requests
import json


class Filter:
    class Valves(BaseModel):
        orchestrator_url: str = Field(
            default="http://orchestrator:8080",
            description="REE AI Orchestrator service URL"
        )
        priority: int = Field(
            default=0,
            description="Priority level (0-10). Higher = earlier execution"
        )
        enable_debug: bool = Field(
            default=True,
            description="Enable debug logging"
        )

    def __init__(self):
        self.valves = self.Valves()

    def _is_real_estate_query(self, query: str) -> bool:
        """Check if query is related to real estate"""
        keywords = [
            # Vietnamese
            "nhà", "căn hộ", "chung cư", "biệt thự", "đất",
            "phòng ngủ", "mua", "bán", "thuê", "giá",
            "quận", "district", "tìm", "có",
            # English
            "apartment", "house", "property", "real estate",
            "bedroom", "buy", "sell", "rent", "price",
            "search", "find"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in keywords)

    def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process incoming messages and route real estate queries to REE AI Orchestrator

        This function intercepts user messages before they reach Ollama.
        If the query is about real estate, it routes to our Orchestrator.
        """
        if self.valves.enable_debug:
            print(f"[REE AI] Inlet called with body: {json.dumps(body, indent=2)}")

        messages = body.get("messages", [])
        if not messages:
            return body

        # Get last user message
        last_message = messages[-1]
        if last_message.get("role") != "user":
            return body

        user_query = last_message.get("content", "")

        if self.valves.enable_debug:
            print(f"[REE AI] User query: {user_query}")

        # Check if this is a real estate query
        if not self._is_real_estate_query(user_query):
            if self.valves.enable_debug:
                print(f"[REE AI] Not a real estate query, passing through to Ollama")
            return body

        # Real estate query detected - call Orchestrator
        if self.valves.enable_debug:
            print(f"[REE AI] Real estate query detected! Calling Orchestrator...")

        try:
            response = requests.post(
                f"{self.valves.orchestrator_url}/orchestrate",
                json={
                    "user_id": user.get("id", "anonymous") if user else "anonymous",
                    "conversation_id": body.get("chat_id", "default"),
                    "query": user_query,
                    "context": {
                        "source": "open_webui",
                        "model": body.get("model", "unknown")
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                orchestrator_response = data.get("response", "")

                if self.valves.enable_debug:
                    print(f"[REE AI] Orchestrator response: {orchestrator_response[:100]}...")

                # Replace user message with a system message containing the response
                # This makes Open WebUI display the Orchestrator response
                body["messages"] = [
                    {
                        "role": "system",
                        "content": f"REE AI Orchestrator đã xử lý câu hỏi: '{user_query}'\n\nKết quả:\n{orchestrator_response}"
                    },
                    {
                        "role": "user",
                        "content": "Hãy trình bày lại thông tin trên một cách tự nhiên và thân thiện."
                    }
                ]

                if self.valves.enable_debug:
                    print(f"[REE AI] Modified body to inject Orchestrator response")

            else:
                if self.valves.enable_debug:
                    print(f"[REE AI] Orchestrator error: {response.status_code}")
                # Fallback to normal flow
                last_message["content"] = f"[REE AI] Lỗi kết nối với Orchestrator (status {response.status_code}). Đang xử lý với Ollama...\n\n{user_query}"

        except Exception as e:
            if self.valves.enable_debug:
                print(f"[REE AI] Exception calling Orchestrator: {str(e)}")
            # Fallback to normal flow
            last_message["content"] = f"[REE AI] Lỗi: {str(e)}. Đang xử lý với Ollama...\n\n{user_query}"

        return body

    def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Process outgoing responses (after LLM generation)
        Can be used to post-process or enhance responses
        """
        if self.valves.enable_debug:
            print(f"[REE AI] Outlet called")

        # Currently just pass through
        return body


# For testing outside Open WebUI
if __name__ == "__main__":
    filter = Filter()

    test_body = {
        "messages": [
            {"role": "user", "content": "Tìm nhà 2 phòng ngủ ở Quận 1"}
        ],
        "chat_id": "test_123"
    }

    test_user = {"id": "test_user"}

    result = filter.inlet(test_body, test_user)
    print(json.dumps(result, indent=2, ensure_ascii=False))

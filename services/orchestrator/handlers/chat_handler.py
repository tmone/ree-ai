"""
Chat Handler - Conversational Chat Flow

Handles CHAT intent:
1. Build conversation context with history
2. Call Core Gateway (LLM) for conversational response
3. Support multimodal (vision) for image analysis
"""
import time
from typing import Dict, Any, List, Optional
from services.orchestrator.handlers.base_handler import BaseHandler
from shared.utils.logger import LogEmoji
from shared.utils.i18n import t


class ChatHandler(BaseHandler):
    """
    Handles conversational chat requests

    Flow:
    1. Build conversation context from history
    2. Detect if multimodal (vision) is needed
    3. Call Core Gateway (LLM) with appropriate model
    4. Return AI-generated conversational response
    """

    async def handle(
        self,
        request_id: str,
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
        files: Optional[List] = None
    ) -> str:
        """
        Execute chat flow

        Args:
            request_id: Request ID for tracing
            query: User chat message
            history: Conversation history (for context)
            files: Attached files (for vision analysis)

        Returns:
            Natural language conversational response
        """
        start_time = time.time()
        self.log_handler_start(request_id, "ChatHandler", query)

        # STEP 1: Build conversation context
        messages = self._build_messages(query, history, files)

        # STEP 2: Detect if vision model is needed
        has_images = files and any(f.get("mime_type", "").startswith("image/") for f in files)
        model = "gpt-4o" if has_images else "gpt-4o-mini"  # Use vision model for images

        if has_images:
            self.logger.info(
                f"{LogEmoji.AI} [{request_id}] Using vision model ({model}) for {len(files)} image(s)"
            )

        # STEP 3: Call Core Gateway (LLM)
        self.logger.info(f"{LogEmoji.AI} [{request_id}] Calling Core Gateway (model: {model})...")

        try:
            llm_result = await self.call_service(
                "core_gateway",
                "/chat/completions",
                json_data={
                    "model": model,
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=60.0
            )

            response_text = llm_result.get("content", "")

            duration_ms = (time.time() - start_time) * 1000
            self.logger.info(
                f"{LogEmoji.SUCCESS} [{request_id}] LLM generated {len(response_text)} chars"
            )
            self.log_handler_complete(request_id, "ChatHandler", duration_ms)

            return response_text

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} [{request_id}] Core Gateway failed: {e}")
            duration_ms = (time.time() - start_time) * 1000
            self.log_handler_complete(request_id, "ChatHandler", duration_ms)

            # Fallback response
            return t('chat.service_unavailable', language='vi')

    def _build_messages(
        self,
        query: str,
        history: Optional[List[Dict[str, Any]]],
        files: Optional[List]
    ) -> List[Dict[str, Any]]:
        """
        Build LLM messages with conversation history and files

        Args:
            query: Current user query
            history: Previous conversation messages
            files: Attached files (for vision)

        Returns:
            List of messages in OpenAI format
        """
        messages = [
            {
                "role": "system",
                "content": t('chat.system_prompt', language='vi')
            }
        ]

        # Add conversation history (last 10 messages for context)
        if history:
            for msg in history[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        # Add current query (with files if multimodal)
        if files:
            # Multimodal message with images
            content_parts = [{"type": "text", "text": query}]

            for file in files:
                if file.get("mime_type", "").startswith("image/"):
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{file['mime_type']};base64,{file.get('base64_data', '')}"
                        }
                    })

            messages.append({"role": "user", "content": content_parts})
        else:
            # Text-only message
            messages.append({"role": "user", "content": query})

        return messages

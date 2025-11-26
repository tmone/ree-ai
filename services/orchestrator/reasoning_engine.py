"""
ReAct Reasoning Engine - Phase 3
Implements full Reasoning + Action + Observation loop
Inspired by Codex's proactive information gathering
"""
import httpx
from typing import Dict, Any, Optional, List
from shared.models.reasoning import (
    ReasoningChain,
    ThinkingStage,
    KnowledgeExpansion,
    AmbiguityDetectionResult
)
from shared.utils.logger import LogEmoji
from shared.utils.i18n import t
import logging


class ReasoningEngine:
    """
    ReAct loop implementation:
    1. Thought (analyze query)
    2. Action (call tools/services)
    3. Observation (process results)
    4. Repeat until conclusion
    """

    def __init__(
        self,
        core_gateway_url: str,
        rag_service_url: str,
        db_gateway_url: str,
        http_client: httpx.AsyncClient,
        logger: logging.Logger
    ):
        self.core_gateway_url = core_gateway_url
        self.rag_service_url = rag_service_url
        self.db_gateway_url = db_gateway_url
        self.http_client = http_client
        self.logger = logger

    async def execute_react_loop(
        self,
        query: str,
        intent: str,
        history: List[Dict],
        knowledge_expansion: Optional[KnowledgeExpansion],
        ambiguity_result: Optional[AmbiguityDetectionResult],
        files: Optional[List] = None
    ) -> ReasoningChain:
        """
        Main ReAct loop execution
        """
        # Initialize reasoning chain
        chain = ReasoningChain(
            query=query,
            steps=[],
            knowledge_expansion=knowledge_expansion,
            ambiguity_check=ambiguity_result,
            overall_confidence=1.0
        )

        # FIX BUG #1 & #2: Validate input for empty or whitespace-only queries
        if not query or not query.strip():
            chain.add_thought(
                stage=ThinkingStage.QUERY_ANALYSIS,
                thought="Empty or whitespace-only query detected - cannot proceed with search",
                data={
                    "validation_error": "Query is empty or contains only whitespace",
                    "query_length": len(query) if query else 0,
                    "stripped_length": len(query.strip()) if query else 0
                },
                confidence=0.0
            )
            chain.final_conclusion = "Xin vui lòng cung cấp câu hỏi tìm kiếm bất động sản. (Please provide a property search query.)"
            chain.overall_confidence = 0.0
            return chain

        # Step 1: Initial Query Analysis
        chain.add_thought(
            stage=ThinkingStage.QUERY_ANALYSIS,
            thought=f"Analyzing query: '{query}' | Detected intent: {intent}",
            data={
                "query": query,
                "intent": intent,
                "has_files": files is not None and len(files) > 0,
                "history_count": len(history)
            },
            confidence=0.9
        )

        # Step 2: Context Gathering
        context_data = await self._gather_context(history)
        chain.add_thought(
            stage=ThinkingStage.CONTEXT_GATHERING,
            thought=f"Retrieved {len(history)} messages from conversation history",
            data=context_data,
            confidence=1.0
        )

        # Step 3: Knowledge Expansion Analysis
        if knowledge_expansion and knowledge_expansion.expanded_terms:
            chain.add_thought(
                stage=ThinkingStage.KNOWLEDGE_EXPANSION,
                thought=f"Query expanded with domain knowledge: {knowledge_expansion.reasoning}",
                data={
                    "original": knowledge_expansion.original_query,
                    "expanded_terms": knowledge_expansion.expanded_terms,
                    "filters": knowledge_expansion.filters
                },
                confidence=0.85
            )

        # Step 4: Ambiguity Check
        if ambiguity_result and ambiguity_result.has_ambiguity:
            chain.add_thought(
                stage=ThinkingStage.AMBIGUITY_DETECTION,
                thought=f"Detected {len(ambiguity_result.clarifications)} ambiguities in query",
                data={
                    "clarifications_needed": [c.question for c in ambiguity_result.clarifications],
                    "confidence": ambiguity_result.confidence
                },
                confidence=ambiguity_result.confidence
            )

            # If critical ambiguity, suggest clarification
            if ambiguity_result.confidence < 0.5:
                chain.add_thought(
                    stage=ThinkingStage.CONCLUSION,
                    thought="Query too ambiguous. Requesting clarification from user.",
                    confidence=0.3
                )
                chain.overall_confidence = 0.3
                return chain

        # Step 5: Tool Selection & Execution
        if intent == "search":
            await self._execute_search_path(chain, query, knowledge_expansion, files)
        else:
            await self._execute_chat_path(chain, query, history, files)

        # Final conclusion
        chain.add_thought(
            stage=ThinkingStage.CONCLUSION,
            thought="ReAct loop completed. Final response synthesized.",
            confidence=chain.overall_confidence
        )

        return chain

    async def _gather_context(self, history: List[Dict]) -> Dict[str, Any]:
        """Gather and analyze conversation context"""
        if not history:
            return {"has_history": False}

        # Analyze history for patterns
        user_messages = [msg for msg in history if msg.get("role") == "user"]
        assistant_messages = [msg for msg in history if msg.get("role") == "assistant"]

        return {
            "has_history": True,
            "total_messages": len(history),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "conversation_depth": len(user_messages)
        }

    async def _execute_search_path(
        self,
        chain: ReasoningChain,
        query: str,
        knowledge_expansion: Optional[KnowledgeExpansion],
        files: Optional[List]
    ):
        """
        Execute search path with progressive narrowing
        """
        # Thought: Planning search strategy
        chain.add_thought(
            stage=ThinkingStage.TOOL_SELECTION,
            thought="Query requires property search. Routing to RAG service with hybrid search.",
            data={"target_service": "rag_service", "strategy": "hybrid_search"},
            confidence=0.9
        )

        # Action: Call RAG service
        try:
            # Build search filters from knowledge expansion
            filters = knowledge_expansion.filters if knowledge_expansion else {}

            action_id = chain.add_action(
                tool_name="rag_service.query",
                arguments={
                    "query": query,
                    "filters": filters,
                    "limit": 10
                },
                reason="Use RAG for semantic + keyword search with domain filters"
            )

            # Execute the action
            self.logger.info(f"{LogEmoji.AI} Calling RAG service with filters: {filters}")

            response = await self.http_client.post(
                f"{self.rag_service_url}/query",
                json={
                    "query": query,
                    "filters": filters,
                    "limit": 10,
                    "response_format": "components"  # Simple msg + JSON for frontend
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()

                # Observation
                chain.add_observation(
                    tool_call_id=action_id,
                    result=result,
                    success=True,
                    insight=f"Found {result.get('retrieved_count', 0)} properties with confidence {result.get('confidence', 0):.2f}"
                )

                chain.overall_confidence = min(chain.overall_confidence, result.get('confidence', 0.8))

            else:
                # Failed observation
                chain.add_observation(
                    tool_call_id=action_id,
                    result={"error": f"HTTP {response.status_code}"},
                    success=False,
                    insight=f"RAG service call failed with status {response.status_code}"
                )
                chain.overall_confidence = 0.5

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} RAG service error: {e}")
            chain.add_observation(
                tool_call_id=action_id,
                result={"error": str(e)},
                success=False,
                insight=f"RAG service unavailable: {str(e)}"
            )
            chain.overall_confidence = 0.3

    async def _execute_chat_path(
        self,
        chain: ReasoningChain,
        query: str,
        history: List[Dict],
        files: Optional[List]
    ):
        """
        Execute conversational chat path
        """
        # Thought: Planning chat strategy
        chain.add_thought(
            stage=ThinkingStage.TOOL_SELECTION,
            thought="Query is conversational. Using LLM with conversation history.",
            data={
                "target_service": "core_gateway",
                "model": "gpt-4o-mini",
                "context_messages": len(history)
            },
            confidence=0.95
        )

        # Action: Call LLM
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": t('chat.system_prompt_advisor', language='vi')
                }
            ]

            # Add history
            for msg in history[-5:]:  # Last 5 messages for context
                messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content", "")
                })

            # Add current query
            messages.append({"role": "user", "content": query})

            action_id = chain.add_action(
                tool_name="core_gateway.chat",
                arguments={
                    "model": "gpt-4o-mini",
                    "messages": messages
                },
                reason="Generate conversational response with history context"
            )

            # Execute
            self.logger.info(f"{LogEmoji.AI} Calling LLM with {len(messages)} messages")

            response = await self.http_client.post(
                f"{self.core_gateway_url}/v1/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30.0
            )

            if response.status_code == 200:
                result = response.json()

                chain.add_observation(
                    tool_call_id=action_id,
                    result=result,
                    success=True,
                    insight=f"LLM generated response with {len(result.get('content', ''))} characters"
                )

                chain.overall_confidence = 0.9

            else:
                chain.add_observation(
                    tool_call_id=action_id,
                    result={"error": f"HTTP {response.status_code}"},
                    success=False,
                    insight=f"LLM call failed with status {response.status_code}"
                )
                chain.overall_confidence = 0.5

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} LLM error: {e}")
            chain.add_observation(
                tool_call_id=action_id,
                result={"error": str(e)},
                success=False,
                insight=f"LLM service unavailable: {str(e)}"
            )
            chain.overall_confidence = 0.3

    async def synthesize_response(self, chain: ReasoningChain) -> str:
        """
        Synthesize final response from reasoning chain
        """
        # Get the last observation result
        if not chain.steps:
            return t('errors.no_request', language='vi')

        # FIX BUG #10A: Find the last step with an observation (not just the last step)
        # The last step is usually a "conclusion" thought without observation
        last_step_with_obs = None
        for step in reversed(chain.steps):
            if step.observation:
                last_step_with_obs = step
                break

        if not last_step_with_obs or not last_step_with_obs.observation:
            return t('errors.no_request', language='vi')

        if not last_step_with_obs.observation.success:
            return t('errors.retry_error', language='vi')

        result = last_step_with_obs.observation.result

        # Extract response based on service type
        if last_step_with_obs.action and "rag_service" in last_step_with_obs.action.tool_name:
            # RAG service response
            return result.get("response", "Không tìm thấy kết quả phù hợp.")

        elif last_step_with_obs.action and "core_gateway" in last_step_with_obs.action.tool_name:
            # LLM response
            return result.get("content", "Không có phản hồi từ hệ thống.")

        return "Đã xử lý xong yêu cầu."

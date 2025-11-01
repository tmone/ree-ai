"""
Orchestrator Service Prompts - CTO Service #2
Custom prompts for intelligent routing and intent detection
"""
from typing import Dict, List, Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Import shared prompts
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from shared.prompts.real_estate_prompts import (
    SYSTEM_PROMPTS, PromptTemplate as SharedPromptTemplate,
    FEW_SHOT_EXAMPLES
)


class OrchestratorPrompts:
    """
    Orchestrator-specific prompts for CTO Service #2
    Handles: Intent detection, routing, entity extraction
    """

    # Improved intent detection prompt with better structure and examples
    INTENT_DETECTION_SYSTEM = """You are an expert intent classifier for a Vietnamese real estate AI system.

TASK: Analyze the user's query and return ONLY a JSON object with the correct intent classification.

CRITICAL RULES - READ CAREFULLY:

1. **PRICE_ANALYSIS**: Questions asking if a price is reasonable/fair
   - Signals: "hợp lý không", "hợp lý ko", "có đắt không", "giá này có cao không"
   - Example: "Giá 2.5 tỷ cho căn hộ 70m² quận 7 có hợp lý không?"
   - ⚠️ Even if query mentions property specs, if it asks "reasonable?", it's PRICE_ANALYSIS, NOT SEARCH!

2. **LOCATION_INSIGHTS**: Questions about area amenities, neighborhood info
   - Signals: "có tiện ích gì", "khu vực ... có gì", "có trường học không", "gần chợ không"
   - Example: "Quận Thủ Đức có tiện ích gì?"
   - ⚠️ Focus is on the AREA, not finding a specific property

3. **LEGAL_GUIDANCE**: Questions about procedures, documents, legal process
   - Signals: "thủ tục", "giấy tờ", "sổ đỏ", "sổ hồng", "hợp đồng", "cần chuẩn bị gì"
   - Example: "Thủ tục mua nhà cần giấy tờ gì?"
   - ⚠️ Legal/administrative questions, not property search

4. **CHAT**: Greetings, identity questions, general conversation
   - Signals: "xin chào", "hello", "bạn là ai", "cảm ơn", "thank you"
   - Example: "Xin chào, bạn là ai?"
   - ⚠️ Conversational, not real estate related

5. **INVESTMENT_ADVICE**: Questions about where to invest, profitability
   - Signals: "nên đầu tư", "tiềm năng", "lợi nhuận", "nên mua ... hay ..."
   - Example: "Nên đầu tư vào quận 2 hay quận 7 với 5 tỷ?"
   - ⚠️ Advisory question, not specific property search

6. **COMPARE**: Comparing two or more properties/projects
   - Signals: "so sánh", "compare", "khác gì", "vs", "tốt hơn"
   - Example: "So sánh căn hộ Vinhomes Grand Park với Masteri Thảo Điền"

7. **SEARCH**: Finding specific properties with criteria
   - Signals: "tìm", "cần", "có", "danh sách", "muốn mua"
   - Example: "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ"
   - ⚠️ Only use when actually searching for properties, NOT when asking about prices/areas

8. **UNKNOWN**: Query doesn't fit any category above

DECISION FLOWCHART:
1. Does it greet or ask who I am? → CHAT
2. Does it ask about procedures/documents? → LEGAL_GUIDANCE
3. Does it ask if price is reasonable? → PRICE_ANALYSIS
4. Does it ask about area amenities? → LOCATION_INSIGHTS
5. Does it ask for investment advice? → INVESTMENT_ADVICE
6. Does it compare properties? → COMPARE
7. Does it search for properties? → SEARCH
8. Otherwise → UNKNOWN

OUTPUT FORMAT (JSON only, NO markdown, NO explanation):
{"intent": "INTENT_NAME", "confidence": 0.95, "entities": {}}

EXAMPLES:

Input: "Giá 2.5 tỷ cho căn hộ 70m² quận 7 có hợp lý không?"
Output: {"intent": "PRICE_ANALYSIS", "confidence": 0.95, "entities": {}}

Input: "Quận Thủ Đức có tiện ích gì?"
Output: {"intent": "LOCATION_INSIGHTS", "confidence": 0.93, "entities": {}}

Input: "Thủ tục mua nhà cần giấy tờ gì?"
Output: {"intent": "LEGAL_GUIDANCE", "confidence": 0.95, "entities": {}}

Input: "Xin chào, bạn là ai?"
Output: {"intent": "CHAT", "confidence": 0.98, "entities": {}}

Input: "Nên đầu tư vào quận 2 hay quận 7 với 5 tỷ?"
Output: {"intent": "INVESTMENT_ADVICE", "confidence": 0.94, "entities": {}}

Input: "So sánh căn hộ Vinhomes Grand Park với Masteri Thảo Điền"
Output: {"intent": "COMPARE", "confidence": 0.96, "entities": {}}

Input: "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ"
Output: {"intent": "SEARCH", "confidence": 0.92, "entities": {}}

Now classify the following query:
"""

    # Few-shot examples for intent detection
    INTENT_FEW_SHOT_EXAMPLES = [
        {
            "input": "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ",
            "output": {
                "intent": "SEARCH",
                "confidence": 0.95,
                "entities": {
                    "bedrooms": 2,
                    "location": "Quận 7",
                    "price_range": {"max": 3000000000},
                    "property_type": "căn hộ"
                },
                "reasoning": "Câu hỏi tìm kiếm rõ ràng với điều kiện cụ thể"
            }
        },
        {
            "input": "So sánh 2 căn hộ tại Vinhomes Grand Park",
            "output": {
                "intent": "COMPARE",
                "confidence": 0.92,
                "entities": {
                    "property_type": "căn hộ",
                    "location": "Vinhomes Grand Park",
                    "count": 2
                },
                "reasoning": "Yêu cầu so sánh 2 bất động sản"
            }
        },
        {
            "input": "Giá 2.5 tỷ cho 70m² Q7 có hợp lý không?",
            "output": {
                "intent": "PRICE_ANALYSIS",
                "confidence": 0.93,
                "entities": {
                    "price": 2500000000,
                    "area": 70,
                    "location": "Quận 7"
                },
                "reasoning": "Yêu cầu đánh giá tính hợp lý của giá"
            }
        },
        {
            "input": "Nên đầu tư vào Q2 hay Q7 với 5 tỷ?",
            "output": {
                "intent": "INVESTMENT_ADVICE",
                "confidence": 0.90,
                "entities": {
                    "locations": ["Quận 2", "Quận 7"],
                    "budget": 5000000000
                },
                "reasoning": "Tư vấn đầu tư với ngân sách cụ thể"
            }
        },
        {
            "input": "Quận Thủ Đức có gì hay?",
            "output": {
                "intent": "LOCATION_INSIGHTS",
                "confidence": 0.88,
                "entities": {
                    "location": "Quận Thủ Đức"
                },
                "reasoning": "Hỏi về thông tin khu vực"
            }
        },
        {
            "input": "Xin chào, bạn là ai?",
            "output": {
                "intent": "CHAT",
                "confidence": 0.95,
                "entities": {},
                "reasoning": "Câu chào hỏi chung"
            }
        }
    ]

    # Routing decision prompt
    ROUTING_DECISION_SYSTEM = """Bạn là REE AI Router - Quyết định service nào xử lý request.

🎯 ROUTING RULES:

**SEARCH Intent** → RAG Service
- Service: `rag_service`
- Endpoint: `/rag`
- Reason: Tìm kiếm vector + BM25 trong OpenSearch
- Should_use_RAG: true

**COMPARE Intent** → RAG Service (lấy 2+ properties) → Analysis Chain
- Service: `rag_service` + custom analysis
- Endpoint: `/compare`
- Reason: Lấy data từ RAG, sau đó phân tích so sánh
- Should_use_RAG: true

**PRICE_ANALYSIS Intent** → Price Suggestion Service
- Service: `price_suggestion`
- Endpoint: `/analyze`
- Reason: Phân tích giá với market data
- Should_use_RAG: false

**INVESTMENT_ADVICE Intent** → RAG Service + Investment Analysis
- Service: `rag_service` + investment chain
- Endpoint: `/investment`
- Reason: Lấy market data + phân tích đầu tư
- Should_use_RAG: true

**LOCATION_INSIGHTS Intent** → RAG Service (area data) + Analysis
- Service: `rag_service`
- Endpoint: `/location`
- Reason: Thông tin khu vực từ database
- Should_use_RAG: true

**LEGAL_GUIDANCE Intent** → Core Gateway (LLM direct)
- Service: `core_gateway`
- Endpoint: `/chat/completions`
- Reason: Tư vấn pháp lý từ knowledge base LLM
- Should_use_RAG: false

**CHAT Intent** → Core Gateway (LLM direct)
- Service: `core_gateway`
- Endpoint: `/chat/completions`
- Reason: Trò chuyện thông thường
- Should_use_RAG: false

**UNKNOWN Intent** → Core Gateway (fallback)
- Service: `core_gateway`
- Endpoint: `/chat/completions`
- Reason: Fallback to general LLM
- Should_use_RAG: false

📤 OUTPUT FORMAT (JSON):
{
  "target_service": "rag_service",
  "endpoint": "/rag",
  "should_use_rag": true,
  "routing_params": {
    "query_rewrite": "Tìm căn hộ 2PN Quận 7 giá dưới 3 tỷ",
    "filters": {"bedrooms": 2, "district": "Quận 7"},
    "limit": 10
  },
  "reasoning": "SEARCH intent requires RAG retrieval"
}
"""

    @staticmethod
    def build_intent_detection_prompt() -> ChatPromptTemplate:
        """Build LangChain prompt for intent detection"""
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                OrchestratorPrompts.INTENT_DETECTION_SYSTEM
            ),
            HumanMessagePromptTemplate.from_template(
                "Phân loại câu hỏi sau:\n\n{query}\n\n"
                "Dựa vào few-shot examples:\n{examples}"
            )
        ])

    @staticmethod
    def build_routing_prompt() -> ChatPromptTemplate:
        """Build LangChain prompt for routing decision"""
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                OrchestratorPrompts.ROUTING_DECISION_SYSTEM
            ),
            HumanMessagePromptTemplate.from_template(
                "Intent detected: {intent}\n"
                "Confidence: {confidence}\n"
                "Extracted entities: {entities}\n"
                "User query: {query}\n\n"
                "Quyết định routing:"
            )
        ])

    @staticmethod
    def build_multi_turn_context_prompt(
        conversation_history: List[Dict[str, str]],
        current_query: str
    ) -> str:
        """Build prompt with conversation context for multi-turn conversations"""

        # Format conversation history (last 5 turns)
        history_text = ""
        if conversation_history:
            history_text = "\n📜 LỊCH SỬ HỘI THOẠI (5 tin nhắn gần nhất):\n"
            for msg in conversation_history[-5:]:
                role = "👤 User" if msg["role"] == "user" else "🤖 Assistant"
                history_text += f"{role}: {msg['content']}\n"

        return f"""
{OrchestratorPrompts.INTENT_DETECTION_SYSTEM}

{history_text}

👤 CURRENT QUERY: {current_query}

💡 CONTEXT ANALYSIS:
- Xem xét lịch sử hội thoại để hiểu ngữ cảnh
- Nếu user đang tham chiếu ("căn đó", "so sánh với căn trước"), sử dụng context
- Intent có thể thay đổi theo flow hội thoại

📤 Phân tích intent và entities cho câu hỏi hiện tại:
"""

    @staticmethod
    def get_few_shot_examples_text() -> str:
        """Get formatted few-shot examples as text"""
        examples_text = ""
        for i, example in enumerate(OrchestratorPrompts.INTENT_FEW_SHOT_EXAMPLES, 1):
            examples_text += f"\nExample {i}:\n"
            examples_text += f"Input: {example['input']}\n"
            examples_text += f"Output: {example['output']}\n"
        return examples_text


# Convenience functions for quick access
def get_intent_detection_prompt() -> ChatPromptTemplate:
    """Get intent detection prompt"""
    return OrchestratorPrompts.build_intent_detection_prompt()


def get_routing_prompt() -> ChatPromptTemplate:
    """Get routing decision prompt"""
    return OrchestratorPrompts.build_routing_prompt()


def get_multi_turn_prompt(history: List[Dict[str, str]], query: str) -> str:
    """Get multi-turn conversation prompt"""
    return OrchestratorPrompts.build_multi_turn_context_prompt(history, query)

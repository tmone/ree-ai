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

    # Enhanced intent detection with Vietnamese real estate expertise
    INTENT_DETECTION_SYSTEM = """Bạn là REE AI Orchestrator - Bộ định tuyến thông minh cho hệ thống bất động sản.

🎯 NHIỆM VỤ:
Phân tích câu hỏi của người dùng và xác định intent (ý định) để định tuyến đến service phù hợp.

📊 CÁC INTENT TYPES:

1. **SEARCH** - Tìm kiếm bất động sản
   Keywords: "tìm", "find", "search", "có", "cần", "muốn mua"
   Examples:
   - "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ"
   - "Có nhà nào gần Metro không?"

2. **COMPARE** - So sánh bất động sản
   Keywords: "so sánh", "compare", "khác gì", "tốt hơn", "vs"
   Examples:
   - "So sánh 2 căn hộ này"
   - "Căn nào tốt hơn?"

3. **PRICE_ANALYSIS** - Phân tích giá
   Keywords: "giá", "price", "bao nhiêu", "đánh giá giá", "hợp lý không"
   Examples:
   - "Giá 2.5 tỷ cho căn hộ 70m² Q7 có hợp lý không?"
   - "Phân tích giá căn này"

4. **INVESTMENT_ADVICE** - Tư vấn đầu tư
   Keywords: "đầu tư", "investment", "nên mua", "tiềm năng", "sinh lời"
   Examples:
   - "Nên đầu tư vào khu nào?"
   - "Căn này có tiềm năng không?"

5. **LOCATION_INSIGHTS** - Thông tin khu vực
   Keywords: "quận", "khu vực", "location", "infrastructure", "tiện ích"
   Examples:
   - "Quận 2 có gì?"
   - "Khu vực Thủ Đức phát triển thế nào?"

6. **LEGAL_GUIDANCE** - Tư vấn pháp lý
   Keywords: "pháp lý", "legal", "sổ đỏ", "sổ hồng", "thủ tục"
   Examples:
   - "Sổ đỏ khác sổ hồng thế nào?"
   - "Thủ tục mua nhà gồm gì?"

7. **CHAT** - Trò chuyện chung
   Keywords: "xin chào", "hello", "cảm ơn", "thank you"
   Examples:
   - "Xin chào"
   - "Bạn là ai?"

8. **UNKNOWN** - Không xác định
   Fallback khi không match intent nào

🔍 ENTITY EXTRACTION:
Trích xuất thông tin từ câu hỏi:
- **bedrooms**: Số phòng ngủ (2PN, 3 phòng ngủ)
- **price_range**: Khoảng giá (dưới 3 tỷ, 2-3 tỷ)
- **location**: Địa điểm (Quận 7, Q2, Thủ Đức)
- **property_type**: Loại BĐS (căn hộ, nhà phố, biệt thự, đất)
- **area**: Diện tích (70m², 100m2)
- **district**: Quận/huyện cụ thể

💡 LƯU Ý:
- Ưu tiên intent cụ thể (SEARCH, COMPARE) hơn CHAT
- Với câu hỏi mơ hồ, chọn intent có confidence cao nhất
- Extract tất cả entities có thể từ câu hỏi
- Confidence score: 0.0-1.0 (càng cao càng chắc chắn)

📤 OUTPUT FORMAT (JSON):
{
  "intent": "INTENT_NAME",
  "confidence": 0.95,
  "entities": {
    "bedrooms": 2,
    "location": "Quận 7",
    "price_range": {"max": 3000000000},
    "property_type": "căn hộ"
  },
  "reasoning": "Người dùng đang tìm kiếm căn hộ với điều kiện cụ thể"
}
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

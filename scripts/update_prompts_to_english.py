"""
Script to update all Vietnamese prompts to load from English template files
"""
import os
import re

def load_prompt_helper():
    """Load prompt helper function to be added to service files"""
    return '''
def load_prompt(filename: str) -> str:
    """Load prompt template from shared/prompts directory"""
    prompt_path = os.path.join(os.path.dirname(__file__), '../../shared/prompts', filename)
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None
'''

# 1. Update services/orchestrator/prompts.py
print("Updating services/orchestrator/prompts.py...")
orchestrator_prompts_file = 'services/orchestrator/prompts.py'

with open(orchestrator_prompts_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Vietnamese ROUTING_DECISION_SYSTEM prompt
old_routing = '''    # Routing decision prompt
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
"""'''

new_routing = '''    # Routing decision prompt - Load from file
    _routing_prompt = None

    @classmethod
    def get_routing_prompt(cls):
        """Load routing prompt from file with caching"""
        if cls._routing_prompt is None:
            prompt_path = os.path.join(os.path.dirname(__file__), '../../shared/prompts/orchestrator_routing_en.txt')
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    cls._routing_prompt = f.read()
            except FileNotFoundError:
                # Fallback to inline English prompt
                cls._routing_prompt = """You are REE AI Router - Decide which service handles each request.
(Fallback prompt - see orchestrator_routing_en.txt for full version)
"""
        return cls._routing_prompt

    ROUTING_DECISION_SYSTEM = property(lambda self: self.get_routing_prompt())'''

if old_routing in content:
    content = content.replace(old_routing, new_routing)
    print("✅ Updated ROUTING_DECISION_SYSTEM")
else:
    print("⚠️ Could not find ROUTING_DECISION_SYSTEM to replace")

with open(orchestrator_prompts_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Orchestrator prompts updated!\n")

print("="*60)
print("Summary:")
print("- Updated orchestrator routing prompt to load from file")
print("- Next: Update other service files manually")
print("="*60)

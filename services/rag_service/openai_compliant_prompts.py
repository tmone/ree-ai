"""
OpenAI Design Standards - Compliant Prompt Templates for RAG Service

CRITICAL: These prompts enforce OpenAI's communication standards:
1. CONCISE: Keep responses under 3 sentences for property listings
2. CONTEXT-DRIVEN: Always reference user's stated preferences
3. JARGON-FREE: Use simple Vietnamese, avoid marketing buzzwords
4. NO MARKETING: Never use promotional language (🔥, HOT, SIÊU ƯU ĐÃI, etc.)
5. TRANSPARENT: Explain why you're suggesting these properties

References:
- https://developers.openai.com/apps-sdk/concepts/design-guidelines/
- Section: "Communication Standards"

Last Updated: 2025-11-01
"""

# ============================================
# SYSTEM PROMPTS
# ============================================

SYSTEM_PROMPT_OPENAI_COMPLIANT = """You are a professional real estate assistant for REE AI.

Your role is to help users find suitable properties through natural, conversational interactions.

COMMUNICATION GUIDELINES (OpenAI Compliance):

⛔ CRITICAL RULE #0: NO HALLUCINATION (HIGHEST PRIORITY)
   ✅ ONLY use properties provided in the context data
   ✅ If context has 1 property, present ONLY 1 property
   ✅ If context has 0 properties, say "Tôi không tìm thấy bất động sản phù hợp"
   ❌ ABSOLUTELY FORBIDDEN: Creating, inventing, or suggesting properties not in the data
   ❌ ABSOLUTELY FORBIDDEN: Making up addresses, prices, or property details
   ❌ ABSOLUTELY FORBIDDEN: Using examples like "District 1", "District 7" if not in data

   **If you create fake properties, the system will be considered broken and unusable.**

1. CONCISE RESPONSES
   ✅ Keep property listing responses to 2-3 sentences maximum
   ✅ Show ALL properties from context (1-5 properties max), never more than provided
   ❌ Don't write long paragraphs about each property

2. CONTEXT-DRIVEN
   ✅ Always reference user's stated preferences (budget, location, type)
   ✅ Explain WHY these properties match their needs
   ❌ Don't suggest properties without explaining relevance

3. JARGON-FREE LANGUAGE
   ✅ Use simple Vietnamese that anyone can understand
   ✅ Example: "căn hộ 2 phòng ngủ" not "unit 2BR"
   ❌ Avoid real estate jargon: "mặt tiền", "hẻm xe hơi", "thổ cư 100%"

4. NO MARKETING LANGUAGE (CRITICAL)
   ❌ FORBIDDEN: 🔥, HOT, SIÊU ƯU ĐÃI, CƠ HỘI VÀNG, ĐẲNG CẤP, SANG TRỌNG
   ❌ FORBIDDEN: "Chỉ hôm nay!", "Số lượng có hạn!", "Liên hệ ngay!"
   ❌ FORBIDDEN: Superlatives without context: "Tốt nhất", "Hoàn hảo nhất"
   ✅ ALLOWED: Factual descriptions: "Căn hộ này có view sông", "Gần trường quốc tế"

5. PROACTIVE BUT NOT PUSHY
   ✅ Contextual nudges: "Dựa trên ngân sách dưới 5 tỷ của bạn, tôi gợi ý..."
   ❌ Unsolicited promotions: "Check out our premium listings!"

6. TRANSPARENCY
   ✅ Explain why properties appear: "Căn hộ này phù hợp vì..."
   ✅ Acknowledge limitations: "Tôi chưa có thông tin về..."
   ❌ Don't make up information or overstate confidence

RESPONSE STRUCTURE:

For property search queries, follow this structure:

1. **Acknowledgment** (1 sentence)
   "Tôi tìm thấy [EXACT_NUMBER] bất động sản phù hợp với yêu cầu [repeat user preference]."

   IMPORTANT: [EXACT_NUMBER] must match the actual count in context data!
   - If context has 0 properties → "Tôi không tìm thấy bất động sản phù hợp"
   - If context has 1 property → "Tôi tìm thấy 1 bất động sản phù hợp"
   - If context has 2 properties → "Tôi tìm thấy 2 bất động sản phù hợp"
   - Never say "3 properties" if context only has 1!

2. **Property Listing** (EXACTLY as many as in context, 1-5 max)
   For each property FROM CONTEXT ONLY, provide ONLY 4 key details:
   - Title (use exact title from data)
   - Location (use exact location from data)
   - Key feature (e.g., "2 phòng ngủ, 75m²" - from data only)
   - Price (use exact price from data)

3. **Contextual Insight** (1 sentence, optional)
   "Căn hộ này gần trường quốc tế như bạn đã đề cập."

4. **Clear Next Action** (1 sentence)
   "Bạn muốn xem chi tiết không?"

GOOD EXAMPLE:
--------------
User: "Tìm căn hộ 2 phòng ngủ Quận 1 dưới 5 tỷ"

Assistant Response:
"Tôi tìm thấy 8 căn hộ 2 phòng ngủ tại Quận 1 trong khoảng giá của bạn. Đây là 3 lựa chọn phù hợp nhất:

1. Căn hộ The Manor - Mê Linh Point
   📍 Quận 1 • 2 phòng ngủ, 75m² • 3.2 tỷ

2. Vinhomes Golden River
   📍 Quận 1 • 2 phòng ngủ, 82m² • 4.5 tỷ

3. The Ascent Thảo Điền
   📍 Quận 2 (gần Quận 1) • 2 phòng ngủ, 70m² • 3.8 tỷ

Căn hộ đầu tiên gần trường quốc tế BIS. Bạn muốn xem chi tiết căn nào?"

BAD EXAMPLE (DO NOT USE):
--------------------------
❌ "🔥 SIÊU HOT! 8 căn hộ ĐẲNG CẤP tại Quận 1 chỉ từ 3.2 tỷ! CƠ HỘI VÀNG sở hữu BĐS cao cấp với SIÊU ƯU ĐÃI! Liên hệ NGAY để được tư vấn miễn phí và nhận ưu đãi đặc biệt chỉ có hôm nay!"

Why this is bad:
- Uses marketing language (🔥, SIÊU HOT, ĐẲNG CẤP, CƠ HỘI VÀNG)
- Creates false urgency ("chỉ có hôm nay")
- Too promotional, not conversational
- Violates OpenAI guidelines completely

FORMAT GUIDE:
-------------
Preferred text format (simple, clean):
✅ "Căn hộ 2 phòng ngủ, 75m², giá 3.2 tỷ tại Quận 1"
✅ "Gần trường quốc tế BIS, có hồ bơi và gym"

Avoid excessive formatting:
❌ "**🔥 CĂN HỘ SIÊU HOT 🔥** - 2PN/75m²/3.2 TỶ!!!"
❌ "⭐⭐⭐⭐⭐ ĐẲNG CẤP 5 SAO ⭐⭐⭐⭐⭐"

Use emojis sparingly (max 1 per line for clarity):
✅ "📍 Quận 1"
✅ "💰 3.2 tỷ"
❌ "🏠🌟💎✨ Căn hộ cao cấp 🔥💯🎉"
"""


# ============================================
# USER PROMPTS
# ============================================

def build_user_prompt_openai_compliant(query: str, context: str) -> str:
    """
    Build user prompt for LLM generation

    Args:
        query: User's original query
        context: Retrieved property data (markdown formatted)

    Returns:
        Formatted user prompt string
    """
    return f"""User's question: {query}

Retrieved property data:
{context}

⛔ CRITICAL INSTRUCTIONS:
1. ONLY use properties listed in the "Retrieved property data" above
2. Count the properties carefully - if there's only 1, present only 1
3. NEVER invent or create fake properties
4. If no properties found, say "Tôi không tìm thấy bất động sản phù hợp"

Generate a natural, helpful response following the guidelines above. Remember:
- Keep it CONCISE (2-3 sentences max)
- Reference user's preferences
- NO marketing language
- NO hallucination - ONLY real data
- Provide clear next action"""


# ============================================
# FALLBACK RESPONSES (No Marketing)
# ============================================

FALLBACK_NO_RESULTS = """Xin lỗi, tôi không tìm thấy bất động sản phù hợp với yêu cầu của bạn.

Bạn có thể thử:
- Tăng ngân sách hoặc mở rộng khu vực tìm kiếm
- Điều chỉnh yêu cầu về diện tích hoặc số phòng
- Cho tôi biết thêm chi tiết về nhu cầu của bạn"""

FALLBACK_ERROR = """Xin lỗi, tôi gặp sự cố khi tìm kiếm bất động sản.

Vui lòng thử lại sau hoặc liên hệ hỗ trợ nếu vấn đề vẫn tiếp tục."""


# ============================================
# PROACTIVE SUGGESTIONS (Context-Aware Only)
# ============================================

def generate_proactive_suggestion(user_context: dict) -> str:
    """
    Generate contextual proactive suggestion (OpenAI compliant)

    OpenAI Rule: "Only surface contextual nudges tied to user intent"

    Args:
        user_context: Dict containing:
            - budget_range: Tuple of (min, max) price
            - preferred_locations: List of locations
            - property_types: List of property types
            - last_search_date: Datetime of last search

    Returns:
        Contextual suggestion string or empty string if not relevant
    """
    # ✅ ALLOWED: Contextual nudge based on user behavior
    if (user_context.get("budget_range")
        and user_context.get("preferred_locations")
        and user_context.get("last_search_date")):

        location = user_context["preferred_locations"][0]
        max_price = user_context["budget_range"][1]
        price_str = f"{max_price/1_000_000_000:.1f} tỷ" if max_price >= 1_000_000_000 else f"{max_price/1_000_000:.0f} triệu"

        return (f"Dựa trên lịch sử tìm kiếm của bạn ({location}, dưới {price_str}), "
                f"tôi có thể gợi ý thêm các bất động sản mới đăng hôm nay.")

    # ❌ FORBIDDEN: Unsolicited promotion
    # return "Check out our premium listings! Limited time offer!"

    # No suggestion if not contextually relevant
    return ""


# ============================================
# PROMPT VALIDATION (Development Helper)
# ============================================

FORBIDDEN_MARKETING_TERMS = [
    # Vietnamese marketing buzzwords
    "🔥", "HOT", "SIÊU ƯU ĐÃI", "CƠ HỘI VÀNG", "ĐẲNG CẤP", "SANG TRỌNG",
    "SIÊU HOT", "CAO CẤP", "ĐẲNG CẤP QUỐC TẾ", "HIỆN ĐẠI BẬC NHẤT",
    "HOÀN HẢO NHẤT", "TỐT NHẤT", "KHỦNG", "XỊN", "XINH", "CỰC PHẨM",

    # False urgency
    "CHỈ HÔM NAY", "SỐ LƯỢNG CÓ HẠN", "NHANH TAY", "LIÊN HỆ NGAY",
    "ĐỪNG BỎ LỠ", "CƠ HỘI DUY NHẤT", "KHÔNG THỂ BỎ QUA",

    # Excessive punctuation
    "!!!", "???", "🎉🎉🎉", "⭐⭐⭐⭐⭐",

    # English marketing terms
    "HOT DEAL", "LIMITED TIME", "ACT NOW", "BEST OFFER", "PREMIUM",
]


def validate_response_compliance(response: str) -> tuple[bool, list[str]]:
    """
    Validate that response follows OpenAI communication standards

    Args:
        response: Generated response text

    Returns:
        Tuple of (is_valid, violations_list)
    """
    violations = []

    # Check for forbidden marketing terms
    response_upper = response.upper()
    for term in FORBIDDEN_MARKETING_TERMS:
        if term.upper() in response_upper:
            violations.append(f"Contains marketing term: '{term}'")

    # Check response length (should be concise)
    sentences = response.split('.')
    if len(sentences) > 5:
        violations.append(f"Response too long ({len(sentences)} sentences, should be <5)")

    # Check for excessive emojis
    emoji_count = sum(1 for char in response if ord(char) > 127000)
    if emoji_count > 10:
        violations.append(f"Too many emojis ({emoji_count}, should be <10)")

    return (len(violations) == 0, violations)


# ============================================
# USAGE EXAMPLE
# ============================================

"""
# In RAG Service main.py:

from services.rag_service.openai_compliant_prompts import (
    SYSTEM_PROMPT_OPENAI_COMPLIANT,
    build_user_prompt_openai_compliant,
    validate_response_compliance,
    FALLBACK_NO_RESULTS
)

async def _generate_response(self, query: str, context: str, retrieved_properties: List[Dict]):
    # Use OpenAI-compliant prompts
    system_prompt = SYSTEM_PROMPT_OPENAI_COMPLIANT
    user_prompt = build_user_prompt_openai_compliant(query, context)

    llm_request = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 500,  # Force conciseness
        "temperature": 0.7
    }

    response = await self.http_client.post(
        f"{self.core_gateway_url}/chat/completions",
        json=llm_request
    )

    if response.status_code == 200:
        generated_text = response.json().get("content", "").strip()

        # Validate compliance (in development)
        is_valid, violations = validate_response_compliance(generated_text)
        if not is_valid:
            self.logger.warning(f"Response violates OpenAI standards: {violations}")

        return generated_text
    else:
        return FALLBACK_NO_RESULTS
"""

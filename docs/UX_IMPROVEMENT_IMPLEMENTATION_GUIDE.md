# UX Improvement Implementation Guide

## Overview

This guide provides step-by-step instructions to implement the conversational property posting UX improvements requested by the user.

**User Complaint**: "Sao bạn cứ hỏi hoài vậy? Họ đã bảo họ không có thời gian!"

**Goal**: Make property posting fast, conversational, and with a clear endpoint.

---

## Changes Required

### 1. Update Completeness Service Prompts

**File**: `services/completeness/prompts.py`

**Current behavior**: Returns verbose JSON with all missing fields, strengths, suggestions, priority actions

**New behavior**: Return minimal JSON with:
- `ready_to_post` (boolean): `true` if score >= 60%
- `next_questions` (list): 1-2 most important fields to ask next
- `collected_summary` (list): Short bullet points of what we have

**Changes needed**:

1. Update `COMPLETENESS_SYSTEM_PROMPT` (line 24):
   - Add UX principles section
   - Change output format to include `ready_to_post` and `next_questions`
   - Remove verbose `strengths`, `suggestions`, `priority_actions`

2. Update output JSON schema (line 141-173):

```python
📤 OUTPUT FORMAT (JSON):
{
  "overall_score": 68,
  "ready_to_post": true,  // NEW: true if overall_score >= 60
  "next_questions": [      // NEW: Only 1-2 most critical missing fields
    {
      "field": "district",
      "question_vi": "Căn hộ ở quận nào?"
    },
    {
      "field": "price",
      "question_vi": "Giá thuê bao nhiêu/tháng?"
    }
  ],
  "collected_summary": [   // NEW: Short summary of collected info
    "Căn hộ cho thuê",
    "2 phòng ngủ, 70m²"
  ],
  "missing_critical": ["contact_phone", "title"]  // Only CRITICAL fields
}
```

3. Update few-shot examples (line 176-264) to match new format

---

### 2. Create Response Generator

**New File**: `services/orchestrator/utils/response_generator.py`

This file will format the completeness check output into user-friendly responses.

```python
"""
Response Generator for Conversational Property Posting
Converts completeness check output into short, user-friendly messages
"""

def generate_property_posting_response(completeness_data: dict, entities: dict) -> str:
    """
    Generate conversational response based on completeness score

    Args:
        completeness_data: Output from completeness check service
        entities: Currently collected property entities

    Returns:
        User-friendly response string
    """
    score = completeness_data.get("overall_score", 0)
    ready_to_post = completeness_data.get("ready_to_post", False)
    next_questions = completeness_data.get("next_questions", [])
    collected_summary = completeness_data.get("collected_summary", [])

    # Case 1: Ready to post (score >= 60%)
    if ready_to_post:
        summary_text = "\n- ".join(collected_summary)
        return f"""Tuyệt! Đã có đủ thông tin cơ bản:
- {summary_text}

Bạn có muốn đăng tin ngay không? (có/không)

(Nếu muốn bổ sung thêm thông tin, cứ nói thêm nhé)"""

    # Case 2: Not ready, ask for next 1-2 fields
    if next_questions:
        questions_text = "\n".join([
            f"{i+1}. {q['question_vi']}"
            for i, q in enumerate(next_questions[:2])  # Max 2 questions
        ])

        return f"""Để đăng tin nhanh, cho tôi biết:
{questions_text}

(Có thể trả lời ngắn gọn)"""

    # Case 3: Just started
    return """Cảm ơn bạn! Tôi hiểu bạn muốn đăng tin.

Để bắt đầu, cho tôi biết:
1. Loại bất động sản gì? (căn hộ/nhà/đất/...)
2. Bán hay cho thuê?"""
```

---

### 3. Update Orchestrator to Detect Confirmation

**File**: `services/orchestrator/main.py`

**Add confirmation detection logic**:

```python
def detect_confirmation(user_input: str) -> bool:
    """Detect if user confirms to post the property"""
    confirmation_keywords = [
        "có", "đăng luôn", "đăng ngay", "ok", "được", "đồng ý",
        "yes", "post it", "đăng đi"
    ]

    user_lower = user_input.lower().strip()
    return any(keyword in user_lower for keyword in confirmation_keywords)


def handle_property_posting_flow(user_input: str, conversation_state: dict) -> dict:
    """
    Handle property posting conversation flow

    Returns:
        {
            "response": str,  # Message to user
            "end_conversation": bool,  # True if should end
            "posted": bool  # True if property was posted
        }
    """
    # Get completeness check
    completeness = call_completeness_service(conversation_state["entities"])

    # Check if ready to post and user confirmed
    if completeness.get("ready_to_post") and detect_confirmation(user_input):
        # TODO: Actually post the property to database
        property_id = post_property_to_db(conversation_state["entities"])

        return {
            "response": f"✅ Đã đăng tin thành công!\n\nMã tin: #{property_id}\n\nCảm ơn bạn đã sử dụng dịch vụ!",
            "end_conversation": True,
            "posted": True
        }

    # Generate conversational response
    from .utils.response_generator import generate_property_posting_response
    response = generate_property_posting_response(completeness, conversation_state["entities"])

    return {
        "response": response,
        "end_conversation": False,
        "posted": False
    }
```

---

### 4. Priority Queue for Questions

**Logic**: Determine which 1-2 fields to ask next based on:

1. **CRITICAL fields** (must have for posting):
   - property_type, transaction_type, district, price, area

2. **HIGH PRIORITY** (important for quality):
   - bedrooms, bathrooms (if not LAND)
   - contact_phone
   - title

3. **MEDIUM PRIORITY** (nice to have):
   - ward, street, furniture, direction, legal_status

**Questioning order**:
```
Turn 1: property_type, transaction_type
Turn 2: district, price
Turn 3: area, bedrooms
Turn 4 (if score < 60%): contact_phone, title
Turn 5 (if score >= 60%): Ask confirmation
```

Add this logic to completeness service prompt:

```python
🎯 QUESTIONING PRIORITY:

**CRITICAL (Ask first if missing):**
1. property_type, transaction_type
2. district, price/price_rent
3. area

**HIGH PRIORITY (Ask second if missing):**
4. bedrooms, bathrooms (skip for LAND)
5. contact_phone

**MEDIUM PRIORITY (Ask third if score < 60%):**
6. title
7. ward, street
8. furniture, direction, legal_status

**STOP POINT:**
When overall_score >= 60%, set ready_to_post = true and STOP asking.
User can volunteer more info, but don't push.
```

---

## Implementation Checklist

### Phase 1: Completeness Service (services/completeness/)
- [ ] Update `prompts.py` line 24-28: Add UX principles
- [ ] Update `prompts.py` line 141-173: Change output JSON format
- [ ] Update `prompts.py` line 176-264: Update few-shot examples
- [ ] Test completeness service returns new format

### Phase 2: Response Generator (services/orchestrator/utils/)
- [ ] Create `response_generator.py`
- [ ] Implement `generate_property_posting_response()`
- [ ] Test with sample completeness data

### Phase 3: Orchestrator Updates (services/orchestrator/)
- [ ] Add `detect_confirmation()` function
- [ ] Add `handle_property_posting_flow()` function
- [ ] Add `post_property_to_db()` stub (implement later)
- [ ] Update main conversation handler to use new flow

### Phase 4: Testing
- [ ] Test Turn 1: "Cho thuê căn hộ" → Asks for district, price
- [ ] Test Turn 2: "Quận 7, 10 triệu" → Asks for area, bedrooms
- [ ] Test Turn 3: "70m2, 2 phòng" → Asks confirmation (score = 68%)
- [ ] Test Turn 4: "Đăng luôn" → Posts and ends conversation
- [ ] Run AI-to-AI test with 19 scenarios

### Phase 5: Deployment
- [ ] Backup current orchestrator code
- [ ] Deploy new completeness service
- [ ] Deploy new orchestrator
- [ ] Monitor user feedback

---

## Testing Scenarios

### Scenario 1: Fast Path (3 turns)
```
User: "Cho thuê căn hộ"
AI: "Để đăng tin nhanh, cho tôi biết:
     1. Căn hộ ở quận nào?
     2. Giá thuê bao nhiêu/tháng?"

User: "Quận 7, 10 triệu"
AI: "Tuyệt! Còn 2 thông tin:
     1. Diện tích bao nhiêu m²?
     2. Bao nhiêu phòng ngủ?"

User: "70m2, 2 phòng"
AI: "Tuyệt! Đã có đủ thông tin cơ bản:
     - Căn hộ cho thuê, Quận 7
     - 70m², 2 phòng ngủ
     - Giá: 10 triệu/tháng

     Bạn có muốn đăng tin ngay không?"

User: "Có"
AI: "✅ Đã đăng tin thành công! Mã tin: #12345"
```

### Scenario 2: User Provides Everything At Once
```
User: "Cho thuê căn hộ 2 phòng ở Quận 7, 70m2, giá 10 triệu/tháng"
AI: "Tuyệt! Đã có đủ thông tin cơ bản:
     - Căn hộ cho thuê, Quận 7
     - 70m², 2 phòng ngủ
     - Giá: 10 triệu/tháng

     Bạn có muốn đăng tin ngay không?"

User: "Đăng luôn"
AI: "✅ Đã đăng tin thành công! Mã tin: #12346"
```

### Scenario 3: User Wants to Add More Info
```
User: "Cho thuê căn hộ 2 phòng ở Quận 7, 70m2, giá 10 triệu/tháng"
AI: "Tuyệt! Đã có đủ thông tin cơ bản... Bạn có muốn đăng tin ngay không?"

User: "Thêm full nội thất, view sông"
AI: "Đã cập nhật! Đã có:
     - Căn hộ cho thuê, Quận 7
     - 70m², 2 phòng ngủ, full nội thất
     - View sông
     - Giá: 10 triệu/tháng

     Bạn có muốn đăng tin ngay không?"

User: "Có"
AI: "✅ Đã đăng tin thành công! Mã tin: #12347"
```

---

## Success Metrics

After implementation, we expect:

- ✅ **Average turns to post**: 3-4 turns (vs current 10+ turns)
- ✅ **Response length**: Max 4 lines (vs current 20+ lines)
- ✅ **Completion rate**: 80%+ users finish posting (vs current ~50%)
- ✅ **User satisfaction**: Positive feedback on speed

---

## Rollback Plan

If users complain about new flow:

1. Keep both prompts in code with feature flag
2. A/B test: 50% old flow, 50% new flow
3. Measure metrics for 1 week
4. Choose winning version

---

**Created**: 2025-11-16
**Priority**: HIGH
**Status**: Ready for implementation

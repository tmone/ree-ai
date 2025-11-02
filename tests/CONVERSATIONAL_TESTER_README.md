# 🎭 CONVERSATIONAL AI TESTER

## Khác biệt với Autonomous Tester

| Feature | **Autonomous Tester** ❌ | **Conversational Tester** ✅ |
|---------|------------------------|----------------------------|
| Test approach | Single queries | Multi-turn conversations |
| Context | No history | Maintains conversation history |
| Realism | Isolated questions | Natural chat flow |
| Personas | No | 4+ realistic personas |
| Follow-up | No | AI generates contextual follow-ups |
| Session-based | No | Complete conversation sessions |

## Cách hoạt động

### 1. **Define Personas với thông số trước**

```python
Persona(
    type=PersonaType.FAMILY_WITH_KIDS,
    name="Chị Lan",
    age_range="35-40",
    family_size=4,
    budget_range="3-5 tỷ",
    preferred_districts=["Quận 7", "Quận 2"],
    requirements=["gần trường học", "an ninh tốt"],
    personality_traits=["hỏi chi tiết", "quan tâm tiện ích"],
    conversation_turns=8
)
```

### 2. **AI generates FIRST query**

Ollama/llama3.2 tạo câu hỏi đầu tiên dựa trên persona:

```
Prompt: "Bạn là Chị Lan, 35-40 tuổi, tìm nhà cho 4 người...
         Tạo câu hỏi ĐẦU TIÊN tự nhiên, KHÔNG đưa hết thông tin."

AI Output:
QUERY: Chào bạn! Tôi đang tìm nhà ở Quận 7 cho gia đình.
REASONING: Bắt đầu khái quát, để chatbot hỏi thêm chi tiết.
```

### 3. **Send → Receive → Analyze**

```
👤 User: "Chào bạn! Tôi đang tìm nhà ở Quận 7 cho gia đình."
   ↓ (gửi tới Orchestrator)
🤖 Bot: "Chào chị! Gia đình chị có bao nhiêu người? Ngân sách dự kiến là bao nhiêu?"
   ↓ (AI phân tích response)
✅ Valid - Bot hỏi thêm thông tin hợp lý
```

### 4. **AI generates NEXT query** (based on history)

```
Prompt: "Bạn là Chị Lan. Lịch sử trò chuyện:
         Turn 1: Bạn: 'Tôi đang tìm nhà ở Quận 7...'
                 Bot: 'Gia đình chị có bao nhiêu người?...'

         NHIỆM VỤ: Tạo câu hỏi TIẾP THEO tự nhiên."

AI Output:
QUERY: Gia đình tôi 4 người, ngân sách khoảng 3-5 tỷ.
REASONING: Trả lời câu hỏi của bot, cung cấp thông tin budget.
```

### 5. **Continue for 6-10 turns**

```
Turn 1: 👤 "Tìm nhà ở Quận 7 cho gia đình"
        🤖 "Có bao nhiêu người? Ngân sách?"

Turn 2: 👤 "4 người, ngân sách 3-5 tỷ"
        🤖 "Tôi tìm thấy 5 căn hộ phù hợp..."

Turn 3: 👤 "Căn đầu tiên có gần trường học không?"
        🤖 "Có, cách trường quốc tế ABC 500m..."

Turn 4: 👤 "So với căn thứ 2 thì sao?"
        🤖 "Căn 2 rẻ hơn nhưng xa hơn..."

Turn 5: 👤 "Khu vực đó an ninh thế nào?"
        🤖 "An ninh rất tốt, có bảo vệ 24/7..."
...
```

## 4 Personas có sẵn

### 1. **👨‍👩‍👧‍👦 Family with Kids (Chị Lan)**
- 4 người, 3-5 tỷ
- Quan tâm: trường học, công viên, an ninh
- Tính cách: hỏi chi tiết, so sánh nhiều
- 8 turns

### 2. **👔 Young Professional (Anh Minh)**
- 1 người, 2-3 tỷ
- Quan tâm: gần công ty, gym, hiện đại
- Tính cách: quyết đoán, quan tâm ROI
- 6 turns

### 3. **💼 Investor (Anh Hùng)**
- 2 người, 5-10 tỷ
- Quan tâm: tiềm năng tăng giá, cho thuê
- Tính cách: phân tích kỹ, hỏi về đầu tư
- 9 turns

### 4. **🏠 First Time Buyer (Chị Mai)**
- 2 người, 2-4 tỷ
- Quan tâm: thủ tục, vay ngân hàng
- Tính cách: hỏi nhiều, lo ngại thủ tục
- 10 turns

## Usage

### Quick Demo (1 persona, 3 turns)

```bash
python3 /tmp/test_conversational_quick.py
```

### Full Test (4 personas, 8-10 turns each)

```bash
cd /Users/tmone/ree-ai
python3 tests/conversational_ai_tester.py
```

**Expected output:**
```
🤖 CONVERSATIONAL AI TESTER
======================================================================
Testing 4 personas
Model: llama3.2
Orchestrator: http://localhost:8090
======================================================================

🎭 Persona 1/4
======================================================================
🎭 CONVERSATION SESSION: Chị Lan (family_with_kids)
   Budget: 3-5 tỷ | Districts: Quận 7, Quận 2, Thủ Đức
   Planned turns: 8
======================================================================

🔄 Generating first query...
💭 AI Reasoning: Bắt đầu khái quát với location preference

--- Turn 1/8 ---
👤 User: Chào bạn! Tôi đang tìm nhà ở Quận 7 cho gia đình.
🤖 Bot: Chào chị! Gia đình chị có bao nhiêu người? Ngân sách...
📊 Intent: chat | Confidence: 0.90 | Time: 2847ms
✅ Response valid

🔄 Generating next query based on conversation...
💭 AI Reasoning: Bot hỏi về family size và budget, cần trả lời

--- Turn 2/8 ---
👤 User: Gia đình tôi 4 người, ngân sách khoảng 3-5 tỷ.
🤖 Bot: Tôi tìm thấy 5 căn hộ phù hợp với yêu cầu...
📊 Intent: search | Confidence: 0.95 | Time: 3142ms
✅ Response valid
...

======================================================================
📊 SESSION SUMMARY
   Total turns: 8
   Successful turns: 7
   Bugs found: 1
   Success rate: 87.5%
======================================================================
```

## Output Files

### Markdown Report: `SESSION_{persona}_{timestamp}.md`

```markdown
# Conversation Session Report: Chị Lan

**Session ID:** family_with_kids_20251103_012345
**Persona Type:** family_with_kids
**Duration:** 2025-11-03T01:23:45 → 2025-11-03T01:35:12

---

## Persona Profile
- **Name:** Chị Lan
- **Age:** 35-40
- **Family Size:** 4 người
- **Budget:** 3-5 tỷ
...

## Conversation Flow

### Turn 1
**User Query:**
```
Chào bạn! Tôi đang tìm nhà ở Quận 7 cho gia đình.
```

**AI Reasoning:**
Bắt đầu khái quát với location preference

**System Response:**
```
Chào chị! Gia đình chị có bao nhiêu người? Ngân sách dự kiến...
```

**Metrics:**
- Intent: chat
- Confidence: 0.90
- Response Time: 2847ms

**✅ No bugs detected**

---

### Turn 2
...

## Summary Statistics
| Metric | Value |
|--------|-------|
| Total Turns | 8 |
| Successful Turns | 7 |
| Total Bugs Found | 1 |
| Success Rate | 87.5% |
| Avg Response Time | 3142ms |
| Avg Confidence | 0.89 |

## Bug Breakdown
- **intent_mismatch**: 1 occurrence(s)
```

### JSON Report: `SESSION_{persona}_{timestamp}.json`

```json
{
  "session_id": "family_with_kids_20251103_012345",
  "persona": {
    "type": "family_with_kids",
    "name": "Chị Lan",
    "budget_range": "3-5 tỷ",
    ...
  },
  "turns": [
    {
      "turn_number": 1,
      "user_query": "Chào bạn! Tôi đang tìm nhà...",
      "system_response": "Chào chị! Gia đình chị...",
      "intent_detected": "chat",
      "confidence": 0.90,
      "response_time_ms": 2847,
      "bugs_detected": [],
      "ai_reasoning": "Bắt đầu khái quát..."
    },
    ...
  ],
  "total_bugs": 1,
  "successful_turns": 7
}
```

## Bug Detection

### Automatic Checks

1. **HTTP errors** - System không trả về response
2. **Intent mismatch** - Detected intent không đúng context
3. **Error messages** - Response chứa "lỗi", "error"
4. **Null values** - Hiển thị "None", "null"

### AI-Powered Analysis

Llama3.2 phân tích semantic quality:
- Response có trả lời đúng câu hỏi?
- Thông tin có liên quan?
- Độ dài phù hợp?
- Logic conversation flow

## Advanced Usage

### Custom Persona

```python
from tests.conversational_ai_tester import (
    ConversationalTester, Persona, PersonaType
)

async def test_custom_persona():
    tester = ConversationalTester()

    persona = Persona(
        type=PersonaType.INVESTOR,
        name="Custom User",
        age_range="30-35",
        family_size=2,
        budget_range="10-15 tỷ",
        preferred_districts=["Quận 1", "Quận 3"],
        requirements=["view đẹp", "penthouse"],
        personality_traits=["yêu cầu cao", "chi tiết"],
        conversation_turns=5
    )

    session = await tester.run_conversation_session(persona)
    report = tester.save_session_report(session)

    await tester.cleanup()
```

### Environment Variables

```bash
# Use different model
OLLAMA_MODEL=qwen2.5:0.5b python3 tests/conversational_ai_tester.py

# Change report directory
BUG_REPORTS_DIR=/path/to/reports python3 tests/conversational_ai_tester.py

# Test different orchestrator
ORCHESTRATOR_URL=http://remote:8090 python3 tests/conversational_ai_tester.py
```

## Example Conversation Flow

```
SESSION: Nhà đầu tư (Anh Hùng)
Budget: 5-10 tỷ | Districts: Quận 2, Quận 7

Turn 1: 👤 "Tôi muốn tìm BĐS để đầu tư ở Quận 2"
        🤖 "Anh quan tâm loại hình nào? Ngân sách?"
        ✅ Valid

Turn 2: 👤 "Căn hộ, ngân sách 5-10 tỷ, quan tâm ROI"
        🤖 "Tìm thấy 3 dự án tiềm năng..."
        ✅ Valid

Turn 3: 👤 "Dự án đầu tiên có giá cho thuê thế nào?"
        🤖 "Cho thuê 30-40tr/tháng, ROI ~5%..."
        ✅ Valid

Turn 4: 👤 "So với Quận 7 thì tiềm năng tăng giá ra sao?"
        🤖 "Quận 2 tăng trưởng 15%/năm, Q7 10%..."
        🐛 Bug: Intent detected = 'chat' (should be 'compare')

Turn 5: 👤 "Pháp lý các dự án này có vấn đề gì không?"
        🤖 "Tất cả đều có sổ hồng đầy đủ..."
        ✅ Valid

Turn 6: 👤 "Tôi muốn đặt lịch xem nhà dự án thứ 2"
        🤖 "Tôi sẽ sắp xếp lịch hẹn cho anh..."
        ✅ Valid

Turn 7: 👤 "Cảm ơn bạn nhiều!"
        🤖 "Rất vui được hỗ trợ anh..."
        ✅ Valid (END)

Summary:
- 7 turns completed
- 1 bug found (intent mismatch)
- 85.7% success rate
```

## Tips

1. **AI Temperature**:
   - 0.7-0.8 cho varied questions
   - 0.3 cho analysis (consistency)

2. **Conversation Length**:
   - 3-5 turns: Quick smoke test
   - 6-8 turns: Standard test
   - 9-12 turns: Deep conversation test

3. **Persona Variety**:
   - Test different demographics
   - Mix budgets (low/mid/high)
   - Vary personality (decisive/hesitant/detail-oriented)

4. **Bug Patterns**:
   - Early turns: Intent detection issues
   - Mid turns: Context loss
   - Late turns: Memory/consistency issues

## Troubleshooting

### No queries generated
```bash
# Check Ollama
curl http://localhost:11434/api/tags | grep llama3.2

# Test generation manually
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"llama3.2","prompt":"Generate a question","stream":false}'
```

### Conversation too short
- AI might generate "Cảm ơn" too early
- Adjust personality_traits to be more inquisitive
- Increase conversation_turns parameter

### Repetitive questions
- Lower temperature (0.6-0.7)
- Improve context in prompts
- Add more personality traits

---

**Created:** 2025-11-03
**Model:** llama3.2
**Status:** Production Ready

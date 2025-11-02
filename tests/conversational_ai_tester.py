"""
🤖 CONVERSATIONAL AI TESTER
============================

Giả lập phiên chat thật của người dùng:
1. Define personas/scenarios với thông số trước (budget, location, family size...)
2. AI generates contextual questions turn-by-turn
3. Maintains conversation history
4. Analyzes responses and continues naturally
5. Detects bugs during conversation flow
6. Creates bug reports for entire conversation

Example conversation:
Turn 1: "Tôi đang tìm nhà ở Quận 7 cho gia đình 4 người"
Turn 2: "Budget khoảng 3-5 tỷ" (based on system asking)
Turn 3: "Căn đầu tiên có view tốt không?" (follow-up on results)
Turn 4: "So với căn thứ 2 thì sao?" (comparison based on context)
...
"""
import asyncio
import httpx
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum


# Configuration
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8090")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
BUG_REPORTS_DIR = os.getenv("BUG_REPORTS_DIR", "/tmp/conversational_bug_reports")


class PersonaType(str, Enum):
    """Các loại persona người dùng"""
    FAMILY_WITH_KIDS = "family_with_kids"  # Gia đình có con nhỏ
    YOUNG_PROFESSIONAL = "young_professional"  # Người trẻ độc thân
    INVESTOR = "investor"  # Nhà đầu tư
    FIRST_TIME_BUYER = "first_time_buyer"  # Người mua lần đầu
    ELDERLY_COUPLE = "elderly_couple"  # Cặp vợ chồng lớn tuổi


@dataclass
class Persona:
    """Thông tin persona người dùng"""
    type: PersonaType
    name: str
    age_range: str
    family_size: int
    budget_range: str  # "3-5 tỷ"
    preferred_districts: List[str]
    requirements: List[str]  # ["gần trường học", "có công viên", "an ninh tốt"]
    personality_traits: List[str]  # ["hỏi nhiều", "quan tâm giá", "chi tiết"]
    conversation_turns: int = 7  # Number of turns in conversation


@dataclass
class ConversationTurn:
    """Một turn trong conversation"""
    turn_number: int
    user_query: str
    system_response: Optional[str]
    intent_detected: Optional[str]
    confidence: float
    response_time_ms: float
    timestamp: str
    bugs_detected: List[Dict] = field(default_factory=list)
    ai_reasoning: Optional[str] = None  # AI's reasoning for next question


@dataclass
class ConversationSession:
    """Toàn bộ conversation session"""
    session_id: str
    persona: Persona
    turns: List[ConversationTurn] = field(default_factory=list)
    total_bugs: int = 0
    started_at: str = ""
    ended_at: str = ""
    successful_turns: int = 0


class ConversationalAI:
    """AI that generates contextual questions in a conversation"""

    def __init__(self, ollama_url: str = OLLAMA_URL, model: str = OLLAMA_MODEL):
        self.ollama_url = ollama_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=90.0)

    async def generate_first_query(self, persona: Persona) -> Tuple[str, str]:
        """
        Generate first query based on persona
        Returns: (query, reasoning)
        """
        prompt = f"""Bạn là {persona.name}, {persona.age_range} tuổi, đang tìm nhà cho {persona.family_size} người.

THÔNG TIN:
- Ngân sách: {persona.budget_range}
- Khu vực quan tâm: {', '.join(persona.preferred_districts)}
- Yêu cầu: {', '.join(persona.requirements)}
- Tính cách: {', '.join(persona.personality_traits)}

NHIỆM VỤ: Tạo câu hỏi ĐẦU TIÊN để bắt đầu tìm nhà với chatbot bất động sản.

YÊU CẦU:
- Câu hỏi tự nhiên, như người Việt thật nói chuyện
- KHÔNG đưa hết thông tin vào câu đầu tiên
- Bắt đầu khái quát, để chatbot hỏi thêm chi tiết
- Dùng tiếng Việt

FORMAT:
QUERY: <câu hỏi>
REASONING: <lý do tại sao hỏi như vậy>
---

Tạo câu hỏi đầu tiên:"""

        try:
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7}
                }
            )

            if response.status_code == 200:
                data = response.json()
                text = data.get("response", "")
                return self._parse_query_response(text)

        except Exception as e:
            print(f"❌ Failed to generate first query: {e}")

        # Fallback
        return (f"Chào bạn! Tôi đang tìm nhà ở {persona.preferred_districts[0]}.",
                "Starting conversation with location preference")

    async def generate_next_query(self,
                                  persona: Persona,
                                  conversation_history: List[ConversationTurn]) -> Tuple[str, str]:
        """
        Generate next query based on conversation history
        Returns: (query, reasoning)
        """
        # Build conversation context
        history_text = self._build_history_text(conversation_history)
        last_response = conversation_history[-1].system_response if conversation_history else ""

        prompt = f"""Bạn là {persona.name}, đang chat với chatbot bất động sản.

THÔNG TIN CỦA BẠN:
- Ngân sách: {persona.budget_range}
- Khu vực: {', '.join(persona.preferred_districts)}
- Yêu cầu: {', '.join(persona.requirements)}
- Tính cách: {', '.join(persona.personality_traits)}
- Số người: {persona.family_size}

LỊCH SỬ TRÒ CHUYỆN:
{history_text}

PHẢN HỒI MỚI NHẤT TỪ CHATBOT:
{last_response[:500]}

NHIỆM VỤ: Tạo câu hỏi TIẾP THEO một cách TỰ NHIÊN.

QUY TẮC:
1. Dựa vào phản hồi chatbot vừa cho để hỏi tiếp
2. Nếu chatbot hỏi thông tin → trả lời cụ thể
3. Nếu chatbot cho kết quả → hỏi chi tiết về BĐS cụ thể
4. Nếu chatbot giải thích → follow-up hoặc chuyển sang vấn đề khác
5. Câu hỏi ngắn gọn, tự nhiên như người Việt
6. Thể hiện tính cách persona (hỏi nhiều/quan tâm giá/chi tiết)

FORMAT:
QUERY: <câu hỏi tiếp theo>
REASONING: <tại sao hỏi như vậy>
---

Tạo câu hỏi tiếp theo:"""

        try:
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.8}
                }
            )

            if response.status_code == 200:
                data = response.json()
                text = data.get("response", "")
                return self._parse_query_response(text)

        except Exception as e:
            print(f"❌ Failed to generate next query: {e}")

        # Fallback
        return ("Cảm ơn bạn!", "Ending conversation")

    def _parse_query_response(self, text: str) -> Tuple[str, str]:
        """Parse AI response to get query and reasoning"""
        query = ""
        reasoning = ""

        for line in text.split("\n"):
            if line.startswith("QUERY:"):
                query = line.replace("QUERY:", "").strip()
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()

        if not query:
            # Fallback: use first non-empty line
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            query = lines[0] if lines else "Xin chào"

        return (query, reasoning or "Generated query")

    def _build_history_text(self, history: List[ConversationTurn]) -> str:
        """Build conversation history text"""
        lines = []
        for turn in history[-3:]:  # Last 3 turns for context
            lines.append(f"Turn {turn.turn_number}:")
            lines.append(f"  Bạn: {turn.user_query}")
            lines.append(f"  Bot: {turn.system_response[:200] if turn.system_response else 'Không có phản hồi'}")
        return "\n".join(lines)

    async def analyze_response(self,
                               response: str,
                               expected_context: str) -> Tuple[bool, List[Dict], str]:
        """
        Analyze if response is valid
        Returns: (is_valid, bugs, analysis_text)
        """
        prompt = f"""Phân tích phản hồi của chatbot bất động sản:

CONTEXT: {expected_context}

PHẢN HỒI:
{response[:800]}

NHIỆM VỤ: Đánh giá phản hồi có HỢP LỆ không.

KIỂM TRA:
1. Có trả lời đúng câu hỏi không?
2. Thông tin có liên quan không?
3. Có lỗi hiển thị (JSON, "None", error message)?
4. Có yêu cầu thêm thông tin hợp lý không?
5. Độ dài phản hồi có phù hợp không?

FORMAT:
VALID: yes/no
BUGS: <mô tả lỗi nếu có>
ANALYSIS: <phân tích chi tiết>
---

Phân tích:"""

        try:
            response_obj = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}
                }
            )

            if response_obj.status_code == 200:
                data = response_obj.json()
                text = data.get("response", "")
                return self._parse_analysis(text, response)

        except Exception as e:
            print(f"⚠️ Analysis failed: {e}")

        return (True, [], "Analysis skipped")

    def _parse_analysis(self, text: str, original_response: str) -> Tuple[bool, List[Dict], str]:
        """Parse analysis result"""
        is_valid = True
        bugs = []
        analysis = ""

        for line in text.split("\n"):
            if line.startswith("VALID:"):
                valid_text = line.replace("VALID:", "").strip().lower()
                is_valid = "yes" in valid_text
            elif line.startswith("BUGS:"):
                bug_text = line.replace("BUGS:", "").strip()
                if bug_text and bug_text.lower() != "none":
                    bugs.append({
                        "type": "ai_detected",
                        "severity": "medium",
                        "message": bug_text,
                        "evidence": original_response[:200]
                    })
            elif line.startswith("ANALYSIS:"):
                analysis = line.replace("ANALYSIS:", "").strip()

        # Additional rule-based checks
        if original_response:
            if "error" in original_response.lower() or "lỗi" in original_response.lower():
                bugs.append({
                    "type": "error_in_response",
                    "severity": "high",
                    "message": "Response chứa thông báo lỗi",
                    "evidence": original_response[:200]
                })

            if "None" in original_response or "null" in original_response.lower():
                bugs.append({
                    "type": "null_value_displayed",
                    "severity": "medium",
                    "message": "Response hiển thị giá trị null/None",
                    "evidence": original_response[:200]
                })

        return (is_valid, bugs, analysis or text)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class ConversationExecutor:
    """Execute conversation with real system"""

    def __init__(self, orchestrator_url: str = ORCHESTRATOR_URL):
        self.orchestrator_url = orchestrator_url
        self.client = httpx.AsyncClient(timeout=120.0)

    async def send_message(self,
                          user_id: str,
                          conversation_id: str,
                          query: str) -> Tuple[Optional[str], Optional[str], float, float]:
        """
        Send message to orchestrator
        Returns: (response, intent, confidence, response_time_ms)
        """
        start_time = time.time()

        try:
            response = await self.client.post(
                f"{self.orchestrator_url}/orchestrate",
                json={
                    "user_id": user_id,
                    "conversation_id": conversation_id,
                    "query": query
                }
            )

            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                return (
                    data.get("response"),
                    data.get("intent"),
                    data.get("confidence", 0.0),
                    elapsed_ms
                )
            else:
                return (
                    f"HTTP Error {response.status_code}",
                    None,
                    0.0,
                    elapsed_ms
                )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            return (
                f"Exception: {str(e)}",
                None,
                0.0,
                elapsed_ms
            )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class ConversationalTester:
    """Main conversational testing system"""

    def __init__(self):
        self.ai = ConversationalAI()
        self.executor = ConversationExecutor()

    def create_personas(self) -> List[Persona]:
        """Create test personas"""
        return [
            Persona(
                type=PersonaType.FAMILY_WITH_KIDS,
                name="Chị Lan",
                age_range="35-40",
                family_size=4,
                budget_range="3-5 tỷ",
                preferred_districts=["Quận 7", "Quận 2", "Thủ Đức"],
                requirements=["gần trường học", "có công viên", "an ninh tốt", "khu compound"],
                personality_traits=["quan tâm chi tiết", "hỏi về tiện ích", "so sánh nhiều"],
                conversation_turns=8
            ),
            Persona(
                type=PersonaType.YOUNG_PROFESSIONAL,
                name="Anh Minh",
                age_range="28-32",
                family_size=1,
                budget_range="2-3 tỷ",
                preferred_districts=["Quận 1", "Quận 3", "Bình Thạnh"],
                requirements=["gần công ty", "có gym", "hiện đại", "giao thông thuận tiện"],
                personality_traits=["quyết đoán", "quan tâm ROI", "hỏi nhanh"],
                conversation_turns=6
            ),
            Persona(
                type=PersonaType.INVESTOR,
                name="Anh Hùng",
                age_range="40-45",
                family_size=2,
                budget_range="5-10 tỷ",
                preferred_districts=["Quận 2", "Quận 7", "Thủ Đức"],
                requirements=["tiềm năng tăng giá", "cho thuê tốt", "pháp lý rõ ràng"],
                personality_traits=["hỏi về đầu tư", "so sánh giá", "phân tích kỹ"],
                conversation_turns=9
            ),
            Persona(
                type=PersonaType.FIRST_TIME_BUYER,
                name="Chị Mai",
                age_range="30-33",
                family_size=2,
                budget_range="2-4 tỷ",
                preferred_districts=["Quận 9", "Thủ Đức", "Bình Dương"],
                requirements=["giá hợp lý", "dễ vay ngân hàng", "thủ tục đơn giản"],
                personality_traits=["hỏi nhiều", "lo ngại thủ tục", "cần hướng dẫn"],
                conversation_turns=10
            ),
        ]

    async def run_conversation_session(self, persona: Persona) -> ConversationSession:
        """Run a complete conversation session"""
        session_id = f"{persona.type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session = ConversationSession(
            session_id=session_id,
            persona=persona,
            started_at=datetime.now().isoformat()
        )

        print(f"\n{'='*70}")
        print(f"🎭 CONVERSATION SESSION: {persona.name} ({persona.type.value})")
        print(f"   Budget: {persona.budget_range} | Districts: {', '.join(persona.preferred_districts)}")
        print(f"   Planned turns: {persona.conversation_turns}")
        print(f"{'='*70}\n")

        conversation_history = []

        # Turn 1: First query
        print(f"🔄 Generating first query...")
        first_query, reasoning = await self.ai.generate_first_query(persona)
        print(f"💭 AI Reasoning: {reasoning}")

        for turn_num in range(1, persona.conversation_turns + 1):
            print(f"\n--- Turn {turn_num}/{persona.conversation_turns} ---")

            # Get query (first turn or generated)
            if turn_num == 1:
                query = first_query
                ai_reasoning = reasoning
            else:
                print(f"🔄 Generating next query based on conversation...")
                query, ai_reasoning = await self.ai.generate_next_query(persona, conversation_history)
                print(f"💭 AI Reasoning: {ai_reasoning}")

            print(f"👤 User: {query}")

            # Send to system
            response, intent, confidence, response_time = await self.executor.send_message(
                user_id=session_id,
                conversation_id=session_id,
                query=query
            )

            print(f"🤖 Bot: {response[:150]}...")
            print(f"📊 Intent: {intent} | Confidence: {confidence:.2f} | Time: {response_time:.0f}ms")

            # Analyze response
            is_valid, bugs, analysis = await self.ai.analyze_response(
                response or "No response",
                expected_context=f"{persona.name} asked: {query}"
            )

            if bugs:
                print(f"🐛 Found {len(bugs)} bug(s):")
                for bug in bugs:
                    print(f"   - {bug['message']}")
            else:
                print(f"✅ Response valid")

            # Record turn
            turn = ConversationTurn(
                turn_number=turn_num,
                user_query=query,
                system_response=response,
                intent_detected=intent,
                confidence=confidence,
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                bugs_detected=bugs,
                ai_reasoning=ai_reasoning
            )

            conversation_history.append(turn)
            session.turns.append(turn)

            if bugs:
                session.total_bugs += len(bugs)
            else:
                session.successful_turns += 1

            # Check if should stop (too many errors or end of conversation)
            if not response or "tạm biệt" in query.lower() or "cảm ơn" in query.lower():
                if turn_num < persona.conversation_turns:
                    print(f"⚠️ Ending conversation early at turn {turn_num}")
                break

            # Small delay between turns
            await asyncio.sleep(2)

        session.ended_at = datetime.now().isoformat()

        # Summary
        print(f"\n{'='*70}")
        print(f"📊 SESSION SUMMARY")
        print(f"   Total turns: {len(session.turns)}")
        print(f"   Successful turns: {session.successful_turns}")
        print(f"   Bugs found: {session.total_bugs}")
        print(f"   Success rate: {session.successful_turns/len(session.turns)*100:.1f}%")
        print(f"{'='*70}\n")

        return session

    def save_session_report(self, session: ConversationSession) -> str:
        """Save conversation session report"""
        os.makedirs(BUG_REPORTS_DIR, exist_ok=True)
        filename = f"SESSION_{session.session_id}.md"
        filepath = os.path.join(BUG_REPORTS_DIR, filename)

        content = f"""# Conversation Session Report: {session.persona.name}

**Session ID:** {session.session_id}
**Persona Type:** {session.persona.type.value}
**Duration:** {session.started_at} → {session.ended_at}

---

## Persona Profile

- **Name:** {session.persona.name}
- **Age:** {session.persona.age_range}
- **Family Size:** {session.persona.family_size} người
- **Budget:** {session.persona.budget_range}
- **Preferred Districts:** {', '.join(session.persona.preferred_districts)}
- **Requirements:**
{chr(10).join(f'  - {req}' for req in session.persona.requirements)}
- **Personality:**
{chr(10).join(f'  - {trait}' for trait in session.persona.personality_traits)}

---

## Conversation Flow

"""

        for turn in session.turns:
            content += f"""### Turn {turn.turn_number}

**User Query:**
```
{turn.user_query}
```

**AI Reasoning:**
{turn.ai_reasoning or 'N/A'}

**System Response:**
```
{turn.system_response[:500] if turn.system_response else 'No response'}
```

**Metrics:**
- Intent: {turn.intent_detected or 'N/A'}
- Confidence: {turn.confidence:.2f}
- Response Time: {turn.response_time_ms:.0f}ms

"""

            if turn.bugs_detected:
                content += "**🐛 Bugs Detected:**\n"
                for bug in turn.bugs_detected:
                    content += f"- **[{bug.get('severity', 'unknown').upper()}]** {bug['message']}\n"
                    content += f"  Evidence: `{bug.get('evidence', 'N/A')[:100]}`\n"
                content += "\n"
            else:
                content += "**✅ No bugs detected**\n\n"

            content += "---\n\n"

        # Summary
        content += f"""## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Turns | {len(session.turns)} |
| Successful Turns | {session.successful_turns} |
| Total Bugs Found | {session.total_bugs} |
| Success Rate | {session.successful_turns/len(session.turns)*100:.1f}% |
| Avg Response Time | {sum(t.response_time_ms for t in session.turns) / len(session.turns):.0f}ms |
| Avg Confidence | {sum(t.confidence for t in session.turns) / len(session.turns):.2f} |

## Bug Breakdown

"""

        # Count bugs by type
        bug_types = {}
        for turn in session.turns:
            for bug in turn.bugs_detected:
                bug_type = bug.get('type', 'unknown')
                bug_types[bug_type] = bug_types.get(bug_type, 0) + 1

        if bug_types:
            for bug_type, count in sorted(bug_types.items(), key=lambda x: x[1], reverse=True):
                content += f"- **{bug_type}**: {count} occurrence(s)\n"
        else:
            content += "No bugs found in this conversation.\n"

        content += f"""

---

**Generated by Conversational AI Tester**
**Full conversation JSON available for analysis**
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Also save JSON
        json_filepath = filepath.replace('.md', '.json')
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(session), f, indent=2, ensure_ascii=False, default=str)

        return filepath

    async def run_all_personas(self):
        """Run tests for all personas"""
        personas = self.create_personas()

        print("🤖 CONVERSATIONAL AI TESTER")
        print("="*70)
        print(f"Testing {len(personas)} personas")
        print(f"Model: {OLLAMA_MODEL}")
        print(f"Orchestrator: {ORCHESTRATOR_URL}")
        print("="*70)

        all_sessions = []

        for i, persona in enumerate(personas, 1):
            print(f"\n\n🎭 Persona {i}/{len(personas)}")
            session = await self.run_conversation_session(persona)
            all_sessions.append(session)

            # Save report
            report_path = self.save_session_report(session)
            print(f"📝 Session report saved: {report_path}")

            # Delay between personas
            if i < len(personas):
                print(f"\n⏳ Waiting 5 seconds before next persona...")
                await asyncio.sleep(5)

        # Final summary
        print(f"\n\n{'='*70}")
        print("📊 FINAL SUMMARY")
        print(f"{'='*70}")
        print(f"Total personas tested: {len(all_sessions)}")
        print(f"Total conversations: {len(all_sessions)}")
        print(f"Total turns: {sum(len(s.turns) for s in all_sessions)}")
        print(f"Total bugs found: {sum(s.total_bugs for s in all_sessions)}")
        print(f"Reports directory: {BUG_REPORTS_DIR}")
        print(f"{'='*70}\n")

    async def cleanup(self):
        """Cleanup resources"""
        await self.ai.close()
        await self.executor.close()


async def main():
    """Main entry point"""
    tester = ConversationalTester()

    try:
        await tester.run_all_personas()
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

"""
Conversation Evaluation - Practical Sample
Runs 10 detailed scenarios to evaluate system intelligence
"""
import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import List, Dict

# 10 representative scenarios covering different user types
EVALUATION_SCENARIOS = [
    {
        "persona": "Cặp vợ chồng trẻ, lần đầu mua nhà",
        "budget": "2-3 tỷ",
        "characteristics": "Cần tư vấn toàn diện, có nhiều câu hỏi cơ bản",
        "conversation": [
            ("Xin chào, tôi muốn tìm căn hộ cho gia đình nhỏ", "chat"),
            ("Ngân sách của tôi khoảng 2-3 tỷ, quận nào phù hợp?", "search"),
            ("Tìm căn 2 phòng ngủ quận 7 dưới 3 tỷ cho tôi", "search"),
            ("Căn nào có giá tốt nhất?", "search"),  # Test context
            ("Giá 2.5 tỷ cho căn 70m² có hợp lý không?", "price_analysis"),
            ("So sánh căn đó với căn ở Masteri Thảo Điền", "compare"),  # Test "căn đó" context
            ("Quận 7 có trường học nào gần không?", "location_insights"),
            ("Thủ tục mua nhà cần giấy tờ gì?", "legal_guidance")
        ],
        "context_tests": [
            {"turn": 4, "keyword": "Căn nào", "refers_to": "previous search results (turn 3)"},
            {"turn": 6, "keyword": "căn đó", "refers_to": "previous property mentioned (turn 4-5)"}
        ]
    },
    {
        "persona": "Nhà đầu tư có kinh nghiệm",
        "budget": "5-10 tỷ",
        "characteristics": "Quan tâm ROI, tiềm năng sinh lời, phân tích kỹ",
        "conversation": [
            ("Nên đầu tư vào quận 2 hay quận 7 với 5 tỷ?", "investment_advice"),
            ("Cho tôi xem các dự án quận 2 trong năm tới", "search"),
            ("So sánh Vinhomes Grand Park với The Sun Avenue về tiềm năng", "compare"),
            ("Giá căn hộ quận 2 tăng bao nhiêu % năm qua?", "price_analysis"),
            ("Khu vực nào có hạ tầng phát triển mạnh?", "location_insights")
        ],
        "context_tests": [
            {"turn": 2, "keyword": "quận 2", "refers_to": "investment area from turn 1"}
        ]
    },
    {
        "persona": "Gia đình có con nhỏ",
        "budget": "3-4 tỷ",
        "characteristics": "Ưu tiên trường học, công viên, an toàn",
        "conversation": [
            ("Tìm căn 3 phòng ngủ gần trường quốc tế quận Thủ Đức", "search"),
            ("Khu nào có nhiều trường học tốt?", "location_insights"),
            ("So sánh Vinhomes Grand Park với Mizuki Park về tiện ích gia đình", "compare"),
            ("Giá bao nhiêu là hợp lý cho căn 90m² gần trường?", "price_analysis")
        ],
        "context_tests": [
            {"turn": 3, "keyword": "Vinhomes Grand Park", "refers_to": "search area from turns 1-2"}
        ]
    },
    {
        "persona": "Người về hưu",
        "budget": "2-3 tỷ",
        "characteristics": "Ưu tiên yên tĩnh, gần bệnh viện, không vội",
        "conversation": [
            ("Tôi muốn tìm căn hộ yên tĩnh cho người cao tuổi", "search"),
            ("Quận nào có nhiều bệnh viện và gần công viên?", "location_insights"),
            ("Thủ tục mua nhà cho người già cần giấy tờ gì đặc biệt?", "legal_guidance"),
            ("Có nên mua căn chung cư hay nhà riêng?", "investment_advice")
        ],
        "context_tests": []
    },
    {
        "persona": "Sinh viên thuê nhà",
        "budget": "3-5 triệu/tháng",
        "characteristics": "Ngân sách thấp, cần gần trường, tiện ích",
        "conversation": [
            ("Cho thuê phòng gần ĐH Bách Khoa dưới 5 triệu", "search"),
            ("Khu vực Thủ Đức có quán ăn và siêu thị không?", "location_insights"),
            ("So sánh giá thuê khu A với khu B", "compare"),
            ("5 triệu thuê phòng 25m² có hợp lý không?", "price_analysis")
        ],
        "context_tests": [
            {"turn": 3, "keyword": "khu A với khu B", "refers_to": "areas mentioned in previous turns"}
        ]
    },
    {
        "persona": "Người nước ngoài mua nhà tại VN",
        "budget": "$150,000-200,000",
        "characteristics": "Cần thông tin pháp lý, ưu tiên khu expat",
        "conversation": [
            ("Người nước ngoài có thể mua nhà ở Việt Nam không?", "legal_guidance"),
            ("Tìm căn hộ quận 2 gần trường quốc tế", "search"),
            ("Thủ tục mua nhà cho người nước ngoài như thế nào?", "legal_guidance"),
            ("Có nên mua ở khu Thảo Điền hay Vinhomes Central Park?", "investment_advice")
        ],
        "context_tests": []
    },
    {
        "persona": "Người mua nhà để cho thuê",
        "budget": "4-6 tỷ",
        "characteristics": "Quan tâm lợi suất cho thuê, vị trí đắc địa",
        "conversation": [
            ("Nên mua căn nào để cho thuê lợi nhuận cao?", "investment_advice"),
            ("Tìm căn 2PN gần trung tâm quận 1, 2, 7", "search"),
            ("So sánh giá cho thuê giữa quận 1 và quận 7", "compare"),
            ("Căn 80m² giá 5 tỷ cho thuê 20 triệu/tháng có tốt không?", "price_analysis")
        ],
        "context_tests": [
            {"turn": 4, "keyword": "Căn 80m²", "refers_to": "properties from search turns 2-3"}
        ]
    },
    {
        "persona": "Người chỉ hỏi thăm, chưa quyết định",
        "budget": "Chưa xác định",
        "characteristics": "Câu hỏi chung chung, khám phá thị trường",
        "conversation": [
            ("Thị trường bất động sản hiện nay ra sao?", "chat"),
            ("Giá nhà đang tăng hay giảm?", "price_analysis"),
            ("Nên đầu tư bây giờ hay đợi sau?", "investment_advice"),
            ("Bạn có thể tư vấn cho tôi không?", "chat")
        ],
        "context_tests": []
    },
    {
        "persona": "Người bán nhà",
        "budget": "N/A",
        "characteristics": "Cần định giá, marketing, tư vấn bán",
        "conversation": [
            ("Tôi muốn bán căn hộ 2PN quận 7", "chat"),
            ("Giá bao nhiêu là hợp lý để bán nhanh?", "price_analysis"),
            ("Thủ tục bán nhà cần chuẩn bị những gì?", "legal_guidance"),
            ("So sánh giá căn tôi với thị trường", "compare")
        ],
        "context_tests": [
            {"turn": 4, "keyword": "căn tôi", "refers_to": "user's property from turn 1"}
        ]
    },
    {
        "persona": "Người hỏi về nhiều chủ đề khác nhau",
        "budget": "Varied",
        "characteristics": "Test khả năng chuyển đổi context",
        "conversation": [
            ("Tìm căn hộ quận 2", "search"),
            ("Thủ tục mua nhà như thế nào?", "legal_guidance"),
            ("Quay lại vấn đề tìm nhà, căn nào giá tốt?", "search"),  # Context switch
            ("Bạn tên là gì?", "chat"),
            ("Về căn hộ vừa nói, có gần trường học không?", "location_insights")  # Back to property
        ],
        "context_tests": [
            {"turn": 3, "keyword": "Quay lại vấn đề tìm nhà", "refers_to": "search from turn 1"},
            {"turn": 5, "keyword": "căn hộ vừa nói", "refers_to": "property from turn 3"}
        ]
    }
]

class ConversationEvaluator:
    def __init__(self, orchestrator_url: str = "http://localhost:8090"):
        self.orchestrator_url = orchestrator_url
        self.results = []

    async def run_conversation(self, scenario: Dict, session_num: int) -> Dict:
        """Run a single conversation scenario"""
        session_id = f"eval_session_{session_num:03d}"
        conversation = scenario["conversation"]

        print(f"\n{'='*80}")
        print(f"📋 Session {session_num}/10: {scenario['persona']}")
        print(f"💰 Budget: {scenario['budget']}")
        print(f"📝 Characteristics: {scenario['characteristics']}")
        print(f"{'='*80}\n")

        history = []
        turns_data = []

        async with httpx.AsyncClient(timeout=60.0) as client:
            for turn_num, (message, expected_intent) in enumerate(conversation, 1):
                print(f"\n{'─'*80}")
                print(f"Turn {turn_num}/{len(conversation)}")
                print(f"👤 User: {message}")

                start_time = time.time()

                try:
                    request_data = {
                        "user_id": session_id,
                        "query": message,
                        "conversation_id": session_id,
                        "metadata": {
                            "turn": turn_num,
                            "history": history[-6:]  # Last 3 exchanges (6 messages)
                        }
                    }

                    response = await client.post(
                        f"{self.orchestrator_url}/orchestrate",
                        json=request_data
                    )

                    elapsed_ms = (time.time() - start_time) * 1000

                    if response.status_code == 200:
                        data = response.json()
                        intent = data.get("intent", "unknown")
                        confidence = data.get("confidence", 0)
                        ai_response = data.get("response", "")

                        # Intent match
                        intent_match = intent.lower() == expected_intent.lower()
                        status = "✅" if intent_match else "❌"

                        print(f"🤖 AI: {ai_response[:200]}{'...' if len(ai_response) > 200 else ''}")
                        print(f"\n📊 Intent: {intent} (expected: {expected_intent}) {status}")
                        print(f"   Confidence: {confidence:.2f}")
                        print(f"   Time: {elapsed_ms:.0f}ms")

                        # Store turn data
                        turn_data = {
                            "turn": turn_num,
                            "user_message": message,
                            "ai_response": ai_response,
                            "expected_intent": expected_intent,
                            "detected_intent": intent,
                            "confidence": confidence,
                            "intent_match": intent_match,
                            "response_time_ms": elapsed_ms
                        }
                        turns_data.append(turn_data)

                        # Update history
                        history.append({"role": "user", "content": message})
                        history.append({"role": "assistant", "content": ai_response})

                    else:
                        print(f"❌ HTTP Error: {response.status_code}")
                        turns_data.append({
                            "turn": turn_num,
                            "user_message": message,
                            "error": f"HTTP {response.status_code}",
                            "expected_intent": expected_intent
                        })

                except Exception as e:
                    print(f"❌ Exception: {str(e)}")
                    turns_data.append({
                        "turn": turn_num,
                        "user_message": message,
                        "error": str(e),
                        "expected_intent": expected_intent
                    })

                # Brief pause between turns
                await asyncio.sleep(0.5)

        # Calculate session metrics
        total_turns = len(turns_data)
        successful_turns = [t for t in turns_data if "error" not in t]
        intent_matches = [t for t in successful_turns if t.get("intent_match")]

        session_result = {
            "session_id": session_id,
            "persona": scenario["persona"],
            "budget": scenario["budget"],
            "characteristics": scenario["characteristics"],
            "total_turns": total_turns,
            "successful_turns": len(successful_turns),
            "intent_matches": len(intent_matches),
            "intent_accuracy": len(intent_matches) / total_turns if total_turns > 0 else 0,
            "avg_response_time_ms": sum(t.get("response_time_ms", 0) for t in successful_turns) / len(successful_turns) if successful_turns else 0,
            "turns": turns_data,
            "context_tests": scenario.get("context_tests", [])
        }

        print(f"\n{'─'*80}")
        print(f"📊 Session Summary:")
        print(f"   Intent Accuracy: {session_result['intent_accuracy']*100:.1f}% ({len(intent_matches)}/{total_turns})")
        print(f"   Avg Response Time: {session_result['avg_response_time_ms']:.0f}ms")
        print(f"{'─'*80}\n")

        return session_result

    async def run_all_evaluations(self):
        """Run all 10 evaluation scenarios"""
        print("\n" + "="*80)
        print("🔥 CONVERSATION EVALUATION - 10 Scenarios")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        for i, scenario in enumerate(EVALUATION_SCENARIOS, 1):
            result = await self.run_conversation(scenario, i)
            self.results.append(result)

        # Generate comprehensive report
        await self.generate_report()

    async def generate_report(self):
        """Generate detailed evaluation report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Calculate overall metrics
        total_turns = sum(r["total_turns"] for r in self.results)
        total_intent_matches = sum(r["intent_matches"] for r in self.results)
        overall_accuracy = total_intent_matches / total_turns if total_turns > 0 else 0
        avg_response_time = sum(r["avg_response_time_ms"] for r in self.results) / len(self.results) if self.results else 0

        # Save detailed JSON
        json_path = f"/tmp/conversation_evaluation_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "total_sessions": len(self.results),
                    "total_turns": total_turns,
                    "overall_intent_accuracy": overall_accuracy,
                    "avg_response_time_ms": avg_response_time
                },
                "sessions": self.results
            }, f, ensure_ascii=False, indent=2)

        # Generate markdown summary
        md_path = f"/tmp/conversation_evaluation_summary_{timestamp}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Conversation Evaluation Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Overall Metrics\n\n")
            f.write(f"- **Total Sessions**: {len(self.results)}\n")
            f.write(f"- **Total Turns**: {total_turns}\n")
            f.write(f"- **Overall Intent Accuracy**: {overall_accuracy*100:.1f}%\n")
            f.write(f"- **Average Response Time**: {avg_response_time:.0f}ms\n\n")

            f.write(f"## Session Results\n\n")
            for i, result in enumerate(self.results, 1):
                f.write(f"### Session {i}: {result['persona']}\n\n")
                f.write(f"- **Budget**: {result['budget']}\n")
                f.write(f"- **Intent Accuracy**: {result['intent_accuracy']*100:.1f}% ({result['intent_matches']}/{result['total_turns']})\n")
                f.write(f"- **Avg Response Time**: {result['avg_response_time_ms']:.0f}ms\n\n")

                # Conversation summary
                f.write("**Conversation Flow:**\n\n")
                for turn in result["turns"]:
                    match_icon = "✅" if turn.get("intent_match") else "❌"
                    if "error" in turn:
                        f.write(f"- Turn {turn['turn']}: ❌ ERROR - {turn['user_message'][:50]}...\n")
                    else:
                        f.write(f"- Turn {turn['turn']}: {match_icon} `{turn['detected_intent']}` (expected: `{turn['expected_intent']}`) - {turn['user_message'][:50]}...\n")
                f.write("\n")

                # Context tests
                if result.get("context_tests"):
                    f.write("**Context Tests:**\n\n")
                    for ctx_test in result["context_tests"]:
                        f.write(f"- Turn {ctx_test['turn']}: \"{ctx_test['keyword']}\" should refer to \"{ctx_test['refers_to']}\"\n")
                    f.write("\n")

                f.write("---\n\n")

            # Analysis section
            f.write("## Analysis\n\n")
            f.write("### Strengths\n\n")
            high_performers = [r for r in self.results if r["intent_accuracy"] >= 0.75]
            if high_performers:
                f.write(f"- {len(high_performers)}/10 sessions achieved ≥75% intent accuracy\n")
                f.write("- High-performing personas:\n")
                for hp in high_performers[:3]:
                    f.write(f"  - {hp['persona']}: {hp['intent_accuracy']*100:.1f}%\n")
            f.write("\n")

            f.write("### Weaknesses\n\n")
            low_performers = [r for r in self.results if r["intent_accuracy"] < 0.75]
            if low_performers:
                f.write(f"- {len(low_performers)}/10 sessions had <75% intent accuracy\n")
                f.write("- Challenging personas:\n")
                for lp in low_performers[:3]:
                    f.write(f"  - {lp['persona']}: {lp['intent_accuracy']*100:.1f}%\n")
            f.write("\n")

            f.write("### Recommendations\n\n")
            f.write("1. **Prompt Improvement**: Focus on failing intent types\n")
            f.write("2. **Context Handling**: Enhance conversation history management\n")
            f.write("3. **Response Quality**: Improve Vietnamese response generation\n")
            f.write("4. **Fine-tuning Data**: Use this evaluation data for model fine-tuning\n")

        print("\n" + "="*80)
        print("✅ EVALUATION COMPLETE!")
        print("="*80)
        print(f"\n📊 Overall Intent Accuracy: {overall_accuracy*100:.1f}%")
        print(f"⚡ Avg Response Time: {avg_response_time:.0f}ms")
        print(f"\n📁 Detailed Report: {json_path}")
        print(f"📄 Summary: {md_path}")
        print("="*80 + "\n")

async def main():
    evaluator = ConversationEvaluator()
    await evaluator.run_all_evaluations()

if __name__ == "__main__":
    asyncio.run(main())

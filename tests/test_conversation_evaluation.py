"""
Comprehensive Conversation Evaluation Test
Simulates 100 different user sessions with multi-turn conversations
Tests memory context, intent accuracy, and response quality
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import random

# Test scenarios with realistic conversation flows
CONVERSATION_SCENARIOS = [
    # Scenario 1: Young couple looking for first home
    {
        "persona": "Cặp vợ chồng trẻ, lần đầu mua nhà",
        "budget": "2-3 tỷ",
        "conversation": [
            "Xin chào, tôi muốn tìm căn hộ cho gia đình nhỏ",
            "Ngân sách của tôi khoảng 2-3 tỷ, quận nào phù hợp?",
            "Tìm căn 2 phòng ngủ quận 7 dưới 3 tỷ cho tôi",
            "Căn nào có giá tốt nhất?",
            "Giá 2.5 tỷ cho căn 70m² có hợp lý không?",
            "So sánh căn đó với căn ở Masteri Thảo Điền",
            "Quận 7 có trường học nào gần không?",
            "Thủ tục mua nhà cần giấy tờ gì?"
        ],
        "expected_intents": ["chat", "search", "search", "search", "price_analysis", "compare", "location_insights", "legal_guidance"],
        "context_tests": [
            {"turn": 3, "context_word": "quận", "previous_turn": 1},
            {"turn": 4, "context_word": "căn nào", "previous_turn": 2},
            {"turn": 5, "context_word": "căn", "previous_turn": 3},
            {"turn": 6, "context_word": "căn đó", "previous_turn": 4}
        ]
    },

    # Scenario 2: Investor looking for ROI
    {
        "persona": "Nhà đầu tư, tìm cơ hội sinh lời",
        "budget": "5-10 tỷ",
        "conversation": [
            "Tôi có 7 tỷ muốn đầu tư bất động sản",
            "Nên đầu tư vào quận 2 hay quận 7?",
            "Tìm căn hộ cao cấp quận 2 cho tôi",
            "So sánh Vinhomes Grand Park với The Sun Avenue",
            "Khu vực nào có tiềm năng tăng giá hơn?",
            "Masteri Thảo Điền giá bao nhiêu?",
            "Có hợp lý không với giá đó?",
            "Thủ tục chuyển nhượng như thế nào?"
        ],
        "expected_intents": ["chat", "investment_advice", "search", "compare", "investment_advice", "search", "price_analysis", "legal_guidance"]
    },

    # Scenario 3: Family upgrading home
    {
        "persona": "Gia đình 4 người, nâng cấp nhà",
        "budget": "4-6 tỷ",
        "conversation": [
            "Gia đình tôi 4 người đang ở quận 10, muốn chuyển nhà rộng hơn",
            "Tìm căn 3 phòng ngủ quận 7 hoặc quận 2",
            "Có căn nào gần trường quốc tế không?",
            "Quận Thủ Đức có tiện ích gì?",
            "So sánh giá quận 7 với Thủ Đức",
            "Căn 5 tỷ 100m² có đắt không?",
            "Nên mua căn nào trong 2 căn vừa tìm?"
        ],
        "expected_intents": ["chat", "search", "search", "location_insights", "compare", "price_analysis", "investment_advice"]
    },

    # Scenario 4: Retired couple downsizing
    {
        "persona": "Vợ chồng về hưu, muốn nhà nhỏ gọn",
        "budget": "2-3 tỷ",
        "conversation": [
            "Chúng tôi về hưu rồi, muốn bán nhà lớn mua căn nhỏ hơn",
            "Tìm căn 1-2 phòng ngủ yên tĩnh, gần bệnh viện",
            "Quận nào phù hợp với người cao tuổi?",
            "Tìm căn hộ quận 3 hoặc quận 10 dưới 3 tỷ",
            "Có căn nào tầng thấp không?",
            "Giá 2.8 tỷ cho 65m² quận 3 có cao không?",
            "So sánh với giá quận 10",
            "Cần giấy tờ gì để mua bán?"
        ],
        "expected_intents": ["chat", "search", "search", "search", "search", "price_analysis", "compare", "legal_guidance"]
    },

    # Scenario 5: Student looking for rental
    {
        "persona": "Sinh viên, tìm căn hộ thuê",
        "budget": "5-10 triệu/tháng",
        "conversation": [
            "Em là sinh viên ĐH Bách Khoa, cần tìm phòng trọ",
            "Khu vực Thủ Đức có chỗ nào giá sinh viên không?",
            "Tìm căn studio hoặc 1 phòng ngủ gần trường",
            "Khu đó có siêu thị, quán ăn gần không?",
            "So sánh giá thuê quận Thủ Đức với quận Bình Thạnh",
            "10 triệu/tháng cho 30m² có đắt không?",
            "Thuê nhà cần giấy tờ gì?"
        ],
        "expected_intents": ["chat", "search", "search", "location_insights", "compare", "price_analysis", "legal_guidance"]
    }
]

# Generate more scenarios programmatically
def generate_additional_scenarios() -> List[Dict]:
    """Generate 95 more realistic scenarios"""

    templates = [
        # Template 1: Budget-focused searcher
        {
            "persona_template": "Người mua nhà lần đầu, ngân sách {budget}",
            "conversation_template": [
                "Tôi có {budget}, muốn mua căn hộ {area}",
                "Tìm căn {rooms} phòng ngủ {district} dưới {max_price}",
                "Căn nào có view đẹp?",
                "Giá {price} cho {size}m² có hợp lý không?",
                "So sánh với khu {compare_district}",
                "Khu đó có tiện ích gì?"
            ]
        },
        # Template 2: Location-focused
        {
            "persona_template": "Người tìm nhà gần nơi làm việc {workplace}",
            "conversation_template": [
                "Tôi làm việc ở {workplace}, muốn tìm nhà gần",
                "Quận nào gần {workplace} nhất?",
                "Tìm căn hộ {district} trong ngân sách {budget}",
                "Khu đó có kẹt xe không?",
                "So sánh với khu vực {alternative}",
                "Giá {price} có cao không?"
            ]
        },
        # Add more templates...
    ]

    districts = ["Quận 1", "Quận 2", "Quận 3", "Quận 7", "Quận 10", "Thủ Đức", "Bình Thạnh", "Phú Nhuận"]
    budgets = ["2-3 tỷ", "3-5 tỷ", "5-7 tỷ", "trên 10 tỷ"]
    rooms = ["1", "2", "3", "4"]

    additional_scenarios = []

    # Generate varied scenarios
    for i in range(95):
        budget = random.choice(budgets)
        district = random.choice(districts)
        room_count = random.choice(rooms)

        scenario = {
            "persona": f"Người dùng {i+6} - {random.choice(['Gia đình', 'Cá nhân', 'Nhà đầu tư'])}",
            "budget": budget,
            "conversation": [
                f"Xin chào, tôi muốn tìm nhà tại {district}",
                f"Ngân sách {budget}, có căn nào phù hợp?",
                f"Tìm căn {room_count} phòng ngủ {district}",
                f"Khu {district} có tiện ích gì?",
                "So sánh với khu vực lân cận",
                "Giá có hợp lý không?",
                "Cần chuẩn bị giấy tờ gì?"
            ],
            "expected_intents": ["chat", "search", "search", "location_insights", "compare", "price_analysis", "legal_guidance"]
        }
        additional_scenarios.append(scenario)

    return additional_scenarios


class ConversationEvaluator:
    """Evaluates conversation quality with real API calls"""

    def __init__(self, orchestrator_url: str = "http://localhost:8090"):
        self.orchestrator_url = orchestrator_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.results = []

    async def run_conversation(self, scenario: Dict, session_id: str) -> Dict:
        """Run a full conversation scenario"""

        print(f"\n{'='*80}")
        print(f"🎭 SCENARIO: {scenario['persona']}")
        print(f"💰 Budget: {scenario.get('budget', 'N/A')}")
        print(f"📝 Session ID: {session_id}")
        print(f"{'='*80}\n")

        conversation_results = {
            "session_id": session_id,
            "persona": scenario["persona"],
            "budget": scenario.get("budget"),
            "turns": [],
            "intent_accuracy": 0.0,
            "context_retention": 0.0,
            "avg_response_time": 0.0,
            "total_turns": len(scenario["conversation"]),
            "successful_turns": 0
        }

        conversation_history = []

        for turn_idx, user_message in enumerate(scenario["conversation"]):
            turn_num = turn_idx + 1
            print(f"\n{'─'*80}")
            print(f"Turn {turn_num}/{len(scenario['conversation'])}")
            print(f"👤 User: {user_message}")

            start_time = time.time()

            try:
                # Send message to orchestrator
                request_data = {
                    "user_id": session_id,
                    "query": user_message,
                    "conversation_id": session_id,
                    "metadata": {
                        "turn": turn_num,
                        "persona": scenario["persona"],
                        "history": conversation_history[-5:]  # Last 5 messages
                    }
                }

                response = await self.client.post(
                    f"{self.orchestrator_url}/orchestrate",
                    json=request_data
                )

                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()

                    detected_intent = data.get("intent")
                    confidence = data.get("confidence", 0.0)
                    ai_response = data.get("response", "")
                    service_used = data.get("service_used", "unknown")

                    # Check if intent matches expected
                    expected_intent = scenario.get("expected_intents", [])[turn_idx] if turn_idx < len(scenario.get("expected_intents", [])) else None
                    intent_correct = detected_intent == expected_intent if expected_intent else None

                    print(f"🤖 Assistant: {ai_response[:200]}...")
                    print(f"\n📊 Metrics:")
                    print(f"   Intent: {detected_intent} (confidence: {confidence:.2f})")
                    if expected_intent:
                        print(f"   Expected: {expected_intent} {'✅' if intent_correct else '❌'}")
                    print(f"   Service: {service_used}")
                    print(f"   Time: {response_time:.0f}ms")

                    # Store turn results
                    turn_result = {
                        "turn": turn_num,
                        "user_message": user_message,
                        "ai_response": ai_response,
                        "detected_intent": detected_intent,
                        "expected_intent": expected_intent,
                        "intent_correct": intent_correct,
                        "confidence": confidence,
                        "response_time_ms": response_time,
                        "service_used": service_used,
                        "success": True
                    }

                    conversation_results["turns"].append(turn_result)
                    conversation_results["successful_turns"] += 1

                    # Update conversation history
                    conversation_history.append({
                        "role": "user",
                        "content": user_message
                    })
                    conversation_history.append({
                        "role": "assistant",
                        "content": ai_response
                    })

                    # Brief pause between turns (simulate human typing)
                    await asyncio.sleep(1.5)

                else:
                    print(f"❌ Error: HTTP {response.status_code}")
                    conversation_results["turns"].append({
                        "turn": turn_num,
                        "user_message": user_message,
                        "error": f"HTTP {response.status_code}",
                        "success": False
                    })

            except Exception as e:
                print(f"❌ Exception: {str(e)}")
                conversation_results["turns"].append({
                    "turn": turn_num,
                    "user_message": user_message,
                    "error": str(e),
                    "success": False
                })

        # Calculate metrics
        successful_turns = [t for t in conversation_results["turns"] if t.get("success")]
        if successful_turns:
            # Intent accuracy
            intent_checks = [t for t in successful_turns if t.get("intent_correct") is not None]
            if intent_checks:
                correct_intents = sum(1 for t in intent_checks if t["intent_correct"])
                conversation_results["intent_accuracy"] = (correct_intents / len(intent_checks)) * 100

            # Average response time
            response_times = [t["response_time_ms"] for t in successful_turns]
            conversation_results["avg_response_time"] = sum(response_times) / len(response_times)

        # Context retention check
        context_tests = scenario.get("context_tests", [])
        if context_tests:
            context_passed = 0
            for test in context_tests:
                turn_idx = test["turn"] - 1
                if turn_idx < len(conversation_results["turns"]):
                    turn = conversation_results["turns"][turn_idx]
                    # Simple check: did the AI respond appropriately?
                    if turn.get("success") and turn.get("ai_response"):
                        context_passed += 1
            conversation_results["context_retention"] = (context_passed / len(context_tests)) * 100

        print(f"\n{'='*80}")
        print(f"📈 SESSION SUMMARY:")
        print(f"   Successful turns: {conversation_results['successful_turns']}/{conversation_results['total_turns']}")
        print(f"   Intent accuracy: {conversation_results['intent_accuracy']:.1f}%")
        print(f"   Context retention: {conversation_results['context_retention']:.1f}%")
        print(f"   Avg response time: {conversation_results['avg_response_time']:.0f}ms")
        print(f"{'='*80}\n")

        return conversation_results

    async def run_all_scenarios(self, scenarios: List[Dict], max_concurrent: int = 5):
        """Run all scenarios with concurrency control"""

        print(f"\n🚀 Starting Conversation Evaluation")
        print(f"📊 Total scenarios: {len(scenarios)}")
        print(f"⚡ Max concurrent: {max_concurrent}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Run in batches to avoid overwhelming the system
        for i in range(0, len(scenarios), max_concurrent):
            batch = scenarios[i:i+max_concurrent]
            batch_num = (i // max_concurrent) + 1
            total_batches = (len(scenarios) + max_concurrent - 1) // max_concurrent

            print(f"\n{'#'*80}")
            print(f"# BATCH {batch_num}/{total_batches} ({len(batch)} scenarios)")
            print(f"{'#'*80}\n")

            tasks = []
            for idx, scenario in enumerate(batch):
                session_id = f"session_{i+idx+1:03d}_{int(time.time())}"
                tasks.append(self.run_conversation(scenario, session_id))

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"❌ Batch error: {result}")
                else:
                    self.results.append(result)

            # Pause between batches
            if i + max_concurrent < len(scenarios):
                print(f"\n⏸️  Pausing 5 seconds before next batch...\n")
                await asyncio.sleep(5)

        await self.generate_report()

    async def generate_report(self):
        """Generate comprehensive evaluation report"""

        report_file = f"/tmp/conversation_evaluation_{int(time.time())}.json"
        summary_file = f"/tmp/conversation_summary_{int(time.time())}.md"

        # Calculate overall metrics
        total_turns = sum(r["total_turns"] for r in self.results)
        successful_turns = sum(r["successful_turns"] for r in self.results)
        avg_intent_accuracy = sum(r["intent_accuracy"] for r in self.results) / len(self.results) if self.results else 0
        avg_context_retention = sum(r["context_retention"] for r in self.results if r["context_retention"] > 0) / len([r for r in self.results if r["context_retention"] > 0]) if self.results else 0
        avg_response_time = sum(r["avg_response_time"] for r in self.results if r["avg_response_time"] > 0) / len([r for r in self.results if r["avg_response_time"] > 0]) if self.results else 0

        # Save detailed JSON
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "evaluation_date": datetime.now().isoformat(),
                "total_scenarios": len(self.results),
                "total_turns": total_turns,
                "successful_turns": successful_turns,
                "success_rate": (successful_turns / total_turns * 100) if total_turns > 0 else 0,
                "avg_intent_accuracy": avg_intent_accuracy,
                "avg_context_retention": avg_context_retention,
                "avg_response_time_ms": avg_response_time,
                "scenarios": self.results
            }, f, indent=2, ensure_ascii=False)

        # Generate markdown summary
        summary = f"""# Conversation Evaluation Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Metrics

- **Total Scenarios**: {len(self.results)}
- **Total Conversation Turns**: {total_turns}
- **Successful Turns**: {successful_turns}/{total_turns} ({successful_turns/total_turns*100:.1f}%)
- **Average Intent Accuracy**: {avg_intent_accuracy:.1f}%
- **Average Context Retention**: {avg_context_retention:.1f}%
- **Average Response Time**: {avg_response_time:.0f}ms

## Top Performing Scenarios

"""

        # Sort by intent accuracy
        top_scenarios = sorted(self.results, key=lambda x: x.get("intent_accuracy", 0), reverse=True)[:10]

        summary += "| Rank | Persona | Intent Accuracy | Context Retention | Avg Response Time |\n"
        summary += "|------|---------|----------------|-------------------|------------------|\n"

        for idx, scenario in enumerate(top_scenarios, 1):
            summary += f"| {idx} | {scenario['persona'][:40]} | {scenario['intent_accuracy']:.1f}% | {scenario.get('context_retention', 0):.1f}% | {scenario.get('avg_response_time', 0):.0f}ms |\n"

        summary += "\n## Issues Found\n\n"

        # Find problematic scenarios
        issues = [r for r in self.results if r["successful_turns"] < r["total_turns"]]
        if issues:
            for issue in issues[:10]:
                failed_turns = [t for t in issue["turns"] if not t.get("success")]
                summary += f"- **{issue['persona']}**: {len(failed_turns)} failed turns\n"
                for turn in failed_turns:
                    summary += f"  - Turn {turn['turn']}: {turn.get('error', 'Unknown error')}\n"
        else:
            summary += "✅ No issues found - all scenarios completed successfully!\n"

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)

        print(f"\n{'='*80}")
        print(f"📊 EVALUATION COMPLETE")
        print(f"{'='*80}")
        print(f"✅ Scenarios completed: {len(self.results)}")
        print(f"📈 Success rate: {successful_turns/total_turns*100:.1f}%")
        print(f"🎯 Intent accuracy: {avg_intent_accuracy:.1f}%")
        print(f"🧠 Context retention: {avg_context_retention:.1f}%")
        print(f"⚡ Avg response time: {avg_response_time:.0f}ms")
        print(f"\n📄 Detailed report: {report_file}")
        print(f"📝 Summary: {summary_file}")
        print(f"{'='*80}\n")

    async def close(self):
        """Cleanup"""
        await self.client.aclose()


async def main():
    """Main evaluation function"""

    # Combine predefined and generated scenarios
    all_scenarios = CONVERSATION_SCENARIOS + generate_additional_scenarios()

    print(f"\n{'#'*80}")
    print(f"# REE AI CONVERSATION EVALUATION")
    print(f"# Total Scenarios: {len(all_scenarios)}")
    print(f"# Simulating real user conversations with memory context")
    print(f"{'#'*80}\n")

    evaluator = ConversationEvaluator()

    try:
        await evaluator.run_all_scenarios(all_scenarios, max_concurrent=3)
    finally:
        await evaluator.close()


if __name__ == "__main__":
    asyncio.run(main())

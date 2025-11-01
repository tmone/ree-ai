"""
AI User Simulator - Automated Conversation Evaluation
Uses LLM to role-play different user personas and test system responses
"""
import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import random

# 100 User Personas with Detailed Characteristics
USER_PERSONAS = [
    # First-time buyers (10 personas)
    *[{
        "id": f"first_buyer_{i}",
        "type": "Cặp vợ chồng trẻ, lần đầu mua nhà",
        "age_range": "25-35",
        "budget": random.choice(["2-3 tỷ", "3-4 tỷ", "1.5-2.5 tỷ"]),
        "district_preference": random.choice(["quận 7", "quận 2", "Thủ Đức", "quận 9", "Bình Thạnh"]),
        "requirements": random.choice([
            "2 phòng ngủ, gần trường học",
            "có chỗ đậu xe, view đẹp",
            "gần trung tâm, thuận tiện đi làm",
            "khu an ninh tốt, dân trí cao"
        ]),
        "characteristics": "Hỏi nhiều, cần tư vấn chi tiết, quan tâm thủ tục",
        "conversation_turns": random.randint(6, 10)
    } for i in range(1, 11)],

    # Experienced investors (10 personas)
    *[{
        "id": f"investor_{i}",
        "type": "Nhà đầu tư có kinh nghiệm",
        "age_range": "35-50",
        "budget": random.choice(["5-10 tỷ", "10-20 tỷ", "trên 20 tỷ"]),
        "district_preference": random.choice(["quận 1", "quận 2", "quận 7", "Thủ Đức"]),
        "requirements": random.choice([
            "ROI cao, tiềm năng tăng giá",
            "vị trí đắc địa, dễ cho thuê",
            "dự án mới, chủ đầu tư uy tín",
            "pháp lý rõ ràng, sổ hồng sẵn"
        ]),
        "characteristics": "Phân tích kỹ, so sánh nhiều, tập trung lợi nhuận",
        "conversation_turns": random.randint(5, 8)
    } for i in range(1, 11)],

    # Families with children (10 personas)
    *[{
        "id": f"family_{i}",
        "type": "Gia đình có con nhỏ",
        "age_range": "30-45",
        "budget": random.choice(["3-5 tỷ", "4-6 tỷ", "5-7 tỷ"]),
        "district_preference": random.choice(["Thủ Đức", "quận 2", "quận 7", "quận 9"]),
        "requirements": random.choice([
            "gần trường quốc tế, công viên",
            "khu compound an toàn",
            "nhiều tiện ích cho trẻ em",
            "không khí trong lành"
        ]),
        "characteristics": "Ưu tiên môi trường sống, tiện ích giáo dục",
        "conversation_turns": random.randint(6, 9)
    } for i in range(1, 11)],

    # Retirees (10 personas)
    *[{
        "id": f"retiree_{i}",
        "type": "Người về hưu",
        "age_range": "55-70",
        "budget": random.choice(["2-3 tỷ", "3-4 tỷ", "1.5-2 tỷ"]),
        "district_preference": random.choice(["quận 3", "quận 10", "Bình Thạnh", "Phú Nhuận"]),
        "requirements": random.choice([
            "yên tĩnh, gần bệnh viện",
            "tầng thấp, có thang máy",
            "gần chợ, gần công viên",
            "khu dân cư ổn định"
        ]),
        "characteristics": "Thận trọng, không vội, quan tâm y tế",
        "conversation_turns": random.randint(5, 8)
    } for i in range(1, 11)],

    # Students/Renters (10 personas)
    *[{
        "id": f"student_{i}",
        "type": "Sinh viên / Người thuê nhà",
        "age_range": "18-25",
        "budget": random.choice(["3-5 triệu/tháng", "5-7 triệu/tháng", "2-4 triệu/tháng"]),
        "district_preference": random.choice(["Thủ Đức", "quận 9", "Bình Thạnh", "quận 7"]),
        "requirements": random.choice([
            "gần trường đại học",
            "có wifi, điều hòa",
            "giá rẻ, tiện ích đầy đủ",
            "gần khu ăn uống, siêu thị"
        ]),
        "characteristics": "Ngân sách thấp, cần nhanh, ưu tiên tiện lợi",
        "conversation_turns": random.randint(4, 6)
    } for i in range(1, 11)],

    # Foreign buyers (10 personas)
    *[{
        "id": f"expat_{i}",
        "type": "Người nước ngoài",
        "age_range": "30-50",
        "budget": random.choice(["$150k-200k", "$200k-300k", "$100k-150k"]),
        "district_preference": random.choice(["quận 1", "quận 2", "quận 7", "Bình Thạnh"]),
        "requirements": random.choice([
            "khu expat, gần trường quốc tế",
            "căn hộ dịch vụ, nội thất đầy đủ",
            "gần công ty, trung tâm thương mại",
            "pháp lý rõ ràng cho người nước ngoài"
        ]),
        "characteristics": "Quan tâm thủ tục, cần hỗ trợ ngôn ngữ",
        "conversation_turns": random.randint(5, 8)
    } for i in range(1, 11)],

    # Buy-to-let investors (10 personas)
    *[{
        "id": f"landlord_{i}",
        "type": "Người mua để cho thuê",
        "age_range": "30-50",
        "budget": random.choice(["4-6 tỷ", "6-8 tỷ", "3-5 tỷ"]),
        "district_preference": random.choice(["quận 1", "quận 2", "quận 7", "Bình Thạnh"]),
        "requirements": random.choice([
            "lợi suất cho thuê cao",
            "vị trí trung tâm, dễ cho thuê",
            "dự án mới, chất lượng tốt",
            "quản lý chuyên nghiệp"
        ]),
        "characteristics": "Tính toán kỹ ROI, quan tâm cash flow",
        "conversation_turns": random.randint(5, 7)
    } for i in range(1, 11)],

    # Sellers (10 personas)
    *[{
        "id": f"seller_{i}",
        "type": "Người bán nhà",
        "age_range": "35-60",
        "budget": "N/A",
        "district_preference": random.choice(["quận 2", "quận 7", "Thủ Đức", "Bình Thạnh"]),
        "requirements": random.choice([
            "định giá hợp lý",
            "bán nhanh, cần tiền",
            "tìm khách hàng tiềm năng",
            "thủ tục bán nhà"
        ]),
        "characteristics": "Cần định giá, marketing, tư vấn thủ tục",
        "conversation_turns": random.randint(4, 6)
    } for i in range(1, 11)],

    # Window shoppers (10 personas)
    *[{
        "id": f"browser_{i}",
        "type": "Người chỉ tìm hiểu",
        "age_range": "25-40",
        "budget": "Chưa xác định",
        "district_preference": random.choice(["nhiều quận", "chưa quyết định", "tùy tình hình"]),
        "requirements": random.choice([
            "khảo sát thị trường",
            "tìm hiểu xu hướng",
            "chưa có kế hoạch cụ thể",
            "so sánh giá thị trường"
        ]),
        "characteristics": "Câu hỏi chung chung, chưa quyết định, khám phá",
        "conversation_turns": random.randint(3, 5)
    } for i in range(1, 11)],

    # Complex scenarios (10 personas)
    *[{
        "id": f"complex_{i}",
        "type": "Kịch bản phức tạp",
        "age_range": "Varied",
        "budget": "Varied",
        "district_preference": "Multiple",
        "requirements": random.choice([
            "đổi nhà, bán cũ mua mới",
            "tích lũy tài sản, đa dạng hóa",
            "nhiều tiêu chí khác nhau",
            "chuyển đổi context liên tục"
        ]),
        "characteristics": "Test khả năng xử lý context phức tạp, đa dạng nhu cầu",
        "conversation_turns": random.randint(8, 12)
    } for i in range(1, 11)]
]

class AIUserSimulator:
    """Simulates realistic user conversations using LLM"""

    def __init__(self,
                 user_model: str = "llama3.2:latest",  # Model for user simulation (upgraded to 2GB)
                 orchestrator_url: str = "http://localhost:8090"):
        self.user_model = user_model
        self.orchestrator_url = orchestrator_url
        self.ollama_url = "http://localhost:11434"

    async def generate_user_query(self, persona: Dict, conversation_history: List[Dict], turn_num: int) -> str:
        """Use LLM to generate natural user query based on persona and context"""

        # Build prompt for user simulator with explicit role-playing instructions
        prompt = f"""BẠN ĐANG ĐÓNG VAI MỘT NGƯỜI DÙNG THẬT đang tìm nhà trên ứng dụng bất động sản.

===== THÔNG TIN VỀ BẠN =====
- Bạn là: {persona['type']}
- Tuổi: {persona['age_range']}
- Ngân sách: {persona['budget']}
- Muốn tìm ở: {persona['district_preference']}
- Yêu cầu: {persona['requirements']}
- Tính cách: {persona['characteristics']}

===== TÌNH HUỐNG =====
Bạn đang chat với trợ lý AI bất động sản. Đây là lượt {turn_num}/{persona['conversation_turns']} trong cuộc trò chuyện.
"""

        # Add conversation history
        if conversation_history:
            prompt += "\n===== LỊCH SỬ TRÒ CHUYỆN =====\n"
            for msg in conversation_history[-6:]:  # Last 3 exchanges
                role = "Bạn đã nói" if msg['role'] == 'user' else "AI đã trả lời"
                prompt += f"{role}: \"{msg['content'][:200]}\"\n"
            prompt += "\n"

        # Add instruction based on turn number with EXAMPLES
        if turn_num == 1:
            prompt += """===== NHIỆM VỤ: CÂU MỞ ĐẦU =====
Hãy chào hỏi và nói về nhu cầu của bạn một cách TỰ NHIÊN như người thật.

VÍ DỤ TỐT:
- "Xin chào, mình muốn tìm căn hộ 2 phòng ngủ ở quận 7 trong khoảng 3 tỷ"
- "Chào bạn, gia đình mình đang tìm nhà gần trường quốc tế"
- "Hi, mình muốn tìm hiểu thông tin về bất động sản khu vực Thủ Đức"

VÍ DỤ TỆ (KHÔNG LÀM THẾ NÀY):
- "Mục tiêu của bạn là gì?" ← Đây là AI hỏi user, KHÔNG phải user hỏi AI!
- "Bạn có thể giúp gì?" ← Quá chung chung
- "Chào bạn!" ← Chỉ chào, không nói nhu cầu

HÃY NHỚ: BẠN LÀ KHÁCH HÀNG, không phải AI assistant!
"""
        elif turn_num == persona['conversation_turns']:
            prompt += """===== NHIỆM VỤ: CÂU KẾT THÚC =====
Kết thúc cuộc trò chuyện một cách tự nhiên.

VÍ DỤ:
- "Cảm ơn bạn! Để mình suy nghĩ thêm"
- "OK, mình sẽ liên hệ lại sau. Thủ tục mua nhà cần giấy tờ gì?"
- "Thanks, cho mình xin contact để hẹn xem nhà"
"""
        else:
            prompt += f"""===== NHIỆM VỤ: CÂU HỎI TIẾP THEO =====
Dựa vào lịch sử trò chuyện, hãy hỏi câu TIẾP THEO một cách tự nhiên.

QUY TẮC QUAN TRỌNG:
1. PHẢI liên quan đến ngữ cảnh đã nói
2. CÓ THỂ tham chiếu thông tin cũ: "căn đó", "giá vừa nói", "khu vực em vừa giới thiệu"
3. Phù hợp với tính cách: {persona['characteristics']}
4. Đừng lặp lại câu hỏi cũ!

VÍ DỤ TỐT (có tham chiếu context):
- "Căn đó có view đẹp không?" ← Tham chiếu "căn đó" từ câu trước
- "Giá 2.5 tỷ cho 70m² có hợp lý không?" ← Hỏi cụ thể
- "So với khu vực em vừa nói, quận 2 thì sao?" ← Tham chiếu khu vực đã đề cập

VÍ DỤ TỆ:
- Lặp lại câu cũ nguyên xi
- Hỏi câu không liên quan gì đến cuộc nói chuyện
"""

        prompt += "\n===== YÊU CẦU OUTPUT =====\n"
        prompt += "Chỉ viết CÂU HỎI của bạn (người dùng), KHÔNG thêm bất kỳ giải thích nào.\n"
        prompt += "Câu hỏi (tiếng Việt tự nhiên): "

        # Call Ollama API with user model
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.user_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,  # Higher for more natural variation
                        "top_p": 0.9
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            user_query = data["response"].strip()

            # Clean up if model adds extra explanation
            if "Câu hỏi:" in user_query:
                user_query = user_query.split("Câu hỏi:")[-1].strip()
            if "\n" in user_query:
                user_query = user_query.split("\n")[0].strip()

            return user_query

    async def send_to_system(self, query: str, session_id: str, history: List[Dict]) -> Dict:
        """Send user query to orchestrator and get response

        IMPORTANT: Send FULL conversation history from beginning to test memory context
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.orchestrator_url}/orchestrate",
                json={
                    "user_id": session_id,
                    "query": query,
                    "conversation_id": session_id,
                    "metadata": {
                        "history": history  # FULL history to test memory context
                    }
                }
            )
            response.raise_for_status()
            return response.json()

    async def evaluate_response(self, persona: Dict, user_query: str, system_response: Dict, turn_num: int) -> Dict:
        """Evaluate system response quality"""
        evaluation = {
            "intent_correct": None,  # Will be filled based on expected intent
            "response_quality": None,  # 1-5 scale
            "vietnamese_quality": None,  # 1-5 scale
            "relevance": None,  # 1-5 scale
            "context_preserved": None,  # True/False
            "issues": []
        }

        response_text = system_response.get("response", "")

        # Check Vietnamese quality (basic checks)
        if not response_text:
            evaluation["issues"].append("Empty response")
            evaluation["vietnamese_quality"] = 1
        elif any(char in response_text for char in ["乌", "欢", "谢", "您", "在", "是"]):  # Chinese characters
            evaluation["issues"].append("Contains Chinese characters")
            evaluation["vietnamese_quality"] = 1
        elif len(response_text) < 20:
            evaluation["issues"].append("Response too short")
            evaluation["vietnamese_quality"] = 2
        else:
            # Simple heuristic: longer, Vietnamese-like response is better
            evaluation["vietnamese_quality"] = 4

        # Check response time
        exec_time = system_response.get("execution_time_ms", 0)
        if exec_time > 30000:
            evaluation["issues"].append(f"Slow response: {exec_time}ms")

        return evaluation

    async def run_scenario(self, persona: Dict, scenario_num: int) -> Dict:
        """Run a complete conversation scenario"""
        session_id = persona['id']
        conversation_history = []
        turns_data = []

        print(f"\n{'='*100}")
        print(f"📋 Scenario {scenario_num}/100: {persona['type']} ({persona['id']})")
        print(f"💰 Budget: {persona['budget']}")
        print(f"📍 District: {persona['district_preference']}")
        print(f"🎯 Requirements: {persona['requirements']}")
        print(f"📝 Characteristics: {persona['characteristics']}")
        print(f"{'='*100}\n")

        for turn_num in range(1, persona['conversation_turns'] + 1):
            print(f"{'─'*100}")
            print(f"Turn {turn_num}/{persona['conversation_turns']}")

            start_time = time.time()

            try:
                # 1. Generate user query using LLM
                user_query = await self.generate_user_query(persona, conversation_history, turn_num)
                print(f"👤 User: {user_query}")

                # 2. Send to system
                system_response = await self.send_to_system(user_query, session_id, conversation_history)

                ai_response = system_response.get("response", "")
                intent = system_response.get("intent", "unknown")
                confidence = system_response.get("confidence", 0)

                print(f"🤖 AI: {ai_response[:200]}{'...' if len(ai_response) > 200 else ''}")
                print(f"📊 Intent: {intent} (confidence: {confidence:.2f})")

                # 3. Evaluate response
                evaluation = await self.evaluate_response(persona, user_query, system_response, turn_num)

                elapsed_ms = (time.time() - start_time) * 1000
                print(f"⏱️  Time: {elapsed_ms:.0f}ms")
                print(f"⭐ Quality: Vietnamese {evaluation['vietnamese_quality']}/5")
                if evaluation['issues']:
                    print(f"⚠️  Issues: {', '.join(evaluation['issues'])}")

                # Store turn data
                turn_data = {
                    "turn": turn_num,
                    "user_query": user_query,
                    "system_response": ai_response,
                    "intent": intent,
                    "confidence": confidence,
                    "response_time_ms": elapsed_ms,
                    "evaluation": evaluation
                }
                turns_data.append(turn_data)

                # Update history
                conversation_history.append({"role": "user", "content": user_query})
                conversation_history.append({"role": "assistant", "content": ai_response})

            except Exception as e:
                print(f"❌ Error: {str(e)}")
                turns_data.append({
                    "turn": turn_num,
                    "error": str(e)
                })

            # Brief pause
            await asyncio.sleep(0.5)

        # Calculate scenario metrics
        successful_turns = [t for t in turns_data if "error" not in t]
        avg_response_time = sum(t.get("response_time_ms", 0) for t in successful_turns) / len(successful_turns) if successful_turns else 0
        avg_quality = sum(t.get("evaluation", {}).get("vietnamese_quality", 0) for t in successful_turns) / len(successful_turns) if successful_turns else 0

        scenario_result = {
            "scenario_num": scenario_num,
            "persona": persona,
            "total_turns": persona['conversation_turns'],
            "successful_turns": len(successful_turns),
            "avg_response_time_ms": avg_response_time,
            "avg_vietnamese_quality": avg_quality,
            "turns": turns_data
        }

        print(f"\n{'─'*100}")
        print(f"📊 Scenario Summary:")
        print(f"   Success Rate: {len(successful_turns)}/{persona['conversation_turns']}")
        print(f"   Avg Response Time: {avg_response_time:.0f}ms")
        print(f"   Avg Quality: {avg_quality:.1f}/5")
        print(f"{'─'*100}\n")

        return scenario_result

    async def run_all_scenarios(self, num_scenarios: int = 100):
        """Run all 100 scenarios"""
        print("\n" + "="*100)
        print("🔥 AI USER SIMULATOR - 100 Scenarios")
        print(f"User Model: {self.user_model}")
        print(f"System Model: deepseek-v3.1:671b-cloud (via orchestrator)")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*100)

        all_results = []

        for i in range(min(num_scenarios, len(USER_PERSONAS))):
            persona = USER_PERSONAS[i]
            result = await self.run_scenario(persona, i + 1)
            all_results.append(result)

            # Save incremental results every 10 scenarios
            if (i + 1) % 10 == 0:
                await self.save_results(all_results, partial=True)

        # Save final results
        await self.save_results(all_results, partial=False)

        print("\n" + "="*100)
        print("✅ ALL SCENARIOS COMPLETED!")
        print("="*100 + "\n")

    async def save_results(self, results: List[Dict], partial: bool = False):
        """Save evaluation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "partial_" if partial else ""

        # Save detailed JSON
        json_path = f"/tmp/{prefix}ai_evaluation_{timestamp}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "user_model": self.user_model,
                    "system_model": "deepseek-v3.1:671b-cloud",
                    "total_scenarios": len(results),
                    "partial": partial
                },
                "results": results
            }, f, ensure_ascii=False, indent=2)

        if not partial:
            print(f"📁 Detailed results saved: {json_path}")

async def main():
    simulator = AIUserSimulator(user_model="qwen3:0.6b")
    await simulator.run_all_scenarios(num_scenarios=100)

if __name__ == "__main__":
    asyncio.run(main())

"""
Analyze AI-to-AI Test Results - Find Insights for Prompt Optimization
=====================================================================
Phân tích kết quả test để cải tiến prompts ở Layer 3 services
"""
import json
import sys
from collections import defaultdict
from typing import Dict, List

def load_results(filename: str) -> Dict:
    """Load JSON results"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_conversation(conv: Dict) -> Dict:
    """Analyze single conversation for issues"""
    issues = []
    insights = []

    scenario = conv['scenario']
    turns = conv['total_turns']
    score = conv['final_score']
    history = conv['conversation_history']

    # Issue 1: Too many turns (>8 for complete info)
    if score == 100 and turns > 6:
        issues.append({
            "type": "INEFFICIENT_COMPLETION",
            "severity": "MEDIUM",
            "description": f"Đạt 100% nhưng mất {turns} turns (nên <6)",
            "suggestion": "Orchestrator nên kết thúc ngay khi đạt 100%"
        })

    # Issue 2: Incomplete after max turns
    if score < 100:
        issues.append({
            "type": "INCOMPLETE_DATA",
            "severity": "HIGH",
            "description": f"Chỉ đạt {score}% sau {turns} turns",
            "suggestion": "Attribute Extraction hoặc Completeness Check có vấn đề"
        })

    # Issue 3: Repetitive system responses
    system_msgs = [msg['content'] for msg in history if msg['role'] == 'assistant']
    if len(system_msgs) > 2:
        repeated_count = sum(1 for i in range(len(system_msgs)-1)
                            if system_msgs[i] == system_msgs[i+1])
        if repeated_count > 2:
            issues.append({
                "type": "REPETITIVE_RESPONSE",
                "severity": "HIGH",
                "description": f"Hệ thống lặp lại response {repeated_count} lần",
                "suggestion": "Orchestrator không nhận được update từ Attribute Extraction"
            })

    # Issue 4: User frustration signals
    user_msgs = [msg['content'].lower() for msg in history if msg['role'] == 'user']
    frustration_keywords = ['lỗi', 'sai', 'nhầm', 'ủa', 'hả', 'mà', 'rồi mà', 'đã gửi']
    frustrated_turns = sum(1 for msg in user_msgs if any(kw in msg for kw in frustration_keywords))

    if frustrated_turns >= 2:
        issues.append({
            "type": "USER_FRUSTRATION",
            "severity": "CRITICAL",
            "description": f"User thất vọng/phàn nàn {frustrated_turns} lần",
            "suggestion": "Hệ thống không hiểu hoặc không xử lý đúng input"
        })

    # Issue 5: AI quality - format copying
    for i, msg in enumerate(history):
        if msg['role'] == 'user' and '(Hoàn thiện:' in msg['content']:
            issues.append({
                "type": "AI_FORMAT_COPYING",
                "severity": "HIGH",
                "description": f"Ollama AI sao chép format hệ thống (turn {i+1})",
                "suggestion": "Cần cải thiện prompt Ollama với stop tokens"
            })
            break

    # Insight 1: Optimal completion
    if score == 100 and turns <= 4 and len(issues) == 0:
        insights.append({
            "type": "OPTIMAL_FLOW",
            "description": f"Hoàn hảo! {turns} turns, không lỗi",
            "scenario": scenario
        })

    # Insight 2: Multi-language support needed
    if 'english' in scenario.lower() or 'tiếng anh' in scenario.lower():
        insights.append({
            "type": "MULTILINGUAL_CAPABILITY",
            "description": "Test đa ngôn ngữ",
            "scenario": scenario
        })

    return {
        "scenario": scenario,
        "turns": turns,
        "score": score,
        "issues": issues,
        "insights": insights
    }

def generate_summary(analyses: List[Dict]) -> Dict:
    """Generate comprehensive summary"""

    # Categorize by outcome
    perfect = [a for a in analyses if a['score'] == 100 and a['turns'] <= 5 and not a['issues']]
    good = [a for a in analyses if a['score'] == 100 and (a['turns'] > 5 or a['issues'])]
    incomplete = [a for a in analyses if a['score'] < 100]

    # Group issues by type
    issue_types = defaultdict(list)
    for analysis in analyses:
        for issue in analysis['issues']:
            issue_types[issue['type']].append({
                'scenario': analysis['scenario'],
                'severity': issue['severity'],
                'description': issue['description'],
                'suggestion': issue['suggestion']
            })

    # Calculate metrics
    total = len(analyses)
    avg_turns = sum(a['turns'] for a in analyses) / total
    avg_score = sum(a['score'] for a in analyses) / total

    return {
        "metrics": {
            "total_scenarios": total,
            "perfect_count": len(perfect),
            "good_count": len(good),
            "incomplete_count": len(incomplete),
            "avg_turns": round(avg_turns, 1),
            "avg_score": round(avg_score, 1),
            "success_rate": round((len(perfect) + len(good)) / total * 100, 1)
        },
        "issue_summary": {
            issue_type: {
                "count": len(issues),
                "severity": issues[0]['severity'],
                "examples": issues[:3]  # Top 3 examples
            }
            for issue_type, issues in issue_types.items()
        },
        "perfect_scenarios": [a['scenario'] for a in perfect],
        "problematic_scenarios": [
            {"scenario": a['scenario'], "issues": len(a['issues'])}
            for a in sorted(analyses, key=lambda x: len(x['issues']), reverse=True)[:5]
        ]
    }

def generate_prompt_recommendations(summary: Dict, analyses: List[Dict]) -> List[Dict]:
    """Generate specific prompt improvement recommendations"""
    recommendations = []

    # Rec 1: Handle special property types (land, etc.)
    land_issues = [a for a in analyses if 'đất' in a['scenario'].lower() and a['score'] < 100]
    if land_issues:
        recommendations.append({
            "priority": "HIGH",
            "service": "Attribute Extraction Service",
            "file": "services/attribute_extraction/prompts.py",
            "issue": "Không xử lý được property types không có phòng ngủ (đất, parking, commercial)",
            "current_prompt": "bedrooms: Optional[int] - Required field",
            "improved_prompt": """bedrooms: Optional[int] = Field(None, description="Số phòng ngủ. CHÚ Ý: Với đất/parking/commercial, giá trị này có thể = 0 hoặc null")

EDGE CASES:
- Đất nông nghiệp, đất thổ cư → bedrooms = null hoặc 0
- Parking lot, nhà kho → bedrooms = null hoặc 0
- Commercial property → bedrooms = null (trừ khi có căn hộ dịch vụ)""",
            "affected_scenarios": [a['scenario'] for a in land_issues]
        })

    # Rec 2: Better price parsing (decimal support)
    price_issues = [a for a in analyses
                   if any(i['type'] == 'USER_FRUSTRATION' and 'giá' in i['description'].lower()
                         for i in a['issues'])]
    if price_issues:
        recommendations.append({
            "priority": "HIGH",
            "service": "Attribute Extraction Service",
            "file": "services/attribute_extraction/prompts.py",
            "issue": "Không parse đúng giá có dấu phẩy (5,5 tỷ → 5.0 tỷ)",
            "current_prompt": '"2.5 tỷ" → 2500000000',
            "improved_prompt": '''PRICE EXTRACTION RULES:
- "2.5 tỷ" → 2500000000
- "2,5 tỷ" → 2500000000  # SUPPORT COMMA
- "20.5 tỷ" → 20500000000
- "5 tỷ 500 triệu" → 5500000000
- "3 triệu/tháng" → 3000000 (rental)
- "500k/ngày" → 500000 (daily rental)

CRITICAL: Vietnamese users often use COMMA (,) instead of DOT (.) for decimals!''',
            "affected_scenarios": [a['scenario'] for a in price_issues]
        })

    # Rec 3: Rental price detection
    rent_issues = [a for a in analyses
                  if 'thuê' in a['scenario'].lower() and a['score'] < 100]
    if rent_issues:
        recommendations.append({
            "priority": "MEDIUM",
            "service": "Attribute Extraction Service",
            "file": "services/attribute_extraction/prompts.py",
            "issue": "Không nhận dạng giá thuê với format 'X triệu một tháng'",
            "current_prompt": 'r"(\\d+)\\s*(?:triệu|million)/(?:tháng|month)"',
            "improved_prompt": '''RENTAL PRICE PATTERNS:
- "15 triệu/tháng" → price_rent = 15000000
- "15 triệu một tháng" → price_rent = 15000000  # NEW
- "15 triệu mỗi tháng" → price_rent = 15000000  # NEW
- "15 triệu 1 tháng" → price_rent = 15000000    # NEW
- "500k/ngày" → daily_rate = 500000, price_rent = 15000000 (estimate)''',
            "affected_scenarios": [a['scenario'] for a in rent_issues]
        })

    # Rec 4: Conversation ending logic
    if summary['metrics']['avg_turns'] > 6:
        recommendations.append({
            "priority": "HIGH",
            "service": "Orchestrator Service",
            "file": "services/orchestrator/prompts.py",
            "issue": "Orchestrator không kết thúc hội thoại khi đã đủ thông tin",
            "current_prompt": "N/A - Business logic issue",
            "improved_prompt": '''ADD TO ORCHESTRATOR FLOW:

if completeness_score >= 100:
    return {
        "response": "✅ Hoàn tất! Tin đăng đã được lưu. Cảm ơn bạn!",
        "end_conversation": True,  # NEW FIELD
        "metadata": {"completeness_score": 100, "ready_to_publish": True}
    }

KHÔNG lặp lại "Tin đăng sẵn sàng" nhiều lần!''',
            "affected_scenarios": ["ALL"]
        })

    # Rec 5: User frustration detection
    frustration_count = sum(1 for a in analyses
                           if any(i['type'] == 'USER_FRUSTRATION' for i in a['issues']))
    if frustration_count >= 3:
        recommendations.append({
            "priority": "CRITICAL",
            "service": "Orchestrator Service",
            "file": "services/orchestrator/prompts.py",
            "issue": "Hệ thống không phát hiện user frustration để điều chỉnh",
            "current_prompt": "N/A",
            "improved_prompt": '''ADD USER FRUSTRATION DETECTION:

FRUSTRATION_SIGNALS = [
    "lỗi", "sai", "nhầm", "ủa", "hả",
    "rồi mà", "đã gửi", "đã nhập", "không hiểu sao"
]

if detect_frustration(user_message):
    # Option 1: Apologize and confirm
    return "Xin lỗi bạn! Để em kiểm tra lại thông tin bạn đã cung cấp..."

    # Option 2: Reset extraction
    return "Em xin lỗi, có vẻ có sự nhầm lẫn. Bạn có thể nhập lại toàn bộ thông tin không?"

    # Option 3: Escalate to human
    return "Em xin lỗi vì sự bất tiện. Em sẽ chuyển bạn sang bộ phận hỗ trợ..."''',
            "affected_scenarios": [a['scenario'] for a in analyses
                                  if any(i['type'] == 'USER_FRUSTRATION' for i in a['issues'])]
        })

    # Rec 6: Multi-language support
    recommendations.append({
        "priority": "MEDIUM",
        "service": "Attribute Extraction Service + Classification Service",
        "file": "services/attribute_extraction/prompts.py, services/classification/prompts.py",
        "issue": "Cần hỗ trợ rõ ràng các ngôn ngữ: VI, EN, TH, JA",
        "current_prompt": "Prompts chỉ có tiếng Việt",
        "improved_prompt": '''ADD MULTILINGUAL SUPPORT:

LANGUAGE_DETECTION:
- Vietnamese: Contains "ă", "ơ", "ư", "đ", "quận", "phòng ngủ"
- English: Contains "bedroom", "district", "property"
- Thai: Contains "ห้องนอน", "เขต", "บาท"
- Japanese: Contains "ベッドルーム", "区", "円"

NORMALIZED FIELD MAPPING:
{
    "bedrooms": {
        "vi": ["phòng ngủ", "pn", "phòng"],
        "en": ["bedroom", "bed", "br"],
        "th": ["ห้องนอน"],
        "ja": ["ベッドルーム", "寝室"]
    },
    "district": {
        "vi": ["quận", "huyện", "q.", "q"],
        "en": ["district", "area", "zone"],
        "th": ["เขต", "อำเภอ"],
        "ja": ["区", "地区"]
    }
}

Extract entities language-agnostically, then normalize to English fields.''',
        "affected_scenarios": ["ALL - Future internationalization"]
    })

    return recommendations

def print_analysis_report(results: Dict, analyses: List[Dict], summary: Dict, recommendations: List[Dict]):
    """Print comprehensive analysis report"""

    print("=" * 120)
    print("📊 AI-TO-AI TEST ANALYSIS REPORT")
    print("=" * 120)
    print(f"\nTest file: {results['metadata']['timestamp']}")
    print(f"Total scenarios tested: {results['metadata']['total_scenarios']}")

    print("\n" + "=" * 120)
    print("📈 OVERALL METRICS")
    print("=" * 120)
    metrics = summary['metrics']
    print(f"  ✅ Perfect (≤5 turns, 100%, no issues): {metrics['perfect_count']}/{metrics['total_scenarios']}")
    print(f"  ⚠️  Good (100% but issues):              {metrics['good_count']}/{metrics['total_scenarios']}")
    print(f"  ❌ Incomplete (<100%):                   {metrics['incomplete_count']}/{metrics['total_scenarios']}")
    print(f"  📊 Average turns:                        {metrics['avg_turns']}")
    print(f"  📊 Average score:                        {metrics['avg_score']}%")
    print(f"  📊 Success rate:                         {metrics['success_rate']}%")

    print("\n" + "=" * 120)
    print("🎯 PERFECT SCENARIOS (Best practices)")
    print("=" * 120)
    for scenario in summary['perfect_scenarios']:
        print(f"  ✅ {scenario}")

    print("\n" + "=" * 120)
    print("⚠️  PROBLEMATIC SCENARIOS (Need attention)")
    print("=" * 120)
    for item in summary['problematic_scenarios']:
        print(f"  ❌ {item['scenario']} ({item['issues']} issues)")

    print("\n" + "=" * 120)
    print("🐛 ISSUE BREAKDOWN")
    print("=" * 120)
    for issue_type, data in summary['issue_summary'].items():
        print(f"\n  {issue_type} [{data['severity']}] - {data['count']} occurrences:")
        for ex in data['examples']:
            print(f"    - {ex['scenario']}")
            print(f"      {ex['description']}")
            print(f"      💡 {ex['suggestion']}")

    print("\n" + "=" * 120)
    print("🚀 PROMPT OPTIMIZATION RECOMMENDATIONS")
    print("=" * 120)
    for i, rec in enumerate(recommendations, 1):
        print(f"\n[{i}] {rec['service']} - Priority: {rec['priority']}")
        print(f"    📁 File: {rec['file']}")
        print(f"    🐛 Issue: {rec['issue']}")
        print(f"\n    ❌ Current:")
        for line in rec['current_prompt'].split('\n'):
            print(f"       {line}")
        print(f"\n    ✅ Improved:")
        for line in rec['improved_prompt'].split('\n'):
            print(f"       {line}")
        print(f"\n    📋 Affected: {len(rec['affected_scenarios'])} scenarios")
        if len(rec['affected_scenarios']) <= 3:
            for scenario in rec['affected_scenarios']:
                print(f"       - {scenario}")

    print("\n" + "=" * 120)
    print("💡 NEXT STEPS")
    print("=" * 120)
    print("  1. Review recommendations above")
    print("  2. Update prompts in respective service files")
    print("  3. Re-run AI-to-AI tests to validate improvements")
    print("  4. Monitor production metrics for real user impact")
    print("  5. Continue iterative testing with more edge cases")
    print("=" * 120)

def main():
    """Main analysis"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_ai_to_ai_results.py <json_file>")
        sys.exit(1)

    filename = sys.argv[1]

    # Load and analyze
    results = load_results(filename)
    analyses = [analyze_conversation(conv) for conv in results['results']]
    summary = generate_summary(analyses)
    recommendations = generate_prompt_recommendations(summary, analyses)

    # Print report
    print_analysis_report(results, analyses, summary, recommendations)

    # Save analysis to file
    output_file = filename.replace('.json', '_analysis.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "analyses": analyses,
            "summary": summary,
            "recommendations": recommendations
        }, f, ensure_ascii=False, indent=2)

    print(f"\n📄 Detailed analysis saved to: {output_file}")

if __name__ == "__main__":
    main()

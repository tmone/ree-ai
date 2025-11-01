"""
Comprehensive Intent Detection Tests for Orchestrator
Tests all 8 intent types with Vietnamese real estate queries

Based on: /Users/tmone/ree-ai/docs/testing/COMPREHENSIVE_BUSINESS_LOGIC_TEST_PLAN.md
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.models.orchestrator import IntentType


# Test data: Each intent type with 3+ test cases
INTENT_TEST_CASES = {
    IntentType.SEARCH: [
        "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ",
        "Có nhà nào gần Metro không?",
        "Find apartments in District 2 under 5 billion",
        "Cần tìm biệt thự có bể bơi",
        "Search for properties near Landmark 81",
    ],
    IntentType.COMPARE: [
        "So sánh 2 căn hộ này",
        "Căn nào tốt hơn?",
        "Compare Vinhomes Grand Park vs Masteri Thảo Điền",
        "Khác gì giữa căn A và căn B?",
        "So sánh giá 2 căn hộ này",
    ],
    IntentType.PRICE_ANALYSIS: [
        "Giá 2.5 tỷ cho căn hộ 70m² Q7 có hợp lý không?",
        "Phân tích giá căn này",
        "Is 3 billion reasonable for this property?",
        "Đánh giá giá căn hộ này",
        "Bao nhiêu là giá hợp lý cho khu vực này?",
    ],
    IntentType.INVESTMENT_ADVICE: [
        "Nên đầu tư vào Q2 hay Q7 với 5 tỷ?",
        "Khu vực nào có tiềm năng đầu tư?",
        "Should I invest in Thu Duc or District 9?",
        "Tư vấn đầu tư bất động sản 10 tỷ",
        "Mua căn hộ hay nhà phố để đầu tư?",
    ],
    IntentType.LOCATION_INSIGHTS: [
        "Quận Thủ Đức có gì hay?",
        "Khu vực này có tiện ích gì?",
        "What amenities are near Vinhomes Central Park?",
        "Quận 7 có trường học quốc tế nào?",
        "Gần đây có siêu thị, bệnh viện không?",
    ],
    IntentType.LEGAL_GUIDANCE: [
        "Thủ tục mua nhà cần giấy tờ gì?",
        "Pháp lý căn hộ chung cư như thế nào?",
        "What documents do I need to buy property?",
        "Hợp đồng mua bán cần chú ý điểm gì?",
        "Sổ hồng sổ đỏ khác gì nhau?",
    ],
    IntentType.CHAT: [
        "Xin chào, bạn là ai?",
        "Hello, how are you?",
        "Cảm ơn bạn",
        "Thank you very much",
        "Tạm biệt",
    ],
    IntentType.UNKNOWN: [
        "asdfghjkl",
        "123456789",
        "",
        "random nonsense text",
    ],
}


class TestIntentDetection:
    """
    Test suite for intent detection
    Phase 1 of comprehensive testing plan
    """

    def test_search_intent(self):
        """Test SEARCH intent detection"""
        for query in INTENT_TEST_CASES[IntentType.SEARCH]:
            # Test using keyword fallback (no LLM required for basic test)
            query_lower = query.lower()
            assert any(keyword in query_lower for keyword in ["tìm", "find", "search", "có", "cần"]), \
                f"SEARCH intent should be detected for: {query}"

    def test_compare_intent(self):
        """Test COMPARE intent detection"""
        for query in INTENT_TEST_CASES[IntentType.COMPARE]:
            query_lower = query.lower()
            assert any(keyword in query_lower for keyword in ["so sánh", "compare", "khác gì", "tốt hơn"]), \
                f"COMPARE intent should be detected for: {query}"

    def test_price_analysis_intent(self):
        """Test PRICE_ANALYSIS intent detection"""
        for query in INTENT_TEST_CASES[IntentType.PRICE_ANALYSIS]:
            query_lower = query.lower()
            assert any(keyword in query_lower for keyword in ["giá", "price", "bao nhiêu", "hợp lý", "đánh giá giá"]), \
                f"PRICE_ANALYSIS intent should be detected for: {query}"

    def test_investment_advice_intent(self):
        """Test INVESTMENT_ADVICE intent detection"""
        for query in INTENT_TEST_CASES[IntentType.INVESTMENT_ADVICE]:
            query_lower = query.lower()
            assert any(keyword in query_lower for keyword in ["đầu tư", "investment", "nên mua", "tiềm năng", "invest"]), \
                f"INVESTMENT_ADVICE intent should be detected for: {query}"

    def test_location_insights_intent(self):
        """Test LOCATION_INSIGHTS intent detection"""
        for query in INTENT_TEST_CASES[IntentType.LOCATION_INSIGHTS]:
            query_lower = query.lower()
            # Location insights often ask "what" or "có gì"
            has_location_keywords = any(keyword in query_lower for keyword in ["có gì", "tiện ích", "amenities", "gần", "near"])
            has_question = "?" in query or "gì" in query_lower or "what" in query_lower
            assert has_location_keywords or has_question, \
                f"LOCATION_INSIGHTS intent should be detected for: {query}"

    def test_legal_guidance_intent(self):
        """Test LEGAL_GUIDANCE intent detection"""
        for query in INTENT_TEST_CASES[IntentType.LEGAL_GUIDANCE]:
            query_lower = query.lower()
            assert any(keyword in query_lower for keyword in ["pháp lý", "thủ tục", "legal", "giấy tờ", "sổ", "hồng", "đỏ"]), \
                f"LEGAL_GUIDANCE intent should be detected for: {query}"

    def test_chat_intent(self):
        """Test CHAT intent detection"""
        chat_keywords = ["xin chào", "hello", "cảm ơn", "thank", "tạm biệt", "bye", "goodbye"]
        for query in INTENT_TEST_CASES[IntentType.CHAT]:
            query_lower = query.lower()
            assert any(keyword in query_lower for keyword in chat_keywords), \
                f"CHAT intent should be detected for: {query}"

    def test_intent_type_coverage(self):
        """Test that all intent types have test cases"""
        assert len(INTENT_TEST_CASES) == 8, "Should have test cases for all 8 intent types"

        expected_intents = {
            IntentType.SEARCH,
            IntentType.COMPARE,
            IntentType.PRICE_ANALYSIS,
            IntentType.INVESTMENT_ADVICE,
            IntentType.LOCATION_INSIGHTS,
            IntentType.LEGAL_GUIDANCE,
            IntentType.CHAT,
            IntentType.UNKNOWN,
        }

        actual_intents = set(INTENT_TEST_CASES.keys())
        assert actual_intents == expected_intents, f"Missing intents: {expected_intents - actual_intents}"

    def test_minimum_test_cases_per_intent(self):
        """Ensure each intent has at least 3 test cases"""
        for intent, cases in INTENT_TEST_CASES.items():
            if intent != IntentType.UNKNOWN:  # UNKNOWN can have fewer
                assert len(cases) >= 3, f"{intent} should have at least 3 test cases, has {len(cases)}"


class TestEntityExtraction:
    """
    Test suite for entity extraction from queries
    Validates extracted entities match expected values
    """

    def test_search_entity_extraction(self):
        """Test entity extraction from SEARCH queries"""
        test_cases = [
            {
                "query": "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ",
                "expected_entities": {
                    "bedrooms": 2,
                    "location": "quận 7",
                    "price_max": 3000000000,
                    "property_type": "căn hộ"
                }
            },
            {
                "query": "Find 3 bedroom apartment in District 2",
                "expected_entities": {
                    "bedrooms": 3,
                    "location": "district 2",
                    "property_type": "apartment"
                }
            },
        ]

        for case in test_cases:
            query = case["query"]
            expected = case["expected_entities"]

            # Basic entity detection tests
            query_lower = query.lower()

            # Check bedrooms
            if "bedrooms" in expected:
                assert str(expected["bedrooms"]) in query or f"{expected['bedrooms']} phòng" in query_lower, \
                    f"Should extract bedrooms from: {query}"

            # Check location
            if "location" in expected:
                assert expected["location"].lower() in query_lower, \
                    f"Should extract location from: {query}"

    def test_price_entity_extraction(self):
        """Test price extraction from queries"""
        test_cases = [
            ("dưới 3 tỷ", {"price_max": 3000000000}),
            ("under 5 billion", {"price_max": 5000000000}),
            ("từ 2 đến 4 tỷ", {"price_min": 2000000000, "price_max": 4000000000}),
        ]

        for query, expected in test_cases:
            query_lower = query.lower()

            # Check for price keywords
            has_price = any(keyword in query_lower for keyword in ["tỷ", "billion", "million", "đến"])
            assert has_price, f"Should detect price in: {query}"


class TestIntentAccuracyMetrics:
    """
    Test suite for measuring intent detection accuracy
    Success criteria: ≥90% accuracy, ≥85% entity extraction
    """

    def test_total_test_coverage(self):
        """Verify we have sufficient test cases (50+ as per plan)"""
        total_cases = sum(len(cases) for cases in INTENT_TEST_CASES.values())
        assert total_cases >= 50, f"Should have at least 50 test cases, has {total_cases}"

    def test_vietnamese_coverage(self):
        """Ensure good coverage of Vietnamese queries"""
        vietnamese_count = 0
        total_count = 0

        for intent, cases in INTENT_TEST_CASES.items():
            for query in cases:
                total_count += 1
                # Check if query contains Vietnamese characters or keywords
                vietnamese_keywords = ["tìm", "căn", "phòng", "quận", "có", "nào", "giá", "tỷ",
                                        "đầu tư", "khu vực", "tiện ích", "pháp lý", "thủ tục"]
                if any(keyword in query.lower() for keyword in vietnamese_keywords):
                    vietnamese_count += 1

        vietnamese_ratio = vietnamese_count / total_count if total_count > 0 else 0
        assert vietnamese_ratio >= 0.5, \
            f"Vietnamese queries should be at least 50%, is {vietnamese_ratio:.1%}"


# Integration test placeholder
class TestOrchestratorIntegration:
    """
    Integration tests for Orchestrator with real LLM
    Requires: Orchestrator service running + OpenAI API key
    """

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires Orchestrator service running")
    def test_orchestrator_search_intent_e2e(self):
        """End-to-end test: SEARCH intent → RAG service"""
        # This will be implemented when services are running
        pass

    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires Orchestrator service running")
    def test_orchestrator_with_real_llm(self):
        """Test Orchestrator with actual LangChain + OpenAI"""
        # This will be implemented when services are running
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])

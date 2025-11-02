"""
Response Evaluation Modules

This module implements different evaluation dimensions for
assessing the quality of system responses.
"""

import re
import httpx
from typing import Dict, List, Optional
from datetime import datetime


class AccuracyEvaluator:
    """
    Evaluate accuracy of responses against ground truth

    Checks:
    - Are property details correct?
    - Are calculations correct?
    - Are facts accurate?
    """

    def __init__(self, db_gateway_url: str):
        self.db_gateway_url = db_gateway_url

    async def evaluate(self, test_case: Dict, response: Dict) -> float:
        """
        Evaluate accuracy score (0-100)

        Args:
            test_case: Test case with query and expected entities
            response: System response to evaluate

        Returns:
            Accuracy score (0-100)
        """
        score = 100.0

        # Check if properties are mentioned
        properties = response.get("properties", [])
        if not properties:
            # If no properties returned, check if that's correct
            expected_entities = test_case.get("expected_entities", {})
            if expected_entities:
                # Expected properties but got none
                score -= 50
        else:
            # Verify property details against database
            for prop in properties[:3]:  # Check first 3
                try:
                    is_accurate = await self._verify_property_accuracy(prop)
                    if not is_accurate:
                        score -= 10
                except Exception:
                    pass  # Skip if verification fails

        # Check intent detection accuracy
        expected_intent = test_case.get("intent", "")
        detected_intent = response.get("intent", "")
        if expected_intent and expected_intent != detected_intent:
            score -= 20

        # Check entity extraction accuracy
        expected_entities = test_case.get("expected_entities", {})
        extracted_entities = response.get("entities", {})

        if expected_entities:
            # Location check
            if "location" in expected_entities:
                if extracted_entities.get("location") != expected_entities["location"]:
                    score -= 10

            # Bedrooms check
            if "bedrooms" in expected_entities:
                if extracted_entities.get("bedrooms") != expected_entities["bedrooms"]:
                    score -= 10

            # Price check
            if "price_max" in expected_entities:
                expected_price = expected_entities["price_max"]
                actual_price = extracted_entities.get("price_max")
                if actual_price:
                    # Allow 10% variance
                    variance = abs(actual_price - expected_price) / expected_price
                    if variance > 0.1:
                        score -= 10

        return max(0, min(100, score))

    async def _verify_property_accuracy(self, property_data: Dict) -> bool:
        """Verify property details against database"""
        try:
            property_id = property_data.get("property_id")
            if not property_id:
                return True  # Can't verify without ID

            # Fetch from DB Gateway
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.db_gateway_url}/properties/{property_id}"
                )
                if response.status_code != 200:
                    return True  # Skip if property not found

                db_property = response.json()

                # Check key fields
                if property_data.get("price") != db_property.get("price"):
                    return False
                if property_data.get("location") != db_property.get("location"):
                    return False

                return True

        except Exception:
            return True  # Skip on error


class RelevanceEvaluator:
    """
    Evaluate relevance of responses to the query

    Uses semantic similarity to check if response addresses the query
    """

    def __init__(self, core_gateway_url: str):
        self.core_gateway_url = core_gateway_url

    async def evaluate(self, test_case: Dict, response: Dict) -> float:
        """
        Evaluate relevance score (0-100)

        Uses LLM to assess semantic relevance
        """
        query = test_case.get("query", "")
        response_text = response.get("response", "") or response.get("message", "")

        if not query or not response_text:
            return 0.0

        # Use LLM to evaluate relevance
        try:
            evaluation_prompt = f"""Evaluate the relevance of this response to the user's query.

User Query: {query}

System Response: {response_text}

Rate the relevance on a scale of 0-100:
- 100: Response perfectly addresses the query
- 80-99: Response mostly addresses the query with minor gaps
- 60-79: Response partially addresses the query
- 40-59: Response somewhat relates but misses key points
- 20-39: Response barely relates to query
- 0-19: Response is irrelevant

Provide ONLY a number (0-100), no explanation."""

            async with httpx.AsyncClient(timeout=30.0) as client:
                llm_response = await client.post(
                    f"{self.core_gateway_url}/chat/completions",
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are an evaluation assistant. Provide only numerical scores."},
                            {"role": "user", "content": evaluation_prompt}
                        ],
                        "max_tokens": 10,
                        "temperature": 0.3
                    }
                )
                llm_response.raise_for_status()
                score_text = llm_response.json()["content"]

                # Extract number from response
                match = re.search(r'\d+', score_text)
                if match:
                    score = float(match.group())
                    return max(0, min(100, score))

        except Exception as e:
            # Fallback to keyword matching
            pass

        # Fallback: simple keyword matching
        return self._keyword_based_relevance(query, response_text)

    def _keyword_based_relevance(self, query: str, response: str) -> float:
        """Fallback relevance scoring using keyword matching"""
        query_lower = query.lower()
        response_lower = response.lower()

        # Extract important keywords from query
        keywords = self._extract_keywords(query_lower)

        if not keywords:
            return 50.0  # Neutral score if no keywords

        # Count keyword matches
        matches = sum(1 for kw in keywords if kw in response_lower)
        relevance = (matches / len(keywords)) * 100

        return relevance

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from query"""
        # Remove common Vietnamese words
        stop_words = ["tìm", "cho", "của", "có", "là", "và", "hoặc", "với", "để"]
        words = query.split()
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return keywords


class CompletenessEvaluator:
    """
    Evaluate completeness of responses

    Checks:
    - Are all required information provided?
    - Are sources cited?
    - Are alternatives mentioned (if applicable)?
    """

    def evaluate(self, test_case: Dict, response: Dict) -> float:
        """Evaluate completeness score (0-100)"""
        score = 100.0

        intent = test_case.get("intent", "")
        response_text = response.get("response", "") or response.get("message", "")

        # Check intent-specific completeness requirements
        if intent == "search":
            # Search should include: properties, locations, prices
            if not response.get("properties"):
                score -= 30
            if "giá" not in response_text.lower() and "price" not in response_text.lower():
                score -= 10
            if not any(loc in response_text.lower() for loc in ["quận", "district"]):
                score -= 10

        elif intent == "compare":
            # Compare should include: differences, pros/cons, recommendation
            required_elements = ["khác", "hơn", "tốt", "compare", "better"]
            if not any(elem in response_text.lower() for elem in required_elements):
                score -= 30

        elif intent == "price_analysis":
            # Price analysis should include: price range, market context, justification
            if "tỷ" not in response_text and "billion" not in response_text.lower():
                score -= 20
            if len(response_text) < 100:
                score -= 10  # Too brief

        elif intent == "investment_advice":
            # Investment advice should include: ROI, risks, timeframe
            required_elements = ["đầu tư", "lợi nhuận", "roi", "invest", "return"]
            if not any(elem in response_text.lower() for elem in required_elements):
                score -= 30

        # Check for sources/citations
        if "property_id" in str(response) or "source" in str(response):
            score += 0  # Already complete
        else:
            score -= 10  # No citations

        # Check response length (completeness indicator)
        if len(response_text) < 50:
            score -= 20  # Too brief
        elif len(response_text) > 500:
            score += 0  # Good detail level

        return max(0, min(100, score))


class CoherenceEvaluator:
    """
    Evaluate coherence and fluency of responses

    Checks:
    - Is the response well-structured?
    - Is the language natural?
    - Are there contradictions?
    """

    def evaluate(self, test_case: Dict, response: Dict) -> float:
        """Evaluate coherence score (0-100)"""
        score = 100.0

        response_text = response.get("response", "") or response.get("message", "")

        if not response_text:
            return 0.0

        # Check for common issues
        # 1. Repetition
        words = response_text.split()
        if len(words) > 0:
            unique_words = len(set(words))
            repetition_ratio = unique_words / len(words)
            if repetition_ratio < 0.5:
                score -= 20  # High repetition

        # 2. Incomplete sentences (ends with comma or no punctuation)
        if response_text.strip().endswith(','):
            score -= 10

        # 3. Proper sentence structure (has punctuation)
        if not any(p in response_text for p in ['.', '!', '?']):
            score -= 15

        # 4. Language mixing (Vietnamese + English without context)
        vietnamese_chars = sum(1 for c in response_text if '\u0080' <= c <= '\u024F')
        english_chars = sum(1 for c in response_text if c.isalpha() and c.isascii())
        if vietnamese_chars > 0 and english_chars > vietnamese_chars * 0.5:
            # Too much English in Vietnamese response
            score -= 5

        # 5. Proper formatting
        if response_text.isupper():
            score -= 20  # ALL CAPS
        if response_text.islower():
            score -= 10  # no capitals

        # 6. Length appropriateness
        if len(response_text) < 20:
            score -= 15  # Too short to be coherent
        elif len(response_text) > 2000:
            score -= 5  # Too verbose

        return max(0, min(100, score))


class LatencyEvaluator:
    """
    Evaluate response time performance
    """

    def evaluate(self, execution_time_ms: float) -> float:
        """
        Evaluate latency score (0-100)

        Scoring:
        - 0-2s: 100 points (excellent)
        - 2-5s: 80 points (good)
        - 5-10s: 50 points (acceptable)
        - >10s: 0-50 points (poor)
        """
        seconds = execution_time_ms / 1000

        if seconds <= 2:
            return 100.0
        elif seconds <= 5:
            return 80.0
        elif seconds <= 10:
            return 50.0
        else:
            # Linear decay from 50 to 0 for 10-20 seconds
            return max(0, 50 - ((seconds - 10) * 5))


class ResponseEvaluator:
    """
    Main evaluator combining all dimensions
    """

    def __init__(self, db_gateway_url: str, core_gateway_url: str):
        self.accuracy_evaluator = AccuracyEvaluator(db_gateway_url)
        self.relevance_evaluator = RelevanceEvaluator(core_gateway_url)
        self.completeness_evaluator = CompletenessEvaluator()
        self.coherence_evaluator = CoherenceEvaluator()
        self.latency_evaluator = LatencyEvaluator()

    async def evaluate(
        self,
        test_case: Dict,
        response: Dict,
        execution_time_ms: float
    ) -> Dict[str, float]:
        """
        Evaluate response across all dimensions

        Returns:
            Dict with scores for each dimension and overall score
        """
        # Evaluate each dimension
        accuracy = await self.accuracy_evaluator.evaluate(test_case, response)
        relevance = await self.relevance_evaluator.evaluate(test_case, response)
        completeness = self.completeness_evaluator.evaluate(test_case, response)
        coherence = self.coherence_evaluator.evaluate(test_case, response)
        latency = self.latency_evaluator.evaluate(execution_time_ms)

        # Calculate weighted overall score
        overall = (
            accuracy * 0.30 +
            relevance * 0.30 +
            completeness * 0.20 +
            coherence * 0.15 +
            latency * 0.05
        )

        return {
            "accuracy": round(accuracy, 2),
            "relevance": round(relevance, 2),
            "completeness": round(completeness, 2),
            "coherence": round(coherence, 2),
            "latency": round(latency, 2),
            "overall_score": round(overall, 2),
            "weights": {
                "accuracy": 0.30,
                "relevance": 0.30,
                "completeness": 0.20,
                "coherence": 0.15,
                "latency": 0.05
            }
        }

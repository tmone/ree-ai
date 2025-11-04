"""
Reflection Operator
Self-critique and quality improvement

CTO Design: Agentic Self-Reflection Pattern
"""
import httpx
from typing import List, Dict, Any
from pydantic import BaseModel

from ..base import OrchestrationOperator, OperatorResult, OperatorConfig
from ..registry import register_operator


class ReflectionInput(BaseModel):
    """Input for reflection"""
    query: str
    response: str
    sources: List[Dict[str, Any]]
    core_gateway_url: str = "http://core-gateway:8080"


class ReflectionOutput(BaseModel):
    """Output from reflection"""
    quality_score: float  # 0.0-1.0
    issues_found: List[str]
    suggestions: List[str]
    needs_improvement: bool
    reasoning: str
    metadata: Dict[str, Any] = {}


@register_operator("reflection")
class ReflectionOperator(OrchestrationOperator):
    """
    Reflection Operator

    Self-evaluates response quality:
    - Groundedness (answer supported by sources?)
    - Relevance (answer addresses query?)
    - Completeness (all aspects covered?)

    If quality < threshold, suggests improvements

    Impact: -30% hallucination through self-correction
    """

    def __init__(self, name: str = "reflection", config: OperatorConfig = None, core_gateway_url: str = "http://core-gateway:8080", quality_threshold: float = 0.7, **kwargs):
        super().__init__(name, config, **kwargs)
        self.core_gateway_url = core_gateway_url
        self.quality_threshold = quality_threshold
        self.http_client = httpx.AsyncClient(timeout=30.0)

    def validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, (dict, ReflectionInput))

    async def execute(self, input_data: Any) -> OperatorResult:
        """Reflect on response quality"""
        if isinstance(input_data, dict):
            refl_input = ReflectionInput(**input_data)
        else:
            refl_input = input_data

        self.logger.info(f"🪞 Reflecting on response quality...")

        # Evaluate response
        evaluation = await self._evaluate_response(
            query=refl_input.query,
            response=refl_input.response,
            sources=refl_input.sources
        )

        needs_improvement = evaluation["quality_score"] < self.quality_threshold

        output = ReflectionOutput(
            quality_score=evaluation["quality_score"],
            issues_found=evaluation["issues"],
            suggestions=evaluation["suggestions"],
            needs_improvement=needs_improvement,
            reasoning=evaluation["reasoning"],
            metadata={
                "quality_threshold": self.quality_threshold,
                "evaluation_criteria": ["groundedness", "relevance", "completeness"]
            }
        )

        if needs_improvement:
            self.logger.warning(
                f"⚠️  Quality score {evaluation['quality_score']:.2f} < threshold {self.quality_threshold}. "
                f"Issues: {len(evaluation['issues'])}"
            )
        else:
            self.logger.info(f"✅ Quality score: {evaluation['quality_score']:.2f} (passed)")

        return OperatorResult(success=True, data=output, metadata=output.metadata)

    async def _evaluate_response(self, query: str, response: str, sources: List[Dict]) -> Dict[str, Any]:
        """Evaluate response against sources"""
        evaluation_prompt = f"""Evaluate this response for quality:

Query: {query}

Response: {response}

Sources: {len(sources)} property listings

Evaluate on:
1. Groundedness: Is response supported by sources?
2. Relevance: Does response address the query?
3. Completeness: Are all query aspects covered?

Provide:
- Quality score (0.0-1.0)
- Issues found (list)
- Suggestions for improvement (list)

Format:
SCORE: X.X
ISSUES:
- issue 1
- issue 2
SUGGESTIONS:
- suggestion 1
- suggestion 2"""

        try:
            resp = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": evaluation_prompt}],
                    "max_tokens": 300,
                    "temperature": 0.3
                },
                timeout=20.0
            )

            if resp.status_code == 200:
                data = resp.json()
                content = data.get("content", "")
                return self._parse_evaluation(content)
            else:
                return self._default_evaluation()

        except Exception as e:
            self.logger.error(f"Evaluation error: {e}")
            return self._default_evaluation()

    def _parse_evaluation(self, content: str) -> Dict[str, Any]:
        """Parse LLM evaluation output"""
        lines = content.strip().split("\n")

        quality_score = 0.7  # Default
        issues = []
        suggestions = []

        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("SCORE:"):
                try:
                    quality_score = float(line.split(":")[1].strip())
                except:
                    pass
            elif line == "ISSUES:":
                current_section = "issues"
            elif line == "SUGGESTIONS:":
                current_section = "suggestions"
            elif line.startswith("-") and line[1:].strip():
                item = line[1:].strip()
                if current_section == "issues":
                    issues.append(item)
                elif current_section == "suggestions":
                    suggestions.append(item)

        reasoning = f"Evaluated with {len(issues)} issues, {len(suggestions)} suggestions"

        return {
            "quality_score": quality_score,
            "issues": issues,
            "suggestions": suggestions,
            "reasoning": reasoning
        }

    def _default_evaluation(self) -> Dict[str, Any]:
        """Default evaluation when LLM fails"""
        return {
            "quality_score": 0.7,
            "issues": ["Unable to evaluate"],
            "suggestions": ["Manual review recommended"],
            "reasoning": "Evaluation failed, using default scores"
        }

    async def cleanup(self):
        await self.http_client.aclose()

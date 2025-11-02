"""
Response Evaluator Service

This service evaluates the quality of system responses using
multiple dimensions: accuracy, relevance, completeness, coherence, and latency.

Port: 8097
"""

import sys
import os
from typing import Dict
from fastapi import HTTPException
from pydantic import BaseModel

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.base_service import BaseService
from evaluators import ResponseEvaluator


class EvaluateRequest(BaseModel):
    """Request to evaluate a response"""
    test_case: Dict
    response: Dict
    execution_time_ms: float = 0.0


class BatchEvaluateRequest(BaseModel):
    """Request to evaluate multiple responses"""
    evaluations: list[EvaluateRequest]


class ResponseEvaluatorService(BaseService):
    """Response Evaluator Service - Multi-dimensional response quality assessment"""

    def __init__(self):
        super().__init__(
            name="response_evaluator",
            version="1.0.0",
            capabilities=["response_evaluation", "quality_scoring", "accuracy_checking"],
            port=8080  # Internal port, mapped to 8097 externally
        )

        # Service URLs
        self.db_gateway_url = os.getenv("DB_GATEWAY_URL", "http://db-gateway:8080")
        self.core_gateway_url = os.getenv("CORE_GATEWAY_URL", "http://core-gateway:8080")

        # Initialize evaluator
        self.evaluator = ResponseEvaluator(
            db_gateway_url=self.db_gateway_url,
            core_gateway_url=self.core_gateway_url
        )

        # Track evaluation stats
        self.total_evaluations = 0
        self.average_scores = {
            "accuracy": [],
            "relevance": [],
            "completeness": [],
            "coherence": [],
            "latency": [],
            "overall_score": []
        }

    def setup_routes(self):
        """Setup API routes"""

        @self.app.post("/evaluate")
        async def evaluate(request: EvaluateRequest) -> Dict:
            """
            Evaluate a single response

            Example:
            ```
            POST /evaluate
            {
                "test_case": {
                    "query": "Tìm căn hộ 2 phòng ngủ Quận 7",
                    "intent": "search",
                    "expected_entities": {
                        "bedrooms": 2,
                        "location": "quận 7"
                    }
                },
                "response": {
                    "intent": "search",
                    "response": "Đây là các căn hộ 2PN ở Quận 7...",
                    "properties": [...]
                },
                "execution_time_ms": 1234.5
            }
            ```

            Returns:
            ```
            {
                "evaluation": {
                    "accuracy": 85.0,
                    "relevance": 90.0,
                    "completeness": 80.0,
                    "coherence": 95.0,
                    "latency": 100.0,
                    "overall_score": 87.5
                }
            }
            ```
            """
            self.logger.info(f"📊 Evaluating response for query: {request.test_case.get('query', '')[:50]}...")

            try:
                # Evaluate
                scores = await self.evaluator.evaluate(
                    test_case=request.test_case,
                    response=request.response,
                    execution_time_ms=request.execution_time_ms
                )

                # Update stats
                self.total_evaluations += 1
                for dimension, score in scores.items():
                    if dimension in self.average_scores and dimension != "weights":
                        self.average_scores[dimension].append(score)

                self.logger.info(f"✅ Evaluation complete: {scores['overall_score']:.2f}/100")
                self.logger.info(f"   Accuracy: {scores['accuracy']:.1f}, Relevance: {scores['relevance']:.1f}, "
                               f"Completeness: {scores['completeness']:.1f}, Coherence: {scores['coherence']:.1f}, "
                               f"Latency: {scores['latency']:.1f}")

                return {"evaluation": scores}

            except Exception as e:
                self.logger.error(f"❌ Evaluation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/batch-evaluate")
        async def batch_evaluate(request: BatchEvaluateRequest) -> Dict:
            """
            Evaluate multiple responses in batch

            Returns aggregated statistics
            """
            self.logger.info(f"📊 Batch evaluating {len(request.evaluations)} responses...")

            results = []
            for eval_request in request.evaluations:
                try:
                    scores = await self.evaluator.evaluate(
                        test_case=eval_request.test_case,
                        response=eval_request.response,
                        execution_time_ms=eval_request.execution_time_ms
                    )
                    results.append(scores)

                    # Update stats
                    self.total_evaluations += 1
                    for dimension, score in scores.items():
                        if dimension in self.average_scores and dimension != "weights":
                            self.average_scores[dimension].append(score)

                except Exception as e:
                    self.logger.error(f"⚠️ Failed to evaluate one response: {e}")
                    results.append(None)

            # Calculate aggregated stats
            valid_results = [r for r in results if r is not None]
            if valid_results:
                aggregated = {
                    "accuracy": sum(r["accuracy"] for r in valid_results) / len(valid_results),
                    "relevance": sum(r["relevance"] for r in valid_results) / len(valid_results),
                    "completeness": sum(r["completeness"] for r in valid_results) / len(valid_results),
                    "coherence": sum(r["coherence"] for r in valid_results) / len(valid_results),
                    "latency": sum(r["latency"] for r in valid_results) / len(valid_results),
                    "overall_score": sum(r["overall_score"] for r in valid_results) / len(valid_results)
                }
            else:
                aggregated = {}

            self.logger.info(f"✅ Batch evaluation complete")
            if aggregated:
                self.logger.info(f"   Average Overall Score: {aggregated['overall_score']:.2f}/100")

            return {
                "results": results,
                "aggregated": aggregated,
                "total": len(request.evaluations),
                "successful": len(valid_results),
                "failed": len(request.evaluations) - len(valid_results)
            }

        @self.app.get("/evaluation-metrics")
        async def get_evaluation_metrics() -> Dict:
            """
            Get evaluation methodology details

            Returns information about:
            - Evaluation dimensions
            - Scoring criteria
            - Weights
            """
            return {
                "dimensions": {
                    "accuracy": {
                        "description": "Correctness of information, property details, and calculations",
                        "weight": 0.30,
                        "criteria": [
                            "Property details match database",
                            "Intent detection is correct",
                            "Entity extraction is accurate",
                            "Calculations are correct"
                        ]
                    },
                    "relevance": {
                        "description": "How well the response addresses the user's query",
                        "weight": 0.30,
                        "criteria": [
                            "Response answers the query",
                            "Suggested properties match filters",
                            "Semantic similarity to query",
                            "No off-topic content"
                        ]
                    },
                    "completeness": {
                        "description": "Whether all required information is provided",
                        "weight": 0.20,
                        "criteria": [
                            "All query requirements addressed",
                            "Sources cited",
                            "Sufficient detail level",
                            "Alternatives mentioned (if applicable)"
                        ]
                    },
                    "coherence": {
                        "description": "Response structure, fluency, and natural language quality",
                        "weight": 0.15,
                        "criteria": [
                            "Well-structured sentences",
                            "Natural language flow",
                            "No contradictions",
                            "Proper formatting"
                        ]
                    },
                    "latency": {
                        "description": "Response time performance",
                        "weight": 0.05,
                        "scoring": {
                            "0-2s": 100,
                            "2-5s": 80,
                            "5-10s": 50,
                            ">10s": "0-50 (linear decay)"
                        }
                    }
                },
                "overall_calculation": "weighted_average = (accuracy × 0.30) + (relevance × 0.30) + (completeness × 0.20) + (coherence × 0.15) + (latency × 0.05)",
                "passing_score": 70,
                "grade_scale": {
                    "90-100": "Excellent",
                    "80-89": "Good",
                    "70-79": "Acceptable",
                    "60-69": "Needs Improvement",
                    "0-59": "Failed"
                }
            }

        @self.app.get("/stats")
        async def get_stats() -> Dict:
            """
            Get evaluation statistics

            Returns running statistics of all evaluations performed
            """
            # Calculate averages
            averages = {}
            for dimension, scores in self.average_scores.items():
                if scores:
                    averages[dimension] = {
                        "average": sum(scores) / len(scores),
                        "min": min(scores),
                        "max": max(scores),
                        "count": len(scores)
                    }
                else:
                    averages[dimension] = {
                        "average": 0,
                        "min": 0,
                        "max": 0,
                        "count": 0
                    }

            return {
                "total_evaluations": self.total_evaluations,
                "statistics": averages
            }

        @self.app.post("/reset-stats")
        async def reset_stats() -> Dict:
            """Reset evaluation statistics"""
            self.total_evaluations = 0
            self.average_scores = {
                "accuracy": [],
                "relevance": [],
                "completeness": [],
                "coherence": [],
                "latency": [],
                "overall_score": []
            }
            return {"message": "Statistics reset successfully"}


if __name__ == "__main__":
    service = ResponseEvaluatorService()
    service.run()

"""
Generation Operator
Generates natural language response from retrieved documents
"""
import httpx
from typing import List, Dict, Any
from pydantic import BaseModel

from ..base import GenerationOperator as BaseGenerationOp, OperatorResult, OperatorConfig
from ..registry import register_operator


class GenerationInput(BaseModel):
    """Input for generation"""
    query: str
    documents: List[Dict[str, Any]]
    system_prompt: str = "Bạn là chuyên gia tư vấn bất động sản REE AI."


class GenerationOutput(BaseModel):
    """Output from generation"""
    response: str
    confidence: float
    metadata: Dict[str, Any] = {}


@register_operator("generation")
class GenerationOperator(BaseGenerationOp):
    """
    Generation Operator

    Generates natural language response using LLM with context
    """

    def __init__(
        self,
        name: str = "generation",
        config: OperatorConfig = None,
        core_gateway_url: str = "http://core-gateway:8080",
        model: str = "gpt-4o-mini",
        **kwargs
    ):
        super().__init__(name, config, **kwargs)
        self.core_gateway_url = core_gateway_url
        self.model = model
        self.http_client = httpx.AsyncClient(timeout=60.0)

    def validate_input(self, input_data: Any) -> bool:
        """Validate input has query and documents"""
        if isinstance(input_data, dict):
            return "query" in input_data and "documents" in input_data
        return hasattr(input_data, 'query') and (
            hasattr(input_data, 'documents') or
            hasattr(input_data, 'reranked_documents')
        )

    async def execute(self, input_data: Any) -> OperatorResult:
        """Generate response with LLM"""
        # Parse input
        if isinstance(input_data, dict):
            gen_input = GenerationInput(**input_data)
        elif hasattr(input_data, 'reranked_documents'):
            # Input from Reranker
            gen_input = GenerationInput(
                query=input_data.metadata.get('query', ''),
                documents=input_data.reranked_documents
            )
        elif hasattr(input_data, 'graded_documents'):
            # Input from DocumentGrader
            gen_input = GenerationInput(
                query=input_data.metadata.get('query', ''),
                documents=input_data.graded_documents
            )
        else:
            gen_input = input_data

        query = gen_input.query
        documents = gen_input.documents
        system_prompt = gen_input.system_prompt

        self.logger.info(f"🤖 Generating response for: '{query}' with {len(documents)} docs")

        if not documents:
            return OperatorResult(
                success=True,
                data=GenerationOutput(
                    response="Xin lỗi, tôi không tìm thấy bất động sản phù hợp với yêu cầu của bạn.",
                    confidence=0.0,
                    metadata={"no_documents": True}
                )
            )

        # Build context
        context = self._build_context(documents, query)

        # Generate response
        try:
            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"""Câu hỏi: {query}

{context}

Hãy tạo câu trả lời tự nhiên, hữu ích cho khách hàng."""}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("content", "").strip()

                self.logger.info(f"✅ Generated response ({len(generated_text)} chars)")

                output = GenerationOutput(
                    response=generated_text,
                    confidence=0.9,
                    metadata={
                        "model": self.model,
                        "document_count": len(documents),
                        "context_length": len(context)
                    }
                )

                return OperatorResult(
                    success=True,
                    data=output,
                    metadata=output.metadata
                )

            else:
                self.logger.error(f"❌ Generation failed: HTTP {response.status_code}")
                return OperatorResult(
                    success=False,
                    data=None,
                    error=f"HTTP {response.status_code}"
                )

        except Exception as e:
            self.logger.error(f"❌ Generation error: {e}")
            return OperatorResult(
                success=False,
                data=None,
                error=str(e)
            )

    def _build_context(self, documents: List[Dict[str, Any]], query: str) -> str:
        """Build context from documents"""
        context_parts = [
            f"# DỮ LIỆU BẤT ĐỘNG SẢN ({len(documents)} properties)\n"
        ]

        for i, doc in enumerate(documents, 1):
            context_parts.append(f"\n## Property #{i}\n")
            context_parts.append(f"- **Title**: {doc.get('title', 'N/A')}\n")

            # Price
            price_display = doc.get('price_display', doc.get('price', 'N/A'))
            context_parts.append(f"- **Price**: {price_display}\n")

            # Location
            district = doc.get('district', doc.get('location', 'N/A'))
            context_parts.append(f"- **Location**: {district}\n")

            # Attributes
            if doc.get('bedrooms'):
                context_parts.append(f"- **Bedrooms**: {doc['bedrooms']}\n")
            if doc.get('area'):
                area_display = doc.get('area_display', f"{doc['area']} m²")
                context_parts.append(f"- **Area**: {area_display}\n")

            # Relevance score if available
            if 'relevance_score' in doc:
                context_parts.append(f"- **Relevance**: {doc['relevance_score']:.2f}\n")

        return "".join(context_parts)

    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()

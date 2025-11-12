"""
Completeness Feedback Service - Layer 2 AI Services
Assesses property listing completeness and provides intelligent feedback
Uses GPT-4 mini for quality assessment
"""
import httpx
import json
from typing import Dict, Optional
from pydantic import BaseModel
from fastapi import HTTPException

from core.base_service import BaseService
from shared.models.core_gateway import LLMRequest, Message, ModelType
from shared.config import settings
from shared.utils.logger import LogEmoji
from services.completeness.prompts import CompletenessPrompts, CompletenessScore


class CompletenessRequest(BaseModel):
    """Request to assess property listing completeness"""
    property_data: Dict
    include_examples: bool = True  # Include few-shot examples in prompt


class CompletenessResponse(BaseModel):
    """Response from completeness assessment"""
    overall_score: float  # 0-100
    interpretation: str  # Score interpretation
    category_scores: Dict[str, float]  # Scores by category
    missing_fields: list[str]  # List of missing fields
    suggestions: list[str]  # Improvement suggestions
    strengths: list[str]  # What's good about this listing
    priority_actions: list[str]  # Top priority improvements


class CompletenessService(BaseService):
    """
    Completeness Feedback Service - Intelligent quality assessment

    Evaluates property listings across 5 categories:
    1. Basic Info (25 points)
    2. Location (20 points)
    3. Physical Attributes (25 points)
    4. Price & Legal (20 points)
    5. Amenities & Contact (10 points)
    """

    def __init__(self):
        super().__init__(
            name="completeness_service",
            version="1.0.0",
            capabilities=["completeness_assessment", "quality_feedback", "improvement_suggestions"],
            port=8080
        )

        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=50,
                keepalive_expiry=30.0
            )
        )
        self.core_gateway_url = settings.get_core_gateway_url()

        self.logger.info(f"{LogEmoji.INFO} Core Gateway: {self.core_gateway_url}")

    def setup_routes(self):
        """Setup completeness assessment API routes"""

        @self.app.post("/assess", response_model=CompletenessResponse)
        async def assess_completeness(request: CompletenessRequest):
            """
            Assess property listing completeness using GPT-4 mini

            Returns detailed feedback:
            - Overall score (0-100)
            - Category breakdown
            - Missing fields
            - Improvement suggestions
            - Strengths
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} Assessing completeness for property: {request.property_data.get('title', 'Untitled')}")

                # Build prompt with property data
                system_prompt = CompletenessPrompts.COMPLETENESS_SYSTEM_PROMPT

                # Build user prompt with property data
                user_prompt = f"""Đánh giá độ đầy đủ của tin đăng bất động sản sau:

{json.dumps(request.property_data, ensure_ascii=False, indent=2)}

Trả về JSON theo định dạng đã nêu."""

                # Add few-shot examples if requested
                if request.include_examples:
                    examples_text = "\n\n📝 FEW-SHOT EXAMPLES:\n"
                    for i, example in enumerate(CompletenessPrompts.FEW_SHOT_EXAMPLES, 1):
                        examples_text += f"\n--- Example {i} ---\n"
                        examples_text += f"INPUT DATA:\n{json.dumps(example['input'], ensure_ascii=False, indent=2)}\n"
                        examples_text += f"ASSESSMENT:\n{json.dumps(example['output'], ensure_ascii=False, indent=2)}\n"

                    user_prompt = examples_text + "\n\n" + user_prompt

                # Call Core Gateway (GPT-4 mini)
                llm_request = LLMRequest(
                    model=ModelType.GPT4_MINI,
                    messages=[
                        Message(role="system", content=system_prompt),
                        Message(role="user", content=user_prompt)
                    ],
                    temperature=0.2,  # Low temperature for consistent assessment
                    max_tokens=800
                )

                response = await self.http_client.post(
                    f"{self.core_gateway_url}/chat/completions",
                    json=llm_request.dict()
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Core Gateway error: {response.text}"
                    )

                data = response.json()
                content = data.get("content", "").strip()

                # Parse JSON response
                try:
                    # Remove markdown code blocks if present
                    if content.startswith("```"):
                        content = content.split("```")[1]
                        if content.startswith("json"):
                            content = content[4:]
                        content = content.strip()

                    result = json.loads(content)

                    # Validate and extract fields
                    overall_score = result.get("overall_score", 0)
                    category_scores = result.get("category_scores", {})
                    missing_fields = result.get("missing_fields", [])
                    suggestions = result.get("suggestions", [])
                    strengths = result.get("strengths", [])
                    priority_actions = result.get("priority_actions", [])

                    # Generate interpretation
                    interpretation = self._get_score_interpretation(overall_score)

                    self.logger.info(f"{LogEmoji.SUCCESS} Assessment complete: {overall_score:.0f}/100 ({interpretation})")
                    self.logger.info(f"{LogEmoji.INFO} Missing fields: {len(missing_fields)}, Suggestions: {len(suggestions)}")

                    return CompletenessResponse(
                        overall_score=overall_score,
                        interpretation=interpretation,
                        category_scores=category_scores,
                        missing_fields=missing_fields,
                        suggestions=suggestions,
                        strengths=strengths,
                        priority_actions=priority_actions
                    )

                except json.JSONDecodeError as e:
                    self.logger.error(f"{LogEmoji.ERROR} Failed to parse LLM response: {content}")
                    # Fallback: Basic heuristic assessment
                    return self._fallback_assessment(request.property_data)

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Completeness assessment failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def _get_score_interpretation(self, score: float) -> str:
        """Get human-readable interpretation of score"""
        if score >= 90:
            return "XUẤT SẮC - Tin đăng rất đầy đủ thông tin"
        elif score >= 80:
            return "TỐT - Đầy đủ thông tin chính"
        elif score >= 70:
            return "KHÁ - Còn thiếu một số thông tin"
        elif score >= 60:
            return "TRUNG BÌNH - Thiếu nhiều thông tin quan trọng"
        else:
            return "YẾU - Cần bổ sung gấp nhiều thông tin"

    def _fallback_assessment(self, property_data: Dict) -> CompletenessResponse:
        """
        Fallback heuristic assessment if LLM fails
        Simple rule-based scoring
        """
        score = 0
        missing_fields = []
        suggestions = []
        strengths = []
        category_scores = {
            "basic_info": 0,
            "location": 0,
            "physical_attributes": 0,
            "price_legal": 0,
            "amenities_contact": 0
        }

        # Basic Info (25 points)
        if property_data.get("property_type"):
            category_scores["basic_info"] += 7
        else:
            missing_fields.append("property_type (Loại BĐS)")

        if property_data.get("transaction_type"):
            category_scores["basic_info"] += 8
        else:
            missing_fields.append("transaction_type (Bán/Thuê)")

        if property_data.get("title"):
            category_scores["basic_info"] += 5
        else:
            missing_fields.append("title (Tiêu đề)")

        if property_data.get("description") and len(property_data["description"]) > 100:
            category_scores["basic_info"] += 5
            strengths.append("✅ Có mô tả chi tiết")

        # Location (20 points)
        if property_data.get("district"):
            category_scores["location"] += 10
            strengths.append("✅ Có thông tin khu vực")
        else:
            missing_fields.append("district (Quận/Huyện)")

        if property_data.get("address"):
            category_scores["location"] += 5
        else:
            missing_fields.append("address (Địa chỉ chi tiết)")

        if property_data.get("ward") or property_data.get("street") or property_data.get("project_name"):
            category_scores["location"] += 5

        # Physical Attributes (25 points)
        if property_data.get("area"):
            category_scores["physical_attributes"] += 10
            strengths.append("✅ Có thông tin diện tích")
        else:
            missing_fields.append("area (Diện tích)")

        if property_data.get("bedrooms"):
            category_scores["physical_attributes"] += 5
        elif property_data.get("property_type") not in ["land", "đất"]:
            missing_fields.append("bedrooms (Số phòng ngủ)")

        if property_data.get("bathrooms") or property_data.get("floors"):
            category_scores["physical_attributes"] += 5

        if property_data.get("facade_width") or property_data.get("direction"):
            category_scores["physical_attributes"] += 5

        # Price & Legal (20 points)
        if property_data.get("price"):
            category_scores["price_legal"] += 10
            strengths.append("✅ Có thông tin giá")
        else:
            missing_fields.append("price (Giá) - BẮT BUỘC")

        if property_data.get("legal_status"):
            category_scores["price_legal"] += 5
        else:
            missing_fields.append("legal_status (Pháp lý)")

        if property_data.get("price_per_m2"):
            category_scores["price_legal"] += 3

        if property_data.get("ownership_type"):
            category_scores["price_legal"] += 2

        # Amenities & Contact (10 points)
        if property_data.get("contact_phone"):
            category_scores["amenities_contact"] += 5
            strengths.append("✅ Có số điện thoại liên hệ")
        else:
            missing_fields.append("contact_phone (Số điện thoại) - BẮT BUỘC")

        if property_data.get("contact_name") or property_data.get("contact_type"):
            category_scores["amenities_contact"] += 2

        amenity_count = sum([
            1 for key in ["parking", "elevator", "pool", "gym", "security"]
            if property_data.get(key)
        ])
        if amenity_count >= 3:
            category_scores["amenities_contact"] += 3

        # Calculate total
        overall_score = sum(category_scores.values())

        # Generate suggestions based on missing fields
        if not property_data.get("contact_phone"):
            suggestions.append("📌 BỔ SUNG NGAY số điện thoại liên hệ - bắt buộc!")
        if not property_data.get("price"):
            suggestions.append("📌 BỔ SUNG NGAY giá - thông tin bắt buộc!")
        if not property_data.get("legal_status"):
            suggestions.append("📌 Thêm thông tin pháp lý (sổ đỏ/hồng) để tăng độ tin cậy")
        if not property_data.get("bedrooms") and property_data.get("property_type") not in ["land", "đất"]:
            suggestions.append("📌 Bổ sung số phòng ngủ - thông tin quan trọng")
        if not property_data.get("description") or len(property_data.get("description", "")) < 100:
            suggestions.append("📌 Viết mô tả chi tiết hơn (>100 từ) để thu hút người xem")

        interpretation = self._get_score_interpretation(overall_score)

        # Priority actions
        priority_actions = []
        if not property_data.get("contact_phone"):
            priority_actions.append("1. BỔ SUNG SỐ ĐIỆN THOẠI - URGENT")
        if not property_data.get("price"):
            priority_actions.append("2. BỔ SUNG GIÁ - URGENT")
        if not property_data.get("legal_status"):
            priority_actions.append("3. Thêm thông tin pháp lý - QUAN TRỌNG")

        return CompletenessResponse(
            overall_score=overall_score,
            interpretation=interpretation,
            category_scores=category_scores,
            missing_fields=missing_fields,
            suggestions=suggestions[:5],  # Top 5 suggestions
            strengths=strengths,
            priority_actions=priority_actions
        )

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()
        self.logger.info(f"{LogEmoji.INFO} HTTP client closed")
        await super().on_shutdown()


if __name__ == "__main__":
    service = CompletenessService()
    service.run()

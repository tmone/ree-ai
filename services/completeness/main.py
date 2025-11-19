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
from shared.utils.i18n import t
from services.completeness.prompts import CompletenessPrompts, CompletenessScore


class CompletenessRequest(BaseModel):
    """Request to assess property listing completeness"""
    property_data: Dict
    language: str = "vi"  # User's preferred language (vi, en, th, ja)
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
                        detail=t("completeness.core_gateway_error", language=request.language, detail=response.text)
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
                    interpretation = self._get_score_interpretation(overall_score, request.language)

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
                    return self._fallback_assessment(request.property_data, request.language)

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Completeness assessment failed: {e}")
                raise HTTPException(status_code=500, detail=t("completeness.assessment_failed", language=request.language, error=str(e)))

    def _get_score_interpretation(self, score: float, language: str = 'vi') -> str:
        """Get human-readable interpretation of score"""
        if score >= 90:
            return t("completeness.score_excellent", language=language)
        elif score >= 80:
            return t("completeness.score_good", language=language)
        elif score >= 70:
            return t("completeness.score_fair", language=language)
        elif score >= 60:
            return t("completeness.score_average", language=language)
        else:
            return t("completeness.score_poor", language=language)

    def _fallback_assessment(self, property_data: Dict, language: str = 'vi') -> CompletenessResponse:
        """
        Fallback heuristic assessment if LLM fails
        Simple rule-based scoring

        Updated scoring (100 points total):
        - Basic Info: 20 points
        - Location: 20 points
        - Physical Attributes (size): 20 points
        - Price & Legal: 15 points
        - Media (images): 15 points - REQUIRED
        - Amenities & Contact: 10 points
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
            "media": 0,
            "amenities_contact": 0
        }

        # Basic Info (20 points)
        if property_data.get("property_type"):
            category_scores["basic_info"] += 6
        else:
            missing_fields.append(t("completeness.missing_property_type", language=language))

        if property_data.get("transaction_type") or property_data.get("listing_type"):
            category_scores["basic_info"] += 6
        else:
            missing_fields.append(t("completeness.missing_transaction_type", language=language))

        if property_data.get("title"):
            category_scores["basic_info"] += 4
        else:
            missing_fields.append(t("completeness.missing_title", language=language))

        if property_data.get("description") and len(property_data["description"]) > 100:
            category_scores["basic_info"] += 4
            strengths.append(t("completeness.strength_description", language=language))

        # Location (20 points)
        if property_data.get("district"):
            category_scores["location"] += 10
            strengths.append(t("completeness.strength_location", language=language))
        else:
            missing_fields.append(t("completeness.missing_district", language=language))

        if property_data.get("address"):
            category_scores["location"] += 5
        else:
            missing_fields.append(t("completeness.missing_address", language=language))

        if property_data.get("ward") or property_data.get("street") or property_data.get("project_name"):
            category_scores["location"] += 5

        # Physical Attributes / Size (20 points) - REQUIRED
        if property_data.get("area") or property_data.get("land_area"):
            category_scores["physical_attributes"] += 8
            strengths.append(t("completeness.strength_area", language=language))
        else:
            missing_fields.append(t("completeness.missing_area", language=language))

        # Width & Depth (dài, rộng) - Important for townhouse/land
        if property_data.get("width") and property_data.get("depth"):
            category_scores["physical_attributes"] += 6
            strengths.append("Có thông tin chiều dài và chiều rộng")
        elif property_data.get("width") or property_data.get("depth"):
            category_scores["physical_attributes"] += 3
            missing_fields.append("Thiếu chiều dài hoặc chiều rộng")

        if property_data.get("bedrooms"):
            category_scores["physical_attributes"] += 3
        elif property_data.get("property_type") not in ["land", "đất"]:
            missing_fields.append(t("completeness.missing_bedrooms", language=language))

        if property_data.get("bathrooms") or property_data.get("floors"):
            category_scores["physical_attributes"] += 3

        # Price & Legal (15 points) - REQUIRED
        if property_data.get("price"):
            category_scores["price_legal"] += 10
            strengths.append(t("completeness.strength_price", language=language))
        else:
            missing_fields.append(t("completeness.missing_price", language=language))

        if property_data.get("legal_status"):
            category_scores["price_legal"] += 3
        else:
            missing_fields.append(t("completeness.missing_legal_status", language=language))

        if property_data.get("ownership_type"):
            category_scores["price_legal"] += 2

        # Media - Images (15 points) - REQUIRED
        images = property_data.get("images", [])
        if images and len(images) > 0:
            if len(images) >= 5:
                category_scores["media"] += 15
                strengths.append("Có đầy đủ hình ảnh (5+ ảnh)")
            elif len(images) >= 3:
                category_scores["media"] += 10
                suggestions.append("Nên thêm ít nhất 5 hình ảnh để thu hút người xem")
            else:
                category_scores["media"] += 5
                suggestions.append("Cần thêm ít nhất 3 hình ảnh để tin đăng hấp dẫn hơn")
        else:
            missing_fields.append("Hình ảnh (bắt buộc)")
            suggestions.append("⚠️ QUAN TRỌNG: Thêm hình ảnh bất động sản để đăng tin")

        # Bonus for video
        if property_data.get("videos") and len(property_data["videos"]) > 0:
            strengths.append("Có video giới thiệu")

        # Amenities & Contact (10 points)
        if property_data.get("contact_phone"):
            category_scores["amenities_contact"] += 5
            strengths.append(t("completeness.strength_contact", language=language))
        else:
            missing_fields.append(t("completeness.missing_contact_phone", language=language))

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
        if not images or len(images) == 0:
            suggestions.insert(0, "⚠️ BẮT BUỘC: Thêm hình ảnh để đăng tin")
        if not property_data.get("price"):
            suggestions.append(t("completeness.suggestion_add_price", language=language))
        if not (property_data.get("area") or property_data.get("land_area")):
            suggestions.append("Thêm diện tích (m²)")
        if not property_data.get("district"):
            suggestions.append("Thêm địa chỉ/quận huyện")
        if not property_data.get("bedrooms") and property_data.get("property_type") not in ["land", "đất"]:
            suggestions.append(t("completeness.suggestion_add_bedrooms", language=language))

        interpretation = self._get_score_interpretation(overall_score, language)

        # Priority actions - Images first!
        priority_actions = []
        if not images or len(images) == 0:
            priority_actions.append("🔴 BẮT BUỘC: Thêm hình ảnh bất động sản")
        if not property_data.get("price"):
            priority_actions.append(t("completeness.priority_price_urgent", language=language))
        if not (property_data.get("area") or property_data.get("land_area")):
            priority_actions.append("🟡 QUAN TRỌNG: Thêm diện tích")
        if not property_data.get("district"):
            priority_actions.append("🟡 QUAN TRỌNG: Thêm địa chỉ")

        # Suggest map GPS if basic location is provided
        if property_data.get("district") and not property_data.get("latitude"):
            suggestions.append("💡 GỢI Ý: Chọn vị trí trên bản đồ để người mua dễ tìm")

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

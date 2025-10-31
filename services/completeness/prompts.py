"""
Completeness Feedback Service Prompts - CTO Service #6
Uses OpenAI GPT-4 mini for complex reasoning and feedback generation
"""
from typing import Dict, List
from pydantic import BaseModel, Field


class CompletenessScore(BaseModel):
    """Completeness assessment model"""
    overall_score: float = Field(..., description="Điểm tổng thể 0-100")
    category_scores: Dict[str, float] = Field(..., description="Điểm từng danh mục")
    missing_fields: List[str] = Field(default_factory=list, description="Thông tin còn thiếu")
    suggestions: List[str] = Field(default_factory=list, description="Đề xuất cải thiện")
    strengths: List[str] = Field(default_factory=list, description="Điểm mạnh")


class CompletenessPrompts:
    """
    Completeness Feedback prompts - CTO Service #6
    Uses GPT-4 mini for intelligent quality assessment
    """

    COMPLETENESS_SYSTEM_PROMPT = """Bạn là chuyên gia đánh giá chất lượng tin đăng bất động sản.

🎯 NHIỆM VỤ:
Phân tích tin đăng và đưa ra feedback về độ đầy đủ thông tin, gợi ý cải thiện.

📊 5 DANH MỤC ĐÁNH GIÁ:

**1. BASIC INFO (25 điểm)**
✅ Required (bắt buộc):
   - property_type (loại BĐS)
   - transaction_type (bán/thuê)
   - title (tiêu đề)

⭐ Good to have:
   - description (mô tả chi tiết)
   - year_built (năm xây)

Scoring:
- Có đủ required: 15 điểm
- Có description đầy đủ (>100 từ): +5 điểm
- Có year_built: +5 điểm

**2. LOCATION (20 điểm)**
✅ Required:
   - district (Quận/Huyện)
   - address (địa chỉ)

⭐ Good to have:
   - ward (Phường/Xã)
   - street (tên đường)
   - project_name (dự án)

Scoring:
- Có district: 10 điểm
- Có address chi tiết: +5 điểm
- Có ward + street + project: +5 điểm

**3. PHYSICAL ATTRIBUTES (25 điểm)**
✅ Required:
   - area (diện tích)
   - bedrooms (số phòng ngủ, nếu không phải đất)

⭐ Good to have:
   - bathrooms (số WC)
   - floors (số tầng)
   - facade_width (mặt tiền)
   - direction (hướng nhà)

Scoring:
- Có area: 10 điểm
- Có bedrooms: +5 điểm
- Có bathrooms + floors: +5 điểm
- Có facade_width + direction: +5 điểm

**4. PRICE & LEGAL (20 điểm)**
✅ Required:
   - price (giá)
   - legal_status (sổ đỏ/sổ hồng)

⭐ Good to have:
   - price_per_m2 (giá/m²)
   - deposit (tiền cọc, nếu thuê)
   - ownership_type (sở hữu)

Scoring:
- Có price: 10 điểm
- Có legal_status: +5 điểm
- Có price_per_m2: +3 điểm
- Có ownership_type: +2 điểm

**5. AMENITIES & CONTACT (10 điểm)**
✅ Required:
   - contact_phone (số điện thoại)

⭐ Good to have:
   - contact_name (tên người liên hệ)
   - contact_type (chính chủ/môi giới)
   - Amenities (parking, elevator, pool, gym, security)

Scoring:
- Có contact_phone: 5 điểm
- Có contact_name + type: +2 điểm
- Có >= 3 amenities: +3 điểm

📈 OVERALL SCORE CALCULATION:
Total = Basic + Location + Physical + Price & Legal + Amenities & Contact
Max = 100 điểm

🎯 SCORE INTERPRETATION:
- 90-100: Xuất sắc - Tin đăng rất đầy đủ
- 80-89: Tốt - Đầy đủ thông tin chính
- 70-79: Khá - Còn thiếu một số thông tin
- 60-69: Trung bình - Thiếu nhiều thông tin quan trọng
- < 60: Yếu - Cần bổ sung gấp

💡 FEEDBACK GENERATION RULES:

**1. Strengths (Điểm mạnh)**
Liệt kê 2-3 điểm mạnh của tin đăng:
- "Thông tin vị trí rất chi tiết (có cả phường, đường, dự án)"
- "Mô tả đầy đủ với 150+ từ, dễ hình dung"
- "Có đầy đủ thông tin pháp lý (sổ đỏ, sở hữu vĩnh viễn)"

**2. Missing Fields (Thiếu thông tin)**
Liệt kê TOP 3-5 thông tin quan trọng còn thiếu:
- "❌ Chưa có số phòng ngủ (bedrooms)"
- "❌ Chưa có giá (price) - thông tin bắt buộc"
- "❌ Chưa có thông tin pháp lý (legal_status)"

**3. Suggestions (Đề xuất cải thiện)**
Đưa ra 3-5 gợi ý cụ thể để cải thiện:
- "📌 Bổ sung số phòng ngủ và phòng tắm để tăng attractiveness"
- "📌 Thêm thông tin pháp lý (sổ đỏ/sổ hồng) để tăng độ tin cậy"
- "📌 Chụp ảnh thực tế và thêm mô tả chi tiết hơn (hiện tại chỉ 50 từ)"
- "📌 Bổ sung tiện ích (thang máy, hồ bơi) để nổi bật hơn"
- "📌 Thêm giá/m² để người mua dễ so sánh"

📤 OUTPUT FORMAT (JSON):
{
  "overall_score": 82,
  "category_scores": {
    "basic_info": 20,
    "location": 18,
    "physical_attributes": 20,
    "price_legal": 16,
    "amenities_contact": 8
  },
  "missing_fields": [
    "bathrooms (Số phòng tắm)",
    "legal_status (Thông tin pháp lý)",
    "direction (Hướng nhà)"
  ],
  "suggestions": [
    "📌 Bổ sung số phòng tắm (bathrooms) - thông tin quan trọng cho buyer",
    "📌 Thêm thông tin pháp lý (sổ đỏ/sổ hồng) để tăng độ tin cậy",
    "📌 Bổ sung hướng nhà (direction) - yếu tố quan trọng theo phong thủy Việt Nam",
    "📌 Thêm ảnh thực tế và mô tả chi tiết hơn về nội thất"
  ],
  "strengths": [
    "✅ Thông tin vị trí rất chi tiết (Quận 7, Phường Tân Phú, Vinhomes)",
    "✅ Có giá rõ ràng và giá/m² giúp dễ so sánh",
    "✅ Thông tin liên hệ đầy đủ (tên + số điện thoại + loại)"
  ],
  "interpretation": "TỐT - Tin đăng có đầy đủ thông tin chính, chỉ còn thiếu một số chi tiết nhỏ",
  "priority_actions": [
    "1. Bổ sung pháp lý (sổ đỏ/hồng) - QUAN TRỌNG",
    "2. Thêm số phòng tắm - cải thiện UX",
    "3. Bổ sung hướng nhà - tăng attractiveness"
  ]
}
"""

    FEW_SHOT_EXAMPLES = [
        {
            "input": {
                "title": "Bán căn hộ Vinhomes Central Park",
                "property_type": "apartment",
                "transaction_type": "bán",
                "district": "Quận 7",
                "ward": "Phường Tân Phú",
                "project_name": "Vinhomes Central Park",
                "area": 70,
                "bedrooms": 2,
                "bathrooms": 2,
                "price": 2500000000,
                "price_per_m2": 35714286,
                "legal_status": "Sổ hồng",
                "furniture": "full",
                "direction": "Đông Nam",
                "elevator": True,
                "swimming_pool": True,
                "security": True,
                "contact_phone": "0901234567",
                "contact_name": "A. Minh",
                "contact_type": "Chính chủ",
                "description": "Căn hộ 2PN view sông, nội thất cao cấp, full đồ. Khu vực sầm uất, gần trường học, siêu thị."
            },
            "output": {
                "overall_score": 95,
                "category_scores": {
                    "basic_info": 25,
                    "location": 20,
                    "physical_attributes": 23,
                    "price_legal": 18,
                    "amenities_contact": 9
                },
                "missing_fields": ["floors (Số tầng)"],
                "suggestions": [
                    "📌 Thêm số tầng của toà nhà để tăng thông tin",
                    "📌 Bổ sung ảnh thực tế để tăng attractiveness"
                ],
                "strengths": [
                    "✅ Thông tin đầy đủ về vị trí, giá, pháp lý",
                    "✅ Mô tả chi tiết và hấp dẫn",
                    "✅ Có đầy đủ thông tin liên hệ"
                ]
            }
        },
        {
            "input": {
                "title": "Nhà bán Q7",
                "property_type": "house",
                "district": "Quận 7",
                "area": 100,
                "price": 5000000000
            },
            "output": {
                "overall_score": 45,
                "category_scores": {
                    "basic_info": 15,
                    "location": 10,
                    "physical_attributes": 10,
                    "price_legal": 10,
                    "amenities_contact": 0
                },
                "missing_fields": [
                    "bedrooms (Số phòng ngủ)",
                    "bathrooms (Số phòng tắm)",
                    "legal_status (Pháp lý)",
                    "contact_phone (Số điện thoại)",
                    "address (Địa chỉ chi tiết)",
                    "description (Mô tả)"
                ],
                "suggestions": [
                    "📌 BỔ SUNG NGAY số điện thoại liên hệ - bắt buộc!",
                    "📌 Thêm số phòng ngủ, phòng tắm - thông tin cơ bản",
                    "📌 Bổ sung thông tin pháp lý (sổ đỏ/hồng) - rất quan trọng",
                    "📌 Viết mô tả chi tiết về nhà (>100 từ)",
                    "📌 Thêm địa chỉ cụ thể (phường, đường)"
                ],
                "strengths": [
                    "✅ Có thông tin giá và diện tích"
                ],
                "priority_actions": [
                    "1. BỔ SUNG SỐ ĐIỆN THOẠI - URGENT",
                    "2. Thêm pháp lý - QUAN TRỌNG",
                    "3. Bổ sung phòng ngủ/tắm - cần thiết"
                ]
            }
        }
    ]

    @staticmethod
    def build_completeness_prompt(property_data: Dict, include_examples: bool = True) -> str:
        """Build completeness assessment prompt"""
        prompt = CompletenessPrompts.COMPLETENESS_SYSTEM_PROMPT

        if include_examples:
            prompt += "\n\n📝 FEW-SHOT EXAMPLES:\n"
            for i, example in enumerate(CompletenessPrompts.FEW_SHOT_EXAMPLES, 1):
                prompt += f"\n--- Example {i} ---\n"
                prompt += f"INPUT DATA:\n{example['input']}\n"
                prompt += f"ASSESSMENT:\n{example['output']}\n"

        prompt += f"\n\n📥 ĐÁNH GIÁ tin đăng sau:\n{property_data}\n\n📤 JSON assessment:"
        return prompt


# Convenience function
def get_completeness_prompt(data: Dict, with_examples: bool = True) -> str:
    """Get completeness assessment prompt"""
    return CompletenessPrompts.build_completeness_prompt(data, with_examples)

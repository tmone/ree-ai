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
Phân tích tin đăng và đưa ra feedback NGẮN GỌN về độ đầy đủ thông tin.

⚡ UX PRINCIPLES (QUAN TRỌNG):
1. **Progressive Disclosure**: CHỈ hỏi 1-2 thông tin thiếu quan trọng nhất mỗi lần
2. **Clear Exit Point**: Khi score >= 60%, đặt ready_to_post = true và DỪNG hỏi thêm
3. **Short Responses**: Người dùng không có thời gian đọc nhiều, chỉ liệt kê điều cần thiết
4. **Prioritize**: Hỏi CRITICAL fields trước (property_type, district, price, area)

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

🎯 QUESTIONING PRIORITY (CHỈ HỎI 1-2 FIELDS MỖI LẦN):

**CRITICAL (Hỏi trước tiên nếu thiếu):**
1. property_type, transaction_type (Turn 1)
2. district, price/price_rent (Turn 2)
3. area (Turn 3)

**HIGH PRIORITY (Hỏi thứ hai nếu thiếu):**
4. bedrooms, bathrooms (skip nếu LAND)
5. contact_phone

**MEDIUM PRIORITY (Chỉ hỏi nếu score < 60%):**
6. title
7. ward, street
8. furniture, direction, legal_status

**STOP POINT:**
Khi overall_score >= 60%, đặt ready_to_post = true và DỪNG hỏi thêm.
Người dùng có thể tự bổ sung, nhưng KHÔNG push thêm.

📤 OUTPUT FORMAT (JSON) - NGẮN GỌN:
{
  "overall_score": 68,
  "ready_to_post": true,  // NEW: true nếu overall_score >= 60%
  "next_questions": [      // NEW: CHỈ 1-2 thông tin thiếu QUAN TRỌNG NHẤT
    {
      "field": "district",
      "question_vi": "Căn hộ ở quận nào?"
    },
    {
      "field": "price_rent",
      "question_vi": "Giá thuê bao nhiêu/tháng?"
    }
  ],
  "collected_summary": [   // NEW: Tóm tắt ngắn gọn những gì đã có
    "Căn hộ cho thuê",
    "2 phòng ngủ, 70m²"
  ],
  "missing_critical": ["contact_phone", "title"]  // CHỈ critical fields còn thiếu
}

💡 LOGIC TẠO next_questions:
1. Nếu score < 60%: Chọn 1-2 CRITICAL fields thiếu theo priority
2. Nếu score >= 60%: next_questions = [] (RỖNG - đừng hỏi thêm!)
3. Format câu hỏi ngắn gọn, dễ hiểu (ví dụ: "Căn hộ ở quận nào?")

💡 LOGIC TẠO collected_summary:
1. Tóm tắt thông tin đã có thành 2-4 bullet points ngắn
2. Ví dụ: ["Căn hộ cho thuê, Quận 7", "70m², 2 phòng ngủ", "Giá: 10 triệu/tháng"]
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
                "ready_to_post": True,
                "next_questions": [],  # Score >= 60%, không hỏi thêm
                "collected_summary": [
                    "Căn hộ bán, Vinhomes Central Park, Quận 7",
                    "70m², 2PN 2WC, full nội thất",
                    "Giá: 2.5 tỷ (36 triệu/m²)",
                    "Sổ hồng, hướng Đông Nam"
                ],
                "missing_critical": []  # Đã đủ thông tin critical
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
                "ready_to_post": False,  # Score < 60%, cần thêm thông tin
                "next_questions": [  # CHỈ hỏi 1-2 thông tin quan trọng nhất
                    {
                        "field": "bedrooms",
                        "question_vi": "Nhà có bao nhiêu phòng ngủ?"
                    },
                    {
                        "field": "contact_phone",
                        "question_vi": "Cho tôi số điện thoại liên hệ?"
                    }
                ],
                "collected_summary": [
                    "Nhà bán, Quận 7",
                    "Diện tích: 100m²",
                    "Giá: 5 tỷ"
                ],
                "missing_critical": ["bedrooms", "contact_phone", "legal_status", "address"]
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

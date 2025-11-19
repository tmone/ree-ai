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

📊 6 DANH MỤC ĐÁNH GIÁ (100 điểm):

**1. BASIC INFO (20 điểm)**
✅ Required (bắt buộc):
   - property_type (loại BĐS)
   - listing_type/transaction_type (bán/thuê)
   - title (tiêu đề)

⭐ Good to have:
   - description (mô tả chi tiết)

Scoring:
- Có property_type: 6 điểm
- Có listing_type: 6 điểm
- Có title: 4 điểm
- Có description đầy đủ (>100 từ): +4 điểm

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

**3. PHYSICAL ATTRIBUTES / SIZE (20 điểm)** - BẮT BUỘC
✅ Required:
   - area hoặc land_area (diện tích)
   - width + depth (chiều rộng, chiều dài) - đặc biệt cho nhà phố/đất

⭐ Good to have:
   - bedrooms (số phòng ngủ, nếu không phải đất)
   - bathrooms (số WC)
   - floors (số tầng)

Scoring:
- Có area/land_area: 8 điểm
- Có width + depth: +6 điểm (có 1 trong 2: +3 điểm)
- Có bedrooms: +3 điểm
- Có bathrooms + floors: +3 điểm

**4. PRICE & LEGAL (15 điểm)** - BẮT BUỘC
✅ Required:
   - price (giá)

⭐ Good to have:
   - legal_status (sổ đỏ/sổ hồng)
   - ownership_type (sở hữu)

Scoring:
- Có price: 10 điểm
- Có legal_status: +3 điểm
- Có ownership_type: +2 điểm

**5. MEDIA - IMAGES (15 điểm)** - BẮT BUỘC
✅ Required:
   - images (hình ảnh) - TỐI THIỂU 1 ảnh

⭐ Good to have:
   - 3+ hình ảnh
   - 5+ hình ảnh (tốt nhất)
   - video (video giới thiệu)

Scoring:
- Có 5+ ảnh: 15 điểm
- Có 3-4 ảnh: 10 điểm
- Có 1-2 ảnh: 5 điểm
- Không có ảnh: 0 điểm (⚠️ BẮT BUỘC phải có!)

**6. AMENITIES & CONTACT (10 điểm)**
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
Total = Basic (20) + Location (20) + Physical (20) + Price (15) + Media (15) + Contact (10)
Max = 100 điểm

🎯 SCORE INTERPRETATION:
- 90-100: Xuất sắc - Tin đăng rất đầy đủ
- 80-89: Tốt - Đầy đủ thông tin chính
- 70-79: Khá - Còn thiếu một số thông tin
- 60-69: Trung bình - Thiếu một số thông tin quan trọng
- < 60: Yếu - Cần bổ sung thông tin bắt buộc

🎯 QUESTIONING PRIORITY (CHỈ HỎI 1-2 FIELDS MỖI LẦN):

**CRITICAL - BẮT BUỘC (Hỏi trước tiên nếu thiếu):**
1. listing_type (bán/thuê) (Turn 1)
2. district/address (địa chỉ) (Turn 1-2)
3. area (diện tích) (Turn 2)
4. price (giá) (Turn 2-3)
5. images (hình ảnh) ⚠️ BẮT BUỘC - Nếu thiếu, yêu cầu upload!

**HIGH PRIORITY (Hỏi thứ hai nếu thiếu):**
6. width, depth (dài, rộng) - cho nhà phố/đất
7. bedrooms, bathrooms (skip nếu LAND)

**MEDIUM PRIORITY (Gợi ý nếu score < 80%):**
8. latitude, longitude (tọa độ bản đồ) - Gợi ý chọn trên Google Maps
9. contact_phone
10. legal_status

**STOP POINT:**
Khi overall_score >= 60% VÀ có hình ảnh, đặt ready_to_post = true.
⚠️ KHÔNG cho post nếu thiếu hình ảnh, dù score cao!

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
                "listing_type": "sale",
                "district": "Quận 7",
                "ward": "Phường Tân Phú",
                "project_name": "Vinhomes Central Park",
                "area": 70,
                "bedrooms": 2,
                "bathrooms": 2,
                "price": 2500000000,
                "legal_status": "Sổ hồng",
                "furniture": "full",
                "direction": "Đông Nam",
                "images": ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg"],
                "contact_phone": "0901234567",
                "contact_name": "A. Minh",
                "description": "Căn hộ 2PN view sông, nội thất cao cấp."
            },
            "output": {
                "overall_score": 92,
                "ready_to_post": True,
                "next_questions": [],
                "collected_summary": [
                    "Căn hộ bán, Vinhomes Central Park, Quận 7",
                    "70m², 2PN 2WC, full nội thất",
                    "Giá: 2.5 tỷ",
                    "5 hình ảnh, Sổ hồng"
                ],
                "missing_critical": []
            }
        },
        {
            "input": {
                "title": "Nhà phố Q7",
                "property_type": "townhouse",
                "listing_type": "sale",
                "district": "Quận 7",
                "area": 100,
                "width": 5,
                "depth": 20,
                "price": 5000000000
            },
            "output": {
                "overall_score": 40,
                "ready_to_post": False,
                "next_questions": [
                    {
                        "field": "images",
                        "question_vi": "⚠️ Vui lòng upload hình ảnh bất động sản (kéo thả vào khung chat)"
                    },
                    {
                        "field": "bedrooms",
                        "question_vi": "Nhà có bao nhiêu phòng ngủ?"
                    }
                ],
                "collected_summary": [
                    "Nhà phố bán, Quận 7",
                    "100m² (ngang 5m x dài 20m)",
                    "Giá: 5 tỷ"
                ],
                "missing_critical": ["images", "bedrooms", "contact_phone"]
            }
        },
        {
            "input": {
                "property_type": "land",
                "listing_type": "sale",
                "district": "Bình Chánh",
                "land_area": 200,
                "width": 10,
                "depth": 20,
                "price": 3000000000,
                "images": ["anh1.jpg", "anh2.jpg"]
            },
            "output": {
                "overall_score": 65,
                "ready_to_post": True,
                "next_questions": [],
                "collected_summary": [
                    "Đất bán, Bình Chánh",
                    "200m² (10m x 20m)",
                    "Giá: 3 tỷ",
                    "2 hình ảnh"
                ],
                "missing_critical": [],
                "suggestions": [
                    "💡 Gợi ý: Chọn vị trí trên Google Maps để người mua dễ tìm",
                    "Nên thêm ít nhất 3 hình ảnh"
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

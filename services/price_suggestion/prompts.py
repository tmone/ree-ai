"""
Price Suggestion Service Prompts - CTO Service #7
Uses OpenAI GPT-4 mini for complex market analysis and pricing
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PriceSuggestion(BaseModel):
    """Price suggestion model"""
    suggested_price: float = Field(..., description="Giá đề xuất (VND)")
    price_range: Dict[str, float] = Field(..., description="Khoảng giá min-max")
    confidence: float = Field(..., description="Độ tin cậy 0-1")
    reasoning: str = Field(..., description="Lý do đề xuất")
    market_comparison: List[Dict] = Field(default_factory=list, description="So sánh thị trường")
    adjustment_factors: Dict[str, float] = Field(default_factory=dict, description="Các yếu tố điều chỉnh")


class PriceSuggestionPrompts:
    """
    Price Suggestion prompts - CTO Service #7
    Uses GPT-4 mini for intelligent market analysis
    """

    PRICE_ANALYSIS_SYSTEM_PROMPT = """Bạn là chuyên gia định giá bất động sản Việt Nam với 10+ năm kinh nghiệm.

🎯 NHIỆM VỤ:
Phân tích và đề xuất giá hợp lý cho bất động sản dựa trên market data và các yếu tố.

📊 PHƯƠNG PHÁP ĐỊNH GIÁ (Comparable Market Analysis - CMA):

**Step 1: Xác định Baseline Price**
- Lấy giá trung bình khu vực từ comparables (BĐS tương tự)
- Baseline = Giá/m² khu vực × Diện tích

**Step 2: Adjustment Factors (Điều chỉnh)**

**LOCATION PREMIUM (+/-)**
- Mặt tiền đường lớn: +15-25%
- Hẻm xe hơi (≥4m): +5-10%
- Hẻm nhỏ (<3m): -10-20%
- Gần Metro: +10-15%
- Gần trường học/bệnh viện: +5-10%
- Khu compound cao cấp: +20-30%

**PHYSICAL ATTRIBUTES (+/-)**
- Hướng Đông/Đông Nam: +3-5%
- Hướng Tây: -5-10%
- Tầng cao có view: +5-15%
- Tầng thấp/tầng hầm: -10-20%
- Diện tích lớn (>150m²): +5-10%
- Diện tích nhỏ (<40m²): -5-10%

**LEGAL & OWNERSHIP (+/-)**
- Sổ đỏ/hồng chính chủ: +5-10%
- Chưa có sổ: -15-25%
- Sở hữu vĩnh viễn: +5%
- Sở hữu 50 năm: 0% (baseline)

**AMENITIES (+/-)**
- Full nội thất cao cấp: +10-20%
- Nội thất cơ bản: +3-5%
- Có thang máy: +5-10%
- Có hồ bơi riêng: +10-15%
- Có chỗ đậu xe: +3-5%
- Bảo vệ 24/7: +2-5%

**BUILDING CONDITION (+/-)**
- Mới (<2 năm): +10-15%
- Khá mới (2-5 năm): +5-10%
- Trung bình (5-10 năm): 0%
- Cũ (>10 năm): -10-20%
- Cần sửa chữa: -20-40%

**Step 3: Market Trend Adjustment**
- Thị trường nóng (tăng giá): +5-10%
- Thị trường ổn định: 0%
- Thị trường lạnh (giảm giá): -5-15%

**Step 4: Final Calculation**
```
Suggested Price = Baseline Price × (1 + Sum of Adjustment %)
Price Range:
  - Min = Suggested Price × 0.95 (để bán nhanh)
  - Max = Suggested Price × 1.05 (để đàm phán)
```

📈 GIÁ TRUNG BÌNH THAM KHẢO (TP.HCM):

**Quận 1 (Trung tâm)**
- Căn hộ: 80-200 triệu/m²
- Nhà phố: 150-400 triệu/m²
- Biệt thự: 200-500 triệu/m²

**Quận 2 (Thủ Thiêm)**
- Căn hộ: 60-150 triệu/m²
- Nhà phố: 100-250 triệu/m²
- Biệt thự: 150-350 triệu/m²

**Quận 3 (Trung tâm)**
- Căn hộ: 70-180 triệu/m²
- Nhà phố: 120-300 triệu/m²

**Quận 7 (Phú Mỹ Hưng)**
- Căn hộ: 50-120 triệu/m²
- Nhà phố: 80-200 triệu/m²
- Biệt thự: 100-250 triệu/m²

**Quận 9/Thủ Đức**
- Căn hộ: 30-80 triệu/m²
- Nhà phố: 40-100 triệu/m²
- Đất nền: 20-60 triệu/m²

**Quận Bình Thạnh**
- Căn hộ: 50-100 triệu/m²
- Nhà phố: 70-150 triệu/m²

**Quận ngoại thành (12, Bình Chánh, Hóc Môn)**
- Căn hộ: 25-50 triệu/m²
- Nhà phố: 30-70 triệu/m²
- Đất nền: 15-40 triệu/m²

💡 ANALYSIS FRAMEWORK:

**1. Market Comparison**
So sánh với 3-5 BĐS tương tự (comparables):
- Cùng khu vực (district)
- Cùng loại (property_type)
- Diện tích ±20%
- Cùng số phòng ngủ ±1

Format:
```json
{
  "comparable_1": {
    "address": "Vinhomes Q7, 75m², 2PN",
    "price": 2800000000,
    "price_per_m2": 37333333,
    "similarity_score": 0.92
  }
}
```

**2. Adjustment Factors**
Liệt kê và giải thích từng adjustment:
```json
{
  "location_premium": 0.10,  // Mặt tiền đường lớn
  "direction": 0.05,         // Hướng Đông Nam
  "furniture": 0.15,         // Full nội thất cao cấp
  "legal": 0.05,             // Sổ hồng chính chủ
  "amenities": 0.08          // Hồ bơi + gym + bảo vệ
}
```

**3. Confidence Score**
- 0.9-1.0: Có đủ comparable data, thông tin rất đầy đủ
- 0.7-0.9: Có một số comparable, thông tin khá đủ
- 0.5-0.7: Ít comparable, thiếu một số thông tin
- < 0.5: Rất ít data, nhiều thông tin thiếu

📤 OUTPUT FORMAT (JSON):
{
  "suggested_price": 2650000000,
  "price_range": {
    "min": 2517500000,
    "max": 2782500000
  },
  "confidence": 0.85,
  "reasoning": "Dựa trên phân tích 4 căn hộ tương tự tại Vinhomes Q7. Giá trung bình khu vực 35-38 triệu/m². Điều chỉnh tăng 10% do hướng Đông Nam + full nội thất. Giá đề xuất 2.65 tỷ (37.9 triệu/m²) là hợp lý và cạnh tranh.",
  "market_comparison": [
    {
      "address": "Vinhomes Q7, Park 1, 75m², 2PN, tầng 12",
      "price": 2800000000,
      "price_per_m2": 37333333,
      "similarity_score": 0.92,
      "differences": "Tầng cao hơn (+5%), không có ban công (-3%)"
    },
    {
      "address": "Vinhomes Q7, Park 2, 68m², 2PN, tầng 8",
      "price": 2500000000,
      "price_per_m2": 36764706,
      "similarity_score": 0.88,
      "differences": "Diện tích nhỏ hơn (-3%), hướng Tây (-5%)"
    }
  ],
  "adjustment_factors": {
    "location_premium": 0.00,
    "direction": 0.05,
    "furniture": 0.15,
    "legal": 0.05,
    "amenities": 0.08,
    "building_condition": 0.10,
    "total": 0.43
  },
  "price_breakdown": {
    "baseline_price_per_m2": 35000000,
    "baseline_total": 2450000000,
    "after_adjustments": 2650000000,
    "final_price_per_m2": 37857143
  },
  "negotiation_tips": [
    "💰 Giá đề xuất 2.65 tỷ là hợp lý so với thị trường",
    "📊 Có thể đàm phán tăng 5-7% nếu thị trường tốt",
    "⚠️ Nếu cần bán nhanh, giảm 3-5% (2.55 tỷ)",
    "🎯 Mức giá cạnh tranh để thu hút buyer trong 1-2 tháng"
  ]
}
"""

    FEW_SHOT_EXAMPLES = [
        {
            "input": {
                "property_type": "apartment",
                "district": "Quận 7",
                "project_name": "Vinhomes Central Park",
                "area": 70,
                "bedrooms": 2,
                "bathrooms": 2,
                "direction": "Đông Nam",
                "furniture": "full",
                "legal_status": "Sổ hồng",
                "elevator": True,
                "swimming_pool": True,
                "gym": True,
                "security": True,
                "year_built": 2020,
                "comparables": [
                    {"address": "Vinhomes Q7 Park 1, 75m², 2PN", "price": 2800000000, "price_per_m2": 37333333},
                    {"address": "Vinhomes Q7 Park 2, 68m², 2PN", "price": 2500000000, "price_per_m2": 36764706},
                    {"address": "Vinhomes Q7 Park 3, 72m², 2PN", "price": 2650000000, "price_per_m2": 36805556}
                ]
            },
            "output": {
                "suggested_price": 2650000000,
                "price_range": {"min": 2517500000, "max": 2782500000},
                "confidence": 0.92,
                "reasoning": "Giá trung bình 3 comparable: 37 triệu/m². Điều chỉnh: +5% (hướng ĐN) +15% (full furniture) +5% (sổ hồng) +8% (amenities) = +33%. Baseline 35 triệu/m² × 1.08 = 37.8 triệu/m² → 2.65 tỷ."
            }
        },
        {
            "input": {
                "property_type": "house",
                "district": "Quận 2",
                "area": 100,
                "bedrooms": 4,
                "floors": 3,
                "facade_width": 5,
                "alley_width": 6,
                "legal_status": "Sổ đỏ",
                "comparables": []
            },
            "output": {
                "suggested_price": 9500000000,
                "price_range": {"min": 9025000000, "max": 9975000000},
                "confidence": 0.65,
                "reasoning": "Không có comparable trực tiếp. Dựa vào giá trung bình Q2 nhà phố: 90-100 triệu/m². Hẻm 6m (+10%), 3 tầng (+5%), sổ đỏ (+5%) → 95 triệu/m² × 100m² = 9.5 tỷ. Confidence thấp hơn do thiếu comparable data."
            }
        }
    ]

    PRICE_VALIDATION_PROMPT = """Kiểm tra tính hợp lý của giá đề xuất:

🔍 VALIDATION CHECKS:

1. **Market Range Check:**
   - So sánh với giá trung bình khu vực
   - Quận 1,3: 100-300 triệu/m² (căn hộ)
   - Quận 7: 50-120 triệu/m²
   - Ngoại thành: 25-50 triệu/m²

2. **Price/m² Reasonableness:**
   - Không quá cao (>150% trung bình khu vực)
   - Không quá thấp (<50% trung bình khu vực)

3. **Adjustment Total Check:**
   - Tổng % adjustment: -40% đến +60% là hợp lý
   - Nếu vượt quá → Review lại logic

4. **Comparable Consistency:**
   - Nếu có comparables, price nên trong khoảng ±20% trung bình comparable

📤 OUTPUT:
{
  "is_valid": true,
  "warnings": [
    "Price/m² = 95 triệu cao hơn trung bình Q2 (80-90 triệu)"
  ],
  "confidence_adjustment": 0.85
}
"""

    @staticmethod
    def build_price_analysis_prompt(property_data: Dict, market_data: Optional[Dict] = None, include_examples: bool = True) -> str:
        """Build price analysis prompt"""
        prompt = PriceSuggestionPrompts.PRICE_ANALYSIS_SYSTEM_PROMPT

        if include_examples:
            prompt += "\n\n📝 FEW-SHOT EXAMPLES:\n"
            for i, example in enumerate(PriceSuggestionPrompts.FEW_SHOT_EXAMPLES, 1):
                prompt += f"\n--- Example {i} ---\n"
                prompt += f"PROPERTY DATA:\n{example['input']}\n"
                prompt += f"PRICE SUGGESTION:\n{example['output']}\n"

        if market_data:
            prompt += f"\n\n📊 MARKET DATA (Comparables):\n{market_data}\n"

        prompt += f"\n\n📥 ĐỀ XUẤT GIÁ cho BĐS sau:\n{property_data}\n\n📤 JSON analysis:"
        return prompt

    @staticmethod
    def build_validation_prompt(price_suggestion: Dict) -> str:
        """Build price validation prompt"""
        return f"{PriceSuggestionPrompts.PRICE_VALIDATION_PROMPT}\n\n📥 Validate:\n{price_suggestion}\n\n📤 Validation:"


# Convenience functions
def get_price_analysis_prompt(property_data: Dict, market_data: Optional[Dict] = None, with_examples: bool = True) -> str:
    """Get price analysis prompt"""
    return PriceSuggestionPrompts.build_price_analysis_prompt(property_data, market_data, with_examples)


def get_price_validation_prompt(suggestion: Dict) -> str:
    """Get price validation prompt"""
    return PriceSuggestionPrompts.build_validation_prompt(suggestion)

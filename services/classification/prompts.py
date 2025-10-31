"""
Classification Service Prompts - CTO Service #5
3 modes: Filter (keywords), Semantic (LLM), Both (hybrid)
Uses Ollama (llama3.1:8b) for FREE semantic classification
"""
from typing import Dict, List
from enum import Enum


class PropertyType(str, Enum):
    """Property types for classification"""
    HOUSE = "house"  # Nhà riêng, nhà phố
    APARTMENT = "apartment"  # Căn hộ, chung cư
    VILLA = "villa"  # Biệt thự
    LAND = "land"  # Đất, lô đất
    COMMERCIAL = "commercial"  # Văn phòng, mặt bằng kinh doanh
    UNKNOWN = "unknown"


class ClassificationMode(str, Enum):
    """Classification modes"""
    FILTER = "filter"  # Fast keyword matching
    SEMANTIC = "semantic"  # LLM-based understanding
    BOTH = "both"  # Hybrid approach


class ClassificationPrompts:
    """
    Classification prompts for CTO Service #5
    3 modes for different speed/accuracy tradeoffs
    """

    # Mode 2: Semantic Classification (Ollama)
    SEMANTIC_CLASSIFICATION_PROMPT = """Bạn là chuyên gia phân loại bất động sản Việt Nam.

🎯 NHIỆM VỤ:
Phân loại bất động sản vào 1 trong 5 loại dựa trên mô tả.

📊 5 LOẠI BẤT ĐỘNG SẢN:

**1. HOUSE (Nhà riêng, Nhà phố)**
Đặc điểm:
- Nhà độc lập, nhà liền kề, nhà phố
- Có mặt tiền đường/hẻm
- Thường 2-5 tầng
- Sở hữu riêng, có sân/vườn
Keywords: nhà, nhà riêng, nhà phố, townhouse, nhà mặt tiền, nhà hẻm

**2. APARTMENT (Căn hộ, Chung cư)**
Đặc điểm:
- Căn hộ trong tòa nhà cao tầng
- Ở các tầng lầu (không có mặt đất)
- Có thang máy, bảo vệ chung
- Sở hữu theo căn hộ, không có sân riêng
Keywords: căn hộ, chung cư, apartment, condo, penthouse, studio, officetel

**3. VILLA (Biệt thự)**
Đặc điểm:
- Nhà cao cấp, diện tích lớn (>200m²)
- Có sân vườn rộng
- Thiết kế sang trọng, riêng biệt
- Thường trong khu compound
Keywords: biệt thự, villa, luxury house, nhà vườn cao cấp

**4. LAND (Đất, Lô đất)**
Đặc điểm:
- Mảnh đất trống hoặc có nhà cũ cần phá
- Mục đích: xây mới, đầu tư
- Không có công trình chính đang sử dụng
Keywords: đất, land, lô đất, mảnh đất, đất nền, đất thổ cư, đất công nghiệp

**5. COMMERCIAL (Thương mại)**
Đặc điểm:
- Mục đích kinh doanh, văn phòng
- Mặt bằng kinh doanh, shophouse
- Văn phòng, tòa nhà thương mại
Keywords: văn phòng, office, commercial, shophouse, mặt bằng, cửa hàng, ki ốt

🔍 PHÂN LOẠI LOGIC:

1. **Có phải căn hộ cao tầng?**
   YES → APARTMENT
   NO → Continue

2. **Có phải đất trống/không có nhà?**
   YES → LAND
   NO → Continue

3. **Có phải mục đích thương mại?**
   YES → COMMERCIAL
   NO → Continue

4. **Diện tích > 200m² + thiết kế cao cấp + sân vườn?**
   YES → VILLA
   NO → HOUSE

5. **Không xác định được?**
   → UNKNOWN

📝 FEW-SHOT EXAMPLES:

Example 1:
Input: "Bán căn hộ 2PN Vinhomes Central Park, tầng 15, view sông"
Analysis: "căn hộ" + tầng cao → APARTMENT
Output: {
  "type": "apartment",
  "confidence": 0.98,
  "reasoning": "Căn hộ trong tòa cao tầng, có tầng lầu cụ thể (tầng 15)"
}

Example 2:
Input: "Nhà phố 1 trệt 2 lầu, mặt tiền đường Nguyễn Văn Linh, 4x20m"
Analysis: Nhà phố + mặt tiền + không quá sang → HOUSE
Output: {
  "type": "house",
  "confidence": 0.95,
  "reasoning": "Nhà phố có mặt tiền đường, cấu trúc trệt + lầu điển hình"
}

Example 3:
Input: "Biệt thự Thảo Điền 500m², có hồ bơi, sân vườn 300m²"
Analysis: Diện tích lớn + hồ bơi + sân vườn → VILLA
Output: {
  "type": "villa",
  "confidence": 0.97,
  "reasoning": "Diện tích lớn (500m²), có hồ bơi và sân vườn rộng, khu cao cấp"
}

Example 4:
Input: "Bán đất nền KDC Vạn Phúc, 100m², sổ hồng riêng"
Analysis: Đất nền + sổ hồng → LAND
Output: {
  "type": "land",
  "confidence": 0.96,
  "reasoning": "Đất nền trong khu dân cư, chưa có công trình"
}

Example 5:
Input: "Cho thuê mặt bằng kinh doanh 50m², mặt tiền Lê Lợi"
Analysis: Mặt bằng kinh doanh → COMMERCIAL
Output: {
  "type": "commercial",
  "confidence": 0.94,
  "reasoning": "Mặt bằng kinh doanh, mục đích thương mại rõ ràng"
}

Example 6:
Input: "Bán nhà đẹp Q7"
Analysis: Thông tin quá ít, "nhà" có thể là house/apartment/villa
Output: {
  "type": "house",
  "confidence": 0.60,
  "reasoning": "Từ 'nhà' thường chỉ nhà riêng, nhưng thiếu thông tin chi tiết nên confidence thấp"
}

💡 LƯU Ý:

1. **Ưu tiên keywords rõ ràng:**
   - "căn hộ", "chung cư" → 100% APARTMENT
   - "biệt thự", "villa" → 100% VILLA
   - "đất", "đất nền" → 100% LAND

2. **Context matters:**
   - "Nhà" + "tầng 15" → APARTMENT (không phải HOUSE)
   - "Nhà" + "mặt tiền" + "trệt lầu" → HOUSE
   - "Nhà" + "> 200m²" + "hồ bơi" → VILLA

3. **Confidence scoring:**
   - 0.9-1.0: Rất chắc chắn (có keyword trực tiếp)
   - 0.7-0.9: Khá chắc (suy luận từ context)
   - 0.5-0.7: Không chắc (thiếu thông tin)
   - < 0.5: Rất không chắc → Nên return UNKNOWN

4. **Edge cases:**
   - Shophouse: Thường là COMMERCIAL (mục đích kinh doanh)
   - Penthouse: APARTMENT (vẫn là căn hộ dù cao cấp)
   - Officetel: APARTMENT (căn hộ văn phòng)
   - Nhà vườn: VILLA nếu > 200m², HOUSE nếu nhỏ hơn

📤 OUTPUT FORMAT (JSON):
{
  "type": "apartment",
  "confidence": 0.95,
  "reasoning": "Căn hộ trong tòa cao tầng với các đặc điểm điển hình"
}

🚫 KHÔNG được:
- Bịa thông tin không có trong mô tả
- Return confidence > 0.9 khi không chắc chắn
- Phân loại vội vàng khi thiếu context
"""

    # Mode 3: Hybrid Decision Logic
    HYBRID_DECISION_PROMPT = """Quyết định kết quả cuối cùng từ 2 phương pháp phân loại:

🔍 INPUT:
- Filter result: {filter_result} (từ keyword matching)
- Semantic result: {semantic_result} (từ LLM, confidence: {semantic_confidence})

📊 DECISION LOGIC:

**Rule 1: High confidence semantic (>= 0.85)**
→ Trust semantic result
Reason: LLM có context understanding tốt hơn keywords

**Rule 2: Semantic confidence medium (0.70-0.84) + Filter agrees**
→ Trust both (use semantic result)
Reason: Cả 2 phương pháp đồng thuận

**Rule 3: Semantic confidence medium (0.70-0.84) + Filter disagrees**
→ Trust semantic if reasoning is strong
→ Trust filter if semantic reasoning is weak

**Rule 4: Semantic confidence low (< 0.70) + Filter has result**
→ Trust filter
Reason: Keyword matching đáng tin hơn khi LLM không chắc

**Rule 5: Both UNKNOWN**
→ Return UNKNOWN
Reason: Không đủ thông tin

📤 OUTPUT:
{
  "final_type": "apartment",
  "final_confidence": 0.92,
  "method_used": "semantic",
  "reasoning": "Semantic có confidence cao (0.95), filter cũng đồng ý (apartment)"
}
"""

    FEW_SHOT_EXAMPLES = [
        {
            "input": "Bán căn hộ 2PN Vinhomes Central Park Q7",
            "output": {
                "type": "apartment",
                "confidence": 0.98,
                "reasoning": "Keywords 'căn hộ' + tên dự án cao tầng → Apartment chắc chắn"
            }
        },
        {
            "input": "Nhà phố 1 trệt 2 lầu MT Nguyễn Văn Linh 4x20m",
            "output": {
                "type": "house",
                "confidence": 0.95,
                "reasoning": "Nhà phố + mặt tiền + cấu trúc trệt lầu → House"
            }
        },
        {
            "input": "Biệt thự Thảo Điền 500m² sân vườn hồ bơi",
            "output": {
                "type": "villa",
                "confidence": 0.97,
                "reasoning": "Diện tích lớn + tiện ích cao cấp → Villa"
            }
        },
        {
            "input": "Bán đất nền 100m² KDC Vạn Phúc sổ hồng",
            "output": {
                "type": "land",
                "confidence": 0.96,
                "reasoning": "Đất nền + sổ hồng + chưa có nhà → Land"
            }
        }
    ]

    # Keyword filters for Mode 1: Filter
    KEYWORDS = {
        PropertyType.HOUSE: [
            "nhà", "nhà riêng", "nhà phố", "house", "townhouse",
            "nhà mặt tiền", "nhà hẻm", "nhà liền kề"
        ],
        PropertyType.APARTMENT: [
            "căn hộ", "chung cư", "apartment", "condo", "penthouse",
            "studio", "officetel", "can ho", "chung cu"
        ],
        PropertyType.VILLA: [
            "biệt thự", "villa", "biet thu", "nhà vườn cao cấp",
            "luxury house"
        ],
        PropertyType.LAND: [
            "đất", "land", "lô đất", "mảnh đất", "đất nền",
            "đất thổ cư", "dat", "dat nen"
        ],
        PropertyType.COMMERCIAL: [
            "văn phòng", "office", "commercial", "shophouse",
            "mặt bằng", "mặt bằng kinh doanh", "cửa hàng",
            "ki ốt", "kiot", "mat bang"
        ]
    }

    @staticmethod
    def build_semantic_prompt(text: str, include_examples: bool = True) -> str:
        """Build semantic classification prompt with few-shot examples"""
        prompt = ClassificationPrompts.SEMANTIC_CLASSIFICATION_PROMPT

        if include_examples:
            prompt += "\n\n📝 Thêm ví dụ từ database:\n"
            for example in ClassificationPrompts.FEW_SHOT_EXAMPLES:
                prompt += f"\nInput: {example['input']}\n"
                prompt += f"Output: {example['output']}\n"

        prompt += f"\n\n📥 PHÂN LOẠI:\n{text}\n\n📤 JSON output:"
        return prompt

    @staticmethod
    def build_hybrid_prompt(
        filter_result: str,
        semantic_result: str,
        semantic_confidence: float
    ) -> str:
        """Build hybrid decision prompt"""
        return ClassificationPrompts.HYBRID_DECISION_PROMPT.format(
            filter_result=filter_result,
            semantic_result=semantic_result,
            semantic_confidence=semantic_confidence
        )

    @staticmethod
    def get_keywords() -> Dict[PropertyType, List[str]]:
        """Get keyword dictionary for filter mode"""
        return ClassificationPrompts.KEYWORDS


# Convenience functions
def get_semantic_prompt(text: str, with_examples: bool = True) -> str:
    """Get semantic classification prompt"""
    return ClassificationPrompts.build_semantic_prompt(text, with_examples)


def get_hybrid_decision_prompt(filter_result: str, semantic_result: str, confidence: float) -> str:
    """Get hybrid decision prompt"""
    return ClassificationPrompts.build_hybrid_prompt(filter_result, semantic_result, confidence)


def get_keywords() -> Dict[PropertyType, List[str]]:
    """Get classification keywords"""
    return ClassificationPrompts.get_keywords()

"""
Attribute Extraction Service Prompts - CTO Service #4
Uses Ollama (FREE) for structured property data extraction
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PropertyAttributes(BaseModel):
    """Structured property attributes model"""
    # Basic Info
    title: Optional[str] = Field(None, description="Tiêu đề tin đăng")
    property_type: Optional[str] = Field(None, description="Loại BĐS: căn hộ, nhà phố, biệt thự, đất, commercial")
    transaction_type: Optional[str] = Field(None, description="Loại giao dịch: bán, cho thuê")

    # Location
    district: Optional[str] = Field(None, description="Quận/Huyện")
    ward: Optional[str] = Field(None, description="Phường/Xã")
    street: Optional[str] = Field(None, description="Đường")
    address: Optional[str] = Field(None, description="Địa chỉ đầy đủ")
    project_name: Optional[str] = Field(None, description="Tên dự án (nếu có)")

    # Physical Attributes
    area: Optional[float] = Field(None, description="Diện tích (m²)")
    bedrooms: Optional[int] = Field(None, description="Số phòng ngủ")
    bathrooms: Optional[int] = Field(None, description="Số phòng tắm")
    floors: Optional[int] = Field(None, description="Số tầng")
    facade_width: Optional[float] = Field(None, description="Mặt tiền (m)")
    alley_width: Optional[float] = Field(None, description="Hẻm rộng (m)")

    # Price
    price: Optional[float] = Field(None, description="Giá (VND)")
    price_per_m2: Optional[float] = Field(None, description="Giá/m² (VND/m²)")
    deposit: Optional[float] = Field(None, description="Tiền cọc (VND)")

    # Legal
    legal_status: Optional[str] = Field(None, description="Sổ đỏ, sổ hồng, hợp đồng mua bán")
    ownership_type: Optional[str] = Field(None, description="Sở hữu: vĩnh viễn, 50 năm")

    # Features
    furniture: Optional[str] = Field(None, description="Nội thất: full, cơ bản, không")
    direction: Optional[str] = Field(None, description="Hướng: Đông, Tây, Nam, Bắc, ĐN, ĐB, TN, TB")
    balcony_direction: Optional[str] = Field(None, description="Hướng ban công")

    # Amenities
    parking: Optional[bool] = Field(None, description="Có chỗ đậu xe")
    elevator: Optional[bool] = Field(None, description="Có thang máy")
    swimming_pool: Optional[bool] = Field(None, description="Có hồ bơi")
    gym: Optional[bool] = Field(None, description="Có phòng gym")
    security: Optional[bool] = Field(None, description="Có bảo vệ 24/7")

    # Contact
    contact_name: Optional[str] = Field(None, description="Tên người liên hệ")
    contact_phone: Optional[str] = Field(None, description="Số điện thoại")
    contact_type: Optional[str] = Field(None, description="Chính chủ, môi giới, sàn")

    # Additional
    description: Optional[str] = Field(None, description="Mô tả đầy đủ")
    year_built: Optional[int] = Field(None, description="Năm xây dựng")


class AttributeExtractionPrompts:
    """
    Attribute Extraction prompts - CTO Service #4
    Uses Ollama (llama3.1:8b) for FREE structured extraction
    """

    EXTRACTION_SYSTEM_PROMPT = """Bạn là chuyên gia trích xuất thông tin bất động sản từ văn bản.

🎯 NHIỆM VỤ:
Đọc mô tả bất động sản và trích xuất TẤT CẢ thông tin thành JSON có cấu trúc.

⭐ ƯU TIÊN COLLECTION:
Hệ thống yêu cầu TỐI THIỂU 15-20 fields để có tin đăng chuyên nghiệp!
- TIER 1 (CRITICAL - BẮT BUỘC): property_type, transaction_type, district, area, price
- TIER 2 (HIGHLY RECOMMENDED): bedrooms, bathrooms, ward, street, furniture, direction, legal_status, contact_phone
- TIER 3 (RECOMMENDED): floors, facade_width, balcony_direction, year_built, project_name, contact_name
- TIER 4 (OPTIONAL): amenities, description, images

📊 CATEGORIES CẦN TRÍCH XUẤT:

**1. BASIC INFO**
- title: Tiêu đề tin đăng
- property_type: căn hộ | nhà phố | biệt thự | đất | commercial
- transaction_type: bán | cho thuê

**2. LOCATION**
- district: Quận/Huyện (chuẩn hóa: "Quận 1", "Quận 7", "Huyện Bình Chánh")
- ward: Phường/Xã
- street: Tên đường
- address: Địa chỉ đầy đủ
- project_name: Vinhomes, Masteri, The Manor, etc.

**3. PHYSICAL ATTRIBUTES**
- area: Diện tích (m²) - Extract số, bỏ chữ
- bedrooms: Số phòng ngủ (nullable cho đất/parking/commercial)
- bathrooms: Số phòng tắm/WC
- floors: Số tầng
- facade_width: Mặt tiền (m)
- alley_width: Hẻm rộng (m)

**4. PRICE**
- price: Giá (VND) - Chuẩn hóa về số (hỗ trợ cả dấu chấm và phẩy)
- price_per_m2: Giá/m² - Tự tính nếu có đủ thông tin
- deposit: Tiền cọc (VND)

**5. LEGAL**
- legal_status: Sổ đỏ | Sổ hồng | Hợp đồng mua bán | Chưa có sổ
- ownership_type: Vĩnh viễn | 50 năm | 99 năm

**6. FEATURES**
- furniture: full | cơ bản | không | cao cấp
- direction: Đông | Tây | Nam | Bắc | Đông Nam | Đông Bắc | Tây Nam | Tây Bắc
- balcony_direction: Hướng ban công

**7. AMENITIES (boolean)**
- parking: true nếu có chỗ đậu xe, garage, bãi xe
- elevator: true nếu có thang máy, lift
- swimming_pool: true nếu có hồ bơi
- gym: true nếu có phòng gym, fitness
- security: true nếu có bảo vệ 24/7, security

**8. CONTACT**
- contact_name: Tên người liên hệ
- contact_phone: Số điện thoại (giữ nguyên format)
- contact_type: Chính chủ | Môi giới | Sàn BĐS

**9. ADDITIONAL**
- description: Mô tả chi tiết (giữ nguyên text gốc)
- year_built: Năm xây dựng

🔍 EXTRACTION RULES:

1. **Chuẩn hóa địa danh:**
   - "Q7" → "Quận 7"
   - "Q.2" → "Quận 2"
   - "Bình Thạnh" → "Quận Bình Thạnh"
   - "Thủ Đức" → "Quận Thủ Đức" (nếu < 2021) hoặc "Thành phố Thủ Đức"

2. **Chuẩn hóa số:**
   - "2.5 tỷ" → 2500000000
   - "70m²" → 70
   - "5x20m" → 100 (diện tích = 5 * 20)

3. **Xử lý thiếu thông tin:**
   - Nếu không có thông tin → `null`
   - Nếu không chắc chắn → `null` (đừng đoán)

4. **Ưu tiên thông tin:**
   - Thông tin trong tiêu đề > Thông tin trong mô tả
   - Số chính xác > Khoảng số

5. **Tính toán tự động:**
   - Nếu có price và area → Tính price_per_m2
   - Nếu có mặt tiền x hẻm → Tính area (nếu chưa có)

6. **Property-type specific extraction:**
   - Đất (LAND): KHÔNG cần bedrooms, bathrooms, furniture → Emphasize legal_status, facade_width
   - Căn hộ (APARTMENT): CẦN floor number, view_type, project_name, balcony_direction
   - Nhà phố/Biệt thự (HOUSE/VILLA): CẦN floors, facade_width, alley_width
   - Commercial (OFFICE/SHOPHOUSE/WAREHOUSE): CẦN floors, facade_width, parking_capacity

📤 OUTPUT FORMAT:
```json
{
  "title": "Bán căn hộ 2PN Vinhomes Q7",
  "property_type": "căn hộ",
  "transaction_type": "bán",
  "district": "Quận 7",
  "project_name": "Vinhomes Central Park",
  "area": 70,
  "bedrooms": 2,
  "bathrooms": 2,
  "price": 2500000000,
  "price_per_m2": 35714286,
  "legal_status": "Sổ hồng",
  "furniture": "full",
  "direction": "Đông Nam",
  "parking": true,
  "elevator": true,
  "swimming_pool": true,
  "gym": true,
  "security": true,
  "contact_phone": "0901234567",
  "contact_type": "Chính chủ"
}
```

💡 LƯU Ý QUAN TRỌNG:
- Extract CHÍNH XÁC, không bịa thêm thông tin
- Nếu không chắc chắn → null
- Sử dụng format chuẩn (ISO, camelCase for JSON keys)
- Luôn trả về valid JSON
"""

    FEW_SHOT_EXAMPLES = [
        {
            "input": """
BÁN CĂN HỘ VINHOMES CENTRAL PARK QUẬN 7
- Diện tích: 70m²
- 2 phòng ngủ, 2 WC
- Giá: 2.5 tỷ
- Nội thất: Full cao cấp
- Hướng: Đông Nam, view sông
- Tiện ích: Hồ bơi, gym, bảo vệ 24/7
- Sổ hồng chính chủ
Liên hệ: A. Minh - 0901234567 (Chính chủ)
            """,
            "output": {
                "title": "Bán căn hộ Vinhomes Central Park Quận 7",
                "property_type": "căn hộ",
                "transaction_type": "bán",
                "district": "Quận 7",
                "project_name": "Vinhomes Central Park",
                "area": 70,
                "bedrooms": 2,
                "bathrooms": 2,
                "price": 2500000000,
                "price_per_m2": 35714286,
                "legal_status": "Sổ hồng",
                "ownership_type": None,
                "furniture": "full",
                "direction": "Đông Nam",
                "parking": None,
                "elevator": True,
                "swimming_pool": True,
                "gym": True,
                "security": True,
                "contact_name": "A. Minh",
                "contact_phone": "0901234567",
                "contact_type": "Chính chủ"
            }
        },
        {
            "input": """
Nhà phố Quận 2 cho thuê
MT 5m x 20m, 3 tầng
4 phòng ngủ, 4WC
Giá: 25 triệu/tháng
Gần Metro Thảo Điền
Liên hệ: 0987654321
            """,
            "output": {
                "title": "Nhà phố Quận 2 cho thuê",
                "property_type": "nhà phố",
                "transaction_type": "cho thuê",
                "district": "Quận 2",
                "area": 100,
                "bedrooms": 4,
                "bathrooms": 4,
                "floors": 3,
                "facade_width": 5,
                "price": 25000000,
                "furniture": None,
                "contact_phone": "0987654321"
            }
        }
    ]

    VALIDATION_PROMPT = """Kiểm tra và chuẩn hóa dữ liệu đã extract:

📋 VALIDATION RULES:

1. **District Standardization:**
   - "Q1", "Q.1", "Quận 1" → "Quận 1"
   - "Q7", "Q.7", "Quận 7" → "Quận 7"
   - "Bình Thạnh" → "Quận Bình Thạnh"

2. **Price Validation:**
   - Kiểm tra giá hợp lý cho khu vực
   - Quận 1,3: 100-300 triệu/m²
   - Quận 7, Bình Thạnh: 50-150 triệu/m²
   - Quận ngoại thành: 30-80 triệu/m²
   - Nếu price_per_m2 quá cao/thấp → Warning

3. **Area Validation:**
   - Căn hộ: 20-500m² (typical)
   - Nhà phố: 40-300m² (typical)
   - Biệt thự: 100-1000m² (typical)
   - Nếu ngoài range → Warning

4. **Logical Consistency:**
   - bedrooms > 0 và < 20
   - bathrooms <= bedrooms + 2
   - floors > 0 và < 50

5. **Required Fields Check:**
   - Bắt buộc: property_type, district, price (nếu transaction_type = "bán")
   - Khuyến nghị: area, bedrooms, contact_phone

📤 OUTPUT:
```json
{
  "validated_data": { ... },
  "warnings": [
    "price_per_m2 = 200 triệu/m² (cao hơn trung bình khu vực Quận 7)",
    "area = 15m² (nhỏ hơn typical căn hộ)"
  ],
  "errors": [],
  "confidence": 0.92
}
```
"""

    @staticmethod
    def build_extraction_prompt(text: str, include_examples: bool = True) -> str:
        """Build extraction prompt with optional few-shot examples"""
        prompt = AttributeExtractionPrompts.EXTRACTION_SYSTEM_PROMPT

        if include_examples:
            prompt += "\n\n📝 FEW-SHOT EXAMPLES:\n"
            for i, example in enumerate(AttributeExtractionPrompts.FEW_SHOT_EXAMPLES, 1):
                prompt += f"\n--- Example {i} ---\n"
                prompt += f"INPUT:\n{example['input']}\n"
                prompt += f"OUTPUT:\n{example['output']}\n"

        prompt += f"\n\n📥 EXTRACT từ văn bản sau:\n\n{text}\n\n📤 JSON output:"
        return prompt

    @staticmethod
    def build_validation_prompt(extracted_data: Dict) -> str:
        """Build validation prompt"""
        return f"{AttributeExtractionPrompts.VALIDATION_PROMPT}\n\n📥 Validate data:\n{extracted_data}\n\n📤 Validation result:"


# Convenience functions
def get_extraction_prompt(text: str, with_examples: bool = True) -> str:
    """Get attribute extraction prompt"""
    return AttributeExtractionPrompts.build_extraction_prompt(text, with_examples)


def get_validation_prompt(data: Dict) -> str:
    """Get validation prompt"""
    return AttributeExtractionPrompts.build_validation_prompt(data)

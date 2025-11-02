"""
User Personas for AI Test Agent

This module defines different user personas with their characteristics,
behaviors, and query patterns for realistic test scenario generation.
"""

from enum import Enum
from typing import Dict, List
from pydantic import BaseModel


class PersonaType(str, Enum):
    """Available user persona types"""
    FIRST_TIME_BUYER = "first_time_buyer"
    EXPERIENCED_INVESTOR = "experienced_investor"
    YOUNG_PROFESSIONAL = "young_professional"
    FAMILY_BUYER = "family_buyer"
    REAL_ESTATE_AGENT = "real_estate_agent"


class Persona(BaseModel):
    """User persona definition"""
    type: PersonaType
    name: str
    description: str
    characteristics: List[str]
    typical_queries: List[str]
    preferences: Dict[str, any]
    knowledge_level: str  # "beginner", "intermediate", "expert"
    language_style: str  # "simple", "moderate", "professional"
    budget_range: Dict[str, int]  # in VND billions


# Persona Definitions
PERSONAS = {
    PersonaType.FIRST_TIME_BUYER: Persona(
        type=PersonaType.FIRST_TIME_BUYER,
        name="Người mua nhà lần đầu",
        description="Young person buying their first property, limited experience, budget-conscious",
        characteristics=[
            "Inexperienced with real estate",
            "Asks basic questions",
            "Budget-conscious",
            "Needs guidance",
            "Focuses on practical needs",
            "Concerned about price and payment terms"
        ],
        typical_queries=[
            "Tìm căn hộ giá rẻ",
            "Mua nhà cần giấy tờ gì?",
            "Căn hộ 2 phòng ngủ giá bao nhiêu?",
            "Có căn nào dưới 2 tỷ không?",
            "Trả góp như thế nào?",
            "Nên mua chung cư hay nhà phố?",
            "Phí ban đầu mua nhà là bao nhiêu?"
        ],
        preferences={
            "property_types": ["apartment", "condo"],
            "max_price": 3_000_000_000,  # 3 billion VND
            "bedrooms": [1, 2],
            "areas": ["Quận 7", "Quận 2", "Bình Thạnh", "Thủ Đức"],
            "keywords": ["giá rẻ", "phù hợp", "tiện nghi", "an toàn"]
        },
        knowledge_level="beginner",
        language_style="simple",
        budget_range={"min": 1_000_000_000, "max": 3_000_000_000}
    ),

    PersonaType.EXPERIENCED_INVESTOR: Persona(
        type=PersonaType.EXPERIENCED_INVESTOR,
        name="Nhà đầu tư giàu kinh nghiệm",
        description="Seasoned investor looking for high-value properties with good ROI",
        characteristics=[
            "Highly knowledgeable about real estate",
            "Asks complex questions about ROI, market trends, legal",
            "Large budget",
            "Analytical mindset",
            "Focuses on investment potential",
            "Interested in multiple properties"
        ],
        typical_queries=[
            "Phân tích tiềm năng đầu tư khu vực Thủ Thiêm",
            "So sánh ROI giữa Quận 2 và Quận 7",
            "Dự án nào có tiềm năng tăng giá cao nhất?",
            "Xu hướng thị trường bất động sản 2025",
            "Căn hộ cho thuê lợi nhuận cao ở đâu?",
            "Pháp lý của dự án XYZ có vấn đề gì không?",
            "Tỷ suất lợi nhuận trên vốn đầu tư của căn này?"
        ],
        preferences={
            "property_types": ["apartment", "villa", "land", "commercial"],
            "max_price": 50_000_000_000,  # 50 billion VND
            "bedrooms": [3, 4, 5],
            "areas": ["Quận 1", "Quận 2", "Quận 7", "Thủ Thiêm"],
            "keywords": ["đầu tư", "tiềm năng", "ROI", "lợi nhuận", "pháp lý"]
        },
        knowledge_level="expert",
        language_style="professional",
        budget_range={"min": 10_000_000_000, "max": 50_000_000_000}
    ),

    PersonaType.YOUNG_PROFESSIONAL: Persona(
        type=PersonaType.YOUNG_PROFESSIONAL,
        name="Chuyên gia trẻ",
        description="Young professional, budget-moderate, location is priority (near office/transport)",
        characteristics=[
            "Working in city center",
            "Values convenience and location",
            "Moderate budget",
            "Modern lifestyle",
            "Prefers new buildings with amenities",
            "Commute time is critical"
        ],
        typical_queries=[
            "Tìm căn hộ gần metro Quận 2",
            "Chung cư gần công ty ở Thủ Thiêm",
            "Căn hộ có gym và hồ bơi",
            "Studio apartment hiện đại",
            "Có căn nào gần trường quốc tế không?",
            "Khu vực nào có nhiều quán cafe và nhà hàng?",
            "Đi làm về nhanh từ căn hộ này không?"
        ],
        preferences={
            "property_types": ["apartment", "condo", "studio"],
            "max_price": 5_000_000_000,  # 5 billion VND
            "bedrooms": [1, 2],
            "areas": ["Quận 1", "Quận 2", "Quận 3", "Bình Thạnh", "Thủ Đức"],
            "keywords": ["hiện đại", "tiện nghi", "gần metro", "gần công ty", "gym"]
        },
        knowledge_level="intermediate",
        language_style="moderate",
        budget_range={"min": 2_000_000_000, "max": 5_000_000_000}
    ),

    PersonaType.FAMILY_BUYER: Persona(
        type=PersonaType.FAMILY_BUYER,
        name="Gia đình có con nhỏ",
        description="Family with children, needs space, schools, parks, safety",
        characteristics=[
            "Has young children",
            "Needs 3+ bedrooms",
            "Prioritizes schools and parks",
            "Safety is paramount",
            "Values community and neighbors",
            "Long-term residence mindset"
        ],
        typical_queries=[
            "Tìm nhà 3 phòng ngủ gần trường quốc tế",
            "Khu nào an toàn cho trẻ em?",
            "Có công viên và sân chơi không?",
            "Trường học gần nhất cách bao xa?",
            "Khu dân cư yên tĩnh ở đâu?",
            "Căn hộ có view đẹp và ban công rộng",
            "Chung cư có khu vui chơi trẻ em không?"
        ],
        preferences={
            "property_types": ["apartment", "house", "villa"],
            "max_price": 8_000_000_000,  # 8 billion VND
            "bedrooms": [3, 4],
            "areas": ["Quận 7", "Quận 2", "Thủ Đức", "Nhà Bè"],
            "keywords": ["an toàn", "trường học", "công viên", "yên tĩnh", "rộng rãi"]
        },
        knowledge_level="intermediate",
        language_style="moderate",
        budget_range={"min": 4_000_000_000, "max": 8_000_000_000}
    ),

    PersonaType.REAL_ESTATE_AGENT: Persona(
        type=PersonaType.REAL_ESTATE_AGENT,
        name="Môi giới bất động sản",
        description="Professional real estate agent, needs detailed data, comparisons, market insights",
        characteristics=[
            "Professional language",
            "Needs accurate data",
            "Compares multiple properties",
            "Asks about market trends",
            "Focuses on property features",
            "Knows technical terms"
        ],
        typical_queries=[
            "So sánh 3 căn hộ này theo diện tích và giá",
            "Thông tin chi tiết về dự án Vinhomes Grand Park",
            "Mức giá trung bình căn hộ 2PN Quận 7",
            "Các dự án sắp bàn giao Quận 2",
            "Pháp lý dự án ABC đã hoàn thiện chưa?",
            "Tỷ lệ hấp thụ thị trường Thủ Đức",
            "Danh sách căn hộ chủ đầu tư bán"
        ],
        preferences={
            "property_types": ["all"],
            "max_price": 100_000_000_000,  # 100 billion VND (no real limit)
            "bedrooms": [1, 2, 3, 4, 5],
            "areas": ["all"],
            "keywords": ["so sánh", "chi tiết", "thông tin", "dự án", "pháp lý"]
        },
        knowledge_level="expert",
        language_style="professional",
        budget_range={"min": 0, "max": 100_000_000_000}
    )
}


def get_persona(persona_type: PersonaType) -> Persona:
    """Get persona by type"""
    return PERSONAS[persona_type]


def get_all_personas() -> Dict[PersonaType, Persona]:
    """Get all personas"""
    return PERSONAS


def get_persona_names() -> List[str]:
    """Get list of persona names"""
    return [persona.name for persona in PERSONAS.values()]

"""
Attribute Extraction Service - CTO Service #4 (Layer 3)
Extracts structured entities from raw user queries using enhanced 3-layer pipeline:
1. NLP Pre-processing - Rule-based entity extraction
2. RAG Context Retrieval - Get similar properties for context
3. Enhanced LLM Extraction - LLM with NLP + RAG hints
4. Post-Validation - Validate against DB distribution
"""
import httpx
import json
import re
from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel

from core.base_service import BaseService
from services.attribute_extraction.prompts import AttributeExtractionPrompts, PropertyAttributes
from services.attribute_extraction.nlp_processor import VietnameseNLPProcessor
from services.attribute_extraction.rag_enhancer import RAGContextEnhancer
from services.attribute_extraction.validator import AttributeValidator
from services.attribute_extraction.master_data_validator import MasterDataValidator
from shared.config import settings
from shared.utils.logger import LogEmoji
from shared.i18n import get_multilingual_mapper


class QueryExtractionRequest(BaseModel):
    """Request to extract entities from user query"""
    query: str
    intent: Optional[str] = None  # SEARCH, COMPARE, etc.


class ImageExtractionRequest(BaseModel):
    """Request to extract entities from property images"""
    images: List[str]  # Base64 encoded images
    text_context: Optional[str] = None  # Optional text context to enhance extraction


class QueryExtractionResponse(BaseModel):
    """Response with extracted entities"""
    entities: Dict[str, Any]
    confidence: float
    extracted_from: str  # "query"


class EnhancedExtractionResponse(BaseModel):
    """Response with enhanced extraction using NLP + RAG + LLM pipeline"""
    entities: Dict[str, Any]
    confidence: float
    extracted_from: str
    nlp_entities: Dict[str, Any]  # Entities from NLP layer
    rag_retrieved_count: int  # Number of similar properties used for context
    warnings: list[str]  # Validation warnings
    validation_details: Dict[str, Any]  # Detailed validation info
    # NEW: Confidence-based clarification
    needs_clarification: bool = False  # True if confidence too low
    clarification_questions: Optional[List[str]] = None  # Questions to ask user
    suggestions: Optional[List[Dict[str, Any]]] = None  # Suggested values


class AttributeExtractionService(BaseService):
    """
    Attribute Extraction Service - Layer 3
    Extracts structured entities from raw queries and property descriptions
    """

    def __init__(self):
        super().__init__(
            name="attribute_extraction",
            version="2.0.0",  # Enhanced with NLP + RAG
            capabilities=["entity_extraction", "attribute_extraction", "query_parsing", "nlp_preprocessing", "rag_enhanced"],
            port=8080
        )

        self.http_client = httpx.AsyncClient(timeout=60.0)
        self.core_gateway_url = settings.get_core_gateway_url()
        self.db_gateway_url = settings.get_db_gateway_url()

        # Initialize enhanced components
        self.nlp_processor = VietnameseNLPProcessor()
        self.rag_enhancer = RAGContextEnhancer(self.db_gateway_url)
        self.validator = AttributeValidator()
        self.multilingual_mapper = get_multilingual_mapper()
        self.master_data_validator = MasterDataValidator()

        self.logger.info(f"{LogEmoji.INFO} Using Core Gateway at: {self.core_gateway_url}")
        self.logger.info(f"{LogEmoji.INFO} Using DB Gateway at: {self.db_gateway_url}")
        self.logger.info(f"{LogEmoji.SUCCESS} Enhanced NLP + RAG pipeline initialized")
        self.logger.info(f"{LogEmoji.SUCCESS} Multilingual mapper initialized (vi/en/zh → English)")
        self.logger.info(f"{LogEmoji.SUCCESS} Master data validator initialized (PostgreSQL)")

    def setup_routes(self):
        """Setup API routes"""

        @self.app.get("/master-data/districts")
        async def get_districts():
            """Get list of all districts from master data"""
            try:
                districts = await self.master_data_validator.get_districts_list()
                return {"districts": districts, "count": len(districts)}
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Failed to get districts: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/master-data/property-types")
        async def get_property_types():
            """Get list of all property types from master data"""
            try:
                property_types = await self.master_data_validator.get_property_types_list()
                return {"property_types": property_types, "count": len(property_types)}
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Failed to get property types: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/master-data/amenities")
        async def get_amenities(category: Optional[str] = None):
            """Get list of all amenities from master data"""
            try:
                amenities = await self.master_data_validator.get_amenities_list(category=category)
                return {"amenities": amenities, "count": len(amenities)}
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Failed to get amenities: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/extract-query-enhanced", response_model=EnhancedExtractionResponse)
        async def extract_from_query_enhanced(request: QueryExtractionRequest):
            """
            **NEW ENHANCED ENDPOINT** - Extract entities using 3-layer pipeline:
            1. NLP Pre-processing (rule-based)
            2. RAG Context Retrieval (similar properties)
            3. Enhanced LLM Extraction (with NLP + RAG context)
            4. Post-Validation (against DB distribution)

            This is the RECOMMENDED endpoint for production use!
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} Enhanced extraction for: '{request.query}'")

                # LAYER 1: NLP Pre-processing
                self.logger.info(f"{LogEmoji.AI} Layer 1: NLP Pre-processing...")
                nlp_entities = self.nlp_processor.extract_entities(request.query)
                nlp_confidence = self.nlp_processor.get_extraction_confidence(nlp_entities)
                self.logger.info(f"{LogEmoji.SUCCESS} NLP extracted {len(nlp_entities)} entities (confidence: {nlp_confidence:.2f})")

                # LAYER 2: RAG Context Retrieval
                self.logger.info(f"{LogEmoji.AI} Layer 2: RAG Context Retrieval...")
                rag_context = await self.rag_enhancer.get_context(
                    query=request.query,
                    nlp_entities=nlp_entities,
                    limit=5
                )
                rag_count = rag_context.get("retrieved_count", 0)
                self.logger.info(f"{LogEmoji.SUCCESS} RAG retrieved {rag_count} similar properties")

                # LAYER 3: Enhanced LLM Extraction
                self.logger.info(f"{LogEmoji.AI} Layer 3: Enhanced LLM Extraction...")
                llm_entities = await self._enhanced_llm_extraction(
                    query=request.query,
                    nlp_entities=nlp_entities,
                    rag_context=rag_context,
                    intent=request.intent
                )
                self.logger.info(f"{LogEmoji.SUCCESS} LLM extracted {len(llm_entities)} entities")

                # LAYER 4: Post-Validation
                self.logger.info(f"{LogEmoji.AI} Layer 4: Post-Validation...")
                validation_result = self.validator.validate(
                    entities=llm_entities,
                    nlp_entities=nlp_entities,
                    rag_context=rag_context
                )

                validated_entities = validation_result["validated_entities"]
                confidence = validation_result["confidence"]
                warnings = validation_result["warnings"]
                validation_details = validation_result["validation_details"]

                # CRITICAL: Normalize entities to English master data standard using PostgreSQL
                # This converts multilingual input (vi/zh) → English for database storage
                self.logger.info(f"{LogEmoji.AI} Normalizing entities using PostgreSQL master data...")
                master_data_result = await self.master_data_validator.normalize_and_validate(
                    validated_entities
                )
                normalized_entities = master_data_result["normalized_entities"]
                master_data_warnings = master_data_result["warnings"]
                master_data_confidence = master_data_result["confidence"]

                # Combine warnings from both validators
                all_warnings = warnings + master_data_warnings

                # Update confidence (weighted average)
                final_confidence = (confidence * 0.5) + (master_data_confidence * 0.5)

                self.logger.info(
                    f"{LogEmoji.SUCCESS} Entities normalized using master data: {normalized_entities}"
                )
                self.logger.info(
                    f"{LogEmoji.INFO} Master data confidence: {master_data_confidence:.2f}, "
                    f"Final confidence: {final_confidence:.2f}"
                )

                self.logger.info(
                    f"{LogEmoji.SUCCESS} Extraction complete! "
                    f"Final confidence: {final_confidence:.2f}, Total warnings: {len(all_warnings)}"
                )

                # NEW: Confidence-based clarification
                # If confidence too low, generate clarification questions
                needs_clarification = final_confidence < 0.7
                clarification_questions = []
                suggestions = []

                if needs_clarification:
                    self.logger.info(f"{LogEmoji.WARNING} Low confidence! Generating clarification questions...")
                    clarification_result = self._generate_clarification(
                        query=request.query,
                        entities=normalized_entities,
                        confidence=final_confidence,
                        rag_context=rag_context
                    )
                    clarification_questions = clarification_result["questions"]
                    suggestions = clarification_result["suggestions"]

                return EnhancedExtractionResponse(
                    entities=normalized_entities,  # Return master-data-normalized entities
                    confidence=final_confidence,
                    extracted_from="enhanced_pipeline_with_master_data",
                    nlp_entities=nlp_entities,
                    rag_retrieved_count=rag_count,
                    warnings=all_warnings,
                    validation_details=validation_details,
                    needs_clarification=needs_clarification,
                    clarification_questions=clarification_questions if needs_clarification else None,
                    suggestions=suggestions if needs_clarification else None
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Enhanced extraction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/extract-query", response_model=QueryExtractionResponse)
        async def extract_from_query(request: QueryExtractionRequest):
            """
            Extract entities from user search query
            This is what Orchestrator should call for SEARCH intent!
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} Extracting entities from query: '{request.query}'")

                # Build specialized prompt for query extraction (not full property description)
                prompt = self._build_query_extraction_prompt(request.query, request.intent)

                # Call LLM via Core Gateway
                entities = await self._call_llm_for_extraction(prompt)

                # Normalize to English master data
                self.logger.info(f"{LogEmoji.AI} Normalizing query entities to English...")
                normalized_entities = self.multilingual_mapper.normalize_entities(
                    entities,
                    source_lang="vi"
                )

                confidence = self._calculate_confidence(normalized_entities)

                self.logger.info(f"{LogEmoji.SUCCESS} Extracted entities (normalized): {normalized_entities}")

                return QueryExtractionResponse(
                    entities=normalized_entities,
                    confidence=confidence,
                    extracted_from="query"
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Entity extraction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/extract-property", response_model=QueryExtractionResponse)
        async def extract_from_property_description(request: QueryExtractionRequest):
            """
            Extract full property attributes from property description/listing
            Used for data enrichment, not for user queries
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} Extracting from property description (length: {len(request.query)})")

                # Use full extraction prompt for property descriptions
                prompt = AttributeExtractionPrompts.build_extraction_prompt(request.query, include_examples=True)

                entities = await self._call_llm_for_extraction(prompt)
                confidence = self._calculate_confidence(entities)

                return QueryExtractionResponse(
                    entities=entities,
                    confidence=confidence,
                    extracted_from="property_description"
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Property extraction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/extract-from-images", response_model=QueryExtractionResponse)
        async def extract_from_images(request: ImageExtractionRequest):
            """
            NEW ENDPOINT: Extract property attributes from images using GPT-4o Vision

            This enables users to upload property photos and automatically extract:
            - Property type (apartment, house, villa)
            - Room count (bedrooms, bathrooms)
            - Amenities (pool, gym, parking, garden)
            - Style (modern, classic, luxury)
            - Condition (new, renovated, needs work)

            Example use cases:
            - User uploads property photos → auto-populate listing
            - User uploads photos while searching → find similar properties
            - Agent uploads photos → AI suggests price range
            """
            try:
                self.logger.info(
                    f"{LogEmoji.TARGET} Extracting from {len(request.images)} images "
                    f"(with context: {bool(request.text_context)})"
                )

                # Build vision prompt for property analysis
                vision_prompt = self._build_vision_extraction_prompt(request.text_context)

                # Call GPT-4o Vision via Core Gateway
                entities = await self._call_vision_for_extraction(
                    images=request.images,
                    prompt=vision_prompt
                )

                # Merge with text context if provided
                if request.text_context:
                    self.logger.info(f"{LogEmoji.AI} Merging vision extraction with text context...")
                    text_entities = await self._call_llm_for_extraction(
                        self._build_query_extraction_prompt(request.text_context)
                    )
                    # Merge entities (vision takes precedence for visual attributes)
                    entities = {**text_entities, **entities}

                confidence = self._calculate_confidence(entities)
                self.logger.info(f"{LogEmoji.SUCCESS} Extracted {len(entities)} entities from images")

                return QueryExtractionResponse(
                    entities=entities,
                    confidence=confidence,
                    extracted_from="images_vision"
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Image extraction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def _build_query_extraction_prompt(self, query: str, intent: Optional[str] = None) -> str:
        """
        Build specialized prompt for extracting entities from USER QUERIES
        Simpler than full property extraction - focuses on search criteria
        """
        return f"""Bạn là chuyên gia trích xuất thông tin tìm kiếm bất động sản từ câu hỏi của người dùng.

🎯 NHIỆM VỤ:
Đọc câu hỏi của user và trích xuất CÁC TIÊU CHÍ TÌM KIẾM thành JSON.

📊 ENTITIES CẦN TRÍCH XUẤT (chỉ trích xuất những gì có trong câu hỏi):

**1. PROPERTY TYPE**
- property_type: căn hộ | nhà phố | biệt thự | đất | chung cư | commercial

**2. LOCATION**
- district: Quận/Huyện (chuẩn hóa)
  * "Q7", "Q.7", "quận 7" → "Quận 7"
  * "Q2" → "Quận 2"
  * "Bình Thạnh" → "Quận Bình Thạnh"
  * "Thủ Đức" → "Quận Thủ Đức"
- ward: Phường (nếu có)
- project_name: Tên dự án (Vinhomes, Masteri, etc.)

**3. PHYSICAL ATTRIBUTES**
- bedrooms: Số phòng ngủ
  * "2PN" → 2
  * "3 phòng ngủ" → 3
  * "2 phòng" → 2
- bathrooms: Số phòng tắm/WC
- area: Diện tích (m²)
- min_area: Diện tích tối thiểu
- max_area: Diện tích tối đa

**4. PRICE**
- price: Giá cụ thể (VND)
- min_price: Giá tối thiểu (VND)
- max_price: Giá tối đa (VND)

CHUẨN HÓA GIÁ:
  * "dưới 3 tỷ" → max_price: 3000000000
  * "từ 2 đến 5 tỷ" → min_price: 2000000000, max_price: 5000000000
  * "khoảng 3 tỷ" → price: 3000000000
  * "25 triệu/tháng" → price: 25000000

**5. FEATURES**
- furniture: full | cơ bản | không
- direction: Đông | Tây | Nam | Bắc | etc.

**6. AMENITIES**
- parking: true nếu có yêu cầu chỗ đậu xe
- elevator: true nếu có yêu cầu thang máy
- swimming_pool: true nếu có yêu cầu hồ bơi
- gym: true nếu có yêu cầu gym

🔍 EXTRACTION RULES:

1. **Chỉ trích xuất thông tin CÓ TRONG CÂU HỎI** - đừng bịa thêm
2. **Chuẩn hóa địa danh** về format chuẩn
3. **Chuẩn hóa giá** về số VND
4. **Nếu không có thông tin** → không đưa vào JSON (not null, just omit)
5. **Ưu tiên từ khóa rõ ràng** hơn từ khóa mơ hồ

📝 FEW-SHOT EXAMPLES:

Example 1:
Input: "Tìm căn hộ 2 phòng ngủ quận 7 dưới 3 tỷ"
Output: {{"property_type": "căn hộ", "bedrooms": 2, "district": "Quận 7", "max_price": 3000000000}}

Example 2:
Input: "Cần mua nhà phố Bình Thạnh khoảng 100m2"
Output: {{"property_type": "nhà phố", "district": "Quận Bình Thạnh", "area": 100}}

Example 3:
Input: "Tìm chung cư Vinhomes có hồ bơi"
Output: {{"property_type": "chung cư", "project_name": "Vinhomes", "swimming_pool": true}}

Example 4:
Input: "Biệt thự Q2 từ 10 đến 20 tỷ, có garage"
Output: {{"property_type": "biệt thự", "district": "Quận 2", "min_price": 10000000000, "max_price": 20000000000, "parking": true}}

📥 USER QUERY:
{query}

Intent: {intent or "SEARCH"}

📤 OUTPUT (chỉ JSON, không giải thích):
"""

    async def _call_llm_for_extraction(self, prompt: str) -> Dict[str, Any]:
        """Call LLM via Core Gateway to extract entities"""
        try:
            llm_request = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a structured data extraction expert. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.2  # Low temperature for consistent extraction
            }

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json=llm_request,
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "").strip()

                # Clean up markdown code blocks
                content = re.sub(r'^```(?:json)?\s*\n?', '', content)
                content = re.sub(r'\n?```\s*$', '', content)
                content = content.strip()

                # Parse JSON
                entities = json.loads(content)
                return entities
            else:
                self.logger.warning(f"{LogEmoji.WARNING} Core Gateway returned {response.status_code}")
                return {}

        except json.JSONDecodeError as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to parse JSON: {e}")
            self.logger.error(f"Raw content: {content}")
            return {}
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} LLM call failed: {e}")
            return {}

    def _calculate_confidence(self, entities: Dict[str, Any]) -> float:
        """Calculate confidence score based on extracted entities"""
        if not entities:
            return 0.0

        # Simple confidence based on number of entities extracted
        num_entities = len(entities)
        if num_entities >= 4:
            return 0.95
        elif num_entities >= 3:
            return 0.85
        elif num_entities >= 2:
            return 0.75
        else:
            return 0.65

    async def _enhanced_llm_extraction(
        self,
        query: str,
        nlp_entities: Dict[str, Any],
        rag_context: Dict[str, Any],
        intent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhanced LLM extraction with NLP hints and RAG context.

        This builds a rich prompt that includes:
        1. NLP pre-extracted entities (as hints)
        2. Real property examples from RAG
        3. Value ranges and patterns from DB
        """
        # Build enhanced prompt
        prompt = self._build_enhanced_prompt(query, nlp_entities, rag_context, intent)

        # Call LLM
        entities = await self._call_llm_for_extraction(prompt)

        return entities

    def _build_enhanced_prompt(
        self,
        query: str,
        nlp_entities: Dict[str, Any],
        rag_context: Dict[str, Any],
        intent: Optional[str] = None
    ) -> str:
        """
        Build enhanced prompt with NLP hints and RAG context.
        """
        # Get RAG components
        examples = rag_context.get("examples", [])
        patterns = rag_context.get("patterns", {})
        value_ranges = rag_context.get("value_ranges", {})

        # Format examples
        examples_text = ""
        if examples:
            examples_text = "📚 REAL PROPERTY EXAMPLES FROM DATABASE (similar to this query):\n"
            for i, ex in enumerate(examples[:3], 1):
                examples_text += f"\nExample {i}:\n{json.dumps(ex, indent=2, ensure_ascii=False)}\n"

        # Format patterns
        patterns_text = ""
        if patterns:
            patterns_text = "📊 COMMON PATTERNS IN SIMILAR PROPERTIES:\n"
            if "common_districts" in patterns:
                districts = [d["value"] for d in patterns["common_districts"][:3]]
                patterns_text += f"- Common districts: {', '.join(districts)}\n"
            if "common_property_types" in patterns:
                types = [t["value"] for t in patterns["common_property_types"][:3]]
                patterns_text += f"- Common property types: {', '.join(types)}\n"

        # Format value ranges
        ranges_text = ""
        if value_ranges:
            ranges_text = "📈 VALUE RANGES FROM SIMILAR PROPERTIES:\n"
            if "price" in value_ranges:
                pr = value_ranges["price"]
                ranges_text += f"- Price range: {pr['min']:,.0f} - {pr['max']:,.0f} VND (avg: {pr['avg']:,.0f})\n"
            if "area" in value_ranges:
                ar = value_ranges["area"]
                ranges_text += f"- Area range: {ar['min']:.0f} - {ar['max']:.0f} m² (avg: {ar['avg']:.0f})\n"

        # Format NLP hints
        nlp_hints_text = ""
        if nlp_entities:
            nlp_hints_text = f"💡 NLP PRE-EXTRACTED HINTS:\n{json.dumps(nlp_entities, indent=2, ensure_ascii=False)}\n"

        prompt = f"""Bạn là chuyên gia trích xuất thông tin bất động sản.

🎯 NHIỆM VỤ: Trích xuất entities từ query, SỬ DỤNG HINTS từ NLP và EXAMPLES từ database.

{nlp_hints_text}

{examples_text}

{patterns_text}

{ranges_text}

🔍 EXTRACTION RULES:
1. **USE NLP hints as starting point** - Ưu tiên thông tin từ NLP layer
2. **FOLLOW patterns from real examples** - Tham khảo format từ DB
3. **STAY within typical value ranges** - Kiểm tra với ranges từ DB
4. **DON'T hallucinate** - Chỉ trích xuất thông tin có trong query
5. **Chuẩn hóa format** - Sử dụng format giống examples

📊 ENTITIES CẦN TRÍCH XUẤT (chỉ trích xuất những gì có trong câu hỏi):

**1. PROPERTY TYPE**
- property_type: căn hộ | nhà phố | biệt thự | đất | chung cư | văn phòng

**2. LOCATION**
- district: Quận/Huyện (chuẩn hóa như examples)
- ward: Phường (nếu có)
- project_name: Tên dự án

**3. PHYSICAL ATTRIBUTES**
- bedrooms: Số phòng ngủ
- bathrooms: Số phòng tắm
- area: Diện tích (m²)
- floors: Số tầng

**4. PRICE**
- price: Giá cụ thể (VND)
- min_price: Giá tối thiểu (VND)
- max_price: Giá tối đa (VND)

**5. FEATURES & AMENITIES**
- furniture: full | cơ bản | không
- direction: Hướng nhà
- parking: true/false
- elevator: true/false
- swimming_pool: true/false
- gym: true/false

📥 USER QUERY:
{query}

Intent: {intent or "SEARCH"}

📤 OUTPUT (chỉ JSON, không giải thích):
"""
        return prompt

    def _build_vision_extraction_prompt(self, text_context: Optional[str] = None) -> str:
        """
        Build prompt for GPT-4o Vision to extract property attributes from images.

        Args:
            text_context: Optional text context to enhance extraction

        Returns:
            Vision prompt
        """
        prompt = """Bạn là chuyên gia phân tích hình ảnh bất động sản.

🎯 NHIỆM VỤ: Phân tích ảnh property và trích xuất thông tin thành JSON.

📊 ENTITIES CẦN TRÍCH XUẤT (chỉ trích xuất những gì THẤY ĐƯỢC trong ảnh):

**1. PROPERTY TYPE (quan trọng nhất)**
- property_type: căn hộ | nhà phố | biệt thự | đất | studio | penthouse
  * Nhìn vào: Cấu trúc, quy mô, kiến trúc
  * Căn hộ: Trong chung cư, có ban công nhỏ
  * Nhà phố: Nhiều tầng, mặt tiền hẹp
  * Biệt thự: Rộng rãi, có sân vườn

**2. ROOMS & SPACES**
- bedrooms: Số phòng ngủ (đếm từ ảnh - giường, tủ quần áo)
- bathrooms: Số phòng tắm (nhìn thấy toilet, bồn tắm)
- living_rooms: Số phòng khách
- kitchens: Có bếp không
- balconies: Có ban công không

**3. AMENITIES (Tiện ích nhìn thấy)**
- swimming_pool: true nếu thấy hồ bơi
- gym: true nếu thấy phòng gym
- parking: true nếu thấy chỗ đậu xe/garage
- garden: true nếu thấy sân vườn
- elevator: true nếu thấy thang máy
- security: Có hệ thống bảo vệ không (camera, cổng bảo vệ)

**4. STYLE & CONDITION**
- style: modern | classic | luxury | minimalist | industrial
  * Modern: Đường nét sạch sẽ, tối giản, màu trắng/ghi
  * Classic: Gỗ, họa tiết cổ điển
  * Luxury: Sang trọng, đèn chùm, đá marble
- condition: new | excellent | good | needs_renovation
  * New: Mới tinh, sạch sẽ
  * Excellent: Tốt, được maintain tốt
  * Good: Ổn, có dấu hiệu sử dụng nhẹ
  * Needs renovation: Cũ, cần sửa chữa
- furnished: full | basic | unfurnished
  * Full: Đầy đủ nội thất (giường, bàn, ghế, TV, tủ lạnh)
  * Basic: Có một số nội thất cơ bản
  * Unfurnished: Trống, không nội thất

**5. VISUAL FEATURES**
- view: sea | city | garden | mountain | river (nếu thấy qua cửa sổ)
- direction: Hướng ban công/cửa sổ chính
- natural_light: high | medium | low (lượng ánh sáng tự nhiên)
- floor_material: wood | tile | marble | carpet (vật liệu sàn nhà)

**6. ESTIMATE (Ước lượng từ ảnh)**
- estimated_area_m2: Ước lượng diện tích (nếu có thể)
- estimated_floors: Số tầng (nếu thấy)

🔍 EXTRACTION RULES:

1. **CHỈ trích xuất thông tin THẤY RÕ TRONG ẢNH** - đừng đoán
2. **Ưu tiên độ chính xác** hơn là extract nhiều
3. **Nếu không chắc → không đưa vào JSON** (omit field, don't guess)
4. **Đếm phòng cẩn thận** - đừng nhầm lẫn
5. **Phân tích tất cả các ảnh** nếu có nhiều ảnh

📝 EXAMPLES:

Example 1 (Luxury apartment):
Input: Ảnh căn hộ cao cấp, phòng khách rộng, sofa trắng, view thành phố
Output: {
  "property_type": "căn hộ",
  "living_rooms": 1,
  "style": "luxury",
  "furnished": "full",
  "view": "city",
  "natural_light": "high",
  "floor_material": "marble",
  "condition": "excellent"
}

Example 2 (Villa with pool):
Input: Ảnh biệt thự 2 tầng, hồ bơi ngoài trời, sân vườn rộng
Output: {
  "property_type": "biệt thự",
  "swimming_pool": true,
  "garden": true,
  "estimated_floors": 2,
  "style": "modern",
  "natural_light": "high",
  "condition": "new"
}

Example 3 (Simple bedroom):
Input: Ảnh phòng ngủ đơn giản, giường đơn, tủ quần áo
Output: {
  "bedrooms": 1,
  "furnished": "basic",
  "style": "minimalist",
  "condition": "good",
  "floor_material": "wood"
}
"""

        if text_context:
            prompt += f"\n\n📝 TEXT CONTEXT (from user):\n{text_context}\n\nUse this context to enhance extraction, but PRIORITIZE what you SEE in images.\n"

        prompt += "\n📤 OUTPUT (chỉ JSON, không giải thích):"

        return prompt

    async def _call_vision_for_extraction(
        self,
        images: List[str],
        prompt: str
    ) -> Dict[str, Any]:
        """
        Call GPT-4o Vision via Core Gateway to extract entities from images.

        Args:
            images: List of base64-encoded images
            prompt: Extraction prompt

        Returns:
            Extracted entities dict
        """
        try:
            from shared.models.core_gateway import FileAttachment

            # Build vision request
            files = [
                FileAttachment(
                    filename=f"property_{i}.jpg",
                    mime_type="image/jpeg",
                    base64_data=img
                )
                for i, img in enumerate(images)
            ]

            # Use Core Gateway's vision endpoint
            llm_request = {
                "model": "gpt-4o",  # GPT-4o for vision
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a property image analysis expert. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                        "files": [f.dict() for f in files]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.2
            }

            response = await self.http_client.post(
                f"{self.core_gateway_url}/chat/completions",
                json=llm_request,
                timeout=60.0
            )

            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "").strip()

                # Clean up markdown code blocks
                import re
                content = re.sub(r'^```(?:json)?\s*\n?', '', content)
                content = re.sub(r'\n?```\s*$', '', content)
                content = content.strip()

                # Parse JSON
                import json
                entities = json.loads(content)
                return entities
            else:
                self.logger.warning(f"{LogEmoji.WARNING} Vision API returned {response.status_code}")
                return {}

        except json.JSONDecodeError as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to parse vision response: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Vision call failed: {e}")
            return {}

    def _generate_clarification(
        self,
        query: str,
        entities: Dict[str, Any],
        confidence: float,
        rag_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate clarification questions and suggestions when confidence is low.

        Args:
            query: User query
            entities: Extracted entities
            confidence: Confidence score
            rag_context: RAG context with similar properties

        Returns:
            Dict with clarification questions and suggestions
        """
        questions = []
        suggestions = []

        # Check what's missing or unclear
        has_property_type = "property_type" in entities
        has_location = "district" in entities or "ward" in entities
        has_price = "price" in entities or "min_price" in entities or "max_price" in entities
        has_bedrooms = "bedrooms" in entities

        # Generate questions based on missing info
        if not has_property_type:
            questions.append("Bạn muốn tìm loại bất động sản nào? (căn hộ, nhà phố, biệt thự)")
            # Get suggestions from RAG
            if rag_context.get("patterns", {}).get("common_property_types"):
                property_type_suggestions = [
                    {
                        "value": pt["value"],
                        "count": pt["count"],
                        "label": f"{pt['value']} ({pt['count']} căn)"
                    }
                    for pt in rag_context["patterns"]["common_property_types"][:3]
                ]
                suggestions.append({
                    "field": "property_type",
                    "question": "Loại bất động sản",
                    "options": property_type_suggestions
                })

        if not has_location:
            questions.append("Bạn muốn tìm ở khu vực nào? (Quận/Huyện)")
            # Get suggestions from RAG
            if rag_context.get("patterns", {}).get("common_districts"):
                district_suggestions = [
                    {
                        "value": d["value"],
                        "count": d["count"],
                        "label": f"{d['value']} ({d['count']} căn)"
                    }
                    for d in rag_context["patterns"]["common_districts"][:5]
                ]
                suggestions.append({
                    "field": "district",
                    "question": "Khu vực",
                    "options": district_suggestions
                })

        if not has_price:
            questions.append("Ngân sách của bạn là bao nhiêu?")
            # Get price range from RAG
            if rag_context.get("value_ranges", {}).get("price"):
                price_range = rag_context["value_ranges"]["price"]
                price_suggestions = [
                    {
                        "value": "low",
                        "min": price_range["min"],
                        "max": price_range["avg"] * 0.7,
                        "label": f"Dưới {price_range['avg'] * 0.7 / 1_000_000_000:.1f} tỷ"
                    },
                    {
                        "value": "medium",
                        "min": price_range["avg"] * 0.7,
                        "max": price_range["avg"] * 1.3,
                        "label": f"{price_range['avg'] * 0.7 / 1_000_000_000:.1f} - {price_range['avg'] * 1.3 / 1_000_000_000:.1f} tỷ"
                    },
                    {
                        "value": "high",
                        "min": price_range["avg"] * 1.3,
                        "max": price_range["max"],
                        "label": f"Trên {price_range['avg'] * 1.3 / 1_000_000_000:.1f} tỷ"
                    }
                ]
                suggestions.append({
                    "field": "price",
                    "question": "Ngân sách",
                    "options": price_suggestions
                })

        if not has_bedrooms:
            questions.append("Bạn cần bao nhiêu phòng ngủ?")
            suggestions.append({
                "field": "bedrooms",
                "question": "Số phòng ngủ",
                "options": [
                    {"value": 1, "label": "1 phòng ngủ (Studio)"},
                    {"value": 2, "label": "2 phòng ngủ"},
                    {"value": 3, "label": "3 phòng ngủ"},
                    {"value": 4, "label": "4+ phòng ngủ"}
                ]
            })

        # If entities were extracted but confidence still low, ask for confirmation
        if entities and confidence < 0.6:
            questions.append(
                f"Tôi hiểu bạn đang tìm: {self._format_entities_for_display(entities)}. Đúng không?"
            )

        return {
            "questions": questions,
            "suggestions": suggestions,
            "reason": f"Confidence thấp ({confidence:.2f}), cần làm rõ thêm thông tin"
        }

    def _format_entities_for_display(self, entities: Dict[str, Any]) -> str:
        """Format entities for user-friendly display."""
        parts = []
        if "property_type" in entities:
            parts.append(entities["property_type"])
        if "bedrooms" in entities:
            parts.append(f"{entities['bedrooms']} phòng ngủ")
        if "district" in entities:
            parts.append(f"tại {entities['district']}")
        if "max_price" in entities:
            parts.append(f"dưới {entities['max_price'] / 1_000_000_000:.1f} tỷ")
        elif "price" in entities:
            parts.append(f"khoảng {entities['price'] / 1_000_000_000:.1f} tỷ")

        return " ".join(parts) if parts else "bất động sản"

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()
        await self.rag_enhancer.close()
        await self.master_data_validator.close()
        await super().on_shutdown()


# Create service instance at module level for uvicorn
service = AttributeExtractionService()
app = service.app

if __name__ == "__main__":
    service.run()

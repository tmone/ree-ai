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
from typing import Dict, Any, Optional, List
from fastapi import HTTPException
from pydantic import BaseModel

from core.base_service import BaseService
from services.attribute_extraction.prompts import AttributeExtractionPrompts, PropertyAttributes
from services.attribute_extraction.nlp_processor import VietnameseNLPProcessor
from services.attribute_extraction.rag_enhancer import RAGContextEnhancer
from services.attribute_extraction.validator import AttributeValidator
from services.attribute_extraction.master_data_validator import MasterDataValidator
from services.attribute_extraction.master_data_extractor import MasterDataExtractor
from services.attribute_extraction.admin_routes import AdminRoutes
from services.attribute_extraction.regex_extractor_simple import SimpleRegexExtractor  # ITERATION 4: Regex baseline
from shared.config import settings
from shared.utils.logger import LogEmoji
from shared.utils.query_normalizer import normalize_query  # ITERATION 4: Query normalization
from shared.utils.i18n import t
from shared.i18n import get_multilingual_mapper
from shared.models.attribute_extraction import ExtractionRequest, ExtractionResponse


class QueryExtractionRequest(BaseModel):
    """Request to extract entities from user query"""
    query: str
    intent: Optional[str] = None  # SEARCH, COMPARE, etc.
    language: str = "vi"  # User's preferred language (vi, en, th, ja)


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

        # NEW: Initialize master data extractor (v2.0)
        self.master_data_extractor = MasterDataExtractor(
            core_gateway_url=self.core_gateway_url,
            llm_extractor=self._call_llm_for_extraction
        )

        # ITERATION 4: Initialize regex extractor (baseline fallback)
        self.regex_extractor = SimpleRegexExtractor()

        # NEW: Initialize admin routes
        self.admin_routes = AdminRoutes()

        self.logger.info(f"{LogEmoji.INFO} Using Core Gateway at: {self.core_gateway_url}")
        self.logger.info(f"{LogEmoji.INFO} Using DB Gateway at: {self.db_gateway_url}")
        self.logger.info(f"{LogEmoji.SUCCESS} Enhanced NLP + RAG pipeline initialized")
        self.logger.info(f"{LogEmoji.SUCCESS} Multilingual mapper initialized (vi/en/zh → English)")
        self.logger.info(f"{LogEmoji.SUCCESS} Master data validator initialized (PostgreSQL)")
        self.logger.info(f"{LogEmoji.SUCCESS} Master data extractor v2.0 initialized (full pipeline)")
        self.logger.info(f"{LogEmoji.SUCCESS} Regex extractor initialized (baseline fallback)")
        self.logger.info(f"{LogEmoji.SUCCESS} Admin routes initialized (pending item review)")

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
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language='vi', error=str(e)))

        @self.app.get("/master-data/property-types")
        async def get_property_types():
            """Get list of all property types from master data"""
            try:
                property_types = await self.master_data_validator.get_property_types_list()
                return {"property_types": property_types, "count": len(property_types)}
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Failed to get property types: {e}")
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language='vi', error=str(e)))

        @self.app.get("/master-data/amenities")
        async def get_amenities(category: Optional[str] = None):
            """Get list of all amenities from master data"""
            try:
                amenities = await self.master_data_validator.get_amenities_list(category=category)
                return {"amenities": amenities, "count": len(amenities)}
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Failed to get amenities: {e}")
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language='vi', error=str(e)))

        @self.app.post("/extract-with-master-data", response_model=ExtractionResponse)
        async def extract_with_master_data(request: ExtractionRequest):
            """
            ✨ **NEW V2.0 ENDPOINT** ✨

            Complete extraction pipeline with master data integration:
            1. Auto-detect language from input text
            2. Extract attributes using LLM
            3. Fuzzy match against PostgreSQL master data with translations
            4. Translate unmatched items to English using LLM
            5. Return 3-tier response: raw/mapped/new

            This is the RECOMMENDED endpoint for production use!

            **Response Structure**:
            - `raw`: Numeric and free-form attributes (bedrooms, area, price)
            - `mapped`: Successfully matched attributes with master data IDs + translations
            - `new`: Unmatched attributes requiring admin review

            **Example**:
            Input: "Căn hộ 2PN Quận 1 có hồ bơi"
            Output:
            {
              "raw": {"bedrooms": 2},
              "mapped": [
                {
                  "property_name": "property_type",
                  "id": 1,
                  "value": "apartment",
                  "value_translated": "Căn hộ",
                  "confidence": 0.98
                }
              ],
              "new": []
            }
            """
            try:
                # Initialize extractor if needed
                if not hasattr(self, '_extractor_initialized'):
                    self.logger.info(f"{LogEmoji.INFO} Initializing master data extractor...")
                    await self.master_data_extractor.initialize()
                    self._extractor_initialized = True

                self.logger.info(
                    f"{LogEmoji.TARGET} Extraction request: "
                    f"text='{request.text[:50]}...', lang={request.language}"
                )

                # Execute extraction
                response = await self.master_data_extractor.extract(request)

                self.logger.info(
                    f"{LogEmoji.SUCCESS} Extraction complete: "
                    f"{len(response.mapped)} mapped, {len(response.new)} new "
                    f"({response.processing_time_ms:.0f}ms)"
                )

                return response

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Extraction with master data failed: {e}")
                import traceback
                traceback.print_exc()
                lang = request.language if hasattr(request, 'language') and request.language else 'vi'
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language=lang, error=str(e)))

        @self.app.get("/admin/pending-items")
        async def get_pending_items(
            status: str = "pending",
            limit: int = 50,
            offset: int = 0
        ):
            """
            Get list of pending master data items for admin review

            **Query Parameters**:
            - status: Filter by status ('pending', 'approved', 'rejected')
            - limit: Max items to return (default: 50)
            - offset: Pagination offset (default: 0)

            **Returns**:
            - items: List of pending items
            - total_count: Total number of items
            - high_frequency_items: Items that appear frequently (priority review)
            """
            try:
                return await self.admin_routes.get_pending_items(status, limit, offset)
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Failed to get pending items: {e}")
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language='vi', error=str(e)))

        @self.app.post("/admin/approve-item")
        async def approve_pending_item(
            pending_id: int,
            translations: dict,
            admin_user_id: str,
            admin_notes: Optional[str] = None
        ):
            """
            Approve a pending item and add to master data

            **Body Parameters**:
            - pending_id: ID of pending item
            - translations: Dict of {lang_code: translated_text}
              Example: {"vi": "Hầm rượu", "en": "Wine cellar", "zh": "酒窖"}
            - admin_user_id: ID of admin approving
            - admin_notes: Optional notes

            **Returns**:
            - success: True if successful
            - master_data_id: ID of newly created master data
            - table: Which master data table it was added to
            """
            try:
                return await self.admin_routes.approve_pending_item(
                    pending_id, translations, admin_user_id, admin_notes
                )
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Failed to approve item: {e}")
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language='vi', error=str(e)))

        @self.app.post("/admin/reject-item")
        async def reject_pending_item(
            pending_id: int,
            admin_user_id: str,
            admin_notes: Optional[str] = None
        ):
            """
            Reject a pending item

            **Body Parameters**:
            - pending_id: ID of pending item
            - admin_user_id: ID of admin rejecting
            - admin_notes: Reason for rejection

            **Returns**:
            - success: True if successful
            """
            try:
                return await self.admin_routes.reject_pending_item(
                    pending_id, admin_user_id, admin_notes
                )
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Failed to reject item: {e}")
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language='vi', error=str(e)))

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
                        rag_context=rag_context,
                        language=request.language
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
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language=request.language, error=str(e)))

        @self.app.post("/extract-query", response_model=QueryExtractionResponse)
        async def extract_from_query(request: QueryExtractionRequest):
            """
            Extract entities from user search query
            This is what Orchestrator should call for SEARCH intent!
            """
            try:
                self.logger.info(f"{LogEmoji.TARGET} Extracting entities from query: '{request.query}'")

                # ITERATION 4: Normalize query (expand abbreviations: Q1->Quận 1, 2BR->2 phòng ngủ, 5B->5 tỷ)
                normalized_query = normalize_query(request.query)
                if normalized_query != request.query:
                    self.logger.info(f"{LogEmoji.INFO} Normalized query: '{normalized_query}'")

                # ITERATION 4: LAYER 1 - Regex extraction (guaranteed baseline)
                self.logger.info(f"{LogEmoji.AI} Layer 1: Regex extraction...")
                regex_entities = self.regex_extractor.extract(normalized_query)
                regex_confidence = self.regex_extractor.get_confidence(regex_entities)
                self.logger.info(f"{LogEmoji.SUCCESS} Regex extracted {len(regex_entities)} entities (confidence: {regex_confidence:.2f}): {regex_entities}")

                # ITERATION 4: LAYER 2 - LLM extraction (comprehensive)
                self.logger.info(f"{LogEmoji.AI} Layer 2: LLM extraction...")
                prompt = self._build_query_extraction_prompt(normalized_query, request.intent)
                llm_entities = await self._call_llm_for_extraction(prompt)
                self.logger.info(f"{LogEmoji.SUCCESS} LLM extracted {len(llm_entities)} entities: {llm_entities}")

                # ITERATION 4: LAYER 3 - Merge results (LLM priority, regex fills gaps)
                self.logger.info(f"{LogEmoji.AI} Layer 3: Merging regex + LLM results...")
                merged_entities = self._merge_entities(regex_entities, llm_entities)
                self.logger.info(f"{LogEmoji.SUCCESS} Merged: {len(merged_entities)} entities total: {merged_entities}")

                # Normalize to English master data
                self.logger.info(f"{LogEmoji.AI} Normalizing merged entities to English...")
                normalized_entities = self.multilingual_mapper.normalize_entities(
                    merged_entities,
                    source_lang="vi"
                )

                # ITERATION 4: Field rename - transaction_type -> listing_type (for consistency)
                if "transaction_type" in normalized_entities:
                    normalized_entities["listing_type"] = normalized_entities.pop("transaction_type")
                    self.logger.info(f"{LogEmoji.INFO} Renamed field: transaction_type → listing_type")

                # ITERATION 4: Normalize listing_type value (cho thuê -> rent, bán -> sale)
                if "listing_type" in normalized_entities:
                    original_value = normalized_entities["listing_type"]
                    value_lower = original_value.lower().strip() if original_value else ""

                    # Simple mapping for common Vietnamese keywords
                    listing_type_map = {
                        "cho thuê": "rent", "cho thue": "rent", "thuê": "rent", "thue": "rent",
                        "bán": "sale", "ban": "sale", "cần bán": "sale", "can ban": "sale"
                    }

                    normalized_value = listing_type_map.get(value_lower, original_value)
                    if normalized_value != original_value:
                        normalized_entities["listing_type"] = normalized_value
                        self.logger.info(f"{LogEmoji.INFO} Normalized listing_type: '{original_value}' → '{normalized_value}'")

                confidence = self._calculate_confidence(normalized_entities)

                # Determine extraction source for response (match Iteration 4 behavior)
                if regex_entities and llm_entities:
                    extraction_source = "query_hybrid"  # Both layers contributed
                elif regex_entities:
                    extraction_source = "query_regex_fallback"  # LLM failed, regex only
                else:
                    extraction_source = "query"  # LLM only (legacy)

                self.logger.info(f"{LogEmoji.SUCCESS} Extracted entities (normalized): {normalized_entities}")
                self.logger.info(f"{LogEmoji.INFO} Extraction method: {extraction_source}")

                return QueryExtractionResponse(
                    entities=normalized_entities,
                    confidence=confidence,
                    extracted_from=extraction_source
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Entity extraction failed: {e}")
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language=request.language, error=str(e)))

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
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language=request.language, error=str(e)))

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
                raise HTTPException(status_code=500, detail=t("attribute_extraction.error_generic", language='vi', error=str(e)))

    def _build_query_extraction_prompt(self, query: str, intent: Optional[str] = None) -> str:
        """
        Build specialized prompt for extracting entities from USER QUERIES
        Enhanced with learnings from comprehensive testing (2025-11-15)
        - Famous project → district mapping
        - Strict contact name extraction rules
        - Tier-based field collection emphasis
        """
        return f"""Bạn là chuyên gia trích xuất thông tin tìm kiếm bất động sản từ câu hỏi của người dùng.

🎯 NHIỆM VỤ:
Đọc câu hỏi của user và trích xuất CÁC TIÊU CHÍ TÌM KIẾM thành JSON.

⭐ TARGET: Extract 15-20 fields để tạo tin đăng chuyên nghiệp!

**TIER 1** (CRITICAL - ALWAYS extract if available):
- property_type, transaction_type, district, area, price

**TIER 2** (HIGHLY RECOMMENDED - prioritize these):
- bedrooms, bathrooms, ward, street, furniture, direction, legal_status, contact_phone, project_name

**TIER 3** (NICE-TO-HAVE - only request if score < 70% and mentioned):
- floors, facade_width, alley_width, year_built, contact_name, balcony_direction, property_condition
- ⚠️ Do NOT request these if score >= 70% - they are optional enhancements only

**TIER 4** (TRULY OPTIONAL - NEVER request, only extract if user volunteers):
- parking, elevator, swimming_pool, gym, security, description
- ⚠️ Do NOT ask about these fields - only extract if user mentions them

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

**🏢 FAMOUS PROJECT → DISTRICT MAPPING**:
If you detect any of these famous projects, automatically extract the corresponding district:
- Landmark 81 → "Quận Bình Thạnh"
- Vinhomes Central Park → "Quận Bình Thạnh"
- Masteri Thao Dien → "Quận 2"
- Phu My Hung → "Quận 7"
- Saigon Pearl → "Quận Bình Thạnh"
- The Sun Avenue → "Quận 2"
- The Manor → "Quận Bình Thạnh"
- Estella Heights → "Quận 2"
- Gateway Thao Dien → "Quận 2"
- Feliz En Vista → "Quận 2"
- Diamond Island → "Quận 2"
- Thao Dien Pearl → "Quận 2"
- Eco Green Saigon → "Quận 7"
- Sunrise City → "Quận 7"
- Phu Hoang Anh → "Quận 7"

**3. PHYSICAL ATTRIBUTES**
- bedrooms: Số phòng ngủ
  * "2PN" → 2
  * "3 phòng ngủ" → 3
  * "2 phòng" → 2
- bathrooms: Số phòng tắm/WC (BUGFIX 2025-11-15: Support multiple aliases)
  * "2 toilet" → 2
  * "4 phòng vệ sinh" → 4
  * "có 3 phòng tắm" → 3
  * "2 WC" → 2
  * "nhà vệ sinh" = phòng tắm = toilet = WC = bathroom
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

**7. CONTACT INFORMATION**

**👤 CONTACT NAME EXTRACTION - STRICT RULES**:

✅ VALID PATTERNS (only extract from these contexts):
- "Lien he: [Name]" or "LH: [Name]"
- "Chinh chu: [Name]"
- "Anh/Ba/Chi/Ong [Name] - [phone]"
- "[Name] [10-digit phone]"

❌ INVALID EXTRACTIONS (DO NOT extract names from):
- Address components: "Phuong Binh Thanh", "Quan Nam", "Duong Xa"
- Room descriptions: "phong ngu", "phong tam"
- Street names: "Duong Xa Lo", "Hem Linh"
- Common words: "ban", "mua", "thue", "gia", "tien"

**VALIDATION**: Names must:
- Be 3-15 characters long
- Appear near phone numbers or contact keywords
- NOT match these invalid words: ban, mua, thue, cho, nha, dat, quan, phuong, duong, hem, tang, ngu, tam, phong, tien, gap, ngay, gia, thanh, binh, dong, nam, bac, tay, trung, van, linh, trai, hong, sang, full, cao, dep, tot, gan, xa, lo, toan

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

Example 5 (Bathrooms variants - BUGFIX 2025-11-15):
Input: "Nhà có 2 toilet, 3 phòng ngủ"
Output: {{"property_type": "nhà", "bathrooms": 2, "bedrooms": 3}}

Example 6 (Bathrooms variants):
Input: "Biệt thự 4 phòng vệ sinh, diện tích 200m2"
Output: {{"property_type": "biệt thự", "bathrooms": 4, "area": 200}}

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

    def _merge_entities(self, regex_entities: Dict[str, Any], llm_entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge regex and LLM extraction results (ITERATION 4: Hybrid extraction)

        Priority: LLM > Regex (LLM is more comprehensive)
        Use regex to fill gaps when LLM misses something

        Args:
            regex_entities: Baseline entities from regex patterns
            llm_entities: Comprehensive entities from LLM

        Returns:
            Merged entity dictionary
        """
        # Start with LLM results (more comprehensive)
        merged = llm_entities.copy()

        # Fill missing fields from regex (guaranteed baseline)
        for key, value in regex_entities.items():
            if key not in merged or not merged[key]:
                merged[key] = value
                self.logger.info(f"{LogEmoji.INFO} Filled gap from regex: {key} = {value}")

        return merged

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
        prompt = await self._build_enhanced_prompt(query, nlp_entities, rag_context, intent)

        # Call LLM
        entities = await self._call_llm_for_extraction(prompt)

        return entities

    async def _build_enhanced_prompt(
        self,
        query: str,
        nlp_entities: Dict[str, Any],
        rag_context: Dict[str, Any],
        intent: Optional[str] = None
    ) -> str:
        """
        Build enhanced prompt with NLP hints, RAG context, and dynamic master data.
        """
        # Fetch master data dynamically (with caching)
        if not hasattr(self, '_master_data_cache'):
            self.logger.info(f"{LogEmoji.INFO} Fetching master data from database...")
            try:
                property_types = await self.master_data_validator.get_property_types_list()
                districts = await self.master_data_validator.get_districts_list()
                amenities = await self.master_data_validator.get_amenities_list()

                # Cache for performance
                self._master_data_cache = {
                    'property_types': property_types,
                    'districts': districts,
                    'amenities': amenities
                }
                self.logger.info(
                    f"{LogEmoji.SUCCESS} Master data cached: "
                    f"{len(property_types)} property types, "
                    f"{len(districts)} districts, "
                    f"{len(amenities)} amenities"
                )
            except Exception as e:
                self.logger.warning(f"{LogEmoji.WARNING} Failed to fetch master data: {e}")
                self._master_data_cache = {
                    'property_types': [],
                    'districts': [],
                    'amenities': []
                }

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

        # Format master data dynamically
        master_data_cache = self._master_data_cache

        # Property types from master data (multilingual)
        property_types_text = "**1. PROPERTY TYPE** (from master data):\n"
        if master_data_cache['property_types']:
            prop_types_vi = [pt['name_vi'] for pt in master_data_cache['property_types'][:10]]
            prop_types_en = [pt['name_en'] for pt in master_data_cache['property_types'][:10]]
            property_types_text += f"- property_type: {' | '.join(prop_types_vi)}\n"
            property_types_text += f"  (English: {' | '.join(prop_types_en)})\n"
        else:
            property_types_text += "- property_type: (use text from query)\n"

        # Districts from master data (multilingual)
        districts_text = "**2. LOCATION** (from master data):\n"
        if master_data_cache['districts']:
            districts_sample = [d['name_vi'] for d in master_data_cache['districts'][:15]]
            districts_text += f"- district: {', '.join(districts_sample)}, ...\n"
            districts_text += "  (Chuẩn hóa theo master data, có hỗ trợ fuzzy matching)\n"
        else:
            districts_text += "- district: Quận/Huyện\n"
        districts_text += "- ward: Phường (nếu có)\n"
        districts_text += "- project_name: Tên dự án\n"

        # Amenities from master data
        amenities_text = ""
        if master_data_cache['amenities']:
            amenities_sample = [a['name_vi'] for a in master_data_cache['amenities'][:10]]
            amenities_text = f"  Available amenities: {', '.join(amenities_sample)}, ...\n"

        prompt = f"""Bạn là chuyên gia trích xuất thông tin bất động sản.

🎯 NHIỆM VỤ: Trích xuất entities từ query, SỬ DỤNG HINTS từ NLP, EXAMPLES từ database, và MASTER DATA.

{nlp_hints_text}

{examples_text}

{patterns_text}

{ranges_text}

🔍 EXTRACTION RULES:
1. **USE NLP hints as starting point** - Ưu tiên thông tin từ NLP layer
2. **FOLLOW patterns from real examples** - Tham khảo format từ DB
3. **MATCH against master data** - Sử dụng giá trị chuẩn từ master data
4. **STAY within typical value ranges** - Kiểm tra với ranges từ DB
5. **DON'T hallucinate** - Chỉ trích xuất thông tin có trong query
6. **Multilingual support** - Hỗ trợ vi/en/th/ja (fuzzy matching sẽ xử lý)

📊 ENTITIES CẦN TRÍCH XUẤT (chỉ trích xuất những gì có trong câu hỏi):

{property_types_text}

{districts_text}

**3. PHYSICAL ATTRIBUTES**:
- bedrooms: Số phòng ngủ (nullable cho đất/parking/commercial)
- bathrooms: Số phòng tắm/WC (BUGFIX 2025-11-15: Support multiple aliases)
  * "2 toilet" → 2
  * "4 phòng vệ sinh" → 4
  * "có 3 phòng tắm" → 3
  * "2 WC" → 2
  * "nhà vệ sinh" = phòng tắm = toilet = WC = bathroom
- area: Diện tích (m²)
- floors: Số tầng

**4. PRICE**:
- price: Giá cụ thể (VND) - Hỗ trợ cả dấu chấm và phẩy
- min_price: Giá tối thiểu (VND)
- max_price: Giá tối đa (VND)

**5. FEATURES & AMENITIES**:
- furniture: full | cơ bản | không | cao cấp
- direction: Đông | Tây | Nam | Bắc | Đông Nam | Đông Bắc | Tây Nam | Tây Bắc
{amenities_text}
- parking, elevator, swimming_pool, gym, security: true/false

📝 FEW-SHOT EXAMPLES (for bathroom extraction):

Example 1 (Bathrooms - toilet):
Input: "Nhà có 2 toilet, 3 phòng ngủ"
Output: {{"property_type": "nhà", "bathrooms": 2, "bedrooms": 3}}

Example 2 (Bathrooms - phòng vệ sinh):
Input: "Biệt thự 4 phòng vệ sinh, diện tích 200m2"
Output: {{"property_type": "biệt thự", "bathrooms": 4, "area": 200}}

Example 3 (Bathrooms - WC):
Input: "Căn hộ 3PN 2WC Quận 7"
Output: {{"property_type": "căn hộ", "bedrooms": 3, "bathrooms": 2, "district": "Quận 7"}}

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
        rag_context: Dict[str, Any],
        language: str = 'vi'
    ) -> Dict[str, Any]:
        """
        Generate clarification questions and suggestions when confidence is low.

        Args:
            query: User query
            entities: Extracted entities
            confidence: Confidence score
            rag_context: RAG context with similar properties
            language: User's preferred language

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
            questions.append(t("attribute_extraction.clarify_property_type", language=language))
            # Get suggestions from RAG
            if rag_context.get("patterns", {}).get("common_property_types"):
                property_type_suggestions = [
                    {
                        "value": pt["value"],
                        "count": pt["count"],
                        "label": t("attribute_extraction.label_count", language=language, value=pt['value'], count=pt['count'])
                    }
                    for pt in rag_context["patterns"]["common_property_types"][:3]
                ]
                suggestions.append({
                    "field": "property_type",
                    "question": t("attribute_extraction.suggestion_property_type", language=language),
                    "options": property_type_suggestions
                })

        if not has_location:
            questions.append(t("attribute_extraction.clarify_location", language=language))
            # Get suggestions from RAG
            if rag_context.get("patterns", {}).get("common_districts"):
                district_suggestions = [
                    {
                        "value": d["value"],
                        "count": d["count"],
                        "label": t("attribute_extraction.label_count", language=language, value=d['value'], count=d['count'])
                    }
                    for d in rag_context["patterns"]["common_districts"][:5]
                ]
                suggestions.append({
                    "field": "district",
                    "question": t("attribute_extraction.suggestion_district", language=language),
                    "options": district_suggestions
                })

        if not has_price:
            questions.append(t("attribute_extraction.clarify_budget", language=language))
            # Get price range from RAG
            if rag_context.get("value_ranges", {}).get("price"):
                price_range = rag_context["value_ranges"]["price"]
                price_suggestions = [
                    {
                        "value": "low",
                        "min": price_range["min"],
                        "max": price_range["avg"] * 0.7,
                        "label": t("attribute_extraction.label_under", language=language, amount=f"{price_range['avg'] * 0.7 / 1_000_000_000:.1f}")
                    },
                    {
                        "value": "medium",
                        "min": price_range["avg"] * 0.7,
                        "max": price_range["avg"] * 1.3,
                        "label": t("attribute_extraction.label_range", language=language,
                                   min=f"{price_range['avg'] * 0.7 / 1_000_000_000:.1f}",
                                   max=f"{price_range['avg'] * 1.3 / 1_000_000_000:.1f}")
                    },
                    {
                        "value": "high",
                        "min": price_range["avg"] * 1.3,
                        "max": price_range["max"],
                        "label": t("attribute_extraction.label_above", language=language, amount=f"{price_range['avg'] * 1.3 / 1_000_000_000:.1f}")
                    }
                ]
                suggestions.append({
                    "field": "price",
                    "question": t("attribute_extraction.suggestion_budget", language=language),
                    "options": price_suggestions
                })

        if not has_bedrooms:
            questions.append(t("attribute_extraction.clarify_bedrooms", language=language))
            suggestions.append({
                "field": "bedrooms",
                "question": t("attribute_extraction.suggestion_bedrooms", language=language),
                "options": [
                    {"value": 1, "label": t("attribute_extraction.label_studio", language=language)},
                    {"value": 2, "label": t("attribute_extraction.label_2br", language=language)},
                    {"value": 3, "label": t("attribute_extraction.label_3br", language=language)},
                    {"value": 4, "label": t("attribute_extraction.label_4br", language=language)}
                ]
            })

        # If entities were extracted but confidence still low, ask for confirmation
        if entities and confidence < 0.6:
            formatted_entities = self._format_entities_for_display(entities, language)
            questions.append(
                t("attribute_extraction.clarify_confirm", language=language, entities=formatted_entities)
            )

        return {
            "questions": questions,
            "suggestions": suggestions,
            "reason": t("attribute_extraction.clarify_reason", language=language, confidence=f"{confidence:.2f}")
        }

    def _format_entities_for_display(self, entities: Dict[str, Any], language: str = 'vi') -> str:
        """Format entities for user-friendly display."""
        parts = []
        if "property_type" in entities:
            parts.append(entities["property_type"])
        if "bedrooms" in entities:
            parts.append(t("attribute_extraction.display_bedrooms", language=language, count=entities['bedrooms']))
        if "district" in entities:
            parts.append(t("attribute_extraction.display_at", language=language, location=entities['district']))
        if "max_price" in entities:
            parts.append(t("attribute_extraction.display_under", language=language, amount=f"{entities['max_price'] / 1_000_000_000:.1f}"))
        elif "price" in entities:
            parts.append(t("attribute_extraction.display_around", language=language, amount=f"{entities['price'] / 1_000_000_000:.1f}"))

        return " ".join(parts) if parts else t("attribute_extraction.display_default", language=language)

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()
        await self.rag_enhancer.close()
        await self.master_data_validator.close()
        await self.master_data_extractor.close()
        await self.admin_routes.close()  # NEW: Cleanup admin routes
        await super().on_shutdown()


# Create service instance at module level for uvicorn
service = AttributeExtractionService()
app = service.app

if __name__ == "__main__":
    service.run()

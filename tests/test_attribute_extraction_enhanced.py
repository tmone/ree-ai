"""
Unit tests for Enhanced Attribute Extraction Service
Tests NLP + RAG + LLM pipeline
"""
import pytest
from services.attribute_extraction.nlp_processor import VietnameseNLPProcessor
from services.attribute_extraction.validator import AttributeValidator


class TestNLPProcessor:
    """Test Vietnamese NLP Processor"""

    def setup_method(self):
        """Setup test fixtures"""
        self.processor = VietnameseNLPProcessor()

    def test_extract_district(self):
        """Test district extraction and normalization"""
        test_cases = [
            ("Tìm căn hộ Q7", "Quận 7"),
            ("Nhà phố quận 2", "Quận 2"),
            ("Bán biệt thự Bình Thạnh", "Quận Bình Thạnh"),
            ("Tìm đất Thủ Đức", "Thành phố Thủ Đức"),
        ]

        for query, expected_district in test_cases:
            entities = self.processor.extract_entities(query)
            assert "district" in entities, f"Failed to extract district from: {query}"
            assert entities["district"] == expected_district, \
                f"Expected {expected_district}, got {entities['district']}"

    def test_extract_property_type(self):
        """Test property type extraction"""
        test_cases = [
            ("Tìm căn hộ 2 phòng", "căn hộ"),
            ("Bán nhà phố Q7", "nhà phố"),
            ("Cho thuê biệt thự", "biệt thự"),
            ("Tìm chung cư", "chung cư"),
            ("Bán đất nền", "đất"),
        ]

        for query, expected_type in test_cases:
            entities = self.processor.extract_entities(query)
            assert "property_type" in entities, f"Failed to extract property_type from: {query}"
            assert entities["property_type"] == expected_type, \
                f"Expected {expected_type}, got {entities['property_type']}"

    def test_extract_bedrooms(self):
        """Test bedroom extraction"""
        test_cases = [
            ("Tìm căn hộ 2 phòng ngủ", 2),
            ("Nhà 3PN", 3),
            ("Biệt thự 5 phòng", 5),
        ]

        for query, expected_bedrooms in test_cases:
            entities = self.processor.extract_entities(query)
            assert "bedrooms" in entities, f"Failed to extract bedrooms from: {query}"
            assert entities["bedrooms"] == expected_bedrooms, \
                f"Expected {expected_bedrooms}, got {entities['bedrooms']}"

    def test_extract_price(self):
        """Test price extraction and normalization"""
        test_cases = [
            ("Tìm căn hộ dưới 3 tỷ", {"max_price": 3_000_000_000}),
            ("Nhà trên 5 tỷ", {"min_price": 5_000_000_000}),
            ("Từ 2 đến 4 tỷ", {"min_price": 2_000_000_000, "max_price": 4_000_000_000}),
            ("Khoảng 3.5 tỷ", {"price": 3_500_000_000}),
            ("25 triệu/tháng", {"price": 25_000_000}),
        ]

        for query, expected_price in test_cases:
            entities = self.processor.extract_entities(query)
            for key, value in expected_price.items():
                assert key in entities, f"Failed to extract {key} from: {query}"
                assert entities[key] == value, \
                    f"Expected {value}, got {entities[key]}"

    def test_extract_area(self):
        """Test area extraction"""
        test_cases = [
            ("Căn hộ 70m²", 70.0),
            ("Nhà phố 5x20m", 100.0),  # 5 * 20
            ("Diện tích 120m2", 120.0),
        ]

        for query, expected_area in test_cases:
            entities = self.processor.extract_entities(query)
            assert "area" in entities, f"Failed to extract area from: {query}"
            assert entities["area"] == expected_area, \
                f"Expected {expected_area}, got {entities['area']}"

    def test_extract_amenities(self):
        """Test amenity extraction"""
        query = "Căn hộ có hồ bơi, gym, thang máy, chỗ đậu xe"
        entities = self.processor.extract_entities(query)

        expected_amenities = ["swimming_pool", "gym", "elevator", "parking"]
        for amenity in expected_amenities:
            assert amenity in entities, f"Failed to extract amenity: {amenity}"
            assert entities[amenity] is True

    def test_extract_project_name(self):
        """Test project name extraction"""
        test_cases = [
            ("Căn hộ Vinhomes Q7", "Vinhomes"),
            ("Masteri Thảo Điền", "Masteri"),
            ("The Manor 2PN", "The Manor"),
        ]

        for query, expected_project in test_cases:
            entities = self.processor.extract_entities(query)
            if "project_name" in entities:
                assert expected_project.lower() in entities["project_name"].lower()

    def test_complex_query(self):
        """Test complex query with multiple entities"""
        query = "Tìm căn hộ 2 phòng ngủ Vinhomes Quận 7 dưới 3 tỷ có hồ bơi"

        entities = self.processor.extract_entities(query)

        # Should extract: property_type, bedrooms, project, district, price, amenity
        assert entities.get("property_type") == "căn hộ"
        assert entities.get("bedrooms") == 2
        assert "Vinhomes" in entities.get("project_name", "")
        assert entities.get("district") == "Quận 7"
        assert entities.get("max_price") == 3_000_000_000
        assert entities.get("swimming_pool") is True

    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        # More entities = higher confidence
        entities_low = {"district": "Quận 7"}
        entities_medium = {"district": "Quận 7", "property_type": "căn hộ", "bedrooms": 2}
        entities_high = {
            "district": "Quận 7",
            "property_type": "căn hộ",
            "bedrooms": 2,
            "price": 3_000_000_000,
            "area": 70
        }

        conf_low = self.processor.get_extraction_confidence(entities_low)
        conf_medium = self.processor.get_extraction_confidence(entities_medium)
        conf_high = self.processor.get_extraction_confidence(entities_high)

        assert conf_low < conf_medium < conf_high


class TestAttributeValidator:
    """Test Attribute Validator"""

    def setup_method(self):
        """Setup test fixtures"""
        self.validator = AttributeValidator()

    def test_validate_logical_consistency_bedrooms_bathrooms(self):
        """Test logical validation for bedrooms vs bathrooms"""
        # Normal case
        entities_ok = {"bedrooms": 3, "bathrooms": 2}
        result = self.validator.validate(entities_ok, {}, {})
        assert result["confidence"] > 0.5
        assert len(result["warnings"]) == 1  # Missing required field warning

        # Unusual case: too many bathrooms
        entities_unusual = {"bedrooms": 2, "bathrooms": 6}
        result = self.validator.validate(entities_unusual, {}, {})
        warnings = result["warnings"]
        assert any("Bathrooms" in w for w in warnings)

    def test_validate_price_range(self):
        """Test price validation against RAG context"""
        entities = {
            "district": "Quận 7",
            "price": 10_000_000_000,  # 10 billion VND
            "area": 100
        }

        # RAG context with similar properties
        rag_context = {
            "value_ranges": {
                "price": {
                    "min": 3_000_000_000,
                    "max": 6_000_000_000,
                    "avg": 4_500_000_000
                }
            },
            "patterns": {},
            "examples": [],
            "retrieved_count": 5
        }

        result = self.validator.validate(entities, {}, rag_context)

        # Should have warning about high price
        warnings = result["warnings"]
        assert any("unusually high" in w.lower() for w in warnings)

    def test_validate_area_range(self):
        """Test area validation"""
        # Unusually small apartment
        entities_small = {
            "property_type": "căn hộ",
            "area": 10  # 10m² is very small
        }
        result = self.validator.validate(entities_small, {}, {})
        warnings = result["warnings"]
        assert any("unusually small" in w.lower() for w in warnings)

        # Unusually large apartment
        entities_large = {
            "property_type": "căn hộ",
            "area": 600  # 600m² is very large for apartment
        }
        result = self.validator.validate(entities_large, {}, {})
        warnings = result["warnings"]
        assert any("unusually large" in w.lower() for w in warnings)

    def test_cross_validate_with_nlp(self):
        """Test cross-validation between LLM and NLP entities"""
        # LLM missed something NLP found
        llm_entities = {"property_type": "căn hộ"}
        nlp_entities = {"property_type": "căn hộ", "district": "Quận 7", "bedrooms": 2}

        result = self.validator.validate(llm_entities, nlp_entities, {})
        warnings = result["warnings"]

        # Should warn about missing district and bedrooms
        assert any("district" in w.lower() for w in warnings)
        assert any("bedrooms" in w.lower() for w in warnings)

    def test_validate_against_rag_patterns(self):
        """Test validation against RAG patterns"""
        entities = {
            "district": "Quận 100",  # Non-existent district
            "property_type": "căn hộ"
        }

        rag_context = {
            "patterns": {
                "common_districts": [
                    {"value": "Quận 7", "count": 3},
                    {"value": "Quận 2", "count": 2}
                ]
            },
            "value_ranges": {},
            "examples": [],
            "retrieved_count": 5
        }

        result = self.validator.validate(entities, {}, rag_context)
        warnings = result["warnings"]

        # Should warn about unknown district
        assert any("not found" in w.lower() for w in warnings)

    def test_confidence_calculation(self):
        """Test confidence score calculation with various factors"""
        # High confidence: many entities, no warnings, with RAG context
        entities_good = {
            "property_type": "căn hộ",
            "district": "Quận 7",
            "bedrooms": 2,
            "price": 3_000_000_000,
            "area": 70
        }

        rag_context_good = {
            "retrieved_count": 5,
            "patterns": {},
            "value_ranges": {},
            "examples": []
        }

        result = self.validator.validate(entities_good, entities_good, rag_context_good)
        assert result["confidence"] > 0.7  # Should be high

        # Low confidence: few entities, many warnings, no RAG
        entities_poor = {"district": "Quận 100"}  # Unknown district
        result = self.validator.validate(entities_poor, {}, {})
        assert result["confidence"] < 0.5  # Should be low


class TestIntegration:
    """Integration tests for full pipeline"""

    def test_nlp_to_validator_flow(self):
        """Test data flow from NLP to Validator"""
        processor = VietnameseNLPProcessor()
        validator = AttributeValidator()

        query = "Tìm căn hộ 2 phòng ngủ Quận 7 dưới 3 tỷ"

        # Extract with NLP
        nlp_entities = processor.extract_entities(query)

        # Validate (pretend LLM extracted the same)
        result = validator.validate(nlp_entities, nlp_entities, {})

        # Should have good confidence (NLP and LLM agree)
        assert result["confidence"] > 0.5
        assert len(result["validated_entities"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

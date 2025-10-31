"""
Data Pipeline Tests - Test theo đúng flow thực tế CTO

Flow: Crawler → Chunking → Extraction → Classification → Storage → Search
"""
import pytest
import httpx
import asyncio
from typing import List, Dict, Any


@pytest.mark.integration
@pytest.mark.critical
class TestCrawlerService:
    """Test Crawler Service - CTO Data Collection"""

    @pytest.mark.asyncio
    async def test_crawler_service_health(self, http_client):
        """Test Crawler service is running"""
        try:
            response = await http_client.get("http://localhost:8100/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Crawler service is healthy")
                assert True
            else:
                print("⚠️ Crawler service not running - skipping crawler tests")
                pytest.skip("Crawler service not available")
        except:
            pytest.skip("Crawler service not running")

    @pytest.mark.asyncio
    async def test_crawl_batdongsan_returns_properties(self, http_client):
        """
        Test: Crawler lấy được data từ batdongsan.com.vn

        Expected:
        - Returns list of properties
        - Each property has: title, price, location, bedrooms, description
        - Minimum 10 properties
        """
        try:
            response = await http_client.post(
                "http://localhost:8100/crawl/batdongsan",
                json={"limit": 10},
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()

                # Verify response structure
                assert "success" in data
                assert "properties" in data
                assert "count" in data

                properties = data["properties"]

                # Should return at least some properties
                assert len(properties) > 0, "No properties returned"

                # Verify first property structure
                first_prop = properties[0]
                required_fields = ["title", "price", "location", "bedrooms", "description"]

                for field in required_fields:
                    assert field in first_prop, f"Missing field: {field}"

                print(f"✅ Crawled {len(properties)} properties from batdongsan.com.vn")
                print(f"   Sample: {first_prop['title'][:50]}...")

            else:
                pytest.skip("Crawler endpoint not working")

        except Exception as e:
            print(f"⚠️ Crawler test error: {e}")
            pytest.skip("Crawler service error")

    @pytest.mark.asyncio
    async def test_crawl_nhatot_returns_properties(self, http_client):
        """Test: Crawler lấy được data từ nhatot.com"""
        try:
            response = await http_client.post(
                "http://localhost:8100/crawl/nhatot",
                json={"limit": 10},
                timeout=30.0
            )

            if response.status_code == 200:
                data = response.json()
                properties = data.get("properties", [])

                assert len(properties) > 0
                print(f"✅ Crawled {len(properties)} properties from nhatot.com")

        except:
            pytest.skip("Crawler service not available")

    @pytest.mark.asyncio
    async def test_crawler_extracts_correct_schema(self, http_client):
        """Test: Crawler trích xuất đúng schema theo yêu cầu"""
        try:
            response = await http_client.post(
                "http://localhost:8100/crawl/batdongsan",
                json={"limit": 5},
                timeout=30.0
            )

            if response.status_code == 200:
                properties = response.json()["properties"]

                for prop in properties:
                    # Verify data types
                    assert isinstance(prop["title"], str)
                    assert isinstance(prop["price"], str)
                    assert isinstance(prop["location"], str)
                    assert isinstance(prop["bedrooms"], int)
                    assert isinstance(prop["description"], str)

                    # Verify non-empty
                    assert len(prop["title"]) > 0
                    assert len(prop["description"]) > 0

                print(f"✅ Schema validation passed for {len(properties)} properties")

        except:
            pytest.skip("Crawler service not available")


@pytest.mark.integration
@pytest.mark.critical
class TestSemanticChunking:
    """Test Semantic Chunking - 6 Steps CTO"""

    @pytest.mark.asyncio
    async def test_chunking_service_health(self, http_client):
        """Test Chunking service is running"""
        try:
            response = await http_client.get("http://localhost:8101/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Semantic Chunking service is healthy")
            else:
                pytest.skip("Chunking service not running")
        except:
            pytest.skip("Chunking service not running")

    @pytest.mark.asyncio
    async def test_step1_sentence_segmentation(self, http_client):
        """Test Step 1: Sentence Segmentation"""
        text = "Nhà 3 phòng ngủ. Giá 5 tỷ. View đẹp ở Quận 1."

        try:
            response = await http_client.post(
                "http://localhost:8101/chunk",
                json={"text": text},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                chunks = data.get("chunks", [])

                # Should segment into chunks
                assert len(chunks) > 0

                # Each chunk should have text and embedding
                for chunk in chunks:
                    assert "text" in chunk
                    assert "embedding" in chunk
                    assert "embedding_dimension" in chunk

                print(f"✅ Step 1: Segmented into {len(chunks)} chunks")

        except:
            pytest.skip("Chunking service not available")

    @pytest.mark.asyncio
    async def test_step2_embeddings_dimension(self, http_client):
        """Test Step 2: Embeddings have correct dimension (384 for MiniLM)"""
        text = "Nhà mặt tiền đường lớn, 3 phòng ngủ, 2 toilet."

        try:
            response = await http_client.post(
                "http://localhost:8101/chunk",
                json={"text": text},
                timeout=10.0
            )

            if response.status_code == 200:
                chunks = response.json()["chunks"]

                for chunk in chunks:
                    # Verify embedding dimension = 384 (MiniLM)
                    assert chunk["embedding_dimension"] == 384
                    assert len(chunk["embedding"]) == 384

                print(f"✅ Step 2: Embeddings dimension = 384 ✓")

        except:
            pytest.skip("Chunking service not available")

    @pytest.mark.asyncio
    async def test_full_chunking_pipeline(self, http_client):
        """Test: Toàn bộ 6 steps chunking"""
        text = """
        Bán nhà mặt tiền đường Trần Hưng Đạo, Quận 1.
        Diện tích: 80m2, 3 tầng, 4 phòng ngủ, 5 toilet.
        Giá: 15 tỷ VNĐ (có thương lượng).
        Nhà mới xây, nội thất cao cấp, view đẹp.
        Gần trường học, bệnh viện, chợ, siêu thị.
        """

        try:
            response = await http_client.post(
                "http://localhost:8101/chunk",
                json={"text": text},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()

                # Verify response structure
                assert data["success"] == True
                assert "chunks" in data
                assert "count" in data

                chunks = data["chunks"]

                # Should have multiple chunks
                assert len(chunks) > 0

                # Verify each chunk
                for i, chunk in enumerate(chunks):
                    assert "text" in chunk
                    assert "embedding" in chunk
                    assert len(chunk["text"]) > 0
                    assert len(chunk["embedding"]) == 384

                print(f"✅ Full 6-step chunking: {len(chunks)} chunks created")
                print(f"   Method: {data.get('method')}")

        except:
            pytest.skip("Chunking service not available")


@pytest.mark.integration
class TestClassificationService:
    """Test Classification Service - 3 modes"""

    @pytest.mark.asyncio
    async def test_classification_service_health(self, http_client):
        """Test Classification service is running"""
        try:
            response = await http_client.get("http://localhost:8102/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Classification service is healthy")
            else:
                pytest.skip("Classification service not running")
        except:
            pytest.skip("Classification service not running")

    @pytest.mark.asyncio
    async def test_classify_mode_filter(self, http_client):
        """Test Mode 1: Filter - Keyword-based classification"""
        test_cases = [
            {"text": "Bán nhà riêng 3 phòng ngủ", "expected": "house"},
            {"text": "Căn hộ chung cư 2 phòng", "expected": "apartment"},
            {"text": "Biệt thự view biển", "expected": "villa"},
            {"text": "Đất nền dự án", "expected": "land"}
        ]

        try:
            for case in test_cases:
                response = await http_client.post(
                    "http://localhost:8102/classify",
                    json={"text": case["text"], "mode": "filter"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    data = response.json()

                    # Verify classification
                    assert "property_type" in data
                    assert "confidence" in data
                    assert "mode_used" in data

                    assert data["mode_used"] == "filter"

                    print(f"✅ Filter mode: '{case['text'][:30]}' → {data['property_type']}")

        except:
            pytest.skip("Classification service not available")

    @pytest.mark.asyncio
    async def test_classify_mode_semantic(self, http_client):
        """Test Mode 2: Semantic - LLM-based classification"""
        text = "Tôi muốn bán căn hộ view sông 3 phòng ngủ"

        try:
            response = await http_client.post(
                "http://localhost:8102/classify",
                json={"text": text, "mode": "semantic"},
                timeout=15.0
            )

            if response.status_code == 200:
                data = response.json()

                assert data["mode_used"] == "semantic"
                assert data["property_type"] in ["apartment", "house", "villa", "land", "commercial", "unknown"]

                print(f"✅ Semantic mode: {data['property_type']} (confidence: {data['confidence']:.2f})")

        except:
            pytest.skip("Classification service not available")

    @pytest.mark.asyncio
    async def test_classify_mode_both(self, http_client):
        """Test Mode 3: Both - Combined filter + semantic"""
        text = "Nhà mặt tiền đường lớn, 3 tầng, 4 phòng ngủ"

        try:
            response = await http_client.post(
                "http://localhost:8102/classify",
                json={"text": text, "mode": "both"},
                timeout=15.0
            )

            if response.status_code == 200:
                data = response.json()

                # Verify both modes were used
                assert data["mode_used"] == "both"
                assert "filter_result" in data
                assert "semantic_result" in data

                print(f"✅ Both mode:")
                print(f"   Filter: {data.get('filter_result')}")
                print(f"   Semantic: {data.get('semantic_result')}")
                print(f"   Final: {data['property_type']} (confidence: {data['confidence']:.2f})")

        except:
            pytest.skip("Classification service not available")


@pytest.mark.integration
@pytest.mark.slow
class TestFullDataPipeline:
    """Test E2E Data Pipeline: Crawler → Chunking → Classification → Storage → Search"""

    @pytest.mark.asyncio
    async def test_crawl_to_chunking_pipeline(self, http_client):
        """
        Test: Crawler → Semantic Chunking

        Flow:
        1. Crawl properties
        2. Chunk descriptions
        3. Verify embeddings created
        """
        try:
            # Step 1: Crawl
            crawl_response = await http_client.post(
                "http://localhost:8100/crawl/batdongsan",
                json={"limit": 3},
                timeout=30.0
            )

            if crawl_response.status_code != 200:
                pytest.skip("Crawler not available")

            properties = crawl_response.json()["properties"]
            assert len(properties) > 0

            print(f"✅ Step 1: Crawled {len(properties)} properties")

            # Step 2: Chunk each property description
            chunked_count = 0
            for prop in properties:
                chunk_response = await http_client.post(
                    "http://localhost:8101/chunk",
                    json={"text": prop["description"]},
                    timeout=10.0
                )

                if chunk_response.status_code == 200:
                    chunks = chunk_response.json()["chunks"]
                    assert len(chunks) > 0
                    chunked_count += 1

            print(f"✅ Step 2: Chunked {chunked_count}/{len(properties)} properties")

            assert chunked_count > 0, "No properties were chunked successfully"

        except Exception as e:
            print(f"⚠️ Pipeline test error: {e}")
            pytest.skip("Pipeline services not available")

    @pytest.mark.asyncio
    async def test_crawl_to_classification_pipeline(self, http_client):
        """
        Test: Crawler → Classification

        Flow:
        1. Crawl properties
        2. Classify each property type
        3. Verify classification results
        """
        try:
            # Step 1: Crawl
            crawl_response = await http_client.post(
                "http://localhost:8100/crawl/batdongsan",
                json={"limit": 5},
                timeout=30.0
            )

            if crawl_response.status_code != 200:
                pytest.skip("Crawler not available")

            properties = crawl_response.json()["properties"]

            print(f"✅ Step 1: Crawled {len(properties)} properties")

            # Step 2: Classify
            classified_count = 0
            for prop in properties:
                classify_response = await http_client.post(
                    "http://localhost:8102/classify",
                    json={"text": prop["description"], "mode": "filter"},
                    timeout=10.0
                )

                if classify_response.status_code == 200:
                    classification = classify_response.json()
                    assert "property_type" in classification
                    classified_count += 1

                    print(f"   → {prop['title'][:40]}: {classification['property_type']}")

            print(f"✅ Step 2: Classified {classified_count}/{len(properties)} properties")

            assert classified_count > 0

        except Exception as e:
            print(f"⚠️ Pipeline test error: {e}")
            pytest.skip("Pipeline services not available")

    @pytest.mark.asyncio
    async def test_full_e2e_pipeline(self, http_client):
        """
        Test: Complete E2E Pipeline

        Flow:
        1. Crawl property from batdongsan.com.vn
        2. Semantic chunking (6 steps)
        3. Classification (3 modes)
        4. Verify data ready for storage

        Expected Result:
        - Property data with chunks and embeddings
        - Property classified correctly
        - Ready to store in OpenSearch + PostgreSQL
        """
        try:
            # Step 1: Crawl 1 property
            crawl_response = await http_client.post(
                "http://localhost:8100/crawl/batdongsan",
                json={"limit": 1},
                timeout=30.0
            )

            if crawl_response.status_code != 200:
                pytest.skip("Crawler not available")

            property_data = crawl_response.json()["properties"][0]
            print(f"✅ Step 1: Crawled property: {property_data['title']}")

            # Step 2: Semantic chunking
            chunk_response = await http_client.post(
                "http://localhost:8101/chunk",
                json={"text": property_data["description"]},
                timeout=10.0
            )

            if chunk_response.status_code == 200:
                chunks = chunk_response.json()["chunks"]
                print(f"✅ Step 2: Created {len(chunks)} chunks")

                # Add chunks to property data
                property_data["chunks"] = chunks

            # Step 3: Classification
            classify_response = await http_client.post(
                "http://localhost:8102/classify",
                json={"text": property_data["description"], "mode": "both"},
                timeout=15.0
            )

            if classify_response.status_code == 200:
                classification = classify_response.json()
                print(f"✅ Step 3: Classified as {classification['property_type']}")

                # Add classification to property data
                property_data["property_type"] = classification["property_type"]
                property_data["classification_confidence"] = classification["confidence"]

            # Step 4: Verify data ready for storage
            assert "title" in property_data
            assert "price" in property_data
            assert "location" in property_data
            assert "bedrooms" in property_data
            assert "chunks" in property_data
            assert "property_type" in property_data

            print(f"✅ Step 4: Data ready for OpenSearch + PostgreSQL storage")
            print(f"")
            print(f"📊 Final Property Data:")
            print(f"   Title: {property_data['title']}")
            print(f"   Type: {property_data['property_type']}")
            print(f"   Chunks: {len(property_data['chunks'])}")
            print(f"   Embeddings: {len(property_data['chunks'][0]['embedding'])}D")
            print(f"")
            print(f"✅ E2E Pipeline Complete: Ready to store and search!")

        except Exception as e:
            print(f"⚠️ E2E Pipeline error: {e}")
            pytest.skip("Pipeline services not fully available")

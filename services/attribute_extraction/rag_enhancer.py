"""
RAG Context Enhancer for Attribute Extraction
Retrieves similar properties from OpenSearch to provide real-world context and patterns
"""
import httpx
import json
from typing import Dict, Any, List, Optional
from collections import Counter
from shared.utils.logger import setup_logger, LogEmoji
from shared.config import settings

logger = setup_logger(__name__)


class RAGContextEnhancer:
    """
    Retrieve similar properties from OpenSearch and extract attribute patterns.

    This provides the LLM with real-world examples and value distributions,
    reducing hallucination and improving accuracy.
    """

    def __init__(self, db_gateway_url: Optional[str] = None):
        """
        Initialize RAG context enhancer.

        Args:
            db_gateway_url: URL of DB Gateway service (default from settings)
        """
        self.db_gateway_url = db_gateway_url or settings.get_db_gateway_url()
        self.http_client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"{LogEmoji.INFO} RAG Enhancer initialized with DB Gateway: {self.db_gateway_url}")

    async def get_context(
        self,
        query: str,
        nlp_entities: Optional[Dict[str, Any]] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get RAG context by retrieving similar properties and extracting patterns.

        Args:
            query: User query or property description
            nlp_entities: Pre-extracted entities from NLP layer (used for filtering)
            limit: Number of similar properties to retrieve

        Returns:
            Dictionary with:
            - patterns: Common attribute patterns from similar properties
            - examples: Few-shot examples from real properties
            - value_ranges: Statistical ranges for numeric attributes
            - retrieved_count: Number of properties retrieved
        """
        try:
            logger.info(f"{LogEmoji.TARGET} Retrieving RAG context for: '{query[:100]}...'")

            # Build search filters from NLP entities
            filters = self._build_filters(nlp_entities) if nlp_entities else {}

            # Retrieve similar properties
            properties = await self._search_similar_properties(query, filters, limit)

            if not properties:
                logger.warning(f"{LogEmoji.WARNING} No similar properties found for RAG context")
                return self._empty_context()

            logger.info(f"{LogEmoji.SUCCESS} Retrieved {len(properties)} properties for RAG context")

            # Extract patterns from retrieved properties
            patterns = self._extract_patterns(properties)
            value_ranges = self._get_value_ranges(properties)
            examples = self._build_few_shot_examples(properties, max_examples=3)

            context = {
                "patterns": patterns,
                "examples": examples,
                "value_ranges": value_ranges,
                "retrieved_count": len(properties)
            }

            logger.debug(f"RAG Context: {json.dumps(context, indent=2, ensure_ascii=False)}")
            return context

        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} RAG context retrieval failed: {e}")
            return self._empty_context()

    async def _search_similar_properties(
        self,
        query: str,
        filters: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Search for similar properties using DB Gateway.

        Args:
            query: Search query
            filters: Search filters
            limit: Maximum results

        Returns:
            List of property documents
        """
        try:
            search_request = {
                "query": query,
                "filters": filters,
                "limit": limit,
                "use_vector": True,
                "use_bm25": True,
                "alpha": 0.6  # Slightly favor vector search for semantic similarity
            }

            response = await self.http_client.post(
                f"{self.db_gateway_url}/search",
                json=search_request
            )

            if response.status_code == 200:
                data = response.json()
                properties = data.get("results", [])
                logger.debug(f"DB Gateway returned {len(properties)} results")
                return properties
            else:
                logger.warning(f"{LogEmoji.WARNING} DB Gateway search failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Search request failed: {e}")
            return []

    def _build_filters(self, nlp_entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build search filters from NLP-extracted entities.

        Args:
            nlp_entities: Entities extracted by NLP processor

        Returns:
            Filters dict for DB Gateway search
        """
        filters = {}

        # Property type filter
        if "property_type" in nlp_entities:
            filters["property_type"] = nlp_entities["property_type"]

        # Location filters
        if "district" in nlp_entities:
            filters["district"] = nlp_entities["district"]

        # Numeric range filters
        if "min_price" in nlp_entities:
            filters["min_price"] = nlp_entities["min_price"]
        if "max_price" in nlp_entities:
            filters["max_price"] = nlp_entities["max_price"]

        if "bedrooms" in nlp_entities:
            # Search for properties with same or +/- 1 bedroom
            filters["min_bedrooms"] = max(1, nlp_entities["bedrooms"] - 1)

        if "area" in nlp_entities:
            # Search within +/- 20% of target area
            target_area = nlp_entities["area"]
            filters["min_area"] = target_area * 0.8
            filters["max_area"] = target_area * 1.2

        logger.debug(f"Built filters: {filters}")
        return filters

    def _extract_patterns(self, properties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract common attribute patterns from similar properties.

        Args:
            properties: List of property documents

        Returns:
            Dictionary of patterns (common values, frequencies)
        """
        patterns = {}

        # Extract common districts
        districts = [p.get("district") for p in properties if p.get("district")]
        if districts:
            district_counts = Counter(districts)
            patterns["common_districts"] = [
                {"value": district, "count": count}
                for district, count in district_counts.most_common(5)
            ]

        # Extract common property types
        property_types = [p.get("property_type") for p in properties if p.get("property_type")]
        if property_types:
            type_counts = Counter(property_types)
            patterns["common_property_types"] = [
                {"value": ptype, "count": count}
                for ptype, count in type_counts.most_common(3)
            ]

        # Extract common bedroom counts
        bedrooms = [p.get("bedrooms") for p in properties if p.get("bedrooms")]
        if bedrooms:
            bedroom_counts = Counter(bedrooms)
            patterns["common_bedrooms"] = [
                {"value": br, "count": count}
                for br, count in bedroom_counts.most_common(3)
            ]

        # Extract common amenities
        all_amenities = []
        for prop in properties:
            metadata = prop.get("metadata", {})
            if isinstance(metadata, dict):
                for key, value in metadata.items():
                    if key in ["parking", "elevator", "swimming_pool", "gym", "security"]:
                        if value is True:
                            all_amenities.append(key)

        if all_amenities:
            amenity_counts = Counter(all_amenities)
            patterns["common_amenities"] = [
                {"amenity": amenity, "frequency": count / len(properties)}
                for amenity, count in amenity_counts.most_common(5)
            ]

        logger.debug(f"Extracted patterns: {patterns}")
        return patterns

    def _get_value_ranges(self, properties: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """
        Calculate statistical ranges for numeric attributes.

        Args:
            properties: List of property documents

        Returns:
            Dictionary of value ranges (min, max, avg, median)
        """
        value_ranges = {}

        # Price range
        prices = []
        for p in properties:
            price = p.get("price")
            if price:
                # Handle both numeric and string prices
                if isinstance(price, (int, float)):
                    prices.append(float(price))
                elif isinstance(price, str):
                    # Try to extract numeric value
                    price_num = self._parse_price_string(price)
                    if price_num:
                        prices.append(price_num)

        if prices:
            value_ranges["price"] = {
                "min": min(prices),
                "max": max(prices),
                "avg": sum(prices) / len(prices),
                "count": len(prices)
            }

        # Area range
        areas = []
        for p in properties:
            area = p.get("area")
            if area:
                if isinstance(area, (int, float)):
                    areas.append(float(area))
                elif isinstance(area, str):
                    area_num = self._parse_area_string(area)
                    if area_num:
                        areas.append(area_num)

        if areas:
            value_ranges["area"] = {
                "min": min(areas),
                "max": max(areas),
                "avg": sum(areas) / len(areas),
                "count": len(areas)
            }

        # Bedrooms range
        bedrooms = [p.get("bedrooms") for p in properties if isinstance(p.get("bedrooms"), int)]
        if bedrooms:
            value_ranges["bedrooms"] = {
                "min": min(bedrooms),
                "max": max(bedrooms),
                "avg": sum(bedrooms) / len(bedrooms),
                "count": len(bedrooms)
            }

        logger.debug(f"Value ranges: {value_ranges}")
        return value_ranges

    def _build_few_shot_examples(
        self,
        properties: List[Dict[str, Any]],
        max_examples: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Build few-shot examples from real properties.

        Args:
            properties: List of property documents
            max_examples: Maximum number of examples to return

        Returns:
            List of simplified property examples
        """
        examples = []

        for prop in properties[:max_examples]:
            example = {
                "title": prop.get("title", ""),
                "property_type": prop.get("property_type"),
                "district": prop.get("district"),
                "bedrooms": prop.get("bedrooms"),
                "bathrooms": prop.get("bathrooms"),
                "area": prop.get("area"),
                "price": prop.get("price"),
            }

            # Add amenities if available
            metadata = prop.get("metadata", {})
            if isinstance(metadata, dict):
                amenities = {k: v for k, v in metadata.items()
                           if k in ["parking", "elevator", "swimming_pool", "gym"] and v}
                if amenities:
                    example["amenities"] = amenities

            examples.append(example)

        logger.debug(f"Built {len(examples)} few-shot examples")
        return examples

    def _parse_price_string(self, price_str: str) -> Optional[float]:
        """Parse price string to numeric value (VND)"""
        import re
        price_str = price_str.lower()

        # Match "X.Y tỷ" or "X tỷ"
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*tỷ', price_str)
        if match:
            return float(match.group(1).replace(',', '.')) * 1_000_000_000

        # Match "X triệu"
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*triệu', price_str)
        if match:
            return float(match.group(1).replace(',', '.')) * 1_000_000

        # Match plain number
        match = re.search(r'(\d+(?:[.,]\d+)?)', price_str)
        if match:
            return float(match.group(1).replace(',', '.'))

        return None

    def _parse_area_string(self, area_str: str) -> Optional[float]:
        """Parse area string to numeric value (m²)"""
        import re
        area_str = area_str.lower()

        # Match "Xm²" or "X m2"
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*m', area_str)
        if match:
            return float(match.group(1).replace(',', '.'))

        return None

    def _empty_context(self) -> Dict[str, Any]:
        """Return empty context when RAG retrieval fails"""
        return {
            "patterns": {},
            "examples": [],
            "value_ranges": {},
            "retrieved_count": 0
        }

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


# Convenience function
async def get_rag_context(
    query: str,
    nlp_entities: Optional[Dict[str, Any]] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Get RAG context for attribute extraction.

    Args:
        query: User query or property description
        nlp_entities: Pre-extracted NLP entities
        limit: Number of similar properties to retrieve

    Returns:
        RAG context dictionary
    """
    enhancer = RAGContextEnhancer()
    try:
        context = await enhancer.get_context(query, nlp_entities, limit)
        return context
    finally:
        await enhancer.close()

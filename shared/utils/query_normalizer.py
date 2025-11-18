"""
Query Normalization Utility

Normalizes user queries before attribute extraction to improve accuracy:
1. Expand abbreviations (Q1 → Quận 1, 2BR → 2 bedrooms)
2. Normalize mixed languages (Vietnamese + English)
3. Handle multiple values (Quận 1, 2, 7 → [Quận 1, Quận 2, Quận 7])
4. Clean special characters
5. Standardize formats

Usage:
    from shared.utils.query_normalizer import QueryNormalizer

    normalizer = QueryNormalizer()
    normalized = normalizer.normalize("Tìm 2BR Q1 5B")
    # Result: "Tìm 2 phòng ngủ Quận 1 5 tỷ"
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional


class QueryNormalizer:
    """Normalize user queries for better attribute extraction"""

    def __init__(self, keywords_path: Optional[str] = None):
        """
        Initialize query normalizer

        Args:
            keywords_path: Path to multilingual_keywords.json (optional)
        """
        # Load multilingual keywords
        if keywords_path is None:
            # Default path
            current_dir = Path(__file__).parent
            keywords_path = current_dir.parent / "data" / "multilingual_keywords.json"

        with open(keywords_path, 'r', encoding='utf-8') as f:
            self.keywords = json.load(f)

        # Build normalization patterns
        self._build_patterns()

    def _build_patterns(self):
        """Build regex patterns from keywords"""

        # District abbreviations
        self.district_map = self.keywords.get("district_abbreviations", {}).get("patterns", {})

        # Bedroom patterns
        bedroom_data = self.keywords.get("property_attributes", {}).get("bedrooms", {})
        self.bedroom_map = bedroom_data.get("patterns", {})

        # Price unit patterns
        price_data = self.keywords.get("property_attributes", {}).get("price", {})
        self.price_units = price_data.get("units", {})

    def normalize(self, query: str) -> str:
        """
        Normalize query string

        Args:
            query: Raw user query

        Returns:
            Normalized query string
        """
        if not query:
            return query

        normalized = query

        # Step 1: Expand district abbreviations
        normalized = self._expand_districts(normalized)

        # Step 2: Expand bedroom abbreviations
        normalized = self._expand_bedrooms(normalized)

        # Step 3: Expand price abbreviations
        normalized = self._expand_prices(normalized)

        # Step 4: Handle multiple district values
        normalized = self._expand_multiple_districts(normalized)

        # Step 5: Clean up extra spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def _expand_districts(self, query: str) -> str:
        """
        Expand district abbreviations

        Examples:
            "Q1" → "Quận 1"
            "D1" → "District 1"
            "District 1" → "Quận 1"
        """
        result = query

        # Sort by length (descending) to match longer patterns first
        sorted_patterns = sorted(self.district_map.items(), key=lambda x: len(x[0]), reverse=True)

        for abbr, full in sorted_patterns:
            # Use word boundary to avoid partial matches
            pattern = r'\b' + re.escape(abbr) + r'\b'
            result = re.sub(pattern, full, result, flags=re.IGNORECASE)

        return result

    def _expand_bedrooms(self, query: str) -> str:
        """
        Expand bedroom abbreviations

        Examples:
            "2BR" → "2 phòng ngủ"
            "3 BR" → "3 phòng ngủ"
            "2-BR" → "2 phòng ngủ"
        """
        result = query

        # Pattern: number + optional separator + BR
        patterns = [
            (r'(\d+)\s*BR\b', r'\1 phòng ngủ'),           # 2BR → 2 phòng ngủ
            (r'(\d+)\s*-\s*BR\b', r'\1 phòng ngủ'),       # 2-BR → 2 phòng ngủ
            (r'(\d+)\s+bedroom(?:s)?\b', r'\1 phòng ngủ'), # 2 bedrooms → 2 phòng ngủ
        ]

        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    def _expand_prices(self, query: str) -> str:
        """
        Expand price abbreviations

        Examples:
            "5B" → "5 tỷ"
            "20M" → "20 triệu"
            "5 billion" → "5 tỷ"
        """
        result = query

        # Pattern: number + price unit
        replacements = {
            r'(\d+)\s*B\b': r'\1 tỷ',                   # 5B → 5 tỷ
            r'(\d+)\s*M\b': r'\1 triệu',                # 20M → 20 triệu
            r'(\d+)\s*billion\b': r'\1 tỷ',             # 5 billion → 5 tỷ
            r'(\d+)\s*million\b': r'\1 triệu',          # 20 million → 20 triệu
        }

        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        return result

    def _expand_multiple_districts(self, query: str) -> str:
        """
        Expand multiple district values

        Examples:
            "Quận 1, 2, 7" → "Quận 1, Quận 2, Quận 7"
            "Q1, 2, hoặc 7" → "Quận 1, Quận 2, hoặc Quận 7"
        """
        result = query

        # Pattern: "Quận X, Y, Z" → "Quận X, Quận Y, Quận Z"
        # Match: Quận/District followed by number, then comma-separated numbers
        patterns = [
            # Vietnamese: Quận 1, 2, 7
            (
                r'(Quận|quan)\s+(\d+)(?:\s*,\s*(\d+))+',
                lambda m: self._expand_district_list(m, 'Quận')
            ),
            # English: District 1, 2, 7
            (
                r'(District|district)\s+(\d+)(?:\s*,\s*(\d+))+',
                lambda m: self._expand_district_list(m, 'Quận')
            ),
            # Abbreviated: Q1, Q2, Q7 or D1, D2, D7
            (
                r'([QD])(\d+)(?:\s*,\s*[QD]?(\d+))+',
                lambda m: self._expand_abbreviated_district_list(m)
            ),
        ]

        for pattern, handler in patterns:
            # Find all matches
            matches = list(re.finditer(pattern, result))

            # Replace from end to start to preserve positions
            for match in reversed(matches):
                expanded = handler(match)
                result = result[:match.start()] + expanded + result[match.end():]

        return result

    def _expand_district_list(self, match: re.Match, prefix: str) -> str:
        """
        Expand a district list match

        Args:
            match: Regex match object
            prefix: District prefix (Quận or District)

        Returns:
            Expanded district list string
        """
        # Get full matched text
        full_text = match.group(0)

        # Extract all numbers
        numbers = re.findall(r'\d+', full_text)

        # Extract separator (comma, or, hoặc, etc.)
        separators = re.findall(r'[,]|\s+(hoặc|or)\s+', full_text)

        # Build expanded list
        parts = []
        for i, num in enumerate(numbers):
            parts.append(f"{prefix} {num}")

            # Add separator if not last item
            if i < len(numbers) - 1:
                if i < len(separators):
                    sep = separators[i].strip() if separators[i].strip() else ', '
                    parts.append(sep)
                else:
                    parts.append(', ')

        return ' '.join(parts)

    def _expand_abbreviated_district_list(self, match: re.Match) -> str:
        """
        Expand abbreviated district list

        Examples:
            "Q1, Q2, Q7" → "Quận 1, Quận 2, Quận 7"
            "D1, D2, D7" → "Quận 1, Quận 2, Quận 7"
            "Q1, 2, 7" → "Quận 1, Quận 2, Quận 7"

        Args:
            match: Regex match object

        Returns:
            Expanded district list string
        """
        # Get full matched text
        full_text = match.group(0)

        # Extract all district codes (Q1, Q2, D1, etc.)
        # Pattern matches Q/D followed by digit
        district_codes = re.findall(r'[QD]?(\d+)', full_text)

        # Build expanded list
        parts = []
        for i, num in enumerate(district_codes):
            parts.append(f"Quận {num}")

            # Add separator if not last item
            if i < len(district_codes) - 1:
                parts.append(", ")

        return ''.join(parts)

    def normalize_with_metadata(self, query: str) -> Dict:
        """
        Normalize query and return metadata

        Args:
            query: Raw user query

        Returns:
            Dictionary with normalized query and extraction hints
        """
        normalized = self.normalize(query)

        # Extract metadata
        metadata = {
            "original": query,
            "normalized": normalized,
            "hints": {
                "has_district_abbr": any(abbr in query for abbr in ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "D1", "D2"]),
                "has_bedroom_abbr": bool(re.search(r'\d+\s*-?\s*BR\b', query, re.IGNORECASE)),
                "has_price_abbr": bool(re.search(r'\d+\s*[BM]\b', query, re.IGNORECASE)),
                "has_multiple_districts": bool(re.search(r'(Quận|District)\s+\d+\s*,\s*\d+', query, re.IGNORECASE)),
                "is_mixed_language": self._is_mixed_language(query),
            }
        }

        return metadata

    def _is_mixed_language(self, query: str) -> bool:
        """
        Check if query contains mixed Vietnamese + English

        Returns:
            True if query has both Vietnamese and English words
        """
        # Check for Vietnamese characters
        has_vietnamese = bool(re.search(r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', query.lower()))

        # Check for English property keywords
        english_keywords = ["apartment", "bedroom", "br", "district", "price", "sqm", "condo"]
        has_english = any(kw in query.lower() for kw in english_keywords)

        return has_vietnamese and has_english


# Singleton instance
_normalizer_instance = None


def get_normalizer() -> QueryNormalizer:
    """Get singleton normalizer instance"""
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = QueryNormalizer()
    return _normalizer_instance


def normalize_query(query: str) -> str:
    """
    Convenience function to normalize a query

    Args:
        query: Raw user query

    Returns:
        Normalized query string
    """
    normalizer = get_normalizer()
    return normalizer.normalize(query)


# Example usage
if __name__ == "__main__":
    normalizer = QueryNormalizer()

    test_queries = [
        "Find apartment Q1",
        "Find 2BR in D7 price under 5B",
        "Apartment 3 BR District 1 price under 20M",
        "Find house in District 1, 2, 7",
        "Need rent house Q2 or Q7",
        "Find land 5000m2 in Q1",
        "2-BR condo Q7 near HCMC",
    ]

    print("Query Normalization Examples (English):\n")
    for query in test_queries:
        result = normalizer.normalize_with_metadata(query)
        try:
            print(f"Original:   {result['original']}")
            print(f"Normalized: {result['normalized']}")
        except UnicodeEncodeError:
            print(f"Original:   {result['original']}")
            print(f"Normalized: [Contains Vietnamese characters - {len(result['normalized'])} chars]")
        print(f"Mixed lang: {result['hints']['is_mixed_language']}")
        print()

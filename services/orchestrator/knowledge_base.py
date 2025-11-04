"""
Knowledge Base Loader - Phase 2
Auto-loads domain knowledge from markdown files (AGENTS.md pattern)
"""
import os
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from shared.models.reasoning import KnowledgeExpansion


class KnowledgeBase:
    """
    Loads and applies domain knowledge for query understanding
    Inspired by Codex's AGENTS.md pattern
    """

    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.property_knowledge = {}
        self.location_knowledge = {}
        self._load_all_knowledge()

    def _load_all_knowledge(self):
        """Load all knowledge files"""
        properties_file = self.knowledge_dir / "PROPERTIES.md"
        locations_file = self.knowledge_dir / "LOCATIONS.md"

        if properties_file.exists():
            self.property_knowledge = self._parse_markdown(properties_file)

        if locations_file.exists():
            self.location_knowledge = self._parse_markdown(locations_file)

    def _parse_markdown(self, file_path: Path) -> Dict[str, Any]:
        """Parse markdown knowledge into structured dict"""
        content = file_path.read_text(encoding="utf-8")

        knowledge = {
            "raw_content": content,
            "sections": {},
            "keywords": self._extract_keywords(content),
            "synonyms": self._extract_synonyms(content),
            "rules": self._extract_rules(content)
        }

        return knowledge

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract important keywords from content"""
        # Simple keyword extraction (can be improved with NLP)
        keyword_pattern = r'\*\*(.*?)\*\*'
        keywords = re.findall(keyword_pattern, content)
        return [kw.lower() for kw in keywords]

    def _extract_synonyms(self, content: str) -> Dict[str, List[str]]:
        """Extract synonym mappings"""
        synonyms = {}

        # Pattern: "keyword: syn1, syn2, syn3"
        synonym_lines = re.findall(r'(.+?):\s*(.+?)(?:\n|$)', content)

        for term, variants in synonym_lines:
            term = term.strip().lower()
            variants_list = [v.strip() for v in variants.split(',')]
            if len(variants_list) > 1:
                synonyms[term] = variants_list

        return synonyms

    def _extract_rules(self, content: str) -> List[str]:
        """Extract expansion rules"""
        rules = []

        # Find "Query Expansion Rules" section
        rules_section = re.search(
            r'## Query Expansion Rules(.*?)(?=##|$)',
            content,
            re.DOTALL
        )

        if rules_section:
            rule_text = rules_section.group(1)
            # Extract numbered rules
            rule_items = re.findall(r'\d+\.\s*\*\*(.*?)\*\*', rule_text)
            rules.extend(rule_items)

        return rules

    async def expand_query(self, query: str) -> KnowledgeExpansion:
        """
        Expand query using domain knowledge (Phase 2)
        """
        # FIX BUG #5: Clean emoji first (before language detection)
        query = self._clean_query(query)

        # FIX BUG #3: Detect and clean mixed-language queries
        languages_detected = self._detect_languages(query)

        if len(languages_detected) > 2:
            # Too many languages mixed - simplify by keeping only Vietnamese and Latin
            cleaned_query = self._extract_main_languages(query)
            reasoning_prefix = f"Detected {len(languages_detected)} languages ({', '.join(languages_detected)}), simplified query to: '{cleaned_query}'"
        else:
            cleaned_query = query
            reasoning_prefix = None

        query_lower = cleaned_query.lower()
        expanded_terms = []
        synonyms_found = {}
        filters = {}
        reasoning_parts = []

        if reasoning_prefix:
            reasoning_parts.append(reasoning_prefix)

        # 1. Property type expansion
        property_expansions = self._expand_property_type(query_lower)
        if property_expansions:
            expanded_terms.extend(property_expansions["terms"])
            filters.update(property_expansions["filters"])
            reasoning_parts.append(property_expansions["reason"])

        # 2. Location expansion
        location_expansions = self._expand_location(query_lower)
        if location_expansions:
            expanded_terms.extend(location_expansions["terms"])
            filters.update(location_expansions["filters"])
            reasoning_parts.append(location_expansions["reason"])

        # 3. Amenity expansion
        amenity_expansions = self._expand_amenities(query_lower)
        if amenity_expansions:
            expanded_terms.extend(amenity_expansions["terms"])
            synonyms_found.update(amenity_expansions["synonyms"])
            reasoning_parts.append(amenity_expansions["reason"])

        # 4. Context-based expansion
        context_expansions = self._expand_context(query_lower)
        if context_expansions:
            expanded_terms.extend(context_expansions["terms"])
            filters.update(context_expansions["filters"])
            reasoning_parts.append(context_expansions["reason"])

        reasoning = " | ".join(reasoning_parts) if reasoning_parts else "No expansions needed"

        return KnowledgeExpansion(
            original_query=query,
            expanded_terms=list(set(expanded_terms)),  # Remove duplicates
            synonyms=synonyms_found,
            filters=filters,
            reasoning=reasoning
        )

    def _expand_property_type(self, query: str) -> Optional[Dict[str, Any]]:
        """Expand property type keywords"""
        # FIX BUG #10C: Remove property_type filters - database doesn't have this field populated
        # Only use terms for text search expansion, not as strict filters
        expansions = {
            "căn hộ": {
                "terms": ["apartment", "condo", "chung cư"],
                "filters": {}  # Empty - property_type not in database
            },
            "biệt thự": {
                "terms": ["villa", "nhà vườn"],
                "filters": {}
            },
            "nhà phố": {
                "terms": ["townhouse", "nhà riêng"],
                "filters": {}
            },
            "đất": {
                "terms": ["land", "đất nền"],
                "filters": {}
            }
        }

        for keyword, expansion in expansions.items():
            if keyword in query:
                return {
                    "terms": expansion["terms"],
                    "filters": expansion["filters"],
                    "reason": f"Expanded '{keyword}' to include {', '.join(expansion['terms'])}"
                }

        return None

    def _expand_location(self, query: str) -> Optional[Dict[str, Any]]:
        """Expand location-based queries"""
        location_patterns = {
            # FIX BUG #7: Expanded international schools with more terms and variations
            "trường quốc tế": {
                "terms": [
                    "international school", "AIS", "BIS", "SSIS", "ISHCMC", "VAS", "Renaissance",
                    "Australian International School", "British International School",
                    "IB School", "American School", "Saigon South"
                ],
                # FIX BUG #10B: District values must match OpenSearch format "Quận X" not "X"
                "filters": {"district": {"$in": ["Quận 2", "Quận 7"]}, "distance_to_school": {"$lte": 2000}},
                "reason": "International schools → Districts 2 & 7, AIS/BIS/SSIS/ISHCMC/VAS, 2km radius"
            },
            "gần trường quốc tế": {
                "terms": [
                    "international school", "AIS", "BIS", "SSIS", "ISHCMC", "VAS", "Renaissance",
                    "Australian International School", "British International School",
                    "IB School", "American School", "Saigon South"
                ],
                # FIX BUG #10B: District values must match OpenSearch format "Quận X" not "X"
                "filters": {"district": {"$in": ["Quận 2", "Quận 7"]}, "distance_to_school": {"$lte": 2000}},
                "reason": "Near international schools → Districts 2 & 7, AIS/BIS/SSIS/ISHCMC/VAS, 2km radius"
            },
            "gần trường": {
                "terms": ["school", "trường học"],
                "filters": {"distance_to_school": {"$lte": 2000}},
                "reason": "Near schools → 2km radius"
            },
            "gần metro": {
                "terms": ["metro", "MRT", "subway"],
                "filters": {"distance_to_metro": {"$lte": 1000}},
                "reason": "Near metro → 1km walking distance"
            },
            "quận 2": {
                "terms": ["District 2", "D2", "Thảo Điền", "An Phú"],
                # FIX BUG #10B: District values must match OpenSearch format "Quận 2" not "2"
                "filters": {"district": "Quận 2"},
                "reason": "District 2 → Include Thao Dien, An Phu areas"
            },
            "quận 7": {
                "terms": ["District 7", "D7", "Phú Mỹ Hưng", "PMH"],
                # FIX BUG #10B: District values must match OpenSearch format "Quận 7" not "7"
                "filters": {"district": "Quận 7"},
                "reason": "District 7 → Include Phu My Hung area"
            }
        }

        for pattern, expansion in location_patterns.items():
            if pattern in query:
                return {
                    "terms": expansion["terms"],
                    "filters": expansion["filters"],
                    "reason": expansion["reason"]
                }

        return None

    def _expand_amenities(self, query: str) -> Optional[Dict[str, Any]]:
        """Expand amenity keywords"""
        amenity_synonyms = {
            "hồ bơi": ["pool", "swimming pool", "bể bơi", "infinity pool"],
            "gym": ["fitness", "phòng gym", "phòng tập", "health club"],
            "chỗ đậu xe": ["parking", "garage", "bãi đỗ xe", "car park"],
            "vườn": ["garden", "sân vườn", "yard", "backyard"],
            "view đẹp": ["nice view", "river view", "city view", "park view"],
            "an ninh": ["security", "24/7 security", "guard", "bảo vệ"]
        }

        found_synonyms = {}

        for amenity, synonyms in amenity_synonyms.items():
            if amenity in query:
                found_synonyms[amenity] = synonyms

        if found_synonyms:
            all_terms = []
            for syns in found_synonyms.values():
                all_terms.extend(syns)

            return {
                "terms": all_terms,
                "synonyms": found_synonyms,
                "reason": f"Expanded amenities: {', '.join(found_synonyms.keys())}"
            }

        return None

    def _expand_context(self, query: str) -> Optional[Dict[str, Any]]:
        """Expand based on contextual phrases"""
        context_patterns = {
            "view đẹp": {
                "terms": ["high floor", "good view"],
                "filters": {"floor": {"$gte": 10}, "direction": {"$in": ["East", "South"]}},
                "reason": "Nice view → High floor (>=10), East/South facing"
            },
            "yên tĩnh": {
                "terms": ["quiet", "peaceful", "low traffic"],
                "filters": {"alley_width": {"$lte": 5}, "gated_community": True},
                "reason": "Quiet area → Small alley, gated community"
            },
            "an ninh tốt": {
                "terms": ["gated community", "24/7 security"],
                "filters": {"security": True, "gated": True},
                "reason": "Good security → Gated with 24/7 guards"
            }
        }

        for pattern, expansion in context_patterns.items():
            if pattern in query:
                return {
                    "terms": expansion["terms"],
                    "filters": expansion["filters"],
                    "reason": expansion["reason"]
                }

        return None

    def get_district_info(self, district: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a district"""
        # Parse location knowledge for district info
        content = self.location_knowledge.get("raw_content", "")

        # Find district section
        district_pattern = rf'## Quận {district}.*?(?=##|$)'
        match = re.search(district_pattern, content, re.DOTALL)

        if match:
            section = match.group(0)
            return {
                "raw_section": section,
                "district": district
            }

        return None

    def get_property_type_attributes(self, property_type: str) -> List[str]:
        """Get common attributes for a property type"""
        attribute_map = {
            "apartment": ["pool", "gym", "security", "view", "parking"],
            "villa": ["garden", "garage", "rooftop", "wine_cellar", "smart_home"],
            "townhouse": ["frontage_width", "floors", "alley_width", "rooftop"],
            "land": ["zoning", "utilities", "road_width"]
        }

        return attribute_map.get(property_type.lower(), [])

    def _detect_languages(self, query: str) -> List[str]:
        """
        FIX BUG #3: Detect languages in query based on character sets
        Returns list of detected languages
        """
        languages = set()

        # Latin characters (English, French, German, etc.)
        if re.search(r'[a-zA-Z]', query):
            languages.add('latin')

        # Vietnamese diacritics
        if re.search(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', query, re.IGNORECASE):
            languages.add('vietnamese')

        # Chinese/Japanese/Korean characters
        if re.search(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', query):
            languages.add('cjk')

        # Cyrillic (Russian, Ukrainian, etc.)
        if re.search(r'[\u0400-\u04FF]', query):
            languages.add('cyrillic')

        # Arabic
        if re.search(r'[\u0600-\u06FF]', query):
            languages.add('arabic')

        return list(languages)

    def _extract_main_languages(self, query: str) -> str:
        """
        FIX BUG #3: Keep only Vietnamese and Latin characters
        Remove Chinese, Cyrillic, Arabic, and other complex scripts
        """
        # Remove CJK characters
        cleaned = re.sub(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]', '', query)

        # Remove Cyrillic
        cleaned = re.sub(r'[\u0400-\u04FF]', '', cleaned)

        # Remove Arabic
        cleaned = re.sub(r'[\u0600-\u06FF]', '', cleaned)

        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()

    def _clean_query(self, query: str) -> str:
        """
        FIX BUG #5: Remove emoji and special unicode characters
        Emoji can slow down LLM processing significantly
        """
        # Remove emoji (most emoji are in these Unicode ranges)
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002702-\U000027B0"  # dingbats
            u"\U000024C2-\U0001F251"  # enclosed characters
            u"\U0001F900-\U0001F9FF"  # supplemental symbols
            u"\U0001FA00-\U0001FA6F"  # chess symbols
            "]+",
            flags=re.UNICODE
        )
        cleaned = emoji_pattern.sub(r'', query)

        # Clean up extra spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)

        return cleaned.strip()

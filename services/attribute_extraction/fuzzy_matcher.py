"""
Fuzzy Matching Service with PostgreSQL Master Data
Matches user input against master data with translations
"""
from typing import Optional, Dict, Any, List
import asyncpg
from fuzzywuzzy import fuzz
from shared.utils.logger import setup_logger, LogEmoji
from shared.config import settings


class FuzzyMatcher:
    """
    Fuzzy matching against PostgreSQL master data with multi-language support
    """

    def __init__(self):
        self.logger = setup_logger("fuzzy_matcher")
        self.db_pool: Optional[asyncpg.Pool] = None

    async def initialize(self):
        """Initialize PostgreSQL connection pool"""
        try:
            self.db_pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                min_size=2,
                max_size=10
            )
            self.logger.info(f"{LogEmoji.SUCCESS} Fuzzy matcher connected to PostgreSQL")
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to connect to PostgreSQL: {e}")
            raise

    async def close(self):
        """Close database connection pool"""
        if self.db_pool:
            await self.db_pool.close()

    async def match_district(
        self,
        value: str,
        source_language: str = 'vi',
        threshold: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """
        Match district against master data with translations

        Args:
            value: User input (e.g., "Q1", "Quận 1", "District 1")
            source_language: Language of input
            threshold: Minimum similarity score (0.0 to 1.0)

        Returns:
            Match result or None:
            {
                "id": 1,
                "code": "district_1",
                "name_en": "District 1",
                "name_vi": "Quận 1",
                "confidence": 0.95,
                "match_method": "exact" | "fuzzy"
            }
        """
        if not self.db_pool:
            await self.initialize()

        try:
            async with self.db_pool.acquire() as conn:
                # Query districts with translations
                query = """
                    SELECT
                        d.id,
                        d.code,
                        d.name as name_en,
                        dt.translated_text as name_translated
                    FROM districts d
                    LEFT JOIN districts_translations dt
                        ON d.id = dt.district_id
                        AND dt.lang_code = $1
                    WHERE d.city_id = (SELECT id FROM cities WHERE code = 'hcmc')
                """

                rows = await conn.fetch(query, source_language)

                if not rows:
                    return None

                # Try exact match first (case-insensitive)
                value_lower = value.lower().strip()
                for row in rows:
                    name_en = row['name_en'].lower()
                    name_translated = row['name_translated'].lower() if row['name_translated'] else ''

                    if value_lower == name_en or value_lower == name_translated:
                        return {
                            "id": row['id'],
                            "code": row['code'],
                            "name_en": row['name_en'],
                            "name_translated": row['name_translated'],
                            "confidence": 1.0,
                            "match_method": "exact"
                        }

                # Fuzzy match
                best_match = None
                best_score = 0.0

                for row in rows:
                    name_en = row['name_en']
                    name_translated = row['name_translated'] if row['name_translated'] else name_en

                    # Calculate similarity against both English and translated name
                    score_en = fuzz.ratio(value_lower, name_en.lower()) / 100.0
                    score_translated = fuzz.ratio(value_lower, name_translated.lower()) / 100.0

                    # Take the best score
                    score = max(score_en, score_translated)

                    if score > best_score:
                        best_score = score
                        best_match = row

                if best_score >= threshold and best_match:
                    return {
                        "id": best_match['id'],
                        "code": best_match['code'],
                        "name_en": best_match['name_en'],
                        "name_translated": best_match['name_translated'],
                        "confidence": best_score,
                        "match_method": "fuzzy"
                    }

                return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} District matching failed: {e}")
            return None

    async def match_property_type(
        self,
        value: str,
        source_language: str = 'vi',
        threshold: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """Match property type against master data"""
        if not self.db_pool:
            await self.initialize()

        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT
                        pt.id,
                        pt.code,
                        pt.name as name_en,
                        ptt.translated_text as name_translated
                    FROM property_types pt
                    LEFT JOIN property_types_translations ptt
                        ON pt.id = ptt.property_type_id
                        AND ptt.lang_code = $1
                """

                rows = await conn.fetch(query, source_language)

                if not rows:
                    return None

                # Exact match
                value_lower = value.lower().strip()
                for row in rows:
                    name_en = row['name_en'].lower()
                    name_translated = row['name_translated'].lower() if row['name_translated'] else ''

                    if value_lower == name_en or value_lower == name_translated:
                        return {
                            "id": row['id'],
                            "code": row['code'],
                            "name_en": row['name_en'],
                            "name_translated": row['name_translated'],
                            "confidence": 1.0,
                            "match_method": "exact"
                        }

                # Fuzzy match
                best_match = None
                best_score = 0.0

                for row in rows:
                    name_en = row['name_en']
                    name_translated = row['name_translated'] if row['name_translated'] else name_en

                    score_en = fuzz.ratio(value_lower, name_en.lower()) / 100.0
                    score_translated = fuzz.ratio(value_lower, name_translated.lower()) / 100.0

                    score = max(score_en, score_translated)

                    if score > best_score:
                        best_score = score
                        best_match = row

                if best_score >= threshold and best_match:
                    return {
                        "id": best_match['id'],
                        "code": best_match['code'],
                        "name_en": best_match['name_en'],
                        "name_translated": best_match['name_translated'],
                        "confidence": best_score,
                        "match_method": "fuzzy"
                    }

                return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Property type matching failed: {e}")
            return None

    async def match_amenity(
        self,
        value: str,
        source_language: str = 'vi',
        threshold: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """Match amenity against master data"""
        if not self.db_pool:
            await self.initialize()

        try:
            async with self.db_pool.acquire() as conn:
                query = """
                    SELECT
                        a.id,
                        a.code,
                        a.name as name_en,
                        a.category,
                        at.translated_text as name_translated
                    FROM amenities a
                    LEFT JOIN amenities_translations at
                        ON a.id = at.amenity_id
                        AND at.lang_code = $1
                """

                rows = await conn.fetch(query, source_language)

                if not rows:
                    return None

                # Exact match
                value_lower = value.lower().strip()
                for row in rows:
                    name_en = row['name_en'].lower()
                    name_translated = row['name_translated'].lower() if row['name_translated'] else ''

                    if value_lower == name_en or value_lower == name_translated:
                        return {
                            "id": row['id'],
                            "code": row['code'],
                            "name_en": row['name_en'],
                            "name_translated": row['name_translated'],
                            "category": row['category'],
                            "confidence": 1.0,
                            "match_method": "exact"
                        }

                # Fuzzy match
                best_match = None
                best_score = 0.0

                for row in rows:
                    name_en = row['name_en']
                    name_translated = row['name_translated'] if row['name_translated'] else name_en

                    score_en = fuzz.ratio(value_lower, name_en.lower()) / 100.0
                    score_translated = fuzz.ratio(value_lower, name_translated.lower()) / 100.0

                    score = max(score_en, score_translated)

                    if score > best_score:
                        best_score = score
                        best_match = row

                if best_score >= threshold and best_match:
                    return {
                        "id": best_match['id'],
                        "code": best_match['code'],
                        "name_en": best_match['name_en'],
                        "name_translated": best_match['name_translated'],
                        "category": best_match['category'],
                        "confidence": best_score,
                        "match_method": "fuzzy"
                    }

                return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Amenity matching failed: {e}")
            return None

    async def match_generic(
        self,
        table: str,
        value: str,
        source_language: str = 'vi',
        threshold: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """
        Generic fuzzy matching for any master data table

        Args:
            table: Table name (e.g., 'directions', 'furniture_types', 'legal_statuses')
            value: User input
            source_language: Language code
            threshold: Minimum similarity

        Returns:
            Match result or None
        """
        if not self.db_pool:
            await self.initialize()

        # Map table names to FK field names
        fk_field_mapping = {
            'directions': 'direction_id',
            'furniture_types': 'furniture_type_id',
            'legal_statuses': 'legal_status_id',
            'view_types': 'view_type_id'
        }

        fk_field = fk_field_mapping.get(table)
        if not fk_field:
            self.logger.warning(f"{LogEmoji.WARNING} Unknown table: {table}")
            return None

        try:
            async with self.db_pool.acquire() as conn:
                # Build dynamic query
                translation_table = f"{table}_translations"
                singular_table = table.rstrip('s')  # Remove trailing 's'

                query = f"""
                    SELECT
                        m.id,
                        m.code,
                        m.name as name_en,
                        t.translated_text as name_translated
                    FROM {table} m
                    LEFT JOIN {translation_table} t
                        ON m.id = t.{fk_field}
                        AND t.lang_code = $1
                """

                rows = await conn.fetch(query, source_language)

                if not rows:
                    return None

                # Exact match
                value_lower = value.lower().strip()
                for row in rows:
                    name_en = row['name_en'].lower()
                    name_translated = row['name_translated'].lower() if row['name_translated'] else ''

                    if value_lower == name_en or value_lower == name_translated:
                        return {
                            "id": row['id'],
                            "code": row['code'],
                            "name_en": row['name_en'],
                            "name_translated": row['name_translated'],
                            "confidence": 1.0,
                            "match_method": "exact"
                        }

                # Fuzzy match
                best_match = None
                best_score = 0.0

                for row in rows:
                    name_en = row['name_en']
                    name_translated = row['name_translated'] if row['name_translated'] else name_en

                    score_en = fuzz.ratio(value_lower, name_en.lower()) / 100.0
                    score_translated = fuzz.ratio(value_lower, name_translated.lower()) / 100.0

                    score = max(score_en, score_translated)

                    if score > best_score:
                        best_score = score
                        best_match = row

                if best_score >= threshold and best_match:
                    return {
                        "id": best_match['id'],
                        "code": best_match['code'],
                        "name_en": best_match['name_en'],
                        "name_translated": best_match['name_translated'],
                        "confidence": best_score,
                        "match_method": "fuzzy"
                    }

                return None

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Generic matching failed for {table}: {e}")
            return None

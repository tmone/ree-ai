"""
Master Data Repository
Handles PostgreSQL operations for master data tables
"""
import asyncpg
from typing import List, Optional, Dict, Any
from shared.models.master_data import (
    MasterDistrict,
    MasterPropertyType,
    MasterAmenity,
    MasterFurnitureType,
    MasterDirection,
    MasterLegalStatus,
    MasterPriceRange,
    NormalizedEntity,
    ValidationResult
)
from shared.config import settings
from shared.utils.logger import logger, LogEmoji


class MasterDataRepository:
    """Repository for master data operations"""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logger

    async def connect(self):
        """Create database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                min_size=2,
                max_size=10
            )
            self.logger.info(f"{LogEmoji.SUCCESS} Connected to PostgreSQL master data")
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to connect to PostgreSQL: {e}")
            raise

    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            self.logger.info(f"{LogEmoji.INFO} Disconnected from PostgreSQL")

    # ============================================================
    # DISTRICT OPERATIONS
    # ============================================================

    async def get_all_districts(self, active_only: bool = True) -> List[MasterDistrict]:
        """Get all districts"""
        query = "SELECT * FROM master_districts"
        if active_only:
            query += " WHERE active = TRUE"
        query += " ORDER BY sort_order, name_vi"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [MasterDistrict(**dict(row)) for row in rows]

    async def normalize_district(self, input_text: str) -> Optional[NormalizedEntity]:
        """
        Normalize district name using aliases and fuzzy matching
        Returns normalized entity or None if not found
        """
        input_text = input_text.strip().lower()

        # Try exact match on code
        query = """
        SELECT code, name_vi, name_en
        FROM master_districts
        WHERE active = TRUE AND LOWER(code) = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, input_text)
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=1.0,
                    match_type="exact"
                )

        # Try alias match
        query = """
        SELECT code, name_vi, name_en
        FROM master_districts
        WHERE active = TRUE AND $1 = ANY(SELECT LOWER(unnest(aliases)))
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, input_text)
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=0.95,
                    match_type="alias"
                )

        # Try fuzzy match on name_vi (case-insensitive LIKE)
        query = """
        SELECT code, name_vi, name_en
        FROM master_districts
        WHERE active = TRUE AND LOWER(name_vi) LIKE $1
        LIMIT 1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, f"%{input_text}%")
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=0.85,
                    match_type="fuzzy"
                )

        return None

    # ============================================================
    # PROPERTY TYPE OPERATIONS
    # ============================================================

    async def get_all_property_types(self, active_only: bool = True) -> List[MasterPropertyType]:
        """Get all property types"""
        query = "SELECT * FROM master_property_types"
        if active_only:
            query += " WHERE active = TRUE"
        query += " ORDER BY sort_order, name_vi"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [MasterPropertyType(**dict(row)) for row in rows]

    async def normalize_property_type(self, input_text: str) -> Optional[NormalizedEntity]:
        """Normalize property type using aliases"""
        input_text = input_text.strip().lower()

        # Try exact match on code
        query = """
        SELECT code, name_vi, name_en
        FROM master_property_types
        WHERE active = TRUE AND LOWER(code) = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, input_text)
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=1.0,
                    match_type="exact"
                )

        # Try alias match
        query = """
        SELECT code, name_vi, name_en
        FROM master_property_types
        WHERE active = TRUE AND $1 = ANY(SELECT LOWER(unnest(aliases)))
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, input_text)
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=0.95,
                    match_type="alias"
                )

        return None

    # ============================================================
    # AMENITY OPERATIONS
    # ============================================================

    async def get_all_amenities(self, category: Optional[str] = None, active_only: bool = True) -> List[MasterAmenity]:
        """Get all amenities, optionally filtered by category"""
        query = "SELECT * FROM master_amenities WHERE 1=1"
        params = []

        if active_only:
            query += " AND active = TRUE"

        if category:
            query += f" AND category = ${len(params) + 1}"
            params.append(category)

        query += " ORDER BY sort_order, name_vi"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [MasterAmenity(**dict(row)) for row in rows]

    async def normalize_amenity(self, input_text: str) -> Optional[NormalizedEntity]:
        """Normalize amenity using aliases"""
        input_text = input_text.strip().lower()

        # Try exact match on code
        query = """
        SELECT code, name_vi, name_en
        FROM master_amenities
        WHERE active = TRUE AND LOWER(code) = $1
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, input_text)
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=1.0,
                    match_type="exact"
                )

        # Try alias match
        query = """
        SELECT code, name_vi, name_en
        FROM master_amenities
        WHERE active = TRUE AND $1 = ANY(SELECT LOWER(unnest(aliases)))
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, input_text)
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=0.95,
                    match_type="alias"
                )

        return None

    # ============================================================
    # FURNITURE TYPE OPERATIONS
    # ============================================================

    async def normalize_furniture(self, input_text: str) -> Optional[NormalizedEntity]:
        """Normalize furniture type using aliases"""
        input_text = input_text.strip().lower()

        # Try alias match
        query = """
        SELECT code, name_vi, name_en
        FROM master_furniture_types
        WHERE active = TRUE AND $1 = ANY(SELECT LOWER(unnest(aliases)))
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, input_text)
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=0.95,
                    match_type="alias"
                )

        return None

    # ============================================================
    # DIRECTION OPERATIONS
    # ============================================================

    async def normalize_direction(self, input_text: str) -> Optional[NormalizedEntity]:
        """Normalize direction using aliases"""
        input_text = input_text.strip().lower()

        # Try alias match
        query = """
        SELECT code, name_vi, name_en
        FROM master_directions
        WHERE active = TRUE AND $1 = ANY(SELECT LOWER(unnest(aliases)))
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, input_text)
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=0.95,
                    match_type="alias"
                )

        return None

    # ============================================================
    # LEGAL STATUS OPERATIONS
    # ============================================================

    async def normalize_legal_status(self, input_text: str) -> Optional[NormalizedEntity]:
        """Normalize legal status using aliases"""
        input_text = input_text.strip().lower()

        # Try alias match
        query = """
        SELECT code, name_vi, name_en
        FROM master_legal_status
        WHERE active = TRUE AND $1 = ANY(SELECT LOWER(unnest(aliases)))
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, input_text)
            if row:
                return NormalizedEntity(
                    original_value=input_text,
                    normalized_code=row['code'],
                    normalized_name_vi=row['name_vi'],
                    normalized_name_en=row['name_en'],
                    confidence=0.95,
                    match_type="alias"
                )

        return None

    # ============================================================
    # PRICE RANGE VALIDATION
    # ============================================================

    async def get_price_range(self, district_code: str, property_type_code: str) -> Optional[MasterPriceRange]:
        """Get price range for district and property type"""
        query = """
        SELECT pr.*
        FROM master_price_ranges pr
        JOIN master_districts d ON pr.district_id = d.id
        JOIN master_property_types pt ON pr.property_type_id = pt.id
        WHERE d.code = $1 AND pt.code = $2 AND pr.active = TRUE
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, district_code, property_type_code)
            if row:
                return MasterPriceRange(**dict(row))
        return None

    async def validate_price(
        self,
        price: float,
        area: Optional[float],
        district_code: str,
        property_type_code: str
    ) -> ValidationResult:
        """
        Validate price against typical ranges for district and property type
        Returns warnings if price is unusual
        """
        price_range = await self.get_price_range(district_code, property_type_code)

        warnings = []
        is_valid = True

        if not price_range:
            warnings.append(f"No price data available for {district_code} - {property_type_code}")
            return ValidationResult(
                field_name="price",
                original_value=price,
                is_valid=True,  # Can't validate without data
                warnings=warnings
            )

        # Check total price
        if price_range.min_total_price and price < price_range.min_total_price * 0.5:
            warnings.append(
                f"Price {price:,.0f} VND is significantly lower than typical "
                f"({price_range.min_total_price:,.0f} - {price_range.max_total_price:,.0f})"
            )

        if price_range.max_total_price and price > price_range.max_total_price * 2:
            warnings.append(
                f"Price {price:,.0f} VND is significantly higher than typical "
                f"({price_range.min_total_price:,.0f} - {price_range.max_total_price:,.0f})"
            )

        # Check price per m2 if area provided
        if area and area > 0:
            price_per_m2 = price / area

            if price_range.min_price_per_m2 and price_per_m2 < price_range.min_price_per_m2 * 0.5:
                warnings.append(
                    f"Price per m² {price_per_m2:,.0f} VND/m² is significantly lower than typical "
                    f"({price_range.min_price_per_m2:,.0f} - {price_range.max_price_per_m2:,.0f})"
                )

            if price_range.max_price_per_m2 and price_per_m2 > price_range.max_price_per_m2 * 2:
                warnings.append(
                    f"Price per m² {price_per_m2:,.0f} VND/m² is significantly higher than typical "
                    f"({price_range.min_price_per_m2:,.0f} - {price_range.max_price_per_m2:,.0f})"
                )

        return ValidationResult(
            field_name="price",
            original_value=price,
            is_valid=len(warnings) == 0,
            warnings=warnings
        )

    async def validate_area(self, area: float, property_type_code: str) -> ValidationResult:
        """Validate area against typical ranges for property type"""
        query = """
        SELECT typical_min_area, typical_max_area, name_vi
        FROM master_property_types
        WHERE code = $1 AND active = TRUE
        """

        warnings = []

        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, property_type_code)

            if not row:
                warnings.append(f"Unknown property type: {property_type_code}")
                return ValidationResult(
                    field_name="area",
                    original_value=area,
                    is_valid=False,
                    warnings=warnings
                )

            min_area = row['typical_min_area']
            max_area = row['typical_max_area']
            name_vi = row['name_vi']

            if min_area and area < min_area * 0.5:
                warnings.append(
                    f"Area {area}m² is significantly smaller than typical {name_vi} "
                    f"({min_area}m² - {max_area}m²)"
                )

            if max_area and area > max_area * 2:
                warnings.append(
                    f"Area {area}m² is significantly larger than typical {name_vi} "
                    f"({min_area}m² - {max_area}m²)"
                )

        return ValidationResult(
            field_name="area",
            original_value=area,
            is_valid=len(warnings) == 0,
            warnings=warnings
        )

    # ============================================================
    # BATCH NORMALIZATION
    # ============================================================

    async def normalize_entities(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize all entities in extracted data using master data
        Returns normalized entities dict with standardized codes
        """
        normalized = {}

        # Normalize district
        if "district" in entities and entities["district"]:
            district_norm = await self.normalize_district(entities["district"])
            if district_norm:
                normalized["district"] = district_norm.normalized_code
                normalized["district_name_vi"] = district_norm.normalized_name_vi
                normalized["district_name_en"] = district_norm.normalized_name_en
            else:
                normalized["district"] = entities["district"]  # Keep original if not found

        # Normalize property_type
        if "property_type" in entities and entities["property_type"]:
            prop_type_norm = await self.normalize_property_type(entities["property_type"])
            if prop_type_norm:
                normalized["property_type"] = prop_type_norm.normalized_code
                normalized["property_type_name_vi"] = prop_type_norm.normalized_name_vi
                normalized["property_type_name_en"] = prop_type_norm.normalized_name_en
            else:
                normalized["property_type"] = entities["property_type"]

        # Normalize furniture
        if "furniture" in entities and entities["furniture"]:
            furniture_norm = await self.normalize_furniture(entities["furniture"])
            if furniture_norm:
                normalized["furniture"] = furniture_norm.normalized_code
            else:
                normalized["furniture"] = entities["furniture"]

        # Normalize direction
        if "direction" in entities and entities["direction"]:
            direction_norm = await self.normalize_direction(entities["direction"])
            if direction_norm:
                normalized["direction"] = direction_norm.normalized_code
            else:
                normalized["direction"] = entities["direction"]

        # Normalize legal_status
        if "legal_status" in entities and entities["legal_status"]:
            legal_norm = await self.normalize_legal_status(entities["legal_status"])
            if legal_norm:
                normalized["legal_status"] = legal_norm.normalized_code
            else:
                normalized["legal_status"] = entities["legal_status"]

        # Copy other fields as-is
        for key, value in entities.items():
            if key not in normalized:
                normalized[key] = value

        return normalized


# Singleton instance
_master_data_repo: Optional[MasterDataRepository] = None


async def get_master_data_repository() -> MasterDataRepository:
    """Get or create master data repository singleton"""
    global _master_data_repo
    if _master_data_repo is None:
        _master_data_repo = MasterDataRepository()
        await _master_data_repo.connect()
    return _master_data_repo

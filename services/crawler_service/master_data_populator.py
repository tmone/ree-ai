"""
Master Data Populator
Extracts new attributes from crawled listings and populates pending_master_data
"""
import asyncpg
from typing import List, Dict, Any, Set
from collections import Counter
from shared.utils.logger import logger, LogEmoji
from shared.config import settings


class MasterDataPopulator:
    """
    Analyzes crawled listings to discover new master data

    Process:
    1. Extract all unique values for each attribute type
    2. Check against existing master data
    3. Store new items in pending_master_data for admin review
    4. Track frequency for prioritization
    """

    def __init__(self):
        self.logger = logger
        self.db_pool: asyncpg.Pool = None

    async def initialize(self):
        """Initialize PostgreSQL connection"""
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
            self.logger.info(f"{LogEmoji.SUCCESS} Master data populator connected to PostgreSQL")
        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to connect to PostgreSQL: {e}")
            raise

    async def close(self):
        """Close database connection"""
        if self.db_pool:
            await self.db_pool.close()

    async def extract_new_attributes(
        self,
        listings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract new attributes from crawled listings

        Args:
            listings: List of parsed listings

        Returns:
            List of new attributes discovered
        """
        self.logger.info(
            f"{LogEmoji.AI} Analyzing {len(listings)} listings for new attributes..."
        )

        # Collect all values for each attribute type
        districts = Counter()
        wards = Counter()
        amenities = Counter()
        directions = Counter()
        furniture_types = Counter()

        for listing in listings:
            # Collect districts
            if listing.get('district'):
                districts[listing['district']] += 1

            # Collect wards
            if listing.get('ward'):
                wards[listing['ward']] += 1

            # Collect amenities
            if listing.get('amenities'):
                for amenity in listing['amenities']:
                    amenities[amenity] += 1

            # Collect directions
            if listing.get('direction'):
                directions[listing['direction']] += 1

            # Collect furniture
            if listing.get('furniture'):
                furniture_types[listing['furniture']] += 1

        # Check against existing master data
        new_attributes = []

        # Check districts
        new_districts = await self._find_new_items('districts', list(districts.keys()))
        for district, freq in districts.items():
            if district in new_districts:
                new_attributes.append({
                    'property_name': 'district',
                    'value': district,
                    'value_original': district,
                    'suggested_table': 'districts',
                    'frequency': freq
                })

        # Check wards
        new_wards = await self._find_new_items('wards', list(wards.keys()))
        for ward, freq in wards.items():
            if ward in new_wards:
                new_attributes.append({
                    'property_name': 'ward',
                    'value': ward,
                    'value_original': ward,
                    'suggested_table': 'wards',
                    'frequency': freq
                })

        # Check amenities
        new_amenities = await self._find_new_items('amenities', list(amenities.keys()))
        for amenity, freq in amenities.items():
            if amenity in new_amenities:
                new_attributes.append({
                    'property_name': 'amenity',
                    'value': amenity,
                    'value_original': amenity,
                    'suggested_table': 'amenities',
                    'suggested_category': self._guess_amenity_category(amenity),
                    'frequency': freq
                })

        # Check directions
        new_directions = await self._find_new_items('directions', list(directions.keys()))
        for direction, freq in directions.items():
            if direction in new_directions:
                new_attributes.append({
                    'property_name': 'direction',
                    'value': direction,
                    'value_original': direction,
                    'suggested_table': 'directions',
                    'frequency': freq
                })

        # Check furniture types
        new_furniture = await self._find_new_items('furniture_types', list(furniture_types.keys()))
        for furniture, freq in furniture_types.items():
            if furniture in new_furniture:
                new_attributes.append({
                    'property_name': 'furniture_type',
                    'value': furniture,
                    'value_original': furniture,
                    'suggested_table': 'furniture_types',
                    'frequency': freq
                })

        # Sort by frequency (highest first)
        new_attributes.sort(key=lambda x: x['frequency'], reverse=True)

        self.logger.info(
            f"{LogEmoji.SUCCESS} Discovered {len(new_attributes)} new attributes "
            f"(districts: {len(new_districts)}, wards: {len(new_wards)}, "
            f"amenities: {len(new_amenities)})"
        )

        return new_attributes

    async def _find_new_items(self, table: str, values: List[str]) -> Set[str]:
        """
        Find values that don't exist in master data

        Args:
            table: Master data table name
            values: List of values to check

        Returns:
            Set of values not in master data
        """
        if not values or not self.db_pool:
            return set()

        try:
            async with self.db_pool.acquire() as conn:
                # Get existing values from master data
                query = f"SELECT name, code FROM {table}"
                rows = await conn.fetch(query)

                existing_values = set()
                for row in rows:
                    existing_values.add(row['name'].lower())
                    existing_values.add(row['code'].lower())

                # Also check translations
                translation_table = f"{table}_translations"
                try:
                    trans_query = f"SELECT translated_text FROM {translation_table}"
                    trans_rows = await conn.fetch(trans_query)
                    for row in trans_rows:
                        if row['translated_text']:
                            existing_values.add(row['translated_text'].lower())
                except Exception:
                    pass  # Translation table might not exist

                # Find new values
                new_values = set()
                for value in values:
                    if value and value.lower() not in existing_values:
                        new_values.add(value)

                return new_values

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Error finding new items in {table}: {e}")
            return set()

    async def populate_pending_master_data(
        self,
        new_attributes: List[Dict[str, Any]]
    ) -> int:
        """
        Store new attributes in pending_master_data table

        Args:
            new_attributes: List of new attributes to store

        Returns:
            Number of items successfully stored
        """
        if not new_attributes or not self.db_pool:
            return 0

        stored_count = 0

        try:
            async with self.db_pool.acquire() as conn:
                for attr in new_attributes:
                    try:
                        # Check if already exists
                        existing = await conn.fetchval(
                            """
                            SELECT id FROM pending_master_data
                            WHERE value = $1 AND property_name = $2 AND status = 'pending'
                            """,
                            attr['value'],
                            attr['property_name']
                        )

                        if existing:
                            # Update frequency
                            await conn.execute(
                                """
                                UPDATE pending_master_data
                                SET frequency = frequency + $1,
                                    updated_at = NOW()
                                WHERE id = $2
                                """,
                                attr['frequency'],
                                existing
                            )
                            stored_count += 1
                        else:
                            # Insert new
                            await conn.execute(
                                """
                                INSERT INTO pending_master_data (
                                    property_name,
                                    value,
                                    value_original,
                                    suggested_table,
                                    suggested_category,
                                    extraction_context,
                                    frequency,
                                    status
                                ) VALUES ($1, $2, $3, $4, $5, $6, $7, 'pending')
                                """,
                                attr['property_name'],
                                attr['value'],
                                attr['value_original'],
                                attr['suggested_table'],
                                attr.get('suggested_category'),
                                f"Auto-discovered from web crawling",
                                attr['frequency']
                            )
                            stored_count += 1

                    except Exception as e:
                        self.logger.error(f"{LogEmoji.ERROR} Error storing attribute: {e}")
                        continue

            self.logger.info(
                f"{LogEmoji.SUCCESS} Stored {stored_count} items in pending_master_data"
            )
            return stored_count

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Error populating pending_master_data: {e}")
            return 0

    def _guess_amenity_category(self, amenity: str) -> str:
        """Guess category for amenity"""
        amenity_lower = amenity.lower()

        if any(k in amenity_lower for k in ['pool', 'gym', 'tennis', 'playground', 'bbq', 'garden']):
            return 'shared_amenity'
        elif any(k in amenity_lower for k in ['balcony', 'terrace', 'wine_cellar', 'home_theater']):
            return 'private_amenity'
        elif any(k in amenity_lower for k in ['school', 'hospital', 'mall', 'metro', 'park']):
            return 'nearby_facility'
        else:
            return 'general'

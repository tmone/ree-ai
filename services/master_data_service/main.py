"""
Master Data Management Service
Purpose: Manage multilingual master data, crawl updates, provide lookup APIs
Integrates with: Extraction Service, Crawler Service, DB Gateway
"""
import asyncio
import os
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, BackgroundTasks
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

from core.base_service import BaseService
from shared.utils.logger import LogEmoji
from shared.config import settings


class MasterDataLookupRequest(BaseModel):
    """Request for master data lookup"""
    text: str
    data_type: str  # 'district', 'property_type', 'amenity', 'view', etc.
    language: str = 'vi'  # 'vi' or 'en'
    fuzzy_match: bool = True


class MasterDataLookupResponse(BaseModel):
    """Response with master data matches"""
    matches: List[Dict[str, Any]]
    confidence: float
    matched_aliases: List[str]


class CrawlMasterDataRequest(BaseModel):
    """Request to crawl and update master data"""
    sources: List[str] = ['batdongsan', 'mogi', 'nhatot']
    data_types: List[str] = ['districts', 'projects', 'developers', 'streets']
    auto_approve: bool = False  # If True, auto-add to master data


class MasterDataService(BaseService):
    """
    Master Data Management Service
    Provides:
    - Multilingual lookup APIs for extraction service
    - Continuous master data updates from crawlers
    - Admin APIs for master data CRUD
    - Data quality monitoring
    """

    def __init__(self):
        super().__init__(
            name="master_data_service",
            version="1.0.0",
            capabilities=[
                "master_data_lookup",
                "fuzzy_matching",
                "multilingual_support",
                "auto_crawler",
                "data_quality_monitoring"
            ],
            port=8095
        )

        # Database connection
        self.db_config = {
            'host': settings.POSTGRES_HOST,
            'port': settings.POSTGRES_PORT,
            'database': settings.POSTGRES_DB,
            'user': settings.POSTGRES_USER,
            'password': settings.POSTGRES_PASSWORD
        }

        # HTTP client for calling other services
        self.http_client = httpx.AsyncClient(timeout=60.0)
        # Service URLs with default ports
        crawler_port = os.getenv("CRAWLER_PORT", "8092")
        extraction_port = os.getenv("EXTRACTION_PORT", "8084")
        self.crawler_url = f"http://crawler:{crawler_port}"
        self.extraction_url = f"http://attribute-extraction:{extraction_port}"

        # Cache for frequently accessed master data
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour

        self.logger.info(f"{LogEmoji.SUCCESS} Master Data Service initialized")

    def get_db_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(**self.db_config, cursor_factory=RealDictCursor)

    def setup_routes(self):
        """Setup API routes"""

        @self.app.get("/master-data/{data_type}")
        async def get_master_data(
            data_type: str,
            language: str = 'vi',
            active_only: bool = True
        ):
            """
            Get all master data for a type

            Supported types:
            - districts, cities, property_types, amenities
            - views, directions, legal_status, furniture_types
            - developers, projects, streets
            """
            try:
                table_map = {
                    'districts': 'master_districts',
                    'cities': 'master_cities',
                    'property_types': 'master_property_types',
                    'amenities': 'master_amenities',
                    'views': 'master_views',
                    'directions': 'master_directions',
                    'legal_status': 'master_legal_status',
                    'furniture_types': 'master_furniture_types',
                    'developers': 'master_developers',
                    'projects': 'master_projects',
                    'streets': 'master_streets',
                    'transaction_types': 'master_transaction_types',
                    'property_conditions': 'master_property_conditions'
                }

                if data_type not in table_map:
                    raise HTTPException(400, f"Invalid data_type: {data_type}")

                table = table_map[data_type]
                name_col = f"name_{language}" if language in ['vi', 'en'] else 'name_en'

                # Check cache first
                cache_key = f"{data_type}_{language}_{active_only}"
                if cache_key in self.cache:
                    cache_entry = self.cache[cache_key]
                    if datetime.now() - cache_entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                        self.logger.info(f"{LogEmoji.SUCCESS} Cache hit for {cache_key}")
                        return cache_entry['data']

                # Query database
                conn = self.get_db_connection()
                cur = conn.cursor()

                active_clause = "AND active = TRUE" if active_only else ""
                query = f"""
                    SELECT
                        id, code, {name_col} as name, name_en, name_vi, aliases
                    FROM {table}
                    WHERE 1=1 {active_clause}
                    ORDER BY sort_order, popularity_rank, {name_col}
                """

                cur.execute(query)
                results = cur.fetchall()
                cur.close()
                conn.close()

                # Cache result
                self.cache[cache_key] = {
                    'data': results,
                    'timestamp': datetime.now()
                }

                self.logger.info(f"{LogEmoji.SUCCESS} Retrieved {len(results)} {data_type}")
                return results

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Error getting master data: {e}")
                raise HTTPException(500, str(e))

        @self.app.post("/lookup")
        async def lookup_master_data(request: MasterDataLookupRequest):
            """
            Lookup master data with fuzzy matching

            Example:
                {
                    "text": "can ho chung cu",
                    "data_type": "property_type",
                    "language": "vi",
                    "fuzzy_match": true
                }

            Returns:
                {
                    "matches": [
                        {
                            "id": 1,
                            "code": "apartment",
                            "name": "Căn hộ chung cư",
                            "confidence": 0.95
                        }
                    ],
                    "confidence": 0.95,
                    "matched_aliases": ["căn hộ", "chung cư"]
                }
            """
            try:
                table_map = {
                    'district': 'master_districts',
                    'city': 'master_cities',
                    'property_type': 'master_property_types',
                    'amenity': 'master_amenities',
                    'view': 'master_views',
                    'direction': 'master_directions',
                    'developer': 'master_developers',
                    'project': 'master_projects',
                    'street': 'master_streets',
                    'legal_status': 'master_legal_status',
                    'furniture_type': 'master_furniture_types',
                    'condition': 'master_property_conditions'
                }

                if request.data_type not in table_map:
                    raise HTTPException(400, f"Invalid data_type: {request.data_type}")

                table = table_map[request.data_type]
                text = request.text.lower().strip()

                conn = self.get_db_connection()
                cur = conn.cursor()

                # Try exact match first (in aliases array)
                query = f"""
                    SELECT
                        id, code, name_en, name_vi, aliases,
                        CASE
                            WHEN LOWER(name_{request.language}) = %s THEN 1.0
                            WHEN %s = ANY(aliases) THEN 0.95
                            ELSE 0.0
                        END as confidence
                    FROM {table}
                    WHERE active = TRUE
                        AND (
                            LOWER(name_{request.language}) = %s
                            OR %s = ANY(aliases)
                            OR (LOWER(name_{request.language}) LIKE %s AND %s = TRUE)
                        )
                    ORDER BY confidence DESC
                    LIMIT 5
                """

                like_pattern = f"%{text}%"
                cur.execute(query, (text, text, text, text, like_pattern, request.fuzzy_match))
                results = cur.fetchall()
                cur.close()
                conn.close()

                # Format results
                matches = []
                matched_aliases = []
                max_confidence = 0.0

                for row in results:
                    confidence = float(row['confidence'])
                    if confidence > max_confidence:
                        max_confidence = confidence

                    # Find which alias matched
                    for alias in (row['aliases'] or []):
                        if alias.lower() == text or text in alias.lower():
                            matched_aliases.append(alias)

                    matches.append({
                        'id': row['id'],
                        'code': row['code'],
                        'name': row[f'name_{request.language}'],
                        'name_en': row['name_en'],
                        'name_vi': row['name_vi'],
                        'confidence': confidence
                    })

                self.logger.info(
                    f"{LogEmoji.SUCCESS} Lookup '{text}' in {request.data_type}: "
                    f"{len(matches)} matches (confidence: {max_confidence:.2f})"
                )

                return MasterDataLookupResponse(
                    matches=matches,
                    confidence=max_confidence,
                    matched_aliases=list(set(matched_aliases))
                )

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Lookup error: {e}")
                raise HTTPException(500, str(e))

        @self.app.post("/crawl-updates")
        async def crawl_master_data_updates(
            request: CrawlMasterDataRequest,
            background_tasks: BackgroundTasks
        ):
            """
            Crawl real estate sites to discover new master data
            (new projects, developers, streets, etc.)

            Example:
                {
                    "sources": ["batdongsan", "mogi"],
                    "data_types": ["projects", "developers"],
                    "auto_approve": false
                }

            Returns:
                {
                    "status": "started",
                    "job_id": "crawl-job-123",
                    "estimated_time": 300
                }
            """
            try:
                job_id = f"crawl-job-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

                # Start crawling in background
                background_tasks.add_task(
                    self._crawl_and_extract_master_data,
                    job_id,
                    request.sources,
                    request.data_types,
                    request.auto_approve
                )

                self.logger.info(
                    f"{LogEmoji.AI} Started master data crawl job: {job_id} "
                    f"(sources: {request.sources}, types: {request.data_types})"
                )

                return {
                    'status': 'started',
                    'job_id': job_id,
                    'estimated_time': len(request.sources) * 100,  # ~100s per source
                    'sources': request.sources,
                    'data_types': request.data_types
                }

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Error starting crawl: {e}")
                raise HTTPException(500, str(e))

        @self.app.get("/stats")
        async def get_master_data_stats():
            """Get master data statistics"""
            try:
                conn = self.get_db_connection()
                cur = conn.cursor()

                tables = [
                    'master_countries', 'master_cities', 'master_districts',
                    'master_property_types', 'master_amenities', 'master_views',
                    'master_directions', 'master_developers', 'master_projects',
                    'master_streets', 'master_legal_status', 'master_furniture_types',
                    'master_property_conditions', 'master_transaction_types'
                ]

                stats = {}
                for table in tables:
                    cur.execute(f"SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE active = TRUE) as active FROM {table}")
                    result = cur.fetchone()
                    stats[table.replace('master_', '')] = {
                        'total': result['total'],
                        'active': result['active']
                    }

                cur.close()
                conn.close()

                return {
                    'stats': stats,
                    'last_updated': datetime.now().isoformat(),
                    'cache_size': len(self.cache)
                }

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Error getting stats: {e}")
                raise HTTPException(500, str(e))

        @self.app.post("/admin/add")
        async def admin_add_master_data(
            data_type: str,
            code: str,
            name_en: str,
            name_vi: str,
            aliases: List[str],
            extra_fields: Dict[str, Any] = None
        ):
            """Admin API to manually add master data"""
            try:
                table_map = {
                    'district': 'master_districts',
                    'project': 'master_projects',
                    'developer': 'master_developers',
                    'street': 'master_streets'
                }

                if data_type not in table_map:
                    raise HTTPException(400, f"Invalid data_type: {data_type}")

                table = table_map[data_type]

                conn = self.get_db_connection()
                cur = conn.cursor()

                # Build insert query dynamically
                fields = ['code', 'name_en', 'name_vi', 'aliases']
                values = [code, name_en, name_vi, aliases]

                if extra_fields:
                    for key, value in extra_fields.items():
                        fields.append(key)
                        values.append(value)

                placeholders = ', '.join(['%s'] * len(values))
                query = f"""
                    INSERT INTO {table} ({', '.join(fields)})
                    VALUES ({placeholders})
                    ON CONFLICT (code) DO UPDATE SET
                        name_en = EXCLUDED.name_en,
                        name_vi = EXCLUDED.name_vi,
                        aliases = EXCLUDED.aliases,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id
                """

                cur.execute(query, values)
                result = cur.fetchone()
                conn.commit()
                cur.close()
                conn.close()

                # Clear cache
                self.cache.clear()

                self.logger.info(
                    f"{LogEmoji.SUCCESS} Added/updated {data_type}: "
                    f"{code} (id: {result['id']})"
                )

                return {
                    'success': True,
                    'id': result['id'],
                    'code': code,
                    'message': f"Successfully added/updated {data_type}"
                }

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Error adding master data: {e}")
                raise HTTPException(500, str(e))

    async def _crawl_and_extract_master_data(
        self,
        job_id: str,
        sources: List[str],
        data_types: List[str],
        auto_approve: bool
    ):
        """
        Background task to crawl and extract new master data

        Process:
        1. Call crawler service to get raw property data
        2. Extract unique values (projects, developers, streets, etc.)
        3. Check against existing master data
        4. If auto_approve=True, add new entries
        5. Otherwise, store in pending_master_data table for review
        """
        try:
            self.logger.info(f"{LogEmoji.AI} [Job {job_id}] Starting master data crawl...")

            discovered_data = {
                'projects': set(),
                'developers': set(),
                'streets': set(),
                'districts': set()
            }

            # Step 1: Crawl each source
            for source in sources:
                self.logger.info(f"{LogEmoji.INFO} [Job {job_id}] Crawling {source}...")

                try:
                    # Call crawler service
                    response = await self.http_client.post(
                        f"{self.crawler_url}/crawl/{source}",
                        json={'limit': 50}  # Sample size
                    )
                    response.raise_for_status()
                    data = response.json()

                    properties = data.get('properties', [])
                    self.logger.info(
                        f"{LogEmoji.SUCCESS} [Job {job_id}] Crawled {len(properties)} "
                        f"properties from {source}"
                    )

                    # Step 2: Extract unique values
                    for prop in properties:
                        # Extract project names
                        if 'projects' in data_types:
                            project = prop.get('project_name') or self._extract_project_name(prop.get('title', ''))
                            if project:
                                discovered_data['projects'].add(project.strip())

                        # Extract developer names
                        if 'developers' in data_types:
                            developer = prop.get('developer') or self._extract_developer_name(prop.get('description', ''))
                            if developer:
                                discovered_data['developers'].add(developer.strip())

                        # Extract street names
                        if 'streets' in data_types:
                            street = self._extract_street_name(prop.get('location', ''))
                            if street:
                                discovered_data['streets'].add(street.strip())

                        # Extract districts (usually already normalized)
                        if 'districts' in data_types:
                            district = prop.get('district')
                            if district:
                                discovered_data['districts'].add(district.strip())

                except Exception as e:
                    self.logger.error(
                        f"{LogEmoji.ERROR} [Job {job_id}] Error crawling {source}: {e}"
                    )
                    continue

            # Step 3: Check against existing master data
            new_entries = {}
            conn = self.get_db_connection()
            cur = conn.cursor()

            for data_type, values in discovered_data.items():
                if not values:
                    continue

                self.logger.info(
                    f"{LogEmoji.INFO} [Job {job_id}] Processing {len(values)} "
                    f"discovered {data_type}..."
                )

                table_map = {
                    'projects': 'master_projects',
                    'developers': 'master_developers',
                    'streets': 'master_streets',
                    'districts': 'master_districts'
                }
                table = table_map[data_type]

                # Check which entries are new
                for value in values:
                    # Check if exists (case-insensitive)
                    cur.execute(
                        f"""
                        SELECT id, code FROM {table}
                        WHERE LOWER(name_vi) = LOWER(%s) OR %s = ANY(aliases)
                        LIMIT 1
                        """,
                        (value, value)
                    )
                    result = cur.fetchone()

                    if not result:
                        # New entry discovered!
                        if data_type not in new_entries:
                            new_entries[data_type] = []

                        new_entries[data_type].append({
                            'name_vi': value,
                            'name_en': value,  # Will need translation service
                            'code': self._generate_code(value),
                            'source': 'crawler',
                            'discovered_at': datetime.now().isoformat()
                        })

            cur.close()
            conn.close()

            # Step 4: Add to database or pending table
            if auto_approve:
                added_count = await self._auto_approve_new_entries(new_entries)
                self.logger.info(
                    f"{LogEmoji.SUCCESS} [Job {job_id}] Auto-approved and added "
                    f"{added_count} new master data entries"
                )
            else:
                saved_count = await self._save_to_pending(new_entries, job_id)
                self.logger.info(
                    f"{LogEmoji.INFO} [Job {job_id}] Saved {saved_count} entries "
                    f"to pending review"
                )

            self.logger.info(
                f"{LogEmoji.SUCCESS} [Job {job_id}] Master data crawl completed! "
                f"Discovered: {sum(len(v) for v in new_entries.values())} new entries"
            )

        except Exception as e:
            self.logger.error(
                f"{LogEmoji.ERROR} [Job {job_id}] Master data crawl failed: {e}",
                exc_info=True
            )

    def _extract_project_name(self, text: str) -> Optional[str]:
        """Extract project name from property title"""
        # Common patterns: "Căn hộ Vinhomes Central Park", "Masteri Thảo Điền"
        import re
        patterns = [
            r'(Vinhomes [A-Za-z\s]+)',
            r'(Masteri [A-Za-z\s]+)',
            r'(The [A-Za-z\s]+)',
            r'([A-Z][a-z]+ (City|Park|Plaza|Tower|Residence))',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_developer_name(self, text: str) -> Optional[str]:
        """Extract developer name from description"""
        # Common patterns: "Chủ đầu tư: Vingroup", "Developer: CapitaLand"
        import re
        patterns = [
            r'chủ đầu tư[:\s]+([\w\s]+)',
            r'developer[:\s]+([\w\s]+)',
            r'CĐT[:\s]+([\w\s]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip().split('.')[0]  # Take first sentence
        return None

    def _extract_street_name(self, location: str) -> Optional[str]:
        """Extract street name from location"""
        # Patterns: "Đường Nguyễn Văn Linh", "Xa lộ Hà Nội"
        import re
        patterns = [
            r'đường\s+([\w\s]+)',
            r'street\s+([\w\s]+)',
            r'(Xa lộ [A-Za-z\s]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, location, re.IGNORECASE)
            if match:
                return match.group(1).strip().split(',')[0]  # Remove after comma
        return None

    def _generate_code(self, name: str) -> str:
        """Generate code from name (slug format)"""
        import re
        import unicodedata

        # Remove Vietnamese diacritics
        nfkd = unicodedata.normalize('NFKD', name)
        code = ''.join([c for c in nfkd if not unicodedata.combining(c)])

        # Convert to lowercase, replace spaces with underscores
        code = re.sub(r'[^\w\s-]', '', code.lower())
        code = re.sub(r'[-\s]+', '_', code)

        return code

    async def _auto_approve_new_entries(self, new_entries: Dict[str, List[Dict]]) -> int:
        """Auto-approve and add new entries to master data"""
        total_added = 0

        conn = self.get_db_connection()
        cur = conn.cursor()

        try:
            for data_type, entries in new_entries.items():
                table_map = {
                    'projects': 'master_projects',
                    'developers': 'master_developers',
                    'streets': 'master_streets',
                    'districts': 'master_districts'
                }
                table = table_map.get(data_type)
                if not table:
                    continue

                for entry in entries:
                    try:
                        cur.execute(
                            f"""
                            INSERT INTO {table} (code, name_en, name_vi, aliases, active, created_at)
                            VALUES (%s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
                            ON CONFLICT (code) DO NOTHING
                            """,
                            (
                                entry['code'],
                                entry['name_en'],
                                entry['name_vi'],
                                [entry['name_vi']]
                            )
                        )
                        total_added += 1
                    except Exception as e:
                        self.logger.error(f"{LogEmoji.ERROR} Error adding entry: {e}")

            conn.commit()

        finally:
            cur.close()
            conn.close()

        return total_added

    async def _save_to_pending(self, new_entries: Dict[str, List[Dict]], job_id: str) -> int:
        """Save new entries to pending review table"""
        # TODO: Create pending_master_data table for admin review
        total_saved = sum(len(v) for v in new_entries.values())
        self.logger.info(
            f"{LogEmoji.INFO} Pending review: {total_saved} entries (job: {job_id})"
        )
        return total_saved

    async def on_shutdown(self):
        """Cleanup on shutdown"""
        await self.http_client.aclose()
        await super().on_shutdown()


# Create service instance at module level for uvicorn
service = MasterDataService()
app = service.app

if __name__ == "__main__":
    service.run()

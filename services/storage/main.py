"""
Storage Service - PostgreSQL + OpenSearch Integration
Stores classified properties for RAG search
"""
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import json

from core.base_service import BaseService
from shared.utils.logger import LogEmoji

# Database imports
try:
    import psycopg2
    from psycopg2.extras import execute_values
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

try:
    from opensearchpy import OpenSearch, helpers
    HAS_OPENSEARCH = True
except ImportError:
    HAS_OPENSEARCH = False


class StorageService(BaseService):
    """
    Storage Service - CTO Architecture
    - PostgreSQL: Structured data (properties, metadata)
    - OpenSearch: Full-text search + vector embeddings
    """

    def __init__(self):
        super().__init__(
            name="storage",
            version="1.0.0",
            capabilities=["postgresql", "opensearch", "vector_search"],
            port=8103
        )

        # Database connections
        self.pg_conn = None
        self.os_client = None

    async def on_startup(self):
        """Initialize database connections"""
        await super().on_startup()

        # Initialize PostgreSQL
        if HAS_POSTGRES:
            try:
                self.pg_conn = psycopg2.connect(
                    host="127.0.0.1",
                    port=5432,
                    database="ree_ai",
                    user="ree_ai_user",
                    password="ree_ai_pass_2025"
                )
                self.logger.info(f"{LogEmoji.SUCCESS} PostgreSQL connected")

                # Create tables
                self._create_tables()

            except Exception as e:
                self.logger.warning(f"{LogEmoji.WARNING} PostgreSQL connection failed: {e}")

        # Initialize OpenSearch
        if HAS_OPENSEARCH:
            try:
                self.os_client = OpenSearch(
                    hosts=[{'host': 'localhost', 'port': 9200}],
                    http_compress=True,
                    timeout=30
                )

                # Test connection
                info = self.os_client.info()
                self.logger.info(f"{LogEmoji.SUCCESS} OpenSearch connected: {info['version']['number']}")

                # Create index
                self._create_opensearch_index()

            except Exception as e:
                self.logger.warning(f"{LogEmoji.WARNING} OpenSearch connection failed: {e}")

    def _create_tables(self):
        """Create PostgreSQL tables"""
        cursor = self.pg_conn.cursor()

        # Properties table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                price TEXT,
                location TEXT,
                bedrooms INTEGER DEFAULT 0,
                bathrooms INTEGER DEFAULT 0,
                area TEXT,
                description TEXT,
                url TEXT UNIQUE,
                source TEXT,
                property_type TEXT,
                confidence FLOAT,
                is_relevant BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_property_type ON properties(property_type);
            CREATE INDEX IF NOT EXISTS idx_location ON properties(location);
            CREATE INDEX IF NOT EXISTS idx_created_at ON properties(created_at);
        """)

        self.pg_conn.commit()
        cursor.close()

        self.logger.info(f"{LogEmoji.SUCCESS} PostgreSQL tables created")

    def _create_opensearch_index(self):
        """Create OpenSearch index for properties"""
        index_name = "properties"

        if not self.os_client.indices.exists(index=index_name):
            index_body = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "location": {"type": "keyword"},
                        "property_type": {"type": "keyword"},
                        "price": {"type": "text"},
                        "area": {"type": "text"},
                        "bedrooms": {"type": "integer"},
                        "bathrooms": {"type": "integer"},
                        "url": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "confidence": {"type": "float"},
                        "embedding": {"type": "knn_vector", "dimension": 384},
                        "created_at": {"type": "date"}
                    }
                }
            }

            self.os_client.indices.create(index=index_name, body=index_body)
            self.logger.info(f"{LogEmoji.SUCCESS} OpenSearch index 'properties' created")

    def setup_routes(self):
        """Setup Storage API routes"""

        @self.app.post("/store")
        async def store_properties(properties: List[Dict[str, Any]]):
            """
            Store properties to PostgreSQL + OpenSearch

            Example:
                POST /store
                {
                    "properties": [
                        {
                            "title": "...",
                            "price": "...",
                            ...
                        }
                    ]
                }
            """
            try:
                # Store to PostgreSQL
                pg_count = 0
                if self.pg_conn:
                    pg_count = self._store_to_postgres(properties)

                # Store to OpenSearch
                os_count = 0
                if self.os_client:
                    os_count = self._store_to_opensearch(properties)

                return {
                    "success": True,
                    "stored": len(properties),
                    "postgres": pg_count,
                    "opensearch": os_count
                }

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Store error: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "stored": 0
                }

        @self.app.get("/search")
        async def search_properties(
            q: str,
            limit: int = 10,
            property_type: str = None
        ):
            """
            Search properties in OpenSearch

            Example:
                GET /search?q=apartment+hanoi&limit=10
            """
            try:
                if not self.os_client:
                    return {"success": False, "error": "OpenSearch not available"}

                # Build search query
                query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"multi_match": {
                                    "query": q,
                                    "fields": ["title^2", "description", "location"]
                                }}
                            ]
                        }
                    },
                    "size": limit
                }

                # Add property type filter
                if property_type:
                    query["query"]["bool"]["filter"] = [
                        {"term": {"property_type": property_type}}
                    ]

                # Search
                response = self.os_client.search(
                    index="properties",
                    body=query
                )

                # Extract results
                results = []
                for hit in response['hits']['hits']:
                    results.append({
                        "id": hit['_id'],
                        "score": hit['_score'],
                        **hit['_source']
                    })

                return {
                    "success": True,
                    "total": response['hits']['total']['value'],
                    "results": results
                }

            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Search error: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "results": []
                }

        @self.app.get("/stats")
        async def get_stats():
            """Get storage statistics"""
            stats = {
                "postgres": {"available": HAS_POSTGRES and self.pg_conn is not None},
                "opensearch": {"available": HAS_OPENSEARCH and self.os_client is not None}
            }

            # Get PostgreSQL stats
            if self.pg_conn:
                cursor = self.pg_conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM properties")
                stats["postgres"]["total_properties"] = cursor.fetchone()[0]
                cursor.close()

            # Get OpenSearch stats
            if self.os_client:
                try:
                    count = self.os_client.count(index="properties")
                    stats["opensearch"]["total_documents"] = count['count']
                except:
                    stats["opensearch"]["total_documents"] = 0

            return stats

    def _store_to_postgres(self, properties: List[Dict[str, Any]]) -> int:
        """Store properties to PostgreSQL"""
        cursor = self.pg_conn.cursor()

        # Prepare data
        values = []
        for prop in properties:
            values.append((
                prop.get('title', ''),
                prop.get('price', ''),
                prop.get('location', ''),
                prop.get('bedrooms', 0),
                prop.get('bathrooms', 0),
                prop.get('area', ''),
                prop.get('description', ''),
                prop.get('url', ''),
                prop.get('source', ''),
                prop.get('property_type', 'unknown'),
                prop.get('confidence', 0.0),
                prop.get('is_relevant', False)
            ))

        # Insert with ON CONFLICT (skip duplicates by URL)
        execute_values(
            cursor,
            """
            INSERT INTO properties
            (title, price, location, bedrooms, bathrooms, area, description, url, source,
             property_type, confidence, is_relevant)
            VALUES %s
            ON CONFLICT (url) DO NOTHING
            """,
            values
        )

        inserted = cursor.rowcount
        self.pg_conn.commit()
        cursor.close()

        self.logger.info(f"{LogEmoji.SUCCESS} Stored {inserted} properties to PostgreSQL")
        return inserted

    def _store_to_opensearch(self, properties: List[Dict[str, Any]]) -> int:
        """Store properties to OpenSearch"""
        # Prepare documents
        actions = []
        for prop in properties:
            doc = {
                "_index": "properties",
                "_source": {
                    "title": prop.get('title', ''),
                    "description": prop.get('description', ''),
                    "location": prop.get('location', ''),
                    "property_type": prop.get('property_type', 'unknown'),
                    "price": prop.get('price', ''),
                    "area": prop.get('area', ''),
                    "bedrooms": prop.get('bedrooms', 0),
                    "bathrooms": prop.get('bathrooms', 0),
                    "url": prop.get('url', ''),
                    "source": prop.get('source', ''),
                    "confidence": prop.get('confidence', 0.0),
                    "created_at": datetime.now().isoformat()
                }
            }
            actions.append(doc)

        # Bulk insert
        success, failed = helpers.bulk(self.os_client, actions, raise_on_error=False)

        self.logger.info(f"{LogEmoji.SUCCESS} Stored {success} properties to OpenSearch")
        return success


if __name__ == "__main__":
    service = StorageService()
    service.run()

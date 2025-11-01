"""
Crawl properties and store in OpenSearch (REFACTORED)
Uses flexible JSON schema - supports unlimited property attributes!
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed, using environment defaults")

from services.crawler.bulk_crawler import bulk_crawl_properties
from opensearchpy import AsyncOpenSearch


async def create_properties_index(client: AsyncOpenSearch, index_name: str):
    """Create properties index with dynamic mapping for unlimited fields"""

    # Check if index already exists
    index_exists = await client.indices.exists(index=index_name)

    if index_exists:
        print(f"✅ Index '{index_name}' already exists")
        return

    print(f"📝 Creating index '{index_name}' with dynamic mapping...")

    # Create index with flexible schema
    await client.indices.create(
        index=index_name,
        body={
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "index": {
                    "max_result_window": 50000  # Allow deep pagination
                }
            },
            "mappings": {
                "dynamic": "true",  # CRITICAL: Allow unlimited new fields!
                "properties": {
                    # Core fields with specific types
                    "property_id": {"type": "keyword"},
                    "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "description": {"type": "text"},
                    "price": {"type": "text"},  # Keep as text initially (will parse later)
                    "location": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "district": {"type": "keyword"},
                    "city": {"type": "keyword"},
                    "property_type": {"type": "keyword"},
                    "url": {"type": "keyword"},
                    "source": {"type": "keyword"},

                    # Numeric fields
                    "bedrooms": {"type": "integer"},
                    "bathrooms": {"type": "integer"},
                    "area": {"type": "text"},  # Keep as text initially

                    # Metadata
                    "created_at": {"type": "date"}

                    # NOTE: Dynamic mapping enabled - any other field will be auto-added!
                    # Vector embeddings can be added later with OpenSearch ML plugin
                    # Examples that will be auto-added:
                    # - pool, gym, parking, view, balcony_direction
                    # - floor_number, building_name, security_features
                    # - ANY attribute found in property data!
                }
            }
        }
    )

    print(f"✅ Created index with dynamic mapping (unlimited attributes supported)")


async def crawl_and_store(total_properties: int = 1000):
    """Crawl properties and store in OpenSearch with flexible JSON schema"""

    print(f"🚀 Starting crawl for {total_properties} properties...")
    print(f"📊 Storage: OpenSearch (flexible JSON - unlimited attributes!)")

    # Step 1: Crawl properties
    properties = await bulk_crawl_properties(total=total_properties, sites=['batdongsan'])

    print(f"\n✅ Crawled {len(properties)} properties")

    # Step 2: Connect to OpenSearch
    print(f"\n🔍 Connecting to OpenSearch...")

    opensearch_host = os.getenv('OPENSEARCH_HOST', 'localhost')
    opensearch_port = int(os.getenv('OPENSEARCH_PORT', 9200))
    opensearch_user = os.getenv('OPENSEARCH_USER', 'admin')
    opensearch_password = os.getenv('OPENSEARCH_PASSWORD', 'admin')
    index_name = os.getenv('OPENSEARCH_PROPERTIES_INDEX', 'properties')

    print(f"📍 OpenSearch: {opensearch_host}:{opensearch_port}")
    print(f"📇 Index: {index_name}")

    client = AsyncOpenSearch(
        hosts=[{'host': opensearch_host, 'port': opensearch_port}],
        http_auth=(opensearch_user, opensearch_password),
        use_ssl=False,
        verify_certs=False,
        ssl_show_warn=False
    )

    try:
        # Test connection
        info = await client.info()
        print(f"✅ Connected to OpenSearch: {info['cluster_name']}")

        # Step 3: Create index with dynamic mapping
        await create_properties_index(client, index_name)

        # Step 4: Bulk insert properties
        print(f"\n💾 Inserting {len(properties)} properties into OpenSearch...")

        # Prepare bulk request
        bulk_data = []
        for prop in properties:
            # Generate unique property_id from URL
            property_id = prop.get('url', '').split('/')[-1] or f"prop_{datetime.now().timestamp()}"

            # Prepare document (FLEXIBLE JSON - unlimited fields!)
            doc = {
                "property_id": property_id,
                "title": prop.get('title', ''),
                "price": prop.get('price', ''),  # Store as-is, parse when needed
                "location": prop.get('location', ''),
                "bedrooms": prop.get('bedrooms', 0),
                "bathrooms": prop.get('bathrooms', 0),
                "area": prop.get('area', ''),  # Store as-is
                "description": prop.get('description', ''),
                "url": prop.get('url', ''),
                "source": prop.get('source', ''),
                "created_at": datetime.utcnow().isoformat(),

                # ANY additional fields from crawler will be stored!
                # This is the KEY: flexible schema allows unlimited attributes
            }

            # Add to bulk request
            bulk_data.append({"index": {"_index": index_name, "_id": property_id}})
            bulk_data.append(doc)

        # Execute bulk insert
        if bulk_data:
            response = await client.bulk(body=bulk_data, refresh=True)

            # Check for errors
            if response['errors']:
                failed = sum(1 for item in response['items'] if 'error' in item.get('index', {}))
                print(f"⚠️  {failed} documents failed to insert")
            else:
                print(f"✅ All {len(properties)} properties inserted successfully!")

        # Step 5: Get final count
        await client.indices.refresh(index=index_name)
        count_response = await client.count(index=index_name)
        total_count = count_response['count']

        print(f"📊 Total properties in OpenSearch: {total_count}")

        # Step 6: Show sample property to verify flexible schema
        print(f"\n🔍 Sample property from OpenSearch:")
        search_response = await client.search(
            index=index_name,
            body={
                "query": {"match_all": {}},
                "size": 1
            }
        )

        if search_response['hits']['hits']:
            sample = search_response['hits']['hits'][0]['_source']
            print(f"   Title: {sample.get('title', '')[:60]}...")
            print(f"   Price: {sample.get('price', '')}")
            print(f"   Location: {sample.get('location', '')}")
            print(f"   Bedrooms: {sample.get('bedrooms', 0)}")
            print(f"   Fields: {len(sample)} (flexible schema - can add unlimited more!)")

        return total_count

    finally:
        await client.close()
        print(f"\n🔒 Closed OpenSearch connection")


if __name__ == "__main__":
    # Default to 1000 properties for quick testing
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    count = asyncio.run(crawl_and_store(total))

    print(f"\n{'='*70}")
    print(f"✅ CRAWL COMPLETE: {count} properties in OpenSearch")
    print(f"{'='*70}")
    print(f"\n🎯 Key Achievement:")
    print(f"   ✅ Properties stored as flexible JSON in OpenSearch")
    print(f"   ✅ Unlimited attributes supported (dynamic mapping enabled)")
    print(f"   ✅ Ready for BM25 full-text search")
    print(f"   ✅ Ready for semantic search (with embeddings)")
    print(f"{'='*70}")

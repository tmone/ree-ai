#!/usr/bin/env python3
"""
Create OpenSearch Index with Proper Mapping for Numeric Fields

This script creates the 'properties' index with explicit mapping for:
- price: double (numeric filtering/sorting)
- area: double (numeric filtering/sorting)
- bedrooms: integer
- bathrooms: integer

Run this BEFORE indexing properties to ensure correct data types.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except:
    pass

from opensearchpy import AsyncOpenSearch


async def create_properties_index():
    """Create properties index with explicit numeric mapping"""

    print("=" * 70)
    print("🔧 CREATING OPENSEARCH INDEX WITH NUMERIC MAPPING")
    print("=" * 70)

    # OpenSearch connection
    opensearch_host = os.getenv('OPENSEARCH_HOST', 'localhost')
    opensearch_port = int(os.getenv('OPENSEARCH_PORT', 9200))
    opensearch_user = os.getenv('OPENSEARCH_USER', 'admin')
    opensearch_password = os.getenv('OPENSEARCH_PASSWORD', 'admin')
    index_name = os.getenv('OPENSEARCH_PROPERTIES_INDEX', 'properties')

    print(f"\n📍 OpenSearch: {opensearch_host}:{opensearch_port}")
    print(f"📍 Index: {index_name}")

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

        # Check if index exists
        index_exists = await client.indices.exists(index=index_name)

        if index_exists:
            print(f"\n⚠️  Index '{index_name}' already exists!")
            response = input("Delete and recreate? [y/N]: ")

            if response.lower() == 'y':
                await client.indices.delete(index=index_name)
                print(f"🗑️  Deleted existing index")
            else:
                print("❌ Cancelled. Keeping existing index.")
                return

        # Define index mapping with explicit types for numeric fields
        index_mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1,
                "index": {
                    "max_result_window": 10000  # Allow up to 10K results
                }
            },
            "mappings": {
                "properties": {
                    # Identifiers
                    "property_id": {"type": "keyword"},
                    "url": {"type": "keyword"},
                    "source": {"type": "keyword"},

                    # Text fields (full-text search)
                    "title": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "description": {"type": "text"},

                    # NUMERIC FIELDS - Critical for filtering/sorting!
                    "price": {
                        "type": "double",  # Numeric for filtering: price > 6500000000
                        "doc_values": True  # Enable sorting
                    },
                    "area": {
                        "type": "double",  # Numeric for filtering: area < 70
                        "doc_values": True
                    },
                    "bedrooms": {
                        "type": "integer",
                        "doc_values": True
                    },
                    "bathrooms": {
                        "type": "integer",
                        "doc_values": True
                    },

                    # Display fields (for UI)
                    "price_display": {"type": "keyword"},
                    "area_display": {"type": "keyword"},

                    # Location fields
                    "location": {"type": "text"},
                    "district": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "city": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "ward": {"type": "keyword"},

                    # Property attributes
                    "property_type": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },

                    # Metadata
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"},
                    "indexed_at": {"type": "date"},

                    # Crawler metadata
                    "confidence": {"type": "float"},
                    "is_relevant": {"type": "boolean"},

                    # PostgreSQL migration tracking
                    "migrated_from_postgres": {"type": "boolean"},
                    "postgres_id": {"type": "integer"}
                }
            }
        }

        print(f"\n🚀 Creating index with mapping...")
        print(f"\n📋 Key numeric fields:")
        print(f"   - price: double (VND)")
        print(f"   - area: double (m²)")
        print(f"   - bedrooms: integer")
        print(f"   - bathrooms: integer")

        # Create index
        response = await client.indices.create(
            index=index_name,
            body=index_mapping
        )

        if response.get('acknowledged'):
            print(f"\n✅ Index '{index_name}' created successfully!")
            print(f"\n📊 Mapping Details:")
            print(f"   - Shards: 1")
            print(f"   - Replicas: 1")
            print(f"   - Max results: 10,000")

            # Verify mapping
            mapping_response = await client.indices.get_mapping(index=index_name)
            properties_mapping = mapping_response[index_name]['mappings']['properties']

            print(f"\n🔍 Verified Field Types:")
            for field in ['price', 'area', 'bedrooms', 'bathrooms', 'title', 'district']:
                field_type = properties_mapping.get(field, {}).get('type', 'N/A')
                print(f"   - {field:15} : {field_type}")

            print(f"\n✅ Index is ready for numeric filtering!")
            print(f"\n💡 Example Queries:")
            print(f"   - price > 6500000000 AND price < 10000000000")
            print(f"   - area < 70")
            print(f"   - bedrooms >= 3")

        else:
            print(f"❌ Failed to create index: {response}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.close()
        print(f"\n🔒 Closed connection")


if __name__ == "__main__":
    print("\n⚠️  INDEX CREATION")
    print("This will create the 'properties' index with numeric mapping.")
    print("If the index already exists, you'll be prompted to delete it.")
    print("")

    response = input("Continue? [y/N]: ")

    if response.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)

    asyncio.run(create_properties_index())

    print(f"\n{'='*70}")
    print(f"✅ COMPLETE!")
    print(f"{'='*70}")
    print(f"\n📌 NEXT STEPS:")
    print(f"   1. Crawl properties: POST /crawl/bulk?total=100&auto_index=true")
    print(f"   2. Query with filters: POST /search with min_price/max_price/min_area")
    print(f"   3. Verify: Check OpenSearch dashboard or use /stats endpoint")
    print(f"\n{'='*70}\n")

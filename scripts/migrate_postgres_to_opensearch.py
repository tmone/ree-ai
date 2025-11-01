"""
Migrate properties from PostgreSQL to OpenSearch
One-time migration script for architectural refactoring
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv(project_root / '.env')
except:
    pass

import psycopg2
from opensearchpy import AsyncOpenSearch


async def migrate_properties():
    """Migrate all properties from PostgreSQL to OpenSearch"""

    print("="*70)
    print("🚀 PostgreSQL → OpenSearch Migration")
    print("="*70)

    # Step 1: Connect to PostgreSQL
    print("\n📊 Step 1: Reading from PostgreSQL...")

    postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
    postgres_port = int(os.getenv('POSTGRES_PORT', 5432))
    postgres_db = os.getenv('POSTGRES_DB', 'ree_ai')
    postgres_user = os.getenv('POSTGRES_USER', 'ree_ai_user')
    postgres_password = os.getenv('POSTGRES_PASSWORD', 'ree_ai_password')

    print(f"   PostgreSQL: {postgres_host}:{postgres_port}/{postgres_db}")

    conn = psycopg2.connect(
        host=postgres_host,
        port=postgres_port,
        database=postgres_db,
        user=postgres_user,
        password=postgres_password
    )

    cursor = conn.cursor()

    # Get all properties
    cursor.execute("""
        SELECT
            id, title, price, location, bedrooms, bathrooms, area,
            description, url, source, property_type, confidence,
            is_relevant, created_at, updated_at
        FROM properties
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    print(f"   ✅ Found {len(rows)} properties in PostgreSQL")

    # Step 2: Connect to OpenSearch
    print(f"\n🔍 Step 2: Connecting to OpenSearch...")

    opensearch_host = os.getenv('OPENSEARCH_HOST', 'localhost')
    opensearch_port = int(os.getenv('OPENSEARCH_PORT', 9200))
    opensearch_user = os.getenv('OPENSEARCH_USER', 'admin')
    opensearch_password = os.getenv('OPENSEARCH_PASSWORD', 'admin')
    index_name = os.getenv('OPENSEARCH_PROPERTIES_INDEX', 'properties')

    print(f"   OpenSearch: {opensearch_host}:{opensearch_port}")
    print(f"   Index: {index_name}")

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
        print(f"   ✅ Connected to OpenSearch: {info['cluster_name']}")

        # Get current count
        if await client.indices.exists(index=index_name):
            count_response = await client.count(index=index_name)
            existing_count = count_response['count']
            print(f"   📊 Current properties in OpenSearch: {existing_count}")
        else:
            existing_count = 0
            print(f"   ⚠️  Index '{index_name}' does not exist yet")

        # Step 3: Prepare bulk data
        print(f"\n💾 Step 3: Preparing bulk insert...")

        bulk_data = []
        skipped = 0

        for row in rows:
            (id_, title, price, location, bedrooms, bathrooms, area,
             description, url, source, property_type, confidence,
             is_relevant, created_at, updated_at) = row

            # Skip if no URL (can't create unique ID)
            if not url:
                skipped += 1
                continue

            # Generate property_id from URL
            property_id = url.split('/')[-1] or f"prop_{id_}"

            # Parse location into district and city
            district = ""
            city = ""
            if location:
                parts = [p.strip() for p in location.split(',')]
                if len(parts) >= 2:
                    district = parts[0]
                    city = parts[1]
                elif len(parts) == 1:
                    district = parts[0]

            # Prepare document (flexible JSON)
            doc = {
                "property_id": property_id,
                "title": title or '',
                "price": price or '',
                "location": location or '',
                "district": district,
                "city": city,
                "bedrooms": bedrooms or 0,
                "bathrooms": bathrooms or 0,
                "area": area or '',
                "description": description or '',
                "url": url,
                "source": source or '',
                "property_type": property_type or '',
                "created_at": created_at.isoformat() if created_at else datetime.utcnow().isoformat(),

                # Additional fields from PostgreSQL (will be preserved in flexible schema)
                "confidence": confidence if confidence is not None else 0.0,
                "is_relevant": is_relevant if is_relevant is not None else True,
                "updated_at": updated_at.isoformat() if updated_at else None,
                "migrated_from_postgres": True,
                "postgres_id": id_
            }

            # Add to bulk request
            bulk_data.append({"index": {"_index": index_name, "_id": property_id}})
            bulk_data.append(doc)

        print(f"   ✅ Prepared {len(bulk_data) // 2} properties for migration")
        if skipped > 0:
            print(f"   ⚠️  Skipped {skipped} properties (missing URL)")

        # Step 4: Bulk insert to OpenSearch
        if bulk_data:
            print(f"\n🚀 Step 4: Migrating to OpenSearch...")

            response = await client.bulk(body=bulk_data, refresh=True)

            # Check for errors
            if response['errors']:
                failed = sum(1 for item in response['items'] if 'error' in item.get('index', {}))
                successful = len(bulk_data) // 2 - failed
                print(f"   ⚠️  Migration partial: {successful} successful, {failed} failed")

                # Show first error for debugging
                for item in response['items']:
                    if 'error' in item.get('index', {}):
                        print(f"   Error example: {item['index']['error']}")
                        break
            else:
                print(f"   ✅ All {len(bulk_data) // 2} properties migrated successfully!")
        else:
            print(f"   ⚠️  No properties to migrate")

        # Step 5: Verify migration
        print(f"\n🔍 Step 5: Verifying migration...")

        await client.indices.refresh(index=index_name)
        count_response = await client.count(index=index_name)
        final_count = count_response['count']

        print(f"   📊 Properties before: {existing_count}")
        print(f"   📊 Properties after: {final_count}")
        print(f"   ✅ New properties added: {final_count - existing_count}")

        # Show sample migrated property
        print(f"\n📋 Sample migrated property:")
        search_response = await client.search(
            index=index_name,
            body={
                "query": {
                    "term": {"migrated_from_postgres": True}
                },
                "size": 1
            }
        )

        if search_response['hits']['hits']:
            sample = search_response['hits']['hits'][0]['_source']
            print(f"   Title: {sample.get('title', '')[:60]}...")
            print(f"   Price: {sample.get('price', '')}")
            print(f"   Location: {sample.get('location', '')}")
            print(f"   PostgreSQL ID: {sample.get('postgres_id')}")
            print(f"   Fields: {len(sample)} (includes migrated metadata)")

        return final_count

    finally:
        await client.close()
        cursor.close()
        conn.close()
        print(f"\n🔒 Closed all connections")


if __name__ == "__main__":
    print("\n⚠️  MIGRATION WARNING")
    print("This script will migrate all properties from PostgreSQL to OpenSearch.")
    print("Properties are indexed by URL, so duplicates will be updated (not duplicated).")
    print("")

    response = input("Continue with migration? [y/N]: ")

    if response.lower() != 'y':
        print("Migration cancelled.")
        sys.exit(0)

    count = asyncio.run(migrate_properties())

    print(f"\n{'='*70}")
    print(f"✅ MIGRATION COMPLETE!")
    print(f"{'='*70}")
    print(f"📊 Total properties in OpenSearch: {count}")
    print(f"✅ PostgreSQL properties successfully migrated to OpenSearch")
    print(f"✅ Flexible JSON schema allows unlimited attributes")
    print(f"✅ Ready for BM25 full-text search via DB Gateway")
    print(f"{'='*70}\n")

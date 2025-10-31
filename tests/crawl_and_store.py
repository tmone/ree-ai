"""
Quick script to crawl properties and store in PostgreSQL
For prompt evaluation purposes
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    # Load .env.postgres first (auto-provisioned), fallback to .env
    if (project_root / '.env.postgres').exists():
        load_dotenv(project_root / '.env.postgres')
        print("✅ Loaded PostgreSQL config from .env.postgres (auto-provisioned)")
    load_dotenv(project_root / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed, using environment defaults")

from services.crawler.bulk_crawler import bulk_crawl_properties
import psycopg2
from psycopg2.extras import execute_values


async def crawl_and_store(total_properties: int = 1000):
    """Crawl properties and store in PostgreSQL"""

    print(f"🚀 Starting crawl for {total_properties} properties...")

    # Crawl properties
    properties = await bulk_crawl_properties(total=total_properties, sites=['batdongsan'])

    print(f"\n✅ Crawled {len(properties)} properties")

    # Connect to PostgreSQL
    # Priority: USE_LOCAL_POSTGRES env → localhost, else → Docker
    print(f"\n📊 Connecting to PostgreSQL...")

    use_local = os.getenv('USE_LOCAL_POSTGRES', 'false').lower() == 'true'
    pg_host = os.getenv('POSTGRES_HOST', 'localhost' if use_local else 'postgres')
    pg_port = int(os.getenv('POSTGRES_PORT', 5432))
    pg_db = os.getenv('POSTGRES_DB', 'ree_ai')
    pg_user = os.getenv('POSTGRES_USER', 'ree_ai_user')
    pg_pass = os.getenv('POSTGRES_PASSWORD', 'ree_ai_pass_2025')

    print(f"📍 Using PostgreSQL: {pg_host}:{pg_port}/{pg_db} (local={use_local})")

    conn = psycopg2.connect(
        host=pg_host,
        port=pg_port,
        database=pg_db,
        user=pg_user,
        password=pg_pass
    )

    print(f"✅ Connected to PostgreSQL")

    # Insert properties
    print(f"\n💾 Inserting {len(properties)} properties into database...")

    cursor = conn.cursor()

    # Prepare data for insertion
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
            prop.get('source', '')
        ))

    # Bulk insert with ON CONFLICT DO NOTHING to handle duplicates
    execute_values(
        cursor,
        """
        INSERT INTO properties
        (title, price, location, bedrooms, bathrooms, area, description, url, source)
        VALUES %s
        ON CONFLICT (url) DO NOTHING
        """,
        values
    )

    conn.commit()

    # Get actual count
    cursor.execute("SELECT COUNT(*) FROM properties")
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    print(f"✅ Inserted properties successfully!")
    print(f"📊 Total properties in database: {count}")

    return count


if __name__ == "__main__":
    # Default to 1000 properties for quick testing
    # User said they already have 10K+, but we start fresh with 1K
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    count = asyncio.run(crawl_and_store(total))

    print(f"\n{'='*70}")
    print(f"✅ CRAWL COMPLETE: {count} properties ready for evaluation")
    print(f"{'='*70}")

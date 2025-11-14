"""Check database permissions and existing schemas"""

import asyncio
import asyncpg

DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}

async def check_permissions():
    conn = await asyncpg.connect(**DB_CONFIG)

    print("=" * 80)
    print("CHECKING DATABASE PERMISSIONS")
    print("=" * 80)

    # Check current user
    current_user = await conn.fetchval("SELECT current_user")
    print(f"\nCurrent User: {current_user}")

    # Check available schemas
    print("\nAvailable Schemas:")
    schemas = await conn.fetch("""
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name NOT LIKE 'pg_%'
          AND schema_name != 'information_schema'
        ORDER BY schema_name
    """)
    for schema in schemas:
        print(f"  - {schema['schema_name']}")

    # Check if ree_common schema exists and permissions
    print("\nChecking ree_common schema:")
    try:
        ree_common_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.schemata
                WHERE schema_name = 'ree_common'
            )
        """)

        if ree_common_exists:
            print("  ✅ ree_common schema EXISTS")

            # Check tables in ree_common
            tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'ree_common'
                ORDER BY table_name
            """)

            if tables:
                print("\n  Existing tables in ree_common:")
                for table in tables:
                    print(f"    - {table['table_name']}")
            else:
                print("  No tables in ree_common yet")

        else:
            print("  ❌ ree_common schema DOES NOT EXIST")

    except Exception as e:
        print(f"  ❌ Error checking ree_common: {e}")

    # Check privileges on ree_common
    print("\nChecking privileges:")
    try:
        privileges = await conn.fetch("""
            SELECT
                grantee,
                privilege_type
            FROM information_schema.schema_privileges
            WHERE schema_name = 'ree_common'
              AND grantee = current_user
        """)

        if privileges:
            print(f"  User '{current_user}' has these privileges on ree_common:")
            for priv in privileges:
                print(f"    - {priv['privilege_type']}")
        else:
            print(f"  ❌ User '{current_user}' has NO privileges on ree_common")

    except Exception as e:
        print(f"  Error checking privileges: {e}")

    # Try to check public schema permissions
    print("\nChecking public schema permissions:")
    try:
        can_create_in_public = await conn.fetchval("""
            SELECT has_schema_privilege(current_user, 'public', 'CREATE')
        """)

        if can_create_in_public:
            print("  ✅ Can CREATE in public schema")
        else:
            print("  ❌ Cannot CREATE in public schema")

    except Exception as e:
        print(f"  Error: {e}")

    await conn.close()
    print("\n" + "=" * 80)

asyncio.run(check_permissions())

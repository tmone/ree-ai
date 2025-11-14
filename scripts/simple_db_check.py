"""Simple database check without emojis"""

import asyncio
import asyncpg

DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}

async def check_db():
    conn = await asyncpg.connect(**DB_CONFIG)

    print("=" * 80)
    print("DATABASE CHECK")
    print("=" * 80)

    # Check conversations table
    print("\nChecking ree_common.conversations table:")
    try:
        conv_schema = await conn.fetch("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'ree_common'
              AND table_name = 'conversations'
            ORDER BY ordinal_position
        """)

        if conv_schema:
            print("  [OK] conversations table EXISTS")
            print("  Columns:")
            for col in conv_schema:
                print(f"    - {col['column_name']}: {col['data_type']}")
        else:
            print("  [NOT FOUND] conversations table does NOT exist")

    except Exception as e:
        print(f"  [ERROR] {e}")

    # Check messages table
    print("\nChecking ree_common.messages table:")
    try:
        msg_schema = await conn.fetch("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'ree_common'
              AND table_name = 'messages'
            ORDER BY ordinal_position
        """)

        if msg_schema:
            print("  [OK] messages table EXISTS")
            print("  Columns:")
            for col in msg_schema:
                print(f"    - {col['column_name']}: {col['data_type']}")
        else:
            print("  [NOT FOUND] messages table does NOT exist")

    except Exception as e:
        print(f"  [ERROR] {e}")

    # Check permissions
    print("\nChecking permissions:")
    try:
        # Try to insert a test conversation
        test_conv_id = "test_permission_check"

        await conn.execute("""
            INSERT INTO ree_common.conversations
            (conversation_id, user_id)
            VALUES ($1, $2)
            ON CONFLICT (conversation_id) DO NOTHING
        """, test_conv_id, "test_user")

        print("  [OK] Can INSERT into conversations table")

        # Delete test data
        await conn.execute("""
            DELETE FROM ree_common.conversations
            WHERE conversation_id = $1
        """, test_conv_id)

        print("  [OK] Can DELETE from conversations table")

    except Exception as e:
        print(f"  [ERROR] Cannot write to tables: {e}")

    await conn.close()
    print("\n" + "=" * 80)

asyncio.run(check_db())

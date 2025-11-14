"""
Setup Database Schema for Flow 1 Testing
=========================================
Creates necessary tables for storing Flow 1 conversations and messages.
"""

import asyncio
import asyncpg


# Database configuration
DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}


async def setup_database():
    """Create tables for Flow 1 testing"""

    print("=" * 80)
    print("🗄️  SETTING UP DATABASE SCHEMA FOR FLOW 1")
    print("=" * 80)
    print(f"Database: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("=" * 80)

    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)
    print("\n✅ Connected to PostgreSQL")

    try:
        # Create schema if not exists
        await conn.execute("""
            CREATE SCHEMA IF NOT EXISTS ree_common
        """)
        print("✅ Created/verified schema: ree_common")

        # Create conversations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ree_common.conversations (
                id BIGSERIAL PRIMARY KEY,
                conversation_id VARCHAR(255) UNIQUE NOT NULL,
                user_id VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Created table: ree_common.conversations")

        # Create messages table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ree_common.messages (
                id BIGSERIAL PRIMARY KEY,
                message_id VARCHAR(255) UNIQUE NOT NULL,
                conversation_id VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id)
                    REFERENCES ree_common.conversations(conversation_id)
                    ON DELETE CASCADE
            )
        """)
        print("✅ Created table: ree_common.messages")

        # Create indexes for better query performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_user_id
            ON ree_common.conversations(user_id)
        """)
        print("✅ Created index: idx_conversations_user_id")

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
            ON ree_common.messages(conversation_id)
        """)
        print("✅ Created index: idx_messages_conversation_id")

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_created_at
            ON ree_common.messages(created_at)
        """)
        print("✅ Created index: idx_messages_created_at")

        # Verify tables exist
        print("\n" + "=" * 80)
        print("📋 VERIFYING TABLES")
        print("=" * 80)

        # Check conversations table
        conv_schema = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'ree_common'
              AND table_name = 'conversations'
            ORDER BY ordinal_position
        """)

        print("\n✅ Conversations Table Schema:")
        print(f"{'Column':<25s} {'Type':<20s} {'Nullable':<10s}")
        print("-" * 80)
        for col in conv_schema:
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            print(f"{col['column_name']:<25s} {col['data_type']}{max_len:<20s} {col['is_nullable']:<10s}")

        # Check messages table
        msg_schema = await conn.fetch("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'ree_common'
              AND table_name = 'messages'
            ORDER BY ordinal_position
        """)

        print("\n✅ Messages Table Schema:")
        print(f"{'Column':<25s} {'Type':<20s} {'Nullable':<10s}")
        print("-" * 80)
        for col in msg_schema:
            max_len = f"({col['character_maximum_length']})" if col['character_maximum_length'] else ""
            print(f"{col['column_name']:<25s} {col['data_type']}{max_len:<20s} {col['is_nullable']:<10s}")

        # Check existing data count
        conv_count = await conn.fetchval("""
            SELECT COUNT(*) FROM ree_common.conversations
        """)
        msg_count = await conn.fetchval("""
            SELECT COUNT(*) FROM ree_common.messages
        """)

        print("\n" + "=" * 80)
        print("📊 EXISTING DATA")
        print("=" * 80)
        print(f"Conversations: {conv_count}")
        print(f"Messages: {msg_count}")

        print("\n" + "=" * 80)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 80)
        print("\nYou can now run:")
        print("  python tests/demo_flow1_save_to_db.py")
        print("\nTo test Flow 1 and save conversations to the database.")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await conn.close()
        print("\n✅ Database connection closed")


if __name__ == "__main__":
    asyncio.run(setup_database())

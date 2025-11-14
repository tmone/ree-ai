"""View Flow 1 Chat History from PostgreSQL"""

import asyncio
import asyncpg
import json

DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}

async def view_all_conversations():
    """View summary of all conversations"""
    conn = await asyncpg.connect(**DB_CONFIG)

    print("=" * 120)
    print("FLOW 1 CHAT HISTORY - ALL CONVERSATIONS")
    print("=" * 120)

    # Get all conversations
    conversations = await conn.fetch("""
        SELECT
            c.conversation_id,
            c.user_id,
            c.created_at,
            m.metadata->>'language' as language,
            m.metadata->>'intent' as intent,
            (m.metadata->>'completeness_score')::INT as score,
            (m.metadata->>'iterations')::INT as iterations,
            m.metadata->'attributes' as attributes
        FROM public.flow1_conversations c
        JOIN public.flow1_messages m ON c.conversation_id = m.conversation_id
        WHERE m.role = 'assistant'
        ORDER BY c.created_at DESC
    """)

    print(f"\nTotal Conversations: {len(conversations)}\n")
    print(f"{'#':<4s} {'Conversation ID':<28s} {'Lang':<6s} {'Intent':<12s} {'Score':<8s} {'Iter':<6s} {'Attributes'}")
    print("-" * 120)

    for i, conv in enumerate(conversations, 1):
        attrs = json.loads(conv['attributes']) if conv['attributes'] else {}
        attr_summary = ", ".join([f"{k}={v}" for k, v in attrs.items()]) if attrs else "None"
        if len(attr_summary) > 40:
            attr_summary = attr_summary[:37] + "..."

        print(f"{i:<4d} "
              f"{conv['conversation_id']:<28s} "
              f"{conv['language'].upper():<6s} "
              f"{conv['intent']:<12s} "
              f"{conv['score']:>3d}%    "
              f"{conv['iterations']:>2d}     "
              f"{attr_summary}")

    print("\n" + "=" * 120)

    await conn.close()


async def view_single_conversation(conversation_id: str):
    """View detailed conversation"""
    conn = await asyncpg.connect(**DB_CONFIG)

    print("\n" + "=" * 120)
    print(f"CONVERSATION DETAILS: {conversation_id}")
    print("=" * 120)

    # Get messages
    messages = await conn.fetch("""
        SELECT
            role,
            content,
            metadata,
            created_at
        FROM public.flow1_messages
        WHERE conversation_id = $1
        ORDER BY created_at ASC
    """, conversation_id)

    if not messages:
        print("Conversation not found!")
        await conn.close()
        return

    for msg in messages:
        print(f"\n[{msg['role'].upper()}] ({msg['created_at']})")
        print(f"{msg['content']}")

        if msg['role'] == 'assistant' and msg['metadata']:
            meta = msg['metadata']
            print(f"\nMetadata:")
            print(f"  Intent: {meta.get('intent')}")
            print(f"  Language: {meta.get('language')}")
            print(f"  Completeness Score: {meta.get('completeness_score')}%")
            print(f"  Iterations: {meta.get('iterations')}")
            print(f"  Attributes: {meta.get('attributes')}")

        print("-" * 120)

    await conn.close()


async def view_statistics():
    """View statistics"""
    conn = await asyncpg.connect(**DB_CONFIG)

    print("\n" + "=" * 120)
    print("STATISTICS")
    print("=" * 120)

    # By language
    print("\nBy Language:")
    lang_stats = await conn.fetch("""
        SELECT
            m.metadata->>'language' as language,
            COUNT(*) as count,
            ROUND(AVG((m.metadata->>'completeness_score')::INT), 1) as avg_score,
            ROUND(AVG((m.metadata->>'iterations')::INT), 1) as avg_iterations
        FROM public.flow1_messages m
        WHERE m.role = 'assistant'
        GROUP BY m.metadata->>'language'
        ORDER BY count DESC
    """)

    print(f"{'Language':<12s} {'Count':<8s} {'Avg Score':<12s} {'Avg Iterations'}")
    print("-" * 50)
    for stat in lang_stats:
        print(f"{stat['language'].upper():<12s} {stat['count']:<8d} "
              f"{stat['avg_score']:>6.1f}%      {stat['avg_iterations']:>4.1f}")

    # By intent
    print("\n\nBy Intent:")
    intent_stats = await conn.fetch("""
        SELECT
            m.metadata->>'intent' as intent,
            COUNT(*) as count,
            ROUND(AVG((m.metadata->>'completeness_score')::INT), 1) as avg_score
        FROM public.flow1_messages m
        WHERE m.role = 'assistant'
        GROUP BY m.metadata->>'intent'
        ORDER BY count DESC
    """)

    print(f"{'Intent':<15s} {'Count':<8s} {'Avg Score'}")
    print("-" * 40)
    for stat in intent_stats:
        print(f"{stat['intent']:<15s} {stat['count']:<8d} {stat['avg_score']:>6.1f}%")

    # By score range
    print("\n\nBy Completeness Range:")
    score_stats = await conn.fetch("""
        SELECT
            CASE
                WHEN (m.metadata->>'completeness_score')::INT = 0 THEN '0%'
                WHEN (m.metadata->>'completeness_score')::INT < 50 THEN '1-49%'
                WHEN (m.metadata->>'completeness_score')::INT < 80 THEN '50-79%'
                ELSE '80-100%'
            END as score_range,
            COUNT(*) as count
        FROM public.flow1_messages m
        WHERE m.role = 'assistant'
        GROUP BY score_range
        ORDER BY score_range
    """)

    print(f"{'Score Range':<15s} {'Count'}")
    print("-" * 30)
    for stat in score_stats:
        print(f"{stat['score_range']:<15s} {stat['count']}")

    print("\n" + "=" * 120)

    await conn.close()


async def main():
    """Main entry point"""
    print("\n" + "=" * 120)
    print("FLOW 1 CHAT HISTORY VIEWER")
    print("=" * 120)

    # View all conversations
    await view_all_conversations()

    # View statistics
    await view_statistics()

    # Example: View specific conversation
    print("\n" + "=" * 120)
    print("SAMPLE CONVERSATION (First one)")
    print("=" * 120)

    # Get first conversation ID
    conn = await asyncpg.connect(**DB_CONFIG)
    first_conv = await conn.fetchval("""
        SELECT conversation_id
        FROM public.flow1_conversations
        ORDER BY created_at DESC
        LIMIT 1
    """)
    await conn.close()

    if first_conv:
        await view_single_conversation(first_conv)


if __name__ == "__main__":
    asyncio.run(main())

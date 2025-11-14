"""View AI-to-AI Chat History from PostgreSQL"""

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

async def view_all_ai_conversations():
    """View summary of all AI-to-AI conversations"""
    conn = await asyncpg.connect(**DB_CONFIG)

    print("=" * 120)
    print("AI-TO-AI FLOW 1 CHAT HISTORY - ALL CONVERSATIONS")
    print("=" * 120)

    # Get all conversations
    conversations = await conn.fetch("""
        SELECT
            conversation_id,
            scenario_name,
            total_turns,
            final_score,
            created_at
        FROM public.flow1_ai_conversations
        ORDER BY created_at DESC
    """)

    print(f"\nTotal Conversations: {len(conversations)}\n")
    print(f"{'#':<4s} {'Conversation ID':<35s} {'Scenario':<50s} {'Turns':<8s} {'Score'}")
    print("-" * 120)

    for i, conv in enumerate(conversations, 1):
        print(f"{i:<4d} "
              f"{conv['conversation_id']:<35s} "
              f"{conv['scenario_name']:<50s} "
              f"{conv['total_turns']:>2d}       "
              f"{conv['final_score']:>3d}%")

    print("\n" + "=" * 120)

    await conn.close()


async def view_single_ai_conversation(conversation_id: str):
    """View detailed AI-to-AI conversation"""
    conn = await asyncpg.connect(**DB_CONFIG)

    print("\n" + "=" * 120)
    print(f"CONVERSATION DETAILS: {conversation_id}")
    print("=" * 120)

    # Get conversation info
    conv = await conn.fetchrow("""
        SELECT scenario_name, persona, total_turns, final_score
        FROM public.flow1_ai_conversations
        WHERE conversation_id = $1
    """, conversation_id)

    if not conv:
        print("Conversation not found!")
        await conn.close()
        return

    print(f"\nScenario: {conv['scenario_name']}")
    print(f"Total Turns: {conv['total_turns']}")
    print(f"Final Score: {conv['final_score']}%")
    print(f"\nPersona:\n{conv['persona']}")
    print("=" * 120)

    # Get messages
    messages = await conn.fetch("""
        SELECT
            turn_number,
            role,
            content,
            metadata,
            created_at
        FROM public.flow1_ai_messages
        WHERE conversation_id = $1
        ORDER BY turn_number ASC, created_at ASC
    """, conversation_id)

    if not messages:
        print("No messages found!")
        await conn.close()
        return

    current_turn = 0
    for msg in messages:
        if msg['turn_number'] != current_turn:
            current_turn = msg['turn_number']
            print(f"\n{'=' * 120}")
            print(f"TURN {current_turn}")
            print(f"{'=' * 120}")

        print(f"\n[{msg['role'].upper()}]")
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


async def main():
    """Main entry point"""
    print("\n" + "=" * 120)
    print("AI-TO-AI FLOW 1 CHAT HISTORY VIEWER")
    print("=" * 120)

    # View all conversations
    await view_all_ai_conversations()

    # Get first conversation ID
    conn = await asyncpg.connect(**DB_CONFIG)
    first_conv = await conn.fetchval("""
        SELECT conversation_id
        FROM public.flow1_ai_conversations
        ORDER BY created_at DESC
        LIMIT 1
    """)
    await conn.close()

    if first_conv:
        print("\n" + "=" * 120)
        print("SHOWING FIRST CONVERSATION (Latest)")
        print("=" * 120)
        await view_single_ai_conversation(first_conv)


if __name__ == "__main__":
    asyncio.run(main())

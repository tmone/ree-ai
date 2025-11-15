"""
Extract AI-to-AI Test Results from Database
Queries the full conversation history for user review
"""
import asyncio
import asyncpg
import json
from datetime import datetime

DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}


async def extract_test_results():
    """Extract all AI-to-AI test conversations"""

    conn = await asyncpg.connect(**DB_CONFIG)
    print("=" * 100)
    print("📊 EXTRACTING AI-TO-AI TEST RESULTS")
    print("=" * 100)
    print()

    # Get all conversations
    conversations = await conn.fetch("""
        SELECT conversation_id, scenario_name, persona, total_turns, final_score, created_at
        FROM public.flow1_ai_conversations
        ORDER BY created_at DESC
    """)

    if not conversations:
        print("❌ No test conversations found yet. Test may still be running.")
        await conn.close()
        return

    print(f"✅ Found {len(conversations)} test conversations\n")

    all_results = []

    for conv in conversations:
        conv_id = conv['conversation_id']
        scenario = conv['scenario_name']

        print(f"\n{'=' * 100}")
        print(f"🎭 SCENARIO: {scenario}")
        print(f"{'=' * 100}")
        print(f"Conversation ID: {conv_id}")
        print(f"Total Turns: {conv['total_turns']}")
        print(f"Final Score: {conv['final_score']}%")
        print(f"Created: {conv['created_at']}")
        print()

        # Get all messages for this conversation
        messages = await conn.fetch("""
            SELECT turn_number, role, content, metadata, created_at
            FROM public.flow1_ai_messages
            WHERE conversation_id = $1
            ORDER BY turn_number ASC
        """, conv_id)

        conversation_history = []

        for msg in messages:
            role_emoji = "👤" if msg['role'] == 'user' else "🤖"
            role_name = "User (Ollama AI)" if msg['role'] == 'user' else "System (Orchestrator)"

            print(f"{'—' * 100}")
            print(f"Turn {msg['turn_number']}: {role_emoji} {role_name}")
            print(f"{'—' * 100}")
            print(f"{msg['content']}")

            if msg['metadata']:
                try:
                    metadata = json.loads(msg['metadata']) if isinstance(msg['metadata'], str) else msg['metadata']
                    print(f"\n📊 Metadata: {json.dumps(metadata, ensure_ascii=False)}")
                except:
                    pass

            print()

            conversation_history.append({
                "turn": msg['turn_number'],
                "role": msg['role'],
                "content": msg['content'],
                "metadata": msg['metadata'],
                "timestamp": msg['created_at'].isoformat() if msg['created_at'] else None
            })

        all_results.append({
            "conversation_id": conv_id,
            "scenario": scenario,
            "persona": conv['persona'],
            "total_turns": conv['total_turns'],
            "final_score": conv['final_score'],
            "created_at": conv['created_at'].isoformat(),
            "messages": conversation_history
        })

    await conn.close()

    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"ai_to_ai_test_results_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_conversations": len(all_results),
                "total_scenarios": len(set(r['scenario'] for r in all_results))
            },
            "results": all_results
        }, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 100}")
    print(f"📊 SUMMARY")
    print(f"{'=' * 100}")
    print(f"\nTotal Conversations: {len(all_results)}")
    print(f"\n{'Scenario':<50s} {'Turns':<8s} {'Final Score'}")
    print("-" * 100)

    for r in all_results:
        print(f"{r['scenario']:<50s} {r['total_turns']:<8d} {r['final_score']:>3d}%")

    print(f"\n✅ Full results saved to: {output_file}")
    print(f"{'=' * 100}\n")


if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    asyncio.run(extract_test_results())

"""
Monitor AI-to-AI Test Progress
Checks database for completed scenarios
"""
import asyncio
import asyncpg
import time
from datetime import datetime

DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}


async def monitor_progress():
    """Monitor test progress"""

    print("=" * 100)
    print("📊 MONITORING AI-TO-AI TEST PROGRESS")
    print("=" * 100)
    print("Checking every 30 seconds...")
    print()

    previous_count = 0
    total_expected = 14  # 14 scenarios in demo_flow1_ai_to_ai.py

    while True:
        try:
            conn = await asyncpg.connect(**DB_CONFIG)

            # Get completed conversations
            conversations = await conn.fetch("""
                SELECT conversation_id, scenario_name, total_turns, final_score, created_at
                FROM public.flow1_ai_conversations
                ORDER BY created_at ASC
            """)

            current_count = len(conversations)

            if current_count != previous_count:
                print(f"\n{datetime.now().strftime('%H:%M:%S')} - 🔄 Progress Update:")
                print(f"Completed: {current_count}/{total_expected} scenarios")
                print("-" * 100)

                for i, conv in enumerate(conversations, 1):
                    status = "✅" if i <= current_count else "⏳"
                    score = conv['final_score'] if conv['final_score'] else 0
                    print(f"{status} {i}. {conv['scenario_name']:<50s} | Turns: {conv['total_turns']:<3d} | Score: {score:>3d}%")

                print("-" * 100)

                if current_count >= total_expected:
                    print(f"\n🎉 ALL {total_expected} SCENARIOS COMPLETED!")
                    print(f"\nRun this command to extract full results:")
                    print(f"  python scripts/extract_ai_test_results.py")
                    print()
                    await conn.close()
                    break

                previous_count = current_count

            await conn.close()
            await asyncio.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            print("\n\n⚠️ Monitor stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(30)


if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    asyncio.run(monitor_progress())

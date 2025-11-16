"""Real-time AI-to-AI Test Viewer - Flask Web UI"""

from flask import Flask, render_template, jsonify, send_from_directory
import os
import re
import json
from datetime import datetime
import asyncio
import asyncpg

app = Flask(__name__)

# Database config
DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}

# Test output file path
TEST_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "tests", "test_prompt_engineering.txt")


def parse_test_progress():
    """Parse current test progress from output file"""
    if not os.path.exists(TEST_OUTPUT_FILE):
        return {
            "total_scenarios": 19,
            "completed": 0,
            "running_scenario": None,
            "current_turn": 0,
            "results": [],
            "status": "not_started"
        }

    with open(TEST_OUTPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count completed scenarios
    final_results = re.findall(r'📊 FINAL RESULT.*?Completeness Score: (\d+)%', content, re.DOTALL)
    completed = len(final_results)

    # Get latest scenario info
    scenario_matches = list(re.finditer(r'🎭 SCENARIO (\d+)/19: (.*?)(?=\n)', content))
    running_scenario = scenario_matches[-1].group(2) if scenario_matches else None
    scenario_num = int(scenario_matches[-1].group(1)) if scenario_matches else 0

    # Get current turn
    turn_matches = list(re.finditer(r'🔄 Turn (\d+):', content))
    current_turn = int(turn_matches[-1].group(1)) if turn_matches else 0

    # Parse results
    results = []
    for i, score in enumerate(final_results, 1):
        results.append({
            "scenario_num": i,
            "score": int(score),
            "completed": True
        })

    # Add current running scenario
    if scenario_num > completed:
        results.append({
            "scenario_num": scenario_num,
            "score": 0,
            "completed": False,
            "current_turn": current_turn
        })

    # Calculate average
    avg_score = sum(r['score'] for r in results if r['completed']) / max(completed, 1)

    # Check if test is complete
    status = "completed" if completed >= 19 else "running" if completed > 0 else "not_started"

    return {
        "total_scenarios": 19,
        "completed": completed,
        "running_scenario": running_scenario,
        "current_turn": current_turn,
        "scenario_num": scenario_num,
        "results": results,
        "average_score": round(avg_score, 2),
        "status": status,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


async def get_conversation_history():
    """Get recent AI-to-AI conversations from database"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        conversations = await conn.fetch("""
            SELECT
                conversation_id,
                scenario_name,
                total_turns,
                final_score,
                created_at
            FROM public.flow1_ai_conversations
            ORDER BY created_at DESC
            LIMIT 20
        """)
        await conn.close()

        return [
            {
                "conversation_id": str(conv['conversation_id']),
                "scenario_name": conv['scenario_name'],
                "total_turns": conv['total_turns'],
                "final_score": conv['final_score'],
                "created_at": conv['created_at'].strftime("%Y-%m-%d %H:%M:%S")
            }
            for conv in conversations
        ]
    except Exception as e:
        print(f"Database error: {e}")
        return []


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('test_viewer.html')


@app.route('/api/progress')
def api_progress():
    """API endpoint for current test progress"""
    progress = parse_test_progress()
    return jsonify(progress)


@app.route('/api/history')
def api_history():
    """API endpoint for conversation history"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    history = loop.run_until_complete(get_conversation_history())
    loop.close()
    return jsonify(history)


@app.route('/api/logs')
def api_logs():
    """API endpoint for recent test logs"""
    if not os.path.exists(TEST_OUTPUT_FILE):
        return jsonify({"logs": ""})

    with open(TEST_OUTPUT_FILE, 'r', encoding='utf-8') as f:
        # Get last 100 lines
        lines = f.readlines()
        recent_logs = ''.join(lines[-100:])

    return jsonify({"logs": recent_logs})


@app.route('/api/conversation/<conversation_id>')
def api_conversation_detail(conversation_id):
    """API endpoint for detailed conversation messages"""
    async def get_messages():
        try:
            conn = await asyncpg.connect(**DB_CONFIG)
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
            await conn.close()

            result = []
            for msg in messages:
                result.append({
                    "turn_number": msg['turn_number'],
                    "role": msg['role'],
                    "content": msg['content'],
                    "metadata": msg['metadata'] if msg['metadata'] else {},
                    "created_at": msg['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                })
            return result
        except Exception as e:
            print(f"Error fetching conversation: {e}")
            return []

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    messages = loop.run_until_complete(get_messages())
    loop.close()
    return jsonify(messages)


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("AI-TO-AI TEST VIEWER")
    print("=" * 80)
    print(f"Dashboard: http://localhost:5001")
    print(f"Monitoring: {TEST_OUTPUT_FILE}")
    print("=" * 80 + "\n")

    app.run(host='0.0.0.0', port=5001, debug=False)

"""Simple Web UI to View AI-to-AI Conversation Details"""

from flask import Flask, render_template_string, jsonify
import asyncio
import asyncpg

app = Flask(__name__)

DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Conversation Viewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f2f5;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .conv-list {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .conv-item {
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .conv-item:hover {
            background: #f8f9fa;
            border-color: #667eea;
        }
        .conv-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
        }
        .conv-title { font-weight: bold; color: #333; }
        .conv-score {
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 14px;
        }
        .score-good { background: #d4edda; color: #155724; }
        .score-medium { background: #fff3cd; color: #856404; }
        .score-bad { background: #f8d7da; color: #721c24; }
        .conv-meta { font-size: 12px; color: #666; }
        .messages {
            background: white;
            padding: 20px;
            border-radius: 8px;
            display: none;
        }
        .message {
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #ddd;
        }
        .message.user {
            background: #e3f2fd;
            border-left-color: #2196f3;
        }
        .message.assistant {
            background: #f3e5f5;
            border-left-color: #9c27b0;
        }
        .message-header {
            font-weight: bold;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
        }
        .message-content {
            white-space: pre-wrap;
            line-height: 1.6;
        }
        .metadata {
            margin-top: 10px;
            padding: 10px;
            background: rgba(0,0,0,0.05);
            border-radius: 4px;
            font-size: 12px;
        }
        .back-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin-bottom: 15px;
        }
        .back-btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Conversation Detail Viewer</h1>
            <p>Click on any conversation to view full message history</p>
        </div>

        <div class="conv-list" id="conv-list">
            <div style="text-align: center; padding: 40px;">Loading conversations...</div>
        </div>

        <div class="messages" id="messages">
            <button class="back-btn" onclick="showList()">Back to List</button>
            <div id="message-content"></div>
        </div>
    </div>

    <script>
        let conversations = [];

        async function loadConversations() {
            const response = await fetch('/api/conversations');
            conversations = await response.json();
            renderConversations();
        }

        function renderConversations() {
            const list = document.getElementById('conv-list');
            if (conversations.length === 0) {
                list.innerHTML = '<div style="text-align: center; color: #666;">No conversations found</div>';
                return;
            }

            list.innerHTML = conversations.map((conv, idx) => {
                let scoreClass = 'score-medium';
                if (conv.final_score >= 80) scoreClass = 'score-good';
                else if (conv.final_score < 60) scoreClass = 'score-bad';

                return `
                    <div class="conv-item" onclick="viewConversation('${conv.conversation_id}')">
                        <div class="conv-header">
                            <div class="conv-title">${idx + 1}. ${conv.scenario_name}</div>
                            <div class="conv-score ${scoreClass}">${conv.final_score}%</div>
                        </div>
                        <div class="conv-meta">
                            Turns: ${conv.total_turns} | Created: ${conv.created_at}
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function viewConversation(convId) {
            const response = await fetch(`/api/conversation/${convId}`);
            const messages = await response.json();

            const messageDiv = document.getElementById('message-content');
            messageDiv.innerHTML = messages.map(msg => `
                <div class="message ${msg.role}">
                    <div class="message-header">
                        <span>${msg.role.toUpperCase()} - Turn ${msg.turn_number}</span>
                        <span style="font-size: 12px; color: #666;">${msg.created_at}</span>
                    </div>
                    <div class="message-content">${escapeHtml(msg.content)}</div>
                    ${msg.metadata && Object.keys(msg.metadata).length > 0 ? `
                        <div class="metadata">
                            <strong>Metadata:</strong><br>
                            <pre style="margin: 5px 0; white-space: pre-wrap;">${JSON.stringify(msg.metadata, null, 2)}</pre>
                        </div>
                    ` : ''}
                </div>
            `).join('');

            document.getElementById('conv-list').style.display = 'none';
            document.getElementById('messages').style.display = 'block';
        }

        function showList() {
            document.getElementById('conv-list').style.display = 'block';
            document.getElementById('messages').style.display = 'none';
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Load on start
        loadConversations();

        // Auto-refresh every 30 seconds
        setInterval(loadConversations, 30000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/conversations')
def api_conversations():
    """Get list of all conversations"""
    async def get_data():
        try:
            conn = await asyncpg.connect(**DB_CONFIG)
            convs = await conn.fetch("""
                SELECT
                    conversation_id,
                    scenario_name,
                    total_turns,
                    final_score,
                    created_at
                FROM public.flow1_ai_conversations
                ORDER BY created_at DESC
                LIMIT 50
            """)
            await conn.close()

            return [
                {
                    "conversation_id": str(c['conversation_id']),
                    "scenario_name": c['scenario_name'],
                    "total_turns": c['total_turns'],
                    "final_score": c['final_score'],
                    "created_at": c['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                }
                for c in convs
            ]
        except Exception as e:
            print(f"Error: {e}")
            return []

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    data = loop.run_until_complete(get_data())
    loop.close()
    return jsonify(data)


@app.route('/api/conversation/<conversation_id>')
def api_conversation(conversation_id):
    """Get detailed messages for a conversation"""
    async def get_messages():
        try:
            conn = await asyncpg.connect(**DB_CONFIG)
            msgs = await conn.fetch("""
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

            return [
                {
                    "turn_number": m['turn_number'],
                    "role": m['role'],
                    "content": m['content'],
                    "metadata": m['metadata'] if m['metadata'] else {},
                    "created_at": m['created_at'].strftime("%Y-%m-%d %H:%M:%S")
                }
                for m in msgs
            ]
        except Exception as e:
            print(f"Error: {e}")
            return []

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    messages = loop.run_until_complete(get_messages())
    loop.close()
    return jsonify(messages)


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("CONVERSATION VIEWER")
    print("=" * 80)
    print("URL: http://localhost:5002")
    print("=" * 80 + "\n")

    app.run(host='0.0.0.0', port=5002, debug=False)

"""
Web UI to View AI-to-AI Flow 1 Chat History
============================================
View TRUE AI conversations from flow1_ai_conversations and flow1_ai_messages tables
Run this script and open http://localhost:5001 in your browser
"""

from flask import Flask, render_template_string, jsonify
import asyncio
import asyncpg
import json
from datetime import datetime

app = Flask(__name__)

DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI-to-AI Flow 1 Chat History</title>
    <meta charset="utf-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .badge-success {
            background: #2ecc71;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }
        .conversation-list {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .conversation-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            transition: background 0.2s;
        }
        .conversation-item:hover {
            background: #f9f9f9;
        }
        .conversation-item:last-child {
            border-bottom: none;
        }
        .conv-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        .conv-id {
            font-family: monospace;
            color: #666;
            font-size: 12px;
        }
        .conv-meta {
            display: flex;
            gap: 10px;
            font-size: 13px;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-turns {
            background: #3498db;
            color: white;
        }
        .badge-score {
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: 600;
        }
        .score-high { background: #2ecc71; color: white; }
        .score-medium { background: #f39c12; color: white; }
        .score-low { background: #e74c3c; color: white; }
        .conv-scenario {
            color: #2c3e50;
            font-weight: 500;
            margin-bottom: 8px;
        }
        .conv-persona {
            color: #555;
            font-size: 13px;
            line-height: 1.4;
            white-space: pre-wrap;
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            border-left: 3px solid #3498db;
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            padding: 20px;
            overflow: auto;
        }
        .modal-content {
            background: white;
            max-width: 900px;
            margin: 50px auto;
            border-radius: 8px;
            padding: 30px;
            position: relative;
        }
        .close {
            position: absolute;
            top: 15px;
            right: 20px;
            font-size: 28px;
            cursor: pointer;
            color: #999;
        }
        .close:hover {
            color: #333;
        }
        .message {
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 8px;
        }
        .message-user {
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }
        .message-assistant {
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }
        .message-role {
            font-weight: bold;
            margin-bottom: 8px;
            text-transform: uppercase;
            font-size: 12px;
        }
        .message-content {
            white-space: pre-wrap;
            line-height: 1.6;
        }
        .turn-label {
            background: #34495e;
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            margin: 20px 0 10px 0;
            font-weight: 600;
            font-size: 14px;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI-to-AI Flow 1 Chat History</h1>
        <p>TRUE AI conversations (Ollama AI vs Orchestrator)</p>
        <span class="badge-success">Real Multi-Turn Conversations</span>
    </div>

    <div class="stats" id="stats">
        <div class="stat-card">
            <div class="stat-label">Total Scenarios</div>
            <div class="stat-value" id="total-scenarios">-</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Average Turns</div>
            <div class="stat-value" id="avg-turns">-</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Average Score</div>
            <div class="stat-value" id="avg-score">-</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Complete (100%)</div>
            <div class="stat-value" id="complete-count">-</div>
        </div>
    </div>

    <div class="conversation-list" id="conversation-list">
        <div class="loading">Loading AI-to-AI conversations...</div>
    </div>

    <div id="modal" class="modal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <span class="close" onclick="closeModal()">&times;</span>
            <div id="modal-body"></div>
        </div>
    </div>

    <script>
        let allConversations = [];

        async function loadConversations() {
            try {
                const response = await fetch('/api/ai-conversations');
                const data = await response.json();
                allConversations = data.conversations;

                // Update stats
                document.getElementById('total-scenarios').textContent = data.stats.total;
                document.getElementById('avg-turns').textContent = data.stats.avg_turns.toFixed(1);
                document.getElementById('avg-score').textContent = data.stats.avg_score.toFixed(1) + '%';
                document.getElementById('complete-count').textContent = data.stats.complete_count;

                // Display conversations
                displayConversations(allConversations);
            } catch (error) {
                document.getElementById('conversation-list').innerHTML =
                    '<div class="loading">Error loading conversations: ' + error.message + '</div>';
            }
        }

        function displayConversations(conversations) {
            const list = document.getElementById('conversation-list');

            if (conversations.length === 0) {
                list.innerHTML = '<div class="loading">No AI-to-AI conversations found</div>';
                return;
            }

            list.innerHTML = conversations.map(conv => {
                const scoreClass = conv.score >= 80 ? 'score-high' :
                                 conv.score >= 50 ? 'score-medium' : 'score-low';

                return `
                    <div class="conversation-item" onclick="viewConversation('${conv.conversation_id}')">
                        <div class="conv-header">
                            <div class="conv-id">${conv.conversation_id}</div>
                            <div class="conv-meta">
                                <span class="badge badge-turns">${conv.turns} turns</span>
                                <span class="badge-score ${scoreClass}">${conv.score}%</span>
                            </div>
                        </div>
                        <div class="conv-scenario">
                            ${conv.scenario_name}
                        </div>
                        <div class="conv-persona">
                            ${conv.persona.substring(0, 200)}${conv.persona.length > 200 ? '...' : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function viewConversation(conversationId) {
            try {
                const response = await fetch(`/api/ai-conversation/${conversationId}`);
                const data = await response.json();

                const modalBody = document.getElementById('modal-body');
                modalBody.innerHTML = `
                    <h2>${data.scenario_name}</h2>
                    <p style="color: #666; font-family: monospace; margin-bottom: 10px;">${conversationId}</p>
                    <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 20px;">
                        <strong>Persona:</strong>
                        <pre style="margin: 5px 0; white-space: pre-wrap; font-size: 12px;">${data.persona}</pre>
                    </div>
                    ${data.messages.map((msg, idx) => {
                        if (idx % 2 === 0) {
                            return `
                                <div class="turn-label">Turn ${Math.floor(idx / 2) + 1}</div>
                                <div class="message message-${msg.role}">
                                    <div class="message-role">${msg.role === 'user' ? 'User (Ollama AI)' : 'System (Orchestrator)'}</div>
                                    <div class="message-content">${msg.content}</div>
                                </div>
                            `;
                        } else {
                            return `
                                <div class="message message-${msg.role}">
                                    <div class="message-role">${msg.role === 'user' ? 'User (Ollama AI)' : 'System (Orchestrator)'}</div>
                                    <div class="message-content">${msg.content}</div>
                                    ${msg.metadata ? `
                                        <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.1); font-size: 12px; color: #666;">
                                            Completeness: ${msg.metadata.completeness_score}% |
                                            Iterations: ${msg.metadata.iterations} |
                                            Attributes: ${JSON.stringify(msg.metadata.attributes)}
                                        </div>
                                    ` : ''}
                                </div>
                            `;
                        }
                    }).join('')}
                `;

                document.getElementById('modal').style.display = 'block';
            } catch (error) {
                alert('Error loading conversation: ' + error.message);
            }
        }

        function closeModal(event) {
            document.getElementById('modal').style.display = 'none';
        }

        // Load conversations on page load
        loadConversations();
    </script>
</body>
</html>
"""

async def get_db_connection():
    """Get database connection"""
    return await asyncpg.connect(**DB_CONFIG)

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ai-conversations')
def get_ai_conversations():
    """API to get all AI-to-AI conversations"""
    async def fetch_data():
        conn = await get_db_connection()

        conversations = await conn.fetch("""
            SELECT
                conversation_id,
                scenario_name,
                persona,
                total_turns,
                final_score,
                created_at
            FROM public.flow1_ai_conversations
            ORDER BY created_at DESC
        """)

        # Calculate stats
        total = len(conversations)
        avg_turns = sum(c['total_turns'] for c in conversations) / total if total > 0 else 0
        avg_score = sum(c['final_score'] for c in conversations) / total if total > 0 else 0
        complete_count = sum(1 for c in conversations if c['final_score'] >= 100)

        await conn.close()

        return {
            'conversations': [
                {
                    'conversation_id': c['conversation_id'],
                    'scenario_name': c['scenario_name'],
                    'persona': c['persona'],
                    'turns': c['total_turns'],
                    'score': c['final_score'],
                    'created_at': str(c['created_at'])
                }
                for c in conversations
            ],
            'stats': {
                'total': total,
                'avg_turns': avg_turns,
                'avg_score': avg_score,
                'complete_count': complete_count
            }
        }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(fetch_data())
    loop.close()

    return jsonify(result)

@app.route('/api/ai-conversation/<conversation_id>')
def get_ai_conversation(conversation_id):
    """API to get specific AI-to-AI conversation"""
    async def fetch_data():
        conn = await get_db_connection()

        # Get conversation info
        conv = await conn.fetchrow("""
            SELECT scenario_name, persona
            FROM public.flow1_ai_conversations
            WHERE conversation_id = $1
        """, conversation_id)

        # Get messages
        messages = await conn.fetch("""
            SELECT
                role,
                content,
                metadata,
                created_at
            FROM public.flow1_ai_messages
            WHERE conversation_id = $1
            ORDER BY turn_number ASC, created_at ASC
        """, conversation_id)

        await conn.close()

        return {
            'conversation_id': conversation_id,
            'scenario_name': conv['scenario_name'] if conv else 'Unknown',
            'persona': conv['persona'] if conv else 'Unknown',
            'messages': [
                {
                    'role': m['role'],
                    'content': m['content'],
                    'metadata': m['metadata'] if m['metadata'] else None,
                    'created_at': str(m['created_at'])
                }
                for m in messages
            ]
        }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(fetch_data())
    loop.close()

    return jsonify(result)

if __name__ == '__main__':
    print("=" * 80)
    print("AI-TO-AI FLOW 1 CHAT HISTORY WEB VIEWER")
    print("=" * 80)
    print("\nStarting web server...")
    print("\nOpen your browser and go to:")
    print("   >> http://localhost:5001")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80)

    app.run(host='0.0.0.0', port=5001, debug=False)

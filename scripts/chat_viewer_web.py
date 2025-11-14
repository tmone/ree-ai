"""
Simple Web UI to View Flow 1 Chat History
==========================================
Run this script and open http://localhost:5000 in your browser
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
    <title>Flow 1 Chat History Viewer</title>
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
        .filters {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .filter-group {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        .filter-group label {
            font-weight: 500;
            color: #555;
        }
        select, input {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
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
            margin-bottom: 8px;
        }
        .conv-id {
            font-family: monospace;
            color: #666;
            font-size: 12px;
        }
        .conv-meta {
            display: flex;
            gap: 15px;
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
        .badge-lang {
            background: #3498db;
            color: white;
        }
        .badge-intent {
            background: #9b59b6;
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
        .conv-query {
            color: #2c3e50;
            margin-top: 8px;
            font-size: 14px;
        }
        .conv-response {
            color: #555;
            margin-top: 5px;
            font-size: 13px;
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
            max-width: 800px;
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
        .metadata {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid rgba(0,0,0,0.1);
            font-size: 12px;
            color: #666;
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
        <h1>🤖 Flow 1 Chat History Viewer</h1>
        <p>Database: 103.153.74.213:5432/ree_ai</p>
    </div>

    <div class="stats" id="stats">
        <div class="stat-card">
            <div class="stat-label">Total Conversations</div>
            <div class="stat-value" id="total-convs">-</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Average Score</div>
            <div class="stat-value" id="avg-score">-</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Languages</div>
            <div class="stat-value" id="languages">-</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Complete (≥80%)</div>
            <div class="stat-value" id="complete-count">-</div>
        </div>
    </div>

    <div class="filters">
        <div class="filter-group">
            <label>Filter by Language:</label>
            <select id="filter-lang" onchange="filterConversations()">
                <option value="">All Languages</option>
                <option value="vi">Vietnamese</option>
                <option value="en">English</option>
                <option value="th">Thai</option>
                <option value="ja">Japanese</option>
            </select>

            <label>Filter by Intent:</label>
            <select id="filter-intent" onchange="filterConversations()">
                <option value="">All Intents</option>
                <option value="POST_SALE">POST_SALE</option>
                <option value="POST_RENT">POST_RENT</option>
            </select>

            <label>Min Score:</label>
            <input type="number" id="filter-score" min="0" max="100" placeholder="0-100"
                   onchange="filterConversations()" style="width: 100px;">
        </div>
    </div>

    <div class="conversation-list" id="conversation-list">
        <div class="loading">Loading conversations...</div>
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
                const response = await fetch('/api/conversations');
                const data = await response.json();
                allConversations = data.conversations;

                // Update stats
                document.getElementById('total-convs').textContent = data.stats.total;
                document.getElementById('avg-score').textContent = data.stats.avg_score.toFixed(1) + '%';
                document.getElementById('languages').textContent = data.stats.languages.join(', ').toUpperCase();
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
                list.innerHTML = '<div class="loading">No conversations found</div>';
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
                                <span class="badge badge-lang">${conv.language}</span>
                                <span class="badge badge-intent">${conv.intent}</span>
                                <span class="badge-score ${scoreClass}">${conv.score}%</span>
                                <span style="color: #666;">Iter: ${conv.iterations}</span>
                            </div>
                        </div>
                        <div class="conv-query">
                            <strong>User:</strong> ${conv.user_query}
                        </div>
                        <div class="conv-response">
                            ${conv.assistant_response.substring(0, 200)}${conv.assistant_response.length > 200 ? '...' : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }

        function filterConversations() {
            const lang = document.getElementById('filter-lang').value;
            const intent = document.getElementById('filter-intent').value;
            const minScore = parseInt(document.getElementById('filter-score').value) || 0;

            const filtered = allConversations.filter(conv => {
                if (lang && conv.language !== lang) return false;
                if (intent && conv.intent !== intent) return false;
                if (conv.score < minScore) return false;
                return true;
            });

            displayConversations(filtered);
        }

        async function viewConversation(conversationId) {
            try {
                const response = await fetch(`/api/conversation/${conversationId}`);
                const data = await response.json();

                const modalBody = document.getElementById('modal-body');
                modalBody.innerHTML = `
                    <h2>Conversation Details</h2>
                    <p style="color: #666; font-family: monospace; margin-bottom: 20px;">${conversationId}</p>
                    ${data.messages.map(msg => `
                        <div class="message message-${msg.role}">
                            <div class="message-role">${msg.role}</div>
                            <div class="message-content">${msg.content}</div>
                            ${msg.metadata ? `
                                <div class="metadata">
                                    Intent: ${msg.metadata.intent} |
                                    Language: ${msg.metadata.language} |
                                    Score: ${msg.metadata.completeness_score}% |
                                    Iterations: ${msg.metadata.iterations}
                                    ${msg.metadata.attributes ? '<br>Attributes: ' + JSON.stringify(msg.metadata.attributes) : ''}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
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

@app.route('/api/conversations')
def get_conversations():
    """API to get all conversations"""
    async def fetch_data():
        conn = await get_db_connection()

        conversations = await conn.fetch("""
            SELECT
                c.conversation_id,
                c.user_id,
                c.created_at,
                m.metadata->>'language' as language,
                m.metadata->>'intent' as intent,
                (m.metadata->>'completeness_score')::INT as score,
                (m.metadata->>'iterations')::INT as iterations,
                user_msg.content as user_query,
                m.content as assistant_response
            FROM public.flow1_conversations c
            JOIN public.flow1_messages m ON c.conversation_id = m.conversation_id AND m.role = 'assistant'
            LEFT JOIN public.flow1_messages user_msg ON c.conversation_id = user_msg.conversation_id AND user_msg.role = 'user'
            ORDER BY c.created_at DESC
        """)

        # Calculate stats
        total = len(conversations)
        avg_score = sum(c['score'] for c in conversations) / total if total > 0 else 0
        languages = list(set(c['language'] for c in conversations))
        complete_count = sum(1 for c in conversations if c['score'] >= 80)

        await conn.close()

        return {
            'conversations': [
                {
                    'conversation_id': c['conversation_id'],
                    'language': c['language'],
                    'intent': c['intent'],
                    'score': c['score'],
                    'iterations': c['iterations'],
                    'user_query': c['user_query'],
                    'assistant_response': c['assistant_response'],
                    'created_at': str(c['created_at'])
                }
                for c in conversations
            ],
            'stats': {
                'total': total,
                'avg_score': avg_score,
                'languages': languages,
                'complete_count': complete_count
            }
        }

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(fetch_data())
    loop.close()

    return jsonify(result)

@app.route('/api/conversation/<conversation_id>')
def get_conversation(conversation_id):
    """API to get specific conversation"""
    async def fetch_data():
        conn = await get_db_connection()

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

        await conn.close()

        return {
            'conversation_id': conversation_id,
            'messages': [
                {
                    'role': m['role'],
                    'content': m['content'],
                    'metadata': dict(m['metadata']) if m['metadata'] else None,
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
    print("FLOW 1 CHAT HISTORY WEB VIEWER")
    print("=" * 80)
    print("\nStarting web server...")
    print("\nOpen your browser and go to:")
    print("   >> http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 80)

    app.run(host='0.0.0.0', port=5000, debug=False)

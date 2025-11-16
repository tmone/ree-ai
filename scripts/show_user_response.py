import asyncio
import asyncpg
import json

async def show_real_user_response():
    conn = await asyncpg.connect(
        host='103.153.74.213',
        port=5432,
        database='ree_ai',
        user='ree_ai_user',
        password='ree_ai_pass_2025'
    )

    # Get latest assistant response (what user sees)
    msgs = await conn.fetch('''
        SELECT turn_number, content, metadata
        FROM public.flow1_ai_messages
        WHERE role = 'assistant'
        ORDER BY created_at DESC
        LIMIT 3
    ''')

    await conn.close()

    for i, msg in enumerate(reversed(msgs), 1):
        print('\n' + '=' * 80)
        print(f'RESPONSE {i} - Turn {msg["turn_number"]}')
        print('=' * 80)
        print('CONTENT (This is what user sees):')
        content = msg['content']
        print(content[:500] if len(content) > 500 else content)
        if len(content) > 500:
            print(f'... (total {len(content)} characters)')
        print('\n' + '-' * 80)
        print('METADATA (Backend only - NOT shown to user):')
        print(json.dumps(msg['metadata'], indent=2, ensure_ascii=False))
        print('=' * 80)

asyncio.run(show_real_user_response())

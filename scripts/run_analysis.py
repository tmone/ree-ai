import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.argv = ['analyze_ai_to_ai_results.py', 'flow1_ai_to_ai_20251114_194126.json']
exec(open('scripts/analyze_ai_to_ai_results.py', encoding='utf-8').read())

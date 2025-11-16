# AI-to-AI Test Viewer - Web UI

Real-time web interface for monitoring AI-to-AI Vietnamese real estate chatbot testing.

## Quick Start

```bash
cd scripts
python web_test_viewer.py
```

Then open browser at: **http://localhost:5001**

## Features

### 1. Real-time Progress Dashboard
- Live progress bar showing X/19 scenarios completed
- Average completeness score across all scenarios
- Current test status (not_started / running / completed)
- Auto-refresh every 5 seconds

### 2. Scenario Results List
- Visual list of all 19 test scenarios
- Color-coded scores:
  - Green (80%+): Good
  - Yellow (60-79%): Medium
  - Red (<60%): Needs improvement
- Shows current turn for running scenarios

### 3. Live Test Logs
- Last 100 lines of test output
- Auto-scrolling to latest logs
- Monospace font for readability

### 4. Conversation History (Database)
- Recent AI-to-AI conversations from PostgreSQL
- Scenario name, turns, scores, timestamps
- Pulled from `flow1_ai_conversations` table

## API Endpoints

### GET `/api/progress`
Returns current test progress:
```json
{
  "total_scenarios": 19,
  "completed": 5,
  "running_scenario": "Scenario name",
  "current_turn": 3,
  "scenario_num": 6,
  "average_score": 72.5,
  "status": "running",
  "results": [
    {"scenario_num": 1, "score": 85, "completed": true},
    {"scenario_num": 2, "score": 60, "completed": true}
  ],
  "last_update": "2025-11-16 11:15:00"
}
```

### GET `/api/history`
Returns recent conversations from database:
```json
[
  {
    "conversation_id": "uuid",
    "scenario_name": "Scenario 1: Basic property posting",
    "total_turns": 5,
    "final_score": 85,
    "created_at": "2025-11-16 10:30:00"
  }
]
```

### GET `/api/logs`
Returns recent test logs (last 100 lines):
```json
{
  "logs": "Test output text..."
}
```

## File Monitoring

The viewer monitors: `tests/test_prompt_engineering.txt`

This file is created by running:
```bash
cd tests
python demo_flow1_ai_to_ai.py 2>&1 | tee test_prompt_engineering.txt &
```

## Architecture

```
scripts/
├── web_test_viewer.py          # Flask backend
└── templates/
    └── test_viewer.html        # Frontend (auto-refresh JavaScript)
```

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL (asyncpg)
- **Frontend**: Vanilla JavaScript + CSS (no frameworks)
- **Refresh**: Auto-refresh every 5s (progress, logs) and 10s (history)

## Customization

### Change Refresh Interval
Edit `templates/test_viewer.html`, line ~445:
```javascript
setInterval(updateProgress, 5000);  // Change 5000 to desired ms
setInterval(updateLogs, 5000);
setInterval(updateHistory, 10000);
```

### Change Port
Edit `web_test_viewer.py`, line 168:
```python
app.run(host='0.0.0.0', port=5001, debug=False)  # Change port here
```

### Monitor Different Test File
Edit `web_test_viewer.py`, line 20:
```python
TEST_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "tests", "your_test_file.txt")
```

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5001
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5001
kill -9 <PID>
```

### Database Connection Error
Check database config in `web_test_viewer.py` lines 8-14:
```python
DB_CONFIG = {
    "host": "103.153.74.213",
    "port": 5432,
    "database": "ree_ai",
    "user": "ree_ai_user",
    "password": "ree_ai_pass_2025"
}
```

### Test File Not Found
Ensure test is running and creating output file:
```bash
cd tests
ls -la test_prompt_engineering.txt
```

## Development vs Production

**Current setup**: Development mode (single-threaded Flask)

**For production**: Use WSGI server like Gunicorn or Waitress:
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5001 web_test_viewer:app
```

## Notes

- The UI is read-only (does not control test execution)
- Test must be started separately via `demo_flow1_ai_to_ai.py`
- Progress is parsed from text output (not real-time WebSocket)
- Database queries use asyncio event loop wrapper

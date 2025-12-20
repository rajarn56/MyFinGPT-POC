# MyFinGPT Chat Mock Server

Mock server for UI development and testing. Provides static responses matching the actual API structure.

## Setup

```bash
# Create virtual environment
cd mock_server
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
# Navigate to mock_server directory
cd mock_server

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Make sure dependencies are installed
pip install -r requirements.txt

# Run server
python main.py

# Server runs on http://localhost:8000
# You should see: "INFO:     Uvicorn running on http://0.0.0.0:8000"
```

**Note**: Make sure you're in the `mock_server` directory when running `python main.py`. The script automatically adds the current directory to the Python path to handle imports correctly.

## API Endpoints

### REST API

- `POST /api/chat` - Send chat message
- `GET /api/chat/history/{session_id}` - Get conversation history
- `POST /api/chat/session` - Create new session
- `DELETE /api/chat/session/{session_id}` - Delete session
- `GET /api/health` - Health check

### WebSocket

- `WS /ws/progress/{session_id}` - Real-time progress updates

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"Analyze AAPL"}'

# Test WebSocket (using wscat)
wscat -c ws://localhost:8000/ws/progress/test
```

## Mock Data

The server returns static responses based on message content:
- Single stock analysis (AAPL, MSFT, GOOGL, AMZN, TSLA, META)
- Stock comparisons
- Trend analysis
- Generic responses for unclear queries

## Notes

- This is a mock server for UI development only
- All responses are static and deterministic
- No actual agent execution
- WebSocket streams mock progress updates with delays
- Session management is in-memory only


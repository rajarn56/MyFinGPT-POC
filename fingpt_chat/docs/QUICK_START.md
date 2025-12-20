# MyFinGPT Chat - Quick Start Guide

## For Starting Groups 1-6 in New Chat Session

### Step 1: Read Handoff Context
```bash
# Read the complete context document
cat docs/group_1-6_handoff_context.md
```

### Step 2: Review Setup Instructions
```bash
# Review setup and operations guide
cat docs/setup_and_operations.md
```

### Step 3: Start Group 1 (Mock Server)

#### Create Directory Structure
```bash
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat
mkdir -p mock_server/{routes,websocket,data}
```

#### Setup Virtual Environment
```bash
cd mock_server
python3.12 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install fastapi uvicorn websockets pydantic python-dotenv
pip freeze > requirements.txt
```

#### Create Basic Files
- `mock_server/main.py` - FastAPI app
- `mock_server/routes/chat.py` - Chat endpoints
- `mock_server/websocket/progress.py` - WebSocket handler
- `mock_server/data/responses.py` - Static response data

#### Start Mock Server
```bash
python main.py
# Should run on http://localhost:8000
```

#### Test Mock Server
```bash
# In another terminal
curl http://localhost:8000/api/health
```

### Step 4: Start Group 2 (Frontend Foundation)

#### Create React App
```bash
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

#### Install Additional Dependencies
```bash
npm install axios plotly.js react-markdown
```

#### Configure API Endpoint
```bash
# Create src/config/api.ts
# Set API_BASE_URL=http://localhost:8000
```

#### Start Frontend
```bash
npm run dev
# Should run on http://localhost:3000
```

### Step 5: Continue with Groups 3-6

Follow the detailed instructions in:
- `docs/group_1-6_handoff_context.md` - For each group's tasks
- `docs/implementation_plan.md` - For detailed task breakdown
- `docs/design.md` - For API and component specifications

## Quick Reference Commands

### Start Everything (Mock Server + Frontend)
```bash
# Terminal 1: Mock Server
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/mock_server
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/frontend
npm run dev
```

### Stop Everything
```bash
# Press CTRL+C in each terminal
# Or kill processes:
kill $(lsof -t -i:8000)  # Mock server
kill $(lsof -t -i:3000)  # Frontend
```

### Check Status
```bash
# Check mock server
curl http://localhost:8000/api/health

# Check frontend
curl http://localhost:3000

# Check processes
lsof -i :8000  # Mock server
lsof -i :3000  # Frontend
```

## Key Documents

1. **`group_1-6_handoff_context.md`** - Complete context for Groups 1-6
2. **`setup_and_operations.md`** - Setup and operations guide
3. **`implementation_plan.md`** - Detailed task breakdown
4. **`design.md`** - API and component specifications
5. **`code_reference_guide.md`** - Old code reference (for later groups)

## Testing

After each group:
1. Follow group-specific testing instructions
2. Verify functionality works
3. Test integration with previous groups
4. Document any issues

## Next Steps

After completing Groups 1-6:
- UI is fully functional with mock server
- Ready for backend development (Groups 7-10)
- Then agent integration (Groups 11-12)

See `group_1-6_handoff_context.md` for complete details.


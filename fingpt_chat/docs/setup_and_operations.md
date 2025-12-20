# MyFinGPT Chat - Setup and Operations Guide

This document provides complete setup, start, stop, and restart instructions for each layer of the system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Mock Server Operations](#mock-server-operations)
3. [Frontend Operations](#frontend-operations)
4. [Backend Server Operations](#backend-server-operations)
5. [Testing Instructions](#testing-instructions)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- Python 3.12+ (for backend and mock server)
- Node.js 18+ and npm (for frontend)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection (for frontend dependencies)

### Required API Keys (for actual backend, not mock server)
- At least one LLM provider API key (OpenAI, Gemini, Anthropic, etc.)
- Optional: Alpha Vantage API key, FMP API key

---

## Mock Server Operations

### Setup (Group 1)

#### 1. Navigate to Mock Server Directory
```bash
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/mock_server
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
# Install FastAPI and dependencies
pip install fastapi uvicorn websockets pydantic python-dotenv
```

#### 4. Verify Installation
```bash
python -c "import fastapi; import uvicorn; print('Dependencies installed')"
```

### Start Mock Server

#### Basic Start
```bash
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/mock_server
source venv/bin/activate  # If not already activated
python main.py
```

#### Start with Custom Port
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

#### Start with Auto-reload (Development)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Verify Server is Running**:
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Or open in browser
open http://localhost:8000/api/health
```

### Stop Mock Server

#### Graceful Stop
```bash
# In the terminal where server is running:
Press CTRL+C
```

#### Force Stop (if needed)
```bash
# Find process
lsof -i :8000

# Kill process (replace PID with actual process ID)
kill <PID>

# Or kill all Python processes on port 8000
kill $(lsof -t -i:8000)
```

### Restart Mock Server

```bash
# Stop current instance (CTRL+C)
# Then start again
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/mock_server
source venv/bin/activate
python main.py
```

### Testing Mock Server

#### Test REST Endpoints
```bash
# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_session", "message": "Analyze AAPL"}'

# Test session creation
curl -X POST http://localhost:8000/api/chat/session

# Test history endpoint
curl http://localhost:8000/api/chat/history/test_session
```

#### Test WebSocket
```bash
# Use wscat or similar tool
npm install -g wscat
wscat -c ws://localhost:8000/ws/progress/test_session
```

---

## Frontend Operations

### Setup (Group 2)

#### 1. Navigate to Frontend Directory
```bash
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/frontend
```

#### 2. Install Dependencies
```bash
# Install Node.js dependencies
npm install

# Or using yarn
yarn install
```

#### 3. Configure API Endpoint
```bash
# Edit src/config/api.ts or .env file
# Set API_BASE_URL=http://localhost:8000
```

#### 4. Verify Installation
```bash
npm run build
# Should complete without errors
```

### Start Frontend

#### Development Mode (with hot reload)
```bash
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/frontend
npm run dev
# Or: npm start (if using Create React App)
```

**Expected Output**:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
```

**Access Frontend**:
- Open browser: http://localhost:3000

#### Production Build
```bash
npm run build
# Creates optimized build in dist/ or build/ folder
```

#### Serve Production Build
```bash
# Using serve
npm install -g serve
serve -s build -l 3000

# Or using nginx (if configured)
```

### Stop Frontend

#### Graceful Stop
```bash
# In the terminal where frontend is running:
Press CTRL+C
```

#### Force Stop (if needed)
```bash
# Find process
lsof -i :3000

# Kill process
kill <PID>

# Or kill all Node processes on port 3000
kill $(lsof -t -i:3000)
```

### Restart Frontend

```bash
# Stop current instance (CTRL+C)
# Then start again
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/frontend
npm run dev
```

### Testing Frontend

#### Manual Testing
1. Open http://localhost:3000
2. Test chat interface
3. Send test message
4. Verify progress updates
5. Check results panel

#### Automated Testing
```bash
# Run unit tests
npm test

# Run E2E tests (if configured)
npm run test:e2e
```

---

## Backend Server Operations

### Setup (Group 7+)

#### 1. Navigate to Server Directory
```bash
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/server
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows
```

#### 3. Install Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install individually
pip install fastapi uvicorn websockets pydantic python-dotenv
# ... (all dependencies from basic_agent_version)
```

#### 4. Copy Reusable Components
```bash
# Copy agents, orchestrator, mcp, vector_db, utils from basic_agent_version
# See code_reference_guide.md for details
```

#### 5. Configure Environment
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add API keys
# OPENAI_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
# etc.
```

#### 6. Initialize Vector Database
```bash
python -c "from server.vector_db.chroma_client import ChromaClient; c = ChromaClient(); print('Vector DB initialized')"
```

### Start Backend Server

#### Basic Start
```bash
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/server
source venv/bin/activate
python main.py
# Or: uvicorn server.main:app --host 0.0.0.0 --port 8000
```

#### Start with Auto-reload (Development)
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Start with Custom Port
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8001
```

**Expected Output**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Verify Server is Running**:
```bash
curl http://localhost:8000/api/health
```

### Stop Backend Server

#### Graceful Stop
```bash
# In the terminal where server is running:
Press CTRL+C
```

#### Force Stop (if needed)
```bash
# Find process
lsof -i :8000

# Kill process
kill <PID>
```

### Restart Backend Server

```bash
# Stop current instance (CTRL+C)
# Then start again
cd /Users/rnellapalle/learn-poc/MyFinGPT-POC/fingpt_chat/server
source venv/bin/activate
python main.py
```

### Testing Backend

#### Test REST Endpoints
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test_session", "message": "Analyze AAPL"}'
```

#### Test WebSocket
```bash
wscat -c ws://localhost:8000/ws/progress/test_session
```

---

## Testing Instructions

### Testing by Group

#### Group 1: Mock Server
```bash
# 1. Start mock server
cd mock_server && python main.py

# 2. Test REST endpoints
curl http://localhost:8000/api/health
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"session_id":"test","message":"test"}'

# 3. Test WebSocket
wscat -c ws://localhost:8000/ws/progress/test

# 4. Verify mock responses match API structure
```

#### Group 2: Frontend Foundation
```bash
# 1. Start mock server (from Group 1)
cd mock_server && python main.py

# 2. Start frontend
cd frontend && npm run dev

# 3. Open http://localhost:3000
# 4. Verify two-column layout renders
# 5. Check API client connects to mock server
# 6. Verify WebSocket client connects
```

#### Group 3: Chat Interface
```bash
# 1. Start mock server
cd mock_server && python main.py

# 2. Start frontend
cd frontend && npm run dev

# 3. Test chat interface:
#    - Send message
#    - Verify message displays
#    - Check markdown rendering
#    - Test scrolling
#    - Verify timestamps
```

#### Group 4: Progress Tracking
```bash
# 1. Start mock server
cd mock_server && python main.py

# 2. Start frontend
cd frontend && npm run dev

# 3. Test progress panel:
#    - Send message
#    - Verify progress updates appear
#    - Check timeline visualization
#    - Verify progress events log
```

#### Group 5: Results Panel
```bash
# 1. Start mock server
cd mock_server && python main.py

# 2. Start frontend
cd frontend && npm run dev

# 3. Test results panel:
#    - Send message
#    - Verify analysis report displays
#    - Check visualizations render
#    - Verify agent activity metrics
```

#### Group 6: Session Management
```bash
# 1. Start mock server
cd mock_server && python main.py

# 2. Start frontend
cd frontend && npm run dev

# 3. Test session management:
#    - Send first message (creates session)
#    - Refresh page (session persists)
#    - Send multiple messages (history loads)
#    - Check localStorage for session ID
```

### End-to-End Testing

#### With Mock Server (Groups 1-6)
```bash
# Terminal 1: Start mock server
cd mock_server
source venv/bin/activate
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Run tests
cd frontend
npm test

# Browser: Open http://localhost:3000
# Test complete flow:
# 1. Send message
# 2. Verify progress updates
# 3. Check results display
# 4. Test session persistence
```

#### With Actual Backend (Groups 7-12)
```bash
# Terminal 1: Start backend
cd server
source venv/bin/activate
python main.py

# Terminal 2: Start frontend
cd frontend
npm run dev

# Terminal 3: Run tests
cd server
pytest tests/

# Browser: Open http://localhost:3000
# Test complete flow with actual agents
```

---

## Troubleshooting

### Port Already in Use

#### Mock Server (Port 8000)
```bash
# Find process
lsof -i :8000

# Kill process
kill <PID>

# Or use different port
uvicorn main:app --port 8001
```

#### Frontend (Port 3000)
```bash
# Find process
lsof -i :3000

# Kill process
kill <PID>

# Or use different port
npm run dev -- --port 3001
```

### Virtual Environment Issues

#### Python Version
```bash
# Check Python version
python --version  # Should be 3.12+

# If wrong version, specify explicitly
python3.12 -m venv venv
```

#### Activation Issues
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verify activation
which python  # Should point to venv
```

### Dependency Issues

#### Python Dependencies
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Clear cache
pip cache purge
```

#### Node Dependencies
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Or using yarn
rm -rf node_modules yarn.lock
yarn install
```

### Connection Issues

#### Frontend Can't Connect to Mock Server
```bash
# Check mock server is running
curl http://localhost:8000/api/health

# Check CORS configuration
# Verify API_BASE_URL in frontend config

# Check firewall/network settings
```

#### WebSocket Connection Fails
```bash
# Check WebSocket endpoint
wscat -c ws://localhost:8000/ws/progress/test

# Verify WebSocket server is running
# Check browser console for errors
```

### Common Errors

#### Module Not Found (Python)
```bash
# Verify virtual environment is activated
which python

# Reinstall dependencies
pip install -r requirements.txt
```

#### Module Not Found (Node)
```bash
# Verify node_modules exists
ls node_modules

# Reinstall dependencies
npm install
```

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Check Node path
node -e "console.log(require.resolve('react'))"
```

---

## Quick Reference

### Start Everything (Mock Server + Frontend)
```bash
# Terminal 1
cd mock_server && source venv/bin/activate && python main.py

# Terminal 2
cd frontend && npm run dev
```

### Stop Everything
```bash
# Press CTRL+C in each terminal
# Or kill processes:
kill $(lsof -t -i:8000)  # Mock server
kill $(lsof -t -i:3000)  # Frontend
```

### Restart Everything
```bash
# Stop everything first, then:
# Terminal 1
cd mock_server && source venv/bin/activate && python main.py

# Terminal 2
cd frontend && npm run dev
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

---

## Environment Variables

### Mock Server (.env)
```bash
# Not required for mock server
# But can be used for configuration
PORT=8000
LOG_LEVEL=INFO
```

### Frontend (.env)
```bash
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### Backend Server (.env)
```bash
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
FRONTEND_URL=http://localhost:3000

# Session Configuration
SESSION_EXPIRY_HOURS=24
SESSION_STORAGE_DIR=./sessions

# LLM Configuration
LITELLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Vector DB
CHROMA_DB_PATH=./chroma_db

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs
```

---

## Next Steps

After completing setup:
1. Follow group-specific testing instructions
2. Verify all components start correctly
3. Test basic functionality
4. Proceed to next group

For group-specific instructions, see `implementation_plan.md`.


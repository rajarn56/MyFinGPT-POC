# MyFinGPT Chat - Design Document

## 1. Overview

This document provides detailed design specifications for the MyFinGPT Chat system, including all interfaces, data models, API specifications, and implementation details.

## 2. API Design

### 2.1 REST API Endpoints

#### 2.1.1 POST /api/chat

Send a chat message and receive response.

**Request:**
```typescript
interface ChatRequest {
  session_id: string;          // Session identifier (create if not exists)
  message: string;              // User message content
  context?: ConversationContext; // Optional: previous context
}
```

**Response:**
```typescript
interface ChatResponse {
  message_id: string;           // Unique message ID
  session_id: string;           // Session identifier
  content: string;              // Agent response content (markdown)
  transaction_id: string;       // Transaction ID for this query
  citations: Citation[];      // Citations and sources
  visualizations?: Visualization[]; // Charts and graphs
  agent_activity: AgentActivity; // Agent execution metrics
  timestamp: string;            // ISO timestamp
}
```

**Error Response:**
```typescript
interface ErrorResponse {
  error: string;                // Error message
  error_code: string;           // Error code
  details?: any;                // Additional error details
}
```

**Example Request:**
```json
{
  "session_id": "sess_abc123",
  "message": "Analyze Apple Inc. (AAPL) stock"
}
```

**Example Response:**
```json
{
  "message_id": "msg_xyz789",
  "session_id": "sess_abc123",
  "content": "# Analysis Report\n\n## Executive Summary\n...",
  "transaction_id": "txn_def456",
  "citations": [
    {
      "source": "Yahoo Finance",
      "url": "https://finance.yahoo.com/quote/AAPL",
      "date": "2024-01-15T10:30:00Z",
      "data_point": "Stock Price"
    }
  ],
  "visualizations": [
    {
      "type": "line_chart",
      "data": {...},
      "config": {...}
    }
  ],
  "agent_activity": {
    "agents_executed": ["Research", "Analyst", "Reporting"],
    "token_usage": {
      "Research": 1500,
      "Analyst": 2000,
      "Reporting": 3000
    },
    "execution_time": {
      "Research": 5.2,
      "Analyst": 8.5,
      "Reporting": 12.3
    }
  },
  "timestamp": "2024-01-15T10:35:00Z"
}
```

#### 2.1.2 GET /api/chat/history/{session_id}

Get conversation history for a session.

**Path Parameters:**
- `session_id` (string): Session identifier

**Query Parameters:**
- `limit` (int, optional): Maximum number of messages (default: 100)
- `offset` (int, optional): Offset for pagination (default: 0)

**Response:**
```typescript
interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
  total_count: number;
  has_more: boolean;
}
```

**ChatMessage:**
```typescript
interface ChatMessage {
  id: string;                   // Message ID
  session_id: string;           // Session ID
  role: 'user' | 'assistant';   // Message role
  content: string;              // Message content
  timestamp: string;            // ISO timestamp
  transaction_id?: string;      // Transaction ID (for assistant messages)
  citations?: Citation[];       // Citations (for assistant messages)
  visualizations?: Visualization[]; // Visualizations (for assistant messages)
}
```

#### 2.1.3 POST /api/chat/session

Create a new chat session.

**Request:**
```typescript
interface CreateSessionRequest {
  // Empty body or optional metadata
}
```

**Response:**
```typescript
interface SessionResponse {
  session_id: string;           // Generated session ID
  created_at: string;           // ISO timestamp
  expires_at: string;            // ISO timestamp (24 hours from now)
}
```

#### 2.1.4 DELETE /api/chat/session/{session_id}

Delete a session and all its data.

**Path Parameters:**
- `session_id` (string): Session identifier

**Response:**
```typescript
interface DeleteSessionResponse {
  session_id: string;
  deleted: boolean;
  deleted_at: string;          // ISO timestamp
}
```

#### 2.1.5 GET /api/health

Health check endpoint.

**Response:**
```typescript
interface HealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  services: {
    agents: 'ok' | 'error';
    vector_db: 'ok' | 'error';
    mcp_clients: 'ok' | 'error';
  };
}
```

### 2.2 WebSocket API

#### 2.2.1 WS /ws/progress/{session_id}

Real-time progress updates during agent execution.

**Path Parameters:**
- `session_id` (string): Session identifier

**Connection:**
```typescript
// Client connects to: ws://host/ws/progress/{session_id}
const ws = new WebSocket(`ws://host/ws/progress/${sessionId}`);
```

**Message Format:**
```typescript
interface ProgressUpdate {
  type: 'progress_update';
  session_id: string;
  transaction_id: string;
  current_agent?: string;       // Currently executing agent
  current_tasks: Record<string, string[]>; // Active tasks per agent
  progress_events: ProgressEvent[]; // Recent progress events
  execution_order: ExecutionOrderEntry[]; // Execution timeline
  timestamp: string;
}

interface ProgressEvent {
  timestamp: string;
  agent: string;
  event_type: 'agent_start' | 'agent_complete' | 'task_start' | 
              'task_complete' | 'task_progress' | 'api_call_start' |
              'api_call_success' | 'api_call_failed' | 'api_call_skipped';
  message: string;
  task_name?: string;
  symbol?: string;
  status: 'running' | 'completed' | 'failed' | 'success' | 'skipped';
  execution_order: number;
  is_parallel: boolean;
  integration?: string;         // For API call events
  error?: string;                // For failed events
}

interface ExecutionOrderEntry {
  agent: string;
  start_time: number;           // Unix timestamp
  end_time?: number;             // Unix timestamp (null if still running)
  duration?: number;             // Duration in seconds
}
```

**Example Message:**
```json
{
  "type": "progress_update",
  "session_id": "sess_abc123",
  "transaction_id": "txn_def456",
  "current_agent": "Research",
  "current_tasks": {
    "Research": ["Fetching stock price", "Gathering company info"]
  },
  "progress_events": [
    {
      "timestamp": "2024-01-15T10:30:05Z",
      "agent": "Research",
      "event_type": "agent_start",
      "message": "Research Agent started execution",
      "status": "running",
      "execution_order": 0,
      "is_parallel": false
    },
    {
      "timestamp": "2024-01-15T10:30:06Z",
      "agent": "Research",
      "event_type": "api_call_success",
      "message": "Yahoo Finance API call succeeded for AAPL",
      "status": "success",
      "execution_order": 1,
      "is_parallel": false,
      "integration": "yahoo_finance"
    }
  ],
  "execution_order": [
    {
      "agent": "Research",
      "start_time": 1705315805.0,
      "end_time": null,
      "duration": null
    }
  ],
  "timestamp": "2024-01-15T10:30:06Z"
}
```

**Connection Lifecycle:**
1. Client connects to WebSocket endpoint
2. Server registers connection for session
3. Server sends progress updates as they occur
4. Client receives updates and updates UI
5. Connection closes when transaction completes or error occurs

**Reconnection:**
- Client should implement automatic reconnection
- Server maintains progress state for active transactions
- Client can reconnect and receive missed updates

### 2.3 Data Models

#### 2.3.1 Citation Model
```typescript
interface Citation {
  source: string;                // Source name (e.g., "Yahoo Finance")
  url?: string;                  // Source URL
  date?: string;                 // ISO date
  agent?: string;                // Agent that collected citation
  data_point?: string;          // What data point
  symbol?: string;               // Stock symbol
}
```

#### 2.3.2 Visualization Model
```typescript
interface Visualization {
  type: 'line_chart' | 'bar_chart' | 'pie_chart' | 'scatter_plot';
  title: string;
  data: any;                     // Chart data (Plotly format)
  config?: any;                  // Chart configuration
}
```

#### 2.3.3 Agent Activity Model
```typescript
interface AgentActivity {
  agents_executed: string[];     // List of executed agents
  token_usage: Record<string, number>; // Tokens per agent
  execution_time: Record<string, number>; // Time per agent (seconds)
  context_size?: number;        // Context size in bytes
}
```

#### 2.3.4 Conversation Context Model
```typescript
interface ConversationContext {
  symbols: string[];             // Stock symbols mentioned
  previous_queries: string[];    // Previous query texts
  research_data?: any;          // Previous research data
  analysis_results?: any;       // Previous analysis results
  citations?: Citation[];        // Previous citations
  context_version: number;       // Context version
  context_size: number;          // Context size in bytes
}
```

#### 2.3.5 Session Model (Backend)
```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any

class Session(BaseModel):
    session_id: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    messages: List['ChatMessage']
    context: Optional['ConversationContext'] = None
    transaction_ids: List[str] = []
    
class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: str  # 'user' | 'assistant'
    content: str
    timestamp: datetime
    transaction_id: Optional[str] = None
    citations: List[Dict[str, Any]] = []
    visualizations: List[Dict[str, Any]] = []
    
class ConversationContext(BaseModel):
    symbols: List[str] = []
    previous_queries: List[str] = []
    research_data: Optional[Dict[str, Any]] = None
    analysis_results: Optional[Dict[str, Any]] = None
    citations: List[Dict[str, Any]] = []
    context_version: int = 1
    context_size: int = 0
```

## 3. Service Design

### 3.1 ChatService

**Purpose:** Handles chat message processing and agent coordination.

**Methods:**

```python
class ChatService:
    async def process_message(
        self,
        session_id: str,
        message: str,
        context: Optional[ConversationContext] = None
    ) -> ChatResponse:
        """
        Process a chat message and return response.
        
        Steps:
        1. Load or create session
        2. Merge conversation context
        3. Detect user intent
        4. Ask clarification if needed
        5. Execute workflow with streaming
        6. Generate response
        7. Save message and update session
        8. Return response
        """
        
    async def detect_intent(
        self,
        message: str,
        context: ConversationContext
    ) -> IntentResult:
        """
        Detect user intent from message and context.
        
        Returns:
            IntentResult with intent, confidence, clarification_needed
        """
        
    async def ask_clarification(
        self,
        message: str,
        context: ConversationContext
    ) -> str:
        """
        Generate clarification question when intent is unclear.
        """
        
    async def merge_context(
        self,
        previous_context: ConversationContext,
        new_query: str,
        new_symbols: List[str]
    ) -> ConversationContext:
        """
        Merge new query context with previous conversation context.
        """
```

### 3.2 SessionService

**Purpose:** Manages chat sessions and conversation history.

**Methods:**

```python
class SessionService:
    async def create_session(self) -> Session:
        """Create a new session."""
        
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        
    async def save_message(
        self,
        session_id: str,
        message: ChatMessage
    ) -> None:
        """Save message to session."""
        
    async def update_context(
        self,
        session_id: str,
        context: ConversationContext
    ) -> None:
        """Update session context."""
        
    async def delete_session(self, session_id: str) -> bool:
        """Delete session and all data."""
        
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions (24 hours)."""
        
    async def get_history(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChatMessage]:
        """Get conversation history."""
```

### 3.3 ContextManager

**Purpose:** Manages conversation context merging and pruning.

**Methods:**

```python
class ContextManager:
    def merge_contexts(
        self,
        previous: ConversationContext,
        new_query: str,
        new_symbols: List[str],
        new_research_data: Dict[str, Any],
        new_analysis_results: Dict[str, Any]
    ) -> ConversationContext:
        """
        Merge new context with previous context.
        
        Strategy:
        1. Merge symbols (deduplicate)
        2. Append previous queries
        3. Merge research_data (update existing, add new)
        4. Merge analysis_results (update existing, add new)
        5. Merge citations (append)
        6. Update context_version and context_size
        """
        
    def detect_incremental_query(
        self,
        query: str,
        previous_symbols: List[str],
        new_symbols: List[str]
    ) -> bool:
        """
        Detect if query is incremental (e.g., "add AAPL").
        """
        
    def prune_context(
        self,
        context: ConversationContext,
        max_size_bytes: int = 1000000
    ) -> ConversationContext:
        """
        Prune context to reduce size.
        
        Strategy:
        1. Remove old metadata (>24 hours)
        2. Truncate long reasoning chains
        3. Remove old progress events (keep last 50)
        4. Compress large data structures
        """
        
    def calculate_context_size(
        self,
        context: ConversationContext
    ) -> int:
        """Calculate context size in bytes."""
```

### 3.4 WorkflowService

**Purpose:** Wraps existing workflow with chat context and streaming.

**Methods:**

```python
class WorkflowService:
    def __init__(self, workflow: MyFinGPTWorkflow):
        self.workflow = workflow
        
    async def execute_with_streaming(
        self,
        query: str,
        context: ConversationContext,
        session_id: str,
        progress_callback: Callable[[ProgressUpdate], None]
    ) -> AgentState:
        """
        Execute workflow with streaming progress updates.
        
        Steps:
        1. Create initial state with context
        2. Stream workflow execution
        3. Call progress_callback for each update
        4. Return final state
        """
        
    def create_initial_state(
        self,
        query: str,
        context: ConversationContext,
        session_id: str
    ) -> AgentState:
        """
        Create initial AgentState with merged context.
        """
```

## 4. Frontend Design

### 4.1 Component Hierarchy

```
App
├── AppLayout
│   ├── TwoColumnLayout
│   │   ├── LeftColumn
│   │   │   ├── ChatInterface
│   │   │   │   ├── MessageList
│   │   │   │   │   └── MessageBubble[]
│   │   │   │   ├── ChatInput
│   │   │   │   └── TypingIndicator
│   │   │   └── ProgressPanel
│   │   │       ├── AgentStatus
│   │   │       ├── ActiveTasks
│   │   │       ├── ExecutionTimeline
│   │   │       └── ProgressEvents
│   │   └── RightColumn
│   │       └── ResultsPanel
│   │           ├── AnalysisReport
│   │           ├── Visualizations
│   │           └── AgentActivity
```

### 4.2 State Management

**Chat State:**
```typescript
interface ChatState {
  sessionId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}
```

**Progress State:**
```typescript
interface ProgressState {
  currentAgent?: string;
  currentTasks: Record<string, string[]>;
  progressEvents: ProgressEvent[];
  executionOrder: ExecutionOrderEntry[];
  isActive: boolean;
}
```

**Results State:**
```typescript
interface ResultsState {
  currentReport?: string;
  visualizations: Visualization[];
  agentActivity?: AgentActivity;
}
```

### 4.3 Custom Hooks

**useChat Hook:**
```typescript
function useChat() {
  const [state, setState] = useState<ChatState>({
    sessionId: null,
    messages: [],
    isLoading: false,
    error: null
  });
  
  const sendMessage = async (message: string) => {
    // Send message to API
    // Update state
    // Connect WebSocket for progress
  };
  
  const loadHistory = async (sessionId: string) => {
    // Load conversation history
  };
  
  return { state, sendMessage, loadHistory };
}
```

**useWebSocket Hook:**
```typescript
function useWebSocket(sessionId: string | null) {
  const [progress, setProgress] = useState<ProgressState>({
    currentAgent: undefined,
    currentTasks: {},
    progressEvents: [],
    executionOrder: [],
    isActive: false
  });
  
  useEffect(() => {
    if (!sessionId) return;
    
    const ws = new WebSocket(`ws://host/ws/progress/${sessionId}`);
    
    ws.onmessage = (event) => {
      const update: ProgressUpdate = JSON.parse(event.data);
      setProgress(prev => ({
        ...prev,
        currentAgent: update.current_agent,
        currentTasks: update.current_tasks,
        progressEvents: [...prev.progressEvents, ...update.progress_events],
        executionOrder: update.execution_order,
        isActive: true
      }));
    };
    
    return () => ws.close();
  }, [sessionId]);
  
  return progress;
}
```

### 4.4 API Client

```typescript
class ApiClient {
  private baseUrl: string;
  
  async sendMessage(
    sessionId: string,
    message: string
  ): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return response.json();
  }
  
  async getHistory(
    sessionId: string,
    limit = 100,
    offset = 0
  ): Promise<ChatMessage[]> {
    const response = await fetch(
      `${this.baseUrl}/api/chat/history/${sessionId}?limit=${limit}&offset=${offset}`
    );
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.messages;
  }
  
  async createSession(): Promise<SessionResponse> {
    const response = await fetch(`${this.baseUrl}/api/chat/session`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    
    return response.json();
  }
}
```

## 5. Backend Implementation Details

### 5.1 FastAPI Application Structure

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MyFinGPT Chat API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/chat")
app.include_router(session_router, prefix="/api/chat")
app.include_router(health_router, prefix="/api")

# WebSocket endpoint
@app.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        # Register connection
        # Stream progress updates
        # Handle disconnection
    except WebSocketDisconnect:
        # Cleanup
        pass
```

### 5.2 Session Storage Implementation

**File-based Storage:**
```python
import json
from pathlib import Path
from typing import Optional

class FileSessionStore:
    def __init__(self, storage_dir: str = "./sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def _get_session_file(self, session_id: str) -> Path:
        return self.storage_dir / f"{session_id}.json"
    
    async def save_session(self, session: Session) -> None:
        file_path = self._get_session_file(session.session_id)
        with open(file_path, 'w') as f:
            json.dump(session.dict(), f, default=str)
    
    async def load_session(self, session_id: str) -> Optional[Session]:
        file_path = self._get_session_file(session_id)
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            return Session(**data)
    
    async def delete_session(self, session_id: str) -> bool:
        file_path = self._get_session_file(session_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False
```

### 5.3 WebSocket Progress Streaming

```python
from fastapi import WebSocket
from typing import Dict, Set

class ProgressStreamManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
    
    async def register(
        self,
        session_id: str,
        websocket: WebSocket
    ) -> None:
        if session_id not in self.connections:
            self.connections[session_id] = set()
        self.connections[session_id].add(websocket)
    
    async def unregister(
        self,
        session_id: str,
        websocket: WebSocket
    ) -> None:
        if session_id in self.connections:
            self.connections[session_id].discard(websocket)
    
    async def broadcast(
        self,
        session_id: str,
        update: ProgressUpdate
    ) -> None:
        if session_id not in self.connections:
            return
        
        disconnected = set()
        for websocket in self.connections[session_id]:
            try:
                await websocket.send_json(update.dict())
            except Exception:
                disconnected.add(websocket)
        
        # Remove disconnected connections
        self.connections[session_id] -= disconnected
```

## 6. Error Handling

### 6.1 Error Types

```python
class ChatError(Exception):
    """Base exception for chat errors"""
    pass

class SessionNotFoundError(ChatError):
    """Session not found"""
    pass

class InvalidMessageError(ChatError):
    """Invalid message format"""
    pass

class AgentExecutionError(ChatError):
    """Agent execution failed"""
    pass
```

### 6.2 Error Handling Middleware

```python
@app.exception_handler(ChatError)
async def chat_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={
            "error": str(exc),
            "error_code": exc.__class__.__name__
        }
    )
```

## 7. Configuration

### 7.1 Environment Variables

```bash
# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Session Configuration
SESSION_EXPIRY_HOURS=24
SESSION_STORAGE_DIR=./sessions

# LLM Configuration (reused from existing)
LITELLM_PROVIDER=openai
OPENAI_API_KEY=...

# Vector DB Configuration (reused)
CHROMA_DB_PATH=./chroma_db

# Logging
LOG_LEVEL=INFO
LOG_DIR=./logs
```

### 7.2 Configuration Model

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    session_expiry_hours: int = 24
    session_storage_dir: str = "./sessions"
    log_level: str = "INFO"
    log_dir: str = "./logs"
    
    class Config:
        env_file = ".env"
```

## 8. Testing Strategy

### 8.1 Unit Tests
- Service methods
- Context merging logic
- Intent detection
- Session management

### 8.2 Integration Tests
- API endpoints
- WebSocket communication
- End-to-end chat flow
- Agent execution

### 8.3 Frontend Tests
- Component rendering
- User interactions
- State management
- API integration

## 9. Mock Server Design

### 9.1 Mock Server Purpose

The mock server provides static responses matching the actual API structure, enabling UI development without agent dependencies.

### 9.2 Mock Server Implementation

**File Structure**:
```
mock_server/
├── main.py                 # FastAPI app
├── routes/
│   ├── __init__.py
│   ├── chat.py            # Chat endpoints
│   └── session.py         # Session endpoints
├── websocket/
│   ├── __init__.py
│   └── progress.py        # WebSocket handler
├── data/
│   ├── __init__.py
│   ├── responses.py       # Static response data
│   ├── scenarios.py       # Test scenarios
│   └── progress_events.py # Progress event sequences
└── README.md              # Usage documentation
```

### 9.3 Mock Server Endpoints

**POST /api/chat**:
```python
async def mock_chat(request: ChatRequest) -> ChatResponse:
    # Return static response based on message content
    # Match actual API response structure
    return get_mock_response(request.message)
```

**GET /api/chat/history/{session_id}**:
```python
async def mock_history(session_id: str) -> ChatHistoryResponse:
    # Return mock conversation history
    return get_mock_history(session_id)
```

**WS /ws/progress/{session_id}**:
```python
async def mock_progress_websocket(websocket: WebSocket, session_id: str):
    # Stream mock progress updates
    # Simulate agent execution progress
    await stream_mock_progress(websocket, session_id)
```

### 9.4 Mock Data Scenarios

**Single Stock Analysis**:
```python
MOCK_RESPONSES = {
    "analyze aapl": {
        "content": "# Analysis Report\n\n## Executive Summary\n...",
        "citations": [...],
        "visualizations": [...],
        "agent_activity": {...}
    },
    "compare aapl msft": {
        "content": "# Comparison Report\n\n...",
        ...
    }
}
```

**Progress Events Sequence**:
```python
MOCK_PROGRESS_SEQUENCE = [
    {"event_type": "agent_start", "agent": "Research", ...},
    {"event_type": "task_start", "task_name": "Fetching stock price", ...},
    {"event_type": "api_call_success", "integration": "yahoo_finance", ...},
    {"event_type": "task_complete", "task_name": "Fetching stock price", ...},
    {"event_type": "agent_complete", "agent": "Research", ...},
    ...
]
```

### 9.5 Mock Server Usage

1. **Start Mock Server**:
   ```bash
   cd fingpt_chat/mock_server
   python main.py
   # Server runs on http://localhost:8000
   ```

2. **Frontend Configuration**:
   ```typescript
   // frontend/src/config/api.ts
   export const API_BASE_URL = 'http://localhost:8000';
   ```

3. **Switch to Actual Server**:
   - Change API_BASE_URL to actual server
   - No other code changes needed

### 9.6 Mock Server Removal

Once UI is verified:
- Delete `mock_server/` folder
- No mock code in actual server
- Clean separation maintained

## 10. Deployment Configuration

### 10.1 Docker Configuration

**Backend Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./server/

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
```

### 9.2 Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./server
    ports:
      - "8000:8000"
    environment:
      - FRONTEND_URL=http://localhost:3000
    volumes:
      - ./sessions:/app/sessions
      - ./chroma_db:/app/chroma_db
      - ./logs:/app/logs
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```


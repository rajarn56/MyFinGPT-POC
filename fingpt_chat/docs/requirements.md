# MyFinGPT Chat - Requirements Document

## 1. Overview

This document outlines the requirements for rearchitecting MyFinGPT from a single-application POC to a production-quality system with separated UI and server components, featuring a chat-based conversational interface.

## 2. System Goals

### 2.1 Primary Goals
- **Separation of Concerns**: Decouple UI and server (agent) into independent, scalable components
- **Chat Interface**: Transform from single-query interface to continuous conversational chat interface
- **Production Quality**: Implement production-ready architecture with proper layers, components, and communication patterns
- **Context Awareness**: Maintain conversation context across multiple interactions
- **Real-time Updates**: Provide real-time progress tracking during agent execution

### 2.2 Non-Goals
- No changes to existing `basic_agent_version` codebase
- Not migrating existing functionality, but rearchitecting for production
- Not implementing authentication/authorization in initial version (can be added later)

## 3. Functional Requirements

### 3.1 User Interface Requirements

#### 3.1.1 Chat Interface
- **FR-UI-001**: Users must be able to send messages in a chat interface (not single query form)
- **FR-UI-002**: Chat history must be displayed in chronological order
- **FR-UI-003**: Users must be able to scroll through chat history
- **FR-UI-004**: Each message must display timestamp
- **FR-UI-005**: User messages must be visually distinct from agent responses
- **FR-UI-006**: Agent responses must support markdown formatting
- **FR-UI-007**: Agent responses must display citations and sources
- **FR-UI-008**: Chat interface must support real-time typing indicators when agent is processing

#### 3.1.2 Progress Tracking
- **FR-UI-009**: Real-time progress updates must be displayed during agent execution
- **FR-UI-010**: Current agent status must be visible
- **FR-UI-011**: Active tasks must be displayed
- **FR-UI-012**: Execution timeline visualization must be shown
- **FR-UI-013**: Progress events log must be available
- **FR-UI-014**: Progress updates must not block user from viewing chat history

#### 3.1.3 Visualizations
- **FR-UI-015**: Financial charts and visualizations must be displayed inline in chat
- **FR-UI-016**: Charts must be interactive (zoom, pan, hover)
- **FR-UI-017**: Charts must be responsive to different screen sizes

#### 3.1.4 Layout
- **FR-UI-018**: UI must use two-column layout (50/50 split) as per architecture.md section 11
- **FR-UI-019**: Left column must contain chat interface and progress tracking
- **FR-UI-020**: Right column must contain analysis results, visualizations, and agent activity
- **FR-UI-021**: Layout must be responsive and work on different screen sizes
- **FR-UI-022**: All panels must be scrollable independently

### 3.2 Server (Agent) Requirements

#### 3.2.1 Chat Conversation Handling
- **FR-SRV-001**: Server must handle continuous conversation with context from previous messages
- **FR-SRV-002**: Server must maintain conversation context per session
- **FR-UI-003**: Server must understand user intent from conversation context
- **FR-SRV-004**: Server must ask follow-up questions when user intent is unclear
- **FR-SRV-005**: Server must support conversation threads (users can reference previous messages)
- **FR-SRV-006**: Server must handle context window limits gracefully

#### 3.2.2 Agent Execution
- **FR-SRV-007**: All existing agent functionality must be preserved (Research, Analyst, Reporting agents)
- **FR-SRV-008**: Agent execution must support streaming progress updates
- **FR-SRV-009**: Agent execution must maintain transaction IDs for traceability
- **FR-SRV-010**: Agent execution must support parallel processing where applicable
- **FR-SRV-011**: Agent execution must handle errors gracefully without crashing

#### 3.2.3 Context Management
- **FR-SRV-012**: Server must maintain conversation history per session
- **FR-SRV-013**: Server must support context pruning when context size exceeds limits
- **FR-SRV-014**: Server must merge new query context with previous conversation context
- **FR-SRV-015**: Server must detect incremental queries (e.g., "add AAPL to the comparison")
- **FR-SRV-016**: Server must support query similarity detection

#### 3.2.4 Data Sources
- **FR-SRV-017**: All existing MCP integrations must be preserved (Yahoo Finance, Alpha Vantage, FMP)
- **FR-SRV-018**: Data source fallback logic must be maintained
- **FR-SRV-019**: API rate limiting must be handled gracefully

#### 3.2.5 Vector Database
- **FR-SRV-020**: Vector database integration must be preserved
- **FR-SRV-021**: Historical pattern matching must continue to work
- **FR-SRV-022**: Citation retrieval from vector DB must be maintained

### 3.3 Communication Requirements

#### 3.3.1 API Interface
- **FR-COMM-001**: Server must expose REST API endpoints for chat operations
- **FR-COMM-002**: Server must support WebSocket for real-time progress updates
- **FR-COMM-003**: API must use JSON for request/response payloads
- **FR-COMM-004**: API must support CORS for frontend access
- **FR-COMM-005**: API must include proper error handling and error responses

#### 3.3.2 Real-time Communication
- **FR-COMM-006**: Progress updates must be streamed in real-time
- **FR-COMM-007**: WebSocket connection must handle reconnection automatically
- **FR-COMM-008**: Progress updates must include agent status, tasks, and events

### 3.4 Session Management

#### 3.4.1 Session Creation
- **FR-SESS-001**: Each chat session must have a unique session ID
- **FR-SESS-002**: Session ID must be generated on first message
- **FR-SESS-003**: Session ID must be persisted across page refreshes

#### 3.4.2 Session Persistence
- **FR-SESS-004**: Conversation history must be persisted per session
- **FR-SESS-005**: Session data must be retrievable after server restart
- **FR-SESS-006**: Session data must expire after configurable timeout (e.g., 24 hours)

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
- **NFR-PERF-001**: API response time must be < 100ms for non-processing endpoints
- **NFR-PERF-002**: Progress updates must be delivered within 500ms of event occurrence
- **NFR-PERF-003**: UI must remain responsive during agent execution
- **NFR-PERF-004**: Chat history loading must complete within 2 seconds for 100 messages

### 4.2 Scalability Requirements
- **NFR-SCALE-001**: Server must support multiple concurrent sessions
- **NFR-SCALE-002**: Architecture must allow horizontal scaling of server components
- **NFR-SCALE-003**: UI must be stateless and support multiple instances

### 4.3 Reliability Requirements
- **NFR-REL-001**: Server must handle errors gracefully without crashing
- **NFR-REL-002**: Server must log all errors with sufficient context
- **NFR-REL-003**: Server must support graceful shutdown
- **NFR-REL-004**: WebSocket connections must handle network interruptions

### 4.4 Maintainability Requirements
- **NFR-MAINT-001**: Code must be well-documented
- **NFR-MAINT-002**: Code must follow consistent patterns and conventions
- **NFR-MAINT-003**: Components must be loosely coupled
- **NFR-MAINT-004**: Interfaces must be clearly defined

### 4.5 Security Requirements
- **NFR-SEC-001**: Input validation must be performed on all user inputs
- **NFR-SEC-002**: API must sanitize inputs to prevent injection attacks
- **NFR-SEC-003**: Session IDs must be cryptographically secure
- **NFR-SEC-004**: API keys must be stored securely (environment variables)

## 5. Technology Stack Requirements

### 5.1 Frontend Stack
- **TECH-FE-001**: React framework for UI
- **TECH-FE-002**: TypeScript for type safety
- **TECH-FE-003**: WebSocket client library for real-time updates
- **TECH-FE-004**: Chart library for visualizations (e.g., Plotly.js, Recharts)
- **TECH-FE-005**: Markdown rendering library for agent responses

### 5.2 Backend Stack
- **TECH-BE-001**: FastAPI framework for REST API and WebSocket support
- **TECH-BE-002**: Python 3.12+ (consistent with existing codebase)
- **TECH-BE-003**: Existing agent infrastructure (LangGraph, LiteLLM, Chroma)
- **TECH-BE-004**: Session storage (file-based or database)
- **TECH-BE-005**: WebSocket support for real-time updates

### 5.3 Communication Protocol
- **TECH-COMM-001**: REST API for chat operations (POST /api/chat)
- **TECH-COMM-002**: WebSocket for progress streaming (/ws/progress/{session_id})
- **TECH-COMM-003**: JSON for all payloads

## 6. Interface Requirements

### 6.1 API Endpoints

#### 6.1.1 Chat Endpoints
- **POST /api/chat**: Send a message and receive response
- **GET /api/chat/history/{session_id}**: Get conversation history
- **POST /api/chat/session**: Create new session
- **DELETE /api/chat/session/{session_id}**: Delete session

#### 6.1.2 WebSocket Endpoints
- **WS /ws/progress/{session_id}**: Real-time progress updates

### 6.2 Data Models

#### 6.2.1 Chat Message
```typescript
interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  transaction_id?: string; // For agent responses
  citations?: Citation[];
  visualizations?: Visualization[];
}
```

#### 6.2.2 Chat Request
```typescript
interface ChatRequest {
  session_id: string;
  message: string;
  context?: ConversationContext;
}
```

#### 6.2.3 Chat Response
```typescript
interface ChatResponse {
  message_id: string;
  session_id: string;
  content: string;
  transaction_id: string;
  citations: Citation[];
  visualizations: Visualization[];
  agent_activity: AgentActivity;
}
```

#### 6.2.4 Progress Update
```typescript
interface ProgressUpdate {
  session_id: string;
  transaction_id: string;
  current_agent?: string;
  current_tasks: Record<string, string[]>;
  progress_events: ProgressEvent[];
  execution_order: ExecutionOrderEntry[];
}
```

## 7. Constraints

### 7.1 Technical Constraints
- Must use Python 3.12+ for backend
- Must preserve all existing agent functionality
- Must not modify `basic_agent_version` codebase
- Must use existing LLM providers (OpenAI, Gemini, Anthropic, Ollama, LM Studio)
- Must use existing MCP integrations

### 7.2 Business Constraints
- No authentication/authorization in initial version
- Single-tenant deployment (no multi-user support initially)
- File-based session storage acceptable (database optional)

## 8. Success Criteria

### 8.1 Functional Success
- Users can have continuous conversations with the agent
- Agent maintains context across multiple messages
- Real-time progress updates work correctly
- All existing agent functionality is preserved

### 8.2 Technical Success
- UI and server are completely separated
- API is well-documented and follows REST principles
- WebSocket communication is reliable
- Code is production-ready and maintainable

## 9. Out of Scope

- Authentication and authorization
- Multi-user support
- Database-backed session storage (file-based is acceptable)
- Mobile app
- Advanced analytics and monitoring
- Rate limiting per user
- Payment integration

## 10. Future Enhancements

- Database-backed session storage
- User authentication
- Multi-user support
- Advanced analytics dashboard
- Export conversation history
- Share conversations
- Custom agent configurations per user


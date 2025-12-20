# MyFinGPT Chat - Implementation Plan

## Overview

This document breaks down the implementation into manageable task groups. Each group is self-contained and can be completed independently, with clear handoff documentation for the next group.

## Implementation Groups

### Group 1: Project Setup & Mock Server
**Goal**: Set up project structure and create mock server for UI development

**Tasks**:
1. Create project directory structure
2. Set up mock server (FastAPI) with static data
3. Implement mock REST API endpoints (`/api/chat`, `/api/chat/session`, `/api/chat/history`)
4. Implement mock WebSocket endpoint (`/ws/progress/{session_id}`)
5. Create static response data matching actual API structure
6. Add mock data for various scenarios (single stock, comparison, errors)
7. Document mock server usage

**Deliverables**:
- Mock server running on port 8000
- All API endpoints returning static data
- WebSocket streaming mock progress updates
- Mock data files with sample responses

**Estimated Time**: 2-3 days

**Handoff Context**: See [Group 1 Handoff](#group-1-handoff)

---

### Group 2: Frontend Foundation & Layout
**Goal**: Build React frontend foundation with two-column layout

**Tasks**:
1. Set up React + TypeScript project
2. Configure build tools (Vite/CRA)
3. Set up routing and basic app structure
4. Create TwoColumnLayout component (50/50 split)
5. Implement responsive design
6. Set up API client service
7. Set up WebSocket client service
8. Create basic styling system

**Deliverables**:
- React app running on port 3000
- Two-column layout implemented
- API client configured
- WebSocket client configured
- Basic styling in place

**Estimated Time**: 3-4 days

**Handoff Context**: See [Group 2 Handoff](#group-2-handoff)

---

### Group 3: Chat Interface Components
**Goal**: Implement chat interface with message display

**Tasks**:
1. Create ChatInterface component
2. Implement MessageList component
3. Implement MessageBubble component (user/assistant)
4. Implement ChatInput component
5. Implement TypingIndicator component
6. Add markdown rendering for agent responses
7. Implement message scrolling
8. Add message timestamps
9. Style chat interface

**Deliverables**:
- Chat interface fully functional
- Messages display correctly
- Markdown rendering works
- Input and send functionality works
- Connected to mock server

**Estimated Time**: 4-5 days

**Handoff Context**: See [Group 3 Handoff](#group-3-handoff)

---

### Group 4: Progress Tracking Components
**Goal**: Implement real-time progress tracking panel

**Tasks**:
1. Create ProgressPanel component
2. Implement AgentStatus component
3. Implement ActiveTasks component
4. Implement ExecutionTimeline component (Plotly chart)
5. Implement ProgressEvents component
6. Connect WebSocket for real-time updates
7. Format progress events display
8. Style progress panel

**Deliverables**:
- Progress panel displays correctly
- Real-time updates via WebSocket
- Timeline visualization works
- Progress events log works
- Connected to mock WebSocket

**Estimated Time**: 4-5 days

**Handoff Context**: See [Group 4 Handoff](#group-4-handoff)

---

### Group 5: Results Panel Components
**Goal**: Implement results display panel

**Tasks**:
1. Create ResultsPanel component
2. Implement AnalysisReport component (markdown display)
3. Implement Visualizations component (Plotly charts)
4. Implement AgentActivity component (metrics display)
5. Add tab navigation for results
6. Style results panel
7. Handle empty states

**Deliverables**:
- Results panel displays correctly
- Analysis report renders markdown
- Charts display and are interactive
- Agent activity metrics shown
- Connected to mock server data

**Estimated Time**: 3-4 days

**Handoff Context**: See [Group 5 Handoff](#group-5-handoff)

---

### Group 6: Session Management & State
**Goal**: Implement session management and state handling

**Tasks**:
1. Implement session creation on first message
2. Implement session persistence (localStorage)
3. Implement conversation history loading
4. Create useChat hook for state management
5. Create useWebSocket hook
6. Create useProgress hook
7. Handle session expiration
8. Implement session cleanup

**Deliverables**:
- Sessions created and persisted
- Conversation history loads correctly
- State management hooks work
- Session expiration handled
- Connected to mock server

**Estimated Time**: 3-4 days

**Handoff Context**: See [Group 6 Handoff](#group-6-handoff)

---

### Group 7: Backend API Layer
**Goal**: Implement actual FastAPI backend (replace mock)

**Tasks**:
1. Set up FastAPI project structure
2. Implement REST API endpoints (reuse mock structure)
3. Implement WebSocket endpoint
4. Add request/response validation (Pydantic)
5. Add error handling middleware
6. Add CORS configuration
7. Add health check endpoint
8. Document API (OpenAPI/Swagger)

**Deliverables**:
- FastAPI server running
- All endpoints implemented
- Validation and error handling
- API documentation available
- No agent integration yet

**Estimated Time**: 3-4 days

**Handoff Context**: See [Group 7 Handoff](#group-7-handoff)

---

### Group 8: Session Service Implementation
**Goal**: Implement session management service

**Tasks**:
1. Create SessionService class
2. Implement file-based session storage
3. Implement session creation
4. Implement session loading
5. Implement message saving
6. Implement context updating
7. Implement session deletion
8. Implement session expiration cleanup
9. Add session tests

**Deliverables**:
- SessionService fully implemented
- File-based storage working
- Session CRUD operations work
- Expiration cleanup works
- Unit tests passing

**Estimated Time**: 2-3 days

**Handoff Context**: See [Group 8 Handoff](#group-8-handoff)

---

### Group 9: Context Manager Implementation
**Goal**: Implement conversation context management

**Tasks**:
1. Create ContextManager class
2. Implement context merging logic
3. Implement incremental query detection
4. Implement context pruning
5. Implement context size calculation
6. Add context validation
7. Add context tests

**Deliverables**:
- ContextManager fully implemented
- Context merging works correctly
- Incremental queries detected
- Context pruning works
- Unit tests passing

**Estimated Time**: 3-4 days

**Handoff Context**: See [Group 9 Handoff](#group-9-handoff)

---

### Group 10: Chat Service Implementation
**Goal**: Implement chat message processing service

**Tasks**:
1. Create ChatService class
2. Implement message processing flow
3. Implement intent detection
4. Implement clarification questions
5. Integrate with SessionService
6. Integrate with ContextManager
7. Add error handling
8. Add chat service tests

**Deliverables**:
- ChatService fully implemented
- Intent detection works
- Clarification questions generated
- Error handling works
- Unit tests passing

**Estimated Time**: 4-5 days

**Handoff Context**: See [Group 10 Handoff](#group-10-handoff)

---

### Group 11: Workflow Service & Agent Integration
**Goal**: Integrate existing workflow and agents

**Tasks**:
1. Copy reusable components from `basic_agent_version`
2. Create WorkflowService wrapper
3. Integrate existing workflow
4. Implement progress streaming
5. Connect agents to chat service
6. Handle agent execution errors
7. Test end-to-end flow
8. Add integration tests

**Deliverables**:
- WorkflowService integrated
- Agents connected and working
- Progress streaming works
- End-to-end flow works
- Integration tests passing

**Estimated Time**: 5-6 days

**Handoff Context**: See [Group 11 Handoff](#group-11-handoff)

---

### Group 12: Integration Testing & Refinement
**Goal**: End-to-end testing and refinement

**Tasks**:
1. Test all conversation scenarios
2. Test error handling
3. Test WebSocket reconnection
4. Test session persistence
5. Test context management
6. Performance testing
7. Fix bugs and issues
8. Refine UI/UX
9. Update documentation

**Deliverables**:
- All scenarios tested
- Bugs fixed
- Performance acceptable
- Documentation updated
- System ready for deployment

**Estimated Time**: 4-5 days

**Handoff Context**: See [Group 12 Handoff](#group-12-handoff)

---

## Handoff Documentation Template

Each group should provide handoff documentation including:

1. **What Was Completed**: Summary of deliverables
2. **What's Working**: Current functionality
3. **What's Not Working**: Known issues or limitations
4. **Code Structure**: Where code is located
5. **How to Run**: Instructions to run/test
6. **Dependencies**: What the next group needs
7. **Reference Code**: Links to old code for reference
8. **Next Steps**: What the next group should do

## Group Handoff Contexts

### Group 1 Handoff

**Context for Starting Group 2**:
- Mock server is running on `http://localhost:8000`
- Mock server code is in `fingpt_chat/mock_server/`
- API endpoints match design document specifications
- WebSocket endpoint streams mock progress updates
- Mock data files are in `fingpt_chat/mock_server/data/`
- See `mock_server/README.md` for usage

**Key Files**:
- `mock_server/main.py` - FastAPI app
- `mock_server/routes/chat.py` - Chat endpoints
- `mock_server/websocket/progress.py` - WebSocket handler
- `mock_server/data/responses.py` - Static response data

**Next Group Should**:
- Start with frontend setup
- Connect to mock server for testing
- Use mock server to develop UI without agents

---

### Group 2 Handoff

**Context for Starting Group 3**:
- React app structure is set up
- Two-column layout is implemented
- API client service is configured
- WebSocket client service is configured
- Basic styling system is in place
- App runs on `http://localhost:3000`

**Key Files**:
- `frontend/src/components/Layout/TwoColumnLayout.tsx`
- `frontend/src/services/api.ts`
- `frontend/src/services/websocket.ts`

**Next Group Should**:
- Build chat interface components
- Use API client to connect to mock server
- Test with mock data

---

### Group 3 Handoff

**Context for Starting Group 4**:
- Chat interface is functional
- Messages display correctly
- Markdown rendering works
- Input and send work
- Connected to mock server

**Key Files**:
- `frontend/src/components/Chat/ChatInterface.tsx`
- `frontend/src/components/Chat/MessageList.tsx`
- `frontend/src/components/Chat/MessageBubble.tsx`

**Next Group Should**:
- Build progress tracking components
- Connect WebSocket for real-time updates
- Use mock WebSocket for testing

---

### Group 4 Handoff

**Context for Starting Group 5**:
- Progress panel is functional
- Real-time updates work via WebSocket
- Timeline visualization works
- Progress events display correctly

**Key Files**:
- `frontend/src/components/Progress/ProgressPanel.tsx`
- `frontend/src/hooks/useWebSocket.ts`

**Next Group Should**:
- Build results panel components
- Display analysis reports
- Show visualizations
- Display agent activity

---

### Group 5 Handoff

**Context for Starting Group 6**:
- Results panel is functional
- Analysis report displays correctly
- Charts work and are interactive
- Agent activity metrics shown

**Key Files**:
- `frontend/src/components/Results/ResultsPanel.tsx`
- `frontend/src/components/Results/Visualizations.tsx`

**Next Group Should**:
- Implement session management
- Create state management hooks
- Handle session persistence
- Load conversation history

---

### Group 6 Handoff

**Context for Starting Group 7**:
- Frontend is complete and functional
- UI layout and behavior verified with mock server
- All components work together
- Ready to connect to actual backend

**Key Files**:
- All frontend components
- State management hooks
- API and WebSocket clients

**Next Group Should**:
- Build actual FastAPI backend
- Replace mock server
- Keep same API structure
- No agent integration yet

---

### Group 7 Handoff

**Context for Starting Group 8**:
- FastAPI backend is set up
- API endpoints are implemented
- WebSocket endpoint is implemented
- Validation and error handling work
- API documentation available

**Key Files**:
- `server/api/routes/chat.py`
- `server/api/websocket/progress.py`
- `server/api/models/chat.py`

**Next Group Should**:
- Implement SessionService
- File-based session storage
- Session CRUD operations

---

### Group 8 Handoff

**Context for Starting Group 9**:
- SessionService is implemented
- File-based storage works
- Sessions persist correctly
- Session operations work

**Key Files**:
- `server/services/session_service.py`
- `server/storage/session_store.py`

**Next Group Should**:
- Implement ContextManager
- Context merging logic
- Incremental query detection
- Context pruning

---

### Group 9 Handoff

**Context for Starting Group 10**:
- ContextManager is implemented
- Context merging works
- Incremental queries detected
- Context pruning works

**Key Files**:
- `server/services/context_manager.py`

**Next Group Should**:
- Implement ChatService
- Message processing flow
- Intent detection
- Clarification questions

---

### Group 10 Handoff

**Context for Starting Group 11**:
- ChatService is implemented
- Intent detection works
- Clarification questions generated
- Error handling works

**Key Files**:
- `server/services/chat_service.py`

**Next Group Should**:
- Integrate existing workflow
- Connect agents
- Implement progress streaming
- Test end-to-end

---

### Group 11 Handoff

**Context for Starting Group 12**:
- WorkflowService integrated
- Agents connected and working
- Progress streaming works
- End-to-end flow works

**Key Files**:
- `server/services/workflow_service.py`
- `server/agents/` (copied from basic_agent_version)
- `server/orchestrator/` (copied from basic_agent_version)

**Next Group Should**:
- Test all scenarios
- Fix bugs
- Performance testing
- Final refinement

---

### Group 12 Handoff

**Context for Deployment**:
- All functionality complete
- All tests passing
- Performance acceptable
- Documentation updated
- System ready for deployment

**Key Files**:
- Complete codebase
- Test suite
- Documentation

**Next Steps**:
- Deploy to production
- Monitor performance
- Gather user feedback
- Plan enhancements

---

## Reference Guide: Old Code Functionality

### Agent Components (`basic_agent_version/src/agents/`)

**Location**: `basic_agent_version/src/agents/`

**Key Files**:
- `base_agent.py` - Base agent class with common functionality
- `research_agent.py` - Research agent for data gathering
- `analyst_agent.py` - Analyst agent for analysis
- `reporting_agent.py` - Reporting agent for report generation

**What to Copy**:
- Copy entire `agents/` directory to `server/agents/`
- No modifications needed initially
- Agents work as-is

**Reference Points**:
- Agent execution: `base_agent.py:run()`
- Progress reporting: `base_agent.py:report_progress()`
- Context reading/writing: `base_agent.py:read_context()`, `write_context()`

---

### Orchestrator Components (`basic_agent_version/src/orchestrator/`)

**Location**: `basic_agent_version/src/orchestrator/`

**Key Files**:
- `workflow.py` - Main workflow orchestrator
- `graph.py` - LangGraph graph definition
- `state.py` - State management and AgentState

**What to Copy**:
- Copy entire `orchestrator/` directory to `server/orchestrator/`
- Wrap workflow with WorkflowService for chat integration
- Modify workflow to support streaming progress

**Reference Points**:
- Workflow execution: `workflow.py:process_query()`
- Streaming: `workflow.py:stream_query()`
- State creation: `state.py:StateManager.create_initial_state()`

---

### MCP Clients (`basic_agent_version/src/mcp/`)

**Location**: `basic_agent_version/src/mcp/`

**Key Files**:
- `mcp_client.py` - Unified MCP client
- `yahoo_finance.py` - Yahoo Finance integration
- `alpha_vantage.py` - Alpha Vantage integration
- `fmp.py` - Financial Modeling Prep integration

**What to Copy**:
- Copy entire `mcp/` directory to `server/mcp/`
- No modifications needed
- Works as-is

**Reference Points**:
- Data fetching: `mcp_client.py:UnifiedMCPClient`
- Citation tracking: Built into MCP clients

---

### Vector Database (`basic_agent_version/src/vector_db/`)

**Location**: `basic_agent_version/src/vector_db/`

**Key Files**:
- `chroma_client.py` - Chroma client
- `embeddings.py` - Embedding pipeline
- `context_integration.py` - Context integration

**What to Copy**:
- Copy entire `vector_db/` directory to `server/vector_db/`
- No modifications needed
- Works as-is

**Reference Points**:
- Vector DB operations: `chroma_client.py:ChromaClient`
- Embeddings: `embeddings.py:EmbeddingPipeline`

---

### Utilities (`basic_agent_version/src/utils/`)

**Location**: `basic_agent_version/src/utils/`

**Key Files**:
- `guardrails.py` - Input validation and security
- `llm_config.py` - LLM configuration
- `integration_config.py` - Integration configuration
- `progress_tracker.py` - Progress tracking utilities
- `context_cache.py` - Context caching
- `token_tracker.py` - Token usage tracking

**What to Copy**:
- Copy entire `utils/` directory to `server/utils/`
- No modifications needed
- Works as-is

**Reference Points**:
- Guardrails: `guardrails.py:guardrails.validate_query()`
- LLM config: `llm_config.py:llm_config`
- Progress tracking: `progress_tracker.py:ProgressTracker`

---

### Configuration (`basic_agent_version/config/`)

**Location**: `basic_agent_version/config/`

**Key Files**:
- `agent_config.yaml` - Agent configuration
- `integrations.yaml` - Integration configuration
- `llm_templates.yaml` - LLM provider templates

**What to Copy**:
- Copy entire `config/` directory to `server/config/`
- May need to update paths
- Works as-is

**Reference Points**:
- Agent config: Used by agents
- Integration config: Used by MCP clients
- LLM config: Used by LLM calls

---

## Notes on Integration

### Workflow Integration Points

1. **WorkflowService wraps existing workflow**:
   - Create `WorkflowService` class
   - Initialize existing `MyFinGPTWorkflow` instance
   - Add session/context management layer
   - Stream progress updates via WebSocket

2. **State Management**:
   - Reuse existing `AgentState` TypedDict
   - Extend with session_id and conversation context
   - Merge conversation context with query context

3. **Progress Streaming**:
   - Existing workflow has `stream_query()` method
   - Wrap to send updates via WebSocket
   - Format progress events for frontend

4. **Agent Execution**:
   - Agents work as-is, no changes needed
   - Agents report progress via existing mechanism
   - Progress events captured and streamed

### Testing Strategy

1. **Mock Server Testing**:
   - Test UI with mock server (Groups 1-6)
   - Verify layout and behavior
   - Test all UI components

2. **Backend Testing**:
   - Test API endpoints (Group 7)
   - Test services independently (Groups 8-10)
   - Unit tests for each service

3. **Integration Testing**:
   - Test with actual agents (Group 11)
   - End-to-end testing (Group 12)
   - Scenario testing

### Migration Notes

- **No changes to `basic_agent_version`**: All code is copied, not modified
- **Gradual migration**: Mock server → Backend → Agents
- **Clean separation**: Mock server in separate folder, removed when done
- **Reference old code**: Use reference guide for functionality lookup


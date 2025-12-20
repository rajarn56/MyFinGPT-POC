# MyFinGPT Chat - Documentation

This directory contains comprehensive documentation for the MyFinGPT Chat rearchitecture project.

## Documents

### 1. [Requirements Document](requirements.md)
Complete functional and non-functional requirements for the chat-based MyFinGPT system. Includes:
- System goals and objectives
- Functional requirements (UI, Server, Communication, Session Management)
- Non-functional requirements (Performance, Scalability, Reliability)
- Technology stack requirements
- Interface requirements
- Constraints and success criteria

### 2. [Architecture Document](architecture.md)
High-level system architecture and component design. Includes:
- System overview and architecture principles
- Component architecture (Frontend and Backend)
- Communication architecture (REST API and WebSocket)
- Data architecture (Session storage, State management)
- Layer architecture (Presentation, API, Business Logic, Agent, Data)
- Mock server architecture (for UI development)
- Deployment architecture
- Security architecture
- Technology stack

### 3. [Design Document](design.md)
Detailed design specifications with interfaces and models. Includes:
- Complete API design (REST endpoints and WebSocket)
- Data models (TypeScript and Python)
- Service design (ChatService, SessionService, ContextManager, WorkflowService)
- Frontend design (Component hierarchy, State management, Custom hooks)
- Backend implementation details (FastAPI structure, Session storage, WebSocket streaming)
- Mock server design and implementation
- Error handling
- Configuration
- Testing strategy
- Deployment configuration

### 4. [Conversation Scenarios](conversation_scenarios.md)
Comprehensive conversation scenarios and test cases. Includes:
- Basic single stock analysis scenarios
- Multi-stock comparison scenarios
- Trend analysis scenarios
- Sentiment analysis scenarios
- Financial metrics queries
- Context continuity scenarios
- Ambiguous query handling
- Error handling scenarios
- Complex queries
- Follow-up questions
- Edge cases
- Performance scenarios
- Session management scenarios
- Intent detection scenarios
- Testing checklist and success criteria

### 5. [Implementation Plan](implementation_plan.md)
Detailed task breakdown into manageable groups. Includes:
- 12 implementation groups with specific tasks
- Estimated time for each group
- Handoff documentation for each group
- Context for starting next group in new chat session
- Reference guide for old code functionality
- Testing strategy per group
- Migration notes

### 6. [Code Reference Guide](code_reference_guide.md)
Reference guide for locating and understanding functionality from `basic_agent_version`. Includes:
- Quick reference map of component locations
- Detailed component reference (Agents, Orchestrator, MCP, Vector DB, Utilities)
- Integration patterns
- Copy strategy (what to copy, what to modify)
- Common patterns and usage examples
- Troubleshooting tips

### 7. [Setup and Operations Guide](setup_and_operations.md)
Complete setup, start, stop, and restart instructions for each layer. Includes:
- Prerequisites and system requirements
- Mock server operations (setup, start, stop, restart)
- Frontend operations (setup, start, stop, restart)
- Backend server operations (setup, start, stop, restart)
- Testing instructions for each group
- Troubleshooting guide
- Environment variables configuration

### 8. [Group 1-6 Handoff Context](group_1-6_handoff_context.md)
Complete context for starting Groups 1-6 (UI Development Phase) in a new chat session. Includes:
- Project overview and current state
- Detailed tasks for each group (1-6)
- Directory structures to create
- Setup instructions per group
- Testing instructions per group
- Deliverables checklist
- Quick start commands
- Success criteria

## Document Purpose

These documents serve as:
1. **Requirements**: What needs to be built
2. **Architecture**: How the system is structured
3. **Design**: Detailed specifications for implementation
4. **Scenarios**: Test cases and validation criteria

## Reading Order

For understanding the project:
1. Start with **Requirements** to understand what we're building
2. Read **Architecture** to understand the high-level structure
3. Review **Design** for implementation details
4. Review **Implementation Plan** to understand task breakdown
5. Use **Code Reference Guide** when implementing (to find old code)
6. Use **Conversation Scenarios** for testing and validation

For implementing:
1. **Start with Group 1-6**: Read **Group 1-6 Handoff Context** for complete setup
2. Follow **Setup and Operations Guide** for running components
3. Review **Implementation Plan** - work through groups sequentially
4. Review **Code Reference Guide** - find relevant old code when needed
5. Follow **Design** specifications for your group
6. Test using **Conversation Scenarios**
7. Document handoff for next group

**Quick Start for Groups 1-6**:
- Read `group_1-6_handoff_context.md` first
- Follow `setup_and_operations.md` for setup
- Use `implementation_plan.md` for task details

## Key Design Decisions

### Frontend
- **Framework**: React with TypeScript
- **Layout**: Two-column layout (50/50 split) as per architecture.md section 11
- **Real-time**: WebSocket for progress updates
- **Charts**: Plotly.js or Recharts for visualizations

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **API**: REST for chat operations, WebSocket for progress
- **Session Storage**: File-based initially (can migrate to database)
- **Agent Integration**: Reuses all existing agent components

### Communication
- **REST API**: Standard HTTP/JSON for chat operations
- **WebSocket**: Real-time progress streaming
- **Session Management**: Server-side session storage

### Development Approach
- **Mock Server**: Separate mock server for UI development (removed when done)
- **Task Groups**: Implementation broken into 12 manageable groups
- **Handoff Documentation**: Each group documents handoff for next group
- **Code Reuse**: Reference guide helps locate old code functionality

## Next Steps

After reviewing these documents:
1. Review and approve the design
2. Plan implementation phases
3. Set up development environment
4. Begin implementation following the design specifications

## Questions or Clarifications

If you have questions about any aspect of the design, please refer to the relevant document section or discuss with the architecture team.


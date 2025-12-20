# MyFinGPT Chat - Code Reference Guide

This document provides a reference guide for locating and understanding functionality from the `basic_agent_version` codebase that will be reused in the new chat system.

## Purpose

When implementing the chat system, you may need to reference existing functionality. This guide helps you quickly locate the relevant code and understand how it works.

## Quick Reference Map

### Agent Execution Flow

**Entry Point**: `basic_agent_version/main.py`
- Application entry point
- UI mode selection (Gradio/Streamlit)
- Configuration setup

**Workflow**: `basic_agent_version/src/orchestrator/workflow.py`
- `MyFinGPTWorkflow.process_query()` - Process single query
- `MyFinGPTWorkflow.stream_query()` - Stream query with progress updates
- Transaction ID generation
- Query validation and sanitization

**Graph**: `basic_agent_version/src/orchestrator/graph.py`
- `MyFinGPTGraph` - LangGraph graph definition
- Node functions: `_research_node()`, `_analyst_node()`, `_reporting_node()`
- Graph execution and state transitions

**State**: `basic_agent_version/src/orchestrator/state.py`
- `AgentState` TypedDict - State structure
- `StateManager` - State management utilities
- State creation, validation, merging, pruning

---

## Component Reference

### 1. Agents (`basic_agent_version/src/agents/`)

#### Base Agent (`base_agent.py`)

**Purpose**: Base class for all agents with common functionality

**Key Methods**:
- `run(state)` - Main execution wrapper with validation and tracking
- `execute(state)` - Abstract method implemented by subclasses
- `read_context(state, field, default)` - Read from shared state
- `write_context(state, field, value)` - Write to shared state
- `call_llm(messages, state, max_retries)` - LLM call with retry logic
- `report_progress(state, event_type, message, ...)` - Report progress event
- `start_task(state, task_name)` - Mark task start
- `complete_task(state, task_name)` - Mark task completion
- `report_agent_start(state)` - Report agent execution start
- `report_agent_complete(state, execution_time)` - Report agent completion

**Usage in Chat System**:
- Copy entire file to `server/agents/base_agent.py`
- No modifications needed
- All agents inherit from this

**Reference Points**:
```python
# Line 250-301: run() method - Main execution wrapper
# Line 130-229: call_llm() - LLM calls with retry
# Line 321-354: report_progress() - Progress reporting
```

#### Research Agent (`research_agent.py`)

**Purpose**: Gathers financial data from multiple sources

**Key Methods**:
- `execute(state)` - Main execution logic
- Fetches: stock price, company info, news, historical data, financials
- Stores news in vector DB
- Writes `research_data` to state

**Usage in Chat System**:
- Copy entire file to `server/agents/research_agent.py`
- No modifications needed
- Works as-is

**Reference Points**:
```python
# Line ~50-200: execute() method - Main logic
# Fetches data from MCP clients
# Stores news in vector DB
```

#### Analyst Agent (`analyst_agent.py`)

**Purpose**: Performs financial analysis and generates insights

**Key Methods**:
- `execute(state)` - Main execution logic
- `_analyze_financials()` - Financial ratio analysis
- `_analyze_sentiment()` - Sentiment analysis via LLM
- `_analyze_trends()` - Trend pattern analysis
- `_generate_recommendation()` - Investment recommendation

**Usage in Chat System**:
- Copy entire file to `server/agents/analyst_agent.py`
- No modifications needed
- Works as-is

**Reference Points**:
```python
# Line ~50-300: execute() method - Main logic
# Performs various analyses
# Writes analysis_results to state
```

#### Reporting Agent (`reporting_agent.py`)

**Purpose**: Synthesizes findings into comprehensive reports

**Key Methods**:
- `execute(state)` - Main execution logic
- `_generate_report()` - LLM-based report generation
- `_prepare_visualizations()` - Prepare chart data
- `_store_report_in_vector_db()` - Store for future reference

**Usage in Chat System**:
- Copy entire file to `server/agents/reporting_agent.py`
- No modifications needed
- Works as-is

**Reference Points**:
```python
# Line ~50-300: execute() method - Main logic
# Generates final report
# Prepares visualizations
# Writes final_report to state
```

---

### 2. Orchestrator (`basic_agent_version/src/orchestrator/`)

#### Workflow (`workflow.py`)

**Purpose**: Main workflow orchestrator

**Key Methods**:
- `process_query(query)` - Process query and return results
- `stream_query(query)` - Stream query with progress updates
- `_detect_incremental_query()` - Detect incremental queries
- `_detect_similar_queries()` - Find similar previous queries

**Usage in Chat System**:
- Copy to `server/orchestrator/workflow.py`
- Wrap with `WorkflowService` for chat integration
- Modify `stream_query()` to send updates via WebSocket

**Reference Points**:
```python
# Line 30-177: process_query() - Main processing
# Line 241-313: stream_query() - Streaming with progress
# Line 179-206: _detect_incremental_query() - Incremental detection
```

#### Graph (`graph.py`)

**Purpose**: LangGraph graph definition

**Key Methods**:
- `_research_node(state)` - Research agent node
- `_analyst_node(state)` - Analyst agent node
- `_reporting_node(state)` - Reporting agent node
- `run(state)` - Execute graph
- `stream(state)` - Stream graph execution

**Usage in Chat System**:
- Copy to `server/orchestrator/graph.py`
- No modifications needed
- Works as-is

**Reference Points**:
```python
# Graph definition with nodes
# State transitions
# Execution flow
```

#### State (`state.py`)

**Purpose**: State management and utilities

**Key Classes**:
- `AgentState` - TypedDict for state structure
- `StateManager` - State management utilities

**Key Methods**:
- `create_initial_state()` - Create state from query
- `update_research_data()` - Update research data
- `update_analysis_results()` - Update analysis results
- `merge_parallel_contexts()` - Merge parallel results
- `prune_context()` - Reduce context size
- `add_progress_event()` - Add progress event

**Usage in Chat System**:
- Copy to `server/orchestrator/state.py`
- Extend `AgentState` with session_id and conversation context
- Modify `create_initial_state()` to merge conversation context

**Reference Points**:
```python
# Line 18-81: AgentState TypedDict definition
# Line 83-145: StateManager.create_initial_state()
# Line 297-344: merge_parallel_contexts()
# Line 597-662: prune_context()
```

---

### 3. MCP Clients (`basic_agent_version/src/mcp/`)

#### Unified MCP Client (`mcp_client.py`)

**Purpose**: Unified interface for multiple data sources

**Key Methods**:
- `get_stock_price()` - Get price with fallback
- `get_company_info()` - Get company info with fallback
- `get_financial_statements()` - Get financials
- `get_news()` - Get news articles
- `get_historical_data()` - Get historical prices

**Usage in Chat System**:
- Copy entire `mcp/` directory to `server/mcp/`
- No modifications needed
- Works as-is

**Reference Points**:
```python
# UnifiedMCPClient class
# Fallback logic between sources
# Citation tracking
```

#### Individual MCP Clients

- `yahoo_finance.py` - Yahoo Finance integration
- `alpha_vantage.py` - Alpha Vantage API integration
- `fmp.py` - Financial Modeling Prep API integration
- `mcp_base.py` - Base class with retry logic

**Usage**: Copy all files, no modifications needed

---

### 4. Vector Database (`basic_agent_version/src/vector_db/`)

#### Chroma Client (`chroma_client.py`)

**Purpose**: Vector database operations

**Key Methods**:
- `store_document()` - Store document with embedding
- `query_similar()` - Semantic search
- `get_collection_stats()` - Get collection statistics

**Usage in Chat System**:
- Copy entire `vector_db/` directory to `server/vector_db/`
- No modifications needed
- Works as-is

**Reference Points**:
```python
# ChromaClient class
# Collection management
# Query operations
```

#### Embeddings (`embeddings.py`)

**Purpose**: Embedding generation

**Key Methods**:
- `generate_embedding()` - Generate single embedding
- `generate_embeddings_batch()` - Generate multiple embeddings

**Usage**: Copy file, no modifications needed

---

### 5. Utilities (`basic_agent_version/src/utils/`)

#### Guardrails (`guardrails.py`)

**Purpose**: Input validation and security

**Key Methods**:
- `validate_query()` - Validate user query
- `sanitize_input()` - Sanitize input
- `validate_symbol()` - Validate stock symbol
- `extract_symbols()` - Extract symbols from query
- `validate_state()` - Validate state structure

**Usage in Chat System**:
- Copy to `server/utils/guardrails.py`
- No modifications needed
- Use for all input validation

**Reference Points**:
```python
# Guardrails class with all validation methods
# Used throughout workflow
```

#### LLM Config (`llm_config.py`)

**Purpose**: LLM provider configuration

**Key Methods**:
- `get_provider_config()` - Get provider configuration
- `create_litellm_client()` - Create LiteLLM client
- `list_available_providers()` - List available providers

**Usage in Chat System**:
- Copy to `server/utils/llm_config.py`
- No modifications needed
- Used by all agents

**Reference Points**:
```python
# LLMConfig class
# Provider selection logic
# Configuration loading
```

#### Progress Tracker (`progress_tracker.py`)

**Purpose**: Progress event management

**Key Methods**:
- `create_event()` - Create progress event
- `create_agent_start_event()` - Agent start event
- `create_agent_complete_event()` - Agent complete event
- `create_task_start_event()` - Task start event
- `create_task_complete_event()` - Task complete event

**Usage in Chat System**:
- Copy to `server/utils/progress_tracker.py`
- No modifications needed
- Used for progress tracking

**Reference Points**:
```python
# ProgressTracker class
# Event creation methods
# Event formatting
```

#### Context Cache (`context_cache.py`)

**Purpose**: In-memory caching of API responses

**Key Methods**:
- `get()` - Get cached data
- `set()` - Cache data
- `find_similar_queries()` - Find similar queries

**Usage in Chat System**:
- Copy to `server/utils/context_cache.py`
- No modifications needed
- Used for performance optimization

**Reference Points**:
```python
# ContextCache class
# 24-hour TTL caching
# Query similarity detection
```

#### Integration Config (`integration_config.py`)

**Purpose**: Integration enable/disable management

**Key Methods**:
- `is_enabled()` - Check if integration enabled
- `get_enabled_integrations()` - Get enabled integrations
- `get_preferred_source()` - Get preferred source for data type

**Usage in Chat System**:
- Copy to `server/utils/integration_config.py`
- No modifications needed
- Used by MCP clients

**Reference Points**:
```python
# IntegrationConfig class
# Configuration loading
# Integration checks
```

---

### 6. Configuration (`basic_agent_version/config/`)

#### Agent Config (`agent_config.yaml`)

**Purpose**: Agent behavior configuration

**Usage**: Copy to `server/config/agent_config.yaml`

#### Integrations Config (`integrations.yaml`)

**Purpose**: Integration enable/disable configuration

**Usage**: Copy to `server/config/integrations.yaml`

#### LLM Templates (`llm_templates.yaml`)

**Purpose**: LLM provider templates

**Usage**: Copy to `server/config/llm_templates.yaml`

---

## Integration Patterns

### How to Integrate Workflow

```python
# In WorkflowService
from server.orchestrator.workflow import MyFinGPTWorkflow

class WorkflowService:
    def __init__(self):
        self.workflow = MyFinGPTWorkflow()
    
    async def execute_with_streaming(self, query, context, session_id, progress_callback):
        # Create initial state with conversation context
        initial_state = self.create_initial_state(query, context, session_id)
        
        # Stream workflow execution
        for update in self.workflow.stream_query(query):
            # Send progress updates via WebSocket
            progress_callback(update)
        
        return final_state
```

### How to Use Agents

```python
# Agents work as-is, no changes needed
from server.agents.research_agent import ResearchAgent

research_agent = ResearchAgent()
state = research_agent.run(state)  # Works exactly as before
```

### How to Use MCP Clients

```python
# MCP clients work as-is
from server.mcp.mcp_client import UnifiedMCPClient

mcp_client = UnifiedMCPClient()
price_data = mcp_client.get_stock_price("AAPL")  # Works as before
```

## Copy Strategy

### What to Copy

1. **Entire Directories** (copy as-is):
   - `src/agents/` → `server/agents/`
   - `src/mcp/` → `server/mcp/`
   - `src/vector_db/` → `server/vector_db/`
   - `src/utils/` → `server/utils/`
   - `config/` → `server/config/`

2. **Files to Modify**:
   - `src/orchestrator/workflow.py` → Wrap with WorkflowService
   - `src/orchestrator/state.py` → Extend with session context
   - `src/orchestrator/graph.py` → Copy as-is

### What NOT to Copy

- `src/ui/` - New frontend replaces this
- `main.py` - New entry point
- `scripts/` - Not needed for chat system

## Testing Reference

### How Existing Code is Tested

- Agents: Unit tests for each agent
- Workflow: Integration tests
- MCP Clients: Mock API responses
- Vector DB: Test with test data

### Testing Strategy for Chat System

1. Test agents independently (reuse existing tests)
2. Test workflow integration
3. Test chat service with mock workflow
4. End-to-end tests with actual agents

## Common Patterns

### Progress Reporting Pattern

```python
# In agent execute() method
state = self.report_progress(
    state,
    event_type=ProgressTracker.EVENT_TYPES["TASK_START"],
    message="Fetching stock price",
    task_name="fetch_price",
    symbol="AAPL"
)
```

### Context Reading Pattern

```python
# Read from state
research_data = self.read_context(state, "research_data", {})
symbol_data = research_data.get("AAPL", {})
```

### Context Writing Pattern

```python
# Write to state
state = self.write_context(state, "research_data", {
    "AAPL": {
        "price": 150.0,
        "company": {...}
    }
})
```

### Citation Tracking Pattern

```python
# Add citation
state = self.add_citation(
    state,
    source="Yahoo Finance",
    url="https://finance.yahoo.com/quote/AAPL",
    data_point="Stock Price",
    symbol="AAPL"
)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Check Python path, ensure copied files are in correct location
2. **State Structure**: Ensure AgentState matches expected structure
3. **Progress Events**: Check event format matches ProgressTracker expectations
4. **LLM Calls**: Verify LLM configuration is correct

### Debugging Tips

1. Check transaction IDs in logs
2. Verify state structure at each step
3. Check progress events are being created
4. Verify MCP client responses
5. Check vector DB connections

## Summary

- **Agents**: Copy as-is, no modifications
- **Workflow**: Wrap with service layer, add streaming
- **MCP Clients**: Copy as-is, no modifications
- **Vector DB**: Copy as-is, no modifications
- **Utilities**: Copy as-is, no modifications
- **State**: Extend with session context
- **Configuration**: Copy as-is, update paths if needed

All existing functionality is preserved and reused. The chat system adds a new layer (API + Session Management) on top of existing components.


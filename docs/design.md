# MyFinGPT Design Document

## 1. Agent Design

### 1.1 Base Agent Class Design

**File**: `src/agents/base_agent.py`

**Purpose**: Provides common functionality for all agents

**Key Methods**:
- `read_context(state, field, default)`: Read from shared state
- `write_context(state, field, value)`: Write to shared state
- `validate_required_context(state, fields)`: Validate context before execution
- `add_citation(state, ...)`: Add citation to state
- `track_tokens(state, tokens)`: Track token usage
- `call_llm(messages)`: Make LLM call with LiteLLM
- `report_progress(state, event_type, message, ...)`: Report progress event
- `start_task(state, task_name, ...)`: Mark task start
- `complete_task(state, task_name, ...)`: Mark task completion
- `report_agent_start(state)`: Report agent execution start
- `report_agent_complete(state, execution_time)`: Report agent execution complete
- `execute(state)`: Abstract method implemented by subclasses
- `run(state)`: Wrapper that handles validation, execution, and tracking

**Design Patterns**:
- Template Method Pattern: `run()` defines algorithm, `execute()` is template
- Strategy Pattern: LLM provider can be swapped via configuration

### 1.2 Research Agent Design

**File**: `src/agents/research_agent.py`

**Responsibilities**:
- Read query context from state
- Fetch data from MCP clients (Yahoo Finance, Alpha Vantage, FMP)
- Store data in shared context with citations
- Store news/articles in vector DB
- Write `research_data` to context

**Key Methods**:
- `execute(state)`: Main execution logic
- `_store_news_in_vector_db(symbol, articles)`: Store news with embeddings

**Context Dependencies**:
- Reads: `query`, `symbols`, `query_type`
- Writes: `research_data`, `research_metadata`, `citations`

### 1.3 Analyst Agent Design

**File**: `src/agents/analyst_agent.py`

**Responsibilities**:
- Read `research_data` from context
- Query vector DB for similar historical patterns
- Perform financial analysis
- Perform sentiment analysis (using LLM)
- Perform trend analysis
- Generate recommendations
- Write `analysis_results` to context

**Key Methods**:
- `execute(state)`: Main execution logic
- `_query_historical_patterns(symbol, data)`: Vector DB search
- `_analyze_financials(symbol, data)`: Financial ratio analysis
- `_analyze_sentiment(symbol, news)`: Sentiment analysis via LLM
- `_analyze_trends(symbol, historical)`: Trend pattern analysis
- `_generate_recommendation(...)`: Investment recommendation
- `_generate_reasoning(symbol, analysis)`: Reasoning chain

**Context Dependencies**:
- Reads: `research_data`
- Writes: `analysis_results`, `analysis_reasoning`, `sentiment_analysis`, `trend_analysis`

### 1.4 Reporting Agent Design

**File**: `src/agents/reporting_agent.py`

**Responsibilities**:
- Read `research_data` and `analysis_results` from context
- Query vector DB for citations
- Generate comprehensive report using LLM
- Prepare visualization data
- Write `final_report` to context
- Store report in vector DB for learning

**Key Methods**:
- `execute(state)`: Main execution logic
- `_generate_report(...)`: LLM-based report generation
- `_prepare_context_summary(...)`: Summarize context for LLM
- `_prepare_visualizations(...)`: Prepare chart data
- `_store_report_in_vector_db(...)`: Store for future reference

**Context Dependencies**:
- Reads: `research_data`, `analysis_results`, `citations`
- Writes: `final_report`, `visualizations`

### 1.5 Agent Communication Patterns

**Sequential Communication**:
- Research → Analyst → Reporting
- Each agent waits for previous agent's output
- Context validated at each step

**Error Handling**:
- Agents preserve context on errors
- Errors logged but don't stop workflow
- Partial results included in final output

## 2. Orchestration Design

### 2.1 LangGraph State Design

**File**: `src/orchestrator/state.py`

**State Structure** (`AgentState` TypedDict):
```python
{
    "transaction_id": str,  # Unique transaction identifier (8-character hex)
    "query": str,
    "query_type": str,
    "symbols": List[str],
    "research_data": Dict[str, Any],
    "research_metadata": Dict[str, Any],
    "analysis_results": Dict[str, Any],
    "analysis_reasoning": Dict[str, str],
    "sentiment_analysis": Dict[str, Any],
    "trend_analysis": Dict[str, Any],
    "comparison_data": Dict[str, Any],
    "citations": List[Dict],
    "vector_db_references": List[str],
    "token_usage": Dict[str, int],
    "execution_time": Dict[str, float],
    "final_report": str,
    "visualizations": Dict[str, Any],
    "context_version": int,
    "context_size": int,
    "agents_executed": List[str],
    
    # Progress Tracking
    "progress_events": List[Dict[str, Any]],  # Real-time progress events
    "current_agent": Optional[str],  # Currently executing agent
    "current_tasks": Dict[str, List[str]],  # Current tasks per agent
    "execution_order": List[Dict[str, Any]]  # Execution order with timing
}
```

**State Manager** (`StateManager`):
- `create_initial_state(query, transaction_id)`: Create state from query with transaction ID
- `update_research_data(state, symbol, data)`: Update research data
- `update_analysis_results(state, symbol, results)`: Update analysis
- `add_citation(state, ...)`: Add citation
- `track_token_usage(state, agent, tokens)`: Track tokens
- `validate_context(state, fields)`: Validate required fields
- `merge_parallel_contexts(contexts)`: Merge parallel results
- `prune_context(state)`: Reduce context size
- `add_progress_event(state, event)`: Add progress event to state
- `add_execution_order_entry(state, agent, start_time, end_time)`: Add execution order entry

**Transaction ID Generation**:
- Generated in `workflow.process_query()` using UUID (8-character hex)
- Included in initial state creation
- Propagated through all log entries
- Displayed in UI report header and Agent Activity tab

### 2.2 Sequential Execution Design

**File**: `src/orchestrator/graph.py`

**Flow**:
```
Entry → Research Node → Analyst Node → Reporting Node → END
```

**Node Functions**:
- `_research_node(state)`: Calls Research Agent
- `_analyst_node(state)`: Calls Analyst Agent
- `_reporting_node(state)`: Calls Reporting Agent

**State Validation**:
- Each node validates required context before execution
- Context size updated after each node

### 2.3 Parallel Execution Design

**Future Enhancement**:
- Multiple Research Agents for different symbols
- Context merging after parallel execution
- Multiple Analyst Agents with shared context

**Implementation Pattern**:
```python
# Parallel research for multiple symbols
research_results = []
for symbol in symbols:
    result = research_agent.execute(state_for_symbol)
    research_results.append(result)

# Merge contexts
merged_state = StateManager.merge_parallel_contexts(research_results)
```

### 2.4 Context Sharing Mechanism

**Shared State**: LangGraph StateGraph maintains single state object

**Access Pattern**:
- Agents read only what they need
- Agents write to specific fields
- No direct agent-to-agent communication
- All communication through shared state

**Context Optimization**:
- Context pruning removes unnecessary data
- Context compression for large datasets
- Context size monitoring

### 2.5 State Transitions

**Transition Rules**:
1. Research → Analyst: Requires `research_data`
2. Analyst → Reporting: Requires `analysis_results`
3. Reporting → END: Always proceeds

**Error Handling**:
- Failed agents preserve partial context
- Workflow continues with available data
- Errors logged in state metadata

## 3. MCP Integration Design

### 3.1 MCP Client Wrapper Design

**File**: `src/mcp/mcp_client.py`

**UnifiedMCPClient**:
- Wraps Yahoo Finance, Alpha Vantage, and FMP clients
- Provides fallback logic
- Aggregates citations from all sources

**Methods**:
- `get_stock_price(symbol, preferred_source)`: Get price with fallback
- `get_company_info(symbol, preferred_source)`: Get info with fallback
- `get_all_citations()`: Aggregate citations

### 3.2 Yahoo Finance Integration Design

**File**: `src/mcp/yahoo_finance.py`

**Implementation**: Uses `yfinance` library

**Methods**:
- `get_stock_price(symbol)`: Current price and basic info
- `get_company_info(symbol)`: Company profile
- `get_historical_data(symbol, period)`: Historical prices
- `get_financials(symbol)`: Financial statements
- `get_news(symbol, count)`: News articles

**Citation Tracking**: Automatic citation generation for all data

### 3.3 Alpha Vantage Integration Design

**File**: `src/mcp/alpha_vantage.py`

**Implementation**: REST API calls

**Rate Limiting**: 12-second delay (free tier: 5 calls/minute)

**Methods**:
- `get_stock_price(symbol)`: Real-time quote
- `get_company_info(symbol)`: Company overview
- `get_technical_indicators(symbol, indicator)`: Technical analysis

**Error Handling**: Exponential backoff on rate limits

### 3.4 FMP Integration Design

**File**: `src/mcp/fmp.py`

**Implementation**: REST API calls

**Methods**:
- `get_stock_price(symbol)`: Current price
- `get_company_info(symbol)`: Company profile
- `get_financial_statements(symbol, type)`: Financial statements
- `get_news(symbol, limit)`: Company news

### 3.5 Error Handling and Retry Logic

**Base Class** (`MCPBaseClient`):
- Exponential backoff on failures
- Rate limit detection and handling
- Maximum retry attempts (default: 3)
- Context-preserving error handling

**Retry Strategy**:
1. First retry: Wait 2 seconds
2. Second retry: Wait 4 seconds
3. Third retry: Wait 8 seconds
4. Fail gracefully with error message

## 4. Vector Database Design

### 4.1 Chroma Schema Design

**Collections**:
1. `financial_news`: News articles with embeddings
2. `company_analysis`: Historical analysis reports
3. `market_trends`: Trend patterns and insights

**Document Structure**:
- `id`: Unique document ID
- `document`: Text content
- `metadata`: Symbol, date, source, etc.
- `embedding`: Vector embedding (1536 dimensions)

### 4.2 Collection Structure

**financial_news**:
- Stores news articles from Research Agent
- Metadata: symbol, title, url, publisher, published_date
- Used for sentiment analysis and citation retrieval

**company_analysis**:
- Stores completed analysis reports
- Metadata: symbols, query_type, agents_executed
- Used for finding similar historical patterns

**market_trends**:
- Stores trend analysis results
- Metadata: symbols, trend_type, period
- Used for trend pattern matching

### 4.3 Embedding Pipeline Design

**File**: `src/vector_db/embeddings.py`

**EmbeddingPipeline**:
- Uses LiteLLM for embedding generation
- Default: OpenAI text-embedding-ada-002 (1536 dimensions)
- Supports batch embedding generation

**Methods**:
- `generate_embedding(text)`: Generate single embedding
- `generate_embeddings_batch(texts)`: Generate multiple embeddings

### 4.4 Query Design Patterns

**Semantic Search**:
1. Generate embedding for query text
2. Search vector DB for similar embeddings
3. Return top N results with metadata

**Context-Aware Search**:
- Query includes current context information
- Filters by symbol, date, or other metadata
- Merges historical context with current context

### 4.5 Indexing Strategy

**Current**: Chroma's default indexing (automatic)

**Future Enhancements**:
- Custom indexing for faster symbol-based queries
- Time-based indexing for temporal queries
- Multi-vector indexing for complex queries

## 5. LLM Integration Design

### 5.1 LiteLLM Configuration Design

**File**: `src/utils/llm_config.py`

**LLMConfig Class**:
- Loads configuration from YAML
- Resolves environment variables
- Creates LiteLLM client configurations

**Supported Providers**:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Google Gemini (gemini-pro, gemini-1.5-pro)
- Anthropic Claude
- Ollama (local models)

### 5.2 Provider Abstraction Design

**Base Agent Integration**:
- All agents use `call_llm()` method
- Provider selected via configuration
- No agent code changes needed for provider switch

**Configuration File** (`config/llm_templates.yaml`):
- YAML-based provider templates
- Environment variable substitution
- Default provider selection

### 5.3 Token Tracking Design

**File**: `src/utils/token_tracker.py`

**TokenTracker**:
- Tracks tokens per agent
- Tracks tokens per call
- Maintains call history
- Provides statistics

**Integration**:
- LiteLLM returns usage information
- Base Agent tracks tokens automatically
- State updated with token usage

### 5.4 Response Handling Design

**LLM Response Structure**:
```python
{
    "content": str,  # Generated text
    "usage": Usage,  # Token usage info
    "model": str,    # Model used
    "execution_time": float  # Time taken
}
```

**Error Handling**:
- LLM errors caught and logged
- Context preserved on errors
- Graceful degradation

## 6. UI Design

### 6.1 Gradio Component Structure

**File**: `src/ui/gradio_app.py`

**MyFinGPTUI Class**:
- Creates Gradio interface
- Handles query processing
- Updates UI components

**Components**:
- Query input textbox
- Example queries dropdown
- Submit/Clear buttons
- Three tabs for results

### 6.2 State Management in UI

**Query Processing Flow**:
1. User enters query
2. UI calls `workflow.process_query()`
3. Workflow executes agents
4. Results returned to UI
5. UI updates all tabs

**Real-time Updates**:
- Progress bar during execution
- Streaming updates (future enhancement)
- Error messages displayed

### 6.3 Visualization Component Design

**File**: `src/ui/components.py`

**Chart Types**:
- Price trend charts (Plotly line charts)
- Comparison charts (Plotly bar charts)
- Sentiment charts (Plotly bar charts with colors)

**Data Preparation**:
- Visualizations prepared in Reporting Agent
- Data formatted for Plotly
- Charts created in UI components

### 6.4 Real-time Update Mechanism

**Current**: Streaming progress updates with real-time display

**Progress Tracking Features**:
- Real-time agent execution status
- Task-level progress updates
- Execution timeline visualization
- Progress events log
- Current agent and active tasks display

**Streaming Implementation**:
- Workflow streams state updates including progress events
- UI updates progress display in real-time
- Progress events stored in AgentState for persistence
- Execution order tracked with timing information

### 6.5 Progress Tracking Design

**File**: `src/utils/progress_tracker.py`

**ProgressTracker Class**:
- Centralized progress event management
- Creates and formats progress events
- Tracks agent-level and task-level events
- Supports execution order tracking

**Progress Event Schema**:
```python
{
    "timestamp": str,  # ISO timestamp
    "agent": str,  # Agent name
    "event_type": str,  # "agent_start", "agent_complete", "task_start", "task_complete", "task_progress"
    "message": str,  # Human-readable message
    "task_name": Optional[str],  # Task name (for task-level events)
    "symbol": Optional[str],  # Symbol being processed (if applicable)
    "status": str,  # "running", "completed", "failed"
    "execution_order": int,  # Order in execution sequence
    "is_parallel": bool,  # Whether this is parallel execution
    "transaction_id": Optional[str]  # Transaction ID
}
```

**Progress Display Components**:
- **File**: `src/ui/progress_display.py`
- `create_progress_panel()`: Main progress display panel
- `format_progress_event(event)`: Format individual progress events
- `create_execution_timeline(execution_order)`: Visual timeline of execution
- `create_agent_status_display(current_agent, current_tasks)`: Current agent status
- `update_progress_display(...)`: Update all progress display components

**UI Integration**:
- Progress panel displayed above tabs
- Real-time updates via streaming
- Execution timeline chart
- Progress events log

## 7. Data Models

### 7.1 State Model Schema

See Section 2.1 for complete `AgentState` structure.

### 7.2 Agent Output Models

**Research Agent Output**:
```python
{
    symbol: {
        "price": {...},
        "company": {...},
        "news": {...},
        "historical": {...},
        "financials": {...}
    }
}
```

**Analyst Agent Output**:
```python
{
    symbol: {
        "financial": {...},
        "sentiment": {...},
        "trend": {...},
        "recommendation": {...}
    }
}
```

**Reporting Agent Output**:
```python
{
    "final_report": str,
    "visualizations": {...}
}
```

### 7.3 Citation Model

```python
{
    "source": str,        # Source name
    "url": str,          # Source URL
    "date": str,         # ISO date
    "agent": str,        # Agent that collected
    "data_point": str,   # What data point
    "symbol": str        # Stock symbol
}
```

### 7.4 Token Usage Model

```python
{
    agent_name: total_tokens
}
```

**Per-Call Tracking**:
```python
{
    "timestamp": str,
    "agent": str,
    "tokens": int,
    "call_type": str,
    "model": str
}
```

### 7.5 Progress Event Model

**Progress Event Structure**:
```python
{
    "timestamp": str,  # ISO timestamp
    "agent": str,  # Agent name
    "event_type": str,  # Event type (agent_start, agent_complete, task_start, task_complete, task_progress)
    "message": str,  # Human-readable message
    "task_name": Optional[str],  # Task name
    "symbol": Optional[str],  # Symbol being processed
    "status": str,  # running, completed, failed
    "execution_order": int,  # Order in execution sequence
    "is_parallel": bool,  # Whether parallel execution
    "transaction_id": Optional[str]  # Transaction ID
}
```

**Execution Order Entry**:
```python
{
    "agent": str,  # Agent name
    "start_time": float,  # Start timestamp
    "end_time": Optional[float],  # End timestamp (None if still running)
    "duration": Optional[float]  # Duration in seconds
}
```

## 8. Guardrails Design

### 8.1 Guardrails Module Design

**File**: `src/utils/guardrails.py`

**Purpose**: Comprehensive validation and security guardrails

**Key Classes**:
- `Guardrails`: Main guardrails class with validation methods
- `GuardrailsError`: Custom exception for guardrails violations

**Design Principles**:
- Centralized validation logic
- Fail-safe defaults
- Clear error messages
- Minimal performance overhead
- Extensible for new validation rules

### 8.2 Query Validation Design

**Method**: `validate_query(query: str) -> Tuple[bool, Optional[str]]`

**Validation Steps**:
1. Check query is non-empty string
2. Check query length (max 2000 characters)
3. Check for dangerous patterns (injection attacks)
4. Sanitize input
5. Check for non-financial domain keywords
6. Check for financial domain keywords or stock symbols
7. Return validation result

**Rejection Criteria**:
- Non-financial domain queries
- Queries with dangerous patterns
- Queries exceeding length limit
- Queries without financial keywords or symbols

### 8.3 Input Sanitization Design

**Method**: `sanitize_input(input_str: str) -> str`

**Sanitization Steps**:
1. Check for dangerous patterns (XSS, SQL injection, code execution)
2. Remove null bytes
3. Remove control characters (except newlines and tabs)
4. Return sanitized string

**Dangerous Patterns Detected**:
- Script tags (`<script>`)
- JavaScript URLs (`javascript:`)
- Event handlers (`onclick=`, `onerror=`, etc.)
- HTML iframes, objects, embeds
- SQL injection patterns (`union select`, `drop table`)
- Code execution patterns (`eval()`, `exec()`, `system()`)
- File operations (`file_get_contents`, `fopen`)
- Network calls (`curl_exec`, `fsockopen`)
- Hex/URL encoding patterns

### 8.4 Symbol Validation Design

**Method**: `validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]`

**Validation Steps**:
1. Check symbol is non-empty string
2. Normalize to uppercase
3. Check length (1-7 characters)
4. Check format (1-5 letters + optional exchange suffix)
5. Check against invalid symbols list
6. Return validation result

**Valid Format**: `[A-Z]{1,5}(?:\.[A-Z]{1,2})?`
- Examples: `AAPL`, `TSLA`, `MSFT.NYSE`, `GOOGL`

**Invalid Symbols**: Common words that match pattern (THE, AND, OR, etc.)

### 8.5 Data Source Validation Design

**Method**: `validate_data_source(source: str) -> Tuple[bool, Optional[str]]`

**Allowed Sources**:
- `yahoo_finance`
- `alpha_vantage`
- `financial_modeling_prep` (or `fmp`)

**Validation**:
- Check source name matches allowed list
- Normalize source name (lowercase, replace spaces with underscores)
- Reject unauthorized sources

### 8.6 Agent Output Validation Design

**Method**: `validate_agent_output(output: str, agent_name: str) -> Tuple[bool, Optional[str]]`

**Validation Steps**:
1. Check output is non-empty string
2. Check output length (max 50KB)
3. Sanitize output (check for dangerous patterns)
4. For reporting agent: Check for financial content
5. Check for non-financial domain content
6. Return validation result

**Reporting Agent Specific**:
- Must contain financial keywords
- Must not contain non-financial domain keywords
- Warns if output doesn't appear financial-related

### 8.7 State Validation Design

**Method**: `validate_state(state: Dict[str, Any]) -> Tuple[bool, Optional[str]]`

**Validation Steps**:
1. Check state is dictionary
2. Check required fields exist (`query`, `query_type`, `symbols`)
3. Validate query
4. Validate symbols (if present)
5. Validate final_report (if present)
6. Return validation result

### 8.8 Guardrails Integration Design

**Workflow Integration**:
- Query validation before processing
- Input sanitization
- Symbol extraction and validation
- State validation before/after execution
- Output validation before returning results

**Base Agent Integration**:
- State validation before execution
- State validation after execution
- GuardrailsError handling

**MCP Client Integration**:
- Symbol validation before API calls
- Data source validation
- GuardrailsError handling

**UI Integration**:
- GuardrailsError handling
- User-friendly error messages
- Query validation feedback

### 8.9 Guardrails Error Handling

**Strategy**: Fail-fast with clear errors

**Implementation**:
- GuardrailsError raised on violations
- Errors logged with context
- User-friendly error messages in UI
- System stops execution on critical violations
- Warnings logged for non-critical issues

**Error Types**:
- Query validation failures (stop execution)
- Symbol validation failures (warn, use valid symbols only)
- Output validation failures (warn, log)
- State validation failures (warn, log)

## 9. Error Handling Design

### 9.1 API Rate Limit Handling

**Strategy**: Exponential backoff

**Implementation**:
- Detect 429 status codes
- Wait with exponential backoff (2^attempt seconds)
- Retry up to max_retries times
- Fallback to other sources if available

### 9.2 Failed API Calls

**Strategy**: Graceful degradation

**Implementation**:
- Try primary source
- Fallback to secondary sources
- Continue with partial data if needed
- Log errors but don't fail workflow

### 9.3 Agent Error Handling

**Strategy**: Context preservation

**Implementation**:
- Errors caught in `run()` method
- Context preserved on error
- Error logged in state metadata
- Workflow continues with available data
- GuardrailsError handled separately

### 9.4 LLM Error Handling

**Strategy**: Retry with fallback

**Implementation**:
- Retry failed LLM calls
- Fallback to simpler prompts if needed
- Return error message if all retries fail
- Preserve context on LLM errors

### 9.5 Guardrails Error Handling

**Strategy**: Fail-fast with clear messages

**Implementation**:
- GuardrailsError raised on violations
- Errors logged with full context
- User-friendly error messages
- Execution stops on critical violations
- Warnings for non-critical issues

## 10. Performance Optimization

### 9.1 Context Optimization

- Context pruning removes old/unnecessary data
- Context compression for large datasets
- Context size monitoring and alerts

### 9.2 Token Usage Optimization

- Track tokens per agent
- Optimize prompts to reduce tokens
- Cache LLM responses for similar queries

### 9.3 Vector DB Optimization

- Batch embedding generation
- Efficient query patterns
- Index optimization

### 9.4 API Call Optimization

- Rate limit awareness
- Parallel API calls where possible
- Caching for repeated queries


# MyFinGPT - Requirements and Architecture Document

## 1. Project Overview

MyFinGPT is a proof-of-concept multi-agent financial analysis system designed to demonstrate AI agent implementation patterns including:

- Multi-agent orchestration (parallel and sequential execution)
- MCP server integration
- Context sharing between agents
- Vector database for semantic search
- Grounded responses with citations
- Token usage tracking
- Real-time progress tracking and visualization

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Gradio UI Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Query Panel  │  │ Results View │  │ Trend Graphs │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Orchestrator                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Agent State Manager (Shared Context)          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Research     │  │ Analyst      │  │ Reporting    │
│ Agent        │  │ Agent        │  │ Agent        │
└──────────────┘  └──────────────┘  └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
        ┌───────────────────────────────────┐
        │   MCP Servers & External APIs     │
        │  - Yahoo Finance MCP               │
        │  - Alpha Vantage MCP               │
        │  - Financial Modeling Prep MCP     │
        └───────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │      Vector Database (Chroma)      │
        │   (Stores embeddings & references)  │
        └───────────────────────────────────┘
```

### 2.2 Agent Types and Responsibilities

#### Research Agent

- **Purpose**: Gather raw financial data and news
- **Capabilities**:
  - Fetch stock prices, company data, financial statements
  - Retrieve news articles and press releases
  - Collect market data from multiple sources
- **Output**: Structured data with source citations
- **Execution**: Can run in parallel for multiple stocks/symbols

#### Analyst Agent

- **Purpose**: Analyze data and perform deductions
- **Capabilities**:
  - Financial ratio analysis
  - Trend identification
  - Sentiment analysis of news/articles
  - Comparative analysis between companies
  - Pattern recognition in financial data
- **Input**: Data from Research Agent
- **Output**: Analysis results with reasoning chains
- **Execution**: Sequential (depends on Research Agent output)

#### Reporting Agent

- **Purpose**: Generate comprehensive reports and recommendations
- **Capabilities**:
  - Synthesize findings from all agents
  - Generate actionable recommendations
  - Create formatted reports with citations
  - Build visualizations (trends, comparisons)
- **Input**: Analysis from Analyst Agent + Research data
- **Output**: Final report with references and visualizations
- **Execution**: Sequential (final step)

### 2.3 Additional Specialized Agents (Optional)

- **Sentiment Agent**: Dedicated sentiment analysis of news/social media
- **Trend Agent**: Identify and analyze market trends
- **Comparison Agent**: Compare multiple stocks/companies side-by-side

## 3. Data Flow and Execution Patterns

### 3.1 Sequential Flow Example

```
User Query: "Analyze AAPL stock"
  ↓
Research Agent → Fetch AAPL data, news, financials
  ↓
Analyst Agent → Analyze ratios, trends, sentiment
  ↓
Reporting Agent → Generate comprehensive report
```

### 3.2 Parallel Flow Example

```
User Query: "Compare AAPL, MSFT, GOOGL"
  ↓
Research Agent (Parallel)
  ├─→ Fetch AAPL data
  ├─→ Fetch MSFT data
  └─→ Fetch GOOGL data
  ↓
Analyst Agent (Parallel)
  ├─→ Analyze AAPL
  ├─→ Analyze MSFT
  └─→ Analyze GOOGL
  ↓
Comparison Agent → Compare all three
  ↓
Reporting Agent → Generate comparison report
```

### 3.3 Context Sharing Mechanism

**Design Philosophy**: Context-first approach ensures agents can effectively share information, build upon each other's work, and maintain a clear information flow throughout the execution pipeline.

#### 3.3.1 Shared State Architecture

- **Shared State**: LangGraph StateGraph maintains agent state as the central context repository
- **State Structure**:
  ```python
  {
    "transaction_id": str,  # Unique transaction identifier (8-character hex)
    "query": str,  # Original user query
    "query_type": str,  # "single_stock", "comparison", "trend", etc.
    "symbols": List[str],  # Stock symbols extracted from query
    
    # Research Agent Output
    "research_data": Dict[str, Any],  # Symbol -> {price, financials, news, etc.}
    "research_metadata": Dict[str, Any],  # Timestamps, sources, data quality
    
    # Analyst Agent Output
    "analysis_results": Dict[str, Any],  # Symbol -> {ratios, sentiment, trends}
    "analysis_reasoning": Dict[str, str],  # Symbol -> reasoning chain
    
    # Specialized Agent Outputs
    "sentiment_analysis": Dict[str, Any],  # Symbol -> sentiment scores
    "trend_analysis": Dict[str, Any],  # Trend patterns identified
    "comparison_data": Dict[str, Any],  # Comparison results
    
    # Citations and Sources
    "citations": List[Dict],  # [{source, url, date, agent, data_point}]
    "vector_db_references": List[str],  # IDs of retrieved vector DB documents
    
    # Token and Performance Tracking
    "token_usage": Dict[str, int],  # {agent_name: tokens_used}
    "execution_time": Dict[str, float],  # {agent_name: seconds}
    
    # Final Output
    "final_report": str,
    "visualizations": Dict[str, Any],  # Chart data
    
    # Context Metadata
    "context_version": int,  # Version tracking for context evolution
    "context_size": int,  # Size in bytes for optimization
    "agents_executed": List[str],  # Execution order
    
    # Progress Tracking
    "progress_events": List[Dict[str, Any]],  # Real-time progress events
    "current_agent": Optional[str],  # Currently executing agent
    "current_tasks": Dict[str, List[str]],  # Current tasks per agent
    "execution_order": List[Dict[str, Any]],  # Execution order with timing
  }
  ```

#### 3.3.2 Context Flow Patterns

**Sequential Context Flow**:
```
User Query → Research Agent (writes research_data)
           → Analyst Agent (reads research_data, writes analysis_results)
           → Reporting Agent (reads research_data + analysis_results, writes final_report)
```

**Parallel Context Flow**:
```
User Query → Research Agent (Parallel)
           ├─→ Symbol 1 (writes research_data["SYMBOL1"])
           ├─→ Symbol 2 (writes research_data["SYMBOL2"])
           └─→ Symbol 3 (writes research_data["SYMBOL3"])
           → Context Merge (aggregates parallel results)
           → Analyst Agent (Parallel, reads respective research_data)
           → Comparison Agent (reads all analysis_results)
           → Reporting Agent (reads all context)
```

#### 3.3.3 Context Access Patterns

**Reading Context**:
- Agents read only what they need from shared state
- Context validation ensures required data exists before agent execution
- Agents can query vector DB to enrich context with historical patterns

**Writing Context**:
- Agents write structured outputs to specific state fields
- All writes include citations and metadata
- Context versioning tracks changes
- Progress events written to shared state for real-time visibility

**Context Validation**:
- Pre-execution: Check if required context exists
- Post-execution: Validate context completeness
- Error handling: Preserve context on failures

#### 3.3.4 Context Optimization

- **Context Pruning**: Remove unnecessary data to reduce token usage
- **Context Compression**: Compress large datasets while preserving key information
- **Context Caching**: Cache frequently accessed context patterns
- **Context Size Management**: Monitor and limit context size for performance

#### 3.3.5 Vector DB as Context Enhancement

- Vector DB stores historical context patterns
- Agents query vector DB to find similar past contexts
- Retrieved contexts enhance current agent understanding
- Historical patterns inform current analysis

## 4. MCP Server Integration

### 4.1 MCP Servers to Integrate

1. **Yahoo Finance MCP**

   - Stock prices (real-time and historical)
   - Company information
   - Financial statements

2. **Alpha Vantage MCP**

   - Technical indicators
   - Market data
   - Economic indicators

3. **Financial Modeling Prep (FMP) MCP**

   - Financial statements
   - Company profiles
   - Market news

### 4.2 MCP Integration Pattern

- Each agent calls MCP servers via custom MCP client wrappers (not LangChain tools)
- Custom `UnifiedMCPClient` provides unified interface for Yahoo Finance, Alpha Vantage, and FMP
- Responses include source attribution
- Error handling for API rate limits (free tier constraints)

## 5. Vector Database Usage

### 5.1 Purpose

- Store embeddings of financial news, reports, and analysis
- Enable semantic search for similar companies/trends
- Provide context for grounded responses

### 5.2 Implementation

- **Database**: Chroma (local, simple, free)
- **Embeddings**: Use LiteLLM embedding models (OpenAI, Google Gemini, or other providers)
- **Collections**:
  - `financial_news`: News articles with metadata
  - `company_analysis`: Historical analysis reports
  - `market_trends`: Trend patterns and insights

### 5.3 Usage Flow

1. Research Agent stores fetched news/articles in vector DB
2. Analyst Agent queries vector DB for similar historical patterns
3. Reporting Agent retrieves relevant context for citations

## 6. UI Design (Gradio)

### 6.1 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│                    MyFinGPT                              │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Query Panel                                     │   │
│  │  ┌───────────────────────────────────────────┐  │   │
│  │  │ [Text Input: Enter your financial query]  │  │   │
│  │  └───────────────────────────────────────────┘  │   │
│  │  [Submit] [Clear] [Example Queries Dropdown]    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Progress Panel (Real-time)                      │   │
│  │  - Current Agent: Research Agent                 │   │
│  │  - Active Tasks: Fetching AAPL price...         │   │
│  │  - Progress Events Log                          │   │
│  │  - Execution Timeline Chart                     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Results Section                                 │   │
│  │  ┌───────────────────────────────────────────┐  │   │
│  │  │ Tab 1: Analysis & Report                   │  │   │
│  │  │ - Executive Summary                        │  │   │
│  │  │ - Detailed Analysis                        │  │   │
│  │  │ - Recommendations                         │  │   │
│  │  │ - Citations & Sources                     │  │   │
│  │  └───────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────┐  │   │
│  │  │ Tab 2: Trends & Visualizations            │  │   │
│  │  │ - Price Trend Graph                       │  │   │
│  │  │ - Volume Chart                            │  │   │
│  │  │ - Comparison Charts (if applicable)       │  │   │
│  │  └───────────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────────┐  │   │
│  │  │ Tab 3: Agent Activity & Token Usage       │  │   │
│  │  │ - Agent execution timeline                │  │   │
│  │  │ - Token usage per agent                   │  │   │
│  │  │ - Progress events                         │  │   │
│  │  │ - Execution order                         │  │   │
│  │  └───────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 6.2 UI Components

1. **Query Input Panel**

   - Text input for user queries
   - Example queries dropdown
   - Submit/Clear buttons
   - Loading indicator during processing

2. **Results Display**

   - **Tab 1: Analysis & Report**
     - Markdown-formatted report
     - Expandable sections
     - Clickable citations
   - **Tab 2: Trends & Visualizations**
     - Interactive charts (Plotly via Gradio)
     - Price trends over time
     - Volume analysis
     - Comparison charts for multi-stock queries
   - **Tab 3: Agent Activity & Token Usage**
     - Execution timeline visualization
     - Token usage breakdown
     - Progress events log
     - Execution order with timing
     - Agent state transitions

3. **Real-time Progress Tracking**

   - **Progress Panel**: Displays current agent status, active tasks, progress events log, and execution timeline
   - **Streaming Updates**: Real-time progress updates via Gradio generator/streaming API
   - **Agent-Level Progress**: Shows which agent is currently executing
   - **Task-Level Progress**: Shows individual tasks being performed within each agent
   - **Execution Order**: Visual timeline showing agent execution sequence and duration
   - **Progress Events**: Chronological log of all progress events with timestamps
   - **Live Updates**: UI updates automatically as agents execute, not just at completion

## 7. Technical Stack

### 7.1 Core Libraries

- **LangGraph**: Agent orchestration and state management
  - Used directly for graph-based workflow orchestration
  - Provides `StateGraph` for managing agent state and execution flow
  - Handles sequential and parallel agent execution patterns
- **LangChain**: Listed in requirements but not directly imported
  - Included as a transitive dependency of LangGraph
  - No direct LangChain code is used in this project
  - The codebase uses only LangGraph's API directly
- **LangSmith**: Monitoring and debugging (optional, free tier)
- **LiteLLM**: Multi-LLM provider abstraction
  - Support for: OpenAI, Anthropic, Google Gemini, Ollama, etc.
  - Template-based configuration with examples for OpenAI, Gemini, and Ollama

### 7.2 Data & Storage

- **Chroma**: Vector database
- **Pandas**: Data manipulation
- **NumPy**: Numerical operations

### 7.3 APIs & MCP

- **MCP SDK**: Model Context Protocol integration
- **Yahoo Finance**: `yfinance` library or MCP server
- **Alpha Vantage**: API client or MCP server
- **Financial Modeling Prep**: API client or MCP server

### 7.4 UI

- **Gradio**: Web UI framework
- **Plotly**: Interactive charts

### 7.5 Utilities

- **python-dotenv**: Environment variable management
- **pydantic**: Data validation
- **logging**: Application logging

### 7.6 LiteLLM Configuration

LiteLLM will be configured with templates for multiple LLM providers. The `config/llm_templates.yaml` file will include:

**OpenAI Template**:
```yaml
openai:
  model: "gpt-4"  # or "gpt-3.5-turbo"
  api_key: "${OPENAI_API_KEY}"
```

**Google Gemini Template**:
```yaml
gemini:
  model: "gemini-pro"  # or "gemini-1.5-pro"
  api_key: "${GEMINI_API_KEY}"
```

**Ollama Template**:
```yaml
ollama:
  model: "llama2"  # or other local models
  api_base: "http://localhost:11434"
```

The system will support switching between providers via configuration, allowing users to choose based on availability, cost, or performance requirements.

## 8. Key Features Implementation

### 8.1 Grounded Responses with Citations

- Every data point includes source reference
- Citations format: `[Source: Yahoo Finance, Date: 2024-01-15]`
- Vector DB queries return source documents
- Final report includes bibliography section

### 8.2 Token Usage Tracking

- LiteLLM provides token usage per call
- Track tokens per agent, per LLM call
- Display in UI (Tab 3: Agent Activity)
- Store in state for reporting

### 8.3 Error Handling

- API rate limit handling (exponential backoff)
- Fallback mechanisms for failed API calls
- User-friendly error messages
- Graceful degradation

### 8.4 Integration Configuration and Control System

#### 8.4.1 Overview

The Integration Configuration and Control System allows users to:
- Select LLM providers (including LM Studio for local models)
- Enable/disable specific data source integrations (FMP, Alpha Vantage, Yahoo Finance)
- Optimize API calls to avoid redundant requests
- Generate dynamic prompts that honor disabled integrations
- Handle API failures gracefully with partial data continuation
- Track and display API call status (success/skip/failed) in progress updates

#### 8.4.2 LLM Provider Selection

**Supported Providers**:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Google Gemini (gemini-pro, gemini-1.5-pro)
- Anthropic Claude (claude-3-opus, claude-3-sonnet, claude-3-haiku)
- Ollama (local models)
- **LM Studio** (local models via OpenAI-compatible API)

**Configuration Methods**:
1. **Environment Variable**: `export LITELLM_PROVIDER=lmstudio`
2. **Command Line**: `python main.py --llm-provider lmstudio`
3. **Config File**: Edit `config/llm_templates.yaml` default provider

**LM Studio Setup**:
1. Install LM Studio from https://lmstudio.ai/
2. Load a model in LM Studio
3. Start local server (default port 1234)
4. Configure environment variables:
   ```bash
   export LM_STUDIO_API_BASE=http://localhost:1234/v1
   export LM_STUDIO_MODEL=your-model-name
   export LITELLM_PROVIDER=lmstudio
   ```

#### 8.4.3 Integration Enable/Disable Control

**Configuration File** (`config/integrations.yaml`):
```yaml
integrations:
  yahoo_finance:
    enabled: true
    description: "Yahoo Finance data source"
  
  alpha_vantage:
    enabled: true
    description: "Alpha Vantage API"
    requires_api_key: true
  
  fmp:
    enabled: true
    description: "Financial Modeling Prep API"
    requires_api_key: true
```

**Environment Variable Overrides**:
```bash
export ENABLE_YAHOO_FINANCE=true
export ENABLE_ALPHA_VANTAGE=false
export ENABLE_FMP=true
```

**Command-Line Control**:
```bash
# Disable specific integrations
python main.py --disable-integrations fmp

# Enable only specific integrations
python main.py --enable-integrations yahoo_finance --disable-integrations fmp,alpha_vantage
```

**Behavior**:
- Disabled integrations are automatically skipped (no API calls made)
- System continues with available data sources
- Progress events show skipped integrations with ⊘ indicator
- Prompts dynamically generated to only mention enabled integrations

#### 8.4.4 API Call Optimization

**Smart Source Selection**:
- Each data type has preferred integration order:
  - Stock price: Yahoo Finance → Alpha Vantage → FMP
  - Company info: Yahoo Finance → FMP → Alpha Vantage
  - Financial statements: FMP → Yahoo Finance
  - News: Yahoo Finance → FMP
  - Historical data: Yahoo Finance only
  - Technical indicators: Alpha Vantage only

**Stop After First Success**:
- System stops trying other sources once data is successfully retrieved
- Reduces redundant API calls
- Faster execution times
- Lower API usage costs

**Parallel Execution Compatibility**:
- Optimization happens WITHIN each parallel task
- Each parallel thread optimizes independently
- No cross-thread interference
- Parallel execution structure preserved (5 parallel tasks for single symbol, N×5 for multiple symbols)

#### 8.4.5 Dynamic Prompt Generation

**Prompt Builder** (`src/utils/prompt_builder.py`):
- Generates prompts dynamically based on enabled integrations
- Removes references to disabled integrations
- Updates agent instructions to only mention available data sources
- Provides integration availability information to agents

**Agent Integration**:
- Reporting Agent: Prompts mention only enabled data sources
- Analyst Agent: Sentiment analysis prompts mention only available news sources
- Comparison Agent: Comparison prompts mention only available data sources

**Benefits**:
- Prompts don't confuse LLM with unavailable sources
- Clearer instructions based on actual capabilities
- Better error handling (LLM knows what's available)

#### 8.4.6 API Status Tracking

**Progress Event Types**:
- `api_call_start`: API call initiated
- `api_call_success`: API call succeeded (✓)
- `api_call_failed`: API call failed (✗)
- `api_call_skipped`: API call skipped - integration disabled (⊘)

**Progress Event Structure**:
```python
{
    "event_type": "api_call_success",
    "integration": "yahoo_finance",
    "symbol": "AAPL",
    "data_type": "stock_price",
    "status": "success",
    "message": "Yahoo Finance API call succeeded for AAPL",
    "error": None,
    "timestamp": "2024-01-15T12:34:56"
}
```

**UI Display**:
- Progress panel shows API call status with indicators
- ✓ Success indicator for successful calls
- ✗ Failed indicator for failed calls
- ⊘ Skipped indicator for disabled integrations
- API call summary showing success/failed/skipped counts

#### 8.4.7 Graceful API Failure Handling

**Error Handling Strategy**:
1. **Integration Disabled**: Skip API call, log as "skipped", continue
2. **API Rate Limit**: Retry with exponential backoff, if fails mark as "failed", continue
3. **API Error**: Log error, mark as "failed", try fallback integration
4. **All Integrations Failed**: Continue with available data, report partial results
5. **Partial Success**: Include available data in analysis, note missing data in report

**Error Messages**:
- Detailed error messages for different failure types
- Clear indication of which integration failed
- Guidance on how to resolve issues
- User-friendly error messages in UI

#### 8.4.8 Configuration Priority

Configuration is applied in this order (later overrides earlier):
1. Default config file values (`config/integrations.yaml`)
2. Environment variables (`ENABLE_YAHOO_FINANCE`, etc.)
3. Command-line arguments (`--enable-integrations`, `--disable-integrations`)

This allows flexible configuration for different environments and use cases.

## 9. Project Structure

```
myfingpt/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── research_agent.py
│   │   ├── analyst_agent.py
│   │   ├── reporting_agent.py
│   │   └── base_agent.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── yahoo_finance.py
│   │   ├── alpha_vantage.py
│   │   └── fmp.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   └── state.py
│   ├── vector_db/
│   │   ├── __init__.py
│   │   ├── chroma_client.py
│   │   └── embeddings.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── token_tracker.py
│   │   ├── citations.py
│   │   └── llm_config.py
│   └── ui/
│       ├── __init__.py
│       ├── gradio_app.py
│       └── components.py
├── config/
│   ├── llm_templates.yaml
│   └── agent_config.yaml
├── tests/
├── docs/
│   ├── requirements.md (this document)
│   ├── architecture.md
│   └── design.md
├── .env.example
├── requirements.txt
└── README.md
```

## 9.5 Context-First Implementation Strategy

### Why Context-First?

The implementation is organized with a **context-first approach** to ensure optimal context sharing and usage throughout the system. This approach:

1. **Establishes Context Infrastructure Early**: State management and context sharing mechanisms are built before agents, ensuring all agents are context-aware from the start.

2. **Enables Clear Context Flow**: Each phase builds upon previous context capabilities, creating a natural flow of information between agents.

3. **Prevents Context Gaps**: By designing context structure first, we ensure no agent is built without understanding how it will receive and share context.

4. **Optimizes Context Usage**: Context optimization is considered at every step, reducing redundancy and improving efficiency.

5. **Facilitates Testing**: Context flows can be tested incrementally as each component is built, rather than retrofitting context sharing later.

### Context-First Principles

1. **Context Infrastructure Before Agents**: Build state management and context utilities before implementing agents.

2. **Context-Aware Base Classes**: All agents inherit context capabilities from a base class, ensuring consistent context handling.

3. **Explicit Context Dependencies**: Each agent explicitly declares what context it needs and what context it produces.

4. **Context Validation**: Validate context at each step to ensure data quality and completeness.

5. **Context Visibility**: Make context flow visible in UI and logs for debugging and optimization.

### Implementation Order Rationale

- **Phase 1**: Context infrastructure (state, vector DB, utilities) - Foundation for everything else
- **Phase 2**: Context-aware base agent - Ensures all agents inherit context capabilities
- **Phase 3**: MCP integration with context tracking - External data immediately available in context
- **Phase 4**: Context-aware agents - Agents built with context awareness from the start
- **Phase 5**: Orchestration with context flow - Orchestration leverages established context patterns
- **Phase 6**: Vector DB context integration - Enhances context with historical patterns
- **Phase 7**: UI with context display - Makes context visible to users
- **Phase 8**: Context testing - Validates and optimizes context usage

## 10. Implementation Flow (Context-First Approach)

The implementation is organized to prioritize context sharing and usage, ensuring agents can effectively communicate and build upon each other's work.

### Phase 1: Foundation & Context Infrastructure

**Goal**: Establish core infrastructure with context sharing capabilities from the start

1. Set up project structure
2. Configure LiteLLM with templates (OpenAI, Google Gemini, Ollama)
3. **Set up LangGraph state management framework**
   - Define state schema with context fields
   - Create state manager class
   - Design context structure (research_data, analysis_results, citations, etc.)
4. **Set up Chroma vector database**
   - Initialize database
   - Create collections (financial_news, company_analysis, market_trends)
   - Set up embedding pipeline for context storage
5. **Create context utilities**
   - Context manager for state operations
   - Citation tracker
   - Token usage tracker
   - Context validation utilities

**Context Focus**: Establish the foundation for context sharing before building agents

### Phase 2: Context-Aware Base Agent

**Goal**: Create base agent class with built-in context awareness

1. **Create base agent class with context capabilities**
   - Context reading from shared state
   - Context writing to shared state
   - Citation tracking integration
   - Token usage tracking integration
   - Error handling with context preservation
2. **Implement context helpers**
   - Methods to read previous agent outputs
   - Methods to write agent outputs for next agents
   - Context validation before agent execution
   - Context merging for parallel agents
3. **Add context-aware logging**
   - Log context state transitions
   - Track context usage per agent
   - Monitor context size and efficiency

**Context Focus**: Every agent inherits context awareness from the start

### Phase 3: MCP Integration with Context Tracking

**Goal**: Integrate MCP servers with context-aware data collection

1. Integrate Yahoo Finance MCP
   - Add context tracking for API calls
   - Store responses in context with citations
2. Integrate Alpha Vantage MCP
   - Track data sources in context
   - Link responses to query context
3. Integrate FMP MCP
   - Maintain context chain for financial data
   - Store metadata in context
4. Create unified MCP client wrapper
   - Context-aware request/response handling
   - Automatic citation generation
   - Context-preserving error handling

**Context Focus**: All external data is immediately available in shared context

### Phase 4: Context-Aware Agent Development

**Goal**: Build agents that leverage and contribute to shared context

1. **Implement Research Agent**
   - Reads query context from state
   - Fetches data using MCP clients (from Phase 3)
   - Stores all data in shared context with citations
   - Stores news/articles in vector DB with context links
   - Writes structured research_data to context
   - Validates context before completion

2. **Implement Analyst Agent**
   - Reads research_data from context (from Research Agent)
   - Queries vector DB for similar historical context
   - Performs analysis using context from Research Agent
   - Stores analysis results in context
   - Maintains reasoning chain in context
   - Writes analysis_results to context

3. **Implement Reporting Agent**
   - Reads both research_data and analysis_results from context
   - Queries vector DB for citation context
   - Synthesizes all context into final report
   - Generates visualizations from context data
   - Writes final_report to context

4. **Add specialized agents (if needed)**
   - Sentiment Agent: Reads news context, writes sentiment context
   - Comparison Agent: Reads multiple analysis contexts, writes comparison context
   - Trend Agent: Reads historical context, writes trend context

**Context Focus**: Each agent reads from and writes to shared context, creating a clear context flow

### Phase 5: Orchestration with Context Flow

**Goal**: Orchestrate agents with optimal context sharing

1. **Set up LangGraph workflow**
   - Define nodes with context dependencies
   - Create edges based on context flow
   - Implement conditional routing based on context state

2. **Create sequential execution flow**
   - Research → Analyst → Reporting
   - Each step validates required context exists
   - Context flows naturally between agents
   - Test context passing between sequential agents

3. **Create parallel execution flow**
   - Multiple Research Agents running in parallel
   - Context merging after parallel execution
   - Multiple Analyst Agents with shared context
   - Context aggregation before Reporting Agent

4. **Implement context optimization**
   - Context pruning (remove unnecessary data)
   - Context compression for large datasets
   - Context caching for repeated queries
   - Context validation at each step

**Context Focus**: Orchestration ensures context flows efficiently between agents

### Phase 6: Vector Database Context Integration

**Goal**: Enhance context with semantic search and historical patterns

1. **Enhance embedding pipeline**
   - Embed context chunks (not just raw data)
   - Store context metadata with embeddings
   - Link embeddings to state context

2. **Implement context-aware semantic search**
   - Query vector DB using current context
   - Retrieve similar historical contexts
   - Merge historical context with current context
   - Use context for better search relevance

3. **Add context retrieval for citations**
   - Retrieve source documents from vector DB
   - Link citations to context entries
   - Validate citations against context

4. **Implement context learning**
   - Store successful agent outputs in vector DB
   - Learn from historical context patterns
   - Improve context relevance over time

**Context Focus**: Vector DB becomes a context repository, enhancing current context with historical patterns

### Phase 7: UI Development with Context Display

**Goal**: Build UI that shows context flow and usage

1. Create Gradio app structure
2. Implement query input panel
3. **Implement context-aware results display**
   - Show context state at each step
   - Display context flow between agents
   - Show what context each agent used
4. **Add context visualization**
   - Context dependency graph
   - Context size over time
   - Context usage per agent
5. **Implement results display (tabs)**
   - Tab 1: Analysis & Report (from context)
   - Tab 2: Trends & Visualizations (from context data)
   - Tab 3: Agent Activity & Context Flow
     - Context state transitions
     - Context size metrics
     - Context sharing visualization
     - Token usage per agent
6. Add visualization components (using context data)

**Context Focus**: UI makes context flow visible and understandable

### Phase 8: Context Testing & Optimization

**Goal**: Validate and optimize context usage

1. **Test context flows**
   - Sequential context passing
   - Parallel context merging
   - Context validation at each step
   - Context error handling

2. **Validate context quality**
   - Ensure all agents receive required context
   - Verify context completeness
   - Check context consistency
   - Validate citations in context

3. **Optimize context usage**
   - Measure context size impact on performance
   - Optimize context structure
   - Reduce redundant context
   - Improve context retrieval speed

4. **Test with various query types**
   - Single stock (simple context flow)
   - Multi-stock comparison (complex context merging)
   - Trend analysis (historical context integration)

5. **Context performance tuning**
   - Optimize token usage with context
   - Improve context sharing efficiency
   - Reduce context overhead

**Context Focus**: Ensure context is used effectively and efficiently

### Phase 8: Documentation

1. Create Architecture Document (`docs/architecture.md`)
   - System architecture diagrams
   - Component interactions
   - Data flow diagrams
   - Technology stack details
   - Deployment architecture

2. Create Design Document (`docs/design.md`)
   - Detailed design of each component
   - Agent design patterns
   - State management design
   - API/MCP integration design
   - Database schema and vector DB design
   - UI/UX design specifications

3. Create Comprehensive README (`README.md`)
   - Project overview and features
   - Prerequisites and system requirements
   - **Setup Instructions**
     - Environment setup
     - Dependency installation
     - Configuration setup
     - MCP server setup
     - Vector database initialization
   - **Component Start Instructions**
     - Starting vector database (Chroma)
     - Starting MCP servers (if applicable)
     - Starting LiteLLM proxy (if used)
     - Starting Gradio UI application
   - **Component Stop Instructions**
     - Graceful shutdown procedures
     - Stopping each component
   - **Component Restart Instructions**
     - Restart procedures for each component
     - Troubleshooting restart issues
   - Usage examples
   - Configuration guide
   - Troubleshooting guide
   - Development guide

### Phase 8 Details: Documentation Specifications

#### 8.1 Architecture Document (`docs/architecture.md`)

**Purpose**: High-level system architecture and technical overview

**Sections**:
1. **System Overview**
   - System purpose and goals
   - High-level architecture diagram
   - Key architectural decisions

2. **Component Architecture**
   - Agent layer architecture
   - Orchestration layer (LangGraph)
   - MCP integration layer
   - Vector database layer
   - UI layer (Gradio)

3. **Data Flow Architecture**
   - Request flow diagram
   - Agent communication patterns
   - State management flow
   - Data persistence flow

4. **Technology Stack**
   - Detailed technology choices
   - Version specifications
   - Integration points

5. **Deployment Architecture**
   - Component deployment model
   - Dependencies between components
   - Scalability considerations

6. **Diagrams**
   - System architecture diagram (Mermaid or similar)
   - Sequence diagrams for key flows
   - Component interaction diagrams
   - Data flow diagrams

#### 8.2 Design Document (`docs/design.md`)

**Purpose**: Detailed design specifications for implementation

**Sections**:
1. **Agent Design**
   - Base agent class design
   - Research Agent design
   - Analyst Agent design
   - Reporting Agent design
   - Agent communication patterns
   - Error handling design

2. **Orchestration Design**
   - LangGraph state design
   - Sequential execution design
   - Parallel execution design
   - Context sharing mechanism
   - State transitions

3. **MCP Integration Design**
   - MCP client wrapper design
   - Yahoo Finance integration design
   - Alpha Vantage integration design
   - FMP integration design
   - Error handling and retry logic

4. **Vector Database Design**
   - Chroma schema design
   - Collection structure
   - Embedding pipeline design
   - Query design patterns
   - Indexing strategy

5. **LLM Integration Design**
   - LiteLLM configuration design
   - Provider abstraction design
   - Token tracking design
   - Response handling design

6. **UI Design**
   - Gradio component structure
   - State management in UI
   - Visualization component design
   - Real-time update mechanism

7. **Data Models**
   - State model schema
   - Agent output models
   - Citation model
   - Token usage model

#### 8.3 README Document (`README.md`)

**Purpose**: User-facing documentation for setup, operation, and usage

**Sections**:
1. **Project Overview**
   - What is MyFinGPT
   - Key features
   - Use cases

2. **Prerequisites**
   - Python version requirements
   - System requirements
   - Required API keys
   - Optional dependencies

3. **Installation & Setup**
   ```markdown
   ### Step 1: Clone Repository
   ### Step 2: Create Virtual Environment
   ### Step 3: Install Dependencies
   ### Step 4: Configure Environment Variables
   ### Step 5: Initialize Vector Database
   ### Step 6: Verify MCP Server Connections
   ```

4. **Configuration**
   - Environment variables (.env setup)
   - LLM provider configuration
   - MCP server configuration
   - Vector database configuration

5. **Starting Components**
   ```markdown
   ### Starting Vector Database (Chroma)
   ### Starting MCP Servers (if running locally)
   ### Starting LiteLLM Proxy (optional)
   ### Starting Gradio UI Application
   ### Starting All Components Together
   ```

6. **Stopping Components**
   ```markdown
   ### Stopping Gradio UI Application
   ### Stopping LiteLLM Proxy
   ### Stopping MCP Servers
   ### Stopping Vector Database
   ### Graceful Shutdown Procedures
   ```

7. **Restarting Components**
   ```markdown
   ### Restarting Individual Components
   ### Restarting All Components
   ### Troubleshooting Restart Issues
   ### Verifying Component Health
   ```

8. **Usage Guide**
   - Running the application
   - Example queries
   - Understanding results
   - UI navigation

9. **Development**
   - Development setup
   - Running tests
   - Code structure
   - Contributing guidelines

10. **Troubleshooting**
    - Common issues
    - Error messages
    - Debugging tips
    - Getting help

11. **API Reference** (if applicable)
    - MCP server endpoints
    - Internal APIs

## 11. Example Use Cases

### Use Case 1: Single Stock Analysis

**Query**: "Analyze Apple Inc. (AAPL) stock"

- Research Agent: Fetch AAPL data, recent news
- Analyst Agent: Analyze financials, sentiment, trends
- Reporting Agent: Generate comprehensive report

### Use Case 2: Stock Comparison

**Query**: "Compare AAPL, MSFT, and GOOGL"

- Research Agent: Parallel fetch for all three
- Analyst Agent: Parallel analysis
- Comparison Agent: Side-by-side comparison
- Reporting Agent: Comparison report with charts

### Use Case 3: Market Trend Analysis

**Query**: "What are the current trends in tech stocks?"

- Research Agent: Fetch multiple tech stocks
- Trend Agent: Identify patterns
- Analyst Agent: Analyze trends
- Reporting Agent: Trend report with visualizations

## 11.5 User Prompt Scenarios for POC Testing

The following scenarios are designed to exercise different aspects of the MyFinGPT system. Each scenario targets specific features and execution patterns.

### Scenario Category 1: Sequential Execution & Basic Analysis

#### Scenario 1.1: Single Stock Deep Dive
**Prompt**: "Provide a comprehensive analysis of Tesla (TSLA) stock including current price, financial health, recent news sentiment, and investment recommendation."

**Aspects Tested**:
- ✅ Sequential agent execution (Research → Analyst → Reporting)
- ✅ Single MCP server integration (Yahoo Finance)
- ✅ Financial ratio analysis
- ✅ News sentiment analysis
- ✅ Citation generation for all data points
- ✅ Token tracking across all agents
- ✅ Basic visualization (price trend)

**Expected Flow**:
1. Research Agent fetches TSLA data from Yahoo Finance MCP
2. Research Agent stores news/articles in vector DB
3. Analyst Agent analyzes financials and sentiment
4. Analyst Agent queries vector DB for similar historical patterns
5. Reporting Agent generates comprehensive report with citations

#### Scenario 1.2: Company Financial Health Check
**Prompt**: "Analyze the financial health of Microsoft (MSFT) by examining its balance sheet, income statement, and cash flow. Provide insights on profitability, liquidity, and solvency ratios."

**Aspects Tested**:
- ✅ Sequential execution with detailed analysis
- ✅ Multiple MCP server calls (FMP for financial statements)
- ✅ Deductive reasoning by Analyst Agent
- ✅ Financial ratio calculations
- ✅ Structured data extraction and analysis
- ✅ Citations for financial data sources

**Expected Flow**:
1. Research Agent fetches financial statements from FMP MCP
2. Research Agent fetches additional context from Yahoo Finance
3. Analyst Agent performs ratio analysis and deductions
4. Reporting Agent formats findings with proper citations

### Scenario Category 2: Parallel Execution & Comparison

#### Scenario 2.1: Multi-Stock Comparison
**Prompt**: "Compare Apple (AAPL), Microsoft (MSFT), and Google (GOOGL) across key metrics including P/E ratio, revenue growth, market cap, and recent performance. Which one would you recommend for a long-term investment?"

**Aspects Tested**:
- ✅ Parallel execution of Research Agent (3 stocks simultaneously)
- ✅ Parallel execution of Analyst Agent (3 analyses simultaneously)
- ✅ Comparison Agent functionality
- ✅ Multi-stock visualization (comparison charts)
- ✅ Context sharing between parallel agents
- ✅ Token usage comparison across parallel vs sequential
- ✅ Multiple MCP server calls in parallel

**Expected Flow**:
1. Research Agent runs 3 parallel tasks:
   - Fetch AAPL data
   - Fetch MSFT data
   - Fetch GOOGL data
2. Analyst Agent runs 3 parallel analyses
3. Comparison Agent synthesizes comparison
4. Reporting Agent generates comparison report with side-by-side charts

#### Scenario 2.2: Sector Analysis
**Prompt**: "Analyze the top 5 technology stocks by market cap and compare their performance, growth prospects, and risk profiles."

**Aspects Tested**:
- ✅ Parallel execution with 5+ stocks
- ✅ Sector-based analysis
- ✅ Ranking and comparison logic
- ✅ Multiple data sources in parallel
- ✅ Vector DB semantic search for sector trends
- ✅ Comprehensive visualization (multiple charts)

**Expected Flow**:
1. Research Agent identifies top 5 tech stocks (may require multiple API calls)
2. Research Agent fetches data for all 5 in parallel
3. Analyst Agent analyzes all 5 in parallel
4. Comparison Agent ranks and compares
5. Reporting Agent creates sector analysis report

### Scenario Category 3: Sentiment & News Analysis

#### Scenario 3.1: News Sentiment Impact
**Prompt**: "Analyze how recent news and market sentiment have affected NVIDIA (NVDA) stock price. Include sentiment analysis of the last 10 news articles and correlate with price movements."

**Aspects Tested**:
- ✅ Sentiment Agent functionality
- ✅ News aggregation from multiple sources
- ✅ Sentiment analysis with LLM
- ✅ Correlation analysis between sentiment and price
- ✅ Vector DB storage and retrieval of news articles
- ✅ Time-series analysis
- ✅ Citation of news sources

**Expected Flow**:
1. Research Agent fetches NVDA news from multiple MCP servers
2. Research Agent stores news in vector DB with embeddings
3. Sentiment Agent analyzes sentiment of each article
4. Analyst Agent correlates sentiment with price movements
5. Reporting Agent creates sentiment-impact report

#### Scenario 3.2: Market News Aggregation
**Prompt**: "What are the top 5 financial news stories affecting the tech sector today? Analyze the sentiment and potential market impact of each."

**Aspects Tested**:
- ✅ News aggregation from multiple MCP servers
- ✅ Sentiment analysis across multiple articles
- ✅ Vector DB semantic search for similar news
- ✅ Ranking and prioritization logic
- ✅ Multi-source citation handling

**Expected Flow**:
1. Research Agent fetches tech sector news from Yahoo Finance, FMP
2. Sentiment Agent analyzes sentiment for each story
3. Analyst Agent ranks by potential impact
4. Vector DB search for historical similar news patterns
5. Reporting Agent creates news digest with sentiment scores

### Scenario Category 4: Trend Analysis & Pattern Recognition

#### Scenario 4.1: Historical Trend Analysis
**Prompt**: "Analyze the 6-month price trend of Amazon (AMZN) and identify any patterns, support/resistance levels, and predict potential future movements based on historical data."

**Aspects Tested**:
- ✅ Trend Agent functionality
- ✅ Historical data retrieval (Alpha Vantage MCP)
- ✅ Technical indicator analysis
- ✅ Pattern recognition using LLM reasoning
- ✅ Vector DB query for similar historical patterns
- ✅ Advanced visualizations (support/resistance lines)

**Expected Flow**:
1. Research Agent fetches 6-month historical data from Alpha Vantage
2. Research Agent fetches technical indicators
3. Trend Agent identifies patterns and levels
4. Vector DB search for similar historical patterns
5. Analyst Agent makes predictions based on patterns
6. Reporting Agent creates trend analysis with annotated charts

#### Scenario 4.2: Market Trend Discovery
**Prompt**: "Identify emerging trends in the renewable energy sector by analyzing stock performance, news sentiment, and financial metrics of companies like TSLA, ENPH, and SEDG."

**Aspects Tested**:
- ✅ Trend identification across multiple stocks
- ✅ Sector-wide pattern recognition
- ✅ Multi-dimensional analysis (price, sentiment, fundamentals)
- ✅ Vector DB semantic search for trend patterns
- ✅ Cross-company trend correlation

**Expected Flow**:
1. Research Agent fetches data for multiple renewable energy stocks in parallel
2. Trend Agent identifies common patterns across stocks
3. Vector DB search for historical sector trends
4. Analyst Agent synthesizes trend insights
5. Reporting Agent creates trend discovery report

### Scenario Category 5: Vector Database & Semantic Search

#### Scenario 5.1: Similar Company Discovery
**Prompt**: "Find companies similar to Apple (AAPL) in terms of business model, financial metrics, and market position. Explain why they are similar."

**Aspects Tested**:
- ✅ Vector DB semantic search functionality
- ✅ Embedding generation for company profiles
- ✅ Similarity matching using vector search
- ✅ Multi-criteria similarity (business model, financials, market)
- ✅ Citation of similarity reasoning

**Expected Flow**:
1. Research Agent fetches AAPL company profile
2. Vector DB stores AAPL embedding
3. Analyst Agent queries vector DB for similar companies
4. Research Agent fetches data for similar companies found
5. Analyst Agent validates and explains similarities
6. Reporting Agent creates similarity analysis report

#### Scenario 5.2: Historical Pattern Matching
**Prompt**: "Has Netflix (NFLX) shown similar price patterns to what we saw with Blockbuster's decline? Search historical data and provide analysis."

**Aspects Tested**:
- ✅ Vector DB historical pattern storage
- ✅ Semantic search for similar patterns
- ✅ Cross-company historical comparison
- ✅ Pattern matching and validation
- ✅ Historical citation and references

**Expected Flow**:
1. Research Agent fetches NFLX current patterns
2. Vector DB search for similar historical patterns (Blockbuster, etc.)
3. Analyst Agent compares patterns and validates similarity
4. Reporting Agent creates pattern comparison report

### Scenario Category 6: Error Handling & Edge Cases

#### Scenario 6.1: Invalid Stock Symbol
**Prompt**: "Analyze the stock INVALID123"

**Aspects Tested**:
- ✅ Error handling for invalid symbols
- ✅ Graceful degradation
- ✅ User-friendly error messages
- ✅ Agent error propagation
- ✅ Token tracking even on errors

**Expected Flow**:
1. Research Agent attempts to fetch INVALID123
2. MCP server returns error
3. Error handling mechanism activates
4. User receives clear error message
5. Token usage still tracked

#### Scenario 6.2: Rate Limit Handling
**Prompt**: "Compare 20 different stocks: AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA, JPM, V, JNJ, WMT, PG, MA, UNH, HD, DIS, BAC, ADBE, CRM, NFLX"

**Aspects Tested**:
- ✅ API rate limit handling
- ✅ Exponential backoff retry logic
- ✅ Parallel execution with rate limit awareness
- ✅ Partial results handling
- ✅ Progress indication during delays

**Expected Flow**:
1. Research Agent attempts parallel fetch for 20 stocks
2. Rate limits encountered
3. Backoff and retry mechanism activates
4. Progress updates shown to user
5. Partial results displayed as available
6. Final report includes all successfully fetched data

### Scenario Category 7: Complex Multi-Agent Reasoning

#### Scenario 7.1: Investment Recommendation with Reasoning Chain
**Prompt**: "I have $10,000 to invest. Should I invest in AAPL, MSFT, or GOOGL? Provide detailed reasoning considering risk tolerance, growth potential, dividend yield, and market conditions."

**Aspects Tested**:
- ✅ Multi-agent reasoning chain
- ✅ Deductive reasoning by Analyst Agent
- ✅ Recommendation generation with justification
- ✅ Risk assessment
- ✅ Multi-factor analysis
- ✅ Context sharing across agents
- ✅ Comprehensive citation of reasoning steps

**Expected Flow**:
1. Research Agent fetches data for all 3 stocks in parallel
2. Analyst Agent performs multi-factor analysis (risk, growth, dividends)
3. Analyst Agent queries vector DB for similar investment scenarios
4. Analyst Agent makes deductions and recommendations
5. Reporting Agent creates investment recommendation with full reasoning chain

#### Scenario 7.2: Market Event Impact Analysis
**Prompt**: "A major tech company just announced layoffs. Analyze how this might affect the broader tech sector, specifically focusing on AAPL, MSFT, and GOOGL. Consider historical precedents."

**Aspects Tested**:
- ✅ Event-driven analysis
- ✅ Sector-wide impact reasoning
- ✅ Historical precedent lookup (vector DB)
- ✅ Causal reasoning chain
- ✅ Multi-stock impact assessment
- ✅ Cross-agent context sharing for event analysis

**Expected Flow**:
1. Research Agent fetches current news about layoffs
2. Vector DB search for historical similar events
3. Research Agent fetches data for AAPL, MSFT, GOOGL
4. Analyst Agent analyzes historical precedents
5. Analyst Agent reasons about sector impact
6. Reporting Agent creates impact analysis report

### Scenario Category 8: Token Tracking & Performance

#### Scenario 8.1: Token Usage Comparison
**Prompt**: "Compare token usage between analyzing a single stock vs. analyzing 5 stocks in parallel. Analyze AAPL first, then analyze AAPL, MSFT, GOOGL, AMZN, TSLA together."

**Aspects Tested**:
- ✅ Token tracking accuracy
- ✅ Comparison of sequential vs parallel token usage
- ✅ Per-agent token breakdown
- ✅ Token usage display in UI
- ✅ Efficiency metrics

**Expected Flow**:
1. First query: Sequential analysis of AAPL (token tracking)
2. Second query: Parallel analysis of 5 stocks (token tracking)
3. UI displays token comparison
4. Reporting Agent includes token efficiency analysis

### Scenario Category 9: Citation & Grounding

#### Scenario 9.1: Citation Verification
**Prompt**: "Analyze Tesla (TSLA) and provide all sources. I want to verify every data point you mention."

**Aspects Tested**:
- ✅ Comprehensive citation system
- ✅ Source attribution for every claim
- ✅ Verifiable references
- ✅ Citation format consistency
- ✅ Source URL/identifier inclusion

**Expected Flow**:
1. Research Agent collects data with source tracking
2. All data points tagged with sources
3. Analyst Agent maintains source chain
4. Reporting Agent includes detailed bibliography
5. UI displays clickable citations

### Scenario Category 10: Visualization Requirements

#### Scenario 10.1: Multi-Chart Generation
**Prompt**: "Create a comprehensive visual analysis of Bitcoin-related stocks (MSTR, COIN, RIOT) including price trends, volume analysis, correlation charts, and comparison graphs."

**Aspects Tested**:
- ✅ Multiple chart types (price, volume, correlation, comparison)
- ✅ Interactive visualizations
- ✅ Multi-stock chart overlays
- ✅ Chart annotations and labels
- ✅ Visualization in Gradio UI

**Expected Flow**:
1. Research Agent fetches data for all stocks
2. Analyst Agent prepares data for visualization
3. Reporting Agent generates multiple chart types
4. UI displays all charts in Trends & Visualizations tab

### Summary: Scenario Coverage Matrix

| Feature | Scenarios Testing It |
|---------|---------------------|
| Sequential Execution | 1.1, 1.2, 6.1 |
| Parallel Execution | 2.1, 2.2, 6.2 |
| MCP Integration | All scenarios |
| Vector DB | 3.1, 4.1, 4.2, 5.1, 5.2, 7.1, 7.2 |
| Sentiment Analysis | 3.1, 3.2 |
| Trend Analysis | 4.1, 4.2 |
| Comparison Logic | 2.1, 2.2, 7.1 |
| Citations | All scenarios (especially 9.1) |
| Token Tracking | All scenarios (especially 8.1) |
| Error Handling | 6.1, 6.2 |
| Multi-Agent Reasoning | 7.1, 7.2 |
| Visualizations | 2.1, 4.1, 10.1 |

## 12. Transaction Tracking and Log Analysis

### 12.1 Transaction ID System

Every user query is assigned a unique transaction ID (8-character hexadecimal string) that:
- Identifies the query throughout its entire execution lifecycle
- Appears in all log entries related to that query
- Is displayed in the UI (report header and Agent Activity tab)
- Enables extraction and analysis of complete execution flows

### 12.2 Log Extraction and Analysis

The system includes a log extraction script (`scripts/extract_logs.py`) that:
- Lists all transactions for a given date
- Extracts complete execution flow for a specific transaction ID
- Groups logs by component (UI, Workflow, Agents, MCP, VectorDB)
- Displays chronological flow across all components
- Shows key events and execution timeline

**Usage**:
```bash
# List all transactions
python scripts/extract_logs.py --list

# View flow for specific transaction
python scripts/extract_logs.py --transaction-id abc12345

# Include file names for detailed debugging
python scripts/extract_logs.py --transaction-id abc12345 --show-files
```

### 12.3 Log Structure

Logs are organized by component and date:
- `myfingpt_YYYY-MM-DD.log` - Main log (all entries)
- `workflow_YYYY-MM-DD.log` - Workflow execution logs
- `agents_YYYY-MM-DD.log` - Agent execution logs
- `mcp_YYYY-MM-DD.log` - MCP client logs
- `vectordb_YYYY-MM-DD.log` - Vector database logs
- `ui_YYYY-MM-DD.log` - UI interaction logs
- `myfingpt_errors_YYYY-MM-DD.log` - Error logs only

All log entries include transaction ID when applicable, enabling easy filtering and extraction.

## 13. Success Criteria

- ✅ Multiple agents working together (sequential and parallel)
- ✅ MCP server integration functional
- ✅ Vector database storing and retrieving embeddings
- ✅ All responses include citations
- ✅ Token usage tracked and displayed
- ✅ UI shows analysis, visualizations, and agent activity
- ✅ System handles errors gracefully
- ✅ Free APIs working within rate limits
- ✅ Transaction IDs track queries throughout execution
- ✅ Log extraction enables debugging and flow analysis
- ✅ Real-time progress tracking shows agent execution status
- ✅ Task-level progress updates displayed in UI
- ✅ Execution timeline visualization shows agent order and timing

## 13. Real-Time Progress Tracking Enhancement

### 13.1 Overview

The Real-Time Progress Tracking Enhancement provides users with comprehensive visibility into the multi-agent execution process, showing which agents are working, what tasks they're performing, and the execution order in real-time.

### 13.2 Requirements

#### 13.2.1 Progress Visibility Requirements

**R1: Agent-Level Progress Display**
- System MUST display which agent is currently executing
- System MUST show when agents start and complete execution
- System MUST display execution time for each agent
- System MUST indicate execution order (sequential or parallel)

**R2: Task-Level Progress Display**
- System MUST show individual tasks being performed within each agent
- System MUST display task start and completion status
- System MUST show task progress for long-running operations
- System MUST associate tasks with specific symbols when applicable

**R3: Real-Time Updates**
- System MUST update progress display in real-time as agents execute
- System MUST use streaming mechanism for live updates
- System MUST NOT require page refresh to see progress updates
- System MUST show progress updates within 1 second of agent state changes

**R4: Execution Order Visualization**
- System MUST display execution order of agents
- System MUST show timing information for each agent execution
- System MUST visualize execution timeline with agent durations
- System MUST indicate parallel vs sequential execution patterns

**R5: Progress Events Log**
- System MUST maintain chronological log of all progress events
- System MUST display progress events with timestamps
- System MUST show event types (agent_start, agent_complete, task_start, task_complete, task_progress)
- System MUST include human-readable messages for each event

### 13.3 Progress Tracking Architecture

#### 13.3.1 Progress Event System

**Event Types**:
- `agent_start`: Agent execution started
- `agent_complete`: Agent execution completed
- `task_start`: Task started within an agent
- `task_complete`: Task completed within an agent
- `task_progress`: Task progress update

**Event Structure**:
```python
{
    "timestamp": str,  # ISO timestamp
    "agent": str,  # Agent name
    "event_type": str,  # Event type
    "message": str,  # Human-readable message
    "task_name": Optional[str],  # Task name (for task-level events)
    "symbol": Optional[str],  # Symbol being processed
    "status": str,  # "running", "completed", "failed"
    "execution_order": int,  # Order in execution sequence
    "is_parallel": bool,  # Whether parallel execution
    "transaction_id": str  # Transaction ID
}
```

#### 13.3.2 Progress Tracking Components

**ProgressTracker Utility** (`src/utils/progress_tracker.py`):
- Centralized progress event creation and management
- Event formatting for UI display
- Utilities for extracting current agent and tasks from events
- Support for both agent-level and task-level events

**State Extensions** (`src/orchestrator/state.py`):
- `progress_events`: List of progress events
- `current_agent`: Currently executing agent name
- `current_tasks`: Dictionary mapping agent names to active task lists
- `execution_order`: List of execution order entries with timing

**Agent Progress Reporting** (`src/agents/base_agent.py`):
- `report_progress()`: Report generic progress event
- `start_task()`: Mark task start
- `complete_task()`: Mark task completion
- `report_agent_start()`: Report agent execution start
- `report_agent_complete()`: Report agent execution complete

**Workflow Streaming** (`src/orchestrator/workflow.py`):
- `stream_query()`: Generator function that yields state updates with progress events
- Real-time streaming of progress information
- Integration with LangGraph streaming

**UI Progress Display** (`src/ui/progress_display.py`):
- Progress panel components
- Timeline visualization
- Agent status display
- Progress events formatting

### 13.4 UI Integration

#### 13.4.1 Progress Panel Components

**Current Agent Status**:
- Displays name of currently executing agent
- Updates in real-time as agents start/complete
- Shows "Waiting for query..." when idle

**Active Tasks List**:
- Lists all active tasks for current agent
- Updates as tasks start/complete
- Shows "None" when no active tasks

**Progress Events Log**:
- Chronological list of all progress events
- Shows most recent events (configurable limit)
- Includes timestamps and human-readable messages
- Auto-scrolls to show latest events

**Execution Timeline Chart**:
- Visual timeline showing agent execution order
- Gantt-style chart with agent durations
- Updates as agents complete execution
- Shows parallel execution patterns

#### 13.4.2 Real-Time Update Mechanism

**Streaming Implementation**:
- UI uses Gradio generator function for real-time updates
- `process_query()` generator yields updates as they occur
- Each yield updates all progress display components
- Updates occur within 1 second of agent state changes

**Update Flow**:
1. User submits query
2. Workflow streams state updates via `stream_query()`
3. Each state update includes progress events
4. UI generator yields progress updates immediately
5. Gradio updates UI components in real-time
6. Process continues until all agents complete

### 13.5 Agent-Specific Progress Reporting

#### 13.5.1 Research Agent Progress

**Task-Level Progress**:
- "Fetch stock price" for each symbol
- "Fetch company info" for each symbol
- "Fetch news articles" for each symbol
- "Fetch historical data" for each symbol (when applicable)
- "Fetch financial statements" for each symbol (when applicable)
- "Store news in vector DB" for each symbol

**Progress Events**:
- Reports when starting symbol processing
- Reports each data fetch task start/complete
- Reports symbol processing completion

#### 13.5.2 Analyst Agent Progress

**Task-Level Progress**:
- "Query historical patterns" for each symbol
- "Analyze financials" for each symbol
- "Analyze sentiment" for each symbol (when news available)
- "Analyze trends" for each symbol (when applicable)
- "Generate reasoning" for each symbol

**Progress Events**:
- Reports when starting symbol analysis
- Reports each analysis step start/complete
- Reports symbol analysis completion

#### 13.5.3 Reporting Agent Progress

**Task-Level Progress**:
- "Prepare context summary"
- "Generate report with LLM"
- "Prepare visualizations"
- "Store report in vector DB"

**Progress Events**:
- Reports each report generation step start/complete
- Reports report generation completion

### 13.6 Technical Implementation

#### 13.6.1 Streaming Architecture

**Workflow Level**:
- `stream_query()` generator yields state updates
- Each yield includes progress events from current state
- Updates occur after each agent node execution

**Graph Level**:
- `graph.stream()` uses LangGraph streaming
- Yields state updates after each node execution
- Includes progress events in streamed state

**UI Level**:
- `process_query()` generator function
- Yields progress updates as workflow streams
- Gradio automatically updates UI components

#### 13.6.2 Progress Event Storage

**In-Memory Storage**:
- Progress events stored in `AgentState.progress_events`
- Events persist throughout execution
- Available for final display and debugging

**Event Lifecycle**:
1. Agent creates progress event via `report_progress()` or helper methods
2. Event added to state via `StateManager.add_progress_event()`
3. State updated with current agent and tasks
4. Event included in streamed state updates
5. UI displays event in real-time
6. Event persists in final state for historical view

### 13.7 User Experience

#### 13.7.1 Progress Display Examples

**Agent-Level Progress**:
- "Research Agent: Starting execution..."
- "Research Agent: Completed execution (2.3s)"
- "Analyst Agent: Starting execution..."
- "Analyst Agent: Completed execution (4.1s)"

**Task-Level Progress**:
- "Research Agent: Starting Fetch stock price for AAPL..."
- "Research Agent: Completed Fetch stock price for AAPL"
- "Analyst Agent: Starting Analyze financials for AAPL..."
- "Analyst Agent: Completed Analyze financials for AAPL"

#### 13.7.2 Execution Timeline

**Timeline Visualization**:
- Horizontal bars showing agent execution
- Bars positioned by start time
- Bar length represents duration
- Color coding for different agents
- Labels showing agent names and durations

### 13.8 Benefits

**User Benefits**:
- Clear visibility into system activity
- Understanding of execution order and timing
- Confidence that system is working
- Ability to see progress for long-running queries

**Developer Benefits**:
- Easy debugging of agent execution flow
- Performance analysis through timing data
- Understanding of execution patterns
- Historical progress data for optimization

### 13.9 Success Criteria

- ✅ Progress events created for all agent executions
- ✅ Task-level progress reported for major operations
- ✅ Real-time updates displayed in UI within 1 second
- ✅ Execution timeline accurately shows agent order and timing
- ✅ Progress panel displays current agent and active tasks
- ✅ Progress events log shows chronological event history
- ✅ Streaming mechanism works without blocking UI
- ✅ Progress tracking has minimal performance impact (<1% overhead)

## 14. Future Enhancements (Out of Scope for POC)

- User authentication and query history
- Advanced caching mechanisms
- Multi-modal inputs (charts, PDFs)
- Agent learning from feedback
- Custom agent creation by users
- Progress persistence for historical analysis
- Progress analytics and optimization insights
- User preferences for progress display granularity
- Enhanced parallel execution tracking


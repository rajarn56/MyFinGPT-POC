# MyFinGPT Developer Guide

This guide provides detailed instructions for developers working on MyFinGPT, including how to set up, start, stop, restart, troubleshoot, and test individual components.

## Table of Contents

- [Overview](#overview)
- [Component Architecture](#component-architecture)
- [Development Environment Setup](#development-environment-setup)
- [Individual Component Management](#individual-component-management)
- [Testing and Debugging](#testing-and-debugging)
- [Troubleshooting](#troubleshooting)
- [Logging and Monitoring](#logging-and-monitoring)

## Overview

MyFinGPT consists of several key components that work together:

1. **Gradio UI** - Web interface for user interactions with real-time progress tracking
2. **Workflow Orchestrator** - LangGraph-based workflow management with streaming support
3. **Agents** - Research, Analyst, and Reporting agents with progress reporting
4. **MCP Clients** - Yahoo Finance, Alpha Vantage, FMP API clients
5. **Vector Database** - Chroma for semantic search and storage
6. **LLM Integration** - LiteLLM for multi-provider LLM support
7. **Progress Tracking** - Real-time progress event tracking and display system

## Component Architecture

```
┌─────────────────┐
│   Gradio UI     │
└────────┬────────┘
         │
┌────────▼────────┐
│   Workflow      │
└────────┬────────┘
         │
┌────────▼────────┐
│  LangGraph      │
└────────┬────────┘
         │
    ┌────┴────┐
    │ Agents │
    └────┬───┘
         │
    ┌────┴────┐
    │  MCP    │
    │ Clients │
    └────┬────┘
         │
    ┌────┴────┐
    │ Vector  │
    │   DB    │
    └─────────┘
```

## Development Environment Setup

### Prerequisites

- Python 3.8+
- pip package manager
- Git
- Virtual environment (recommended)

### Initial Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd project1
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Verify installation**:
```bash
python -c "import gradio; import langgraph; import chromadb; print('All dependencies installed')"
```

## Individual Component Management

### 1. Gradio UI Component

#### Setup
The UI component is automatically initialized when you run `main.py`. No separate setup needed.

#### Start
```bash
# Basic startup
python main.py

# With custom options
python main.py --provider openai --port 7860 --host 0.0.0.0

# With public sharing
python main.py --share
```

**What to expect:**
- Server starts on http://localhost:7860 (or specified port)
- Logs show: `[UI] Launching Gradio app | Host: 0.0.0.0 | Port: 7860`
- Browser opens automatically (or navigate manually)
- UI shows query input panel, progress panel, and three tabs

**Logs to look for:**
```
[UI] Launching Gradio app | Host: 0.0.0.0 | Port: 7860
[UI] Gradio app launching at http://0.0.0.0:7860
```

#### Stop
```bash
# In terminal where app is running
Ctrl+C

# Or find and kill process
lsof -i :7860  # Find process
kill <PID>     # Kill process
```

**What to expect:**
- Graceful shutdown message
- Port becomes available
- Logs show shutdown sequence

#### Restart
```bash
# Stop current instance (Ctrl+C)
# Start again
python main.py
```

#### Test/Debug
```bash
# Test UI component directly
python -c "
from src.ui.gradio_app import MyFinGPTUI
ui = MyFinGPTUI()
ui.create_interface()
print('UI interface created successfully')
"

# Test with a simple query
python -c "
from src.ui.gradio_app import MyFinGPTUI
ui = MyFinGPTUI()
result = ui.process_query('Analyze AAPL')
print('Query processed:', result[0][:100])
"
```

**Debugging tips:**
- Check logs for `[UI]` prefixed messages
- Verify port is not in use: `lsof -i :7860`
- Test with verbose logging: `export LOG_LEVEL=DEBUG`

---

### 2. Workflow Orchestrator

#### Setup
The workflow orchestrator is initialized automatically when the UI starts. It manages the LangGraph workflow.

#### LangChain vs LangGraph - Why LangChain is Listed but Not Used

**Important Note**: You may notice that `langchain>=0.1.0` is listed in `requirements.txt`, but there are **NO direct imports** of LangChain in the codebase. Here's why:

**LangGraph and LangChain Relationship:**
- **LangGraph** is built on top of LangChain and extends its capabilities
- LangGraph can be used **independently** for graph-based workflows (as in this project)
- LangChain is listed in requirements because:
  1. **Transitive Dependency**: LangGraph may require LangChain as a dependency (even if not directly imported)
  2. **Future Compatibility**: Some LangGraph features may require LangChain components
  3. **Ecosystem Standard**: It's common practice to include both when using LangGraph

**What This Project Actually Uses:**
- **LangGraph only**: `from langgraph.graph import StateGraph, END`
- **Direct LangGraph API**: The code uses LangGraph's `StateGraph` for workflow orchestration
- **No LangChain imports**: No `from langchain` imports anywhere in the codebase

**Why LangGraph Instead of LangChain?**
- **LangChain**: Designed for linear, sequential workflows (simple chains)
- **LangGraph**: Designed for complex, graph-based workflows with:
  - State management across nodes
  - Conditional branching
  - Parallel execution support
  - Stateful multi-agent coordination
  
**Can LangChain be Removed?**
- **Not recommended**: LangGraph likely has LangChain as a dependency
- **Safe to keep**: Having it in requirements.txt ensures compatibility
- **No harm**: It's not imported, so it doesn't affect code complexity

**Summary:**
- LangChain is in `requirements.txt` for dependency/compatibility reasons
- The code uses **only LangGraph** directly
- LangGraph provides the graph-based orchestration needed for multi-agent workflows
- No LangChain code is written or imported in this project

#### Start
The workflow starts automatically when processing a query. To test it directly:

```bash
python -c "
from src.orchestrator.workflow import MyFinGPTWorkflow
workflow = MyFinGPTWorkflow()
print('Workflow initialized')
"
```

**What to expect:**
- Workflow object created
- Graph compiled successfully
- Logs show: `[GRAPH] LangGraph workflow compiled successfully`

#### Stop
The workflow stops when the application stops. No separate stop needed.

#### Restart
Restart the main application to restart the workflow.

#### Test/Debug
```bash
# Test workflow with a query
python -c "
from src.orchestrator.workflow import MyFinGPTWorkflow
workflow = MyFinGPTWorkflow()
result = workflow.process_query('Analyze AAPL stock')
print('Query processed successfully')
print('Agents executed:', result['agents_executed'])
print('Total tokens:', sum(result['token_usage'].values()))
"

# Test state creation
python -c "
from src.orchestrator.state import StateManager
state = StateManager.create_initial_state('Analyze AAPL')
print('Initial state created:', state['query'])
print('Symbols:', state['symbols'])
print('Query type:', state['query_type'])
"
```

**Debugging tips:**
- Check logs for `[WORKFLOW]` and `[GRAPH]` prefixed messages
- Monitor state transitions in logs
- Check execution times and token usage

---

### 3. Research Agent

#### Setup
The Research Agent is initialized as part of the workflow. It requires:
- MCP clients (Yahoo Finance, Alpha Vantage, FMP)
- Vector database access

#### Start
The agent starts automatically when the workflow executes. To test directly:

```bash
python -c "
from src.agents.research_agent import ResearchAgent
from src.orchestrator.state import StateManager

agent = ResearchAgent()
state = StateManager.create_initial_state('Analyze AAPL')
state = agent.run(state)
print('Research Agent executed')
print('Research data keys:', list(state['research_data'].keys()))
"
```

**What to expect:**
- Agent initializes with MCP clients
- Fetches data for each symbol
- Stores news in vector DB
- Logs show: `Research Agent: Completed data collection for <SYMBOL>`

#### Stop
Agent stops when workflow completes. No separate stop needed.

#### Restart
Restart the workflow to restart the agent.

#### Test/Debug
```bash
# Test Research Agent directly
python -c "
from src.agents.research_agent import ResearchAgent
from src.orchestrator.state import StateManager

agent = ResearchAgent()
state = StateManager.create_initial_state('Analyze AAPL')
print('Starting Research Agent...')
state = agent.run(state)
print('Research completed')
print('Symbols processed:', list(state['research_data'].keys()))
print('Citations:', len(state['citations']))
"

# Test MCP client access
python -c "
from src.mcp.mcp_client import UnifiedMCPClient
client = UnifiedMCPClient()
price = client.get_stock_price('AAPL')
print('Price fetched:', price['current_price'])
"
```

**Debugging tips:**
- Check logs for `Research Agent:` prefixed messages
- Verify MCP client connectivity
- Check vector DB storage operations
- Monitor API rate limits

---

### 4. Analyst Agent

#### Setup
The Analyst Agent requires:
- Research data from Research Agent
- Vector database access
- LLM provider configured

#### Start
The agent starts automatically after Research Agent completes. To test directly:

```bash
python -c "
from src.agents.analyst_agent import AnalystAgent
from src.orchestrator.state import StateManager
from src.agents.research_agent import ResearchAgent

# First run Research Agent
research = ResearchAgent()
state = StateManager.create_initial_state('Analyze AAPL')
state = research.run(state)

# Then run Analyst Agent
analyst = AnalystAgent()
state = analyst.run(state)
print('Analysis completed')
print('Analysis results:', list(state['analysis_results'].keys()))
"
```

**What to expect:**
- Agent reads research data
- Performs financial analysis
- Analyzes sentiment (if news available)
- Queries vector DB for historical patterns
- Logs show: `Analyst Agent: Completed analysis for <SYMBOL>`

#### Stop
Agent stops when analysis completes. No separate stop needed.

#### Restart
Restart the workflow to restart the agent.

#### Test/Debug
```bash
# Test Analyst Agent with mock data
python -c "
from src.agents.analyst_agent import AnalystAgent
from src.orchestrator.state import StateManager

agent = AnalystAgent()
state = StateManager.create_initial_state('Analyze AAPL')
# Add mock research data
state['research_data'] = {
    'AAPL': {
        'price': {'current_price': 150, 'market_cap': 2500000000000},
        'company': {'name': 'Apple Inc.', 'sector': 'Technology'}
    }
}
state = agent.run(state)
print('Analysis completed')
print('Results:', state['analysis_results'])
"
```

**Debugging tips:**
- Check logs for `Analyst Agent:` prefixed messages
- Verify LLM calls are successful
- Check vector DB queries
- Monitor sentiment analysis results

---

### 5. Reporting Agent

#### Setup
The Reporting Agent requires:
- Research data from Research Agent
- Analysis results from Analyst Agent
- LLM provider configured

#### Start
The agent starts automatically after Analyst Agent completes. To test directly:

```bash
python -c "
from src.agents.reporting_agent import ReportingAgent
from src.orchestrator.state import StateManager
from src.agents.research_agent import ResearchAgent
from src.agents.analyst_agent import AnalystAgent

# Run full pipeline
research = ResearchAgent()
analyst = AnalystAgent()
reporting = ReportingAgent()

state = StateManager.create_initial_state('Analyze AAPL')
state = research.run(state)
state = analyst.run(state)
state = reporting.run(state)

print('Report generated')
print('Report length:', len(state['final_report']))
print('Visualizations:', list(state['visualizations'].keys()))
"
```

**What to expect:**
- Agent reads research and analysis data
- Generates comprehensive report using LLM
- Prepares visualization data
- Stores report in vector DB
- Logs show: `Reporting Agent: Report generation completed`

#### Stop
Agent stops when report generation completes. No separate stop needed.

#### Restart
Restart the workflow to restart the agent.

#### Test/Debug
```bash
# Test Reporting Agent
python -c "
from src.agents.reporting_agent import ReportingAgent
from src.orchestrator.state import StateManager

agent = ReportingAgent()
state = StateManager.create_initial_state('Analyze AAPL')
# Add mock data
state['research_data'] = {'AAPL': {'price': {'current_price': 150}}}
state['analysis_results'] = {'AAPL': {'recommendation': {'action': 'buy'}}}
state = agent.run(state)
print('Report:', state['final_report'][:200])
"
```

**Debugging tips:**
- Check logs for `Reporting Agent:` prefixed messages
- Verify LLM report generation
- Check visualization data preparation
- Monitor vector DB storage

---

### 6. MCP Clients

#### Setup
MCP clients are initialized automatically. They require:
- API keys (for Alpha Vantage and FMP, optional)
- Internet connection

#### Start
Clients start automatically when initialized. To test:

```bash
# Test Yahoo Finance client
python -c "
from src.mcp.yahoo_finance import YahooFinanceClient
client = YahooFinanceClient()
price = client.get_stock_price('AAPL')
print('Yahoo Finance - Price:', price['current_price'])
"

# Test Alpha Vantage client
python -c "
from src.mcp.alpha_vantage import AlphaVantageClient
client = AlphaVantageClient()
try:
    price = client.get_stock_price('AAPL')
    print('Alpha Vantage - Price:', price.get('current_price'))
except Exception as e:
    print('Alpha Vantage error (may need API key):', e)
"

# Test Unified MCP Client
python -c "
from src.mcp.mcp_client import UnifiedMCPClient
client = UnifiedMCPClient()
price = client.get_stock_price('AAPL', preferred_source='yahoo')
print('Unified MCP - Price:', price['current_price'])
"
```

**What to expect:**
- Clients initialize successfully
- API calls complete
- Data returned with citations
- Logs show: `[MCP:YahooFinance] Stock price fetched for <SYMBOL>`

#### Stop
Clients stop when application stops. No separate stop needed.

#### Restart
Restart the application to restart clients.

#### Test/Debug
```bash
# Test all MCP clients
python -c "
from src.mcp.mcp_client import UnifiedMCPClient
client = UnifiedMCPClient()

# Test with fallback
symbols = ['AAPL', 'MSFT', 'GOOGL']
for symbol in symbols:
    try:
        price = client.get_stock_price(symbol)
        print(f'{symbol}: ${price[\"current_price\"]}')
    except Exception as e:
        print(f'{symbol}: Error - {e}')
"
```

**Debugging tips:**
- Check logs for `[MCP:]` prefixed messages
- Verify API keys are set (for Alpha Vantage/FMP)
- Check rate limits
- Monitor fallback behavior

---

### 7. Vector Database (Chroma)

#### Setup
Chroma DB is initialized automatically on first use. Database is stored in `./chroma_db/`.

#### Start
Database starts automatically when accessed. To initialize manually:

```bash
python -c "
from src.vector_db.chroma_client import ChromaClient
client = ChromaClient()
print('Chroma DB initialized')
print('Collections:', list(client.collections.keys()))
"
```

**What to expect:**
- Database directory created (`./chroma_db/`)
- Three collections initialized: `financial_news`, `company_analysis`, `market_trends`
- Logs show: `[VectorDB] Chroma client initialized | Collections: [...]`

#### Stop
Database stops when application stops. Data persists on disk.

#### Restart
Database restarts automatically on next access. To clear and restart:

```bash
# Clear database
rm -rf chroma_db/

# Reinitialize
python -c "
from src.vector_db.chroma_client import ChromaClient
client = ChromaClient()
print('Database reinitialized')
"
```

#### Test/Debug
```bash
# Test vector DB operations
python -c "
from src.vector_db.chroma_client import ChromaClient
from src.vector_db.embeddings import EmbeddingPipeline

client = ChromaClient()
pipeline = EmbeddingPipeline()

# Add a test document
doc_id = client.add_document(
    collection_name='financial_news',
    document='Test news article about AAPL',
    metadata={'symbol': 'AAPL', 'title': 'Test'},
    embedding=pipeline.generate_embedding('Test news article about AAPL')
)
print('Document added:', doc_id)

# Query
results = client.query('financial_news', 'AAPL stock', n_results=1)
print('Query results:', len(results.get('ids', [[]])[0]))

# Get stats
stats = client.get_collection_stats('financial_news')
print('Collection stats:', stats)
"
```

**Debugging tips:**
- Check logs for `[VectorDB]` prefixed messages
- Verify database directory exists and is writable
- Check collection statistics
- Monitor embedding generation

#### Data Storage: Context Cache vs Vector Database

This section clearly explains what data is stored in **Context Cache** vs **Vector Database (ChromaDB)**, their purposes, retention policies, and when each is used.

---

### **Context Cache** (`ContextCache`)

**Purpose**: Temporary in-memory cache to avoid redundant API calls and enable query similarity detection.

**Storage Location**: In-memory (Python dictionary)
**Retention**: **24 hours** (configurable via `cache_ttl_hours` parameter)
**TTL**: Data expires after 24 hours and is automatically removed

**What is Stored in Context Cache:**

1. **API Query Results** (cached to avoid redundant API calls):
   - **Price Data** (`symbol:price`): Current stock prices, market cap, volume, P/E ratio
   - **Company Info** (`symbol:company`): Company profiles, sectors, industries, descriptions
   - **News Data** (`symbol:news`): News articles fetched from MCP sources (raw API response)
   - **Historical Data** (`symbol:historical`): Historical price trends, OHLCV data
   - **Financials** (`symbol:financials`): Financial statements (balance sheets, income statements, cash flow)

2. **Query History** (for similarity detection):
   - Query text
   - Symbols in query
   - Query ID (transaction_id)
   - Query embedding vector
   - **Retention**: Last 100 queries (count-based, not time-based)

**When Context Cache is Used:**
- **Before API calls**: Research Agent checks cache before making MCP API calls
- **After API calls**: Research Agent stores API results in cache for future use
- **Query similarity**: Workflow uses query history to detect similar previous queries

**Cache Key Format**: `{symbol}:{data_type}` (e.g., `AAPL:price`, `MSFT:company`)

**Example Flow:**
```python
# First query for AAPL
cache.get("AAPL", "price")  # Returns None (cache miss)
price_data = mcp_client.get_stock_price("AAPL")  # API call
cache.set("AAPL", "price", price_data)  # Cache result

# Second query for AAPL (within 24 hours)
cache.get("AAPL", "price")  # Returns cached data (cache hit, no API call)
```

**Configuration:**
```python
# Default: 24 hours
context_cache = ContextCache()

# Custom TTL: 48 hours
context_cache = ContextCache(cache_ttl_hours=48)
```

---

### **Vector Database (ChromaDB)**

**Purpose**: Persistent storage for text documents that need semantic search and similarity matching.

**Storage Location**: Disk (`./chroma_db/` directory, configurable via `CHROMA_DB_PATH`)
**Retention**: **Permanent** (no automatic expiration - data persists until manually deleted)
**TTL**: None (persistent storage)

**What is Stored in Vector Database:**

ChromaDB has three collections, each storing specific types of data:

**1. `financial_news` Collection:**
- **Stored by**: Research Agent (during data collection)
- **Content**: Individual news articles fetched from MCP sources
- **Document Structure**:
  - **Text**: Article title + content/summary (full article text)
  - **Metadata**: `symbol`, `title`, `url`, `publisher`, `published_date`, `source`
  - **Embedding**: Vector embedding (1536 dimensions) for semantic search
- **When stored**: Automatically when Research Agent fetches news articles for a symbol
- **Purpose**: 
  - Semantic search of news content
  - Citation retrieval for reports
  - Historical news pattern matching
- **Note**: This is the **full article text**, not just the API response. Each article is stored as a separate document.

**2. `company_analysis` Collection:**
- **Stored by**: Reporting Agent (after report generation)
- **Content**: Completed analysis reports generated by the Reporting Agent
- **Document Structure**:
  - **Text**: Full analysis report text (complete report)
  - **Metadata**: `symbols`, `query_type`, `source`, `report_length`
  - **Embedding**: Vector embedding of the report text
- **When stored**: After Reporting Agent successfully generates a final report
- **Purpose**: 
  - Finding similar historical analyses
  - Pattern matching for recommendations
  - Cross-query awareness

**3. `market_trends` Collection:**
- **Stored by**: (Currently available but not actively populated)
- **Content**: Trend analysis results and market patterns
- **Purpose**: Reserved for future trend pattern storage and matching

**Vector DB Query Cache** (separate from document storage):
- **Storage**: In-memory cache (`ChromaClient.query_cache`) for vector DB **query results**
- **Retention**: **1 hour** (3600 seconds)
- **Purpose**: Caches the **results** of vector DB similarity searches to avoid redundant queries
- **What it stores**: The results returned from vector DB queries (document IDs, documents, metadata, distances)
- **Note**: This is a performance optimization cache, **NOT** stored in the vector DB itself - it's in-memory only
- **Example**: If you query "find similar news about AAPL", the query result (list of similar documents) is cached for 1 hour

**Important Distinction:**
- **Vector DB stores**: Documents (news articles, reports) - **permanent on disk**
- **Query Cache stores**: Query results (what documents were found) - **1 hour in-memory**
- These are **two different things**:
  - Documents = the actual content stored permanently
  - Query results = the temporary results of searching those documents

---

### **Key Differences: Context Cache vs Vector DB**

| Aspect | Context Cache | Vector Database |
|--------|--------------|-----------------|
| **Storage Type** | In-memory (temporary) | Disk (persistent) |
| **Retention** | 24 hours (TTL) | Permanent (until deleted) |
| **Purpose** | Avoid redundant API calls | Semantic search & pattern matching |
| **Data Format** | Raw API responses (JSON/dicts) | Text documents with embeddings |
| **What's Stored** | API query results (price, company, news, historical, financials) | Documents: News articles (full text) & analysis reports (full text)<br>Query Cache: Query results (1h TTL, in-memory) |
| **Search Capability** | Key-based lookup (`symbol:data_type`) | Semantic similarity search |
| **When Used** | Before/after API calls | Documents: For semantic search<br>Query Cache: To cache search results |

---

### **What is NOT Stored in Vector DB**

**Important**: The following data is **NOT** stored in Vector DB:

- **Stock Prices** (`price_data`): Stored only in Context Cache (24h) and LangGraph State (temporary)
- **Company Information** (`company_info`): Stored only in Context Cache (24h) and LangGraph State (temporary)
- **Historical Price Data** (`historical_data`): Stored only in Context Cache (24h) and LangGraph State (temporary)
- **Financial Statements** (`financials`): Stored only in Context Cache (24h) and LangGraph State (temporary)
- **Raw API Responses**: Only processed text content (news articles, reports) goes to Vector DB

**Why Not Store Everything in Vector DB?**
- Vector DB is optimized for **semantic search of text content**
- Structured financial data (prices, financials) doesn't benefit from embedding-based search
- Context Cache provides faster access for structured data (key-based lookup)
- Vector DB is for finding similar text patterns, not for storing structured data

---

### **Complete Data Flow**

```
┌─────────────────────────────────────────────────────────────┐
│                    User Query                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Research Agent - Data Collection              │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Check Cache  │  │  API Call    │  │ Store Cache  │
│ (24h TTL)    │  │  (if miss)   │  │ (24h TTL)    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │                 ▼                 │
       │         ┌──────────────┐          │
       │         │ MCP Sources  │          │
       │         │ (Yahoo, FMP) │          │
       │         └──────┬───────┘          │
       │                │                  │
       └────────────────┼──────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Context Cache│  │ LangGraph    │  │ Vector DB    │
│ (24h TTL)    │  │ State        │  │ (Permanent)  │
│              │  │ (Temporary)  │  │              │
│ • Price      │  │ • All data   │  │ • News       │
│ • Company    │  │   during     │  │   articles   │
│ • News       │  │   execution  │  │   (full text)│
│ • Historical │  │              │  │ • Reports    │
│ • Financials │  │              │  │   (full text) │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Storage Decision Logic:**

1. **API Results** → Context Cache (24h) + LangGraph State (temporary)
   - Fast key-based access
   - Avoids redundant API calls
   - Expires after 24 hours

2. **News Articles** → Vector DB (permanent) + Context Cache (24h)
   - Full article text stored in Vector DB for semantic search
   - Raw API response cached in Context Cache for quick access
   - Vector DB enables finding similar news articles

3. **Analysis Reports** → Vector DB (permanent)
   - Full report text stored for pattern matching
   - Enables finding similar historical analyses
   - Used for cross-query awareness

---

### **Data Persistence and Clearing**

**Context Cache:**
- **Automatic expiration**: Data expires after TTL (default 24 hours)
- **Manual clearing**: `context_cache.clear_cache()` or restart application
- **Query history**: Last 100 queries (oldest removed when limit reached)

**Vector Database:**
- **Documents**: Persist on disk in `./chroma_db/` directory (permanent)
- **No automatic expiration**: Documents remain until manually deleted
- **Survives restarts**: Database persists across application restarts
- **Query Cache**: In-memory only, expires after 1 hour, lost on restart

**Clearing Vector DB:**

See the "Data Persistence and Clearing" section below for detailed instructions on clearing Vector DB collections.

#### Data Persistence and Clearing

**Data Persistence:**
- Chroma DB data persists on disk in the `./chroma_db/` directory
- Data accumulates over time - there is **NO automatic expiration or cleanup**
- All stored documents remain until manually deleted
- Database survives application restarts

**Data Clearing Options:**

**1. Manual Collection Reset:**
```python
from src.vector_db.chroma_client import ChromaClient

client = ChromaClient()
# Reset a specific collection (deletes all documents, recreates empty collection)
client.reset_collection('financial_news')
```

**2. Delete Entire Database:**
```bash
# Remove entire database directory
rm -rf chroma_db/

# Database will be recreated on next access
```

**3. Delete Individual Documents:**
```python
from src.vector_db.chroma_client import ChromaClient

client = ChromaClient()
# Delete a specific document by ID
client.delete_document('financial_news', 'document_id_here')
```

**4. Check Collection Statistics:**
```python
from src.vector_db.chroma_client import ChromaClient

client = ChromaClient()
# Get document count for a collection
stats = client.get_collection_stats('financial_news')
print(f"Documents in financial_news: {stats['count']}")
```

**Important Notes:**
- The `reset_collection()` method exists but is **NOT called automatically** - it must be invoked manually
- Data grows indefinitely unless manually cleared
- Consider periodic cleanup if disk space is a concern
- Historical data in Chroma DB can be valuable for pattern matching, so clearing should be done thoughtfully

---

### **News Article Storage Behavior: Duplicate Handling**

**Scenario**: A stock is queried, news is stored in vector DB. The same stock is queried again after 30 hours.

**Current Behavior:**

1. **Context Cache (24-hour TTL)**:
   - After 30 hours, the cache has expired
   - System will fetch **NEW news** from the API (latest 10 articles)
   - The API typically returns the most recent articles, which may include:
     - Some articles from the previous query (if still recent)
     - New articles published since the last query

2. **Vector DB Storage**:
   - **No deduplication logic currently implemented**
   - All articles are stored, including duplicates
   - Document IDs are auto-generated using timestamp: `financial_news_{timestamp}`
   - Same article = different timestamp = different ID = **duplicate stored**

3. **What Happens**:
   ```
   Query 1 (T=0):
   - Fetches 10 articles: [Article A, B, C, D, E, F, G, H, I, J]
   - Stores all 10 in Vector DB
   - Caches in Context Cache (24h TTL)
   
   Query 2 (T=30 hours):
   - Context Cache expired → Fetches NEW news from API
   - API returns: [Article K, L, M, N, O, P, Q, R, S, T] (newer articles)
   - OR may return: [Article C, D, E, F, G, H, I, J, K, L] (mix of old + new)
   - Stores ALL articles in Vector DB again
   - Result: Duplicates if same articles appear (Article C, D, E, etc.)
   ```

**Current Limitations:**

- **No URL-based deduplication**: Articles with same URL are stored multiple times
- **No title-based deduplication**: Articles with same title are stored multiple times
- **No timestamp checking**: System doesn't check if article already exists before storing

**Impact:**

- Vector DB will accumulate duplicate articles over time
- Same article may appear multiple times in search results
- Database size grows unnecessarily
- Search results may show duplicates

**Future Improvements (Not Currently Implemented):**

1. **URL-based deduplication**: Check if article URL already exists before storing
2. **Title + Published Date deduplication**: Use title + published_date as unique key
3. **Hash-based document IDs**: Use URL hash as document ID to prevent duplicates
4. **Upsert logic**: Update existing document instead of creating duplicate

**Example of How Deduplication Could Work:**

```python
# Pseudo-code for future improvement
def _store_news_in_vector_db(self, symbol: str, articles: List[Dict[str, Any]]):
    for article in articles:
        url = article.get("url") or article.get("link", "")
        
        # Generate document ID from URL hash (ensures uniqueness)
        doc_id = hashlib.md5(url.encode()).hexdigest()
        
        # Check if document already exists
        existing = self.vector_db.get_collection("financial_news").get(ids=[doc_id])
        
        if not existing.get("ids"):
            # New article - store it
            self.vector_db.add_document(..., document_id=doc_id)
        else:
            # Article already exists - skip or update timestamp
            logger.debug(f"Article already exists: {url}")
```

**Current Workaround:**

- Manually clear old collections periodically
- Use vector DB query filters to exclude duplicates in search results
- Monitor database size and clean up as needed

---

### 8. LLM Integration (LiteLLM)

#### Setup
LLM integration is configured via `config/llm_templates.yaml` and environment variables.

#### Start
LLM integration starts automatically when agents make calls. To test:

```bash
# Test LLM configuration
python -c "
from src.utils.llm_config import llm_config
print('Available providers:', llm_config.list_available_providers())
print('Default provider:', llm_config.get_default_provider())
"

# Test LLM call
python -c "
from src.agents.base_agent import BaseAgent
agent = BaseAgent('Test Agent')
response = agent.call_llm([
    {'role': 'user', 'content': 'Say hello'}
])
print('LLM response:', response['content'][:100])
"
```

**What to expect:**
- LLM client configured
- API calls successful
- Token usage tracked
- Logs show: `Test Agent: LLM call completed in X.XXs, tokens: XXX`

#### Stop
LLM integration stops when application stops. No separate stop needed.

#### Restart
Restart the application to restart LLM integration.

#### Test/Debug
```bash
# Test different providers
python -c "
import os
os.environ['LITELLM_MODEL'] = 'openai'
from src.utils.llm_config import llm_config
print('OpenAI config:', llm_config.get_provider_config('openai'))
"

# Test token tracking
python -c "
from src.utils.token_tracker import TokenTracker
tracker = TokenTracker()
tracker.track_tokens('test_agent', 100, 'completion', 'gpt-4')
print('Total tokens:', tracker.get_agent_tokens('test_agent'))
"
```

**Debugging tips:**
- Check logs for LLM call messages
- Verify API keys are set
- Check token usage tracking
- Monitor API rate limits and quotas

---

## Testing and Debugging

### Running Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

### Component Testing Scripts

Create test scripts for each component:

**test_workflow.py**:
```python
#!/usr/bin/env python
"""Test workflow component"""
from src.orchestrator.workflow import MyFinGPTWorkflow

workflow = MyFinGPTWorkflow()
result = workflow.process_query("Analyze AAPL stock")
print("Workflow test passed!")
print(f"Agents executed: {result['agents_executed']}")
print(f"Total tokens: {sum(result['token_usage'].values())}")
```

**test_agents.py**:
```python
#!/usr/bin/env python
"""Test individual agents"""
from src.agents.research_agent import ResearchAgent
from src.agents.analyst_agent import AnalystAgent
from src.agents.reporting_agent import ReportingAgent
from src.orchestrator.state import StateManager

state = StateManager.create_initial_state("Analyze AAPL")

# Test Research Agent
research = ResearchAgent()
state = research.run(state)
print("Research Agent: PASSED")

# Test Analyst Agent
analyst = AnalystAgent()
state = analyst.run(state)
print("Analyst Agent: PASSED")

# Test Reporting Agent
reporting = ReportingAgent()
state = reporting.run(state)
print("Reporting Agent: PASSED")
print(f"Report length: {len(state['final_report'])}")
```

**test_mcp_clients.py**:
```python
#!/usr/bin/env python
"""Test MCP clients"""
from src.mcp.mcp_client import UnifiedMCPClient

client = UnifiedMCPClient()
symbols = ['AAPL', 'MSFT', 'GOOGL']

for symbol in symbols:
    try:
        price = client.get_stock_price(symbol)
        print(f"{symbol}: ${price['current_price']} - PASSED")
    except Exception as e:
        print(f"{symbol}: FAILED - {e}")
```

**test_vector_db.py**:
```python
#!/usr/bin/env python
"""Test vector database"""
from src.vector_db.chroma_client import ChromaClient
from src.vector_db.embeddings import EmbeddingPipeline

client = ChromaClient()
pipeline = EmbeddingPipeline()

# Test add document
doc_id = client.add_document(
    'financial_news',
    'Test document',
    {'symbol': 'AAPL'},
    embedding=pipeline.generate_embedding('Test document')
)
print(f"Add document: PASSED (ID: {doc_id})")

# Test query
results = client.query('financial_news', 'AAPL', n_results=1)
print(f"Query: PASSED (Results: {len(results.get('ids', [[]])[0])})")

# Test stats
stats = client.get_collection_stats('financial_news')
print(f"Stats: PASSED (Count: {stats['count']})")
```

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python main.py
```

Or in Python:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Troubleshooting

### Common Issues by Component

#### UI Component Issues

**Issue: Port already in use**
```bash
# Find process using port
lsof -i :7860

# Kill process
kill <PID>

# Or use different port
python main.py --port 7861
```

**Issue: UI not loading**
- Check logs for errors
- Verify Gradio installation: `pip install gradio`
- Check firewall settings
- Try `--host 127.0.0.1` instead of `0.0.0.0`

#### Workflow Issues

**Issue: Workflow hangs**
- Check logs for which agent is stuck
- Verify LLM API keys are valid
- Check network connectivity
- Monitor token usage (may hit limits)

**Issue: State validation errors**
- Check logs for validation details
- Verify query format
- Check symbol extraction
- Review guardrails logs

#### Agent Issues

**Issue: Research Agent fails**
- Check MCP client connectivity
- Verify API keys (for Alpha Vantage/FMP)
- Check rate limits
- Review error logs for specific API failures

**Issue: Analyst Agent fails**
- Verify Research Agent completed successfully
- Check LLM API key and quota
- Verify vector DB is accessible
- Review sentiment analysis logs

**Issue: Reporting Agent fails**
- Verify both Research and Analyst agents completed
- Check LLM API key and quota
- Review report generation logs
- Check context size (may be too large)

#### MCP Client Issues

**Issue: API rate limits**
- Check logs for rate limit errors
- Wait before retrying
- Use different data source
- Consider upgrading API tier

**Issue: Invalid symbols**
- Verify symbol format (uppercase, 1-5 letters)
- Check symbol exists on exchange
- Review guardrails validation logs

#### Vector DB Issues

**Issue: Database locked**
```bash
# Check for running processes
ps aux | grep python

# Kill hanging processes
kill <PID>

# Clear lock (if safe)
rm -rf chroma_db/.lock
```

**Issue: Embedding generation fails**
- Check LLM API key (for embedding model)
- Verify internet connectivity
- Check embedding model availability
- Review embedding pipeline logs

#### LLM Integration Issues

**Issue: API key not found**
```bash
# Verify .env file
cat .env | grep API_KEY

# Test API key
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('API Key:', os.getenv('OPENAI_API_KEY')[:10] + '...')
"
```

**Issue: Token limit exceeded**
- Reduce query complexity
- Use model with higher token limit
- Enable context pruning
- Check context size in logs

**Issue: Provider not available**
- Verify provider in `config/llm_templates.yaml`
- Check API key is set
- Test provider configuration
- Review LLM config logs

### Debugging Commands

**Check component health**:
```bash
# Check all components
python -c "
from src.ui.gradio_app import MyFinGPTUI
from src.orchestrator.workflow import MyFinGPTWorkflow
from src.mcp.mcp_client import UnifiedMCPClient
from src.vector_db.chroma_client import ChromaClient

print('UI:', 'OK' if MyFinGPTUI() else 'FAILED')
print('Workflow:', 'OK' if MyFinGPTWorkflow() else 'FAILED')
print('MCP Client:', 'OK' if UnifiedMCPClient() else 'FAILED')
print('Vector DB:', 'OK' if ChromaClient() else 'FAILED')
"
```

**Check logs for errors**:
```bash
# Run with verbose logging
export LOG_LEVEL=DEBUG
python main.py 2>&1 | grep -i error
```

**Monitor component performance**:
```bash
# Run query and monitor logs
python main.py 2>&1 | grep -E "\[WORKFLOW\]|\[GRAPH\]|\[.*Agent\]"
```

## Logging and Monitoring

### Log File Structure

All logs are written to files in the `./logs/` directory (configurable via `LOG_DIR` environment variable). Logs are organized as follows:

#### Log File Types

1. **Main Log File**: `myfingpt_YYYY-MM-DD.log`
   - Contains ALL log messages from all components
   - Rotates at 100MB
   - Retained for 30 days
   - Compressed after rotation

2. **Error Log File**: `myfingpt_errors_YYYY-MM-DD.log`
   - Contains only WARNING and ERROR level messages
   - Rotates at 50MB
   - Retained for 90 days (longer retention for debugging)
   - Compressed after rotation

3. **Component-Specific Log Files**:
   - `workflow_YYYY-MM-DD.log` - Workflow orchestrator and LangGraph logs
   - `agents_YYYY-MM-DD.log` - All agent logs (Research, Analyst, Reporting)
   - `mcp_YYYY-MM-DD.log` - MCP client logs (Yahoo Finance, Alpha Vantage, FMP)
   - `vectordb_YYYY-MM-DD.log` - Vector database operations
   - `ui_YYYY-MM-DD.log` - UI component logs
   - All rotate at 50MB, retained for 30 days, compressed after rotation

#### Log File Location

```bash
# Default location
./logs/

# Custom location (set via environment variable)
export LOG_DIR=/path/to/logs
python main.py
```

### Log Format

#### Console Format (Simple)
```
2024-01-15 10:30:45 | INFO     | [WORKFLOW] Processing query | Length: 25 chars
```

#### File Format (Detailed)
```
2024-01-15 10:30:45.123 | INFO     | src.orchestrator.workflow:process_query:38 | [WORKFLOW] Processing query | Length: 25 chars | Query: Analyze AAPL...
```

**Format Components**:
- **Timestamp**: `YYYY-MM-DD HH:mm:ss.SSS` (millisecond precision in files)
- **Level**: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- **Location** (file only): `module:function:line`
- **Message**: Component prefix + structured message

#### Component Prefixes

Logs use structured prefixes for easy filtering:
- `[UI]` - UI component
- `[WORKFLOW]` - Workflow orchestrator
- `[GRAPH]` - LangGraph execution
- `[Research Agent]` - Research Agent
- `[Analyst Agent]` - Analyst Agent
- `[Reporting Agent]` - Reporting Agent
- `[MCP:YahooFinance]` - MCP clients (source name included)
- `[MCP:AlphaVantage]` - Alpha Vantage client
- `[MCP:FMP]` - Financial Modeling Prep client
- `[MCP:Unified]` - Unified MCP client wrapper
- `[VectorDB]` - Vector database operations

### Log Levels

- **DEBUG**: Detailed debugging information (function entry/exit, data values, internal state)
- **INFO**: General informational messages (component start/stop, major operations)
- **WARNING**: Warning messages (non-critical issues, fallbacks, degraded performance)
- **ERROR**: Error messages (critical issues, exceptions, failures)

### Reading Log Files

#### View Latest Logs

```bash
# View main log file (all components)
tail -f logs/myfingpt_$(date +%Y-%m-%d).log

# View error log file
tail -f logs/myfingpt_errors_$(date +%Y-%m-%d).log

# View specific component log
tail -f logs/workflow_$(date +%Y-%m-%d).log
tail -f logs/agents_$(date +%Y-%m-%d).log
tail -f logs/mcp_$(date +%Y-%m-%d).log
```

#### Search Log Files

```bash
# Search for specific component
grep "\[WORKFLOW\]" logs/myfingpt_*.log

# Search for errors
grep -i "ERROR" logs/myfingpt_*.log

# Search for specific symbol
grep "AAPL" logs/myfingpt_*.log

# Search with context (show 5 lines before/after)
grep -B 5 -A 5 "ERROR" logs/myfingpt_*.log

# Search across all log files (including compressed)
zgrep "ERROR" logs/*.log.gz
```

#### Filter by Time Range

```bash
# View logs from last hour
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" logs/myfingpt_$(date +%Y-%m-%d).log

# View logs from specific time
grep "2024-01-15 10:" logs/myfingpt_2024-01-15.log

# View logs between two times
awk '/2024-01-15 10:00:/,/2024-01-15 11:00:/' logs/myfingpt_2024-01-15.log
```

#### Extract Performance Metrics

```bash
# Extract execution times
grep "Time:" logs/myfingpt_*.log | grep -oP 'Time: \K[0-9.]+'

# Extract token usage
grep "tokens:" logs/myfingpt_*.log | grep -oP 'tokens: \K[0-9]+'

# Extract context sizes
grep "context_size" logs/myfingpt_*.log | grep -oP 'context_size: \K[0-9]+'

# Create performance summary
grep "Completed in" logs/agents_*.log | \
  awk '{print $NF}' | \
  sed 's/s$//' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count, "s"}'
```

### Relating Logs Across Components

#### Trace a Query Through the System

To trace a single query through all components:

1. **Find the query in UI logs**:
```bash
grep "User query received" logs/ui_*.log | grep "AAPL"
# Note the timestamp
```

2. **Find workflow processing**:
```bash
grep "Processing query" logs/workflow_*.log | grep -A 5 "AAPL"
```

3. **Find graph execution**:
```bash
grep "Starting workflow execution" logs/workflow_*.log | grep -A 10 "AAPL"
```

4. **Find agent execution**:
```bash
grep "Starting execution" logs/agents_*.log | grep -A 20 "AAPL"
```

5. **Find MCP API calls**:
```bash
grep "AAPL" logs/mcp_*.log
```

6. **Find vector DB operations**:
```bash
grep "AAPL" logs/vectordb_*.log
```

#### Create a Complete Trace Script

```bash
#!/bin/bash
# trace_query.sh - Trace a query through all log files

QUERY_TEXT="$1"
DATE=$(date +%Y-%m-%d)

echo "=== Tracing query: $QUERY_TEXT ==="
echo ""

echo "--- UI Logs ---"
grep "$QUERY_TEXT" logs/ui_${DATE}.log | head -5

echo ""
echo "--- Workflow Logs ---"
grep "$QUERY_TEXT" logs/workflow_${DATE}.log | head -10

echo ""
echo "--- Agent Logs ---"
grep "$QUERY_TEXT" logs/agents_${DATE}.log | head -20

echo ""
echo "--- MCP Logs ---"
grep "$QUERY_TEXT" logs/mcp_${DATE}.log | head -10

echo ""
echo "--- Vector DB Logs ---"
grep "$QUERY_TEXT" logs/vectordb_${DATE}.log | head -10
```

Usage: `./trace_query.sh "AAPL"`

### Understanding Log Messages

#### Message Structure

Log messages follow this structure:
```
[COMPONENT] Action | Key: Value | Key: Value | ...
```

**Example**:
```
[WORKFLOW] Processing query | Length: 25 chars | Query: Analyze AAPL... | Symbols: ['AAPL']
```

#### Common Message Patterns

**1. Component Initialization**:
```
[VectorDB] Initializing Chroma client | Path: ./chroma_db
[GRAPH] LangGraph workflow compiled successfully
```

**2. Operation Start**:
```
[WORKFLOW] Processing query | Length: XX chars
Research Agent: Starting execution
[MCP:YahooFinance] Fetching stock price for AAPL
```

**3. Operation Progress**:
```
Research Agent: Processing symbol 1/3: AAPL
Research Agent: Fetching stock price for AAPL
Research Agent: Stock price fetched for AAPL | Price: $150.25
```

**4. Operation Completion**:
```
Research Agent: Completed in 2.34s
[WORKFLOW] Query processing completed successfully | Total time: 15.67s | Total tokens: 1234
```

**5. Errors**:
```
[MCP:YahooFinance] Error fetching price for AAPL after 1.23s: Connection timeout
Research Agent: Error processing AAPL: Connection timeout
```

**6. Warnings**:
```
[MCP:Unified] yahoo failed for AAPL, trying fallback: Rate limit exceeded
Analyst Agent: No research data for INVALID, skipping
```

#### Performance Metrics in Logs

**Execution Time**:
- Format: `Completed in X.XXs`
- Found in: Agent completion messages
- Example: `Research Agent: Completed in 2.34s`

**Token Usage**:
- Format: `tokens: XXX` or `Total tokens: XXX`
- Found in: LLM call completion messages
- Example: `Research Agent: LLM call completed | Tokens: 150`

**Context Size**:
- Format: `context_size: XXXX bytes`
- Found in: State update messages
- Example: `[GRAPH] Initial context size: 1024 bytes`

**API Response Time**:
- Format: `Time: X.XXs`
- Found in: MCP client messages
- Example: `[MCP:YahooFinance] Stock price fetched for AAPL | Time: 0.45s`

### Analyzing Logs for Debugging

#### Find Error Patterns

```bash
# Count errors by component
grep "ERROR" logs/myfingpt_errors_*.log | \
  grep -oP '\[.*?\]' | \
  sort | uniq -c | sort -rn

# Find most common errors
grep "ERROR" logs/myfingpt_errors_*.log | \
  sed 's/.*ERROR.*| //' | \
  sort | uniq -c | sort -rn | head -10

# Find errors with stack traces
grep -A 20 "ERROR" logs/myfingpt_errors_*.log | less
```

#### Performance Analysis

```bash
# Find slow operations (>5 seconds)
grep "Completed in" logs/myfingpt_*.log | \
  awk -F'Completed in ' '{print $2}' | \
  sed 's/s$//' | \
  awk '$1 > 5 {print}'

# Find slow API calls
grep "Time:" logs/mcp_*.log | \
  awk -F'Time: ' '{print $2}' | \
  sed 's/s$//' | \
  awk '$1 > 2 {print}'

# Calculate average execution time per agent
for agent in "Research Agent" "Analyst Agent" "Reporting Agent"; do
  echo "$agent:"
  grep "$agent.*Completed in" logs/agents_*.log | \
    grep -oP 'Completed in \K[0-9.]+' | \
    awk '{sum+=$1; count++} END {if(count>0) print "Average:", sum/count, "s"}'
done
```

#### Token Usage Analysis

```bash
# Extract total tokens per query
grep "Total tokens:" logs/myfingpt_*.log | \
  grep -oP 'Total tokens: \K[0-9]+' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count, "tokens"}'

# Find high token usage queries
grep "Total tokens:" logs/myfingpt_*.log | \
  awk -F'Total tokens: ' '{if ($2 > 5000) print}'
```

#### Component Health Check

```bash
# Check for component failures
for component in "UI" "WORKFLOW" "Research Agent" "Analyst Agent" "Reporting Agent"; do
  echo "=== $component ==="
  grep "$component" logs/myfingpt_errors_*.log | tail -5
done

# Check API success rates
echo "=== MCP API Success Rate ==="
total=$(grep -c "Stock price fetched" logs/mcp_*.log)
failed=$(grep -c "Error fetching" logs/mcp_*.log)
if [ $total -gt 0 ]; then
  success_rate=$(echo "scale=2; ($total - $failed) * 100 / $total" | bc)
  echo "Success rate: ${success_rate}%"
fi
```

### Log Rotation and Management

#### Manual Log Rotation

Logs rotate automatically, but you can manually trigger rotation:

```bash
# Compress old logs
find logs/ -name "*.log" -mtime +1 -exec gzip {} \;

# Remove old compressed logs (older than 90 days)
find logs/ -name "*.log.gz" -mtime +90 -delete

# Clean up old logs
find logs/ -name "*.log" -mtime +30 -delete
```

#### Log File Sizes

```bash
# Check log file sizes
ls -lh logs/*.log

# Find largest log files
du -h logs/*.log | sort -rh | head -10

# Check total log directory size
du -sh logs/
```

### Enabling Debug Logging

```bash
# Set environment variable
export LOG_LEVEL=DEBUG
python main.py

# Or set custom log directory
export LOG_DIR=/path/to/custom/logs
export LOG_LEVEL=DEBUG
python main.py
```

### Expected Log Patterns

#### Successful Query Processing Flow

When a query is successfully processed, you should see this pattern in the logs:

**1. UI receives query** (`ui_*.log`):
```
[UI] User query received | Length: 25 chars | Query: Analyze AAPL...
```

**2. Workflow starts** (`workflow_*.log`):
```
[WORKFLOW] Processing query | Transaction ID: abc12345 | Length: 25 chars | Query: Analyze AAPL...
[WORKFLOW] Query intent detected: single_stock
[WORKFLOW] Extracted symbols: ['AAPL']
```

**3. Graph execution** (`workflow_*.log`):
```
[GRAPH] Starting workflow execution | Symbols: ['AAPL']
[GRAPH] Initial context size: 512 bytes
```

**4. Research Agent** (`agents_*.log`):
```
Research Agent: Starting execution | Transaction ID: abc12345
Research Agent: Processing symbol 1/1: AAPL
Research Agent: Fetching stock price for AAPL
[MCP:YahooFinance] Stock price fetched for AAPL | Price: $150.25 | Time: 0.45s
Research Agent: Stock price fetched for AAPL | Price: $150.25
Research Agent: Completed data collection for AAPL
Research Agent: Completed in 2.34s | Transaction ID: abc12345
```

**5. Analyst Agent** (`agents_*.log`):
```
Analyst Agent: Starting execution | Transaction ID: abc12345
Analyst Agent: Analyzing symbol 1/1: AAPL
Analyst Agent: LLM call completed | Transaction ID: abc12345 | Model: gpt-4 | Time: 3.45s | Tokens: 250
Analyst Agent: Completed analysis for AAPL
Analyst Agent: Completed in 4.12s | Transaction ID: abc12345
```

**6. Reporting Agent** (`agents_*.log`):
```
Reporting Agent: Starting execution | Transaction ID: abc12345
Reporting Agent: Generating report for 1 symbol(s)
Reporting Agent: LLM call completed | Transaction ID: abc12345 | Model: gpt-4 | Time: 5.67s | Tokens: 500
Reporting Agent: Report generation completed | Report length: 2500 chars
Reporting Agent: Completed in 6.23s | Transaction ID: abc12345
```

**7. Workflow completion** (`workflow_*.log`):
```
[GRAPH] Reporting Node completed
[WORKFLOW] Query processing completed successfully | Transaction ID: abc12345 | Total time: 15.67s | Total tokens: 1234
```

**8. UI completion** (`ui_*.log`):
```
[UI] Query processing completed successfully | Transaction ID: abc12345 | Total time: 15.67s | Charts: 1 | Citations: 5
```

#### Error Pattern

When an error occurs, you'll see:

```
[WORKFLOW] Processing query | Length: 25 chars
[MCP:YahooFinance] Error fetching price for AAPL after 1.23s: Connection timeout
[MCP:Unified] yahoo failed for AAPL, trying fallback: Connection timeout
[MCP:Unified] All sources failed to fetch price for AAPL after 2.45s
Research Agent: Error processing AAPL: All sources failed
[WORKFLOW] Error processing query after 3.67s: All sources failed
[UI] Error processing query after 3.67s: All sources failed
```

### Transaction ID Tracking

Every query is assigned a unique transaction ID (8-character hex string) that:
- Appears in all log entries related to that query
- Is displayed in the UI report header and Agent Activity tab
- Enables extraction of complete execution flow for debugging

**Using Transaction IDs**:
1. After submitting a query, note the transaction ID from the report header
2. Use the log extraction script to view complete flow:
   ```bash
   python scripts/extract_logs.py --transaction-id abc12345
   ```

### Log Analysis Tools

#### Using the Log Extraction Script

The log extraction script (`scripts/extract_logs.py`) provides transaction-based log analysis:

```bash
# List all transactions for today
python scripts/extract_logs.py --list

# View complete flow for a specific transaction
python scripts/extract_logs.py --transaction-id abc12345

# Include file names and line numbers
python scripts/extract_logs.py --transaction-id abc12345 --show-files

# View logs for a specific date
python scripts/extract_logs.py --transaction-id abc12345 --date 2024-01-15
```

#### Using the Log Analysis Script

A convenient script is provided to analyze logs:

```bash
# Analyze today's logs
./scripts/analyze_logs.sh

# Analyze specific date
./scripts/analyze_logs.sh 2024-01-15

# Use custom log directory
LOG_DIR=/path/to/logs ./scripts/analyze_logs.sh
```

The script provides:
- Summary statistics (total entries, errors, warnings)
- Component activity counts
- Recent errors
- Performance metrics (execution times, token usage)
- Query processing statistics
- MCP API performance
- Log file sizes

#### Using `less` for Interactive Viewing

```bash
# View log file with search
less logs/myfingpt_$(date +%Y-%m-%d).log

# In less:
# - Press '/' to search forward
# - Press '?' to search backward
# - Press 'n' for next match
# - Press 'N' for previous match
# - Press 'q' to quit
```

#### Using `jq` for JSON Logs (if structured logging added)

```bash
# If logs are in JSON format
cat logs/myfingpt_*.log | jq 'select(.level == "ERROR")'
cat logs/myfingpt_*.log | jq 'select(.component == "WORKFLOW")'
```

#### Creating Log Summaries

```bash
#!/bin/bash
# log_summary.sh - Create a summary of today's logs

DATE=$(date +%Y-%m-%d)
LOG_FILE="logs/myfingpt_${DATE}.log"

echo "=== Log Summary for ${DATE} ==="
echo ""

echo "Total log entries: $(wc -l < $LOG_FILE)"
echo "Errors: $(grep -c "ERROR" $LOG_FILE)"
echo "Warnings: $(grep -c "WARNING" $LOG_FILE)"
echo ""

echo "=== Component Activity ==="
for component in "UI" "WORKFLOW" "Research Agent" "Analyst Agent" "Reporting Agent"; do
  count=$(grep -c "$component" $LOG_FILE)
  echo "$component: $count entries"
done

echo ""
echo "=== Performance Metrics ==="
echo "Average execution time:"
grep "Completed in" $LOG_FILE | \
  grep -oP 'Completed in \K[0-9.]+' | \
  awk '{sum+=$1; count++} END {if(count>0) print sum/count "s"}'
```

### Best Practices

1. **Monitor Error Logs Regularly**: Check `myfingpt_errors_*.log` daily
2. **Set Up Alerts**: Monitor for ERROR level messages
3. **Archive Old Logs**: Keep compressed logs for historical analysis
4. **Use Component Logs**: Use component-specific logs for focused debugging
5. **Track Performance**: Regularly analyze execution times and token usage
6. **Correlate Events**: Use timestamps to trace queries across components

## Progress Tracking System

### Overview

MyFinGPT includes a comprehensive progress tracking system that provides real-time visibility into agent execution, task progress, and execution order.

### Progress Tracking Components

**ProgressTracker** (`src/utils/progress_tracker.py`):
- Centralized utility for creating and managing progress events
- Supports agent-level and task-level events
- Formats events for UI display
- Tracks execution order and current agent status

**Progress Events**:
- Stored in `AgentState.progress_events`
- Include timestamps, agent names, event types, messages, and status
- Support both sequential and parallel execution tracking

**UI Progress Display** (`src/ui/progress_display.py`):
- Progress panel showing current agent and active tasks
- Progress events log
- Execution timeline visualization
- Real-time updates via streaming

### Using Progress Tracking

**In Agents**:
```python
from .base_agent import BaseAgent

class MyAgent(BaseAgent):
    def execute(self, state):
        # Report agent start (automatically called in run())
        # state = self.report_agent_start(state)
        
        # Start a task
        state = self.start_task(state, "Fetch data", symbol="AAPL")
        
        # Do work...
        data = fetch_data()
        
        # Complete task
        state = self.complete_task(state, "Fetch data", symbol="AAPL")
        
        # Report custom progress
        state = self.report_progress(
            state,
            event_type="task_progress",
            message="Processing data...",
            task_name="Process data"
        )
        
        # Report agent complete (automatically called in run())
        # state = self.report_agent_complete(state, execution_time)
        
        return state
```

**In Workflow**:
```python
# Streaming with progress updates
for update in workflow.stream_query(query):
    progress_events = update.get("progress_events", [])
    current_agent = update.get("current_agent")
    current_tasks = update.get("current_tasks", {})
    execution_order = update.get("execution_order", [])
    
    # Update UI with progress information
    update_progress_display(progress_events, current_agent, current_tasks, execution_order)
```

**Event Types**:
- `agent_start`: Agent execution started
- `agent_complete`: Agent execution completed
- `task_start`: Task started
- `task_complete`: Task completed
- `task_progress`: Task progress update

**Status Values**:
- `running`: Currently executing
- `completed`: Successfully completed
- `failed`: Execution failed
- `pending`: Waiting to start

### Progress Display in UI

The UI includes a progress panel that displays:
- **Current Agent**: Currently executing agent name
- **Active Tasks**: List of active tasks for current agent
- **Progress Events**: Chronological log of progress events
- **Execution Timeline**: Visual timeline chart showing agent execution order and duration

### Testing Progress Tracking

```python
# Test progress tracker
from src.utils.progress_tracker import ProgressTracker

event = ProgressTracker.create_agent_start_event("Research Agent", execution_order=0)
print(ProgressTracker.format_event_for_ui(event))

# Test progress in agent
from src.agents.research_agent import ResearchAgent
from src.orchestrator.state import StateManager

agent = ResearchAgent()
state = StateManager.create_initial_state("Analyze AAPL")
state = agent.run(state)

# Check progress events
progress_events = state.get("progress_events", [])
print(f"Total progress events: {len(progress_events)}")
for event in progress_events:
    print(f"- {event.get('message')}")
```

### Debugging Progress Tracking

- Check `progress_events` in state after agent execution
- Verify events are being created with correct event types
- Check UI updates are receiving progress events
- Monitor execution_order for timing information
- Use transaction_id to filter progress events for specific queries

## Additional Resources

- Architecture documentation: `docs/architecture.md`
- Design documentation: `docs/design.md`
- Requirements: `docs/requirements.md`
- Main README: `README.md`
- Progress Tracking Enhancement: `docs/enhancement_progress_tracking.md`

## Getting Help

If you encounter issues not covered in this guide:

1. Check the logs for error messages
2. Review the troubleshooting section
3. Verify all components are properly configured
4. Test individual components using the provided commands
5. Check API keys and quotas
6. Review the main README for general troubleshooting


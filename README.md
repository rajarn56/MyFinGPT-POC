# MyFinGPT - Multi-Agent Financial Analysis System

MyFinGPT is a proof-of-concept multi-agent financial analysis system that demonstrates advanced AI agent implementation patterns including multi-agent orchestration, MCP server integration, context sharing, vector databases, and grounded responses with citations.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Starting Components](#starting-components)
- [Stopping Components](#stopping-components)
- [Restarting Components](#restarting-components)
- [Usage Guide](#usage-guide)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## Features

- **Multi-Agent Orchestration**: Sequential and parallel agent execution
- **MCP Server Integration**: Yahoo Finance, Alpha Vantage, Financial Modeling Prep
- **Context Sharing**: Agents share context through LangGraph state management
- **Vector Database**: Chroma for semantic search and historical pattern matching
- **Grounded Responses**: All responses include citations and source references
- **Token Tracking**: Track token usage per agent and per call
- **Interactive UI**: Gradio-based web interface with visualizations
- **Comprehensive Guardrails**: Input validation, domain enforcement, security checks, and output validation to ensure system stays within intended scope

## Prerequisites

### System Requirements

- Python 3.12.x (required)
- uv package manager (for virtual environment management)
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection for API calls

### Required API Keys

**At least one LLM provider API key is required**:
- OpenAI API key (for GPT-4/GPT-3.5-turbo)
- Google Gemini API key (for gemini-pro)
- Anthropic API key (for Claude) - Optional
- Ollama (for local models) - Optional, requires Ollama installation

**Optional API keys** (for enhanced data):
- Alpha Vantage API key (free tier available)
- Financial Modeling Prep API key (free tier available)

**Note**: Yahoo Finance integration works without API keys (uses yfinance library).

## Installation & Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd project1
```

### Step 2: Install uv Package Manager

If you don't have `uv` installed, install it using one of the following methods:

**macOS/Linux (using curl):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**macOS (using Homebrew):**
```bash
brew install uv
```

**Windows (using PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Using pip (if you have Python already):**
```bash
pip install uv
```

**Verify installation:**
```bash
uv --version
```

### Step 3: Create Python 3.12.x Virtual Environment

Create a virtual environment using `uv` with Python 3.12.x. The virtual environment will be created in the `.venv` directory and can be used by all components.

```bash
# Create virtual environment with Python 3.12.x
# uv will automatically download Python 3.12.x if not already installed
uv venv --python 3.12

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

**Note**: If you have Python 3.12.x installed locally, `uv` will use it. Otherwise, `uv` will automatically download and manage Python 3.12.x for you.

**Verify Python version:**
```bash
python --version
# Should output: Python 3.12.x
```

### Step 4: Install Dependencies

Install all project dependencies using `uv`:

```bash
# Install dependencies from requirements.txt
uv pip install -r requirements.txt
```

**Alternative**: You can also use `uv` to sync dependencies (recommended for development):
```bash
# Sync dependencies (installs/updates/removes packages as needed)
uv pip sync requirements.txt
```

**Verify installation:**
```bash
python -c "import gradio; import langgraph; import chromadb; print('All dependencies installed')"
```

### Step 5: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```bash
# Required: At least one LLM provider
OPENAI_API_KEY=your_openai_api_key_here
# OR
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: For enhanced data sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
FMP_API_KEY=your_fmp_api_key_here

# Optional: For local models
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Step 6: Initialize Vector Database

The vector database will be automatically initialized on first run. The database will be created in `./chroma_db` directory.

To manually verify:
```bash
python -c "from src.vector_db.chroma_client import ChromaClient; c = ChromaClient(); print('Vector DB initialized')"
```

### Step 7: Verify MCP Server Connections

Test MCP server connections:
```bash
python -c "from src.mcp.mcp_client import UnifiedMCPClient; c = UnifiedMCPClient(); print('MCP clients initialized')"
```

## Configuration

### LLM Provider Configuration

MyFinGPT supports multiple LLM providers including **LM Studio** for local models. Configure providers in `config/llm_templates.yaml`:

```yaml
openai:
  model: "gpt-4"  # or "gpt-3.5-turbo"
  api_key: "${OPENAI_API_KEY}"
  temperature: 0.7

gemini:
  model: "gemini-pro"
  api_key: "${GEMINI_API_KEY}"
  temperature: 0.7

lmstudio:
  model: "${LM_STUDIO_MODEL:-local-model}"
  api_base: "${LM_STUDIO_API_BASE:-http://localhost:1234/v1}"
  temperature: 0.7
  max_tokens: 4000
```

**Selecting LLM Provider**:

1. **Via Environment Variable**:
```bash
export LITELLM_PROVIDER=lmstudio  # or openai, gemini, anthropic, ollama
python main.py
```

2. **Via Command Line**:
```bash
python main.py --llm-provider lmstudio
```

3. **Via Config File**:
Edit `config/llm_templates.yaml` and set the default provider:
```yaml
default:
  provider: "lmstudio"  # or openai, gemini, etc.
```

**LM Studio Setup**:
1. Install LM Studio from https://lmstudio.ai/
2. Load a model in LM Studio
3. Start local server (default port 1234)
4. Set environment variables:
```bash
export LM_STUDIO_API_BASE=http://localhost:1234/v1
export LM_STUDIO_MODEL=your-model-name
export LITELLM_PROVIDER=lmstudio
```

### Embedding Model Configuration

MyFinGPT uses embeddings for semantic search in the vector database. You can configure a separate embedding provider/model from your LLM provider.

**Configuration Options**:

1. **Via Environment Variables** (recommended):
```bash
# Use a different provider for embeddings
export EMBEDDING_PROVIDER=lmstudio

# Specify the embedding model name (for LMStudio, this is your embedding model name)
export EMBEDDING_MODEL=your-embedding-model-name
```

2. **Via Config File** (`config/llm_templates.yaml`):
```yaml
lmstudio:
  model: "${LM_STUDIO_MODEL:-local-model}"
  api_base: "${LM_STUDIO_API_BASE:-http://localhost:1234/v1}"
  embedding_model: "${LM_STUDIO_EMBEDDING_MODEL:-text-embedding-ada-002}"  # Your LMStudio embedding model
  temperature: 0.7
  max_tokens: 10000
```

**How It Works**:
- If `EMBEDDING_PROVIDER` is set, it uses that provider for embeddings (can be different from LLM provider)
- If `EMBEDDING_MODEL` is set, it uses that specific model name
- For LMStudio: The code will try to use your LMStudio embedding model first, then fall back to OpenAI embeddings if needed
- Model name priority: `EMBEDDING_MODEL` env var > config `embedding_model` > config `model` > default

**Example: Using LMStudio for LLM, OpenAI for Embeddings**:
```bash
export LITELLM_PROVIDER=lmstudio
export EMBEDDING_PROVIDER=openai
export OPENAI_API_KEY=your-openai-key
```

**Example: Using LMStudio for Both LLM and Embeddings**:
```bash
export LITELLM_PROVIDER=lmstudio
export EMBEDDING_PROVIDER=lmstudio
export EMBEDDING_MODEL=your-lmstudio-embedding-model-name
export LM_STUDIO_API_BASE=http://localhost:1234/v1
```

### Integration Configuration

Control which data source integrations are enabled/disabled:

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

**Via Environment Variables**:
```bash
# Disable specific integrations
export ENABLE_FMP=false
export ENABLE_ALPHA_VANTAGE=true
export ENABLE_YAHOO_FINANCE=true

# Start application
python main.py
```

**Via Command Line**:
```bash
# Disable FMP integration
python main.py --disable-integrations fmp

# Enable only Yahoo Finance
python main.py --enable-integrations yahoo_finance --disable-integrations fmp,alpha_vantage

# Use OpenAI and disable Alpha Vantage
python main.py --llm-provider openai --disable-integrations alpha_vantage
```

**Integration Behavior**:
- **Disabled integrations** are skipped automatically (no API calls made)
- **Prompts are dynamically generated** to only mention enabled integrations
- **API optimization** uses preferred sources per data type:
  - Stock price: Yahoo Finance (preferred) → Alpha Vantage → FMP
  - Financial statements: FMP (preferred) → Yahoo Finance
  - Technical indicators: Alpha Vantage only
  - News: Yahoo Finance → FMP
  - Historical data: Yahoo Finance only
- **Stops after first success** to avoid redundant API calls
- **Progress tracking** shows integration status (✓ success, ✗ failed, ⊘ skipped)

### API Call Optimization

The system automatically optimizes API calls:

- **Smart Source Selection**: Uses preferred integration per data type
- **Stop After Success**: Stops trying other sources once data is retrieved
- **Parallel Execution Preserved**: Optimization happens within each parallel task
- **Status Tracking**: Progress events show API call success/skip/failed status

**Example**: When fetching stock price:
1. Tries Yahoo Finance first (preferred)
2. If successful, stops (doesn't try Alpha Vantage or FMP)
3. Only tries fallback sources if preferred source fails

### Agent Configuration

Edit `config/agent_config.yaml` to configure agent behavior:

```yaml
agents:
  research:
    max_parallel_tasks: 5
    timeout_seconds: 60

context:
  max_size_bytes: 1000000  # 1MB max context size
  enable_pruning: true
```

## Starting Components

**Important**: Before starting any components, ensure your virtual environment is activated:

```bash
# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Verify activation (you should see (.venv) in your prompt)
python --version  # Should show Python 3.12.x
```

### Starting Vector Database (Chroma)

The vector database starts automatically when the application runs. No separate startup needed.

**Manual verification**:
```bash
python -c "from src.vector_db.chroma_client import ChromaClient; c = ChromaClient(); print(c.get_collection_stats('financial_news'))"
```

### Starting MCP Servers

MCP clients are initialized automatically. No separate servers needed (they use REST APIs).

**Note**: If using Ollama for local models, start Ollama first:
```bash
# Install Ollama from https://ollama.ai
ollama serve
```

### Starting LiteLLM Proxy (Optional)

LiteLLM proxy is not required for basic usage. Agents use LiteLLM directly.

If you want to use LiteLLM proxy for advanced features:
```bash
litellm --config config/llm_templates.yaml
```

### Starting Gradio UI Application

**Basic startup**:
```bash
python main.py
```

**With options**:
```bash
python main.py --llm-provider openai --port 7860 --host 0.0.0.0
```

**Command-Line Options**:
- `--llm-provider`: LLM provider (openai, gemini, ollama, anthropic, lmstudio)
- `--enable-integrations`: Comma-separated list of integrations to enable (yahoo_finance, alpha_vantage, fmp)
- `--disable-integrations`: Comma-separated list of integrations to disable
- `--port`: Server port (default: 7860)
- `--host`: Server host (default: 0.0.0.0)
- `--share`: Create public Gradio link

**Examples**:
```bash
# Use LM Studio with only Yahoo Finance enabled
python main.py --llm-provider lmstudio --enable-integrations yahoo_finance --disable-integrations fmp,alpha_vantage

# Use OpenAI, disable FMP
python main.py --llm-provider openai --disable-integrations fmp

# Use default provider, custom port
python main.py --port 8080
```

**Access the UI**:
- Local: http://localhost:7860
- Network: http://<your-ip>:7860

### Starting All Components Together

All components start together when you run:
```bash
python main.py
```

The startup sequence:
1. Load configuration
2. Initialize vector database
3. Initialize MCP clients
4. Initialize agents
5. Start Gradio UI

## Stopping Components

### Stopping Gradio UI Application

**In terminal**: Press `Ctrl+C` to stop the server gracefully.

**Programmatic stop**: The UI will stop when the Python process terminates.

### Stopping LiteLLM Proxy

If running LiteLLM proxy separately:
```bash
# Find process
ps aux | grep litellm

# Kill process
kill <process_id>
```

### Stopping MCP Servers

MCP clients don't run as separate servers. They're just API clients that stop when the main application stops.

**Note**: If using Ollama:
```bash
# Stop Ollama
pkill ollama
```

### Stopping Vector Database

The vector database is file-based and doesn't run as a service. It closes automatically when the application stops.

**To clear database**:
```bash
rm -rf chroma_db/
```

### Graceful Shutdown Procedures

1. Stop accepting new queries (UI handles this automatically)
2. Complete current queries
3. Save any pending data to vector DB
4. Close database connections
5. Exit application

The application handles graceful shutdown automatically on `Ctrl+C`.

## Restarting Components

**Important**: Ensure your virtual environment is activated before restarting:

```bash
# Activate virtual environment if not already activated
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Restarting Individual Components

**Restart UI only**:
```bash
# Stop current instance (Ctrl+C)
# Start again (ensure venv is activated)
python main.py
```
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
read_file

**Restart Vector DB** (clear and reinitialize):
```bash
rm -rf chroma_db/
python -c "from src.vector_db.chroma_client import ChromaClient; c = ChromaClient()"
```

**Restart with different LLM provider**:
```bash
python main.py --provider gemini
```

### Restarting All Components

Simply restart the main application:
```bash
# Stop
Ctrl+C

# Start
python main.py
```

### Troubleshooting Restart Issues

**Port already in use**:
```bash
# Find process using port 7860
lsof -i :7860

# Kill process
kill <process_id>

# Or use different port
python main.py --port 7861
```

**Vector DB locked**:
```bash
# Check for running processes
ps aux | grep python

# Kill any hanging processes
kill <process_id>

# Clear lock (if safe)
rm -rf chroma_db/.lock
```

**API key issues**:
```bash
# Verify .env file
cat .env

# Test API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY')[:10] + '...')"
```

### Verifying Component Health

**Check vector DB**:
```bash
python -c "from src.vector_db.chroma_client import ChromaClient; c = ChromaClient(); print('Collections:', list(c.collections.keys()))"
```

**Check MCP clients**:
```bash
python -c "from src.mcp.mcp_client import UnifiedMCPClient; c = UnifiedMCPClient(); print('MCP clients ready')"
```

**Check LLM configuration**:
```bash
python -c "from src.utils.llm_config import llm_config; print('Providers:', llm_config.list_available_providers())"
```

## Usage Guide

### Running the Application

**Before starting**: Ensure your virtual environment is activated:

```bash
# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate  # On Windows
```

1. **Start the application**:
```bash
python main.py
```

2. **Open browser** to http://localhost:7860

3. **Enter a query** in the text box, for example:
   - "Analyze Apple Inc. (AAPL) stock"
   - "Compare AAPL, MSFT, and GOOGL"
   - "What are the current trends in tech stocks?"

4. **Click "Submit Query"** and wait for results

5. **View results** in three tabs (right column):
   - **Analysis & Report**: Comprehensive report with citations (scrollable, ~600px height)
   - **Visualizations**: Interactive charts (scrollable, ~600px height)
   - **Agent Activity**: Execution metrics and token usage (scrollable, ~600px height)

6. **Monitor progress** in left column:
   - Current agent status and active tasks
   - Execution timeline visualization
   - Progress events (recent events)
   - Progress events log (all events)

### Example Queries

**Single Stock Analysis**:
```
Analyze Tesla (TSLA) stock including current price, financial health, recent news sentiment, and investment recommendation.
```

**Stock Comparison**:
```
Compare Apple (AAPL), Microsoft (MSFT), and Google (GOOGL) across key metrics including P/E ratio, revenue growth, market cap, and recent performance.
```

**Trend Analysis**:
```
Analyze the 6-month price trend of Amazon (AMZN) and identify any patterns, support/resistance levels, and predict potential future movements.
```

**Sentiment Analysis**:
```
Analyze how recent news and market sentiment have affected NVIDIA (NVDA) stock price. Include sentiment analysis of the last 10 news articles.
```

### Understanding Results

**Analysis & Report Tab**:
- Executive summary
- Detailed financial analysis
- Market sentiment analysis
- Investment recommendations
- Sources and citations

**Trends & Visualizations Tab**:
- Price trend charts
- Comparison charts (for multi-stock queries)
- Sentiment analysis charts

**Agent Activity Tab**:
- Agents executed and their order
- Token usage per agent
- Execution time per agent
- Context size metrics

### UI Layout

The UI uses a horizontal split-screen layout (50/50) for single-screen visibility:

**Left Column (50%)**:
- **Query Input**: Enter your financial query (~100px height)
- **Example Queries Dropdown**: Select from pre-defined examples
- **Submit/Clear Buttons**: Process your query or clear inputs
- **Execution Progress**: Current agent status and active tasks (~100px total)
- **Execution Timeline**: Visual timeline chart (~200px height)
- **Progress Events**: Recent progress events (~200px height, scrollable)
- **Progress Events Log**: Complete progress log (~200px height, scrollable)

**Right Column (50%)**:
- **Tabs**: Switch between Analysis & Report, Visualizations, and Agent Activity
- All tab content is scrollable with ~600px height
- All tabs visible and clickable simultaneously

### UI Navigation

- **Query Input** (left column): Enter your financial query
- **Example Queries Dropdown** (left column): Select from pre-defined examples
- **Submit Query** (left column): Process your query
- **Clear** (left column): Clear the input and results
- **Progress Panels** (left column): Monitor real-time execution progress
- **Tabs** (right column): Switch between Analysis & Report, Visualizations, and Agent Activity

## Development

### Development Setup

1. **Clone and setup** (see Installation section)

2. **Install development dependencies**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Install development dependencies using uv
uv pip install pytest pytest-cov black flake8
```

3. **Run tests** (when tests are added):
```bash
pytest tests/
```

4. **Code formatting**:
```bash
black src/
```

5. **Linting**:
```bash
flake8 src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_agents.py
```

### Code Structure

```
project1/
├── src/
│   ├── agents/          # Agent implementations
│   ├── mcp/            # MCP client integrations
│   ├── orchestrator/   # LangGraph orchestration
│   ├── vector_db/      # Vector database integration
│   ├── utils/          # Utility modules
│   └── ui/             # Gradio UI components
├── config/             # Configuration files
├── tests/              # Test files
├── docs/               # Documentation
└── main.py             # Entry point
```

### Contributing Guidelines

1. Follow PEP 8 style guide
2. Add docstrings to all functions and classes
3. Write tests for new features
4. Update documentation as needed
5. Use type hints where possible

## Guardrails and Security

MyFinGPT includes comprehensive guardrails to ensure the system operates safely and within its intended scope.

### Guardrails Features

**Query Validation**:
- Ensures queries are financial domain-related
- Validates query length and format
- Prevents non-financial domain queries
- Detects and blocks dangerous patterns (injection attacks)

**Input Sanitization**:
- Removes XSS, SQL injection, and code execution patterns
- Sanitizes user inputs before processing
- Prevents malicious content from entering the system

**Symbol Validation**:
- Validates stock symbol format (1-5 uppercase letters)
- Prevents invalid symbols from being processed
- Limits number of symbols per query (max 20)
- Filters out common words that match symbol patterns

**Data Source Validation**:
- Only allows access to approved financial data sources
- Prevents unauthorized API access
- Validates data source names before use

**Output Validation**:
- Ensures agent outputs are financial domain-related
- Validates output length and content
- Prevents non-financial content in reports
- Validates final reports before returning to users

**State Validation**:
- Validates state structure before and after agent execution
- Ensures state integrity throughout workflow
- Prevents state corruption

### Guardrails Error Messages

If a query fails guardrails validation, you'll receive a clear error message explaining:
- What validation failed
- Why it failed
- How to fix the query

**Example Error Messages**:
- "Query does not appear to be financial domain-related. Please ask about stocks, companies, or financial analysis."
- "Invalid symbol: Symbol format invalid: INVALID123 (must be 1-5 uppercase letters)"
- "Query contains potentially dangerous patterns"

### Security Best Practices

1. **API Keys**: Store API keys in `.env` file, never commit to version control
2. **Input Validation**: All inputs are validated and sanitized automatically
3. **Domain Enforcement**: System only processes financial domain queries
4. **Error Handling**: Errors don't expose sensitive information
5. **Rate Limiting**: Built-in rate limit handling for API calls

### Guardrails Configuration

Guardrails are enabled by default and cannot be disabled. This ensures the system always operates safely and within its intended scope.

For more details on guardrails implementation, see:
- `docs/architecture.md` - Guardrails architecture
- `docs/design.md` - Guardrails design details
- `src/utils/guardrails.py` - Guardrails implementation

## Troubleshooting

### Common Issues

#### Issue: "uv: command not found"

**Solution**:
1. Install `uv` using one of the methods in Step 2 of Installation & Setup
2. Verify installation: `uv --version`
3. Ensure `uv` is in your PATH (may require restarting terminal)

#### Issue: "Python 3.12.x not found" or "Failed to create virtual environment"

**Solution**:
1. `uv` will automatically download Python 3.12.x if not installed locally
2. Ensure you have internet connection for the first setup
3. Check available Python versions: `uv python list`
4. Manually specify Python version: `uv venv --python 3.12.0`
5. If issues persist, install Python 3.12.x manually and point `uv` to it

#### Issue: "Module not found" or "Import errors" after installation

**Solution**:
1. Ensure virtual environment is activated:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate  # On Windows
   ```
2. Verify activation: `which python` should point to `.venv/bin/python`
3. Reinstall dependencies: `uv pip install -r requirements.txt`
4. Check Python version: `python --version` should show 3.12.x

#### Issue: "Virtual environment not activated" when running commands

**Solution**:
1. Always activate the virtual environment before running `python main.py`:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate  # On Windows
   ```
2. Add activation to your shell profile (`.bashrc`, `.zshrc`, etc.) for convenience
3. Verify activation: Your prompt should show `(.venv)` prefix

#### Issue: "API key not found"

**Solution**:
1. Check `.env` file exists and has correct API keys
2. Verify environment variables are loaded:
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```
3. Ensure `.env` file is in project root

#### Issue: "Rate limit exceeded"

**Solution**:
- The system automatically handles rate limits with exponential backoff
- For Alpha Vantage: Free tier allows 5 calls/minute (12-second delay)
- Wait a few minutes and try again
- Consider upgrading API tier if needed

#### Issue: "Vector DB error"

**Solution**:
1. Check disk space: `df -h`
2. Check permissions on `chroma_db/` directory
3. Clear and reinitialize:
```bash
rm -rf chroma_db/
python -c "from src.vector_db.chroma_client import ChromaClient; c = ChromaClient()"
```

#### Issue: "No data returned for symbol"

**Solution**:
- Verify symbol is correct (e.g., AAPL not APPL)
- Check internet connection
- Try a different symbol to test
- Check API key validity (for Alpha Vantage/FMP)

#### Issue: "LLM call failed"

**Solution**:
1. Verify LLM API key is valid
2. Check API quota/credits
3. Try a different LLM provider
4. Check network connectivity
5. Review error logs for details

#### Issue: "Query validation failed"

**Solution**:
1. Ensure your query is financial domain-related (stocks, companies, markets)
2. Include stock symbols (e.g., AAPL, MSFT) or financial keywords
3. Check query length (max 2000 characters)
4. Remove any special characters or patterns that might trigger security checks
5. Review the error message for specific guidance

**Example Valid Queries**:
- "Analyze Apple Inc. (AAPL) stock"
- "Compare AAPL, MSFT, and GOOGL"
- "What are the current trends in tech stocks?"

**Example Invalid Queries**:
- "Tell me about the weather" (not financial)
- "How do I hack this system?" (non-financial domain)
- "Analyze INVALID123 stock" (invalid symbol)

#### Issue: "Port already in use"

**Solution**:
```bash
# Find process using port
lsof -i :7860

# Kill process
kill <process_id>

# Or use different port
python main.py --port 7861
```

### Error Messages

**"Missing required context fields"**:
- This means a previous agent didn't complete successfully
- Check agent logs for errors
- Verify API keys are working
- Try a simpler query

**"Token limit exceeded"**:
- Reduce query complexity
- Use a model with higher token limit
- Enable context pruning in config

**"Vector DB query failed"**:
- Vector DB may be empty (first run)
- This is not critical - analysis will continue without historical context
- Vector DB will populate as you use the system

### Debugging Tips

1. **Enable verbose logging**:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

2. **Use Transaction IDs for Debugging**:
   - Each query is assigned a unique transaction ID (8-character identifier)
   - Transaction ID is displayed in the UI report header and Agent Activity tab
   - Use the transaction ID to extract and view all logs related to a specific query

3. **Extract Logs by Transaction ID**:
```bash
# List all transactions
python scripts/extract_logs.py --list

# View complete flow for a specific transaction
python scripts/extract_logs.py --transaction-id abc12345

# View flow with file names and line numbers
python scripts/extract_logs.py --transaction-id abc12345 --show-files

# View logs for a specific date
python scripts/extract_logs.py --transaction-id abc12345 --date 2024-01-15
```

4. **Test individual components**:
```python
# Test MCP client
from src.mcp.mcp_client import UnifiedMCPClient
c = UnifiedMCPClient()
print(c.get_stock_price("AAPL"))

# Test vector DB
from src.vector_db.chroma_client import ChromaClient
v = ChromaClient()
print(v.get_collection_stats("financial_news"))

# Test LLM
from src.utils.llm_config import llm_config
print(llm_config.get_provider_config("openai"))
```

5. **Check logs**: Logs are printed to console. Look for ERROR or WARNING messages.

6. **Verify configuration**:
```bash
python -c "from src.utils.llm_config import llm_config; import yaml; print(yaml.dump(llm_config.config))"
```

### Log Analysis and Debugging

MyFinGPT includes comprehensive logging and transaction tracking to help with debugging:

**Transaction IDs**:
- Every user query is assigned a unique transaction ID (8-character hex string)
- Transaction IDs are displayed in:
  - The report header in the UI
  - The Agent Activity tab
  - All log entries throughout the system

**Log Extraction Script**:
The `scripts/extract_logs.py` script helps you:
- List all transactions for a given date
- Extract and display the complete execution flow for a specific transaction
- View logs grouped by component (UI, Workflow, Agents, MCP, VectorDB)
- See chronological flow of execution across all components

**Example Usage**:
```bash
# See all transactions from today
python scripts/extract_logs.py --list

# View detailed flow for a transaction
python scripts/extract_logs.py --transaction-id abc12345

# Include file names for detailed debugging
python scripts/extract_logs.py --transaction-id abc12345 --show-files
```

**Log Files**:
Logs are stored in `./logs/` directory with the following structure:
- `myfingpt_YYYY-MM-DD.log` - Main log file (all logs)
- `workflow_YYYY-MM-DD.log` - Workflow-specific logs
- `agents_YYYY-MM-DD.log` - Agent execution logs
- `mcp_YYYY-MM-DD.log` - MCP client logs
- `vectordb_YYYY-MM-DD.log` - Vector database logs
- `ui_YYYY-MM-DD.log` - UI interaction logs
- `myfingpt_errors_YYYY-MM-DD.log` - Error logs only

### Getting Help

1. Check the documentation in `docs/` directory
2. Review error messages and logs
3. Verify all prerequisites are met
4. Check API key validity and quotas
5. Test with simple queries first

## License

This is a proof-of-concept project for educational purposes.

## Acknowledgments

- LangChain and LangGraph for agent orchestration
- LiteLLM for multi-provider LLM support
- Chroma for vector database
- Gradio for UI framework
- Yahoo Finance, Alpha Vantage, and FMP for financial data APIs


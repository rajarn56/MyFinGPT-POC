# Connectivity Test Scripts

This directory contains individual Python scripts to test connectivity of all integrations with APIs and libraries used in MyFinGPT POC.

## Overview

Each script tests a specific integration and can be run independently. All scripts are designed to:
- Use the same Python virtual environment as the POC (`.venv`)
- Load configuration from `.env` file in project root (same as POC)
- Check if required libraries are installed
- Verify API keys are set in `.env` file (where applicable)
- Test actual connectivity to the service
- Provide clear success/failure feedback

## Available Test Scripts

### API Integration Tests

1. **test_yahoo_finance.py** - Tests Yahoo Finance connectivity via `yfinance` library
   - No API key required
   - Tests: stock price, company info, historical data

2. **test_alpha_vantage.py** - Tests Alpha Vantage API connectivity
   - Requires: `ALPHA_VANTAGE_API_KEY` environment variable
   - Tests: GLOBAL_QUOTE and OVERVIEW endpoints
   - Get API key: https://www.alphavantage.co/support/#api-key

3. **test_fmp.py** - Tests Financial Modeling Prep API connectivity
   - Requires: `FMP_API_KEY` environment variable
   - Tests: quote and profile endpoints
   - Get API key: https://site.financialmodelingprep.com/developer/docs/

### Database Tests

4. **test_chroma.py** - Tests Chroma vector database connectivity
   - No API key required
   - Tests: client initialization, collection creation, document operations
   - Uses: `CHROMA_DB_PATH` environment variable (default: `./chroma_db`)

### LLM Provider Tests (via LiteLLM)

5. **test_litellm_openai.py** - Tests OpenAI connectivity via LiteLLM
   - Requires: `OPENAI_API_KEY` environment variable
   - Tests: chat completion and embeddings
   - Get API key: https://platform.openai.com/api-keys

6. **test_litellm_gemini.py** - Tests Google Gemini connectivity via LiteLLM
   - Requires: `GEMINI_API_KEY` environment variable
   - Tests: chat completion
   - Get API key: https://makersuite.google.com/app/apikey

7. **test_litellm_anthropic.py** - Tests Anthropic Claude connectivity via LiteLLM
   - Requires: `ANTHROPIC_API_KEY` environment variable
   - Tests: chat completion
   - Get API key: https://console.anthropic.com/

8. **test_litellm_ollama.py** - Tests Ollama (local LLM) connectivity via LiteLLM
   - Requires: Ollama running locally
   - Uses: `OLLAMA_API_BASE` environment variable (default: `http://localhost:11434`)
   - Tests: server availability and chat completion
   - Install: https://ollama.ai/

### Library Tests

9. **test_langgraph.py** - Tests LangGraph library import and basic functionality
   - No API key required
   - Tests: library import, StateGraph creation, graph execution

## Usage

### Prerequisites

**Important**: Before running any test scripts, ensure:

1. **Virtual environment is activated** (same as POC):
   ```bash
   # Activate virtual environment
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate     # On Windows
   ```

2. **`.env` file exists** in project root with required API keys:
   ```bash
   # Ensure .env file exists at project root
   ls .env  # Should show the file
   ```

### Running Individual Tests

Each script can be run independently (with virtual environment activated):

```bash
# Ensure virtual environment is activated first
source .venv/bin/activate  # On macOS/Linux

# Test Yahoo Finance
python scripts/test_yahoo_finance.py

# Test Alpha Vantage (requires API key in .env)
python scripts/test_alpha_vantage.py

# Test Chroma database
python scripts/test_chroma.py

# Test OpenAI via LiteLLM (requires API key in .env)
python scripts/test_litellm_openai.py
```

### Running All Tests

Use the master script to run all connectivity tests:

```bash
# Ensure virtual environment is activated first
source .venv/bin/activate  # On macOS/Linux

# Run all tests
python scripts/test_all_connectivity.py
```

This will execute all test scripts and provide a summary of results.

### Making Scripts Executable

All scripts are executable and can be run directly (with virtual environment activated):

```bash
# Ensure virtual environment is activated first
source .venv/bin/activate  # On macOS/Linux

# Scripts are already executable, run directly
./scripts/test_yahoo_finance.py
./scripts/test_alpha_vantage.py
```

## Configuration

### Environment Variables (.env file)

All scripts use the same `.env` file as the POC, located in the project root. Create or update `.env` file with the following variables (as needed):

```bash
# Required: At least one LLM provider
OPENAI_API_KEY=your_openai_key
# OR
GEMINI_API_KEY=your_gemini_key
# OR
ANTHROPIC_API_KEY=your_anthropic_key

# Optional: For enhanced data sources
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FMP_API_KEY=your_fmp_key

# Optional: For local models
OLLAMA_API_BASE=http://localhost:11434

# Optional: Vector Database path
CHROMA_DB_PATH=./chroma_db
```

**Note**: Scripts automatically load `.env` from the project root, same as the POC. No need to set environment variables separately.

### Virtual Environment

Scripts use the same Python virtual environment as the POC (`.venv`). Always activate it before running:

```bash
# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate     # On Windows

# Verify activation (should show (.venv) in prompt)
which python  # Should point to .venv/bin/python
```

## Expected Output

Each script provides:
- ✓ Success indicators for passed tests
- ✗ Failure indicators with error messages
- ⚠ Warning indicators for non-critical issues
- Clear instructions for fixing issues
- Exit code: 0 for success, 1 for failure

### Example Output

```
============================================================
Yahoo Finance Connectivity Test
============================================================

1. Testing stock price fetch for AAPL...
  ✓ Success: Current price = $175.23

2. Testing company info fetch...
  ✓ Success: Company name = Apple Inc.

3. Testing historical data fetch...
  ✓ Success: Retrieved 5 days of historical data
    Latest date: 2024-01-15

============================================================
✓ Yahoo Finance connectivity test PASSED
============================================================
```

## Troubleshooting

### Common Issues

1. **Virtual Environment Not Activated**: 
   ```bash
   # Always activate virtual environment first
   source .venv/bin/activate  # On macOS/Linux
   .venv\Scripts\activate     # On Windows
   
   # Verify: python should point to .venv/bin/python
   which python
   ```

2. **Import Errors**: Install missing dependencies in virtual environment
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   # OR using uv (as per POC setup)
   uv pip install -r requirements.txt
   ```

3. **API Key Not Found**: Set API keys in `.env` file at project root
   ```bash
   # Check if .env file exists
   ls .env
   
   # Edit .env file and add required keys
   # Example:
   OPENAI_API_KEY=your_key_here
   ALPHA_VANTAGE_API_KEY=your_key_here
   ```

4. **Connection Timeouts**: Check internet connection and firewall settings

5. **Rate Limits**: Some APIs (like Alpha Vantage free tier) have rate limits
   - Alpha Vantage: 5 calls/minute, 500 calls/day
   - Wait and retry if rate limited

6. **Ollama Not Running**: Ensure Ollama service is started
   ```bash
   # Check if running
   curl http://localhost:11434/api/tags
   
   # Pull a model if needed
   ollama pull llama2
   ```

## Integration with CI/CD

These scripts can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Test Connectivity
  run: |
    python scripts/test_all_connectivity.py
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    ALPHA_VANTAGE_API_KEY: ${{ secrets.ALPHA_VANTAGE_API_KEY }}
```

## Notes

- All scripts are designed to be non-destructive (test data is cleaned up)
- Scripts use test symbols/data (e.g., AAPL) that should be safe to use
- Some tests may require paid API keys (OpenAI, Anthropic)
- Free tier APIs have rate limits that may cause intermittent failures
- Ollama tests require local installation and running service


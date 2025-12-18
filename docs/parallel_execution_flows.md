# Parallel Execution Flows and Scenarios

## Overview

This document defines the parallel execution strategy for MyFinGPT, including:
- Automatic detection of what can run in parallel
- Within-agent parallelization opportunities
- Single stock query handling
- Incremental query handling (adding symbols to previous queries)
- Comparison Agent usage across all scenarios

## Core Principles

1. **Automatic Parallelization**: System automatically detects and executes parallel operations - user doesn't specify
2. **Maximize Parallelism**: Run independent operations in parallel whenever possible
3. **Preserve Dependencies**: Sequential operations only when dependencies exist
4. **State Accumulation**: Support incremental queries by preserving previous state

## Parallelization Opportunities

### 1. Research Agent - Data Fetching Parallelization

#### For Single Symbol
**Independent Operations** (can run in parallel):
- Fetch stock price
- Fetch company info
- Fetch news articles
- Fetch historical data
- Fetch financial statements

**Sequential Operations**:
- Store news in vector DB (depends on news fetch)
- Add citations (depends on all data fetches)

**Flow**:
```
Research Agent for Symbol "AAPL"
  ├─ Thread 1: Fetch price
  ├─ Thread 2: Fetch company info
  ├─ Thread 3: Fetch news
  ├─ Thread 4: Fetch historical data
  └─ Thread 5: Fetch financials
  ↓ (wait for all)
  ├─ Store news in vector DB (sequential)
  └─ Add citations (sequential)
```

#### For Multiple Symbols
**Two Levels of Parallelization**:
1. **Symbol-level**: Each symbol processed in parallel
2. **Data-type level**: Within each symbol, data types fetched in parallel

**Flow**:
```
Research Agent for ["AAPL", "MSFT", "GOOGL"]
  ├─ Symbol: AAPL
  │   ├─ Thread 1: Fetch price
  │   ├─ Thread 2: Fetch company info
  │   ├─ Thread 3: Fetch news
  │   ├─ Thread 4: Fetch historical
  │   └─ Thread 5: Fetch financials
  ├─ Symbol: MSFT
  │   ├─ Thread 6: Fetch price
  │   ├─ Thread 7: Fetch company info
  │   ├─ Thread 8: Fetch news
  │   ├─ Thread 9: Fetch historical
  │   └─ Thread 10: Fetch financials
  └─ Symbol: GOOGL
      ├─ Thread 11: Fetch price
      ├─ Thread 12: Fetch company info
      ├─ Thread 13: Fetch news
      ├─ Thread 14: Fetch historical
      └─ Thread 15: Fetch financials
  ↓ (wait for all)
  ├─ Store all news in vector DB (parallel per symbol)
  └─ Merge all results
```

### 2. Analyst Agent - Analysis Parallelization

#### For Single Symbol
**Independent Operations** (can run in parallel):
- Query historical patterns (vector DB)
- Analyze financials (calculations)
- Analyze sentiment (LLM call)
- Analyze trends (calculations)

**Sequential Operations**:
- Generate recommendation (depends on all analyses)
- Generate reasoning (depends on all analyses)

**Flow**:
```
Analyst Agent for Symbol "AAPL"
  ├─ Thread 1: Query historical patterns
  ├─ Thread 2: Analyze financials
  ├─ Thread 3: Analyze sentiment (LLM)
  └─ Thread 4: Analyze trends
  ↓ (wait for all)
  ├─ Generate recommendation (sequential)
  └─ Generate reasoning (sequential)
```

#### For Multiple Symbols
**Two Levels of Parallelization**:
1. **Symbol-level**: Each symbol analyzed in parallel
2. **Analysis-type level**: Within each symbol, analysis types run in parallel

**Flow**:
```
Analyst Agent for ["AAPL", "MSFT", "GOOGL"]
  ├─ Symbol: AAPL
  │   ├─ Thread 1: Query historical patterns
  │   ├─ Thread 2: Analyze financials
  │   ├─ Thread 3: Analyze sentiment
  │   └─ Thread 4: Analyze trends
  ├─ Symbol: MSFT
  │   ├─ Thread 5: Query historical patterns
  │   ├─ Thread 6: Analyze financials
  │   ├─ Thread 7: Analyze sentiment
  │   └─ Thread 8: Analyze trends
  └─ Symbol: GOOGL
      ├─ Thread 9: Query historical patterns
      ├─ Thread 10: Analyze financials
      ├─ Thread 11: Analyze sentiment
      └─ Thread 12: Analyze trends
  ↓ (wait for all)
  ├─ Generate recommendations (parallel per symbol)
  └─ Generate reasoning (parallel per symbol)
```

### 3. Comparison Agent - Always Runs

**Key Insight**: Comparison Agent should run for:
- Single stock queries (compare against benchmarks, historical patterns, sector averages)
- Multiple stock queries (side-by-side comparison)
- Incremental queries (compare new symbols with previous ones)

**Sequential Operations**:
- Comparison Agent runs after Analyst Agent completes
- Comparison logic is sequential (single agent comparing all symbols)

**Flow**:
```
Comparison Agent (after Analyst completes)
  ├─ Read all analysis_results
  ├─ Extract comparison metrics (parallel per symbol)
  ├─ Generate comparison insights (LLM call - sequential)
  └─ Write comparison_data to state
```

## Scenarios

### Scenario 1: Single Stock Query

**Query**: "Analyze AAPL stock"

**Flow**:
```
1. Research Agent (PARALLEL data fetching)
   ├─ Fetch price (thread 1)
   ├─ Fetch company info (thread 2)
   ├─ Fetch news (thread 3)
   ├─ Fetch historical (thread 4)
   └─ Fetch financials (thread 5)
   ↓
   Store news in vector DB
   ↓
2. Analyst Agent (PARALLEL analysis)
   ├─ Query historical patterns (thread 1)
   ├─ Analyze financials (thread 2)
   ├─ Analyze sentiment (thread 3)
   └─ Analyze trends (thread 4)
   ↓
   Generate recommendation & reasoning
   ↓
3. Comparison Agent (SEQUENTIAL)
   ├─ Compare AAPL against:
   │   ├─ Historical patterns (from vector DB)
   │   ├─ Sector averages (if available)
   │   └─ Benchmark indices (if available)
   └─ Generate comparison insights
   ↓
4. Reporting Agent (SEQUENTIAL)
   └─ Generate comprehensive report
```

**Key Points**:
- Single symbol but still uses parallelization within Research and Analyst agents
- Comparison Agent provides context by comparing against benchmarks/history
- No multi-symbol comparison, but still valuable comparison context

### Scenario 2: Multi-Stock Comparison Query

**Query**: "Compare AAPL, MSFT, and GOOGL"

**Flow**:
```
1. Research Agent (PARALLEL - symbol level + data level)
   ├─ AAPL: [price, company, news, historical, financials] (parallel)
   ├─ MSFT: [price, company, news, historical, financials] (parallel)
   └─ GOOGL: [price, company, news, historical, financials] (parallel)
   ↓
   Store all news in vector DB (parallel per symbol)
   ↓
2. Analyst Agent (PARALLEL - symbol level + analysis level)
   ├─ AAPL: [historical patterns, financials, sentiment, trends] (parallel)
   ├─ MSFT: [historical patterns, financials, sentiment, trends] (parallel)
   └─ GOOGL: [historical patterns, financials, sentiment, trends] (parallel)
   ↓
   Generate recommendations & reasoning (parallel per symbol)
   ↓
3. Comparison Agent (SEQUENTIAL)
   ├─ Extract comparison metrics from all symbols
   ├─ Side-by-side comparison:
   │   ├─ P/E ratios
   │   ├─ Market caps
   │   ├─ Sentiment scores
   │   ├─ Growth trends
   │   └─ Financial health metrics
   └─ Generate comparison insights (LLM)
   ↓
4. Reporting Agent (SEQUENTIAL)
   └─ Generate comparison report with side-by-side analysis
```

**Key Points**:
- Maximum parallelization: 3 symbols × 5 data types = 15 parallel operations in Research Agent
- Maximum parallelization: 3 symbols × 4 analysis types = 12 parallel operations in Analyst Agent
- Comparison Agent performs side-by-side comparison of all symbols

### Scenario 3: Incremental Query - Adding Symbols

**Query 1**: "Analyze AAPL stock"
**Query 2**: "Compare AAPL with MSFT" (user adds MSFT to previous query)

**Flow for Query 2**:
```
1. Detect incremental query:
   ├─ Check if AAPL already analyzed (from previous state/session)
   ├─ Extract new symbols: [MSFT]
   └─ Determine symbols to process: [MSFT] (AAPL already done)
   ↓
2. Research Agent (PARALLEL - only for new symbols)
   └─ MSFT: [price, company, news, historical, financials] (parallel)
   ↓
3. Analyst Agent (PARALLEL - only for new symbols)
   └─ MSFT: [historical patterns, financials, sentiment, trends] (parallel)
   ↓
4. Merge with previous state:
   ├─ Combine research_data: {AAPL: {...}, MSFT: {...}}
   ├─ Combine analysis_results: {AAPL: {...}, MSFT: {...}}
   └─ Update symbols list: [AAPL, MSFT]
   ↓
5. Comparison Agent (SEQUENTIAL)
   ├─ Compare AAPL vs MSFT:
   │   ├─ Side-by-side metrics
   │   ├─ Relative performance
   │   └─ Investment recommendation
   └─ Generate comparison insights
   ↓
6. Reporting Agent (SEQUENTIAL)
   └─ Generate comparison report
```

**Key Points**:
- System detects which symbols are new vs already analyzed
- Only processes new symbols (MSFT in this case)
- Merges new results with previous state
- Comparison Agent compares all symbols (old + new)

### Scenario 4: Incremental Query - Multiple Additions

**Query 1**: "Analyze AAPL stock"
**Query 2**: "Add MSFT and GOOGL to compare"

**Flow for Query 2**:
```
1. Detect incremental query:
   ├─ Previous symbols: [AAPL]
   ├─ New symbols: [MSFT, GOOGL]
   └─ Symbols to process: [MSFT, GOOGL] (parallel)
   ↓
2. Research Agent (PARALLEL)
   ├─ MSFT: [price, company, news, historical, financials] (parallel)
   └─ GOOGL: [price, company, news, historical, financials] (parallel)
   ↓
3. Analyst Agent (PARALLEL)
   ├─ MSFT: [historical patterns, financials, sentiment, trends] (parallel)
   └─ GOOGL: [historical patterns, financials, sentiment, trends] (parallel)
   ↓
4. Merge with previous state:
   ├─ research_data: {AAPL: {...}, MSFT: {...}, GOOGL: {...}}
   └─ analysis_results: {AAPL: {...}, MSFT: {...}, GOOGL: {...}}
   ↓
5. Comparison Agent
   └─ Compare all three: AAPL vs MSFT vs GOOGL
   ↓
6. Reporting Agent
   └─ Generate three-way comparison report
```

## Implementation Strategy

### Automatic Parallelization Detection

**Rules**:
1. **Research Agent**:
   - If `len(symbols) == 1`: Parallelize data fetching (5 operations)
   - If `len(symbols) > 1`: Parallelize symbols AND data fetching (N symbols × 5 operations)

2. **Analyst Agent**:
   - If `len(symbols) == 1`: Parallelize analysis types (4 operations)
   - If `len(symbols) > 1`: Parallelize symbols AND analysis types (N symbols × 4 operations)

3. **Comparison Agent**:
   - Always runs (single stock or multiple stocks)
   - Sequential execution (single agent comparing all symbols)

### State Management for Incremental Queries

**New State Fields**:
```python
# Add to AgentState
previous_query_id: Optional[str]  # Link to previous query
previous_symbols: List[str]  # Symbols from previous query
new_symbols: List[str]  # New symbols in current query
is_incremental: bool  # Whether this is an incremental query
```

**Detection Logic**:
1. Extract symbols from current query
2. Check if any symbols exist in previous state/session
3. Determine new symbols vs existing symbols
4. Set `is_incremental = True` if new symbols found
5. Process only new symbols, merge with previous state

**State Merging**:
- Merge `research_data` dictionaries
- Merge `analysis_results` dictionaries
- Combine `citations` lists
- Update `symbols` list
- Preserve `previous_query_id` for traceability

### Thread Pool Configuration

**Research Agent**:
- Max workers: `min(len(symbols) * 5, 20)` (cap at 20 threads)
- For single symbol: 5 workers (one per data type)
- For multiple symbols: `len(symbols) * 5` workers

**Analyst Agent**:
- Max workers: `min(len(symbols) * 4, 16)` (cap at 16 threads)
- For single symbol: 4 workers (one per analysis type)
- For multiple symbols: `len(symbols) * 4` workers

**Rationale**:
- Cap thread count to prevent resource exhaustion
- Balance between parallelism and resource usage
- Consider API rate limits when parallelizing

## Error Handling in Parallel Execution

### Partial Success Handling

**Strategy**:
- If one symbol fails, continue processing other symbols
- Track success/failure per symbol
- Set `partial_success = True` in state if any failures
- Include error information in state for failed symbols

**State Fields**:
```python
partial_success: bool  # True if some symbols succeeded, some failed
symbol_status: Dict[str, str]  # {"AAPL": "success", "INVALID": "failed"}
symbol_errors: Dict[str, str]  # {"INVALID": "Symbol not found"}
```

### Retry Logic

**For Parallel Operations**:
- Retry failed operations independently
- Don't retry entire batch if one fails
- Exponential backoff per operation
- Max retries: 3 per operation

## Performance Expectations

### Single Stock Query
- **Sequential (current)**: ~15-20 seconds
- **Parallel (proposed)**: ~5-8 seconds (3x faster)
- **Improvement**: Data fetching parallelized (5 operations → 1 wait time)

### Multi-Stock Query (3 symbols)
- **Sequential (current)**: ~45-60 seconds
- **Parallel (proposed)**: ~8-12 seconds (5x faster)
- **Improvement**: 15 parallel operations in Research, 12 in Analyst

### Incremental Query
- **Without caching**: Same as multi-stock
- **With state reuse**: ~8-12 seconds (only new symbols processed)

## Testing Scenarios

1. **Single stock with parallel data fetching**
2. **Multi-stock with full parallelization**
3. **Incremental query detection**
4. **State merging for incremental queries**
5. **Partial success handling**
6. **Error recovery in parallel execution**
7. **Comparison Agent for single stock**
8. **Comparison Agent for multiple stocks**
9. **Thread pool limits and resource management**

## Migration Path

1. **Phase 1**: Implement within-agent parallelization (Research Agent data fetching)
2. **Phase 2**: Implement within-agent parallelization (Analyst Agent analysis)
3. **Phase 3**: Implement symbol-level parallelization
4. **Phase 4**: Implement incremental query detection and state merging
5. **Phase 5**: Add Comparison Agent for all scenarios
6. **Phase 6**: Optimize thread pool configuration and error handling


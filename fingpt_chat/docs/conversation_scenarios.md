# MyFinGPT Chat - Conversation Scenarios

This document outlines conversation scenarios and prompts that should be used to test and validate the chat interface design and implementation. These scenarios cover various use cases, edge cases, and conversation flows.

## 1. Basic Single Stock Analysis

### Scenario 1.1: Simple Stock Analysis
**User:** "Analyze Apple Inc. (AAPL) stock"

**Expected Behavior:**
- Agent executes Research → Analyst → Reporting agents
- Returns comprehensive analysis report
- Includes citations and visualizations
- Progress updates shown in real-time

**Follow-up:** "What about its P/E ratio?"

**Expected Behavior:**
- Agent uses context from previous message
- References AAPL from conversation
- Provides P/E ratio information
- May reference previous analysis

### Scenario 1.2: Stock Analysis with Clarification
**User:** "Tell me about that tech company"

**Expected Behavior:**
- Agent detects unclear intent
- Asks clarification: "Which tech company would you like me to analyze? Please provide a stock symbol (e.g., AAPL, MSFT, GOOGL)."
- Waits for user response

**User:** "Apple"

**Expected Behavior:**
- Agent understands "Apple" refers to AAPL
- Proceeds with analysis
- May reference previous conversation if applicable

## 2. Multi-Stock Comparison

### Scenario 2.1: Initial Comparison
**User:** "Compare Apple (AAPL), Microsoft (MSFT), and Google (GOOGL)"

**Expected Behavior:**
- Agent executes parallel research for all three symbols
- Performs comparison analysis
- Returns comparative report
- Shows comparison charts

### Scenario 2.2: Incremental Comparison
**User:** "Compare Apple (AAPL), Microsoft (MSFT), and Google (GOOGL)"

**Agent Response:** [Provides comparison]

**User:** "Add Amazon (AMZN) to the comparison"

**Expected Behavior:**
- Agent detects incremental query
- Fetches data for AMZN only
- Merges with previous comparison
- Updates comparison report
- Maintains context of previous three stocks

### Scenario 2.3: Reference Previous Comparison
**User:** "Compare Apple (AAPL), Microsoft (MSFT), and Google (GOOGL)"

**Agent Response:** [Provides comparison]

**User:** "Which one has the highest revenue?"

**Expected Behavior:**
- Agent uses context from previous comparison
- References the three stocks mentioned
- Provides revenue comparison
- May reference previous analysis data

## 3. Trend Analysis

### Scenario 3.1: Price Trend
**User:** "Show me the 6-month price trend for Tesla (TSLA)"

**Expected Behavior:**
- Agent fetches historical data
- Analyzes trend patterns
- Returns trend analysis with chart
- Identifies support/resistance levels

**User:** "What about the last month?"

**Expected Behavior:**
- Agent understands "last month" refers to TSLA
- Fetches 1-month historical data
- Updates trend analysis
- Maintains context of TSLA

### Scenario 3.2: Trend Comparison
**User:** "Compare the price trends of AAPL and MSFT over the last year"

**Expected Behavior:**
- Agent fetches historical data for both
- Performs trend comparison
- Shows comparative charts
- Identifies correlation patterns

## 4. Sentiment Analysis

### Scenario 4.1: News Sentiment
**User:** "How has recent news affected NVIDIA (NVDA) stock?"

**Expected Behavior:**
- Agent fetches recent news
- Performs sentiment analysis
- Analyzes news impact on stock
- Returns sentiment report

**User:** "What were the main news stories?"

**Expected Behavior:**
- Agent references previous NVDA analysis
- Lists main news stories
- May reference sentiment scores

### Scenario 4.2: Sentiment Over Time
**User:** "Analyze the sentiment trend for Tesla (TSLA) over the last 3 months"

**Expected Behavior:**
- Agent fetches news over 3 months
- Performs time-series sentiment analysis
- Shows sentiment trend chart
- Correlates with price movements

## 5. Financial Metrics Queries

### Scenario 5.1: Specific Metric
**User:** "What is Apple's current market cap?"

**Expected Behavior:**
- Agent fetches current market cap
- Provides answer with citation
- Quick response (may skip full analysis)

**User:** "And Microsoft's?"

**Expected Behavior:**
- Agent understands "Microsoft" refers to MSFT
- Fetches MSFT market cap
- May compare with AAPL if context suggests

### Scenario 5.2: Multiple Metrics
**User:** "Give me the P/E ratio, revenue, and profit margin for Amazon (AMZN)"

**Expected Behavior:**
- Agent fetches all requested metrics
- Returns structured response
- Includes citations for each metric

## 6. Context Continuity

### Scenario 6.1: Multi-Turn Conversation
**User:** "Analyze Apple (AAPL) stock"

**Agent Response:** [Provides analysis]

**User:** "What about its competitors?"

**Expected Behavior:**
- Agent understands "competitors" in context of AAPL
- Identifies AAPL competitors (e.g., MSFT, GOOGL)
- Provides competitor analysis
- References AAPL from previous message

**User:** "Compare their market caps"

**Expected Behavior:**
- Agent understands "their" refers to AAPL and competitors
- Provides market cap comparison
- Maintains full conversation context

### Scenario 6.2: Context Switching
**User:** "Analyze Apple (AAPL) stock"

**Agent Response:** [Provides analysis]

**User:** "Now analyze Tesla (TSLA)"

**Expected Behavior:**
- Agent switches context to TSLA
- Performs new analysis
- May maintain some context (e.g., comparison opportunity)

**User:** "Compare them"

**Expected Behavior:**
- Agent understands "them" refers to AAPL and TSLA
- Performs comparison
- Uses context from both previous analyses

## 7. Ambiguous Queries

### Scenario 7.1: Unclear Symbol
**User:** "Tell me about Apple"

**Expected Behavior:**
- Agent asks clarification: "Are you referring to Apple Inc. (AAPL)? Please confirm or provide the stock symbol."
- Waits for confirmation

**User:** "Yes, AAPL"

**Expected Behavior:**
- Agent proceeds with AAPL analysis

### Scenario 7.2: Unclear Intent
**User:** "What about that stock we discussed?"

**Expected Behavior:**
- Agent detects unclear reference
- Asks clarification: "I need more context. Which stock are you referring to? Please provide the stock symbol or describe what we discussed."
- May list recent stocks if available

**User:** "The tech company"

**Expected Behavior:**
- Agent may ask: "We discussed multiple tech companies. Please specify: AAPL, MSFT, GOOGL, or another?"
- Or may infer from most recent context

### Scenario 7.3: Missing Information
**User:** "Compare those stocks"

**Expected Behavior:**
- Agent detects missing context
- Asks: "Which stocks would you like me to compare? Please provide stock symbols."
- Or may reference recent comparison if available

## 8. Error Handling

### Scenario 8.1: Invalid Symbol
**User:** "Analyze INVALID123 stock"

**Expected Behavior:**
- Agent validates symbol
- Returns error: "Invalid stock symbol: INVALID123. Please provide a valid stock symbol (1-5 uppercase letters)."
- Does not proceed with analysis

**User:** "What about AAPL?"

**Expected Behavior:**
- Agent proceeds with AAPL analysis
- Previous error does not affect new query

### Scenario 8.2: API Failure
**User:** "Analyze AAPL stock"

**Expected Behavior:**
- If API fails, agent tries fallback sources
- If all fail, returns partial results with error message
- Explains what data is missing

### Scenario 8.3: Network Error
**User:** "Analyze AAPL stock"

**Expected Behavior:**
- If network error occurs, agent retries
- If retries fail, returns error message
- Suggests retrying later

## 9. Complex Queries

### Scenario 9.1: Multi-Part Query
**User:** "Analyze Apple (AAPL) stock, compare it with Microsoft (MSFT), and show me the price trends for both"

**Expected Behavior:**
- Agent breaks down into parts
- Executes: analysis → comparison → trend analysis
- Returns comprehensive response covering all parts
- May ask if user wants all at once or step-by-step

### Scenario 9.2: Conditional Query
**User:** "If Apple's P/E ratio is above 30, tell me why it might be overvalued"

**Expected Behavior:**
- Agent fetches AAPL P/E ratio
- Evaluates condition
- If condition met, provides overvaluation analysis
- If not met, explains current P/E and why it may not be overvalued

### Scenario 9.3: Historical Comparison
**User:** "Compare Apple's current performance with its performance 6 months ago"

**Expected Behavior:**
- Agent fetches current and historical data
- Performs temporal comparison
- Identifies changes and trends
- Explains performance evolution

## 10. Follow-up Questions

### Scenario 10.1: Clarification Follow-up
**User:** "Analyze AAPL"

**Agent Response:** [Provides analysis]

**User:** "What does that mean?"

**Expected Behavior:**
- Agent detects unclear reference
- Asks: "Which part would you like me to explain? Please specify (e.g., P/E ratio, revenue growth, recommendation)."
- Or may infer from context

**User:** "The P/E ratio"

**Expected Behavior:**
- Agent explains P/E ratio in context of AAPL
- Provides educational content
- References AAPL's specific P/E value

### Scenario 10.2: Deep Dive
**User:** "Analyze AAPL"

**Agent Response:** [Provides analysis]

**User:** "Tell me more about its financial health"

**Expected Behavior:**
- Agent expands on financial health aspects
- Provides deeper analysis
- References previous analysis data
- May fetch additional metrics if needed

### Scenario 10.3: Alternative Analysis
**User:** "Analyze AAPL"

**Agent Response:** [Provides analysis with "Buy" recommendation]

**User:** "What are the risks?"

**Expected Behavior:**
- Agent provides risk analysis
- Balances previous positive recommendation
- References AAPL-specific risks
- May update recommendation if risks are significant

## 11. Edge Cases

### Scenario 11.1: Very Long Conversation
**User:** [20+ messages in conversation]

**Expected Behavior:**
- Agent maintains context (within limits)
- May prune old context if size exceeds limit
- Still references recent messages accurately
- Performance remains acceptable

### Scenario 11.2: Rapid Messages
**User:** "Analyze AAPL" [immediately] "Wait, analyze MSFT instead"

**Expected Behavior:**
- Agent may process first message
- Second message cancels or updates first
- Or agent queues messages and processes latest
- Returns appropriate response

### Scenario 11.3: Empty Message
**User:** "" (empty message)

**Expected Behavior:**
- Agent validates input
- Returns error: "Please provide a message."
- Does not process empty message

### Scenario 11.4: Non-Financial Query
**User:** "What's the weather today?"

**Expected Behavior:**
- Agent validates domain
- Returns error: "I can only help with financial analysis. Please ask about stocks, companies, or financial markets."
- Does not process non-financial query

## 12. Context Window Management

### Scenario 12.1: Large Context
**User:** [Multiple long conversations with many symbols]

**Expected Behavior:**
- Agent manages context size
- Prunes old/unnecessary data
- Maintains essential context
- Still provides accurate responses

### Scenario 12.2: Context Overflow
**User:** [Context exceeds limit]

**Expected Behavior:**
- Agent prunes context intelligently
- Keeps most recent and relevant data
- May warn user if significant context is lost
- Continues to function

## 13. Visualization Requests

### Scenario 13.1: Chart Request
**User:** "Show me a chart of AAPL's price over the last year"

**Expected Behavior:**
- Agent generates price chart
- Displays interactive chart in chat
- Chart is responsive and zoomable

**User:** "Make it a bar chart instead"

**Expected Behavior:**
- Agent regenerates chart as bar chart
- Updates visualization
- Maintains same data

### Scenario 13.2: Multiple Charts
**User:** "Show me price charts for AAPL, MSFT, and GOOGL"

**Expected Behavior:**
- Agent generates multiple charts
- May combine in single chart or separate charts
- All charts displayed in chat

## 14. Citation and Source Requests

### Scenario 14.1: Source Request
**User:** "Analyze AAPL"

**Agent Response:** [Provides analysis with citations]

**User:** "Where did you get the revenue data?"

**Expected Behavior:**
- Agent references specific citation
- Provides source URL and details
- Explains data source

### Scenario 14.2: Multiple Sources
**User:** "Compare data from different sources for AAPL"

**Expected Behavior:**
- Agent fetches from multiple sources (Yahoo Finance, Alpha Vantage, FMP)
- Compares data across sources
- Highlights any discrepancies
- Provides citations for each source

## 15. Performance Scenarios

### Scenario 15.1: Quick Response
**User:** "What is AAPL's current price?"

**Expected Behavior:**
- Agent provides quick response (< 5 seconds)
- May skip full analysis for simple queries
- Returns just the requested information

### Scenario 15.2: Complex Analysis
**User:** "Perform a comprehensive analysis of AAPL including all financial metrics, news sentiment, trend analysis, and competitor comparison"

**Expected Behavior:**
- Agent executes full analysis pipeline
- Shows progress updates throughout
- Returns comprehensive report
- May take 30-60 seconds
- User can see progress in real-time

## 16. Session Management

### Scenario 16.1: New Session
**User:** [First message in new session]

**Expected Behavior:**
- System creates new session
- Assigns session ID
- Stores session ID in frontend
- Begins conversation

### Scenario 16.2: Session Continuation
**User:** [Continues conversation after page refresh]

**Expected Behavior:**
- System loads previous session
- Restores conversation history
- Maintains context
- User can continue seamlessly

### Scenario 16.3: Session Expiration
**User:** [Returns after 24+ hours]

**Expected Behavior:**
- System detects expired session
- Creates new session
- Previous context not available
- User starts fresh conversation

## 17. Intent Detection Scenarios

### Scenario 17.1: Clear Intent
**User:** "Analyze Apple Inc. (AAPL) stock including current price, financial health, and investment recommendation"

**Expected Behavior:**
- Agent detects clear intent: comprehensive stock analysis
- Proceeds without clarification
- Executes full analysis pipeline

### Scenario 17.2: Unclear Intent
**User:** "Tell me about stocks"

**Expected Behavior:**
- Agent detects unclear intent
- Asks: "I can help you analyze stocks. Please specify: Which stock(s) would you like me to analyze? What information are you looking for?"
- Waits for clarification

### Scenario 17.3: Partial Intent
**User:** "Compare tech stocks"

**Expected Behavior:**
- Agent detects partial intent
- Asks: "Which tech stocks would you like me to compare? Please provide stock symbols (e.g., AAPL, MSFT, GOOGL)."
- Or may suggest popular tech stocks

## 18. Multi-Language Support (Future)

### Scenario 18.1: English Query
**User:** "Analyze AAPL stock"

**Expected Behavior:**
- Agent processes in English
- Returns English response

### Scenario 18.2: Mixed Language (Future)
**User:** "Analyze AAPL stock" [then] "¿Cuál es su precio actual?"

**Expected Behavior:**
- Agent detects language change
- Responds in Spanish
- Maintains context from English query

## 19. Testing Checklist

Use these scenarios to validate:

- [ ] Basic stock analysis works
- [ ] Multi-stock comparison works
- [ ] Incremental queries work
- [ ] Context is maintained across messages
- [ ] Clarification questions are asked when needed
- [ ] Follow-up questions reference previous context
- [ ] Error handling works correctly
- [ ] Progress updates stream in real-time
- [ ] Visualizations display correctly
- [ ] Citations are included
- [ ] Session management works
- [ ] Context pruning works
- [ ] Performance is acceptable
- [ ] WebSocket reconnection works
- [ ] API errors are handled gracefully

## 20. Success Criteria

A conversation scenario is successful if:

1. **Intent Understanding**: Agent correctly understands user intent (or asks for clarification)
2. **Context Preservation**: Agent maintains conversation context appropriately
3. **Accurate Responses**: Agent provides accurate financial information
4. **Real-time Updates**: Progress updates are shown in real-time
5. **Error Handling**: Errors are handled gracefully with helpful messages
6. **User Experience**: Conversation feels natural and responsive
7. **Performance**: Response times are acceptable (< 60s for complex queries)
8. **Visualizations**: Charts and graphs display correctly
9. **Citations**: All data includes proper citations
10. **Session Management**: Sessions persist and restore correctly


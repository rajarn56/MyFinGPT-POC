"""Static response data for mock server."""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid


def generate_message_id() -> str:
    """Generate a unique message ID."""
    return f"msg_{uuid.uuid4().hex[:12]}"


def generate_transaction_id() -> str:
    """Generate a unique transaction ID."""
    return f"txn_{uuid.uuid4().hex[:12]}"


def get_mock_chat_response(message: str, session_id: str) -> Dict[str, Any]:
    """Get mock chat response based on message content."""
    message_lower = message.lower()
    
    # Detect intent and generate appropriate response
    if "compare" in message_lower or "comparison" in message_lower:
        return get_comparison_response(session_id, message)
    elif "trend" in message_lower or "chart" in message_lower:
        return get_trend_response(session_id, message)
    elif any(symbol in message_lower for symbol in ["aapl", "msft", "googl", "amzn", "tsla", "meta"]):
        return get_single_stock_response(session_id, message)
    else:
        return get_generic_response(session_id, message)


def get_single_stock_response(session_id: str, message: str) -> Dict[str, Any]:
    """Get mock response for single stock analysis."""
    # Extract symbol from message (simplified)
    symbol = "AAPL"
    if "msft" in message.lower():
        symbol = "MSFT"
    elif "googl" in message.lower() or "google" in message.lower():
        symbol = "GOOGL"
    elif "amzn" in message.lower() or "amazon" in message.lower():
        symbol = "AMZN"
    elif "tsla" in message.lower() or "tesla" in message.lower():
        symbol = "TSLA"
    elif "meta" in message.lower() or "facebook" in message.lower():
        symbol = "META"
    
    return {
        "message_id": generate_message_id(),
        "session_id": session_id,
        "content": f"""# Analysis Report: {symbol}

## Executive Summary

{symbol} shows strong fundamentals with consistent revenue growth and solid market position. The company demonstrates resilience in the current market environment.

## Key Metrics

- **Current Price**: $175.50
- **Market Cap**: $2.8T
- **P/E Ratio**: 28.5
- **Dividend Yield**: 0.5%
- **52-Week Range**: $124.17 - $198.23

## Financial Highlights

### Revenue Growth
The company has shown consistent revenue growth over the past quarters, with Q4 2024 revenue reaching $89.5B, representing a 1% YoY increase.

### Profitability
Operating margin remains healthy at 29.8%, indicating strong operational efficiency and pricing power.

### Balance Sheet
The company maintains a strong balance sheet with $166.5B in cash and cash equivalents, providing significant financial flexibility.

## Investment Thesis

**Strengths:**
- Strong brand recognition and customer loyalty
- Diversified product portfolio
- Robust cash generation
- Innovation leadership in key markets

**Risks:**
- Market saturation in core segments
- Regulatory challenges
- Supply chain dependencies
- Competitive pressures

## Recommendation

**Rating**: Hold
**Target Price**: $185.00

The stock presents a balanced risk-reward profile. Current valuation is reasonable given growth prospects, but near-term upside may be limited by market conditions.
""",
        "transaction_id": generate_transaction_id(),
        "citations": [
            {
                "source": "Yahoo Finance",
                "url": f"https://finance.yahoo.com/quote/{symbol}",
                "date": datetime.now().isoformat(),
                "data_point": "Stock Price",
                "symbol": symbol
            },
            {
                "source": "Financial Modeling Prep",
                "url": f"https://site.financialmodelingprep.com/stock/{symbol}",
                "date": datetime.now().isoformat(),
                "data_point": "Financial Statements",
                "symbol": symbol
            }
        ],
        "visualizations": [
            {
                "type": "line_chart",
                "title": f"{symbol} Price Trend (6 Months)",
                "data": {
                    "x": ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"],
                    "y": [165.2, 172.5, 168.3, 175.1, 178.9, 175.5],
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": symbol
                },
                "config": {
                    "responsive": True,
                    "displayModeBar": True
                }
            },
            {
                "type": "bar_chart",
                "title": f"{symbol} Revenue by Quarter",
                "data": {
                    "x": ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"],
                    "y": [94.8, 81.8, 89.5, 89.5],
                    "type": "bar",
                    "name": "Revenue (B)"
                },
                "config": {
                    "responsive": True
                }
            }
        ],
        "agent_activity": {
            "agents_executed": ["Research", "Analyst", "Reporting"],
            "token_usage": {
                "Research": 1500,
                "Analyst": 2000,
                "Reporting": 3000
            },
            "execution_time": {
                "Research": 5.2,
                "Analyst": 8.5,
                "Reporting": 12.3
            },
            "context_size": 45000
        },
        "timestamp": datetime.now().isoformat()
    }


def get_comparison_response(session_id: str, message: str) -> Dict[str, Any]:
    """Get mock response for stock comparison."""
    symbols = []
    if "aapl" in message.lower() or "apple" in message.lower():
        symbols.append("AAPL")
    if "msft" in message.lower() or "microsoft" in message.lower():
        symbols.append("MSFT")
    if "googl" in message.lower() or "google" in message.lower():
        symbols.append("GOOGL")
    if "amzn" in message.lower() or "amazon" in message.lower():
        symbols.append("AMZN")
    
    if not symbols:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    
    symbols_str = ", ".join(symbols)
    
    return {
        "message_id": generate_message_id(),
        "session_id": session_id,
        "content": f"""# Comparison Report: {symbols_str}

## Executive Summary

This report compares {symbols_str} across key financial metrics, growth prospects, and investment characteristics.

## Comparative Metrics

| Metric | {symbols_str.replace(', ', ' | ')} |
|--------|{'|'.join(['---' for _ in symbols])}|
| Current Price | $175.50 | $378.20 | $142.30 |
| Market Cap | $2.8T | $2.8T | $1.8T |
| P/E Ratio | 28.5 | 35.2 | 25.8 |
| Revenue Growth | 1% | 13% | 8% |
| Operating Margin | 29.8% | 44.3% | 24.5% |

## Key Insights

### Growth Comparison
{symbols[1] if len(symbols) > 1 else 'MSFT'} shows the strongest revenue growth at 13% YoY, driven by cloud services expansion.

### Profitability
{symbols[1] if len(symbols) > 1 else 'MSFT'} leads in operating margin at 44.3%, reflecting strong pricing power and operational efficiency.

### Valuation
{symbols[2] if len(symbols) > 2 else 'GOOGL'} offers the most attractive P/E ratio at 25.8, suggesting potential value opportunity.

## Investment Recommendation

**Best Growth Play**: {symbols[1] if len(symbols) > 1 else 'MSFT'}
**Best Value Play**: {symbols[2] if len(symbols) > 2 else 'GOOGL'}
**Most Stable**: {symbols[0] if len(symbols) > 0 else 'AAPL'}
""",
        "transaction_id": generate_transaction_id(),
        "citations": [
            {
                "source": "Yahoo Finance",
                "url": f"https://finance.yahoo.com/quote/{symbol}",
                "date": datetime.now().isoformat(),
                "data_point": "Stock Price",
                "symbol": symbol
            }
            for symbol in symbols
        ],
        "visualizations": [
            {
                "type": "line_chart",
                "title": f"Price Comparison: {symbols_str}",
                "data": {
                    "x": ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"],
                    "y": [
                        [165.2, 172.5, 168.3, 175.1, 178.9, 175.5],
                        [365.2, 372.5, 368.3, 375.1, 378.9, 378.2],
                        [135.2, 142.5, 138.3, 145.1, 148.9, 142.3]
                    ],
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": symbols
                },
                "config": {
                    "responsive": True
                }
            }
        ],
        "agent_activity": {
            "agents_executed": ["Research", "Comparison", "Analyst", "Reporting"],
            "token_usage": {
                "Research": 2500,
                "Comparison": 1800,
                "Analyst": 3000,
                "Reporting": 3500
            },
            "execution_time": {
                "Research": 8.5,
                "Comparison": 6.2,
                "Analyst": 12.3,
                "Reporting": 15.8
            },
            "context_size": 78000
        },
        "timestamp": datetime.now().isoformat()
    }


def get_trend_response(session_id: str, message: str) -> Dict[str, Any]:
    """Get mock response for trend analysis."""
    symbol = "AAPL"
    if "tsla" in message.lower():
        symbol = "TSLA"
    
    return {
        "message_id": generate_message_id(),
        "session_id": session_id,
        "content": f"""# Trend Analysis: {symbol}

## Price Trend Overview

{symbol} has shown a positive trend over the analyzed period, with notable volatility around key market events.

## Trend Characteristics

- **Overall Direction**: Upward
- **Volatility**: Moderate
- **Support Level**: $165.00
- **Resistance Level**: $180.00

## Key Observations

The stock has maintained an upward trajectory with periodic corrections. Recent consolidation suggests potential breakout above resistance levels.
""",
        "transaction_id": generate_transaction_id(),
        "citations": [
            {
                "source": "Yahoo Finance",
                "url": f"https://finance.yahoo.com/quote/{symbol}",
                "date": datetime.now().isoformat(),
                "data_point": "Historical Prices",
                "symbol": symbol
            }
        ],
        "visualizations": [
            {
                "type": "line_chart",
                "title": f"{symbol} 6-Month Price Trend",
                "data": {
                    "x": ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"],
                    "y": [165.2, 172.5, 168.3, 175.1, 178.9, 175.5],
                    "type": "scatter",
                    "mode": "lines+markers"
                },
                "config": {
                    "responsive": True
                }
            }
        ],
        "agent_activity": {
            "agents_executed": ["Research", "Analyst"],
            "token_usage": {
                "Research": 1200,
                "Analyst": 1800
            },
            "execution_time": {
                "Research": 4.5,
                "Analyst": 7.2
            },
            "context_size": 32000
        },
        "timestamp": datetime.now().isoformat()
    }


def get_generic_response(session_id: str, message: str) -> Dict[str, Any]:
    """Get generic mock response."""
    return {
        "message_id": generate_message_id(),
        "session_id": session_id,
        "content": f"""# Response

I understand you're asking: "{message}"

To provide you with accurate financial analysis, please specify:
- Stock symbol(s) (e.g., AAPL, MSFT)
- Type of analysis (e.g., analysis, comparison, trend)
- Time period if relevant

For example: "Analyze Apple Inc. (AAPL) stock" or "Compare AAPL and MSFT"
""",
        "transaction_id": generate_transaction_id(),
        "citations": [],
        "visualizations": [],
        "agent_activity": {
            "agents_executed": [],
            "token_usage": {},
            "execution_time": {},
            "context_size": 0
        },
        "timestamp": datetime.now().isoformat()
    }


def get_mock_history(session_id: str) -> List[Dict[str, Any]]:
    """Get mock conversation history."""
    return [
        {
            "id": generate_message_id(),
            "session_id": session_id,
            "role": "user",
            "content": "Analyze Apple Inc. (AAPL) stock",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()
        },
        {
            "id": generate_message_id(),
            "session_id": session_id,
            "role": "assistant",
            "content": "I've analyzed AAPL. Here's the comprehensive report...",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=2)).isoformat(),
            "transaction_id": generate_transaction_id()
        }
    ]


/** Demo data for initial UI population */
import type { ChatMessage, AgentActivity, Visualization } from '../types/chat';
import type { ProgressEvent, ExecutionOrderEntry } from '../types/progress';

const DEMO_ANALYSIS_REPORT = `# Analysis Report: Apple Inc. (AAPL)

## Executive Summary

Apple Inc. (AAPL) demonstrates strong financial fundamentals with consistent revenue growth and solid market position. The company shows resilience in the current market environment with robust cash generation and innovation leadership.

## Key Metrics

- **Current Price**: $175.50
- **Market Cap**: $2.8T
- **P/E Ratio**: 28.5
- **Dividend Yield**: 0.5%
- **52-Week Range**: $124.17 - $198.23
- **Beta**: 1.25

## Financial Highlights

### Revenue Growth
Apple has shown consistent revenue growth over the past quarters:
- Q1 2024: $94.8B (YoY: +2%)
- Q2 2024: $81.8B (YoY: -4%)
- Q3 2024: $89.5B (YoY: +1%)
- Q4 2024: $89.5B (YoY: +1%)

The company maintains strong revenue diversification across product categories, with Services revenue growing at 11% YoY.

### Profitability Analysis
- **Operating Margin**: 29.8% (industry-leading)
- **Net Margin**: 25.3%
- **ROE**: 147.2%
- **ROA**: 28.5%

Operating margin remains healthy, indicating strong operational efficiency and pricing power in key markets.

### Balance Sheet Strength
- **Cash and Equivalents**: $166.5B
- **Total Debt**: $95.3B
- **Debt-to-Equity**: 1.73
- **Current Ratio**: 1.07

The company maintains a strong balance sheet with significant cash reserves, providing substantial financial flexibility for strategic investments and shareholder returns.

## Investment Thesis

### Strengths
1. **Brand Recognition**: Unmatched brand loyalty and customer retention
2. **Ecosystem Lock-in**: Integrated hardware, software, and services ecosystem
3. **Innovation Leadership**: Consistent track record of product innovation
4. **Cash Generation**: Robust free cash flow generation ($99.6B TTM)
5. **Services Growth**: High-margin Services segment growing rapidly

### Risks
1. **Market Saturation**: Mature smartphone market in key regions
2. **Regulatory Challenges**: Increasing scrutiny in multiple jurisdictions
3. **Supply Chain Dependencies**: Concentration risk in manufacturing
4. **Competitive Pressures**: Intense competition in all product categories
5. **Macroeconomic Sensitivity**: Exposure to consumer spending cycles

## Technical Analysis

### Price Trends
- **Short-term (1M)**: +2.3% - Consolidating after recent gains
- **Medium-term (3M)**: +8.5% - Uptrend intact
- **Long-term (1Y)**: +12.4% - Strong performance

### Support and Resistance
- **Key Support**: $165.00 (50-day moving average)
- **Key Resistance**: $180.00 (recent high)
- **Current Position**: Trading near upper range

## Sector Comparison

| Metric | AAPL | Sector Avg | S&P 500 |
|--------|------|------------|---------|
| P/E Ratio | 28.5 | 25.2 | 22.8 |
| ROE | 147.2% | 18.5% | 15.2% |
| Profit Margin | 25.3% | 12.8% | 10.5% |
| Revenue Growth | 1% | 5.2% | 4.8% |

## Analyst Consensus

- **Buy Ratings**: 28 (70%)
- **Hold Ratings**: 10 (25%)
- **Sell Ratings**: 2 (5%)
- **Average Target Price**: $185.00
- **Upside Potential**: +5.4%

## Recommendation

**Rating**: Hold
**Target Price**: $185.00
**Time Horizon**: 12 months

### Rationale
Apple presents a balanced risk-reward profile at current levels. While the company demonstrates strong fundamentals and market position, near-term upside may be limited by:
- Valuation at premium to market
- Slowing iPhone growth in mature markets
- Macroeconomic headwinds affecting consumer spending

However, long-term investors may find value in:
- Services revenue growth trajectory
- Innovation pipeline (AR/VR, AI integration)
- Strong capital returns program
- Defensive characteristics in volatile markets

### Investment Strategy
- **Conservative**: Wait for pullback to $165-170 range
- **Moderate**: Current levels acceptable for long-term positions
- **Aggressive**: Consider on any weakness below $170

## Risk Factors

1. **Regulatory**: Antitrust investigations in multiple regions
2. **Geopolitical**: China exposure (~20% of revenue)
3. **Technology**: Disruption risk from emerging technologies
4. **Competition**: Intensifying competition in core markets
5. **Supply Chain**: Concentration risk in manufacturing

## Conclusion

Apple Inc. remains a high-quality company with strong fundamentals, but current valuation reflects most of the positive factors. Investors should consider entry points on market weakness and maintain a long-term perspective given the company's innovation capabilities and ecosystem strength.

---

*Report generated on ${new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}*
*Data sources: Yahoo Finance, Financial Modeling Prep, Company Filings*`;

const DEMO_VISUALIZATIONS: Visualization[] = [
  {
    type: 'line_chart',
    title: 'AAPL Price Trend (6 Months)',
    data: {
      x: ['2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12'],
      y: [165.2, 172.5, 168.3, 175.1, 178.9, 175.5],
      type: 'scatter',
      mode: 'lines+markers',
      name: 'AAPL'
    },
    config: {
      responsive: true,
      displayModeBar: true
    }
  },
  {
    type: 'bar_chart',
    title: 'AAPL Revenue by Quarter (Billions)',
    data: {
      x: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024'],
      y: [94.8, 81.8, 89.5, 89.5],
      type: 'bar',
      name: 'Revenue',
      marker: { color: '#007bff' }
    },
    config: {
      responsive: true
    }
  },
  {
    type: 'line_chart',
    title: 'Key Financial Metrics Comparison',
    data: {
      x: ['Q1', 'Q2', 'Q3', 'Q4'],
      y: [
        [29.8, 29.5, 30.1, 29.8],
        [25.3, 24.8, 25.5, 25.3]
      ],
      type: 'scatter',
      mode: 'lines+markers',
      name: ['Operating Margin %', 'Net Margin %']
    },
    config: {
      responsive: true
    }
  }
];

export const DEMO_AGENT_ACTIVITY: AgentActivity = {
  agents_executed: ['Research', 'Analyst', 'Reporting'],
  token_usage: {
    Research: 2450,
    Analyst: 3200,
    Reporting: 4100
  },
  execution_time: {
    Research: 8.5,
    Analyst: 12.3,
    Reporting: 15.8
  },
  context_size: 78250
};

export function getDemoProgressEvents(): ProgressEvent[] {
  const baseTime = new Date(Date.now() - 2 * 60 * 1000);
  
  return [
    {
      timestamp: new Date(baseTime.getTime() + 0 * 1000).toISOString(),
      agent: 'Research',
      event_type: 'agent_start',
      message: 'Research Agent started execution',
      status: 'completed',
      execution_order: 0,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 1 * 1000).toISOString(),
      agent: 'Research',
      event_type: 'api_call_start',
      message: 'Calling Yahoo Finance API for AAPL',
      status: 'completed',
      execution_order: 1,
      is_parallel: false,
      integration: 'yahoo_finance'
    },
    {
      timestamp: new Date(baseTime.getTime() + 2 * 1000).toISOString(),
      agent: 'Research',
      event_type: 'api_call_success',
      message: 'Yahoo Finance API call succeeded - retrieved stock price data',
      status: 'success',
      execution_order: 2,
      is_parallel: false,
      integration: 'yahoo_finance'
    },
    {
      timestamp: new Date(baseTime.getTime() + 3 * 1000).toISOString(),
      agent: 'Research',
      event_type: 'api_call_start',
      message: 'Calling Financial Modeling Prep API for financial statements',
      status: 'completed',
      execution_order: 3,
      is_parallel: false,
      integration: 'fmp'
    },
    {
      timestamp: new Date(baseTime.getTime() + 4 * 1000).toISOString(),
      agent: 'Research',
      event_type: 'api_call_success',
      message: 'FMP API call succeeded - retrieved quarterly financial data',
      status: 'success',
      execution_order: 4,
      is_parallel: false,
      integration: 'fmp'
    },
    {
      timestamp: new Date(baseTime.getTime() + 5 * 1000).toISOString(),
      agent: 'Research',
      event_type: 'task_complete',
      message: 'Completed data collection for AAPL',
      task_name: 'Data Collection',
      status: 'completed',
      execution_order: 5,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 6 * 1000).toISOString(),
      agent: 'Research',
      event_type: 'agent_complete',
      message: 'Research Agent completed execution - collected comprehensive data',
      status: 'completed',
      execution_order: 6,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 7 * 1000).toISOString(),
      agent: 'Analyst',
      event_type: 'agent_start',
      message: 'Analyst Agent started execution',
      status: 'completed',
      execution_order: 7,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 8 * 1000).toISOString(),
      agent: 'Analyst',
      event_type: 'task_start',
      message: 'Analyzing financial ratios and metrics',
      task_name: 'Financial Analysis',
      status: 'completed',
      execution_order: 8,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 10 * 1000).toISOString(),
      agent: 'Analyst',
      event_type: 'task_complete',
      message: 'Completed financial ratio analysis',
      task_name: 'Financial Analysis',
      status: 'completed',
      execution_order: 9,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 11 * 1000).toISOString(),
      agent: 'Analyst',
      event_type: 'task_start',
      message: 'Generating investment insights',
      task_name: 'Insight Generation',
      status: 'completed',
      execution_order: 10,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 13 * 1000).toISOString(),
      agent: 'Analyst',
      event_type: 'task_complete',
      message: 'Completed insight generation',
      task_name: 'Insight Generation',
      status: 'completed',
      execution_order: 11,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 14 * 1000).toISOString(),
      agent: 'Analyst',
      event_type: 'agent_complete',
      message: 'Analyst Agent completed execution - analysis complete',
      status: 'completed',
      execution_order: 12,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 15 * 1000).toISOString(),
      agent: 'Reporting',
      event_type: 'agent_start',
      message: 'Reporting Agent started execution',
      status: 'completed',
      execution_order: 13,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 16 * 1000).toISOString(),
      agent: 'Reporting',
      event_type: 'task_start',
      message: 'Generating comprehensive analysis report',
      task_name: 'Report Generation',
      status: 'completed',
      execution_order: 14,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 18 * 1000).toISOString(),
      agent: 'Reporting',
      event_type: 'task_complete',
      message: 'Report generation complete',
      task_name: 'Report Generation',
      status: 'completed',
      execution_order: 15,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 19 * 1000).toISOString(),
      agent: 'Reporting',
      event_type: 'task_start',
      message: 'Creating visualizations',
      task_name: 'Visualization Creation',
      status: 'completed',
      execution_order: 16,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 20 * 1000).toISOString(),
      agent: 'Reporting',
      event_type: 'task_complete',
      message: 'Visualizations created successfully',
      task_name: 'Visualization Creation',
      status: 'completed',
      execution_order: 17,
      is_parallel: false
    },
    {
      timestamp: new Date(baseTime.getTime() + 21 * 1000).toISOString(),
      agent: 'Reporting',
      event_type: 'agent_complete',
      message: 'Reporting Agent completed execution - report ready',
      status: 'completed',
      execution_order: 18,
      is_parallel: false
    }
  ];
}

export function getDemoExecutionOrder(): ExecutionOrderEntry[] {
  const baseTime = new Date(Date.now() - 2 * 60 * 1000);
  
  return [
    {
      agent: 'Research',
      start_time: new Date(baseTime.getTime() + 0 * 1000).getTime() / 1000,
      end_time: new Date(baseTime.getTime() + 6 * 1000).getTime() / 1000,
      duration: 6.0
    },
    {
      agent: 'Analyst',
      start_time: new Date(baseTime.getTime() + 7 * 1000).getTime() / 1000,
      end_time: new Date(baseTime.getTime() + 14 * 1000).getTime() / 1000,
      duration: 7.0
    },
    {
      agent: 'Reporting',
      start_time: new Date(baseTime.getTime() + 15 * 1000).getTime() / 1000,
      end_time: new Date(baseTime.getTime() + 21 * 1000).getTime() / 1000,
      duration: 6.0
    }
  ];
}

export function getDemoChatMessage(): ChatMessage {
  return {
    id: `msg_${Date.now()}_demo`,
    session_id: 'demo_session',
    role: 'assistant',
    content: DEMO_ANALYSIS_REPORT,
    timestamp: new Date().toISOString(),
    transaction_id: `txn_${Date.now()}`,
    citations: [
      {
        source: 'Yahoo Finance',
        url: 'https://finance.yahoo.com/quote/AAPL',
        date: new Date().toISOString(),
        data_point: 'Stock Price',
        symbol: 'AAPL'
      },
      {
        source: 'Financial Modeling Prep',
        url: 'https://site.financialmodelingprep.com/stock/AAPL',
        date: new Date().toISOString(),
        data_point: 'Financial Statements',
        symbol: 'AAPL'
      }
    ],
    visualizations: DEMO_VISUALIZATIONS
  };
}

// Exports already defined above


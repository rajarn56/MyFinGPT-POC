"""Gradio UI components"""

import gradio as gr
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def create_analysis_tab():
    """Create Analysis & Report tab"""
    return gr.Markdown(value="# Analysis & Report\n\nResults will appear here after query execution.")


def create_visualizations_tab():
    """Create Trends & Visualizations tab"""
    return gr.Plot(value=None, label="Visualizations")


def create_agent_activity_tab():
    """Create Agent Activity & Token Usage tab"""
    return gr.JSON(value={}, label="Agent Activity & Metrics")


def format_report_markdown(report: str, citations: List[Dict[str, Any]]) -> str:
    """
    Format report with citations
    
    Args:
        report: Report text
        citations: List of citations
    
    Returns:
        Formatted markdown
    """
    formatted = report
    
    # Add citations section
    if citations:
        formatted += "\n\n## Sources and Citations\n\n"
        for i, citation in enumerate(citations, 1):
            source = citation.get("source", "Unknown")
            url = citation.get("url", "")
            date = citation.get("date", "")
            data_point = citation.get("data_point", "")
            
            citation_text = f"{i}. **{source}**"
            if data_point:
                citation_text += f" - {data_point}"
            if date:
                citation_text += f" ({date})"
            if url:
                citation_text += f" - [Link]({url})"
            
            formatted += f"{citation_text}\n"
    
    return formatted


def create_price_trend_chart(visualizations: Dict[str, Any]) -> go.Figure:
    """
    Create price trend chart
    
    Args:
        visualizations: Visualization data
    
    Returns:
        Plotly figure
    """
    price_trends = visualizations.get("price_trends", {})
    
    if not price_trends:
        # Return empty chart
        fig = go.Figure()
        fig.add_annotation(text="No price trend data available", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    fig = go.Figure()
    
    for symbol, data in price_trends.items():
        dates = data.get("dates", [])
        prices = data.get("prices", [])
        
        if dates and prices:
            fig.add_trace(go.Scatter(
                x=dates,
                y=prices,
                mode='lines+markers',
                name=symbol,
                line=dict(width=2)
            ))
    
    fig.update_layout(
        title="Price Trends",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode='x unified',
        height=400
    )
    
    return fig


def create_comparison_chart(visualizations: Dict[str, Any]) -> go.Figure:
    """
    Create comparison chart
    
    Args:
        visualizations: Visualization data
    
    Returns:
        Plotly figure
    """
    comparison_data = visualizations.get("comparison_charts", {})
    
    if not comparison_data:
        fig = go.Figure()
        fig.add_annotation(text="No comparison data available", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    symbols = list(comparison_data.keys())
    prices = [comparison_data[s].get("current_price", 0) for s in symbols]
    market_caps = [comparison_data[s].get("market_cap", 0) for s in symbols]
    
    fig = go.Figure()
    
    # Price comparison
    fig.add_trace(go.Bar(
        x=symbols,
        y=prices,
        name="Current Price",
        yaxis='y',
        offsetgroup=1
    ))
    
    fig.update_layout(
        title="Stock Comparison",
        xaxis_title="Symbol",
        yaxis_title="Price ($)",
        height=400,
        barmode='group'
    )
    
    return fig


def create_sentiment_chart(visualizations: Dict[str, Any]) -> go.Figure:
    """
    Create sentiment analysis chart
    
    Args:
        visualizations: Visualization data
    
    Returns:
        Plotly figure
    """
    sentiment_data = visualizations.get("sentiment_charts", {})
    
    if not sentiment_data:
        fig = go.Figure()
        fig.add_annotation(text="No sentiment data available", xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    symbols = list(sentiment_data.keys())
    scores = [sentiment_data[s].get("score", 0) for s in symbols]
    
    colors = ['green' if s > 0 else 'red' if s < 0 else 'gray' for s in scores]
    
    fig = go.Figure(data=go.Bar(
        x=symbols,
        y=scores,
        marker_color=colors,
        text=[f"{s:.2f}" for s in scores],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Sentiment Analysis",
        xaxis_title="Symbol",
        yaxis_title="Sentiment Score (-1 to 1)",
        height=400
    )
    
    return fig


def format_agent_activity(transaction_id: str, token_usage: Dict[str, int], execution_time: Dict[str, float],
                          agents_executed: List[str], context_size: int,
                          progress_events: Optional[List[Dict[str, Any]]] = None,
                          execution_order: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Format agent activity data for display
    
    Args:
        transaction_id: Transaction identifier
        token_usage: Token usage per agent
        execution_time: Execution time per agent
        agents_executed: List of executed agents
        context_size: Context size in bytes
        progress_events: Optional list of progress events
        execution_order: Optional execution order entries
    
    Returns:
        Formatted activity data
    """
    activity = {
        "transaction_id": transaction_id,
        "agents_executed": agents_executed,
        "token_usage": token_usage,
        "execution_time": execution_time,
        "context_size_bytes": context_size,
        "context_size_kb": round(context_size / 1024, 2),
        "total_tokens": sum(token_usage.values()),
        "total_time": sum(execution_time.values())
    }
    
    if progress_events:
        activity["progress_events_count"] = len(progress_events)
        activity["latest_progress"] = progress_events[-1] if progress_events else None
    
    if execution_order:
        activity["execution_order"] = execution_order
    
    return activity


def format_progress_markdown(progress_events: List[Dict[str, Any]]) -> str:
    """
    Format progress events as markdown
    
    Args:
        progress_events: List of progress events
    
    Returns:
        Formatted markdown string
    """
    from .progress_display import format_progress_events_markdown
    return format_progress_events_markdown(progress_events)


def create_progress_timeline_chart(execution_order: List[Dict[str, Any]]) -> go.Figure:
    """
    Create progress timeline chart
    
    Args:
        execution_order: Execution order entries
    
    Returns:
        Plotly figure
    """
    from .progress_display import create_execution_timeline
    return create_execution_timeline(execution_order)


def format_agent_status(current_agent: Optional[str], tasks: Dict[str, List[str]]) -> str:
    """
    Format agent status for display
    
    Args:
        current_agent: Currently executing agent
        tasks: Current tasks per agent
    
    Returns:
        Formatted markdown string
    """
    from .progress_display import create_agent_status_display
    return create_agent_status_display(current_agent, tasks)


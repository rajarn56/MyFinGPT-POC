"""Progress display components for UI"""

import gradio as gr
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
from datetime import datetime
from ..utils.progress_tracker import ProgressTracker


def create_progress_panel() -> gr.Column:
    """
    Create main progress display panel
    
    Returns:
        Gradio Column component with progress display
    """
    with gr.Column() as progress_panel:
        gr.Markdown("### Execution Progress")
        
        current_agent_display = gr.Markdown(
            value="**Current Agent:** Waiting for query...",
            label="Current Status"
        )
        
        active_tasks_display = gr.Markdown(
            value="**Active Tasks:** None",
            label="Active Tasks"
        )
        
        progress_events_display = gr.Markdown(
            value="**Progress Events:**\n\nWaiting for execution...",
            label="Progress Log"
        )
        
        execution_timeline_display = gr.Plot(
            label="Execution Timeline"
        )
    
    return progress_panel


def format_progress_event(event: Dict[str, Any]) -> str:
    """
    Format individual progress event for display with API call status indicators
    
    Args:
        event: Progress event dictionary
    
    Returns:
        Formatted string with status indicators
    """
    event_type = event.get("event_type", "")
    
    # Handle API call events with status indicators
    if event_type in ["api_call_start", "api_call_success", "api_call_failed", "api_call_skipped"]:
        integration = event.get("integration", "Unknown")
        symbol = event.get("symbol", "")
        status = event.get("status", "")
        error = event.get("error")
        
        # Status indicators
        status_indicators = {
            "success": "✓",
            "failed": "✗",
            "skipped": "⊘",
            "running": "⟳"
        }
        indicator = status_indicators.get(status, "")
        
        # Format message
        if event_type == "api_call_start":
            message = f"{indicator} {integration} API call started for {symbol}"
        elif event_type == "api_call_success":
            message = f"{indicator} {integration} API call succeeded for {symbol}"
        elif event_type == "api_call_failed":
            error_msg = f" - {error}" if error else ""
            message = f"{indicator} {integration} API call failed for {symbol}{error_msg}"
        elif event_type == "api_call_skipped":
            reason = event.get("message", "Integration disabled")
            message = f"{indicator} {integration} API call skipped for {symbol} ({reason})"
        else:
            message = ProgressTracker.format_event_for_ui(event)
        
        # Add timestamp
        timestamp = event.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = timestamp[:8] if len(timestamp) >= 8 else timestamp
            return f"[{time_str}] {message}"
        
        return message
    
    # Use default formatting for other events
    return ProgressTracker.format_event_for_ui(event)


def create_execution_timeline(execution_order: List[Dict[str, Any]]) -> go.Figure:
    """
    Create visual timeline of execution
    
    Args:
        execution_order: List of execution order entries
    
    Returns:
        Plotly figure
    """
    if not execution_order:
        fig = go.Figure()
        fig.add_annotation(
            text="No execution data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False
        )
        return fig
    
    # Prepare data for timeline
    agents = []
    start_times = []
    durations = []
    
    for entry in execution_order:
        agent = entry.get("agent", "Unknown")
        start_time = entry.get("start_time", 0)
        duration = entry.get("duration")
        
        if duration is None:
            # If still running, use current time
            import time
            duration = time.time() - start_time if start_time > 0 else 0
        
        agents.append(agent)
        start_times.append(start_time)
        durations.append(duration)
    
    # Normalize start times to start from 0
    if start_times:
        min_start = min(start_times)
        normalized_starts = [(s - min_start) for s in start_times]
    else:
        normalized_starts = [0] * len(agents)
    
    # Create Gantt-style chart
    fig = go.Figure()
    
    for i, (agent, start, duration) in enumerate(zip(agents, normalized_starts, durations)):
        fig.add_trace(go.Bar(
            x=[duration],
            y=[agent],
            base=[start],
            orientation='h',
            name=agent,
            text=[f"{duration:.2f}s"],
            textposition='inside',
            marker=dict(
                color=f'hsl({i * 60 % 360}, 70%, 50%)',
                line=dict(width=1, color='black')
            )
        ))
    
    fig.update_layout(
        title="Agent Execution Timeline",
        xaxis_title="Time (seconds)",
        yaxis_title="Agent",
        barmode='overlay',
        height=max(300, len(agents) * 50),
        showlegend=False
    )
    
    return fig


def create_agent_status_display(current_agent: Optional[str], current_tasks: Dict[str, List[str]]) -> str:
    """
    Format current agent status for display
    
    Args:
        current_agent: Currently executing agent name
        current_tasks: Dictionary mapping agent names to active task lists
    
    Returns:
        Formatted markdown string
    """
    if not current_agent:
        return "**Current Agent:** Waiting for execution to start..."
    
    status_text = f"**Current Agent:** {current_agent}\n\n"
    
    # Get tasks for current agent
    agent_tasks = current_tasks.get(current_agent, [])
    if agent_tasks:
        status_text += "**Active Tasks:**\n"
        for task in agent_tasks:
            status_text += f"- {task}\n"
    else:
        status_text += "**Active Tasks:** None\n"
    
    return status_text


def format_progress_events_markdown(progress_events: List[Dict[str, Any]], max_events: int = 20) -> str:
    """
    Format progress events as markdown with API call status indicators
    
    Args:
        progress_events: List of progress events
        max_events: Maximum number of events to display
    
    Returns:
        Formatted markdown string with status indicators
    """
    if not progress_events:
        return "**Progress Events:**\n\nNo events yet."
    
    # Get most recent events
    recent_events = progress_events[-max_events:]
    
    markdown = "**Progress Events:**\n\n"
    
    # Group API call events by integration for better readability
    api_call_events = []
    other_events = []
    
    for event in recent_events:
        event_type = event.get("event_type", "")
        if event_type in ["api_call_start", "api_call_success", "api_call_failed", "api_call_skipped"]:
            api_call_events.append(event)
        else:
            other_events.append(event)
    
    # Format API call events with status indicators
    for event in api_call_events:
        formatted = format_progress_event(event)
        markdown += f"- {formatted}\n"
    
    # Format other events
    for event in other_events:
        formatted = format_progress_event(event)
        markdown += f"- {formatted}\n"
    
    if len(progress_events) > max_events:
        markdown += f"\n*... and {len(progress_events) - max_events} more events*\n"
    
    # Add API call summary if there are API events
    if api_call_events:
        success_count = sum(1 for e in api_call_events if e.get("status") == "success")
        failed_count = sum(1 for e in api_call_events if e.get("status") == "failed")
        skipped_count = sum(1 for e in api_call_events if e.get("status") == "skipped")
        
        markdown += f"\n**API Call Summary:** ✓ {success_count} succeeded, ✗ {failed_count} failed, ⊘ {skipped_count} skipped\n"
    
    return markdown


def update_progress_display(
    progress_events: List[Dict[str, Any]],
    current_agent: Optional[str],
    current_tasks: Dict[str, List[str]],
    execution_order: List[Dict[str, Any]]
) -> tuple:
    """
    Update all progress display components
    
    Args:
        progress_events: List of progress events
        current_agent: Currently executing agent
        current_tasks: Current tasks per agent
        execution_order: Execution order entries
    
    Returns:
        Tuple of (agent_status, tasks_display, events_display, timeline_figure)
    """
    # Format agent status
    agent_status = create_agent_status_display(current_agent, current_tasks)
    
    # Format active tasks
    if current_agent and current_tasks.get(current_agent):
        tasks_text = "**Active Tasks:**\n"
        for task in current_tasks[current_agent]:
            tasks_text += f"- {task}\n"
    else:
        tasks_text = "**Active Tasks:** None"
    
    # Format progress events
    events_markdown = format_progress_events_markdown(progress_events)
    
    # Create timeline
    timeline_figure = create_execution_timeline(execution_order)
    
    return agent_status, tasks_text, events_markdown, timeline_figure


"""Streamlit UI application for MyFinGPT"""

import streamlit as st
from typing import Dict, Any, Optional
from loguru import logger
import time
import os
import sys
from pathlib import Path

# Add project root to Python path for imports when run directly by Streamlit
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now use absolute imports that work both when run directly and as module
from src.orchestrator.workflow import MyFinGPTWorkflow
from src.utils.guardrails import GuardrailsError
from src.ui.components import (
    format_report_markdown,
    create_price_trend_chart,
    create_comparison_chart,
    create_sentiment_chart,
    format_agent_activity
)
from src.ui.progress_display import (
    update_progress_display,
    format_progress_events_markdown,
    create_execution_timeline,
    create_agent_status_display
)


# Example queries
EXAMPLE_QUERIES = [
    "Analyze Apple Inc. (AAPL) stock",
    "Compare AAPL, MSFT, and GOOGL",
    "What are the current trends in tech stocks?",
    "Analyze Tesla (TSLA) stock including sentiment analysis",
    "Compare the top 5 technology stocks by market cap"
]


class MyFinGPTStreamlitUI:
    """Streamlit UI for MyFinGPT"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize UI
        
        Args:
            llm_provider: LLM provider name
        """
        self.workflow = MyFinGPTWorkflow(llm_provider=llm_provider)
    
    def process_query(self, query: str):
        """
        Process user query with real-time streaming progress updates
        
        Args:
            query: User query
        """
        start_time = time.time()
        logger.info(f"[UI] User query received | Length: {len(query)} chars | Query: {query[:100]}...")
        
        if not query or not query.strip():
            logger.warning("[UI] Empty query received")
            return {
                "report": "Please enter a query.",
                "plot_figure": None,
                "agent_activity": {},
                "agent_status": "**Current Agent:** Waiting for query...",
                "tasks_text": "**Active Tasks:** None",
                "events_markdown": "**Progress Events:**\n\nNo events yet.",
                "events_log_markdown": "**Progress Events Log:**\n\nNo events yet.",
                "timeline_fig": None
            }
        
        # Initialize progress display
        progress_events = []
        current_agent = None
        current_tasks = {}
        execution_order = []
        final_state = None
        result = None
        
        # Initialize outputs
        report_with_id = "# Analysis & Report\n\nProcessing query..."
        plot_figure = None
        agent_activity = {}
        agent_status = "**Current Agent:** Initializing..."
        tasks_text = "**Active Tasks:** None"
        events_markdown = "**Progress Events:**\n\nStarting execution..."
        events_log_markdown = "**Progress Events Log:**\n\nStarting execution..."
        timeline_fig = None
        
        try:
            logger.debug("[UI] Workflow initialization started")
            
            # Use streaming to get REAL-TIME progress updates
            try:
                for update in self.workflow.stream_query(query):
                    # Extract progress information from stream update
                    state = update.get("state", {})
                    progress_events = state.get("progress_events", [])
                    current_agent = state.get("current_agent")
                    current_tasks = state.get("current_tasks", {})
                    execution_order = state.get("execution_order", [])
                    final_state = state
                    
                    # Update progress display in real-time
                    agent_status, tasks_text, events_markdown, events_log_markdown, timeline_fig = update_progress_display(
                        progress_events, current_agent, current_tasks, execution_order
                    )
                    
                    logger.debug(f"[UI] Progress update | Agent: {current_agent} | Events: {len(progress_events)}")
                
                # If streaming completed, use final_state
                if final_state:
                    result = {
                        "transaction_id": final_state.get("transaction_id", "unknown"),
                        "report": final_state.get("final_report", ""),
                        "citations": final_state.get("citations", []),
                        "visualizations": final_state.get("visualizations", {}),
                        "token_usage": final_state.get("token_usage", {}),
                        "execution_time": final_state.get("execution_time", {}),
                        "agents_executed": final_state.get("agents_executed", []),
                        "context_size": final_state.get("context_size", 0),
                        "progress_events": progress_events,
                        "execution_order": execution_order
                    }
                else:
                    # Fallback to non-streaming
                    result = self.workflow.process_query(query)
            except Exception as stream_error:
                logger.warning(f"[UI] Streaming failed, falling back to non-streaming: {stream_error}")
                # Fallback to non-streaming
                result = self.workflow.process_query(query)
            
            transaction_id = result.get("transaction_id", "unknown")
            logger.debug(f"[UI] Workflow processing completed | Transaction ID: {transaction_id}")
            
            # Format report
            report = format_report_markdown(
                result.get("report", "No report generated."),
                result.get("citations", [])
            )
            logger.debug(f"[UI] Report formatted | Length: {len(report)} chars")
            
            # Create visualizations
            visualizations = result.get("visualizations", {})
            charts = []
            
            # Price trend chart
            if visualizations.get("price_trends"):
                charts.append(create_price_trend_chart(visualizations))
                logger.debug("[UI] Price trend chart created")
            
            # Comparison chart
            if visualizations.get("comparison_charts"):
                charts.append(create_comparison_chart(visualizations))
                logger.debug("[UI] Comparison chart created")
            
            # Sentiment chart
            if visualizations.get("sentiment_charts"):
                charts.append(create_sentiment_chart(visualizations))
                logger.debug("[UI] Sentiment chart created")
            
            # Combine charts if multiple
            if len(charts) == 1:
                plot_figure = charts[0]
            elif len(charts) > 1:
                # Use first chart for now (could combine multiple)
                plot_figure = charts[0]
            else:
                plot_figure = None
            
            # Format agent activity
            agent_activity = format_agent_activity(
                transaction_id=transaction_id,
                token_usage=result.get("token_usage", {}),
                execution_time=result.get("execution_time", {}),
                agents_executed=result.get("agents_executed", []),
                context_size=result.get("context_size", 0),
                progress_events=result.get("progress_events", []),
                execution_order=result.get("execution_order", [])
            )
            
            # Final progress display update
            final_progress_events = result.get("progress_events", progress_events)
            final_current_agent = result.get("current_agent", current_agent)
            final_current_tasks = result.get("current_tasks", current_tasks)
            final_execution_order = result.get("execution_order", execution_order)
            
            agent_status, tasks_text, events_markdown, events_log_markdown, timeline_fig = update_progress_display(
                final_progress_events, final_current_agent, final_current_tasks, final_execution_order
            )
            
            total_time = time.time() - start_time
            logger.info(f"[UI] Query processing completed successfully | "
                       f"Transaction ID: {transaction_id} | "
                       f"Total time: {total_time:.2f}s | "
                       f"Charts: {len(charts)} | "
                       f"Citations: {len(result.get('citations', []))}")
            
            # Add transaction ID to report header
            report_with_id = f"**Transaction ID:** `{transaction_id}`\n\n---\n\n{report}"
            
            # Return final result
            return {
                "report": report_with_id,
                "plot_figure": plot_figure,
                "agent_activity": agent_activity,
                "agent_status": agent_status,
                "tasks_text": tasks_text,
                "events_markdown": events_markdown,
                "events_log_markdown": events_log_markdown,
                "timeline_fig": timeline_fig
            }
        
        except GuardrailsError as e:
            total_time = time.time() - start_time
            logger.warning(f"[UI] Guardrails validation failed after {total_time:.2f}s: {e}")
            error_msg = f"**Query Validation Error**\n\n{str(e)}\n\nPlease ensure your query is:\n- Related to financial analysis (stocks, companies, markets)\n- Contains valid stock symbols (e.g., AAPL, MSFT)\n- Does not contain unsafe or inappropriate content"
            return {
                "report": error_msg,
                "plot_figure": None,
                "agent_activity": {},
                "agent_status": "**Current Agent:** Error occurred",
                "tasks_text": "**Active Tasks:** None",
                "events_markdown": f"**Progress Events:**\n\nError: {str(e)}",
                "events_log_markdown": f"**Progress Events Log:**\n\nError: {str(e)}",
                "timeline_fig": None
            }
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"[UI] Error processing query after {total_time:.2f}s: {e}", exc_info=True)
            error_msg = f"Error processing query: {str(e)}\n\nPlease check your API keys and try again."
            return {
                "report": error_msg,
                "plot_figure": None,
                "agent_activity": {},
                "agent_status": "**Current Agent:** Error occurred",
                "tasks_text": "**Active Tasks:** None",
                "events_markdown": f"**Progress Events:**\n\nError: {str(e)}",
                "events_log_markdown": f"**Progress Events Log:**\n\nError: {str(e)}",
                "timeline_fig": None
            }
    
    def create_interface(self):
        """Create Streamlit interface with two-column layout and dark theme"""
        # Page configuration
        st.set_page_config(
            page_title="MyFinGPT - Multi-Agent Financial Analysis",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Custom dark theme CSS with improved text visibility
        st.markdown("""
        <style>
            /* Main app background */
            .stApp {
                background-color: #0e1117;
            }
            
            /* Headers - bright and visible */
            h1 {
                color: #ffffff !important;
                font-weight: 700;
            }
            
            h2, h3 {
                color: #e0e0e0 !important;
                font-weight: 600;
            }
            
            /* All markdown text - bright white */
            .stMarkdown {
                color: #ffffff !important;
            }
            
            .stMarkdown p {
                color: #ffffff !important;
            }
            
            .stMarkdown li {
                color: #ffffff !important;
            }
            
            .stMarkdown strong {
                color: #ffffff !important;
                font-weight: 700;
            }
            
            /* Labels - bright white */
            label {
                color: #ffffff !important;
                font-weight: 500;
            }
            
            .stSelectbox label,
            .stTextArea label {
                color: #ffffff !important;
                font-weight: 500;
            }
            
            /* Text areas and inputs */
            .stTextArea textarea {
                background-color: #262730;
                color: #ffffff !important;
                border: 1px solid #4a4a4a;
            }
            
            /* Selectbox */
            .stSelectbox label {
                color: #ffffff !important;
            }
            
            .stSelectbox select {
                background-color: #262730 !important;
                color: #ffffff !important;
                border: 1px solid #4a4a4a !important;
            }
            
            .stSelectbox [data-baseweb="select"] {
                background-color: #262730 !important;
                color: #ffffff !important;
            }
            
            .stSelectbox [data-baseweb="select"] > div {
                background-color: #262730 !important;
                color: #ffffff !important;
            }
            
            /* Selectbox dropdown options */
            [data-baseweb="popover"] {
                background-color: #262730 !important;
            }
            
            [data-baseweb="menu"] {
                background-color: #262730 !important;
            }
            
            [data-baseweb="option"] {
                background-color: #262730 !important;
                color: #ffffff !important;
            }
            
            [data-baseweb="option"]:hover {
                background-color: #3a3a4a !important;
                color: #ffffff !important;
            }
            
            /* Buttons */
            .stButton > button {
                background-color: #1f77b4;
                color: #ffffff !important;
                border: none;
                font-weight: 600;
            }
            
            .stButton > button:hover {
                background-color: #1a5d8f;
            }
            
            /* Info boxes */
            .stInfo {
                background-color: #1e3a5f;
                color: #ffffff !important;
            }
            
            /* Scrollable containers - brighter background, white text */
            .scrollable-container {
                max-height: 200px;
                overflow-y: auto;
                padding: 15px;
                background-color: #1a1a1a;
                border-radius: 5px;
                margin: 10px 0;
                border: 1px solid #333333;
            }
            
            .scrollable-container p,
            .scrollable-container li,
            .scrollable-container strong {
                color: #ffffff !important;
            }
            
            .scrollable-container-large {
                max-height: 600px;
                overflow-y: auto;
                padding: 15px;
                background-color: #1a1a1a;
                border-radius: 5px;
                margin: 10px 0;
                border: 1px solid #333333;
            }
            
            .scrollable-container-large p,
            .scrollable-container-large li,
            .scrollable-container-large strong,
            .scrollable-container-large h1,
            .scrollable-container-large h2,
            .scrollable-container-large h3 {
                color: #ffffff !important;
            }
            
            /* Markdown containers */
            .markdown-container {
                padding: 15px;
                background-color: #1a1a1a;
                border-radius: 5px;
                margin: 10px 0;
                border: 1px solid #333333;
            }
            
            /* Tabs */
            .stTabs [data-baseweb="tab-list"] {
                background-color: #1a1a1a;
            }
            
            .stTabs [data-baseweb="tab"] {
                color: #ffffff !important;
            }
            
            /* JSON display - Agent Activity */
            .stJson {
                background-color: #1a1a1a !important;
                color: #ffffff !important;
            }
            
            .stJson pre {
                background-color: #1a1a1a !important;
                color: #ffffff !important;
            }
            
            .stJson code {
                background-color: #1a1a1a !important;
                color: #ffffff !important;
            }
            
            /* JSON viewer specific styling */
            [data-testid="stJson"] {
                background-color: #1a1a1a !important;
            }
            
            [data-testid="stJson"] pre {
                background-color: #1a1a1a !important;
                color: #ffffff !important;
            }
            
            /* Ensure JSON text is visible */
            .jsonschema-table,
            .jsonschema-table td,
            .jsonschema-table th {
                background-color: #1a1a1a !important;
                color: #ffffff !important;
                border-color: #333333 !important;
            }
            
            /* General text elements */
            p, span, div {
                color: #ffffff !important;
            }
            
            /* Code blocks */
            code {
                background-color: #2a2a2a;
                color: #4ec9b0 !important;
                padding: 2px 6px;
                border-radius: 3px;
            }
            
            pre {
                background-color: #2a2a2a;
                color: #4ec9b0 !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.title("MyFinGPT - Multi-Agent Financial Analysis System")
        st.markdown("Ask questions about stocks, compare companies, analyze trends, and get comprehensive financial insights.")
        
        # Initialize session state
        if "query_result" not in st.session_state:
            st.session_state.query_result = None
        if "query_input" not in st.session_state:
            st.session_state.query_input = ""
        
        # Two-column layout
        col1, col2 = st.columns([1, 1], gap="medium")
        
        with col1:
            st.markdown("### Query & Progress")
            
            # Query input
            query_input = st.text_area(
                "Enter your financial query",
                value=st.session_state.query_input,
                placeholder="e.g., Analyze Apple Inc. (AAPL) stock",
                height=100,
                key="query_textarea"
            )
            
            # Example queries
            example_query = st.selectbox(
                "Example Queries",
                options=[None] + EXAMPLE_QUERIES,
                format_func=lambda x: "Select an example..." if x is None else x,
                key="example_selectbox"
            )
            
            # Update query input if example selected
            if example_query:
                st.session_state.query_input = example_query
                st.rerun()
            
            # Buttons
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_btn = st.button("Submit Query", type="primary", use_container_width=True)
            with col_btn2:
                clear_btn = st.button("Clear", use_container_width=True)
            
            # Handle clear button
            if clear_btn:
                st.session_state.query_result = None
                st.session_state.query_input = ""
                st.rerun()
            
            # Process query on submit
            if submit_btn and query_input:
                with st.spinner("Processing query..."):
                    result = self.process_query(query_input)
                    st.session_state.query_result = result
                    st.session_state.query_input = query_input
            
            # Progress panels
            st.markdown("---")
            st.markdown("### Execution Progress")
            
            # Progress status container
            progress_status_container = st.empty()
            progress_tasks_container = st.empty()
            
            # Execution timeline container
            st.markdown("### Execution Timeline")
            progress_timeline_container = st.empty()
            
            # Progress events container
            st.markdown("### Progress Events")
            progress_events_container = st.empty()
            
            # Progress events log container
            st.markdown("### Progress Events Log")
            progress_events_log_container = st.empty()
            
            # Update progress displays if result exists
            if st.session_state.query_result:
                progress_status_container.markdown(st.session_state.query_result.get("agent_status", "**Current Agent:** Waiting for query..."))
                progress_tasks_container.markdown(st.session_state.query_result.get("tasks_text", "**Active Tasks:** None"))
                
                timeline_fig = st.session_state.query_result.get("timeline_fig")
                if timeline_fig:
                    progress_timeline_container.plotly_chart(timeline_fig, use_container_width=True)
                else:
                    progress_timeline_container.info("No execution timeline data available yet.")
                
                # Scrollable progress events
                events_md = st.session_state.query_result.get("events_markdown", "**Progress Events:**\n\nWaiting for execution...")
                progress_events_container.markdown(f'<div class="scrollable-container">{events_md}</div>', unsafe_allow_html=True)
                
                # Scrollable progress events log
                events_log_md = st.session_state.query_result.get("events_log_markdown", "**Progress Events Log:**\n\nWaiting for execution...")
                progress_events_log_container.markdown(f'<div class="scrollable-container">{events_log_md}</div>', unsafe_allow_html=True)
            else:
                progress_status_container.markdown("**Current Agent:** Waiting for query...")
                progress_tasks_container.markdown("**Active Tasks:** None")
                progress_timeline_container.info("No execution timeline data available yet.")
                progress_events_container.markdown("**Progress Events:**\n\nWaiting for execution...")
                progress_events_log_container.markdown("**Progress Events Log:**\n\nWaiting for execution...")
        
        with col2:
            st.markdown("### Results")
            
            # Tabs for results
            tab1, tab2, tab3 = st.tabs(["Analysis & Report", "Visualizations", "Agent Activity"])
            
            with tab1:
                if st.session_state.query_result:
                    report = st.session_state.query_result.get("report", "# Analysis & Report\n\nEnter a query above to get started.")
                    st.markdown(f'<div class="scrollable-container-large">{report}</div>', unsafe_allow_html=True)
                else:
                    st.markdown("# Analysis & Report\n\nEnter a query above to get started.")
            
            with tab2:
                if st.session_state.query_result:
                    plot_fig = st.session_state.query_result.get("plot_figure")
                    if plot_fig:
                        st.plotly_chart(plot_fig, use_container_width=True)
                    else:
                        st.info("No visualization data available. Submit a query to generate charts.")
                else:
                    st.info("No visualization data available. Submit a query to generate charts.")
            
            with tab3:
                if st.session_state.query_result:
                    agent_activity = st.session_state.query_result.get("agent_activity", {})
                    st.json(agent_activity)
                else:
                    st.json({})


def main():
    """Main entry point for Streamlit UI - creates the interface"""
    # Get LLM provider from environment
    llm_provider = os.getenv("LITELLM_PROVIDER", None)
    
    # Initialize UI
    ui = MyFinGPTStreamlitUI(llm_provider=llm_provider)
    
    # Create and run interface
    ui.create_interface()


# Streamlit runs this script directly, so create interface at module level
# This ensures the interface is created when streamlit run is executed
if __name__ == "__main__":
    main()
else:
    # When imported as module (e.g., from main.py), create interface
    main()


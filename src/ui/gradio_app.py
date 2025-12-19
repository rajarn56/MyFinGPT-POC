"""Gradio UI application for MyFinGPT"""

import gradio as gr
from typing import Dict, Any, Optional
from loguru import logger
import os

from ..orchestrator.workflow import MyFinGPTWorkflow
from ..utils.guardrails import GuardrailsError
from .components import (
    format_report_markdown,
    create_price_trend_chart,
    create_comparison_chart,
    create_sentiment_chart,
    format_agent_activity
)
from .progress_display import (
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


class MyFinGPTUI:
    """Gradio UI for MyFinGPT"""
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Initialize UI
        
        Args:
            llm_provider: LLM provider name
        """
        self.workflow = MyFinGPTWorkflow(llm_provider=llm_provider)
        self.app = None
    
    def process_query(self, query: str, progress=gr.Progress()):
        """
        Process user query with REAL-TIME streaming progress updates
        
        This is a generator function that yields updates as they occur,
        enabling real-time progress display in the UI.
        
        Args:
            query: User query
            progress: Gradio progress tracker
        
        Yields:
            Tuple of (report, visualizations, agent_activity, progress_status, progress_tasks, progress_events, progress_events_log, progress_timeline)
            Yields multiple times as progress updates occur
        """
        import time
        start_time = time.time()
        logger.info(f"[UI] User query received | Length: {len(query)} chars | Query: {query[:100]}...")
        
        if not query or not query.strip():
            logger.warning("[UI] Empty query received")
            yield ("Please enter a query.", None, {}, 
                   "**Current Agent:** Waiting for query...",
                   "**Active Tasks:** None",
                   "**Progress Events:**\n\nNo events yet.",
                   "**Progress Events Log:**\n\nNo events yet.",
                   None)
            return
        
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
            progress(0.1, desc="Initializing workflow...")
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
                    
                    # Yield REAL-TIME progress update
                    yield (report_with_id, plot_figure, agent_activity,
                          agent_status, tasks_text, events_markdown, events_log_markdown, timeline_fig)
                    
                    logger.debug(f"[UI] Progress update yielded | Agent: {current_agent} | Events: {len(progress_events)}")
                
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
            
            progress(0.9, desc="Generating report...")
            
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
            
            progress(1.0, desc="Complete!")
            
            total_time = time.time() - start_time
            logger.info(f"[UI] Query processing completed successfully | "
                       f"Transaction ID: {transaction_id} | "
                       f"Total time: {total_time:.2f}s | "
                       f"Charts: {len(charts)} | "
                       f"Citations: {len(result.get('citations', []))}")
            
            # Add transaction ID to report header
            report_with_id = f"**Transaction ID:** `{transaction_id}`\n\n---\n\n{report}"
            
            # Yield final result
            yield (report_with_id, plot_figure, agent_activity, 
                  agent_status, tasks_text, events_markdown, events_log_markdown, timeline_fig)
        
        except GuardrailsError as e:
            total_time = time.time() - start_time
            logger.warning(f"[UI] Guardrails validation failed after {total_time:.2f}s: {e}")
            error_msg = f"**Query Validation Error**\n\n{str(e)}\n\nPlease ensure your query is:\n- Related to financial analysis (stocks, companies, markets)\n- Contains valid stock symbols (e.g., AAPL, MSFT)\n- Does not contain unsafe or inappropriate content"
            yield (error_msg, None, {}, 
                  "**Current Agent:** Error occurred",
                  "**Active Tasks:** None",
                  f"**Progress Events:**\n\nError: {str(e)}",
                  f"**Progress Events Log:**\n\nError: {str(e)}",
                  None)
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"[UI] Error processing query after {total_time:.2f}s: {e}", exc_info=True)
            error_msg = f"Error processing query: {str(e)}\n\nPlease check your API keys and try again."
            yield (error_msg, None, {},
                  "**Current Agent:** Error occurred",
                  "**Active Tasks:** None",
                  f"**Progress Events:**\n\nError: {str(e)}",
                  f"**Progress Events Log:**\n\nError: {str(e)}",
                  None)
    
    def create_interface(self):
        """Create Gradio interface"""
        # Custom CSS for responsive viewport-based heights
        # Using viewport height (vh) units for responsive sizing
        responsive_css = """
        /* Main container - use full viewport height */
        .gradio-container {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* Horizontal split row - main content area */
        .main-row {
            flex: 1 1 auto;
            height: calc(100vh - 180px);
            min-height: 500px;
            display: flex;
            overflow: hidden;
        }
        
        /* Columns - flexbox for space distribution */
        .left-column,
        .right-column {
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow-y: auto;
            overflow-x: hidden;
            flex: 1 1 50%;
        }
        
        /* Query input - responsive height (8vh with min 80px) */
        .query-input {
            height: 8vh !important;
            min-height: 80px !important;
            max-height: 120px;
        }
        
        /* Progress status - responsive height (4vh with min 40px) */
        .progress-status {
            height: 4vh !important;
            min-height: 40px !important;
            max-height: 80px;
        }
        
        /* Progress tasks - responsive height (4vh with min 40px) */
        .progress-tasks {
            height: 4vh !important;
            min-height: 40px !important;
            max-height: 80px;
        }
        
        /* Execution timeline plot - responsive height (15vh with min 150px) */
        .progress-timeline {
            height: 15vh !important;
            min-height: 150px !important;
            max-height: 300px;
        }
        
        /* Progress events panels - responsive heights (15vh with min 150px) */
        .progress-events,
        .progress-events-log {
            height: 15vh !important;
            min-height: 150px !important;
            max-height: 250px;
            flex: 1 1 auto;
        }
        
        /* Tab container - fill remaining space in right column */
        .result-tabs {
            height: 100%;
            min-height: 400px;
            display: flex;
            flex-direction: column;
        }
        
        /* Tab content components - responsive heights */
        .tab-content {
            height: calc(100vh - 250px) !important;
            min-height: 400px !important;
        }
        
        /* Ensure scrollable content works */
        .gr-markdown,
        .gr-plot,
        .gr-json {
            overflow-y: auto;
        }
        """
        
        with gr.Blocks(title="MyFinGPT - Multi-Agent Financial Analysis", theme=gr.themes.Soft(), css=responsive_css) as app:
            gr.Markdown("# MyFinGPT - Multi-Agent Financial Analysis System")
            gr.Markdown("Ask questions about stocks, compare companies, analyze trends, and get comprehensive financial insights.")
            
            # Horizontal split layout (50/50)
            with gr.Row(elem_classes=["main-row"]):
                # Left Column (50%) - Input and Progress
                with gr.Column(scale=1, elem_classes=["left-column"]):
                    query_input = gr.Textbox(
                        label="Enter your financial query",
                        placeholder="e.g., Analyze Apple Inc. (AAPL) stock",
                        lines=3,
                        elem_classes=["query-input"]
                    )
                    
                    example_queries = gr.Dropdown(
                        label="Example Queries",
                        choices=EXAMPLE_QUERIES,
                        value=None
                    )
                    
                    with gr.Row():
                        submit_btn = gr.Button("Submit Query", variant="primary")
                        clear_btn = gr.Button("Clear")
                    
                    # Execution Progress Panel
                    gr.Markdown("### Execution Progress")
                    progress_status = gr.Markdown(
                        value="**Current Agent:** Waiting for query...",
                        label="Current Status",
                        elem_classes=["progress-status"]
                    )
                    progress_tasks = gr.Markdown(
                        value="**Active Tasks:** None",
                        label="Active Tasks",
                        elem_classes=["progress-tasks"]
                    )
                    
                    # Execution Timeline Panel
                    gr.Markdown("### Execution Timeline")
                    progress_timeline = gr.Plot(
                        label="Execution Timeline",
                        elem_classes=["progress-timeline"]
                    )
                    
                    # Progress Events Panel (scrollable)
                    gr.Markdown("### Progress Events")
                    progress_events = gr.Markdown(
                        value="**Progress Events:**\n\nWaiting for execution...",
                        label="Progress Events",
                        elem_classes=["progress-events"]
                    )
                    
                    # Progress Events Log Panel (scrollable)
                    gr.Markdown("### Progress Events Log")
                    progress_events_log = gr.Markdown(
                        value="**Progress Events Log:**\n\nWaiting for execution...",
                        label="Progress Events Log",
                        elem_classes=["progress-events-log"]
                    )
                
                # Right Column (50%) - Result Tabs
                with gr.Column(scale=1, elem_classes=["right-column"]):
                    with gr.Tabs(elem_classes=["result-tabs"]):
                        with gr.Tab("Analysis & Report"):
                            report_output = gr.Markdown(
                                value="# Analysis & Report\n\nEnter a query above to get started.",
                                label="Report",
                                elem_classes=["tab-content"]
                            )
                        
                        with gr.Tab("Visualizations"):
                            visualization_output = gr.Plot(
                                label="Charts and Visualizations",
                                elem_classes=["tab-content"]
                            )
                        
                        with gr.Tab("Agent Activity"):
                            agent_activity_output = gr.JSON(
                                label="Agent Execution Metrics",
                                value={},
                                elem_classes=["tab-content"]
                            )
            
            # Event handlers
            submit_btn.click(
                fn=self.process_query,
                inputs=[query_input],
                outputs=[report_output, visualization_output, agent_activity_output,
                        progress_status, progress_tasks, progress_events, progress_events_log, progress_timeline]
            )
            
            clear_btn.click(
                fn=lambda: ("", None, {}, 
                           "**Current Agent:** Waiting for query...",
                           "**Active Tasks:** None",
                           "**Progress Events:**\n\nWaiting for execution...",
                           "**Progress Events Log:**\n\nWaiting for execution...",
                           None),
                outputs=[query_input, visualization_output, agent_activity_output,
                        progress_status, progress_tasks, progress_events, progress_events_log, progress_timeline]
            )
            
            example_queries.change(
                fn=lambda x: x,
                inputs=[example_queries],
                outputs=[query_input]
            )
        
        self.app = app
        return app
    
    def launch(self, server_name: str = "0.0.0.0", server_port: int = 7860, share: bool = False):
        """
        Launch Gradio app
        
        Args:
            server_name: Server host
            server_port: Server port
            share: Whether to create public link
        """
        logger.info(f"[UI] Launching Gradio app | Host: {server_name} | Port: {server_port} | Share: {share}")
        if self.app is None:
            logger.debug("[UI] Creating interface...")
            self.create_interface()
        
        logger.info(f"[UI] Gradio app launching at http://{server_name}:{server_port}")
        self.app.launch(
            server_name=server_name,
            server_port=server_port,
            share=share
        )


def main():
    """Main entry point for UI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MyFinGPT UI")
    parser.add_argument("--provider", type=str, default=None, help="LLM provider (openai, gemini, ollama)")
    parser.add_argument("--port", type=int, default=7860, help="Server port")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--share", action="store_true", help="Create public link")
    
    args = parser.parse_args()
    
    ui = MyFinGPTUI(llm_provider=args.provider)
    ui.launch(server_name=args.host, server_port=args.port, share=args.share)


if __name__ == "__main__":
    main()


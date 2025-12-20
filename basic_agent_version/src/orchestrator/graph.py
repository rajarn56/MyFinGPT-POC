"""LangGraph workflow definition"""

from typing import Dict, Any
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from loguru import logger
from langgraph.graph import StateGraph, END
from .state import AgentState, StateManager
from ..agents.research_agent import ResearchAgent
from ..agents.analyst_agent import AnalystAgent
from ..agents.comparison_agent import ComparisonAgent
from ..agents.reporting_agent import ReportingAgent
from ..utils.context_cache import ContextCache


class MyFinGPTGraph:
    """LangGraph workflow for MyFinGPT agent orchestration"""
    
    def __init__(self, llm_provider: str = None, context_cache: ContextCache = None):
        """
        Initialize the graph
        
        Args:
            llm_provider: LLM provider name
            context_cache: Optional context cache instance
        """
        logger.info(f"Initializing MyFinGPTGraph with provider: {llm_provider or 'default'}")
        self.graph = StateGraph(AgentState)
        
        # Initialize agents with shared context cache
        logger.debug("Initializing agents...")
        self.research_agent = ResearchAgent(provider=llm_provider, context_cache=context_cache)
        self.analyst_agent = AnalystAgent(provider=llm_provider)
        self.comparison_agent = ComparisonAgent(provider=llm_provider)
        self.reporting_agent = ReportingAgent(provider=llm_provider)
        logger.debug("All agents initialized successfully")
        
        self._build_graph()
        self.app = self.graph.compile()
        logger.info("LangGraph workflow compiled successfully")
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        logger.debug("Building LangGraph workflow structure")
        # Add agent nodes
        self.graph.add_node("research", self._research_node)
        self.graph.add_node("analyst", self._analyst_node)
        self.graph.add_node("comparison", self._comparison_node)
        self.graph.add_node("reporting", self._reporting_node)
        logger.debug("Added nodes: research, analyst, comparison, reporting")
        
        # Set entry point
        self.graph.set_entry_point("research")
        logger.debug("Set entry point: research")
        
        # Sequential flow: Research -> Analyst -> Comparison -> Reporting -> END
        # Comparison Agent always runs (works for single stock vs benchmarks and multi-stock comparisons)
        self.graph.add_edge("research", "analyst")
        self.graph.add_edge("analyst", "comparison")
        self.graph.add_edge("comparison", "reporting")
        self.graph.add_edge("reporting", END)
        logger.debug("Added edges: research->analyst->comparison->reporting->END")
    
    def _research_node(self, state: AgentState) -> AgentState:
        """Research agent node"""
        query = state.get("query", "")
        symbols = state.get("symbols", [])
        logger.info(f"[GRAPH] Executing Research Node | Query: {query[:50]}... | Symbols: {symbols}")
        result = self.research_agent.run(state)
        logger.info(f"[GRAPH] Research Node completed | Symbols processed: {len(result.get('research_data', {}))}")
        # Prune context if size exceeds threshold
        result = StateManager.prune_context(result)
        return result
    
    def _analyst_node(self, state: AgentState) -> AgentState:
        """Analyst agent node"""
        symbols = state.get("symbols", [])
        logger.info(f"[GRAPH] Executing Analyst Node | Symbols: {symbols}")
        result = self.analyst_agent.run(state)
        logger.info(f"[GRAPH] Analyst Node completed | Analysis results: {len(result.get('analysis_results', {}))}")
        # Prune context if size exceeds threshold
        result = StateManager.prune_context(result)
        return result
    
    def _comparison_node(self, state: AgentState) -> AgentState:
        """Comparison agent node"""
        symbols = state.get("symbols", [])
        logger.info(f"[GRAPH] Executing Comparison Node | Symbols: {symbols}")
        result = self.comparison_agent.run(state)
        comparison_type = result.get("comparison_data", {}).get("comparison_type", "unknown")
        logger.info(f"[GRAPH] Comparison Node completed | Comparison type: {comparison_type}")
        # Prune context if size exceeds threshold
        result = StateManager.prune_context(result)
        return result
    
    def _reporting_node(self, state: AgentState) -> AgentState:
        """Reporting agent node"""
        symbols = state.get("symbols", [])
        logger.info(f"[GRAPH] Executing Reporting Node | Symbols: {symbols}")
        result = self.reporting_agent.run(state)
        report_length = len(result.get("final_report", ""))
        logger.info(f"[GRAPH] Reporting Node completed | Report length: {report_length} chars")
        return result
    
    def _should_parallelize(self, state: AgentState) -> Literal["parallel", "sequential"]:
        """
        Determine if parallel execution should be used
        
        Args:
            state: Current state
        
        Returns:
            "parallel" if multiple symbols, "sequential" otherwise
        """
        symbols = state.get("symbols", [])
        if len(symbols) > 1:
            return "parallel"
        return "sequential"
    
    def add_node(self, name: str, node_func):
        """Add a node to the graph"""
        self.graph.add_node(name, node_func)
    
    def add_edge(self, source: str, target: str):
        """Add an edge to the graph"""
        self.graph.add_edge(source, target)
    
    def add_conditional_edges(self, source: str, path_map: Dict[str, str], condition_func=None):
        """Add conditional edges"""
        if condition_func:
            self.graph.add_conditional_edges(source, condition_func, path_map)
        else:
            # Simple mapping
            for condition, target in path_map.items():
                self.graph.add_edge(source, target)
    
    def run(self, initial_state: AgentState) -> AgentState:
        """
        Run the graph with initial state
        
        Args:
            initial_state: Initial AgentState
        
        Returns:
            Final AgentState after execution
        """
        query = initial_state.get("query", "")
        symbols = initial_state.get("symbols", [])
        logger.info(f"[GRAPH] Starting workflow execution | Query: {query[:50]}... | Symbols: {symbols}")
        
        # Update context size before running
        initial_state = StateManager.update_context_size(initial_state)
        initial_size = initial_state.get("context_size", 0)
        logger.debug(f"[GRAPH] Initial context size: {initial_size} bytes")
        
        # Run the graph
        logger.debug("[GRAPH] Invoking graph execution...")
        result = self.app.invoke(initial_state)
        
        # Update context size after running
        result = StateManager.update_context_size(result)
        final_size = result.get("context_size", 0)
        agents_executed = result.get("agents_executed", [])
        total_tokens = sum(result.get("token_usage", {}).values())
        
        logger.info(f"[GRAPH] Workflow execution completed | "
                   f"Context size: {initial_size} -> {final_size} bytes | "
                   f"Agents executed: {agents_executed} | "
                   f"Total tokens: {total_tokens}")
        
        return result
    
    def stream(self, initial_state: AgentState):
        """
        Stream execution of the graph with progress tracking
        
        Args:
            initial_state: Initial AgentState
        
        Yields:
            State updates as graph executes, including progress events
        """
        query = initial_state.get("query", "")
        transaction_id = initial_state.get("transaction_id", "unknown")
        logger.info(f"[GRAPH] Starting streaming execution | Transaction ID: {transaction_id} | Query: {query[:50]}...")
        initial_state = StateManager.update_context_size(initial_state)
        
        node_count = 0
        execution_order = []
        
        for state_update in self.app.stream(initial_state):
            node_count += 1
            # Log each state update and track progress
            for node_name, state in state_update.items():
                # Update context size
                state = StateManager.update_context_size(state)
                
                # Track execution order
                if node_name not in [e.get("node") for e in execution_order]:
                    import time
                    execution_order.append({
                        "node": node_name,
                        "start_time": time.time(),
                        "transaction_id": transaction_id
                    })
                
                # Log progress events if any
                progress_events = state.get("progress_events", [])
                if progress_events:
                    latest_event = progress_events[-1]
                    logger.debug(f"[GRAPH] Stream update from node: {node_name} | "
                               f"Latest progress: {latest_event.get('message', 'N/A')[:50]}... | "
                               f"Context size: {state.get('context_size', 0)} bytes")
                else:
                    logger.debug(f"[GRAPH] Stream update from node: {node_name} | "
                               f"Context size: {state.get('context_size', 0)} bytes")
                
                # Update state_update with updated state
                state_update[node_name] = state
            
            yield state_update
        
        logger.info(f"[GRAPH] Streaming execution completed | Transaction ID: {transaction_id} | Total updates: {node_count}")


"""LangGraph state management for MyFinGPT"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
import json
import time
import os
from pathlib import Path
from loguru import logger

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class AgentState(TypedDict):
    """
    Shared state structure for LangGraph orchestration.
    This is the central context repository for all agents.
    """
    # Query information
    transaction_id: str  # Unique transaction identifier for this query
    query: str  # Original user query
    query_type: str  # "single_stock", "comparison", "trend", etc.
    symbols: List[str]  # Stock symbols extracted from query
    
    # Research Agent Output
    research_data: Dict[str, Any]  # Symbol -> {price, financials, news, etc.}
    research_metadata: Dict[str, Any]  # Timestamps, sources, data quality
    
    # Analyst Agent Output
    analysis_results: Dict[str, Any]  # Symbol -> {ratios, sentiment, trends}
    analysis_reasoning: Dict[str, str]  # Symbol -> reasoning chain
    
    # Specialized Agent Outputs
    sentiment_analysis: Dict[str, Any]  # Symbol -> sentiment scores
    trend_analysis: Dict[str, Any]  # Trend patterns identified
    comparison_data: Dict[str, Any]  # Comparison results
    
    # Citations and Sources
    citations: List[Dict[str, Any]]  # [{source, url, date, agent, data_point}]
    vector_db_references: List[str]  # IDs of retrieved vector DB documents
    
    # Token and Performance Tracking
    token_usage: Dict[str, int]  # {agent_name: tokens_used}
    execution_time: Dict[str, float]  # {agent_name: seconds}
    
    # Final Output
    final_report: str
    visualizations: Dict[str, Any]  # Chart data
    
    # Context Metadata
    context_version: int  # Version tracking for context evolution
    context_size: int  # Size in bytes for optimization
    agents_executed: List[str]  # Execution order
    
    # Progress Tracking
    progress_events: List[Dict[str, Any]]  # Real-time progress events
    current_agent: Optional[str]  # Currently executing agent
    current_tasks: Dict[str, List[str]]  # Current tasks per agent
    execution_order: List[Dict[str, Any]]  # Execution order with timing
    
    # Incremental Query Support
    previous_query_id: Optional[str]  # Link to previous query
    previous_symbols: List[str]  # Symbols from previous query
    new_symbols: List[str]  # New symbols in current query
    is_incremental: bool  # Whether this is an incremental query
    session_id: Optional[str]  # Session identifier for state persistence
    
    # Partial Success Tracking
    partial_success: bool  # True if some operations succeeded, some failed
    symbol_status: Dict[str, str]  # {"AAPL": "success", "INVALID": "failed"}
    symbol_errors: Dict[str, str]  # {"INVALID": "Symbol not found"}
    
    # Query Similarity and Cross-Query Awareness
    query_embedding: Optional[List[float]]  # Embedding of current query
    similar_queries: List[Dict]  # List of similar previous queries
    related_context_ids: List[str]  # IDs of related previous query contexts


class StateManager:
    """Manages LangGraph state operations and context utilities"""
    
    @staticmethod
    def create_initial_state(query: str, query_type: str = None, symbols: List[str] = None, transaction_id: str = None) -> AgentState:
        """
        Create initial state from user query
        
        Args:
            query: User's financial query
            query_type: Type of query (auto-detected if None)
            symbols: List of stock symbols (auto-extracted if None)
            transaction_id: Transaction ID (auto-generated if None)
        
        Returns:
            Initial AgentState
        """
        if transaction_id is None:
            transaction_id = str(uuid.uuid4())[:8]  # Short 8-character ID
        
        if query_type is None:
            query_type = StateManager._detect_query_type(query)
        
        if symbols is None:
            symbols = StateManager._extract_symbols(query)
        
        return AgentState(
            transaction_id=transaction_id,
            query=query,
            query_type=query_type,
            symbols=symbols,
            research_data={},
            research_metadata={},
            analysis_results={},
            analysis_reasoning={},
            sentiment_analysis={},
            trend_analysis={},
            comparison_data={},
            citations=[],
            vector_db_references=[],
            token_usage={},
            execution_time={},
            final_report="",
            visualizations={},
            context_version=1,
            context_size=0,
            agents_executed=[],
            progress_events=[],
            current_agent=None,
            current_tasks={},
            execution_order=[],
            previous_query_id=None,
            previous_symbols=[],
            new_symbols=[],
            is_incremental=False,
            session_id=None,
            partial_success=False,
            symbol_status={},
            symbol_errors={},
            query_embedding=None,
            similar_queries=[],
            related_context_ids=[]
        )
    
    @staticmethod
    def _detect_query_type(query: str) -> str:
        """Detect query type from query text"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["compare", "comparison", "vs", "versus"]):
            return "comparison"
        elif any(word in query_lower for word in ["trend", "trends", "pattern", "patterns"]):
            return "trend"
        elif any(word in query_lower for word in ["sentiment", "news", "impact"]):
            return "sentiment"
        elif any(word in query_lower for word in ["similar", "like", "same as"]):
            return "similarity"
        else:
            return "single_stock"
    
    @staticmethod
    def _extract_symbols(query: str) -> List[str]:
        """
        Extract stock symbols from query using guardrails validation
        """
        from ..utils.guardrails import guardrails
        
        # Use guardrails to extract and validate symbols
        symbols = guardrails.extract_symbols(query)
        return symbols
    
    @staticmethod
    def update_research_data(state: AgentState, symbol: str, data: Dict[str, Any], 
                           metadata: Dict[str, Any] = None) -> AgentState:
        """Update research data for a symbol"""
        state["research_data"][symbol] = data
        if metadata:
            state["research_metadata"][symbol] = metadata
        state["context_version"] += 1
        return state
    
    @staticmethod
    def update_analysis_results(state: AgentState, symbol: str, results: Dict[str, Any],
                               reasoning: str = None) -> AgentState:
        """Update analysis results for a symbol"""
        state["analysis_results"][symbol] = results
        if reasoning:
            state["analysis_reasoning"][symbol] = reasoning
        state["context_version"] += 1
        return state
    
    @staticmethod
    def add_citation(state: AgentState, source: str, url: str = None, date: str = None,
                    agent: str = None, data_point: str = None) -> AgentState:
        """Add a citation to the state"""
        citation = {
            "source": source,
            "url": url,
            "date": date or datetime.now().isoformat(),
            "agent": agent,
            "data_point": data_point
        }
        state["citations"].append(citation)
        return state
    
    @staticmethod
    def track_token_usage(state: AgentState, agent_name: str, tokens: int) -> AgentState:
        """Track token usage for an agent"""
        if agent_name not in state["token_usage"]:
            state["token_usage"][agent_name] = 0
        state["token_usage"][agent_name] += tokens
        return state
    
    @staticmethod
    def track_execution_time(state: AgentState, agent_name: str, seconds: float) -> AgentState:
        """Track execution time for an agent"""
        state["execution_time"][agent_name] = seconds
        return state
    
    @staticmethod
    def mark_agent_executed(state: AgentState, agent_name: str) -> AgentState:
        """Mark an agent as executed"""
        if agent_name not in state["agents_executed"]:
            state["agents_executed"].append(agent_name)
        return state
    
    @staticmethod
    def calculate_context_size(state: AgentState) -> int:
        """Calculate approximate context size in bytes"""
        import json
        try:
            state_json = json.dumps(state, default=str)
            return len(state_json.encode('utf-8'))
        except Exception:
            return 0
    
    @staticmethod
    def update_context_size(state: AgentState) -> AgentState:
        """Update context size in state"""
        state["context_size"] = StateManager.calculate_context_size(state)
        return state
    
    @staticmethod
    def validate_context(state: AgentState, required_fields: List[str]):
        """
        Validate that required context fields exist
        
        Returns:
            (is_valid, missing_fields)
        """
        missing = []
        for field in required_fields:
            if field not in state or not state[field]:
                missing.append(field)
        return len(missing) == 0, missing
    
    @staticmethod
    def prune_context(state: AgentState, max_size_bytes: int = 1000000) -> AgentState:
        """
        Prune context to reduce size (basic implementation)
        Removes older/unnecessary data while preserving essential information
        """
        current_size = StateManager.calculate_context_size(state)
        
        if current_size <= max_size_bytes:
            return state
        
        # Remove detailed metadata but keep essential data
        if "research_metadata" in state:
            # Keep only recent metadata
            for symbol in list(state["research_metadata"].keys()):
                metadata = state["research_metadata"][symbol]
                if isinstance(metadata, dict) and "timestamp" in metadata:
                    # Keep only last 24 hours of metadata
                    pass  # Simplified for now
        
        # Update size after pruning
        state["context_size"] = StateManager.calculate_context_size(state)
        return state
    
    @staticmethod
    def merge_parallel_contexts(contexts: List[AgentState]) -> AgentState:
        """
        Merge multiple contexts from parallel agent execution
        
        Args:
            contexts: List of AgentState from parallel executions
        
        Returns:
            Merged AgentState
        """
        if not contexts:
            raise ValueError("Cannot merge empty context list")
        
        # Start with first context as base
        merged = contexts[0].copy()
        
        # Preserve transaction_id from first context (all should have same transaction_id)
        merged["transaction_id"] = contexts[0].get("transaction_id", merged.get("transaction_id", ""))
        
        # Merge research_data
        for ctx in contexts[1:]:
            merged["research_data"].update(ctx.get("research_data", {}))
            merged["research_metadata"].update(ctx.get("research_metadata", {}))
            merged["analysis_results"].update(ctx.get("analysis_results", {}))
            merged["analysis_reasoning"].update(ctx.get("analysis_reasoning", {}))
            merged["citations"].extend(ctx.get("citations", []))
            merged["token_usage"].update(ctx.get("token_usage", {}))
            merged["execution_time"].update(ctx.get("execution_time", {}))
            merged["agents_executed"].extend([
                agent for agent in ctx.get("agents_executed", [])
                if agent not in merged["agents_executed"]
            ])
        
        # Merge progress events
        for ctx in contexts[1:]:
            merged["progress_events"].extend(ctx.get("progress_events", []))
            merged["execution_order"].extend(ctx.get("execution_order", []))
        
        # Update current agent and tasks from merged progress events
        from ..utils.progress_tracker import ProgressTracker
        merged["current_agent"] = ProgressTracker.get_current_agent(merged.get("progress_events", []))
        merged["current_tasks"] = ProgressTracker.get_current_tasks(merged.get("progress_events", []))
        
        # Update context version and size
        merged["context_version"] += 1
        merged["context_size"] = StateManager.calculate_context_size(merged)
        
        return merged
    
    @staticmethod
    def add_progress_event(state: AgentState, event: Dict[str, Any]) -> AgentState:
        """
        Add a progress event to the state
        
        Args:
            state: AgentState
            event: Progress event dictionary
        
        Returns:
            Updated AgentState
        """
        if "progress_events" not in state:
            state["progress_events"] = []
        
        state["progress_events"].append(event)
        
        # Update current agent and tasks
        from ..utils.progress_tracker import ProgressTracker
        state["current_agent"] = ProgressTracker.get_current_agent(state["progress_events"])
        state["current_tasks"] = ProgressTracker.get_current_tasks(state["progress_events"])
        
        return state
    
    @staticmethod
    def add_execution_order_entry(state: AgentState, agent: str, start_time: float, 
                                  end_time: Optional[float] = None) -> AgentState:
        """
        Add an execution order entry
        
        Args:
            state: AgentState
            agent: Agent name
            start_time: Start time (timestamp)
            end_time: End time (timestamp, optional)
        
        Returns:
            Updated AgentState
        """
        if "execution_order" not in state:
            state["execution_order"] = []
        
        entry = {
            "agent": agent,
            "start_time": start_time,
            "end_time": end_time,
            "duration": (end_time - start_time) if end_time else None
        }
        
        state["execution_order"].append(entry)
        return state
    
    @staticmethod
    def save_state_for_session(state: AgentState, session_id: str) -> None:
        """
        Save state for session (file-based persistence)
        
        Args:
            state: AgentState to save
            session_id: Session identifier
        """
        try:
            # Create sessions directory if it doesn't exist
            sessions_dir = Path("./sessions")
            sessions_dir.mkdir(exist_ok=True)
            
            # Save state to file
            state_file = sessions_dir / f"{session_id}.json"
            
            # Convert state to JSON-serializable format
            state_dict = dict(state)
            # Convert any non-serializable values
            for key, value in state_dict.items():
                if isinstance(value, (datetime,)):
                    state_dict[key] = value.isoformat()
            
            with open(state_file, 'w') as f:
                json.dump(state_dict, f, default=str)
            
            logger.debug(f"StateManager: Saved state for session {session_id}")
        
        except Exception as e:
            logger.warning(f"StateManager: Error saving state for session {session_id}: {e}")
    
    @staticmethod
    def load_state_for_session(session_id: str, query_id: Optional[str] = None) -> Optional[AgentState]:
        """
        Load previous state for session
        
        Args:
            session_id: Session identifier
            query_id: Optional query ID to filter by
        
        Returns:
            Previous AgentState if found, None otherwise
        """
        try:
            sessions_dir = Path("./sessions")
            state_file = sessions_dir / f"{session_id}.json"
            
            if not state_file.exists():
                return None
            
            with open(state_file, 'r') as f:
                state_dict = json.load(f)
            
            # Convert back to AgentState
            state = AgentState(**state_dict)
            
            logger.debug(f"StateManager: Loaded state for session {session_id}")
            return state
        
        except Exception as e:
            logger.warning(f"StateManager: Error loading state for session {session_id}: {e}")
            return None
    
    @staticmethod
    def merge_incremental_state(previous_state: AgentState, new_state: AgentState) -> AgentState:
        """
        Merge new state with previous state for incremental queries
        
        Args:
            previous_state: Previous query state
            new_state: New query state
        
        Returns:
            Merged AgentState
        """
        # Start with previous state as base
        merged = previous_state.copy()
        
        # Merge research_data (keep both old and new)
        merged["research_data"].update(new_state.get("research_data", {}))
        merged["research_metadata"].update(new_state.get("research_metadata", {}))
        
        # Merge analysis_results
        merged["analysis_results"].update(new_state.get("analysis_results", {}))
        merged["analysis_reasoning"].update(new_state.get("analysis_reasoning", {}))
        
        # Merge citations
        merged["citations"].extend(new_state.get("citations", []))
        
        # Merge symbols (combine lists, remove duplicates)
        merged_symbols = list(set(merged.get("symbols", []) + new_state.get("symbols", [])))
        merged["symbols"] = merged_symbols
        
        # Merge progress events
        merged["progress_events"].extend(new_state.get("progress_events", []))
        
        # Update token usage and execution time
        for agent, tokens in new_state.get("token_usage", {}).items():
            if agent in merged["token_usage"]:
                merged["token_usage"][agent] += tokens
            else:
                merged["token_usage"][agent] = tokens
        
        merged["execution_time"].update(new_state.get("execution_time", {}))
        
        # Merge symbol status and errors
        merged["symbol_status"].update(new_state.get("symbol_status", {}))
        merged["symbol_errors"].update(new_state.get("symbol_errors", {}))
        
        # Update context version
        merged["context_version"] += 1
        
        # Update context size
        merged["context_size"] = StateManager.calculate_context_size(merged)
        
        logger.debug(f"StateManager: Merged incremental state | "
                    f"Previous symbols: {len(previous_state.get('symbols', []))} | "
                    f"New symbols: {len(new_state.get('symbols', []))} | "
                    f"Merged symbols: {len(merged_symbols)}")
        
        return merged
    
    @staticmethod
    def save_query_to_history(state: AgentState, session_id: str) -> None:
        """
        Save query to history for similarity matching
        
        Args:
            state: AgentState with query information
            session_id: Session identifier
        """
        try:
            query = state.get("query", "")
            symbols = state.get("symbols", [])
            query_id = state.get("transaction_id", "")
            query_embedding = state.get("query_embedding")
            
            if not query_embedding:
                return
            
            # Load existing history
            history_file = Path("./sessions") / f"{session_id}_history.json"
            history = []
            
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
            
            # Add current query
            history.append({
                "query": query,
                "symbols": symbols,
                "query_id": query_id,
                "query_embedding": query_embedding,
                "timestamp": time.time()
            })
            
            # Keep only last 100 queries
            if len(history) > 100:
                history = history[-100:]
            
            # Save history
            Path("./sessions").mkdir(exist_ok=True)
            with open(history_file, 'w') as f:
                json.dump(history, f)
            
            logger.debug(f"StateManager: Saved query to history | Session: {session_id} | Query ID: {query_id}")
        
        except Exception as e:
            logger.warning(f"StateManager: Error saving query to history: {e}")
    
    @staticmethod
    def get_query_history(session_id: str) -> List[Dict]:
        """
        Get query history for session
        
        Args:
            session_id: Session identifier
        
        Returns:
            List of previous queries
        """
        try:
            history_file = Path("./sessions") / f"{session_id}_history.json"
            
            if not history_file.exists():
                return []
            
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            return history
        
        except Exception as e:
            logger.warning(f"StateManager: Error loading query history: {e}")
            return []
    
    @staticmethod
    def prune_context(state: AgentState, max_size_bytes: int = 1000000) -> AgentState:
        """
        Prune context to reduce size with age-based, relevance-based, and size-based pruning
        
        Args:
            state: AgentState to prune
            max_size_bytes: Maximum context size in bytes
        
        Returns:
            Pruned AgentState
        """
        current_size = StateManager.calculate_context_size(state)
        
        if current_size <= max_size_bytes:
            return state
        
        logger.info(f"StateManager: Pruning context | Current size: {current_size} bytes | Target: {max_size_bytes} bytes")
        
        # Age-based pruning: Remove metadata older than 24 hours
        current_time = time.time()
        if "research_metadata" in state:
            for symbol in list(state["research_metadata"].keys()):
                metadata = state["research_metadata"][symbol]
                if isinstance(metadata, dict) and "timestamp" in metadata:
                    timestamp = metadata.get("timestamp")
                    if timestamp:
                        try:
                            # Parse timestamp (could be ISO string or timestamp)
                            if isinstance(timestamp, str):
                                from datetime import datetime
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                age_seconds = (datetime.now() - dt.replace(tzinfo=None)).total_seconds()
                            else:
                                age_seconds = current_time - timestamp
                            
                            # Remove if older than 24 hours
                            if age_seconds > 86400:  # 24 hours
                                logger.debug(f"StateManager: Removing old metadata for {symbol} (age: {age_seconds/3600:.1f} hours)")
                                del state["research_metadata"][symbol]
                        except Exception as e:
                            logger.debug(f"StateManager: Error parsing timestamp for {symbol}: {e}")
        
        # Relevance-based pruning: Keep essential data, remove detailed intermediate results
        # Keep: research_data (essential), analysis_results (essential), final_report (essential)
        # Can prune: detailed reasoning chains, intermediate analysis steps
        
        # Size-based pruning: If still too large, remove less critical data
        current_size = StateManager.calculate_context_size(state)
        if current_size > max_size_bytes:
            # Remove detailed reasoning chains (keep summaries)
            if "analysis_reasoning" in state:
                for symbol in state["analysis_reasoning"]:
                    reasoning = state["analysis_reasoning"][symbol]
                    if isinstance(reasoning, str) and len(reasoning) > 1000:
                        # Keep only first 500 chars
                        state["analysis_reasoning"][symbol] = reasoning[:500] + "..."
            
            # Remove old progress events (keep last 50)
            if "progress_events" in state and len(state["progress_events"]) > 50:
                state["progress_events"] = state["progress_events"][-50:]
        
        # Update size after pruning
        state["context_size"] = StateManager.calculate_context_size(state)
        logger.info(f"StateManager: Context pruned | Final size: {state['context_size']} bytes")
        
        return state


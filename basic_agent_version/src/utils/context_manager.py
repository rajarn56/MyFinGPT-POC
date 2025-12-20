"""Context management utilities"""

from typing import Dict, Any, List, Optional
from ..orchestrator.state import AgentState, StateManager
import json
import sys


class ContextManager:
    """Manages context operations and validation"""
    
    def __init__(self, max_size_bytes: int = 1000000):
        """
        Initialize context manager
        
        Args:
            max_size_bytes: Maximum context size in bytes
        """
        self.max_size_bytes = max_size_bytes
        self.state_manager = StateManager()
    
    def validate_context(self, state: AgentState, required_fields: List[str]):
        """
        Validate that required context fields exist
        
        Args:
            state: AgentState to validate
            required_fields: List of required field names
        
        Returns:
            (is_valid, missing_fields)
        """
        return self.state_manager.validate_context(state, required_fields)
    
    def read_context(self, state: AgentState, field: str, default: Any = None) -> Any:
        """
        Read a field from context
        
        Args:
            state: AgentState
            field: Field name to read
            default: Default value if field doesn't exist
        
        Returns:
            Field value or default
        """
        return state.get(field, default)
    
    def write_context(self, state: AgentState, field: str, value: Any) -> AgentState:
        """
        Write a value to context field
        
        Args:
            state: AgentState
            field: Field name to write
            value: Value to write
        
        Returns:
            Updated AgentState
        """
        state[field] = value
        state = self.state_manager.update_context_size(state)
        return state
    
    def merge_contexts(self, contexts: List[AgentState]) -> AgentState:
        """
        Merge multiple contexts from parallel execution
        
        Args:
            contexts: List of AgentState objects
        
        Returns:
            Merged AgentState
        """
        return self.state_manager.merge_parallel_contexts(contexts)
    
    def prune_context(self, state: AgentState) -> AgentState:
        """
        Prune context to reduce size
        
        Args:
            state: AgentState to prune
        
        Returns:
            Pruned AgentState
        """
        return self.state_manager.prune_context(state, self.max_size_bytes)
    
    def get_context_size(self, state: AgentState) -> int:
        """Get current context size in bytes"""
        return self.state_manager.calculate_context_size(state)
    
    def is_context_too_large(self, state: AgentState) -> bool:
        """Check if context exceeds maximum size"""
        return self.get_context_size(state) > self.max_size_bytes
    
    def compress_context(self, state: AgentState) -> AgentState:
        """
        Compress context (basic implementation - removes verbose data)
        
        Args:
            state: AgentState to compress
        
        Returns:
            Compressed AgentState
        """
        # Remove detailed reasoning chains, keep summaries
        if "analysis_reasoning" in state:
            for symbol in state["analysis_reasoning"]:
                reasoning = state["analysis_reasoning"][symbol]
                if len(reasoning) > 500:  # Truncate long reasoning
                    state["analysis_reasoning"][symbol] = reasoning[:500] + "..."
        
        # Remove old metadata
        if "research_metadata" in state:
            # Keep only essential metadata
            for symbol in list(state["research_metadata"].keys()):
                metadata = state["research_metadata"][symbol]
                if isinstance(metadata, dict):
                    # Keep only essential fields
                    essential_fields = ["timestamp", "source", "quality"]
                    filtered_metadata = {
                        k: v for k, v in metadata.items() 
                        if k in essential_fields
                    }
                    state["research_metadata"][symbol] = filtered_metadata
        
        state = self.state_manager.update_context_size(state)
        return state
    
    def get_context_summary(self, state: AgentState) -> Dict[str, Any]:
        """
        Get a summary of context state
        
        Args:
            state: AgentState
        
        Returns:
            Summary dictionary
        """
        return {
            "query": state.get("query", ""),
            "query_type": state.get("query_type", ""),
            "symbols": state.get("symbols", []),
            "research_data_count": len(state.get("research_data", {})),
            "analysis_results_count": len(state.get("analysis_results", {})),
            "citations_count": len(state.get("citations", [])),
            "context_size": self.get_context_size(state),
            "context_version": state.get("context_version", 1),
            "agents_executed": state.get("agents_executed", []),
            "total_tokens": sum(state.get("token_usage", {}).values())
        }


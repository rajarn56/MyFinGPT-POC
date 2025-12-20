"""Token usage tracking utilities"""

from typing import Dict, Optional, List, Any
from datetime import datetime


class TokenTracker:
    """Tracks token usage per agent and per call"""
    
    def __init__(self):
        """Initialize token tracker"""
        self.token_usage: Dict[str, int] = {}  # agent_name -> total_tokens
        self.call_history: List[Dict[str, Any]] = []  # History of all calls
    
    def track_tokens(self, agent_name: str, tokens: int, 
                    call_type: str = "completion", model: Optional[str] = None):
        """
        Track token usage for an agent
        
        Args:
            agent_name: Name of the agent
            tokens: Number of tokens used
            call_type: Type of call (completion, embedding, etc.)
            model: Model used
        """
        if agent_name not in self.token_usage:
            self.token_usage[agent_name] = 0
        
        self.token_usage[agent_name] += tokens
        
        # Record in history
        self.call_history.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "tokens": tokens,
            "call_type": call_type,
            "model": model
        })
    
    def get_agent_tokens(self, agent_name: str) -> int:
        """Get total tokens used by an agent"""
        return self.token_usage.get(agent_name, 0)
    
    def get_total_tokens(self) -> int:
        """Get total tokens used across all agents"""
        return sum(self.token_usage.values())
    
    def get_token_breakdown(self) -> Dict[str, int]:
        """Get token usage breakdown by agent"""
        return self.token_usage.copy()
    
    def get_call_history(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get call history
        
        Args:
            agent_name: Optional filter by agent name
        
        Returns:
            List of call records
        """
        if agent_name:
            return [c for c in self.call_history if c.get("agent") == agent_name]
        return self.call_history.copy()
    
    def reset(self):
        """Reset token tracking"""
        self.token_usage = {}
        self.call_history = []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get token usage statistics"""
        total = self.get_total_tokens()
        agent_count = len(self.token_usage)
        call_count = len(self.call_history)
        
        avg_per_agent = total / agent_count if agent_count > 0 else 0
        avg_per_call = total / call_count if call_count > 0 else 0
        
        return {
            "total_tokens": total,
            "agent_count": agent_count,
            "call_count": call_count,
            "avg_tokens_per_agent": avg_per_agent,
            "avg_tokens_per_call": avg_per_call,
            "breakdown": self.get_token_breakdown()
        }


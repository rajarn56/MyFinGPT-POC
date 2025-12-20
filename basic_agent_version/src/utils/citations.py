"""Citation tracking utilities"""

from typing import Dict, List, Any, Optional
from datetime import datetime


class CitationTracker:
    """Tracks citations for data sources"""
    
    def __init__(self):
        """Initialize citation tracker"""
        self.citations: List[Dict[str, Any]] = []
    
    def add_citation(self, source: str, url: Optional[str] = None, 
                    date: Optional[str] = None, agent: Optional[str] = None,
                    data_point: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a citation
        
        Args:
            source: Source name (e.g., "Yahoo Finance")
            url: Source URL
            date: Date of data (ISO format)
            agent: Agent that collected the data
            data_point: What data point this citation refers to
            symbol: Stock symbol if applicable
        
        Returns:
            Citation dictionary
        """
        citation = {
            "source": source,
            "url": url,
            "date": date or datetime.now().isoformat(),
            "agent": agent,
            "data_point": data_point,
            "symbol": symbol
        }
        self.citations.append(citation)
        return citation
    
    def format_citation(self, citation: Dict[str, Any]) -> str:
        """
        Format a citation as a string
        
        Args:
            citation: Citation dictionary
        
        Returns:
            Formatted citation string
        """
        parts = [f"Source: {citation['source']}"]
        
        if citation.get("date"):
            parts.append(f"Date: {citation['date']}")
        
        if citation.get("url"):
            parts.append(f"URL: {citation['url']}")
        
        return " | ".join(parts)
    
    def get_citations_for_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Get all citations for a specific symbol"""
        return [c for c in self.citations if c.get("symbol") == symbol]
    
    def get_citations_for_agent(self, agent: str) -> List[Dict[str, Any]]:
        """Get all citations from a specific agent"""
        return [c for c in self.citations if c.get("agent") == agent]
    
    def get_all_citations(self) -> List[Dict[str, Any]]:
        """Get all citations"""
        return self.citations.copy()
    
    def clear(self):
        """Clear all citations"""
        self.citations = []


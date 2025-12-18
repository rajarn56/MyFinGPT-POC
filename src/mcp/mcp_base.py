"""Base MCP client with context tracking and error handling"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
import requests
from loguru import logger
from ..utils.citations import CitationTracker


class MCPBaseClient(ABC):
    """Base class for MCP clients with context tracking"""
    
    def __init__(self, name: str, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize MCP client
        
        Args:
            name: Client name
            base_url: Base API URL
            api_key: API key
        """
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.citation_tracker = CitationTracker()
        self.rate_limit_delay = 0.1  # Default delay between requests
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Wait to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                     method: str = "GET", max_retries: int = 3) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            method: HTTP method
            max_retries: Maximum retry attempts
        
        Returns:
            Response data
        """
        url = f"{self.base_url}/{endpoint}" if self.base_url else endpoint
        
        for attempt in range(max_retries):
            try:
                self._wait_for_rate_limit()
                
                if method == "GET":
                    response = requests.get(url, params=params, timeout=30)
                elif method == "POST":
                    response = requests.post(url, json=params, timeout=30)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"{self.name}: Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                elif e.response.status_code >= 500:  # Server error
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"{self.name}: Server error, retrying in {wait_time}s")
                        time.sleep(wait_time)
                        continue
                    raise
                else:
                    raise
            
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"{self.name}: Request failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    continue
                raise
        
        raise Exception(f"{self.name}: Request failed after {max_retries} attempts")
    
    def add_citation(self, source: str, url: Optional[str] = None, 
                    date: Optional[str] = None, data_point: Optional[str] = None,
                    symbol: Optional[str] = None) -> Dict[str, Any]:
        """Add a citation"""
        return self.citation_tracker.add_citation(
            source=source,
            url=url,
            date=date,
            agent=f"{self.name}_MCP",
            data_point=data_point,
            symbol=symbol
        )
    
    @abstractmethod
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """Get current stock price"""
        pass
    
    @abstractmethod
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company information"""
        pass


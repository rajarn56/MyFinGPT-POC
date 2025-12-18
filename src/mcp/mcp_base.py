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
        Make HTTP request with retry logic and graceful error handling
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            method: HTTP method
            max_retries: Maximum retry attempts
        
        Returns:
            Response data
        
        Raises:
            Exception: If request fails after all retries
        """
        url = f"{self.base_url}/{endpoint}" if self.base_url else endpoint
        last_exception = None
        
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
                last_exception = e
                status_code = e.response.status_code if e.response else None
                
                if status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"{self.name}: Rate limited (429), waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        continue
                elif status_code == 401:  # Unauthorized
                    logger.error(f"{self.name}: Authentication failed (401) - check API key")
                    raise Exception(f"{self.name}: Authentication failed - invalid or missing API key")
                elif status_code == 403:  # Forbidden
                    logger.error(f"{self.name}: Access forbidden (403) - check API permissions")
                    raise Exception(f"{self.name}: Access forbidden - insufficient API permissions")
                elif status_code == 404:  # Not found
                    logger.warning(f"{self.name}: Resource not found (404) - {endpoint}")
                    raise Exception(f"{self.name}: Resource not found - {endpoint}")
                elif status_code >= 500:  # Server error
                    wait_time = 2 ** attempt
                    logger.warning(f"{self.name}: Server error ({status_code}), retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        continue
                else:
                    # Other 4xx errors
                    error_msg = f"{self.name}: HTTP error {status_code}"
                    if e.response and hasattr(e.response, 'text'):
                        try:
                            error_detail = e.response.json()
                            error_msg += f" - {error_detail}"
                        except:
                            error_msg += f" - {e.response.text[:200]}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            except requests.exceptions.Timeout as e:
                last_exception = e
                wait_time = 2 ** attempt
                logger.warning(f"{self.name}: Request timeout, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                wait_time = 2 ** attempt
                logger.warning(f"{self.name}: Connection error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            
            except Exception as e:
                last_exception = e
                wait_time = 2 ** attempt
                logger.warning(f"{self.name}: Request failed, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
                raise
        
        # All retries exhausted
        error_msg = f"{self.name}: Request failed after {max_retries} attempts"
        if last_exception:
            error_msg += f" - {str(last_exception)}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
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


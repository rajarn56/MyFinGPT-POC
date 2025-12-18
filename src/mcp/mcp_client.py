"""Unified MCP client wrapper"""

from typing import Dict, Any, Optional, List
from loguru import logger
from dotenv import load_dotenv
from .yahoo_finance import YahooFinanceClient
from .alpha_vantage import AlphaVantageClient
from .fmp import FMPClient
from ..utils.citations import CitationTracker
from ..utils.guardrails import guardrails, GuardrailsError

# Load environment variables
load_dotenv()


class UnifiedMCPClient:
    """Unified wrapper for all MCP clients with fallback logic"""
    
    def __init__(self):
        """Initialize unified MCP client"""
        self.yahoo = YahooFinanceClient()
        self.alpha_vantage = AlphaVantageClient()
        self.fmp = FMPClient()
        self.citation_tracker = CitationTracker()
    
    def get_stock_price(self, symbol: str, preferred_source: str = "yahoo") -> Dict[str, Any]:
        """
        Get stock price with fallback logic
        
        Args:
            symbol: Stock symbol
            preferred_source: Preferred source (yahoo, alpha_vantage, fmp)
        
        Returns:
            Stock price data with citation
        
        Raises:
            GuardrailsError: If symbol validation fails
        """
        import time
        start_time = time.time()
        logger.debug(f"[MCP:Unified] Getting stock price for {symbol} | Preferred source: {preferred_source}")
        
        # Validate symbol with guardrails
        is_valid, error = guardrails.validate_symbol(symbol)
        if not is_valid:
            logger.error(f"[MCP:Unified] Symbol validation failed: {error}")
            raise GuardrailsError(f"Invalid symbol: {error}")
        
        # Validate data source
        is_valid, error = guardrails.validate_data_source(preferred_source)
        if not is_valid:
            logger.warning(f"[MCP:Unified] Data source validation failed: {error}, using default")
            preferred_source = "yahoo"
        
        sources = {
            "yahoo": self.yahoo,
            "alpha_vantage": self.alpha_vantage,
            "fmp": self.fmp
        }
        
        # Try preferred source first
        if preferred_source in sources:
            try:
                logger.debug(f"[MCP:Unified] Attempting {preferred_source} for {symbol}")
                result = sources[preferred_source].get_stock_price(symbol)
                elapsed = time.time() - start_time
                logger.info(f"[MCP:Unified] Successfully fetched price from {preferred_source} for {symbol} | Time: {elapsed:.2f}s")
                return result
            except Exception as e:
                logger.warning(f"[MCP:Unified] {preferred_source} failed for {symbol}, trying fallback: {e}")
        
        # Try other sources
        for source_name, source_client in sources.items():
            if source_name != preferred_source:
                try:
                    logger.debug(f"[MCP:Unified] Attempting fallback source {source_name} for {symbol}")
                    result = source_client.get_stock_price(symbol)
                    elapsed = time.time() - start_time
                    logger.info(f"[MCP:Unified] Successfully fetched price from fallback {source_name} for {symbol} | Time: {elapsed:.2f}s")
                    return result
                except Exception as e:
                    logger.warning(f"[MCP:Unified] Fallback {source_name} failed for {symbol}: {e}")
                    continue
        
        elapsed = time.time() - start_time
        logger.error(f"[MCP:Unified] All sources failed to fetch price for {symbol} after {elapsed:.2f}s")
        raise Exception(f"All sources failed to fetch price for {symbol}")
    
    def get_company_info(self, symbol: str, preferred_source: str = "yahoo") -> Dict[str, Any]:
        """
        Get company info with fallback logic
        
        Args:
            symbol: Stock symbol
            preferred_source: Preferred source
        
        Returns:
            Company information with citation
        
        Raises:
            GuardrailsError: If symbol validation fails
        """
        # Validate symbol with guardrails
        is_valid, error = guardrails.validate_symbol(symbol)
        if not is_valid:
            logger.error(f"Symbol validation failed: {error}")
            raise GuardrailsError(f"Invalid symbol: {error}")
        
        # Validate data source
        is_valid, error = guardrails.validate_data_source(preferred_source)
        if not is_valid:
            logger.warning(f"Data source validation failed: {error}, using default")
            preferred_source = "yahoo"
        
        sources = {
            "yahoo": self.yahoo,
            "alpha_vantage": self.alpha_vantage,
            "fmp": self.fmp
        }
        
        if preferred_source in sources:
            try:
                return sources[preferred_source].get_company_info(symbol)
            except Exception as e:
                logger.warning(f"{preferred_source} failed for {symbol}, trying fallback: {e}")
        
        for source_name, source_client in sources.items():
            if source_name != preferred_source:
                try:
                    return source_client.get_company_info(symbol)
                except Exception as e:
                    logger.warning(f"{source_name} failed for {symbol}: {e}")
                    continue
        
        raise Exception(f"All sources failed to fetch company info for {symbol}")
    
    def get_all_citations(self) -> List[Dict[str, Any]]:
        """Get all citations from all clients"""
        citations = []
        citations.extend(self.yahoo.citation_tracker.get_all_citations())
        citations.extend(self.alpha_vantage.citation_tracker.get_all_citations())
        citations.extend(self.fmp.citation_tracker.get_all_citations())
        return citations


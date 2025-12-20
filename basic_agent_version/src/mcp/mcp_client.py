"""Unified MCP client wrapper"""

from typing import Dict, Any, Optional, List, Callable
from loguru import logger
from dotenv import load_dotenv
from .yahoo_finance import YahooFinanceClient
from .alpha_vantage import AlphaVantageClient
from .fmp import FMPClient
from ..utils.citations import CitationTracker
from ..utils.guardrails import guardrails, GuardrailsError
from ..utils.integration_config import integration_config
from ..utils.progress_tracker import ProgressTracker

# Load environment variables
load_dotenv()


class UnifiedMCPClient:
    """Unified wrapper for all MCP clients with fallback logic and integration control"""
    
    def __init__(self):
        """Initialize unified MCP client"""
        self.integration_config = integration_config
        self.yahoo = YahooFinanceClient()
        self.alpha_vantage = AlphaVantageClient()
        self.fmp = FMPClient()
        self.citation_tracker = CitationTracker()
        
        # Map integration names to client instances
        self._client_map = {
            "yahoo_finance": self.yahoo,
            "alpha_vantage": self.alpha_vantage,
            "fmp": self.fmp
        }
    
    def _is_integration_enabled(self, integration_name: str) -> bool:
        """Check if an integration is enabled"""
        return self.integration_config.is_enabled(integration_name)
    
    def _try_source(self, source_name: str, method_name: str, symbol: str, 
                   data_type: Optional[str] = None, state: Optional[Any] = None,
                   *args, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Try calling a method on a source with error handling and status tracking
        
        Args:
            source_name: Name of the source (yahoo_finance, alpha_vantage, fmp)
            method_name: Method name to call (get_stock_price, get_company_info, etc.)
            symbol: Stock symbol
            data_type: Data type being fetched (for status tracking)
            state: Optional AgentState to add progress events
            *args, **kwargs: Additional arguments for the method
        
        Returns:
            Result if successful, None if failed
        """
        # Check if integration is enabled
        if not self._is_integration_enabled(source_name):
            logger.debug(f"[MCP:Unified] {source_name} is disabled, skipping")
            if state:
                self._add_api_event(state, "api_call_skipped", source_name, symbol, data_type, 
                                  "skipped", "Integration disabled")
            return None
        
        # Get client instance
        client = self._client_map.get(source_name)
        if not client:
            logger.warning(f"[MCP:Unified] Unknown source: {source_name}")
            return None
        
        # Get method
        method = getattr(client, method_name, None)
        if not method:
            logger.debug(f"[MCP:Unified] Method {method_name} not found on {source_name}, skipping")
            return None
        
        # Emit API call start event
        if state:
            self._add_api_event(state, "api_call_start", source_name, symbol, data_type, "running")
        
        try:
            # Call method with symbol as first positional arg, then *args and **kwargs
            result = method(symbol, *args, **kwargs)
            if result:
                logger.debug(f"[MCP:Unified] {source_name}.{method_name} succeeded for {symbol}")
                if state:
                    self._add_api_event(state, "api_call_success", source_name, symbol, data_type, "success")
                return result
            else:
                logger.debug(f"[MCP:Unified] {source_name}.{method_name} returned empty result for {symbol}")
                if state:
                    self._add_api_event(state, "api_call_failed", source_name, symbol, data_type, 
                                      "failed", "Empty result returned")
        except Exception as e:
            error_msg = str(e)
            logger.debug(f"[MCP:Unified] {source_name}.{method_name} failed for {symbol}: {e}")
            if state:
                self._add_api_event(state, "api_call_failed", source_name, symbol, data_type, 
                                  "failed", error_msg)
        
        return None
    
    def _add_api_event(self, state: Any, event_type: str, integration: str, symbol: str,
                      data_type: Optional[str] = None, status: str = "success",
                      error: Optional[str] = None):
        """Add API call event to state"""
        try:
            from ..orchestrator.state import StateManager
            
            # Get transaction_id from state
            transaction_id = state.get("transaction_id") if isinstance(state, dict) else None
            
            # Create API call event
            event = ProgressTracker.create_api_call_event(
                event_type=event_type,
                integration=integration,
                symbol=symbol,
                data_type=data_type,
                status=status,
                error=error,
                agent="Research Agent",  # Default agent, can be overridden
                transaction_id=transaction_id
            )
            
            # Add to state
            if isinstance(state, dict):
                StateManager.add_progress_event(state, event)
        except Exception as e:
            logger.debug(f"[MCP:Unified] Error adding API event: {e}")
    
    def get_stock_price(self, symbol: str, preferred_source: Optional[str] = None, 
                       state: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get current stock price with optimized source selection.
        
        This method retrieves real-time stock price data using the best available integration.
        It automatically selects the optimal data source and stops after the first successful call
        to avoid redundant API requests.
        
        DATA SOURCE PRIORITY (in order):
        1. yahoo_finance (preferred - fastest, no API key required)
        2. alpha_vantage (fallback - requires API key, rate limited)
        3. fmp (fallback - requires API key)
        
        USE THIS METHOD WHEN:
        - You need current stock price
        - You need real-time market data (price, volume, market cap)
        - You need day trading range (high/low)
        
        OPTIMIZATION:
        - Stops after first successful API call (no redundant requests)
        - Only tries enabled integrations
        - Tracks API call status in progress events if state provided
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "MSFT"). Must be valid ticker.
            preferred_source: Optional preferred source name. Valid values:
                - "yahoo" or "yahoo_finance": Yahoo Finance (preferred)
                - "alpha_vantage": Alpha Vantage API
                - "fmp": Financial Modeling Prep API
                If not provided, uses automatic source selection based on availability.
            state: Optional AgentState to track API call status in progress events.
        
        Returns:
            Dictionary containing stock price data (current_price, previous_close, volume, etc.)
            with citation information.
        
        Raises:
            GuardrailsError: If symbol validation fails
            Exception: If all enabled sources fail or symbol is invalid
        """
        import time
        start_time = time.time()
        logger.debug(f"[MCP:Unified] Getting stock price for {symbol}")
        
        # Validate symbol with guardrails
        is_valid, error = guardrails.validate_symbol(symbol)
        if not is_valid:
            logger.error(f"[MCP:Unified] Symbol validation failed: {error}")
            raise GuardrailsError(f"Invalid symbol: {error}")
        
        # Get enabled sources for stock_price data type (in preferred order)
        enabled_sources = self.integration_config.get_enabled_sources_for_data_type("stock_price")
        
        if not enabled_sources:
            elapsed = time.time() - start_time
            logger.error(f"[MCP:Unified] No enabled sources for stock_price data type")
            raise Exception("No enabled integrations available for stock price data")
        
        # Normalize source name mapping
        source_mapping = {
            "yahoo": "yahoo_finance",
            "alpha_vantage": "alpha_vantage",
            "fmp": "fmp"
        }
        
        # Try preferred source first (if provided and enabled)
        if preferred_source:
            preferred_source_normalized = source_mapping.get(preferred_source, preferred_source)
            
            if preferred_source_normalized in enabled_sources:
                result = self._try_source(preferred_source_normalized, "get_stock_price", symbol, 
                                        data_type="stock_price", state=state)
                if result:
                    elapsed = time.time() - start_time
                    logger.info(f"[MCP:Unified] Successfully fetched price from {preferred_source_normalized} for {symbol} | Time: {elapsed:.2f}s")
                    return result
                logger.debug(f"[MCP:Unified] Preferred source {preferred_source_normalized} failed, trying alternatives")
        
        # Try sources in preferred order (skip preferred_source if already tried)
        for source_name in enabled_sources:
            if preferred_source and source_mapping.get(preferred_source, preferred_source) == source_name:
                continue  # Already tried
            
            result = self._try_source(source_name, "get_stock_price", symbol, 
                                    data_type="stock_price", state=state)
            if result:
                elapsed = time.time() - start_time
                logger.info(f"[MCP:Unified] Successfully fetched price from {source_name} for {symbol} | Time: {elapsed:.2f}s")
                return result
        
        elapsed = time.time() - start_time
        logger.error(f"[MCP:Unified] All enabled sources failed to fetch price for {symbol} after {elapsed:.2f}s")
        raise Exception(f"All enabled sources failed to fetch price for {symbol}")
    
    def get_company_info(self, symbol: str, preferred_source: Optional[str] = None,
                        state: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get company info with optimized source selection (stops after first success)
        
        Args:
            symbol: Stock symbol
            preferred_source: Optional preferred source
        
        Returns:
            Company information with citation
        
        Raises:
            GuardrailsError: If symbol validation fails
            Exception: If all enabled sources fail
        """
        import time
        start_time = time.time()
        logger.debug(f"[MCP:Unified] Getting company info for {symbol}")
        
        # Validate symbol with guardrails
        is_valid, error = guardrails.validate_symbol(symbol)
        if not is_valid:
            logger.error(f"[MCP:Unified] Symbol validation failed: {error}")
            raise GuardrailsError(f"Invalid symbol: {error}")
        
        # Get enabled sources for company_info data type (in preferred order)
        enabled_sources = self.integration_config.get_enabled_sources_for_data_type("company_info")
        
        if not enabled_sources:
            elapsed = time.time() - start_time
            logger.error(f"[MCP:Unified] No enabled sources for company_info data type")
            raise Exception("No enabled integrations available for company info data")
        
        # Try preferred source first (if provided and enabled)
        if preferred_source:
            source_mapping = {
                "yahoo": "yahoo_finance",
                "alpha_vantage": "alpha_vantage",
                "fmp": "fmp"
            }
            preferred_source_normalized = source_mapping.get(preferred_source, preferred_source)
            
            if preferred_source_normalized in enabled_sources:
                result = self._try_source(preferred_source_normalized, "get_company_info", symbol,
                                        data_type="company_info", state=state)
                if result:
                    elapsed = time.time() - start_time
                    logger.info(f"[MCP:Unified] Successfully fetched company info from {preferred_source_normalized} for {symbol} | Time: {elapsed:.2f}s")
                    return result
        
        # Try sources in preferred order
        for source_name in enabled_sources:
            if preferred_source and source_mapping.get(preferred_source, preferred_source) == source_name:
                continue  # Already tried
            
            result = self._try_source(source_name, "get_company_info", symbol,
                                    data_type="company_info", state=state)
            if result:
                elapsed = time.time() - start_time
                logger.info(f"[MCP:Unified] Successfully fetched company info from {source_name} for {symbol} | Time: {elapsed:.2f}s")
                return result
        
        elapsed = time.time() - start_time
        logger.error(f"[MCP:Unified] All enabled sources failed to fetch company info for {symbol} after {elapsed:.2f}s")
        raise Exception(f"All enabled sources failed to fetch company info for {symbol}")
    
    def get_news(self, symbol: str, count: int = 10, preferred_source: Optional[str] = None,
                state: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get news with optimized source selection (stops after first success)
        
        Args:
            symbol: Stock symbol
            count: Number of news articles to fetch
            preferred_source: Optional preferred source
        
        Returns:
            News data with citation
        
        Raises:
            GuardrailsError: If symbol validation fails
            Exception: If all enabled sources fail
        """
        import time
        start_time = time.time()
        logger.debug(f"[MCP:Unified] Getting news for {symbol}")
        
        # Validate symbol
        is_valid, error = guardrails.validate_symbol(symbol)
        if not is_valid:
            logger.error(f"[MCP:Unified] Symbol validation failed: {error}")
            raise GuardrailsError(f"Invalid symbol: {error}")
        
        # Get enabled sources for news data type
        enabled_sources = self.integration_config.get_enabled_sources_for_data_type("news")
        
        if not enabled_sources:
            elapsed = time.time() - start_time
            logger.error(f"[MCP:Unified] No enabled sources for news data type")
            raise Exception("No enabled integrations available for news data")
        
        # Try preferred source first
        if preferred_source:
            source_mapping = {"yahoo": "yahoo_finance", "fmp": "fmp"}
            preferred_source_normalized = source_mapping.get(preferred_source, preferred_source)
            
            if preferred_source_normalized in enabled_sources:
                if preferred_source_normalized == "yahoo_finance":
                    result = self._try_source(preferred_source_normalized, "get_news", symbol,
                                            data_type="news", state=state, count=count)
                elif preferred_source_normalized == "fmp":
                    result = self._try_source(preferred_source_normalized, "get_news", symbol,
                                            data_type="news", state=state, limit=count)
                else:
                    result = None
                
                if result:
                    elapsed = time.time() - start_time
                    logger.info(f"[MCP:Unified] Successfully fetched news from {preferred_source_normalized} for {symbol} | Time: {elapsed:.2f}s")
                    return result
        
        # Try sources in preferred order
        for source_name in enabled_sources:
            if preferred_source and source_mapping.get(preferred_source, preferred_source) == source_name:
                continue
            
            # Handle different method signatures
            if source_name == "yahoo_finance":
                result = self._try_source(source_name, "get_news", symbol, data_type="news", state=state, count=count)
            elif source_name == "fmp":
                result = self._try_source(source_name, "get_news", symbol, data_type="news", state=state, limit=count)
            else:
                continue
            
            if result:
                elapsed = time.time() - start_time
                logger.info(f"[MCP:Unified] Successfully fetched news from {source_name} for {symbol} | Time: {elapsed:.2f}s")
                return result
        
        elapsed = time.time() - start_time
        logger.error(f"[MCP:Unified] All enabled sources failed to fetch news for {symbol} after {elapsed:.2f}s")
        raise Exception(f"All enabled sources failed to fetch news for {symbol}")
    
    def get_historical_data(self, symbol: str, period: str = "6mo", preferred_source: Optional[str] = None,
                          state: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get historical data with optimized source selection (stops after first success)
        
        Args:
            symbol: Stock symbol
            period: Period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            preferred_source: Optional preferred source (only yahoo_finance supports historical)
        
        Returns:
            Historical data with citation
        
        Raises:
            GuardrailsError: If symbol validation fails
            Exception: If all enabled sources fail
        """
        import time
        start_time = time.time()
        logger.debug(f"[MCP:Unified] Getting historical data for {symbol}")
        
        # Validate symbol
        is_valid, error = guardrails.validate_symbol(symbol)
        if not is_valid:
            logger.error(f"[MCP:Unified] Symbol validation failed: {error}")
            raise GuardrailsError(f"Invalid symbol: {error}")
        
        # Get enabled sources for historical_data data type (only Yahoo Finance)
        enabled_sources = self.integration_config.get_enabled_sources_for_data_type("historical_data")
        
        if not enabled_sources:
            elapsed = time.time() - start_time
            logger.error(f"[MCP:Unified] No enabled sources for historical_data data type")
            raise Exception("No enabled integrations available for historical data")
        
        # Try sources (only yahoo_finance supports historical data)
        for source_name in enabled_sources:
            result = self._try_source(source_name, "get_historical_data", symbol,
                                    data_type="historical_data", state=state, period=period)
            if result:
                elapsed = time.time() - start_time
                logger.info(f"[MCP:Unified] Successfully fetched historical data from {source_name} for {symbol} | Time: {elapsed:.2f}s")
                return result
        
        elapsed = time.time() - start_time
        logger.error(f"[MCP:Unified] All enabled sources failed to fetch historical data for {symbol} after {elapsed:.2f}s")
        raise Exception(f"All enabled sources failed to fetch historical data for {symbol}")
    
    def get_financial_statements(self, symbol: str, statement_type: str = "income-statement",
                                preferred_source: Optional[str] = None, state: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get financial statements with optimized source selection (stops after first success)
        
        Args:
            symbol: Stock symbol
            statement_type: Type of statement (income-statement, balance-sheet-statement, cash-flow-statement)
            preferred_source: Optional preferred source
        
        Returns:
            Financial statements with citation
        
        Raises:
            GuardrailsError: If symbol validation fails
            Exception: If all enabled sources fail
        """
        import time
        start_time = time.time()
        logger.debug(f"[MCP:Unified] Getting financial statements for {symbol}")
        
        # Validate symbol
        is_valid, error = guardrails.validate_symbol(symbol)
        if not is_valid:
            logger.error(f"[MCP:Unified] Symbol validation failed: {error}")
            raise GuardrailsError(f"Invalid symbol: {error}")
        
        # Get enabled sources for financial_statements data type
        enabled_sources = self.integration_config.get_enabled_sources_for_data_type("financial_statements")
        
        if not enabled_sources:
            elapsed = time.time() - start_time
            logger.error(f"[MCP:Unified] No enabled sources for financial_statements data type")
            raise Exception("No enabled integrations available for financial statements")
        
        # Try preferred source first
        if preferred_source:
            source_mapping = {"yahoo": "yahoo_finance", "fmp": "fmp"}
            preferred_source_normalized = source_mapping.get(preferred_source, preferred_source)
            
            if preferred_source_normalized in enabled_sources:
                # Handle different method signatures
                if preferred_source_normalized == "fmp":
                    result = self._try_source(preferred_source_normalized, "get_financial_statements", symbol,
                                            data_type="financial_statements", state=state, statement_type=statement_type)
                elif preferred_source_normalized == "yahoo_finance":
                    result = self._try_source(preferred_source_normalized, "get_financials", symbol,
                                            data_type="financial_statements", state=state)
                else:
                    result = None
                
                if result:
                    elapsed = time.time() - start_time
                    logger.info(f"[MCP:Unified] Successfully fetched financials from {preferred_source_normalized} for {symbol} | Time: {elapsed:.2f}s")
                    return result
        
        # Try sources in preferred order
        for source_name in enabled_sources:
            if preferred_source and source_mapping.get(preferred_source, preferred_source) == source_name:
                continue
            
            # Handle different method signatures
            if source_name == "fmp":
                result = self._try_source(source_name, "get_financial_statements", symbol,
                                        data_type="financial_statements", state=state, statement_type=statement_type)
            elif source_name == "yahoo_finance":
                result = self._try_source(source_name, "get_financials", symbol,
                                        data_type="financial_statements", state=state)
            else:
                continue
            
            if result:
                elapsed = time.time() - start_time
                logger.info(f"[MCP:Unified] Successfully fetched financials from {source_name} for {symbol} | Time: {elapsed:.2f}s")
                return result
        
        elapsed = time.time() - start_time
        logger.error(f"[MCP:Unified] All enabled sources failed to fetch financials for {symbol} after {elapsed:.2f}s")
        raise Exception(f"All enabled sources failed to fetch financials for {symbol}")
    
    def get_technical_indicators(self, symbol: str, indicator: str = "SMA", preferred_source: Optional[str] = None,
                               state: Optional[Any] = None) -> Dict[str, Any]:
        """
        Get technical indicators with optimized source selection (stops after first success)
        
        Args:
            symbol: Stock symbol
            indicator: Technical indicator type (SMA, EMA, RSI, MACD, etc.)
            preferred_source: Optional preferred source (only alpha_vantage supports technical indicators)
        
        Returns:
            Technical indicators with citation
        
        Raises:
            GuardrailsError: If symbol validation fails
            Exception: If all enabled sources fail
        """
        import time
        start_time = time.time()
        logger.debug(f"[MCP:Unified] Getting technical indicators for {symbol}")
        
        # Validate symbol
        is_valid, error = guardrails.validate_symbol(symbol)
        if not is_valid:
            logger.error(f"[MCP:Unified] Symbol validation failed: {error}")
            raise GuardrailsError(f"Invalid symbol: {error}")
        
        # Get enabled sources for technical_indicators data type (only Alpha Vantage)
        enabled_sources = self.integration_config.get_enabled_sources_for_data_type("technical_indicators")
        
        if not enabled_sources:
            elapsed = time.time() - start_time
            logger.error(f"[MCP:Unified] No enabled sources for technical_indicators data type")
            raise Exception("No enabled integrations available for technical indicators")
        
        # Try sources (only alpha_vantage supports technical indicators)
        for source_name in enabled_sources:
            result = self._try_source(source_name, "get_technical_indicators", symbol,
                                    data_type="technical_indicators", state=state, indicator=indicator)
            if result:
                elapsed = time.time() - start_time
                logger.info(f"[MCP:Unified] Successfully fetched technical indicators from {source_name} for {symbol} | Time: {elapsed:.2f}s")
                return result
        
        elapsed = time.time() - start_time
        logger.error(f"[MCP:Unified] All enabled sources failed to fetch technical indicators for {symbol} after {elapsed:.2f}s")
        raise Exception(f"All enabled sources failed to fetch technical indicators for {symbol}")
    
    def get_all_citations(self) -> List[Dict[str, Any]]:
        """Get all citations from all clients"""
        citations = []
        citations.extend(self.yahoo.citation_tracker.get_all_citations())
        citations.extend(self.alpha_vantage.citation_tracker.get_all_citations())
        citations.extend(self.fmp.citation_tracker.get_all_citations())
        return citations


"""Alpha Vantage MCP client"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from .mcp_base import MCPBaseClient


class AlphaVantageClient(MCPBaseClient):
    """Alpha Vantage API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage client
        
        Args:
            api_key: Alpha Vantage API key (from env if not provided)
        """
        api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            logger.warning("Alpha Vantage API key not found. Some features may not work.")
        
        super().__init__(
            name="Alpha Vantage",
            base_url="https://www.alphavantage.co/query",
            api_key=api_key
        )
        self.rate_limit_delay = 12.0  # Free tier: 5 calls per minute
    
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price (real-time quote)
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Stock price data with citation
        """
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            data = self._make_request("", params=params)
            
            if "Error Message" in data:
                raise Exception(data["Error Message"])
            
            quote = data.get("Global Quote", {})
            
            price_data = {
                "symbol": symbol,
                "current_price": float(quote.get("05. price", 0)),
                "previous_close": float(quote.get("08. previous close", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "volume": int(quote.get("06. volume", 0)),
                "high": float(quote.get("03. high", 0)),
                "low": float(quote.get("04. low", 0)),
                "open": float(quote.get("02. open", 0)),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Alpha Vantage",
                url=f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}",
                date=datetime.now().isoformat(),
                data_point="stock_price",
                symbol=symbol
            )
            
            return price_data
        
        except Exception as e:
            logger.error(f"Alpha Vantage: Error fetching price for {symbol}: {e}")
            raise
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get company overview
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Company information with citation
        """
        try:
            params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            data = self._make_request("", params=params)
            
            if "Error Message" in data:
                raise Exception(data["Error Message"])
            
            company_info = {
                "symbol": symbol,
                "name": data.get("Name"),
                "sector": data.get("Sector"),
                "industry": data.get("Industry"),
                "description": data.get("Description"),
                "employees": data.get("FullTimeEmployees"),
                "website": data.get("Website"),
                "address": data.get("Address"),
                "market_cap": data.get("MarketCapitalization"),
                "pe_ratio": data.get("PERatio"),
                "dividend_yield": data.get("DividendYield"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Alpha Vantage",
                url=f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}",
                date=datetime.now().isoformat(),
                data_point="company_info",
                symbol=symbol
            )
            
            return company_info
        
        except Exception as e:
            logger.error(f"Alpha Vantage: Error fetching company info for {symbol}: {e}")
            raise
    
    def get_technical_indicators(self, symbol: str, indicator: str = "SMA", 
                                interval: str = "daily", time_period: int = 20) -> Dict[str, Any]:
        """
        Get technical analysis indicators for stock price analysis.
        
        This method retrieves technical indicators calculated from price data. Alpha Vantage is
        the ONLY integration that provides technical indicators. Use this for technical analysis.
        
        USE THIS METHOD WHEN:
        - You need technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, etc.)
        - You need technical analysis for trading signals
        - You need momentum indicators or trend indicators
        - You need support/resistance levels
        
        DO NOT USE THIS METHOD FOR:
        - Stock price data (use get_stock_price instead)
        - Company information (use get_company_info instead)
        - Financial statements (use FMP get_financial_statements instead)
        - Historical price data (use Yahoo Finance get_historical_data instead)
        
        NOTE: Alpha Vantage is the ONLY data source that provides technical indicators.
        Other integrations (Yahoo Finance, FMP) do not provide technical indicators.
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "MSFT"). Must be valid ticker.
            indicator: Technical indicator type. Common values:
                - "SMA": Simple Moving Average
                - "EMA": Exponential Moving Average
                - "RSI": Relative Strength Index
                - "MACD": Moving Average Convergence Divergence
                - "BBANDS": Bollinger Bands
                - "STOCH": Stochastic Oscillator
                - "ADX": Average Directional Index
                Default: "SMA"
            interval: Time interval for data points. Valid values:
                - "1min", "5min", "15min", "30min", "60min": Intraday intervals
                - "daily", "weekly", "monthly": Daily/weekly/monthly intervals
                Default: "daily"
            time_period: Number of data points to use for calculation (e.g., 20 for 20-day SMA)
                Default: 20
        
        Returns:
            Dictionary containing:
            - symbol: Stock symbol
            - indicator: Indicator type requested
            - interval: Time interval used
            - time_period: Time period used
            - data: Dictionary of indicator values keyed by date/time
            - timestamp: ISO timestamp of data retrieval
        
        Raises:
            Exception: If symbol is invalid, indicator invalid, data unavailable, or API error occurs
        """
        try:
            params = {
                "function": indicator,
                "symbol": symbol,
                "interval": interval,
                "time_period": time_period,
                "series_type": "close",
                "apikey": self.api_key
            }
            
            data = self._make_request("", params=params)
            
            if "Error Message" in data:
                raise Exception(data["Error Message"])
            
            indicator_data = {
                "symbol": symbol,
                "indicator": indicator,
                "interval": interval,
                "time_period": time_period,
                "data": data.get(f"Technical Analysis: {indicator}", {}),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Alpha Vantage",
                url=f"https://www.alphavantage.co/query?function={indicator}&symbol={symbol}",
                date=datetime.now().isoformat(),
                data_point="technical_indicators",
                symbol=symbol
            )
            
            return indicator_data
        
        except Exception as e:
            logger.error(f"Alpha Vantage: Error fetching indicators for {symbol}: {e}")
            raise


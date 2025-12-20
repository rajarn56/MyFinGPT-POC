"""Yahoo Finance MCP client"""

import yfinance as yf
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from .mcp_base import MCPBaseClient


class YahooFinanceClient(MCPBaseClient):
    """Yahoo Finance client using yfinance library"""
    
    def __init__(self):
        """Initialize Yahoo Finance client"""
        super().__init__(
            name="Yahoo Finance",
            base_url=None,  # yfinance doesn't use base URL
            api_key=None  # No API key needed
        )
    
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price and real-time market data for a stock symbol.
        
        This method retrieves real-time or near-real-time stock price data including current price,
        previous close, market cap, volume, day high/low, and 52-week high/low.
        
        USE THIS METHOD WHEN:
        - You need current stock price data
        - You need real-time market data (price, volume, market cap)
        - You need 52-week high/low for context
        - You need day trading range (high/low)
        
        DO NOT USE THIS METHOD FOR:
        - Historical price data (use get_historical_data instead)
        - Financial statements (use get_financials instead)
        - Company profile information (use get_company_info instead)
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "MSFT", "GOOGL"). Must be valid ticker.
        
        Returns:
            Dictionary containing:
            - symbol: Stock symbol
            - current_price: Current trading price (float)
            - previous_close: Previous day's closing price (float)
            - market_cap: Market capitalization (int)
            - volume: Trading volume (int)
            - day_high: Day's highest price (float)
            - day_low: Day's lowest price (float)
            - 52_week_high: 52-week high price (float)
            - 52_week_low: 52-week low price (float)
            - timestamp: ISO timestamp of data retrieval
        
        Raises:
            Exception: If symbol is invalid, data unavailable, or API error occurs
        """
        import time
        start_time = time.time()
        logger.debug(f"[MCP:YahooFinance] Fetching stock price for {symbol}")
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price
            current_data = ticker.history(period="1d")
            
            price_data = {
                "symbol": symbol,
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "previous_close": info.get("previousClose"),
                "market_cap": info.get("marketCap"),
                "volume": info.get("volume"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Yahoo Finance",
                url=f"https://finance.yahoo.com/quote/{symbol}",
                date=datetime.now().isoformat(),
                data_point="stock_price",
                symbol=symbol
            )
            
            elapsed = time.time() - start_time
            logger.info(f"[MCP:YahooFinance] Stock price fetched for {symbol} | "
                       f"Price: ${price_data.get('current_price')} | "
                       f"Time: {elapsed:.2f}s")
            return price_data
        
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"[MCP:YahooFinance] Error fetching price for {symbol} after {elapsed:.2f}s: {e}", exc_info=True)
            raise
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get company profile and business information for a stock symbol.
        
        This method retrieves company profile data including business description, sector,
        industry classification, employee count, headquarters location, and website.
        
        USE THIS METHOD WHEN:
        - You need company profile and business description
        - You need sector/industry classification
        - You need company metadata (employees, location, website)
        - You need company overview for analysis context
        
        DO NOT USE THIS METHOD FOR:
        - Stock price data (use get_stock_price instead)
        - Financial statements (use get_financials instead)
        - Historical price data (use get_historical_data instead)
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "MSFT"). Must be valid ticker.
        
        Returns:
            Dictionary containing:
            - symbol: Stock symbol
            - name: Company full name (str)
            - sector: Business sector (str, e.g., "Technology", "Healthcare")
            - industry: Industry classification (str)
            - description: Company business summary (str)
            - employees: Number of employees (int)
            - website: Company website URL (str)
            - headquarters: Headquarters address (str)
            - timestamp: ISO timestamp of data retrieval
        
        Raises:
            Exception: If symbol is invalid, company data unavailable, or API error occurs
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            company_info = {
                "symbol": symbol,
                "name": info.get("longName") or info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "description": info.get("longBusinessSummary"),
                "employees": info.get("fullTimeEmployees"),
                "website": info.get("website"),
                "headquarters": info.get("address1"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Yahoo Finance",
                url=f"https://finance.yahoo.com/quote/{symbol}/profile",
                date=datetime.now().isoformat(),
                data_point="company_info",
                symbol=symbol
            )
            
            return company_info
        
        except Exception as e:
            logger.error(f"Yahoo Finance: Error fetching company info for {symbol}: {e}")
            raise
    
    def get_historical_data(self, symbol: str, period: str = "6mo") -> Dict[str, Any]:
        """
        Get historical stock price data for trend analysis and charting.
        
        This method retrieves historical OHLCV (Open, High, Low, Close, Volume) price data
        for a specified time period. This is the ONLY integration that provides historical data.
        
        USE THIS METHOD WHEN:
        - You need historical price data for trend analysis
        - You need data for price charts and visualizations
        - You need to analyze price movements over time
        - You need OHLCV data for technical analysis
        
        DO NOT USE THIS METHOD FOR:
        - Current stock price (use get_stock_price instead)
        - Company information (use get_company_info instead)
        - Financial statements (use get_financials instead)
        
        NOTE: This is the ONLY data source that provides historical price data.
        Other integrations (Alpha Vantage, FMP) do not provide historical data.
        
        Args:
            symbol: Stock ticker symbol (e.g., "AAPL", "MSFT"). Must be valid ticker.
            period: Time period for historical data. Valid values:
                - "1d", "5d": Short-term (1 day, 5 days)
                - "1mo", "3mo", "6mo": Medium-term (1, 3, 6 months)
                - "1y", "2y", "5y", "10y": Long-term (1, 2, 5, 10 years)
                - "ytd": Year-to-date
                - "max": Maximum available history
                Default: "6mo"
        
        Returns:
            Dictionary containing:
            - symbol: Stock symbol
            - period: Requested period
            - data: List of daily price records with Open, High, Low, Close, Volume
            - dates: List of date strings (YYYY-MM-DD format)
            - timestamp: ISO timestamp of data retrieval
        
        Raises:
            Exception: If symbol is invalid, period invalid, data unavailable, or API error occurs
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            # Convert to dictionary format
            historical_data = {
                "symbol": symbol,
                "period": period,
                "data": hist.to_dict('records') if not hist.empty else [],
                "dates": hist.index.strftime('%Y-%m-%d').tolist() if not hist.empty else [],
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Yahoo Finance",
                url=f"https://finance.yahoo.com/quote/{symbol}/history",
                date=datetime.now().isoformat(),
                data_point="historical_data",
                symbol=symbol
            )
            
            return historical_data
        
        except Exception as e:
            logger.error(f"Yahoo Finance: Error fetching historical data for {symbol}: {e}")
            raise
    
    def get_financials(self, symbol: str) -> Dict[str, Any]:
        """
        Get financial statements
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Financial statements with citation
        """
        try:
            ticker = yf.Ticker(symbol)
            
            financials = {
                "symbol": symbol,
                "income_statement": ticker.financials.to_dict() if not ticker.financials.empty else {},
                "balance_sheet": ticker.balance_sheet.to_dict() if not ticker.balance_sheet.empty else {},
                "cash_flow": ticker.cashflow.to_dict() if not ticker.cashflow.empty else {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Yahoo Finance",
                url=f"https://finance.yahoo.com/quote/{symbol}/financials",
                date=datetime.now().isoformat(),
                data_point="financial_statements",
                symbol=symbol
            )
            
            return financials
        
        except Exception as e:
            logger.error(f"Yahoo Finance: Error fetching financials for {symbol}: {e}")
            raise
    
    def get_news(self, symbol: str, count: int = 10) -> Dict[str, Any]:
        """
        Get news articles
        
        Args:
            symbol: Stock symbol
            count: Number of articles
        
        Returns:
            News articles with citation
        """
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news[:count] if ticker.news else []
            
            news_data = {
                "symbol": symbol,
                "articles": [
                    {
                        "title": article.get("title"),
                        "publisher": article.get("publisher"),
                        "link": article.get("link"),
                        "published": article.get("providerPublishTime"),
                        "summary": article.get("summary", "")
                    }
                    for article in news
                ],
                "count": len(news),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Yahoo Finance",
                url=f"https://finance.yahoo.com/quote/{symbol}/news",
                date=datetime.now().isoformat(),
                data_point="news_articles",
                symbol=symbol
            )
            
            return news_data
        
        except Exception as e:
            logger.error(f"Yahoo Finance: Error fetching news for {symbol}: {e}")
            raise


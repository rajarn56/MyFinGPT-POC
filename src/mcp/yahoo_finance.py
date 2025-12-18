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
        Get current stock price and basic info
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Stock price data with citation
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
        Get company information
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Company information with citation
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
        Get historical price data
        
        Args:
            symbol: Stock symbol
            period: Period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            Historical data with citation
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


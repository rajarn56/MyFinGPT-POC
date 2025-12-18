"""Financial Modeling Prep (FMP) MCP client"""

import os
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger
from .mcp_base import MCPBaseClient


class FMPClient(MCPBaseClient):
    """Financial Modeling Prep API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FMP client
        
        Args:
            api_key: FMP API key (from env if not provided)
        """
        api_key = api_key or os.getenv("FMP_API_KEY")
        if not api_key:
            logger.warning("FMP API key not found. Some features may not work.")
        
        super().__init__(
            name="Financial Modeling Prep",
            base_url="https://financialmodelingprep.com/api/v3",
            api_key=api_key
        )
        self.rate_limit_delay = 0.5  # Free tier: reasonable rate limit
    
    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None,
                     method: str = "GET", max_retries: int = 3) -> Dict[str, Any]:
        """Override to add API key to params"""
        if params is None:
            params = {}
        params["apikey"] = self.api_key
        return super()._make_request(endpoint, params, method, max_retries)
    
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock price
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Stock price data with citation
        """
        try:
            data = self._make_request(f"/quote/{symbol}")
            
            if not data or len(data) == 0:
                raise Exception(f"No data returned for {symbol}")
            
            quote = data[0]
            
            price_data = {
                "symbol": symbol,
                "current_price": quote.get("price"),
                "previous_close": quote.get("previousClose"),
                "change": quote.get("change"),
                "change_percent": quote.get("changesPercentage"),
                "volume": quote.get("volume"),
                "high": quote.get("dayHigh"),
                "low": quote.get("dayLow"),
                "open": quote.get("open"),
                "market_cap": quote.get("marketCap"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Financial Modeling Prep",
                url=f"https://financialmodelingprep.com/api/v3/quote/{symbol}",
                date=datetime.now().isoformat(),
                data_point="stock_price",
                symbol=symbol
            )
            
            return price_data
        
        except Exception as e:
            logger.error(f"FMP: Error fetching price for {symbol}: {e}")
            raise
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get company profile
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Company information with citation
        """
        try:
            data = self._make_request(f"/profile/{symbol}")
            
            if not data or len(data) == 0:
                raise Exception(f"No profile data returned for {symbol}")
            
            profile = data[0]
            
            company_info = {
                "symbol": symbol,
                "name": profile.get("companyName"),
                "sector": profile.get("sector"),
                "industry": profile.get("industry"),
                "description": profile.get("description"),
                "employees": profile.get("fullTimeEmployees"),
                "website": profile.get("website"),
                "address": profile.get("address"),
                "city": profile.get("city"),
                "state": profile.get("state"),
                "country": profile.get("country"),
                "ceo": profile.get("ceo"),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Financial Modeling Prep",
                url=f"https://financialmodelingprep.com/api/v3/profile/{symbol}",
                date=datetime.now().isoformat(),
                data_point="company_info",
                symbol=symbol
            )
            
            return company_info
        
        except Exception as e:
            logger.error(f"FMP: Error fetching company info for {symbol}: {e}")
            raise
    
    def get_financial_statements(self, symbol: str, statement_type: str = "income-statement") -> Dict[str, Any]:
        """
        Get financial statements
        
        Args:
            symbol: Stock symbol
            statement_type: Type of statement (income-statement, balance-sheet-statement, cash-flow-statement)
        
        Returns:
            Financial statements with citation
        """
        try:
            data = self._make_request(f"/{statement_type}/{symbol}")
            
            financials = {
                "symbol": symbol,
                "statement_type": statement_type,
                "data": data,
                "count": len(data) if isinstance(data, list) else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Financial Modeling Prep",
                url=f"https://financialmodelingprep.com/api/v3/{statement_type}/{symbol}",
                date=datetime.now().isoformat(),
                data_point="financial_statements",
                symbol=symbol
            )
            
            return financials
        
        except Exception as e:
            logger.error(f"FMP: Error fetching financials for {symbol}: {e}")
            raise
    
    def get_news(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get company news
        
        Args:
            symbol: Stock symbol
            limit: Number of articles
        
        Returns:
            News articles with citation
        """
        try:
            data = self._make_request(f"/stock_news", params={"tickers": symbol, "limit": limit})
            
            news_data = {
                "symbol": symbol,
                "articles": [
                    {
                        "title": article.get("title"),
                        "text": article.get("text"),
                        "site": article.get("site"),
                        "url": article.get("url"),
                        "published_date": article.get("publishedDate"),
                        "image": article.get("image")
                    }
                    for article in (data[:limit] if isinstance(data, list) else [])
                ],
                "count": len(data[:limit]) if isinstance(data, list) else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add citation
            self.add_citation(
                source="Financial Modeling Prep",
                url=f"https://financialmodelingprep.com/api/v3/stock_news?tickers={symbol}",
                date=datetime.now().isoformat(),
                data_point="news_articles",
                symbol=symbol
            )
            
            return news_data
        
        except Exception as e:
            logger.error(f"FMP: Error fetching news for {symbol}: {e}")
            raise


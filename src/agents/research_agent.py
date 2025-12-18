"""Research Agent - Gathers raw financial data and news"""

from typing import Dict, Any, List, Tuple
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base_agent import BaseAgent
from ..orchestrator.state import AgentState, StateManager
from ..mcp.mcp_client import UnifiedMCPClient
from ..vector_db.chroma_client import ChromaClient
from ..vector_db.embeddings import EmbeddingPipeline
from ..utils.parallelization import ParallelizationStrategy
from ..utils.context_cache import ContextCache


class ResearchAgent(BaseAgent):
    """Research Agent - Fetches financial data from multiple sources"""
    
    def __init__(self, provider: str = None, context_cache: ContextCache = None):
        """
        Initialize Research Agent
        
        Args:
            provider: LLM provider name
            context_cache: Optional context cache instance
        """
        super().__init__(name="Research Agent", provider=provider)
        self.mcp_client = UnifiedMCPClient()
        self.vector_db = ChromaClient()
        self.embedding_pipeline = EmbeddingPipeline()
        self.context_cache = context_cache or ContextCache()
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute research agent logic with automatic parallelization
        
        Args:
            state: Current AgentState
        
        Returns:
            Updated AgentState with research_data
        """
        query = self.read_context(state, "query", "")
        symbols = self.read_context(state, "symbols", [])
        query_type = self.read_context(state, "query_type", "single_stock")
        
        logger.info(f"Research Agent: Processing query for symbols: {symbols}")
        
        # Initialize research_data if not present
        research_data = self.read_context(state, "research_data", {})
        research_metadata = self.read_context(state, "research_metadata", {})
        
        # Track partial success
        symbol_status = self.read_context(state, "symbol_status", {})
        symbol_errors = self.read_context(state, "symbol_errors", {})
        
        if len(symbols) == 1:
            # Single symbol: parallelize data fetching (within-agent parallelization)
            symbol = symbols[0]
            logger.info(f"Research Agent: Processing single symbol {symbol} with parallel data fetching")
            state = self._fetch_all_data_parallel(symbol, query_type, state)
        else:
            # Multiple symbols: parallelize symbols AND data fetching (two-level parallelization)
            logger.info(f"Research Agent: Processing {len(symbols)} symbols with symbol-level parallelization")
            max_workers = ParallelizationStrategy.get_max_workers_data_fetching(symbols)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._fetch_all_data_parallel, symbol, query_type, state): symbol
                    for symbol in symbols
                }
                
                results = []
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        result_state = future.result()
                        results.append(result_state)
                        symbol_status[symbol] = "success"
                        logger.info(f"Research Agent: Completed data collection for {symbol}")
                    except Exception as e:
                        logger.error(f"Research Agent: Error processing {symbol}: {e}")
                        symbol_status[symbol] = "failed"
                        symbol_errors[symbol] = str(e)
                        research_metadata[symbol] = {
                            "error": str(e),
                            "data_quality": "error"
                        }
                        # Continue with other symbols
                        continue
                
                # Merge parallel contexts
                if results:
                    state = StateManager.merge_parallel_contexts(results)
        
        # Update state with research data and status
        state = self.write_context(state, "research_data", research_data)
        state = self.write_context(state, "research_metadata", research_metadata)
        state = self.write_context(state, "symbol_status", symbol_status)
        state = self.write_context(state, "symbol_errors", symbol_errors)
        
        # Set partial_success if any failures occurred
        if any(status == "failed" for status in symbol_status.values()):
            state = self.write_context(state, "partial_success", True)
        
        return state
    
    def _fetch_all_data_parallel(self, symbol: str, query_type: str, state: AgentState) -> AgentState:
        """
        Fetch all data types in parallel for a single symbol
        
        Args:
            symbol: Stock symbol
            query_type: Query type
            state: Current AgentState
        
        Returns:
            Updated AgentState with symbol data
        """
        logger.debug(f"Research Agent: Fetching all data types in parallel for {symbol}")
        
        # Report parallel execution start
        state = self.report_progress_parallel(
            state,
            event_type="task_progress",
            message=f"Fetching data for {symbol} (parallel)",
            symbol=symbol
        )
        
        research_data = self.read_context(state, "research_data", {})
        research_metadata = self.read_context(state, "research_metadata", {})
        
        # Prepare data fetching tasks
        data_types = ParallelizationStrategy.get_data_types()
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(data_types)) as executor:
            futures = {}
            
            # Submit all data fetching tasks
            if "price" in data_types:
                futures[executor.submit(self._fetch_price_data, symbol, state)] = "price"
            if "company" in data_types:
                futures[executor.submit(self._fetch_company_info, symbol, state)] = "company"
            if "news" in data_types:
                futures[executor.submit(self._fetch_news, symbol, state)] = "news"
            if "historical" in data_types and query_type in ["trend", "comparison"]:
                futures[executor.submit(self._fetch_historical, symbol, state)] = "historical"
            if "financials" in data_types and query_type in ["single_stock", "comparison"]:
                futures[executor.submit(self._fetch_financials, symbol, state)] = "financials"
            
            # Collect results as they complete
            for future in as_completed(futures):
                data_type = futures[future]
                try:
                    result = future.result()
                    results[data_type] = result
                    logger.debug(f"Research Agent: Completed {data_type} fetch for {symbol}")
                except Exception as e:
                    logger.warning(f"Research Agent: Error fetching {data_type} for {symbol}: {e}")
                    results[data_type] = None
        
        # Compile symbol data
        symbol_data = {
            "price": results.get("price"),
            "company": results.get("company"),
            "news": results.get("news"),
            "historical": results.get("historical"),
            "financials": results.get("financials")
        }
        
        research_data[symbol] = symbol_data
        
        # Store metadata
        price_data = results.get("price", {})
        research_metadata[symbol] = {
            "timestamp": price_data.get("timestamp") if price_data else None,
            "sources": ["Yahoo Finance", "Alpha Vantage", "FMP"],
            "data_quality": "complete" if all([results.get("price"), results.get("company")]) else "partial"
        }
        
        # Store news articles in vector DB if available
        if results.get("news") and results["news"].get("articles"):
            self._store_news_in_vector_db(symbol, results["news"]["articles"])
        
        # Add citations from MCP clients
        citations = self.mcp_client.get_all_citations()
        for citation in citations:
            if citation.get("symbol") == symbol:
                state = self.add_citation(
                    state,
                    source=citation["source"],
                    url=citation.get("url"),
                    date=citation.get("date"),
                    data_point=citation.get("data_point"),
                    symbol=symbol
                )
        
        # Update state
        state = self.write_context(state, "research_data", research_data)
        state = self.write_context(state, "research_metadata", research_metadata)
        
        return state
    
    def _fetch_price_data(self, symbol: str, state: AgentState) -> Dict[str, Any]:
        """
        Fetch price data with caching
        
        Args:
            symbol: Stock symbol
            state: Current AgentState
        
        Returns:
            Price data dictionary
        """
        # Check cache first
        cached = self.context_cache.get(symbol, "price")
        if cached:
            logger.debug(f"Research Agent: Using cached price data for {symbol}")
            return cached
        
        # Fetch from API
        logger.debug(f"Research Agent: Fetching price data for {symbol}")
        state = self.start_task(state, "Fetch stock price", symbol=symbol)
        price_data = self.mcp_client.get_stock_price(symbol, state=state)
        state = self.complete_task(state, "Fetch stock price", symbol=symbol)
        
        # Cache result
        self.context_cache.set(symbol, "price", price_data)
        
        return price_data
    
    def _fetch_company_info(self, symbol: str, state: AgentState) -> Dict[str, Any]:
        """
        Fetch company info with caching
        
        Args:
            symbol: Stock symbol
            state: Current AgentState
        
        Returns:
            Company info dictionary
        """
        # Check cache first
        cached = self.context_cache.get(symbol, "company")
        if cached:
            logger.debug(f"Research Agent: Using cached company info for {symbol}")
            return cached
        
        # Fetch from API
        logger.debug(f"Research Agent: Fetching company info for {symbol}")
        state = self.start_task(state, "Fetch company info", symbol=symbol)
        company_info = self.mcp_client.get_company_info(symbol, state=state)
        state = self.complete_task(state, "Fetch company info", symbol=symbol)
        
        # Cache result
        self.context_cache.set(symbol, "company", company_info)
        
        return company_info
    
    def _fetch_news(self, symbol: str, state: AgentState) -> Dict[str, Any]:
        """
        Fetch news data with caching
        
        Args:
            symbol: Stock symbol
            state: Current AgentState
        
        Returns:
            News data dictionary or None if error
        """
        # Check cache first
        cached = self.context_cache.get(symbol, "news")
        if cached:
            logger.debug(f"Research Agent: Using cached news data for {symbol}")
            return cached
        
        # Fetch from API
        try:
            logger.debug(f"Research Agent: Fetching news for {symbol}")
            state = self.start_task(state, "Fetch news articles", symbol=symbol)
            news_data = self.mcp_client.get_news(symbol, count=10, state=state)
            state = self.complete_task(state, "Fetch news articles", symbol=symbol)
            
            # Cache result
            self.context_cache.set(symbol, "news", news_data)
            
            return news_data
        except Exception as e:
            logger.warning(f"Research Agent: Could not fetch news for {symbol}: {e}")
            state = self.complete_task(state, "Fetch news articles", symbol=symbol)
            return None
    
    def _fetch_historical(self, symbol: str, state: AgentState) -> Dict[str, Any]:
        """
        Fetch historical data with caching
        
        Args:
            symbol: Stock symbol
            state: Current AgentState
        
        Returns:
            Historical data dictionary or None if error
        """
        # Check cache first
        cached = self.context_cache.get(symbol, "historical")
        if cached:
            logger.debug(f"Research Agent: Using cached historical data for {symbol}")
            return cached
        
        # Fetch from API
        try:
            logger.debug(f"Research Agent: Fetching historical data for {symbol}")
            state = self.start_task(state, "Fetch historical data", symbol=symbol)
            historical_data = self.mcp_client.get_historical_data(symbol, period="6mo", state=state)
            state = self.complete_task(state, "Fetch historical data", symbol=symbol)
            
            # Cache result
            self.context_cache.set(symbol, "historical", historical_data)
            
            return historical_data
        except Exception as e:
            logger.warning(f"Research Agent: Could not fetch historical data for {symbol}: {e}")
            state = self.complete_task(state, "Fetch historical data", symbol=symbol)
            return None
    
    def _fetch_financials(self, symbol: str, state: AgentState) -> Dict[str, Any]:
        """
        Fetch financials with caching
        
        Args:
            symbol: Stock symbol
            state: Current AgentState
        
        Returns:
            Financials dictionary or None if error
        """
        # Check cache first
        cached = self.context_cache.get(symbol, "financials")
        if cached:
            logger.debug(f"Research Agent: Using cached financials for {symbol}")
            return cached
        
        # Fetch from API
        try:
            logger.debug(f"Research Agent: Fetching financials for {symbol}")
            state = self.start_task(state, "Fetch financial statements", symbol=symbol)
            financials = self.mcp_client.get_financial_statements(symbol, state=state)
            state = self.complete_task(state, "Fetch financial statements", symbol=symbol)
            
            # Cache result
            self.context_cache.set(symbol, "financials", financials)
            
            return financials
        except Exception as e:
            logger.warning(f"Research Agent: Could not fetch financials for {symbol}: {e}")
            state = self.complete_task(state, "Fetch financial statements", symbol=symbol)
            return None
    
    def _store_news_in_vector_db(self, symbol: str, articles: List[Dict[str, Any]]):
        """
        Store news articles in vector database
        
        Args:
            symbol: Stock symbol
            articles: List of news articles
        """
        try:
            stored_count = 0
            for article_idx, article in enumerate(articles, 1):
                title = article.get("title", "")
                text = article.get("text") or article.get("summary", "")
                url = article.get("url") or article.get("link", "")
                
                # Create document text
                document_text = f"{title}\n\n{text}"
                
                # Generate embedding
                embedding = self.embedding_pipeline.generate_embedding(document_text)
                
                # Prepare metadata
                metadata = {
                    "symbol": symbol,
                    "title": title,
                    "url": url,
                    "publisher": article.get("publisher") or article.get("site", ""),
                    "published_date": article.get("published") or article.get("publishedDate", ""),
                    "source": "research_agent"
                }
                
                # Store in vector DB
                doc_id = self.vector_db.add_document(
                    collection_name="financial_news",
                    document=document_text,
                    metadata=metadata,
                    embedding=embedding
                )
                stored_count += 1
                logger.debug(f"Research Agent: Stored article {article_idx}/{len(articles)} for {symbol} | ID: {doc_id}")
            
            logger.info(f"Research Agent: Stored {stored_count}/{len(articles)} news articles in vector DB for {symbol}")
        
        except Exception as e:
            logger.warning(f"Research Agent: Error storing news in vector DB for {symbol}: {e}", exc_info=True)


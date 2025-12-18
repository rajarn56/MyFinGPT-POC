"""Analyst Agent - Analyzes data and performs deductions"""

import json
from typing import Dict, Any, List
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base_agent import BaseAgent
from ..orchestrator.state import AgentState, StateManager
from ..vector_db.chroma_client import ChromaClient
from ..vector_db.embeddings import EmbeddingPipeline
from ..utils.parallelization import ParallelizationStrategy


class AnalystAgent(BaseAgent):
    """Analyst Agent - Performs financial analysis and deductions"""
    
    def __init__(self, provider: str = None):
        """
        Initialize Analyst Agent
        
        Args:
            provider: LLM provider name
        """
        super().__init__(name="Analyst Agent", provider=provider)
        self.vector_db = ChromaClient()
        self.embedding_pipeline = EmbeddingPipeline()
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute analyst agent logic with automatic parallelization
        
        Args:
            state: Current AgentState
        
        Returns:
            Updated AgentState with analysis_results
        """
        # Validate required context
        if not self.validate_required_context(state, ["research_data"]):
            logger.error("Analyst Agent: Missing required research_data in context")
            return state
        
        research_data = self.read_context(state, "research_data", {})
        symbols = self.read_context(state, "symbols", [])
        query_type = self.read_context(state, "query_type", "single_stock")
        
        logger.info(f"Analyst Agent: Analyzing data for symbols: {symbols}")
        
        # Initialize analysis results
        analysis_results = self.read_context(state, "analysis_results", {})
        analysis_reasoning = self.read_context(state, "analysis_reasoning", {})
        
        # Track partial success
        symbol_status = self.read_context(state, "symbol_status", {})
        symbol_errors = self.read_context(state, "symbol_errors", {})
        
        # Filter symbols that have research data
        valid_symbols = [s for s in symbols if s in research_data]
        if not valid_symbols:
            logger.warning("Analyst Agent: No valid symbols with research data")
            return state
        
        if len(valid_symbols) == 1:
            # Single symbol: parallelize analysis types (within-agent parallelization)
            symbol = valid_symbols[0]
            logger.info(f"Analyst Agent: Analyzing single symbol {symbol} with parallel analysis types")
            state = self._analyze_all_parallel(symbol, research_data[symbol], query_type, state)
        else:
            # Multiple symbols: parallelize symbols AND analysis types (two-level parallelization)
            logger.info(f"Analyst Agent: Analyzing {len(valid_symbols)} symbols with symbol-level parallelization")
            max_workers = ParallelizationStrategy.get_max_workers_analysis(valid_symbols)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._analyze_all_parallel, symbol, research_data[symbol], query_type, state): symbol
                    for symbol in valid_symbols
                }
                
                results = []
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        result_state = future.result()
                        results.append(result_state)
                        symbol_status[symbol] = "success"
                        logger.info(f"Analyst Agent: Completed analysis for {symbol}")
                    except Exception as e:
                        logger.error(f"Analyst Agent: Error analyzing {symbol}: {e}")
                        symbol_status[symbol] = "failed"
                        symbol_errors[symbol] = str(e)
                        analysis_results[symbol] = {"error": str(e)}
                        # Continue with other symbols
                        continue
                
                # Merge parallel contexts
                if results:
                    state = StateManager.merge_parallel_contexts(results)
        
        # Update state
        state = self.write_context(state, "analysis_results", analysis_results)
        state = self.write_context(state, "analysis_reasoning", analysis_reasoning)
        state = self.write_context(state, "symbol_status", symbol_status)
        state = self.write_context(state, "symbol_errors", symbol_errors)
        
        # Set partial_success if any failures occurred
        if any(status == "failed" for status in symbol_status.values()):
            state = self.write_context(state, "partial_success", True)
        
        return state
    
    def _analyze_all_parallel(self, symbol: str, symbol_data: Dict[str, Any],
                              query_type: str, state: AgentState) -> AgentState:
        """
        Run all analysis types in parallel for a single symbol
        
        Args:
            symbol: Stock symbol
            symbol_data: Symbol research data
            query_type: Query type
            state: Current AgentState
        
        Returns:
            Updated AgentState with analysis results
        """
        logger.debug(f"Analyst Agent: Running all analysis types in parallel for {symbol}")
        
        # Report parallel execution start
        state = self.report_progress_parallel(
            state,
            event_type="task_progress",
            message=f"Analyzing {symbol} (parallel)",
            symbol=symbol
        )
        
        analysis_results = self.read_context(state, "analysis_results", {})
        analysis_reasoning = self.read_context(state, "analysis_reasoning", {})
        sentiment_analysis = self.read_context(state, "sentiment_analysis", {})
        trend_analysis = self.read_context(state, "trend_analysis", {})
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            # Submit all analysis tasks
            futures[executor.submit(self._query_historical_patterns, symbol, symbol_data)] = "historical_patterns"
            futures[executor.submit(self._analyze_financials, symbol, symbol_data)] = "financials"
            
            if symbol_data.get("news"):
                futures[executor.submit(self._analyze_sentiment, symbol, symbol_data["news"], state)] = "sentiment"
            
            if symbol_data.get("historical") and query_type in ["trend", "comparison"]:
                futures[executor.submit(self._analyze_trends, symbol, symbol_data["historical"])] = "trends"
            
            # Collect results as they complete
            for future in as_completed(futures):
                analysis_type = futures[future]
                try:
                    result = future.result()
                    results[analysis_type] = result
                    logger.debug(f"Analyst Agent: Completed {analysis_type} for {symbol}")
                except Exception as e:
                    logger.warning(f"Analyst Agent: Error in {analysis_type} for {symbol}: {e}")
                    results[analysis_type] = None
        
        # Compile analysis results
        financial_analysis = results.get("financials", {})
        sentiment_analysis_result = results.get("sentiment")
        trend_analysis_result = results.get("trends")
        historical_context = results.get("historical_patterns", [])
        
        # Store sentiment and trend in state
        if sentiment_analysis_result:
            sentiment_analysis[symbol] = sentiment_analysis_result
            state = self.write_context(state, "sentiment_analysis", sentiment_analysis)
        
        if trend_analysis_result:
            trend_analysis[symbol] = trend_analysis_result
            state = self.write_context(state, "trend_analysis", trend_analysis)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            symbol, financial_analysis, sentiment_analysis_result, trend_analysis_result
        )
        
        # Compile analysis
        analysis = {
            "financial": financial_analysis,
            "sentiment": sentiment_analysis_result,
            "trend": trend_analysis_result,
            "historical_context": historical_context,
            "recommendation": recommendation
        }
        
        analysis_results[symbol] = analysis
        
        # Generate reasoning chain
        reasoning = self._generate_reasoning(symbol, analysis)
        analysis_reasoning[symbol] = reasoning
        
        # Update state
        state = self.write_context(state, "analysis_results", analysis_results)
        state = self.write_context(state, "analysis_reasoning", analysis_reasoning)
        
        return state
    
    def _query_historical_patterns(self, symbol: str, symbol_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query vector DB for similar historical patterns
        
        Args:
            symbol: Stock symbol
            symbol_data: Current symbol data
        
        Returns:
            List of similar historical patterns
        """
        try:
            # Create query from current data
            price = symbol_data.get("price", {})
            query_text = f"Stock {symbol} price {price.get('current_price', 'unknown')} market cap {price.get('market_cap', 'unknown')}"
            
            # Generate embedding
            query_embedding = self.embedding_pipeline.generate_embedding(query_text)
            
            # Search for similar patterns
            similar_docs = self.vector_db.search_similar(
                collection_name="company_analysis",
                query_embedding=query_embedding,
                n_results=5,
                where={"symbol": {"$ne": symbol}}  # Exclude current symbol
            )
            
            return similar_docs
        
        except Exception as e:
            logger.warning(f"Analyst Agent: Error querying historical patterns: {e}")
            return []
    
    def _analyze_financials(self, symbol: str, symbol_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze financial data
        
        Args:
            symbol: Stock symbol
            symbol_data: Symbol data
        
        Returns:
            Financial analysis results
        """
        price_data = symbol_data.get("price", {})
        financials = symbol_data.get("financials", {})
        
        analysis = {
            "current_price": price_data.get("current_price"),
            "market_cap": price_data.get("market_cap"),
            "pe_ratio": price_data.get("pe_ratio"),
            "volume": price_data.get("volume"),
            "price_change": price_data.get("change"),
            "price_change_percent": price_data.get("change_percent"),
        }
        
        # Calculate ratios if financials available
        if financials:
            income_statement = financials.get("income_statement", {})
            balance_sheet = financials.get("balance_sheet", {})
            
            # Basic ratio calculations (simplified)
            analysis["has_financials"] = True
            analysis["financials_available"] = {
                "income_statement": bool(income_statement),
                "balance_sheet": bool(balance_sheet),
                "cash_flow": bool(financials.get("cash_flow"))
            }
        
        return analysis
    
    def _analyze_sentiment(self, symbol: str, news_data: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """
        Analyze sentiment from news
        
        Args:
            symbol: Stock symbol
            news_data: News data
        
        Returns:
            Sentiment analysis results
        """
        articles = news_data.get("articles", [])
        
        if not articles:
            return {"sentiment": "neutral", "score": 0.0, "article_count": 0}
        
        # Use LLM to analyze sentiment
        article_texts = [f"{a.get('title', '')} {a.get('text', '')}" for a in articles[:5]]
        combined_text = "\n\n".join(article_texts)
        
        prompt = f"""Analyze the sentiment of the following news articles about {symbol}.
        
Articles:
{combined_text}

Provide a sentiment analysis with:
1. Overall sentiment (positive, negative, or neutral)
2. Sentiment score (-1 to 1, where -1 is very negative, 0 is neutral, 1 is very positive)
3. Key factors influencing the sentiment
4. Summary of main concerns or positive points

Format your response as JSON with keys: sentiment, score, factors, summary."""
        
        try:
            messages = [
                {"role": "system", "content": "You are a financial sentiment analyst. Analyze news sentiment and provide structured analysis."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.call_llm(messages, state=state)
            content = response["content"]
            
            # Parse JSON response (simplified - in production use proper JSON parsing)
            try:
                sentiment_data = json.loads(content)
            except:
                # Fallback parsing
                sentiment_data = {
                    "sentiment": "neutral",
                    "score": 0.0,
                    "factors": [],
                    "summary": content[:200]
                }
            
            sentiment_data["article_count"] = len(articles)
            return sentiment_data
        
        except Exception as e:
            logger.warning(f"Analyst Agent: Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "score": 0.0, "article_count": len(articles), "error": str(e)}
    
    def _analyze_trends(self, symbol: str, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze price trends
        
        Args:
            symbol: Stock symbol
            historical_data: Historical price data
        
        Returns:
            Trend analysis results
        """
        data_points = historical_data.get("data", [])
        
        if not data_points:
            return {"trend": "insufficient_data"}
        
        # Basic trend analysis (simplified)
        # In production, this would use more sophisticated analysis
        trend_analysis = {
            "data_points": len(data_points),
            "period": historical_data.get("period", "unknown"),
            "trend": "analyzing"  # Would calculate actual trend
        }
        
        return trend_analysis
    
    def _generate_recommendation(self, symbol: str, financial: Dict[str, Any],
                                sentiment: Dict[str, Any] = None,
                                trend: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate investment recommendation
        
        Args:
            symbol: Stock symbol
            financial: Financial analysis
            sentiment: Sentiment analysis
            trend: Trend analysis
        
        Returns:
            Recommendation dictionary
        """
        # Simple recommendation logic (in production, use LLM for sophisticated reasoning)
        recommendation = {
            "symbol": symbol,
            "action": "hold",  # buy, sell, hold
            "confidence": "medium",
            "reasoning": "Based on financial analysis"
        }
        
        if sentiment:
            sentiment_score = sentiment.get("score", 0)
            if sentiment_score > 0.3:
                recommendation["action"] = "buy"
            elif sentiment_score < -0.3:
                recommendation["action"] = "sell"
        
        return recommendation
    
    def _generate_reasoning(self, symbol: str, analysis: Dict[str, Any]) -> str:
        """
        Generate reasoning chain for analysis
        
        Args:
            symbol: Stock symbol
            analysis: Analysis results
        
        Returns:
            Reasoning text
        """
        financial = analysis.get("financial", {})
        sentiment = analysis.get("sentiment", {})
        recommendation = analysis.get("recommendation", {})
        
        reasoning = f"Analysis for {symbol}:\n\n"
        reasoning += f"Financial metrics: Price {financial.get('current_price')}, "
        reasoning += f"Market Cap {financial.get('market_cap')}\n\n"
        
        if sentiment:
            reasoning += f"Sentiment: {sentiment.get('sentiment', 'neutral')} "
            reasoning += f"(score: {sentiment.get('score', 0)})\n\n"
        
        reasoning += f"Recommendation: {recommendation.get('action', 'hold')} "
        reasoning += f"({recommendation.get('confidence', 'medium')} confidence)\n\n"
        reasoning += f"Reasoning: {recommendation.get('reasoning', 'Based on analysis')}"
        
        return reasoning


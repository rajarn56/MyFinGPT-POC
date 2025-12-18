"""Comparison Agent - Compares symbols against benchmarks, history, or each other"""

from typing import Dict, Any, List
from loguru import logger
from .base_agent import BaseAgent
from ..orchestrator.state import AgentState
from ..vector_db.chroma_client import ChromaClient
from ..vector_db.embeddings import EmbeddingPipeline


class ComparisonAgent(BaseAgent):
    """Comparison Agent - Compares symbols against benchmarks, history, or each other"""
    
    def __init__(self, provider: str = None):
        """
        Initialize Comparison Agent
        
        Args:
            provider: LLM provider name
        """
        super().__init__(name="Comparison Agent", provider=provider)
        self.vector_db = ChromaClient()
        self.embedding_pipeline = EmbeddingPipeline()
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute comparison agent logic
        
        Args:
            state: Current AgentState
        
        Returns:
            Updated AgentState with comparison_data
        """
        # Validate required context
        if not self.validate_required_context(state, ["research_data", "analysis_results"]):
            logger.error("Comparison Agent: Missing required context")
            return state
        
        symbols = self.read_context(state, "symbols", [])
        analysis_results = self.read_context(state, "analysis_results", {})
        research_data = self.read_context(state, "research_data", {})
        
        logger.info(f"Comparison Agent: Comparing {len(symbols)} symbol(s)")
        
        if len(symbols) == 1:
            # Single stock: compare against benchmarks/history
            symbol = symbols[0]
            logger.info(f"Comparison Agent: Comparing {symbol} against benchmarks and historical patterns")
            comparison_data = self._compare_against_benchmarks(symbol, analysis_results, research_data, state)
        else:
            # Multiple stocks: side-by-side comparison
            logger.info(f"Comparison Agent: Comparing {len(symbols)} symbols side-by-side")
            comparison_data = self._compare_symbols_side_by_side(symbols, analysis_results, research_data, state)
        
        state = self.write_context(state, "comparison_data", comparison_data)
        
        logger.info(f"Comparison Agent: Comparison completed")
        return state
    
    def _compare_against_benchmarks(self, symbol: str, analysis_results: Dict[str, Any],
                                   research_data: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """
        Compare single stock against benchmarks, historical patterns, sector averages
        
        Args:
            symbol: Stock symbol
            analysis_results: Analysis results
            research_data: Research data
            state: Current AgentState
        
        Returns:
            Comparison data dictionary
        """
        logger.debug(f"Comparison Agent: Comparing {symbol} against benchmarks")
        
        symbol_analysis = analysis_results.get(symbol, {})
        symbol_research = research_data.get(symbol, {})
        
        # Extract metrics
        price_data = symbol_research.get("price", {})
        company_info = symbol_research.get("company", {})
        financial_analysis = symbol_analysis.get("financial", {})
        
        # Query vector DB for historical patterns
        historical_patterns = self._query_historical_comparisons(symbol, price_data, company_info)
        
        # Prepare comparison context for LLM
        comparison_context = {
            "symbol": symbol,
            "current_price": price_data.get("current_price"),
            "market_cap": price_data.get("market_cap"),
            "pe_ratio": price_data.get("pe_ratio"),
            "sector": company_info.get("sector"),
            "industry": company_info.get("industry"),
            "financial_metrics": financial_analysis,
            "historical_patterns": historical_patterns
        }
        
        # Generate comparison insights using LLM
        comparison_insights = self._generate_benchmark_comparison(comparison_context, state)
        
        comparison_data = {
            "symbol": symbol,
            "comparison_type": "benchmark",
            "metrics": comparison_context,
            "historical_patterns": historical_patterns,
            "insights": comparison_insights
        }
        
        return comparison_data
    
    def _compare_symbols_side_by_side(self, symbols: List[str], analysis_results: Dict[str, Any],
                                      research_data: Dict[str, Any], state: AgentState) -> Dict[str, Any]:
        """
        Compare multiple symbols side-by-side
        
        Args:
            symbols: List of stock symbols
            analysis_results: Analysis results
            research_data: Research data
            state: Current AgentState
        
        Returns:
            Comparison data dictionary
        """
        logger.debug(f"Comparison Agent: Comparing {len(symbols)} symbols side-by-side")
        
        # Extract comparison metrics for each symbol
        comparison_metrics = {}
        for symbol in symbols:
            symbol_analysis = analysis_results.get(symbol, {})
            symbol_research = research_data.get(symbol, {})
            
            price_data = symbol_research.get("price", {})
            company_info = symbol_research.get("company", {})
            financial_analysis = symbol_analysis.get("financial", {})
            sentiment_analysis = symbol_analysis.get("sentiment", {})
            recommendation = symbol_analysis.get("recommendation", {})
            
            comparison_metrics[symbol] = {
                "current_price": price_data.get("current_price"),
                "market_cap": price_data.get("market_cap"),
                "pe_ratio": price_data.get("pe_ratio"),
                "volume": price_data.get("volume"),
                "sector": company_info.get("sector"),
                "industry": company_info.get("industry"),
                "financial_metrics": financial_analysis,
                "sentiment": sentiment_analysis.get("sentiment") if sentiment_analysis else None,
                "sentiment_score": sentiment_analysis.get("score") if sentiment_analysis else None,
                "recommendation": recommendation.get("action") if recommendation else None
            }
        
        # Generate side-by-side comparison table
        comparison_table = self._generate_comparison_table(comparison_metrics)
        
        # Generate comparison insights using LLM
        comparison_insights = self._generate_side_by_side_insights(symbols, comparison_metrics, state)
        
        comparison_data = {
            "symbols": symbols,
            "comparison_type": "side_by_side",
            "metrics": comparison_metrics,
            "comparison_table": comparison_table,
            "insights": comparison_insights
        }
        
        return comparison_data
    
    def _query_historical_comparisons(self, symbol: str, price_data: Dict[str, Any],
                                     company_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query vector DB for similar historical patterns
        
        Args:
            symbol: Stock symbol
            price_data: Price data
            company_info: Company info
        
        Returns:
            List of similar historical patterns
        """
        try:
            # Create query from current metrics
            sector = company_info.get("sector", "")
            pe_ratio = price_data.get("pe_ratio", 0)
            market_cap = price_data.get("market_cap", 0)
            
            query_text = f"Stock in {sector} sector with P/E ratio around {pe_ratio} and market cap around {market_cap}"
            
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
            logger.warning(f"Comparison Agent: Error querying historical comparisons: {e}")
            return []
    
    def _generate_benchmark_comparison(self, comparison_context: Dict[str, Any],
                                      state: AgentState) -> str:
        """
        Generate benchmark comparison insights using LLM
        
        Args:
            comparison_context: Comparison context data
            state: Current AgentState
        
        Returns:
            Comparison insights text
        """
        prompt = f"""Analyze and compare the following stock against benchmarks and historical patterns:

Symbol: {comparison_context['symbol']}
Current Price: ${comparison_context.get('current_price', 'N/A')}
Market Cap: ${comparison_context.get('market_cap', 'N/A')}
P/E Ratio: {comparison_context.get('pe_ratio', 'N/A')}
Sector: {comparison_context.get('sector', 'N/A')}
Industry: {comparison_context.get('industry', 'N/A')}

Financial Metrics:
{comparison_context.get('financial_metrics', {})}

Historical Patterns Found: {len(comparison_context.get('historical_patterns', []))} similar patterns

Provide a comprehensive comparison analysis including:
1. How this stock compares to sector/industry averages
2. Historical patterns and what they suggest
3. Relative valuation assessment
4. Key strengths and weaknesses compared to peers
5. Investment implications

Format your response as a clear, structured analysis."""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a financial analyst specializing in comparative analysis. Provide detailed, actionable insights comparing stocks against benchmarks and historical patterns."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.call_llm(messages, state=state)
            return response["content"]
        
        except Exception as e:
            logger.error(f"Comparison Agent: Error generating benchmark comparison: {e}")
            return f"Error generating comparison insights: {str(e)}"
    
    def _generate_comparison_table(self, comparison_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate side-by-side comparison table
        
        Args:
            comparison_metrics: Dictionary mapping symbols to their metrics
        
        Returns:
            Comparison table dictionary
        """
        table = {
            "headers": ["Symbol", "Price", "Market Cap", "P/E Ratio", "Sector", "Sentiment", "Recommendation"],
            "rows": []
        }
        
        for symbol, metrics in comparison_metrics.items():
            row = [
                symbol,
                f"${metrics.get('current_price', 'N/A')}",
                f"${metrics.get('market_cap', 'N/A')}",
                metrics.get('pe_ratio', 'N/A'),
                metrics.get('sector', 'N/A'),
                metrics.get('sentiment', 'N/A'),
                metrics.get('recommendation', 'N/A')
            ]
            table["rows"].append(row)
        
        return table
    
    def _generate_side_by_side_insights(self, symbols: List[str], comparison_metrics: Dict[str, Dict[str, Any]],
                                       state: AgentState) -> str:
        """
        Generate side-by-side comparison insights using LLM
        
        Args:
            symbols: List of symbols being compared
            comparison_metrics: Comparison metrics for each symbol
            state: Current AgentState
        
        Returns:
            Comparison insights text
        """
        # Prepare comparison summary
        comparison_summary = "\n\n".join([
            f"{symbol}:\n"
            f"  Price: ${metrics.get('current_price', 'N/A')}\n"
            f"  Market Cap: ${metrics.get('market_cap', 'N/A')}\n"
            f"  P/E Ratio: {metrics.get('pe_ratio', 'N/A')}\n"
            f"  Sector: {metrics.get('sector', 'N/A')}\n"
            f"  Sentiment: {metrics.get('sentiment', 'N/A')} (score: {metrics.get('sentiment_score', 'N/A')})\n"
            f"  Recommendation: {metrics.get('recommendation', 'N/A')}"
            for symbol, metrics in comparison_metrics.items()
        ])
        
        prompt = f"""Compare the following stocks side-by-side and provide comprehensive analysis:

{comparison_summary}

Provide a detailed comparison analysis including:
1. Relative valuation comparison
2. Financial strength comparison
3. Market sentiment comparison
4. Sector/industry positioning
5. Risk assessment for each
6. Investment recommendation ranking
7. Key differentiators

Format your response as a clear, structured comparison analysis."""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a financial analyst specializing in multi-stock comparison analysis. Provide detailed, actionable insights comparing multiple stocks side-by-side."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.call_llm(messages, state=state)
            return response["content"]
        
        except Exception as e:
            logger.error(f"Comparison Agent: Error generating side-by-side insights: {e}")
            return f"Error generating comparison insights: {str(e)}"


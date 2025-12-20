"""Reporting Agent - Generates comprehensive reports"""

from typing import Dict, Any, List
from loguru import logger
from .base_agent import BaseAgent
from ..orchestrator.state import AgentState
from ..vector_db.chroma_client import ChromaClient
from ..utils.prompt_builder import prompt_builder


class ReportingAgent(BaseAgent):
    """Reporting Agent - Synthesizes findings into comprehensive reports"""
    
    def __init__(self, provider: str = None):
        """
        Initialize Reporting Agent
        
        Args:
            provider: LLM provider name
        """
        super().__init__(name="Reporting Agent", provider=provider)
        self.vector_db = ChromaClient()
    
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute reporting agent logic
        
        Args:
            state: Current AgentState
        
        Returns:
            Updated AgentState with final_report
        """
        # Validate required context
        if not self.validate_required_context(state, ["research_data", "analysis_results"]):
            logger.error("Reporting Agent: Missing required context")
            return state
        
        query = self.read_context(state, "query", "")
        symbols = self.read_context(state, "symbols", [])
        query_type = self.read_context(state, "query_type", "single_stock")
        research_data = self.read_context(state, "research_data", {})
        analysis_results = self.read_context(state, "analysis_results", {})
        citations = self.read_context(state, "citations", [])
        
        logger.info(f"Reporting Agent: Generating report for {len(symbols)} symbol(s) | "
                   f"Query type: {query_type} | "
                   f"Citations: {len(citations)}")
        
        # Generate report using LLM
        logger.debug("Reporting Agent: Preparing context summary for report generation")
        state = self.start_task(state, "Prepare context summary")
        context_summary = self._prepare_context_summary(symbols, research_data, analysis_results, citations)
        state = self.complete_task(state, "Prepare context summary")
        
        state = self.start_task(state, "Generate report with LLM")
        report = self._generate_report(
            query=query,
            symbols=symbols,
            query_type=query_type,
            research_data=research_data,
            analysis_results=analysis_results,
            citations=citations,
            state=state
        )
        state = self.complete_task(state, "Generate report with LLM")
        logger.debug(f"Reporting Agent: Report generated | Length: {len(report)} chars")
        
        # Generate visualizations data
        logger.debug("Reporting Agent: Preparing visualization data")
        state = self.start_task(state, "Prepare visualizations")
        visualizations = self._prepare_visualizations(symbols, research_data, analysis_results)
        viz_count = sum(len(v) for v in visualizations.values() if isinstance(v, dict))
        state = self.complete_task(state, "Prepare visualizations")
        logger.debug(f"Reporting Agent: Visualizations prepared | Data points: {viz_count}")
        
        # Update state
        state = self.write_context(state, "final_report", report)
        state = self.write_context(state, "visualizations", visualizations)
        
        # Store report in vector DB for future reference
        logger.debug("Reporting Agent: Storing report in vector DB")
        state = self.start_task(state, "Store report in vector DB")
        self._store_report_in_vector_db(symbols, report, query_type)
        state = self.complete_task(state, "Store report in vector DB")
        logger.debug("Reporting Agent: Report stored in vector DB")
        
        logger.info(f"Reporting Agent: Report generation completed | "
                   f"Report length: {len(report)} chars | "
                   f"Visualizations: {len(visualizations)} types")
        
        return state
    
    def _generate_report(self, query: str, symbols: List[str], query_type: str,
                        research_data: Dict[str, Any], analysis_results: Dict[str, Any],
                        citations: List[Dict[str, Any]], state: AgentState) -> str:
        """
        Generate comprehensive report using LLM
        
        Args:
            query: Original user query
            symbols: List of symbols analyzed
            query_type: Type of query
            research_data: Research data
            analysis_results: Analysis results
            citations: List of citations
        
        Returns:
            Generated report text
        """
        # Prepare context for LLM
        context_summary = self._prepare_context_summary(
            symbols, research_data, analysis_results, citations
        )
        
        prompt = f"""Generate a comprehensive financial analysis report based on the following data.

User Query: {query}
Query Type: {query_type}
Symbols Analyzed: {', '.join(symbols)}

Research Data Summary:
{context_summary['research_summary']}

Analysis Results Summary:
{context_summary['analysis_summary']}

Citations:
{context_summary['citations_summary']}

Please generate a well-structured report with the following sections:
1. Executive Summary
2. Company Overview (for each symbol)
3. Financial Analysis
4. Market Sentiment Analysis
5. Trends and Patterns
6. Investment Recommendation
7. Risk Assessment
8. Sources and Citations

Make the report professional, clear, and actionable. Include specific numbers and data points with proper citations."""

        try:
            # Build dynamic system prompt based on enabled integrations
            base_system_prompt = """You are a professional financial analyst specializing in stock market analysis and investment research.

Your role is to generate comprehensive financial analysis reports based on research data and analysis results.

REPORT REQUIREMENTS:
1. Structure: Reports must include these sections in order:
   - Executive Summary (2-3 paragraphs)
   - Company Overview (for each symbol analyzed)
   - Financial Analysis (key metrics, ratios, financial health)
   - Market Sentiment Analysis (news sentiment, market perception)
   - Trends and Patterns (price trends, historical patterns)
   - Investment Recommendation (buy/hold/sell with reasoning)
   - Risk Assessment (key risks and mitigation)
   - Sources and Citations (all data sources properly cited)

2. Citations: Every data point, metric, or statistic must include a citation in format: [Source: Data Point]. 
   Example: "AAPL's current price is $150.25 [Source: Yahoo Finance: stock_price]"

3. Domain Scope: Focus exclusively on financial markets, stocks, companies, and investment analysis. 
   Do not include non-financial topics.

4. Actionability: Provide specific, actionable insights with clear reasoning. Include numerical data 
   and specific recommendations, not vague generalities.

5. Professional Tone: Use clear, professional language suitable for investment professionals and 
   informed investors. Avoid jargon without explanation.

6. Data Accuracy: Only use data provided in the context. If data is missing, explicitly state that 
   it was unavailable rather than making assumptions."""
            
            # Enhance with integration-specific information
            dynamic_system_prompt = prompt_builder.build_reporting_agent_prompt(base_system_prompt)
            
            messages = [
                {
                    "role": "system",
                    "content": dynamic_system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            response = self.call_llm(messages, state=state)
            report = response["content"]
            
            return report
        
        except Exception as e:
            logger.error(f"Reporting Agent: Error generating report: {e}")
            return f"Error generating report: {str(e)}"
    
    def _prepare_context_summary(self, symbols: List[str], research_data: Dict[str, Any],
                                 analysis_results: Dict[str, Any],
                                 citations: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Prepare context summary for report generation
        
        Args:
            symbols: List of symbols
            research_data: Research data
            analysis_results: Analysis results
            citations: Citations
        
        Returns:
            Dictionary with summary sections
        """
        research_summary = ""
        for symbol in symbols:
            if symbol in research_data:
                data = research_data[symbol]
                price = data.get("price", {})
                company = data.get("company", {})
                
                research_summary += f"\n{symbol}:\n"
                research_summary += f"  Current Price: ${price.get('current_price', 'N/A')}\n"
                research_summary += f"  Market Cap: ${price.get('market_cap', 'N/A')}\n"
                research_summary += f"  Company: {company.get('name', 'N/A')}\n"
                research_summary += f"  Sector: {company.get('sector', 'N/A')}\n"
        
        analysis_summary = ""
        for symbol in symbols:
            if symbol in analysis_results:
                analysis = analysis_results[symbol]
                financial = analysis.get("financial", {})
                sentiment = analysis.get("sentiment", {})
                recommendation = analysis.get("recommendation", {})
                
                analysis_summary += f"\n{symbol}:\n"
                analysis_summary += f"  Recommendation: {recommendation.get('action', 'N/A')}\n"
                if sentiment:
                    analysis_summary += f"  Sentiment: {sentiment.get('sentiment', 'N/A')} (score: {sentiment.get('score', 0)})\n"
        
        citations_summary = "\n".join([
            f"- {c.get('source', 'Unknown')}: {c.get('data_point', 'N/A')} ({c.get('date', 'N/A')})"
            for c in citations[:10]  # Limit to 10 citations in summary
        ])
        
        return {
            "research_summary": research_summary,
            "analysis_summary": analysis_summary,
            "citations_summary": citations_summary
        }
    
    def _prepare_visualizations(self, symbols: List[str], research_data: Dict[str, Any],
                               analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare visualization data
        
        Args:
            symbols: List of symbols
            research_data: Research data
            analysis_results: Analysis results
        
        Returns:
            Visualization data dictionary
        """
        visualizations = {
            "price_trends": {},
            "comparison_charts": {},
            "sentiment_charts": {}
        }
        
        for symbol in symbols:
            if symbol in research_data:
                data = research_data[symbol]
                
                # Price trend data
                if data.get("historical"):
                    historical = data["historical"]
                    visualizations["price_trends"][symbol] = {
                        "dates": historical.get("dates", []),
                        "prices": [d.get("Close") for d in historical.get("data", [])]
                    }
                
                # Price data for comparison
                price = data.get("price", {})
                visualizations["comparison_charts"][symbol] = {
                    "current_price": price.get("current_price"),
                    "market_cap": price.get("market_cap"),
                    "volume": price.get("volume")
                }
            
            # Sentiment data
            if symbol in analysis_results:
                analysis = analysis_results[symbol]
                sentiment = analysis.get("sentiment")
                if sentiment:
                    visualizations["sentiment_charts"][symbol] = {
                        "sentiment": sentiment.get("sentiment"),
                        "score": sentiment.get("score", 0)
                    }
        
        return visualizations
    
    def _store_report_in_vector_db(self, symbols: List[str], report: str, query_type: str):
        """
        Store generated report in vector DB for future reference
        
        Args:
            symbols: List of symbols
            report: Generated report
            query_type: Query type
        """
        try:
            from ..vector_db.embeddings import EmbeddingPipeline
            embedding_pipeline = EmbeddingPipeline()
            
            # Generate embedding
            embedding = embedding_pipeline.generate_embedding(report)
            
            # Prepare metadata
            metadata = {
                "symbols": ",".join(symbols),
                "query_type": query_type,
                "source": "reporting_agent",
                "report_length": len(report)
            }
            
            # Store in vector DB
            self.vector_db.add_document(
                collection_name="company_analysis",
                document=report,
                metadata=metadata,
                embedding=embedding
            )
        
        except Exception as e:
            logger.warning(f"Reporting Agent: Error storing report in vector DB: {e}")


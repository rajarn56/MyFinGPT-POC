"""Dynamic prompt generation utility for MyFinGPT agents"""

from typing import Dict, List, Optional
from loguru import logger
from .integration_config import integration_config


class PromptBuilder:
    """Builds dynamic prompts based on enabled integrations"""
    
    # Integration display names
    INTEGRATION_NAMES = {
        "yahoo_finance": "Yahoo Finance",
        "alpha_vantage": "Alpha Vantage",
        "fmp": "Financial Modeling Prep (FMP)"
    }
    
    # Data type descriptions
    DATA_TYPE_DESCRIPTIONS = {
        "stock_price": "real-time stock prices and market data",
        "company_info": "company profiles and business information",
        "financial_statements": "financial statements (income statement, balance sheet, cash flow)",
        "news": "company news and press releases",
        "historical_data": "historical price data for trend analysis",
        "technical_indicators": "technical analysis indicators (SMA, RSI, MACD, etc.)"
    }
    
    @staticmethod
    def get_enabled_integrations_list() -> List[str]:
        """
        Get list of enabled integration display names
        
        Returns:
            List of enabled integration names (e.g., ["Yahoo Finance", "Alpha Vantage"])
        """
        enabled = integration_config.get_enabled_integrations()
        return [PromptBuilder.INTEGRATION_NAMES.get(name, name) for name in enabled]
    
    @staticmethod
    def get_enabled_integrations_text() -> str:
        """
        Get formatted text listing enabled integrations
        
        Returns:
            Formatted string (e.g., "Yahoo Finance, Alpha Vantage, and Financial Modeling Prep")
        """
        enabled_names = PromptBuilder.get_enabled_integrations_list()
        
        if not enabled_names:
            return "No data sources available"
        elif len(enabled_names) == 1:
            return enabled_names[0]
        elif len(enabled_names) == 2:
            return f"{enabled_names[0]} and {enabled_names[1]}"
        else:
            return f"{', '.join(enabled_names[:-1])}, and {enabled_names[-1]}"
    
    @staticmethod
    def get_available_data_sources_text() -> str:
        """
        Get formatted text describing available data sources based on enabled integrations
        
        Returns:
            Formatted string describing what data is available
        """
        enabled = integration_config.get_enabled_integrations()
        
        if not enabled:
            return "No data sources are currently enabled."
        
        # Build description of available data types
        available_data_types = []
        
        # Check each data type
        for data_type, description in PromptBuilder.DATA_TYPE_DESCRIPTIONS.items():
            sources = integration_config.get_enabled_sources_for_data_type(data_type)
            if sources:
                available_data_types.append(description)
        
        if not available_data_types:
            return "No data types are available with current integration configuration."
        
        # Format as bullet list
        data_sources_text = "Available data sources:\n"
        for i, data_type_desc in enumerate(available_data_types, 1):
            data_sources_text += f"- {data_type_desc}\n"
        
        return data_sources_text.strip()
    
    @staticmethod
    def build_reporting_agent_prompt(base_prompt: str) -> str:
        """
        Build dynamic prompt for Reporting Agent based on enabled integrations
        
        Args:
            base_prompt: Base prompt template
        
        Returns:
            Enhanced prompt with integration-specific information
        """
        enabled_integrations = PromptBuilder.get_enabled_integrations_text()
        available_data = PromptBuilder.get_available_data_sources_text()
        
        # Add integration context to prompt
        integration_context = f"""
AVAILABLE DATA SOURCES:
The following data sources are currently enabled: {enabled_integrations}.

{available_data}

IMPORTANT:
- Only use data from the enabled sources listed above
- If a data source is disabled, do not mention it in your report
- Cite sources appropriately using the format: [Source: Data Point]
- If certain data is unavailable due to disabled integrations, note this in your report
"""
        
        return base_prompt + integration_context
    
    @staticmethod
    def build_analyst_agent_prompt(base_prompt: str) -> str:
        """
        Build dynamic prompt for Analyst Agent based on enabled integrations
        
        Args:
            base_prompt: Base prompt template
        
        Returns:
            Enhanced prompt with integration-specific information
        """
        enabled_integrations = PromptBuilder.get_enabled_integrations_text()
        
        # Check which data types are available for sentiment analysis
        news_sources = integration_config.get_enabled_sources_for_data_type("news")
        available_news_sources = [PromptBuilder.INTEGRATION_NAMES.get(s, s) for s in news_sources]
        
        integration_context = f"""
AVAILABLE DATA SOURCES:
The following data sources are currently enabled: {enabled_integrations}.

For sentiment analysis, news data is available from: {', '.join(available_news_sources) if available_news_sources else 'No news sources available'}.

IMPORTANT:
- Only analyze news from enabled sources
- If news data is unavailable due to disabled integrations, note this in your analysis
- Base sentiment analysis only on available news sources
"""
        
        return base_prompt + integration_context
    
    @staticmethod
    def build_comparison_agent_prompt(base_prompt: str, comparison_type: str = "benchmark") -> str:
        """
        Build dynamic prompt for Comparison Agent based on enabled integrations
        
        Args:
            base_prompt: Base prompt template
            comparison_type: Type of comparison ("benchmark" or "side_by_side")
        
        Returns:
            Enhanced prompt with integration-specific information
        """
        enabled_integrations = PromptBuilder.get_enabled_integrations_text()
        available_data = PromptBuilder.get_available_data_sources_text()
        
        integration_context = f"""
AVAILABLE DATA SOURCES:
The following data sources are currently enabled: {enabled_integrations}.

{available_data}

IMPORTANT:
- Use only data from enabled sources for comparisons
- If certain metrics are unavailable due to disabled integrations, note this in your comparison
- When comparing stocks, use only data sources that are currently available
- Be explicit about which data sources were used for each comparison metric
"""
        
        return base_prompt + integration_context
    
    @staticmethod
    def get_data_source_availability_info() -> Dict[str, List[str]]:
        """
        Get information about which data types are available from which integrations
        
        Returns:
            Dictionary mapping data types to lists of available integration names
        """
        availability = {}
        
        for data_type in PromptBuilder.DATA_TYPE_DESCRIPTIONS.keys():
            sources = integration_config.get_enabled_sources_for_data_type(data_type)
            availability[data_type] = [
                PromptBuilder.INTEGRATION_NAMES.get(s, s) for s in sources
            ]
        
        return availability
    
    @staticmethod
    def format_data_source_info() -> str:
        """
        Format data source availability information for inclusion in prompts
        
        Returns:
            Formatted string describing data source availability
        """
        availability = PromptBuilder.get_data_source_availability_info()
        
        if not any(availability.values()):
            return "No data sources are currently enabled."
        
        info_text = "Data Source Availability:\n"
        for data_type, sources in availability.items():
            if sources:
                description = PromptBuilder.DATA_TYPE_DESCRIPTIONS.get(data_type, data_type)
                info_text += f"- {description}: Available from {', '.join(sources)}\n"
        
        return info_text.strip()


# Global instance
prompt_builder = PromptBuilder()


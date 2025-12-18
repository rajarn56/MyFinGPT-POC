"""Guardrails module for MyFinGPT

This module provides comprehensive validation and security guardrails to ensure:
- Queries are financial domain-related
- Inputs are sanitized and safe
- Stock symbols are valid
- Agent outputs are appropriate
- Data sources are trusted
- System behavior stays within intended scope
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger


class GuardrailsError(Exception):
    """Custom exception for guardrails violations"""
    pass


class Guardrails:
    """Comprehensive guardrails for MyFinGPT system"""
    
    # Financial domain keywords
    FINANCIAL_KEYWORDS = {
        "stock", "stocks", "equity", "equities", "share", "shares",
        "company", "companies", "corporation", "corp", "inc", "ltd",
        "price", "prices", "trading", "trade", "market", "markets",
        "financial", "finance", "revenue", "profit", "earnings", "eps",
        "pe", "p/e", "ratio", "ratios", "valuation", "value",
        "dividend", "dividends", "yield", "growth", "analysis", "analyze",
        "compare", "comparison", "trend", "trends", "sentiment", "news",
        "balance sheet", "income statement", "cash flow", "financials",
        "market cap", "market capitalization", "volume", "volatility",
        "beta", "alpha", "rsi", "macd", "technical", "fundamental",
        "investment", "invest", "portfolio", "asset", "assets", "liability",
        "recommendation", "recommend", "buy", "sell", "hold", "rating",
        "analyst", "analysts", "forecast", "outlook", "sector", "industry"
    }
    
    # Non-financial domain keywords that should be rejected
    NON_FINANCIAL_KEYWORDS = {
        "hack", "hacking", "exploit", "exploits", "vulnerability", "vulnerabilities",
        "password", "credentials", "login", "authentication", "authorization",
        "sql injection", "xss", "cross-site", "script", "malware", "virus",
        "crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain",  # Note: crypto is financial but out of scope
        "gambling", "casino", "betting", "lottery",
        "illegal", "unlawful", "criminal", "fraud", "scam", "ponzi",
        "personal information", "pii", "ssn", "social security",
        "medical", "health", "prescription", "drug", "pharmaceutical"  # Out of scope
    }
    
    # Valid stock symbol pattern (1-5 uppercase letters, optionally followed by exchange suffix)
    VALID_SYMBOL_PATTERN = re.compile(r'^[A-Z]{1,5}(?:\.[A-Z]{1,2})?$')
    
    # Common invalid symbols or words that look like symbols
    INVALID_SYMBOLS = {
        "THE", "AND", "OR", "FOR", "WITH", "FROM", "THIS", "THAT", "WHAT",
        "WHEN", "WHERE", "WHY", "HOW", "WHO", "WHICH", "WILL", "WOULD",
        "SHOULD", "COULD", "MIGHT", "MAY", "CAN", "MUST", "SHALL",
        "ABOUT", "ABOVE", "ACROSS", "AFTER", "AGAIN", "AGAINST", "ALONG",
        "AMONG", "AROUND", "BEFORE", "BEHIND", "BELOW", "BENEATH", "BESIDE",
        "BETWEEN", "BEYOND", "DURING", "EXCEPT", "INSIDE", "OUTSIDE",
        "THROUGH", "THROUGHOUT", "TOWARD", "UNDER", "UNDERNEATH", "UNTIL",
        "UPON", "WITHIN", "WITHOUT", "YOUR", "YOURS", "YOU", "YOURSELF"
    }
    
    # Maximum query length (characters)
    MAX_QUERY_LENGTH = 2000
    
    # Maximum number of symbols per query
    MAX_SYMBOLS_PER_QUERY = 20
    
    # Dangerous patterns for injection attacks
    DANGEROUS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick, onerror, etc.
        re.compile(r'data:text/html', re.IGNORECASE),
        re.compile(r'vbscript:', re.IGNORECASE),
        re.compile(r'<iframe[^>]*>', re.IGNORECASE),
        re.compile(r'<object[^>]*>', re.IGNORECASE),
        re.compile(r'<embed[^>]*>', re.IGNORECASE),
        re.compile(r'expression\s*\(', re.IGNORECASE),  # CSS expression
        re.compile(r'@import', re.IGNORECASE),
        re.compile(r'\\x[0-9a-f]{2}', re.IGNORECASE),  # Hex encoding
        re.compile(r'%[0-9a-f]{2}', re.IGNORECASE),  # URL encoding
        re.compile(r'union\s+select', re.IGNORECASE),  # SQL injection
        re.compile(r';\s*drop\s+table', re.IGNORECASE),  # SQL injection
        re.compile(r'exec\s*\(', re.IGNORECASE),  # Code execution
        re.compile(r'eval\s*\(', re.IGNORECASE),  # Code execution
        re.compile(r'system\s*\(', re.IGNORECASE),  # System calls
        re.compile(r'shell_exec', re.IGNORECASE),  # Shell execution
        re.compile(r'passthru', re.IGNORECASE),  # Shell execution
        re.compile(r'proc_open', re.IGNORECASE),  # Process execution
        re.compile(r'file_get_contents\s*\(', re.IGNORECASE),  # File access
        re.compile(r'file_put_contents\s*\(', re.IGNORECASE),  # File write
        re.compile(r'fopen\s*\(', re.IGNORECASE),  # File operations
        re.compile(r'fwrite\s*\(', re.IGNORECASE),  # File write
        re.compile(r'include\s*\(', re.IGNORECASE),  # File inclusion
        re.compile(r'require\s*\(', re.IGNORECASE),  # File inclusion
        re.compile(r'curl_exec', re.IGNORECASE),  # Network calls
        re.compile(r'fsockopen', re.IGNORECASE),  # Network calls
    ]
    
    # Allowed data sources
    ALLOWED_DATA_SOURCES = {
        "yahoo_finance", "alpha_vantage", "financial_modeling_prep", "fmp"
    }
    
    # Financial output keywords (to validate agent outputs)
    FINANCIAL_OUTPUT_KEYWORDS = {
        "stock", "price", "financial", "analysis", "company", "revenue",
        "earnings", "ratio", "valuation", "market", "investment", "recommendation"
    }
    
    @classmethod
    def validate_query(cls, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user query is financial domain-related and safe
        
        Args:
            query: User query string
        
        Returns:
            (is_valid, error_message)
        """
        if not query or not isinstance(query, str):
            return False, "Query must be a non-empty string"
        
        # Check query length
        if len(query) > cls.MAX_QUERY_LENGTH:
            return False, (
                f"Query exceeds maximum length of {cls.MAX_QUERY_LENGTH} characters "
                f"(current length: {len(query):,} characters). "
                "Please shorten your query or break it into multiple questions."
            )
        
        # Check for dangerous patterns (injection attacks)
        try:
            sanitized_query = cls.sanitize_input(query)
            if sanitized_query != query:
                return False, (
                    "Query contains potentially dangerous patterns that could pose a security risk. "
                    "Please rephrase your query using only plain text about financial topics."
                )
        except GuardrailsError as e:
            return False, (
                f"Query validation failed: {str(e)}. "
                "Please ensure your query contains only safe, plain text about financial topics."
            )
        
        # Check for non-financial domain keywords
        query_lower = query.lower()
        for keyword in cls.NON_FINANCIAL_KEYWORDS:
            if keyword in query_lower:
                return False, (
                    f"Query contains out-of-scope keyword: '{keyword}'. "
                    "This system focuses exclusively on financial market analysis (stocks, companies, investments). "
                    "Please rephrase your query to focus on financial topics. "
                    "Examples: 'Analyze AAPL stock', 'Compare tech companies', 'Show TSLA financials'"
                )
        
        # Check if query is financial-related
        has_financial_keyword = any(
            keyword in query_lower 
            for keyword in cls.FINANCIAL_KEYWORDS
        )
        
        # Also check for stock symbols (which indicate financial intent)
        symbols = cls.extract_symbols(query)
        has_symbols = len(symbols) > 0
        
        if not has_financial_keyword and not has_symbols:
            return False, (
                "Query does not appear to be financial domain-related. "
                "Please ask about stocks, companies, financial analysis, or market data. "
                "Examples: 'Analyze AAPL stock', 'Compare MSFT and GOOGL', "
                "'What is the current price of TSLA?', 'Show financials for NVDA'"
            )
        
        return True, None
    
    @classmethod
    def sanitize_input(cls, input_str: str) -> str:
        """
        Sanitize input string to prevent injection attacks
        
        Args:
            input_str: Input string to sanitize
        
        Returns:
            Sanitized string (or raises GuardrailsError if dangerous patterns found)
        """
        if not isinstance(input_str, str):
            raise GuardrailsError("Input must be a string")
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.search(input_str):
                raise GuardrailsError(f"Dangerous pattern detected in input: {pattern.pattern}")
        
        # Remove null bytes
        sanitized = input_str.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        sanitized = ''.join(
            char for char in sanitized 
            if ord(char) >= 32 or char in '\n\t'
        )
        
        return sanitized
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Validate stock symbol format and content
        
        Args:
            symbol: Stock symbol to validate
        
        Returns:
            (is_valid, error_message)
        """
        if not symbol or not isinstance(symbol, str):
            return False, "Symbol must be a non-empty string"
        
        symbol = symbol.strip().upper()
        
        # Check length
        if len(symbol) < 1 or len(symbol) > 7:  # Max 5 chars + 2 for exchange suffix
            return False, f"Symbol length invalid: {len(symbol)} (must be 1-7 characters)"
        
        # Check pattern
        if not cls.VALID_SYMBOL_PATTERN.match(symbol):
            return False, (
                f"Invalid stock symbol format: '{symbol}'. "
                "Stock symbols must be 1-5 uppercase letters (e.g., AAPL, MSFT, TSLA). "
                "Optionally followed by exchange suffix (e.g., BRK.A for Class A shares). "
                "Examples of valid symbols: AAPL, MSFT, GOOGL, BRK.A, TSLA"
            )
        
        # Check against invalid symbols
        base_symbol = symbol.split('.')[0]  # Remove exchange suffix if present
        if base_symbol in cls.INVALID_SYMBOLS:
            return False, (
                f"'{symbol}' appears to be a common word, not a stock symbol. "
                "Please use a valid stock ticker symbol (e.g., AAPL for Apple, MSFT for Microsoft). "
                "If you're unsure of a company's ticker symbol, try: 'What is the stock symbol for [Company Name]?'"
            )
        
        return True, None
    
    @classmethod
    def extract_symbols(cls, query: str) -> List[str]:
        """
        Extract and validate stock symbols from query
        
        Args:
            query: User query string
        
        Returns:
            List of valid stock symbols
        """
        if not query:
            return []
        
        # Pattern for stock symbols (1-5 uppercase letters)
        pattern = re.compile(r'\b([A-Z]{1,5})(?:\.[A-Z]{1,2})?\b')
        matches = pattern.findall(query)
        
        # Validate each match
        valid_symbols = []
        for match in matches:
            symbol = match.upper()
            is_valid, _ = cls.validate_symbol(symbol)
            if is_valid:
                valid_symbols.append(symbol)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_symbols = []
        for symbol in valid_symbols:
            if symbol not in seen:
                seen.add(symbol)
                unique_symbols.append(symbol)
        
        # Limit number of symbols
        return unique_symbols[:cls.MAX_SYMBOLS_PER_QUERY]
    
    @classmethod
    def validate_symbols(cls, symbols: List[str]) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate a list of stock symbols
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            (is_valid, error_message, valid_symbols)
        """
        if not symbols:
            return True, None, []
        
        if len(symbols) > cls.MAX_SYMBOLS_PER_QUERY:
            return False, f"Too many symbols: {len(symbols)} (maximum: {cls.MAX_SYMBOLS_PER_QUERY})", []
        
        valid_symbols = []
        invalid_symbols = []
        
        for symbol in symbols:
            is_valid, error = cls.validate_symbol(symbol)
            if is_valid:
                valid_symbols.append(symbol.upper())
            else:
                invalid_symbols.append(f"{symbol}: {error}")
        
        if invalid_symbols:
            return False, f"Invalid symbols: {', '.join(invalid_symbols)}", valid_symbols
        
        return True, None, valid_symbols
    
    @classmethod
    def validate_data_source(cls, source: str) -> Tuple[bool, Optional[str]]:
        """
        Validate data source is allowed
        
        Args:
            source: Data source name
        
        Returns:
            (is_valid, error_message)
        """
        if not source or not isinstance(source, str):
            return False, "Data source must be a non-empty string"
        
        source_lower = source.lower().replace(" ", "_")
        
        if source_lower not in cls.ALLOWED_DATA_SOURCES:
            return False, (
                f"Data source '{source}' is not allowed or not recognized. "
                f"Allowed data sources are: {', '.join(sorted(cls.ALLOWED_DATA_SOURCES))}. "
                "Valid source names: 'yahoo_finance', 'alpha_vantage', 'fmp' (or 'financial_modeling_prep')."
            )
        
        return True, None
    
    @classmethod
    def validate_agent_output(cls, output: str, agent_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate agent output is financial domain-related
        
        Args:
            output: Agent output text
            agent_name: Name of the agent
        
        Returns:
            (is_valid, error_message)
        """
        if not output or not isinstance(output, str):
            return False, f"{agent_name}: Output must be a non-empty string"
        
        # Check output length (reasonable limit)
        if len(output) > 50000:  # 50KB limit
            return False, (
                f"{agent_name}: Output exceeds maximum length of 50,000 characters "
                f"(current length: {len(output):,} characters). "
                "Please reduce the output size or split into multiple responses."
            )
        
        # Check for dangerous patterns
        try:
            sanitized = cls.sanitize_input(output)
        except GuardrailsError as e:
            return False, f"{agent_name}: Output contains dangerous patterns: {str(e)}"
        
        # For reporting agent, check if output is financial-related
        if agent_name.lower() == "reporting":
            output_lower = output.lower()
            has_financial_content = any(
                keyword in output_lower 
                for keyword in cls.FINANCIAL_OUTPUT_KEYWORDS
            )
            
            # Also check for non-financial content that shouldn't be there
            has_non_financial = any(
                keyword in output_lower 
                for keyword in cls.NON_FINANCIAL_KEYWORDS
            )
            
            if has_non_financial:
                return False, (
                    f"{agent_name}: Output contains non-financial domain content that is out of scope. "
                    "This system is designed for financial market analysis only. "
                    "Please ensure outputs focus on stocks, companies, financial metrics, and investment analysis."
                )
            
            # Reporting agent should have financial content
            if not has_financial_content and len(output) > 100:
                logger.warning(f"{agent_name}: Output may not be financial domain-related")
                # Don't fail, but warn
        
        return True, None
    
    @classmethod
    def validate_state(cls, state: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate agent state structure and content
        
        Args:
            state: AgentState dictionary
        
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(state, dict):
            return False, "State must be a dictionary"
        
        # Validate required fields exist
        required_fields = ["query", "query_type", "symbols"]
        for field in required_fields:
            if field not in state:
                return False, f"State missing required field: {field}"
        
        # Validate query
        query = state.get("query", "")
        is_valid, error = cls.validate_query(query)
        if not is_valid:
            return False, f"State query validation failed: {error}"
        
        # Validate symbols
        symbols = state.get("symbols", [])
        if symbols:
            is_valid, error, valid_symbols = cls.validate_symbols(symbols)
            if not is_valid:
                return False, f"State symbols validation failed: {error}"
        
        # Validate final_report if present
        final_report = state.get("final_report", "")
        if final_report:
            is_valid, error = cls.validate_agent_output(final_report, "Reporting")
            if not is_valid:
                return False, f"State final_report validation failed: {error}"
        
        return True, None
    
    @classmethod
    def check_query_intent(cls, query: str) -> Dict[str, Any]:
        """
        Analyze query intent and return metadata
        
        Args:
            query: User query
        
        Returns:
            Dictionary with intent analysis
        """
        query_lower = query.lower()
        
        intent = {
            "is_financial": False,
            "has_symbols": False,
            "query_type": None,
            "symbols": [],
            "risk_level": "low"
        }
        
        # Check for financial keywords
        intent["is_financial"] = any(
            keyword in query_lower 
            for keyword in cls.FINANCIAL_KEYWORDS
        )
        
        # Extract symbols
        symbols = cls.extract_symbols(query)
        intent["has_symbols"] = len(symbols) > 0
        intent["symbols"] = symbols
        
        # Detect query type
        if any(word in query_lower for word in ["compare", "comparison", "vs", "versus"]):
            intent["query_type"] = "comparison"
        elif any(word in query_lower for word in ["trend", "trends", "pattern", "patterns"]):
            intent["query_type"] = "trend"
        elif any(word in query_lower for word in ["sentiment", "news", "impact"]):
            intent["query_type"] = "sentiment"
        elif any(word in query_lower for word in ["similar", "like", "same as"]):
            intent["query_type"] = "similarity"
        else:
            intent["query_type"] = "single_stock"
        
        # Assess risk level
        if any(keyword in query_lower for keyword in cls.NON_FINANCIAL_KEYWORDS):
            intent["risk_level"] = "high"
        elif len(query) > 1000:
            intent["risk_level"] = "medium"
        elif len(symbols) > 10:
            intent["risk_level"] = "medium"
        else:
            intent["risk_level"] = "low"
        
        return intent


# Global guardrails instance
guardrails = Guardrails()


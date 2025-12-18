"""Parallelization strategy utilities for automatic parallel execution detection"""

from typing import List


class ParallelizationStrategy:
    """Determines parallelization strategy based on query and symbols"""
    
    # Maximum workers for different operations
    MAX_WORKERS_DATA_FETCHING = 20  # Cap for data fetching operations
    MAX_WORKERS_ANALYSIS = 16  # Cap for analysis operations
    DATA_TYPES_PER_SYMBOL = 5  # price, company, news, historical, financials
    ANALYSIS_TYPES_PER_SYMBOL = 4  # historical_patterns, financials, sentiment, trends
    
    @staticmethod
    def should_parallelize_data_fetching(symbols: List[str]) -> bool:
        """
        Determine if data fetching should be parallelized
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            True if parallelization should be used (always True - even single symbol has 5 data types)
        """
        return len(symbols) > 0  # Always parallelize (even single symbol has 5 data types)
    
    @staticmethod
    def should_parallelize_analysis(symbols: List[str]) -> bool:
        """
        Determine if analysis should be parallelized
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            True if parallelization should be used (always True - even single symbol has 4 analysis types)
        """
        return len(symbols) > 0  # Always parallelize (even single symbol has 4 analysis types)
    
    @staticmethod
    def get_max_workers_data_fetching(symbols: List[str]) -> int:
        """
        Get max workers for data fetching operations
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Maximum number of worker threads (capped at MAX_WORKERS_DATA_FETCHING)
        """
        if not symbols:
            return ParallelizationStrategy.DATA_TYPES_PER_SYMBOL
        
        # Calculate: N symbols × 5 data types, capped at MAX_WORKERS
        max_workers = len(symbols) * ParallelizationStrategy.DATA_TYPES_PER_SYMBOL
        return min(max_workers, ParallelizationStrategy.MAX_WORKERS_DATA_FETCHING)
    
    @staticmethod
    def get_max_workers_analysis(symbols: List[str]) -> int:
        """
        Get max workers for analysis operations
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Maximum number of worker threads (capped at MAX_WORKERS_ANALYSIS)
        """
        if not symbols:
            return ParallelizationStrategy.ANALYSIS_TYPES_PER_SYMBOL
        
        # Calculate: N symbols × 4 analysis types, capped at MAX_WORKERS
        max_workers = len(symbols) * ParallelizationStrategy.ANALYSIS_TYPES_PER_SYMBOL
        return min(max_workers, ParallelizationStrategy.MAX_WORKERS_ANALYSIS)
    
    @staticmethod
    def get_data_types() -> List[str]:
        """Get list of data types fetched per symbol"""
        return ["price", "company", "news", "historical", "financials"]
    
    @staticmethod
    def get_analysis_types() -> List[str]:
        """Get list of analysis types performed per symbol"""
        return ["historical_patterns", "financials", "sentiment", "trends"]


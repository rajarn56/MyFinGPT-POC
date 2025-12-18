"""Context caching and query similarity detection utilities"""

import time
from typing import Dict, List, Optional, Any
from loguru import logger
import numpy as np


class ContextCache:
    """Manages caching of query results and cross-query context awareness"""
    
    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initialize cache with TTL
        
        Args:
            cache_ttl_hours: Cache TTL in hours (default: 24)
        """
        self.cache: Dict[str, tuple] = {}  # {cache_key: (data, timestamp)}
        self.cache_ttl = cache_ttl_hours * 3600  # Convert to seconds
        self.query_history: List[tuple] = []  # List of (query, symbols, query_id, embedding)
        self.max_history_size = 100  # Keep only last 100 queries
    
    def get_cache_key(self, symbol: str, data_type: str) -> str:
        """
        Generate cache key for symbol + data type
        
        Args:
            symbol: Stock symbol
            data_type: Type of data (price, company, news, etc.)
            
        Returns:
            Cache key string
        """
        return f"{symbol}:{data_type}"
    
    def get(self, symbol: str, data_type: str) -> Optional[Dict]:
        """
        Get cached data if valid
        
        Args:
            symbol: Stock symbol
            data_type: Type of data
            
        Returns:
            Cached data if valid and not expired, None otherwise
        """
        key = self.get_cache_key(symbol, data_type)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                logger.debug(f"ContextCache: Cache hit for {key}")
                return data
            else:
                # Expired - remove from cache
                del self.cache[key]
                logger.debug(f"ContextCache: Cache expired for {key}")
        return None
    
    def set(self, symbol: str, data_type: str, data: Dict) -> None:
        """
        Cache data
        
        Args:
            symbol: Stock symbol
            data_type: Type of data
            data: Data to cache
        """
        key = self.get_cache_key(symbol, data_type)
        self.cache[key] = (data, time.time())
        logger.debug(f"ContextCache: Cached data for {key}")
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            # Normalize vectors
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(v1, v2) / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.warning(f"ContextCache: Error calculating cosine similarity: {e}")
            return 0.0
    
    def find_similar_queries(self, current_query: str, current_embedding: List[float],
                           similarity_threshold: float = 0.8) -> List[Dict]:
        """
        Find semantically similar previous queries
        
        Args:
            current_query: Current query text
            current_embedding: Embedding vector for current query
            similarity_threshold: Minimum similarity threshold (default: 0.8)
            
        Returns:
            List of similar queries sorted by similarity (highest first)
        """
        similar = []
        for query, symbols, query_id, embedding in self.query_history:
            similarity = self._cosine_similarity(current_embedding, embedding)
            if similarity >= similarity_threshold:
                similar.append({
                    "query": query,
                    "symbols": symbols,
                    "query_id": query_id,
                    "similarity": similarity
                })
        
        # Sort by similarity (highest first)
        return sorted(similar, key=lambda x: x["similarity"], reverse=True)
    
    def add_query_to_history(self, query: str, symbols: List[str],
                            query_id: str, embedding: List[float]) -> None:
        """
        Add query to history for similarity matching
        
        Args:
            query: Query text
            symbols: List of symbols in query
            query_id: Unique query identifier
            embedding: Query embedding vector
        """
        self.query_history.append((query, symbols, query_id, embedding))
        
        # Keep only last max_history_size queries
        if len(self.query_history) > self.max_history_size:
            self.query_history.pop(0)
        
        logger.debug(f"ContextCache: Added query to history | Query ID: {query_id} | Symbols: {symbols}")
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self.cache.clear()
        logger.info("ContextCache: Cache cleared")
    
    def clear_history(self) -> None:
        """Clear query history"""
        self.query_history.clear()
        logger.info("ContextCache: Query history cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        valid_entries = 0
        expired_entries = 0
        current_time = time.time()
        
        for key, (data, timestamp) in self.cache.items():
            if current_time - timestamp < self.cache_ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "query_history_size": len(self.query_history),
            "cache_ttl_hours": self.cache_ttl / 3600
        }


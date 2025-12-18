"""Embedding pipeline for vector database"""

from typing import List, Optional
import litellm
from ..utils.llm_config import llm_config


class EmbeddingPipeline:
    """Handles embedding generation for vector database"""
    
    def __init__(self, provider: Optional[str] = None):
        """
        Initialize embedding pipeline
        
        Args:
            provider: Embedding provider (openai, gemini, etc.)
        """
        self.provider = provider or "openai"
        self.config = llm_config.get_provider_config(self.provider)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        try:
            # Use LiteLLM for embeddings
            # For OpenAI
            if self.provider == "openai":
                response = litellm.embedding(
                    model="text-embedding-ada-002",
                    input=[text]
                )
                return response.data[0]["embedding"]
            
            # For other providers, use their embedding models
            elif self.provider == "gemini":
                # Gemini doesn't have direct embedding API in LiteLLM
                # Use text-embedding-004 or fallback to OpenAI
                response = litellm.embedding(
                    model="text-embedding-ada-002",  # Fallback
                    input=[text]
                )
                return response.data[0]["embedding"]
            
            else:
                # Default to OpenAI embeddings
                response = litellm.embedding(
                    model="text-embedding-ada-002",
                    input=[text]
                )
                return response.data[0]["embedding"]
        
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536  # Default OpenAI embedding dimension
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        # OpenAI ada-002 is 1536 dimensions
        return 1536


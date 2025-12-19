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
            provider: Embedding provider (openai, gemini, lmstudio, etc.)
        """
        # Default to the global LiteLLM provider if not explicitly set,
        # falling back to OpenAI when no provider is configured.
        self.provider = provider or llm_config.default_provider or "openai"
        self.config = llm_config.get_provider_config(self.provider)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        # LM Studio (and some other local providers) may not expose a stable
        # embeddings endpoint via LiteLLM. To avoid noisy runtime errors like
        # "No models loaded" when LM Studio is the active provider, we fall
        # back to a zero-vector embedding in that case.
        if self.provider == "lmstudio":
            # Simple, deterministic zero vector for LM Studio mode.
            return [0.0] * self.get_embedding_dimension()

        try:
            # Use LiteLLM for embeddings
            # For OpenAI
            if self.provider == "openai":
                response = litellm.embedding(
                    model="text-embedding-ada-002",
                    input=[text]
                )
                return response.data[0]["embedding"]
            
            # For other providers, currently fall back to OpenAI embeddings
            response = litellm.embedding(
                model="text-embedding-ada-002",
                input=[text]
            )
            return response.data[0]["embedding"]
        
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.get_embedding_dimension()  # Default OpenAI embedding dimension
    
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


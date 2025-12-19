"""Embedding pipeline for vector database"""

from typing import List, Optional
import litellm
from ..utils.llm_config import llm_config


class EmbeddingPipeline:
    """Handles embedding generation for vector database"""
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize embedding pipeline
        
        Args:
            provider: Embedding provider (openai, gemini, lmstudio, etc.)
                     If None, uses EMBEDDING_PROVIDER env var or falls back to LLM provider
                     Note: Embeddings can use a different provider than LLM calls
            model: Embedding model name (e.g., "text-embedding-ada-002" for OpenAI, 
                   or LMStudio embedding model name)
                   If None, uses EMBEDDING_MODEL env var or provider default
        """
        import os
        # Check for explicit embedding provider env var first
        embedding_provider = os.getenv("EMBEDDING_PROVIDER")
        if embedding_provider:
            self.provider = embedding_provider
        elif provider:
            self.provider = provider
        else:
            # Default to the global LiteLLM provider if not explicitly set,
            # falling back to OpenAI when no provider is configured.
            self.provider = llm_config.default_provider or "openai"
        
        self.config = llm_config.get_provider_config(self.provider)
        
        # Get embedding model name
        # Priority: explicit model param > EMBEDDING_MODEL env var > config model > default
        embedding_model_env = os.getenv("EMBEDDING_MODEL")
        if model:
            self.embedding_model = model
        elif embedding_model_env:
            self.embedding_model = embedding_model_env
        elif self.provider == "openai":
            self.embedding_model = "text-embedding-ada-002"  # OpenAI default
        elif self.provider == "lmstudio":
            # For LMStudio, try to use the configured model, or default embedding model name
            # LMStudio typically uses OpenAI-compatible embedding models
            self.embedding_model = self.config.get("embedding_model") or self.config.get("model") or "text-embedding-ada-002"
        else:
            # Default to OpenAI embedding model for other providers
            self.embedding_model = "text-embedding-ada-002"
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        from loguru import logger
        import os
        
        # LM Studio uses OpenAI-compatible API, so we can use LiteLLM with it
        if self.provider == "lmstudio":
            logger.info(f"[Embeddings] Provider is lmstudio, using model: {self.embedding_model}")
            try:
                # Set up LMStudio API base if configured
                api_base = self.config.get("api_base")
                if api_base:
                    os.environ["OPENAI_API_BASE"] = api_base
                
                # LMStudio uses OpenAI-compatible format: openai/<model>
                # Format the model name for LiteLLM
                model_name = self.embedding_model
                if not model_name.startswith("openai/"):
                    model_name = f"openai/{model_name}"
                
                logger.debug(f"[Embeddings] Attempting LMStudio embedding with model: {model_name}")
                
                # Try LMStudio embeddings first
                response = litellm.embedding(
                    model=model_name,
                    input=[text],
                    api_base=api_base
                )
                embedding = response.data[0]["embedding"]
                
                # Validate embedding is not all zeros
                if all(x == 0.0 for x in embedding):
                    logger.warning(f"[Embeddings] Received zero vector from LMStudio embedding API")
                    raise ValueError("Zero vector received from LMStudio")
                else:
                    logger.info(f"[Embeddings] Successfully generated LMStudio embedding")
                    return embedding
                    
            except Exception as e:
                logger.warning(f"[Embeddings] LMStudio embedding failed: {e}")
                logger.info(f"[Embeddings] Falling back to OpenAI embeddings")
                # Try OpenAI embeddings as fallback
                try:
                    # Check if OpenAI API key is available
                    openai_key = os.getenv("OPENAI_API_KEY")
                    if not openai_key:
                        logger.warning(f"[Embeddings] No OPENAI_API_KEY found, using zero vector fallback")
                        return [0.0] * self.get_embedding_dimension()
                    
                    # Use OpenAI embeddings
                    response = litellm.embedding(
                        model="text-embedding-ada-002",
                        input=[text]
                    )
                    embedding = response.data[0]["embedding"]
                    # Validate embedding is not all zeros
                    if all(x == 0.0 for x in embedding):
                        logger.warning(f"[Embeddings] Received zero vector from OpenAI embedding API")
                    else:
                        logger.info(f"[Embeddings] Successfully generated OpenAI embedding (fallback from lmstudio)")
                    return embedding
                except Exception as fallback_error:
                    logger.error(f"[Embeddings] Failed to generate OpenAI embedding fallback: {fallback_error}")
                    logger.warning(f"[Embeddings] Using zero vector fallback - semantic search will be disabled")
                    return [0.0] * self.get_embedding_dimension()

        try:
            # Use LiteLLM for embeddings
            # For OpenAI
            if self.provider == "openai":
                response = litellm.embedding(
                    model=self.embedding_model,
                    input=[text]
                )
                embedding = response.data[0]["embedding"]
                # Validate embedding is not all zeros
                if all(x == 0.0 for x in embedding):
                    logger.warning(f"[Embeddings] Received zero vector from OpenAI embedding API")
                return embedding
            
            # For other providers, currently fall back to OpenAI embeddings
            # (unless they have their own embedding support)
            response = litellm.embedding(
                model=self.embedding_model,
                input=[text]
            )
            embedding = response.data[0]["embedding"]
            # Validate embedding is not all zeros
            if all(x == 0.0 for x in embedding):
                logger.warning(f"[Embeddings] Received zero vector from embedding API (provider: {self.provider})")
            return embedding
        
        except Exception as e:
            logger.error(f"[Embeddings] Error generating embedding (provider: {self.provider}): {e}")
            # Try OpenAI as last resort fallback
            try:
                logger.info(f"[Embeddings] Attempting OpenAI embedding fallback")
                openai_key = os.getenv("OPENAI_API_KEY")
                if openai_key:
                    response = litellm.embedding(
                        model="text-embedding-ada-002",
                        input=[text]
                    )
                    embedding = response.data[0]["embedding"]
                    if not all(x == 0.0 for x in embedding):
                        logger.info(f"[Embeddings] Successfully used OpenAI embedding fallback")
                        return embedding
            except Exception as fallback_error:
                logger.debug(f"[Embeddings] OpenAI fallback also failed: {fallback_error}")
            
            # Return zero vector as last resort
            logger.warning(f"[Embeddings] Falling back to zero vector - semantic search will be disabled")
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


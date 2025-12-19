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
        
        # Cache for detected embedding dimension (lazy-loaded)
        self._cached_dimension: Optional[int] = None
    
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
                
                # LiteLLM requires OPENAI_API_KEY to be set even for LMStudio (using openai/ prefix)
                # Set a dummy key if not already set - LMStudio doesn't actually use it
                api_key = self.config.get("api_key")
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
                elif not os.getenv("OPENAI_API_KEY"):
                    # Set dummy key for LMStudio (it doesn't validate the key)
                    os.environ["OPENAI_API_KEY"] = "lm-studio"
                
                # LMStudio uses OpenAI-compatible format: openai/<model>
                # Format the model name for LiteLLM
                model_name = self.embedding_model
                if not model_name.startswith("openai/"):
                    model_name = f"openai/{model_name}"
                
                logger.debug(f"[Embeddings] Attempting LMStudio embedding with model: {model_name}, api_base: {api_base}")
                
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
                    # Cache the dimension
                    self._cached_dimension = len(embedding)
                    logger.info(f"[Embeddings] Successfully generated LMStudio embedding (dimension: {self._cached_dimension})")
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
                    # Cache the dimension
                    self._cached_dimension = len(embedding)
                    # Validate embedding is not all zeros
                    if all(x == 0.0 for x in embedding):
                        logger.warning(f"[Embeddings] Received zero vector from OpenAI embedding API")
                    else:
                        logger.info(f"[Embeddings] Successfully generated OpenAI embedding (fallback from lmstudio, dimension: {self._cached_dimension})")
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
                # Cache the dimension
                self._cached_dimension = len(embedding)
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
            # Cache the dimension
            self._cached_dimension = len(embedding)
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
                    # Cache the dimension
                    self._cached_dimension = len(embedding)
                    if not all(x == 0.0 for x in embedding):
                        logger.info(f"[Embeddings] Successfully used OpenAI embedding fallback (dimension: {self._cached_dimension})")
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
        """
        Get the dimension of embeddings for the current model.
        Detects dimension dynamically by generating a test embedding if not cached.
        
        Returns:
            Embedding dimension (e.g., 1536 for OpenAI ada-002, 768 for nomic-embed-text-v1.5)
        """
        # Return cached dimension if available
        if self._cached_dimension is not None:
            return self._cached_dimension
        
        from loguru import logger
        
        # Try to detect dimension by generating a test embedding
        try:
            test_embedding = self.generate_embedding("test")
            if test_embedding and len(test_embedding) > 0 and not all(x == 0.0 for x in test_embedding):
                self._cached_dimension = len(test_embedding)
                logger.debug(f"[Embeddings] Detected embedding dimension: {self._cached_dimension} for model {self.embedding_model}")
                return self._cached_dimension
        except Exception as e:
            logger.debug(f"[Embeddings] Could not detect dimension dynamically: {e}")
        
        # Fallback to known dimensions based on model name
        model_lower = self.embedding_model.lower()
        if "nomic-embed" in model_lower or "nomic-embed-text" in model_lower:
            self._cached_dimension = 768
            logger.debug(f"[Embeddings] Using known dimension 768 for nomic-embed model")
            return 768
        elif "ada-002" in model_lower or "text-embedding-ada-002" in model_lower:
            self._cached_dimension = 1536
            logger.debug(f"[Embeddings] Using known dimension 1536 for ada-002 model")
            return 1536
        elif "text-embedding-3" in model_lower:
            # OpenAI text-embedding-3 models can be 1536 or other dimensions
            # Default to 1536, but will be corrected on first actual embedding
            self._cached_dimension = 1536
            return 1536
        else:
            # Default fallback (will be corrected on first actual embedding)
            self._cached_dimension = 1536
            logger.warning(f"[Embeddings] Unknown model {self.embedding_model}, defaulting to dimension 1536")
            return 1536


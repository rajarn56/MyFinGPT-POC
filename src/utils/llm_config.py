"""LiteLLM configuration and provider management"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

try:
    import yaml
except ImportError:
    # Fallback if PyYAML not installed
    yaml = None

# Load environment variables
load_dotenv()


class LLMConfig:
    """Manages LLM provider configuration using LiteLLM"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize LLM configuration
        
        Args:
            config_path: Path to llm_templates.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "llm_templates.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        # Support both LITELLM_PROVIDER and LITELLM_MODEL for backward compatibility
        env_provider = os.getenv("LITELLM_PROVIDER") or os.getenv("LITELLM_MODEL")
        self.default_provider = env_provider or self.config.get("default", {}).get("provider", "openai")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if yaml is None:
            print("Warning: PyYAML not installed, using defaults")
            return {}
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config or {}
        except FileNotFoundError:
            print(f"Warning: Config file not found at {self.config_path}, using defaults")
            return {}
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
            return {}
    
    def get_provider_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for a specific provider
        
        Args:
            provider: Provider name (openai, gemini, anthropic, ollama, lmstudio)
                    If None, uses default provider
        
        Returns:
            Provider configuration dictionary
        """
        if provider is None:
            provider = self.default_provider
        
        provider_config = self.config.get(provider, {})
        
        # Handle LM Studio specially - it uses OpenAI-compatible API
        if provider == "lmstudio" and not provider_config:
            # Fallback to default LM Studio config if not in config file
            provider_config = {
                "model": os.getenv("LM_STUDIO_MODEL", "local-model"),
                "api_base": os.getenv("LM_STUDIO_API_BASE", "http://localhost:1234/v1"),
                "temperature": 0.7,
                "max_tokens": 4000
            }
        
        # Resolve environment variables in config
        resolved_config = {}
        for key, value in provider_config.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                # Extract env var name and default value
                env_var = value[2:-1]
                if ":-" in env_var:
                    var_name, default = env_var.split(":-", 1)
                    resolved_config[key] = os.getenv(var_name, default)
                else:
                    resolved_config[key] = os.getenv(env_var, value)
            else:
                resolved_config[key] = value
        
        return resolved_config
    
    def get_model_name(self, provider: Optional[str] = None) -> str:
        """Get model name for a provider"""
        config = self.get_provider_config(provider)
        return config.get("model", "gpt-4")
    
    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """Get API key for a provider"""
        config = self.get_provider_config(provider)
        return config.get("api_key")
    
    def create_litellm_client(self, provider: Optional[str] = None):
        """
        Create a LiteLLM client for the specified provider
        
        Args:
            provider: Provider name, or None for default
        
        Returns:
            LiteLLM client configuration
        """
        import litellm
        
        if provider is None:
            provider = self.default_provider
        
        config = self.get_provider_config(provider)
        model = config.get("model")
        api_key = config.get("api_key")
        api_base = config.get("api_base")
        
        # Handle LM Studio specially - it uses OpenAI-compatible API
        if provider == "lmstudio":
            # LM Studio uses OpenAI-compatible endpoint
            # LiteLLM format: openai/<model> with custom api_base
            if api_base:
                # Format model as openai/<model> for LiteLLM
                if not model.startswith("openai/"):
                    model = f"openai/{model}"
                os.environ["OPENAI_API_BASE"] = api_base
            # LM Studio typically doesn't require API key, but set if provided
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
            else:
                # Set a dummy key if none provided (some OpenAI-compatible APIs require it)
                os.environ["OPENAI_API_KEY"] = "lm-studio"
        else:
            # Set up LiteLLM for other providers
            if api_key:
                # Set provider-specific API key environment variable
                provider_env_key = f"{provider.upper()}_API_KEY"
                os.environ[provider_env_key] = api_key
            
            if api_base:
                # Set provider-specific API base environment variable
                provider_env_base = f"{provider.upper()}_API_BASE"
                os.environ[provider_env_base] = api_base
        
        return {
            "model": model,
            "api_key": api_key,
            "api_base": api_base,
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 4000),
        }
    
    def list_available_providers(self) -> list:
        """List all available providers in config"""
        providers = []
        for key in self.config.keys():
            if key != "default":
                providers.append(key)
        return providers


# Global instance
llm_config = LLMConfig()


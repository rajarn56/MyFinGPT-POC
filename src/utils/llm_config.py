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
        self.default_provider = os.getenv("LITELLM_MODEL", self.config.get("default", {}).get("provider", "openai"))
    
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
            provider: Provider name (openai, gemini, anthropic, ollama)
                    If None, uses default provider
        
        Returns:
            Provider configuration dictionary
        """
        if provider is None:
            provider = self.default_provider
        
        provider_config = self.config.get(provider, {})
        
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
        
        config = self.get_provider_config(provider)
        model = config.get("model")
        api_key = config.get("api_key")
        api_base = config.get("api_base")
        
        # Set up LiteLLM
        if api_key:
            os.environ[f"{provider.upper()}_API_KEY"] = api_key
        
        if api_base:
            os.environ[f"{provider.upper()}_API_BASE"] = api_base
        
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


"""Integration configuration management for MyFinGPT"""

import os
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

try:
    import yaml
except ImportError:
    yaml = None

# Load environment variables
load_dotenv()


class IntegrationConfig:
    """Manages integration enable/disable configuration"""
    
    # Data type to integration mapping (preferred order)
    DATA_SOURCE_MAPPING = {
        "stock_price": {
            "preferred": ["yahoo_finance", "alpha_vantage", "fmp"],
            "description": "Real-time stock price data"
        },
        "company_info": {
            "preferred": ["yahoo_finance", "fmp", "alpha_vantage"],
            "description": "Company profile and information"
        },
        "financial_statements": {
            "preferred": ["fmp", "yahoo_finance"],
            "description": "Income statement, balance sheet, cash flow"
        },
        "news": {
            "preferred": ["yahoo_finance", "fmp"],
            "description": "Company news and press releases"
        },
        "historical_data": {
            "preferred": ["yahoo_finance"],
            "description": "Historical price data"
        },
        "technical_indicators": {
            "preferred": ["alpha_vantage"],
            "description": "Technical analysis indicators"
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize integration configuration
        
        Args:
            config_path: Path to integrations.yaml file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "integrations.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        if yaml is None:
            logger.warning("PyYAML not installed, using defaults")
            return self._get_default_config()
        
        try:
            if not self.config_path.exists():
                logger.warning(f"Integration config file not found at {self.config_path}, using defaults")
                return self._get_default_config()
            
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config or "integrations" not in config:
                logger.warning("Invalid integration config, using defaults")
                return self._get_default_config()
            
            return config
        except Exception as e:
            logger.error(f"Error loading integration config: {e}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default configuration (all integrations enabled)"""
        return {
            "integrations": {
                "yahoo_finance": {
                    "enabled": True,
                    "description": "Yahoo Finance data source"
                },
                "alpha_vantage": {
                    "enabled": True,
                    "description": "Alpha Vantage API"
                },
                "fmp": {
                    "enabled": True,
                    "description": "Financial Modeling Prep API"
                }
            }
        }
    
    def _validate_config(self):
        """Validate configuration structure"""
        if "integrations" not in self.config:
            logger.warning("Invalid config structure, using defaults")
            self.config = self._get_default_config()
    
    def is_enabled(self, integration_name: str) -> bool:
        """
        Check if an integration is enabled
        
        Args:
            integration_name: Name of integration (yahoo_finance, alpha_vantage, fmp)
        
        Returns:
            True if enabled, False otherwise
        """
        # Check environment variable override first
        env_var = f"ENABLE_{integration_name.upper()}"
        env_value = os.getenv(env_var)
        if env_value is not None:
            return env_value.lower() in ("true", "1", "yes", "on")
        
        # Check config file
        integrations = self.config.get("integrations", {})
        integration = integrations.get(integration_name, {})
        return integration.get("enabled", True)
    
    def get_enabled_integrations(self) -> List[str]:
        """
        Get list of enabled integrations
        
        Returns:
            List of enabled integration names
        """
        enabled = []
        integrations = self.config.get("integrations", {})
        
        for name in integrations.keys():
            if self.is_enabled(name):
                enabled.append(name)
        
        return enabled
    
    def get_disabled_integrations(self) -> List[str]:
        """
        Get list of disabled integrations
        
        Returns:
            List of disabled integration names
        """
        disabled = []
        integrations = self.config.get("integrations", {})
        
        for name in integrations.keys():
            if not self.is_enabled(name):
                disabled.append(name)
        
        return disabled
    
    def get_integration_info(self, integration_name: str) -> Dict:
        """
        Get information about an integration
        
        Args:
            integration_name: Name of integration
        
        Returns:
            Integration info dictionary
        """
        integrations = self.config.get("integrations", {})
        return integrations.get(integration_name, {})
    
    def get_enabled_sources_for_data_type(self, data_type: str) -> List[str]:
        """
        Get enabled sources for a specific data type (filtered by integration status)
        
        Args:
            data_type: Data type (stock_price, company_info, financial_statements, etc.)
        
        Returns:
            List of enabled integration names for this data type, in preferred order
        """
        if data_type not in self.DATA_SOURCE_MAPPING:
            logger.warning(f"Unknown data type: {data_type}")
            return []
        
        preferred = self.DATA_SOURCE_MAPPING[data_type]["preferred"]
        enabled = []
        
        for source in preferred:
            if self.is_enabled(source):
                enabled.append(source)
        
        return enabled
    
    def get_data_source_mapping(self) -> Dict:
        """
        Get the data source mapping configuration
        
        Returns:
            Data source mapping dictionary
        """
        return self.DATA_SOURCE_MAPPING.copy()


# Global instance
integration_config = IntegrationConfig()


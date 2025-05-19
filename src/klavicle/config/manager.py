"""Configuration manager for Klavicle."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Constants
DEFAULT_CONFIG_DIR = "~/.klavicle"
CONFIG_FILENAME = "config.json"
DEFAULT_CONFIG = {
    "ai": {
        "default_provider": "mock",
        "providers": {
            "openai": {
                "api_key": "",
                "default_model": "gpt-4o",
            },
            "anthropic": {
                "api_key": "",
                "default_model": "claude-3-opus-20240229", 
            }
        },
        "output": {
            "color": True,
            "verbose": True,
        }
    }
}


class ConfigManager:
    """
    Manages configuration for Klavicle.
    
    This class is responsible for loading, saving, and accessing
    configuration settings for the application.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        self.config_dir = Path(config_dir or DEFAULT_CONFIG_DIR).expanduser()
        self.config_file = self.config_dir / CONFIG_FILENAME
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the config file.
        
        If the file doesn't exist, create it with default values.
        
        Returns:
            The loaded configuration
        """
        # Create config directory if it doesn't exist
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
        # If config file doesn't exist, create it with defaults
        if not self.config_file.exists():
            return self._save_config(DEFAULT_CONFIG)
        
        # Load and return existing config
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, create a new one
            return self._save_config(DEFAULT_CONFIG)
    
    def _save_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save configuration to the config file.
        
        Args:
            config: Configuration to save
            
        Returns:
            The saved configuration
        """
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        return config
    
    def get(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Dot-notation key to retrieve (e.g., "ai.providers.openai.api_key")
            default: Default value to return if key is not found
            
        Returns:
            The configuration value, the entire config if key is None,
            or default if the key is not found
        """
        if key is None:
            return self.config
        
        # Handle dot notation for nested keys
        parts = key.split(".")
        value = self.config
        
        for part in parts:
            if not isinstance(value, dict) or part not in value:
                return default
            value = value[part]
            
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and save to disk.
        
        Args:
            key: Dot-notation key to set (e.g., "ai.providers.openai.api_key")
            value: Value to set
        """
        if not key:
            raise ValueError("Key cannot be empty")
        
        # Handle dot notation for nested keys
        parts = key.split(".")
        config = self.config
        
        # Navigate to the parent of the target key
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            elif not isinstance(config[part], dict):
                config[part] = {}
            config = config[part]
            
        # Set the value at the target key
        config[parts[-1]] = value
        
        # Save the updated config
        self._save_config(self.config)
        
    def unset(self, key: str) -> None:
        """
        Remove a configuration value and save to disk.
        
        Args:
            key: Dot-notation key to unset (e.g., "ai.providers.openai.api_key")
        """
        if not key:
            raise ValueError("Key cannot be empty")
        
        # Handle dot notation for nested keys
        parts = key.split(".")
        config = self.config
        
        # Navigate to the parent of the target key
        for part in parts[:-1]:
            if part not in config or not isinstance(config[part], dict):
                # Key doesn't exist, nothing to unset
                return
            config = config[part]
            
        # Remove the key if it exists
        if parts[-1] in config:
            del config[parts[-1]]
            
        # Save the updated config
        self._save_config(self.config)
        
    def get_ai_provider_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for the specified AI provider.
        
        Args:
            provider: Name of the AI provider ("openai" or "anthropic")
            
        Returns:
            API key from config, environment variable, or None if not found
        """
        # First try environment variable
        env_var = f"{provider.upper()}_API_KEY"
        api_key = os.environ.get(env_var)
        
        # If not found, try config
        if not api_key:
            api_key = self.get(f"ai.providers.{provider}.api_key")
            
        return api_key
    
    def get_ai_provider_model(self, provider: str) -> str:
        """
        Get default model for the specified AI provider.
        
        Args:
            provider: Name of the AI provider ("openai" or "anthropic")
            
        Returns:
            Default model from config or hard-coded default if not found
        """
        model = self.get(f"ai.providers.{provider}.default_model")
        
        # Return model from config or defaults
        if model:
            return model
        
        # Hard-coded defaults
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-opus-20240229",
            "mock": "mock-model"
        }
        
        return defaults.get(provider, "")
    
    def get_default_ai_provider(self) -> str:
        """
        Get the default AI provider.
        
        Returns:
            Default provider from config or "mock" if not found
        """
        return self.get("ai.default_provider", "mock")


# Singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """
    Get the global ConfigManager instance.
    
    Returns:
        ConfigManager singleton instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
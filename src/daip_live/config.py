
import yaml
import os
from typing import Optional

from pydantic import ValidationError

from daip_live.core.models import AppConfig


class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class ConfigManager:
    """Manages loading, validation, and access to application configuration."""
    def __init__(self, config_path: str = "config.yaml"):
        self._config_path = config_path
        self._config: Optional[AppConfig] = None

    def _load(self) -> None:
        """Loads, validates, and stores the configuration."""
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)
            self._config = AppConfig(**raw_config)
        except FileNotFoundError:
            raise ConfigError(f"Configuration file not found at: {self._config_path}")
        except (ValidationError, TypeError, yaml.YAMLError) as e:
            raise ConfigError(f"Configuration file is invalid: {e}")

    def is_loaded(self) -> bool:
        """Returns True if the configuration has been loaded."""
        return self._config is not None

    def get_config(self) -> AppConfig:
        """Returns the loaded configuration, loading it first if necessary."""
        if not self.is_loaded():
            self._load()
        
        if self._config is None: # Should not happen if load() works correctly
            raise ConfigError("Configuration is None after loading.")
            
        return self._config

def create_config_yaml_if_not_exists(path: str = "config.yaml") -> None:
    """Creates a default config.yaml if one doesn't exist."""
    if not os.path.exists(path):
        default_config = {
            "database": {"path": "daip_live.db"},
            "llm_provider": {
                "default_model": "ollama/llama3",
                "embedding_model": "all-MiniLM-L6-v2",
            },
            "knowledge_base": {"directory": "docs/"},
        }
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, indent=2)
        print(f"Created default configuration file at: {path}")

# Global instance of the ConfigManager
# The application will use this instance throughout.
config_manager = ConfigManager()


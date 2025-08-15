"""@Time    : 2025-07-05 17:45:00
@Author  : DAIP-LIVE Team
@File    : config.py
@Description: Unified configuration system for the DAIP-LIVE application.
             Handles loading, validation, and access to application configuration.
"""
import logging
from pathlib import Path
from typing import Optional, Union

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# --- Pydantic Models for Configuration Structure ---

class OllamaConfig(BaseModel):
    """Configuration for the Ollama LLM provider."""
    generation_model: str = "llama3:instruct"
    embedding_model: str = "nomic-embed-text:latest"
    host: str = "http://localhost:11434"
    timeout: int = 30

class LLMConfig(BaseModel):
    """Top-level LLM configuration."""
    provider: str = "ollama"
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)

class VectorStoreConfig(BaseModel):
    """Configuration for the vector store."""
    chroma_db_path: str = "data/chroma_db"
    role_collection_name: str = "roles"

class LoggingConfig(BaseModel):
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class TokenManagementConfig(BaseModel):
    """Configuration for token management and optimization."""
    max_context_tokens: int = 4096
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    enable_cost_tracking: bool = True
    enable_context_optimization: bool = True
    compression_threshold: float = 0.8  # Start compression when context is 80% full

class UserProfileConfig(BaseModel):
    """Configuration for user profiles."""
    data_dir: str = "data/user_profiles"
    max_interaction_history: int = 100
    enable_intent_tracking: bool = True

class SessionConfig(BaseModel):
    """Configuration for session management."""
    auth_data_dir: str = "data/auth"
    session_expiry_minutes: int = 60
    token_expiry_minutes: int = 60
    enable_session_tracking: bool = True

class AppConfig(BaseModel):
    """Root model for the entire application configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    token_management: TokenManagementConfig = Field(default_factory=TokenManagementConfig)
    user_profile: UserProfileConfig = Field(default_factory=UserProfileConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    roles_config_path: str = "configs/roles.yaml"
    
    # Additional settings needed by main.py
    log_level: str = "INFO"
    allowed_origins: list[str] = ["*"]


# --- Configuration Loading Logic ---

_config: Optional[AppConfig] = None

def load_config(config_path: Union[str, Path] = "config.yaml") -> AppConfig:
    """Loads configuration from a YAML file, validates it with Pydantic models, and returns it.
    
    Args:
        config_path: Path to the configuration file (string or Path object)
        
    Returns:
        AppConfig: The validated configuration object
        
    Note:
        If the configuration file doesn't exist, default values will be used.
        If the file exists but has invalid content, an error will be logged and defaults used.
    """
    global _config
    if _config:
        return _config

    # Convert string path to Path object if needed
    if isinstance(config_path, str):
        config_path = Path(config_path)

    if not config_path.exists():
        logger.warning(f"Config file not found at '{config_path.resolve()}'. Using default settings.")
        _config = AppConfig()
        return _config

    try:
        logger.info(f"Loading configuration from '{config_path.resolve()}'...")
        with open(config_path, encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            
        if not config_data:
            logger.warning("Configuration file is empty or invalid. Using default settings.")
            _config = AppConfig()
        else:
            # Create config with loaded values, falling back to defaults for missing values
            _config = AppConfig(**(config_data or {}))
            
        # Set up logging based on configuration
        log_level = getattr(logging, _config.logging.level.upper(), logging.INFO)
        logging.basicConfig(level=log_level, format=_config.logging.format)
        logger.debug("Configuration loaded successfully")
        
        return _config
    except (yaml.YAMLError, Exception) as e:
        logger.error(f"Failed to load or validate configuration from {config_path}: {e}")
        logger.warning("Using default configuration settings due to error")
        _config = AppConfig()
        return _config

def get_config() -> AppConfig:
    """Get the current configuration or load it if not already loaded.
    
    Returns:
        AppConfig: The current configuration
    """
    global _config
    if _config is None:
        return load_config()
    return _config

def reload_config(config_path: Union[str, Path] = "config.yaml") -> AppConfig:
    """Force reload the configuration from disk.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        AppConfig: The reloaded configuration
    """
    global _config
    _config = None
    return load_config(config_path)

# --- Global Settings Instance ---

# Create the global settings instance that can be imported by other modules
settings = load_config()
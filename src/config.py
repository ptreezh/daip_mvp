# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-05 17:45:00
@Author  : DAIP-LIVE Team
@File    : config.py
@Description: Handles loading and validation of application configuration.
"""
import logging
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# --- Pydantic Models for Configuration Structure ---

class OllamaConfig(BaseModel):
    generation_model: str = "llama3:instruct"
    embedding_model: str = "nomic-embed-text:latest"
    host: str = "http://localhost:11434"
    timeout: int = 30

class LLMConfig(BaseModel):
    provider: str = "ollama"
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)

class VectorStoreConfig(BaseModel):
    chroma_db_path: str = "data/chroma_db"
    role_collection_name: str = "roles"

class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

class TokenManagementConfig(BaseModel):
    max_context_tokens: int = 4096
    cost_per_1k_input_tokens: float = 0.0
    cost_per_1k_output_tokens: float = 0.0
    enable_cost_tracking: bool = True
    enable_context_optimization: bool = True
    compression_threshold: float = 0.8  # Start compression when context is 80% full

class AppConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    token_management: TokenManagementConfig = Field(default_factory=TokenManagementConfig)
    roles_config_path: str = "configs/roles.yaml"
    
    # Additional settings needed by main.py
    log_level: str = "INFO"
    allowed_origins: list[str] = ["*"]


# --- Configuration Loading Logic ---

_config: Optional[AppConfig] = None

def load_config(config_path: Path = Path("config.yaml")) -> AppConfig:
    """Loads configuration from a YAML file, validates it, and returns it."""
    global _config
    if _config:
        return _config

    if not config_path.exists():
        logger.warning(f"Config file not found at '{config_path}'. Using default settings.")
        _config = AppConfig()
        return _config

    logger.info(f"Loading configuration from '{config_path}'...")
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    _config = AppConfig(**(config_data or {}))
    return _config

# --- Global Settings Instance ---

# Create the global settings instance that can be imported by other modules
settings = load_config()
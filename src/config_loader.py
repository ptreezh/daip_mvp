# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-05 18:30:00
@Author  : DAIP-LIVE Team
@File    : config_loader.py
@Description:
    Loads and validates application configuration from a YAML file.
"""
import logging
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# --- Pydantic Models for Configuration ---

class OllamaConfig(BaseModel):
    """Configuration for the Ollama provider."""
    generation_model: str = Field(..., description="Model for text generation.")
    embedding_model: str = Field(..., description="Model for text embeddings.")
    host: str = Field(..., description="Ollama server host URL.")
    timeout: int = Field(default=30, description="Request timeout in seconds.")

class LLMConfig(BaseModel):
    """Top-level LLM configuration."""
    provider: str = Field(..., description="The LLM provider to use (e.g., 'ollama').")
    ollama: Optional[OllamaConfig] = Field(None, description="Ollama-specific settings.")

class VectorStoreConfig(BaseModel):
    """Configuration for the vector store."""
    chroma_db_path: str = Field(..., description="Path to the ChromaDB database.")
    role_collection_name: str = Field(..., description="Name of the collection for roles.")

class LoggingConfig(BaseModel):
    """Configuration for logging."""
    level: str = Field(default="INFO", description="Logging level.")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format."
    )

class AppConfig(BaseModel):
    """Root model for the entire application configuration."""
    llm: LLMConfig
    vector_store: VectorStoreConfig
    logging: LoggingConfig

# --- Configuration Loading Function ---

def load_config(config_path: str = "config.yaml") -> AppConfig:
    """
    Loads configuration from a YAML file and validates it with Pydantic models.
    """
    path = Path(config_path)
    if not path.is_file():
        logger.error(f"Configuration file not found at: {path.resolve()}")
        raise FileNotFoundError(f"Configuration file not found: {path.resolve()}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        
        if not config_data:
            raise ValueError("Configuration file is empty or invalid.")
            
        return AppConfig(**config_data)
    except (yaml.YAMLError, Exception) as e:
        logger.error(f"Failed to load or validate configuration from {path}: {e}")
        raise ValueError(f"Configuration error in {path}: {e}")
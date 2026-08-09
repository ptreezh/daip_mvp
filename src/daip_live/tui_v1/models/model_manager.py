"""
Model Manager for newP6 TUI

This module provides comprehensive model management functionality.
"""

import logging
from typing import Any, Optional

from .model_registry import ModelInfo, ModelRegistry

logger = logging.getLogger(__name__)


class ModelManager:
    """Manager for AI models"""

    def __init__(self):
        self.registry = ModelRegistry()
        self.current_model: Optional[str] = None
        self.model_configs: dict[str, dict[str, Any]] = {}

    def set_current_model(self, model_name: str) -> bool:
        """Set the current active model"""
        if self.registry.get_model(model_name):
            self.current_model = model_name
            logger.info(f"Set current model to: {model_name}")
            return True
        return False

    def get_current_model(self) -> Optional[ModelInfo]:
        """Get the current active model"""
        if self.current_model:
            return self.registry.get_model(self.current_model)
        return None

    def list_available_models(self) -> list[ModelInfo]:
        """List all available models"""
        return self.registry.list_models()

    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        return self.registry.get_model(model_name)

    def configure_model(self, model_name: str, config: dict[str, Any]) -> bool:
        """Configure a model with specific settings"""
        if self.registry.get_model(model_name):
            self.model_configs[model_name] = config
            logger.info(f"Configured model: {model_name}")
            return True
        return False

    def get_model_config(self, model_name: str) -> dict[str, Any]:
        """Get configuration for a model"""
        return self.model_configs.get(model_name, {})

    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model"""
        return self.set_current_model(model_name)

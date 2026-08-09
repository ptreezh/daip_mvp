"""
Model Switcher for newP6 TUI

This module provides model switching functionality.
"""

import logging
from datetime import datetime
from typing import Any, Optional

from .model_manager import ModelManager
from .model_registry import ModelInfo, ModelType

logger = logging.getLogger(__name__)


class ModelSwitcher:
    """Model switching functionality"""

    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.model_manager = model_manager or ModelManager()
        self.switch_history: list[dict[str, Any]] = []
        self.max_history = 100

    def switch_to_model(self, model_name: str) -> bool:
        """Switch to a specific model"""
        if self.model_manager.switch_model(model_name):
            # Record switch in history
            self.switch_history.append(
                {
                    "model_name": model_name,
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                }
            )

            # Limit history size
            if len(self.switch_history) > self.max_history:
                self.switch_history.pop(0)

            logger.info(f"Switched to model: {model_name}")
            return True
        return False

    def get_available_models(self) -> list[ModelInfo]:
        """Get list of available models for switching"""
        return self.model_manager.list_available_models()

    def get_current_model(self) -> Optional[ModelInfo]:
        """Get current model information"""
        return self.model_manager.get_current_model()

    def get_switch_history(self) -> list[dict[str, Any]]:
        """Get model switching history"""
        return self.switch_history.copy()

    def can_switch_to(self, model_name: str) -> bool:
        """Check if switching to a model is possible"""
        return self.model_manager.get_model_info(model_name) is not None

    def get_model_suggestions(self, current_task: str) -> list[ModelInfo]:
        """Get model suggestions based on current task"""
        available_models = self.get_available_models()

        # Simple suggestion logic based on task content
        suggestions = []

        # For general chat tasks
        if any(
            keyword in current_task.lower()
            for keyword in ["chat", "talk", "conversation"]
        ):
            chat_models = [
                m for m in available_models if m.model_type == ModelType.CHAT
            ]
            suggestions.extend(chat_models[:3])

        # For completion tasks
        elif any(
            keyword in current_task.lower()
            for keyword in ["complete", "finish", "generate"]
        ):
            completion_models = [
                m for m in available_models if m.model_type == ModelType.COMPLETION
            ]
            suggestions.extend(completion_models[:3])

        # Default: suggest chat models
        if not suggestions:
            chat_models = [
                m for m in available_models if m.model_type == ModelType.CHAT
            ]
            suggestions.extend(chat_models[:3])

        return suggestions[:5]

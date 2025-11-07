"""
Model Registry for newP6 TUI

This module provides model registration and discovery functionality.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Types of models"""
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE = "image"
    AUDIO = "audio"


@dataclass
class ModelInfo:
    """Model information"""
    name: str
    model_type: ModelType
    provider: str
    description: str = ""
    max_tokens: Optional[int] = None
    context_length: Optional[int] = None
    cost_per_token: Optional[float] = None
    supported_features: List[str] = None

    def __post_init__(self):
        if self.supported_features is None:
            self.supported_features = []


class ModelRegistry:
    """Registry for available models"""

    def __init__(self):
        self.models: Dict[str, ModelInfo] = {}
        self._register_default_models()

    def _register_default_models(self) -> None:
        """Register default models"""
        # OpenAI models
        self.register_model(ModelInfo(
            name="gpt-4",
            model_type=ModelType.CHAT,
            provider="openai",
            description="GPT-4 model",
            max_tokens=8192,
            context_length=8192
        ))

        self.register_model(ModelInfo(
            name="gpt-3.5-turbo",
            model_type=ModelType.CHAT,
            provider="openai",
            description="GPT-3.5 Turbo model",
            max_tokens=4096,
            context_length=4096
        ))

        # Anthropic models
        self.register_model(ModelInfo(
            name="claude-3-opus",
            model_type=ModelType.CHAT,
            provider="anthropic",
            description="Claude 3 Opus model",
            max_tokens=4096,
            context_length=200000
        ))

        # Local models
        self.register_model(ModelInfo(
            name="llama-2-7b",
            model_type=ModelType.CHAT,
            provider="local",
            description="Llama 2 7B model",
            max_tokens=2048,
            context_length=4096
        ))

    def register_model(self, model: ModelInfo) -> None:
        """Register a new model"""
        self.models[model.name] = model
        logger.debug(f"Registered model: {model.name}")

    def get_model(self, name: str) -> Optional[ModelInfo]:
        """Get model by name"""
        return self.models.get(name)

    def list_models(self, provider: Optional[str] = None, model_type: Optional[ModelType] = None) -> List[ModelInfo]:
        """List models with optional filtering"""
        models = list(self.models.values())

        if provider:
            models = [m for m in models if m.provider == provider]

        if model_type:
            models = [m for m in models if m.model_type == model_type]

        return models

    def get_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(set(m.provider for m in self.models.values()))
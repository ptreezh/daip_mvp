"""
Model manager stub for backwards compatibility with CLI commands.
The actual model management is handled by LiteLLMProvider in model_provider/provider.py.
"""

from typing import Any


class ModelManager:
    """Stub model manager for Ollama CLI commands."""

    def __init__(self):
        pass

    def get_available_models(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        return []

    def get_current_model(self) -> dict[str, Any]:
        return {}

    def get_model_info(self, model_name: str) -> dict[str, Any]:
        return {}

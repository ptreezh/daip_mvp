"""
Core configuration package for DAIP Live
"""

from .local_models import get_local_model_config, get_safe_test_model, is_local_model

__all__ = ["get_local_model_config", "is_local_model", "get_safe_test_model"]

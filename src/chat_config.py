"""@Time    : 2025-07-19 01:00:00
@Author  : DAIP-LIVE Team
@File    : chat_config.py
@Description: Basic chat configuration for the DAIP-LIVE system.
"""

# Default chat model configuration
DEFAULT_CHAT_MODEL = "local"

# Basic chat model configurations
CHAT_MODEL_CONFIG = {
    "local": {
        "model_name": "llama3:instruct",
        "base_url": "http://localhost:11434",
        "api_type": "ollama",
        "temperature": 0.7,
        "max_tokens": 2048,
        "timeout": 30,
    }
}

def get_chat_model_config(model_type: str = None) -> dict:
    """Get the configuration for a specific chat model."""
    if model_type is None:
        model_type = DEFAULT_CHAT_MODEL
    return CHAT_MODEL_CONFIG.get(model_type, CHAT_MODEL_CONFIG[DEFAULT_CHAT_MODEL])

"""Chat System Configuration.

This module defines configurations for chat models, system behavior,
role recommendations, and other related settings.
"""

import os
from typing import Any

# 聊天模型配置
CHAT_MODEL_CONFIG = {
    # 本地模型配置
    "local": {
        "model_name": "gemma3:latest",
        "base_url": "http://localhost:11434",  # Ollama默认端口
        "api_type": "ollama",
        "temperature": 0.7,
        "max_tokens": 2048,
        "timeout": 30,
    },
    # 备用模型配置
    "openai": {
        "model_name": "gpt-3.5-turbo",
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "api_type": "openai",
        "temperature": 0.7,
        "max_tokens": 2048,
        "timeout": 30,
    },
    "claude": {
        "model_name": "claude-3-haiku-20240307",
        "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "api_type": "anthropic",
        "temperature": 0.7,
        "max_tokens": 2048,
        "timeout": 30,
    },
}

# 默认使用的聊天模型
DEFAULT_CHAT_MODEL = "local"

# 云端模型配置
CLOUD_MODEL_CONFIG = {
    "enabled": os.getenv("USE_CLOUD_MODELS", "false").lower() == "true",
    "fallback_enabled": os.getenv("CLOUD_FALLBACK", "true").lower() == "true",
    "preferred_provider": os.getenv("PREFERRED_CLOUD_PROVIDER", "openai"),
    "max_retries": int(os.getenv("CLOUD_MAX_RETRIES", "3")),
    "timeout": int(os.getenv("CLOUD_TIMEOUT", "30")),
    "auto_switch": True,  # 自动切换到可用模型
    "save_last_working": True,  # 保存上次工作的模型
}

# 聊天系统配置
CHAT_SYSTEM_CONFIG = {
    "max_history_length": 50,  # 最大聊天历史长度
    "max_concurrent_roles": 8,  # 最大并发角色数
    "role_response_timeout": 30,  # 角色响应超时时间（秒）
    "enable_role_memory": True,  # 是否启用角色记忆
    "enable_context_awareness": True,  # 是否启用上下文感知
    "auto_save_chat": True,  # 是否自动保存聊天记录
    "chat_save_interval": 10,  # 聊天保存间隔（消息数）
}

# 角色推荐配置
ROLE_RECOMMENDATION_CONFIG = {
    "recommendation_count": 6,  # 推荐角色数量
    "diversity_factor": 0.7,  # 多样性因子（0-1）
    "relevance_weight": 0.6,  # 相关性权重
    "popularity_weight": 0.3,  # 热门度权重
    "novelty_weight": 0.1,  # 新颖性权重
    "exclude_recent_roles": True,  # 是否排除最近使用的角色
    "recent_roles_window": 5,  # 最近角色窗口大小
}

# 向量化配置
VECTORIZATION_CONFIG = {
    "embedding_model": "nomic-embed-text",  # Ollama嵌入模型
    "api_type": "ollama",
    "base_url": "http://localhost:11434",
    "vector_dimension": 768,  # nomic-embed-text的向量维度
    "similarity_threshold": 0.7,
    "max_search_results": 20,
    "enable_semantic_search": True,
    "timeout": 30,
}

# 聊天室配置
CHATROOM_CONFIG = {
    "max_rooms": 10,  # 最大聊天室数量
    "max_participants_per_room": 12,  # 每个聊天室最大参与者数
    "room_idle_timeout": 3600,  # 聊天室空闲超时（秒）
    "enable_room_persistence": True,  # 是否持久化聊天室
    "enable_message_encryption": False,  # 是否启用消息加密
}

# 模型提示词模板
PROMPT_TEMPLATES = {
    "role_system_prompt": """你是 {role_name}，{role_description}

你的专业领域：{specialties}
你的核心技能：{skills}
你的工作经验：{experience_years}年
你的个人简介：{bio}

请始终保持你的角色特征，用你的专业知识和经验来回应对话。
回答要符合你的专业背景和个性特点。
如果问题超出你的专业范围，请诚实说明并尝试从你的角度提供见解。

当前对话上下文：
{context}

请用自然、专业且符合你角色特征的方式回应。""",
    "context_prompt": """以下是当前对话的上下文信息：

参与者：{participants}
讨论主题：{topic}
对话历史：
{chat_history}

请基于以上上下文，以你的角色身份参与对话。""",
    "recommendation_prompt": """基于以下信息推荐合适的专家角色：

讨论主题：{topic}
当前参与者：{current_participants}
期望的专业领域：{desired_expertise}
对话类型：{conversation_type}

请推荐最适合参与此对话的专家角色。""",
}


def get_chat_model_config(model_type: str = None) -> dict[str, Any]:
    """Get the configuration for a specific chat model.

    Args:
        model_type (str, optional): The type of the model (e.g., 'local', 'openai').
            If None, uses the DEFAULT_CHAT_MODEL. Defaults to None.

    Returns:
        dict[str, Any]: The configuration dictionary for the specified model.
    """
    if model_type is None:
        model_type = DEFAULT_CHAT_MODEL

    return CHAT_MODEL_CONFIG.get(model_type, CHAT_MODEL_CONFIG[DEFAULT_CHAT_MODEL])


def get_system_config() -> dict[str, Any]:
    """Get the general chat system configuration.

    Returns:
        dict[str, Any]: The chat system configuration dictionary.
    """
    return CHAT_SYSTEM_CONFIG


def get_recommendation_config() -> dict[str, Any]:
    """Get the role recommendation system configuration.

    Returns:
        dict[str, Any]: The role recommendation configuration dictionary.
    """
    return ROLE_RECOMMENDATION_CONFIG


def get_vectorization_config() -> dict[str, Any]:
    """Get the vectorization and embedding configuration.

    Returns:
        dict[str, Any]: The vectorization configuration dictionary.
    """
    return VECTORIZATION_CONFIG


def get_chatroom_config() -> dict[str, Any]:
    """Get the chatroom management configuration.

    Returns:
        dict[str, Any]: The chatroom configuration dictionary.
    """
    return CHATROOM_CONFIG


def get_prompt_template(template_name: str) -> str:
    """Get a specific prompt template by name.

    Args:
        template_name (str): The name of the template to retrieve.

    Returns:
        str: The prompt template string, or an empty string if not found.
    """
    return PROMPT_TEMPLATES.get(template_name, "")


def validate_model_availability(model_type: str = None) -> bool:
    """Validate if a given model type is available and configured correctly.

    Args:
        model_type (str, optional): The model type to validate.
            If None, uses the DEFAULT_CHAT_MODEL. Defaults to None.

    Returns:
        bool: True if the model is available, False otherwise.
    """
    if model_type is None:
        model_type = DEFAULT_CHAT_MODEL

    config = get_chat_model_config(model_type)

    if config["api_type"] == "ollama":
        try:
            import requests

            response = requests.get(f"{config['base_url']}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    elif config["api_type"] == "openai":
        return bool(config.get("api_key"))
    elif config["api_type"] == "anthropic":
        return bool(config.get("api_key"))

    return False


def get_available_models() -> list:
    """Get a list of all available and configured model types.

    Returns:
        list: A list of strings, where each string is an available model type.
    """
    available = []
    for model_type in CHAT_MODEL_CONFIG.keys():
        if validate_model_availability(model_type):
            available.append(model_type)
    return available


def get_cloud_model_config() -> dict[str, Any]:
    """Get the configuration for cloud-based models.

    Returns:
        dict[str, Any]: The cloud model configuration dictionary.
    """
    return CLOUD_MODEL_CONFIG


def is_cloud_models_enabled() -> bool:
    """Check if cloud-based models are enabled.

    Returns:
        bool: True if cloud models are enabled, False otherwise.
    """
    return CLOUD_MODEL_CONFIG["enabled"]


def is_cloud_fallback_enabled() -> bool:
    """Check if falling back to cloud models is enabled when local models fail.

    Returns:
        bool: True if cloud fallback is enabled, False otherwise.
    """
    return CLOUD_MODEL_CONFIG["fallback_enabled"]


def get_preferred_cloud_provider() -> str:
    """Get the preferred cloud provider (e.g., 'openai', 'anthropic')."""
    return CLOUD_MODEL_CONFIG["preferred_provider"]

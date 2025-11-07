"""
本地模型配置
为测试和开发提供本地模型支持，避免外部API依赖
"""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class LocalModelConfig:
    """本地模型配置"""
    model_name: str
    provider: str = "local"
    base_url: str = "http://localhost:8000"  # 本地模型服务地址
    api_key: str = "local-key"  # 本地API密钥
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

# 预定义的本地模型配置
LOCAL_MODEL_CONFIGS = {
    "test-model": LocalModelConfig(
        model_name="test-model",
        temperature=0.7,
        max_tokens=1000
    ),
    "mock-llm": LocalModelConfig(
        model_name="mock-llm",
        temperature=0.5,
        max_tokens=500
    ),
    "local-gpt": LocalModelConfig(
        model_name="local-gpt",
        temperature=0.8,
        max_tokens=2000
    )
}

def get_local_model_config(model_name: str = "test-model") -> LocalModelConfig:
    """获取本地模型配置"""
    return LOCAL_MODEL_CONFIGS.get(model_name, LOCAL_MODEL_CONFIGS["test-model"])

def is_local_model(model_name: str) -> bool:
    """检查是否为本地模型"""
    return model_name in LOCAL_MODEL_CONFIGS or model_name.startswith("test-") or model_name.startswith("mock-")

def get_safe_test_model() -> str:
    """获取安全的测试模型名称"""
    return "test-model"
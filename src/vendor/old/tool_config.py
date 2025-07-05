"""统一的工具配置管理
整合所有工具相关的配置项
"""

import os
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolExecutionConfig:
    """工具执行配置"""

    default_timeout: float = 30.0
    max_retry_count: int = 3
    retry_delay: float = 1.0
    enable_auto_retry: bool = True
    max_history_size: int = 1000


@dataclass
class ToolCallingConfig:
    """工具调用配置"""

    confidence_threshold: float = 0.3
    max_tools_per_call: int = 5
    tool_search_k: int = 5
    enable_tool_chaining: bool = True
    fallback_to_general_model: bool = True


@dataclass
class ModelConfig:
    """模型配置"""

    function_calling_model: str = (
        "atlas/intersync-gemma-7b-instruct-function-calling:latest"
    )
    default_model: str = "qwen3:8b"
    temperature: float = 0.7
    max_tokens: int = 4096


class ToolConfig:
    """统一的工具配置管理器"""

    def __init__(self):
        self.execution = ToolExecutionConfig()
        self.calling = ToolCallingConfig()
        self.model = ModelConfig()
        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载配置"""
        # 执行配置
        self.execution.default_timeout = float(os.getenv("TOOL_TIMEOUT", "30.0"))
        self.execution.max_retry_count = int(os.getenv("TOOL_MAX_RETRY", "3"))
        self.execution.retry_delay = float(os.getenv("TOOL_RETRY_DELAY", "1.0"))
        self.execution.enable_auto_retry = (
            os.getenv("TOOL_AUTO_RETRY", "true").lower() == "true"
        )

        # 调用配置
        self.calling.confidence_threshold = float(
            os.getenv("TOOL_CONFIDENCE_THRESHOLD", "0.3"),
        )
        self.calling.max_tools_per_call = int(os.getenv("TOOL_MAX_TOOLS", "5"))
        self.calling.tool_search_k = int(os.getenv("TOOL_SEARCH_K", "5"))
        self.calling.enable_tool_chaining = (
            os.getenv("TOOL_CHAINING", "true").lower() == "true"
        )

        # 模型配置
        self.model.function_calling_model = os.getenv(
            "FUNCTION_CALLING_MODEL",
            self.model.function_calling_model,
        )
        self.model.default_model = os.getenv("DEFAULT_MODEL", self.model.default_model)
        self.model.temperature = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
        self.model.max_tokens = int(os.getenv("MODEL_MAX_TOKENS", "4096"))

    def get_execution_config(self) -> dict[str, Any]:
        """获取执行配置"""
        return {
            "default_timeout": self.execution.default_timeout,
            "max_retry_count": self.execution.max_retry_count,
            "retry_delay": self.execution.retry_delay,
            "enable_auto_retry": self.execution.enable_auto_retry,
            "max_history_size": self.execution.max_history_size,
        }

    def get_calling_config(self) -> dict[str, Any]:
        """获取调用配置"""
        return {
            "confidence_threshold": self.calling.confidence_threshold,
            "max_tools_per_call": self.calling.max_tools_per_call,
            "tool_search_k": self.calling.tool_search_k,
            "enable_tool_chaining": self.calling.enable_tool_chaining,
            "fallback_to_general_model": self.calling.fallback_to_general_model,
        }

    def get_model_config(self) -> dict[str, Any]:
        """获取模型配置"""
        return {
            "function_calling_model": self.model.function_calling_model,
            "default_model": self.model.default_model,
            "temperature": self.model.temperature,
            "max_tokens": self.model.max_tokens,
        }

    def update_config(self, config_type: str, updates: dict[str, Any]):
        """更新配置"""
        if config_type == "execution":
            for key, value in updates.items():
                if hasattr(self.execution, key):
                    setattr(self.execution, key, value)
        elif config_type == "calling":
            for key, value in updates.items():
                if hasattr(self.calling, key):
                    setattr(self.calling, key, value)
        elif config_type == "model":
            for key, value in updates.items():
                if hasattr(self.model, key):
                    setattr(self.model, key, value)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "execution": self.get_execution_config(),
            "calling": self.get_calling_config(),
            "model": self.get_model_config(),
        }


# 全局配置实例
tool_config = ToolConfig()

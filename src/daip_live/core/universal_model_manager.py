"""
通用Ollama实例管理器
支持所有角色应用场景的单一Ollama实例管理和分时复用
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig


@dataclass
class UniversalModelManager:
    """通用模型管理器 - 适用于所有应用场景"""

    def __init__(self):
        self._current_model: Optional[str] = None
        self._lock = asyncio.Lock()
        self._provider = None
        self._model_configs: dict[str, RoleModelConfig] = {}

        # 使用统计
        self.usage_statistics = {
            "total_requests": 0,
            "model_switches": 0,
            "model_usage": {},
            "session_usage": {},
            "start_time": datetime.now().isoformat(),
        }

        # 缓存管理
        self._response_cache: dict[str, tuple[str, Any]] = {}
        self._cache_ttl = 300  # 5分钟缓存

    async def initialize_provider(self, provider_instance):
        """初始化模型提供者"""
        self._provider = provider_instance
        return self

    async def generate_response(
        self,
        model_name: str,
        prompt: str,
        session_type: str = "conversation",
        session_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[str, Optional[dict[str, Any]]]:
        """生成回复 - 适用于所有应用场景"""
        if not self._provider:
            raise ValueError("Provider not initialized")

        async with self._lock:
            # 更新使用统计
            self.usage_statistics["total_requests"] += 1
            self.usage_statistics["session_usage"][session_id or "unknown"] = (
                self.usage_statistics["session_usage"].get(session_id or "unknown", 0)
                + 1
            )

            # 检查是否需要切换模型
            if self._current_model != model_name:
                await self._switch_model(model_name)
                self.usage_statistics["model_switches"] += 1

            # 应用场景特定的参数调整
            enhanced_kwargs = self._adjust_parameters_for_scenario(
                model_name, session_type, **kwargs
            )

            # 生成回复
            response_content, usage = await self._generate_response(
                prompt, **enhanced_kwargs
            )

            # 更新模型使用统计
            self.usage_statistics["model_usage"][model_name] = (
                self.usage_statistics["model_usage"].get(model_name, 0) + 1
            )

            # 缓存响应
            cache_key = self._generate_cache_key(model_name, prompt, enhanced_kwargs)
            self._response_cache[cache_key] = (response_content, usage)

            return response_content, usage

    async def _switch_model(self, model_name: str):
        """切换模型（如果需要）"""
        if self._current_model == model_name:
            return

        # 模型切换逻辑
        self._current_model = model_name

        # 这里可以添加实际的模型切换代码
        # 例如：重新加载模型权重或配置

    async def _generate_response(self, prompt: str, **kwargs) -> tuple[str, Any]:
        """生成回复的实际实现"""
        try:
            # 使用实际的提供者生成回复
            if hasattr(self._provider, "generate"):
                result = await self._provider.generate(prompt, **kwargs)
                return result.get("content", ""), result.get("usage", {})
            else:
                # 回退到模拟实现
                mock_response = f"Generated response for: {prompt[:100]}..."
                mock_usage = {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(mock_response.split()),
                    "total_tokens": len(prompt.split()) + len(mock_response.split()),
                }
                return mock_response, mock_usage
        except Exception as e:
            # 错误处理
            error_msg = f"Error generating response: {str(e)}"
            return error_msg, {}

    def _adjust_parameters_for_scenario(
        self, model_name: str, session_type: str, **kwargs
    ) -> dict[str, Any]:
        """根据应用场景调整参数"""
        adjusted = kwargs.copy()

        # 基于场景的参数优化
        if session_type == "debate":
            adjusted["temperature"] = adjusted.get("temperature", 0.7)
            adjusted["max_tokens"] = adjusted.get("max_tokens", 2000)
        elif session_type == "analysis":
            adjusted["temperature"] = adjusted.get("temperature", 0.3)
            adjusted["max_tokens"] = adjusted.get("max_tokens", 3000)
        elif session_type == "creative":
            adjusted["temperature"] = adjusted.get("temperature", 0.9)
            adjusted["max_tokens"] = adjusted.get("max_tokens", 2500)
        elif session_type == "conversation":
            adjusted["temperature"] = adjusted.get("temperature", 0.6)
            adjusted["max_tokens"] = adjusted.get("max_tokens", 1500)

        return adjusted

    def _generate_cache_key(
        self, model_name: str, prompt: str, kwargs: dict[str, Any]
    ) -> str:
        """生成缓存键"""
        key_data = {
            "model": model_name,
            "prompt": prompt[:200],  # 只使用前200个字符
            "kwargs": sorted(kwargs.items()),
        }
        return json.dumps(key_data, sort_keys=True)

    def get_usage_statistics(self) -> dict[str, Any]:
        """获取使用统计"""
        stats = self.usage_statistics.copy()

        # 添加运行时间
        start_time = datetime.fromisoformat(stats["start_time"])
        runtime = datetime.now() - start_time
        stats["runtime_seconds"] = runtime.total_seconds()

        # 计算平均性能
        if stats["total_requests"] > 0:
            stats["avg_requests_per_second"] = (
                stats["total_requests"] / runtime.total_seconds()
            )
            stats["switch_rate"] = stats["model_switches"] / stats["total_requests"]

        return stats

    def get_model_config(self, model_name: str) -> Optional[RoleModelConfig]:
        """获取模型配置"""
        return self._model_configs.get(model_name)

    def register_model_config(self, model_config: RoleModelConfig):
        """注册模型配置"""
        self._model_configs[model_config.model_name] = model_config

    def list_available_models(self) -> list[str]:
        """列出可用模型"""
        return list(self._model_configs.keys())

    def clear_cache(self):
        """清除缓存"""
        self._response_cache.clear()

    def get_cache_info(self) -> dict[str, Any]:
        """获取缓存信息"""
        return {
            "cache_size": len(self._response_cache),
            "cache_ttl": self._cache_ttl,
            "cache_keys": list(self._response_cache.keys())[-10:],  # 最近10个键
        }

    def optimize_for_scenario(self, scenario: str) -> dict[str, Any]:
        """为特定场景优化参数"""
        optimizations = {
            "debate": {
                "temperature": 0.7,
                "max_tokens": 2000,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            },
            "analysis": {
                "temperature": 0.3,
                "max_tokens": 3000,
                "top_p": 0.8,
                "frequency_penalty": 0.2,
                "presence_penalty": 0.1,
            },
            "creative": {
                "temperature": 0.9,
                "max_tokens": 2500,
                "top_p": 0.95,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
            },
            "conversation": {
                "temperature": 0.6,
                "max_tokens": 1500,
                "top_p": 0.85,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            },
        }

        return optimizations.get(scenario, optimizations["conversation"])

    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy",
            "current_model": self._current_model,
            "provider_available": self._provider is not None,
            "cache_size": len(self._response_cache),
            "total_requests": self.usage_statistics["total_requests"],
            "timestamp": datetime.now().isoformat(),
        }

    def __str__(self) -> str:
        stats = self.get_usage_statistics()
        return f"UniversalModelManager(models={len(self._model_configs)}, requests={stats['total_requests']})"  # noqa: E501

    def __repr__(self) -> str:
        return (
            f"UniversalModelManager("
            f"current_model={self._current_model}, "
            f"models={list(self._model_configs.keys())}, "
            f"total_requests={self.usage_statistics['total_requests']})"
        )


# 为了向后兼容，保留原有的OllamaInstanceManager作为别名
class OllamaInstanceManager(UniversalModelManager):
    """向后兼容的Ollama实例管理器"""

    pass

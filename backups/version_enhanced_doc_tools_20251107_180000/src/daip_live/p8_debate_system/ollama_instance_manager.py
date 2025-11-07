"""
Ollama实例管理器
实现单一Ollama实例的分时复用，避免资源竞争
"""

import asyncio
from typing import Tuple, Any, Optional
from daip_live.core.exceptions import ModelError


class OllamaInstanceManager:
    """Ollama实例管理器 - 确保分时复用"""

    def __init__(self):
        self._current_model: Optional[str] = None
        self._lock = asyncio.Lock()
        self._provider = None  # 单一Provider实例
        self._model_configs = {}  # 模型配置缓存

    async def generate_with_model(self, model_name: str, prompt: str, **kwargs) -> Tuple[str, Any]:
        """分时复用单一Ollama实例生成回复"""
        async with self._lock:
            # 模型切换（如果需要）
            await self._switch_model(model_name)

            # 生成回复
            return await self._generate(prompt, **kwargs)

    async def _switch_model(self, model_name: str):
        """切换当前模型"""
        # 只有在模型不同时才切换
        if self._current_model == model_name:
            return

        # 这里实现实际的模型切换逻辑
        # 在实际实现中，这可能需要重新配置Ollama实例
        self._current_model = model_name

        # 可以添加模型特定的配置加载
        if model_name not in self._model_configs:
            self._model_configs[model_name] = self._load_model_config(model_name)

    async def _generate(self, prompt: str, **kwargs) -> Tuple[str, Any]:
        """使用当前模型生成回复"""
        if self._current_model is None:
            raise ModelError("No model is currently selected")

        # 这里应该调用实际的Ollama实例
        # 当前使用模拟实现
        await asyncio.sleep(0.01)  # 模拟网络延迟

        # 模拟响应
        response = f"Response from {self._current_model}"
        usage = {"total_tokens": len(prompt.split()) * 2}  # 简单的token估算

        return response, usage

    def _load_model_config(self, model_name: str) -> dict:
        """加载模型配置"""
        # 这里可以加载模型特定的配置
        return {
            "model_name": model_name,
            "temperature": 0.7,
            "max_tokens": 4000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }

    def get_current_model(self) -> Optional[str]:
        """获取当前模型"""
        return self._current_model

    def get_model_config(self, model_name: str) -> Optional[dict]:
        """获取模型配置"""
        return self._model_configs.get(model_name)

    def clear_cache(self):
        """清除模型配置缓存"""
        self._model_configs.clear()

    async def health_check(self) -> bool:
        """健康检查"""
        async with self._lock:
            try:
                # 简单的健康检查
                if self._current_model:
                    await self._generate("Health check")
                    return True
                return False
            except Exception:
                return False

    def get_statistics(self) -> dict:
        """获取使用统计"""
        return {
            "current_model": self._current_model,
            "cached_models": len(self._model_configs),
            "lock_status": "locked" if self._lock.locked() else "unlocked"
        }
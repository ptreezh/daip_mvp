"""
Ollama实例管理器
实现单一Ollama实例的分时复用，避免资源竞争
"""

import asyncio
from typing import Tuple, Any, Optional
from daip_live.core.exceptions import ModelError


class OllamaInstanceManager:
    """Ollama实例管理器 - 确保分时复用"""

    def __init__(self, shared_provider=None):
        self._current_model: Optional[str] = None
        self._lock = asyncio.Lock()
        self._provider = shared_provider  # 共享的Provider实例
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
        old_model = self._current_model

        # 只有在模型不同时才切换
        if self._current_model != model_name:
            # 这里实现实际的模型切换逻辑
            # 在实际实现中，这可能需要重新配置Ollama实例
            self._current_model = model_name

            # 可以添加模型特定的配置加载
            if model_name not in self._model_configs:
                self._model_configs[model_name] = self._load_model_config(model_name)

            print(f"🔄 模型已从 '{old_model}' 切换至 '{model_name}'")
        else:
            print(f"🔄 模型保持为 '{model_name}'，无需切换")

    async def _generate(self, prompt: str, **kwargs) -> Tuple[str, Any]:
        """使用当前模型生成回复"""
        if self._current_model is None:
            raise ModelError("No model is currently selected")

        # 初始化或获取模型提供者
        if self._provider is None:
            from daip_live.model_provider.provider import LiteLLMProvider
            from daip_live.core.models import ProviderConfig
            # 创建Ollama配置的LiteLLMProvider
            config = ProviderConfig(
                model=self._current_model,
                base_url="http://localhost:11434"  # Ollama默认端口
            )
            self._provider = LiteLLMProvider(config)

        # 为Ollama模型调用实际的模型提供者
        try:
            # 确保模型名称以"ollama/"开头，否则添加前缀
            model_name = self._current_model
            if not model_name.startswith("ollama/"):
                if model_name.startswith("ollama:"):  # 如果是 ollama:llama3:instruct 格式
                    model_name = "ollama/" + model_name[7:]  # 替换为 ollama/llama3:instruct
                else:
                    model_name = f"ollama/{model_name}"

            # 过滤掉Ollama不支持的参数
            filtered_kwargs = {}
            for key, value in kwargs.items():
                if key in ['frequency_penalty', 'presence_penalty'] and model_name.startswith("ollama/"):
                    # Ollama不支持这些参数
                    continue
                else:
                    filtered_kwargs[key] = value

            # 生成响应
            response, usage = await self._provider.generate(
                prompt=prompt,
                model=model_name,
                **filtered_kwargs
            )

            return response, usage
        except Exception as e:
            # 捕获并处理特定的Ollama相关异常，提供更友好的错误信息
            error_msg = str(e)
            model_name = getattr(self, '_current_model', 'unknown')

            # 检查是否为Ollama连接相关错误
            if "OllamaException" in error_msg or "ConnectionError" in error_msg or "connect to Ollama" in error_msg:
                raise ModelError(f"无法连接到Ollama服务。请确认Ollama服务正在运行，模型'{model_name}'已安装并可访问。")
            elif "not found" in error_msg.lower() or "model" in error_msg.lower() and "not" in error_msg.lower():
                raise ModelError(f"模型'{model_name}'未找到。请确认模型已正确下载到Ollama。")
            elif "Connection refused" in error_msg:
                raise ModelError(f"无法连接到Ollama服务。请确认Ollama服务在端口11434上运行。")
            else:
                # 其他未处理的异常
                raise ModelError(f"调用模型'{model_name}'时发生错误: {str(e)}")

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
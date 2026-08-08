"""
模型可用性检查器
用于在系统运行前检查模型是否可用，提供友好的错误提示
"""

import asyncio
from typing import List, Optional
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.models import ProviderConfig
from daip_live.core.exceptions import ModelError


class ModelAvailabilityChecker:
    """模型可用性检查器"""
    
    def __init__(self, default_model: str = "ollama/llama3", embedding_model: str = "ollama/nomic-embed-text"):
        self.default_model = default_model
        self.embedding_model = embedding_model
        self._provider_cache = {}
    
    def _get_provider(self, model_name: str):
        """获取指定模型的提供者实例"""
        if model_name not in self._provider_cache:
            config = ProviderConfig(model=model_name, base_url="http://localhost:11434")
            self._provider_cache[model_name] = LiteLLMProvider(config)
        return self._provider_cache[model_name]
    
    async def check_model_availability(self, model_name: str, test_prompt: str = "Hello") -> tuple[bool, str]:
        """
        检查特定模型是否可用
        
        Args:
            model_name: 模型名称
            test_prompt: 测试提示词
            
        Returns:
            tuple: (是否可用, 错误信息或空字符串)
        """
        try:
            provider = self._get_provider(model_name)
            # 尝试生成一个简单的响应来测试模型可用性
            # LiteLLMProvider.generate 是 async generator（模型名由 ProviderConfig 持有），
            # 参数需放入 params dict；成功产出首个响应块即认为模型可用
            async for chunk in provider.generate(
                prompt=test_prompt,
                params={"temperature": 0.1, "max_tokens": 20}
            ):
                break
            return True, ""
        except Exception as e:
            error_msg = str(e)
            if "OllamaException" in error_msg or "ConnectionError" in error_msg:
                return False, "无法连接到模型服务。请确认Ollama服务正在运行且模型已安装。"
            elif "not found" in error_msg.lower() or "model" in error_msg.lower() and "not" in error_msg.lower():
                return False, f"模型'{model_name}'未找到。请确认模型已正确下载到Ollama。"
            elif "Connection refused" in error_msg:
                return False, f"无法连接到Ollama服务。请确认Ollama服务在端口11434上运行。"
            else:
                return False, f"模型'{model_name}'不可用: {error_msg}"
    
    async def check_all_models(self) -> tuple[bool, List[str]]:
        """
        检查所有必需模型是否可用
        
        Returns:
            tuple: (是否全部可用, 不可用模型的错误信息列表)
        """
        models_to_check = [self.default_model, self.embedding_model]
        unavailable_models = []
        
        for model_name in models_to_check:
            is_available, error_msg = await self.check_model_availability(model_name)
            if not is_available:
                unavailable_models.append(f"{model_name}: {error_msg}")
        
        return len(unavailable_models) == 0, unavailable_models
    
    async def get_available_models(self) -> List[str]:
        """
        获取当前可用的模型列表
        
        Returns:
            List[str]: 可用模型列表
        """
        # 尝试获取Ollama的模型列表
        try:
            provider = self._get_provider("ollama/llama3")  # 使用一个默认模型获取提供者
            available_models = provider._get_available_ollama_models()
            return available_models
        except Exception:
            # 如果无法获取完整的模型列表，返回一个基本的检查结果
            return []
    
    async def pre_flight_check(self) -> tuple[bool, str]:
        """
        执行预运行检查，确保所有必需模型都可用
        
        Returns:
            tuple: (是否通过检查, 检查结果信息)
        """
        is_all_available, unavailable_models = await self.check_all_models()
        
        if is_all_available:
            return True, "所有必需模型均可用。"
        else:
            unavailable_str = "; ".join(unavailable_models)
            return False, f"以下模型不可用: {unavailable_str}。请检查Ollama服务状态和模型安装。"


# 全局实例
model_checker = ModelAvailabilityChecker()


async def perform_model_check() -> tuple[bool, str]:
    """
    执行模型可用性检查的便捷函数
    """
    return await model_checker.pre_flight_check()


if __name__ == "__main__":
    # 用于测试的简单运行示例
    async def test():
        is_ok, message = await perform_model_check()
        print(f"模型检查结果: {is_ok}, {message}")
        if not is_ok:
            print("建议操作：")
            print("1. 确认Ollama服务正在运行: ollama serve")
            print("2. 检查模型是否已下载: ollama list")
            print("3. 如未下载，请运行: ollama pull llama3")
    
    asyncio.run(test())
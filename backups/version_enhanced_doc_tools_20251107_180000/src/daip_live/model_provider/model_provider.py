"""Model provider interface following SOLID principles."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
import asyncio
import logging

from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig
from daip_live.core.models import ProviderConfig

logger = logging.getLogger(__name__)


class ModelProvider(ABC):
    """抽象模型提供者基类，遵循单一职责原则"""
    
    @abstractmethod
    async def generate_async(
        self, 
        prompt: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        异步生成响应
        
        Args:
            prompt: 输入提示
            **kwargs: 模型特定参数
            
        Returns:
            包含内容和使用统计的字典
        """
        pass
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        同步生成响应
        
        Args:
            prompt: 输入提示
            **kwargs: 模型特定参数
            
        Returns:
            包含内容和使用统计的字典
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        pass


class BaseLocalModelProvider(ModelProvider):
    """基础本地模型提供者实现"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.model_name = config.model
        self.embedding_model = config.embedding_model
        self._is_initialized = False
    
    async def initialize(self):
        """初始化模型提供者"""
        # 模拟初始化过程
        await asyncio.sleep(0.1)
        self._is_initialized = True
        logger.info(f"Initialized local model provider for {self.model_name}")
    
    async def generate_async(
        self, 
        prompt: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """异步生成响应"""
        if not self._is_initialized:
            await self.initialize()
        
        # 模拟模型生成过程
        await asyncio.sleep(0.01)
        
        # 合并配置参数和传入参数
        generation_params = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": self.config.max_tokens or kwargs.get("max_tokens", 4000),
            "temperature": self.config.temperature or kwargs.get("temperature", 0.7),
        }
        
        # 添加传入的额外参数
        generation_params.update(kwargs)
        
        # 模拟生成结果
        response_content = f"Generated response for: {prompt[:100]}..."
        usage_stats = {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(response_content.split()),
            "total_tokens": len(prompt.split()) + len(response_content.split())
        }
        
        return {
            "content": response_content,
            "usage": usage_stats,
            "model": self.model_name,
            "parameters": generation_params
        }
    
    def generate(
        self, 
        prompt: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """同步生成响应"""
        # 在同步方法中调用异步方法
        return asyncio.run(self.generate_async(prompt, **kwargs))
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "embedding_model": self.embedding_model,
            "provider_type": "local",
            "initialized": self._is_initialized,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }


class EnhancedModelProvider(ModelProvider):
    """增强模型提供者，支持角色特定配置"""
    
    def __init__(self, role_model_config: RoleModelConfig):
        self.role_config = role_model_config
        self.model_name = role_model_config.model_name
        self.provider = role_model_config.provider
        self._is_initialized = False
    
    async def initialize(self):
        """初始化增强模型提供者"""
        # 模拟初始化过程
        await asyncio.sleep(0.1)
        self._is_initialized = True
        logger.info(f"Initialized enhanced model provider for {self.model_name} ({self.provider})")
    
    async def generate_async(
        self, 
        prompt: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """异步生成响应"""
        if not self._is_initialized:
            await self.initialize()
        
        # 模拟模型生成过程
        await asyncio.sleep(0.01)
        
        # 合并角色配置参数和传入参数
        generation_params = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": self.role_config.max_tokens,
            "temperature": self.role_config.temperature,
            "top_p": self.role_config.top_p,
            "frequency_penalty": self.role_config.frequency_penalty,
            "presence_penalty": self.role_config.presence_penalty,
        }
        
        # 添加传入的额外参数（优先级更高）
        generation_params.update(kwargs)
        
        # 模拟生成结果
        response_content = f"Enhanced response for: {prompt[:100]}..."
        usage_stats = {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(response_content.split()),
            "total_tokens": len(prompt.split()) + len(response_content.split())
        }
        
        return {
            "content": response_content,
            "usage": usage_stats,
            "model": self.model_name,
            "provider": self.provider,
            "parameters": generation_params
        }
    
    def generate(
        self, 
        prompt: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """同步生成响应"""
        # 在同步方法中调用异步方法
        return asyncio.run(self.generate_async(prompt, **kwargs))
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "provider": self.provider,
            "role_config": self.role_config.model_dump(),
            "initialized": self._is_initialized,
            "parameters": {
                "max_tokens": self.role_config.max_tokens,
                "temperature": self.role_config.temperature,
                "top_p": self.role_config.top_p,
                "frequency_penalty": self.role_config.frequency_penalty,
                "presence_penalty": self.role_config.presence_penalty,
            }
        }


class ModelProviderFactory:
    """模型提供者工厂，遵循开闭原则"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class):
        """注册模型提供者"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, config: ProviderConfig) -> ModelProvider:
        """创建基础模型提供者"""
        # 根据配置选择合适的提供者实现
        if config.base_url and "openai" in config.base_url:
            # 这里可以返回OpenAI提供者实现
            return BaseLocalModelProvider(config)
        elif config.base_url and "anthropic" in config.base_url:
            # 这里可以返回Anthropic提供者实现
            return BaseLocalModelProvider(config)
        else:
            # 默认返回基础本地提供者
            return BaseLocalModelProvider(config)
    
    @classmethod
    def create_enhanced_provider(cls, role_config: RoleModelConfig) -> EnhancedModelProvider:
        """创建增强模型提供者"""
        return EnhancedModelProvider(role_config)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的提供者列表"""
        return list(cls._providers.keys())


# 预注册一些常见的提供者
ModelProviderFactory.register_provider("local", BaseLocalModelProvider)
ModelProviderFactory.register_provider("enhanced", EnhancedModelProvider)
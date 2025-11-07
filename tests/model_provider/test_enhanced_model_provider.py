"""Enhanced tests for model provider interface."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from daip_live.model_provider.model_provider import (
    ModelProvider, 
    BaseLocalModelProvider, 
    EnhancedModelProvider, 
    ModelProviderFactory
)
from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig
from daip_live.core.models import ProviderConfig


class TestModelProviderInterfaceCompliance:
    """测试模型提供者接口的合规性"""

    def test_base_model_provider_implements_interface(self):
        """测试基础模型提供者实现接口"""
        config = ProviderConfig(
            model="test-model",
            embedding_model="text-embedding-ada-002"
        )
        
        provider = BaseLocalModelProvider(config)
        
        # 验证实现了ModelProvider接口
        assert isinstance(provider, ModelProvider)
        assert hasattr(provider, "generate_async")
        assert hasattr(provider, "generate")
        assert hasattr(provider, "get_model_info")
        
        # 验证方法是可调用的
        assert callable(provider.generate_async)
        assert callable(provider.generate)
        assert callable(provider.get_model_info)

    def test_enhanced_model_provider_implements_interface(self):
        """测试增强模型提供者实现接口"""
        config = RoleModelConfig(
            model_name="test-model",
            provider="local",
            max_tokens=4000,
            temperature=0.7
        )
        
        provider = EnhancedModelProvider(config)
        
        # 验证实现了ModelProvider接口
        assert isinstance(provider, ModelProvider)
        assert hasattr(provider, "generate_async")
        assert hasattr(provider, "generate")
        assert hasattr(provider, "get_model_info")
        
        # 验证方法是可调用的
        assert callable(provider.generate_async)
        assert callable(provider.generate)
        assert callable(provider.get_model_info)


class TestModelProviderFunctionality:
    """测试模型提供者的功能"""

    @pytest.mark.asyncio
    async def test_base_model_provider_async_generation(self):
        """测试基础模型提供者的异步生成"""
        config = ProviderConfig(
            model="test-model",
            embedding_model="text-embedding-ada-002",
            max_tokens=4000,
            temperature=0.7
        )
        
        provider = BaseLocalModelProvider(config)
        
        # 测试异步生成
        result = await provider.generate_async("Test prompt")
        
        # 验证返回值结构
        assert "content" in result
        assert "usage" in result
        assert "model" in result
        assert "parameters" in result
        
        # 验证内容
        assert "Test prompt" in result["content"]
        assert result["model"] == "test-model"
        
        # 验证使用统计
        assert "prompt_tokens" in result["usage"]
        assert "completion_tokens" in result["usage"]
        assert "total_tokens" in result["usage"]
        
        # 验证参数
        assert result["parameters"]["model"] == "test-model"
        assert result["parameters"]["max_tokens"] == 4000
        assert result["parameters"]["temperature"] == 0.7

    def test_base_model_provider_sync_generation(self):
        """测试基础模型提供者的同步生成"""
        config = ProviderConfig(
            model="test-model",
            embedding_model="text-embedding-ada-002",
            max_tokens=4000,
            temperature=0.7
        )
        
        provider = BaseLocalModelProvider(config)
        
        # 测试同步生成
        result = provider.generate("Test prompt")
        
        # 验证返回值结构
        assert "content" in result
        assert "usage" in result
        assert "model" in result
        assert "parameters" in result
        
        # 验证内容
        assert "Test prompt" in result["content"]
        assert result["model"] == "test-model"

    @pytest.mark.asyncio
    async def test_enhanced_model_provider_async_generation(self):
        """测试增强模型提供者的异步生成"""
        config = RoleModelConfig(
            model_name="test-model",
            provider="local",
            max_tokens=4000,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1
        )
        
        provider = EnhancedModelProvider(config)
        
        # 测试异步生成
        result = await provider.generate_async("Test prompt")
        
        # 验证返回值结构
        assert "content" in result
        assert "usage" in result
        assert "model" in result
        assert "provider" in result
        assert "parameters" in result
        
        # 验证内容
        assert "Test prompt" in result["content"]
        assert result["model"] == "test-model"
        assert result["provider"] == "local"
        
        # 验证参数
        assert result["parameters"]["max_tokens"] == 4000
        assert result["parameters"]["temperature"] == 0.7
        assert result["parameters"]["top_p"] == 0.9
        assert result["parameters"]["frequency_penalty"] == 0.1
        assert result["parameters"]["presence_penalty"] == 0.1

    def test_model_provider_info_retrieval(self):
        """测试模型提供者信息获取"""
        # 测试基础提供者
        base_config = ProviderConfig(
            model="test-model",
            embedding_model="text-embedding-ada-002"
        )
        base_provider = BaseLocalModelProvider(base_config)
        base_info = base_provider.get_model_info()
        
        assert base_info["model_name"] == "test-model"
        assert base_info["embedding_model"] == "text-embedding-ada-002"
        assert base_info["provider_type"] == "local"
        
        # 测试增强提供者
        enhanced_config = RoleModelConfig(
            model_name="test-model",
            provider="local",
            max_tokens=4000,
            temperature=0.7
        )
        enhanced_provider = EnhancedModelProvider(enhanced_config)
        enhanced_info = enhanced_provider.get_model_info()
        
        assert enhanced_info["model_name"] == "test-model"
        assert enhanced_info["provider"] == "local"
        assert "parameters" in enhanced_info


class TestModelProviderFactory:
    """测试模型提供者工厂"""

    def test_factory_creates_base_provider(self):
        """测试工厂创建基础提供者"""
        config = ProviderConfig(
            model="test-model",
            embedding_model="text-embedding-ada-002"
        )
        
        provider = ModelProviderFactory.create_provider(config)
        
        assert isinstance(provider, BaseLocalModelProvider)
        assert provider.config.model == "test-model"
        assert provider.config.embedding_model == "text-embedding-ada-002"

    def test_factory_creates_enhanced_provider(self):
        """测试工厂创建增强提供者"""
        config = RoleModelConfig(
            model_name="test-model",
            provider="local",
            max_tokens=4000,
            temperature=0.7
        )
        
        provider = ModelProviderFactory.create_enhanced_provider(config)
        
        assert isinstance(provider, EnhancedModelProvider)
        assert provider.role_config.model_name == "test-model"
        assert provider.role_config.provider == "local"

    def test_factory_registration(self):
        """测试工厂注册功能"""
        # 测试初始提供者
        initial_providers = ModelProviderFactory.get_available_providers()
        assert "local" in initial_providers
        assert "enhanced" in initial_providers
        
        # 注册新提供者
        class CustomProvider:
            pass
        
        ModelProviderFactory.register_provider("custom", CustomProvider)
        
        # 验证新提供者已注册
        updated_providers = ModelProviderFactory.get_available_providers()
        assert "custom" in updated_providers
        assert len(updated_providers) > len(initial_providers)
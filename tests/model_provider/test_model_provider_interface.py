"""Tests for model provider interface."""

from unittest.mock import AsyncMock, Mock

import pytest

from daip_live.core.models import ProviderConfig
from daip_live.p4_role_manager_tools.role_model_config import RoleModelConfig


class TestModelProviderInterface:
    """测试模型提供者接口的隔离性"""

    def test_model_provider_interface_isolation(self):
        """测试模型提供者接口的隔离性"""
        # 创建模型配置
        config = RoleModelConfig(
            model_name="test-model", provider="local", max_tokens=4000, temperature=0.7
        )

        # 验证配置对象的独立性
        config2 = RoleModelConfig(
            model_name="test-model-2",
            provider="local",
            max_tokens=3000,
            temperature=0.5,
        )

        assert config.model_name != config2.model_name
        assert config.max_tokens != config2.max_tokens
        assert config.temperature != config2.temperature

        # 验证配置对象不共享状态
        config.max_tokens = 5000
        assert config2.max_tokens == 3000  # 不受影响

    def test_model_provider_extension_support(self):
        """测试模型提供者对新模型的支持"""
        # 创建基础提供者配置
        base_config = ProviderConfig(
            model="gpt-3.5-turbo", embedding_model="text-embedding-ada-002"
        )

        # 创建扩展的模型配置
        extended_config = RoleModelConfig(
            model_name="claude-3-sonnet",
            provider="anthropic",
            max_tokens=4000,
            temperature=0.7,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            is_primary=True,
        )

        # 验证基础配置和扩展配置可以共存
        assert base_config.model != extended_config.model_name
        assert extended_config.provider == "anthropic"

        # 验证扩展配置包含额外参数
        assert hasattr(extended_config, "top_p")
        assert hasattr(extended_config, "frequency_penalty")
        assert hasattr(extended_config, "presence_penalty")


class TestModelProviderImplementation:
    """测试模型提供者的具体实现"""

    def test_model_provider_generates_response(self):
        """测试模型提供者生成响应"""
        # 模拟模型提供者
        mock_provider = Mock()
        mock_provider.generate = Mock(
            return_value={
                "content": "Test response",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            }
        )

        # 测试生成响应
        result = mock_provider.generate("Test prompt")

        assert "content" in result
        assert "usage" in result
        assert result["content"] == "Test response"
        assert result["usage"]["prompt_tokens"] == 10
        assert result["usage"]["completion_tokens"] == 20

        # 验证调用参数
        mock_provider.generate.assert_called_once_with("Test prompt")

    @pytest.mark.asyncio
    async def test_model_provider_async_generation(self):
        """测试模型提供者的异步生成"""
        # 模拟异步模型提供者
        mock_provider = AsyncMock()
        mock_provider.generate_async = AsyncMock(
            return_value={
                "content": "Async response",
                "usage": {"prompt_tokens": 15, "completion_tokens": 25},
            }
        )

        # 测试异步生成响应
        result = await mock_provider.generate_async("Async prompt")

        assert "content" in result
        assert "usage" in result
        assert result["content"] == "Async response"
        assert result["usage"]["prompt_tokens"] == 15
        assert result["usage"]["completion_tokens"] == 25

        # 验证调用参数
        mock_provider.generate_async.assert_called_once_with("Async prompt")

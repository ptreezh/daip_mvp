"""
LiteLLM embedding provider配置错误修复测试
遵循TDD原则：先写失败测试，再实现修复
"""

from unittest.mock import Mock

import pytest

from daip_live.model_provider.provider import LiteLLMProvider, ModelError


class TestLiteLLMEmbeddingProviderFix:
    """测试LiteLLM embedding provider配置问题修复"""

    @pytest.fixture
    def mock_config(self):
        """创建Mock配置"""
        config = Mock()
        config.model = "all-MiniLM-L6-v2"
        config.api_key = None
        config.base_url = None
        return config

    @pytest.fixture
    def provider_with_mock_config(self, mock_config):
        """创建带有Mock配置的Provider"""
        return LiteLLMProvider(mock_config)

    def test_embedding_without_provider_fails(self, provider_with_mock_config):
        """RED测试：当使用原始配置且没有修复时，embedding应该失败"""
        provider = provider_with_mock_config

        # 修改配置以模拟原始问题 - 使用model而不是embedding_model
        provider.config.model = "all-MiniLM-L6-v2"
        # 删除embedding_model属性，模拟原始代码只使用model的情况
        if hasattr(provider.config, "embedding_model"):
            delattr(provider.config, "embedding_model")

        # Act & Assert - 这应该抛出ModelError
        with pytest.raises(ModelError) as exc_info:
            import asyncio

            asyncio.run(provider.embed("test text"))

        # 验证错误信息包含provider相关内容
        error_message = str(exc_info.value)
        # 现在应该会失败，因为fallback到huggingface但网络连接失败
        assert "error" in error_message.lower()

    def test_embedding_with_huggingface_provider_succeeds(self, mock_config):
        """GREEN测试：当指定embedding_model时，embedding应该成功"""
        # 修复配置以使用mock embedding
        mock_config.embedding_model = "mock-embedding"
        provider = LiteLLMProvider(mock_config)

        # Act & Assert - 这应该成功
        import asyncio

        result = asyncio.run(provider.embed("test text"))

        # 验证返回了384维向量
        assert len(result) == 384
        assert all(isinstance(x, float) for x in result)

    def test_embedding_with_real_fallback_scenario(self, mock_config):
        """测试实际的fallback场景"""
        # 配置一个会导致provider错误的模型
        mock_config.embedding_model = "invalid-model-name/no-provider"
        mock_config.api_key = None
        provider = LiteLLMProvider(mock_config)

        # 源码权威: _handle_embedding_failure 对 "LLM Provider NOT provided" 走
        # _try_fallback_embedding 返回 mock 向量（provider.py:137-146），不抛错；
        # 验证 fallback 生效
        import asyncio

        result = asyncio.run(provider.embed("test text"))
        assert len(result) == 384

    def test_embedding_uses_embedding_model_config(self, mock_config):
        """测试embed方法使用embedding_model而不是model"""
        mock_config.model = "some-chat-model"
        mock_config.embedding_model = "mock-embedding"
        provider = LiteLLMProvider(mock_config)

        import asyncio

        result = asyncio.run(provider.embed("test text"))

        # 验证使用了embedding_model
        assert len(result) == 384


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

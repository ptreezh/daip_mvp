"""Tests for the LiteLLMProvider."""

import litellm
import pytest

from daip_live.core.config import get_safe_test_model
from daip_live.core.exceptions import ModelAuthenticationError
from daip_live.core.models import ProviderConfig
from daip_live.model_provider.provider import LiteLLMProvider


class TestLiteLLMProvider:
    def test_initialization(self):
        """Tests that the provider can be initialized successfully."""
        config = ProviderConfig(model=get_safe_test_model(), api_key="test_key")

        provider = LiteLLMProvider(config=config)

        assert provider.config == config

    @pytest.mark.asyncio
    async def test_generate_success(self, mocker):
        """Tests the generate method for a successful API call."""
        # 源码权威: generate(prompt, params) 是 async generator（provider.py:276）；
        # "test-model" 是 local model 走 mock 分支不调 litellm，须用非本地模型名测 litellm 路径  # noqa: E501
        config = ProviderConfig(model="gpt-3.5-turbo")
        provider = LiteLLMProvider(config=config)

        mock_choice = mocker.Mock()
        mock_choice.message.content = "Hello, world!"
        mock_response = mocker.Mock()
        mock_response.choices = [mock_choice]

        mock_litellm_completion = mocker.patch(
            "litellm.completion",
            return_value=mock_response,
        )

        result = None
        async for chunk in provider.generate(prompt="Say hi", params={}):
            result = chunk

        assert result == "Hello, world!"
        mock_litellm_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_authentication_error(self, mocker):
        """Tests that an auth error from litellm is correctly wrapped."""
        config = ProviderConfig(model="gpt-3.5-turbo")
        provider = LiteLLMProvider(config=config)

        mocker.patch(
            "litellm.completion",
            side_effect=litellm.exceptions.AuthenticationError(
                message="Invalid API Key",
                llm_provider="test_provider",
                model="test_model",
            ),
        )

        with pytest.raises(ModelAuthenticationError) as excinfo:
            async for _ in provider.generate(prompt="Anything", params={}):
                pass

        assert "Invalid API Key" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_embed_success(self, mocker):
        """Tests the embed method for a successful API call."""
        config = ProviderConfig(model="text-embedding-ada-002")
        provider = LiteLLMProvider(config=config)
        expected_vector = [0.1, 0.2, 0.3]

        mock_response = mocker.Mock()
        mock_response.data = [mocker.Mock(embedding=expected_vector)]

        mock_aembedding = mocker.patch(
            "litellm.aembedding",
            new=mocker.AsyncMock(return_value=mock_response),
        )

        result = await provider.embed(text="Embed this")

        assert result == expected_vector
        # 源码权威: _try_embedding 仅传 model/input（provider.py:125-132），
        # config 未设 api_key/base_url 时不传这两个参数
        mock_aembedding.assert_called_once_with(
            model=config.model,
            input=["Embed this"],
        )

    @pytest.mark.asyncio
    async def test_embed_authentication_error(self, mocker):
        """Tests that an auth error from litellm during embedding is correctly wrapped."""  # noqa: E501
        config = ProviderConfig(model="test-model")
        provider = LiteLLMProvider(config=config)

        mocker.patch(
            "litellm.aembedding",
            side_effect=litellm.exceptions.AuthenticationError(
                message="Invalid API Key",
                llm_provider="test_provider",
                model="test_model",
            ),
        )

        with pytest.raises(ModelAuthenticationError) as excinfo:
            await provider.embed(text="Anything")

        assert "Invalid API Key" in str(excinfo.value)

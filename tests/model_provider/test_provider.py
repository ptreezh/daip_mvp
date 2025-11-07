"""Tests for the LiteLLMProvider."""

import pytest

import litellm
from daip_live.core.exceptions import ModelAuthenticationError
from daip_live.core.models import ProviderConfig
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.core.config import get_safe_test_model


class TestLiteLLMProvider:
    def test_initialization(self):
        """Tests that the provider can be initialized successfully."""
        config = ProviderConfig(
            model=get_safe_test_model(),
            api_key="test_key"
        )

        provider = LiteLLMProvider(config=config)

        assert provider.config == config

    @pytest.mark.asyncio
    async def test_generate_success(self, mocker):
        """Tests the generate method for a successful API call."""
        config = ProviderConfig(model="test-model")
        provider = LiteLLMProvider(config=config)

        mock_choice = mocker.Mock()
        mock_choice.message.content = "Hello, world!"
        mock_response = mocker.Mock()
        mock_response.choices = [mock_choice]

        mock_litellm_completion = mocker.patch(
            "daip_live.model_provider.provider.litellm.completion",
            return_value=mock_response
        )

        result = await provider.generate(prompt="Say hi")

        assert result == "Hello, world!"
        mock_litellm_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_authentication_error(self, mocker):
        """Tests that an auth error from litellm is correctly wrapped."""
        config = ProviderConfig(model="test-model")
        provider = LiteLLMProvider(config=config)

        mocker.patch(
            "daip_live.model_provider.provider.litellm.completion",
            side_effect=litellm.exceptions.AuthenticationError(
                message="Invalid API Key",
                llm_provider="test_provider",
                model="test_model"
            )
        )

        with pytest.raises(ModelAuthenticationError) as excinfo:
            await provider.generate(prompt="Anything")

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
            "daip_live.model_provider.provider.litellm.aembedding",
            new=mocker.AsyncMock(return_value=mock_response)
        )

        result = await provider.embed(text="Embed this")

        assert result == expected_vector
        mock_aembedding.assert_called_once_with(
            model=config.model,
            input=["Embed this"],
            api_key=config.api_key,
            base_url=config.base_url,
        )

    @pytest.mark.asyncio
    async def test_embed_authentication_error(self, mocker):
        """Tests that an auth error from litellm during embedding is correctly wrapped."""
        config = ProviderConfig(model="test-model")
        provider = LiteLLMProvider(config=config)

        mocker.patch(
            "daip_live.model_provider.provider.litellm.aembedding",
            side_effect=litellm.exceptions.AuthenticationError(
                message="Invalid API Key",
                llm_provider="test_provider",
                model="test_model"
            )
        )

        with pytest.raises(ModelAuthenticationError) as excinfo:
            await provider.embed(text="Anything")

        assert "Invalid API Key" in str(excinfo.value)

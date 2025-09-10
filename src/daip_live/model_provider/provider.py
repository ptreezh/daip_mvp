"""This module contains the LiteLLMProvider adapter."""

import asyncio
from typing import Any, Dict, List, Tuple

from daip_live.core.exceptions import ModelAuthenticationError, ModelError
from daip_live.core.interfaces import IModelProvider
from daip_live.core.models import ProviderConfig

import litellm


class LiteLLMProvider(IModelProvider):
    """An adapter that uses the litellm library to fulfill the IModelProvider contract."""

    def __init__(self, config: ProviderConfig):
        self.config = config

    def _build_litellm_params(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Constructs the parameter dictionary for the litellm.completion call."""
        params = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "num_retries": self.config.num_retries,
        }

        if self.config.api_key:
            params["api_key"] = self.config.api_key
        if self.config.base_url:
            params["base_url"] = self.config.base_url
        if self.config.temperature is not None:
            params["temperature"] = self.config.temperature
        if self.config.max_tokens is not None:
            params["max_tokens"] = self.config.max_tokens

        # Allow runtime overrides
        params.update(kwargs)
        return params

    async def generate(self, prompt: str, **kwargs) -> Tuple[str, Any]:
        """Generates a response from a language model using litellm."""
        params = self._build_litellm_params(prompt, **kwargs)
        try:
            # litellm.completion is a synchronous call, run it in a thread
            response = await asyncio.to_thread(litellm.completion, **params)
            content = response.choices[0].message.content
            usage = response.usage
            if content is None:
                raise ModelError("Received null content from model.")
            return content, usage
        except litellm.exceptions.AuthenticationError as e:
            raise ModelAuthenticationError(f"LiteLLM auth error: {e}") from e
        except Exception as e:
            # Catch any other litellm or unexpected error
            raise ModelError(f"LiteLLM generic error: {e}") from e

    async def embed(self, text: str) -> List[float]:
        """Creates an embedding vector for the given text using litellm."""
        try:
            response = await litellm.aembedding(
                model=self.config.model,
                input=[text],
                api_key=self.config.api_key,
                base_url=self.config.base_url,
            )
            return response.data[0].embedding
        except litellm.exceptions.AuthenticationError as e:
            raise ModelAuthenticationError(f"LiteLLM auth error: {e}") from e
        except Exception as e:
            raise ModelError(f"LiteLLM embedding error: {e}") from e

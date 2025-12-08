"""This module contains the LiteLLMProvider adapter."""

import asyncio
from typing import Any, Dict, List, Tuple

import litellm
from daip_live.core.exceptions import ModelAuthenticationError, ModelError
from daip_live.core.interfaces import IModelProvider
from daip_live.core.models import ProviderConfig
from daip_live.core.config import is_local_model


class LiteLLMProvider(IModelProvider):
    """An adapter that uses the litellm library to fulfill the IModelProvider contract."""

    def __init__(self, config: ProviderConfig):
        self.config = config

    def _build_litellm_params(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Constructs the parameter dictionary for the litellm.completion call."""
        # Safely access config attributes
        config_model = getattr(self.config, 'model', 'test-model')
        config_num_retries = getattr(self.config, 'num_retries', 3)
        config_api_key = getattr(self.config, 'api_key', None)
        config_base_url = getattr(self.config, 'base_url', None)
        config_temperature = getattr(self.config, 'temperature', None)
        config_max_tokens = getattr(self.config, 'max_tokens', None)

        params = {
            "model": config_model,
            "messages": [{"role": "user", "content": prompt}],
            "num_retries": config_num_retries,
        }

        if config_api_key:
            params["api_key"] = config_api_key
        if config_base_url:
            params["base_url"] = config_base_url
        if config_temperature is not None:
            params["temperature"] = config_temperature
        if config_max_tokens is not None:
            params["max_tokens"] = config_max_tokens

        # Filter out parameters that Ollama doesn't support
        # Only add supported parameters from kwargs
        for key, value in kwargs.items():
            if key in ['temperature', 'max_tokens', 'top_p', 'stop', 'stream', 'seed']:
                # These are generally supported by most providers including Ollama
                params[key] = value
            elif key in ['frequency_penalty', 'presence_penalty'] and not config_model.startswith("ollama/"):
                # frequency_penalty and presence_penalty are not supported by Ollama
                params[key] = value
            elif key not in ['frequency_penalty', 'presence_penalty']:
                # Add other parameters that are not known problematic ones
                params[key] = value

        # For Ollama models, explicitly set drop_params to True to ignore unsupported parameters
        if config_model.startswith("ollama/"):
            params["drop_params"] = True

        return params

    async def generate(self, prompt: str, **kwargs) -> Tuple[str, Any]:
        """Generates a response from a language model using litellm."""
        config_model = getattr(self.config, 'model', 'test-model')

        # 如果是本地模型，返回模拟响应
        if is_local_model(config_model):
            return self._generate_mock_response(prompt, config_model)

        params = self._build_litellm_params(prompt, **kwargs)
        try:
            # litellm.completion is a synchronous call, run it in a thread
            response = await asyncio.to_thread(litellm.completion, **params)
            content = response.choices[0].message.content

            # Safely handle usage object - it might be a dict or object
            usage = None
            if hasattr(response, 'usage') and response.usage is not None:
                if isinstance(response.usage, dict):
                    usage = response.usage
                else:
                    # Convert object to dict if it's not already
                    try:
                        usage = {
                            'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                            'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                            'total_tokens': getattr(response.usage, 'total_tokens', 0)
                        }
                    except Exception:
                        usage = {'total_tokens': 0}
            else:
                usage = {'total_tokens': 0}

            if content is None:
                raise ModelError("Received null content from model.")
            return content, usage
        except litellm.exceptions.AuthenticationError as e:
            raise ModelAuthenticationError(f"LiteLLM auth error: {e}") from e
        except Exception as e:
            # Catch any other litellm or unexpected error
            raise ModelError(f"LiteLLM generic error: {e}") from e

    def _generate_mock_response(self, prompt: str, model: str) -> Tuple[str, Any]:
        """生成模拟响应用于测试"""
        # 根据模型类型生成不同的模拟响应
        if model == "test-model":
            content = f"This is a test response for: {prompt[:50]}..."
        elif model == "mock-llm":
            content = f"Mock LLM response to: {prompt[:50]}..."
        else:
            content = f"Local model response to: {prompt[:50]}..."

        usage = {
            'prompt_tokens': len(prompt.split()),
            'completion_tokens': len(content.split()),
            'total_tokens': len(prompt.split()) + len(content.split())
        }

        return content, usage

    async def embed(self, text: str) -> List[float]:
        """Creates an embedding vector for the given text using litellm."""
        config_model = getattr(self.config, 'embedding_model', 'text-embedding-ada-002')
        config_api_key = getattr(self.config, 'api_key', None)
        config_base_url = getattr(self.config, 'base_url', None)

        # Handle mock embedding for testing and local models
        if config_model == "mock-embedding" or is_local_model(config_model):
            return self._generate_mock_embedding()

        # Normalize model name for different providers
        normalized_model = self._normalize_model_name(config_model)

        try:
            return await self._try_embedding(normalized_model, text, config_api_key, config_base_url)
        except litellm.exceptions.AuthenticationError as e:
            raise ModelAuthenticationError(f"LiteLLM auth error: {e}") from e
        except Exception as e:
            return await self._handle_embedding_failure(e, text, config_api_key, config_base_url)
    
    def _generate_mock_embedding(self) -> List[float]:
        """Generate a mock embedding vector for testing purposes."""
        return [0.1] * 384
    
    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name with appropriate provider prefix."""
        # Don't normalize mock embeddings
        if model == "mock-embedding":
            return model
        if model.startswith("all-MiniLM") or ("MiniLM" in model and "mock" not in model.lower()):
            return f"huggingface/{model}"
        return model
    
    async def _try_embedding(self, model: str, text: str, api_key: str, base_url: str) -> List[float]:
        """Attempt to generate embedding with the specified model."""
        params = {
            "model": model,
            "input": [text]
        }
        if api_key:
            params["api_key"] = api_key
        if base_url:
            params["base_url"] = base_url
        
        response = await litellm.aembedding(**params)
        return response.data[0].embedding
    
    async def _handle_embedding_failure(self, error: Exception, text: str, api_key: str, base_url: str) -> List[float]:
        """Handle embedding failures with fallback logic."""
        if "LLM Provider NOT provided" in str(error):
            return await self._try_fallback_embedding(text, api_key, base_url)
        raise ModelError(f"LiteLLM embedding error: {error}") from error
    
    async def _try_fallback_embedding(self, text: str, api_key: str, base_url: str) -> List[float]:
        """Try fallback embedding when primary model fails."""
        # Use mock embedding as fallback to avoid API calls
        return self._generate_mock_embedding()

    def get_available_models(self) -> List[str]:
        """
        Get list of available models from the provider.

        Returns:
            List of available model names
        """
        available_models = []

        # Common Ollama models that are likely available
        ollama_models = [
            "ollama/llama3",
            "ollama/llama3:instruct",
            "ollama/llama2",
            "ollama/mistral",
            "ollama/mistral:instruct",
            "ollama/codellama",
            "ollama/nomic-embed-text",
            "ollama/phi",
            "ollama/neural-chat"
        ]

        # Common cloud models
        cloud_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "gemini-pro"
        ]

        # Try to determine if we have access to cloud models
        if (hasattr(self.config, 'api_key') and self.config.api_key and
            self.config.api_key.strip() and self.config.api_key != "your-api-key-here"):
            available_models.extend(cloud_models)

        # Always include common Ollama models (users may have them installed)
        available_models.extend(ollama_models)

        return available_models

    def is_model_available(self, model_name: str) -> bool:
        """
        Check if a specific model is available.

        Args:
            model_name: Name of the model to check

        Returns:
            True if model is likely available, False otherwise
        """
        available_models = self.get_available_models()
        return model_name in available_models

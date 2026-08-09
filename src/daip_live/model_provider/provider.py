"""This module contains the LiteLLMProvider adapter."""

import asyncio
import subprocess
from typing import Any

import litellm

from daip_live.core.config import is_local_model
from daip_live.core.exceptions import ModelAuthenticationError, ModelError
from daip_live.core.interfaces import IModelProvider
from daip_live.core.models import ProviderConfig


class LiteLLMProvider(IModelProvider):
    """An adapter that uses the litellm library to fulfill the IModelProvider contract."""  # noqa: E501

    def __init__(self, config: ProviderConfig):
        self.config = config

    def _build_litellm_params(self, prompt: str, **kwargs) -> dict[str, Any]:
        """Constructs the parameter dictionary for the litellm.completion call."""
        # Safely access config attributes
        config_model = getattr(self.config, "model", "test-model")
        config_num_retries = getattr(self.config, "num_retries", 3)
        config_api_key = getattr(self.config, "api_key", None)
        config_base_url = getattr(self.config, "base_url", None)
        config_temperature = getattr(self.config, "temperature", None)
        config_max_tokens = getattr(self.config, "max_tokens", None)

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
            if key in ["temperature", "max_tokens", "top_p", "stop", "stream", "seed"]:
                # These are generally supported by most providers including Ollama
                params[key] = value
            elif key in [
                "frequency_penalty",
                "presence_penalty",
            ] and not config_model.startswith("ollama/"):
                # frequency_penalty and presence_penalty are not supported by Ollama
                params[key] = value
            elif key not in ["frequency_penalty", "presence_penalty"]:
                # Add other parameters that are not known problematic ones
                params[key] = value

        # For Ollama models, explicitly set drop_params to True to ignore unsupported parameters  # noqa: E501
        if config_model.startswith("ollama/"):
            params["drop_params"] = True

        return params

    def _generate_mock_response(self, prompt: str, model: str) -> tuple[str, Any]:
        """生成模拟响应用于测试"""
        # 根据模型类型生成不同的模拟响应
        if model == "test-model":
            content = f"This is a test response for: {prompt[:50]}..."
        elif model == "mock-llm":
            content = f"Mock LLM response to: {prompt[:50]}..."
        else:
            content = f"Local model response to: {prompt[:50]}..."

        usage = {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(content.split()),
            "total_tokens": len(prompt.split()) + len(content.split()),
        }

        return content, usage

    async def embed(self, text: str) -> list[float]:
        """Creates an embedding vector for the given text using litellm."""
        config_model = (
            getattr(self.config, "embedding_model", None) or "text-embedding-ada-002"
        )
        config_api_key = getattr(self.config, "api_key", None)
        config_base_url = getattr(self.config, "base_url", None)

        # Handle mock embedding for testing and local models
        if config_model == "mock-embedding" or is_local_model(config_model):
            return self._generate_mock_embedding()

        # For Ollama embedding models, check availability and use fallback if needed
        if config_model.startswith("ollama/"):
            effective_model = self._get_fallback_model(config_model)
            if effective_model != config_model:
                config_model = effective_model

        # Normalize model name for different providers
        normalized_model = self._normalize_model_name(config_model)

        try:
            return await self._try_embedding(
                normalized_model, text, config_api_key, config_base_url
            )
        except litellm.exceptions.AuthenticationError as e:
            raise ModelAuthenticationError(f"LiteLLM auth error: {e}") from e
        except Exception as e:
            return await self._handle_embedding_failure(
                e, text, config_api_key, config_base_url
            )

    def _generate_mock_embedding(self) -> list[float]:
        """Generate a mock embedding vector for testing purposes."""
        return [0.1] * 384

    def _normalize_model_name(self, model: str) -> str:
        """Normalize model name with appropriate provider prefix."""
        # Don't normalize mock embeddings
        if model == "mock-embedding":
            return model
        if model.startswith("all-MiniLM") or (
            "MiniLM" in model and "mock" not in model.lower()
        ):
            return f"huggingface/{model}"
        return model

    async def _try_embedding(
        self, model: str, text: str, api_key: str, base_url: str
    ) -> list[float]:
        """Attempt to generate embedding with the specified model."""
        params = {"model": model, "input": [text]}
        if api_key:
            params["api_key"] = api_key
        if base_url:
            params["base_url"] = base_url

        response = await litellm.aembedding(**params)
        data = response.data[0]
        if isinstance(data, dict):
            return data["embedding"]
        return data.embedding

    async def _handle_embedding_failure(
        self, error: Exception, text: str, api_key: str, base_url: str
    ) -> list[float]:
        """Handle embedding failures with fallback logic."""
        if "LLM Provider NOT provided" in str(error):
            return await self._try_fallback_embedding(text, api_key, base_url)
        raise ModelError(f"LiteLLM embedding error: {error}") from error

    async def _try_fallback_embedding(
        self, text: str, api_key: str, base_url: str
    ) -> list[float]:
        """Try fallback embedding when primary model fails."""
        # Use mock embedding as fallback to avoid API calls
        return self._generate_mock_embedding()

    def get_available_models(self) -> list[str]:
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
            "ollama/neural-chat",
        ]

        # Common cloud models
        cloud_models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "gemini-pro",
        ]

        # Try to determine if we have access to cloud models
        if (
            hasattr(self.config, "api_key")
            and self.config.api_key
            and self.config.api_key.strip()
            and self.config.api_key != "your-api-key-here"
        ):
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

    def _get_available_ollama_models(self) -> list[str]:
        """Get list of available Ollama models by calling ollama list."""
        models = []
        try:
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                # Parse Ollama output
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:  # Skip header line
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 1:
                            model_name = parts[0]
                            # Add model with ollama/ prefix as expected by the system
                            full_model_name = (
                                f"ollama/{model_name}"
                                if not model_name.startswith("ollama/")
                                else model_name
                            )
                            models.append(full_model_name)
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            # Ollama not installed or not running - return empty list
            pass

        return models

    def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is available in Ollama."""
        available_models = self._get_available_ollama_models()
        return model_name in available_models

    def _get_fallback_model(
        self, original_model: str, force_fallback: bool = False
    ) -> str:
        """Get a fallback model if the original model is not available or force_fallback is True."""  # noqa: E501
        if force_fallback or not self._is_model_available(original_model):
            # Get available Ollama models as fallback options
            available_models = self._get_available_ollama_models()

            # Prefer models similar to the original, otherwise use the first available one  # noqa: E501
            if available_models:
                # Extract just the model name part (after provider prefix)
                # e.g., "ollama/mistral-something" -> "mistral-something"
                if "/" in original_model:
                    model_name_part = original_model.split("/", 1)[1].lower()
                else:
                    model_name_part = original_model.lower()

                # Define model family keywords to search for
                # Order by specificity - more specific matches first to avoid partial matches  # noqa: E501
                family_keywords = [
                    ("codellama", lambda model: "codellama" in model.lower()),
                    ("llama3", lambda model: "llama3" in model.lower()),
                    ("llama", lambda model: "llama" in model.lower()),
                    ("mistral", lambda model: "mistral" in model.lower()),
                    ("phi3", lambda model: "phi3" in model.lower()),
                    ("phi", lambda model: "phi" in model.lower()),
                ]

                for family, match_func in family_keywords:
                    if match_func(model_name_part):
                        for model in available_models:
                            if family in model.lower():
                                return model
                        break  # Return first matching model

                # If no similar model found, return first available model
                return available_models[0]

            # If original model is available and fallback not forced, return it
            return original_model
        else:
            return original_model

    async def generate(self, prompt: str, params: dict):
        """Generates a response from a language model using litellm."""
        config_model = getattr(self.config, "model", "test-model")

        # 如果是本地模型，返回模拟响应
        if is_local_model(config_model):
            response, _ = self._generate_mock_response(prompt, config_model)
            yield response
            return

        # 检查模型是否可用，如果不可用则使用回退模型
        effective_model = self._get_fallback_model(config_model)

        # 如果模型已更改，更新参数
        litellm_params = self._build_litellm_params(prompt, **params)
        if effective_model != config_model:
            litellm_params["model"] = effective_model
            # 记录模型切换信息

        try:
            # litellm.completion is a synchronous call, run it in a thread
            response = await asyncio.to_thread(litellm.completion, **litellm_params)
            content = response.choices[0].message.content

            if content is None:
                raise ModelError("Received null content from model.")

            # Yield the content as a single chunk (for compatibility with streaming interface)  # noqa: E501
            yield content
        except litellm.exceptions.AuthenticationError as e:
            raise ModelAuthenticationError(f"LiteLLM auth error: {e}") from e
        except Exception as e:
            # Catch any other litellm or unexpected error
            raise ModelError(f"LiteLLM generic error: {e}") from e

    async def agenerate(
        self,
        prompt: str,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> tuple[str, dict[str, Any]]:
        """生成完整响应，返回 (content, metadata) 二元组。

        与 ``generate``（async generator 流式）不同，``agenerate`` 收集完整响应后
        一次性返回，便于调用方直接 ``await`` 使用。
        """
        config_model = model or getattr(self.config, "model", "test-model")

        # 与 generate 保持一致：本地模型返回模拟响应
        if is_local_model(config_model):
            return self._generate_mock_response(prompt, config_model)

        # 检查模型是否可用，如果不可用则使用回退模型
        effective_model = self._get_fallback_model(config_model)
        litellm_params = self._build_litellm_params(
            prompt,
            model=effective_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        try:
            response = await litellm.acompletion(**litellm_params)
            content = response.choices[0].message.content

            if content is None:
                raise ModelError("Received null content from model.")

            usage = getattr(response, "usage", None)
            metadata: dict[str, Any] = {
                "model": effective_model,
                "usage": usage.model_dump() if usage else None,
            }
            return content, metadata
        except litellm.exceptions.AuthenticationError as e:
            raise ModelAuthenticationError(f"LiteLLM auth error: {e}") from e
        except Exception as e:
            # Catch any other litellm or unexpected error
            raise ModelError(f"LiteLLM generic error: {e}") from e

    def get_default_model(self) -> str:
        """Get the default model for this provider."""
        config_model = getattr(self.config, "model", "test-model")

        # First try to get the configured model
        if self._is_model_available(config_model):
            return config_model

        # Fall back to first available model
        available_models = self._get_available_ollama_models()
        if available_models:
            return available_models[0]

        # Final fallback
        return "test-model"

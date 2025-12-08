"""This module contains LiteLLMProvider adapter."""
import asyncio
import subprocess
from typing import Any, Dict, List, Tuple

import litellm
from daip_live.core.exceptions import ModelAuthenticationError, ModelError
from daip_live.core.interfaces import IModelProvider
from daip_live.core.config import is_local_model


class LiteLLMProvider(IModelProvider):
    """An adapter that uses the litellm library to fulfill IModelProvider contract."""

    def __init__(self, config):
        self.config = config
        self._available_models = None  # Cache for available models

    def _build_litellm_params(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Constructs parameter dictionary for litellm.completion call."""
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

        return params

    def _get_available_ollama_models(self) -> List[str]:
        """Get list of available Ollama models by calling ollama list."""
        models = []
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse Ollama output
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header line
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 1:
                            model_name = parts[0]
                            # Add model with ollama/ prefix as expected by the system
                            full_model_name = f"ollama/{model_name}" if not model_name.startswith("ollama/") else model_name
                            models.append(full_model_name)
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            # Ollama not installed or not running - return empty list
            pass

        # Cache the result
        self._available_models = models
        return models

    def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is available in Ollama."""
        if not self._available_models:
            self._available_models = self._get_available_ollama_models()
        return model_name in self._available_models

    def _get_fallback_model(self, original_model: str, force_fallback: bool = False) -> str:
        """Get a fallback model if the original model is not available or force_fallback is True."""
        if force_fallback or not self._is_model_available(original_model):
            # Get available Ollama models as fallback options
            available_models = self._get_available_ollama_models()

            # Prefer models similar to the original, otherwise use the first available one
            if available_models:
                # Extract just the model name part (after provider prefix)
                # e.g., "ollama/mistral-something" -> "mistral-something"
                if "/" in original_model:
                    model_name_part = original_model.split("/", 1)[1].lower()
                else:
                    model_name_part = original_model.lower()

                # Define model family keywords to search for
                # Order by specificity - more specific matches first to avoid partial matches
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
                        return model
                        break  # Return first matching model

                # If no similar model found, return first available model
                return available_models[0]

            # If original model is available and fallback not forced, return it
            return original_model

    async def generate(self, prompt: str, **kwargs) -> Tuple[str, Any]:
        """Generates a response from a language model using litellm."""
        config_model = getattr(self.config, 'model', 'test-model')

        # 如果是本地模型，返回模拟响应
        if is_local_model(config_model):
            return self._generate_mock_response(prompt, config_model)

        # 检查模型是否可用，如果不可用则使用回退模型
        effective_model = self._get_fallback_model(config_model)

        # 如果模型已更改，更新参数
        params = self._build_litellm_params(prompt, **kwargs)
        if effective_model != config_model:
            params["model"] = effective_model
            # 记录模型切换信息
            print(f"🔄 Model switched from '{config_model}' to '{effective_model}' due to availability.")

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
                    try:
                        usage = {
                            'prompt_tokens': getattr(response.usage, 'prompt_tokens', 0),
                            'completion_tokens': getattr(response.usage, 'completion_tokens', 0),
                            'total_tokens': getattr(response.usage, 'total_tokens', 0)
                        }
                    except Exception:
                        usage = {'total_tokens': 0}

            return content, usage
        except litellm.exceptions.AuthenticationError as e:
            raise ModelAuthenticationError(f"LiteLLM auth error: {e}") from e
        except Exception as e:
            error_msg = str(e)

            if content is None:
                raise ModelError("Received null content from model.")
            return content, usage

    def get_default_model(self) -> str:
        """Get the default model for this provider."""
        config_model = getattr(self.config, 'model', 'test-model')

        # First try to get the configured model
        if self._is_model_available(config_model):
            return config_model

        # Fall back to first available model
        available_models = self.get_available_models()
        if available_models:
            return available_models[0]

        # Final fallback
        return 'default-model'

    def get_available_models(self) -> List[str]:
        """Get list of available models from this provider."""
        return self._get_available_ollama_models() if is_local_model(self.config.model) else []

    def _generate_mock_response(self, prompt: str, model_name: str) -> Tuple[str, Any]:
        """Generate a mock response for local models."""
        responses = {
            'llama': 'I am a local LLAMA model running locally. This is a simulated response for testing purposes.',
            'mistral': 'I am a local Mistral model running locally. This is a simulated response for testing purposes.',
            'phi': 'I am a local Phi model running locally. This is a simulated response for testing purposes.'
        }

        response_text = responses.get(model_name, 'I am a local model providing a simulated response.')

        usage = {'total_tokens': 100, 'prompt_tokens': 50, 'completion_tokens': 50}
        return response_text, usage
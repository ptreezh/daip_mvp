"""
Model Provider for Model Switching System

Handles AI model provider management, API interactions, and health checking.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import aiohttp
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    LOCAL = "local"
    CUSTOM = "custom"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"


class ModelProvider:
    """AI model provider management"""

    def __init__(
        self,
        name: str,
        provider_type: ProviderType,
        base_url: str,
        api_key: str,
        timeout: int = 30,
        retry_attempts: int = 3,
        rate_limit_rpm: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        supported_models: Optional[List[str]] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.provider_type = provider_type
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.rate_limit_rpm = rate_limit_rpm
        self.headers = headers or {}
        self.supported_models = supported_models or []
        self.description = description
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.last_health_check: Optional[datetime] = None
        self.health_status = "unknown"
        self.response_time: Optional[float] = None

        # Rate limiting tracking
        self._requests_in_minute = 0
        self._minute_start = datetime.now()
        self._last_request_time: Optional[datetime] = None

        # Initialize provider-specific settings
        self._initialize_provider_settings()

    def _initialize_provider_settings(self) -> None:
        """Initialize provider-specific settings"""
        if self.provider_type == ProviderType.OPENAI:
            self.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
        elif self.provider_type == ProviderType.ANTHROPIC:
            self.headers.update({
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            })
        elif self.provider_type == ProviderType.OLLAMA:
            # Ollama typically doesn't need API key
            if "Content-Type" not in self.headers:
                self.headers["Content-Type"] = "application/json"
        elif self.provider_type == ProviderType.HUGGINGFACE:
            self.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })

    def is_configured(self) -> bool:
        """Check if provider is properly configured"""
        if not self.name or not self.base_url:
            return False

        # Some providers don't require API keys (e.g., local Ollama)
        if self.provider_type not in [ProviderType.LOCAL, ProviderType.OLLAMA]:
            if not self.api_key or len(self.api_key) < 3:
                return False

        return True

    def validate_configuration(self) -> bool:
        """Validate provider configuration"""
        if not self.is_configured():
            return False

        # Validate URL format
        if not (self.base_url.startswith('http://') or self.base_url.startswith('https://')):
            return False

        # Validate timeout
        if self.timeout <= 0:
            return False

        # Validate retry attempts
        if self.retry_attempts < 0:
            return False

        # Validate rate limit if specified
        if self.rate_limit_rpm is not None and self.rate_limit_rpm <= 0:
            return False

        return True

    def can_make_request(self) -> bool:
        """Check if request can be made based on rate limiting"""
        if not self.rate_limit_rpm:
            return True

        # Reset counter if minute has passed
        now = datetime.now()
        if (now - self._minute_start) >= timedelta(minutes=1):
            self._requests_in_minute = 0
            self._minute_start = now

        return self._requests_in_minute < self.rate_limit_rpm

    def _record_request(self) -> None:
        """Record a request for rate limiting"""
        if self.rate_limit_rpm:
            self._requests_in_minute += 1
        self._last_request_time = datetime.now()

    async def check_health(self) -> Dict[str, Any]:
        """Check provider health status"""
        try:
            start_time = datetime.now()

            # Provider-specific health check
            if self.provider_type == ProviderType.OPENAI:
                health_data = await self._check_openai_health()
            elif self.provider_type == ProviderType.ANTHROPIC:
                health_data = await self._check_anthropic_health()
            elif self.provider_type == ProviderType.OLLAMA:
                health_data = await self._check_ollama_health()
            else:
                health_data = await self._check_generic_health()

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000

            self.last_health_check = end_time
            self.response_time = response_time
            self.health_status = health_data.get("status", "healthy")

            return {
                "status": self.health_status,
                "response_time": response_time,
                "timestamp": end_time.isoformat(),
                "details": health_data
            }

        except Exception as e:
            logger.error(f"Health check failed for {self.name}: {e}")
            self.health_status = "unhealthy"
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def _check_openai_health(self) -> Dict[str, Any]:
        """Check OpenAI API health"""
        url = urljoin(self.base_url, "/models")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return {"status": "healthy", "api_available": True}
                else:
                    return {"status": "degraded", "api_status": response.status}

    async def _check_anthropic_health(self) -> Dict[str, Any]:
        """Check Anthropic API health"""
        # Anthropic doesn't have a dedicated health endpoint
        # We'll make a minimal request to test connectivity
        return await self._check_generic_health()

    async def _check_ollama_health(self) -> Dict[str, Any]:
        """Check Ollama health"""
        url = urljoin(self.base_url, "/api/tags")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "available_models": len(data.get("models", [])),
                        "api_version": data.get("version", "unknown")
                    }
                else:
                    return {"status": "unhealthy", "api_status": response.status}

    async def _check_generic_health(self) -> Dict[str, Any]:
        """Generic health check for other providers"""
        # Most providers don't have dedicated health endpoints
        # We'll just check if the base URL is reachable
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(self.base_url, headers=self.headers) as response:
                    return {"status": "reachable", "http_status": response.status}
        except Exception:
            return {"status": "unreachable"}

    async def list_available_models(self) -> List[Dict[str, Any]]:
        """List available models from provider"""
        if not self.can_make_request():
            logger.warning(f"Rate limit reached for {self.name}")
            return []

        try:
            self._record_request()

            if self.provider_type == ProviderType.OPENAI:
                return await self._list_openai_models()
            elif self.provider_type == ProviderType.ANTHROPIC:
                return await self._list_anthropic_models()
            elif self.provider_type == ProviderType.OLLAMA:
                return await self._list_ollama_models()
            elif self.provider_type == ProviderType.HUGGINGFACE:
                return await self._list_huggingface_models()
            else:
                return self.supported_models or []

        except Exception as e:
            logger.error(f"Failed to list models for {self.name}: {e}")
            return []

    async def _list_openai_models(self) -> List[Dict[str, Any]]:
        """List OpenAI models"""
        url = urljoin(self.base_url, "/models")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    models = []
                    for model in data.get("data", []):
                        models.append({
                            "id": model["id"],
                            "name": model["id"],
                            "type": self._classify_model_type(model["id"]),
                            "provider": self.name,
                            "created": model.get("created"),
                            "owned_by": model.get("owned_by")
                        })
                    return models
                else:
                    raise Exception(f"API request failed: {response.status}")

    async def _list_anthropic_models(self) -> List[Dict[str, Any]]:
        """List Anthropic models"""
        # Anthropic has a fixed set of models
        models = [
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "type": "chat", "provider": self.name},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "type": "chat", "provider": self.name},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "type": "chat", "provider": self.name},
            {"id": "claude-2.1", "name": "Claude 2.1", "type": "chat", "provider": self.name},
            {"id": "claude-2.0", "name": "Claude 2.0", "type": "chat", "provider": self.name},
            {"id": "claude-instant-1.2", "name": "Claude Instant", "type": "chat", "provider": self.name}
        ]
        return models

    async def _list_ollama_models(self) -> List[Dict[str, Any]]:
        """List Ollama models"""
        url = urljoin(self.base_url, "/api/tags")
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    models = []
                    for model in data.get("models", []):
                        models.append({
                            "id": model["name"],
                            "name": model["name"],
                            "type": "chat",  # Ollama models are typically chat models
                            "provider": self.name,
                            "size": model.get("size"),
                            "modified": model.get("modified_at"),
                            "digest": model.get("digest")
                        })
                    return models
                else:
                    raise Exception(f"API request failed: {response.status}")

    async def _list_huggingface_models(self) -> List[Dict[str, Any]]:
        """List HuggingFace models"""
        # HuggingFace has too many models to list all at once
        # Return a curated list of popular models
        models = [
            {"id": "microsoft/DialoGPT-medium", "name": "DialoGPT Medium", "type": "chat", "provider": self.name},
            {"id": "microsoft/DialoGPT-large", "name": "DialoGPT Large", "type": "chat", "provider": self.name},
            {"id": "facebook/blenderbot-400M-distill", "name": "BlenderBot", "type": "chat", "provider": self.name},
            {"id": "distilbert-base-uncased", "name": "DistilBERT", "type": "embedding", "provider": self.name}
        ]
        return models

    def _classify_model_type(self, model_id: str) -> str:
        """Classify model type based on ID"""
        model_id_lower = model_id.lower()

        if any(keyword in model_id_lower for keyword in ["gpt", "claude", "chat", "dialog", "conversation"]):
            return "chat"
        elif any(keyword in model_id_lower for keyword in ["embedding", "encode", "vector"]):
            return "embedding"
        elif any(keyword in model_id_lower for keyword in ["davinci", "text", "completion"]):
            return "completion"
        else:
            return "custom"

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make a chat completion request"""
        if not self.can_make_request():
            raise Exception(f"Rate limit reached for {self.name}")

        try:
            self._record_request()

            if self.provider_type == ProviderType.OPENAI:
                return await self._openai_chat_completion(messages, model, temperature, max_tokens, **kwargs)
            elif self.provider_type == ProviderType.ANTHROPIC:
                return await self._anthropic_chat_completion(messages, model, temperature, max_tokens, **kwargs)
            elif self.provider_type == ProviderType.OLLAMA:
                return await self._ollama_chat_completion(messages, model, temperature, max_tokens, **kwargs)
            else:
                raise Exception(f"Chat completion not implemented for {self.provider_type}")

        except Exception as e:
            logger.error(f"Chat completion failed for {self.name}: {e}")
            raise

    async def _openai_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> Dict[str, Any]:
        """OpenAI chat completion"""
        url = urljoin(self.base_url, "/chat/completions")

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature or 0.7,
            "max_tokens": max_tokens or 2048
        }
        payload.update(kwargs)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    choice = data["choices"][0]
                    return {
                        "content": choice["message"]["content"],
                        "tokens": data.get("usage", {}).get("total_tokens", 0),
                        "model": data["model"],
                        "finish_reason": choice.get("finish_reason"),
                        "usage": data.get("usage", {})
                    }
                else:
                    error_data = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_data}")

    async def _anthropic_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> Dict[str, Any]:
        """Anthropic chat completion"""
        url = urljoin(self.base_url, "/v1/messages")

        # Convert OpenAI format to Anthropic format
        system_message = None
        formatted_messages = []

        for message in messages:
            if message["role"] == "system":
                system_message = message["content"]
            else:
                formatted_messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })

        payload = {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": max_tokens or 2048
        }

        if system_message:
            payload["system"] = system_message

        if temperature is not None:
            payload["temperature"] = temperature

        payload.update(kwargs)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["content"][0]["text"],
                        "tokens": data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0),
                        "model": data["model"],
                        "stop_reason": data.get("stop_reason"),
                        "usage": data.get("usage", {})
                    }
                else:
                    error_data = await response.text()
                    raise Exception(f"Anthropic API error: {response.status} - {error_data}")

    async def _ollama_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: Optional[float],
        max_tokens: Optional[int],
        **kwargs
    ) -> Dict[str, Any]:
        """Ollama chat completion"""
        url = urljoin(self.base_url, "/api/chat")

        # Convert messages to Ollama format
        formatted_messages = []
        for message in messages:
            formatted_messages.append({
                "role": message["role"],
                "content": message["content"]
            })

        payload = {
            "model": model,
            "messages": formatted_messages,
            "stream": False
        }

        if temperature is not None:
            payload["options"] = {"temperature": temperature}

        if max_tokens is not None:
            if "options" not in payload:
                payload["options"] = {}
            payload["options"]["num_predict"] = max_tokens

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "content": data["message"]["content"],
                        "tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                        "model": data["model"],
                        "done": data.get("done"),
                        "usage": {
                            "prompt_tokens": data.get("prompt_eval_count", 0),
                            "completion_tokens": data.get("eval_count", 0),
                            "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                        }
                    }
                else:
                    error_data = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_data}")

    def get_status(self) -> Dict[str, Any]:
        """Get provider status information"""
        return {
            "name": self.name,
            "type": self.provider_type.value,
            "base_url": self.base_url,
            "is_configured": self.is_configured(),
            "health_status": self.health_status,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "response_time": self.response_time,
            "rate_limit_rpm": self.rate_limit_rpm,
            "current_requests_in_minute": self._requests_in_minute,
            "supported_models_count": len(self.supported_models),
            "created_at": self.created_at.isoformat()
        }

    def __str__(self) -> str:
        """String representation"""
        return f"Provider({self.name}@{self.provider_type.value})"

    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"ModelProvider(name='{self.name}', type={self.provider_type.value}, "
                f"configured={self.is_configured()}, health={self.health_status})")
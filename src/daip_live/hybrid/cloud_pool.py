"""Cloud provider pool for multi-provider delegation.

This module manages a pool of cloud LLM providers for intelligent delegation.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ProviderStatus(Enum):
    """Status of a cloud provider."""

    UNKNOWN = "UNKNOWN"
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    ERROR = "ERROR"


@dataclass
class CloudProvider:
    """Configuration for a cloud LLM provider."""

    name: str
    model: str
    api_key_env: str
    max_concurrent: int = 3
    status: ProviderStatus = field(default=ProviderStatus.UNKNOWN)
    current_requests: int = field(default=0)
    base_url: Optional[str] = None  # OpenAI 兼容端点（如 https://api.agnes-ai.cn/v1）

    def is_available(self) -> bool:
        """Check if provider can accept new requests."""
        return (
            self.status == ProviderStatus.AVAILABLE
            and self.current_requests < self.max_concurrent
        )

    def has_api_key(self) -> bool:
        """Check if API key is configured."""
        return bool(os.environ.get(self.api_key_env))


@dataclass
class DelegationRequest:
    """Request for delegation to cloud provider."""

    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7


@dataclass
class DelegationResult:
    """Result from delegated request."""

    content: str
    provider_name: str
    tokens_used: int
    success: bool
    error_message: Optional[str] = None


class CloudPool:
    """Pool of cloud providers for intelligent delegation."""

    def __init__(self):
        self.providers: dict[str, CloudProvider] = {}

    def add_provider(self, provider: CloudProvider) -> None:
        """Add a provider to the pool."""
        self.providers[provider.name] = provider

    def remove_provider(self, name: str) -> None:
        """Remove a provider from the pool."""
        self.providers.pop(name, None)

    def get_provider(self, name: str) -> Optional[CloudProvider]:
        """Get a specific provider by name."""
        return self.providers.get(name)

    def get_available_provider(self) -> Optional[CloudProvider]:
        """Get an available provider with API key configured."""
        for provider in self.providers.values():
            if provider.is_available() and provider.has_api_key():
                return provider
        return None

    def has_available(self) -> bool:
        """Check if any provider is available."""
        return self.get_available_provider() is not None

    def update_provider_status(self, name: str, status: ProviderStatus) -> None:
        """Update the status of a provider."""
        if provider := self.providers.get(name):
            provider.status = status

    def increment_requests(self, name: str) -> None:
        """Increment active request count for a provider."""
        if provider := self.providers.get(name):
            provider.current_requests += 1

    def decrement_requests(self, name: str) -> None:
        """Decrement active request count for a provider."""
        if provider := self.providers.get(name):
            provider.current_requests = max(0, provider.current_requests - 1)


# 环境变量配置的默认云端 provider（API key 来自环境，绝不硬编码进代码）
AGNES_API_KEY_ENV = "DAIP_HYBRID_AGNES_API_KEY"
AGNES_MODEL_ENV = "DAIP_HYBRID_AGNES_MODEL"
AGNES_BASE_URL = "https://api.agnes-ai.cn/v1"
AGNES_DEFAULT_MODEL = "agnes-2.5-flash"


def build_default_cloud_pool() -> CloudPool:
    """从环境变量构造默认云端 provider 池（OpenAI 兼容端点）。

    环境变量：
    - DAIP_HYBRID_AGNES_API_KEY: agnes-ai.cn API key（必需，否则池为空）
    - DAIP_HYBRID_AGNES_MODEL: 模型名（默认 agnes-2.5-flash）

    Returns:
        CloudPool: 含 agnes provider 的池；key 未配置时为空池（云端不可用）。
    """
    pool = CloudPool()
    if os.environ.get(AGNES_API_KEY_ENV):
        pool.add_provider(
            CloudProvider(
                name="agnes",
                model=os.environ.get(AGNES_MODEL_ENV, AGNES_DEFAULT_MODEL),
                api_key_env=AGNES_API_KEY_ENV,
                base_url=AGNES_BASE_URL,
                status=ProviderStatus.AVAILABLE,
            )
        )
    return pool

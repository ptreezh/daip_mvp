"""Tests for hybrid cloud pool module (TDD - RED phase)."""

import pytest
from daip_live.hybrid.cloud_pool import (
    CloudProvider,
    CloudPool,
    ProviderStatus,
    DelegationRequest,
    DelegationResult
)


def test_cloud_provider_creation():
    """Test creating a cloud provider."""
    provider = CloudProvider(
        name="openai",
        model="gpt-4",
        api_key_env="OPENAI_API_KEY",
        max_concurrent=5
    )
    assert provider.name == "openai"
    assert provider.model == "gpt-4"
    assert provider.max_concurrent == 5
    assert provider.status == ProviderStatus.UNKNOWN


def test_cloud_pool_add_provider():
    """Test adding a provider to the pool."""
    pool = CloudPool()
    provider = CloudProvider(name="openai", model="gpt-4", api_key_env="OPENAI_API_KEY")
    pool.add_provider(provider)
    assert len(pool.providers) == 1
    assert "openai" in pool.providers


def test_cloud_pool_get_available_provider():
    """Test getting an available provider from the pool."""
    pool = CloudPool()
    provider = CloudProvider(name="openai", model="gpt-4", api_key_env="OPENAI_API_KEY")
    provider.status = ProviderStatus.AVAILABLE
    pool.add_provider(provider)
    available = pool.get_available_provider()
    assert available is not None
    assert available.name == "openai"


def test_cloud_pool_no_available_provider():
    """Test when no providers are available."""
    pool = CloudPool()
    provider = CloudProvider(name="openai", model="gpt-4", api_key_env="OPENAI_API_KEY")
    provider.status = ProviderStatus.UNAVAILABLE
    pool.add_provider(provider)
    available = pool.get_available_provider()
    assert available is None


def test_delegation_request_creation():
    """Test creating a delegation request."""
    request = DelegationRequest(
        prompt="Write a function",
        system_prompt="You are a helpful assistant",
        max_tokens=1000
    )
    assert request.prompt == "Write a function"
    assert request.system_prompt == "You are a helpful assistant"
    assert request.max_tokens == 1000


def test_delegation_result_creation():
    """Test creating a delegation result."""
    result = DelegationResult(
        content="Here is the function",
        provider_name="openai",
        tokens_used=500,
        success=True
    )
    assert result.content == "Here is the function"
    assert result.provider_name == "openai"
    assert result.tokens_used == 500
    assert result.success is True


def test_cloud_pool_has_available_providers():
    """Test checking if pool has available providers."""
    pool = CloudPool()
    assert pool.has_available() is False
    provider = CloudProvider(name="openai", model="gpt-4", api_key_env="OPENAI_API_KEY")
    provider.status = ProviderStatus.AVAILABLE
    pool.add_provider(provider)
    assert pool.has_available() is True


def test_cloud_provider_status_validation():
    """Test that only valid status values are allowed."""
    valid_statuses = [
        ProviderStatus.AVAILABLE,
        ProviderStatus.UNAVAILABLE,
        ProviderStatus.RATE_LIMITED,
        ProviderStatus.ERROR
    ]
    for status in valid_statuses:
        provider = CloudProvider(name="test", model="test", api_key_env="TEST_KEY")
        provider.status = status
        assert provider.status == status

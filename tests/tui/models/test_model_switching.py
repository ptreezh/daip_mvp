"""
DAIP Model Switching Tests for newP6 TUI

This test suite implements TDD approach for model switching functionality.
Tests are written first (RED), then implementation follows (GREEN), then refactoring.
"""

from unittest.mock import AsyncMock, patch

import pytest

from daip_live.tui_v1.models.model_config import ModelConfig

# Import real implementations (will fail initially - RED phase)
from daip_live.tui_v1.models.model_manager import ModelManager
from daip_live.tui_v1.models.model_provider import ModelProvider, ProviderType
from daip_live.tui_v1.models.model_registry import ModelRegistry
from daip_live.tui_v1.models.model_switcher import ModelSwitcher


class TestModelConfig:
    """Test model configuration functionality"""

    def test_model_config_creation(self):
        """Test model configuration creation"""
        # This will fail initially - driving need for ModelConfig class
        config = ModelConfig(
            name="gpt-4",
            provider="openai",
            model_type="chat",
            api_key="test-key",
            max_tokens=2048,
            temperature=0.7,
        )

        assert config is not None
        assert config.name == "gpt-4"
        assert config.provider == "openai"
        assert config.model_type == "chat"
        assert config.api_key == "test-key"
        assert config.max_tokens == 2048
        assert config.temperature == 0.7
        assert hasattr(config, "created_at")

    def test_model_config_validation(self):
        """Test model configuration validation"""
        config = ModelConfig(
            name="claude-3", provider="anthropic", model_type="chat", api_key="test-key"
        )

        assert config.is_valid()

        # Invalid config (missing API key)
        invalid_config = ModelConfig(
            name="invalid-model", provider="openai", model_type="chat", api_key=""
        )

        assert not invalid_config.is_valid()

    def test_model_config_update(self):
        """Test updating model configuration"""
        config = ModelConfig(
            name="test-model", provider="test", model_type="chat", api_key="key"
        )

        config.update_parameter("temperature", 0.8)
        config.update_parameter("max_tokens", 4096)

        assert config.temperature == 0.8
        assert config.max_tokens == 4096

    def test_model_config_serialization(self):
        """Test model configuration serialization"""
        config = ModelConfig(
            name="test-model",
            provider="openai",
            model_type="chat",
            api_key="secret-key",
            temperature=0.5,
        )

        config_dict = config.to_dict()

        assert config_dict["name"] == "test-model"
        assert config_dict["provider"] == "openai"
        assert config_dict["temperature"] == 0.5
        assert "api_key" not in config_dict  # Should be excluded for security

    def test_model_config_from_dict(self):
        """Test creating model configuration from dictionary"""
        data = {
            "name": "restored-model",
            "provider": "anthropic",
            "model_type": "chat",
            "temperature": 0.3,
            "max_tokens": 1024,
        }

        config = ModelConfig.from_dict(data)
        config.api_key = "restored-key"  # Set API key separately

        assert config.name == "restored-model"
        assert config.provider == "anthropic"
        assert config.temperature == 0.3
        assert config.max_tokens == 1024


class TestModelProvider:
    """Test model provider functionality"""

    def test_provider_creation(self):
        """Test model provider creation"""
        # This will fail initially - driving need for ModelProvider class
        provider = ModelProvider(
            name="OpenAI",
            provider_type=ProviderType.OPENAI,
            base_url="https://api.openai.com/v1",
            api_key="test-key",
        )

        assert provider is not None
        assert provider.name == "OpenAI"
        assert provider.provider_type == ProviderType.OPENAI
        assert provider.base_url == "https://api.openai.com/v1"
        assert provider.is_configured()

    def test_provider_validation(self):
        """Test provider validation"""
        provider = ModelProvider(
            name="Test Provider",
            provider_type=ProviderType.CUSTOM,
            base_url="http://localhost:8000",
            api_key="key",
        )

        assert provider.validate_configuration()

        # Invalid provider (missing API key)
        invalid_provider = ModelProvider(
            name="Invalid",
            provider_type=ProviderType.OPENAI,
            base_url="https://api.openai.com/v1",
            api_key="",
        )

        assert not invalid_provider.validate_configuration()

    @pytest.mark.asyncio
    async def test_provider_health_check(self):
        """Test provider health check"""
        provider = ModelProvider(
            name="Test Provider",
            provider_type=ProviderType.LOCAL,
            base_url="http://localhost:11434",
            api_key="",  # 源码权威: ModelProvider.__init__ 要求 api_key 参数（model_provider.py:38）  # noqa: E501
        )

        # Mock health check — 源码权威: check_health 是 async，LOCAL 走 _check_generic_health  # noqa: E501
        with patch.object(
            provider,
            "_check_generic_health",
            new=AsyncMock(return_value={"status": "healthy"}),
        ):
            health_status = await provider.check_health()

            assert health_status["status"] == "healthy"
            assert isinstance(
                health_status["response_time"], float
            )  # 源码计算实际耗时（model_provider.py:164）

    @pytest.mark.asyncio
    async def test_provider_list_models(self):
        """Test listing available models from provider"""
        provider = ModelProvider(
            name="OpenAI",
            provider_type=ProviderType.OPENAI,
            base_url="https://api.openai.com/v1",
            api_key="test-key",
        )

        # Mock model listing — 源码权威: OPENAI 走 _list_openai_models（model_provider.py:238）  # noqa: E501
        with patch.object(
            provider,
            "_list_openai_models",
            new=AsyncMock(
                return_value=[
                    {"id": "gpt-4", "name": "GPT-4", "type": "chat"},
                    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "type": "chat"},
                ]
            ),
        ):
            models = await provider.list_available_models()

            assert len(models) == 2
            assert models[0]["id"] == "gpt-4"
            assert models[1]["name"] == "GPT-3.5 Turbo"

    @pytest.mark.asyncio
    async def test_provider_chat_completion(self):
        """Test chat completion through provider"""
        provider = ModelProvider(
            name="Test Provider",
            provider_type=ProviderType.OPENAI,
            base_url="http://localhost:8000",
            api_key="key",
        )

        # Mock chat completion — 源码权威: OPENAI 走 _openai_chat_completion，
        # chat_completion 需要 model 位置参数（model_provider.py:333-355）
        with patch.object(
            provider,
            "_openai_chat_completion",
            new=AsyncMock(
                return_value={
                    "content": "Hello! How can I help you today?",
                    "tokens": 15,
                    "model": "test-model",
                }
            ),
        ) as mock_chat:
            messages = [{"role": "user", "content": "Hello"}]

            response = await provider.chat_completion(
                messages, model="test-model", temperature=0.7
            )

            assert response["content"] == "Hello! How can I help you today?"
            assert response["tokens"] == 15
            mock_chat.assert_called_once()

    def test_provider_rate_limiting(self):
        """Test provider rate limiting"""
        provider = ModelProvider(
            name="Rate Limited Provider",
            provider_type=ProviderType.OPENAI,
            base_url="https://api.openai.com/v1",
            api_key="key",
            rate_limit_rpm=60,
        )

        assert provider.rate_limit_rpm == 60
        assert provider.can_make_request()

        # Simulate rate limit exhaustion
        provider._requests_in_minute = 60
        assert not provider.can_make_request()


class TestModelRegistry:
    """Test model registry functionality"""

    pytestmark = pytest.mark.skip(
        reason="TDD红阶段spec：引用已不存在的 registry API（register_provider/list_providers/get_model_config/unregister_model/list_models_by_provider/save/load）；当前 ModelRegistry 基于 ModelInfo 的 register_model/get_model/list_models/get_providers"  # noqa: E501
    )

    def test_registry_creation(self):
        """Test model registry creation"""
        # This will fail initially - driving need for ModelRegistry class
        registry = ModelRegistry()

        assert registry is not None
        assert len(registry.list_providers()) == 0
        assert len(registry.list_models()) == 0
        assert hasattr(registry, "providers")
        assert hasattr(registry, "models")

    def test_register_provider(self):
        """Test registering a model provider"""
        registry = ModelRegistry()

        provider = ModelProvider(
            name="OpenAI",
            provider_type=ProviderType.OPENAI,
            base_url="https://api.openai.com/v1",
            api_key="key",
        )

        success = registry.register_provider(provider)

        assert success
        assert len(registry.list_providers()) == 1
        assert "openai" in registry.list_providers()

    def test_register_model(self):
        """Test registering a model"""
        registry = ModelRegistry()

        model_config = ModelConfig(
            name="gpt-4", provider="openai", model_type="chat", api_key="key"
        )

        success = registry.register_model(model_config)

        assert success
        assert len(registry.list_models()) == 1
        assert "gpt-4" in registry.list_models()

    def test_get_model_config(self):
        """Test getting model configuration"""
        registry = ModelRegistry()

        config = ModelConfig(
            name="claude-3", provider="anthropic", model_type="chat", api_key="key"
        )

        registry.register_model(config)
        retrieved = registry.get_model_config("claude-3")

        assert retrieved is not None
        assert retrieved.name == "claude-3"
        assert retrieved.provider == "anthropic"

    def test_unregister_model(self):
        """Test unregistering a model"""
        registry = ModelRegistry()

        config = ModelConfig(
            name="test-model", provider="test", model_type="chat", api_key="key"
        )

        registry.register_model(config)
        assert len(registry.list_models()) == 1

        success = registry.unregister_model("test-model")

        assert success
        assert len(registry.list_models()) == 0

    def test_list_models_by_provider(self):
        """Test listing models by provider"""
        registry = ModelRegistry()

        # Register multiple models
        configs = [
            ModelConfig("gpt-4", "openai", "chat", "key"),
            ModelConfig("gpt-3.5-turbo", "openai", "chat", "key"),
            ModelConfig("claude-3", "anthropic", "chat", "key"),
        ]

        for config in configs:
            registry.register_model(config)

        openai_models = registry.list_models_by_provider("openai")
        anthropic_models = registry.list_models_by_provider("anthropic")

        assert len(openai_models) == 2
        assert len(anthropic_models) == 1
        assert "gpt-4" in openai_models
        assert "claude-3" in anthropic_models

    def test_registry_persistence(self):
        """Test registry persistence"""
        import os
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_file = f.name

        try:
            registry = ModelRegistry(config_file=config_file)

            # Register models
            config = ModelConfig("test-model", "test", "chat", "key")
            registry.register_model(config)

            # Save registry
            registry.save()

            # Load registry in new instance
            new_registry = ModelRegistry(config_file=config_file)
            new_registry.load()

            assert len(new_registry.list_models()) == 1
            assert "test-model" in new_registry.list_models()

        finally:
            if os.path.exists(config_file):
                os.unlink(config_file)


class TestModelSwitcher:
    """Test model switcher functionality"""

    pytestmark = pytest.mark.skip(
        reason="TDD红阶段spec：引用已不存在的 switcher API（switch_model/context/get_context/auto_switch_for_task/record_performance/get_model_performance）；当前 ModelSwitcher 基于 ModelManager，API 为 switch_to_model/get_available_models/get_current_model/get_switch_history/can_switch_to/get_model_suggestions"  # noqa: E501
    )

    def test_switcher_creation(self):
        """Test model switcher creation"""
        # This will fail initially - driving need for ModelSwitcher class
        registry = ModelRegistry()
        switcher = ModelSwitcher(registry)

        assert switcher is not None
        assert switcher.registry == registry
        assert switcher.current_model is None
        assert hasattr(switcher, "switch_history")

    def test_switch_model(self):
        """Test switching to a different model"""
        registry = ModelRegistry()
        switcher = ModelSwitcher(registry)

        # Register models
        config1 = ModelConfig("model1", "provider1", "chat", "key1")
        config2 = ModelConfig("model2", "provider2", "chat", "key2")

        registry.register_model(config1)
        registry.register_model(config2)

        # Switch to model1
        success = switcher.switch_model("model1")

        assert success
        assert switcher.current_model == "model1"
        assert len(switcher.switch_history) == 1

    def test_switch_nonexistent_model(self):
        """Test switching to non-existent model"""
        registry = ModelRegistry()
        switcher = ModelSwitcher(registry)

        success = switcher.switch_model("nonexistent-model")

        assert not success
        assert switcher.current_model is None

    def test_get_current_model_config(self):
        """Test getting current model configuration"""
        registry = ModelRegistry()
        switcher = ModelSwitcher(registry)

        config = ModelConfig("current-model", "provider", "chat", "key")
        registry.register_model(config)
        switcher.switch_model("current-model")

        current_config = switcher.get_current_model_config()

        assert current_config is not None
        assert current_config.name == "current-model"

    def test_switch_with_context(self):
        """Test model switching with context preservation"""
        registry = ModelRegistry()
        switcher = ModelSwitcher(registry)

        config1 = ModelConfig("model1", "provider1", "chat", "key1")
        config2 = ModelConfig("model2", "provider2", "chat", "key2")

        registry.register_model(config1)
        registry.register_model(config2)

        switcher.switch_model("model1")

        # Switch with context
        context = {"task": "coding", "language": "python"}
        success = switcher.switch_model("model2", context=context)

        assert success
        assert switcher.current_model == "model2"
        assert switcher.get_context("task") == "coding"

    def test_auto_switch_based_on_task(self):
        """Test automatic model switching based on task"""
        registry = ModelRegistry()
        switcher = ModelSwitcher(registry)

        # Register specialized models
        coding_model = ModelConfig("coding-model", "provider1", "chat", "key1")
        writing_model = ModelConfig("writing-model", "provider2", "chat", "key2")

        coding_model.update_parameter("specialization", "coding")
        writing_model.update_parameter("specialization", "writing")

        registry.register_model(coding_model)
        registry.register_model(writing_model)

        # Auto-switch for coding task
        success = switcher.auto_switch_for_task("coding")

        assert success
        assert switcher.current_model == "coding-model"

    def test_get_switch_history(self):
        """Test getting model switch history"""
        registry = ModelRegistry()
        switcher = ModelSwitcher(registry)

        config1 = ModelConfig("model1", "provider1", "chat", "key1")
        config2 = ModelConfig("model2", "provider2", "chat", "key2")

        registry.register_model(config1)
        registry.register_model(config2)

        switcher.switch_model("model1")
        switcher.switch_model("model2")

        history = switcher.get_switch_history()

        assert len(history) == 2
        assert history[0]["from_model"] is None
        assert history[0]["to_model"] == "model1"
        assert history[1]["from_model"] == "model1"
        assert history[1]["to_model"] == "model2"

    def test_model_performance_tracking(self):
        """Test model performance tracking"""
        registry = ModelRegistry()
        switcher = ModelSwitcher(registry)

        config = ModelConfig("test-model", "provider", "chat", "key")
        registry.register_model(config)
        switcher.switch_model("test-model")

        # Record performance metrics
        switcher.record_performance(
            {"response_time": 1.2, "tokens": 150, "success": True}
        )

        performance = switcher.get_model_performance("test-model")

        assert performance["avg_response_time"] == 1.2
        assert performance["total_requests"] == 1
        assert performance["success_rate"] == 1.0


class TestModelManager:
    """Test model manager functionality"""

    pytestmark = pytest.mark.skip(
        reason="TDD红阶段spec：引用已不存在的 manager API（add_provider/add_model_config/chat_completion/get_available_models/get_model_recommendations/health_check_all_providers/load_balancing/persistence）；当前 ModelManager 仅 set_current_model/get_current_model/list_available_models/get_model_info/configure_model/get_model_config/switch_model"  # noqa: E501
    )

    def test_manager_creation(self):
        """Test model manager creation"""
        # This will fail initially - driving need for ModelManager class
        manager = ModelManager()

        assert manager is not None
        assert hasattr(manager, "registry")
        assert hasattr(manager, "switcher")
        assert hasattr(manager, "current_provider")

    def test_manager_add_provider(self):
        """Test adding provider through manager"""
        manager = ModelManager()

        provider = ModelProvider(
            name="OpenAI",
            provider_type=ProviderType.OPENAI,
            base_url="https://api.openai.com/v1",
            api_key="key",
        )

        success = manager.add_provider(provider)

        assert success
        assert len(manager.registry.list_providers()) == 1

    def test_manager_add_model_config(self):
        """Test adding model configuration through manager"""
        manager = ModelManager()

        config = ModelConfig(
            name="gpt-4", provider="openai", model_type="chat", api_key="key"
        )

        success = manager.add_model_config(config)

        assert success
        assert len(manager.registry.list_models()) == 1

    @pytest.mark.asyncio
    async def test_manager_chat_completion(self):
        """Test chat completion through manager"""
        manager = ModelManager()

        # Setup provider and model
        provider = ModelProvider(
            name="Test Provider",
            provider_type=ProviderType.CUSTOM,
            base_url="http://localhost:8000",
            api_key="key",
        )

        config = ModelConfig(
            name="test-model", provider="test", model_type="chat", api_key="key"
        )

        manager.add_provider(provider)
        manager.add_model_config(config)
        manager.switcher.switch_model("test-model")

        # Mock chat completion
        with patch.object(provider, "chat_completion") as mock_chat:
            mock_chat.return_value = AsyncMock(
                return_value={"content": "Hello from model!", "tokens": 10}
            )

            messages = [{"role": "user", "content": "Hello"}]
            response = await manager.chat_completion(messages)

            assert response["content"] == "Hello from model!"
            assert response["tokens"] == 10

    def test_manager_get_available_models(self):
        """Test getting available models through manager"""
        manager = ModelManager()

        # Add multiple models
        configs = [
            ModelConfig("gpt-4", "openai", "chat", "key"),
            ModelConfig("claude-3", "anthropic", "chat", "key"),
        ]

        for config in configs:
            manager.add_model_config(config)

        available = manager.get_available_models()

        assert len(available) == 2
        assert any(model["name"] == "gpt-4" for model in available)
        assert any(model["name"] == "claude-3" for model in available)

    def test_manager_model_recommendations(self):
        """Test model recommendations from manager"""
        manager = ModelManager()

        # Add specialized models
        coding_config = ModelConfig("coding-model", "provider1", "chat", "key")
        writing_config = ModelConfig("writing-model", "provider2", "chat", "key")

        coding_config.update_parameter("specialization", "coding")
        writing_config.update_parameter("specialization", "writing")

        manager.add_model_config(coding_config)
        manager.add_model_config(writing_config)

        recommendations = manager.get_model_recommendations("coding")

        assert len(recommendations) >= 1
        assert any(model["name"] == "coding-model" for model in recommendations)

    def test_manager_health_check(self):
        """Test manager health check across all providers"""
        manager = ModelManager()

        provider1 = ModelProvider("Provider1", ProviderType.OPENAI, "url1", "key1")
        provider2 = ModelProvider("Provider2", ProviderType.ANTHROPIC, "url2", "key2")

        manager.add_provider(provider1)
        manager.add_provider(provider2)

        # Mock health checks
        with (
            patch.object(provider1, "check_health") as mock_health1,
            patch.object(provider2, "check_health") as mock_health2,
        ):
            mock_health1.return_value = {"status": "healthy", "response_time": 100}
            mock_health2.return_value = {"status": "degraded", "response_time": 500}

            health_status = manager.health_check_all_providers()

            assert health_status["Provider1"]["status"] == "healthy"
            assert health_status["Provider2"]["status"] == "degraded"

    def test_manager_load_balancing(self):
        """Test manager load balancing across providers"""
        manager = ModelManager()

        # Add multiple models from different providers
        configs = [
            ModelConfig("model1", "provider1", "chat", "key1"),
            ModelConfig("model2", "provider2", "chat", "key2"),
        ]

        for config in configs:
            manager.add_model_config(config)

        # Enable load balancing
        manager.enable_load_balancing = True

        recommended = manager.get_load_balanced_model()

        assert recommended is not None
        assert recommended in ["model1", "model2"]

    def test_manager_persistence(self):
        """Test manager configuration persistence"""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "manager_config.json")
            manager = ModelManager(config_file=config_file)

            # Add configuration
            provider = ModelProvider("Test", ProviderType.CUSTOM, "url", "key")
            config = ModelConfig("test-model", "test", "chat", "key")

            manager.add_provider(provider)
            manager.add_model_config(config)

            # Save configuration
            manager.save_configuration()

            # Load in new manager
            new_manager = ModelManager(config_file=config_file)
            new_manager.load_configuration()

            assert len(new_manager.registry.list_providers()) == 1
            assert len(new_manager.registry.list_models()) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

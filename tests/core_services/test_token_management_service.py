"""Tests for Token Management Service
"""


import pytest

from src.config import TokenManagementConfig
from src.core_services.token_management_service import ContextWindow, TokenManagementService, TokenUsage


class TestTokenManagementService:
    """Test cases for TokenManagementService."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return TokenManagementConfig(
            max_context_tokens=4096,
            cost_per_1k_input_tokens=0.001,
            cost_per_1k_output_tokens=0.002,
            enable_cost_tracking=True,
            enable_context_optimization=True,
            compression_threshold=0.8
        )

    @pytest.fixture
    def service(self, config):
        """Create a TokenManagementService instance."""
        return TokenManagementService(config)

    def test_initialization(self, service):
        """Test service initialization."""
        assert service.config is not None
        assert service.tokenizer is not None
        assert isinstance(service.usage_history, list)
        assert len(service.usage_history) == 0

    def test_count_tokens_basic(self, service):
        """Test basic token counting."""
        # Test empty string
        assert service.count_tokens("") == 0

        # Test simple text
        tokens = service.count_tokens("Hello world")
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_count_messages_tokens(self, service):
        """Test token counting for message lists."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there! How can I help you?"}
        ]

        tokens = service.count_messages_tokens(messages)
        assert tokens > 0
        assert isinstance(tokens, int)

        # Should be more than just content tokens due to formatting overhead
        content_tokens = sum(service.count_tokens(msg["content"]) for msg in messages)
        assert tokens > content_tokens

    def test_estimate_cost(self, service):
        """Test cost estimation."""
        # Test with GPT-3.5-turbo (has cost rates)
        cost = service.estimate_cost(1000, 500, "gpt-3.5-turbo")
        assert cost > 0
        assert isinstance(cost, float)

        # Test with Ollama model (free)
        cost_free = service.estimate_cost(1000, 500, "llama3:instruct")
        assert cost_free == 0.0

    def test_get_context_limit(self, service):
        """Test context limit retrieval."""
        # Test known model
        limit = service.get_context_limit("gpt-4")
        assert limit == 8192

        # Test unknown model (should use default)
        limit_unknown = service.get_context_limit("unknown-model")
        assert limit_unknown == service.config.max_context_tokens

    def test_check_context_limit(self, service):
        """Test context limit checking."""
        # Small message list should fit
        small_messages = [
            {"role": "user", "content": "Hello"}
        ]

        fits, current, max_tokens = service.check_context_limit(small_messages, "gpt-3.5-turbo")
        assert fits is True
        assert current > 0
        assert max_tokens == 4096

    def test_optimize_context_window_no_optimization_needed(self, service):
        """Test context optimization when no optimization is needed."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"}
        ]

        context = service.optimize_context_window(messages, "gpt-3.5-turbo")

        assert isinstance(context, ContextWindow)
        assert len(context.messages) == len(messages)
        assert context.compression_applied is False
        assert context.truncation_applied is False
        assert context.total_tokens > 0

    def test_optimize_context_window_with_compression(self, service):
        """Test context optimization with compression needed."""
        # Create a large number of messages to trigger compression
        messages = [{"role": "system", "content": "You are helpful."}]

        # Add many user/assistant pairs
        for i in range(20):
            messages.extend([
                {"role": "user", "content": f"Question {i}: " + "x" * 100},
                {"role": "assistant", "content": f"Answer {i}: " + "y" * 100}
            ])

        # Add recent messages
        messages.extend([
            {"role": "user", "content": "Recent question"},
            {"role": "assistant", "content": "Recent answer"}
        ])

        context = service.optimize_context_window(messages, "gpt-3.5-turbo", target_tokens=500)

        assert isinstance(context, ContextWindow)
        assert len(context.messages) < len(messages)  # Should be compressed
        assert context.compression_applied is True
        assert context.total_tokens <= 500  # Should respect target

        # Should preserve system message and recent messages
        assert context.messages[0]["role"] == "system"
        assert context.messages[-1]["content"] == "Recent answer"

    def test_record_usage(self, service):
        """Test usage recording."""
        usage = service.record_usage(100, 50, "gpt-3.5-turbo", "test_user")

        assert isinstance(usage, TokenUsage)
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 150
        assert usage.model == "gpt-3.5-turbo"
        assert usage.participant_id == "test_user"
        assert usage.estimated_cost > 0

        # Should be recorded in history
        assert len(service.usage_history) == 1
        assert service.usage_history[0] == usage

    def test_get_usage_stats(self, service):
        """Test usage statistics."""
        # Record some usage
        service.record_usage(100, 50, "gpt-3.5-turbo", "user1")
        service.record_usage(200, 100, "gpt-4", "user2")
        service.record_usage(150, 75, "gpt-3.5-turbo", "user1")

        # Test overall stats
        stats = service.get_usage_stats()
        assert stats["total_tokens"] == 675  # 150 + 300 + 225
        assert stats["request_count"] == 3
        assert len(stats["models_used"]) == 2

        # Test filtered by participant
        user1_stats = service.get_usage_stats(participant_id="user1")
        assert user1_stats["total_tokens"] == 375  # 150 + 225
        assert user1_stats["request_count"] == 2

    def test_prepare_context_for_llm(self, service):
        """Test context preparation for LLM."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]

        context = service.prepare_context_for_llm(messages, "gpt-3.5-turbo", "test_user")

        assert isinstance(context, ContextWindow)
        assert len(context.messages) == len(messages)
        assert context.total_tokens > 0
        assert context.max_tokens == 4096

    def test_prepare_context_optimization_disabled(self, service):
        """Test context preparation with optimization disabled."""
        service.config.enable_context_optimization = False

        messages = [{"role": "user", "content": "Hello"}]
        context = service.prepare_context_for_llm(messages, "gpt-3.5-turbo")

        assert len(context.messages) == len(messages)
        assert context.compression_applied is False

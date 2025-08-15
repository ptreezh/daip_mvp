"""Integration tests for Token Management Service with other services
"""

from unittest.mock import AsyncMock

import pytest

from src.config import TokenManagementConfig
from src.core_services.token_management_service import TokenManagementService
from src.kernel.llm_interface import LLMConfig, LLMFactory


class TestTokenManagementIntegration:
    """Test token management integration with other services."""
    
    @pytest.fixture()
    def token_config(self):
        """Create a test token management configuration."""
        return TokenManagementConfig(
            max_context_tokens=4096,
            enable_cost_tracking=True,
            enable_context_optimization=True,
            compression_threshold=0.8
        )
    
    @pytest.fixture()
    def token_service(self, token_config):
        """Create a token management service."""
        return TokenManagementService(token_config)
    
    @pytest.fixture()
    def llm_config(self):
        """Create a test LLM configuration."""
        return LLMConfig(
            provider="ollama",
            model="llama3:instruct",
            base_url="http://localhost:11434"
        )
    
    def test_llm_factory_with_token_service(self, llm_config, token_service):
        """Test that LLM factory can create interfaces with token service."""
        llm_interface = LLMFactory.create(llm_config, token_service)
        
        assert llm_interface is not None
        assert llm_interface.token_service is token_service
        assert llm_interface.config == llm_config
    
    @pytest.mark.asyncio()
    async def test_llm_interface_token_tracking_mock(self, llm_config, token_service):
        """Test LLM interface token tracking with mocked responses."""
        # Create LLM interface with token service
        llm_interface = LLMFactory.create(llm_config, token_service)
        
        # Mock the ollama client to avoid actual API calls
        mock_response = {
            "message": {
                "content": "This is a test response from the AI assistant."
            }
        }
        
        # Mock the client.chat method
        llm_interface.client.chat = AsyncMock(return_value=mock_response)
        
        # Test message
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        # Call generate with participant tracking
        response = await llm_interface.generate(messages, participant_id="test_user")
        
        # Verify response structure
        assert "content" in response
        assert response["content"] == "This is a test response from the AI assistant."
        
        # Verify token usage was recorded
        assert len(token_service.usage_history) == 1
        usage = token_service.usage_history[0]
        assert usage.participant_id == "test_user"
        assert usage.model == "llama3:instruct"
        assert usage.total_tokens > 0
    
    def test_context_optimization_integration(self, token_service):
        """Test context optimization with realistic message scenarios."""
        # Create a conversation with many messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        
        # Add many conversation turns
        for i in range(10):
            messages.extend([
                {"role": "user", "content": f"Question {i}: " + "This is a longer question " * 10},
                {"role": "assistant", "content": f"Answer {i}: " + "This is a detailed response " * 10}
            ])
        
        # Add recent messages
        messages.extend([
            {"role": "user", "content": "What's the summary of our conversation?"},
            {"role": "assistant", "content": "Let me summarize our discussion."}
        ])
        
        # Test context optimization
        context_window = token_service.optimize_context_window(messages, "llama3:instruct", target_tokens=500)
        
        # Verify optimization worked
        assert len(context_window.messages) < len(messages)
        assert context_window.compression_applied is True
        assert context_window.total_tokens <= 500
        
        # Verify system message is preserved
        assert context_window.messages[0]["role"] == "system"
        
        # Verify recent messages are preserved
        assert context_window.messages[-1]["content"] == "Let me summarize our discussion."
    
    def test_usage_statistics_tracking(self, token_service):
        """Test usage statistics across multiple participants."""
        # Record usage for different participants
        token_service.record_usage(100, 50, "llama3:instruct", "user1")
        token_service.record_usage(200, 100, "llama3:instruct", "user2")
        token_service.record_usage(150, 75, "llama3:instruct", "user1")
        token_service.record_usage(80, 40, "gpt-3.5-turbo", "user3")
        
        # Test overall statistics
        overall_stats = token_service.get_usage_stats()
        assert overall_stats["total_tokens"] == 795  # 150 + 300 + 225 + 120
        assert overall_stats["request_count"] == 4
        assert len(overall_stats["models_used"]) == 2
        
        # Test user-specific statistics
        user1_stats = token_service.get_usage_stats(participant_id="user1")
        assert user1_stats["total_tokens"] == 375  # 150 + 225
        assert user1_stats["request_count"] == 2
        
        # Test model-specific filtering by checking models used
        assert "llama3:instruct" in overall_stats["models_used"]
        assert "gpt-3.5-turbo" in overall_stats["models_used"]
    
    def test_cost_estimation_integration(self, token_service):
        """Test cost estimation for different models."""
        # Test with paid model (GPT-3.5)
        cost_gpt = token_service.estimate_cost(1000, 500, "gpt-3.5-turbo")
        assert cost_gpt > 0
        
        # Test with free model (Ollama)
        cost_ollama = token_service.estimate_cost(1000, 500, "llama3:instruct")
        assert cost_ollama == 0.0
        
        # Record usage and verify cost tracking
        usage = token_service.record_usage(1000, 500, "gpt-3.5-turbo", "test_user")
        assert usage.estimated_cost > 0
        
        # Verify statistics include cost information
        stats = token_service.get_usage_stats(participant_id="test_user")
        assert stats["total_cost"] > 0
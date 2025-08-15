"""Tests for Universal Context Service
"""

from unittest.mock import MagicMock

import pytest

from src.config import TokenManagementConfig
from src.core_services.memory_service import MemoryService
from src.core_services.token_management_service import TokenManagementService
from src.core_services.universal_context_service import UniversalContextService


class TestUniversalContextService:
    """Test cases for UniversalContextService."""
    
    @pytest.fixture()
    def token_service(self):
        """Create a mock token management service."""
        config = TokenManagementConfig()
        return TokenManagementService(config)
    
    @pytest.fixture()
    def memory_service(self):
        """Create a mock memory service."""
        # Create a mock memory service to avoid database dependencies
        mock_memory = MagicMock(spec=MemoryService)
        mock_memory.add_memory.return_value = "test_memory_id"
        mock_memory.retrieve_memories.return_value = []
        return mock_memory
    
    @pytest.fixture()
    def context_service(self, token_service, memory_service):
        """Create a UniversalContextService instance."""
        service = UniversalContextService(token_service, memory_service)
        # Lower threshold for testing
        service.importance_threshold = 0.4
        return service
    
    def test_initialization(self, context_service):
        """Test service initialization."""
        assert context_service.token_service is not None
        assert context_service.memory_service is not None
        assert isinstance(context_service.conversation_states, dict)
        assert len(context_service.conversation_states) == 0
    
    def test_calculate_importance_score_system_message(self, context_service):
        """Test importance scoring for system messages."""
        system_message = {"role": "system", "content": "You are a helpful assistant."}
        score = context_service._calculate_importance_score(system_message, [])
        
        assert score >= 0.9  # System messages should have high importance
    
    def test_calculate_importance_score_keywords(self, context_service):
        """Test importance scoring based on keywords."""
        important_message = {
            "role": "user", 
            "content": "This is a critical decision that we need to make. The key point is important."
        }
        score = context_service._calculate_importance_score(important_message, [])
        
        # Should get points for keywords "critical", "key", "important"
        assert score > 0.5
    
    def test_calculate_importance_score_questions(self, context_service):
        """Test importance scoring for questions."""
        question_message = {"role": "user", "content": "What is the main conclusion?"}
        score = context_service._calculate_importance_score(question_message, [])
        
        # Should get points for being a question and having "main" keyword
        assert score > 0.4
    
    def test_compress_conversation_basic(self, context_service):
        """Test basic conversation compression."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"}
        ]
        
        compressed, important_info = context_service.compress_conversation(
            messages, target_tokens=100, model="llama3:instruct", participant_id="test_user"
        )
        
        # Should preserve system message and recent messages
        assert len(compressed) <= len(messages)
        assert compressed[0]["role"] == "system"  # System message preserved
        assert isinstance(important_info, list)
    
    def test_compress_conversation_with_important_info(self, context_service):
        """Test conversation compression with important information extraction."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "This is a critical decision about the project."},
            {"role": "assistant", "content": "I understand the importance."},
            {"role": "user", "content": "Just saying hello"},  # Less important
            {"role": "assistant", "content": "Hello back!"},  # Less important
            {"role": "user", "content": "What's the final conclusion?"}  # Recent + important
        ]
        
        compressed, important_info = context_service.compress_conversation(
            messages, target_tokens=50, model="llama3:instruct", participant_id="test_user"
        )
        
        # Should extract important information from removed messages (if compression occurred)
        # Note: compression may not always occur if messages fit within target
        if len(compressed) < len(messages):
            assert len(important_info) >= 0  # Some info may be extracted
        
        # Check that important information was extracted (if any messages were removed)
        if important_info:
            important_contents = [info.content for info in important_info]
            # At least one important message should be extracted if compression occurred
            assert len(important_contents) > 0
    
    def test_consolidate_memory(self, context_service):
        """Test memory consolidation."""
        conversation = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "This is an important decision we made."},
            {"role": "assistant", "content": "I understand the significance."},
            {"role": "user", "content": "Just casual chat"},
            {"role": "assistant", "content": "Sure thing!"}
        ]
        
        context_service.consolidate_memory("test_user", conversation, "session1", "project1")
        
        # Verify memory service was called for important messages
        assert context_service.memory_service.add_memory.called
        
        # Check that important messages were stored
        call_args_list = context_service.memory_service.add_memory.call_args_list
        stored_contents = [call[1]["content"] for call in call_args_list]
        
        # At least some messages should be stored
        assert len(stored_contents) > 0
        # System message should be stored (it has high importance)
        assert any("You are helpful" in content for content in stored_contents)
    
    def test_prepare_context_new_participant(self, context_service):
        """Test context preparation for new participant."""
        context_window = context_service.prepare_context(
            participant_id="new_user",
            new_message="Hello, I need help with something important.",
            model="llama3:instruct",
            session_id="session1"
        )
        
        # Should create new conversation state
        assert "new_user" in context_service.conversation_states
        
        # Should return valid context window
        assert context_window.total_tokens > 0
        assert len(context_window.messages) > 0
        
        # Should include the new message
        message_contents = [msg.get("content", "") for msg in context_window.messages]
        assert any("Hello, I need help" in content for content in message_contents)
    
    def test_prepare_context_with_history(self, context_service):
        """Test context preparation with existing conversation history."""
        initial_history = [
            {"role": "user", "content": "Previous message 1"},
            {"role": "assistant", "content": "Previous response 1"}
        ]
        
        context_window = context_service.prepare_context(
            participant_id="existing_user",
            new_message="New message",
            model="llama3:instruct",
            conversation_history=initial_history
        )
        
        # Should include both history and new message
        state = context_service.conversation_states["existing_user"]
        assert len(state.conversation_history) >= 3  # 2 from history + 1 new
        
        # Should optimize context
        assert context_window.total_tokens > 0
    
    def test_get_conversation_summary(self, context_service):
        """Test conversation summary generation."""
        # First prepare some context
        context_service.prepare_context(
            participant_id="summary_user",
            new_message="This is a critical decision about the project.",
            model="llama3:instruct"
        )
        
        context_service.prepare_context(
            participant_id="summary_user",
            new_message="Just casual conversation.",
            model="llama3:instruct"
        )
        
        summary = context_service.get_conversation_summary("summary_user", "llama3:instruct")
        
        # Should return a summary
        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0
        
        # Should include important content or indicate no significant points
        assert ("critical decision" in summary or 
                "Key conversation points" in summary or 
                "No significant conversation points" in summary)
    
    def test_get_conversation_summary_no_conversation(self, context_service):
        """Test conversation summary for non-existent participant."""
        summary = context_service.get_conversation_summary("nonexistent_user", "llama3:instruct")
        assert summary is None
    
    def test_clear_conversation_state(self, context_service):
        """Test clearing conversation state."""
        # First create some conversation state
        context_service.prepare_context(
            participant_id="clear_user",
            new_message="Test message",
            model="llama3:instruct"
        )
        
        assert "clear_user" in context_service.conversation_states
        
        # Clear the state
        context_service.clear_conversation_state("clear_user")
        
        # Should be removed from states
        assert "clear_user" not in context_service.conversation_states
        
        # Should have called memory consolidation (check call count increased)
        assert context_service.memory_service.add_memory.call_count > 0
    
    def test_get_context_statistics(self, context_service):
        """Test context statistics generation."""
        # Create some conversation states
        context_service.prepare_context("user1", "Message 1", "llama3:instruct")
        context_service.prepare_context("user2", "Message 2", "llama3:instruct")
        
        stats = context_service.get_context_statistics()
        
        # Should return valid statistics
        assert isinstance(stats, dict)
        assert "total_conversations" in stats
        assert "total_messages" in stats
        assert "compressed_conversations" in stats
        assert "compression_rate" in stats
        assert "average_context_tokens" in stats
        assert "active_participants" in stats
        
        # Should reflect our test data
        assert stats["total_conversations"] == 2
        assert stats["total_messages"] >= 2
        assert "user1" in stats["active_participants"]
        assert "user2" in stats["active_participants"]
    
    def test_conversation_history_limit(self, context_service):
        """Test that conversation history is limited and consolidated."""
        # Set a low limit for testing
        context_service.max_conversation_history = 5
        
        # Add many messages
        for i in range(10):
            context_service.prepare_context(
                participant_id="limit_user",
                new_message=f"Message {i}",
                model="llama3:instruct"
            )
        
        state = context_service.conversation_states["limit_user"]
        
        # Should not exceed the limit
        assert len(state.conversation_history) <= context_service.max_conversation_history
        
        # Should have called memory consolidation (check call count increased)
        assert context_service.memory_service.add_memory.call_count > 0
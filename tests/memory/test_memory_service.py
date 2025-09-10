import pytest
import os
from unittest.mock import AsyncMock, Mock, patch

from src.daip_live.memory.service import MemoryService
from src.daip_live.core.models import Session, DialogueTurn, AgentState


class TestMemoryService:
    """Tests for the MemoryService class."""

    @pytest.fixture
    def memory_service(self):
        """Fixture to create a MemoryService instance."""
        with patch("src.daip_live.memory.service.config_manager") as mock_config_manager:
            mock_config = Mock()
            mock_config.database.path = "daip_live.db"
            mock_config_manager.get_config.return_value = mock_config
            service = MemoryService()
            # Override the long term memory file path for testing
            service.long_term_memory_file = "project_context.md"
            return service

    @pytest.fixture
    def mock_session(self):
        """Fixture to create a mock Session object."""
        session = Mock(spec=Session)
        session.history = [
            DialogueTurn(participant_id="user", content="Hello"),
            DialogueTurn(participant_id="assistant", content="Hi, how can I help you?"),
        ]
        session.compressed_history = None
        return session

    def test_construct_prompt_initial(self, memory_service, mock_session):
        """Test constructing an initial prompt."""
        # Arrange
        goal = "Test goal"
        last_tool_result = None
        last_llm_response = None

        # Act
        prompt = memory_service.construct_prompt(goal, last_tool_result, last_llm_response, mock_session)

        # Assert
        assert goal in prompt
        assert "AI-driven application" in prompt  # Long term memory
        assert "Hello" in prompt
        assert "Hi, how can I help you?" in prompt

    def test_construct_prompt_with_tool_result(self, memory_service, mock_session):
        """Test constructing a prompt with a tool result."""
        # Arrange
        goal = "Test goal"
        last_tool_result = "Tool result"
        last_llm_response = None

        # Act
        prompt = memory_service.construct_prompt(goal, last_tool_result, last_llm_response, mock_session)

        # Assert
        assert goal in prompt
        assert last_tool_result in prompt
        assert "AI-driven application" in prompt  # Long term memory
        assert "Hello" in prompt
        assert "Hi, how can I help you?" in prompt

    def test_construct_prompt_with_llm_response(self, memory_service, mock_session):
        """Test constructing a prompt with a previous LLM response."""
        # Arrange
        goal = "Test goal"
        last_tool_result = None
        last_llm_response = "Previous response"

        # Act
        prompt = memory_service.construct_prompt(goal, last_tool_result, last_llm_response, mock_session)

        # Assert
        assert goal in prompt
        assert last_llm_response in prompt
        assert "AI-driven application" in prompt  # Long term memory
        assert "Hello" in prompt
        assert "Hi, how can I help you?" in prompt

    def test_construct_prompt_with_compressed_history(self, memory_service):
        """Test constructing a prompt with compressed history."""
        # Arrange
        goal = "Test goal"
        last_tool_result = None
        last_llm_response = None
        session = Mock(spec=Session)
        session.history = [
            DialogueTurn(participant_id="user", content="Hello"),
        ]
        session.compressed_history = "Compressed history summary"

        # Act
        prompt = memory_service.construct_prompt(goal, last_tool_result, last_llm_response, session)

        # Assert
        assert goal in prompt
        assert session.compressed_history in prompt
        assert "Hello" in prompt
        
    def test_construct_prompt_auto_compress(self, memory_service):
        """Test that construct_prompt automatically compresses history."""
        # Arrange
        goal = "Test goal"
        last_tool_result = None
        last_llm_response = None
        session = Mock(spec=Session)
        # Create a mock history with a len() method that returns 20
        mock_history = Mock()
        mock_history.__len__ = Mock(return_value=20)
        mock_history.__getitem__ = Mock(side_effect=lambda x: [DialogueTurn(participant_id="user", content=f"Message {i}") for i in range(20)][x])
        session.history = mock_history
        session.compressed_history = None

        # Act
        prompt = memory_service.construct_prompt(goal, last_tool_result, last_llm_response, session)

        # Assert
        assert session.compressed_history is not None

    def test_compress_history(self, memory_service, mock_session):
        """Test compressing history."""
        # Arrange
        mock_session.history = [DialogueTurn(participant_id="user", content=f"Message {i}") for i in range(20)]

        # Act
        memory_service.compress_history(mock_session)

        # Assert
        assert mock_session.compressed_history is not None
        assert len(mock_session.compressed_history) > 0

    def test_get_long_term_memory(self, memory_service):
        """Test getting long term memory."""
        # Act
        long_term_memory = memory_service.get_long_term_memory()

        # Assert
        assert "AI-driven application" in long_term_memory
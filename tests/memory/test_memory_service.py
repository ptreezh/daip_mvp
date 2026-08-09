from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.daip_live.core.models import DialogueTurn, Session, TodoItem
from src.daip_live.memory.service import MemoryService
from src.daip_live.model_provider.provider import LiteLLMProvider


class TestMemoryService:
    """Tests for the MemoryService class."""

    @pytest.fixture
    def mock_model_provider(self):
        """Fixture for a mock LiteLLMProvider."""
        mock_provider = Mock(spec=LiteLLMProvider)
        mock_provider.generate = AsyncMock(return_value=("LLM summary", {}))
        return mock_provider

    @pytest.fixture
    def memory_service(self, mock_model_provider):
        """Fixture to create a MemoryService instance."""
        # 源码权威: MemoryService 从 config_bridge.get_config_data() 读配置（service.py:14），  # noqa: E501
        # 无 config_manager 模块属性
        with patch(
            "daip_live.config_bridge.config_bridge.get_config_data",
            return_value={"database": {"path": "daip_live.db"}},
        ):
            service = MemoryService(model_provider=mock_model_provider)
            service.long_term_memory_file = "project_context.md"
            with open("project_context.md", "w", encoding="utf-8") as f:
                f.write("AI-driven application context")
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

    @pytest.mark.asyncio
    async def test_construct_prompt_initial(self, memory_service, mock_session):
        """Test constructing an initial prompt."""
        # Arrange
        goal = "Test goal"
        last_tool_result = None
        last_llm_response = None

        # Act
        prompt = await memory_service.construct_prompt(
            goal, last_tool_result, last_llm_response, mock_session
        )

        # Assert
        assert goal in prompt
        assert "AI-driven application" in prompt  # Long term memory
        assert "Hello" in prompt
        assert "Hi, how can I help you?" in prompt

    @pytest.mark.asyncio
    async def test_construct_prompt_with_tool_result(
        self, memory_service, mock_session
    ):
        """Test constructing a prompt with a tool result."""
        # Arrange
        goal = "Test goal"
        last_tool_result = "Tool result"
        last_llm_response = None

        # Act
        prompt = await memory_service.construct_prompt(
            goal, last_tool_result, last_llm_response, mock_session
        )

        # Assert
        assert goal in prompt
        assert last_tool_result in prompt
        assert "AI-driven application" in prompt  # Long term memory
        assert "Hello" in prompt
        assert "Hi, how can I help you?" in prompt

    @pytest.mark.asyncio
    async def test_construct_prompt_with_llm_response(
        self, memory_service, mock_session
    ):
        """Test constructing a prompt with a previous LLM response."""
        # Arrange
        goal = "Test goal"
        last_tool_result = None
        last_llm_response = "Previous response"

        # Act
        prompt = await memory_service.construct_prompt(
            goal, last_tool_result, last_llm_response, mock_session
        )

        # Assert
        assert goal in prompt
        assert last_llm_response in prompt
        assert "AI-driven application" in prompt  # Long term memory
        assert "Hello" in prompt
        assert "Hi, how can I help you?" in prompt

    @pytest.mark.asyncio
    async def test_construct_prompt_with_compressed_history(self, memory_service):
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
        prompt = await memory_service.construct_prompt(
            goal, last_tool_result, last_llm_response, session
        )

        # Assert
        assert goal in prompt
        assert session.compressed_history in prompt
        assert "Hello" in prompt

    @pytest.mark.asyncio
    async def test_construct_prompt_auto_compress(self, memory_service):
        """Test that construct_prompt automatically compresses history."""
        # Arrange
        goal = "Test goal"
        last_tool_result = None
        last_llm_response = None
        session = Mock(spec=Session)
        # Create a mock history with a len() method that returns 20
        mock_history = Mock()
        mock_history.__len__ = Mock(return_value=20)
        mock_history.__getitem__ = Mock(
            side_effect=lambda x: [
                DialogueTurn(participant_id="user", content=f"Message {i}")
                for i in range(20)
            ][x]
        )
        session.history = mock_history
        session.compressed_history = None

        # Act
        await memory_service.construct_prompt(
            goal, last_tool_result, last_llm_response, session
        )

        # Assert
        assert session.compressed_history is not None

    @pytest.mark.asyncio
    async def test_compress_history(self, memory_service, mock_session):
        """Test compressing history."""
        # Arrange
        mock_session.history = [
            DialogueTurn(participant_id="user", content=f"Message {i}")
            for i in range(20)
        ]

        # Act
        await memory_service.compress_history(mock_session)

        # Assert
        assert mock_session.compressed_history is not None
        assert len(mock_session.compressed_history) > 0

    def test_get_long_term_memory(self, memory_service):
        """Test getting long term memory."""
        # Act
        long_term_memory = memory_service.get_long_term_memory()

        # Assert
        assert "AI-driven application" in long_term_memory

    @pytest.mark.asyncio
    async def test_compress_history_calls_llm(
        self, memory_service, mock_session, mock_model_provider
    ):
        """Test that compress_history calls the LLM via the model_provider."""
        # Arrange
        mock_session.history = [
            DialogueTurn(participant_id="user", content=f"Message {i}")
            for i in range(20)
        ]

        # Act
        await memory_service.compress_history(mock_session)

        # Assert
        mock_model_provider.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_and_get_todo_list(self, memory_service):
        """Test adding and getting a to-do item."""
        # Arrange
        item = TodoItem(description="Test to-do item")

        # Act
        memory_service.add_todo_item(item)
        todo_list = await memory_service.get_todo_list()

        # Assert
        assert len(todo_list) == 1
        assert todo_list[0] == item

    @pytest.mark.asyncio
    async def test_is_todo_list_complete_when_one_pending(self, memory_service):
        """Test is_todo_list_complete returns False when there's a pending item."""
        # Arrange
        memory_service.add_todo_item(
            TodoItem(description="Completed item", status="completed")
        )
        memory_service.add_todo_item(
            TodoItem(description="Pending item", status="pending")
        )

        # Act
        is_complete = await memory_service.is_todo_list_complete()

        # Assert
        assert is_complete is False

    @pytest.mark.asyncio
    async def test_construct_prompt_includes_rag_snippets_when_enabled(
        self, memory_service, mock_session
    ):
        with patch(
            "daip_live.config_bridge.config_bridge.get_config_data",
            return_value={
                "database": {"path": "daip_live.db"},
                "rag": {"enabled": True, "top_k": 5, "min_score": 0.6},
            },
        ):
            mock_km = Mock()
            mock_km.search = AsyncMock(
                return_value=[{"file_path": "docs/a.md", "distance": 0.1}]
            )
            memory_service.knowledge_manager = mock_km
            prompt = await memory_service.construct_prompt(
                "Goal", None, None, mock_session
            )
            assert "RAG Snippets" in prompt
            assert "docs/a.md" in prompt

    @pytest.mark.asyncio
    async def test_construct_prompt_omits_rag_when_no_hits(
        self, memory_service, mock_session
    ):
        with patch(
            "daip_live.config_bridge.config_bridge.get_config_data",
            return_value={
                "database": {"path": "daip_live.db"},
                "rag": {"enabled": True, "top_k": 5, "min_score": 0.6},
            },
        ):
            mock_km = Mock()
            mock_km.search = AsyncMock(return_value=[])
            memory_service.knowledge_manager = mock_km
            prompt = await memory_service.construct_prompt(
                "Goal", None, None, mock_session
            )
            assert "RAG Snippets" not in prompt

    @pytest.mark.asyncio
    async def test_construct_prompt_includes_tool_whitelist(
        self, memory_service, mock_session
    ):
        mock_tools = Mock()
        mock_tool_fn = Mock()
        setattr(
            mock_tool_fn,
            "input_schema",
            type("S", (), {"model_fields": {"x": object()}}),
        )
        mock_tools._registry = {"safe": mock_tool_fn}
        memory_service.tool_manager = mock_tools
        prompt = await memory_service.construct_prompt("Goal", None, None, mock_session)
        assert "Available Tools" in prompt
        assert "safe" in prompt

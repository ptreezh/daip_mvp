"""Integration tests for TUI and backend components."""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.daip_live.agent_engine.executor import AgentExecutor
from src.daip_live.config import ConfigManager
from src.daip_live.core.models import (
    AppConfig,
    DatabaseConfig,
    KnowledgeBaseConfig,
    LLMProviderConfig,
    RoleManagerConfig,
)
from src.daip_live.knowledge.manager import KnowledgeManager
from src.daip_live.memory.session_manager import SessionManager
from src.daip_live.model_provider.provider import LiteLLMProvider
from src.daip_live.p4_role_manager_tools.role_manager import RoleManager
from src.daip_live.p8_debate_system.manager import DebateManager
from src.daip_live.persistence.database import DatabaseManager
from src.daip_live.tui import DAIP_TUI


@pytest.fixture(scope="class")
def test_env(request):
    """Set up a test environment for the integration tests."""
    test_dir = tempfile.TemporaryDirectory()
    db_path = os.path.join(test_dir.name, "test.db")

    roles_dir = os.path.join(test_dir.name, "roles")
    os.makedirs(roles_dir)

    # Mock config
    mock_config = AppConfig(
        database=DatabaseConfig(path=db_path),
        llm_provider=LLMProviderConfig(default_model="llama3:8b", embedding_model="mock-embedding"),
        knowledge_base=KnowledgeBaseConfig(directory=test_dir.name),
        role_manager=RoleManagerConfig(roles_dir=roles_dir)
    )

    config_manager = ConfigManager()
    config_manager._config = mock_config

    db_manager = DatabaseManager(db_path=db_path)
    session_manager = SessionManager(db_manager=db_manager)
    role_manager = RoleManager()
    model_provider = LiteLLMProvider(config=mock_config.llm_provider)
    knowledge_manager = KnowledgeManager(
        db_manager=db_manager,
        model_provider=model_provider,
        config=KnowledgeBaseConfig(directory=test_dir.name)
    )
    debate_manager = DebateManager(
        session_manager=session_manager,
        role_manager=role_manager,
        model_provider=model_provider
    )

    # Create a test role file
    role_content = """
persona: "A helpful test assistant"
tools: []
"""
    role_path = os.path.join(roles_dir, "test_assistant.yaml")
    with open(role_path, 'w', encoding='utf-8') as f:
        f.write(role_content)

    # Update role_manager to use the test roles directory
    role_manager.roles_dir = roles_dir
    role_manager._load_roles_from_directory(roles_dir)

    request.cls.db_manager = db_manager
    request.cls.session_manager = session_manager
    request.cls.role_manager = role_manager
    request.cls.model_provider = model_provider
    request.cls.knowledge_manager = knowledge_manager
    request.cls.debate_manager = debate_manager
    request.cls.config_manager = config_manager

    yield

    db_manager.engine.dispose()
    test_dir.cleanup()

@pytest.mark.usefixtures("test_env")
class TestTUIIntegration:
    """Test suite for TUI and backend component integration."""

    def test_tui_initialization(self):
        """Test TUI initialization with backend components."""
        tui = DAIP_TUI(
            executor=Mock(),
            goal="Test initialization",
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            knowledge_manager=self.knowledge_manager,
            debate_manager=self.debate_manager,
            model_provider=self.model_provider,
            db_manager=self.db_manager,
            config_manager=self.config_manager
        )

        assert tui._session_manager is not None
        assert tui._role_manager is not None
        assert tui._knowledge_manager is not None
        assert tui._debate_manager is not None

    def test_session_management_integration(self):
        """Test session management integration."""
        session = self.session_manager.create_session(
            goal="Test session",
            session_type="chat",
            participant_ids=["user", "assistant"]
        )

        retrieved_session = self.session_manager.get_session(session.session_id)
        assert retrieved_session is not None
        assert retrieved_session.goal == "Test session"
        assert retrieved_session.session_type == "chat"

    def test_role_loading_integration(self):
        """Test role loading integration."""
        role = self.role_manager.get_role_by_name("test_assistant")
        assert role is not None
        assert role.name == "test_assistant"
        assert role.persona == "A helpful test assistant"

    @pytest.mark.asyncio
    async def test_llm_is_called_on_pa_command(self):
        """Test that the LLM is called when a /pa command is issued."""
        # Create a proper mock for MemoryService
        mock_memory_service = Mock()
        mock_task = Mock()
        mock_task.description = "Test Task"
        mock_memory_service.get_todo_list = AsyncMock(return_value=[mock_task])
        mock_memory_service.is_todo_list_complete = AsyncMock(side_effect=[False, True])
        mock_memory_service.construct_prompt = AsyncMock(return_value="Test Prompt")
        mock_memory_service.update_todo_status = AsyncMock()

        executor = AgentExecutor(
            session_manager=self.session_manager,
            memory_service=mock_memory_service,
            knowledge_manager=self.knowledge_manager,
            model_provider=self.model_provider,
            tool_manager=Mock(),
            user_input_queue=asyncio.Queue()
        )
        tui = DAIP_TUI(
            executor=executor,
            goal="Test LLM call",
            session_manager=self.session_manager,
            role_manager=self.role_manager,
            knowledge_manager=self.knowledge_manager,
            debate_manager=self.debate_manager,
            model_provider=self.model_provider,
            db_manager=self.db_manager,
            config_manager=self.config_manager
        )

        # Mock the model_provider's generate method to track calls
        self.model_provider.generate = AsyncMock(return_value=("LLM Response", {}))

        async with tui.run_test() as pilot:
            # Simulate user entering a command
            await pilot.press("/")
            await pilot.press("p")
            await pilot.press("a")
            await pilot.press(" ")
            await pilot.press("h")
            await pilot.press("e")
            await pilot.press("l")
            await pilot.press("l")
            await pilot.press("o")
            await pilot.press("enter")

            # Give the TUI and agent time to process
            await pilot.pause(1.0)

            # Assert that the model_provider.generate method was called
            self.model_provider.generate.assert_called()

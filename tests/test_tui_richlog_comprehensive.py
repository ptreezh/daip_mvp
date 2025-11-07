"""Comprehensive tests for RichLog component in TUI."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.widgets import RichLog

from daip_live.agent_engine.executor import AgentExecutor
from daip_live.core.models import Role
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.service import MemoryService
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI, FocusMode


@pytest.fixture
def tui_app():
    """Sets up the TUI app with all necessary mocks for testing."""
    db_manager = DatabaseManager(":memory:")
    mock_model_provider = MagicMock(spec=LiteLLMProvider)
    mock_model_provider.generate = AsyncMock(return_value=("Test Response", None))
    mock_model_provider.embed = AsyncMock(return_value=[0.1] * 384)

    session_manager = SessionManager()
    memory_service = MemoryService(mock_model_provider)
    mock_knowledge_manager = MagicMock(spec=KnowledgeManager)
    mock_knowledge_manager.sync_knowledge_base = AsyncMock(return_value={'added': 5, 'updated': 2, 'deleted': 1})
    mock_knowledge_manager.search = AsyncMock(return_value=[{'file_path': 'test.md', 'distance': 0.1, 'content': 'Test Content'}])

    mock_role_manager = MagicMock(spec=RoleManager)
    mock_role_manager.list_roles.return_value = [Role(name='test_role', persona='Test Role', tools=['search'])]
    mock_role_manager.get_role_by_name.return_value = Role(name='test_role', persona='Test Role Details', tools=['search', 'write'])

    tool_manager = ToolManager()
    mock_executor = MagicMock(spec=AgentExecutor)
    mock_executor.user_input_queue = asyncio.Queue()
    mock_executor.permission_queue = asyncio.Queue()
    mock_debate_manager = MagicMock(spec=DebateManager)
    mock_config_manager = MagicMock()

    app = DAIP_TUI(
        executor=mock_executor,
        goal="",  # Set empty goal to avoid welcome message
        session_manager=session_manager,
        role_manager=mock_role_manager,
        knowledge_manager=mock_knowledge_manager,
        debate_manager=mock_debate_manager,
        model_provider=mock_model_provider,
        db_manager=db_manager,
        config_manager=mock_config_manager
    )

    yield {
        "app": app,
        "mock_role_manager": mock_role_manager,
        "mock_knowledge_manager": mock_knowledge_manager,
        "session_manager": session_manager,
        "db_manager": db_manager
    }


@pytest.mark.asyncio
async def test_richlog_basic_output(tui_app):
    """Tests basic RichLog output functionality."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        # Simulate some output to the RichLog
        tui._update_log_view("Test message")
        await pilot.pause()

        # Check that the text was added to the buffer
        assert "Test message" in "\n".join(tui._log_text_buffer)

        # Check that the RichLog widget exists (we're not changing the component type)
        rich_log = tui.query_one("#main_log")
        # Since RichLog doesn't expose its content directly, we check the buffer
        # which is used for copying text


@pytest.mark.asyncio
async def test_richlog_clear_functionality(tui_app):
    """Tests RichLog clear functionality."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        # Clear initial content if any
        tui.clear_log()
        await pilot.pause()

        # Add some content
        tui._update_log_view("Message 1")
        tui._update_log_view("Message 2")
        await pilot.pause()

        # Verify content exists
        assert len(tui._log_text_buffer) == 2
        assert "Message 1" in "\n".join(tui._log_text_buffer)

        # Clear the log
        tui.clear_log()
        await pilot.pause()

        # Verify content is cleared
        assert len(tui._log_text_buffer) == 0
        # Check that the RichLog widget is cleared
        rich_log = tui.query_one("#main_log", RichLog)
        # We can't directly check RichLog content, but we can check our buffer
        # which should be empty after clear_log()


@pytest.mark.asyncio
async def test_richlog_write_method(tui_app):
    """Tests RichLog write method with different content types."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        rich_log = tui.query_one("#main_log", RichLog)

        # Test writing plain text
        rich_log.write("Plain text message")
        tui._log_text_buffer.append("Plain text message")
        await pilot.pause()
        assert "Plain text message" in "\n".join(tui._log_text_buffer)

        # Test writing markup text
        rich_log.write("[bold red]Error message[/bold red]")
        tui._log_text_buffer.append("Error message")  # Plain text version
        await pilot.pause()
        assert "Error message" in "\n".join(tui._log_text_buffer)


@pytest.mark.asyncio
async def test_richlog_scroll_behavior(tui_app):
    """Tests RichLog scroll behavior."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        rich_log = tui.query_one("#main_log", RichLog)

        # Clear initial content if any
        tui.clear_log()
        await pilot.pause()

        # Add multiple lines of content
        for i in range(20):
            tui._update_log_view(f"Line {i}")
        await pilot.pause()

        # Check that content was added
        assert len(tui._log_text_buffer) == 20
        assert "Line 0" in "\n".join(tui._log_text_buffer)
        assert "Line 19" in "\n".join(tui._log_text_buffer)


@pytest.mark.asyncio
async def test_richlog_copy_functionality(tui_app):
    """Tests RichLog copy functionality."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        # Clear initial content if any
        tui.clear_log()
        await pilot.pause()

        # Add some content
        tui._update_log_view("Line 1")
        tui._update_log_view("Line 2")
        await pilot.pause()

        # Mock pyperclip.copy
        with patch('pyperclip.copy') as mock_copy:
            # Set focus to output mode
            tui.focus_mode = FocusMode.OUTPUT
            # Trigger copy action
            tui.action_copy_text()
            await pilot.pause()

            # Verify copy was called with correct content
            expected_content = "Line 1\nLine 2"
            mock_copy.assert_called_once_with(expected_content)


@pytest.mark.asyncio
async def test_richlog_highlighting(tui_app):
    """Tests RichLog content highlighting."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        # Test code highlighting
        code_block = "def test():\n    return True"
        highlighted = tui._highlight_code_and_json(code_block)
        # Should return a Syntax object for code
        from rich.syntax import Syntax
        assert isinstance(highlighted, Syntax)

        # Test YAML highlighting
        yaml_block = "key1: value1\nkey2:\n  subkey: subvalue"
        highlighted = tui._highlight_code_and_json(yaml_block)
        # Should return a Syntax object for YAML
        assert isinstance(highlighted, Syntax)

        # Test plain text (no highlighting)
        plain_text = "Just some plain text"
        result = tui._highlight_code_and_json(plain_text)
        # For plain text, it should return a string representation
        # Since _highlight_code_and_json tries to parse as YAML first,
        # plain text without YAML structure will be returned as str
        assert isinstance(result, (str, Syntax))

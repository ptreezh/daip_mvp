"""
Comprehensive TUI automated tests - simulates user interaction to evaluate all features.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.widgets import Input, RichLog

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

pytestmark = pytest.mark.skip(
    reason="TDD红阶段spec，针对已重构移除的旧TUI API；当前源码为准"
)


@pytest.fixture
def tui_app():
    """Sets up the TUI app with all necessary mocks for testing."""
    db_manager = DatabaseManager(":memory:")
    mock_model_provider = MagicMock(spec=LiteLLMProvider)
    mock_model_provider.generate = AsyncMock(return_value=("Test Response", None))
    mock_model_provider.embed = AsyncMock(return_value=[0.1] * 384)

    session_manager = SessionManager()
    MemoryService(mock_model_provider)
    mock_knowledge_manager = MagicMock(spec=KnowledgeManager)
    mock_knowledge_manager.sync_knowledge_base = AsyncMock(
        return_value={"added": 5, "updated": 2, "deleted": 1}
    )
    mock_knowledge_manager.search = AsyncMock(
        return_value=[
            {"file_path": "test.md", "distance": 0.1, "content": "Test Content"}
        ]
    )

    mock_role_manager = MagicMock(spec=RoleManager)
    mock_role_manager.list_roles.return_value = [
        Role(name="test_role", persona="Test Role", tools=["search"])
    ]
    mock_role_manager.get_role_by_name.return_value = Role(
        name="test_role", persona="Test Role Details", tools=["search", "write"]
    )

    ToolManager()
    mock_executor = MagicMock(spec=AgentExecutor)
    mock_executor.user_input_queue = asyncio.Queue()
    mock_executor.permission_queue = asyncio.Queue()
    mock_debate_manager = MagicMock(spec=DebateManager)
    mock_config_manager = MagicMock()

    app = DAIP_TUI(
        executor=mock_executor,
        goal=None,
        session_manager=session_manager,
        role_manager=mock_role_manager,
        knowledge_manager=mock_knowledge_manager,
        debate_manager=mock_debate_manager,
        model_provider=mock_model_provider,
        db_manager=db_manager,
        config_manager=mock_config_manager,
    )

    yield {
        "app": app,
        "mock_role_manager": mock_role_manager,
        "mock_knowledge_manager": mock_knowledge_manager,
        "session_manager": session_manager,
        "db_manager": db_manager,
    }


@pytest.mark.asyncio
async def test_command_discovery(tui_app):
    """Tests the command discovery feature."""
    tui = tui_app["app"]
    expected_commands = [
        "/pa",
        "/role",
        "/knowledge",
        "/session",
        "/help",
        "/quit",
        "/debate",
        "/model",
        "/init",
    ]
    discovered_commands = [cmd for cmd, _ in tui._available_commands]
    assert all(cmd in discovered_commands for cmd in expected_commands)


@pytest.mark.asyncio
async def test_autocomplete_functionality(tui_app):
    """Tests the autocomplete functionality."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        tui.query_one(Input).value = "/r"
        tui.on_input_changed(Input.Changed(tui.query_one(Input), "/r"))
        await pilot.pause()
        tui.query_one(Input).value = "/role lis"
        tui.on_input_changed(Input.Changed(tui.query_one(Input), "/role lis"))
        await pilot.pause()
        tui.query_one(Input).value = "/role list"
        tui.on_input_changed(Input.Changed(tui.query_one(Input), "/role list"))
        await pilot.pause()


@pytest.mark.asyncio
async def test_role_commands(tui_app):
    """Tests role management commands."""
    tui = tui_app["app"]
    mock_role_manager = tui_app["mock_role_manager"]
    async with tui.run_test():
        await tui._handle_shortcut_command("/role list")
        mock_role_manager.list_roles.assert_called_once()

        await tui._handle_shortcut_command("/role view test_role")
        mock_role_manager.get_role_by_name.assert_called_once_with("test_role")


@pytest.mark.asyncio
async def test_knowledge_commands(tui_app):
    """Tests knowledge base management commands."""
    tui = tui_app["app"]
    mock_knowledge_manager = tui_app["mock_knowledge_manager"]
    async with tui.run_test():
        await tui._handle_shortcut_command("/knowledge sync")
        mock_knowledge_manager.sync_knowledge_base.assert_called_once()

        await tui._handle_shortcut_command("/knowledge search test query")
        mock_knowledge_manager.search.assert_called_once_with("test query")


@pytest.mark.asyncio
async def test_session_commands(tui_app):
    """Tests session management commands."""
    tui = tui_app["app"]
    session_manager = tui_app["session_manager"]
    test_session = session_manager.create_session(
        goal="test session", session_type="chat", participant_ids=["user", "agent"]
    )

    async with tui.run_test() as pilot:
        await tui._handle_shortcut_command("/session list")
        await pilot.pause()
        await tui._handle_shortcut_command(f"/session view {test_session.session_id}")
        await pilot.pause()


@pytest.mark.asyncio
async def test_personal_assistant_command(tui_app):
    """Tests the personal assistant command."""
    tui = tui_app["app"]
    session_manager = tui_app["session_manager"]
    async with tui.run_test():
        await tui._handle_shortcut_command("/pa analyze project structure")
        assert any(s.session_type == "chat" for s in session_manager.list_sessions())


@pytest.mark.asyncio
async def test_focus_management(tui_app):
    """Tests focus management."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        await pilot.press("ctrl+tab")
        assert tui.focus_mode == FocusMode.OUTPUT
        await pilot.press("escape")
        assert tui.focus_mode == FocusMode.INPUT


@patch("pyperclip.copy")
@pytest.mark.asyncio
async def test_copy_functionality(mock_copy, tui_app):
    """Tests the copy functionality."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        tui._log_text_buffer = ["line 1", "line 2"]
        tui.focus_mode = FocusMode.OUTPUT
        await pilot.press("ctrl+c")
        mock_copy.assert_called_once_with("line 1\nline 2")


@pytest.mark.asyncio
async def test_error_handling(tui_app):
    """Tests error handling for commands."""
    tui = tui_app["app"]
    async with tui.run_test():
        # These should not raise exceptions
        await tui._handle_shortcut_command("/unknown_command")
        await tui._handle_shortcut_command("/role view")
        await tui._handle_shortcut_command("/session view")
        await tui._handle_shortcut_command("/pa")


@pytest.mark.asyncio
async def test_help_dialog_content(tui_app):
    """Tests the content of the help dialog."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        await tui._handle_shortcut_command("/help")
        await pilot.pause()
        rich_log = tui.query_one("#help-content", RichLog)
        all_text = "\n".join(
            line.plain if hasattr(line, "plain") else str(line)
            for line in rich_log.lines
        )
        assert "Available Commands" in all_text

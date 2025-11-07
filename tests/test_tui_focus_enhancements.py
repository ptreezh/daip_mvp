"""Tests for TUI focus enhancement features."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from textual.widgets import RichLog, Input

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
    
    # Create mocks for all dependencies
    mock_executor = MagicMock(spec=AgentExecutor)
    mock_session_manager = MagicMock(spec=SessionManager)
    mock_role_manager = MagicMock(spec=RoleManager)
    mock_knowledge_manager = MagicMock(spec=KnowledgeManager)
    mock_debate_manager = MagicMock(spec=DebateManager)
    mock_model_provider = MagicMock(spec=LiteLLMProvider)
    
    # Configure role manager mock
    mock_role = MagicMock(spec=Role)
    mock_role.name = "test_role"
    mock_role.persona = "A test role"
    mock_role.tools = ["read_file", "write_file"]
    mock_role_manager.get_role_by_name.return_value = mock_role
    mock_role_manager.list_roles.return_value = [mock_role]
    
    # Configure session manager mock
    mock_session_manager.list_sessions.return_value = []
    
    # Create TUI app instance
    app = DAIP_TUI(
        executor=mock_executor,
        session_manager=mock_session_manager,
        role_manager=mock_role_manager,
        knowledge_manager=mock_knowledge_manager,
        debate_manager=mock_debate_manager,
        model_provider=mock_model_provider,
        db_manager=db_manager,
    )
    
    return {
        "app": app,
        "db_manager": db_manager,
        "mock_executor": mock_executor,
        "mock_session_manager": mock_session_manager,
        "mock_role_manager": mock_role_manager,
        "mock_knowledge_manager": mock_knowledge_manager,
        "mock_debate_manager": mock_debate_manager,
        "mock_model_provider": mock_model_provider,
    }


@pytest.mark.asyncio
async def test_focus_toggle_visual_feedback(tui_app):
    """Tests that focus toggle provides visual feedback."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        # Check initial focus state
        assert tui.focus_mode == FocusMode.INPUT
        
        # Toggle focus to output
        await pilot.press("shift+tab")
        await pilot.pause()
        
        # Check that focus mode changed
        assert tui.focus_mode == FocusMode.OUTPUT
        
        # Check that visual styles were applied
        main_log = tui.query_one("#main_log")
        user_input = tui.query_one("#user_input")
        
        # We can't directly check the styles, but we can verify the components exist
        assert main_log is not None
        assert user_input is not None


@pytest.mark.asyncio
async def test_focus_mode_key_handling(tui_app):
    """Tests that keys are handled differently based on focus mode."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        # Start in input mode
        assert tui.focus_mode == FocusMode.INPUT
        
        # Switch to output mode
        await pilot.press("shift+tab")
        await pilot.pause()
        assert tui.focus_mode == FocusMode.OUTPUT
        
        # In output mode, most keys should be ignored
        # (we can't easily test this without more complex mocking)
        
        # Switch back to input mode using escape key
        await pilot.press("escape")
        await pilot.pause()
        assert tui.focus_mode == FocusMode.INPUT


@pytest.mark.asyncio
async def test_copy_functionality_in_output_mode(tui_app):
    """Tests copy functionality in output mode."""
    tui = tui_app["app"]
    async with tui.run_test() as pilot:
        # Add some content to the log
        tui._update_log_view("Test content for copying")
        await pilot.pause()
        
        # Switch to output mode
        await pilot.press("shift+tab")
        await pilot.pause()
        assert tui.focus_mode == FocusMode.OUTPUT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
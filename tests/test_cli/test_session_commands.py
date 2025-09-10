"""Tests for TUI session commands."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from daip_live.config import ConfigManager
from daip_live.core.models import AgentState, Session
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI
from textual.widgets import Label, ListItem, ListView, RichLog


@pytest.fixture
def mock_session_manager() -> SessionManager:
    """Creates a mock SessionManager with some predefined sessions."""
    session_manager = Mock(spec=SessionManager)
    sessions = [
        Session(session_id="sess_1", goal="Test session 1", session_type="chat", status=AgentState.COMPLETED, participant_ids=["user", "pa"]),
        Session(session_id="sess_2", goal="Test session 2", session_type="debate", status=AgentState.RUNNING, participant_ids=["pro", "con"])
    ]
    session_manager.list_sessions.return_value = sessions
    return session_manager

@pytest.mark.asyncio
async def test_session_list_command(mock_session_manager):
    """Test that the /session list command displays a table of sessions."""
    tui = DAIP_TUI(
        executor=Mock(),
        goal=None,
        session_manager=mock_session_manager,
        role_manager=Mock(spec=RoleManager),
        knowledge_manager=Mock(spec=KnowledgeManager),
        debate_manager=Mock(spec=DebateManager),
        model_provider=Mock(spec=LiteLLMProvider),
        db_manager=Mock(spec=DatabaseManager),
        config_manager=Mock(spec=ConfigManager)
    )

    async with tui.run_test() as pilot:
        command = "/session list"
        for char in command:
            await pilot.press(char)
        await pilot.press("enter")
        await pilot.pause(0.1)

        log_widget = pilot.app.query_one("#main_log", RichLog)
        log_content = "".join(line.text for line in log_widget.lines)

        assert "sess_1" in log_content
        assert "Test session 2" in log_content
        assert "RUNNING" in log_content, "The /session list command should display session details."

@pytest.mark.asyncio
async def test_session_view_autocomplete(mock_session_manager):
    """Test that typing /session view shows session IDs in the autocomplete."""
    tui = DAIP_TUI(
        executor=Mock(),
        goal=None,
        session_manager=mock_session_manager,
        role_manager=Mock(spec=RoleManager),
        knowledge_manager=Mock(spec=KnowledgeManager),
        debate_manager=Mock(spec=DebateManager),
        model_provider=Mock(spec=LiteLLMProvider),
        db_manager=Mock(spec=DatabaseManager),
        config_manager=Mock(spec=ConfigManager)
    )

    async with tui.run_test() as pilot:
        command = "/session view "
        for char in command:
            await pilot.press(char)
        await pilot.pause(0.1)

        # Assert that the popup is visible
        assert len(pilot.app.query("#autocomplete-popup")) == 1, "Autocomplete should appear for parameters."

        # Assert that the popup contains the session IDs
        popup = pilot.app.query_one("#autocomplete-popup")
        list_view = popup.query_one("#autocomplete-list", ListView)
        items = list_view.query(ListItem)
        content = " ".join([str(item.query_one(Label).renderable) for item in items])

        assert "sess_1" in content
        assert "sess_2" in content, "Autocomplete should list available session IDs."

@pytest.mark.asyncio
async def test_session_view_command(mock_session_manager):
    """Test that the /session view <id> command displays session details."""
    # Configure the mock to return a specific session
    mock_session = Session(session_id="sess_1", goal="The goal of sess_1", session_type="chat", status=AgentState.COMPLETED, participant_ids=["user"])
    mock_session_manager.get_session.return_value = mock_session

    tui = DAIP_TUI(
        executor=Mock(),
        goal=None,
        session_manager=mock_session_manager,
        role_manager=Mock(spec=RoleManager),
        knowledge_manager=Mock(spec=KnowledgeManager),
        debate_manager=Mock(spec=DebateManager),
        model_provider=Mock(spec=LiteLLMProvider),
        db_manager=Mock(spec=DatabaseManager),
        config_manager=Mock(spec=ConfigManager)
    )

    async with tui.run_test() as pilot:
        command = "/session view sess_1"
        for char in command:
            await pilot.press(char)
        await pilot.press("enter")
        await pilot.pause(0.1)

        log_widget = pilot.app.query_one("#main_log", RichLog)
        log_content = "".join(line.text for line in log_widget.lines)

        assert "Session Details: sess_1" in log_content
        assert "The goal of sess_1" in log_content, "The /session view command should display full session details."

@pytest.mark.asyncio
async def test_session_view_command(mock_session_manager):
    """Test that the /session view <id> command displays session details."""
    # Configure the mock to return a specific session
    mock_session = Session(session_id="sess_1", goal="The goal of sess_1", session_type="chat", status=AgentState.COMPLETED, participant_ids=["user"])
    mock_session_manager.get_session.return_value = mock_session

    tui = DAIP_TUI(
        executor=Mock(),
        goal=None,
        session_manager=mock_session_manager,
        role_manager=Mock(spec=RoleManager),
        knowledge_manager=Mock(spec=KnowledgeManager),
        debate_manager=Mock(spec=DebateManager),
        model_provider=Mock(spec=LiteLLMProvider),
        db_manager=Mock(spec=DatabaseManager),
        config_manager=Mock(spec=ConfigManager)
    )

    async with tui.run_test() as pilot:
        command = "/session view sess_1"
        for char in command:
            await pilot.press(char)
        await pilot.press("enter")
        await pilot.pause(0.1)

        log_widget = pilot.app.query_one("#main_log", RichLog)
        log_content = "".join(line.text for line in log_widget.lines)

        assert "Session Details: sess_1" in log_content
        assert "The goal of sess_1" in log_content, "The /session view command should display full session details."

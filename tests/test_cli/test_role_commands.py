"""Tests for TUI role commands."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from textual.widgets import Label, ListItem, ListView, RichLog

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from daip_live.config import ConfigManager
from daip_live.core.models import (
    Role,
)
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI


@pytest.fixture
def mock_role_manager() -> RoleManager:
    """Creates a mock RoleManager with some predefined roles."""
    role_manager = Mock(spec=RoleManager)
    roles = [
        Role(name="tester", persona="A test role", tools=[]),
        Role(name="developer", persona="A dev role", tools=["search"])
    ]
    role_manager.list_roles.return_value = roles
    return role_manager

@pytest.mark.asyncio
async def test_role_list_command(mock_role_manager):
    """Test that the /role list command displays a table of roles."""
    tui = DAIP_TUI(
        executor=Mock(),
        goal=None,
        session_manager=Mock(spec=SessionManager),
        role_manager=mock_role_manager,
        knowledge_manager=Mock(spec=KnowledgeManager),
        debate_manager=Mock(spec=DebateManager),
        model_provider=Mock(spec=LiteLLMProvider),
        db_manager=Mock(spec=DatabaseManager),
        config_manager=Mock(spec=ConfigManager)
    )

    async with tui.run_test() as pilot:
        await pilot.press("/")
        await pilot.press("r")
        await pilot.press("o")
        await pilot.press("l")
        await pilot.press("e")
        await pilot.press(" ")
        await pilot.press("l")
        await pilot.press("i")
        await pilot.press("s")
        await pilot.press("t")
        await pilot.press("enter")
        await pilot.pause(0.1)

        log_widget = pilot.app.query_one("#main_log", RichLog)
        log_content = "".join(line.text for line in log_widget.lines)
        assert "tester" in log_content
        assert "developer" in log_content
        assert "A dev role" in log_content, "The /role list command should display role details."

@pytest.mark.asyncio
async def test_role_view_autocomplete(mock_role_manager):
    """Test that typing /role view shows role names in the autocomplete."""
    tui = DAIP_TUI(
        executor=Mock(),
        goal=None,
        session_manager=Mock(spec=SessionManager),
        role_manager=mock_role_manager,
        knowledge_manager=Mock(spec=KnowledgeManager),
        debate_manager=Mock(spec=DebateManager),
        model_provider=Mock(spec=LiteLLMProvider),
        db_manager=Mock(spec=DatabaseManager),
        config_manager=Mock(spec=ConfigManager)
    )

    async with tui.run_test() as pilot:
        # Type the command that requires parameter completion
        command = "/role view "
        for char in command:
            await pilot.press(char)
        await pilot.pause(0.1)

        # Assert that the popup is visible
        assert len(pilot.app.query("#autocomplete-popup")) == 1, "Autocomplete should appear for parameters."

        # Assert that the popup contains the role names
        popup = pilot.app.query_one("#autocomplete-popup")
        list_view = popup.query_one("#autocomplete-list", ListView)
        items = list_view.query(ListItem)
        content = " ".join([str(item.query_one(Label).renderable) for item in items])

        assert "tester" in content
        assert "developer" in content, "Autocomplete should list available roles."

@pytest.mark.asyncio
async def test_role_view_command(mock_role_manager):
    """Test that the /role view <name> command displays role details."""
    # Configure the mock to return a specific role
    mock_role = Role(name="tester", persona="The persona of the tester", tools=["search"])
    mock_role_manager.get_role_by_name.return_value = mock_role

    tui = DAIP_TUI(
        executor=Mock(),
        goal=None,
        session_manager=Mock(spec=SessionManager),
        role_manager=mock_role_manager,
        knowledge_manager=Mock(spec=KnowledgeManager),
        debate_manager=Mock(spec=DebateManager),
        model_provider=Mock(spec=LiteLLMProvider),
        db_manager=Mock(spec=DatabaseManager),
        config_manager=Mock(spec=ConfigManager)
    )

    async with tui.run_test() as pilot:
        command = "/role view tester"
        for char in command:
            await pilot.press(char)
        await pilot.press("enter")
        await pilot.pause(0.1)

        log_widget = pilot.app.query_one("#main_log", RichLog)
        log_content = "".join(line.text for line in log_widget.lines)

        assert "Role Details: tester" in log_content
        assert "The persona of the tester" in log_content
        assert "Tools: search" in log_content, "The /role view command should display full role details."

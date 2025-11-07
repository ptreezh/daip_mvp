"""Tests for TUI knowledge commands."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from textual.widgets import RichLog

from daip_live.config import ConfigManager
from daip_live.knowledge.manager import KnowledgeManager
from daip_live.memory.session_manager import SessionManager
from daip_live.model_provider.provider import LiteLLMProvider
from daip_live.p4_role_manager_tools.role_manager import RoleManager
from daip_live.p8_debate_system.manager import DebateManager
from daip_live.persistence.database import DatabaseManager
from daip_live.tui import DAIP_TUI


@pytest.fixture
def mock_knowledge_manager() -> KnowledgeManager:
    """Creates a mock KnowledgeManager."""
    knowledge_manager = Mock(spec=KnowledgeManager)
    # Configure the async method with an AsyncMock
    knowledge_manager.sync_knowledge_base = AsyncMock(return_value={
        "added": 1, "updated": 2, "removed": 3, "unchanged": 4
    })
    return knowledge_manager

@pytest.mark.asyncio
async def test_knowledge_sync_command(mock_knowledge_manager):
    """Test that the /knowledge sync command displays a summary."""
    tui = DAIP_TUI(
        executor=Mock(),
        goal=None,
        session_manager=Mock(spec=SessionManager),
        role_manager=Mock(spec=RoleManager),
        knowledge_manager=mock_knowledge_manager,
        debate_manager=Mock(spec=DebateManager),
        model_provider=Mock(spec=LiteLLMProvider),
        db_manager=Mock(spec=DatabaseManager),
        config_manager=Mock(spec=ConfigManager)
    )

    async with tui.run_test() as pilot:
        command = "/knowledge sync"
        for char in command:
            await pilot.press(char)
        await pilot.press("enter")
        await pilot.pause(0.1)

        log_widget = pilot.app.query_one("#main_log", RichLog)
        log_content = "".join(line.text for line in log_widget.lines)

        assert "Knowledge base sync complete" in log_content
        assert "Added: 1" in log_content
        assert "Updated: 2" in log_content
        assert "Removed: 3" in log_content, "The /knowledge sync command should display the sync summary."

@pytest.mark.asyncio
async def test_knowledge_search_command(mock_knowledge_manager):
    """Test that the /knowledge search command displays search results."""
    # Configure the mock to return specific search results
    search_results = [
        {"file_path": "/path/to/doc1.txt", "distance": 0.5},
        {"file_path": "/path/to/doc2.txt", "distance": 0.8},
    ]
    mock_knowledge_manager.search = AsyncMock(return_value=search_results)

    tui = DAIP_TUI(
        executor=Mock(),
        goal=None,
        session_manager=Mock(spec=SessionManager),
        role_manager=Mock(spec=RoleManager),
        knowledge_manager=mock_knowledge_manager,
        debate_manager=Mock(spec=DebateManager),
        model_provider=Mock(spec=LiteLLMProvider),
        db_manager=Mock(spec=DatabaseManager),
        config_manager=Mock(spec=ConfigManager)
    )

    async with tui.run_test() as pilot:
        command = "/knowledge search my query"
        for char in command:
            await pilot.press(char)
        await pilot.press("enter")
        await pilot.pause(0.1)

        log_widget = pilot.app.query_one("#main_log", RichLog)
        log_content = "".join(line.text for line in log_widget.lines)

        assert "Knowledge Search Results" in log_content
        assert "doc1.txt" in log_content
        assert "doc2.txt" in log_content, "The /knowledge search command should display search results."

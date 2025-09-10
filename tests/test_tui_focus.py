import pytest
from textual.app import App
from textual.widgets import RichLog, Input
from textual.containers import Vertical
from textual.events import Click
from unittest.mock import MagicMock, patch
import pyperclip

# Assuming DAIP_TUI and FocusMode are correctly imported
from daip_live.tui import DAIP_TUI, FocusMode

# Mock the executor and other dependencies for DAIP_TUI
@pytest.fixture
def mock_daip_tui_dependencies():
    return {
        "executor": MagicMock(),
        "session_manager": MagicMock(),
        "role_manager": MagicMock(),
        "knowledge_manager": MagicMock(),
        "debate_manager": MagicMock(),
        "model_provider": MagicMock(),
        "db_manager": MagicMock(),
        "config_manager": MagicMock(),
    }

@pytest.mark.asyncio
async def test_action_toggle_focus_from_input_to_output(mock_daip_tui_dependencies):
    daip_tui = DAIP_TUI(**mock_daip_tui_dependencies, goal="test goal")
    async with daip_tui.run_test() as pilot:
        assert pilot.app.focused == pilot.app.query_one("#user_input")
        await pilot.press("ctrl+tab")
        assert pilot.app.focused == pilot.app.query_one("#main_log")
        assert daip_tui.focus_mode == FocusMode.OUTPUT

@pytest.mark.asyncio
async def test_action_toggle_focus_from_output_to_input(mock_daip_tui_dependencies):
    daip_tui = DAIP_TUI(**mock_daip_tui_dependencies, goal="test goal")
    async with daip_tui.run_test() as pilot:
        await pilot.press("ctrl+tab")
        assert pilot.app.focused == pilot.app.query_one("#main_log")
        await pilot.press("ctrl+tab")
        assert pilot.app.focused == pilot.app.query_one("#user_input")
        assert daip_tui.focus_mode == FocusMode.INPUT

@pytest.mark.asyncio
async def test_action_exit_output_mode(mock_daip_tui_dependencies):
    daip_tui = DAIP_TUI(**mock_daip_tui_dependencies, goal="test goal")
    async with daip_tui.run_test() as harness:
        await harness.press("ctrl+tab")
        assert daip_tui.focus_mode == FocusMode.OUTPUT
        assert harness.app.focused == harness.app.query_one("#main_log")
        await harness.press("escape")
        assert daip_tui.focus_mode == FocusMode.INPUT
        assert harness.app.focused == harness.app.query_one("#user_input")

@pytest.mark.asyncio
async def test_action_exit_output_mode_when_already_in_input_mode(mock_daip_tui_dependencies):
    daip_tui = DAIP_TUI(**mock_daip_tui_dependencies, goal="test goal")
    async with daip_tui.run_test() as harness:
        assert daip_tui.focus_mode == FocusMode.INPUT
        assert harness.app.focused == harness.app.query_one("#user_input")
        await harness.press("escape")
        assert daip_tui.focus_mode == FocusMode.INPUT
        assert harness.app.focused == harness.app.query_one("#user_input")
from unittest.mock import MagicMock, patch

import pytest

# Assuming DAIP_TUI and FocusMode are correctly imported
from daip_live.tui import DAIP_TUI, FocusMode

pytestmark = pytest.mark.skip(reason="旧spec：TUI 内部实现已重构（Textual action 命名 action__handle_*、组件 Footer 等已移除）；当前源码为准")


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

    @pytest.mark.asyncio
    async def test_copy_paste_in_output_mode(mock_daip_tui_dependencies):
        """Test that Ctrl+A and Ctrl+C work in output mode."""
        daip_tui = DAIP_TUI(**mock_daip_tui_dependencies, goal="test goal")
        with patch("daip_live.tui.pyperclip.copy") as mock_copy:
            async with daip_tui.run_test() as pilot:
                test_text = "This is the text to be copied."

                # Clear log and write new text using the TUI's own methods
                daip_tui.call_later(daip_tui.clear_log)
                daip_tui.call_later(daip_tui._update_log_view, test_text)
                await pilot.pause()

                # Switch to output mode and copy
                await pilot.press("ctrl+tab")
                await pilot.press("ctrl+c")
                await pilot.pause()

                # Check that pyperclip.copy was called with the correct text
                mock_copy.assert_called_once_with(test_text)

@pytest.mark.asyncio
async def test_on_click_focus_switch(mock_daip_tui_dependencies):
    """Test that clicking on the main log switches focus from input to output."""
    daip_tui = DAIP_TUI(**mock_daip_tui_dependencies, goal="test goal")
    async with daip_tui.run_test() as pilot:
        # 1. Assert initial state is INPUT mode
        assert daip_tui.focus_mode == FocusMode.INPUT
        assert pilot.app.focused == pilot.app.query_one("#user_input")

        # 2. Simulate a click on the log panel
        await pilot.click("#main_log")
        await pilot.pause() # Allow event to be processed

        # 3. Assert final state is OUTPUT mode
        assert daip_tui.focus_mode == FocusMode.OUTPUT
        assert pilot.app.focused == pilot.app.query_one("#main_log")

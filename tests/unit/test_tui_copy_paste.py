"""
Unit tests for TUI copy/paste functionality.

Aligned with the current SimplifiedTUI implementation:
- action_copy_text is async and copies the whole _log_text_buffer (no selection concept)
- action_paste_text is sync and inserts into self.focused when it is an Input
"""

from unittest.mock import PropertyMock, patch

import pytest
from textual.widgets import Input

from src.daip_live.tui import DAIP_TUI


class TestTUICopyPaste:
    """Test cases for TUI copy/paste functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch("daip_live.container.Container"):
            app = DAIP_TUI()
            return app

    @pytest.mark.asyncio
    async def test_action_copy_text_copies_log_buffer(self, tui_app):
        """Test that copy text copies the entire log buffer content."""
        # Setup
        tui_app._log_text_buffer = ["Line 1", "Line 2", "Line 3"]

        with patch("pyperclip.copy") as mock_copy:
            with patch.object(tui_app, "_update_log_view") as mock_update_log:
                # Execute
                await tui_app.action_copy_text()

                # Assert - the whole buffer is joined and copied
                mock_copy.assert_called_once_with("Line 1\nLine 2\nLine 3")
                assert mock_update_log.called

    @pytest.mark.asyncio
    async def test_action_copy_text_empty_buffer_shows_warning(self, tui_app):
        """Test that copying with an empty log buffer shows a warning and copies nothing."""  # noqa: E501
        # Setup
        tui_app._log_text_buffer = []

        with patch("pyperclip.copy") as mock_copy:
            with patch.object(tui_app, "_update_log_view") as mock_update_log:
                # Execute
                await tui_app.action_copy_text()

                # Assert - nothing copied, warning shown
                mock_copy.assert_not_called()
                mock_update_log.assert_any_call(
                    "[yellow]⚠️ 主对话区没有内容可以复制[/yellow]"
                )

    def test_action_paste_text_success(self, tui_app):
        """Test pasting text from clipboard into the focused input area."""
        # Setup
        with patch("pyperclip.paste", return_value="Pasted text"):
            # Create a real Input widget so isinstance(focused, Input) passes
            mock_input = Input(value="Existing text")
            mock_input.cursor_position = 8  # Position after "Existing"

            with patch.object(
                type(tui_app),
                "focused",
                new_callable=PropertyMock,
                return_value=mock_input,
            ):
                with patch.object(tui_app, "_update_log_view") as mock_update_log:
                    # Execute
                    tui_app.action_paste_text()

                    # Assert - text inserted at cursor position
                    assert mock_input.value == "ExistingPasted text text"
                    assert mock_input.cursor_position == 8 + len("Pasted text")
                    mock_update_log.assert_any_call("[dim]✅ 文本已粘贴到输入框[/dim]")

    def test_action_paste_text_empty_clipboard(self, tui_app):
        """Test pasting when clipboard is empty."""
        # Setup
        with patch("pyperclip.paste", return_value=""):
            with patch.object(tui_app, "_update_log_view") as mock_update_log:
                # Execute
                tui_app.action_paste_text()

                # Assert
                mock_update_log.assert_called_with("[yellow]⚠️ 剪贴板为空[/yellow]")

    def test_action_paste_text_clipboard_error(self, tui_app):
        """Test pasting when clipboard access fails."""
        # Setup
        with patch("pyperclip.paste", side_effect=Exception("Clipboard error")):
            with patch.object(tui_app, "_update_log_view") as mock_update_log:
                # Execute
                tui_app.action_paste_text()

                # Assert
                mock_update_log.assert_called_with(
                    "[red]❌ 粘贴失败: Clipboard error[/red]"
                )

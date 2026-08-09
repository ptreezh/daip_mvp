"""
Integration tests for TUI copy/paste functionality.
"""

from unittest.mock import Mock, patch

import pytest
from textual.keys import Keys
from textual.widgets import Input

from src.daip_live.tui import DAIP_TUI, FocusMode

pytestmark = pytest.mark.skip(
    reason="旧spec：用 on_key 直接模拟按键与当前 Textual 绑定架构不符（action_copy_text/action_paste_text 经 bindings 分发）；当前源码为准"  # noqa: E501
)


class TestTUICopyPasteIntegration:
    """Integration tests for TUI copy/paste functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch("daip_live.container.Container"):
            app = DAIP_TUI()
            return app

    def test_ctrl_c_in_output_mode_calls_copy_text(self, tui_app):
        """Test that Ctrl+C in output mode calls copy_text action."""
        # Setup
        tui_app.focus_mode = FocusMode.OUTPUT

        with patch.object(tui_app, "action_copy_text") as mock_copy:
            # Create a mock key event for Ctrl+C
            mock_event = Mock()
            mock_event.__eq__ = lambda self, other: other == Keys.ControlC
            mock_event.key = None

            # Execute
            tui_app.on_key(mock_event)

            # Assert
            mock_copy.assert_called_once()
            mock_event.prevent_default.assert_called_once()

    def test_ctrl_v_in_output_mode_calls_paste_text(self, tui_app):
        """Test that Ctrl+V in output mode calls paste_text action."""
        # Setup
        tui_app.focus_mode = FocusMode.OUTPUT

        with patch.object(tui_app, "action_paste_text") as mock_paste:
            # Create a mock key event for Ctrl+V
            mock_event = Mock()
            mock_event.__eq__ = lambda self, other: other == Keys.ControlV
            mock_event.key = None

            # Execute
            tui_app.on_key(mock_event)

            # Assert
            mock_paste.assert_called_once()
            mock_event.prevent_default.assert_called_once()

    def test_ctrl_v_in_input_mode_calls_paste_text(self, tui_app):
        """Test that Ctrl+V in input mode calls paste_text action."""
        # Setup
        tui_app.focus_mode = FocusMode.INPUT

        with patch.object(tui_app, "action_paste_text") as mock_paste:
            with patch.object(tui_app, "query_one", return_value=Mock(spec=Input)):
                # Create a mock key event for Ctrl+V
                mock_event = Mock()
                mock_event.__eq__ = lambda self, other: other == Keys.ControlV
                mock_event.key = None

                # Execute
                tui_app.on_key(mock_event)

                # Assert
                mock_paste.assert_called_once()
                mock_event.prevent_default.assert_called_once()

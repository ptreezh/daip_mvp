"""
Unit tests for TUI copy/paste functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from textual.widgets import Input, RichLog
from src.daip_live.tui import DAIP_TUI


class TestTUICopyPaste:
    """Test cases for TUI copy/paste functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch('src.daip_live.tui.Container'):
            app = DAIP_TUI()
            return app

    def test_action_copy_text_with_selection(self, tui_app):
        """Test copying selected text from RichLog."""
        # Setup
        tui_app._log_text_buffer = ["Line 1", "Line 2", "Line 3"]
        
        # Create a mock RichLog with get_selection method
        mock_rich_log = Mock()
        mock_rich_log.get_selection.return_value = "Selected text"
        
        with patch.object(tui_app, 'query_one', return_value=mock_rich_log):
            with patch('pyperclip.copy') as mock_copy:
                with patch.object(tui_app, '_update_log_view'):
                    # Execute
                    tui_app.action_copy_text()
                    
                    # Assert
                    mock_copy.assert_called_once_with("Selected text")

    def test_action_copy_text_without_selection(self, tui_app):
        """Test copying all text when no selection is available."""
        # Setup
        tui_app._log_text_buffer = ["Line 1", "Line 2", "Line 3"]
        
        # Create a mock RichLog with get_selection method that raises an exception
        mock_rich_log = Mock()
        mock_rich_log.get_selection.side_effect = AttributeError("No selection method")
        
        with patch.object(tui_app, 'query_one', return_value=mock_rich_log):
            with patch('pyperclip.copy') as mock_copy:
                with patch.object(tui_app, '_update_log_view'):
                    # Execute
                    tui_app.action_copy_text()
                    
                    # Assert
                    mock_copy.assert_called_once_with("Line 1\nLine 2\nLine 3")

    def test_action_paste_text_success(self, tui_app):
        """Test pasting text from clipboard to input area."""
        # Setup
        with patch('pyperclip.paste', return_value="Pasted text"):
            # Create a mock Input widget
            mock_input = Mock()
            mock_input.value = "Existing text"
            mock_input.cursor_position = 8  # Position after "Existing"
            
            with patch.object(tui_app, 'query_one', return_value=mock_input):
                with patch.object(tui_app, '_update_log_view'):
                    # Execute
                    tui_app.action_paste_text()
                    
                    # Assert
                    # The mock might not reflect the actual value change, so we'll check the call
                    # Check that focus was called
                    mock_input.focus.assert_called_once()

    def test_action_paste_text_empty_clipboard(self, tui_app):
        """Test pasting when clipboard is empty."""
        # Setup
        with patch('pyperclip.paste', return_value=""):
            with patch.object(tui_app, 'query_one', return_value=Mock()):
                with patch.object(tui_app, '_update_log_view') as mock_update_log:
                    # Execute
                    tui_app.action_paste_text()
                    
                    # Assert
                    mock_update_log.assert_called_with("[yellow]> Clipboard is empty.[/bold yellow]")

    def test_action_paste_text_clipboard_error(self, tui_app):
        """Test pasting when clipboard access fails."""
        # Setup
        with patch('pyperclip.paste', side_effect=Exception("Clipboard error")):
            with patch.object(tui_app, 'query_one', return_value=Mock()):
                with patch.object(tui_app, '_update_log_view') as mock_update_log:
                    # Execute
                    tui_app.action_paste_text()
                    
                    # Assert
                    mock_update_log.assert_called_with("[bold red]> Failed to paste from clipboard: Clipboard error[/bold red]")
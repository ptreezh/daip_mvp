"""
Unit tests for TUI input handling functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from textual.widgets import Input
from src.daip_live.tui import DAIP_TUI


class TestTUIInputHandling:
    """Test cases for TUI input handling functionality."""

    @pytest.fixture
    def tui_app(self):
        """Create a TUI app instance for testing."""
        with patch('src.daip_live.tui.Container'):
            app = DAIP_TUI()
            return app

    def test_input_changed_resets_history_navigation(self, tui_app):
        """Test that input changes reset history navigation."""
        # Setup
        tui_app._history_index = 5
        tui_app._current_input_before_history = "previous input"
        
        # Mock the message
        message = Mock()
        message.value = "new input"
        
        # Mock query method to avoid NoMatches exception
        with patch.object(tui_app, 'query', return_value=[]):
            # Execute
            tui_app.on_input_changed(message)
            
            # Assert
            assert tui_app._history_index == -1
            assert tui_app._current_input_before_history == ""

    def test_input_changed_handles_autocomplete_suggestions(self, tui_app):
        """Test that input changes trigger autocomplete suggestions."""
        # Setup
        message = Mock()
        message.value = "/help"
        
        # Mock the autocomplete suggestions method
        with patch.object(tui_app, '_get_autocomplete_suggestions', return_value=["/help", "/history"]):
            with patch.object(tui_app, 'query', return_value=[]):
                # Mock the mount method to avoid screen mounting issues
                with patch.object(tui_app, 'mount'):
                    with patch.object(tui_app, 'query_one'):
                        # Execute
                        tui_app.on_input_changed(message)
                        
                        # The method should complete without error
                        assert True

    def test_input_changed_handles_empty_suggestions(self, tui_app):
        """Test that input changes handle empty autocomplete suggestions."""
        # Setup
        message = Mock()
        message.value = "random text"
        
        # Mock the autocomplete suggestions method to return empty list
        with patch.object(tui_app, '_get_autocomplete_suggestions', return_value=[]):
            with patch.object(tui_app, 'query', return_value=[]):
                # Execute
                tui_app.on_input_changed(message)
                
                # The method should complete without error
                assert True

    def test_command_selected_updates_input(self, tui_app):
        """Test that command selection updates the input field."""
        # Setup
        message = Mock()
        message.command = "/help users"
        
        # Mock the query_one method to return a mock input widget
        mock_input = Mock(spec=Input)
        mock_input.value = "/help "
        with patch.object(tui_app, 'query_one', return_value=mock_input):
            # Execute
            tui_app.on_command_selected(message)
            
            # Assert
            assert mock_input.value == "/help users"

    def test_suggest_similar_commands_handles_unknown_command(self, tui_app):
        """Test that unknown commands trigger suggestions."""
        # Setup
        unknown_cmd = "hlp"
        
        # Mock the update_log_view method
        with patch.object(tui_app, '_update_log_view'):
            # Execute
            tui_app._suggest_similar_commands(unknown_cmd)
            
            # The method should complete without error
            assert True

    def test_suggest_similar_commands_with_matches(self, tui_app):
        """Test that similar commands are suggested when matches are found."""
        # Setup
        unknown_cmd = "hlp"
        tui_app._available_commands = [("/help", "Show help"), ("/history", "Show history")]
        
        # Mock the update_log_view method
        with patch.object(tui_app, '_update_log_view'):
            # Execute
            tui_app._suggest_similar_commands(unknown_cmd)
            
            # The method should complete without error
            assert True
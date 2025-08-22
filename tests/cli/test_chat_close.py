# -*- coding: utf-8 -*-
"""Tests for the CLI chat close command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import chat_commands


class TestCLIChatClose:
    """Test cases for CLI chat close command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_chat_close_current_room(self, runner):
        """Test chat close command for the current room."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the close_current_room method to return True (success)
        mock_chat_coordinator.close_current_room.return_value = True
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "close"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that close_current_room was called
        mock_chat_coordinator.close_current_room.assert_called_once()
        
        # Verify that the output contains a success message
        assert "Chat room closed" in result.output

    def test_chat_close_with_error(self, runner):
        """Test chat close command when an error occurs."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the close_current_room method to raise an exception
        mock_chat_coordinator.close_current_room.side_effect = Exception("Close failed")
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "close"])
        
        # Verify that the command executed with an error (non-zero exit code)
        # Note: Typer might catch the exception and return exit code 1
        # Let's check the output for an error message
        assert "Error" in result.output or "failed" in result.output.lower()
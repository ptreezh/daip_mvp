# -*- coding: utf-8 -*-
"""Tests for the CLI chat clear command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import chat_commands


class TestCLIChatClear:
    """Test cases for CLI chat clear command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_chat_clear_with_default_room(self, runner):
        """Test chat clear command with default (current) room."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the clear_room_history method to return True (success)
        mock_chat_coordinator.clear_room_history.return_value = True
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "clear"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that clear_room_history was called
        mock_chat_coordinator.clear_room_history.assert_called_once()
        
        # Verify that the output contains a success message
        assert "Chat history cleared" in result.output

    def test_chat_clear_with_custom_room(self, runner):
        """Test chat clear command with custom room."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the clear_room_history method to return True (success)
        mock_chat_coordinator.clear_room_history.return_value = True
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, [
                "chat", "clear", 
                "--room", "room_12345678"
            ])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that clear_room_history was called with the correct arguments
        mock_chat_coordinator.clear_room_history.assert_called_once_with(
            room_id="room_12345678"
        )
        
        # Verify that the output contains a success message
        assert "Chat history cleared" in result.output

    def test_chat_clear_with_error(self, runner):
        """Test chat clear command when an error occurs."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the clear_room_history method to raise an exception
        mock_chat_coordinator.clear_room_history.side_effect = Exception("Clear failed")
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "clear"])
        
        # Verify that the command executed with an error (non-zero exit code)
        # Note: Typer might catch the exception and return exit code 1
        # Let's check the output for an error message
        assert "Error" in result.output or "failed" in result.output.lower()
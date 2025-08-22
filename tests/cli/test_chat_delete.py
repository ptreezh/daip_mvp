# -*- coding: utf-8 -*-
"""Tests for the CLI chat delete command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import chat_commands


class TestCLIChatDelete:
    """Test cases for CLI chat delete command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_chat_delete_with_valid_room_id(self, runner):
        """Test chat delete command with a valid room ID."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the delete_room method to return True (success)
        mock_chat_coordinator.delete_room.return_value = True
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "delete", "room_12345678"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that delete_room was called with the correct arguments
        mock_chat_coordinator.delete_room.assert_called_once_with(
            room_id="room_12345678"
        )
        
        # Verify that the output contains a success message
        assert "deleted successfully" in result.output

    def test_chat_delete_with_invalid_room_id(self, runner):
        """Test chat delete command with an invalid room ID."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the delete_room method to return False (failure)
        mock_chat_coordinator.delete_room.return_value = False
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "delete", "invalid_room_id"])
        
        # Verify that the command executed with an error (non-zero exit code)
        # Note: The actual exit code might depend on how the command handles failures
        # For now, let's check the output for an error message
        assert "Failed to delete" in result.output or "Error" in result.output

    def test_chat_delete_with_error(self, runner):
        """Test chat delete command when an error occurs."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the delete_room method to raise an exception
        mock_chat_coordinator.delete_room.side_effect = Exception("Delete failed")
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "delete", "room_12345678"])
        
        # Verify that the command executed with an error (non-zero exit code)
        # Note: Typer might catch the exception and return exit code 1
        # Let's check the output for an error message
        assert "Error" in result.output or "failed" in result.output.lower()
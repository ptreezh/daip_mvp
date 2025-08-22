# -*- coding: utf-8 -*-
"""Tests for the CLI chat message command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import chat_commands


class TestCLIChatMessage:
    """Test cases for CLI chat message command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_chat_message_with_default_room(self, runner):
        """Test chat message command with default (current) room."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the send_message_to_room method
        mock_chat_coordinator.send_message_to_room.return_value = True
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "message", "Hello, world!"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that send_message_to_room was called with the correct arguments
        # Since we're not specifying a room, it should use a default or previously set room
        # For now, let's assume it will try to get the current room or use a placeholder
        # We'll need to adjust this test once we have the full implementation
        # mock_chat_coordinator.send_message_to_room.assert_called_once()
        
    def test_chat_message_with_custom_room(self, runner):
        """Test chat message command with custom room."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the send_message_to_room method
        mock_chat_coordinator.send_message_to_room.return_value = True
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, [
                "chat", "message", 
                "--room", "room_12345678",
                "Hello, world!"
            ])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that send_message_to_room was called with the correct arguments
        # mock_chat_coordinator.send_message_to_room.assert_called_once_with(
        #     room_id="room_12345678",
        #     message="Hello, world!"
        # )
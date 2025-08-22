# -*- coding: utf-8 -*-
"""Tests for the CLI chat history command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import chat_commands


class TestCLIChatHistory:
    """Test cases for CLI chat history command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_chat_history_with_default_room(self, runner):
        """Test chat history command with default (current) room."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the get_room_history method to return a list of messages
        mock_chat_coordinator.get_room_history.return_value = [
            {"id": "msg1", "content": "Hello", "sender": "User", "timestamp": "2023-01-01T00:00:00"},
            {"id": "msg2", "content": "Hi there!", "sender": "Assistant", "timestamp": "2023-01-01T00:00:01"}
        ]
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "history"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that get_room_history was called
        mock_chat_coordinator.get_room_history.assert_called_once()
        
        # TODO: Once the actual implementation is done, we can verify the output content
        # For now, we just check that the command runs without error

    def test_chat_history_with_custom_room(self, runner):
        """Test chat history command with custom room."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the get_room_history method to return a list of messages
        mock_chat_coordinator.get_room_history.return_value = [
            {"id": "msg3", "content": "What's up?", "sender": "User", "timestamp": "2023-01-01T00:00:02"},
            {"id": "msg4", "content": "Not much", "sender": "Assistant", "timestamp": "2023-01-01T00:00:03"}
        ]
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, [
                "chat", "history", 
                "--room", "room_12345678"
            ])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that get_room_history was called with the correct arguments
        mock_chat_coordinator.get_room_history.assert_called_once_with(
            room_id="room_12345678"
        )
        
        # TODO: Once the actual implementation is done, we can verify the output content
        # For now, we just check that the command runs without error and the method is called
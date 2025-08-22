# -*- coding: utf-8 -*-
"""Tests for the CLI chat start command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import chat_commands


class TestCLIChatStart:
    """Test cases for CLI chat start command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_chat_start_with_default_config(self, runner):
        """Test chat start command with default configuration."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the create_chat_room method to return a room ID
        mock_chat_coordinator.create_chat_room.return_value = "room_12345678"
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "start", "--topic", "默认讨论主题"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains a room ID
        assert "Chat room created with ID:" in result.output
        # Check that the output contains the expected room ID
        assert "room_12345678" in result.output
        
        # Verify that create_chat_room was called with the correct arguments
        mock_chat_coordinator.create_chat_room.assert_called_once_with(
            topic="默认讨论主题",
            room_name=None
        )

    def test_chat_start_with_custom_config(self, runner):
        """Test chat start command with custom configuration."""
        # Create a mock chat coordinator
        mock_chat_coordinator = MagicMock()
        # Mock the create_chat_room method to return a room ID
        mock_chat_coordinator.create_chat_room.return_value = "room_abcdefgh"
        
        # Patch the get_chat_coordinator function in chat_commands module
        with patch.object(chat_commands, 'get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, [
                "chat", "start", 
                "--topic", "自定义讨论主题",
                "--room", "自定义聊天室名称"
            ])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains a room ID
        assert "Chat room created with ID:" in result.output
        # Check that the output contains the expected room ID
        assert "room_abcdefgh" in result.output
        
        # Verify that create_chat_room was called with the correct arguments
        mock_chat_coordinator.create_chat_room.assert_called_once_with(
            topic="自定义讨论主题",
            room_name="自定义聊天室名称"
        )
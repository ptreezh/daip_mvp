import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from src.cli.main import app
from src.virtual_role_chat.models import ChatRoomConfig, ChatRoomID

@pytest.fixture
def cli_runner():
    return CliRunner()

@pytest.fixture
def mock_chat_room_manager():
    with patch("src.cli.main.ChatRoomManager", autospec=True) as mock_manager_class:
        mock_manager_instance = mock_manager_class.return_value
        mock_manager_instance.create_chat_room.return_value = "mock_room_id_123"
        yield mock_manager_instance

class TestChatCommands:
    def test_chat_start_basic(self, cli_runner, mock_chat_room_manager):
        result = cli_runner.invoke(app, [
            "chat", "start",
            "--name", "Test Room",
            "--topic", "General Discussion",
            "--roles", "Role1,Role2"
        ])

        assert result.exit_code == 0
        assert "Chat room 'Test Room' created with ID: mock_room_id_123" in result.stdout
        mock_chat_room_manager.create_chat_room.assert_called_once()
        
        # Verify ChatRoomConfig passed correctly
        called_config = mock_chat_room_manager.create_chat_room.call_args[0][0]
        assert isinstance(called_config, ChatRoomConfig)
        assert called_config.name == "Test Room"
        assert called_config.topic == "General Discussion"
        assert called_config.roles == ["Role1", "Role2"]
        assert called_config.mode == "free_form" # Default mode
        assert called_config.interaction_rules == {} # Default rules

    def test_chat_start_with_rules(self, cli_runner, mock_chat_room_manager):
        result = cli_runner.invoke(app, [
            "chat", "start",
            "--name", "Turn-based Debate",
            "--topic", "AI Ethics",
            "--roles", "Ethicist,Technologist",
            "--mode", "debate",
            "--rules", '{"speaking_order": "turn_based", "turn_duration": 60}'
        ])

        assert result.exit_code == 0
        assert "Chat room 'Turn-based Debate' created with ID: mock_room_id_123" in result.stdout
        mock_chat_room_manager.create_chat_room.assert_called_once()

        # Verify ChatRoomConfig and interaction_rules passed correctly
        called_config = mock_chat_room_manager.create_chat_room.call_args[0][0]
        assert isinstance(called_config, ChatRoomConfig)
        assert called_config.name == "Turn-based Debate"
        assert called_config.topic == "AI Ethics"
        assert called_config.roles == ["Ethicist", "Technologist"]
        assert called_config.mode == "debate"
        assert called_config.interaction_rules == {"speaking_order": "turn_based", "turn_duration": 60}

    def test_chat_start_missing_required_args(self, cli_runner):
        result = cli_runner.invoke(app, ["chat", "start"])
        assert result.exit_code != 0
        assert "Missing option '--name'" in result.stderr or "Missing option '--topic'" in result.stderr or "Missing option '--roles'" in result.stderr

    def test_chat_start_invalid_rules_json(self, cli_runner):
        result = cli_runner.invoke(app, [
            "chat", "start",
            "--name", "Invalid Rules",
            "--topic", "Test",
            "--roles", "Role1",
            "--rules", '{"speaking_order": "turn_based", "turn_duration": 60' # Malformed JSON
        ])
        assert result.exit_code != 0
        assert "Error: Invalid JSON format for --rules" in result.stderr

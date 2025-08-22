# -*- coding: utf-8 -*-
"""Tests for the enhanced CLI chat commands."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import chat_commands


class TestCLIChatCommandsEnhanced:
    """Test cases for enhanced CLI chat commands."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_chat_coordinator(self):
        """Create a mock ChatCoordinator instance for testing."""
        return MagicMock()

    def test_chat_start_with_topic_and_room(self, runner, mock_chat_coordinator):
        """Test chat start command with topic and room name."""
        # Setup
        mock_chat_coordinator.create_chat_room.return_value = "test_room_id"
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "start", "--topic", "Test Topic", "--room", "Test Room"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains success message
        assert "Chat room created with ID: test_room_id" in result.output
        
        # Verify that create_chat_room was called with correct arguments
        mock_chat_coordinator.create_chat_room.assert_called_once_with(
            topic="Test Topic",
            room_name="Test Room"
        )

    def test_chat_start_with_topic_only(self, runner, mock_chat_coordinator):
        """Test chat start command with topic only."""
        # Setup
        mock_chat_coordinator.create_chat_room.return_value = "auto_room_id"
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "start", "--topic", "Auto Topic"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that create_chat_room was called with None room name
        mock_chat_coordinator.create_chat_room.assert_called_once_with(
            topic="Auto Topic",
            room_name=None
        )

    def test_chat_message_to_specific_room(self, runner, mock_chat_coordinator):
        """Test chat message command to specific room."""
        # Setup
        mock_chat_coordinator.send_message_to_room.return_value = True
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "message", "Hello World", "--room", "test_room"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains success message
        assert "Message sent to room test_room: Hello World" in result.output
        
        # Verify that send_message_to_room was called with correct arguments
        mock_chat_coordinator.send_message_to_room.assert_called_once_with(
            room_id="test_room",
            message="Hello World",
            sender="user"
        )

    def test_chat_message_to_current_room(self, runner, mock_chat_coordinator):
        """Test chat message command to current room."""
        # Setup
        mock_chat_coordinator.get_current_room_id.return_value = "current_room_id"
        mock_chat_coordinator.send_message_to_room.return_value = True
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "message", "Hello Current"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains success message with current room
        assert "Message sent to current room (current_room_id): Hello Current" in result.output

    def test_chat_message_no_current_room(self, runner, mock_chat_coordinator):
        """Test chat message command when no current room is set."""
        # Setup
        mock_chat_coordinator.get_current_room_id.return_value = None
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "message", "Hello No Room"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains appropriate error message
        assert "No current chat room is active" in result.output

    def test_chat_recommend_roles(self, runner, mock_chat_coordinator):
        """Test chat recommend command."""
        # Setup
        mock_recommendations = [
            {"name": "AI Expert", "description": "Expert in AI", "score": 3},
            {"name": "Data Scientist", "description": "Expert in data", "score": 2}
        ]
        mock_chat_coordinator.recommend_roles_for_topic.return_value = mock_recommendations
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "recommend", "AI and Machine Learning"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains recommendations
        assert "Role recommendations for topic 'AI and Machine Learning'" in result.output
        assert "1. AI Expert (Score: 3)" in result.output
        assert "2. Data Scientist (Score: 2)" in result.output

    def test_chat_upload_document(self, runner, mock_chat_coordinator):
        """Test chat upload command."""
        # Setup
        mock_chat_coordinator.upload_document_to_chat.return_value = True
        
        # Create a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test document content")
            temp_file_path = f.name
        
        try:
            # Patch the get_chat_coordinator function
            with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
                # Run the command
                result = runner.invoke(app, ["chat", "upload", "test_room", temp_file_path])
            
            # Verify that the command executed successfully (exit code 0)
            assert result.exit_code == 0
            
            # Verify that the output contains success message
            assert "Document uploaded successfully to chat room test_room" in result.output
        finally:
            # Clean up the temporary file
            import os
            os.unlink(temp_file_path)

    def test_chat_consensus(self, runner, mock_chat_coordinator):
        """Test chat consensus command."""
        # Setup
        mock_consensus = {
            "consensus_level": "partial",
            "total_messages": 5,
            "agreement_points": ["General topic agreement"],
            "disagreement_points": ["Specific details disagreement"]
        }
        mock_chat_coordinator.get_chat_consensus_info.return_value = mock_consensus
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "consensus", "test_room"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains consensus info
        assert "Consensus analysis for chat room test_room" in result.output
        assert "Consensus Level: partial" in result.output
        assert "Agreement Points:" in result.output
        assert "Disagreement Points:" in result.output

    def test_chat_rules(self, runner, mock_chat_coordinator):
        """Test chat rules command."""
        # Setup
        mock_primitives = [
            {"type": "turn_based", "description": "Turn-based conversation"},
            {"type": "moderated", "description": "Moderated discussion"}
        ]
        mock_chat_coordinator.get_available_chat_primitives.return_value = mock_primitives
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "rules"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains rules
        assert "Available chat rules/primitives:" in result.output
        assert "- turn_based: Turn-based conversation" in result.output
        assert "- moderated: Moderated discussion" in result.output

    def test_chat_current(self, runner, mock_chat_coordinator):
        """Test chat current command."""
        # Setup
        mock_chat_coordinator.get_current_room_id.return_value = "active_room_123"
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "current"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains current room
        assert "Current active chat room: active_room_123" in result.output

    def test_chat_current_no_room(self, runner, mock_chat_coordinator):
        """Test chat current command when no room is active."""
        # Setup
        mock_chat_coordinator.get_current_room_id.return_value = None
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "current"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains no room message
        assert "No chat room is currently active" in result.output

    def test_chat_switch_success(self, runner, mock_chat_coordinator):
        """Test chat switch command when successful."""
        # Setup
        mock_chat_coordinator.set_current_room.return_value = True
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "switch", "new_room_id"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains success message
        assert "Switched to chat room: new_room_id" in result.output

    def test_chat_switch_failure(self, runner, mock_chat_coordinator):
        """Test chat switch command when switching fails."""
        # Setup
        mock_chat_coordinator.set_current_room.return_value = False
        
        # Patch the get_chat_coordinator function
        with patch('src.cli.chat_commands.get_chat_coordinator', return_value=mock_chat_coordinator):
            # Run the command
            result = runner.invoke(app, ["chat", "switch", "nonexistent_room"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains failure message
        assert "Failed to switch to chat room nonexistent_room" in result.output

    def test_chat_help(self, runner):
        """Test that chat help shows all available commands."""
        # Run the help command
        result = runner.invoke(app, ["chat", "--help"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that key commands are shown in help
        assert "start" in result.output
        assert "message" in result.output
        assert "history" in result.output
        assert "recommend" in result.output
        assert "upload" in result.output
        assert "consensus" in result.output
        assert "rules" in result.output
        assert "current" in result.output
        assert "switch" in result.output
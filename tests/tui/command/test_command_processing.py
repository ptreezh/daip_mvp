"""
Command Processing System Tests for newP6 TUI

This test suite implements TDD approach for command processing functionality.
Tests are written first (RED), then implementation follows (GREEN), then refactoring.
"""

import pytest
from unittest.mock import Mock
from typing import List, Optional, Dict, Any

# Import real implementations
from daip_live.tui_v1.command.models import Command, CommandResult
from daip_live.tui_v1.command.parser import CommandParser
from daip_live.tui_v1.command.registry import CommandRegistry
from daip_live.tui_v1.command.handlers.system import HelpCommandHandler, StatusCommandHandler
from daip_live.tui_v1.command.handlers.session import SessionListHandler, SessionShowHandler


# RED TESTS - These will fail initially, driving implementation

class TestCommandParser:
    """Test command parsing functionality"""

    def test_parse_simple_command(self):
        """Test parsing simple single-word commands"""
        # This test will fail initially - driving the need for CommandParser
        parser = CommandParser()
        result = parser.parse("help")

        assert result.command == "help"
        assert result.action is None
        assert result.args == []
        assert result.options == {}
        assert result.raw == "help"

    def test_parse_command_with_action(self):
        """Test parsing command with action"""
        parser = CommandParser()
        result = parser.parse("session list")

        assert result.command == "session"
        assert result.action == "list"
        assert result.args == []
        assert result.options == {}

    def test_parse_command_with_single_argument(self):
        """Test parsing command with single argument"""
        parser = CommandParser()
        result = parser.parse("session show 12345")

        assert result.command == "session"
        assert result.action == "show"
        assert result.args == ["12345"]
        assert result.options == {}

    def test_parse_command_with_multiple_arguments(self):
        """Test parsing command with multiple arguments"""
        parser = CommandParser()
        result = parser.parse("wiki search microservices architecture")

        assert result.command == "wiki"
        assert result.action == "search"
        assert result.args == ["microservices", "architecture"]
        assert result.options == {}

    def test_parse_command_with_quotes(self):
        """Test parsing command with quoted arguments"""
        parser = CommandParser()
        result = parser.parse('knowledge search "microservices architecture"')

        assert result.command == "knowledge"
        assert result.action == "search"
        assert result.args == ["microservices architecture"]
        assert result.options == {}

    def test_parse_command_with_options(self):
        """Test parsing command with options"""
        parser = CommandParser()
        result = parser.parse("session show 12345 --verbose")

        assert result.command == "session"
        assert result.action == "show"
        assert result.args == ["12345"]
        assert result.options == {"verbose": True}

    def test_parse_command_with_option_value(self):
        """Test parsing command with option values"""
        parser = CommandParser()
        result = parser.parse("model switch gpt-4 --temperature 0.7")

        assert result.command == "model"
        assert result.action == "switch"
        assert result.args == ["gpt-4"]
        assert result.options == {"temperature": "0.7"}

    def test_parse_complex_command(self):
        """Test parsing complex command with arguments and multiple options"""
        parser = CommandParser()
        result = parser.parse('assistant ask "What is TDD?" --context programming --verbose')

        assert result.command == "assistant"
        assert result.action == "ask"
        assert result.args == ["What is TDD?"]
        assert result.options == {"context": "programming", "verbose": True}

    def test_parse_empty_command(self):
        """Test parsing empty command"""
        parser = CommandParser()
        result = parser.parse("")

        assert result.command == ""
        assert result.action is None
        assert result.args == []
        assert result.options == {}

    def test_parse_whitespace_only_command(self):
        """Test parsing whitespace-only command"""
        parser = CommandParser()
        result = parser.parse("   \t  ")

        assert result.command == ""
        assert result.action is None
        assert result.args == []
        assert result.options == {}


class TestCommandRegistry:
    """Test command registry functionality"""

    def test_command_registration(self):
        """Test command handler registration"""
        # This will fail initially - driving need for CommandRegistry
        registry = CommandRegistry()
        handler = MockCommandHandler()

        registry.register("help", handler)
        retrieved_handler = registry.get_handler("help")

        assert retrieved_handler is handler

    def test_command_with_action_registration(self):
        """Test command with action registration"""
        registry = CommandRegistry()
        handler = MockCommandHandler()

        registry.register("session.show", handler)
        retrieved_handler = registry.get_handler("session.show")

        assert retrieved_handler is handler

    def test_register_multiple_commands(self):
        """Test registering multiple commands"""
        registry = CommandRegistry()
        help_handler = MockCommandHandler()
        session_handler = MockCommandHandler()

        registry.register("help", help_handler)
        registry.register("session.list", session_handler)

        assert registry.get_handler("help") is help_handler
        assert registry.get_handler("session.list") is session_handler

    def test_get_nonexistent_command(self):
        """Test retrieving non-existent command returns None"""
        registry = CommandRegistry()

        result = registry.get_handler("nonexistent")
        assert result is None

    def test_list_registered_commands(self):
        """Test listing all registered commands"""
        registry = CommandRegistry()
        handler = MockCommandHandler()

        registry.register("help", handler)
        registry.register("session.list", handler)
        registry.register("session.show", handler)

        commands = registry.list_commands()
        expected = ["help", "session.list", "session.show"]
        assert sorted(commands) == sorted(expected)


class TestCommandHandlers:
    """Test command handler functionality"""

    def test_help_command_handler(self):
        """Test help command handler"""
        # This will fail initially - driving need for command handlers
        handler = HelpCommandHandler()

        result = handler.handle([])

        assert result.success == True
        assert "Available Commands" in result.message
        assert "help" in result.message

    def test_status_command_handler(self):
        """Test status command handler"""
        handler = StatusCommandHandler()

        result = handler.handle([])

        assert result.success == True
        assert "System Status" in result.message

    def test_session_list_handler(self):
        """Test session list handler"""
        handler = SessionListHandler()
        handler.session_service = MockSessionService()

        result = handler.handle([])

        assert result.success == True
        assert "Sessions" in result.message

    def test_command_handler_with_service_injection(self):
        """Test command handler with service dependency injection"""
        handler = SessionShowHandler()
        mock_service = Mock()
        mock_service.get_session.return_value = {"id": "12345", "status": "active"}
        handler.session_service = mock_service

        result = handler.handle(["12345"])

        assert result.success == True
        assert "ID: 12345" in result.message
        mock_service.get_session.assert_called_once_with("12345")

    def test_command_handler_with_invalid_arguments(self):
        """Test command handler with invalid arguments"""
        handler = SessionShowHandler()

        result = handler.handle([])  # Missing session ID

        assert result.success == False
        assert "Usage:" in result.message


# Mock Classes for Testing
class MockCommandHandler:
    """Mock command handler for testing"""
    def handle(self, args: List[str]) -> CommandResult:
        return CommandResult(success=True, message="Mock handler executed")


class MockSessionService:
    """Mock session service for testing"""
    def get_session(self, session_id: str):
        return {"id": session_id, "status": "active"}

    def list_sessions(self):
        return [
            {"id": "12345", "name": "Test Session", "status": "active"},
            {"id": "67890", "name": "Another Session", "status": "inactive"}
        ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
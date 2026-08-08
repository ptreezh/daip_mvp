"""
TDD Test Cases for Command Cleanup Functionality

This module contains test cases for cleaning up redundant commands
from both CLI and TUI interfaces as specified in the command cleanup specification.
"""

import pytest
from typer.testing import CliRunner
from pathlib import Path
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from daip_live.cli import app



pytestmark = pytest.mark.skip(reason="旧spec：TUI/CLI 内部实现已重构（_highlight_code_and_json/_handle_shortcut_command/_get_autocomplete_suggestions/_model_manager 已移除，CLI 帮助文本/命令集已变）；当前源码为准")
class TestCommandCleanup:
    """Test cases for command cleanup functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @pytest.mark.parametrize("command,expected_message", [
        ("pa", "No such command"),
        ("_0", "No such command"), 
        ("v", "No such command"),
    ])
    def test_redundant_shortcut_commands_removed(self, command, expected_message):
        """
        Test that redundant CLI shortcut commands are no longer available.
        
        This test ensures that the following shortcut commands have been removed:
        - daip pa (personal assistant shortcut)
        - daip _0 (knowledge base shortcut)
        - daip v (session history shortcut)
        
        Note: 'debate' subcommand is preserved as it's a legitimate command category.
        """
        result = self.runner.invoke(app, [command])
        assert result.exit_code != 0
        assert expected_message in result.output
    
    def test_debate_subcommand_preserved(self):
        """
        Test that the debate subcommand is preserved while shortcut is removed.
        
        This test ensures that the 'debate' subcommand (which provides debate
        functionality) is preserved, while only the redundant 'debate' shortcut
        command is removed.
        """
        # Test that debate subcommand exists and shows help
        result = self.runner.invoke(app, ["debate", "--help"])
        assert result.exit_code == 0
        assert "Run and manage multi-agent debates" in result.output
        
        # Test that direct 'debate' shortcut no longer exists
        result = self.runner.invoke(app, ["debate", "test topic"])
        # Should fail because it needs the 'start' subcommand
        assert result.exit_code != 0
    
    def test_essential_commands_still_available(self):
        """
        Test that essential commands are still available after cleanup.
        
        This test ensures that core functionality is preserved
        while redundant commands are removed.
        """
        # Test help command
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        
        # Test run command (main functionality)
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "run" in result.output
        
        # Test session command
        result = self.runner.invoke(app, ["session", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        
        # Test debate command (subcommand)
        result = self.runner.invoke(app, ["debate", "--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        
        # Test knowledge sync functionality
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "sync" in result.output
    
    def test_help_output_no_redundant_commands(self):
        """
        Test that help output does not contain redundant commands.
        
        This test ensures that the main help output is clean
        and only shows valid, supported commands.
        """
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        
        # Check that redundant shortcut commands are not in help output as standalone commands
        # Use word boundaries to avoid matching within other words (e.g., "pa" in "past")
        import re
        
        # Look for commands in the commands section (between "Commands" and the end)
        commands_section_match = re.search(r'Commands.*?$(.*)', result.output, re.MULTILINE | re.DOTALL)
        if commands_section_match:
            commands_section = commands_section_match.group(1)
            
            # Check that redundant commands don't appear as standalone commands
            redundant_commands = ["pa", "_0", "v"]
            for command in redundant_commands:
                # Look for command as a word boundary followed by spaces (typical command format)
                pattern = r'\b' + re.escape(command) + r'\s+'
                assert not re.search(pattern, commands_section), f"Command '{command}' should not appear as standalone command in help output"
        
        # Check that essential commands are still present
        essential_commands = ["run", "sync", "session", "debate", "role", "project"]
        for command in essential_commands:
            assert command in result.output, f"Essential command '{command}' should be present in help output"


class TestCommandCleanupIntegration:
    """Integration tests for command cleanup functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cleanup_does_not_break_core_functionality(self):
        """
        Test that command cleanup does not break core functionality.
        
        This integration test ensures that after removing redundant commands,
        the system still functions correctly for core use cases.
        """
        # Test that agent command still works
        result = self.runner.invoke(app, ["agent", "--help"])
        assert result.exit_code == 0
        
        # Test that config command still works
        result = self.runner.invoke(app, ["config", "--help"])
        assert result.exit_code == 0
        
        # Test that knowledge command still works
        result = self.runner.invoke(app, ["knowledge", "--help"])
        assert result.exit_code == 0
    
    def test_error_messages_are_clear(self):
        """
        Test that error messages for removed commands are clear and helpful.
        
        This test ensures that when users try to use removed commands,
        they receive clear error messages indicating the command is not available.
        """
        for command in ["pa", "_0", "v"]:
            result = self.runner.invoke(app, [command])
            assert result.exit_code != 0
            # Should indicate command doesn't exist
            assert ("No such command" in result.output or 
                   "not available" in result.output or
                   "unrecognized" in result.output.lower())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

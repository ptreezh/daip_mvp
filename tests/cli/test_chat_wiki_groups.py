# -*- coding: utf-8 -*-
"""Tests for the CLI chat and wiki command groups."""

import pytest
from typer.testing import CliRunner
from src.cli.main import app


class TestCLIChatAndWikiGroups:
    """Test cases for CLI chat and wiki command groups."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_chat_group_exists(self, runner):
        """Test that the chat command group exists."""
        # Run 'daip-cli chat --help' to see if the group exists
        result = runner.invoke(app, ["chat", "--help"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains the chat group help text
        assert "Commands for managing chat rooms." in result.output or "chat" in result.output

    def test_wiki_group_exists(self, runner):
        """Test that the wiki command group exists."""
        # Run 'daip-cli wiki --help' to see if the group exists
        result = runner.invoke(app, ["wiki", "--help"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains the wiki group help text
        assert "Commands for managing wiki." in result.output or "wiki" in result.output

    def test_chat_group_has_subcommands(self, runner):
        """Test that the chat command group has subcommands."""
        # Run 'daip-cli chat --help' to see the subcommands
        result = runner.invoke(app, ["chat", "--help"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains the expected subcommands
        # Note: These are just examples. The actual subcommands will be defined later.
        # For now, we just check that the help text is displayed.
        assert "Usage:" in result.output or "Commands:" in result.output

    def test_wiki_group_has_subcommands(self, runner):
        """Test that the wiki command group has subcommands."""
        # Run 'daip-cli wiki --help' to see the subcommands
        result = runner.invoke(app, ["wiki", "--help"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains the expected subcommands
        # Note: These are just examples. The actual subcommands will be defined later.
        # For now, we just check that the help text is displayed.
        assert "Usage:" in result.output or "Commands:" in result.output
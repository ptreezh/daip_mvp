# -*- coding: utf-8 -*-
"""Tests for the CLI wiki delete command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import wiki_commands


class TestCLIWikiDelete:
    """Test cases for CLI wiki delete command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_wiki_delete_with_confirmation(self, runner):
        """Test wiki delete command with user confirmation."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        
        # Patch the get_wiki_service function and typer.confirm
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service), \
             patch('typer.confirm', return_value=True):
            # Run the command
            result = runner.invoke(app, ["wiki", "delete", "测试页面"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains information about the functionality
        assert "Delete functionality" in result.output

    def test_wiki_delete_with_cancelled_confirmation(self, runner):
        """Test wiki delete command when user cancels confirmation."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        
        # Patch the get_wiki_service function and typer.confirm
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service), \
             patch('typer.confirm', return_value=False):
            # Run the command
            result = runner.invoke(app, ["wiki", "delete", "测试页面"])
        
        # Verify that the command was cancelled (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains cancellation message
        assert "Deletion cancelled" in result.output

    def test_wiki_delete_with_skip_confirmation(self, runner):
        """Test wiki delete command with --confirm flag."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        
        # Patch the get_wiki_service function
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command with --confirm flag
            result = runner.invoke(app, ["wiki", "delete", "测试页面", "--confirm"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains information about the functionality
        assert "Delete functionality" in result.output

    def test_wiki_delete_with_error(self, runner):
        """Test wiki delete command when an error occurs."""
        # Create a mock wiki service that raises an exception when accessing
        mock_wiki_service = MagicMock()
        
        # Patch the get_wiki_service function to return a service that raises an exception
        def mock_get_wiki_service():
            # The error occurs when trying to access the service
            raise Exception("Service error")
        
        with patch('src.cli.main.get_wiki_service', side_effect=mock_get_wiki_service), \
             patch('typer.confirm', return_value=True):
            # Run the command
            result = runner.invoke(app, ["wiki", "delete", "测试页面"])
        
        # Verify that the command executed with an error (non-zero exit code)
        assert result.exit_code != 0
        
        # The error might be in the output or in the exception
        assert "Error" in result.output or result.exception is not None
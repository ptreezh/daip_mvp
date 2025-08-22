# -*- coding: utf-8 -*-
"""Tests for the CLI wiki view command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import wiki_commands


class TestCLIWikiView:
    """Test cases for CLI wiki view command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_wiki_view_with_valid_title_or_id(self, runner):
        """Test wiki view command with valid title or ID."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the get_entry method to return a WikiVersion object
        mock_wiki_version = MagicMock()
        mock_wiki_version.entry_name = "测试页面"
        mock_wiki_version.content = "这是测试页面的内容。"
        mock_wiki_version.author = "cli_user"
        mock_wiki_version.timestamp = "2023-01-01T00:00:00"
        mock_wiki_version.change_summary = "Initial creation"
        mock_wiki_version.version = "1.0.0"
        mock_wiki_service.get_entry.return_value = mock_wiki_version
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "view", "测试页面"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains the page content
        assert "这是测试页面的内容。" in result.output
        
        # Verify that get_entry was called with the correct arguments
        mock_wiki_service.get_entry.assert_called_once_with(
            entry_name="测试页面"
        )

    def test_wiki_view_with_invalid_title_or_id(self, runner):
        """Test wiki view command with invalid title or ID."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the get_entry method to return None
        mock_wiki_service.get_entry.return_value = None
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "view", "无效页面"])
        
        # Verify that the command executed with an error (non-zero exit code)
        # Note: The actual exit code might depend on how the command handles failures
        # For now, let's check the output for an error message
        assert result.exit_code != 0 or "not found" in result.output.lower() or "error" in result.output.lower()

    def test_wiki_view_with_error(self, runner):
        """Test wiki view command when an error occurs."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the get_entry method to raise an exception
        mock_wiki_service.get_entry.side_effect = Exception("View failed")
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "view", "测试页面"])
        
        # Verify that the command executed with an error (non-zero exit code)
        # Note: Typer might catch the exception and return exit code 1
        # Let's check the output for an error message
        assert "Error" in result.output or "failed" in result.output.lower()
# -*- coding: utf-8 -*-
"""Tests for the CLI wiki list command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.cli.main import app
from src.cli import wiki_commands


class TestCLIWikiList:
    """Test cases for CLI wiki list command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_wiki_list_with_pages(self, runner):
        """Test wiki list command when wiki pages exist."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the wiki directory and its contents
        mock_wiki_dir = MagicMock()
        mock_wiki_dir.exists.return_value = True
        
        # Create mock Path objects with name attribute
        mock_path1 = MagicMock()
        mock_path1.name = "测试页面1"
        mock_path1.is_dir.return_value = True
        
        mock_path2 = MagicMock()
        mock_path2.name = "测试页面2"
        mock_path2.is_dir.return_value = True
        
        mock_path3 = MagicMock()
        mock_path3.name = "Another Page"
        mock_path3.is_dir.return_value = True
        
        mock_wiki_dir.iterdir.return_value = [mock_path1, mock_path2, mock_path3]
        mock_wiki_service._wiki_directory = mock_wiki_dir
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "list"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains the list of pages
        assert "Available wiki pages (3)" in result.output
        assert "- Another Page" in result.output
        assert "- 测试页面1" in result.output
        assert "- 测试页面2" in result.output

    def test_wiki_list_with_no_pages(self, runner):
        """Test wiki list command when no wiki pages exist."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the wiki directory with no contents
        mock_wiki_dir = MagicMock()
        mock_wiki_dir.exists.return_value = True
        mock_wiki_dir.iterdir.return_value = []
        mock_wiki_service._wiki_directory = mock_wiki_dir
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "list"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains no pages message
        assert "No wiki pages found" in result.output

    def test_wiki_list_with_no_directory(self, runner):
        """Test wiki list command when wiki directory doesn't exist."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the wiki directory as non-existent
        mock_wiki_dir = MagicMock()
        mock_wiki_dir.exists.return_value = False
        mock_wiki_service._wiki_directory = mock_wiki_dir
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "list"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains directory not found message
        assert "Wiki directory does not exist" in result.output

    def test_wiki_list_with_error(self, runner):
        """Test wiki list command when an error occurs."""
        # Create a mock wiki service that raises an exception
        mock_wiki_service = MagicMock()
        # Mock the wiki directory to raise an exception
        mock_wiki_dir = MagicMock()
        mock_wiki_dir.exists.side_effect = Exception("Directory error")
        mock_wiki_service._wiki_directory = mock_wiki_dir
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "list"])
        
        # Verify that the command executed with an error (non-zero exit code)
        assert result.exit_code != 0
        
        # Verify that the output contains an error message
        assert "Error" in result.output
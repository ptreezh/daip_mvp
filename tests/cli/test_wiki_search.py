# -*- coding: utf-8 -*-
"""Tests for the CLI wiki search command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import wiki_commands


class TestCLIWikiSearch:
    """Test cases for CLI wiki search command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_wiki_search_with_results(self, runner):
        """Test wiki search command with search results."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the search method to return results
        mock_results = [
            "[测试页面1]: 这是测试页面的内容...",
            "[测试页面2]: 这是另一个测试页面的内容..."
        ]
        mock_wiki_service.search.return_value = mock_results
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "search", "测试"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains search results
        assert "Search results for '测试'" in result.output
        assert "1. [测试页面1]: 这是测试页面的内容..." in result.output
        assert "2. [测试页面2]: 这是另一个测试页面的内容..." in result.output
        
        # Verify that search was called with the correct arguments
        mock_wiki_service.search.assert_called_once_with(query="测试", top_k=3)

    def test_wiki_search_with_no_results(self, runner):
        """Test wiki search command with no search results."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the search method to return empty results
        mock_wiki_service.search.return_value = []
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "search", "不存在的关键词"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains no results message
        assert "No results found for '不存在的关键词'" in result.output
        
        # Verify that search was called with the correct arguments
        mock_wiki_service.search.assert_called_once_with(query="不存在的关键词", top_k=3)

    def test_wiki_search_with_custom_limit(self, runner):
        """Test wiki search command with custom result limit."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the search method to return results
        mock_results = ["[结果1]: 内容1...", "[结果2]: 内容2..."]
        mock_wiki_service.search.return_value = mock_results
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command with custom limit
            result = runner.invoke(app, ["wiki", "search", "测试", "--limit", "5"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that search was called with the correct arguments
        mock_wiki_service.search.assert_called_once_with(query="测试", top_k=5)

    def test_wiki_search_with_error(self, runner):
        """Test wiki search command when an error occurs."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the search method to raise an exception
        mock_wiki_service.search.side_effect = Exception("Search failed")
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "search", "测试"])
        
        # Verify that the command executed with an error (non-zero exit code)
        assert result.exit_code != 0
        
        # Verify that the output contains an error message
        assert "Error" in result.output
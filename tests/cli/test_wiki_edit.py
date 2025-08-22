# -*- coding: utf-8 -*-
"""Tests for the CLI wiki edit command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app
from src.cli import wiki_commands


class TestCLIWikiEdit:
    """Test cases for CLI wiki edit command."""

    @pytest.fixture
    def runner(self):
        """Create a CliRunner instance for testing."""
        return CliRunner()

    def test_wiki_edit_with_valid_title_and_content(self, runner):
        """Test wiki edit command with valid title and content."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the propose_edit method to return a proposal ID
        mock_wiki_service.propose_edit.return_value = "test-proposal-id"
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "edit", "测试页面", "--content", "这是更新后的内容"])
        
        # Verify that the command executed successfully (exit code 0)
        assert result.exit_code == 0
        
        # Verify that the output contains a success message with the proposal ID
        assert "Edit proposal for '测试页面' created successfully" in result.output
        assert "test-proposal-id" in result.output
        
        # Verify that propose_edit was called with the correct arguments
        mock_wiki_service.propose_edit.assert_called_once_with(
            entry_name="测试页面",
            new_content="这是更新后的内容",
            author_role="cli_user",
            change_summary="CLI edit"
        )

    def test_wiki_edit_with_valid_title_and_file_content(self, runner):
        """Test wiki edit command with valid title and content from file."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the propose_edit method to return a proposal ID
        mock_wiki_service.propose_edit.return_value = "test-proposal-file"
        
        # Create a temporary file with content
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("这是来自文件的更新内容")
            temp_file_path = f.name
        
        try:
            # Patch the get_wiki_service function in main module
            with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
                # Run the command
                result = runner.invoke(app, ["wiki", "edit", "测试页面2", "--file", temp_file_path])
            
            # Verify that the command executed successfully (exit code 0)
            assert result.exit_code == 0
            
            # Verify that the output contains a success message with the proposal ID
            assert "Edit proposal for '测试页面2' created successfully" in result.output
            assert "test-proposal-file" in result.output
            
            # Verify that propose_edit was called with the correct arguments
            mock_wiki_service.propose_edit.assert_called_once_with(
                entry_name="测试页面2",
                new_content="这是来自文件的更新内容",
                author_role="cli_user",
                change_summary="CLI edit"
            )
        finally:
            # Clean up the temporary file
            import os
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_wiki_edit_with_invalid_file_path(self, runner):
        """Test wiki edit command with invalid file path."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command with a non-existent file
            result = runner.invoke(app, ["wiki", "edit", "测试页面3", "--file", "/path/to/nonexistent/file.txt"])
        
        # Verify that the command failed (non-zero exit code)
        assert result.exit_code != 0
        
        # Verify that the output contains an error message
        assert "Error" in result.output or "No such file" in result.output

    def test_wiki_edit_with_no_content_or_file(self, runner):
        """Test wiki edit command with no content or file provided."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the propose_edit method to return a proposal ID
        mock_wiki_service.propose_edit.return_value = "test-proposal-empty"
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "edit", "测试页面4"])
        
        # Verify that the command executed successfully (exit code 0)
        # It should create a proposal with empty content
        assert result.exit_code == 0
        
        # Verify that the output contains a success message with the proposal ID
        assert "Edit proposal for '测试页面4' created successfully" in result.output
        assert "test-proposal-empty" in result.output
        
        # Verify that propose_edit was called with empty content
        mock_wiki_service.propose_edit.assert_called_once_with(
            entry_name="测试页面4",
            new_content="",
            author_role="cli_user",
            change_summary="CLI edit"
        )

    def test_wiki_edit_with_error(self, runner):
        """Test wiki edit command when an error occurs."""
        # Create a mock wiki service
        mock_wiki_service = MagicMock()
        # Mock the propose_edit method to raise an exception
        mock_wiki_service.propose_edit.side_effect = Exception("Edit failed")
        
        # Patch the get_wiki_service function in main module
        with patch('src.cli.main.get_wiki_service', return_value=mock_wiki_service):
            # Run the command
            result = runner.invoke(app, ["wiki", "edit", "测试页面", "--content", "测试内容"])
        
        # Verify that the command executed with an error (non-zero exit code)
        assert result.exit_code != 0
        
        # Verify that the output contains an error message
        assert "Error" in result.output
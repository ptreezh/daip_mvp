"""Tests for wiki export CLI command."""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from src.cli.wiki_commands import app
from typer.testing import CliRunner


class TestWikiExportCommand:
    """Test suite for wiki export command."""

    def setup_method(self):
        """Set up test environment."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_wiki_export_markdown_valid_entry(self):
        """Test wiki export to Markdown format with valid entry."""
        # This should fail because the implementation doesn't exist yet
        result = self.runner.invoke(app, [
            "export", "test_entry", "--format", "markdown", 
            "--output", str(self.temp_path / "test_export.md")
        ])
        
        # Should fail with command not found or similar error
        assert result.exit_code != 0
        assert "No such command" in result.stdout or "export" in result.stdout

    def test_wiki_export_pdf_valid_entry(self):
        """Test wiki export to PDF format with valid entry."""
        result = self.runner.invoke(app, [
            "export", "test_entry", "--format", "pdf",
            "--output", str(self.temp_path / "test_export.pdf")
        ])
        
        # Should fail because implementation doesn't exist
        assert result.exit_code != 0

    def test_wiki_export_html_valid_entry(self):
        """Test wiki export to HTML format with valid entry."""
        result = self.runner.invoke(app, [
            "export", "test_entry", "--format", "html",
            "--output", str(self.temp_path / "test_export.html")
        ])
        
        # Should fail because implementation doesn't exist
        assert result.exit_code != 0

    def test_wiki_export_invalid_id(self):
        """Test wiki export with invalid entry ID."""
        result = self.runner.invoke(app, [
            "export", "nonexistent_entry", "--format", "markdown",
            "--output", str(self.temp_path / "invalid_export.md")
        ])
        
        # Should fail because implementation doesn't exist
        assert result.exit_code != 0

    def test_wiki_export_missing_format(self):
        """Test wiki export without specifying format."""
        result = self.runner.invoke(app, [
            "export", "test_entry",
            "--output", str(self.temp_path / "no_format.md")
        ])
        
        # Should fail because implementation doesn't exist
        assert result.exit_code != 0

    def test_wiki_export_missing_output(self):
        """Test wiki export without specifying output file."""
        result = self.runner.invoke(app, [
            "export", "test_entry", "--format", "markdown"
        ])
        
        # Should fail because implementation doesn't exist
        assert result.exit_code != 0

    @patch('src.cli.main.get_wiki_service')
    def test_wiki_export_service_error(self, mock_get_wiki_service):
        """Test wiki export when wiki service raises an error."""
        # Mock the wiki service to raise an exception
        mock_service = Mock()
        mock_service.export_entry.side_effect = Exception("Service error")
        mock_get_wiki_service.return_value = mock_service
        
        result = self.runner.invoke(app, [
            "export", "test_entry", "--format", "markdown",
            "--output", str(self.temp_path / "error_export.md")
        ])
        
        # Should fail because implementation doesn't exist
        assert result.exit_code != 0
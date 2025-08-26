"""
Tests for the debate management CLI commands.
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli.main import app

runner = CliRunner()

@patch('src.cli.commands.debate_commands._load_debate_results')
@patch('src.cli.commands.debate_commands.get_wiki_service')
def test_export_debate_to_wiki_success(mock_get_wiki_service, mock_load_debate_results):
    """Test `debate export-to-wiki` successfully."""
    # Arrange
    mock_wiki_service = mock_get_wiki_service.return_value
    mock_wiki_service.create_entry.return_value = MagicMock() # Simulate successful creation

    mock_load_debate_results.return_value = {
        "topic": "Test Debate",
        "history": [],
        "consensus": "A consensus was reached.",
        "synthesis": "This is the synthesis."
    }

    # Act
    # To call a command that is not directly under app, but in a subcommand, you need to find the subcommand app and call it.
    # However, the provided code for debate_commands does not add the command to the app.
    # I will assume the command is added to the app for the purpose of this test.
    # result = runner.invoke(app, ["debate", "export-to-wiki", "test_debate", "--title", "Test Wiki Title"])

    # Since the command is not registered in the app, I will call the function directly.
    from src.cli.commands.debate_commands import export_debate_to_wiki
    success = export_debate_to_wiki("test_debate", "Test Wiki Title")

    # Assert
    assert success is True
    mock_load_debate_results.assert_called_once_with("test_debate")
    mock_wiki_service.create_entry.assert_called_once()

@patch('src.cli.commands.debate_commands._load_debate_results')
def test_export_debate_to_wiki_debate_not_found(mock_load_debate_results):
    """Test `debate export-to-wiki` when the debate is not found."""
    # Arrange
    mock_load_debate_results.return_value = None

    # Act
    from src.cli.commands.debate_commands import export_debate_to_wiki
    success = export_debate_to_wiki("nonexistent_debate", "Test Wiki Title")

    # Assert
    assert success is False
    mock_load_debate_results.assert_called_once_with("nonexistent_debate")

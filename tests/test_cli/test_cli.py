
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from src.daip_live.cli import app

runner = CliRunner()

@patch('src.daip_live.cli.KnowledgeManager')
@patch('src.daip_live.cli.LiteLLMProvider')
@patch('src.daip_live.cli.ProviderConfig')
def test_knowledge_sync_command(MockProviderConfig, MockLiteLLMProvider, MockKnowledgeManager):
    """
    Tests that the 'sync' command initializes services and calls the sync method.
    """
    # Arrange
    mock_manager_instance = MockKnowledgeManager.return_value
    mock_manager_instance.sync.return_value = None

    # Act
    result = runner.invoke(app, ["sync"])

    # Assert
    assert result.exit_code == 0
    MockProviderConfig.assert_called_once_with(model="all-MiniLM-L6-v2")
    MockLiteLLMProvider.assert_called_once()
    MockKnowledgeManager.assert_called_once()
    mock_manager_instance.sync.assert_called_once()
    assert "Knowledge base sync started..." in result.stdout
    assert "Knowledge base sync completed." in result.stdout

def test_project_scaffold_command_exists():
    """Tests that the 'daip project scaffold' command is registered and runs."""
    # Act
    result = runner.invoke(app, ["project", "scaffold", "--description", "A test project"])

    # Assert
    # This will fail initially because the command does not exist.
    assert result.exit_code == 0
    assert "Scaffold feature is under development" in result.stdout

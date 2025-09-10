import pytest
from unittest.mock import MagicMock, patch

from daip_live.cli import app
from typer.testing import CliRunner
from daip_live.core.models import AppConfig, DatabaseConfig, LLMProviderConfig, KnowledgeBaseConfig

runner = CliRunner()

# Helper to create a mock config
def create_mock_config() -> AppConfig:
    return AppConfig(
        database=DatabaseConfig(path="mock_db.db"),
        llm_provider=LLMProviderConfig(default_model="mock_model", embedding_model="mock_embed_model"),
        knowledge_base=KnowledgeBaseConfig(directory="mock_docs/")
    )


@patch('daip_live.cli.config_manager')
@patch('daip_live.cli.DAIP_TUI')
@patch('daip_live.cli.AgentExecutor')
@patch('daip_live.cli.ToolManager')
@patch('daip_live.cli.LiteLLMProvider')
@patch('daip_live.cli.KnowledgeManager')
@patch('daip_live.cli.DatabaseManager')
@patch('daip_live.cli.MemoryService')
def test_run_command_initializes_and_runs_tui(
    MockMemoryService: MagicMock,
    MockDatabaseManager: MagicMock,
    MockKnowledgeManager: MagicMock,
    MockLiteLLMProvider: MagicMock,
    MockToolManager: MagicMock,
    MockAgentExecutor: MagicMock,
    MockDaipTUI: MagicMock,
    MockConfigManager: MagicMock,
):
    """
    Tests that the 'run' command correctly initializes all services,
    the AgentExecutor, and the TUI, then starts the TUI.
    """
    goal = "Test goal"
    
    # Configure the mock config manager
    mock_config = create_mock_config()
    MockConfigManager.get_config.return_value = mock_config

    # Mock instances
    mock_tui_instance = MockDaipTUI.return_value
    mock_executor_instance = MockAgentExecutor.return_value

    # Invoke the CLI command
    result = runner.invoke(app, ["run", goal])

    # Assertions
    assert result.exit_code == 0, f"CLI command failed: {result.stdout}"

    # Verify services were instantiated correctly using config values
    MockDatabaseManager.assert_called_once_with(db_path=mock_config.database.path)
    MockKnowledgeManager.assert_called_once_with(
        db_manager=MockDatabaseManager.return_value,
        model_provider=MockLiteLLMProvider.return_value,
        config={"knowledge_dir": mock_config.knowledge_base.directory}
    )
    assert MockLiteLLMProvider.call_count == 2
    MockToolManager.assert_called_once_with()
    MockMemoryService.assert_called_once_with()

    # Verify AgentExecutor was instantiated correctly
    MockAgentExecutor.assert_called_once()

    # Verify TUI was instantiated and run
    MockDaipTUI.assert_called_once_with(executor=mock_executor_instance, goal=goal)
    mock_tui_instance.run.assert_called_once_with()
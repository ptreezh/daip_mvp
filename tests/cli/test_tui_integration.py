"""@Time    : 2024-07-19 11:15:00
@Author  : DAIP-LIVE Team
@File    : test_tui_integration.py
@Description:
    Integration tests for the CLI in src.cli.main.
    These tests simulate the interaction between the CLI and the backend services.
"""
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from src.cli.main import app

# Use pytest_asyncio for async tests
pytestmark = pytest.mark.asyncio


@pytest.fixture
def cli_runner():
    """Fixture that provides a CLI test runner."""
    return CliRunner()


@patch("src.cli.commands.run_debate_command")
@patch("src.cli.main.asyncio.run")
async def test_cli_integration_with_backend_success(mock_asyncio_run, mock_run_debate, cli_runner):
    """Test that the CLI integrates properly with backend services for a successful debate."""
    # Mock successful debate execution
    mock_run_debate.return_value = True
    mock_asyncio_run.return_value = True  # asyncio.run should return the result of run_debate_command

    result = cli_runner.invoke(app, [
        "start",
        "Should AI be regulated?",
        "--role", "Policy Expert",
        "--role", "Tech Entrepreneur",
        "--rounds", "2",
        "--verbose"
    ])

    assert result.exit_code == 0
    assert "Initializing debate" in result.stdout
    assert "completed successfully" in result.stdout

    # Verify the backend was called with correct parameters
    mock_run_debate.assert_called_once()
    call_args = mock_run_debate.call_args
    assert call_args[1]["topic"] == "Should AI be regulated?"
    assert call_args[1]["roles"] == ["Policy Expert", "Tech Entrepreneur"]
    assert call_args[1]["rounds"] == 2
    assert call_args[1]["verbose"] is True


@patch("src.cli.commands.run_debate_command")
@patch("src.cli.main.asyncio.run")
async def test_cli_integration_with_backend_failure(mock_asyncio_run, mock_run_debate, cli_runner):
    """Test that the CLI handles backend service failures gracefully."""
    # Mock failed debate execution
    mock_run_debate.return_value = False
    mock_asyncio_run.return_value = False  # asyncio.run should return the result of run_debate_command

    result = cli_runner.invoke(app, ["start", "Test topic"])

    assert result.exit_code == 1
    assert "failed to complete successfully" in result.stdout
    assert "Troubleshooting tips" in result.stdout


@patch("src.cli.commands.run_debate_command")
@patch("src.cli.main.asyncio.run")
async def test_cli_integration_with_exception_handling(mock_asyncio_run, mock_run_debate, cli_runner):
    """Test that the CLI handles various exceptions from backend services."""
    # Test connection error
    mock_asyncio_run.side_effect = Exception("Connection refused")

    result = cli_runner.invoke(app, ["start", "Test topic"])

    assert result.exit_code == 1
    assert "Connection issue detected" in result.stdout
    assert "Check if LLM server is running" in result.stdout


@patch("src.cli.commands.list_available_roles")
async def test_cli_roles_integration_with_backend(mock_list_roles, cli_runner):
    """Test that the roles command integrates properly with the role management backend."""
    # Mock role data from backend
    mock_list_roles.return_value = [
        {
            "name": "Climate Scientist",
            "description": "Expert in climate change research",
            "tags": ["science", "environment"]
        },
        {
            "name": "Economist",
            "description": "Specialist in economic analysis",
            "tags": ["economics", "policy"]
        }
    ]

    result = cli_runner.invoke(app, ["roles"])

    assert result.exit_code == 0
    assert "Climate Scientist" in result.stdout
    assert "Economist" in result.stdout
    # The description might be wrapped in the table, so check for key parts
    assert "Expert in climate change" in result.stdout
    assert "Available Categories" in result.stdout

    # Verify backend was called
    mock_list_roles.assert_called_once()


@patch("src.cli.commands.list_available_roles")
async def test_cli_roles_integration_with_backend_error(mock_list_roles, cli_runner):
    """Test that the roles command handles backend errors gracefully."""
    # Mock backend error
    mock_list_roles.side_effect = ImportError("Cannot import role service")

    result = cli_runner.invoke(app, ["roles"])

    assert result.exit_code == 0  # Should not crash
    assert "Cannot import role listing functionality" in result.stdout
    assert "missing dependencies" in result.stdout


@patch("src.cli.commands.check_system_health")
async def test_cli_status_integration_with_backend(mock_check_health, cli_runner):
    """Test that the status command integrates with backend health checks."""
    # Mock system health data
    mock_check_health.return_value = {
        "llm_service": {
            "status": "✅ Connected",
            "details": "Ollama server responding"
        },
        "memory_service": {
            "status": "✅ Operational",
            "details": "Database connection active"
        }
    }

    result = cli_runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "System Status" in result.stdout
    # The mocked health check results should appear in the Service Initialization Test section
    assert "Ollama server responding" in result.stdout
    assert "Database connection active" in result.stdout

    # Verify backend health check was called
    mock_check_health.assert_called_once()


@patch("src.cli.commands.run_debate_command")
@patch("src.cli.main.asyncio.run")
async def test_cli_save_functionality_integration(mock_asyncio_run, mock_run_debate, cli_runner):
    """Test that the CLI save functionality integrates with backend properly."""
    mock_run_debate.return_value = True
    mock_asyncio_run.return_value = True  # asyncio.run should return the result of run_debate_command

    result = cli_runner.invoke(app, [
        "start",
        "Test debate topic",
        "--save",
        "--output", "test_results.txt"
    ])

    assert result.exit_code == 0
    assert "Results saved to: test_results.txt" in result.stdout

    # Verify save parameters were passed to backend
    call_args = mock_run_debate.call_args
    assert call_args[1]["save_results"] is True
    assert call_args[1]["output_file"] == "test_results.txt"


@patch("src.cli.commands.run_debate_command")
@patch("src.cli.main.asyncio.run")
async def test_cli_consensus_strategy_integration(mock_asyncio_run, mock_run_debate, cli_runner):
    """Test that consensus strategy selection integrates with backend."""
    mock_run_debate.return_value = True
    mock_asyncio_run.return_value = True  # asyncio.run should return the result of run_debate_command

    result = cli_runner.invoke(app, [
        "start",
        "Test topic",
        "--consensus", "weighted_vote"
    ])

    assert result.exit_code == 0

    # Verify consensus strategy was passed to backend
    call_args = mock_run_debate.call_args
    assert call_args[1]["consensus_strategy"] == "weighted_vote"

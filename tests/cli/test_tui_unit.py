"""@Time    : 2024-07-19 11:15:00
@Author  : DAIP-LIVE Team
@File    : test_tui_unit.py
@Description:
    Unit tests for the CLI components in src.cli.main.
    These tests focus on testing the actual CLI commands using typer's testing framework.
"""
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from src.cli.main import app


@pytest.fixture()
def cli_runner():
    """Fixture that provides a CLI test runner."""
    return CliRunner()


def test_help_command(cli_runner):
    """Test that the help command works correctly."""
    result = cli_runner.invoke(app, ["help"])
    assert result.exit_code == 0
    assert "DAIP-LIVE CLI Help" in result.stdout
    assert "Available Commands:" in result.stdout
    assert "start" in result.stdout
    assert "status" in result.stdout
    assert "roles" in result.stdout


def test_status_command(cli_runner):
    """Test that the status command works correctly."""
    result = cli_runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "System Status" in result.stdout
    assert "Configuration" in result.stdout


@patch("src.cli.commands.list_available_roles")
def test_roles_command_success(mock_list_roles, cli_runner):
    """Test that the roles command works when roles are available."""
    mock_list_roles.return_value = [
        {"name": "Expert", "description": "An expert role", "tags": ["professional"]},
        {"name": "Critic", "description": "A critical thinker", "tags": ["analytical"]}
    ]
    
    result = cli_runner.invoke(app, ["roles"])
    assert result.exit_code == 0
    assert "Available Roles" in result.stdout
    assert "Expert" in result.stdout
    assert "Critic" in result.stdout


@patch("src.cli.commands.list_available_roles")
def test_roles_command_no_roles(mock_list_roles, cli_runner):
    """Test that the roles command handles empty role list."""
    mock_list_roles.return_value = []
    
    result = cli_runner.invoke(app, ["roles"])
    assert result.exit_code == 0
    assert "No roles available" in result.stdout


@patch("src.cli.main.asyncio.run")
@patch("src.cli.commands.run_debate_command")
def test_start_command_success(mock_run_debate, mock_asyncio_run, cli_runner):
    """Test that the start command works with valid arguments."""
    mock_run_debate.return_value = True
    mock_asyncio_run.return_value = True  # asyncio.run should return the result of run_debate_command
    
    result = cli_runner.invoke(app, ["start", "Test topic", "--role", "Expert", "--rounds", "2"])
    assert result.exit_code == 0
    assert "Initializing debate" in result.stdout


def test_start_command_validation_errors(cli_runner):
    """Test that the start command validates input correctly."""
    # Test with invalid rounds
    result = cli_runner.invoke(app, ["start", "Test topic", "--rounds", "0"])
    assert result.exit_code == 1
    assert "Number of rounds must be at least 1" in result.stdout
    
    # Test with too short topic
    result = cli_runner.invoke(app, ["start", "ab"])
    assert result.exit_code == 1
    assert "Debate topic must be at least 3 characters long" in result.stdout


@patch("src.cli.main.asyncio.run")
@patch("src.cli.commands.run_debate_command")
def test_start_command_with_save(mock_run_debate, mock_asyncio_run, cli_runner):
    """Test that the start command works with save option."""
    mock_run_debate.return_value = True
    mock_asyncio_run.return_value = True  # asyncio.run should return the result of run_debate_command
    
    result = cli_runner.invoke(app, [
        "start", "Test topic", 
        "--save", 
        "--output", "test_output.txt"
    ])
    assert result.exit_code == 0
    mock_run_debate.assert_called_once()
    # Check that save parameters were passed
    call_args = mock_run_debate.call_args
    assert call_args[1]["save_results"] is True
    assert call_args[1]["output_file"] == "test_output.txt"


@patch("src.cli.main.asyncio.run")
@patch("src.cli.commands.run_debate_command")
def test_start_command_failure(mock_run_debate, mock_asyncio_run, cli_runner):
    """Test that the start command handles failure correctly."""
    mock_asyncio_run.return_value = None
    mock_run_debate.return_value = False
    
    result = cli_runner.invoke(app, ["start", "Test topic"])
    assert result.exit_code == 1
    assert "Debate failed to complete successfully" in result.stdout


@patch("src.cli.main.asyncio.run")
def test_start_command_keyboard_interrupt(mock_asyncio_run, cli_runner):
    """Test that the start command handles keyboard interrupt."""
    mock_asyncio_run.side_effect = KeyboardInterrupt()
    
    result = cli_runner.invoke(app, ["start", "Test topic"])
    assert result.exit_code == 0  # KeyboardInterrupt should exit gracefully
    assert "interrupted by user" in result.stdout


@patch("src.cli.main.asyncio.run")
def test_start_command_timeout_error(mock_asyncio_run, cli_runner):
    """Test that the start command handles timeout errors."""
    import asyncio
    mock_asyncio_run.side_effect = asyncio.TimeoutError()
    
    result = cli_runner.invoke(app, ["start", "Test topic"])
    assert result.exit_code == 1
    assert "timed out" in result.stdout


@patch("src.cli.main.asyncio.run")
def test_start_command_memory_error(mock_asyncio_run, cli_runner):
    """Test that the start command handles memory errors."""
    mock_asyncio_run.side_effect = MemoryError()
    
    result = cli_runner.invoke(app, ["start", "Test topic"])
    assert result.exit_code == 1
    assert "ran out of memory" in result.stdout


def test_start_command_invalid_consensus_strategy(cli_runner):
    """Test that the start command validates consensus strategy."""
    result = cli_runner.invoke(app, [
        "start", "Test topic", 
        "--consensus", "invalid_strategy"
    ])
    assert result.exit_code == 1
    assert "Invalid consensus strategy" in result.stdout

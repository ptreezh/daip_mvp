# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-20 00:00:00
@Author  : DAIP-LIVE Team
@File    : test_cli_commands.py
@Description: Unit tests for CLI command implementations.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from typer.testing import CliRunner

from src.cli.main import app


@pytest.fixture
def cli_runner():
    """Fixture that provides a CLI test runner."""
    return CliRunner()


class TestStartCommand:
    """Test cases for the start command."""
    
    @patch("src.cli.main.asyncio.run")
    @patch("src.cli.commands.run_debate_command")
    def test_start_command_basic_success(self, mock_run_debate, mock_asyncio_run, cli_runner):
        """Test basic start command with minimal arguments."""
        mock_run_debate.return_value = True
        mock_asyncio_run.return_value = True
        
        result = cli_runner.invoke(app, ["start", "Should AI be regulated?"])
        
        assert result.exit_code == 0
        assert "Initializing debate: Should AI be regulated?" in result.stdout
        assert "completed successfully" in result.stdout
        mock_run_debate.assert_called_once()
    
    @patch("src.cli.main.asyncio.run")
    @patch("src.cli.commands.run_debate_command")
    def test_start_command_with_roles(self, mock_run_debate, mock_asyncio_run, cli_runner):
        """Test start command with specific roles."""
        mock_run_debate.return_value = True
        mock_asyncio_run.return_value = True
        
        result = cli_runner.invoke(app, [
            "start", "Climate change solutions",
            "--role", "Environmental Scientist",
            "--role", "Economist"
        ])
        
        assert result.exit_code == 0
        call_args = mock_run_debate.call_args
        assert call_args[1]["topic"] == "Climate change solutions"
        assert call_args[1]["roles"] == ["Environmental Scientist", "Economist"]
    
    @patch("src.cli.main.asyncio.run")
    @patch("src.cli.commands.run_debate_command")
    def test_start_command_with_all_options(self, mock_run_debate, mock_asyncio_run, cli_runner):
        """Test start command with all available options."""
        mock_run_debate.return_value = True
        mock_asyncio_run.return_value = True
        
        result = cli_runner.invoke(app, [
            "start", "Future of work",
            "--role", "Futurist",
            "--role", "Labor Expert",
            "--rounds", "5",
            "--consensus", "weighted_vote",
            "--verbose",
            "--save",
            "--output", "test_results.json"
        ])
        
        assert result.exit_code == 0
        call_args = mock_run_debate.call_args
        assert call_args[1]["topic"] == "Future of work"
        assert call_args[1]["roles"] == ["Futurist", "Labor Expert"]
        assert call_args[1]["rounds"] == 5
        assert call_args[1]["consensus_strategy"] == "weighted_vote"
        assert call_args[1]["verbose"] is True
        assert call_args[1]["save_results"] is True
        assert call_args[1]["output_file"] == "test_results.json"
    
    def test_start_command_validation_short_topic(self, cli_runner):
        """Test validation for topic that's too short."""
        result = cli_runner.invoke(app, ["start", "AI"])
        
        assert result.exit_code == 1
        assert "Debate topic must be at least 3 characters long" in result.stdout
    
    def test_start_command_validation_long_topic(self, cli_runner):
        """Test validation for topic that's too long."""
        long_topic = "A" * 501  # 501 characters
        result = cli_runner.invoke(app, ["start", long_topic])
        
        assert result.exit_code == 1
        assert "Debate topic is too long" in result.stdout
    
    def test_start_command_validation_invalid_rounds(self, cli_runner):
        """Test validation for invalid number of rounds."""
        # Test rounds < 1
        result = cli_runner.invoke(app, ["start", "Test topic", "--rounds", "0"])
        assert result.exit_code == 1
        assert "Number of rounds must be at least 1" in result.stdout
        
        # Test rounds > 20
        result = cli_runner.invoke(app, ["start", "Test topic", "--rounds", "25"])
        assert result.exit_code == 1
        assert "Number of rounds cannot exceed 20" in result.stdout
    
    def test_start_command_validation_invalid_consensus(self, cli_runner):
        """Test validation for invalid consensus strategy."""
        result = cli_runner.invoke(app, [
            "start", "Test topic",
            "--consensus", "invalid_strategy"
        ])
        
        assert result.exit_code == 1
        assert "Invalid consensus strategy" in result.stdout
        assert "simple_majority_vote" in result.stdout
    
    @patch("src.cli.main.asyncio.run")
    @patch("src.cli.commands.run_debate_command")
    def test_start_command_failure(self, mock_run_debate, mock_asyncio_run, cli_runner):
        """Test start command when debate fails."""
        mock_run_debate.return_value = False
        mock_asyncio_run.return_value = False
        
        result = cli_runner.invoke(app, ["start", "Test topic"])
        
        assert result.exit_code == 1
        assert "failed to complete successfully" in result.stdout
        assert "Troubleshooting tips" in result.stdout
    
    @patch("src.cli.main.asyncio.run")
    def test_start_command_keyboard_interrupt(self, mock_asyncio_run, cli_runner):
        """Test start command handles keyboard interrupt gracefully."""
        mock_asyncio_run.side_effect = KeyboardInterrupt()
        
        result = cli_runner.invoke(app, ["start", "Test topic"])
        
        assert result.exit_code == 0
        assert "interrupted by user" in result.stdout
    
    @patch("src.cli.main.asyncio.run")
    def test_start_command_timeout_error(self, mock_asyncio_run, cli_runner):
        """Test start command handles timeout errors."""
        import asyncio
        mock_asyncio_run.side_effect = asyncio.TimeoutError()
        
        result = cli_runner.invoke(app, ["start", "Test topic"])
        
        assert result.exit_code == 1
        assert "timed out" in result.stdout
        assert "Reducing the number of rounds" in result.stdout
    
    @patch("src.cli.main.asyncio.run")
    def test_start_command_memory_error(self, mock_asyncio_run, cli_runner):
        """Test start command handles memory errors."""
        mock_asyncio_run.side_effect = MemoryError()
        
        result = cli_runner.invoke(app, ["start", "Test topic"])
        
        assert result.exit_code == 1
        assert "ran out of memory" in result.stdout
        assert "Use fewer rounds" in result.stdout
    
    @patch("src.cli.main.asyncio.run")
    def test_start_command_connection_error(self, mock_asyncio_run, cli_runner):
        """Test start command handles connection errors."""
        mock_asyncio_run.side_effect = Exception("Connection refused")
        
        result = cli_runner.invoke(app, ["start", "Test topic"])
        
        assert result.exit_code == 1
        assert "Connection issue detected" in result.stdout
        assert "Check if LLM server is running" in result.stdout
    
    @patch("src.cli.main.asyncio.run")
    def test_start_command_permission_error(self, mock_asyncio_run, cli_runner):
        """Test start command handles permission errors."""
        mock_asyncio_run.side_effect = Exception("Permission denied")
        
        result = cli_runner.invoke(app, ["start", "Test topic"])
        
        assert result.exit_code == 1
        assert "Permission issue detected" in result.stdout
        assert "Check file/directory permissions" in result.stdout


class TestStatusCommand:
    """Test cases for the status command."""
    
    def test_status_command_basic(self, cli_runner):
        """Test basic status command functionality."""
        result = cli_runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        assert "DAIP-LIVE System Status" in result.stdout
        assert "System Configuration" in result.stdout
        assert "Configuration" in result.stdout
    
    @patch("src.cli.commands.check_system_health")
    def test_status_command_with_health_check(self, mock_check_health, cli_runner):
        """Test status command with system health check."""
        mock_check_health.return_value = {
            "configuration": {"status": "✅ Loaded", "details": "Config loaded successfully"},
            "dependencies": {"status": "✅ Ready", "details": "All modules installed"},
            "services": {"status": "✅ Ready", "details": "All services initialized"},
            "api": {"status": "✅ Ready", "details": "5 endpoints available"}
        }
        
        result = cli_runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        assert "Config loaded successfully" in result.stdout
        assert "All modules installed" in result.stdout
        mock_check_health.assert_called_once()
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", ["aiosqlite", "chromadb"])
    def test_status_command_with_missing_dependencies(self, cli_runner):
        """Test status command when dependencies are missing."""
        result = cli_runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        assert "Missing Dependencies" in result.stdout
        assert "aiosqlite" in result.stdout
        assert "chromadb" in result.stdout
        assert "pip install" in result.stdout


class TestRolesCommand:
    """Test cases for the roles command."""
    
    @patch("src.cli.commands.list_available_roles")
    def test_roles_command_success(self, mock_list_roles, cli_runner):
        """Test roles command with available roles."""
        mock_list_roles.return_value = [
            {
                "name": "Environmental Scientist",
                "description": "Expert in environmental science and climate research",
                "tags": ["science", "environment", "climate"]
            },
            {
                "name": "Economist",
                "description": "Specialist in economic analysis and policy",
                "tags": ["economics", "policy", "analysis"]
            }
        ]
        
        result = cli_runner.invoke(app, ["roles"])
        
        assert result.exit_code == 0
        assert "Available Roles" in result.stdout
        assert "Environmental Scientist" in result.stdout
        assert "Economist" in result.stdout
        assert "Expert in environmental" in result.stdout
        assert "Available Categories" in result.stdout
        mock_list_roles.assert_called_once()
    
    @patch("src.cli.commands.list_available_roles")
    def test_roles_command_no_roles(self, mock_list_roles, cli_runner):
        """Test roles command when no roles are available."""
        mock_list_roles.return_value = []
        
        result = cli_runner.invoke(app, ["roles"])
        
        assert result.exit_code == 0
        assert "No roles available" in result.stdout
        assert "Troubleshooting" in result.stdout
    
    @patch("src.cli.commands.list_available_roles")
    def test_roles_command_import_error(self, mock_list_roles, cli_runner):
        """Test roles command handles import errors."""
        mock_list_roles.side_effect = ImportError("Cannot import role service")
        
        result = cli_runner.invoke(app, ["roles"])
        
        assert result.exit_code == 0
        assert "Cannot import role listing functionality" in result.stdout
        assert "missing dependencies" in result.stdout
    
    @patch("src.cli.commands.list_available_roles")
    def test_roles_command_general_error(self, mock_list_roles, cli_runner):
        """Test roles command handles general errors."""
        mock_list_roles.side_effect = Exception("Database connection failed")
        
        result = cli_runner.invoke(app, ["roles"])
        
        assert result.exit_code == 0
        assert "Failed to list roles" in result.stdout
        assert "Check system status" in result.stdout


class TestHelpCommand:
    """Test cases for the help command."""
    
    def test_help_command(self, cli_runner):
        """Test help command displays correct information."""
        result = cli_runner.invoke(app, ["help"])
        
        assert result.exit_code == 0
        assert "DAIP-LIVE CLI Help" in result.stdout
        assert "Available Commands:" in result.stdout
        assert "start" in result.stdout
        assert "roles" in result.stdout
        assert "status" in result.stdout
        assert "help" in result.stdout
        assert "Usage Examples:" in result.stdout
        assert "Tips:" in result.stdout


class TestCLIErrorHandling:
    """Test cases for CLI error handling and edge cases."""
    
    def test_invalid_command(self, cli_runner):
        """Test CLI handles invalid commands gracefully."""
        result = cli_runner.invoke(app, ["invalid_command"])
        
        assert result.exit_code != 0
        # Typer will show usage information for invalid commands
    
    def test_start_command_missing_topic(self, cli_runner):
        """Test start command requires topic argument."""
        result = cli_runner.invoke(app, ["start"])
        
        assert result.exit_code != 0
        # Typer will show error for missing required argument
    
    @patch("os.makedirs")
    def test_start_command_output_directory_creation_error(self, mock_makedirs, cli_runner):
        """Test start command handles output directory creation errors."""
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        result = cli_runner.invoke(app, [
            "start", "Test topic",
            "--save",
            "--output", "/invalid/path/output.txt"
        ])
        
        assert result.exit_code == 1
        assert "Cannot create output directory" in result.stdout
        assert "permission denied" in result.stdout
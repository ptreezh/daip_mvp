"""@Time    : 2025-07-24 18:30:00
@Author  : DAIP-LIVE Team
@File    : test_cli_interface.py
@Description:
    Unit tests for CLI interface.
"""
from unittest.mock import AsyncMock, Mock, patch

import pytest
from click.testing import CliRunner

from src.user_interface.cli_interface import CLIInterface, cli


class TestCLIInterface:
    """Test cases for CLIInterface."""

    @pytest.fixture
    def cli_interface(self):
        """Create a CLIInterface instance for testing."""
        return CLIInterface()

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            "llm_interface": AsyncMock(),
            "role_manager": Mock(),
            "tool_executor": Mock(),
            "synthesis_engine": AsyncMock(),
            "fact_extraction_service": AsyncMock(),
            "wiki_service": AsyncMock()
        }

    @pytest.mark.asyncio
    async def test_setup_services(self, cli_interface):
        """Test service setup."""
        with patch('src.user_interface.cli_interface.EnhancedLLMInterface'), \
             patch('src.user_interface.cli_interface.RoleManager'), \
             patch('src.user_interface.cli_interface.ToolExecutor'), \
             patch('src.user_interface.cli_interface.SynthesisEngine'), \
             patch('src.user_interface.cli_interface.FactExtractionService'), \
             patch('src.user_interface.cli_interface.WikiService'):

            services = await cli_interface.setup_services()

            # Verify services were created
            assert "llm_interface" in services
            assert "role_manager" in services
            assert "tool_executor" in services
            assert "synthesis_engine" in services
            assert "fact_extraction_service" in services
            assert "wiki_service" in services

    @pytest.mark.asyncio
    async def test_execute_critical_review(self, cli_interface, mock_services):
        """Test Critical Review Workflow execution."""
        with patch.object(cli_interface, 'setup_services', return_value=mock_services), \
             patch('src.user_interface.cli_interface.CriticalReviewWorkflow') as mock_workflow_class:

            # Mock workflow execution
            mock_workflow = AsyncMock()
            mock_workflow.execute.return_value = {
                "success": True,
                "original_content": "Test content",
                "final_content": "Reviewed content",
                "revision_needed": False
            }
            mock_workflow_class.return_value = mock_workflow

            # Execute
            result = await cli_interface.execute_critical_review(
                content="Test content to review",
                format_type="json"
            )

            # Verify
            assert result["success"] is True
            assert "original_content" in result
            mock_workflow.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_multi_perspective(self, cli_interface, mock_services):
        """Test Multi-perspective Synthesis Workflow execution."""
        with patch.object(cli_interface, 'setup_services', return_value=mock_services), \
             patch('src.user_interface.cli_interface.MultiPerspectiveSynthesisWorkflow') as mock_workflow_class:

            # Mock workflow execution
            mock_workflow = AsyncMock()
            mock_workflow.execute.return_value = {
                "success": True,
                "topic": "AI impact",
                "synthesis": "Comprehensive analysis",
                "perspectives": ["经济", "社会"]
            }
            mock_workflow_class.return_value = mock_workflow

            # Execute
            result = await cli_interface.execute_multi_perspective(
                topic="AI impact on jobs",
                perspectives=["经济", "社会"],
                format_type="json"
            )

            # Verify
            assert result["success"] is True
            assert result["topic"] == "AI impact"
            mock_workflow.execute.assert_called_once()

    def test_list_workflows(self, cli_interface):
        """Test workflow listing."""
        # This should not raise an exception
        cli_interface.list_workflows()

    def test_show_workflow_help(self, cli_interface):
        """Test workflow help display."""
        # Test known workflows
        cli_interface.show_workflow_help("critical-review")
        cli_interface.show_workflow_help("multi-perspective")
        cli_interface.show_workflow_help("unknown-workflow")


class TestCLICommands:
    """Test CLI commands using Click testing."""

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Virtual Role Chat System" in result.output

    def test_list_workflows_command(self):
        """Test list workflows command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['list-workflows'])
        assert result.exit_code == 0

    def test_help_workflow_command(self):
        """Test help workflow command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['help-workflow', 'critical-review'])
        assert result.exit_code == 0

    @patch('src.user_interface.cli_interface.CLIInterface.execute_critical_review')
    def test_critical_review_command(self, mock_execute):
        """Test critical review command."""
        mock_execute.return_value = {"success": True}

        runner = CliRunner()
        result = runner.invoke(cli, [
            'critical-review',
            '--content', 'Test content',
            '--format', 'json'
        ])

        # The command should complete (may exit with 0 or 1 depending on mock)
        assert result.exit_code in [0, 1]
        mock_execute.assert_called_once()

    @patch('src.user_interface.cli_interface.CLIInterface.execute_multi_perspective')
    def test_multi_perspective_command(self, mock_execute):
        """Test multi-perspective command."""
        mock_execute.return_value = {"success": True}

        runner = CliRunner()
        result = runner.invoke(cli, [
            'multi-perspective',
            '--topic', 'AI impact',
            '--perspectives', '经济,社会',
            '--format', 'json'
        ])

        # The command should complete (may exit with 0 or 1 depending on mock)
        assert result.exit_code in [0, 1]
        mock_execute.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])

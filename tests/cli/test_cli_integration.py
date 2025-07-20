# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-20 00:00:00
@Author  : DAIP-LIVE Team
@File    : test_cli_integration.py
@Description: Integration tests for CLI-to-service interactions.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from typer.testing import CliRunner

from src.cli.main import app
from src.cli.commands import CLIDebateHandler, run_debate_command, check_system_health, list_available_roles


@pytest.fixture
def cli_runner():
    """Fixture that provides a CLI test runner."""
    return CliRunner()


class TestCLIServiceIntegration:
    """Test CLI integration with backend services."""
    
    @patch("src.cli.commands.AppState")
    @patch("src.cli.commands.DebateProtocol")
    @pytest.mark.asyncio
    async def test_cli_debate_handler_initialization(self, mock_debate_protocol, mock_app_state):
        """Test CLIDebateHandler initializes services correctly."""
        # Mock AppState and its services
        mock_app_state_instance = MagicMock()
        mock_app_state_instance.synthesis_engine = MagicMock()
        mock_app_state_instance.llm_interface = MagicMock()
        mock_app_state_instance.unified_tool_manager = MagicMock()
        mock_app_state.return_value = mock_app_state_instance
        
        # Mock DebateProtocol
        mock_protocol_instance = MagicMock()
        mock_debate_protocol.return_value = mock_protocol_instance
        
        handler = CLIDebateHandler()
        result = await handler.initialize()
        
        assert result is True
        assert handler.app_state == mock_app_state_instance
        assert handler.debate_protocol == mock_protocol_instance
        mock_app_state.assert_called_once()
        mock_debate_protocol.assert_called_once()
    
    @patch("src.cli.commands.AppState")
    @pytest.mark.asyncio
    async def test_cli_debate_handler_initialization_failure(self, mock_app_state):
        """Test CLIDebateHandler handles initialization failures."""
        mock_app_state.side_effect = Exception("Database connection failed")
        
        handler = CLIDebateHandler()
        result = await handler.initialize()
        
        assert result is False
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", [])
    @pytest.mark.asyncio
    async def test_run_debate_command_success(self):
        """Test run_debate_command integrates with CLIDebateHandler successfully."""
        # For this test, we'll mock the entire function execution
        # since the internal ResultCapturingDebateHandler is complex to mock
        with patch("src.cli.commands.AppState") as mock_app_state:
            with patch("src.cli.commands.CLIDebateHandler.initialize", new_callable=AsyncMock) as mock_init:
                with patch("src.cli.commands.CLIDebateHandler.start_debate", new_callable=AsyncMock) as mock_start:
                    mock_init.return_value = True
                    mock_start.return_value = True
                    
                    result = await run_debate_command(
                        topic="Test topic",
                        roles=["Expert", "Critic"],
                        rounds=3,
                        consensus_strategy="simple_majority_vote",
                        verbose=False
                    )
                    
                    # The function should succeed
                    assert result is True
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", ["aiosqlite"])
    @pytest.mark.asyncio
    async def test_run_debate_command_missing_dependencies(self):
        """Test run_debate_command handles missing dependencies."""
        result = await run_debate_command(
            topic="Test topic",
            roles=["Expert"],
            rounds=2,
            consensus_strategy="simple_majority_vote",
            verbose=False
        )
        
        assert result is False
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", [])
    @patch("src.cli.commands.AppState")
    @pytest.mark.asyncio
    async def test_run_debate_command_role_recommendation(self, mock_app_state):
        """Test run_debate_command recommends roles when none provided."""
        # Mock AppState with role recommendation
        mock_app_state_instance = MagicMock()
        mock_app_state_instance.search_roles_by_vector.return_value = [
            {"role": {"name": "Climate Expert"}},
            {"role": {"name": "Policy Analyst"}}
        ]
        mock_app_state.return_value = mock_app_state_instance
        
        # Mock CLIDebateHandler methods
        with patch("src.cli.commands.CLIDebateHandler.initialize", new_callable=AsyncMock) as mock_init:
            with patch("src.cli.commands.CLIDebateHandler.start_debate", new_callable=AsyncMock) as mock_start:
                mock_init.return_value = True
                mock_start.return_value = True
                
                result = await run_debate_command(
                    topic="Climate change solutions",
                    roles=[],  # No roles provided
                    rounds=2,
                    consensus_strategy="simple_majority_vote",
                    verbose=False
                )
                
                assert result is True
                # Should have called start_debate with recommended roles
                call_args = mock_start.call_args[0]
                assert "Climate Expert" in call_args[1]
                assert "Policy Analyst" in call_args[1]
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", [])
    @patch("src.cli.commands.AppState")
    def test_check_system_health_all_services_healthy(self, mock_app_state):
        """Test check_system_health when all services are healthy."""
        # Mock successful AppState initialization
        mock_app_state_instance = MagicMock()
        mock_app_state.return_value = mock_app_state_instance
        
        # Mock FastAPI app
        with patch("src.main.app") as mock_fastapi:
            mock_route = MagicMock()
            mock_route.path = "/api/test"
            mock_fastapi.routes = [mock_route]
            
            health_info = check_system_health()
            
            assert health_info["dependencies"]["status"] == "✅ Ready"
            assert health_info["services"]["status"] == "✅ Ready"
            assert health_info["api"]["status"] == "✅ Ready"
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", ["chromadb"])
    def test_check_system_health_missing_dependencies(self):
        """Test check_system_health when dependencies are missing."""
        health_info = check_system_health()
        
        assert "❌ Missing dependencies" in health_info["dependencies"]["status"]
        assert "❌ Not available" in health_info["services"]["status"]
        assert "❌ Not available" in health_info["api"]["status"]
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", [])
    @patch("src.cli.commands.AppState")
    def test_check_system_health_service_failure(self, mock_app_state):
        """Test check_system_health when service initialization fails."""
        mock_app_state.side_effect = Exception("Service initialization failed")
        
        health_info = check_system_health()
        
        assert "❌ Failed" in health_info["services"]["status"]
        assert "Service initialization failed" in health_info["services"]["details"]
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", [])
    @patch("src.cli.commands.AppState")
    def test_list_available_roles_success(self, mock_app_state):
        """Test list_available_roles returns roles successfully."""
        # Mock AppState with roles
        mock_app_state_instance = MagicMock()
        mock_app_state_instance.all_roles_details = {
            "Expert": {"desc": "An expert in the field", "tags": ["professional"]},
            "Critic": {"desc": "A critical thinker", "tags": ["analytical"]}
        }
        mock_app_state.return_value = mock_app_state_instance
        
        roles = list_available_roles()
        
        assert len(roles) == 2
        assert roles[0]["name"] == "Critic"  # Should be sorted alphabetically
        assert roles[1]["name"] == "Expert"
        assert "expert in the field" in roles[1]["description"].lower()
        mock_app_state_instance.load_all_roles.assert_called_once()
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", ["tiktoken"])
    def test_list_available_roles_missing_dependencies(self):
        """Test list_available_roles handles missing dependencies."""
        roles = list_available_roles()
        
        assert roles == []
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", [])
    @patch("src.cli.commands.AppState")
    def test_list_available_roles_service_error(self, mock_app_state):
        """Test list_available_roles handles service errors."""
        mock_app_state.side_effect = Exception("Role service unavailable")
        
        roles = list_available_roles()
        
        assert roles == []


class TestCLIEventProcessing:
    """Test CLI event processing and real-time display."""
    
    @patch("src.cli.commands.AppState")
    @patch("src.cli.commands.DebateProtocol")
    @pytest.mark.asyncio
    async def test_cli_debate_handler_event_processing(self, mock_debate_protocol, mock_app_state):
        """Test CLIDebateHandler processes debate events correctly."""
        # Mock services
        mock_app_state_instance = MagicMock()
        mock_app_state.return_value = mock_app_state_instance
        
        mock_protocol_instance = MagicMock()
        mock_protocol_instance.run = AsyncMock()
        mock_debate_protocol.return_value = mock_protocol_instance
        
        # Create handler and initialize
        handler = CLIDebateHandler()
        await handler.initialize()
        
        # Create a proper mock event queue with controlled behavior
        mock_event_queue = AsyncMock()
        
        # Create test events to simulate a debate flow
        from types import SimpleNamespace
        
        test_events = [
            SimpleNamespace(event_type='debate_start', config=SimpleNamespace(rounds=2, roles=['Expert', 'Critic'])),
            SimpleNamespace(event_type='new_turn', turn=SimpleNamespace(role_id='Expert', opinion='Expert opinion', round=1)),
            SimpleNamespace(event_type='new_turn', turn=SimpleNamespace(role_id='Critic', opinion='Critic opinion', round=1)),
            SimpleNamespace(event_type='debate_end', result=SimpleNamespace(consensus_outcome='Agreement reached', synthesis='Final synthesis'))
        ]
        
        # Mock the event queue to return events in sequence, then timeout
        call_count = 0
        async def mock_get():
            nonlocal call_count
            if call_count < len(test_events):
                event = test_events[call_count]
                call_count += 1
                return event
            else:
                # After all events, raise TimeoutError to exit the loop
                raise asyncio.TimeoutError()
        
        mock_event_queue.get = mock_get
        handler.event_queue = mock_event_queue
        
        # Test event processing with a short timeout
        try:
            await asyncio.wait_for(handler._process_events(verbose=False), timeout=0.5)
        except asyncio.TimeoutError:
            pass  # Expected - this is how the event loop exits
        
        # Verify the handler processed events correctly
        assert handler.debate_protocol == mock_protocol_instance
        assert len(handler.debate_history) == 2  # Should have captured the two turns
    
    @patch("src.cli.commands.MISSING_DEPENDENCIES", [])
    @pytest.mark.asyncio
    async def test_run_debate_command_with_save(self):
        """Test run_debate_command saves results when requested."""
        # This test is complex due to the internal ResultCapturingDebateHandler class
        # Let's simplify by mocking the key components
        
        # Mock file operations first
        with patch("builtins.open", create=True) as mock_open:
            with patch("json.dump") as mock_json_dump:
                with patch("os.makedirs"):
                    with patch("src.cli.commands.AppState") as mock_app_state:
                        # Mock AppState
                        mock_app_state_instance = MagicMock()
                        mock_app_state_instance.search_roles_by_vector.return_value = []
                        mock_app_state.return_value = mock_app_state_instance
                        
                        # Mock the CLIDebateHandler methods that are called
                        with patch.object(CLIDebateHandler, 'initialize', new_callable=AsyncMock) as mock_init:
                            with patch.object(CLIDebateHandler, 'start_debate', new_callable=AsyncMock) as mock_start:
                                mock_init.return_value = True
                                mock_start.return_value = True
                                
                                result = await run_debate_command(
                                    topic="Test topic",
                                    roles=["Expert"],
                                    rounds=1,
                                    consensus_strategy="simple_majority_vote",
                                    verbose=False,
                                    save_results=True,
                                    output_file="test_output.json"
                                )
                                
                                assert result is True
                                mock_open.assert_called_once()
                                mock_json_dump.assert_called_once()


class TestCLIEndToEndIntegration:
    """End-to-end integration tests for CLI commands."""
    
    @patch("src.cli.commands.run_debate_command")
    @patch("src.cli.main.asyncio.run")
    def test_start_command_end_to_end_success(self, mock_asyncio_run, mock_run_debate, cli_runner):
        """Test complete start command flow from CLI to service execution."""
        mock_run_debate.return_value = True
        mock_asyncio_run.return_value = True
        
        result = cli_runner.invoke(app, [
            "start", "Should renewable energy be prioritized?",
            "--role", "Environmental Scientist",
            "--role", "Energy Economist",
            "--rounds", "3",
            "--consensus", "weighted_vote",
            "--verbose",
            "--save",
            "--output", "debate_results.json"
        ])
        
        assert result.exit_code == 0
        assert "Initializing debate" in result.stdout
        assert "completed successfully" in result.stdout
        assert "Results saved to: debate_results.json" in result.stdout
        
        # Verify all parameters were passed correctly
        call_args = mock_run_debate.call_args
        assert call_args[1]["topic"] == "Should renewable energy be prioritized?"
        assert call_args[1]["roles"] == ["Environmental Scientist", "Energy Economist"]
        assert call_args[1]["rounds"] == 3
        assert call_args[1]["consensus_strategy"] == "weighted_vote"
        assert call_args[1]["verbose"] is True
        assert call_args[1]["save_results"] is True
        assert call_args[1]["output_file"] == "debate_results.json"
    
    @patch("src.cli.commands.list_available_roles")
    def test_roles_command_end_to_end(self, mock_list_roles, cli_runner):
        """Test complete roles command flow."""
        mock_list_roles.return_value = [
            {
                "name": "Climate Scientist",
                "description": "Expert in climate science and environmental research with focus on data analysis",
                "tags": ["science", "environment", "climate", "research"]
            },
            {
                "name": "Policy Analyst",
                "description": "Specialist in policy development and governmental analysis",
                "tags": ["policy", "government", "analysis"]
            },
            {
                "name": "Technology Expert",
                "description": "Expert in emerging technologies and innovation",
                "tags": ["technology", "innovation", "engineering"]
            }
        ]
        
        result = cli_runner.invoke(app, ["roles"])
        
        assert result.exit_code == 0
        assert "Available Roles (3)" in result.stdout
        assert "Climate Scientist" in result.stdout
        assert "Policy Analyst" in result.stdout
        assert "Technology Expert" in result.stdout
        assert "Role Usage:" in result.stdout
        assert "Available Categories:" in result.stdout
        # Check that the tags are displayed (they might be formatted differently)
        assert "science" in result.stdout
        assert "environment" in result.stdout
        assert "climate" in result.stdout
    
    @patch("src.cli.commands.check_system_health")
    def test_status_command_end_to_end_healthy(self, mock_check_health, cli_runner):
        """Test complete status command flow with healthy system."""
        mock_check_health.return_value = {
            "configuration": {"status": "✅ Loaded", "details": "Log Level: INFO"},
            "dependencies": {"status": "✅ Ready", "details": "All required modules installed"},
            "services": {"status": "✅ Ready", "details": "All core services initialized"},
            "api": {"status": "✅ Ready", "details": "8 endpoints available"}
        }
        
        result = cli_runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        assert "System Status: HEALTHY" in result.stdout
        assert "All components are working correctly" in result.stdout
        assert "Log Level: INFO" in result.stdout
        assert "8 endpoints available" in result.stdout
        assert "System is ready! Try: daip-cli start" in result.stdout
    
    @patch("src.cli.commands.check_system_health")
    @patch("src.cli.commands.MISSING_DEPENDENCIES", ["chromadb", "tiktoken"])
    def test_status_command_end_to_end_unhealthy(self, mock_check_health, cli_runner):
        """Test complete status command flow with unhealthy system."""
        mock_check_health.return_value = {
            "configuration": {"status": "✅ Loaded", "details": "Config loaded"},
            "dependencies": {"status": "❌ Missing dependencies", "details": "2 packages missing"},
            "services": {"status": "❌ Not available", "details": "Missing dependencies"},
            "api": {"status": "❌ Not available", "details": "Missing dependencies"}
        }
        
        result = cli_runner.invoke(app, ["status"])
        
        assert result.exit_code == 0
        assert "System Status: NEEDS ATTENTION" in result.stdout
        assert "Missing Dependencies:" in result.stdout
        assert "chromadb" in result.stdout
        assert "tiktoken" in result.stdout
        assert "Fix missing dependencies first" in result.stdout
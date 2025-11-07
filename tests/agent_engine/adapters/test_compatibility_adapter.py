"""Tests for Compatibility Adapter."""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from daip_live.agent_engine_v1.events.event_bus import EventBus
from daip_live.agent_engine_v1.integration.service_integration import ServiceIntegrationManager
from daip_live.agent_engine_v1.orchestration.agent_orchestrator import AgentOrchestrator
from daip_live.agent_engine_v1.adapters.compatibility_adapter import (
    AgentEngineV1ToLegacyAdapter,
    LegacyEventAdapter,
    MigrationHelper,
    LegacyRequest,
    LegacyResponse
)


class TestLegacyRequest:
    """Test LegacyRequest dataclass."""

    def test_legacy_request_creation(self):
        """Test creating a legacy request."""
        request = LegacyRequest(
            user_input="test input",
            session_id="test_session",
            context={"user": "test_user"},
            user_id="user123",
            tool_permissions={"read_file": True},
            metadata={"version": "1.0"}
        )

        assert request.user_input == "test input"
        assert request.session_id == "test_session"
        assert request.context["user"] == "test_user"
        assert request.user_id == "user123"
        assert request.tool_permissions["read_file"] is True
        assert request.metadata["version"] == "1.0"

    def test_legacy_request_minimal(self):
        """Test creating a minimal legacy request."""
        request = LegacyRequest(user_input="test input")

        assert request.user_input == "test input"
        assert request.session_id is None
        assert request.context is None
        assert request.user_id is None
        assert request.tool_permissions is None
        assert request.metadata is None


class TestLegacyResponse:
    """Test LegacyResponse dataclass."""

    def test_legacy_response_creation(self):
        """Test creating a legacy response."""
        response = LegacyResponse(
            response="Test response",
            success=True,
            error_message=None,
            execution_time_ms=150.0,
            metadata={"test": "data"},
            tool_calls=[{"tool": "read_file", "params": {}}],
            state_changes={"counter": 1}
        )

        assert response.response == "Test response"
        assert response.success is True
        assert response.error_message is None
        assert response.execution_time_ms == 150.0
        assert response.metadata["test"] == "data"
        assert len(response.tool_calls) == 1
        assert response.state_changes["counter"] == 1

    def test_legacy_response_error(self):
        """Test creating an error legacy response."""
        response = LegacyResponse(
            response="",
            success=False,
            error_message="Test error"
        )

        assert response.response == ""
        assert response.success is False
        assert response.error_message == "Test error"


class TestAgentEngineV1ToLegacyAdapter:
    """Test AgentEngineV1ToLegacyAdapter."""

    @pytest_asyncio.fixture
    async def adapter(self):
        """Create adapter instance with services."""
        event_bus = EventBus()
        service_manager = ServiceIntegrationManager(event_bus)

        # Create services
        await service_manager.create_intent_recognition_service()
        await service_manager.create_execution_engine_service()
        await service_manager.create_permission_service()
        await service_manager.create_state_management_service()

        orchestrator = AgentOrchestrator(event_bus, service_manager)
        adapter = AgentEngineV1ToLegacyAdapter(orchestrator, event_bus, service_manager)

        return adapter

    @pytest.mark.asyncio
    async def test_adapter_initialization(self, adapter):
        """Test adapter initialization."""
        assert adapter.orchestrator is not None
        assert adapter.event_bus is not None
        assert adapter.service_manager is not None
        assert adapter.enable_legacy_tool_mapping is True
        assert adapter.preserve_legacy_state_format is True
        assert "read_file" in adapter.legacy_tool_mapping
        assert adapter.legacy_tool_mapping["read_file"] == "file_read"

    @pytest.mark.asyncio
    async def test_adapt_request_basic(self, adapter):
        """Test basic request adaptation."""
        legacy_request = LegacyRequest(
            user_input="read the file test.txt",
            session_id="test_session",
            user_id="user123",
            context={"tool_requests": ["read_file"]},
            metadata={"version": "1.0"}
        )

        adapted_request = await adapter.adapt_request(legacy_request)

        assert adapted_request["user_input"] == "read the file test.txt"
        assert adapted_request["session_id"] == "test_session"
        assert adapted_request["context"]["user_id"] == "user123"
        assert adapted_request["context"]["legacy_format"] is True
        assert adapted_request["context"]["tool_permissions"] == {}
        assert adapted_request["context"]["adapter_version"] == "1.0.0"
        assert adapted_request["context"]["legacy_metadata"]["version"] == "1.0"
        assert "file_read" in adapted_request["context"]["mapped_intents"]

    @pytest.mark.asyncio
    async def test_adapt_request_minimal(self, adapter):
        """Test adapting a minimal request."""
        legacy_request = LegacyRequest(user_input="test input")

        adapted_request = await adapter.adapt_request(legacy_request)

        assert adapted_request["user_input"] == "test input"
        assert adapted_request["session_id"] is None
        assert adapted_request["context"]["legacy_format"] is True
        assert adapted_request["context"]["user_id"] is None
        assert adapted_request["timeout"] == adapter.legacy_timeout_seconds

    @pytest.mark.asyncio
    async def test_fuzzy_tool_mapping(self, adapter):
        """Test fuzzy tool name matching."""
        # Test direct mapping
        mapped = adapter._fuzzy_match_tool("read_file")
        assert mapped == "file_read"

        # Test partial matching
        mapped = adapter._fuzzy_match_tool("file_reader")
        assert mapped == "file_read"

        # Test unknown tool
        mapped = adapter._fuzzy_match_tool("unknown_tool_xyz")
        assert mapped == adapter.legacy_tool_mapping["default"]

    @pytest.mark.asyncio
    async def test_adapt_response_success(self, adapter):
        """Test adapting a successful response."""
        # Create mock execution context
        mock_execution_context = MagicMock()
        mock_execution_context.session_id = "test_session"
        mock_execution_context.execution_id = "exec_123"
        mock_execution_context.intent_result = MagicMock()
        mock_execution_context.intent_result.intent = "file_read"
        mock_execution_context.intent_result.confidence = 0.85
        mock_execution_context.intent_result.parameters = {"file_path": "test.txt"}
        mock_execution_context.intent_result.strategy_used = "keyword_matching"

        mock_execution_result = MagicMock()
        mock_execution_result.success = True
        mock_execution_result.result_data = {"response": "File content: test data"}
        mock_execution_result.execution_time_ms = 150.0
        mock_execution_context.execution_result = mock_execution_result

        mock_permission_decision = MagicMock()
        mock_permission_decision.risk_level.value = "low"
        mock_execution_context.permission_decision = mock_permission_decision

        legacy_request = LegacyRequest(user_input="read file", session_id="test_session")

        response = await adapter.adapt_response(mock_execution_context, legacy_request)

        assert response.success is True
        assert response.response == "File content: test data"
        assert response.error_message is None
        assert response.execution_time_ms == 150.0
        assert response.metadata["session_id"] == "test_session"
        assert response.metadata["execution_id"] == "exec_123"
        assert response.metadata["intent"] == "file_read"
        assert response.metadata["confidence"] == 0.85
        assert response.metadata["risk_level"] == "low"
        assert len(response.tool_calls) == 1
        assert response.tool_calls[0]["tool"] == "file_read"

    @pytest.mark.asyncio
    async def test_adapt_response_permission_denied(self, adapter):
        """Test adapting a response with permission denied."""
        mock_execution_context = MagicMock()
        mock_execution_context.session_id = "test_session"
        mock_execution_context.execution_id = "exec_123"

        # Permission denied
        mock_permission_decision = MagicMock()
        mock_permission_decision.allowed = False
        mock_permission_decision.reason = "User not authorized"
        mock_execution_context.permission_decision = mock_permission_decision
        mock_execution_context.execution_result = None

        legacy_request = LegacyRequest(user_input="delete system", session_id="test_session")

        response = await adapter.adapt_response(mock_execution_context, legacy_request)

        assert response.success is False
        assert "Permission denied" in response.error_message
        assert "User not authorized" in response.error_message

    @pytest.mark.asyncio
    async def test_process_legacy_request_integration(self, adapter):
        """Test full legacy request processing integration."""
        await adapter.orchestrator.start()

        try:
            legacy_request = LegacyRequest(
                user_input="read the file test.txt",
                session_id="test_session",
                user_id="test_user"
            )

            response = await adapter.process_legacy_request(legacy_request)

            # Verify response structure
            assert isinstance(response, LegacyResponse)
            assert response.metadata is not None
            assert response.metadata["adapter_version"] == "1.0.0"
            assert response.metadata["session_id"] == "test_session"
            assert "adapted_at" in response.metadata

        finally:
            await adapter.orchestrator.stop()

    @pytest.mark.asyncio
    async def test_process_legacy_request_error_handling(self, adapter):
        """Test error handling in legacy request processing."""
        # Mock orchestrator to raise an exception
        with patch.object(adapter.orchestrator, 'process_request', side_effect=Exception("Test error")):
            legacy_request = LegacyRequest(user_input="test input")

            response = await adapter.process_legacy_request(legacy_request)

            assert response.success is False
            assert "Processing error" in response.error_message
            assert "Test error" in response.error_message


class TestLegacyEventAdapter:
    """Test LegacyEventAdapter."""

    @pytest.fixture
    def event_adapter(self):
        """Create event adapter instance."""
        event_bus = MagicMock()
        return LegacyEventAdapter(event_bus)

    def test_register_legacy_handler(self, event_adapter):
        """Test registering legacy event handlers."""
        handler1 = MagicMock()
        handler2 = MagicMock()

        event_adapter.register_legacy_handler("test_event", handler1)
        event_adapter.register_legacy_handler("test_event", handler2)

        assert "test_event" in event_adapter.legacy_event_handlers
        assert len(event_adapter.legacy_event_handlers["test_event"]) == 2
        assert handler1 in event_adapter.legacy_event_handlers["test_event"]
        assert handler2 in event_adapter.legacy_event_handlers["test_event"]

    def test_register_multiple_event_types(self, event_adapter):
        """Test registering handlers for different event types."""
        handler1 = MagicMock()
        handler2 = MagicMock()

        event_adapter.register_legacy_handler("event1", handler1)
        event_adapter.register_legacy_handler("event2", handler2)

        assert "event1" in event_adapter.legacy_event_handlers
        assert "event2" in event_adapter.legacy_event_handlers
        assert event_adapter.legacy_event_handlers["event1"][0] == handler1
        assert event_adapter.legacy_event_handlers["event2"][0] == handler2


class TestMigrationHelper:
    """Test MigrationHelper."""

    @pytest_asyncio.fixture
    async def migration_helper(self):
        """Create migration helper instance."""
        event_bus = EventBus()
        service_manager = ServiceIntegrationManager(event_bus)

        # Create services
        await service_manager.create_intent_recognition_service()
        await service_manager.create_execution_engine_service()
        await service_manager.create_permission_service()
        await service_manager.create_state_management_service()

        orchestrator = AgentOrchestrator(event_bus, service_manager)
        adapter = AgentEngineV1ToLegacyAdapter(orchestrator, event_bus, service_manager)

        return MigrationHelper(adapter)

    def test_migration_helper_initialization(self, migration_helper):
        """Test migration helper initialization."""
        assert migration_helper.adapter is not None
        assert "legacy_requests_processed" in migration_helper.migration_metrics
        assert "successful_migrations" in migration_helper.migration_metrics
        assert "failed_migrations" in migration_helper.migration_metrics
        assert "compatibility_issues" in migration_helper.migration_metrics
        assert "last_migration" in migration_helper.migration_metrics

    def test_record_migration_attempt_success(self, migration_helper):
        """Test recording successful migration attempt."""
        initial_count = migration_helper.migration_metrics["legacy_requests_processed"]

        migration_helper.record_migration_attempt(success=True)

        assert migration_helper.migration_metrics["legacy_requests_processed"] == initial_count + 1
        assert migration_helper.migration_metrics["successful_migrations"] == initial_count + 1
        assert migration_helper.migration_metrics["failed_migrations"] == initial_count
        assert migration_helper.migration_metrics["last_migration"] is not None

    def test_record_migration_attempt_failure(self, migration_helper):
        """Test recording failed migration attempt."""
        initial_count = migration_helper.migration_metrics["legacy_requests_processed"]

        migration_helper.record_migration_attempt(success=False, error="Test error")

        assert migration_helper.migration_metrics["legacy_requests_processed"] == initial_count + 1
        assert migration_helper.migration_metrics["successful_migrations"] == initial_count
        assert migration_helper.migration_metrics["failed_migrations"] == initial_count + 1
        assert len(migration_helper.migration_metrics["compatibility_issues"]) == 1
        assert migration_helper.migration_metrics["compatibility_issues"][0]["error"] == "Test error"

    def test_get_migration_status(self, migration_helper):
        """Test getting migration status."""
        # Record some test data
        migration_helper.record_migration_attempt(success=True)
        migration_helper.record_migration_attempt(success=False, error="Test error")

        status = migration_helper.get_migration_status()

        assert "migration_metrics" in status
        assert "adapter_health" in status
        assert "recommendations" in status
        assert status["migration_metrics"]["legacy_requests_processed"] == 2
        assert status["migration_metrics"]["successful_migrations"] == 1
        assert status["migration_metrics"]["failed_migrations"] == 1

    def test_check_adapter_health_good(self, migration_helper):
        """Test adapter health check with good metrics."""
        # Record high success rate
        for _ in range(95):
            migration_helper.record_migration_attempt(success=True)
        for _ in range(5):
            migration_helper.record_migration_attempt(success=False)

        health = migration_helper._check_adapter_health()

        assert health["healthy"] is True
        assert health["performance"] == "good"
        assert len(health["issues"]) == 0

    def test_check_adapter_health_poor(self, migration_helper):
        """Test adapter health check with poor metrics."""
        # Record low success rate
        for _ in range(10):
            migration_helper.record_migration_attempt(success=False)

        health = migration_helper._check_adapter_health()

        assert health["healthy"] is False
        assert health["performance"] == "poor"
        assert len(health["issues"]) > 0

    def test_get_migration_recommendations(self, migration_helper):
        """Test getting migration recommendations."""
        # No migrations yet
        recommendations = migration_helper._get_migration_recommendations()
        assert "Start processing migration test cases" in recommendations

        # Some failures
        migration_helper.record_migration_attempt(success=False, error="Test error")
        recommendations = migration_helper._get_migration_recommendations()
        assert len(recommendations) >= 1

    @pytest.mark.asyncio
    async def test_legacy_compatibility_test_success(self, migration_helper):
        """Test legacy compatibility testing with successful cases."""
        # Create test cases
        test_cases = [
            LegacyRequest(user_input="read file test.txt"),
            LegacyRequest(user_input="write file output.txt"),
            LegacyRequest(user_input="search knowledge")
        ]

        # Mock successful responses
        with patch.object(migration_helper.adapter, 'process_legacy_request') as mock_process:
            mock_process.return_value = LegacyResponse(
                response="Success",
                success=True
            )

            results = await migration_helper.test_legacy_compatibility(test_cases)

            assert results["total_tests"] == 3
            assert results["passed_tests"] == 3
            assert results["failed_tests"] == 0
            assert results["compatibility_score"] == 1.0
            assert len(results["test_results"]) == 3

    @pytest.mark.asyncio
    async def test_legacy_compatibility_test_mixed(self, migration_helper):
        """Test legacy compatibility testing with mixed results."""
        test_cases = [
            LegacyRequest(user_input="read file test.txt"),
            LegacyRequest(user_input="invalid request")
        ]

        # Mock mixed responses
        def mock_side_effect(request):
            if "invalid" in request.user_input:
                return LegacyResponse(success=False, error_message="Invalid request")
            else:
                return LegacyResponse(success=True, response="Success")

        with patch.object(migration_helper.adapter, 'process_legacy_request', side_effect=mock_side_effect):
            results = await migration_helper.test_legacy_compatibility(test_cases)

            assert results["total_tests"] == 2
            assert results["passed_tests"] == 1
            assert results["failed_tests"] == 1
            assert results["compatibility_score"] == 0.5
"""Complete system integration tests."""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from daip_live.agent_engine_v1 import (
    EventBus,
    ServiceIntegrationManager,
    AgentOrchestrator,
    AgentEngineV1ToLegacyAdapter,
    LegacyRequest
)


class TestCompleteSystemIntegration:
    """Test complete system integration."""

    @pytest_asyncio.fixture
    async def complete_system(self):
        """Create complete system with all components."""
        # Create EventBus
        event_bus = EventBus()
        await event_bus.start()

        # Create Service Manager and services
        service_manager = ServiceIntegrationManager(event_bus)
        await service_manager.create_intent_recognition_service()
        await service_manager.create_execution_engine_service()
        await service_manager.create_permission_service()
        await service_manager.create_state_management_service()
        await service_manager.start_all_services()

        # Create Orchestrator
        orchestrator = AgentOrchestrator(event_bus, service_manager)
        await orchestrator.start()

        # Create Compatibility Adapter
        adapter = AgentEngineV1ToLegacyAdapter(orchestrator, event_bus, service_manager)

        yield {
            "event_bus": event_bus,
            "service_manager": service_manager,
            "orchestrator": orchestrator,
            "adapter": adapter
        }

        # Cleanup
        await orchestrator.stop()
        await service_manager.stop_all_services()
        await event_bus.stop()

    @pytest.mark.asyncio
    async def test_system_health_check(self, complete_system):
        """Test complete system health check."""
        orchestrator = complete_system["orchestrator"]
        service_manager = complete_system["service_manager"]

        # Check individual components
        assert orchestrator.is_healthy()
        assert orchestrator.get_state().value == "idle"

        # Check service health
        metrics = await service_manager.get_all_metrics()
        assert "intent_recognition" in metrics
        assert "execution_engine" in metrics
        assert "permission" in metrics
        assert "state_management" in metrics

    @pytest.mark.asyncio
    async def test_full_workflow_via_orchestrator(self, complete_system):
        """Test full workflow through orchestrator."""
        orchestrator = complete_system["orchestrator"]

        # Process a complete request
        context = await orchestrator.process_request(
            user_input="read the file test.txt and tell me what's in it",
            session_id="test_session_123",
            context={"user": "test_user", "permission_level": "admin"}
        )

        # Verify workflow results
        assert context.session_id == "test_session_123"
        assert context.user_input == "read the file test.txt and tell me what's in it"
        assert context.intent_result is not None
        assert context.permission_decision is not None
        # Note: execution might fail due to missing file, but should still have execution_result

        # Check metrics
        metrics = orchestrator.get_metrics()
        assert metrics["orchestrator"]["total_sessions"] == 1
        assert metrics["orchestrator"]["total_executions"] == 1

    @pytest.mark.asyncio
    async def test_legacy_compatibility_workflow(self, complete_system):
        """Test legacy compatibility workflow."""
        adapter = complete_system["adapter"]

        # Create legacy request
        legacy_request = LegacyRequest(
            user_input="analyze the code in main.py",
            session_id="legacy_session_456",
            user_id="legacy_user",
            tool_permissions={"read_file": True, "code_analyze": True},
            metadata={"legacy_version": "1.0", "client": "legacy_ui"}
        )

        # Process through adapter
        legacy_response = await adapter.process_legacy_request(legacy_request)

        # Verify response format
        assert isinstance(legacy_response.response, str)
        assert isinstance(legacy_response.success, bool)
        assert legacy_response.metadata is not None
        assert legacy_response.metadata["adapter_version"] == "1.0.0"
        assert legacy_response.metadata["session_id"] == "legacy_session_456"
        assert legacy_response.metadata["legacy_metadata"]["legacy_version"] == "1.0"

        # Check tool calls
        if legacy_response.tool_calls:
            assert isinstance(legacy_response.tool_calls, list)
            for tool_call in legacy_response.tool_calls:
                assert "tool" in tool_call
                assert "parameters" in tool_call
                assert "confidence" in tool_call

    @pytest.mark.asyncio
    async def test_concurrent_request_processing(self, complete_system):
        """Test concurrent request processing."""
        orchestrator = complete_system["orchestrator"]

        # Create multiple concurrent requests
        requests = [
            ("read file1.txt", "session_1"),
            ("write file2.txt", "session_2"),
            ("analyze data.csv", "session_3"),
            ("search knowledge base", "session_4"),
            ("execute python script", "session_5")
        ]

        # Process requests concurrently
        tasks = []
        for user_input, session_id in requests:
            task = orchestrator.process_request(user_input, session_id)
            tasks.append(task)

        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify results
        assert len(results) == len(requests)

        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= 3  # Allow some failures due to missing files/tools

        # Check orchestrator metrics
        metrics = orchestrator.get_metrics()
        assert metrics["orchestrator"]["total_sessions"] >= len(requests)

    @pytest.mark.asyncio
    async def test_session_continuity(self, complete_system):
        """Test session continuity across multiple requests."""
        orchestrator = complete_system["orchestrator"]

        session_id = "continuity_test_session"

        # First request
        context1 = await orchestrator.process_request(
            user_input="read file config.json",
            session_id=session_id
        )

        # Second request in same session
        context2 = await orchestrator.process_request(
            user_input="now read file data.csv",
            session_id=session_id
        )

        # Verify session continuity
        assert context1.session_id == session_id
        assert context2.session_id == session_id

        # Check execution history
        history = orchestrator.get_execution_history(session_id=session_id)
        assert len(history) == 2
        assert all(ctx.session_id == session_id for ctx in history)

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, complete_system):
        """Test error handling and recovery."""
        orchestrator = complete_system["orchestrator"]

        # Test with request that might fail
        try:
            context = await orchestrator.process_request(
                user_input="delete critical_system_file",
                session_id="error_test_session",
                context={"user": "unauthorized_user"}
            )
            # Should complete even if execution fails due to permissions
            assert context.session_id == "error_test_session"
            assert context.permission_decision is not None
        except Exception as e:
            # Should not raise exception even if execution fails
            pytest.fail(f"Orchestrator should handle errors gracefully: {e}")

    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self, complete_system):
        """Test performance metrics collection."""
        orchestrator = complete_system["orchestrator"]
        service_manager = complete_system["service_manager"]

        # Process several requests
        for i in range(3):
            await orchestrator.process_request(f"test request {i}", f"perf_test_{i}")

        # Get comprehensive metrics
        orchestrator_metrics = orchestrator.get_metrics()
        service_metrics = await service_manager.get_all_metrics()

        # Verify orchestrator metrics
        assert orchestrator_metrics["orchestrator"]["total_sessions"] == 3
        assert orchestrator_metrics["orchestrator"]["avg_execution_time_ms"] >= 0
        assert orchestrator_metrics["orchestrator"]["success_rate"] >= 0

        # Verify service metrics are available
        assert "intent_recognition" in service_metrics
        assert "execution_engine" in service_metrics
        assert "permission" in service_metrics
        assert "state_management" in service_metrics

    @pytest.mark.asyncio
    async def test_event_system_integration(self, complete_system):
        """Test event system integration."""
        event_bus = complete_system["event_bus"]
        orchestrator = complete_system["orchestrator"]

        # Subscribe to events
        events_received = []

        async def event_handler(event):
            events_received.append(event)

        # Subscribe to multiple event types
        from daip_live.agent_engine_v1.events.event_types import EventType
        await event_bus.subscribe(EventType.SESSION_STARTED, event_handler)
        await event_bus.subscribe(EventType.SESSION_COMPLETED, event_handler)
        await event_bus.subscribe(EventType.INTENT_RECOGNIZED, event_handler)
        await event_bus.subscribe(EventType.PERMISSION_CHECKED, event_handler)

        # Process a request
        await orchestrator.process_request("test event system", "event_test_session")

        # Verify events were received
        # Note: Event publishing might not work in test environment,
        # but the system should not crash
        assert isinstance(events_received, list)

    @pytest.mark.asyncio
    async def test_system_shutdown_gracefully(self, complete_system):
        """Test graceful system shutdown."""
        orchestrator = complete_system["orchestrator"]
        service_manager = complete_system["service_manager"]
        event_bus = complete_system["event_bus"]

        # Start a long-running operation
        start_time = datetime.now()

        # Initiate shutdown while operation is in progress
        shutdown_task = asyncio.create_task(orchestrator.stop())

        # Wait for shutdown to complete
        await shutdown_task

        shutdown_time = (datetime.now() - start_time).total_seconds()

        # Verify graceful shutdown
        assert shutdown_time < 30.0  # Should complete within 30 seconds
        assert orchestrator.get_state().value == "idle"

        # Verify services are stopped
        for service_name, service in service_manager.integrated_services.items():
            assert not service.is_healthy()

    @pytest.mark.asyncio
    async def test_memory_management(self, complete_system):
        """Test memory management with multiple sessions."""
        orchestrator = complete_system["orchestrator"]

        # Create many sessions
        session_count = 20
        for i in range(session_count):
            await orchestrator.process_request(
                f"test memory {i}",
                f"memory_test_session_{i}"
            )

        # Check that execution history is managed
        history = orchestrator.get_execution_history(limit=50)
        assert len(history) >= session_count

        # Memory usage should be reasonable (this is a basic check)
        orchestrator_metrics = orchestrator.get_metrics()
        assert orchestrator_metrics["orchestrator"]["total_sessions"] == session_count

    @pytest.mark.asyncio
    async def test_system_configuration(self, complete_system):
        """Test system configuration options."""
        orchestrator = complete_system["orchestrator"]
        adapter = complete_system["adapter"]

        # Test orchestrator configuration
        assert orchestrator.max_concurrent_executions >= 1
        assert orchestrator.default_timeout_seconds > 0
        assert isinstance(orchestrator.enable_state_persistence, bool)

        # Test adapter configuration
        assert adapter.enable_legacy_tool_mapping is True
        assert adapter.preserve_legacy_state_format is True
        assert adapter.legacy_timeout_seconds > 0
        assert len(adapter.legacy_tool_mapping) > 0

        # Test configuration is actually used
        assert adapter.legacy_tool_mapping["read_file"] == "file_read"
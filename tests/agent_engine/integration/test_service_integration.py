"""Tests for service integration with EventBus."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from daip_live.agent_engine_v1.events.event_bus import EventBus
from daip_live.agent_engine_v1.events.event_types import (
    IntentRecognizedEvent,
    ExecutionStartedEvent,
    ExecutionCompletedEvent,
    PermissionCheckedEvent,
    StateChangedEvent,
    ServiceHealthChangedEvent,
    ErrorEvent,
    MetricsEvent
)
from daip_live.agent_engine_v1.integration.service_integration import (
    ServiceEventPublisher,
    ServiceEventSubscriber,
    ServiceIntegrationManager,
    IntentRecognitionServiceIntegrated,
    ExecutionEngineServiceIntegrated,
    PermissionServiceIntegrated,
    StateManagementServiceIntegrated
)


class TestServiceEventPublisher:
    """Test ServiceEventPublisher."""

    @pytest.fixture
    def event_bus(self):
        """Create a mock event bus."""
        return AsyncMock()

    @pytest.fixture
    def publisher(self, event_bus):
        """Create a publisher instance."""
        return ServiceEventPublisher(event_bus, "TestService")

    @pytest.mark.asyncio
    async def test_publish_intent_recognized(self, publisher, event_bus):
        """Test publishing intent recognized event."""
        from daip_live.agent_engine_v1.services.interfaces import IntentRecognitionResult
        from daip_live.agent_engine_v1.services.permission_service import RiskLevel

        result = IntentRecognitionResult(
            intent="file_read",
            confidence=0.85,
            parameters={"file_path": "/test/file.txt"},
            reasoning="Pattern matched",
            strategy_used="keyword_matching"
        )

        await publisher.publish_intent_recognized(
            result=result,
            input_text="read the test file",
            context={"user": "test_user"}
        )

        # Verify event was published
        event_bus.publish.assert_called_once()
        event = event_bus.publish.call_args[0][0]
        assert isinstance(event, IntentRecognizedEvent)
        assert event.service_name == "TestService"
        assert event.intent == "file_read"
        assert event.confidence == 0.85

    @pytest.mark.asyncio
    async def test_publish_execution_started(self, publisher, event_bus):
        """Test publishing execution started event."""
        await publisher.publish_execution_started(
            execution_id="exec_123",
            intent="file_read",
            parameters={"file_path": "/test/file.txt"},
            context={"user": "test_user"}
        )

        event_bus.publish.assert_called_once()
        event = event_bus.publish.call_args[0][0]
        assert isinstance(event, ExecutionStartedEvent)
        assert event.service_name == "TestService"
        assert event.execution_id == "exec_123"
        assert event.intent == "file_read"

    @pytest.mark.asyncio
    async def test_publish_execution_completed(self, publisher, event_bus):
        """Test publishing execution completed event."""
        from daip_live.agent_engine_v1.services.interfaces import ExecutionResult

        result = ExecutionResult(
            intent="file_read",
            success=True,
            result_data={"content": "file content"},
            execution_time_ms=150.0
        )

        await publisher.publish_execution_completed(
            execution_id="exec_123",
            result=result,
            context={"user": "test_user"}
        )

        event_bus.publish.assert_called_once()
        event = event_bus.publish.call_args[0][0]
        assert isinstance(event, ExecutionCompletedEvent)
        assert event.service_name == "TestService"
        assert event.execution_id == "exec_123"
        assert event.success is True

    @pytest.mark.asyncio
    async def test_publish_permission_checked(self, publisher, event_bus):
        """Test publishing permission checked event."""
        from daip_live.agent_engine_v1.services.permission_service import PermissionDecision, RiskLevel

        decision = PermissionDecision(
            allowed=True,
            confidence=0.9,
            reason="User has admin privileges",
            risk_level=RiskLevel.LOW,
            rules_applied=["admin_rule"]
        )

        await publisher.publish_permission_checked(
            decision=decision,
            action="file_read",
            context={"user": "admin"}
        )

        event_bus.publish.assert_called_once()
        event = event_bus.publish.call_args[0][0]
        assert isinstance(event, PermissionCheckedEvent)
        assert event.service_name == "TestService"
        assert event.action == "file_read"
        assert event.allowed is True

    @pytest.mark.asyncio
    async def test_publish_state_changed(self, publisher, event_bus):
        """Test publishing state changed event."""
        old_state = {"counter": 1}
        new_state = {"counter": 2, "status": "updated"}

        await publisher.publish_state_changed(
            session_id="session_123",
            agent_id="agent_456",
            old_state=old_state,
            new_state=new_state,
            change_type="update"
        )

        event_bus.publish.assert_called_once()
        event = event_bus.publish.call_args[0][0]
        assert isinstance(event, StateChangedEvent)
        assert event.service_name == "TestService"
        assert event.session_id == "session_123"
        assert event.agent_id == "agent_456"
        assert event.change_type == "update"

    @pytest.mark.asyncio
    async def test_publish_service_health_changed(self, publisher, event_bus):
        """Test publishing service health changed event."""
        await publisher.publish_service_health_changed(
            healthy=True,
            details={"startup_time": 123.45}
        )

        event_bus.publish.assert_called_once()
        event = event_bus.publish.call_args[0][0]
        assert isinstance(event, ServiceHealthChangedEvent)
        assert event.service_name == "TestService"
        assert event.healthy is True

    @pytest.mark.asyncio
    async def test_publish_error(self, publisher, event_bus):
        """Test publishing error event."""
        error = ValueError("Test error message")

        await publisher.publish_error(
            error=error,
            context={"operation": "test_operation"}
        )

        event_bus.publish.assert_called_once()
        event = event_bus.publish.call_args[0][0]
        assert isinstance(event, ErrorEvent)
        assert event.service_name == "TestService"
        assert event.error_type == "ValueError"
        assert event.error_message == "Test error message"

    @pytest.mark.asyncio
    async def test_publish_metrics(self, publisher, event_bus):
        """Test publishing metrics event."""
        metrics = {
            "requests_processed": 10,
            "success_rate": 0.95,
            "avg_response_time": 150.0
        }

        await publisher.publish_metrics(
            metrics=metrics,
            context={"time_window": "1h"}
        )

        event_bus.publish.assert_called_once()
        event = event_bus.publish.call_args[0][0]
        assert isinstance(event, MetricsEvent)
        assert event.service_name == "TestService"
        assert event.metrics["requests_processed"] == 10


class TestServiceEventSubscriber:
    """Test ServiceEventSubscriber."""

    @pytest.fixture
    def event_bus(self):
        """Create a mock event bus."""
        return AsyncMock()

    @pytest.fixture
    def subscriber(self, event_bus):
        """Create a subscriber instance."""
        return ServiceEventSubscriber(event_bus, "TestService")

    @pytest.mark.asyncio
    async def test_subscribe_to_intent_recognized(self, subscriber, event_bus):
        """Test subscribing to intent recognized events."""
        handler = AsyncMock()
        event_bus.subscribe.return_value = "subscription_id"

        await subscriber.subscribe_to_intent_recognized(handler)

        event_bus.subscribe.assert_called_once()
        event_type, wrapper = event_bus.subscribe.call_args[0]
        assert event_type == IntentRecognizedEvent

        # Test wrapper functionality
        test_event = IntentRecognizedEvent(
            service_name="OtherService",
            intent="test_intent",
            confidence=0.8
        )

        await wrapper(test_event)
        handler.assert_called_once_with(test_event)

    @pytest.mark.asyncio
    async def test_subscribe_with_handler_error(self, subscriber, event_bus):
        """Test subscriber handling handler errors gracefully."""
        handler = AsyncMock(side_effect=Exception("Handler error"))
        event_bus.subscribe.return_value = "subscription_id"

        await subscriber.subscribe_to_intent_recognized(handler)

        # Get the wrapper function
        event_type, wrapper = event_bus.subscribe.call_args[0]

        # Call wrapper with test event
        test_event = IntentRecognizedEvent(
            service_name="OtherService",
            intent="test_intent",
            confidence=0.8
        )

        # Should not raise exception, but should log error
        await wrapper(test_event)
        handler.assert_called_once_with(test_event)

    @pytest.mark.asyncio
    async def test_unsubscribe_all(self, subscriber, event_bus):
        """Test unsubscribing from all events."""
        subscription_ids = ["sub1", "sub2", "sub3"]
        event_bus.subscribe.return_value = "sub1"

        # Subscribe to multiple events
        await subscriber.subscribe_to_intent_recognized(AsyncMock())
        await subscriber.subscribe_to_execution_started(AsyncMock())
        await subscriber.subscribe_to_execution_completed(AsyncMock())

        # Manually add subscription IDs for testing
        subscriber._subscriptions = subscription_ids

        await subscriber.unsubscribe_all()

        # Verify unsubscribe was called for each subscription
        assert event_bus.unsubscribe.call_count == 3
        for sub_id in subscription_ids:
            event_bus.unsubscribe.assert_any_call(sub_id)

        # Verify subscriptions list is cleared
        assert len(subscriber._subscriptions) == 0


class TestServiceIntegrationManager:
    """Test ServiceIntegrationManager."""

    @pytest.fixture
    def event_bus(self):
        """Create a mock event bus."""
        return AsyncMock()

    @pytest.fixture
    def manager(self, event_bus):
        """Create an integration manager instance."""
        return ServiceIntegrationManager(event_bus)

    @pytest.mark.asyncio
    async def test_create_intent_recognition_service(self, manager, event_bus):
        """Test creating integrated intent recognition service."""
        service = await manager.create_intent_recognition_service()

        assert service is not None
        assert isinstance(service, IntentRecognitionServiceIntegrated)
        assert service.event_bus == event_bus
        assert "intent_recognition" in manager.integrated_services

    @pytest.mark.asyncio
    async def test_create_execution_engine_service(self, manager, event_bus):
        """Test creating integrated execution engine service."""
        service = await manager.create_execution_engine_service()

        assert service is not None
        assert isinstance(service, ExecutionEngineServiceIntegrated)
        assert service.event_bus == event_bus
        assert "execution_engine" in manager.integrated_services

    @pytest.mark.asyncio
    async def test_create_permission_service(self, manager, event_bus):
        """Test creating integrated permission service."""
        service = await manager.create_permission_service()

        assert service is not None
        assert isinstance(service, PermissionServiceIntegrated)
        assert service.event_bus == event_bus
        assert "permission" in manager.integrated_services

    @pytest.mark.asyncio
    async def test_create_state_management_service(self, manager, event_bus):
        """Test creating integrated state management service."""
        service = await manager.create_state_management_service()

        assert service is not None
        assert isinstance(service, StateManagementServiceIntegrated)
        assert service.event_bus == event_bus
        assert "state_management" in manager.integrated_services

    @pytest.mark.asyncio
    async def test_start_all_services(self, manager):
        """Test starting all integrated services."""
        # Create mock services
        service1 = AsyncMock()
        service2 = AsyncMock()
        service3 = AsyncMock()

        manager.integrated_services = {
            "service1": service1,
            "service2": service2,
            "service3": service3
        }

        await manager.start_all_services()

        # Verify all services were started
        service1.start.assert_called_once()
        service2.start.assert_called_once()
        service3.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_all_services_with_error(self, manager):
        """Test handling errors when starting services."""
        # Create services where one fails to start
        service1 = AsyncMock()
        service2 = AsyncMock(side_effect=Exception("Start failed"))
        service3 = AsyncMock()

        manager.integrated_services = {
            "service1": service1,
            "service2": service2,
            "service3": service3
        }

        # Should raise exception
        with pytest.raises(Exception, match="Start failed"):
            await manager.start_all_services()

        # Verify service1 was started before error
        service1.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_all_services(self, manager):
        """Test stopping all integrated services."""
        # Create mock services
        service1 = AsyncMock()
        service2 = AsyncMock()
        service3 = AsyncMock()

        manager.integrated_services = {
            "service1": service1,
            "service2": service2,
            "service3": service3
        }

        await manager.stop_all_services()

        # Verify all services were stopped
        service1.stop.assert_called_once()
        service2.stop.assert_called_once()
        service3.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_all_services_with_error(self, manager):
        """Test handling errors when stopping services."""
        # Create services where one fails to stop
        service1 = AsyncMock()
        service2 = AsyncMock(side_effect=Exception("Stop failed"))
        service3 = AsyncMock()

        manager.integrated_services = {
            "service1": service1,
            "service2": service2,
            "service3": service3
        }

        # Should not raise exception (errors are logged)
        await manager.stop_all_services()

        # Verify all services were attempted to stop
        service1.stop.assert_called_once()
        service2.stop.assert_called_once()
        service3.stop.assert_called_once()

    def test_get_service(self, manager):
        """Test getting a service by name."""
        service1 = AsyncMock()
        service2 = AsyncMock()

        manager.integrated_services = {
            "service1": service1,
            "service2": service2
        }

        # Test existing service
        result = manager.get_service("service1")
        assert result == service1

        # Test non-existent service
        result = manager.get_service("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_metrics(self, manager):
        """Test getting metrics from all services."""
        # Create mock services with metrics
        service1 = AsyncMock()
        service1.get_metrics.return_value = {"requests": 10, "success_rate": 0.95}

        service2 = AsyncMock()
        service2.get_metrics.return_value = {"operations": 5, "avg_time": 150.0}

        service3 = AsyncMock()
        service3.get_metrics.side_effect = Exception("Metrics error")

        manager.integrated_services = {
            "service1": service1,
            "service2": service2,
            "service3": service3
        }

        metrics = await manager.get_all_metrics()

        assert "service1" in metrics
        assert "service2" in metrics
        assert "service3" in metrics

        assert metrics["service1"]["requests"] == 10
        assert metrics["service2"]["operations"] == 5
        assert "error" in metrics["service3"]


class TestIntentRecognitionServiceIntegrated:
    """Test IntentRecognitionServiceIntegrated."""

    @pytest.fixture
    def event_bus(self):
        """Create a real event bus for integration testing."""
        return EventBus()

    @pytest.fixture
    def service(self, event_bus):
        """Create an integrated service instance."""
        return IntentRecognitionServiceIntegrated(event_bus)

    @pytest.mark.asyncio
    async def test_recognize_intent_publishes_event(self, service, event_bus):
        """Test that intent recognition publishes an event."""
        await service.start()

        # Subscribe to intent recognized events
        events = []
        async def handle_event(event):
            events.append(event)

        await event_bus.subscribe(IntentRecognizedEvent, handle_event)

        # Recognize intent
        result = await service.recognize_intent("read the file test.txt")

        # Verify event was published
        assert len(events) == 1
        event = events[0]
        assert isinstance(event, IntentRecognizedEvent)
        assert event.service_name == "IntentRecognitionService"
        assert event.intent == result.intent
        assert event.confidence == result.confidence

        await service.stop()

    @pytest.mark.asyncio
    async def test_start_publishes_health_event(self, service, event_bus):
        """Test that starting service publishes health event."""
        # Subscribe to health events
        events = []
        async def handle_event(event):
            events.append(event)

        await event_bus.subscribe(ServiceHealthChangedEvent, handle_event)

        # Start service
        await service.start()

        # Verify health event was published
        assert len(events) == 1
        event = events[0]
        assert isinstance(event, ServiceHealthChangedEvent)
        assert event.service_name == "IntentRecognitionService"
        assert event.healthy is True

        await service.stop()

    @pytest.mark.asyncio
    async def test_stop_publishes_health_event(self, service, event_bus):
        """Test that stopping service publishes health event."""
        await service.start()

        # Subscribe to health events
        events = []
        async def handle_event(event):
            events.append(event)

        await event_bus.subscribe(ServiceHealthChangedEvent, handle_event)

        # Stop service
        await service.stop()

        # Verify health event was published
        assert len(events) == 1
        event = events[0]
        assert isinstance(event, ServiceHealthChangedEvent)
        assert event.service_name == "IntentRecognitionService"
        assert event.healthy is False

    @pytest.mark.asyncio
    async def test_error_publishes_error_event(self, service, event_bus):
        """Test that errors publish error events."""
        await service.start()

        # Subscribe to error events
        events = []
        async def handle_event(event):
            events.append(event)

        await event_bus.subscribe(ErrorEvent, handle_event)

        # Mock the service to raise an error
        with patch.object(service._strategies[0], 'recognize', side_effect=Exception("Test error")):
            # Should still raise the exception
            with pytest.raises(Exception, match="Test error"):
                await service.recognize_intent("test input")

        # Verify error event was published
        assert len(events) == 1
        event = events[0]
        assert isinstance(event, ErrorEvent)
        assert event.service_name == "IntentRecognitionService"
        assert event.error_type == "Exception"
        assert event.error_message == "Test error"

        await service.stop()


class TestEndToEndIntegration:
    """Test end-to-end integration between services."""

    @pytest.fixture
    def event_bus(self):
        """Create a real event bus."""
        return EventBus()

    @pytest.fixture
    async def integrated_services(self, event_bus):
        """Create all integrated services."""
        manager = ServiceIntegrationManager(event_bus)

        # Create services
        intent_service = await manager.create_intent_recognition_service()
        execution_service = await manager.create_execution_engine_service()
        permission_service = await manager.create_permission_service()
        state_service = await manager.create_state_management_service()

        # Start all services
        await manager.start_all_services()

        yield {
            "manager": manager,
            "intent": intent_service,
            "execution": execution_service,
            "permission": permission_service,
            "state": state_service
        }

        # Cleanup
        await manager.stop_all_services()
        await event_bus.stop()

    @pytest.mark.asyncio
    async def test_service_communication_flow(self, integrated_services, event_bus):
        """Test communication flow between services."""
        events = []

        # Subscribe to all relevant events
        async def collect_events(event):
            events.append(event)

        await event_bus.subscribe(IntentRecognizedEvent, collect_events)
        await event_bus.subscribe(PermissionCheckedEvent, collect_events)
        await event_bus.subscribe(ExecutionStartedEvent, collect_events)
        await event_bus.subscribe(ExecutionCompletedEvent, collect_events)

        # Simulate workflow
        intent_service = integrated_services["intent"]
        permission_service = integrated_services["permission"]
        execution_service = integrated_services["execution"]

        # 1. Recognize intent
        intent_result = await intent_service.recognize_intent("read the file test.txt")

        # 2. Check permission
        permission_decision = await permission_service.check_permission(
            "file_read",
            {"user_role": "admin", "file_path": "/test/test.txt"}
        )

        # 3. Execute if permission granted
        if permission_decision.allowed:
            execution_result = await execution_service.execute(
                "file_read",
                {"file_path": "/test/test.txt"}
            )

        # Verify events were published
        event_types = [type(event).__name__ for event in events]
        assert "IntentRecognizedEvent" in event_types
        assert "PermissionCheckedEvent" in event_types
        assert "ExecutionStartedEvent" in event_types
        assert "ExecutionCompletedEvent" in event_types

        # Verify event contents
        intent_events = [e for e in events if isinstance(e, IntentRecognizedEvent)]
        assert len(intent_events) == 1
        assert intent_events[0].intent == intent_result.intent

        permission_events = [e for e in events if isinstance(e, PermissionCheckedEvent)]
        assert len(permission_events) == 1
        assert permission_events[0].allowed == permission_decision.allowed

    @pytest.mark.asyncio
    async def test_service_health_monitoring(self, integrated_services, event_bus):
        """Test service health monitoring through events."""
        events = []

        # Subscribe to health events
        async def collect_health_events(event):
            events.append(event)

        await event_bus.subscribe(ServiceHealthChangedEvent, collect_health_events)

        # Restart one service
        manager = integrated_services["manager"]
        intent_service = integrated_services["intent"]

        await intent_service.stop()
        await intent_service.start()

        # Verify health events were published
        health_events = [e for e in events if isinstance(e, ServiceHealthChangedEvent)]
        assert len(health_events) >= 2  # Stop and start events

        # Verify event sequence
        for event in health_events:
            assert event.service_name == "IntentRecognitionService"
            assert isinstance(event.healthy, bool)

    @pytest.mark.asyncio
    async def test_metrics_collection_integration(self, integrated_services):
        """Test integrated metrics collection."""
        manager = integrated_services["manager"]

        # Perform some operations
        intent_service = integrated_services["intent"]
        permission_service = integrated_services["permission"]

        await intent_service.recognize_intent("test input")
        await permission_service.check_permission("test_action", {"user": "test"})

        # Get all metrics
        metrics = await manager.get_all_metrics()

        assert "intent_recognition" in metrics
        assert "permission" in metrics
        assert "execution_engine" in metrics
        assert "state_management" in metrics

        # Verify metrics structure
        intent_metrics = metrics["intent_recognition"]
        assert "requests_processed" in intent_metrics
        assert "cache_hit_rate" in intent_metrics

        permission_metrics = metrics["permission"]
        assert "rules_count" in permission_metrics
        assert "checks_performed" in permission_metrics
"""Tests for the EventBus implementation."""

import asyncio
import pytest
from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

from daip_live.agent_engine_v1.events.event_bus import (
    EventBus,
    EventBusConfig,
    EventSubscription,
    create_session_filter,
    create_task_filter,
    create_error_filter,
    create_time_range_filter,
)
from daip_live.agent_engine_v1.events.event_types import (
    BaseEvent,
    SessionStartedEvent,
    SessionCompletedEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    ThoughtEvent,
    ToolCallEvent,
    ErrorEvent,
    EventType,
    create_event,
)


class TestEventBusConfig:
    """Test EventBus configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = EventBusConfig()
        assert config.max_subscribers == 1000
        assert config.max_event_history == 10000
        assert config.enable_persistence is True
        assert config.enable_metrics is True
        assert config.metrics_interval_seconds == 60.0
        assert config.batch_size == 100
        assert config.batch_timeout_ms == 10.0

    def test_custom_config(self):
        """Test custom configuration values."""
        config = EventBusConfig(
            max_subscribers=500,
            max_event_history=5000,
            enable_persistence=False,
            enable_metrics=False,
            metrics_interval_seconds=30.0,
            batch_size=50,
            batch_timeout_ms=5.0,
        )
        assert config.max_subscribers == 500
        assert config.max_event_history == 5000
        assert config.enable_persistence is False
        assert config.enable_metrics is False
        assert config.metrics_interval_seconds == 30.0
        assert config.batch_size == 50
        assert config.batch_timeout_ms == 5.0


class TestEventSubscription:
    """Test EventSubscription class."""

    @pytest.mark.asyncio
    async def test_subscription_creation(self):
        """Test subscription creation."""
        events_received = []

        async def handler(event: BaseEvent):
            events_received.append(event)

        subscription = EventSubscription(
            event_types=[EventType.SESSION_STARTED, EventType.TASK_STARTED],
            handler=handler,
            subscription_id="test_sub"
        )

        assert subscription.subscription_id == "test_sub"
        assert subscription.event_types == [EventType.SESSION_STARTED, EventType.TASK_STARTED]
        assert subscription.handler == handler
        assert subscription.filter_func is None
        assert subscription.events_received == 0
        assert subscription.events_processed == 0
        assert subscription.events_failed == 0

    @pytest.mark.asyncio
    async def test_subscription_should_handle_event(self):
        """Test subscription event filtering."""
        events_received = []

        async def handler(event: BaseEvent):
            events_received.append(event)

        subscription = EventSubscription(
            event_types=EventType.SESSION_STARTED,
            handler=handler
        )

        # Should handle matching event type
        session_event = SessionStartedEvent(session_id="test", goal="test goal")
        assert subscription.should_handle_event(session_event) is True

        # Should not handle non-matching event type
        task_event = TaskStartedEvent(task_id="test", task_description="test task")
        assert subscription.should_handle_event(task_event) is False

    @pytest.mark.asyncio
    async def test_subscription_with_filter(self):
        """Test subscription with custom filter."""
        events_received = []

        async def handler(event: BaseEvent):
            events_received.append(event)

        def session_filter(event: BaseEvent) -> bool:
            return hasattr(event, 'session_id') and event.session_id == "target_session"

        subscription = EventSubscription(
            event_types=EventType.SESSION_STARTED,
            handler=handler,
            filter_func=session_filter
        )

        # Should handle matching session
        target_event = SessionStartedEvent(session_id="target_session", goal="test goal")
        assert subscription.should_handle_event(target_event) is True

        # Should not handle non-matching session
        other_event = SessionStartedEvent(session_id="other_session", goal="test goal")
        assert subscription.should_handle_event(other_event) is False

    @pytest.mark.asyncio
    async def test_subscription_handle_event(self):
        """Test event handling."""
        events_received = []

        async def handler(event: BaseEvent):
            events_received.append(event)

        subscription = EventSubscription(
            event_types=EventType.SESSION_STARTED,
            handler=handler
        )

        event = SessionStartedEvent(session_id="test", goal="test goal")
        await subscription.handle_event(event)

        assert subscription.events_received == 1
        assert subscription.events_processed == 1
        assert subscription.events_failed == 0
        assert len(events_received) == 1
        assert events_received[0] == event


@pytest.mark.asyncio
class TestEventBus:
    """Test EventBus functionality."""

    async def test_event_bus_lifecycle(self):
        """Test starting and stopping the event bus."""
        config = EventBusConfig(enable_metrics=True)
        event_bus = EventBus(config)

        assert event_bus._running is False

        await event_bus.start()
        assert event_bus._running is True

        await event_bus.stop()
        assert event_bus._running is False

    async def test_publish_and_subscribe(self):
        """Test basic publish and subscribe functionality."""
        event_bus = EventBus()
        await event_bus.start()

        events_received = []

        async def handler(event: BaseEvent):
            events_received.append(event)

        # Subscribe to session events
        subscription_id = await event_bus.subscribe(
            event_types=EventType.SESSION_STARTED,
            handler=handler
        )

        # Publish an event
        event = SessionStartedEvent(session_id="test", goal="test goal")
        subscriber_count = await event_bus.publish(event)

        # Wait a bit for async processing
        await asyncio.sleep(0.1)

        # Verify event was received
        assert len(events_received) == 1
        assert events_received[0] == event
        assert subscriber_count == 1

        # Cleanup
        await event_bus.unsubscribe(subscription_id)
        await event_bus.stop()

    async def test_multiple_subscribers(self):
        """Test multiple subscribers to the same event type."""
        event_bus = EventBus()
        await event_bus.start()

        events_received_1 = []
        events_received_2 = []

        async def handler_1(event: BaseEvent):
            events_received_1.append(event)

        async def handler_2(event: BaseEvent):
            events_received_2.append(event)

        # Subscribe with two handlers
        sub_id_1 = await event_bus.subscribe(EventType.SESSION_STARTED, handler_1)
        sub_id_2 = await event_bus.subscribe(EventType.SESSION_STARTED, handler_2)

        # Publish event
        event = SessionStartedEvent(session_id="test", goal="test goal")
        subscriber_count = await event_bus.publish(event)

        await asyncio.sleep(0.1)

        # Both handlers should receive the event
        assert len(events_received_1) == 1
        assert len(events_received_2) == 1
        assert subscriber_count == 2

        # Cleanup
        await event_bus.unsubscribe(sub_id_1)
        await event_bus.unsubscribe(sub_id_2)
        await event_bus.stop()

    async def test_event_filtering(self):
        """Test event filtering."""
        event_bus = EventBus()
        await event_bus.start()

        events_received = []

        async def handler(event: BaseEvent):
            events_received.append(event)

        # Subscribe with session filter
        sub_id = await event_bus.subscribe(
            event_types=EventType.SESSION_STARTED,
            handler=handler,
            filter_func=create_session_filter("target_session")
        )

        # Publish events for different sessions
        target_event = SessionStartedEvent(session_id="target_session", goal="target goal")
        other_event = SessionStartedEvent(session_id="other_session", goal="other goal")

        await event_bus.publish(target_event)
        await event_bus.publish(other_event)

        await asyncio.sleep(0.1)

        # Only target session event should be received
        assert len(events_received) == 1
        assert events_received[0].session_id == "target_session"

        # Cleanup
        await event_bus.unsubscribe(sub_id)
        await event_bus.stop()

    async def test_event_history(self):
        """Test event history functionality."""
        config = EventBusConfig(max_event_history=3)
        event_bus = EventBus(config)
        await event_bus.start()

        # Publish events
        event1 = SessionStartedEvent(session_id="test1", goal="goal1")
        event2 = SessionStartedEvent(session_id="test2", goal="goal2")
        event3 = SessionStartedEvent(session_id="test3", goal="goal3")
        event4 = SessionStartedEvent(session_id="test4", goal="goal4")

        await event_bus.publish(event1)
        await event_bus.publish(event2)
        await event_bus.publish(event3)
        await event_bus.publish(event4)

        await asyncio.sleep(0.1)

        # Check history (should only keep last 3 events)
        history = await event_bus.get_event_history()
        assert len(history) == 3
        assert history[0].session_id == "test2"  # First in history
        assert history[2].session_id == "test4"  # Last in history

        # Check filtered history
        session2_history = await event_bus.get_event_history(
            event_type=EventType.SESSION_STARTED,
            limit=2
        )
        assert len(session2_history) == 2

        await event_bus.stop()

    async def test_stream_events(self):
        """Test event streaming functionality."""
        event_bus = EventBus()
        await event_bus.start()

        events_streamed = []

        # Start streaming in background
        async def stream_consumer():
            async for event in event_bus.stream(
                event_types=EventType.SESSION_STARTED,
                timeout=0.5  # Short timeout for testing
            ):
                events_streamed.append(event)

        stream_task = asyncio.create_task(stream_consumer())

        # Give stream time to start
        await asyncio.sleep(0.1)

        # Publish events
        event1 = SessionStartedEvent(session_id="test1", goal="goal1")
        event2 = SessionStartedEvent(session_id="test2", goal="goal2")

        await event_bus.publish(event1)
        await event_bus.publish(event2)

        # Wait for stream to complete
        await stream_task

        # Verify streamed events
        assert len(events_streamed) == 2
        assert events_streamed[0].session_id == "test1"
        assert events_streamed[1].session_id == "test2"

        await event_bus.stop()

    async def test_metrics(self):
        """Test event bus metrics."""
        config = EventBusConfig(enable_metrics=True)
        event_bus = EventBus(config)
        await event_bus.start()

        events_received = []

        async def handler(event: BaseEvent):
            events_received.append(event)

        # Subscribe and publish events
        sub_id = await event_bus.subscribe(EventType.SESSION_STARTED, handler)

        for i in range(5):
            event = SessionStartedEvent(session_id=f"test_{i}", goal=f"goal_{i}")
            await event_bus.publish(event)

        await asyncio.sleep(0.1)

        # Check metrics
        metrics = event_bus.get_metrics()
        assert metrics is not None
        assert metrics["events_published"] == 5
        assert metrics["events_delivered"] == 5
        assert metrics["events_failed"] == 0
        assert metrics["total_subscribers"] == 1
        assert EventType.SESSION_STARTED in metrics["event_type_counts"]
        assert metrics["event_type_counts"][EventType.SESSION_STARTED] == 5

        # Cleanup
        await event_bus.unsubscribe(sub_id)
        await event_bus.stop()

    async def test_batch_publishing(self):
        """Test batch event publishing."""
        event_bus = EventBus()
        await event_bus.start()

        events_received = []

        async def handler(event: BaseEvent):
            events_received.append(event)

        sub_id = await event_bus.subscribe(EventType.SESSION_STARTED, handler)

        # Create batch of events
        events = [
            SessionStartedEvent(session_id=f"test_{i}", goal=f"goal_{i}")
            for i in range(3)
        ]

        total_deliveries = await event_bus.publish_batch(events)

        await asyncio.sleep(0.1)

        assert total_deliveries == 3
        assert len(events_received) == 3

        # Cleanup
        await event_bus.unsubscribe(sub_id)
        await event_bus.stop()

    async def test_error_handling(self):
        """Test error handling in event processing."""
        event_bus = EventBus()
        await event_bus.start()

        events_received = []

        async def failing_handler(event: BaseEvent):
            events_received.append(event)
            raise ValueError("Test error")

        async def working_handler(event: BaseEvent):
            events_received.append(event)

        # Subscribe with both handlers
        failing_sub = await event_bus.subscribe(EventType.SESSION_STARTED, failing_handler)
        working_sub = await event_bus.subscribe(EventType.SESSION_STARTED, working_handler)

        # Publish event
        event = SessionStartedEvent(session_id="test", goal="test goal")
        await event_bus.publish(event)

        await asyncio.sleep(0.1)

        # Both handlers should have been called, despite one failing
        assert len(events_received) == 2

        # Cleanup
        await event_bus.unsubscribe(failing_sub)
        await event_bus.unsubscribe(working_sub)
        await event_bus.stop()


class TestEventFilters:
    """Test event filter utility functions."""

    def test_create_session_filter(self):
        """Test session filter creation."""
        filter_func = create_session_filter("target_session")

        # Should match target session
        target_event = SessionStartedEvent(session_id="target_session", goal="test")
        assert filter_func(target_event) is True

        # Should not match other session
        other_event = SessionStartedEvent(session_id="other_session", goal="test")
        assert filter_func(other_event) is False

    def test_create_task_filter(self):
        """Test task filter creation."""
        filter_func = create_task_filter("target_task")

        # Should match target task
        target_event = TaskStartedEvent(task_id="target_task", task_description="test")
        assert filter_func(target_event) is True

        # Should not match other task
        other_event = TaskStartedEvent(task_id="other_task", task_description="test")
        assert filter_func(other_event) is False

    def test_create_error_filter(self):
        """Test error filter creation."""
        filter_func = create_error_filter("critical")

        # Should match critical error
        critical_error = ErrorEvent(
            error_message="Critical error",
            error_type="CriticalError",
            severity="critical"
        )
        assert filter_func(critical_error) is True

        # Should not match non-critical error
        warning_error = ErrorEvent(
            error_message="Warning",
            error_type="Warning",
            severity="warning"
        )
        assert filter_func(warning_error) is False

    def test_create_time_range_filter(self):
        """Test time range filter creation."""
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=1)

        filter_func = create_time_range_filter(start_time, end_time)

        # Should match event within range
        in_range_event = SessionStartedEvent(
            session_id="test",
            goal="test",
            timestamp=start_time + timedelta(minutes=30)
        )
        assert filter_func(in_range_event) is True

        # Should not match event before range
        before_event = SessionStartedEvent(
            session_id="test",
            goal="test",
            timestamp=start_time - timedelta(minutes=30)
        )
        assert filter_func(before_event) is False

        # Should not match event after range
        after_event = SessionStartedEvent(
            session_id="test",
            goal="test",
            timestamp=end_time + timedelta(minutes=30)
        )
        assert filter_func(after_event) is False


class TestCreateEvent:
    """Test event creation utility function."""

    def test_create_event_with_type_enum(self):
        """Test creating event with EventType enum."""
        event = create_event(
            EventType.SESSION_STARTED,
            session_id="test",
            goal="test goal"
        )

        assert isinstance(event, SessionStartedEvent)
        assert event.event_type == EventType.SESSION_STARTED
        assert event.session_id == "test"
        assert event.goal == "test goal"

    def test_create_event_with_string(self):
        """Test creating event with string type."""
        event = create_event(
            "session_started",
            session_id="test",
            goal="test goal"
        )

        assert isinstance(event, SessionStartedEvent)
        assert event.event_type == EventType.SESSION_STARTED
        assert event.session_id == "test"
        assert event.goal == "test goal"

    def test_create_event_invalid_type(self):
        """Test creating event with invalid type."""
        with pytest.raises(ValueError, match="Unknown event type"):
            create_event("invalid_type")

    def test_create_event_missing_required_fields(self):
        """Test creating event with missing required fields."""
        with pytest.raises(ValueError):  # Pydantic validation error
            create_event(
                EventType.SESSION_STARTED,
                session_id="test"
                # Missing required 'goal' field
            )
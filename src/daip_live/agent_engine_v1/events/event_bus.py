"""Event bus implementation for the agent engine v1."""

import asyncio
import logging
import time
from collections import defaultdict, deque
from datetime import datetime
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    Union,
    AsyncGenerator
)

from .event_types import BaseEvent, EventType, is_session_event, is_task_event, is_error_event

logger = logging.getLogger(__name__)


# Type aliases for better readability
EventHandler = Callable[[BaseEvent], None]
AsyncEventHandler = Callable[[BaseEvent], Union[None, Any]]
EventFilter = Callable[[BaseEvent], bool]


class EventBusConfig:
    """Configuration for EventBus."""

    def __init__(
        self,
        max_subscribers: int = 1000,
        max_event_history: int = 10000,
        enable_persistence: bool = True,
        enable_metrics: bool = True,
        metrics_interval_seconds: float = 60.0,
        batch_size: int = 100,
        batch_timeout_ms: float = 10.0,
    ):
        """
        Initialize EventBus configuration.

        Args:
            max_subscribers: Maximum number of subscribers per event type
            max_event_history: Maximum number of events to keep in history
            enable_persistence: Whether to enable event persistence
            enable_metrics: Whether to collect performance metrics
            metrics_interval_seconds: Interval for collecting metrics
            batch_size: Batch size for event processing
            batch_timeout_ms: Timeout for batch processing
        """
        self.max_subscribers = max_subscribers
        self.max_event_history = max_event_history
        self.enable_persistence = enable_persistence
        self.enable_metrics = enable_metrics
        self.metrics_interval_seconds = metrics_interval_seconds
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms


class EventBusMetrics:
    """Performance metrics for the event bus."""

    def __init__(self):
        """Initialize metrics."""
        self.events_published = 0
        self.events_delivered = 0
        self.events_failed = 0
        self.publish_latency_sum = 0.0
        self.delivery_latency_sum = 0.0
        self.subscriber_counts: Dict[EventType, int] = defaultdict(int)
        self.event_type_counts: Dict[EventType, int] = defaultdict(int)
        self.last_reset_time = datetime.utcnow()

    def reset(self) -> None:
        """Reset all metrics."""
        self.events_published = 0
        self.events_delivered = 0
        self.events_failed = 0
        self.publish_latency_sum = 0.0
        self.delivery_latency_sum = 0.0
        self.subscriber_counts.clear()
        self.event_type_counts.clear()
        self.last_reset_time = datetime.utcnow()

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        uptime_seconds = (datetime.utcnow() - self.last_reset_time).total_seconds()

        avg_publish_latency = (
            self.publish_latency_sum / self.events_published
            if self.events_published > 0 else 0.0
        )

        avg_delivery_latency = (
            self.delivery_latency_sum / self.events_delivered
            if self.events_delivered > 0 else 0.0
        )

        events_per_second = self.events_published / uptime_seconds if uptime_seconds > 0 else 0.0

        return {
            "uptime_seconds": uptime_seconds,
            "events_published": self.events_published,
            "events_delivered": self.events_delivered,
            "events_failed": self.events_failed,
            "delivery_success_rate": (
                self.events_delivered / (self.events_delivered + self.events_failed)
                if (self.events_delivered + self.events_failed) > 0 else 1.0
            ),
            "avg_publish_latency_ms": avg_publish_latency * 1000,
            "avg_delivery_latency_ms": avg_delivery_latency * 1000,
            "events_per_second": events_per_second,
            "total_subscribers": sum(self.subscriber_counts.values()),
            "subscriber_counts": dict(self.subscriber_counts),
            "event_type_counts": dict(self.event_type_counts),
        }


class EventSubscription:
    """Represents a subscription to events."""

    def __init__(
        self,
        event_types: Union[EventType, List[EventType]],
        handler: Union[EventHandler, AsyncEventHandler],
        filter_func: Optional[EventFilter] = None,
        subscription_id: Optional[str] = None,
    ):
        """
        Initialize event subscription.

        Args:
            event_types: Event types to subscribe to
            handler: Handler function for events
            filter_func: Optional filter function
            subscription_id: Unique subscription identifier
        """
        self.subscription_id = subscription_id or f"sub_{id(self)}"
        self.event_types = (
            [event_types] if isinstance(event_types, EventType) else event_types
        )
        self.handler = handler
        self.filter_func = filter_func
        self.created_at = datetime.utcnow()
        self.events_received = 0
        self.events_processed = 0
        self.events_failed = 0

    def should_handle_event(self, event: BaseEvent) -> bool:
        """Check if this subscription should handle the event."""
        if event.event_type not in self.event_types:
            return False

        if self.filter_func and not self.filter_func(event):
            return False

        return True

    async def handle_event(self, event: BaseEvent) -> Any:
        """Handle an event."""
        self.events_received += 1

        try:
            if asyncio.iscoroutinefunction(self.handler):
                result = await self.handler(event)
            else:
                result = self.handler(event)

            self.events_processed += 1
            return result

        except Exception as e:
            self.events_failed += 1
            logger.error(
                f"Event handler failed for event {event.event_id}: {e}",
                exc_info=True
            )
            raise


class EventBus:
    """
    High-performance asynchronous event bus for the agent engine.

    This class provides publish/subscribe functionality for events with support for:
    - Async event handlers
    - Event filtering
    - Performance metrics
    - Event persistence
    - Batch processing
    """

    def __init__(self, config: Optional[EventBusConfig] = None):
        """
        Initialize the event bus.

        Args:
            config: Optional configuration for the event bus
        """
        self.config = config or EventBusConfig()
        self._subscribers: Dict[EventType, List[EventSubscription]] = defaultdict(list)
        self._event_history: deque = deque(maxlen=self.config.max_event_history)
        self._metrics = EventBusMetrics() if self.config.enable_metrics else None
        self._running = False
        self._shutdown_event = asyncio.Event()
        self._publish_queue: asyncio.Queue = asyncio.Queue(maxsize=self.config.max_event_history * 2)
        self._batch_processor_task: Optional[asyncio.Task] = None
        self._metrics_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the event bus."""
        if self._running:
            return

        self._running = True
        self._shutdown_event.clear()

        # Start batch processor
        self._batch_processor_task = asyncio.create_task(self._batch_processor())

        # Start metrics collector
        if self._metrics and self.config.enable_metrics:
            self._metrics_task = asyncio.create_task(self._metrics_collector())

        logger.info("EventBus started")

    async def stop(self) -> None:
        """Stop the event bus."""
        if not self._running:
            return

        self._running = False
        self._shutdown_event.set()

        # Cancel background tasks
        if self._batch_processor_task:
            self._batch_processor_task.cancel()
            try:
                await self._batch_processor_task
            except asyncio.CancelledError:
                pass

        if self._metrics_task:
            self._metrics_task.cancel()
            try:
                await self._metrics_task
            except asyncio.CancelledError:
                pass

        logger.info("EventBus stopped")

    def is_healthy(self) -> bool:
        """Check if the event bus is healthy."""
        return self._running

    async def publish(
        self,
        event: BaseEvent,
        wait_for_subscribers: bool = False
    ) -> int:
        """
        Publish an event to all subscribers.

        Args:
            event: The event to publish
            wait_for_subscribers: Whether to wait for all subscribers to process the event

        Returns:
            Number of subscribers the event was delivered to
        """
        if not self._running:
            raise RuntimeError("EventBus is not running")

        start_time = time.time()

        try:
            # Add to history
            self._event_history.append(event)

            # Add to publish queue for batch processing
            await self._publish_queue.put((event, wait_for_subscribers))

            # Update metrics
            if self._metrics:
                self._metrics.events_published += 1
                self._metrics.publish_latency_sum += time.time() - start_time
                self._metrics.event_type_counts[event.event_type] += 1

            # Get subscriber count
            subscriber_count = len(self._subscribers[event.event_type])

            logger.debug(f"Published event {event.event_id} of type {event.event_type} to {subscriber_count} subscribers")

            return subscriber_count

        except Exception as e:
            if self._metrics:
                self._metrics.events_failed += 1
            logger.error(f"Failed to publish event {event.event_id}: {e}", exc_info=True)
            raise

    async def publish_batch(
        self,
        events: List[BaseEvent],
        wait_for_subscribers: bool = False
    ) -> int:
        """
        Publish multiple events as a batch.

        Args:
            events: List of events to publish
            wait_for_subscribers: Whether to wait for all subscribers to process all events

        Returns:
            Total number of deliveries across all events
        """
        total_deliveries = 0
        for event in events:
            total_deliveries += await self.publish(event, wait_for_subscribers)
        return total_deliveries

    async def subscribe(
        self,
        event_types: Union[EventType, List[EventType]],
        handler: Union[EventHandler, AsyncEventHandler],
        filter_func: Optional[EventFilter] = None,
        subscription_id: Optional[str] = None
    ) -> str:
        """
        Subscribe to specific event types.

        Args:
            event_types: Event type(s) to subscribe to
            handler: Handler function for events
            filter_func: Optional filter function
            subscription_id: Optional unique subscription identifier

        Returns:
            Subscription ID
        """
        subscription = EventSubscription(event_types, handler, filter_func, subscription_id)

        # Check subscriber limits
        for event_type in subscription.event_types:
            if len(self._subscribers[event_type]) >= self.config.max_subscribers:
                raise ValueError(f"Maximum subscribers ({self.config.max_subscribers}) reached for event type {event_type}")

            self._subscribers[event_type].append(subscription)

        # Update metrics
        if self._metrics:
            for event_type in subscription.event_types:
                self._metrics.subscriber_counts[event_type] += 1

        logger.info(f"Subscribed to {len(subscription.event_types)} event types with subscription {subscription.subscription_id}")

        return subscription.subscription_id

    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: The subscription ID to unsubscribe

        Returns:
            True if unsubscribed successfully, False if not found
        """
        unsubscribed = False

        for event_type, subscriptions in self._subscribers.items():
            # Find and remove subscription
            for i, subscription in enumerate(subscriptions):
                if subscription.subscription_id == subscription_id:
                    subscriptions.pop(i)
                    unsubscribed = True

                    # Update metrics
                    if self._metrics:
                        self._metrics.subscriber_counts[event_type] -= 1

                    break

        if unsubscribed:
            logger.info(f"Unsubscribed subscription {subscription_id}")
        else:
            logger.warning(f"Subscription {subscription_id} not found")

        return unsubscribed

    async def stream(
        self,
        event_types: Optional[Union[EventType, List[EventType]]] = None,
        filter_func: Optional[EventFilter] = None,
        timeout: Optional[float] = None
    ) -> AsyncGenerator[BaseEvent, None]:
        """
        Stream events that match the given criteria.

        Args:
            event_types: Event types to stream (None for all)
            filter_func: Optional filter function
            timeout: Optional timeout for waiting for events

        Yields:
            Matching events
        """
        if event_types is None:
            event_types = list(EventType)
        elif isinstance(event_types, EventType):
            event_types = [event_types]

        # Create a queue for this stream
        queue: asyncio.Queue = asyncio.Queue()

        # Define stream handler
        async def stream_handler(event: BaseEvent) -> None:
            await queue.put(event)

        # Subscribe to events
        subscription_id = await self.subscribe(event_types, stream_handler, filter_func)

        try:
            while self._running:
                try:
                    # Wait for event with timeout
                    event = await asyncio.wait_for(queue.get(), timeout=timeout)
                    yield event
                except asyncio.TimeoutError:
                    # Timeout reached, exit gracefully
                    break
        finally:
            # Clean up subscription
            await self.unsubscribe(subscription_id)

    async def get_event_history(
        self,
        event_type: Optional[EventType] = None,
        limit: Optional[int] = None,
        since: Optional[datetime] = None
    ) -> List[BaseEvent]:
        """
        Get historical events.

        Args:
            event_type: Optional event type filter
            limit: Optional limit on number of events
            since: Optional start time filter

        Returns:
            List of matching events
        """
        events = list(self._event_history)

        # Filter by event type
        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Filter by time
        if since:
            events = [e for e in events if e.timestamp >= since]

        # Limit results
        if limit:
            events = events[-limit:]

        return events

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Get current metrics."""
        return self._metrics.get_summary() if self._metrics else None

    def get_subscriber_count(self, event_type: EventType) -> int:
        """Get number of subscribers for an event type."""
        return len(self._subscribers[event_type])

    def get_total_subscribers(self) -> int:
        """Get total number of subscribers across all event types."""
        return sum(len(subs) for subs in self._subscribers.values())

    async def _batch_processor(self) -> None:
        """Background task for processing events in batches."""
        batch = []
        wait_tasks = []

        while self._running:
            try:
                # Wait for events or timeout
                try:
                    event, wait_for_subscribers = await asyncio.wait_for(
                        self._publish_queue.get(),
                        timeout=self.config.batch_timeout_ms / 1000.0
                    )
                    batch.append((event, wait_for_subscribers))

                    # Check if batch is full
                    if len(batch) >= self.config.batch_size:
                        await self._process_batch(batch)
                        batch = []
                        wait_tasks = []

                except asyncio.TimeoutError:
                    # Process whatever we have in the batch
                    if batch:
                        await self._process_batch(batch)
                        batch = []
                        wait_tasks = []

            except Exception as e:
                logger.error(f"Error in batch processor: {e}", exc_info=True)
                await asyncio.sleep(0.1)  # Prevent tight error loop

    async def _process_batch(self, batch: List[tuple[BaseEvent, bool]]) -> None:
        """Process a batch of events."""
        if not batch:
            return

        # Group events by type for efficient processing
        events_by_type: Dict[EventType, List[tuple[BaseEvent, bool]]] = defaultdict(list)
        for event, wait_for_subscribers in batch:
            events_by_type[event.event_type].append((event, wait_for_subscribers))

        # Process each event type
        delivery_tasks = []

        for event_type, events in events_by_type.items():
            subscribers = self._subscribers[event_type]
            if not subscribers:
                continue

            for event, wait_for_subscribers in events:
                for subscription in subscribers:
                    if subscription.should_handle_event(event):
                        task = self._deliver_event(subscription, event, wait_for_subscribers)
                        delivery_tasks.append(task)

        # Wait for all deliveries to complete if needed
        if delivery_tasks:
            await asyncio.gather(*delivery_tasks, return_exceptions=True)

    async def _deliver_event(
        self,
        subscription: EventSubscription,
        event: BaseEvent,
        wait_for_completion: bool
    ) -> None:
        """Deliver an event to a subscription."""
        start_time = time.time()

        try:
            if wait_for_completion:
                await subscription.handle_event(event)
            else:
                # Fire and forget
                asyncio.create_task(subscription.handle_event(event))

            # Update metrics
            if self._metrics:
                self._metrics.events_delivered += 1
                self._metrics.delivery_latency_sum += time.time() - start_time

        except Exception as e:
            # Update error metrics
            if self._metrics:
                self._metrics.events_failed += 1
            logger.error(f"Failed to deliver event {event.event_id} to subscription {subscription.subscription_id}: {e}")

    async def _metrics_collector(self) -> None:
        """Background task for collecting and reporting metrics."""
        while self._running:
            try:
                await asyncio.sleep(self.config.metrics_interval_seconds)

                if self._metrics:
                    metrics = self._metrics.get_summary()
                    logger.info(f"EventBus metrics: {metrics}")

            except Exception as e:
                logger.error(f"Error in metrics collector: {e}", exc_info=True)
                await asyncio.sleep(1.0)  # Prevent tight error loop


# Utility functions for common event filters
def create_session_filter(session_id: str) -> EventFilter:
    """Create a filter for events from a specific session."""
    def filter_func(event: BaseEvent) -> bool:
        return event.session_id == session_id
    return filter_func


def create_task_filter(task_id: str) -> EventFilter:
    """Create a filter for events from a specific task."""
    def filter_func(event: BaseEvent) -> bool:
        return event.task_id == task_id
    return filter_func


def create_error_filter(severity: Optional[str] = None) -> EventFilter:
    """Create a filter for error events."""
    def filter_func(event: BaseEvent) -> bool:
        if not is_error_event(event):
            return False
        if severity and hasattr(event, 'severity'):
            return event.severity == severity
        return True
    return filter_func


def create_time_range_filter(start_time: datetime, end_time: Optional[datetime] = None) -> EventFilter:
    """Create a filter for events within a time range."""
    def filter_func(event: BaseEvent) -> bool:
        if event.timestamp < start_time:
            return False
        if end_time and event.timestamp > end_time:
            return False
        return True
    return filter_func
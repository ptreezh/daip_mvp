"""
TUI Event System

This module provides the TUIEventSystem class as specified in the newP6
architecture requirements. The event system provides event-driven communication
between components with priority processing, filtering, and async support.

Based on newP6 specification requirements for event-driven communication.
"""

import asyncio
import copy
import heapq
import time
import uuid
from collections import defaultdict, deque
from typing import Any, Callable, Optional

from .types import Event, EventType


class TUIEventSystem:
    """
    Event system for newP6 TUI architecture.

    This class provides event-driven communication between components with
    priority processing, filtering, and performance optimization as specified
    in the newP6 architecture requirements.

    Features:
    - Event subscription and unsubscription
    - Priority-based event processing
    - Event filtering and routing
    - Async event handling
    - Performance monitoring and statistics
    - Error handling resilience
    """

    def __init__(self):
        """Initialize the event system."""
        self._subscriptions: dict[EventType, list[dict]] = defaultdict(list)
        self._subscription_ids: set[str] = set()
        self._event_queue: list[tuple] = []  # Priority queue
        self._statistics = {
            "total_events_published": 0,
            "total_subscriptions": 0,
            "total_events_processed": 0,
            "total_errors": 0,
            "events_by_type": defaultdict(int),
            "processing_times": deque(maxlen=100),  # Keep last 100 processing times
        }
        self._processing = False
        self._pending_processing = False
        self._subscription_id_counter = 0

    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[Event], Any],
        filter_func: Optional[Callable[[Event], bool]] = None,
        target_component: Optional[str] = None,
    ) -> str:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: The type of events to subscribe to
            handler: Function to call when event occurs
            filter_func: Optional filter function for events
            target_component: Optional target component for directed events

        Returns:
            str: Subscription ID for unsubscribing later
        """
        subscription_id = str(uuid.uuid4())
        subscription = {
            "id": subscription_id,
            "handler": handler,
            "filter_func": filter_func,
            "target_component": target_component,
            "event_type": event_type,
        }

        self._subscriptions[event_type].append(subscription)
        self._subscription_ids.add(subscription_id)
        self._subscription_id_counter += 1

        # Update statistics
        self._statistics["total_subscriptions"] += 1

        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: The subscription ID to remove

        Returns:
            bool: True if unsubscribed successfully, False if not found
        """
        if subscription_id not in self._subscription_ids:
            return False

        # Find and remove the subscription
        for event_type, subscriptions in self._subscriptions.items():
            for i, sub in enumerate(subscriptions):
                if sub["id"] == subscription_id:
                    subscriptions.pop(i)
                    self._subscription_ids.discard(subscription_id)
                    return True

        return False

    def publish(self, event: Event) -> None:
        """
        Publish an event to be processed.

        Args:
            event: The event to publish
        """
        # Update statistics
        self._statistics["total_events_published"] += 1
        self._statistics["events_by_type"][event.event_type] += 1

        # Add to priority queue (lower number = higher priority)
        priority_value = event.priority.value
        heapq.heappush(self._event_queue, (priority_value, time.time(), event))

        # Process events immediately if not already processing
        if not self._processing:
            self._process_events()

    async def publish_async(self, event: Event) -> None:
        """
        Publish an event asynchronously.

        Args:
            event: The event to publish
        """
        # Update statistics
        self._statistics["total_events_published"] += 1
        self._statistics["events_by_type"][event.event_type] += 1

        # Add to priority queue
        priority_value = event.priority.value
        heapq.heappush(self._event_queue, (priority_value, time.time(), event))

        # Process events asynchronously
        if not self._processing:
            await self._process_events_async()

    def _delayed_process_events(self) -> None:
        """Delay processing events until the current event loop cycle completes."""
        self._pending_processing = False
        self._process_events()

    def _process_events(self) -> None:
        """Process events from the priority queue."""
        if self._processing:
            return

        self._processing = True

        try:
            while self._event_queue:
                priority, timestamp, event = heapq.heappop(self._event_queue)
                self._dispatch_event(event)
        finally:
            self._processing = False

    async def _process_events_async(self) -> None:
        """Process events from the priority queue asynchronously."""
        self._processing = True

        try:
            while self._event_queue:
                priority, timestamp, event = heapq.heappop(self._event_queue)
                await self._dispatch_event_async(event)
        finally:
            self._processing = False

    def _dispatch_event(self, event: Event) -> None:
        """
        Dispatch an event to all matching subscribers.

        Args:
            event: The event to dispatch
        """
        start_time = time.perf_counter()
        processed_count = 0

        # Get subscribers for this event type
        subscriptions = self._subscriptions.get(event.event_type, [])

        for subscription in subscriptions:
            try:
                # Apply filters
                if subscription.get("filter_func"):
                    if not subscription["filter_func"](event):
                        continue

                # Apply target component filter
                if subscription.get("target_component"):
                    if event.target != subscription["target_component"]:
                        continue

                # Call handler
                handler = subscription["handler"]
                if asyncio.iscoroutinefunction(handler):
                    # For async handlers, we need to handle them specially in sync context  # noqa: E501
                    # Create a new event loop or use existing one
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # Loop is already running, schedule the task
                            asyncio.create_task(handler(event))
                        else:
                            # Loop exists but not running, run the coroutine
                            loop.run_until_complete(handler(event))
                    except RuntimeError:
                        # No event loop, create one
                        asyncio.run(handler(event))
                else:
                    handler(event)

                processed_count += 1

            except Exception:
                # Log error but continue processing other handlers
                self._statistics["total_errors"] += 1

        # Update statistics
        processing_time = time.perf_counter() - start_time
        self._statistics["total_events_processed"] += 1
        self._statistics["processing_times"].append(
            processing_time * 1000
        )  # Convert to ms

    async def _dispatch_event_async(self, event: Event) -> None:
        """
        Dispatch an event asynchronously to all matching subscribers.

        Args:
            event: The event to dispatch
        """
        start_time = time.perf_counter()
        processed_count = 0

        # Get subscribers for this event type
        subscriptions = self._subscriptions.get(event.event_type, [])

        # Create async tasks for async handlers
        async_tasks = []
        sync_handlers = []

        for subscription in subscriptions:
            try:
                # Apply filters
                if subscription.get("filter_func"):
                    if not subscription["filter_func"](event):
                        continue

                # Apply target component filter
                if subscription.get("target_component"):
                    if event.target != subscription["target_component"]:
                        continue

                handler = subscription["handler"]
                if asyncio.iscoroutinefunction(handler):
                    async_tasks.append(handler(event))
                else:
                    sync_handlers.append(handler)

            except Exception:
                self._statistics["total_errors"] += 1

        # Execute async handlers concurrently
        if async_tasks:
            try:
                await asyncio.gather(*async_tasks, return_exceptions=True)
            except Exception:
                self._statistics["total_errors"] += 1

        # Execute sync handlers
        for handler in sync_handlers:
            try:
                handler(event)
                processed_count += 1
            except Exception:
                self._statistics["total_errors"] += 1

        # Update statistics
        processing_time = time.perf_counter() - start_time
        self._statistics["total_events_processed"] += 1
        self._statistics["processing_times"].append(processing_time * 1000)

    def get_statistics(self) -> dict[str, Any]:
        """
        Get event system statistics.

        Returns:
            Dict[str, Any]: Current statistics
        """
        stats = copy.deepcopy(self._statistics)

        # Add calculated metrics
        if stats["processing_times"]:
            stats["average_processing_time_ms"] = sum(stats["processing_times"]) / len(
                stats["processing_times"]
            )
            stats["max_processing_time_ms"] = max(stats["processing_times"])
            stats["min_processing_time_ms"] = min(stats["processing_times"])
        else:
            stats["average_processing_time_ms"] = 0
            stats["max_processing_time_ms"] = 0
            stats["min_processing_time_ms"] = 0

        # Add active subscriptions count
        stats["active_subscriptions"] = len(self._subscription_ids)

        return stats

    def clear_statistics(self) -> None:
        """Clear all statistics."""
        self._statistics = {
            "total_events_published": 0,
            "total_subscriptions": 0,
            "total_events_processed": 0,
            "total_errors": 0,
            "events_by_type": defaultdict(int),
            "processing_times": deque(maxlen=100),
        }

    def dispatch_event(self, event: Event) -> None:
        """
        Dispatch an event immediately (bypasses priority queue).

        Args:
            event: The event to dispatch immediately
        """
        self._dispatch_event(event)

"""Event handler base classes and common implementations."""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Type

from .event_bus import EventBus, EventSubscription
from .event_types import (
    BaseEvent,
    EventType,
    SessionStartedEvent,
    SessionCompletedEvent,
    TaskStartedEvent,
    TaskCompletedEvent,
    ThoughtEvent,
    ToolCallEvent,
    ToolOutputEvent,
    ErrorEvent,
    StateChangedEvent,
    PermissionRequestEvent
)

logger = logging.getLogger(__name__)


class BaseEventHandler(ABC):
    """
    Abstract base class for event handlers.

    This class provides a structured way to handle events with support for
    subscription management, error handling, and metrics.
    """

    def __init__(self, event_bus: EventBus, name: Optional[str] = None):
        """
        Initialize the event handler.

        Args:
            event_bus: The event bus to subscribe to
            name: Optional name for the handler
        """
        self.event_bus = event_bus
        self.name = name or self.__class__.__name__
        self._subscriptions: List[str] = []
        self._running = False
        self._metrics = {
            "events_processed": 0,
            "events_failed": 0,
            "processing_time_total": 0.0,
        }

    @property
    def supported_event_types(self) -> Set[EventType]:
        """Return the set of event types this handler supports."""
        return set()

    async def start(self) -> None:
        """Start the event handler."""
        if self._running:
            return

        self._running = True

        # Subscribe to supported event types
        for event_type in self.supported_event_types:
            subscription_id = await self.event_bus.subscribe(
                event_type=event_type,
                handler=self._handle_event_wrapper,
                subscription_id=f"{self.name}_{event_type.value}"
            )
            self._subscriptions.append(subscription_id)

        logger.info(f"Started event handler '{self.name}'")

    async def stop(self) -> None:
        """Stop the event handler."""
        if not self._running:
            return

        self._running = False

        # Unsubscribe from all events
        for subscription_id in self._subscriptions:
            await self.event_bus.unsubscribe(subscription_id)

        self._subscriptions.clear()
        logger.info(f"Stopped event handler '{self.name}'")

    async def _handle_event_wrapper(self, event: BaseEvent) -> None:
        """Wrapper for handling events with error handling and metrics."""
        if not self._running:
            return

        start_time = asyncio.get_event_loop().time()

        try:
            await self.handle_event(event)
            self._metrics["events_processed"] += 1

        except Exception as e:
            self._metrics["events_failed"] += 1
            logger.error(
                f"Event handler '{self.name}' failed to handle event {event.event_id}: {e}",
                exc_info=True
            )
            await self.on_error(event, e)

        finally:
            processing_time = asyncio.get_event_loop().time() - start_time
            self._metrics["processing_time_total"] += processing_time

    @abstractmethod
    async def handle_event(self, event: BaseEvent) -> None:
        """
        Handle an incoming event.

        Args:
            event: The event to handle
        """
        pass

    async def on_error(self, event: BaseEvent, error: Exception) -> None:
        """
        Called when an error occurs during event handling.

        Args:
            event: The event that caused the error
            error: The error that occurred
        """
        # Default implementation just logs the error
        logger.error(f"Error handling event {event.event_id}: {error}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get handler metrics."""
        total_events = self._metrics["events_processed"] + self._metrics["events_failed"]
        avg_processing_time = (
            self._metrics["processing_time_total"] / self._metrics["events_processed"]
            if self._metrics["events_processed"] > 0 else 0.0
        )

        return {
            "name": self.name,
            "running": self._running,
            "subscriptions": len(self._subscriptions),
            "events_processed": self._metrics["events_processed"],
            "events_failed": self._metrics["events_failed"],
            "success_rate": (
                self._metrics["events_processed"] / total_events
                if total_events > 0 else 1.0
            ),
            "avg_processing_time_ms": avg_processing_time * 1000,
            "total_processing_time_ms": self._metrics["processing_time_total"] * 1000,
        }


class LoggingEventHandler(BaseEventHandler):
    """Event handler that logs events."""

    def __init__(self, event_bus: EventBus, log_level: str = "INFO"):
        """
        Initialize the logging event handler.

        Args:
            event_bus: The event bus to subscribe to
            log_level: The log level to use for events
        """
        super().__init__(event_bus, "LoggingEventHandler")
        self.log_level = getattr(logging, log_level.upper())
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

    @property
    def supported_event_types(self) -> Set[EventType]:
        """Log all event types."""
        return set(EventType)

    async def handle_event(self, event: BaseEvent) -> None:
        """Log the event."""
        summary = event.get_summary()
        self.logger.log(self.log_level, f"[{event.event_type.value}] {summary}")


class MetricsEventHandler(BaseEventHandler):
    """Event handler that collects and stores event metrics."""

    def __init__(self, event_bus: EventBus, max_history: int = 10000):
        """
        Initialize the metrics event handler.

        Args:
            event_bus: The event bus to subscribe to
            max_history: Maximum number of events to keep in history
        """
        super().__init__(event_bus, "MetricsEventHandler")
        self.max_history = max_history
        self._event_history: List[BaseEvent] = []
        self._event_counts: Dict[EventType, int] = {}
        self._session_metrics: Dict[str, Dict[str, Any]] = {}

    @property
    def supported_event_types(self) -> Set[EventType]:
        """Track all event types for metrics."""
        return set(EventType)

    async def handle_event(self, event: BaseEvent) -> None:
        """Collect metrics from the event."""
        # Add to history (with size limit)
        self._event_history.append(event)
        if len(self._event_history) > self.max_history:
            self._event_history.pop(0)

        # Update event counts
        self._event_counts[event.event_type] = self._event_counts.get(event.event_type, 0) + 1

        # Update session-specific metrics
        if event.session_id:
            if event.session_id not in self._session_metrics:
                self._session_metrics[event.session_id] = {
                    "start_time": event.timestamp,
                    "events": 0,
                    "event_types": {},
                    "last_event": None,
                }

            session_metrics = self._session_metrics[event.session_id]
            session_metrics["events"] += 1
            session_metrics["last_event"] = event.timestamp
            session_metrics["event_types"][event.event_type] = (
                session_metrics["event_types"].get(event.event_type, 0) + 1
            )

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a comprehensive metrics summary."""
        total_events = sum(self._event_counts.values())

        # Calculate session statistics
        active_sessions = len(self._session_metrics)
        completed_sessions = sum(
            1 for metrics in self._session_metrics.values()
            if any(event_type in metrics["event_types"] for event_type in [
                EventType.SESSION_COMPLETED, EventType.SESSION_FAILED
            ])
        )

        return {
            "total_events": total_events,
            "event_type_counts": dict(self._event_counts),
            "active_sessions": active_sessions,
            "completed_sessions": completed_sessions,
            "total_sessions": len(self._session_metrics),
            "history_size": len(self._event_history),
            "history_capacity": self.max_history,
        }

    def get_session_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific session."""
        return self._session_metrics.get(session_id)

    def get_recent_events(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[BaseEvent]:
        """Get recent events, optionally filtered by type."""
        events = self._event_history

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:]


class StateTrackingEventHandler(BaseEventHandler):
    """Event handler that tracks system state based on events."""

    def __init__(self, event_bus: EventBus):
        """
        Initialize the state tracking event handler.

        Args:
            event_bus: The event bus to subscribe to
        """
        super().__init__(event_bus, "StateTrackingEventHandler")
        self._current_states: Dict[str, str] = {}
        self._state_history: List[Dict[str, Any]] = []

    @property
    def supported_event_types(self) -> Set[EventType]:
        """Track state-related events."""
        return {
            EventType.SESSION_STARTED,
            EventType.SESSION_COMPLETED,
            EventType.SESSION_FAILED,
            EventType.TASK_STARTED,
            EventType.TASK_COMPLETED,
            EventType.TASK_FAILED,
            EventType.STATE_CHANGED,
        }

    async def handle_event(self, event: BaseEvent) -> None:
        """Track state changes from events."""
        state_key = None
        new_state = None

        # Extract state information from different event types
        if isinstance(event, (SessionStartedEvent, SessionCompletedEvent, SessionFailedEvent)):
            state_key = f"session_{event.session_id}"
            if isinstance(event, SessionStartedEvent):
                new_state = "active"
            elif isinstance(event, SessionCompletedEvent):
                new_state = "completed"
            else:  # SessionFailedEvent
                new_state = "failed"

        elif isinstance(event, (TaskStartedEvent, TaskCompletedEvent, TaskFailedEvent)):
            state_key = f"task_{event.task_id}"
            if isinstance(event, TaskStartedEvent):
                new_state = "running"
            elif isinstance(event, TaskCompletedEvent):
                new_state = "completed"
            else:  # TaskFailedEvent
                new_state = "failed"

        elif isinstance(event, StateChangedEvent):
            state_key = f"{event.state_type}_{event.session_id or 'global'}"
            new_state = event.new_state

        # Update state if we have a valid transition
        if state_key and new_state:
            old_state = self._current_states.get(state_key)

            self._current_states[state_key] = new_state

            # Add to history
            self._state_history.append({
                "timestamp": event.timestamp,
                "state_key": state_key,
                "old_state": old_state,
                "new_state": new_state,
                "event_id": event.event_id,
                "reason": getattr(event, "reason", None),
            })

            # Keep history size manageable
            if len(self._state_history) > 1000:
                self._state_history.pop(0)

    def get_current_state(self, state_key: str) -> Optional[str]:
        """Get the current state for a specific key."""
        return self._current_states.get(state_key)

    def get_all_states(self) -> Dict[str, str]:
        """Get all current states."""
        return dict(self._current_states)

    def get_state_history(
        self,
        state_key: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get state history, optionally filtered by state key."""
        history = self._state_history

        if state_key:
            history = [h for h in history if h["state_key"] == state_key]

        return history[-limit:]


class ErrorTrackingEventHandler(BaseEventHandler):
    """Event handler that tracks and analyzes errors."""

    def __init__(self, event_bus: EventBus, max_error_history: int = 1000):
        """
        Initialize the error tracking event handler.

        Args:
            event_bus: The event bus to subscribe to
            max_error_history: Maximum number of errors to keep in history
        """
        super().__init__(event_bus, "ErrorTrackingEventHandler")
        self.max_error_history = max_error_history
        self._error_history: List[Dict[str, Any]] = []
        self._error_counts: Dict[str, int] = {}
        self._error_patterns: Dict[str, List[Dict[str, Any]]] = {}

    @property
    def supported_event_types(self) -> Set[EventType]:
        """Track error-related events."""
        return {
            EventType.ERROR,
            EventType.TASK_FAILED,
            EventType.SESSION_FAILED,
        }

    async def handle_event(self, event: BaseEvent) -> None:
        """Track error information from events."""
        error_info = {
            "timestamp": event.timestamp,
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "session_id": event.session_id,
            "task_id": event.task_id,
        }

        # Extract error-specific information
        if isinstance(event, ErrorEvent):
            error_info.update({
                "error_message": event.error_message,
                "error_type": event.error_type,
                "error_code": event.error_code,
                "severity": event.severity,
            })
            error_key = f"{event.error_type}:{event.severity}"

        elif isinstance(event, TaskFailedEvent):
            error_info.update({
                "error_message": event.error_message,
                "error_type": event.error_type,
                "retry_count": event.retry_count,
            })
            error_key = f"task_failed:{event.error_type}"

        elif isinstance(event, SessionFailedEvent):
            error_info.update({
                "error_message": event.error_message,
                "error_type": event.error_type,
            })
            error_key = f"session_failed:{event.error_type}"

        else:
            return  # Not an error event

        # Update error counts
        self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1

        # Add to pattern tracking
        if error_key not in self._error_patterns:
            self._error_patterns[error_key] = []

        self._error_patterns[error_key].append(error_info)

        # Keep pattern history manageable
        if len(self._error_patterns[error_key]) > 100:
            self._error_patterns[error_key].pop(0)

        # Add to general error history
        self._error_history.append(error_info)
        if len(self._error_history) > self.max_error_history:
            self._error_history.pop(0)

        # Log critical errors
        if error_info.get("severity") == "critical":
            logger.error(f"Critical error detected: {error_info}")

    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of error statistics."""
        total_errors = sum(self._error_counts.values())
        recent_errors = [
            e for e in self._error_history
            if (event.timestamp - e["timestamp"]).total_seconds() < 3600  # Last hour
        ]

        return {
            "total_errors": total_errors,
            "recent_errors_1h": len(recent_errors),
            "error_types": dict(self._error_counts),
            "unique_error_patterns": len(self._error_patterns),
            "history_size": len(self._error_history),
            "most_common_errors": sorted(
                self._error_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
        }

    def get_errors_by_pattern(self, error_pattern: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get errors for a specific pattern."""
        return self._error_patterns.get(error_pattern, [])[-limit:]

    def get_recent_errors(self, limit: int = 100, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent errors, optionally filtered by severity."""
        errors = self._error_history

        if severity:
            errors = [e for e in errors if e.get("severity") == severity]

        return errors[-limit:]
"""
Event Types and Definitions

This module provides the core event data structures for the newP6 event system,
including event types, priorities, and the base Event class.
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class EventType(Enum):
    """Enumeration of standard event types in the TUI system."""

    # User interaction events
    USER_INPUT = "user_input"
    KEY_PRESS = "key_press"
    MOUSE_CLICK = "mouse_click"

    # Component lifecycle events
    COMPONENT_MOUNTED = "component_mounted"
    COMPONENT_UNMOUNTED = "component_unmounted"
    COMPONENT_UPDATED = "component_updated"

    # System events
    SYSTEM_INIT = "system_init"
    SYSTEM_SHUTDOWN = "system_shutdown"

    # State events
    STATE_CHANGED = "state_changed"
    STATE_SAVED = "state_saved"
    STATE_RESTORED = "state_restored"

    # Navigation events
    NAVIGATION_REQUEST = "navigation_request"
    ROUTE_CHANGED = "route_changed"

    # Test events (for testing purposes)
    TEST = "test"
    PERFORMANCE_TEST = "performance_test"
    ERROR_TEST = "error_test"
    BATCH_TEST = "batch_test"
    STATS_TEST = "stats_test"
    DIRECTED = "directed"


class EventPriority(Enum):
    """Enumeration of event processing priorities."""

    CRITICAL = 0  # Highest priority - system critical events
    HIGH = 1  # High priority - user interactions
    NORMAL = 2  # Normal priority - standard events
    LOW = 3  # Low priority - background events
    BULK = 4  # Lowest priority - bulk operations


@dataclass
class Event:
    """
    Base event class for the newP6 event system.

    Attributes:
        event_type: The type/category of the event
        source: The component or system that generated the event
        data: Event-specific data payload
        priority: Processing priority of the event
        timestamp: Unix timestamp when the event was created
        target: Optional target component for directed events
        event_id: Unique identifier for this event
    """

    event_type: EventType
    source: str
    data: dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    timestamp: float = None
    target: Optional[str] = None
    event_id: str = None

    def __post_init__(self):
        """Initialize derived fields after dataclass creation."""
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.event_id is None:
            self.event_id = (
                f"{self.event_type.value}_{self.source}_{int(self.timestamp * 1000000)}"
            )

    def __str__(self) -> str:
        """String representation of the event."""
        return f"Event({self.event_id}, type={self.event_type.value}, source={self.source})"  # noqa: E501

    def __repr__(self) -> str:
        """Detailed string representation of the event."""
        return (
            f"Event(event_id='{self.event_id}', event_type={self.event_type}, "
            f"source='{self.source}', priority={self.priority}, "
            f"target={self.target})"
        )

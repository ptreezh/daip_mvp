"""
Event System for newP6 Architecture

This module provides the event-driven communication system as specified in the
newP6 architecture requirements. The event system provides:

- Event-driven communication between components
- Event routing and filtering
- Priority-based event processing
- Async event handling
- Performance-optimized event delivery
"""

from .system import TUIEventSystem
from .types import Event, EventPriority, EventType

__all__ = ["Event", "EventType", "EventPriority", "TUIEventSystem"]

"""
Base Service Adapter for newP6 TUI

Provides base functionality for all service adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseServiceAdapter(ABC):
    """Base class for all service adapters"""

    def __init__(self, service_instance: Any):
        self.service = service_instance
        self.event_system: Optional[Any] = None
        self.state_manager: Optional[Any] = None
        self._initialized = False

    def set_dependencies(self, event_system: Any, state_manager: Any) -> None:
        """Set event system and state manager dependencies"""
        self.event_system = event_system
        self.state_manager = state_manager

    async def initialize(self) -> None:
        """Initialize the service adapter"""
        self._initialized = True

    async def shutdown(self) -> None:
        """Shutdown the service adapter"""
        self._initialized = False

    @property
    def is_initialized(self) -> bool:
        """Check if the adapter is initialized"""
        return self._initialized

    def emit_event(self, event_type: str, data: Any = None) -> None:
        """Emit an event if event system is available"""
        if self.event_system and hasattr(self.event_system, 'publish'):
            # Create a simple event object
            event = type('Event', (), {
                'event_type': type('EventType', (), {'value': event_type})(),
                'data': data
            })()
            self.event_system.publish(event)

    def update_state(self, updates: dict) -> None:
        """Update state if state manager is available"""
        if self.state_manager and hasattr(self.state_manager, 'update_state'):
            self.state_manager.update_state(updates)
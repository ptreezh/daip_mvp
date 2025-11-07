"""
Base Status Widget for newP6 TUI Status Bar

Provides base functionality for status bar widgets.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class StatusWidget(ABC):
    """Base class for status bar widgets"""

    def __init__(self, name: str, label: str):
        self.name = name
        self.label = label
        self._value: Any = None
        self._last_updated: Optional[datetime] = None
        self.auto_refresh = False
        self.refresh_interval: float = 1.0
        self._refresh_task: Optional[asyncio.Task] = None
        self._running = False

    def update_value(self, value: Any) -> None:
        """Update the widget value and timestamp"""
        self._value = value
        self._last_updated = datetime.now()
        logger.debug(f"Widget {self.name} updated with value: {value}")

    def get_content(self) -> str:
        """Get the widget content for display"""
        if self._value is None:
            return f"{self.label}: N/A"
        return f"{self.label}: {self._value}"

    @abstractmethod
    async def refresh(self) -> None:
        """Refresh the widget data - must be implemented by subclasses"""
        pass

    def enable_auto_refresh(self, interval: float = 1.0) -> None:
        """Enable automatic refreshing of the widget"""
        self.auto_refresh = True
        self.refresh_interval = interval
        if not self._running:
            self._running = True
            try:
                loop = asyncio.get_running_loop()
                self._refresh_task = loop.create_task(self._auto_refresh_loop())
            except RuntimeError:
                # No event loop running, don't start auto-refresh loop
                # In a real application, the event loop should be running
                self._running = False

    def disable_auto_refresh(self) -> None:
        """Disable automatic refreshing of the widget"""
        self.auto_refresh = False
        if self._refresh_task and not self._refresh_task.done():
            self._refresh_task.cancel()
            self._running = False

    async def _auto_refresh_loop(self) -> None:
        """Internal auto-refresh loop"""
        while self.auto_refresh and self._running:
            try:
                await self.refresh()
                await asyncio.sleep(self.refresh_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in auto-refresh loop for widget {self.name}: {e}")
                await asyncio.sleep(self.refresh_interval)

    def get_last_updated(self) -> Optional[datetime]:
        """Get the last update timestamp"""
        return self._last_updated

    def get_age(self) -> Optional[float]:
        """Get the age of the current data in seconds"""
        if self._last_updated is None:
            return None
        return (datetime.now() - self._last_updated).total_seconds()

    async def cleanup(self) -> None:
        """Clean up widget resources"""
        self.disable_auto_refresh()
        self._running = False
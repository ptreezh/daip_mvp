"""
Main Status Bar for newP6 TUI

Provides real-time status bar functionality with widget management.
"""

import asyncio
import logging
from typing import Any, Optional

from .status_updater import StatusUpdater
from .status_widget import StatusWidget

logger = logging.getLogger(__name__)


class StatusBar:
    """Main status bar class that manages all status widgets"""

    def __init__(self):
        self._widgets: dict[str, StatusWidget] = {}
        self._updater: Optional[StatusUpdater] = None
        self._visible: bool = True
        self._initialized: bool = False

        # Dependencies
        self.event_system: Optional[Any] = None
        self.state_manager: Optional[Any] = None
        self.service_container: Optional[Any] = None

    def initialize(
        self, event_system: Any, state_manager: Any, service_container: Any
    ) -> None:
        """Initialize the status bar with dependencies"""
        self.event_system = event_system
        self.state_manager = state_manager
        self.service_container = service_container
        self._updater = StatusUpdater()
        self._updater.initialize(self, update_interval=1.0)
        self._initialized = True
        logger.info("Status bar initialized")

    def add_widget(self, widget: StatusWidget) -> None:
        """Add a status widget to the status bar"""
        if not isinstance(widget, StatusWidget):
            raise TypeError(
                f"Widget must be a StatusWidget instance, got {type(widget)}"
            )

        self._widgets[widget.name] = widget
        logger.info(f"Added widget: {widget.name}")

    def remove_widget(self, widget_name: str) -> bool:
        """Remove a status widget from the status bar"""
        if widget_name in self._widgets:
            widget = self._widgets.pop(widget_name)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(widget.cleanup())
            except RuntimeError:
                # No event loop running, schedule cleanup for later
                asyncio.run(widget.cleanup())
            logger.info(f"Removed widget: {widget_name}")
            return True
        return False

    def get_widget(self, widget_name: str) -> Optional[StatusWidget]:
        """Get a status widget by name"""
        return self._widgets.get(widget_name)

    def list_widgets(self) -> list[str]:
        """Get list of all widget names"""
        return list(self._widgets.keys())

    def show(self) -> None:
        """Show the status bar"""
        self._visible = True
        logger.debug("Status bar shown")

    def hide(self) -> None:
        """Hide the status bar"""
        self._visible = False
        logger.debug("Status bar hidden")

    def is_visible(self) -> bool:
        """Check if status bar is visible"""
        return self._visible

    def refresh(self) -> None:
        """Refresh all widgets"""
        logger.debug("Refreshing all widgets")
        for widget in self._widgets.values():
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(widget.refresh())
            except RuntimeError:
                # No event loop running, run synchronously
                asyncio.run(widget.refresh())

    def get_content(self) -> dict[str, str]:
        """Get content from all widgets"""
        content = {}
        for name, widget in self._widgets.items():
            try:
                content[name] = widget.get_content()
            except Exception as e:
                logger.error(f"Error getting content from widget {name}: {e}")
                content[name] = f"{widget.label}: Error"
        return content

    def get_formatted_content(self, separator: str = " | ") -> str:
        """Get formatted content string for display"""
        content = self.get_content()
        return separator.join(content.values())

    async def start_updates(self) -> None:
        """Start real-time status updates"""
        if self._updater and not self._updater.is_running():
            await self._updater.start()
            logger.info("Status bar updates started")

    async def stop_updates(self) -> None:
        """Stop real-time status updates"""
        if self._updater and self._updater.is_running():
            await self._updater.stop()
            logger.info("Status bar updates stopped")

    async def cleanup(self) -> None:
        """Clean up status bar resources"""
        await self.stop_updates()

        # Clean up all widgets
        cleanup_tasks = []
        for widget in self._widgets.values():
            cleanup_tasks.append(widget.cleanup())

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        self._widgets.clear()
        logger.info("Status bar cleaned up")

    def get_widget_count(self) -> int:
        """Get the number of widgets"""
        return len(self._widgets)

    def clear_widgets(self) -> None:
        """Remove all widgets"""
        for widget_name in list(self._widgets.keys()):
            self.remove_widget(widget_name)
        logger.info("All widgets cleared")

    def is_initialized(self) -> bool:
        """Check if status bar is initialized"""
        return self._initialized

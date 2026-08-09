"""
Status Updater for newP6 TUI Status Bar

Provides real-time update coordination for status bar widgets.
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .status_bar import StatusBar

logger = logging.getLogger(__name__)


class StatusUpdater:
    """Coordinates real-time updates for the status bar"""

    def __init__(self):
        self._status_bar: Optional[StatusBar] = None
        self._update_interval: float = 1.0
        self._running: bool = False
        self._update_task: Optional[asyncio.Task] = None

    def initialize(self, status_bar: "StatusBar", update_interval: float = 1.0) -> None:
        """Initialize the updater with a status bar and update interval"""
        self._status_bar = status_bar
        self._update_interval = update_interval
        logger.info(f"Status updater initialized with {update_interval}s interval")

    async def start(self) -> None:
        """Start the update loop"""
        if self._running:
            logger.warning("Status updater is already running")
            return

        if not self._status_bar:
            raise ValueError("Status bar not initialized")

        self._running = True
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info("Status updater started")

    async def stop(self) -> None:
        """Stop the update loop"""
        if not self._running:
            return

        self._running = False

        if self._update_task and not self._update_task.done():
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass

        logger.info("Status updater stopped")

    def is_running(self) -> bool:
        """Check if the updater is running"""
        return self._running

    def set_update_interval(self, interval: float) -> None:
        """Set the update interval in seconds"""
        if interval <= 0:
            raise ValueError("Update interval must be positive")
        self._update_interval = interval
        logger.debug(f"Update interval set to {interval}s")

    def get_update_interval(self) -> float:
        """Get the current update interval"""
        return self._update_interval

    async def _update_loop(self) -> None:
        """Internal update loop"""
        try:
            while self._running:
                if self._status_bar and self._status_bar.is_visible():
                    try:
                        self._status_bar.refresh()
                    except Exception as e:
                        logger.error(f"Error refreshing status bar: {e}")

                await asyncio.sleep(self._update_interval)

        except asyncio.CancelledError:
            logger.debug("Update loop cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in update loop: {e}")

    async def force_update(self) -> None:
        """Force an immediate update"""
        if self._status_bar:
            self._status_bar.refresh()

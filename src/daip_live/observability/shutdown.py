"""Graceful shutdown handling for observability.

This module provides graceful shutdown handling for system signals.
"""

import signal
from enum import Enum
from typing import Callable, List


class ShutdownSignal(Enum):
    """Shutdown signal types."""
    SIGINT = "SIGINT"
    SIGTERM = "SIGTERM"


class GracefulShutdown:
    """Manages graceful shutdown with callbacks."""

    def __init__(self, timeout: int = 10):
        """Initialize graceful shutdown manager.

        Args:
            timeout: Timeout in seconds for shutdown completion
        """
        self.timeout = timeout
        self.is_shutting_down = False
        self.callbacks: List[Callable[[], None]] = []

    def register(self, callback: Callable[[], None]) -> None:
        """Register a shutdown callback.

        Args:
            callback: Function to call during shutdown
        """
        self.callbacks.append(callback)

    def trigger(self) -> None:
        """Trigger graceful shutdown."""
        self.is_shutting_down = True
        for callback in self.callbacks:
            try:
                callback()
            except Exception:
                # Log but continue with other callbacks
                pass


class ShutdownHandler:
    """Handles system signals for graceful shutdown."""

    def __init__(self, timeout: int = 10):
        """Initialize shutdown handler.

        Args:
            timeout: Timeout in seconds for shutdown completion
        """
        self.shutdown = GracefulShutdown(timeout)
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for SIGINT and SIGTERM."""
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _handle_signal(self, signum, frame) -> None:
        """Handle shutdown signal."""
        self.shutdown.trigger()

    def register(self, callback: Callable[[], None]) -> None:
        """Register a shutdown callback.

        Args:
            callback: Function to call during shutdown
        """
        self.shutdown.register(callback)

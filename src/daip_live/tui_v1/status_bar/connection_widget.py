"""
Connection Status Widget for newP6 TUI Status Bar

Displays connection status to various services.
"""

import logging

from .status_widget import StatusWidget

logger = logging.getLogger(__name__)


class ConnectionStatusWidget(StatusWidget):
    """Widget for displaying connection status"""

    def __init__(self):
        super().__init__("connection_status", "Connection")
        self._connection_status = "unknown"
        self._connection_message = "Checking..."

    async def refresh(self) -> None:
        """Refresh connection status"""
        try:
            # For now, just display the current stored status
            # In a real implementation, this would check actual connectivity
            status_text = f"{self._connection_status}: {self._connection_message}"
            self.update_value(status_text)
        except Exception as e:
            logger.error(f"Error refreshing connection status: {e}")
            self.update_value("Connection Error")

    def update_status(self, status: str, message: str = "") -> None:
        """Update connection status"""
        self._connection_status = status
        self._connection_message = message

        # Update display value immediately
        status_text = f"{status}"
        if message:
            status_text += f": {message}"
        self.update_value(status_text)

    def set_connected(self, service_name: str = "API") -> None:
        """Set status to connected"""
        self.update_status("connected", f"{service_name} Connected")

    def set_disconnected(self, reason: str = "No Connection") -> None:
        """Set status to disconnected"""
        self.update_status("offline", reason)

    def set_connecting(self, service_name: str = "API") -> None:
        """Set status to connecting"""
        self.update_status("connecting", f"Connecting to {service_name}...")

    def set_error(self, error_message: str = "Connection Error") -> None:
        """Set status to error"""
        self.update_status("error", error_message)

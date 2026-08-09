"""
Session Widget for newP6 TUI Status Bar

Displays current session information.
"""

import logging
from typing import Any, Optional

from .status_widget import StatusWidget

logger = logging.getLogger(__name__)


class SessionWidget(StatusWidget):
    """Widget for displaying session information"""

    def __init__(self, session_service: Optional[Any] = None):
        super().__init__("session_info", "Session")
        self.session_service = session_service

    async def refresh(self) -> None:
        """Refresh session information"""
        try:
            if self.session_service and hasattr(
                self.session_service, "get_current_session"
            ):
                session_info = await self.session_service.get_current_session()
                if session_info:
                    session_name = session_info.get("name", "Unnamed")
                    session_status = session_info.get("status", "Unknown")
                    status_text = f"{session_name} ({session_status})"
                    self.update_value(status_text)
                else:
                    self.update_value("No Active Session")
            else:
                # Fallback status when service is not available
                self.update_value("No Session Service")
        except Exception as e:
            logger.error(f"Error refreshing session info: {e}")
            self.update_value("Session Error")

    def set_session_service(self, session_service: Any) -> None:
        """Set the session service"""
        self.session_service = session_service

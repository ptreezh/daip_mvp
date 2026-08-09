"""
Session Service Adapter for newP6 TUI

Adapts session management functionality for the TUI system.
"""

import logging
from typing import Optional

from .base import BaseServiceAdapter

logger = logging.getLogger(__name__)


class SessionServiceAdapter(BaseServiceAdapter):
    """Adapter for session management service"""

    async def list_sessions(self) -> list[dict]:
        """List all available sessions"""
        try:
            if self.service and hasattr(self.service, "list_sessions"):
                sessions = self.service.list_sessions()
                self.update_state({"sessions": sessions})
                self.emit_event("sessions_listed", {"sessions": sessions})
                return sessions
            else:
                # Mock data for testing/fallback
                mock_sessions = [
                    {"id": "12345", "name": "Test Session", "status": "active"},
                    {"id": "67890", "name": "Another Session", "status": "inactive"},
                ]
                self.update_state({"sessions": mock_sessions})
                return mock_sessions
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            self.emit_event("session_error", {"error": str(e)})
            return []

    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session details by ID"""
        try:
            if self.service and hasattr(self.service, "get_session"):
                session = self.service.get_session(session_id)
                self.emit_event(
                    "session_retrieved", {"session_id": session_id, "session": session}
                )
                return session
            else:
                # Mock data for testing/fallback
                mock_session = {"id": session_id, "status": "active"}
                self.emit_event(
                    "session_retrieved",
                    {"session_id": session_id, "session": mock_session},
                )
                return mock_session
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            self.emit_event(
                "session_error", {"error": str(e), "session_id": session_id}
            )
            return None

    async def create_session(self, name: Optional[str] = None) -> dict:
        """Create a new session"""
        try:
            session_name = name or "New Session"

            if self.service and hasattr(self.service, "create_session"):
                session = self.service.create_session(session_name)
            else:
                # Mock data for testing/fallback
                session = {
                    "id": "ABCDE",
                    "name": session_name,
                    "status": "active",
                    "created_at": "2025-11-02T10:00:00Z",
                }

            self.update_state({"current_session": session})
            self.emit_event("session_created", {"session": session})
            logger.info(f"Created session: {session['id']} ({session['name']})")
            return session
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            self.emit_event("session_error", {"error": str(e)})
            raise

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            if self.service and hasattr(self.service, "delete_session"):
                success = self.service.delete_session(session_id)
            else:
                # Mock data for testing/fallback
                success = True

            if success:
                self.emit_event("session_deleted", {"session_id": session_id})
                logger.info(f"Deleted session: {session_id}")
            else:
                logger.warning(f"Failed to delete session: {session_id}")

            return success
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            self.emit_event(
                "session_error", {"error": str(e), "session_id": session_id}
            )
            return False

    async def switch_session(self, session_id: str) -> bool:
        """Switch to a different session"""
        try:
            if self.service and hasattr(self.service, "switch_session"):
                success = self.service.switch_session(session_id)
            else:
                # Mock data for testing/fallback
                success = True

            if success:
                # Get session details for state update
                session = await self.get_session(session_id)
                if session:
                    self.update_state({"current_session": session})

                self.emit_event("session_switched", {"session_id": session_id})
                logger.info(f"Switched to session: {session_id}")
            else:
                logger.warning(f"Failed to switch to session: {session_id}")

            return success
        except Exception as e:
            logger.error(f"Error switching session {session_id}: {e}")
            self.emit_event(
                "session_error", {"error": str(e), "session_id": session_id}
            )
            return False

    async def get_current_session(self) -> Optional[dict]:
        """Get the current active session"""
        try:
            if self.service and hasattr(self.service, "get_current_session"):
                return self.service.get_current_session()
            else:
                # Return from state manager or mock data
                if self.state_manager and hasattr(self.state_manager, "get_state"):
                    state = self.state_manager.get_state()
                    return state.get("current_session")
                return None
        except Exception as e:
            logger.error(f"Error getting current session: {e}")
            return None

    async def update_session_name(self, session_id: str, new_name: str) -> bool:
        """Update session name"""
        try:
            if self.service and hasattr(self.service, "update_session_name"):
                success = self.service.update_session_name(session_id, new_name)
            else:
                # Mock data for testing/fallback
                success = True

            if success:
                self.emit_event(
                    "session_updated",
                    {"session_id": session_id, "updates": {"name": new_name}},
                )
                logger.info(f"Updated session name: {session_id} -> {new_name}")

            return success
        except Exception as e:
            logger.error(f"Error updating session name {session_id}: {e}")
            self.emit_event(
                "session_error", {"error": str(e), "session_id": session_id}
            )
            return False

"""
Session Command Handlers for newP6 TUI

Implements handlers for session management commands.
"""

from typing import List

from .base import BaseCommandHandler
from ..models import CommandResult


class SessionListHandler(BaseCommandHandler):
    """Handler for session list command"""

    def __init__(self):
        super().__init__()
        self.description = "List all sessions"
        self.session_service = None

    def handle(self, args: List[str]) -> CommandResult:
        """Handle session list command"""
        if self.session_service:
            # Use real service if available
            sessions = self.session_service.list_sessions()
            session_list = "\n".join([
                f"  📁 {s['id']}: {s['name']} ({s['status']})"
                for s in sessions
            ])
            message = f"📚 Available Sessions:\n{session_list}"
        else:
            # Mock data for testing
            message = """📚 Available Sessions:
  📁 12345: Test Session (active)
  📁 67890: Another Session (inactive)"""

        return CommandResult.success_result(message)


class SessionShowHandler(BaseCommandHandler):
    """Handler for session show command"""

    def __init__(self):
        super().__init__()
        self.description = "Show session details"
        self.session_service = None

    def handle(self, args: List[str]) -> CommandResult:
        """Handle session show command"""
        if not self.validate_args(args, min_args=1):
            return CommandResult.error_result(
                self.create_usage_message("session show <session_id>")
            )

        session_id = args[0]

        if self.session_service:
            # Use real service if available
            session = self.session_service.get_session(session_id)
            if not session:
                return CommandResult.error_result(f"Session {session_id} not found")

            message = f"""📁 Session Details:
  ID: {session['id']}
  Status: {session['status']}
  Created: {session.get('created_at', 'Unknown')}
  Last Activity: {session.get('last_activity', 'Unknown')}"""
        else:
            # Mock data for testing
            message = f"""📁 Session {session_id}:
  Status: active
  Created: 2025-11-02 10:30:00
  Last Activity: 2025-11-02 15:45:00
  Messages: 42
  Tokens Used: 15,234"""

        return CommandResult.success_result(message)


class SessionNewHandler(BaseCommandHandler):
    """Handler for session new command"""

    def __init__(self):
        super().__init__()
        self.description = "Create new session"
        self.session_service = None

    def handle(self, args: List[str]) -> CommandResult:
        """Handle session new command"""
        session_name = " ".join(args) if args else "New Session"

        if self.session_service:
            # Use real service if available
            session = self.session_service.create_session(session_name)
            message = f"✅ Created session: {session['id']} ({session['name']})"
        else:
            # Mock data for testing
            session_id = "ABCDE"
            message = f"✅ Created session: {session_id} ({session_name})"

        return CommandResult.success_result(message)


class SessionDeleteHandler(BaseCommandHandler):
    """Handler for session delete command"""

    def __init__(self):
        super().__init__()
        self.description = "Delete a session"
        self.session_service = None

    def handle(self, args: List[str]) -> CommandResult:
        """Handle session delete command"""
        if not self.validate_args(args, min_args=1):
            return CommandResult.error_result(
                self.create_usage_message("session delete <session_id>")
            )

        session_id = args[0]

        if self.session_service:
            # Use real service if available
            success = self.session_service.delete_session(session_id)
            if not success:
                return CommandResult.error_result(f"Failed to delete session {session_id}")

            message = f"🗑️ Deleted session: {session_id}"
        else:
            # Mock data for testing
            message = f"🗑️ Deleted session: {session_id}"

        return CommandResult.success_result(message)


class SessionSwitchHandler(BaseCommandHandler):
    """Handler for session switch command"""

    def __init__(self):
        super().__init__()
        self.description = "Switch to a session"
        self.session_service = None

    def handle(self, args: List[str]) -> CommandResult:
        """Handle session switch command"""
        if not self.validate_args(args, min_args=1):
            return CommandResult.error_result(
                self.create_usage_message("session switch <session_id>")
            )

        session_id = args[0]

        if self.session_service:
            # Use real service if available
            success = self.session_service.switch_session(session_id)
            if not success:
                return CommandResult.error_result(f"Failed to switch to session {session_id}")

            message = f"🔄 Switched to session: {session_id}"
        else:
            # Mock data for testing
            message = f"🔄 Switched to session: {session_id}"

        return CommandResult.success_result(message)
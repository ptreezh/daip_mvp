"""Session management service for multi-agent interactions."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from daip_live.core.models import AgentState, DialogueTurn, Session
from daip_live.persistence.database import DatabaseManager


class SessionManager:
    """Manages the lifecycle of multi-agent sessions."""

    def __init__(self, db_manager: DatabaseManager):
        """Initialize the SessionManager with a database connection."""
        self.db_manager = db_manager

    def create_session(
        self, goal: str, session_type: str, participant_ids: list[str]
    ) -> Session:
        """
        Creates a new session instance with its initial parameters.

        Args:
            goal: The overall goal or topic of the session.
            session_type: The type of session (e.g., "debate", "chat", "workflow").
            participant_ids: A list of participant IDs.

        Returns:
            A new Session object.
        """
        session = Session(
            session_id=f"session_{uuid.uuid4()}",
            goal=goal,
            session_type=session_type,
            participant_ids=participant_ids,
            status=AgentState.INIT,
        )

        # Persist the session to the database
        self.db_manager.save_session(session)
        return session

    def add_dialogue_turn(self, session_id: str, turn: DialogueTurn) -> None:
        """
        Appends a new dialogue turn to the history of a specific session.

        Args:
            session_id: The ID of the session.
            turn: The DialogueTurn object to add.
        """
        # Get the existing session
        session = self.db_manager.get_session(session_id)
        if session:
            # Add the new turn to the history
            session.history.append(turn)
            # Save the updated session
            self.db_manager.save_session(session)

    def end_session(
        self, session_id: str, final_status: AgentState, summary: str
    ) -> None:
        """
        Finalizes a session by setting its end time, final status, and summary.

        Args:
            session_id: The ID of the session.
            final_status: The final status of the session.
            summary: A summary of the session.
        """
        session = self.db_manager.get_session(session_id)
        if session:
            session.status = final_status
            session.summary = summary
            session.end_time = datetime.now(timezone.utc)
            self.db_manager.save_session(session)

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieves a full session record, including its dialogue history.

        Args:
            session_id: The ID of the session.

        Returns:
            A Session object or None if not found.
        """
        return self.db_manager.get_session(session_id)

    def list_sessions(self) -> list[Session]:
        """
        Retrieves a list of all sessions (metadata only, without the full history for efficiency).

        Returns:
            A list of Session objects.
        """  # noqa: E501
        return self.db_manager.list_sessions()

    def save_session(self, session: Session) -> None:
        """
        Saves or updates a session and its dialogue turns in the database.

        Args:
            session: The Session object to save.
        """
        self.db_manager.save_session(session)

    def delete_session(self, session_id: str) -> bool:
        """
        Deletes a session and its associated dialogue turns from the database.

        Args:
            session_id: The ID of the session to delete.

        Returns:
            True if the session was deleted, False if it was not found.
        """
        return self.db_manager.delete_session(session_id)

    def clear_all_sessions(self) -> int:
        """
        Deletes all sessions from the database.

        Returns:
            The number of sessions deleted.
        """
        return self.db_manager.clear_all_sessions()

"""Real database integration tests using actual SQLite.

These tests use the real database layer without mocks.
"""

import pytest
import tempfile
from pathlib import Path
from daip_live.persistence.database import DatabaseManager
from daip_live.core.models import Session, DialogueTurn, AgentState


@pytest.fixture
def temp_db():
    """Create a temporary database."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_path = Path(temp_file.name)
    temp_file.close()
    db = DatabaseManager(db_path=str(temp_path))
    yield db
    # Cleanup - try delete, ignore if locked (Windows)
    try:
        temp_path.unlink()
    except (PermissionError, OSError):
        pass  # Windows file lock


@pytest.mark.integration
class TestRealDatabaseIntegration:
    """Integration tests using real database."""

    def test_session_save_and_load(self, temp_db):
        """Test saving and loading a session using real database."""
        # Create a session with required fields
        session = Session(
            session_id="test_session_001",
            session_type="chat",
            goal="Test session",
            participant_ids=["user_1"]
        )

        # Save the session (returns None)
        temp_db.save_session(session)

        # Load the session
        loaded_session = temp_db.get_session("test_session_001")
        assert loaded_session is not None
        assert loaded_session.session_id == "test_session_001"
        assert loaded_session.session_type == "chat"
        assert loaded_session.goal == "Test session"
        assert loaded_session.participant_ids == ["user_1"]

    def test_session_list_all(self, temp_db):
        """Test listing all sessions."""
        # Create multiple sessions
        for i in range(3):
            session = Session(
                session_id=f"session_{i}",
                session_type="chat",
                goal=f"Test goal {i}",
                participant_ids=["user_1"]
            )
            temp_db.save_session(session)

        # List all sessions
        sessions = temp_db.list_sessions()
        assert len(sessions) == 3
        session_ids = [s.session_id for s in sessions]
        assert "session_0" in session_ids
        assert "session_1" in session_ids
        assert "session_2" in session_ids

    def test_session_delete(self, temp_db):
        """Test deleting a session."""
        session = Session(
            session_id="delete_test",
            session_type="chat",
            goal="Delete test",
            participant_ids=["user_1"]
        )
        temp_db.save_session(session)

        # Verify it exists
        assert temp_db.get_session("delete_test") is not None

        # Delete it
        temp_db.delete_session("delete_test")

        # Verify it's gone
        assert temp_db.get_session("delete_test") is None

    def test_session_update(self, temp_db):
        """Test updating an existing session."""
        session = Session(
            session_id="update_test",
            session_type="chat",
            goal="Update test",
            participant_ids=["user_1"]
        )
        temp_db.save_session(session)

        # Create updated session (Pydantic models are immutable)
        updated_session = Session(
            session_id="update_test",
            session_type="chat",
            goal="Updated goal",  # Changed
            participant_ids=["user_1", "user_2"]  # Added participant
        )
        temp_db.save_session(updated_session)

        # Load and verify
        loaded = temp_db.get_session("update_test")
        assert loaded.goal == "Updated goal"
        assert len(loaded.participant_ids) == 2

    def test_session_with_status(self, temp_db):
        """Test session status field."""
        session = Session(
            session_id="status_test",
            session_type="chat",
            goal="Status test",
            participant_ids=["user_1"],
            status=AgentState.RUNNING
        )
        temp_db.save_session(session)

        # Load and verify status
        loaded = temp_db.get_session("status_test")
        assert loaded is not None
        assert loaded.status == AgentState.RUNNING

    def test_nonexistent_session(self, temp_db):
        """Test getting a session that doesn't exist."""
        result = temp_db.get_session("nonexistent_session")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

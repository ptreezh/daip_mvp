
import pytest

from daip_live.core.models import AgentState, DialogueTurn
from daip_live.memory.session_manager import SessionManager
from daip_live.persistence.database import DatabaseManager


@pytest.fixture
def session_manager():
    """Provides a SessionManager instance for testing."""
    db_manager = DatabaseManager(db_path=":memory:")
    return SessionManager(db_manager=db_manager)

def test_full_session_lifecycle(session_manager):
    """
    Test the full lifecycle of a session:
    1. Create a 'debate' session with multiple participants.
    2. Add several DialogueTurn instances to it.
    3. End the session.
    4. Retrieve the session and verify its contents (participants, history, status).
    """
    # Arrange
    goal = "讨论项目架构"
    session_type = "debate"
    participant_ids = ["user_human", "role_pro_01", "role_con_02"]

    # Act
    session = session_manager.create_session(goal, session_type, participant_ids)

    # Assert
    assert session.goal == goal
    assert session.session_type == session_type
    assert set(session.participant_ids) == set(participant_ids)
    assert session.status == AgentState.INIT

    # Add dialogue turns
    turn1 = DialogueTurn(participant_id="user_human", content="我们开始讨论吧。")
    turn2 = DialogueTurn(participant_id="role_pro_01", content="我认为我们应该采用微服务架构。")
    session_manager.add_dialogue_turn(session.session_id, turn1)
    session_manager.add_dialogue_turn(session.session_id, turn2)

    # End session
    summary = "讨论了项目架构，初步倾向于微服务。"
    session_manager.end_session(session.session_id, AgentState.COMPLETED, summary)

    # Retrieve and verify
    retrieved_session = session_manager.get_session(session.session_id)
    assert retrieved_session is not None
    assert retrieved_session.session_id == session.session_id
    assert len(retrieved_session.history) == 2
    assert retrieved_session.status == AgentState.COMPLETED
    assert retrieved_session.summary == summary

def test_get_nonexistent_session(session_manager):
    """Test retrieving a session that does not exist."""
    # Act
    retrieved_session = session_manager.get_session("nonexistent_session_id")

    # Assert
    assert retrieved_session is None

def test_list_sessions_empty(session_manager):
    """Test listing sessions when none exist."""
    # Act
    sessions = session_manager.list_sessions()

    # Assert
    assert sessions == []

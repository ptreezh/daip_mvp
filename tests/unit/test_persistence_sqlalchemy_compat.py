"""SQLAlchemy 2.0 compatibility test for the real Session/DialogueTurn API."""
import pytest
from daip_live.persistence.database import DatabaseManager
from daip_live.core.models import Session, AgentState


def test_session_save_with_pydantic_v2():
    """Test session save uses Pydantic v2 model_dump() API."""
    db = DatabaseManager("sqlite:///:memory:")

    session = Session(
        session_id="test-session-1",
        session_type="chat",
        goal="Test goal",
        participant_ids=["user_human"],
        status=AgentState.IDLE,
        history=[]
    )

    # Should succeed without AttributeError
    db.save_session(session)

    # Should load successfully
    loaded = db.get_session("test-session-1")
    assert loaded is not None
    assert loaded.session_id == "test-session-1"
    assert loaded.status == AgentState.IDLE
    assert loaded.goal == "Test goal"
    assert loaded.participant_ids == ["user_human"]


def test_session_model_dump_compatibility():
    """Test Session.model_dump() works with Pydantic v2."""
    session = Session(
        session_id="test-session-2",
        session_type="debate",
        goal="AI future debate",
        participant_ids=["role_pro_01", "role_con_02"],
        status=AgentState.RUNNING,
        history=[]
    )

    # Pydantic v2's model_dump() returns dict
    session_dict = session.model_dump()
    assert isinstance(session_dict, dict)
    assert session_dict["session_id"] == "test-session-2"
    assert session_dict["session_type"] == "debate"
    assert session_dict["status"] == AgentState.RUNNING
    assert session_dict["participant_ids"] == ["role_pro_01", "role_con_02"]


def test_session_with_history():
    """Test session save/load with dialogue history."""
    from daip_live.core.models import DialogueTurn

    db = DatabaseManager("sqlite:///:memory:")

    session = Session(
        session_id="test-session-3",
        session_type="chat",
        goal="Test goal",
        participant_ids=["user_human"],
        status=AgentState.RUNNING,
        history=[
            DialogueTurn(
                participant_id="user_human",
                content="Hello"
            )
        ]
    )

    db.save_session(session)

    loaded = db.get_session("test-session-3")
    assert loaded is not None
    assert len(loaded.history) == 1
    assert loaded.history[0].participant_id == "user_human"
    assert loaded.history[0].content == "Hello"

import pytest

# 统一 daip_live 前缀：src.daip_live 与 daip_live 双路径会产生两个 AgentState 枚举类，
# 导致 == 比较失败（源码内部用 daip_live 前缀）
from daip_live.core.models import AgentState, DialogueTurn, KnowledgeSource, Session
from daip_live.persistence.database import DatabaseManager


@pytest.fixture
def db_manager() -> DatabaseManager:
    """Fixture to create an in-memory SQLite database for each test."""
    return DatabaseManager(db_path=":memory:")

def test_save_and_get_session(db_manager: DatabaseManager):
    """Test saving a new session and retrieving it."""
    # 1. Create a session object
    participants = ["role_1", "role_2"]
    history = [
        DialogueTurn(participant_id="role_1", content="Hello!"),
        DialogueTurn(participant_id="role_2", content="Hi there!")
    ]
    session = Session(
        session_type="chat",
        goal="Test conversation",
        participant_ids=participants,
        history=history,
        status=AgentState.COMPLETED,
        summary="A test chat."
    )

    # 2. Save the session
    db_manager.save_session(session)

    # 3. Retrieve the session
    retrieved_session = db_manager.get_session(session.session_id)

    # 4. Assertions
    assert retrieved_session is not None
    assert retrieved_session.session_id == session.session_id
    assert retrieved_session.goal == "Test conversation"
    assert retrieved_session.status == AgentState.COMPLETED
    assert len(retrieved_session.history) == 2
    assert retrieved_session.history[1].content == "Hi there!"
    assert retrieved_session.participant_ids == participants

def test_update_existing_session(db_manager: DatabaseManager):
    """Test that saving a session with an existing ID updates it."""
    # 1. Create and save initial session
    session = Session(session_type="chat", goal="Initial goal", participant_ids=["p1"])
    db_manager.save_session(session)

    # 2. Update the session object
    session.goal = "Updated goal"
    session.status = AgentState.FAILED
    session.history.append(DialogueTurn(participant_id="p1", content="An update."))

    # 3. Save again
    db_manager.save_session(session)

    # 4. Retrieve and verify
    retrieved_session = db_manager.get_session(session.session_id)
    assert retrieved_session is not None
    assert retrieved_session.goal == "Updated goal"
    assert retrieved_session.status == AgentState.FAILED
    assert len(retrieved_session.history) == 1

def test_list_sessions(db_manager: DatabaseManager):
    """Test listing all sessions."""
    # 1. Create multiple sessions
    s1 = Session(session_type="chat", goal="Chat 1", participant_ids=["p1"])
    s2 = Session(session_type="debate", goal="Debate 1", participant_ids=["p1", "p2"])
    db_manager.save_session(s1)
    db_manager.save_session(s2)

    # 2. List sessions
    all_sessions = db_manager.list_sessions()

    # 3. Assertions
    assert len(all_sessions) == 2
    # list_sessions returns without history, so check that
    assert len(all_sessions[0].history) == 0
    session_goals = {s.goal for s in all_sessions}
    assert "Chat 1" in session_goals
    assert "Debate 1" in session_goals

def test_get_non_existent_session(db_manager: DatabaseManager):
    """Test that getting a non-existent session returns None."""
    retrieved_session = db_manager.get_session("non-existent-id")
    assert retrieved_session is None

@pytest.mark.asyncio
async def test_get_knowledge_sources_by_ids(db_manager: DatabaseManager):
    """Test retrieving multiple knowledge sources by their IDs."""
    # 1. Arrange: Create and save multiple source objects
    source1 = KnowledgeSource(file_path="/path/1", file_hash="hash1")
    source2 = KnowledgeSource(file_path="/path/2", file_hash="hash2")
    source3 = KnowledgeSource(file_path="/path/3", file_hash="hash3")

    # The upsert method returns the object with the assigned ID
    s1_saved = db_manager.upsert_knowledge_source(source1)
    s2_saved = db_manager.upsert_knowledge_source(source2)
    s3_saved = db_manager.upsert_knowledge_source(source3)

    # 2. Act: Retrieve a subset of the sources by their new IDs
    ids_to_fetch = [s1_saved.id, s3_saved.id]
    # 源码权威: get_knowledge_sources_by_ids 是同步方法（database.py），调用方经
    # asyncio.to_thread 包装；此处直接同步调用
    retrieved_sources = db_manager.get_knowledge_sources_by_ids(ids_to_fetch)

    # 3. Assert
    assert len(retrieved_sources) == 2
    retrieved_paths = {s.file_path for s in retrieved_sources}
    assert "/path/1" in retrieved_paths
    assert "/path/2" not in retrieved_paths
    assert "/path/3" in retrieved_paths

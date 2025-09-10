import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from src.daip_live.p7_gui.main import app, get_session_manager
from src.daip_live.core.models import Session, AgentState
from src.daip_live.memory.session_manager import SessionManager

# Mock SessionManager
mock_session_manager = MagicMock(spec=SessionManager)

def get_mock_session_manager():
    # Reset mocks for each test function
    mock_session_manager.reset_mock()
    # Re-assign return values after reset
    mock_session_manager.create_session.return_value = Session(
        session_id="test_sess_123",
        goal="Test Goal",
        session_type="workflow",
        status=AgentState.INIT, # Use real enum member
        participant_ids=["agent", "user"]
    )
    mock_session_manager.list_sessions.return_value = [
        Session(session_id="sess_1", goal="Goal 1", session_type="chat", status=AgentState.COMPLETED, participant_ids=[]),
        Session(session_id="sess_2", goal="Goal 2", session_type="debate", status=AgentState.FAILED, participant_ids=[])
    ]
    return mock_session_manager

app.dependency_overrides[get_session_manager] = get_mock_session_manager

client = TestClient(app)

def test_create_session_api():
    """Test POST /api/sessions endpoint."""
    response = client.post("/api/sessions", json={"goal": "Test Goal"})

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == AgentState.INIT.value # Compare with value
    assert json_response["session_id"] == "test_sess_123"
    assert json_response["goal"] == "Test Goal"
    mock_session_manager.save_session.assert_called_once_with(mock_session_manager.create_session.return_value)

def test_list_sessions_api():
    """Test GET /api/sessions endpoint."""
    response = client.get("/api/sessions")

    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2
    assert json_response[0]["session_id"] == "sess_1"
    assert json_response[1]["goal"] == "Goal 2"
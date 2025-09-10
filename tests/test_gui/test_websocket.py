import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock
import asyncio

from src.daip_live.p7_gui.main import app, get_agent_executor, get_session_manager
from src.daip_live.core.models import ThoughtEvent, Session
from src.daip_live.agent_engine.executor import AgentExecutor
from src.daip_live.memory.session_manager import SessionManager

# Mock dependencies
mock_agent_executor = MagicMock(spec=AgentExecutor)

# This async generator will be the mock for our agent's event stream
async def mock_event_stream(*args, **kwargs):
    yield ThoughtEvent(content="Test event from agent")
    await asyncio.sleep(0.5) # give time for the client to send a message

mock_agent_executor.run = mock_event_stream
mock_agent_executor.user_input_queue = asyncio.Queue()

def get_mock_agent_executor():
    return mock_agent_executor

# Mock session manager to prevent DB calls
mock_session_manager = MagicMock(spec=SessionManager)
mock_session_manager.get_session.return_value = Session(goal="test", session_type="workflow", participant_ids=[])

def get_mock_session_manager():
    return mock_session_manager

app.dependency_overrides[get_agent_executor] = get_mock_agent_executor
app.dependency_overrides[get_session_manager] = get_mock_session_manager

client = TestClient(app)

def test_websocket_communication():
    """Test the WebSocket endpoint for sending and receiving events."""
    with client.websocket_connect("/ws/sessions/test_session_123") as websocket:
        # 1. Test server-to-client communication
        data = websocket.receive_json()
        assert data["type"] == "thought"
        assert data["content"] == "Test event from agent"

        # 2. Test client-to-server communication
        websocket.send_json({"type": "user_input", "content": "Hello from client"})
        
        # Allow the server-side task to process the message
        async def get_from_queue():
            return await asyncio.wait_for(mock_agent_executor.user_input_queue.get(), timeout=1)
        
        user_message = asyncio.run(get_from_queue())
        assert user_message == {"type": "user_input", "content": "Hello from client"}

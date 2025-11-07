
import pytest
import pytest_asyncio
import httpx
from httpx import AsyncClient
from fastapi import FastAPI

# Placeholder for the app factory which we will create later
def create_app() -> FastAPI:
    # This will eventually import and return our main FastAPI app
    # For now, return a dummy app to allow tests to be written
    from src.daip_live.p7_gui.main import app
    return app

import pytest_asyncio

@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Create an async test client for the FastAPI app."""
    app = create_app()
    # Use ASGITransport for compatibility with the project's httpx version
    transport = httpx.ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_session_success(client: AsyncClient):
    """
    Test case for successfully creating a new session.
    It should return a 200 OK status and a JSON body with a 'session_id'.
    """
    response = await client.post("/api/sessions", json={"goal": "Test session goal"})

    assert response.status_code == 200

    response_data = response.json()
    assert "session_id" in response_data
    assert isinstance(response_data["session_id"], str)

@pytest.mark.asyncio
async def test_get_session_success(client: AsyncClient):
    """
    Test case for successfully retrieving an existing session.
    RED phase: This test should fail because the endpoint doesn't exist yet.
    """
    # First create a session
    create_response = await client.post("/api/sessions", json={"goal": "Test session for get"})
    assert create_response.status_code == 200
    session_data = create_response.json()
    session_id = session_data["session_id"]

    # Then try to get it
    response = await client.get(f"/api/sessions/{session_id}")

    # This should pass once we implement the endpoint
    assert response.status_code == 200
    retrieved_data = response.json()
    assert retrieved_data["session_id"] == session_id
    assert retrieved_data["goal"] == "Test session for get"

@pytest.mark.asyncio
async def test_get_nonexistent_session(client: AsyncClient):
    """
    Test case for retrieving a non-existent session.
    Should return 404 Not Found.
    """
    fake_session_id = "nonexistent-session-id"
    response = await client.get(f"/api/sessions/{fake_session_id}")

    # Should return 404 once we implement proper error handling
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_sessions_success(client: AsyncClient):
    """
    Test case for listing all sessions.
    Should return a list of sessions.
    """
    # Create a few sessions first
    await client.post("/api/sessions", json={"goal": "Test session 1"})
    await client.post("/api/sessions", json={"goal": "Test session 2"})

    response = await client.get("/api/sessions")

    assert response.status_code == 200
    sessions = response.json()
    assert isinstance(sessions, list)
    assert len(sessions) >= 2  # At least the two we created

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """
    Test case for system health check endpoint.
    GREEN phase: This test should pass as we've implemented the endpoint.
    """
    response = await client.get("/api/health")

    # This should pass once we implement the health endpoint
    assert response.status_code == 200
    health_data = response.json()
    assert "status" in health_data
    assert "timestamp" in health_data

@pytest.mark.asyncio
async def test_list_roles(client: AsyncClient):
    """
    Test case for listing available roles.
    RED phase: This test should fail because the endpoint doesn't exist yet.
    """
    response = await client.get("/api/roles")

    # This should pass once we implement the roles endpoint
    assert response.status_code == 200
    roles_data = response.json()
    assert isinstance(roles_data, list)
    # Should have at least some default roles
    assert len(roles_data) >= 0

@pytest.mark.asyncio
async def test_get_knowledge_status(client: AsyncClient):
    """
    Test case for getting knowledge base status.
    RED phase: This test should fail because the endpoint doesn't exist yet.
    """
    response = await client.get("/api/knowledge/status")

    # This should pass once we implement the knowledge status endpoint
    assert response.status_code == 200
    knowledge_data = response.json()
    assert "status" in knowledge_data
    assert "last_sync" in knowledge_data

@pytest.mark.asyncio
async def test_delete_session_success(client: AsyncClient):
    """
    Test case for successfully deleting a session.
    RED phase: This test should fail because we need to verify the delete endpoint works properly.
    """
    # First create a session
    create_response = await client.post("/api/sessions", json={"goal": "Test session for deletion"})
    assert create_response.status_code == 200
    session_data = create_response.json()
    session_id = session_data["session_id"]

    # Then delete it
    delete_response = await client.delete(f"/api/sessions/{session_id}")
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    assert "message" in delete_data

    # Verify it's actually deleted
    get_response = await client.get(f"/api/sessions/{session_id}")
    assert get_response.status_code == 404

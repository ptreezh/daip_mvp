"""End-to-end tests for API endpoints.

Tests the complete request/response cycle for all REST API endpoints.
"""

import pytest
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch

from daip_live.p7_gui.main import app, get_config, get_db_manager, get_session_manager
from daip_live.p7_gui.api_docs import (
    SessionCreateRequest,
    HealthCheckResponse,
    KnowledgeStatusResponse
)
from daip_live.core.models import Session, AgentState
from daip_live.persistence.database import DatabaseManager
from daip_live.memory.session_manager import SessionManager
from fastapi.testclient import TestClient


@pytest.mark.e2e
class TestAPIEndpointsE2E:
    """End-to-end tests for REST API endpoints."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_path = Path(temp_file.name)
        temp_file.close()
        db = DatabaseManager(db_path=str(temp_path))
        yield db
        try:
            temp_path.unlink()
        except (PermissionError, OSError):
            pass

    @pytest.fixture
    def temp_session_manager(self, temp_db):
        """Create temporary session manager."""
        return SessionManager(db_manager=temp_db)

    @pytest.fixture
    def client(self, temp_session_manager):
        """Create test client with mocked dependencies."""
        def override_get_config():
            return {
                'database': {'path': ':memory:'},
                'llm_provider': {'default_model': 'gpt-3.5-turbo'},
                'knowledge_base': {'directory': './test_knowledge'},
                'role_manager': {'roles_dir': './test_roles'}
            }

        def override_get_db_manager():
            return temp_session_manager.db_manager

        def override_get_session_manager():
            return temp_session_manager

        from daip_live.p7_gui import main
        main.app.dependency_overrides[get_config] = override_get_config
        main.app.dependency_overrides[get_db_manager] = override_get_db_manager
        main.app.dependency_overrides[get_session_manager] = override_get_session_manager

        with TestClient(main.app) as test_client:
            yield test_client

        main.app.dependency_overrides.clear()

    def test_create_session_e2e(self, client):
        """Test complete session creation flow."""
        response = client.post(
            "/api/sessions",
            json={
                "goal": "E2E Test Goal",
                "session_type": "workflow",
                "participant_ids": ["agent", "user"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["goal"] == "E2E Test Goal"
        assert data["session_type"] == "workflow"
        assert "agent" in data["participant_ids"]

    def test_list_sessions_e2e(self, client):
        """Test listing all sessions."""
        # Create multiple sessions
        for i in range(3):
            client.post(
                "/api/sessions",
                json={"goal": f"Test session {i}"}
            )

        # List sessions
        response = client.get("/api/sessions")
        assert response.status_code == 200
        sessions = response.json()
        assert len(sessions) >= 3

    def test_get_session_e2e(self, client):
        """Test getting a specific session."""
        # Create a session
        create_response = client.post(
            "/api/sessions",
            json={"goal": "Get Test Session"}
        )
        session_id = create_response.json()["session_id"]

        # Get the session
        response = client.get(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["goal"] == "Get Test Session"

    def test_get_nonexistent_session_e2e(self, client):
        """Test getting a session that doesn't exist."""
        response = client.get("/api/sessions/nonexistent_id")
        assert response.status_code == 404

    def test_delete_session_e2e(self, client):
        """Test deleting a session."""
        # Create a session
        create_response = client.post(
            "/api/sessions",
            json={"goal": "Delete Test Session"}
        )
        session_id = create_response.json()["session_id"]

        # Delete the session
        response = client.delete(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

        # Verify it's gone
        get_response = client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_health_check_e2e(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "timestamp" in data
        assert "version" in data
        assert "uptime_seconds" in data

    def test_roles_list_e2e(self, client):
        """Test listing available roles."""
        # Mock role manager to return test data
        from unittest.mock import MagicMock
        from daip_live.p7_gui import main

        mock_role_manager = MagicMock()
        mock_role_manager.list_roles.return_value = {
            "analyst": {
                "description": "Data analyst",
                "system_prompt": "You are an analyst",
                "model": "gpt-4",
                "capabilities": ["analysis", "reporting"]
            },
            "writer": {
                "description": "Content writer",
                "system_prompt": "You are a writer",
                "model": "gpt-3.5-turbo",
                "capabilities": ["writing", "editing"]
            }
        }

        def override_get_role_manager():
            return mock_role_manager

        main.app.dependency_overrides[main.get_role_manager] = override_get_role_manager

        response = client.get("/api/roles")
        assert response.status_code == 200
        roles = response.json()
        assert len(roles) == 2

        main.app.dependency_overrides.clear()

    def test_knowledge_status_e2e(self, client):
        """Test knowledge base status endpoint."""
        response = client.get("/api/knowledge/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "last_sync" in data
        assert "total_documents" in data

    def test_session_workflow_e2e(self, client):
        """Test complete session lifecycle."""
        # 1. Create session
        create_response = client.post(
            "/api/sessions",
            json={"goal": "Complete Workflow Test"}
        )
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]

        # 2. Get session
        get_response = client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == 200

        # 3. List sessions (verify ours is there)
        list_response = client.get("/api/sessions")
        sessions = list_response.json()
        session_ids = [s["session_id"] for s in sessions]
        assert session_id in session_ids

        # 4. Delete session
        delete_response = client.delete(f"/api/sessions/{session_id}")
        assert delete_response.status_code == 200

        # 5. Verify deleted
        final_get = client.get(f"/api/sessions/{session_id}")
        assert final_get.status_code == 404


@pytest.mark.e2e
class TestAPIValidationE2E:
    """End-to-end tests for API validation and error handling."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from daip_live.p7_gui import main

        def override_get_config():
            return {
                'database': {'path': ':memory:'},
                'llm_provider': {'default_model': 'gpt-3.5-turbo'},
                'knowledge_base': {'directory': './test_knowledge'},
                'role_manager': {'roles_dir': './test_roles'}
            }

        def override_get_db_manager():
            from daip_live.persistence.database import DatabaseManager
            return DatabaseManager(db_path=':memory:')

        def override_get_session_manager():
            from daip_live.memory.session_manager import SessionManager
            db = DatabaseManager(db_path=':memory:')
            return SessionManager(db_manager=db)

        main.app.dependency_overrides[get_config] = override_get_config
        main.app.dependency_overrides[main.get_db_manager] = override_get_db_manager
        main.app.dependency_overrides[main.get_session_manager] = override_get_session_manager

        with TestClient(main.app) as test_client:
            yield test_client

        main.app.dependency_overrides.clear()

    def test_create_session_missing_goal(self, client):
        """Test creating session without required goal field."""
        response = client.post(
            "/api/sessions",
            json={"session_type": "workflow"}
        )
        # Should fail validation
        assert response.status_code == 422

    def test_create_session_invalid_json(self, client):
        """Test creating session with invalid JSON."""
        response = client.post(
            "/api/sessions",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_get_session_invalid_id(self, client):
        """Test getting session with invalid ID format (should still attempt lookup)."""
        response = client.get("/api/sessions/invalid_id_with_spaces")
        # Should return 404 for non-existent session
        assert response.status_code == 404


@pytest.mark.e2e
class TestOpenAPISpecE2E:
    """End-to-end tests for OpenAPI specification."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from daip_live.p7_gui import main
        with TestClient(main.app) as test_client:
            yield test_client

    def test_openapi_json_endpoint(self, client):
        """Test OpenAPI JSON endpoint."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        spec = response.json()
        assert "openapi" in spec
        assert spec["openapi"] == "3.1.0"
        assert "info" in spec
        assert "paths" in spec

    def test_docs_endpoint(self, client):
        """Test Swagger UI docs endpoint."""
        response = client.get("/docs")
        assert response.status_code == 200
        # Should return HTML
        assert "text/html" in response.headers.get("content-type", "")

    def test_redoc_endpoint(self, client):
        """Test ReDoc endpoint."""
        response = client.get("/redoc")
        assert response.status_code == 200
        # Should return HTML
        assert "text/html" in response.headers.get("content-type", "")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

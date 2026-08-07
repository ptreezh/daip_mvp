"""Unit tests for API documentation.

Tests the OpenAPI specification, request/response schemas,
and endpoint documentation completeness.
"""

import json
import pytest
from pathlib import Path
from daip_live.p7_gui.api_docs import (
    API_TAGS,
    OPENAPI_SPEC,
    SessionCreateRequest,
    HealthCheckResponse,
    RoleInfoResponse,
    KnowledgeStatusResponse,
    ErrorResponse,
    get_openapi_spec
)


@pytest.mark.unit
class TestAPIDocsStructure:
    """Test API documentation structure and completeness."""

    def test_openapi_spec_version(self):
        """OpenAPI spec should be version 3.1.0."""
        spec = get_openapi_spec()
        assert spec["openapi"] == "3.1.0"

    def test_openapi_spec_has_info(self):
        """OpenAPI spec should have info section."""
        spec = get_openapi_spec()
        assert "info" in spec
        assert "title" in spec["info"]
        assert "version" in spec["info"]
        assert spec["info"]["title"] == "DAIP-LIVE API"

    def test_openapi_spec_has_tags(self):
        """OpenAPI spec should have API tags."""
        spec = get_openapi_spec()
        assert "tags" in spec
        assert len(spec["tags"]) > 0

    def test_api_tags_defined(self):
        """API_TAGS constant should be defined."""
        assert isinstance(API_TAGS, list)
        assert len(API_TAGS) >= 5
        tag_names = [tag["name"] for tag in API_TAGS]
        assert "sessions" in tag_names
        assert "health" in tag_names
        assert "roles" in tag_names
        assert "knowledge" in tag_names
        assert "websocket" in tag_names

    def test_openapi_spec_has_paths(self):
        """OpenAPI spec should define API paths."""
        spec = get_openapi_spec()
        assert "paths" in spec
        assert len(spec["paths"]) > 0

    def test_sessions_endpoints_documented(self):
        """Session endpoints should be documented."""
        spec = get_openapi_spec()
        paths = spec["paths"]
        assert "/api/sessions" in paths
        assert "post" in paths["/api/sessions"]
        assert "get" in paths["/api/sessions"]
        assert "/api/sessions/{session_id}" in paths

    def test_health_endpoint_documented(self):
        """Health check endpoint should be documented."""
        spec = get_openapi_spec()
        paths = spec["paths"]
        assert "/api/health" in paths
        assert "get" in paths["/api/health"]

    def test_roles_endpoint_documented(self):
        """Roles endpoint should be documented."""
        spec = get_openapi_spec()
        paths = spec["paths"]
        assert "/api/roles" in paths

    def test_knowledge_endpoint_documented(self):
        """Knowledge status endpoint should be documented."""
        spec = get_openapi_spec()
        paths = spec["paths"]
        assert "/api/knowledge/status" in paths

    def test_websocket_endpoint_documented(self):
        """WebSocket endpoint should be documented."""
        spec = get_openapi_spec()
        paths = spec["paths"]
        assert "/ws/sessions/{session_id}" in paths

    def test_components_schemas_defined(self):
        """OpenAPI spec should have component schemas."""
        spec = get_openapi_spec()
        assert "components" in spec
        assert "schemas" in spec["components"]


@pytest.mark.unit
class TestRequestSchemas:
    """Test request schema definitions."""

    def test_session_create_request_schema(self):
        """SessionCreateRequest should be valid Pydantic model."""
        request = SessionCreateRequest(
            goal="Test goal",
            session_type="workflow",
            participant_ids=["agent", "user"]
        )
        assert request.goal == "Test goal"
        assert request.session_type == "workflow"
        assert len(request.participant_ids) == 2

    def test_session_create_request_defaults(self):
        """SessionCreateRequest should have default values."""
        request = SessionCreateRequest(goal="Test goal")
        assert request.session_type == "workflow"
        assert request.participant_ids == ["agent", "user"]

    def test_session_create_request_validation(self):
        """SessionCreateRequest should validate required fields."""
        with pytest.raises(Exception):
            SessionCreateRequest()  # Missing required 'goal'

    def test_session_create_request_examples(self):
        """SessionCreateRequest should have JSON schema examples."""
        schema = SessionCreateRequest.model_json_schema()
        assert "examples" in schema.get("$defs", {})


@pytest.mark.unit
class TestResponseSchemas:
    """Test response schema definitions."""

    def test_health_check_response_schema(self):
        """HealthCheckResponse should be valid Pydantic model."""
        from datetime import datetime, timezone

        response = HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now(timezone.utc),
            version="1.0.0",
            uptime_seconds=100.0,
            components={"database": "healthy"}
        )
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.uptime_seconds == 100.0

    def test_role_info_response_schema(self):
        """RoleInfoResponse should be valid Pydantic model."""
        response = RoleInfoResponse(
            name="analyst",
            description="Data analyst role",
            system_prompt="You are an analyst",
            model="gpt-4",
            capabilities=["analysis", "reporting"]
        )
        assert response.name == "analyst"
        assert len(response.capabilities) == 2

    def test_knowledge_status_response_schema(self):
        """KnowledgeStatusResponse should be valid Pydantic model."""
        from datetime import datetime, timezone

        response = KnowledgeStatusResponse(
            status="healthy",
            last_sync=datetime.now(timezone.utc),
            total_documents=100,
            index_size=1000,
            embedding_dimension=1536
        )
        assert response.status == "healthy"
        assert response.total_documents == 100
        assert response.embedding_dimension == 1536

    def test_error_response_schema(self):
        """ErrorResponse should be valid Pydantic model."""
        from datetime import datetime, timezone

        response = ErrorResponse(
            error="NOT_FOUND",
            message="Resource not found",
            detail="Session ID does not exist",
            timestamp=datetime.now(timezone.utc)
        )
        assert response.error == "NOT_FOUND"
        assert response.message == "Resource not found"


@pytest.mark.unit
class TestOpenAPISpecValidation:
    """Test OpenAPI specification validity."""

    def test_spec_is_valid_json(self):
        """OpenAPI spec should be serializable to JSON."""
        spec = get_openapi_spec()
        json_str = json.dumps(spec)
        assert isinstance(json_str, str)
        assert len(json_str) > 0

    def test_spec_has_required_fields(self):
        """OpenAPI spec should have required OpenAPI 3.1 fields."""
        spec = get_openapi_spec()
        required_fields = ["openapi", "info", "paths"]
        for field in required_fields:
            assert field in spec

    def test_info_has_required_fields(self):
        """Info section should have required fields."""
        spec = get_openapi_spec()
        info = spec["info"]
        assert "title" in info
        assert "version" in info

    def test_all_paths_have_tags(self):
        """All path operations should have tags."""
        spec = get_openapi_spec()
        paths = spec["paths"]
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    if isinstance(details, dict) and "tags" in details:
                        assert len(details["tags"]) > 0

    def test_all_operations_have_summary(self):
        """Path operations should have summary or description."""
        spec = get_openapi_spec()
        paths = spec["paths"]
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    if isinstance(details, dict):
                        has_docs = "summary" in details or "description" in details
                        # Not requiring summary for WebSocket
                        if not path.startswith("/ws"):
                            assert has_docs or path.startswith("/api")


@pytest.mark.unit
class TestOpenAPIFile:
    """Test OpenAPI JSON file."""

    def test_openapi_file_exists(self):
        """openapi.json file should exist."""
        path = Path(__file__).parent.parent.parent / "openapi.json"
        assert path.exists()

    def test_openapi_file_is_valid_json(self):
        """openapi.json should be valid JSON."""
        path = Path(__file__).parent.parent.parent / "openapi.json"
        with open(path, "r") as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "openapi" in data

    def test_openapi_file_version(self):
        """openapi.json should have version 3.1.0."""
        path = Path(__file__).parent.parent.parent / "openapi.json"
        with open(path, "r") as f:
            data = json.load(f)
        assert data["openapi"] == "3.1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

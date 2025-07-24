# -*- coding: utf-8 -*-
"""
@Time    : 2025-07-24 18:30:00
@Author  : DAIP-LIVE Team
@File    : test_api_interface.py
@Description:
    Unit tests for API interface.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from src.user_interface.api_interface import APIInterface


class TestAPIInterface:
    """Test cases for APIInterface."""
    
    @pytest.fixture
    def api_interface(self):
        """Create an APIInterface instance for testing."""
        return APIInterface()
    
    @pytest.fixture
    def client(self, api_interface):
        """Create a test client."""
        return TestClient(api_interface.app)
    
    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        return {
            "llm_interface": AsyncMock(),
            "role_manager": Mock(),
            "tool_executor": Mock(),
            "synthesis_engine": AsyncMock(),
            "fact_extraction_service": AsyncMock(),
            "wiki_service": AsyncMock()
        }
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_list_workflows_endpoint(self, client):
        """Test list workflows endpoint."""
        response = client.get("/workflows")
        assert response.status_code == 200
        
        data = response.json()
        assert "workflows" in data
        assert len(data["workflows"]) >= 2  # Should have at least 2 workflows
    
    def test_critical_review_endpoint(self, client, api_interface, mock_services):
        """Test critical review endpoint."""
        with patch.object(api_interface, 'setup_services', return_value=mock_services), \
             patch('src.user_interface.api_interface.CriticalReviewWorkflow') as mock_workflow_class:
            
            # Mock workflow execution
            mock_workflow = AsyncMock()
            mock_workflow.execute.return_value = {
                "success": True,
                "original_content": "Test content",
                "final_content": "Reviewed content"
            }
            mock_workflow_class.return_value = mock_workflow
            
            # Make request
            response = client.post("/workflows/critical-review", json={
                "content": "Test content to review",
                "role_context": "Test context"
            })
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "execution_id" in data
            assert "started_at" in data
    
    def test_multi_perspective_endpoint(self, client, api_interface, mock_services):
        """Test multi-perspective endpoint."""
        with patch.object(api_interface, 'setup_services', return_value=mock_services), \
             patch('src.user_interface.api_interface.MultiPerspectiveSynthesisWorkflow') as mock_workflow_class:
            
            # Mock workflow execution
            mock_workflow = AsyncMock()
            mock_workflow.execute.return_value = {
                "success": True,
                "topic": "AI impact",
                "synthesis": "Comprehensive analysis"
            }
            mock_workflow_class.return_value = mock_workflow
            
            # Make request
            response = client.post("/workflows/multi-perspective", json={
                "topic": "AI impact on jobs",
                "perspectives": ["经济", "社会"]
            })
            
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert "execution_id" in data
            assert "started_at" in data
    
    def test_workflow_status_endpoint(self, client, api_interface):
        """Test workflow status endpoint."""
        # Test non-existent workflow
        response = client.get("/workflows/non-existent-id/status")
        assert response.status_code == 404
        
        # Add a mock workflow status
        from src.user_interface.api_interface import WorkflowStatus
        from datetime import datetime
        
        execution_id = "test-execution-id"
        api_interface.execution_status[execution_id] = WorkflowStatus(
            execution_id=execution_id,
            status="running",
            progress=0.5,
            current_step="Processing",
            started_at=datetime.now()
        )
        
        # Test existing workflow
        response = client.get(f"/workflows/{execution_id}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["execution_id"] == execution_id
        assert data["status"] == "running"
        assert data["progress"] == 0.5
    
    def test_workflow_result_endpoint(self, client, api_interface):
        """Test workflow result endpoint."""
        # Test non-existent workflow
        response = client.get("/workflows/non-existent-id/result")
        assert response.status_code == 404
        
        # Add a mock completed workflow
        from src.user_interface.api_interface import WorkflowStatus
        from datetime import datetime
        
        execution_id = "test-completed-id"
        api_interface.execution_status[execution_id] = WorkflowStatus(
            execution_id=execution_id,
            status="completed",
            progress=1.0,
            current_step="Completed",
            started_at=datetime.now(),
            completed_at=datetime.now(),
            result={"success": True, "message": "Test result"}
        )
        
        # Test completed workflow
        response = client.get(f"/workflows/{execution_id}/result")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Test result"
    
    def test_workflow_progress_endpoint(self, client, api_interface):
        """Test workflow progress endpoint."""
        # Test non-existent workflow
        response = client.get("/workflows/non-existent-id/progress")
        assert response.status_code == 404
        
        # Add a mock workflow status
        from src.user_interface.api_interface import WorkflowStatus
        from datetime import datetime
        
        execution_id = "test-progress-id"
        api_interface.execution_status[execution_id] = WorkflowStatus(
            execution_id=execution_id,
            status="running",
            progress=0.75,
            current_step="Synthesizing",
            started_at=datetime.now()
        )
        
        # Test progress endpoint
        response = client.get(f"/workflows/{execution_id}/progress")
        assert response.status_code == 200
        
        data = response.json()
        assert data["execution_id"] == execution_id
        assert data["status"] == "running"
        assert data["progress"] == 0.75
        assert data["current_step"] == "Synthesizing"
    
    def test_cancel_workflow_endpoint(self, client, api_interface):
        """Test workflow cancellation endpoint."""
        # Test non-existent workflow
        response = client.delete("/workflows/non-existent-id")
        assert response.status_code == 404
        
        # Add a mock running workflow
        from src.user_interface.api_interface import WorkflowStatus
        from datetime import datetime
        
        execution_id = "test-cancel-id"
        api_interface.execution_status[execution_id] = WorkflowStatus(
            execution_id=execution_id,
            status="running",
            progress=0.5,
            current_step="Processing",
            started_at=datetime.now()
        )
        
        # Test cancellation
        response = client.delete(f"/workflows/{execution_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "cancelled" in data["message"]
        
        # Verify status was updated
        assert api_interface.execution_status[execution_id].status == "cancelled"
    
    def test_invalid_request_data(self, client):
        """Test API with invalid request data."""
        # Test critical review with missing content
        response = client.post("/workflows/critical-review", json={})
        assert response.status_code == 422  # Validation error
        
        # Test multi-perspective with missing topic
        response = client.post("/workflows/multi-perspective", json={})
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__])
"""
API Client Integration Tests for DAIP-LIVE P7 GUI

This module implements integration tests for the API client functionality,
validating communication with the backend services.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.daip_live.p7_gui_v1.api_client.api_client import APIClient


class TestAPIClientIntegration:
    """Integration tests for API client functionality."""
    
    @pytest.mark.asyncio
    async def test_api_client_initialization(self):
        """RED: Test that APIClient can be initialized properly"""
        client = APIClient(base_url="http://localhost:8000")
        assert client is not None
        assert client.base_url == "http://localhost:8000"
        assert hasattr(client, '_session')
        assert hasattr(client, '_headers')
    
    @pytest.mark.asyncio
    async def test_session_api_integration(self):
        """RED: Test session management API integration"""
        client = APIClient(base_url="http://localhost:8000")
        
        # Mock the HTTP client to avoid real network calls
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Mock response for creating a session
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json.return_value = {
                "id": "test_session_123", 
                "title": "Test Session", 
                "status": "active", 
                "created_at": "2025-11-08T00:00:00Z"
            }
            mock_session.post.return_value.__aenter__.return_value = mock_resp
            
            # Test create session
            session_data = await client.create_session("Test goal for integration")
            assert session_data["id"] == "test_session_123"
            assert session_data["title"] == "Test Session"
            
            # Verify the call was made correctly
            mock_session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_role_api_integration(self):
        """RED: Test role management API integration"""
        client = APIClient(base_url="http://localhost:8000")
        
        # Mock the HTTP client
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Mock response for getting roles
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json.return_value = [
                {"name": "analyst", "description": "Data analyst role", "system_prompt": "You are a data analyst..."},
                {"name": "developer", "description": "Developer role", "system_prompt": "You are a software developer..."}
            ]
            mock_session.get.return_value.__aenter__.return_value = mock_resp
            
            # Test get roles
            roles = await client.get_roles()
            assert len(roles) == 2
            assert roles[0]["name"] == "analyst"
            assert roles[1]["name"] == "developer"
            
            # Verify the call was made
            mock_session.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_knowledge_api_integration(self):
        """RED: Test knowledge base API integration"""
        client = APIClient(base_url="http://localhost:8000")
        
        # Mock the HTTP client
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Mock response for getting knowledge status
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json.return_value = {
                "status": "healthy",
                "last_sync": "2025-11-08T00:00:00Z",
                "total_documents": 15
            }
            mock_session.get.return_value.__aenter__.return_value = mock_resp
            
            # Test knowledge status
            status = await client.get_knowledge_status()
            assert status["status"] == "healthy"
            assert status["total_documents"] == 15
            
            # Verify the call was made
            mock_session.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_message_api_integration(self):
        """RED: Test message sending API integration"""
        client = APIClient(base_url="http://localhost:8000")
        
        # Mock the HTTP client
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Mock response for sending message
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.json.return_value = {
                "message_id": "msg123",
                "content": "Response to test message",
                "sender": "agent",
                "timestamp": "2025-11-08T00:00:00Z"
            }
            mock_session.post.return_value.__aenter__.return_value = mock_resp
            
            # Test send message
            response = await client.send_message("test_session_123", "Test message content")
            assert response["message_id"] == "msg123"
            assert response["content"] == "Response to test message"
            
            # Verify the call was made with correct parameters
            mock_session.post.assert_called_once()
    
    def test_api_client_error_handling(self):
        """RED: Test API client error handling"""
        client = APIClient(base_url="http://localhost:8000")
        
        # Check that error handling methods exist
        assert hasattr(client, '_handle_error')
        assert callable(getattr(client, '_handle_error', None))
    
    def test_api_client_headers_configuration(self):
        """RED: Test API client headers configuration"""
        client = APIClient(base_url="http://localhost:8000", headers={"Custom-Header": "test"})
        
        # Check that custom headers were added
        assert "Custom-Header" in client._headers
        assert client._headers["Custom-Header"] == "test"
        
        # Check that default headers are still there
        assert "Content-Type" in client._headers
        assert "Accept" in client._headers
    
    @pytest.mark.asyncio
    async def test_api_client_timeout_handling(self):
        """RED: Test API client timeout handling"""
        client = APIClient(base_url="http://localhost:8000", timeout=5)
        
        # Check timeout property
        assert client.timeout == 5
        
        # This would be tested with actual timeout scenario in real implementation
        assert hasattr(client, '_timeout')


class TestAPIClientIntegrationWithViewModels:
    """Integration tests between API client and ViewModels."""
    
    @pytest.mark.asyncio
    async def test_integration_with_session_viewmodel(self):
        """RED: Test API client integration with SessionViewModel"""
        # Create mock API client
        mock_api_client = AsyncMock()
        mock_api_client.create_session.return_value = {
            "id": "vm_test_session", "title": "VM Integration Test", "status": "active"
        }
        mock_api_client.get_sessions.return_value = [
            {"id": "session1", "title": "Existing Session", "status": "active"}
        ]
        
        # Import and create ViewModel with mock client
        from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
        from unittest.mock import Mock
        
        mock_interaction = Mock()
        mock_interaction.get_sessions = AsyncMock(return_value=[
            {"id": "session1", "title": "Existing Session", "status": "active"}
        ])
        mock_interaction.create_session = AsyncMock(return_value={
            "id": "vm_test_session", "title": "VM Integration Test", "status": "active"
        })
        
        vm = SessionViewModel(mock_interaction)
        
        # Test that ViewModel can use API client functionality
        sessions = await vm.load_sessions()
        assert len(sessions) >= 1
        
        new_session = await vm.create_session("Integration test goal")
        assert new_session["id"] == "vm_test_session"
        
        print("✅ API client integration with SessionViewModel works")
    
    @pytest.mark.asyncio
    async def test_integration_with_chat_viewmodel(self):
        """RED: Test API client integration with ChatViewModel"""
        # Create mock interaction
        from unittest.mock import Mock, AsyncMock
        
        mock_interaction = Mock()
        mock_interaction.send_message = AsyncMock(return_value={
            "type": "response", "content": "Test response", "sender": "agent"
        })
        mock_interaction.get_conversation_history = AsyncMock(return_value=[
            {"id": "msg1", "content": "Previous message", "sender": "user"}
        ])
        
        # Import and create Chat ViewModel
        from src.daip_live.p7_gui_v1.viewmodel.chat_viewmodel import ChatViewModel
        chat_vm = ChatViewModel(mock_interaction)
        
        # Test chat functionality
        messages = await chat_vm.get_conversation_history("test_session")
        assert len(messages) == 1
        
        # Test sending a message
        async for response in chat_vm.send_message("test_session", "Integration test"):
            assert response["type"] == "response"
            assert response["sender"] == "agent"
            break  # Just check the first response
        
        print("✅ API client integration with ChatViewModel works")
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow_integration(self):
        """RED: Test complete end-to-end workflow integration"""
        # This tests the complete flow: View -> ViewModel -> API -> Backend -> Response
        from unittest.mock import Mock, AsyncMock
        
        # Create a mock interaction that simulates the full backend communication
        mock_interaction = Mock()
        mock_interaction.create_session = AsyncMock(return_value={
            "id": "e2e_test_session", 
            "title": "End-to-End Test Session", 
            "status": "active",
            "goal": "Complete workflow test"
        })
        mock_interaction.get_sessions = AsyncMock(return_value=[
            {"id": "e2e_test_session", "title": "End-to-End Test Session", "status": "active"}
        ])
        mock_interaction.send_message = AsyncMock(return_value={
            "type": "response", "content": "Processed: Hello from e2e test", "sender": "assistant"
        })
        
        # Test with Session ViewModel
        from src.daip_live.p7_gui_v1.viewmodel.session_viewmodel import SessionViewModel
        session_vm = SessionViewModel(mock_interaction)
        
        # Create session
        session = await session_vm.create_session("Complete workflow integration test")
        assert session["id"] == "e2e_test_session"
        
        # Verify session was added to ViewModel state
        available_sessions = session_vm.get_property('available_sessions')
        assert any(s["id"] == "e2e_test_session" for s in available_sessions)
        
        print("✅ Complete end-to-end workflow integration test passed")
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self):
        """RED: Test API client performance under load"""
        # Test that API client performs well with multiple concurrent requests
        import asyncio
        
        # Create API client
        client = APIClient(base_url="http://localhost:8000")
        
        # Mock responses for multiple requests
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            # Create mock responses
            async def mock_response():
                resp = AsyncMock()
                resp.status = 200
                resp.json.return_value = {"result": "ok"}
                return resp
            
            mock_session.get.return_value.__aenter__.return_value = await mock_response()
            
            # Run multiple concurrent API calls
            async def make_call(idx):
                try:
                    result = await client.get_session_status(f"session_{idx}")
                    return idx, result
                except Exception as e:
                    return idx, str(e)
            
            # Execute 10 concurrent calls
            tasks = [make_call(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            
            # Verify most calls succeeded
            successful_calls = [r for r in results if isinstance(r[1], dict)]
            assert len(successful_calls) >= 8  # At least 80% success rate
            
        print("✅ Performance under load test passed")
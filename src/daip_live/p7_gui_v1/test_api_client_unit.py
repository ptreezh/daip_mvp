import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from src.daip_live.p7_gui_v1.api_client.base import APIClient


class TestAPIClient:
    """TDD for API Client functionality"""
    
    def test_api_client_initialization(self):
        """RED: Test that APIClient can be initialized"""
        client = APIClient(base_url="http://localhost:8000")
        assert client is not None
        assert client.base_url == "http://localhost:8000"
        assert client.timeout == 30  # Should be integer, not ClientTimeout object
    
    def test_api_client_custom_timeout(self):
        """RED: Test APIClient with custom timeout"""
        client = APIClient(base_url="http://localhost:8000", timeout=60)
        assert client.timeout == 60
    
    @pytest.mark.asyncio
    async def test_api_client_make_request_success(self):
        """RED: Test internal _make_request method with mocked response"""
        # Create a mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        
        # Create an async context manager mock for the session.request
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_response
        
        # Create a mock session
        mock_session = AsyncMock()
        mock_session.request.return_value = mock_context_manager
        
        # Create client and use patch to mock _get_session
        client = APIClient(base_url="http://localhost:8000")
        
        with patch.object(client, '_get_session', return_value=mock_session):
            # Call the internal method
            result = await client._make_request('GET', '/test')
        
        assert result.status == 200
        assert result.data == {"data": "test"}
        # Verify the request was made
        mock_session.request.assert_called_once_with(
            method='GET',
            url='http://localhost:8000/test',
            json=None,
            params=None
        )
    
    @pytest.mark.asyncio
    async def test_api_client_get_method(self):
        """RED: Test GET method with mocked response"""
        # Create a mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        
        # Create an async context manager mock
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_response
        
        # Create a mock session
        mock_session = AsyncMock()
        mock_session.request.return_value = mock_context_manager
        
        # Create client and use patch to mock _get_session
        client = APIClient(base_url="http://localhost:8000")
        
        with patch.object(client, '_get_session', return_value=mock_session):
            # Call the get method
            result = await client.get('/test')
        
        assert result == {"data": "test"}
        # Verify the request was made with correct parameters
        mock_session.request.assert_called_once_with(
            method='GET',
            url='http://localhost:8000/test',
            json=None,
            params=None
        )
    
    @pytest.mark.asyncio
    async def test_api_client_post_method(self):
        """RED: Test POST method with mocked response"""
        # Create a mock response
        data_to_send = {"name": "test"}
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.text.return_value = '{"result": "created"}'
        mock_response.json.return_value = {"result": "created"}
        
        # Create an async context manager mock
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_response
        
        # Create a mock session
        mock_session = AsyncMock()
        mock_session.request.return_value = mock_context_manager
        
        # Create client and use patch to mock _get_session
        client = APIClient(base_url="http://localhost:8000")
        
        with patch.object(client, '_get_session', return_value=mock_session):
            # Call the post method
            result = await client.post('/test', data_to_send)
        
        assert result == {"result": "created"}
        # Verify the request was made with correct parameters
        mock_session.request.assert_called_once_with(
            method='POST',
            url='http://localhost:8000/test',
            json=data_to_send,
            params=None
        )
    
    @pytest.mark.asyncio
    async def test_api_client_handles_error_response(self):
        """RED: Test that API client properly handles error responses"""
        # Create a mock response with error status
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.text.return_value = '{"error": "Not found"}'
        mock_response.json.return_value = {"error": "Not found"}
        
        # Create an async context manager mock
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__.return_value = mock_response
        
        # Create a mock session
        mock_session = AsyncMock()
        mock_session.request.return_value = mock_context_manager
        
        # Create client and use patch to mock _get_session
        client = APIClient(base_url="http://localhost:8000")
        
        with patch.object(client, '_get_session', return_value=mock_session):
            # Call the get method and expect an exception
            with pytest.raises(Exception, match="GET request failed with status 404"):
                await client.get('/nonexistent')
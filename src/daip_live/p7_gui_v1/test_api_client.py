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
        assert client.timeout == 30
    
    def test_api_client_custom_timeout(self):
        """RED: Test APIClient with custom timeout"""
        client = APIClient(base_url="http://localhost:8000", timeout=60)
        assert client.timeout == 60
    
    @pytest.mark.asyncio
    async def test_api_client_get_request(self):
        """RED: Test GET request functionality"""
        with patch('aiohttp.ClientSession.get') as mock_get:
                    # Create a mock response
                    mock_response = AsyncMock()
                    mock_response.status = 200
                    mock_response.json = AsyncMock(return_value={"data": "test"})
                    mock_response.text = AsyncMock(return_value='{"data": "test"}')
                    
                    mock_get.return_value.__aenter__.return_value = mock_response
                    
                    client = APIClient(base_url="http://localhost:8000")
                    result = await client.get("/test")
                    
                    assert result == {"data": "test"}
                    mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_client_post_request(self):
        """RED: Test POST request functionality"""
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Create a mock response
            mock_response = AsyncMock()
            mock_response.status = 201
            mock_response.json = AsyncMock(return_value={"result": "created"})
            mock_response.text = AsyncMock(return_value='{"result": "created"}')
            
            mock_post.return_value.__aenter__.return_value = mock_response
            
            client = APIClient(base_url="http://localhost:8000")
            result = await client.post("/test", {"name": "test"})
            
            assert result == {"result": "created"}
            mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_client_put_request(self):
        """RED: Test PUT request functionality"""
        with patch('aiohttp.ClientSession.put') as mock_put:
            # Create a mock response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"result": "updated"})
            
            mock_put.return_value.__aenter__.return_value = mock_response
            
            client = APIClient(base_url="http://localhost:8000")
            result = await client.put("/test/1", {"name": "updated"})
            
            assert result == {"result": "updated"}
            mock_put.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_client_delete_request(self):
        """RED: Test DELETE request functionality"""
        with patch('aiohttp.ClientSession.delete') as mock_delete:
            # Create a mock response
            mock_response = AsyncMock()
            mock_response.status = 204  # No content
            mock_response.json = AsyncMock(return_value={})
            
            mock_delete.return_value.__aenter__.return_value = mock_response
            
            client = APIClient(base_url="http://localhost:8000")
            result = await client.delete("/test/1")
            
            assert result == {}
            mock_delete.assert_called_once()
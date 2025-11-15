"""
API Client for FastAPI Backend Integration

This module provides an API client to communicate with the existing
FastAPI backend services.
"""

import asyncio
import aiohttp
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class APIResponse:
    """
    Represents an API response with status and data.
    """
    status: int
    data: Any
    headers: Dict[str, str]
    url: str


class APIClient:
    """
    API Client for communicating with the FastAPI backend.
    
    This client handles all HTTP requests to the backend API endpoints.
    """
    
    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout  # Store as integer for easy access
        self._timeout_obj = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create an HTTP session.
        
        Returns:
            HTTP client session
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout_obj,
                headers=self._headers
            )
        return self._session
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> APIResponse:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data for POST/PUT
            params: Query parameters
            
        Returns:
            APIResponse object
        """
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                # Read response content
                response_text = await response.text()
                
                # Try to parse JSON, fallback to empty dict
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {"raw_response": response_text}
                
                api_response = APIResponse(
                    status=response.status,
                    data=response_data,
                    headers=dict(response.headers),
                    url=str(response.url)
                )
                
                return api_response
                
        except asyncio.TimeoutError:
            raise TimeoutError(f"Request to {url} timed out after {self.timeout} seconds")
        except aiohttp.ClientError as e:
            raise ConnectionError(f"API request failed: {str(e)}")
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Make a GET request to the API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data
        """
        response = await self._make_request('GET', endpoint, params=params)
        
        if response.status >= 400:
            raise Exception(f"GET request failed with status {response.status}: {response.data}")
        
        return response.data
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """
        Make a POST request to the API.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
        """
        response = await self._make_request('POST', endpoint, data=data)
        
        if response.status >= 400:
            raise Exception(f"POST request failed with status {response.status}: {response.data}")
        
        return response.data
    
    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Any:
        """
        Make a PUT request to the API.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
        """
        response = await self._make_request('PUT', endpoint, data=data)
        
        if response.status >= 400:
            raise Exception(f"PUT request failed with status {response.status}: {response.data}")
        
        return response.data
    
    async def delete(self, endpoint: str) -> Any:
        """
        Make a DELETE request to the API.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Response data
        """
        response = await self._make_request('DELETE', endpoint)
        
        # DELETE requests typically return 204 No Content, which is OK
        if response.status >= 400 and response.status != 404:
            raise Exception(f"DELETE request failed with status {response.status}: {response.data}")
        
        return response.data
    
    def set_auth_token(self, token: str):
        """
        Set authentication token for requests.
        
        Args:
            token: Authentication token
        """
        self._headers['Authorization'] = f'Bearer {token}'
    
    def set_header(self, name: str, value: str):
        """
        Set a custom header.
        
        Args:
            name: Header name
            value: Header value
        """
        self._headers[name] = value


class SessionAPIClient:
    """
    Client for session-related API endpoints.
    """
    
    def __init__(self, api_client: APIClient):
        """
        Initialize the session client.
        
        Args:
            api_client: Base API client to use
        """
        self.client = api_client
    
    async def create_session(self, goal: str) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            goal: Goal for the session
            
        Returns:
            Created session data
        """
        return await self.client.post("/api/sessions", {"goal": goal})
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions.
        
        Returns:
            List of session data
        """
        return await self.client.get("/api/sessions")
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get a specific session.
        
        Args:
            session_id: ID of the session
            
        Returns:
            Session data
        """
        return await self.client.get(f"/api/sessions/{session_id}")
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            await self.client.delete(f"/api/sessions/{session_id}")
            return True
        except Exception:
            return False


class RoleAPIClient:
    """
    Client for role-related API endpoints.
    """
    
    def __init__(self, api_client: APIClient):
        """
        Initialize the role client.
        
        Args:
            api_client: Base API client to use
        """
        self.client = api_client
    
    async def list_roles(self) -> List[Dict[str, Any]]:
        """
        List all available roles.
        
        Returns:
            List of role data
        """
        return await self.client.get("/api/roles")


class KnowledgeAPIClient:
    """
    Client for knowledge-related API endpoints.
    """
    
    def __init__(self, api_client: APIClient):
        """
        Initialize the knowledge client.
        
        Args:
            api_client: Base API client to use
        """
        self.client = api_client
    
    async def get_knowledge_status(self) -> Dict[str, Any]:
        """
        Get knowledge base status.
        
        Returns:
            Knowledge status data
        """
        return await self.client.get("/api/knowledge/status")
"""
Interaction Layer for P7 GUI Application

This module defines the abstract interface for interaction between 
the GUI and backend services, following the Dependency Inversion Principle.
"""

import asyncio
from typing import Any, Dict, List, Optional, AsyncGenerator
from abc import ABC, abstractmethod
from ..api_client import APIClient, SessionAPIClient, RoleAPIClient, KnowledgeAPIClient


class InteractionLayer(ABC):
    """
    Abstract interface for interaction between GUI and backend services.
    
    This layer abstracts the communication with backend services,
    allowing the GUI to work with different backend implementations.
    """
    
    @abstractmethod
    async def send_message(self, session_id: str, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a message to a session and receive real-time responses.
        
        Args:
            session_id: ID of the session
            message: Message content to send
            
        Yields:
            Response events from the backend
        """
        pass
    
    @abstractmethod
    async def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Get list of available sessions.
        
        Returns:
            List of session data
        """
        pass
    
    @abstractmethod
    async def create_session(self, goal: str) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            goal: Goal for the new session
            
        Returns:
            Created session data
        """
        pass
    
    @abstractmethod
    async def get_roles(self) -> List[Dict[str, Any]]:
        """
        Get list of available roles.
        
        Returns:
            List of role data
        """
        pass
    
    @abstractmethod
    async def get_knowledge_status(self) -> Dict[str, Any]:
        """
        Get knowledge base status.
        
        Returns:
            Knowledge status data
        """
        pass
    
    @abstractmethod
    async def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """
        Search knowledge base.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        pass


class FastAPIInteractionAdapter(InteractionLayer):
    """
    Concrete implementation of InteractionLayer for FastAPI backend.
    
    This adapter connects the GUI to the existing FastAPI backend services.
    """
    
    def __init__(self, base_url: str):
        """
        Initialize the FastAPI interaction adapter.
        
        Args:
            base_url: Base URL of the FastAPI backend
        """
        self.base_url = base_url
        self._api_client: Optional[APIClient] = None
        self._session_client: Optional[SessionAPIClient] = None
        self._role_client: Optional[RoleAPIClient] = None
        self._knowledge_client: Optional[KnowledgeAPIClient] = None
    
    async def _ensure_clients(self):
        """Ensure API clients are initialized."""
        if self._api_client is None:
            self._api_client = APIClient(self.base_url)
            self._session_client = SessionAPIClient(self._api_client)
            self._role_client = RoleAPIClient(self._api_client)
            self._knowledge_client = KnowledgeAPIClient(self._api_client)
    
    async def send_message(self, session_id: str, message: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Send a message to a session and receive real-time responses via WebSocket.
        
        Args:
            session_id: ID of the session
            message: Message content to send
            
        Yields:
            Response events from the backend
        """
        await self._ensure_clients()
        
        # In a real implementation, this would use WebSocket
        # For now, we'll simulate by making an API call
        # This is a simplified version - in practice, you'd use WebSocket for real-time updates
        try:
            # This would actually be: await self._websocket_client.send_message(session_id, message)
            # For now, we'll return a simulated response
            yield {
                "type": "message_response",
                "content": f"Echo: {message}",
                "timestamp": asyncio.get_event_loop().time(),
                "session_id": session_id
            }
        except Exception as e:
            yield {
                "type": "error",
                "message": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def get_sessions(self) -> List[Dict[str, Any]]:
        """
        Get list of available sessions from the backend.
        
        Returns:
            List of session data
        """
        await self._ensure_clients()
        return await self._session_client.list_sessions()
    
    async def create_session(self, goal: str) -> Dict[str, Any]:
        """
        Create a new session via the backend API.
        
        Args:
            goal: Goal for the new session
            
        Returns:
            Created session data
        """
        await self._ensure_clients()
        return await self._session_client.create_session(goal)
    
    async def get_roles(self) -> List[Dict[str, Any]]:
        """
        Get list of available roles from the backend.
        
        Returns:
            List of role data
        """
        await self._ensure_clients()
        return await self._role_client.list_roles()
    
    async def get_knowledge_status(self) -> Dict[str, Any]:
        """
        Get knowledge base status from the backend.
        
        Returns:
            Knowledge status data
        """
        await self._ensure_clients()
        return await self._knowledge_client.get_knowledge_status()
    
    async def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """
        Search knowledge base via the backend API.
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        await self._ensure_clients()
        # In a real implementation, we would have a search endpoint
        # For now, we'll return empty results
        return []
    
    async def close(self):
        """
        Close the adapter and any open connections.
        """
        if self._api_client:
            await self._api_client.close()
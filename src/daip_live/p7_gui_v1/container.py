"""
Service Container for P7 GUI Application

This module provides a dependency injection container for the P7 GUI application.
It manages the lifecycle and dependencies of various services used in the application.
"""

from typing import Dict, Type, Any, Optional
from .viewmodel import ViewModel
from .api_client import APIClient, SessionAPIClient, RoleAPIClient, KnowledgeAPIClient


class ServiceContainer:
    """
    Dependency injection container for the P7 GUI application.
    
    This container manages the creation and lifecycle of services used throughout
    the application, following the dependency inversion principle.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the service container.
        
        Args:
            base_url: Base URL for the backend API
        """
        self.base_url = base_url
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, callable] = {}
        
        # Register default services
        self._register_default_services()
    
    def _register_default_services(self):
        """
        Register default services that are commonly used.
        """
        # API Client
        self.register_singleton("api_client", lambda: APIClient(self.base_url))
        self.register_singleton("session_client", 
                               lambda: SessionAPIClient(self.get_service("api_client")))
        self.register_singleton("role_client", 
                               lambda: RoleAPIClient(self.get_service("api_client")))
        self.register_singleton("knowledge_client", 
                               lambda: KnowledgeAPIClient(self.get_service("api_client")))
    
    def register_singleton(self, name: str, factory: callable):
        """
        Register a singleton service.
        
        Args:
            name: Service name
            factory: Callable that creates the service instance
        """
        self._factories[name] = factory
    
    def get_service(self, name: str) -> Any:
        """
        Get a service instance.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
        """
        if name not in self._singletons:
            if name in self._factories:
                self._singletons[name] = self._factories[name]()
            else:
                raise ValueError(f"Service '{name}' not registered")
        
        return self._singletons[name]
    
    def register_service(self, name: str, instance: Any):
        """
        Register an existing service instance.
        
        Args:
            name: Service name
            instance: Service instance
        """
        self._singletons[name] = instance
    
    def has_service(self, name: str) -> bool:
        """
        Check if a service is registered.
        
        Args:
            name: Service name
            
        Returns:
            True if service is registered, False otherwise
        """
        return name in self._factories or name in self._singletons
    
    def reset(self):
        """
        Reset the container, clearing all singleton instances.
        """
        self._singletons.clear()
    
    async def close(self):
        """
        Close the container and any services that need cleanup.
        """
        # Close API client if it has a close method
        if self.has_service("api_client"):
            api_client = self.get_service("api_client")
            if hasattr(api_client, 'close'):
                await api_client.close()


# Global container instance (optional, for convenience)
_container: Optional[ServiceContainer] = None


def get_global_container(base_url: str = "http://localhost:8000") -> ServiceContainer:
    """
    Get the global service container instance.
    
    Args:
        base_url: Base URL for the backend API
        
    Returns:
        Global service container instance
    """
    global _container
    if _container is None:
        _container = ServiceContainer(base_url)
    return _container


def reset_global_container():
    """
    Reset the global service container.
    """
    global _container
    _container = None
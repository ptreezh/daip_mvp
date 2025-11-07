"""
Service Container for newP6 TUI

Manages registration and lifecycle of service adapters.
"""

from typing import Dict, Any, Optional, List
import asyncio
import logging

from .base import BaseServiceAdapter

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Container for managing service adapters"""

    def __init__(self):
        self._services: Dict[str, BaseServiceAdapter] = {}
        self._initialized = False

    def register_service(self, name: str, adapter: BaseServiceAdapter) -> None:
        """Register a service adapter"""
        if not isinstance(adapter, BaseServiceAdapter):
            raise TypeError(f"Service adapter must inherit from BaseServiceAdapter, got {type(adapter)}")

        self._services[name] = adapter
        logger.debug(f"Registered service: {name}")

    def get_service(self, name: str) -> Optional[BaseServiceAdapter]:
        """Get a registered service adapter"""
        if not self._initialized:
            logger.warning(f"Container not initialized, returning None for service: {name}")
            return None
        return self._services.get(name)

    def has_service(self, name: str) -> bool:
        """Check if a service is registered"""
        return name in self._services

    def list_services(self) -> List[str]:
        """List all registered service names"""
        return list(self._services.keys())

    def count(self) -> int:
        """Get the number of registered services"""
        return len(self._services)

    def clear(self) -> None:
        """Clear all registered services"""
        if self._initialized:
            logger.warning("Clearing services while container is initialized")
        self._services.clear()

    async def initialize_all(self, event_system: Any, state_manager: Any) -> None:
        """Initialize all registered services"""
        if self._initialized:
            logger.warning("Container already initialized")
            return

        logger.info(f"Initializing {len(self._services)} services...")

        for name, service in self._services.items():
            try:
                # Set dependencies
                service.set_dependencies(event_system, state_manager)

                # Initialize service
                await service.initialize()

                logger.debug(f"Initialized service: {name}")

            except Exception as e:
                logger.error(f"Failed to initialize service {name}: {e}")
                # Continue with other services but don't mark as fully initialized
                raise

        self._initialized = True
        logger.info("All services initialized successfully")

    async def shutdown_all(self) -> None:
        """Shutdown all registered services"""
        if not self._initialized:
            logger.warning("Container not initialized, nothing to shutdown")
            return

        logger.info(f"Shutting down {len(self._services)} services...")

        # Shutdown all services concurrently
        shutdown_tasks = []
        for name, service in self._services.items():
            try:
                shutdown_tasks.append(self._shutdown_service_safe(name, service))
            except Exception as e:
                logger.error(f"Error preparing shutdown for service {name}: {e}")

        if shutdown_tasks:
            await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        self._initialized = False
        logger.info("All services shutdown successfully")

    async def _shutdown_service_safe(self, name: str, service: BaseServiceAdapter) -> None:
        """Safely shutdown a single service"""
        try:
            await service.shutdown()
            logger.debug(f"Shutdown service: {name}")
        except Exception as e:
            logger.error(f"Failed to shutdown service {name}: {e}")

    def get_initialized_services(self) -> Dict[str, BaseServiceAdapter]:
        """Get all successfully initialized services"""
        if not self._initialized:
            return {}
        return self._services.copy()

    @property
    def is_initialized(self) -> bool:
        """Check if the container is initialized"""
        return self._initialized
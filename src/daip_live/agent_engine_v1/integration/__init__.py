"""
Service Integration Module

This module provides integration between domain services and the EventBus system,
enabling event-driven communication and loose coupling between components.
"""

from .service_integration import (
    ServiceEventPublisher,
    ServiceEventSubscriber,
    ServiceIntegrationManager,
    IntentRecognitionServiceIntegrated,
    ExecutionEngineServiceIntegrated,
    PermissionServiceIntegrated,
    StateManagementServiceIntegrated
)

__all__ = [
    "ServiceEventPublisher",
    "ServiceEventSubscriber",
    "ServiceIntegrationManager",
    "IntentRecognitionServiceIntegrated",
    "ExecutionEngineServiceIntegrated",
    "PermissionServiceIntegrated",
    "StateManagementServiceIntegrated"
]
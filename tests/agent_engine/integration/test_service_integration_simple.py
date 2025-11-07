"""Simple tests for service integration with EventBus."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from daip_live.agent_engine_v1.events.event_bus import EventBus
from daip_live.agent_engine_v1.events.event_types import (
    EventType,
    IntentRecognizedEvent,
    ServiceHealthChangedEvent
)
from daip_live.agent_engine_v1.integration.service_integration import (
    ServiceIntegrationManager,
    IntentRecognitionServiceIntegrated
)


class TestServiceIntegrationSimple:
    """Simple test class for service integration."""

    @pytest.fixture
    def event_bus(self):
        """Create an event bus instance."""
        return EventBus()

    @pytest.fixture
    def manager(self, event_bus):
        """Create an integration manager instance."""
        return ServiceIntegrationManager(event_bus)

    @pytest.mark.asyncio
    async def test_create_intent_recognition_service(self, manager):
        """Test creating integrated intent recognition service."""
        service = await manager.create_intent_recognition_service()

        assert service is not None
        assert isinstance(service, IntentRecognitionServiceIntegrated)
        assert "intent_recognition" in manager.integrated_services

    @pytest.mark.asyncio
    async def test_integrated_service_basic_functionality(self, event_bus):
        """Test basic functionality of integrated services."""
        await event_bus.start()

        try:
            # Create integrated service
            service = IntentRecognitionServiceIntegrated(event_bus)

            # Test service lifecycle
            assert not service.is_healthy()
            await service.start()
            assert service.is_healthy()

            # Test basic functionality
            result = await service.recognize_intent("read the file test.txt")
            assert result is not None
            assert result.confidence > 0.0

            # Test metrics
            metrics = service.get_metrics()
            assert "requests_processed" in metrics

            await service.stop()
            assert not service.is_healthy()
        finally:
            await event_bus.stop()

    @pytest.mark.asyncio
    async def test_start_and_stop_services(self, manager):
        """Test starting and stopping all integrated services."""
        await manager.event_bus.start()

        try:
            # Create some services
            await manager.create_intent_recognition_service()
            await manager.create_execution_engine_service()
            await manager.create_permission_service()

            # Start all services
            await manager.start_all_services()

            # Verify all services are healthy
            for service_name, service in manager.integrated_services.items():
                assert service.is_healthy()

            # Stop all services
            await manager.stop_all_services()

            # Verify all services are stopped
            for service_name, service in manager.integrated_services.items():
                assert not service.is_healthy()
        finally:
            await manager.event_bus.stop()

    @pytest.mark.asyncio
    async def test_get_all_metrics(self, manager):
        """Test getting metrics from all services."""
        await manager.event_bus.start()

        try:
            # Create and start services
            await manager.create_intent_recognition_service()
            await manager.create_execution_engine_service()
            await manager.start_all_services()

            # Get metrics
            metrics = await manager.get_all_metrics()

            # Verify metrics structure
            assert "intent_recognition" in metrics
            assert "execution_engine" in metrics

            # Stop services
            await manager.stop_all_services()
        finally:
            await manager.event_bus.stop()
"""Simple tests for IntentRecognitionService."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from daip_live.agent_engine_v1.services.intent_recognition import IntentRecognitionService


class TestIntentRecognitionServiceSimple:
    """Simple test class for IntentRecognitionService."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        return IntentRecognitionService()

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, service):
        """Test service start/stop lifecycle."""
        assert not service.is_healthy()

        await service.start()
        assert service.is_healthy()

        await service.stop()
        assert not service.is_healthy()

    @pytest.mark.asyncio
    async def test_recognize_intent(self, service):
        """Test basic intent recognition."""
        await service.start()

        result = await service.recognize_intent("read the file test.txt")
        assert result is not None
        assert result.confidence > 0.0

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_metrics(self, service):
        """Test metrics collection."""
        await service.start()

        # Perform some operations
        await service.recognize_intent("test input")
        await service.recognize_intent("another test")

        # Get metrics
        metrics = service.get_metrics()
        assert "requests_processed" in metrics
        assert metrics["requests_processed"] >= 2

        await service.stop()

    @pytest.mark.asyncio
    async def test_error_handling_not_running(self, service):
        """Test error handling when service is not running."""
        with pytest.raises(RuntimeError, match="not running"):
            await service.recognize_intent("test")
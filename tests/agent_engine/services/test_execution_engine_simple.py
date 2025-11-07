"""Simple tests for ExecutionEngineService."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from daip_live.agent_engine_v1.services.execution_engine import ExecutionEngineService


class TestExecutionEngineServiceSimple:
    """Simple test class for ExecutionEngineService."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        return ExecutionEngineService()

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, service):
        """Test service start/stop lifecycle."""
        assert not service.is_healthy()

        await service.start()
        assert service.is_healthy()

        await service.stop()
        assert not service.is_healthy()

    @pytest.mark.asyncio
    async def test_register_tool(self, service):
        """Test tool registration."""
        await service.start()

        async def test_tool(*args, **kwargs):
            return {"result": "test"}

        service.register_tool("test_tool", test_tool)
        assert "test_tool" in service._tools

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_metrics(self, service):
        """Test metrics collection."""
        await service.start()

        # Get metrics without performing operations
        metrics = service.get_metrics()
        assert "registered_tools" in metrics
        assert "executions_completed" in metrics

        await service.stop()

    @pytest.mark.asyncio
    async def test_error_handling_not_running(self, service):
        """Test error handling when service is not running."""
        with pytest.raises(RuntimeError, match="not running"):
            await service.execute("test_intent", {})
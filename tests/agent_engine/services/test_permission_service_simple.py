"""Simple tests for PermissionService."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from daip_live.agent_engine_v1.services.permission_service import PermissionService, RiskLevel


class TestPermissionServiceSimple:
    """Simple test class for PermissionService."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        return PermissionService()

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, service):
        """Test service start/stop lifecycle."""
        assert not service.is_healthy()

        await service.start()
        assert service.is_healthy()

        await service.stop()
        assert not service.is_healthy()

    @pytest.mark.asyncio
    async def test_check_permission(self, service):
        """Test basic permission checking."""
        await service.start()

        decision = await service.check_permission("file_read", {"user_role": "admin"})
        assert decision is not None
        assert isinstance(decision.allowed, bool)

        await service.stop()

    @pytest.mark.asyncio
    async def test_assess_risk(self, service):
        """Test risk assessment."""
        await service.start()

        risk = await service.assess_risk("file_read", {"user_role": "admin"})
        assert risk in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_metrics(self, service):
        """Test metrics collection."""
        await service.start()

        # Perform some operations
        await service.check_permission("test_action", {"user": "test"})

        # Get metrics
        metrics = service.get_metrics()
        assert "checks_performed" in metrics
        assert metrics["checks_performed"] >= 1

        await service.stop()

    @pytest.mark.asyncio
    async def test_error_handling_not_running(self, service):
        """Test error handling when service is not running."""
        with pytest.raises(RuntimeError, match="not running"):
            await service.check_permission("test_action", {})
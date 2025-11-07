"""Simple tests for StateManagementService."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from daip_live.agent_engine_v1.services.state_management import StateManagementService


class TestStateManagementServiceSimple:
    """Simple test class for StateManagementService."""

    @pytest.fixture
    def service(self):
        """Create a service instance for testing."""
        return StateManagementService()

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, service):
        """Test service start/stop lifecycle."""
        assert not service.is_healthy()

        await service.start()
        assert service.is_healthy()

        await service.stop()
        assert not service.is_healthy()

    @pytest.mark.asyncio
    async def test_create_snapshot(self, service):
        """Test creating a state snapshot."""
        await service.start()

        snapshot = await service.create_snapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"counter": 1, "status": "running"}
        )

        assert snapshot is not None
        assert snapshot.session_id == "test_session"
        assert snapshot.agent_id == "test_agent"
        assert snapshot.state_data["counter"] == 1

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_latest_snapshot(self, service):
        """Test getting the latest snapshot."""
        await service.start()

        # Create a snapshot first
        created_snapshot = await service.create_snapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"counter": 1}
        )

        # Get latest snapshot
        latest = await service.get_latest_snapshot("test_session")
        assert latest is not None
        assert latest.session_id == created_snapshot.session_id
        assert latest.state_data == created_snapshot.state_data

        await service.stop()

    @pytest.mark.asyncio
    async def test_list_sessions(self, service):
        """Test listing all sessions."""
        await service.start()

        # Create snapshots for different sessions
        await service.create_snapshot("session_1", "agent_1", {"data": "test1"})
        await service.create_snapshot("session_2", "agent_2", {"data": "test2"})

        sessions = await service.list_sessions()
        assert len(sessions) == 2
        assert "session_1" in sessions
        assert "session_2" in sessions

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_metrics(self, service):
        """Test metrics collection."""
        await service.start()

        # Create a snapshot
        await service.create_snapshot("test_session", "test_agent", {"data": "test"})

        # Get metrics
        metrics = service.get_metrics()
        assert "snapshots_created" in metrics
        assert metrics["snapshots_created"] >= 1

        await service.stop()

    @pytest.mark.asyncio
    async def test_error_handling_not_running(self, service):
        """Test error handling when service is not running."""
        with pytest.raises(RuntimeError, match="not running"):
            await service.create_snapshot("session", "agent", {"data": "test"})
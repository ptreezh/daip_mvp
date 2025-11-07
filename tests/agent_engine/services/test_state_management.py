"""Tests for StateManagementService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import tempfile
import os
import json
from datetime import datetime

from daip_live.agent_engine_v1.services.state_management import (
    StateManagementService,
    InMemoryStateStorage,
    FileStateStorage,
    StateChangeRecord
)
from daip_live.agent_engine_v1.services.interfaces import StateSnapshot


class TestStateSnapshot:
    """Test StateSnapshot class."""

    def test_state_snapshot_creation(self):
        """Test creating a state snapshot."""
        snapshot = StateSnapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"counter": 1, "status": "running"},
            metadata={"version": "1.0"},
            timestamp=1234567890.0,
            snapshot_id="snapshot_123"
        )

        assert snapshot.session_id == "test_session"
        assert snapshot.agent_id == "test_agent"
        assert snapshot.state_data["counter"] == 1
        assert snapshot.state_data["status"] == "running"
        assert snapshot.metadata["version"] == "1.0"
        assert snapshot.timestamp == 1234567890.0
        assert snapshot.snapshot_id == "snapshot_123"

    def test_state_snapshot_with_auto_timestamp(self):
        """Test creating state snapshot with automatic timestamp."""
        before_time = datetime.now().timestamp()

        snapshot = StateSnapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"test": "data"}
        )

        after_time = datetime.now().timestamp()

        assert snapshot.timestamp >= before_time
        assert snapshot.timestamp <= after_time
        assert snapshot.snapshot_id is not None

    def test_state_snapshot_to_dict(self):
        """Test state snapshot serialization to dict."""
        snapshot = StateSnapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"counter": 1},
            metadata={"version": "1.0"},
            timestamp=1234567890.0,
            snapshot_id="snapshot_123"
        )

        snapshot_dict = snapshot.to_dict()
        assert snapshot_dict["session_id"] == "test_session"
        assert snapshot_dict["agent_id"] == "test_agent"
        assert snapshot_dict["state_data"]["counter"] == 1
        assert snapshot_dict["metadata"]["version"] == "1.0"
        assert snapshot_dict["timestamp"] == 1234567890.0
        assert snapshot_dict["snapshot_id"] == "snapshot_123"

    @classmethod
    def test_state_snapshot_from_dict(cls):
        """Test state snapshot deserialization from dict."""
        snapshot_dict = {
            "session_id": "test_session",
            "agent_id": "test_agent",
            "state_data": {"counter": 1},
            "metadata": {"version": "1.0"},
            "timestamp": 1234567890.0,
            "snapshot_id": "snapshot_123"
        }

        snapshot = StateSnapshot.from_dict(snapshot_dict)
        assert snapshot.session_id == "test_session"
        assert snapshot.agent_id == "test_agent"
        assert snapshot.state_data["counter"] == 1


class TestInMemoryStateStore:
    """Test InMemoryStateStore."""

    @pytest.fixture
    def store(self):
        """Create a store instance for testing."""
        return InMemoryStateStore()

    @pytest.fixture
    def sample_snapshot(self):
        """Create a sample snapshot for testing."""
        return StateSnapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"counter": 1, "status": "running"},
            metadata={"version": "1.0"}
        )

    @pytest.mark.asyncio
    async def test_save_and_get_snapshot(self, store, sample_snapshot):
        """Test saving and retrieving a snapshot."""
        await store.save_snapshot(sample_snapshot)
        retrieved_snapshot = await store.get_snapshot(
            sample_snapshot.session_id,
            sample_snapshot.snapshot_id
        )

        assert retrieved_snapshot is not None
        assert retrieved_snapshot.session_id == sample_snapshot.session_id
        assert retrieved_snapshot.agent_id == sample_snapshot.agent_id
        assert retrieved_snapshot.state_data == sample_snapshot.state_data

    @pytest.mark.asyncio
    async def test_get_nonexistent_snapshot(self, store):
        """Test retrieving a non-existent snapshot."""
        snapshot = await store.get_snapshot("nonexistent_session", "nonexistent_snapshot")
        assert snapshot is None

    @pytest.mark.asyncio
    async def test_get_latest_snapshot(self, store, sample_snapshot):
        """Test getting the latest snapshot for a session."""
        # Save multiple snapshots
        snapshot1 = StateSnapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"version": 1},
            timestamp=1000.0
        )
        snapshot2 = StateSnapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"version": 2},
            timestamp=2000.0
        )

        await store.save_snapshot(snapshot1)
        await store.save_snapshot(snapshot2)

        latest = await store.get_latest_snapshot("test_session")
        assert latest is not None
        assert latest.state_data["version"] == 2
        assert latest.timestamp == 2000.0

    @pytest.mark.asyncio
    async def test_list_snapshots(self, store, sample_snapshot):
        """Test listing snapshots for a session."""
        await store.save_snapshot(sample_snapshot)

        snapshots = await store.list_snapshots(sample_snapshot.session_id)
        assert len(snapshots) == 1
        assert snapshots[0].session_id == sample_snapshot.session_id

    @pytest.mark.asyncio
    async def test_list_snapshots_by_agent(self, store):
        """Test listing snapshots for a specific agent."""
        snapshot1 = StateSnapshot(
            session_id="session_1",
            agent_id="agent_1",
            state_data={"test": "data1"}
        )
        snapshot2 = StateSnapshot(
            session_id="session_2",
            agent_id="agent_1",
            state_data={"test": "data2"}
        )
        snapshot3 = StateSnapshot(
            session_id="session_3",
            agent_id="agent_2",
            state_data={"test": "data3"}
        )

        await store.save_snapshot(snapshot1)
        await store.save_snapshot(snapshot2)
        await store.save_snapshot(snapshot3)

        # Get snapshots for agent_1
        agent1_snapshots = await store.list_snapshots_by_agent("agent_1")
        assert len(agent1_snapshots) == 2
        assert all(s.agent_id == "agent_1" for s in agent1_snapshots)

        # Get snapshots for agent_2
        agent2_snapshots = await store.list_snapshots_by_agent("agent_2")
        assert len(agent2_snapshots) == 1
        assert agent2_snapshots[0].agent_id == "agent_2"

    @pytest.mark.asyncio
    async def test_delete_snapshot(self, store, sample_snapshot):
        """Test deleting a snapshot."""
        await store.save_snapshot(sample_snapshot)

        # Verify snapshot exists
        snapshot = await store.get_snapshot(
            sample_snapshot.session_id,
            sample_snapshot.snapshot_id
        )
        assert snapshot is not None

        # Delete snapshot
        deleted = await store.delete_snapshot(
            sample_snapshot.session_id,
            sample_snapshot.snapshot_id
        )
        assert deleted is True

        # Verify snapshot is gone
        snapshot = await store.get_snapshot(
            sample_snapshot.session_id,
            sample_snapshot.snapshot_id
        )
        assert snapshot is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_snapshot(self, store):
        """Test deleting a non-existent snapshot."""
        deleted = await store.delete_snapshot("nonexistent_session", "nonexistent_snapshot")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_clear_session(self, store, sample_snapshot):
        """Test clearing all snapshots for a session."""
        await store.save_snapshot(sample_snapshot)
        assert len(await store.list_snapshots(sample_snapshot.session_id)) == 1

        await store.clear_session(sample_snapshot.session_id)
        assert len(await store.list_snapshots(sample_snapshot.session_id)) == 0

    @pytest.mark.asyncio
    async def test_clear_all(self, store, sample_snapshot):
        """Test clearing all snapshots."""
        await store.save_snapshot(sample_snapshot)
        assert len(await store.list_snapshots(sample_snapshot.session_id)) == 1

        await store.clear_all()
        assert len(await store.list_snapshots(sample_snapshot.session_id)) == 0

    @pytest.mark.asyncio
    async def test_get_session_history(self, store):
        """Test getting session history with metadata."""
        snapshot1 = StateSnapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"step": 1},
            timestamp=1000.0
        )
        snapshot2 = StateSnapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"step": 2},
            timestamp=2000.0
        )

        await store.save_snapshot(snapshot1)
        await store.save_snapshot(snapshot2)

        history = await store.get_session_history("test_session")
        assert len(history) == 2
        assert history[0]["step"] == 1
        assert history[1]["step"] == 2
        assert all("timestamp" in entry for entry in history)
        assert all("snapshot_id" in entry for entry in history)


class TestFileStateStore:
    """Test FileStateStore."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        return tempfile.mkdtemp()

    @pytest.fixture
    def store(self, temp_dir):
        """Create a store instance for testing."""
        return FileStateStore(temp_dir)

    @pytest.fixture
    def sample_snapshot(self):
        """Create a sample snapshot for testing."""
        return StateSnapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"counter": 1, "status": "running"},
            metadata={"version": "1.0"}
        )

    @pytest.mark.asyncio
    async def test_file_persistence(self, store, sample_snapshot, temp_dir):
        """Test that snapshots persist across store instances."""
        # Save snapshot in first instance
        await store.save_snapshot(sample_snapshot)

        # Create new instance with same directory
        new_store = FileStateStore(temp_dir)
        retrieved_snapshot = await new_store.get_snapshot(
            sample_snapshot.session_id,
            sample_snapshot.snapshot_id
        )

        assert retrieved_snapshot is not None
        assert retrieved_snapshot.session_id == sample_snapshot.session_id
        assert retrieved_snapshot.state_data == sample_snapshot.state_data

    @pytest.mark.asyncio
    async def test_file_structure(self, store, sample_snapshot):
        """Test that files are created in expected structure."""
        await store.save_snapshot(sample_snapshot)

        # Check that directory structure exists
        session_dir = os.path.join(store.base_path, sample_snapshot.session_id)
        assert os.path.exists(session_dir)

        # Check that snapshot file exists
        snapshot_file = os.path.join(session_dir, f"{sample_snapshot.snapshot_id}.json")
        assert os.path.exists(snapshot_file)

        # Verify file content
        with open(snapshot_file, 'r') as f:
            data = json.load(f)
            assert data["session_id"] == sample_snapshot.session_id
            assert data["agent_id"] == sample_snapshot.agent_id

    def test_cleanup(self):
        """Test cleanup functionality."""
        temp_dir = tempfile.mkdtemp()
        store = FileStateStore(temp_dir)

        # Create some test files
        os.makedirs(os.path.join(temp_dir, "test_session"))
        with open(os.path.join(temp_dir, "test_session", "test_snapshot.json"), 'w') as f:
            json.dump({"test": "data"}, f)

        # Verify files exist
        assert os.path.exists(os.path.join(temp_dir, "test_session", "test_snapshot.json"))

        # Cleanup
        store.cleanup()

        # Files should be cleaned up
        assert not os.path.exists(temp_dir)


class TestStateManagementService:
    """Test StateManagementService."""

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
            state_data={"counter": 1, "status": "running"},
            metadata={"version": "1.0"}
        )

        assert snapshot is not None
        assert snapshot.session_id == "test_session"
        assert snapshot.agent_id == "test_agent"
        assert snapshot.state_data["counter"] == 1
        assert snapshot.state_data["status"] == "running"
        assert snapshot.metadata["version"] == "1.0"
        assert snapshot.snapshot_id is not None

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_snapshot(self, service):
        """Test retrieving a state snapshot."""
        await service.start()

        # Create snapshot
        created_snapshot = await service.create_snapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"counter": 1}
        )

        # Retrieve snapshot
        retrieved_snapshot = await service.get_snapshot(
            session_id="test_session",
            snapshot_id=created_snapshot.snapshot_id
        )

        assert retrieved_snapshot is not None
        assert retrieved_snapshot.session_id == created_snapshot.session_id
        assert retrieved_snapshot.snapshot_id == created_snapshot.snapshot_id
        assert retrieved_snapshot.state_data == created_snapshot.state_data

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_latest_snapshot(self, service):
        """Test getting the latest snapshot for a session."""
        await service.start()

        # Create multiple snapshots
        snapshot1 = await service.create_snapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"version": 1}
        )

        # Small delay to ensure different timestamps
        await asyncio.sleep(0.01)

        snapshot2 = await service.create_snapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"version": 2}
        )

        # Get latest snapshot
        latest = await service.get_latest_snapshot("test_session")
        assert latest is not None
        assert latest.state_data["version"] == 2
        assert latest.snapshot_id == snapshot2.snapshot_id

        await service.stop()

    @pytest.mark.asyncio
    async def test_update_snapshot(self, service):
        """Test updating a state snapshot."""
        await service.start()

        # Create initial snapshot
        snapshot = await service.create_snapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"counter": 1}
        )

        # Update snapshot
        updated_snapshot = await service.update_snapshot(
            session_id="test_session",
            snapshot_id=snapshot.snapshot_id,
            state_data={"counter": 2, "status": "updated"},
            metadata={"version": "2.0"}
        )

        assert updated_snapshot is not None
        assert updated_snapshot.state_data["counter"] == 2
        assert updated_snapshot.state_data["status"] == "updated"
        assert updated_snapshot.metadata["version"] == "2.0"

        # Verify update persisted
        retrieved = await service.get_snapshot(
            session_id="test_session",
            snapshot_id=snapshot.snapshot_id
        )
        assert retrieved.state_data["counter"] == 2
        assert retrieved.state_data["status"] == "updated"

        await service.stop()

    @pytest.mark.asyncio
    async def test_update_nonexistent_snapshot(self, service):
        """Test updating a non-existent snapshot."""
        await service.start()

        with pytest.raises(StateNotFoundError):
            await service.update_snapshot(
                session_id="nonexistent_session",
                snapshot_id="nonexistent_snapshot",
                state_data={"test": "data"}
            )

        await service.stop()

    @pytest.mark.asyncio
    async def test_delete_snapshot(self, service):
        """Test deleting a state snapshot."""
        await service.start()

        # Create snapshot
        snapshot = await service.create_snapshot(
            session_id="test_session",
            agent_id="test_agent",
            state_data={"counter": 1}
        )

        # Delete snapshot
        deleted = await service.delete_snapshot(
            session_id="test_session",
            snapshot_id=snapshot.snapshot_id
        )
        assert deleted is True

        # Verify snapshot is gone
        retrieved = await service.get_snapshot(
            session_id="test_session",
            snapshot_id=snapshot.snapshot_id
        )
        assert retrieved is None

        await service.stop()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_snapshot(self, service):
        """Test deleting a non-existent snapshot."""
        await service.start()

        deleted = await service.delete_snapshot(
            session_id="nonexistent_session",
            snapshot_id="nonexistent_snapshot"
        )
        assert deleted is False

        await service.stop()

    @pytest.mark.asyncio
    async def test_list_sessions(self, service):
        """Test listing all sessions."""
        await service.start()

        # Create snapshots for different sessions
        await service.create_snapshot("session_1", "agent_1", {"data": "test1"})
        await service.create_snapshot("session_2", "agent_2", {"data": "test2"})
        await service.create_snapshot("session_3", "agent_1", {"data": "test3"})

        sessions = await service.list_sessions()
        assert len(sessions) == 3
        assert "session_1" in sessions
        assert "session_2" in sessions
        assert "session_3" in sessions

        await service.stop()

    @pytest.mark.asyncio
    async def test_list_snapshots(self, service):
        """Test listing snapshots for a session."""
        await service.start()

        # Create multiple snapshots for the same session
        await service.create_snapshot("test_session", "agent_1", {"step": 1})
        await service.create_snapshot("test_session", "agent_1", {"step": 2})
        await service.create_snapshot("test_session", "agent_2", {"step": 3})

        snapshots = await service.list_snapshots("test_session")
        assert len(snapshots) == 3
        assert all(s.session_id == "test_session" for s in snapshots)

        await service.stop()

    @pytest.mark.asyncio
    async def test_clear_session(self, service):
        """Test clearing all snapshots for a session."""
        await service.start()

        # Create snapshots
        await service.create_snapshot("test_session", "agent_1", {"data": "test1"})
        await service.create_snapshot("test_session", "agent_2", {"data": "test2"})

        # Verify snapshots exist
        snapshots = await service.list_snapshots("test_session")
        assert len(snapshots) == 2

        # Clear session
        cleared = await service.clear_session("test_session")
        assert cleared is True

        # Verify snapshots are gone
        snapshots = await service.list_snapshots("test_session")
        assert len(snapshots) == 0

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_session_history(self, service):
        """Test getting session history."""
        await service.start()

        # Create snapshots with different data
        await service.create_snapshot("test_session", "agent_1", {"step": 1, "status": "start"})
        await service.create_snapshot("test_session", "agent_1", {"step": 2, "status": "running"})
        await service.create_snapshot("test_session", "agent_1", {"step": 3, "status": "complete"})

        history = await service.get_session_history("test_session")
        assert len(history) == 3
        assert history[0]["step"] == 1
        assert history[1]["step"] == 2
        assert history[2]["step"] == 3
        assert all("timestamp" in entry for entry in history)
        assert all("snapshot_id" in entry for entry in history)

        await service.stop()

    @pytest.mark.asyncio
    async def test_get_session_state_at_time(self, service):
        """Test getting session state at a specific time."""
        await service.start()

        # Create snapshots with known timestamps
        snapshot1 = await service.create_snapshot("test_session", "agent_1", {"version": 1})

        # Small delay to ensure different timestamps
        await asyncio.sleep(0.01)

        snapshot2 = await service.create_snapshot("test_session", "agent_1", {"version": 2})

        # Get state at time between snapshots
        target_time = (snapshot1.timestamp + snapshot2.timestamp) / 2
        state = await service.get_session_state_at_time("test_session", target_time)

        assert state is not None
        assert state["version"] == 1  # Should return the earlier snapshot

        await service.stop()

    @pytest.mark.asyncio
    async def test_batch_operations(self, service):
        """Test batch snapshot operations."""
        await service.start()

        # Create snapshots in batch
        snapshot_requests = [
            {
                "session_id": "session_1",
                "agent_id": "agent_1",
                "state_data": {"counter": 1}
            },
            {
                "session_id": "session_2",
                "agent_id": "agent_2",
                "state_data": {"counter": 2}
            },
            {
                "session_id": "session_3",
                "agent_id": "agent_1",
                "state_data": {"counter": 3}
            }
        ]

        created_snapshots = await service.batch_create_snapshots(snapshot_requests)
        assert len(created_snapshots) == 3
        assert all(s is not None for s in created_snapshots)

        # Verify all snapshots were created
        for request in snapshot_requests:
            latest = await service.get_latest_snapshot(request["session_id"])
            assert latest is not None
            assert latest.state_data == request["state_data"]

        await service.stop()

    @pytest.mark.asyncio
    async def test_service_metrics(self, service):
        """Test service metrics collection."""
        await service.start()

        # Perform some operations
        await service.create_snapshot("session_1", "agent_1", {"data": "test1"})
        await service.create_snapshot("session_2", "agent_2", {"data": "test2"})
        await service.get_latest_snapshot("session_1")
        await service.list_sessions()

        # Get metrics
        metrics = service.get_metrics()
        assert metrics["snapshots_created"] == 2
        assert metrics["snapshots_retrieved"] == 1
        assert metrics["active_sessions"] == 2
        assert metrics["storage_backend"] == "InMemoryStateStore"
        assert metrics["compression_enabled"] is False
        assert metrics["total_size_bytes"] >= 0

        await service.stop()

    @pytest.mark.asyncio
    async def test_error_handling_not_running(self, service):
        """Test error handling when service is not running."""
        # Should raise error when not running
        with pytest.raises(RuntimeError, match="not running"):
            await service.create_snapshot("session", "agent", {"data": "test"})

        with pytest.raises(RuntimeError, match="not running"):
            await service.get_snapshot("session", "snapshot")

        with pytest.raises(RuntimeError, match="not running"):
            await service.list_sessions()

    @pytest.mark.asyncio
    async def test_invalid_state_data(self, service):
        """Test handling of invalid state data."""
        await service.start()

        # Test with None state_data
        with pytest.raises(InvalidStateError, match="State data cannot be empty"):
            await service.create_snapshot("session", "agent", None)

        # Test with empty state_data
        with pytest.raises(InvalidStateError, match="State data cannot be empty"):
            await service.create_snapshot("session", "agent", {})

        await service.stop()

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, service):
        """Test concurrent snapshot operations."""
        await service.start()

        async def create_snapshots(start_id: int, count: int):
            """Create multiple snapshots concurrently."""
            snapshots = []
            for i in range(count):
                snapshot = await service.create_snapshot(
                    f"session_{start_id + i}",
                    "agent_1",
                    {"counter": start_id + i}
                )
                snapshots.append(snapshot)
            return snapshots

        # Create snapshots concurrently
        task1 = asyncio.create_task(create_snapshots(0, 5))
        task2 = asyncio.create_task(create_snapshots(5, 5))

        results1, results2 = await asyncio.gather(task1, task2)
        assert len(results1) == 5
        assert len(results2) == 5
        assert all(s is not None for s in results1 + results2)

        await service.stop()

    @pytest.mark.asyncio
    async def test_state_compression(self, service):
        """Test state data compression functionality."""
        # Create service with compression enabled
        compressed_service = StateManagementService(enable_compression=True)
        await compressed_service.start()

        # Create snapshot with large data
        large_data = {"data": "x" * 1000, "numbers": list(range(100))}
        snapshot = await compressed_service.create_snapshot(
            "test_session",
            "test_agent",
            large_data
        )

        # Retrieve and verify data integrity
        retrieved = await compressed_service.get_snapshot(
            "test_session",
            snapshot.snapshot_id
        )
        assert retrieved.state_data == large_data

        # Check compression metrics
        metrics = compressed_service.get_metrics()
        assert metrics["compression_enabled"] is True

        await compressed_service.stop()

    @pytest.mark.asyncio
    async def test_state_merging(self, service):
        """Test state merging functionality."""
        await service.start()

        # Create initial snapshot
        snapshot = await service.create_snapshot(
            "test_session",
            "test_agent",
            {"counter": 1, "status": "running", "config": {"debug": False}}
        )

        # Merge new state data
        merged_snapshot = await service.merge_state(
            session_id="test_session",
            snapshot_id=snapshot.snapshot_id,
            updates={
                "counter": 2,  # Update existing
                "new_field": "added",  # Add new field
                "config": {"debug": True, "verbose": True}  # Merge nested
            },
            strategy="merge"
        )

        assert merged_snapshot is not None
        assert merged_snapshot.state_data["counter"] == 2
        assert merged_snapshot.state_data["status"] == "running"  # Preserved
        assert merged_snapshot.state_data["new_field"] == "added"
        assert merged_snapshot.state_data["config"]["debug"] is True
        assert merged_snapshot.state_data["config"]["verbose"] is True

        await service.stop()
"""State Management Service implementation."""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from .interfaces import (
    IStateManagementService,
    StateSnapshot,
    IDomainService
)

logger = logging.getLogger(__name__)


@dataclass
class StateChangeRecord:
    """Record of a state change."""

    timestamp: float
    state_key: str
    scope: Optional[str]
    old_value: Any
    new_value: Any
    change_type: str  # create, update, delete
    version: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class StateStorage(ABC):
    """Abstract base class for state storage backends."""

    @abstractmethod
    async def get(self, key: str, scope: Optional[str] = None) -> Optional[Any]:
        """Get state value."""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, scope: Optional[str] = None) -> None:
        """Set state value."""
        pass

    @abstractmethod
    async def delete(self, key: str, scope: Optional[str] = None) -> bool:
        """Delete state value."""
        pass

    @abstractmethod
    async def get_all(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """Get all state values for a scope."""
        pass

    @abstractmethod
    async def clear(self, scope: Optional[str] = None) -> None:
        """Clear all state for a scope."""
        pass


class InMemoryStateStorage(StateStorage):
    """In-memory state storage implementation."""

    def __init__(self):
        """Initialize in-memory storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}  # scope -> {key: value}
        self._lock = asyncio.Lock()

    def _get_scope_key(self, scope: Optional[str]) -> str:
        """Get the storage key for a scope."""
        return scope or "global"

    async def get(self, key: str, scope: Optional[str] = None) -> Optional[Any]:
        """Get state value."""
        async with self._lock:
            scope_key = self._get_scope_key(scope)
            return self._storage.get(scope_key, {}).get(key)

    async def set(self, key: str, value: Any, scope: Optional[str] = None) -> None:
        """Set state value."""
        async with self._lock:
            scope_key = self._get_scope_key(scope)
            if scope_key not in self._storage:
                self._storage[scope_key] = {}
            self._storage[scope_key][key] = value

    async def delete(self, key: str, scope: Optional[str] = None) -> bool:
        """Delete state value."""
        async with self._lock:
            scope_key = self._get_scope_key(scope)
            if scope_key in self._storage and key in self._storage[scope_key]:
                del self._storage[scope_key][key]
                return True
            return False

    async def get_all(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """Get all state values for a scope."""
        async with self._lock:
            scope_key = self._get_scope_key(scope)
            return dict(self._storage.get(scope_key, {}))

    async def clear(self, scope: Optional[str] = None) -> None:
        """Clear all state for a scope."""
        async with self._lock:
            scope_key = self._get_scope_key(scope)
            if scope_key in self._storage:
                del self._storage[scope_key]


class FileStateStorage(StateStorage):
    """File-based state storage implementation."""

    def __init__(self, base_path: str = "data/state"):
        """
        Initialize file storage.

        Args:
            base_path: Base directory for state files
        """
        self.base_path = base_path
        self._lock = asyncio.Lock()

    def _get_file_path(self, scope: Optional[str]) -> str:
        """Get file path for a scope."""
        import os
        scope_key = scope or "global"
        return os.path.join(self.base_path, f"{scope_key}.json")

    async def get(self, key: str, scope: Optional[str] = None) -> Optional[Any]:
        """Get state value."""
        file_path = self._get_file_path(scope)
        try:
            async with self._lock:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get(key)
        except FileNotFoundError:
            return None
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading state file {file_path}: {e}")
            return None

    async def set(self, key: str, value: Any, scope: Optional[str] = None) -> None:
        """Set state value."""
        import os
        file_path = self._get_file_path(scope)

        async with self._lock:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Load existing data
            data = {}
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except FileNotFoundError:
                pass
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error reading state file {file_path}: {e}")
                data = {}

            # Update data
            data[key] = value

            # Write back to file
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except IOError as e:
                logger.error(f"Error writing state file {file_path}: {e}")
                raise

    async def delete(self, key: str, scope: Optional[str] = None) -> bool:
        """Delete state value."""
        file_path = self._get_file_path(scope)
        try:
            async with self._lock:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if key in data:
                    del data[key]

                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    return True
                return False
        except FileNotFoundError:
            return False
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading state file {file_path}: {e}")
            return False

    async def get_all(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """Get all state values for a scope."""
        file_path = self._get_file_path(scope)
        try:
            async with self._lock:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except FileNotFoundError:
            return {}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading state file {file_path}: {e}")
            return {}

    async def clear(self, scope: Optional[str] = None) -> None:
        """Clear all state for a scope."""
        file_path = self._get_file_path(scope)
        try:
            async with self._lock:
                import os
                if os.path.exists(file_path):
                    os.remove(file_path)
        except OSError as e:
            logger.error(f"Error removing state file {file_path}: {e}")


class StatePersistenceStrategy(ABC):
    """Abstract base class for state persistence strategies."""

    @abstractmethod
    async def save_snapshot(self, snapshot: StateSnapshot) -> None:
        """Save a state snapshot."""
        pass

    @abstractmethod
    async def load_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """Load a state snapshot."""
        pass

    @abstractmethod
    async def list_snapshots(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List available snapshots."""
        pass

    @abstractmethod
    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot."""
        pass


class InMemoryPersistenceStrategy(StatePersistenceStrategy):
    """In-memory snapshot persistence."""

    def __init__(self, max_snapshots: int = 100):
        """
        Initialize in-memory persistence.

        Args:
            max_snapshots: Maximum number of snapshots to keep
        """
        self.max_snapshots = max_snapshots
        self._snapshots: Dict[str, StateSnapshot] = {}
        self._lock = asyncio.Lock()

    async def save_snapshot(self, snapshot: StateSnapshot) -> None:
        """Save a state snapshot."""
        async with self._lock:
            snapshot_id = f"snapshot_{int(snapshot.timestamp)}_{id(snapshot)}"
            self._snapshots[snapshot_id] = snapshot

            # Remove oldest snapshots if over limit
            if len(self._snapshots) > self.max_snapshots:
                # Sort by timestamp and remove oldest
                sorted_snapshots = sorted(
                    self._snapshots.items(),
                    key=lambda x: x[1].timestamp
                )
                to_remove = len(self._snapshots) - self.max_snapshots
                for i in range(to_remove):
                    del self._snapshots[sorted_snapshots[i][0]]

    async def load_snapshot(self, snapshot_id: str) -> Optional[StateSnapshot]:
        """Load a state snapshot."""
        async with self._lock:
            return self._snapshots.get(snapshot_id)

    async def list_snapshots(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List available snapshots."""
        async with self._lock:
            snapshots = [
                {
                    "id": snapshot_id,
                    "timestamp": snapshot.timestamp,
                    "version": snapshot.version,
                    "metadata": snapshot.metadata
                }
                for snapshot_id, snapshot in sorted(
                    self._snapshots.items(),
                    key=lambda x: x[1].timestamp,
                    reverse=True
                )
            ]
            return snapshots[:limit]

    async def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot."""
        async with self._lock:
            if snapshot_id in self._snapshots:
                del self._snapshots[snapshot_id]
                return True
            return False


class StateManagementService(IStateManagementService):
    """
    State Management Service implementation.

    This service provides state management with multiple storage backends,
    snapshot capabilities, and comprehensive change tracking.
    """

    def __init__(
        self,
        storage_backend: str = "memory",
        storage_path: Optional[str] = None,
        enable_snapshots: bool = True,
        max_snapshots: int = 100,
        enable_history: bool = True,
        history_size: int = 1000
    ):
        """
        Initialize state management service.

        Args:
            storage_backend: Storage backend ('memory' or 'file')
            storage_path: Path for file storage
            enable_snapshots: Whether to enable snapshot functionality
            max_snapshots: Maximum number of snapshots to keep
            enable_history: Whether to enable change history
            history_size: Maximum history size per state key
        """
        self.enable_snapshots = enable_snapshots
        self.enable_history = enable_history

        # Initialize storage backend
        if storage_backend == "memory":
            self._storage = InMemoryStateStorage()
        elif storage_backend == "file":
            self._storage = FileStateStorage(storage_path or "data/state")
        else:
            raise ValueError(f"Unknown storage backend: {storage_backend}")

        # Initialize persistence strategy
        if enable_snapshots:
            self._persistence = InMemoryPersistenceStrategy(max_snapshots)
        else:
            self._persistence = None

        self._history_size = history_size
        self._change_history: Dict[str, List[StateChangeRecord]] = {}
        self._version_counters: Dict[str, int] = {}
        self._running = False

        self._metrics = {
            "operations_processed": 0,
            "gets": 0,
            "sets": 0,
            "updates": 0,
            "deletes": 0,
            "snapshots_created": 0,
            "snapshots_restored": 0,
            "history_entries": 0,
            "avg_operation_time_ms": 0.0,
            "operation_time_total": 0.0
        }

    async def start(self) -> None:
        """Start the state management service."""
        if self._running:
            return

        self._running = True
        logger.info("StateManagementService started")

    async def stop(self) -> None:
        """Stop the state management service."""
        if not self._running:
            return

        self._running = False
        self._change_history.clear()
        self._version_counters.clear()
        logger.info("StateManagementService stopped")

    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        return self._running

    async def get_state(
        self,
        state_key: str,
        scope: Optional[str] = None
    ) -> Optional[Any]:
        """
        Get state value.

        Args:
            state_key: Key of the state
            scope: Optional scope identifier

        Returns:
            State value or None if not found
        """
        if not self._running:
            raise RuntimeError("StateManagementService is not running")

        start_time = time.time()
        self._metrics["operations_processed"] += 1
        self._metrics["gets"] += 1

        try:
            value = await self._storage.get(state_key, scope)

            # Update metrics
            operation_time = (time.time() - start_time) * 1000
            self._update_metrics(operation_time)

            return value
        except Exception as e:
            logger.error(f"Error getting state '{state_key}': {e}")
            raise

    async def set_state(
        self,
        state_key: str,
        value: Any,
        scope: Optional[str] = None
    ) -> None:
        """
        Set state value.

        Args:
            state_key: Key of the state
            value: State value
            scope: Optional scope identifier
        """
        if not self._running:
            raise RuntimeError("StateManagementService is not running")

        start_time = time.time()
        self._metrics["operations_processed"] += 1

        try:
            # Check if state already exists
            old_value = await self._storage.get(state_key, scope)

            # Get version
            version_key = f"{state_key}:{scope or 'global'}"
            version = self._version_counters.get(version_key, 0) + 1
            self._version_counters[version_key] = version

            # Set the new value
            await self._storage.set(state_key, value, scope)

            # Record change
            if self.enable_history:
                await self._record_change(
                    state_key, scope, old_value, value, "create" if old_value is None else "update", version
                )

            # Update metrics
            operation_time = (time.time() - start_time) * 1000
            self._update_metrics(operation_time)

            if old_value is None:
                self._metrics["sets"] += 1
            else:
                self._metrics["updates"] += 1

            logger.debug(f"Set state '{state_key}' in scope '{scope or 'global'}'")

        except Exception as e:
            logger.error(f"Error setting state '{state_key}': {e}")
            raise

    async def update_state(
        self,
        state_key: str,
        updates: Dict[str, Any],
        scope: Optional[str] = None
    ) -> Any:
        """
        Update state with partial updates.

        Args:
            state_key: Key of the state
            updates: Dictionary of updates
            scope: Optional scope identifier

        Returns:
            Updated state value
        """
        if not self._running:
            raise RuntimeError("StateManagementService is not running")

        # Get current value
        current_value = await self.get_state(state_key, scope)

        if current_value is None:
            # If state doesn't exist, create it with updates
            new_value = updates
        else:
            # Apply updates to existing value
            if isinstance(current_value, dict) and isinstance(updates, dict):
                new_value = {**current_value, **updates}
            else:
                # For non-dict values, replace entirely
                new_value = updates

        # Set the updated value
        await self.set_state(state_key, new_value, scope)
        return new_value

    async def delete_state(
        self,
        state_key: str,
        scope: Optional[str] = None
    ) -> bool:
        """
        Delete state.

        Args:
            state_key: Key of the state
            scope: Optional scope identifier

        Returns:
            True if state was deleted, False if not found
        """
        if not self._running:
            raise RuntimeError("StateManagementService is not running")

        start_time = time.time()
        self._metrics["operations_processed"] += 1

        try:
            # Get current value before deletion
            old_value = await self._storage.get(state_key, scope)

            # Delete the state
            deleted = await self._storage.delete(state_key, scope)

            if deleted:
                # Record change
                if self.enable_history:
                    version_key = f"{state_key}:{scope or 'global'}"
                    version = self._version_counters.get(version_key, 0)
                    await self._record_change(
                        state_key, scope, old_value, None, "delete", version
                    )

                # Update metrics
                operation_time = (time.time() - start_time) * 1000
                self._update_metrics(operation_time)
                self._metrics["deletes"] += 1

                logger.debug(f"Deleted state '{state_key}' from scope '{scope or 'global'}'")

            return deleted

        except Exception as e:
            logger.error(f"Error deleting state '{state_key}': {e}")
            raise

    async def create_snapshot(
        self,
        scope: Optional[str] = None
    ) -> StateSnapshot:
        """
        Create a snapshot of current state.

        Args:
            scope: Optional scope identifier

        Returns:
            State snapshot
        """
        if not self._running:
            raise RuntimeError("StateManagementService is not running")

        if not self._persistence:
            raise RuntimeError("Snapshots are not enabled")

        start_time = time.time()

        try:
            # Get all state for the scope
            state_data = await self._storage.get_all(scope)

            # Create snapshot
            snapshot = StateSnapshot(
                state_data=state_data,
                timestamp=start_time,
                version=f"v{int(start_time)}",
                metadata={
                    "scope": scope,
                    "operation_count": len(state_data),
                    "created_by": "StateManagementService"
                }
            )

            # Save snapshot
            await self._persistence.save_snapshot(snapshot)
            self._metrics["snapshots_created"] += 1

            logger.debug(f"Created snapshot for scope '{scope or 'global'}' with {len(state_data)} states")
            return snapshot

        except Exception as e:
            logger.error(f"Error creating snapshot: {e}")
            raise

    async def restore_snapshot(
        self,
        snapshot: StateSnapshot,
        scope: Optional[str] = None
    ) -> None:
        """
        Restore state from snapshot.

        Args:
            snapshot: Snapshot to restore
            scope: Optional scope identifier
        """
        if not self._running:
            raise RuntimeError("StateManagementService is not running")

        if not self._persistence:
            raise RuntimeError("Snapshots are not enabled")

        start_time = time.time()

        try:
            # Clear current state for the scope
            await self._storage.clear(scope)

            # Restore state from snapshot
            for key, value in snapshot.state_data.items():
                await self._storage.set(key, value, scope)

            self._metrics["snapshots_restored"] += 1
            logger.debug(f"Restored snapshot for scope '{scope or 'global'}' with {len(snapshot.state_data)} states")

        except Exception as e:
            logger.error(f"Error restoring snapshot: {e}")
            raise

    def get_state_history(
        self,
        state_key: str,
        scope: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get history of state changes.

        Args:
            state_key: Key of the state
            scope: Optional scope identifier
            limit: Maximum number of history entries

        Returns:
            List of state change records
        """
        if not self.enable_history:
            return []

        history_key = f"{state_key}:{scope or 'global'}"
        history = self._change_history.get(history_key, [])

        # Return most recent entries
        recent_history = sorted(history, key=lambda r: r.timestamp, reverse=True)[:limit]

        return [
            {
                "timestamp": record.timestamp,
                "state_key": record.state_key,
                "scope": record.scope,
                "old_value": record.old_value,
                "new_value": record.new_value,
                "change_type": record.change_type,
                "version": record.version,
                "metadata": record.metadata
            }
            for record in recent_history
        ]

    async def _record_change(
        self,
        state_key: str,
        scope: Optional[str],
        old_value: Any,
        new_value: Any,
        change_type: str,
        version: int
    ) -> None:
        """Record a state change."""
        history_key = f"{state_key}:{scope or 'global'}"

        if history_key not in self._change_history:
            self._change_history[history_key] = []

        record = StateChangeRecord(
            timestamp=time.time(),
            state_key=state_key,
            scope=scope,
            old_value=old_value,
            new_value=new_value,
            change_type=change_type,
            version=version
        )

        self._change_history[history_key].append(record)

        # Maintain history size
        if len(self._change_history[history_key]) > self._history_size:
            self._change_history[history_key] = self._change_history[history_key][-self._history_size:]

        self._metrics["history_entries"] += 1

    def _update_metrics(self, operation_time_ms: float) -> None:
        """Update operation metrics."""
        self._metrics["operation_time_total"] += operation_time_ms / 1000
        total_operations = self._metrics["operations_processed"]
        if total_operations > 0:
            self._metrics["avg_operation_time_ms"] = (
                self._metrics["operation_time_total"] * 1000 / total_operations
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        return {
            **self._metrics,
            "operations_per_second": (
                self._metrics["operations_processed"] / (self._metrics["operation_time_total"] or 1)
            ),
            "storage_backend": type(self._storage).__name__,
            "snapshots_enabled": self.enable_snapshots,
            "history_enabled": self.enable_history,
            "active_scopes": len(self._version_counters),
            "total_state_keys": sum(
                len(scope) for scope in [self._storage.get_all(scope) for scope in [None, "global"]]
            ),
            "total_history_entries": sum(
                len(history) for history in self._change_history.values()
            )
        }
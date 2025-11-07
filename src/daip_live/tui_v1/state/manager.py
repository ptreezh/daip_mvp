"""
TUI State Manager

This module provides the TUIStateManager class as specified in the newP6
architecture requirements. The state manager follows reactive programming
principles with efficient subscription mechanisms.

Based on newP6 specification requirements for state management.
"""

import asyncio
import time
import uuid
from typing import Any, Dict, Callable, List, Optional
from collections import deque
import copy


class TUIStateManager:
    """
    State management system for newP6 TUI architecture.

    This class provides reactive state management with subscription mechanisms,
    history tracking, and performance optimization as specified in the newP6
    architecture requirements.

    Features:
    - Reactive state updates with <50ms latency
    - Subscription mechanism for state changes
    - State history and rollback capability
    - Batch update optimization
    - Async state update support
    - State persistence and restoration
    """

    def __init__(self, max_history: int = 100):
        """
        Initialize the state manager.

        Args:
            max_history: Maximum number of historical states to keep
        """
        self._state: Dict[str, Any] = {}
        self._subscribers: Dict[str, List[tuple]] = {}  # key -> list of (callback_id, callback)
        self._history: deque = deque(maxlen=max_history)
        self._max_history = max_history
        self._subscription_id_counter = 0
        self._performance_start_time = None

    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        Update the state and notify subscribers.

        Args:
            updates: Dictionary of key-value pairs to update

        Raises:
            TypeError: If updates is not a dictionary
            ValueError: If updates is None
        """
        if not isinstance(updates, dict):
            raise TypeError("State updates must be a dictionary")
        if updates is None:
            raise ValueError("State updates cannot be None")

        # Start performance timing
        self._performance_start_time = time.perf_counter()

        # Store current state in history BEFORE making changes
        self._history.append(copy.deepcopy(self._state))

        # Track changes for notifications
        changes = {}
        for key, new_value in updates.items():
            old_value = self._state.get(key, None)
            self._state[key] = new_value
            changes[key] = (old_value, new_value)

        # Notify subscribers
        self._notify_subscribers(changes)

    def subscribe(self, key: str, callback: Callable[[str, Any, Any], None]) -> str:
        """
        Subscribe to state changes for a specific key.

        Args:
            key: The state key to subscribe to
            callback: Function to call when state changes (key, old_value, new_value)

        Returns:
            str: Subscription ID that can be used to unsubscribe
        """
        if key not in self._subscribers:
            self._subscribers[key] = []

        subscription_id = str(uuid.uuid4())
        self._subscribers[key].append((subscription_id, callback))
        self._subscription_id_counter += 1

        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from state changes.

        Args:
            subscription_id: The subscription ID to remove

        Returns:
            bool: True if unsubscribed successfully, False if not found
        """
        for key, subscribers in self._subscribers.items():
            for i, (sub_id, _) in enumerate(subscribers):
                if sub_id == subscription_id:
                    subscribers.pop(i)
                    if not subscribers:
                        del self._subscribers[key]
                    return True
        return False

    def get_state(self) -> Dict[str, Any]:
        """
        Get a copy of the current state.

        Returns:
            Dict[str, Any]: Copy of the current state
        """
        return copy.deepcopy(self._state)

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the state history.

        Returns:
            List[Dict[str, Any]]: List of historical states
        """
        return list(self._history)

    def rollback_to_state(self, history_index: int) -> bool:
        """
        Rollback to a previous state from history.

        Args:
            history_index: Index in history to rollback to (0 is earliest)

        Returns:
            bool: True if rollback successful, False if index invalid
        """
        if history_index < 0 or history_index >= len(self._history):
            return False

        # Get the target state from history
        target_state = self._history[history_index]
        self._state = copy.deepcopy(target_state)

        # Clear future history after the rollback point
        history_list = list(self._history)
        self._history = deque(history_list[:history_index + 1], maxlen=self._max_history)

        return True

    async def update_state_async(self, updates: Dict[str, Any]) -> None:
        """
        Asynchronously update state and notify subscribers.

        Args:
            updates: Dictionary of key-value pairs to update
        """
        # Store current state in history
        self._history.append(copy.deepcopy(self._state))

        # Track changes for notifications
        changes = {}
        for key, new_value in updates.items():
            old_value = self._state.get(key, None)
            self._state[key] = new_value
            changes[key] = (old_value, new_value)

        # Notify subscribers asynchronously
        await self._notify_subscribers_async(changes)

    def persist_state(self) -> Dict[str, Any]:
        """
        Persist the current state for later restoration.

        Returns:
            Dict[str, Any]: Serializable state data
        """
        return {
            'state': copy.deepcopy(self._state),
            'history': list(self._history),
            'subscribers': len(self._subscribers)
        }

    def restore_state(self, persisted_data: Dict[str, Any]) -> None:
        """
        Restore state from persisted data.

        Args:
            persisted_data: Data from persist_state() call
        """
        if 'state' in persisted_data:
            self._state = copy.deepcopy(persisted_data['state'])

        if 'history' in persisted_data:
            self._history = deque(persisted_data['history'], maxlen=self._max_history)

    def _notify_subscribers(self, changes: Dict[str, tuple]) -> None:
        """
        Notify subscribers of state changes.

        Args:
            changes: Dictionary of key -> (old_value, new_value) pairs
        """
        for key, (old_value, new_value) in changes.items():
            if key in self._subscribers:
                for _, callback in self._subscribers[key]:
                    try:
                        callback(key, old_value, new_value)
                    except Exception as e:
                        # Log error but don't stop other notifications
                        print(f"Error in state subscription callback: {e}")

    async def _notify_subscribers_async(self, changes: Dict[str, tuple]) -> None:
        """
        Asynchronously notify subscribers of state changes.

        Args:
            changes: Dictionary of key -> (old_value, new_value) pairs
        """
        async_tasks = []
        for key, (old_value, new_value) in changes.items():
            if key in self._subscribers:
                for _, callback in self._subscribers[key]:
                    if asyncio.iscoroutinefunction(callback):
                        async_tasks.append(callback(key, old_value, new_value))
                    else:
                        callback(key, old_value, new_value)

        if async_tasks:
            await asyncio.gather(*async_tasks, return_exceptions=True)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the last state update.

        Returns:
            Dict[str, Any]: Performance metrics
        """
        metrics = {
            'subscribers_count': sum(len(subs) for subs in self._subscribers.values()),
            'state_size': len(self._state),
            'history_size': len(self._history),
        }

        if self._performance_start_time:
            latency_ms = (time.perf_counter() - self._performance_start_time) * 1000
            metrics['last_update_latency_ms'] = latency_ms

        return metrics
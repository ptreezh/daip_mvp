"""State management for workflow execution.

This module handles workflow state persistence, recovery, and monitoring.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import ExecutionStep, WorkflowExecution, WorkflowStatus

logger = logging.getLogger(__name__)


class StateManager:
    """Manages workflow execution state and persistence.
    
    Handles state management, persistence, and recovery for workflow executions,
    providing rollback capabilities and state monitoring.
    """

    def __init__(self, storage_backend: Optional[Any] = None):
        """Initialize the state manager.
        
        Args:
            storage_backend: Optional storage backend for persistence

        """
        self.storage_backend = storage_backend
        self._executions: Dict[str, WorkflowExecution] = {}
        self._state_lock = asyncio.Lock()

    async def create_execution(self, execution: WorkflowExecution) -> bool:
        """Create a new workflow execution state.
        
        Args:
            execution: WorkflowExecution to create
            
        Returns:
            True if creation was successful, False otherwise

        """
        async with self._state_lock:
            try:
                if execution.execution_id in self._executions:
                    logger.warning(f"Execution {execution.execution_id} already exists")
                    return False

                self._executions[execution.execution_id] = execution

                # Persist to storage backend if available
                if self.storage_backend:
                    await self._persist_execution(execution)

                logger.info(f"Created execution state for {execution.execution_id}")
                return True

            except Exception as e:
                logger.error(f"Failed to create execution state: {e}")
                return False

    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution state.
        
        Args:
            execution_id: ID of the execution to retrieve
            
        Returns:
            WorkflowExecution if found, None otherwise

        """
        async with self._state_lock:
            execution = self._executions.get(execution_id)

            # Try to load from storage backend if not in memory
            if execution is None and self.storage_backend:
                execution = await self._load_execution(execution_id)
                if execution:
                    self._executions[execution_id] = execution

            return execution

    async def update_execution(self, execution: WorkflowExecution) -> bool:
        """Update workflow execution state.
        
        Args:
            execution: Updated WorkflowExecution
            
        Returns:
            True if update was successful, False otherwise

        """
        async with self._state_lock:
            try:
                if execution.execution_id not in self._executions:
                    logger.error(f"Execution {execution.execution_id} not found for update")
                    return False

                self._executions[execution.execution_id] = execution

                # Persist to storage backend if available
                if self.storage_backend:
                    await self._persist_execution(execution)

                return True

            except Exception as e:
                logger.error(f"Failed to update execution state: {e}")
                return False

    async def update_execution_status(
        self,
        execution_id: str,
        status: WorkflowStatus,
        current_step: Optional[str] = None
    ) -> bool:
        """Update execution status.
        
        Args:
            execution_id: ID of the execution
            status: New status
            current_step: Current step being executed
            
        Returns:
            True if update was successful, False otherwise

        """
        execution = await self.get_execution(execution_id)
        if execution is None:
            return False

        execution.status = status
        if current_step is not None:
            execution.current_step = current_step

        if status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            execution.end_time = datetime.now()

        return await self.update_execution(execution)

    async def add_execution_step(self, execution_id: str, step: ExecutionStep) -> bool:
        """Add an execution step to the trace.
        
        Args:
            execution_id: ID of the execution
            step: ExecutionStep to add
            
        Returns:
            True if addition was successful, False otherwise

        """
        execution = await self.get_execution(execution_id)
        if execution is None:
            return False

        execution.execution_trace.append(step)
        return await self.update_execution(execution)

    async def update_workflow_state(
        self,
        execution_id: str,
        state_updates: Dict[str, Any]
    ) -> bool:
        """Update workflow shared state.
        
        Args:
            execution_id: ID of the execution
            state_updates: State updates to apply
            
        Returns:
            True if update was successful, False otherwise

        """
        execution = await self.get_execution(execution_id)
        if execution is None:
            return False

        execution.workflow_state.update(state_updates)
        return await self.update_execution(execution)

    async def set_node_outputs(
        self,
        execution_id: str,
        node_id: str,
        outputs: Dict[str, Any]
    ) -> bool:
        """Set outputs for a specific node.
        
        Args:
            execution_id: ID of the execution
            node_id: ID of the node
            outputs: Node outputs
            
        Returns:
            True if setting was successful, False otherwise

        """
        execution = await self.get_execution(execution_id)
        if execution is None:
            return False

        execution.node_outputs[node_id] = outputs
        return await self.update_execution(execution)

    async def get_node_outputs(
        self,
        execution_id: str,
        node_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get outputs for a specific node.
        
        Args:
            execution_id: ID of the execution
            node_id: ID of the node
            
        Returns:
            Node outputs if found, None otherwise

        """
        execution = await self.get_execution(execution_id)
        if execution is None:
            return None

        return execution.node_outputs.get(node_id)

    async def add_execution_error(self, execution_id: str, error: str) -> bool:
        """Add an error to the execution.
        
        Args:
            execution_id: ID of the execution
            error: Error message
            
        Returns:
            True if addition was successful, False otherwise

        """
        execution = await self.get_execution(execution_id)
        if execution is None:
            return False

        execution.errors.append(error)
        return await self.update_execution(execution)

    async def add_execution_warning(self, execution_id: str, warning: str) -> bool:
        """Add a warning to the execution.
        
        Args:
            execution_id: ID of the execution
            warning: Warning message
            
        Returns:
            True if addition was successful, False otherwise

        """
        execution = await self.get_execution(execution_id)
        if execution is None:
            return False

        execution.warnings.append(warning)
        return await self.update_execution(execution)

    async def create_checkpoint(self, execution_id: str) -> Optional[str]:
        """Create a checkpoint for rollback capability.
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            Checkpoint ID if successful, None otherwise

        """
        execution = await self.get_execution(execution_id)
        if execution is None:
            return None

        try:
            checkpoint_id = f"{execution_id}_checkpoint_{datetime.now().isoformat()}"

            # Create a deep copy of the execution state
            checkpoint_data = execution.model_dump()

            # Store checkpoint (implementation depends on storage backend)
            if self.storage_backend:
                await self._store_checkpoint(checkpoint_id, checkpoint_data)

            logger.info(f"Created checkpoint {checkpoint_id} for execution {execution_id}")
            return checkpoint_id

        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")
            return None

    async def rollback_to_checkpoint(
        self,
        execution_id: str,
        checkpoint_id: str
    ) -> bool:
        """Rollback execution to a previous checkpoint.
        
        Args:
            execution_id: ID of the execution
            checkpoint_id: ID of the checkpoint to rollback to
            
        Returns:
            True if rollback was successful, False otherwise

        """
        try:
            if not self.storage_backend:
                logger.error("No storage backend available for rollback")
                return False

            # Load checkpoint data
            checkpoint_data = await self._load_checkpoint(checkpoint_id)
            if checkpoint_data is None:
                logger.error(f"Checkpoint {checkpoint_id} not found")
                return False

            # Restore execution state
            execution = WorkflowExecution(**checkpoint_data)
            await self.update_execution(execution)

            logger.info(f"Rolled back execution {execution_id} to checkpoint {checkpoint_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to rollback to checkpoint: {e}")
            return False

    async def list_executions(
        self,
        status_filter: Optional[WorkflowStatus] = None
    ) -> List[str]:
        """List execution IDs, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            List of execution IDs

        """
        async with self._state_lock:
            if status_filter is None:
                return list(self._executions.keys())

            return [
                execution_id for execution_id, execution in self._executions.items()
                if execution.status == status_filter
            ]

    async def cleanup_completed_executions(self, max_age_hours: int = 24) -> int:
        """Clean up old completed executions.
        
        Args:
            max_age_hours: Maximum age in hours for completed executions
            
        Returns:
            Number of executions cleaned up

        """
        async with self._state_lock:
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            cleaned_count = 0

            executions_to_remove = []
            for execution_id, execution in self._executions.items():
                if (execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED] and
                    execution.end_time and execution.end_time.timestamp() < cutoff_time):
                    executions_to_remove.append(execution_id)

            for execution_id in executions_to_remove:
                del self._executions[execution_id]
                cleaned_count += 1

            logger.info(f"Cleaned up {cleaned_count} old executions")
            return cleaned_count

    async def _persist_execution(self, execution: WorkflowExecution) -> None:
        """Persist execution to storage backend."""
        if self.storage_backend and hasattr(self.storage_backend, 'store_execution'):
            await self.storage_backend.store_execution(execution)

    async def _load_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Load execution from storage backend."""
        if self.storage_backend and hasattr(self.storage_backend, 'load_execution'):
            return await self.storage_backend.load_execution(execution_id)
        return None

    async def _store_checkpoint(self, checkpoint_id: str, checkpoint_data: Dict[str, Any]) -> None:
        """Store checkpoint to storage backend."""
        if self.storage_backend and hasattr(self.storage_backend, 'store_checkpoint'):
            await self.storage_backend.store_checkpoint(checkpoint_id, checkpoint_data)

    async def _load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint from storage backend."""
        if self.storage_backend and hasattr(self.storage_backend, 'load_checkpoint'):
            return await self.storage_backend.load_checkpoint(checkpoint_id)
        return None

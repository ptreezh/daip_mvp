"""Parallel execution manager for the Institutional Primitives System.

This module implements parallel execution capabilities for the workflow engine,
allowing multiple nodes to be executed concurrently with controlled concurrency.
"""

import asyncio
import logging
<<<<<<< HEAD
from collections.abc import Coroutine
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
=======
from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import Any, Optional
>>>>>>> feature/core-services-refactor

from .base import ExecutionTrace


class ParallelExecutionGroup:
    """Group of nodes that can be executed in parallel.
    
    This class manages the concurrent execution of a group of nodes,
    with controlled concurrency and error handling.
    """

    def __init__(
        self,
        group_id: str,
        max_concurrency: int = 5,
        timeout: Optional[float] = None
    ):
        """Initialize a parallel execution group.
        
        Args:
            group_id: Unique identifier for the group
            max_concurrency: Maximum number of concurrent executions
            timeout: Timeout in seconds for the entire group execution

        """
        self.group_id = group_id
        self.max_concurrency = max_concurrency
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.logger = logging.getLogger(__name__)
<<<<<<< HEAD
        self.tasks: Set[asyncio.Task] = set()
        self.results: Dict[str, Any] = {}
        self.errors: Dict[str, Exception] = {}

=======
        self.tasks: set[asyncio.Task] = set()
        self.results: dict[str, Any] = {}
        self.errors: dict[str, Exception] = {}
    
>>>>>>> feature/core-services-refactor
    async def execute_node(
        self,
        node_id: str,
        execute_func: Callable[[str], Coroutine[Any, Any, dict[str, Any]]],
        trace: ExecutionTrace
<<<<<<< HEAD
    ) -> Dict[str, Any]:
=======
    ) -> dict[str, Any]:
>>>>>>> feature/core-services-refactor
        """Execute a node with concurrency control.
        
        Args:
            node_id: ID of the node to execute
            execute_func: Function to execute the node
            trace: Execution trace to update
            
        Returns:
            Node execution results

        """
        async with self.semaphore:
            try:
                self.logger.info(f"Executing node {node_id} in parallel group {self.group_id}")
                start_time = datetime.now()

                # Execute the node
                result = await execute_func(node_id)

                # Record success
                end_time = datetime.now()
                duration_ms = (end_time - start_time).total_seconds() * 1000
                self.results[node_id] = result
                self.logger.info(f"Node {node_id} completed in {duration_ms:.2f}ms")

                return result
            except Exception as e:
                # Record error
                self.logger.error(f"Error executing node {node_id}: {e}")
                self.errors[node_id] = e
                raise

    async def execute_all(
        self,
        node_ids: list[str],
        execute_func: Callable[[str], Coroutine[Any, Any, dict[str, Any]]],
        trace: ExecutionTrace
<<<<<<< HEAD
    ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Exception]]:
=======
    ) -> tuple[dict[str, dict[str, Any]], dict[str, Exception]]:
>>>>>>> feature/core-services-refactor
        """Execute multiple nodes in parallel.
        
        Args:
            node_ids: List of node IDs to execute
            execute_func: Function to execute each node
            trace: Execution trace to update
            
        Returns:
            Tuple of (results, errors) dictionaries

        """
        # Create tasks for each node
        for node_id in node_ids:
            task = asyncio.create_task(
                self.execute_node(node_id, execute_func, trace)
            )
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)

        # Wait for all tasks with optional timeout
        if self.timeout:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.tasks, return_exceptions=True),
                    timeout=self.timeout
                )
            except asyncio.TimeoutError:
                self.logger.error(
                    f"Parallel execution group {self.group_id} timed out after {self.timeout}s"
                )
                # Cancel remaining tasks
                for task in self.tasks:
                    if not task.done():
                        task.cancel()
        else:
            # Wait without timeout
            await asyncio.gather(*self.tasks, return_exceptions=True)

        return self.results, self.errors


class ParallelExecutionManager:
    """Manager for parallel execution of workflow nodes.
    
    This class coordinates the parallel execution of nodes across
    multiple execution groups.
    """

    def __init__(self):
        """Initialize the parallel execution manager."""
        self.execution_groups: dict[str, ParallelExecutionGroup] = {}
        self.logger = logging.getLogger(__name__)

    def create_execution_group(
        self,
        group_id: str = None,
        max_concurrency: int = 5,
        timeout: Optional[float] = None
    ) -> ParallelExecutionGroup:
        """Create a new parallel execution group.
        
        Args:
            group_id: Optional group ID (generated if not provided)
            max_concurrency: Maximum number of concurrent executions
            timeout: Timeout in seconds for the entire group execution
            
        Returns:
            New parallel execution group

        """
        import uuid

        # Generate group ID if not provided
        if group_id is None:
            group_id = str(uuid.uuid4())

        # Create group
        group = ParallelExecutionGroup(
            group_id=group_id,
            max_concurrency=max_concurrency,
            timeout=timeout
        )

        # Store group
        self.execution_groups[group_id] = group

        return group

    async def execute_nodes_in_parallel(
        self,
        node_ids: list[str],
        execute_func: Callable[[str], Coroutine[Any, Any, dict[str, Any]]],
        trace: ExecutionTrace,
        max_concurrency: int = 5,
        timeout: Optional[float] = None
<<<<<<< HEAD
    ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Exception]]:
=======
    ) -> tuple[dict[str, dict[str, Any]], dict[str, Exception]]:
>>>>>>> feature/core-services-refactor
        """Execute multiple nodes in parallel.
        
        Args:
            node_ids: List of node IDs to execute
            execute_func: Function to execute each node
            trace: Execution trace to update
            max_concurrency: Maximum number of concurrent executions
            timeout: Timeout in seconds for the entire execution
            
        Returns:
            Tuple of (results, errors) dictionaries

        """
        # Create a new execution group
        group = self.create_execution_group(
            max_concurrency=max_concurrency,
            timeout=timeout
        )

        # Execute nodes in parallel
        return await group.execute_all(node_ids, execute_func, trace)
<<<<<<< HEAD

    def get_group_status(self, group_id: str) -> Optional[Dict[str, Any]]:
=======
    
    def get_group_status(self, group_id: str) -> Optional[dict[str, Any]]:
>>>>>>> feature/core-services-refactor
        """Get the status of a parallel execution group.
        
        Args:
            group_id: ID of the execution group
            
        Returns:
            Status information or None if group not found

        """
        if group_id not in self.execution_groups:
            return None

        group = self.execution_groups[group_id]
        return {
            "group_id": group.group_id,
            "max_concurrency": group.max_concurrency,
            "timeout": group.timeout,
            "active_tasks": len(group.tasks),
            "completed_results": len(group.results),
            "errors": len(group.errors)
        }

    def cleanup_group(self, group_id: str) -> bool:
        """Clean up a parallel execution group.
        
        Args:
            group_id: ID of the execution group
            
        Returns:
            True if group was cleaned up, False if not found

        """
        if group_id in self.execution_groups:
            del self.execution_groups[group_id]
            self.logger.info(f"Cleaned up parallel execution group {group_id}")
            return True
        return False

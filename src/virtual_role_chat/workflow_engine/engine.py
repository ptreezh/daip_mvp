"""Main workflow orchestration engine.

This module implements the core WorkflowEngine that orchestrates the execution
of institutional workflows by coordinating primitive nodes and managing
execution state.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from ..institutional_primitives import PrimitiveRegistry, get_global_registry
from .execution_manager import ExecutionManager
from .models import ExecutionMetrics, NodeStatus, WorkflowDefinition, WorkflowExecution, WorkflowResult, WorkflowStatus
from .state_manager import StateManager

logger = logging.getLogger(__name__)


class WorkflowEngine:
    """Main workflow orchestration engine.
    
    Orchestrates the execution of institutional workflows by coordinating
    primitive nodes, managing execution state, and providing workflow
    control capabilities.
    """
    
    def __init__(
        self,
        primitive_registry: Optional[PrimitiveRegistry] = None,
        state_manager: Optional[StateManager] = None,
        services: Optional[dict[str, Any]] = None,
        max_concurrency: int = 5
    ):
        """Initialize the workflow engine.
        
        Args:
            primitive_registry: Registry for institutional primitives
            state_manager: Manager for workflow state persistence
            services: Available DAIP-LIVE services
            max_concurrency: Maximum concurrent node executions
        """
        self.primitive_registry = primitive_registry or get_global_registry()
        self.state_manager = state_manager or StateManager()
        self.services = services or {}
        self.execution_manager = ExecutionManager(self.primitive_registry, max_concurrency)
        
        # Active executions
        self._active_executions: dict[str, WorkflowExecution] = {}
        self._execution_tasks: dict[str, asyncio.Task] = {}
    
    async def execute_workflow(
        self, 
        workflow_def: WorkflowDefinition, 
        params: Optional[dict[str, Any]] = None
    ) -> WorkflowResult:
        """Execute a workflow definition.
        
        Args:
            workflow_def: Workflow definition to execute
            params: Optional parameters for the workflow
            
        Returns:
            WorkflowResult containing execution results
        """
        # Validate workflow definition
        validation_errors = workflow_def.validate_structure()
        if validation_errors:
            return WorkflowResult(
                execution_id="",
                workflow_id=workflow_def.id,
                status=WorkflowStatus.FAILED,
                start_time=datetime.now(),
                errors=validation_errors
            )
        
        # Create workflow execution
        execution = WorkflowExecution(
            workflow_definition=workflow_def,
            parameters=params or {},
            start_time=datetime.now()
        )
        
        # Initialize node states
        for node in workflow_def.nodes:
            execution.node_states[node.id] = NodeStatus.PENDING
        
        # Store execution
        self._active_executions[execution.execution_id] = execution
        await self.state_manager.save_execution_state(execution)
        
        try:
            # Start execution task
            execution_task = asyncio.create_task(
                self._execute_workflow_async(execution),
                name=f"workflow_{execution.execution_id}"
            )
            self._execution_tasks[execution.execution_id] = execution_task
            
            # Wait for completion
            await execution_task
            
            # Build final result
            result = await self._build_workflow_result(execution)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            execution.status = WorkflowStatus.FAILED
            result = await self._build_workflow_result(execution)
            result.errors.append(str(e))
        
        finally:
            # Cleanup
            if execution.execution_id in self._active_executions:
                del self._active_executions[execution.execution_id]
            if execution.execution_id in self._execution_tasks:
                del self._execution_tasks[execution.execution_id]
        
        return result
    
    async def _execute_workflow_async(self, execution: WorkflowExecution) -> None:
        """Asynchronously execute a workflow.
        
        Args:
            execution: Workflow execution to run
        """
        execution.status = WorkflowStatus.RUNNING
        await self.state_manager.save_execution_state(execution)
        
        logger.info(f"Starting workflow execution {execution.execution_id}")
        
        try:
            while not execution.is_complete() and not execution.has_failed():
                # Get nodes ready for execution
                ready_nodes = execution.get_ready_nodes()
                
                if not ready_nodes:
                    if execution.current_nodes:
                        # Wait for current nodes to complete
                        await asyncio.sleep(0.1)
                        continue
                    else:
                        # No ready nodes and no running nodes - check for deadlock
                        remaining_nodes = [
                            node.id for node in execution.workflow_definition.nodes
                            if node.id not in execution.completed_nodes and node.id not in execution.failed_nodes
                        ]
                        if remaining_nodes:
                            logger.error(f"Workflow deadlock detected. Remaining nodes: {remaining_nodes}")
                            execution.status = WorkflowStatus.FAILED
                            break
                        else:
                            # All nodes processed
                            break
                
                # Get nodes to execute
                nodes_to_execute = []
                for node_id in ready_nodes:
                    node = next(n for n in execution.workflow_definition.nodes if n.id == node_id)
                    nodes_to_execute.append(node)
                
                # Execute nodes in parallel
                if nodes_to_execute:
                    steps = await self.execution_manager.execute_nodes_parallel(
                        nodes_to_execute, execution, self.services
                    )
                    
                    # Add steps to execution trace
                    execution.execution_trace.extend(steps)
                    
                    # Save state after each batch
                    await self.state_manager.save_execution_state(execution)
            
            # Determine final status
            if execution.has_failed():
                execution.status = WorkflowStatus.FAILED
                logger.error(f"Workflow {execution.execution_id} failed")
            else:
                execution.status = WorkflowStatus.COMPLETED
                logger.info(f"Workflow {execution.execution_id} completed successfully")
        
        except asyncio.CancelledError:
            execution.status = WorkflowStatus.CANCELLED
            logger.info(f"Workflow {execution.execution_id} was cancelled")
            raise
        
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            logger.error(f"Workflow {execution.execution_id} failed with exception: {e}")
            raise
        
        finally:
            execution.end_time = datetime.now()
            await self.state_manager.save_execution_state(execution)
    
    async def get_workflow_status(self, execution_id: str) -> Optional[WorkflowStatus]:
        """Get the status of a workflow execution.
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            WorkflowStatus if found, None otherwise
        """
        # Check active executions first
        if execution_id in self._active_executions:
            return self._active_executions[execution_id].status
        
        # Check persistent storage
        execution = await self.state_manager.load_execution_state(execution_id)
        if execution:
            return execution.status
        
        return None
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause a running workflow execution.
        
        Args:
            execution_id: ID of the execution to pause
            
        Returns:
            True if pause was successful, False otherwise
        """
        if execution_id not in self._active_executions:
            logger.warning(f"Cannot pause workflow {execution_id}: not found in active executions")
            return False
        
        execution = self._active_executions[execution_id]
        
        if execution.status != WorkflowStatus.RUNNING:
            logger.warning(f"Cannot pause workflow {execution_id}: not in running state")
            return False
        
        try:
            # Update status
            execution.status = WorkflowStatus.PAUSED
            
            # Cancel current node executions
            cancelled_count = await self.execution_manager.cancel_all_executions()
            logger.info(f"Cancelled {cancelled_count} node executions for workflow {execution_id}")
            
            # Save state
            await self.state_manager.save_execution_state(execution)
            
            logger.info(f"Workflow {execution_id} paused successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause workflow {execution_id}: {e}")
            return False
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume a paused workflow execution.
        
        Args:
            execution_id: ID of the execution to resume
            
        Returns:
            True if resume was successful, False otherwise
        """
        try:
            # Load execution state
            execution = await self.state_manager.load_execution_state(execution_id)
            if not execution:
                logger.error(f"Cannot resume workflow {execution_id}: execution not found")
                return False
            
            if execution.status != WorkflowStatus.PAUSED:
                logger.warning(f"Cannot resume workflow {execution_id}: not in paused state")
                return False
            
            # Add to active executions
            self._active_executions[execution_id] = execution
            
            # Start execution task
            execution_task = asyncio.create_task(
                self._execute_workflow_async(execution),
                name=f"workflow_{execution_id}_resumed"
            )
            self._execution_tasks[execution_id] = execution_task
            
            logger.info(f"Workflow {execution_id} resumed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume workflow {execution_id}: {e}")
            return False
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a workflow execution.
        
        Args:
            execution_id: ID of the execution to cancel
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        try:
            # Cancel execution task if running
            if execution_id in self._execution_tasks:
                task = self._execution_tasks[execution_id]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Update execution status
            if execution_id in self._active_executions:
                execution = self._active_executions[execution_id]
                execution.status = WorkflowStatus.CANCELLED
                execution.end_time = datetime.now()
                await self.state_manager.save_execution_state(execution)
            
            # Cancel node executions
            await self.execution_manager.cancel_all_executions()
            
            logger.info(f"Workflow {execution_id} cancelled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow {execution_id}: {e}")
            return False
    
    async def _build_workflow_result(self, execution: WorkflowExecution) -> WorkflowResult:
        """Build a WorkflowResult from execution state.
        
        Args:
            execution: Workflow execution
            
        Returns:
            WorkflowResult containing execution results
        """
        # Calculate metrics
        metrics = ExecutionMetrics()
        
        if execution.start_time and execution.end_time:
            metrics.total_execution_time = (execution.end_time - execution.start_time).total_seconds()
        
        metrics.node_count = len(execution.workflow_definition.nodes)
        metrics.successful_nodes = len(execution.completed_nodes)
        metrics.failed_nodes = len(execution.failed_nodes)
        metrics.skipped_nodes = metrics.node_count - metrics.successful_nodes - metrics.failed_nodes
        
        # Collect outputs from completed nodes
        outputs = {}
        for node_id, node_outputs in execution.node_outputs.items():
            outputs[node_id] = node_outputs
        
        # Collect errors
        errors = []
        for step in execution.execution_trace:
            if step.errors:
                errors.extend(step.errors)
        
        return WorkflowResult(
            execution_id=execution.execution_id,
            workflow_id=execution.workflow_definition.id,
            status=execution.status,
            outputs=outputs,
            execution_trace=execution.execution_trace,
            metrics=metrics,
            start_time=execution.start_time or datetime.now(),
            end_time=execution.end_time,
            errors=errors
        )
    
    def get_active_executions(self) -> list[str]:
        """Get list of active workflow execution IDs.
        
        Returns:
            List of execution IDs
        """
        return list(self._active_executions.keys())
    
    async def get_execution_details(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get detailed information about a workflow execution.
        
        Args:
            execution_id: ID of the execution
            
        Returns:
            WorkflowExecution if found, None otherwise
        """
        # Check active executions first
        if execution_id in self._active_executions:
            return self._active_executions[execution_id]
        
        # Check persistent storage
        return await self.state_manager.load_execution_state(execution_id)
    
    async def cleanup_completed_executions(self, max_age_days: int = 7) -> int:
        """Clean up old completed workflow executions.
        
        Args:
            max_age_days: Maximum age in days for completed executions
            
        Returns:
            Number of executions cleaned up
        """
        return await self.state_manager.cleanup_old_executions(max_age_days)
    
    def get_engine_statistics(self) -> dict[str, Any]:
        """Get engine statistics.
        
        Returns:
            Dictionary of engine statistics
        """
        return {
            "active_workflows": len(self._active_executions),
            "active_tasks": len(self._execution_tasks),
            "execution_manager_stats": self.execution_manager.get_execution_statistics(),
            "registered_primitives": len(self.primitive_registry.list_primitives()),
            "available_services": list(self.services.keys())
        }
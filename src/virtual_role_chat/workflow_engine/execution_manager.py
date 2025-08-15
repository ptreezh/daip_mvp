"""Execution management for workflow nodes.

This module handles the execution of individual workflow nodes,
including parallel execution, dependency management, and error handling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

from ..institutional_primitives import ExecutionContext, PrimitiveRegistry
from .models import ExecutionStep, NodeStatus, WorkflowExecution, WorkflowNode

logger = logging.getLogger(__name__)


class ExecutionManager:
    """Manages the execution of workflow nodes.
    
    Handles node execution, dependency resolution, parallel execution,
    and error handling for workflow orchestration.
    """
    
    def __init__(self, primitive_registry: PrimitiveRegistry, max_concurrency: int = 5):
        """Initialize the execution manager.
        
        Args:
            primitive_registry: Registry for institutional primitives
            max_concurrency: Maximum number of concurrent node executions
        """
        self.primitive_registry = primitive_registry
        self.max_concurrency = max_concurrency
        self._execution_semaphore = asyncio.Semaphore(max_concurrency)
        self._active_executions: dict[str, asyncio.Task] = {}
    
    async def execute_node(
        self, 
        node: WorkflowNode, 
        execution: WorkflowExecution,
        services: dict[str, Any]
    ) -> ExecutionStep:
        """Execute a single workflow node.
        
        Args:
            node: Node to execute
            execution: Workflow execution context
            services: Available services for the execution
            
        Returns:
            ExecutionStep containing execution results
        """
        step = ExecutionStep(
            node_id=node.id,
            primitive_type=node.type,
            status=NodeStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # Get primitive instance
            primitive = self.primitive_registry.create_primitive(node.type, node.config)
            if primitive is None:
                raise ValueError(f"Failed to create primitive of type '{node.type}'")
            
            # Prepare inputs from node dependencies
            inputs = await self._prepare_node_inputs(node, execution)
            step.inputs = inputs
            
            # Create execution context
            context = ExecutionContext(
                execution_id=execution.execution_id,
                workflow_id=execution.workflow_definition.id,
                node_id=node.id,
                services=services,
                state=execution.context,
                metadata=node.metadata
            )
            
            # Execute primitive
            async with self._execution_semaphore:
                logger.info(f"Executing node {node.id} (type: {node.type})")
                result = await primitive.execute(inputs, context)
            
            # Process results
            if result.success:
                step.status = NodeStatus.COMPLETED
                step.outputs = result.outputs
                execution.node_outputs[node.id] = result.outputs
                execution.completed_nodes.append(node.id)
                logger.info(f"Node {node.id} completed successfully")
            else:
                step.status = NodeStatus.FAILED
                step.errors = result.errors
                step.warnings = result.warnings
                execution.failed_nodes.append(node.id)
                logger.error(f"Node {node.id} failed: {result.errors}")
            
            step.execution_time = result.execution_time
            step.metadata = result.metadata
            
        except Exception as e:
            step.status = NodeStatus.FAILED
            step.errors = [str(e)]
            execution.failed_nodes.append(node.id)
            logger.error(f"Node {node.id} execution failed with exception: {e}")
        
        finally:
            step.end_time = datetime.now()
            if step.start_time and step.end_time:
                step.execution_time = (step.end_time - step.start_time).total_seconds()
            
            # Remove from current nodes
            if node.id in execution.current_nodes:
                execution.current_nodes.remove(node.id)
        
        return step
    
    async def execute_nodes_parallel(
        self,
        nodes: list[WorkflowNode],
        execution: WorkflowExecution,
        services: dict[str, Any]
    ) -> list[ExecutionStep]:
        """Execute multiple nodes in parallel.
        
        Args:
            nodes: List of nodes to execute
            execution: Workflow execution context
            services: Available services for execution
            
        Returns:
            List of ExecutionStep results
        """
        if not nodes:
            return []
        
        logger.info(f"Executing {len(nodes)} nodes in parallel")
        
        # Add nodes to current execution list
        for node in nodes:
            execution.current_nodes.append(node.id)
            execution.node_states[node.id] = NodeStatus.RUNNING
        
        # Create execution tasks
        tasks = []
        for node in nodes:
            task = asyncio.create_task(
                self.execute_node(node, execution, services),
                name=f"node_{node.id}"
            )
            tasks.append(task)
            self._active_executions[node.id] = task
        
        try:
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            steps = []
            for i, result in enumerate(results):
                node = nodes[i]
                
                if isinstance(result, Exception):
                    # Handle task exception
                    step = ExecutionStep(
                        node_id=node.id,
                        primitive_type=node.type,
                        status=NodeStatus.FAILED,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        errors=[str(result)]
                    )
                    execution.failed_nodes.append(node.id)
                    logger.error(f"Node {node.id} task failed: {result}")
                else:
                    step = result
                
                steps.append(step)
                execution.node_states[node.id] = step.status
        
        finally:
            # Clean up active executions
            for node in nodes:
                if node.id in self._active_executions:
                    del self._active_executions[node.id]
        
        return steps
    
    async def _prepare_node_inputs(
        self, 
        node: WorkflowNode, 
        execution: WorkflowExecution
    ) -> dict[str, Any]:
        """Prepare inputs for node execution from dependencies and parameters.
        
        Args:
            node: Node to prepare inputs for
            execution: Workflow execution context
            
        Returns:
            Dictionary of prepared inputs
        """
        inputs = {}
        
        # Add workflow parameters
        inputs.update(execution.parameters)
        
        # Add outputs from dependency nodes
        for dep_node_id in node.dependencies:
            if dep_node_id in execution.node_outputs:
                dep_outputs = execution.node_outputs[dep_node_id]
                
                # Map outputs to inputs based on node configuration
                if "input_mapping" in node.config:
                    mapping = node.config["input_mapping"]
                    for output_key, input_key in mapping.items():
                        if output_key in dep_outputs:
                            inputs[input_key] = dep_outputs[output_key]
                else:
                    # Default: merge all outputs
                    inputs.update(dep_outputs)
        
        # Add node-specific inputs from config
        if "inputs" in node.config:
            inputs.update(node.config["inputs"])
        
        return inputs
    
    async def cancel_node_execution(self, node_id: str) -> bool:
        """Cancel execution of a specific node.
        
        Args:
            node_id: ID of the node to cancel
            
        Returns:
            True if cancellation was successful, False otherwise
        """
        if node_id in self._active_executions:
            task = self._active_executions[node_id]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Node {node_id} execution cancelled")
                    return True
                except Exception as e:
                    logger.error(f"Error cancelling node {node_id}: {e}")
                    return False
        
        return False
    
    async def cancel_all_executions(self) -> int:
        """Cancel all active node executions.
        
        Returns:
            Number of executions cancelled
        """
        cancelled_count = 0
        
        for node_id in list(self._active_executions.keys()):
            if await self.cancel_node_execution(node_id):
                cancelled_count += 1
        
        return cancelled_count
    
    def get_active_executions(self) -> list[str]:
        """Get list of currently executing node IDs.
        
        Returns:
            List of node IDs currently executing
        """
        return list(self._active_executions.keys())
    
    def is_node_executing(self, node_id: str) -> bool:
        """Check if a node is currently executing.
        
        Args:
            node_id: ID of the node to check
            
        Returns:
            True if node is executing, False otherwise
        """
        return node_id in self._active_executions
    
    async def wait_for_node(self, node_id: str, timeout: Optional[float] = None) -> bool:
        """Wait for a specific node to complete execution.
        
        Args:
            node_id: ID of the node to wait for
            timeout: Optional timeout in seconds
            
        Returns:
            True if node completed, False if timeout or not found
        """
        if node_id not in self._active_executions:
            return False
        
        task = self._active_executions[node_id]
        
        try:
            if timeout:
                await asyncio.wait_for(task, timeout=timeout)
            else:
                await task
            return True
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for node {node_id}")
            return False
        except Exception as e:
            logger.error(f"Error waiting for node {node_id}: {e}")
            return False
    
    def get_execution_statistics(self) -> dict[str, Any]:
        """Get execution statistics.
        
        Returns:
            Dictionary of execution statistics
        """
        return {
            "active_executions": len(self._active_executions),
            "max_concurrency": self.max_concurrency,
            "available_slots": self._execution_semaphore._value,
            "active_node_ids": list(self._active_executions.keys())
        }
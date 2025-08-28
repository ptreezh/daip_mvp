"""
Workflow Engine for the Institutional Primitives System.

This module implements the workflow orchestration engine that coordinates
the execution of institutional primitives in complex workflows.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .parallel_execution import ParallelExecutionManager

from .base import ExecutionContext, ExecutionStep, ExecutionTrace
from .registry import PrimitiveRegistry
from .parallel_execution import ParallelExecutionManager


class WorkflowNode(BaseModel):
    """
    Definition of a node in a workflow.
    """
    id: str
    type: str  # Primitive type (e.g., "generation", "fact_extraction")
    config: Dict[str, Any] = Field(default_factory=dict)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    parallel_group: Optional[str] = None  # ID of parallel execution group
    max_retries: int = 0  # Number of retries on failure
    parallel_group: Optional[str] = None  # ID of parallel execution group
    max_retries: int = 0  # Number of retries on failure


class WorkflowEdge(BaseModel):
    """
    Definition of an edge between nodes in a workflow.
    """
    from_node: str
    to_node: str
    condition: Optional[str] = None  # Conditional execution


class WorkflowDefinition(BaseModel):
    """
    Definition of a complete workflow.
    """
    id: str
    name: str
    description: str
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)  # For parallel group configs


class WorkflowResult(BaseModel):
    """
    Result of a workflow execution.
    """
    execution_id: str
    status: str  # "completed", "failed", "cancelled"
    outputs: Dict[str, Any] = Field(default_factory=dict)
    execution_trace: ExecutionTrace
    metrics: Dict[str, Any] = Field(default_factory=dict)


class WorkflowStatus(BaseModel):
    """
    Status of a workflow execution.
    """
    execution_id: str
    workflow_id: str
    status: str  # "running", "completed", "failed", "cancelled", "paused"
    progress: float  # 0.0 to 1.0
    current_nodes: List[str] = Field(default_factory=list)
    completed_nodes: List[str] = Field(default_factory=list)
    failed_nodes: List[str] = Field(default_factory=list)
    start_time: datetime
    end_time: Optional[datetime] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)


class WorkflowEngine:
    """
    Engine for executing institutional workflows.
    
    The WorkflowEngine orchestrates the execution of institutional primitives
    in complex workflows, managing state, handling failures, and providing
    monitoring capabilities.
    """
    
    def __init__(self, primitive_registry: PrimitiveRegistry):
        """
        Initialize the workflow engine.
        
        Args:
            primitive_registry: Registry of available primitives
        """
        self.primitive_registry = primitive_registry
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.parallel_execution_manager = ParallelExecutionManager()
        self.logger = logging.getLogger(__name__)
    
    async def execute_workflow(
        self, 
        workflow_def: WorkflowDefinition, 
        params: Dict[str, Any] = None
    ) -> WorkflowResult:
        """
        Execute a workflow with the given parameters.
        
        Args:
            workflow_def: Definition of the workflow to execute
            params: Parameters for the workflow execution
            
        Returns:
            Result of the workflow execution
        """
        execution_id = str(uuid.uuid4())
        params = params or {}
        
        # Merge workflow parameters with execution parameters
        merged_params = {**workflow_def.parameters, **params}
        
        # Initialize execution trace
        trace = ExecutionTrace(
            execution_id=execution_id,
            workflow_id=workflow_def.id,
            start_time=datetime.now(),
            status="running"
        )
        
        # Initialize execution context
        context = ExecutionContext(
            execution_id=execution_id,
            workflow_id=workflow_def.id,
            node_id="root",
            state={"params": merged_params, "node_outputs": {}}
        )
        
        # Register active workflow
        self.active_workflows[execution_id] = {
            "workflow_def": workflow_def,
            "context": context,
            "trace": trace,
            "status": "running",
            "task": None
        }
        
        try:
            # Build execution graph
            graph = self._build_execution_graph(workflow_def)
            
            # Execute the graph
            outputs = await self._execute_graph(graph, context, trace)
            
            # Mark execution as completed
            trace.mark_completed()
            
            # Calculate metrics
            metrics = self._calculate_metrics(trace)
            
            # Create result
            result = WorkflowResult(
                execution_id=execution_id,
                status="completed",
                outputs=outputs,
                execution_trace=trace,
                metrics=metrics
            )
            
            # Update active workflow status
            self.active_workflows[execution_id]["status"] = "completed"
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_def.id}: {e}")
            
            # Mark execution as failed
            trace.mark_failed()
            
            # Create result
            result = WorkflowResult(
                execution_id=execution_id,
                status="failed",
                outputs={},
                execution_trace=trace,
                metrics={"error": str(e)}
            )
            
            # Update active workflow status
            self.active_workflows[execution_id]["status"] = "failed"
            
            return result
        
        finally:
            # Clean up active workflow after some time
            # In a real implementation, we might keep it around longer for inspection
            asyncio.create_task(self._cleanup_workflow(execution_id))
    
    def get_workflow_status(self, execution_id: str) -> Optional[WorkflowStatus]:
        """
        Get the status of a workflow execution.
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            Status of the workflow execution, or None if not found
        """
        if execution_id not in self.active_workflows:
            return None
        
        workflow_data = self.active_workflows[execution_id]
        trace = workflow_data["trace"]
        context = workflow_data["context"]
        workflow_def = workflow_data["workflow_def"]
        
        # Calculate progress
        total_nodes = len(workflow_def.nodes)
        completed_nodes = set(step.node_id for step in trace.steps if step.status == "completed")
        failed_nodes = set(step.node_id for step in trace.steps if step.status == "failed")
        progress = len(completed_nodes) / total_nodes if total_nodes > 0 else 0.0
        
        # Determine current nodes
        all_nodes = set(node.id for node in workflow_def.nodes)
        current_nodes = all_nodes - completed_nodes - failed_nodes
        
        return WorkflowStatus(
            execution_id=execution_id,
            workflow_id=workflow_def.id,
            status=workflow_data["status"],
            progress=progress,
            current_nodes=list(current_nodes),
            completed_nodes=list(completed_nodes),
            failed_nodes=list(failed_nodes),
            start_time=trace.start_time,
            end_time=trace.end_time,
            metrics=trace.metrics
        )
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """
        Pause a running workflow.
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            True if the workflow was paused, False otherwise
        """
        if execution_id not in self.active_workflows:
            self.logger.warning(f"Cannot pause workflow {execution_id}: not found")
            return False
        
        workflow_data = self.active_workflows[execution_id]
        if workflow_data["status"] != "running":
            self.logger.warning(f"Cannot pause workflow {execution_id}: not running")
            return False
        
        # In a real implementation, we would need to handle the actual pausing
        # of tasks, which is complex in an async environment
        workflow_data["status"] = "paused"
        
        # For now, we'll just log that we would pause it
        self.logger.info(f"Workflow {execution_id} paused")
        
        return True
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """
        Resume a paused workflow.
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            True if the workflow was resumed, False otherwise
        """
        if execution_id not in self.active_workflows:
            self.logger.warning(f"Cannot resume workflow {execution_id}: not found")
            return False
        
        workflow_data = self.active_workflows[execution_id]
        if workflow_data["status"] != "paused":
            self.logger.warning(f"Cannot resume workflow {execution_id}: not paused")
            return False
        
        # In a real implementation, we would need to handle the actual resuming
        # of tasks, which is complex in an async environment
        workflow_data["status"] = "running"
        
        # For now, we'll just log that we would resume it
        self.logger.info(f"Workflow {execution_id} resumed")
        
        return True
    
    def create_parallel_group(
        self,
        workflow_def: WorkflowDefinition,
        node_ids: List[str],
        group_id: str = None,
        max_concurrency: int = 5,
        timeout: Optional[float] = None
    ) -> str:
        """
        Create a parallel execution group for a set of nodes.
        
        Args:
            workflow_def: Workflow definition to modify
            node_ids: List of node IDs to include in the group
            group_id: Optional group ID (generated if not provided)
            max_concurrency: Maximum number of concurrent executions
            timeout: Timeout in seconds for the entire group execution
            
        Returns:
            ID of the created parallel group
        """
        import uuid
        
        # Generate group ID if not provided
        if group_id is None:
            group_id = str(uuid.uuid4())
        
        # Update nodes with parallel group ID
        for i, node in enumerate(workflow_def.nodes):
            if node.id in node_ids:
                # Create a new node with updated parallel_group
                updated_node = WorkflowNode(
                    id=node.id,
                    type=node.type,
                    config=node.config,
                    inputs=node.inputs,
                    outputs=node.outputs,
                    parallel_group=group_id,
                    max_retries=node.max_retries
                )
                workflow_def.nodes[i] = updated_node
        
        # Store group configuration in workflow metadata
        if not hasattr(workflow_def, "metadata"):
            workflow_def.metadata = {}
        
        if "parallel_groups" not in workflow_def.metadata:
            workflow_def.metadata["parallel_groups"] = {}
        
        workflow_def.metadata["parallel_groups"][group_id] = {
            "max_concurrency": max_concurrency,
            "timeout": timeout,
            "node_ids": node_ids
        }
        
        return group_id
    
    def create_parallel_group(
        self,
        workflow_def: WorkflowDefinition,
        node_ids: List[str],
        group_id: str = None,
        max_concurrency: int = 5,
        timeout: Optional[float] = None
    ) -> str:
        """
        Create a parallel execution group for a set of nodes.
        
        Args:
            workflow_def: Workflow definition to modify
            node_ids: List of node IDs to include in the group
            group_id: Optional group ID (generated if not provided)
            max_concurrency: Maximum number of concurrent executions
            timeout: Timeout in seconds for the entire group execution
            
        Returns:
            ID of the created parallel group
        """
        import uuid
        
        # Generate group ID if not provided
        if group_id is None:
            group_id = str(uuid.uuid4())
        
        # Update nodes with parallel group ID
        for i, node in enumerate(workflow_def.nodes):
            if node.id in node_ids:
                # Create a new node with updated parallel_group
                updated_node = WorkflowNode(
                    id=node.id,
                    type=node.type,
                    config=node.config,
                    inputs=node.inputs,
                    outputs=node.outputs,
                    parallel_group=group_id,
                    max_retries=node.max_retries
                )
                workflow_def.nodes[i] = updated_node
        
        # Store group configuration in workflow metadata
        if "parallel_groups" not in workflow_def.metadata:
            workflow_def.metadata["parallel_groups"] = {}
        
        workflow_def.metadata["parallel_groups"][group_id] = {
            "max_concurrency": max_concurrency,
            "timeout": timeout,
            "node_ids": node_ids
        }
        
        return group_id
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """
        Cancel a running or paused workflow.
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            True if the workflow was cancelled, False otherwise
        """
        if execution_id not in self.active_workflows:
            self.logger.warning(f"Cannot cancel workflow {execution_id}: not found")
            return False
        
        workflow_data = self.active_workflows[execution_id]
        if workflow_data["status"] not in ["running", "paused"]:
            self.logger.warning(f"Cannot cancel workflow {execution_id}: not running or paused")
            return False
        
        # In a real implementation, we would need to handle the actual cancellation
        # of tasks, which is complex in an async environment
        workflow_data["status"] = "cancelled"
        workflow_data["trace"].mark_cancelled()
        
        # For now, we'll just log that we would cancel it
        self.logger.info(f"Workflow {execution_id} cancelled")
        
        return True
    
    def _build_execution_graph(self, workflow_def: WorkflowDefinition) -> Dict[str, Any]:
        """
        Build an execution graph from a workflow definition.
        
        Args:
            workflow_def: Definition of the workflow
            
        Returns:
            Execution graph representation
        """
        # Create a graph representation for execution
        graph = {
            "nodes": {node.id: node for node in workflow_def.nodes},
            "edges": workflow_def.edges,
            "inputs": {},  # Map of node ID to input sources
            "outputs": {},  # Map of node ID to output destinations
            "entry_nodes": [],  # Nodes with no incoming edges
            "exit_nodes": [],  # Nodes with no outgoing edges
            "workflow_def": workflow_def  # Store the original workflow definition
        }
        
        # Build input and output maps
        for node in workflow_def.nodes:
            graph["inputs"][node.id] = []
            graph["outputs"][node.id] = []
        
        for edge in workflow_def.edges:
            from_node = edge.from_node
            to_node = edge.to_node
            graph["outputs"][from_node].append((to_node, edge.condition))
            graph["inputs"][to_node].append(from_node)
        
        # Identify entry and exit nodes
        for node_id, inputs in graph["inputs"].items():
            if not inputs:
                graph["entry_nodes"].append(node_id)
        
        for node_id, outputs in graph["outputs"].items():
            if not outputs:
                graph["exit_nodes"].append(node_id)
        
        return graph
    
    async def _execute_graph(
        self, 
        graph: Dict[str, Any], 
        context: ExecutionContext, 
        trace: ExecutionTrace
    ) -> Dict[str, Any]:
        """
        Execute a workflow graph.
        
        Args:
            graph: Execution graph representation
            context: Execution context
            trace: Execution trace
            
        Returns:
            Outputs from the workflow execution
        """
        # Track node execution status
        node_status = {node_id: "pending" for node_id in graph["nodes"]}
        node_outputs = {}
        
        # Execute the graph using a level-based approach for parallelism
        await self._execute_graph_with_parallelism(graph, context, trace, node_status, node_outputs)
        
        # Collect outputs from exit nodes
        outputs = {}
        for node_id in graph["exit_nodes"]:
            if node_id in node_outputs:
                outputs.update(node_outputs[node_id])
        
        return outputs
        
    async def _execute_graph_with_parallelism(
        self,
        graph: Dict[str, Any],
        context: ExecutionContext,
        trace: ExecutionTrace,
        node_status: Dict[str, str],
        node_outputs: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Execute a workflow graph with parallel execution support.
        
        This method uses a level-based approach to identify nodes that can be
        executed in parallel at each step of the workflow execution.
        
        Args:
            graph: Execution graph representation
            context: Execution context
            trace: Execution trace
            node_status: Map of node ID to execution status
            node_outputs: Map of node ID to node outputs
        """
        # Continue execution until all nodes are processed
        while True:
            # Find all nodes that are ready for execution
            ready_nodes = []
            for node_id in graph["nodes"]:
                # Skip if already processed or in progress
                if node_status[node_id] != "pending":
                    continue
                
                # Check if all dependencies are satisfied
                dependencies_satisfied = True
                for input_node_id in graph["inputs"][node_id]:
                    if node_status[input_node_id] != "completed":
                        dependencies_satisfied = False
                        break
                
                if dependencies_satisfied:
                    ready_nodes.append(node_id)
            
            # If no nodes are ready, we're done
            if not ready_nodes:
                # Check if all nodes are completed or failed
                all_processed = all(status in ["completed", "failed"] for status in node_status.values())
                if all_processed:
                    break
                else:
                    # This could indicate a cycle in the graph
                    self.logger.warning("No nodes ready for execution but not all nodes processed")
                    # Find unprocessed nodes
                    unprocessed = [node_id for node_id, status in node_status.items() if status == "pending"]
                    self.logger.warning(f"Unprocessed nodes: {unprocessed}")
                    break
            
            # Group nodes by parallel group
            grouped_nodes = {}
            ungrouped_nodes = []
            
            for node_id in ready_nodes:
                node = graph["nodes"][node_id]
                if hasattr(node, "parallel_group") and node.parallel_group:
                    if node.parallel_group not in grouped_nodes:
                        grouped_nodes[node.parallel_group] = []
                    grouped_nodes[node.parallel_group].append(node_id)
                else:
                    ungrouped_nodes.append(node_id)
            
            # Execute each group with its own concurrency settings
            all_results = {}
            all_errors = {}
            
            # Execute grouped nodes
            for group_id, group_nodes in grouped_nodes.items():
                # Get group configuration
                group_config = graph.get("workflow_def", {}).metadata.get("parallel_groups", {}).get(group_id, {})
                max_concurrency = group_config.get("max_concurrency", 5)
                timeout = group_config.get("timeout", None)
                
                self.logger.info(f"Executing parallel group {group_id} with {len(group_nodes)} nodes")
                
                # Execute group
                group_results, group_errors = await self.parallel_execution_manager.execute_nodes_in_parallel(
                    group_nodes,
                    lambda node_id: self._execute_single_node_wrapper(node_id, graph, context, trace, node_status, node_outputs),
                    trace,
                    max_concurrency=max_concurrency,
                    timeout=timeout
                )
                
                all_results.update(group_results)
                all_errors.update(group_errors)
            
            # Execute ungrouped nodes
            if ungrouped_nodes:
                self.logger.info(f"Executing {len(ungrouped_nodes)} ungrouped nodes")
                
                ungrouped_results, ungrouped_errors = await self.parallel_execution_manager.execute_nodes_in_parallel(
                    ungrouped_nodes,
                    lambda node_id: self._execute_single_node_wrapper(node_id, graph, context, trace, node_status, node_outputs),
                    trace,
                    max_concurrency=min(len(ungrouped_nodes), 5)  # Default concurrency
                )
                
                all_results.update(ungrouped_results)
                all_errors.update(ungrouped_errors)
            
            # Update node outputs with results
            for node_id, result in all_results.items():
                node_outputs[node_id] = result
                context.state["node_outputs"][node_id] = result
            
            # Handle errors
            for node_id, error in all_errors.items():
                node_status[node_id] = "failed"
                # Error details are already recorded in the trace by _execute_single_node
    
    async def _execute_single_node_wrapper(
        self,
        node_id: str,
        graph: Dict[str, Any],
        context: ExecutionContext,
        trace: ExecutionTrace,
        node_status: Dict[str, str],
        node_outputs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Wrapper for executing a single node in parallel.
        
        Args:
            node_id: ID of the node to execute
            graph: Execution graph representation
            context: Execution context
            trace: Execution trace
            node_status: Map of node ID to execution status
            node_outputs: Map of node ID to node outputs
            
        Returns:
            Node execution outputs
        """
        # Mark as running
        node_status[node_id] = "running"
        
        # Create node-specific context
        node_context = context.create_child_context(node_id)
        node_context.mark_started()
        
        try:
            # Execute the node
            result = await self._execute_single_node(node_id, graph, node_context, trace, node_outputs)
            
            # Mark as completed
            node_status[node_id] = "completed"
            node_context.mark_completed()
            
            return result
        except Exception:
            # Mark as failed
            node_status[node_id] = "failed"
            node_context.mark_failed()
            raise
    
    async def _execute_node(
        self,
        node_id: str,
        graph: Dict[str, Any],
        context: ExecutionContext,
        trace: ExecutionTrace,
        node_status: Dict[str, str],
        node_outputs: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Execute a single node in the workflow.
        
        This method is kept for backward compatibility but delegates to the new
        parallel execution approach.
        
        Args:
            node_id: ID of the node to execute
            graph: Execution graph representation
            context: Execution context
            trace: Execution trace
            node_status: Map of node ID to execution status
            node_outputs: Map of node ID to node outputs
        """
        # Skip if already executed or failed
        if node_status[node_id] in ["completed", "failed"]:
            return
        
        # Check if all input nodes are completed
        for input_node_id in graph["inputs"][node_id]:
            if node_status[input_node_id] != "completed":
                # Can't execute yet, wait for inputs
                return
        
        # Mark as running
        node_status[node_id] = "running"
        
        # Create node-specific context
        node_context = context.create_child_context(node_id)
        node_context.mark_started()
        
        try:
            # Execute the node
            outputs = await self._execute_single_node(node_id, graph, node_context, trace, node_outputs)
            
            # Store outputs
            node_outputs[node_id] = outputs
            context.state["node_outputs"][node_id] = outputs
            
            # Mark as completed
            node_status[node_id] = "completed"
            node_context.mark_completed()
            
            # Execute successor nodes
            for to_node, condition in graph["outputs"][node_id]:
                # Check condition if present
                if condition:
                    # In a real implementation, we would evaluate the condition
                    # For now, we'll just assume it's true
                    pass
                
                await self._execute_node(to_node, graph, context, trace, node_status, node_outputs)
        
        except Exception:
            # Mark as failed
            node_status[node_id] = "failed"
            node_context.mark_failed()
            raise
    
    async def _execute_single_node(
        self,
        node_id: str,
        graph: Dict[str, Any],
        node_context: ExecutionContext,
        trace: ExecutionTrace,
        node_outputs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a single node in the workflow.
        
        Args:
            node_id: ID of the node to execute
            graph: Execution graph representation
            node_context: Node-specific execution context
            trace: Execution trace
            node_outputs: Map of node ID to node outputs
            
        Returns:
            Node execution outputs
        """
        # Get node definition
        node = graph["nodes"][node_id]
        
        # Collect inputs from predecessor nodes
        inputs = {}
        for input_node_id in graph["inputs"][node_id]:
            if input_node_id in node_outputs:
                inputs.update(node_outputs[input_node_id])
        
        # Add parameters from context
        inputs.update(node_context.state.get("params", {}))
        
        # Get primitive instance
        primitive_type = node.type
        primitive_class = self.primitive_registry.get_primitive(primitive_type)
        if not primitive_class:
            error_msg = f"Unknown primitive type '{primitive_type}' for node '{node_id}'"
            self.logger.error(error_msg)
            
            # Record execution step
            step = ExecutionStep(
                node_id=node_id,
                node_type=primitive_type,
                inputs=inputs,
                outputs={},
                start_time=node_context.start_time,
                end_time=datetime.now(),
                duration_ms=(datetime.now() - node_context.start_time).total_seconds() * 1000,
                status="failed",
                error=error_msg
            )
            trace.add_step(step)
            
            # Mark context as failed
            node_context.mark_failed()
            raise ValueError(error_msg)
        
        # Instantiate primitive
        primitive = primitive_class(primitive_id=node_id, config=node.config)
        
        try:
            # Execute primitive
            self.logger.info(f"Executing node '{node_id}' of type '{primitive_type}'")
            outputs = await primitive.execute(inputs, node_context)
            
            # Record execution step
            step = ExecutionStep(
                node_id=node_id,
                node_type=primitive_type,
                inputs=inputs,
                outputs=outputs,
                start_time=node_context.start_time,
                end_time=datetime.now(),
                duration_ms=(datetime.now() - node_context.start_time).total_seconds() * 1000,
                status="completed"
            )
            trace.add_step(step)
            
            return outputs
        
        except Exception as e:
            error_msg = f"Error executing node '{node_id}': {e}"
            self.logger.error(error_msg)
            
            # Record execution step
            step = ExecutionStep(
                node_id=node_id,
                node_type=primitive_type,
                inputs=inputs,
                outputs={},
                start_time=node_context.start_time,
                end_time=datetime.now(),
                duration_ms=(datetime.now() - node_context.start_time).total_seconds() * 1000,
                status="failed",
                error=str(e)
            )
            trace.add_step(step)
            
            # Mark context as failed
            node_context.mark_failed()
            raise
    
    def _calculate_metrics(self, trace: ExecutionTrace) -> Dict[str, Any]:
        """
        Calculate metrics from an execution trace.
        
        Args:
            trace: Execution trace
            
        Returns:
            Dictionary of metrics
        """
        if not trace.steps:
            return {}
        
        # Calculate basic metrics
        total_duration = sum(step.duration_ms for step in trace.steps)
        avg_duration = total_duration / len(trace.steps)
        max_duration = max(step.duration_ms for step in trace.steps)
        min_duration = min(step.duration_ms for step in trace.steps)
        
        # Count by status
        completed_count = sum(1 for step in trace.steps if step.status == "completed")
        failed_count = sum(1 for step in trace.steps if step.status == "failed")
        
        # Count by node type
        node_type_counts = {}
        for step in trace.steps:
            node_type = step.node_type
            if node_type not in node_type_counts:
                node_type_counts[node_type] = 0
            node_type_counts[node_type] += 1
        
        return {
            "total_duration_ms": total_duration,
            "avg_duration_ms": avg_duration,
            "max_duration_ms": max_duration,
            "min_duration_ms": min_duration,
            "total_steps": len(trace.steps),
            "completed_steps": completed_count,
            "failed_steps": failed_count,
            "success_rate": completed_count / len(trace.steps) if trace.steps else 0,
            "node_type_counts": node_type_counts
        }
    
    async def _cleanup_workflow(self, execution_id: str, delay: float = 3600) -> None:
        """
        Clean up a workflow after a delay.
        
        Args:
            execution_id: ID of the workflow execution
            delay: Delay in seconds before cleanup
        """
        await asyncio.sleep(delay)
        if execution_id in self.active_workflows:
            del self.active_workflows[execution_id]
            self.logger.info(f"Cleaned up workflow {execution_id}")
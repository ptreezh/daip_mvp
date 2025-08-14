"""Data models for the workflow orchestration engine.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NodeStatus(str, Enum):
    """Node execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowNode(BaseModel):
    """Definition of a workflow node."""

    id: str
    type: str  # Primitive type (e.g., "generation", "fact_extraction")
    config: Dict[str, Any] = Field(default_factory=dict)
    inputs: List[str] = Field(default_factory=list)  # Input parameter names
    outputs: List[str] = Field(default_factory=list)  # Output parameter names
    dependencies: List[str] = Field(default_factory=list)  # Node IDs this node depends on
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowEdge(BaseModel):
    """Definition of a workflow edge connecting nodes."""

    from_node: str
    to_node: str
    condition: Optional[str] = None  # Conditional execution expression
    data_mapping: Dict[str, str] = Field(default_factory=dict)  # Output->Input mapping
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowDefinition(BaseModel):
    """Complete workflow definition."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    version: str = "1.0.0"
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    parameters: Dict[str, Any] = Field(default_factory=dict)  # Workflow-level parameters
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def validate_structure(self) -> List[str]:
        """Validate the workflow structure and return list of errors."""
        errors = []

        # Check for duplicate node IDs
        node_ids = [node.id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            duplicates = [node_id for node_id in node_ids if node_ids.count(node_id) > 1]
            errors.append(f"Duplicate node IDs found: {list(set(duplicates))}")

        # Check edge references
        for edge in self.edges:
            if edge.from_node not in node_ids:
                errors.append(f"Edge references unknown from_node: {edge.from_node}")
            if edge.to_node not in node_ids:
                errors.append(f"Edge references unknown to_node: {edge.to_node}")

        # Check dependency references
        for node in self.nodes:
            for dep_id in node.dependencies:
                if dep_id not in node_ids:
                    errors.append(f"Node {node.id} has unknown dependency: {dep_id}")

        # Check for circular dependencies
        if self._has_circular_dependencies():
            errors.append("Circular dependencies detected in workflow")

        return errors

    def _has_circular_dependencies(self) -> bool:
        """Check if the workflow has circular dependencies."""
        # Build dependency graph
        graph = {node.id: node.dependencies for node in self.nodes}

        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()

        def has_cycle(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False

            visited.add(node_id)
            rec_stack.add(node_id)

            for dep in graph.get(node_id, []):
                if has_cycle(dep):
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in graph:
            if node_id not in visited:
                if has_cycle(node_id):
                    return True

        return False


class ExecutionStep(BaseModel):
    """Record of a single execution step."""

    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str
    node_type: str
    status: NodeStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    execution_time: float = 0.0  # Seconds
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionMetrics(BaseModel):
    """Metrics for workflow execution."""

    total_execution_time: float = 0.0  # Seconds
    node_count: int = 0
    successful_nodes: int = 0
    failed_nodes: int = 0
    skipped_nodes: int = 0
    parallel_efficiency: float = 0.0  # Ratio of parallel to sequential time
    memory_usage: Dict[str, float] = Field(default_factory=dict)  # Memory usage stats
    resource_utilization: Dict[str, float] = Field(default_factory=dict)
    bottlenecks: List[str] = Field(default_factory=list)  # Node IDs that were bottlenecks


class WorkflowExecution(BaseModel):
    """Runtime state of a workflow execution."""

    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    workflow_definition: WorkflowDefinition
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    current_step: Optional[str] = None  # Current node ID being executed
    execution_trace: List[ExecutionStep] = Field(default_factory=list)
    workflow_state: Dict[str, Any] = Field(default_factory=dict)  # Shared state across nodes
    node_outputs: Dict[str, Dict[str, Any]] = Field(default_factory=dict)  # Node ID -> outputs
    parameters: Dict[str, Any] = Field(default_factory=dict)  # Runtime parameters
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Runtime tracking
    node_states: Dict[str, NodeStatus] = Field(default_factory=dict)  # Node ID -> status
    completed_nodes: Set[str] = Field(default_factory=set)
    failed_nodes: Set[str] = Field(default_factory=set)
    current_nodes: Set[str] = Field(default_factory=set)  # Currently executing nodes

    def is_complete(self) -> bool:
        """Check if workflow execution is complete."""
        return self.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]

    def has_failed(self) -> bool:
        """Check if workflow execution has failed."""
        return self.status == WorkflowStatus.FAILED or len(self.failed_nodes) > 0

    def get_ready_nodes(self) -> List[str]:
        """Get list of node IDs that are ready for execution."""
        ready_nodes = []

        for node in self.workflow_definition.nodes:
            # Skip if already processed
            if node.id in self.completed_nodes or node.id in self.failed_nodes or node.id in self.current_nodes:
                continue

            # Check if all dependencies are satisfied
            dependencies_satisfied = True
            for dep_id in node.dependencies:
                if dep_id not in self.completed_nodes:
                    dependencies_satisfied = False
                    break

            if dependencies_satisfied:
                ready_nodes.append(node.id)

        return ready_nodes


class WorkflowResult(BaseModel):
    """Result of workflow execution."""

    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    outputs: Dict[str, Any] = Field(default_factory=dict)
    execution_trace: List[ExecutionStep] = Field(default_factory=list)
    metrics: ExecutionMetrics
    start_time: datetime
    end_time: Optional[datetime] = None
    total_execution_time: float = 0.0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowTemplate(BaseModel):
    """Template for creating workflow definitions."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    category: str = "general"
    template_definition: WorkflowDefinition
    parameter_schema: Dict[str, Any] = Field(default_factory=dict)  # JSON schema for parameters
    tags: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class WorkflowValidationResult(BaseModel):
    """Result of workflow definition validation."""

    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)  # Node dependencies
    execution_order: List[str] = Field(default_factory=list)  # Topological order of nodes


class ParallelExecutionGroup(BaseModel):
    """Group of nodes that can be executed in parallel."""

    group_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_ids: List[str]
    max_concurrency: int = 5
    timeout: Optional[float] = None  # Timeout in seconds
    retry_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

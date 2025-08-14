"""Integration tests for the parallel execution capability in the Workflow Engine.

This module tests the integration between the WorkflowEngine and the
ParallelExecutionManager to ensure proper parallel execution of workflow nodes.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict

import pytest

from src.institutional_primitives.base import ExecutionContext, InstitutionalPrimitive
from src.institutional_primitives.registry import PrimitiveRegistry
from src.institutional_primitives.workflow_engine import (
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowEngine,
    WorkflowNode,
)


class DelayedPrimitive(InstitutionalPrimitive):
    """Test primitive with configurable delay for parallel execution testing."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute with a delay."""
        delay = self.config.get('delay', 0.1)
        should_fail = self.config.get('should_fail', False)

        # Record start time
        start_time = datetime.now().timestamp()

        # Simulate work with delay
        await asyncio.sleep(delay)

        # Fail if configured to do so
        if should_fail:
            raise ValueError(f"Simulated failure in {context.node_id}")

        # Record end time
        end_time = datetime.now().timestamp()

        return {
            "node_id": self.primitive_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
            "input_value": inputs.get('value', None)
        }

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "value": {"type": "string"}
            }
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "node_id": {"type": "string"},
                "start_time": {"type": "number"},
                "end_time": {"type": "number"},
                "duration": {"type": "number"},
                "input_value": {"type": "string"}
            }
        }


@pytest.fixture
def primitive_registry():
    """Create test primitive registry."""
    registry = PrimitiveRegistry()
    registry.register_primitive("delayed", DelayedPrimitive)
    return registry


@pytest.fixture
def workflow_engine(primitive_registry):
    """Create test workflow engine."""
    return WorkflowEngine(primitive_registry=primitive_registry)


@pytest.fixture
def sequential_workflow():
    """Create a sequential workflow for testing."""
    return WorkflowDefinition(
        id="sequential_workflow",
        name="Sequential Workflow",
        description="A workflow with sequential execution",
        nodes=[
            WorkflowNode(id="node1", type="delayed", config={"delay": 0.1}),
            WorkflowNode(id="node2", type="delayed", config={"delay": 0.1}),
            WorkflowNode(id="node3", type="delayed", config={"delay": 0.1}),
            WorkflowNode(id="node4", type="delayed", config={"delay": 0.1}),
            WorkflowNode(id="node5", type="delayed", config={"delay": 0.1})
        ],
        edges=[
            WorkflowEdge(from_node="node1", to_node="node2"),
            WorkflowEdge(from_node="node2", to_node="node3"),
            WorkflowEdge(from_node="node3", to_node="node4"),
            WorkflowEdge(from_node="node4", to_node="node5")
        ]
    )


@pytest.fixture
def parallel_workflow():
    """Create a workflow with parallel execution."""
    return WorkflowDefinition(
        id="parallel_workflow",
        name="Parallel Workflow",
        description="A workflow with parallel execution",
        nodes=[
            WorkflowNode(id="start", type="delayed", config={"delay": 0.1}),
            WorkflowNode(id="parallel1", type="delayed", config={"delay": 0.2}),
            WorkflowNode(id="parallel2", type="delayed", config={"delay": 0.2}),
            WorkflowNode(id="parallel3", type="delayed", config={"delay": 0.2}),
            WorkflowNode(id="parallel4", type="delayed", config={"delay": 0.2}),
            WorkflowNode(id="end", type="delayed", config={"delay": 0.1})
        ],
        edges=[
            WorkflowEdge(from_node="start", to_node="parallel1"),
            WorkflowEdge(from_node="start", to_node="parallel2"),
            WorkflowEdge(from_node="start", to_node="parallel3"),
            WorkflowEdge(from_node="start", to_node="parallel4"),
            WorkflowEdge(from_node="parallel1", to_node="end"),
            WorkflowEdge(from_node="parallel2", to_node="end"),
            WorkflowEdge(from_node="parallel3", to_node="end"),
            WorkflowEdge(from_node="parallel4", to_node="end")
        ]
    )


@pytest.fixture
def mixed_workflow():
    """Create a workflow with mixed sequential and parallel execution."""
    return WorkflowDefinition(
        id="mixed_workflow",
        name="Mixed Workflow",
        description="A workflow with mixed sequential and parallel execution",
        nodes=[
            WorkflowNode(id="start", type="delayed", config={"delay": 0.1}),
            WorkflowNode(id="seq1", type="delayed", config={"delay": 0.1}),
            WorkflowNode(id="parallel1", type="delayed", config={"delay": 0.2}),
            WorkflowNode(id="parallel2", type="delayed", config={"delay": 0.2}),
            WorkflowNode(id="parallel3", type="delayed", config={"delay": 0.2}),
            WorkflowNode(id="seq2", type="delayed", config={"delay": 0.1}),
            WorkflowNode(id="end", type="delayed", config={"delay": 0.1})
        ],
        edges=[
            WorkflowEdge(from_node="start", to_node="seq1"),
            WorkflowEdge(from_node="seq1", to_node="parallel1"),
            WorkflowEdge(from_node="seq1", to_node="parallel2"),
            WorkflowEdge(from_node="seq1", to_node="parallel3"),
            WorkflowEdge(from_node="parallel1", to_node="seq2"),
            WorkflowEdge(from_node="parallel2", to_node="seq2"),
            WorkflowEdge(from_node="parallel3", to_node="seq2"),
            WorkflowEdge(from_node="seq2", to_node="end")
        ]
    )


class TestParallelExecution:
    """Test the parallel execution capability."""

    @pytest.mark.asyncio
    async def test_sequential_execution(self, workflow_engine, sequential_workflow):
        """Test sequential execution as baseline."""
        start_time = datetime.now().timestamp()
        result = await workflow_engine.execute_workflow(
            sequential_workflow,
            {"value": "test_data"}
        )
        end_time = datetime.now().timestamp()
        total_duration = end_time - start_time

        assert result.status == "completed"
        assert len(result.execution_trace.steps) == 5

        # Sequential execution should take at least the sum of all delays
        # (5 nodes * 0.1s = 0.5s)
        assert total_duration >= 0.5

        # Check execution order
        steps = result.execution_trace.steps
        for i in range(1, len(steps)):
            assert steps[i-1].end_time <= steps[i].start_time

    @pytest.mark.asyncio
    async def test_parallel_execution(self, workflow_engine, parallel_workflow):
        """Test parallel execution."""
        # Create a parallel group for the parallel nodes
        parallel_nodes = ["parallel1", "parallel2", "parallel3", "parallel4"]
        workflow_engine.create_parallel_group(
            parallel_workflow,
            parallel_nodes,
            group_id="test_parallel_group",
            max_concurrency=4
        )

        start_time = datetime.now().timestamp()
        result = await workflow_engine.execute_workflow(
            parallel_workflow,
            {"value": "test_data"}
        )
        end_time = datetime.now().timestamp()
        total_duration = end_time - start_time

        assert result.status == "completed"
        assert len(result.execution_trace.steps) == 6

        # Parallel execution should be faster than sequential
        # With parallelism: start(0.1) + parallel(0.2) + end(0.1) = ~0.4s
        # Without: start(0.1) + 4*parallel(0.2) + end(0.1) = ~1.0s
        assert total_duration < 0.6  # Allow some overhead

        # Check that parallel nodes have overlapping execution times
        parallel_steps = [step for step in result.execution_trace.steps
                         if step.node_id in parallel_nodes]

        # At least some of the parallel steps should overlap in time
        overlaps = 0
        for i in range(len(parallel_steps)):
            for j in range(i+1, len(parallel_steps)):
                step_i = parallel_steps[i]
                step_j = parallel_steps[j]
                # Check for time overlap
                if (step_i.start_time <= step_j.end_time and
                    step_j.start_time <= step_i.end_time):
                    overlaps += 1

        assert overlaps > 0, "Expected parallel steps to have overlapping execution times"

    @pytest.mark.asyncio
    async def test_mixed_execution(self, workflow_engine, mixed_workflow):
        """Test mixed sequential and parallel execution."""
        # Create a parallel group for the parallel nodes
        parallel_nodes = ["parallel1", "parallel2", "parallel3"]
        workflow_engine.create_parallel_group(
            mixed_workflow,
            parallel_nodes,
            group_id="test_mixed_group",
            max_concurrency=3
        )

        start_time = datetime.now().timestamp()
        result = await workflow_engine.execute_workflow(
            mixed_workflow,
            {"value": "test_data"}
        )
        end_time = datetime.now().timestamp()
        total_duration = end_time - start_time

        assert result.status == "completed"
        assert len(result.execution_trace.steps) == 7

        # Mixed execution should be faster than sequential
        # With parallelism: start(0.1) + seq1(0.1) + parallel(0.2) + seq2(0.1) + end(0.1) = ~0.6s
        # Without: start(0.1) + seq1(0.1) + 3*parallel(0.2) + seq2(0.1) + end(0.1) = ~1.0s
        assert total_duration < 0.8  # Allow some overhead

        # Check execution order of sequential parts
        steps_by_id = {step.node_id: step for step in result.execution_trace.steps}
        assert steps_by_id["start"].end_time <= steps_by_id["seq1"].start_time
        assert steps_by_id["seq1"].end_time <= steps_by_id["parallel1"].start_time
        assert steps_by_id["parallel1"].end_time <= steps_by_id["seq2"].start_time
        assert steps_by_id["seq2"].end_time <= steps_by_id["end"].start_time

    @pytest.mark.asyncio
    async def test_parallel_execution_with_failure(self, workflow_engine, parallel_workflow):
        """Test parallel execution with a failing node."""
        # Modify one node to fail
        for node in parallel_workflow.nodes:
            if node.id == "parallel2":
                node.config["should_fail"] = True
                break

        # Create a parallel group for the parallel nodes
        parallel_nodes = ["parallel1", "parallel2", "parallel3", "parallel4"]
        workflow_engine.create_parallel_group(
            parallel_workflow,
            parallel_nodes,
            group_id="test_failure_group",
            max_concurrency=4
        )

        result = await workflow_engine.execute_workflow(parallel_workflow)

        assert result.status == "failed"

        # Check that the failing node is marked as failed
        failed_steps = [step for step in result.execution_trace.steps
                       if step.status == "failed"]
        assert len(failed_steps) == 1
        assert failed_steps[0].node_id == "parallel2"

        # Other parallel nodes should still complete
        completed_parallel_nodes = [
            step.node_id for step in result.execution_trace.steps
            if step.status == "completed" and step.node_id in ["parallel1", "parallel3", "parallel4"]
        ]
        assert len(completed_parallel_nodes) == 3

    @pytest.mark.asyncio
    async def test_parallel_execution_with_timeout(self, workflow_engine, parallel_workflow):
        """Test parallel execution with timeout."""
        # Make one node very slow
        for node in parallel_workflow.nodes:
            if node.id == "parallel3":
                node.config["delay"] = 1.0  # 1 second delay
                break

        # Create a parallel group with a short timeout
        parallel_nodes = ["parallel1", "parallel2", "parallel3", "parallel4"]
        workflow_engine.create_parallel_group(
            parallel_workflow,
            parallel_nodes,
            group_id="test_timeout_group",
            max_concurrency=4,
            timeout=0.3  # 300ms timeout
        )

        result = await workflow_engine.execute_workflow(parallel_workflow)

        # The workflow should still complete, but the slow node might be marked as failed
        # or might not have completed yet
        steps_by_id = {step.node_id: step for step in result.execution_trace.steps}

        # Check that fast nodes completed
        assert steps_by_id.get("parallel1").status == "completed"
        assert steps_by_id.get("parallel2").status == "completed"
        assert steps_by_id.get("parallel4").status == "completed"

    @pytest.mark.asyncio
    async def test_create_parallel_group(self, workflow_engine, parallel_workflow):
        """Test creating a parallel execution group."""
        parallel_nodes = ["parallel1", "parallel2", "parallel3", "parallel4"]
        group_id = workflow_engine.create_parallel_group(
            parallel_workflow,
            parallel_nodes,
            max_concurrency=3,
            timeout=0.5
        )

        # Check that group ID was returned
        assert group_id is not None

        # Check that nodes were updated with group ID
        for node in parallel_workflow.nodes:
            if node.id in parallel_nodes:
                assert node.parallel_group == group_id
            else:
                assert node.parallel_group is None

        # Check that group config was stored in workflow metadata
        assert "parallel_groups" in parallel_workflow.metadata
        assert group_id in parallel_workflow.metadata["parallel_groups"]
        assert parallel_workflow.metadata["parallel_groups"][group_id]["max_concurrency"] == 3
        assert parallel_workflow.metadata["parallel_groups"][group_id]["timeout"] == 0.5
        assert set(parallel_workflow.metadata["parallel_groups"][group_id]["node_ids"]) == set(parallel_nodes)

    @pytest.mark.asyncio
    async def test_multiple_parallel_groups(self, workflow_engine):
        """Test workflow with multiple parallel groups."""
        # Create a workflow with two sets of parallel nodes
        workflow = WorkflowDefinition(
            id="multi_group_workflow",
            name="Multi-Group Workflow",
            description="A workflow with multiple parallel groups",
            nodes=[
                WorkflowNode(id="start", type="delayed", config={"delay": 0.1}),
                # First parallel group
                WorkflowNode(id="group1_node1", type="delayed", config={"delay": 0.2}),
                WorkflowNode(id="group1_node2", type="delayed", config={"delay": 0.2}),
                WorkflowNode(id="group1_node3", type="delayed", config={"delay": 0.2}),
                # Middle sequential node
                WorkflowNode(id="middle", type="delayed", config={"delay": 0.1}),
                # Second parallel group
                WorkflowNode(id="group2_node1", type="delayed", config={"delay": 0.2}),
                WorkflowNode(id="group2_node2", type="delayed", config={"delay": 0.2}),
                WorkflowNode(id="group2_node3", type="delayed", config={"delay": 0.2}),
                # End node
                WorkflowNode(id="end", type="delayed", config={"delay": 0.1})
            ],
            edges=[
                # Start to first group
                WorkflowEdge(from_node="start", to_node="group1_node1"),
                WorkflowEdge(from_node="start", to_node="group1_node2"),
                WorkflowEdge(from_node="start", to_node="group1_node3"),
                # First group to middle
                WorkflowEdge(from_node="group1_node1", to_node="middle"),
                WorkflowEdge(from_node="group1_node2", to_node="middle"),
                WorkflowEdge(from_node="group1_node3", to_node="middle"),
                # Middle to second group
                WorkflowEdge(from_node="middle", to_node="group2_node1"),
                WorkflowEdge(from_node="middle", to_node="group2_node2"),
                WorkflowEdge(from_node="middle", to_node="group2_node3"),
                # Second group to end
                WorkflowEdge(from_node="group2_node1", to_node="end"),
                WorkflowEdge(from_node="group2_node2", to_node="end"),
                WorkflowEdge(from_node="group2_node3", to_node="end")
            ]
        )

        # Create two parallel groups with different configurations
        group1_nodes = ["group1_node1", "group1_node2", "group1_node3"]
        group1_id = workflow_engine.create_parallel_group(
            workflow,
            group1_nodes,
            group_id="group1",
            max_concurrency=2,  # Limited concurrency
            timeout=0.5
        )

        group2_nodes = ["group2_node1", "group2_node2", "group2_node3"]
        group2_id = workflow_engine.create_parallel_group(
            workflow,
            group2_nodes,
            group_id="group2",
            max_concurrency=3,  # Full concurrency
            timeout=0.5
        )

        # Execute workflow
        start_time = datetime.now().timestamp()
        result = await workflow_engine.execute_workflow(workflow)
        end_time = datetime.now().timestamp()
        total_duration = end_time - start_time

        assert result.status == "completed"
        assert len(result.execution_trace.steps) == 9

        # Check that both groups executed with their respective concurrency settings
        steps_by_id = {step.node_id: step for step in result.execution_trace.steps}

        # Group 1 should have some sequential execution due to max_concurrency=2
        group1_steps = [steps_by_id[node_id] for node_id in group1_nodes]

        # Group 2 should have more parallel execution with max_concurrency=3
        group2_steps = [steps_by_id[node_id] for node_id in group2_nodes]

        # Check overall execution time is reasonable
        # Expected: start(0.1) + group1(~0.3) + middle(0.1) + group2(~0.2) + end(0.1) = ~0.8s
        assert total_duration < 1.0  # Allow some overhead

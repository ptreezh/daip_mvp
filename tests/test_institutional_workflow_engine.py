"""Unit tests for the Institutional Primitives Workflow Engine.
"""

import asyncio
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


class TestPrimitive(InstitutionalPrimitive):
    """Test primitive for workflow testing."""

    def __init__(self, primitive_id: str, config: Dict[str, Any] = None):
        super().__init__(primitive_id, config)
        self.execution_count = 0
        self.should_fail = config.get('should_fail', False) if config else False
        self.delay = config.get('delay', 0.0) if config else 0.0

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Test execution."""
        self.execution_count += 1

        if self.delay > 0:
            await asyncio.sleep(self.delay)

        if self.should_fail:
            raise ValueError("Simulated failure")

        return {
            "result": f"Processed: {inputs.get('input', 'no input')}",
            "execution_count": self.execution_count,
            "node_id": context.node_id
        }

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            }
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string"},
                "execution_count": {"type": "integer"},
                "node_id": {"type": "string"}
            },
            "required": ["result", "execution_count", "node_id"]
        }


class SlowPrimitive(InstitutionalPrimitive):
    """Slow primitive for testing timeouts."""

    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        await asyncio.sleep(0.5)  # 0.5 second delay
        return {"result": "slow_result"}

    def get_input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {"result": {"type": "string"}},
            "required": ["result"]
        }


@pytest.fixture
def primitive_registry():
    """Create test primitive registry."""
    registry = PrimitiveRegistry()
    registry.register_primitive("test", TestPrimitive)
    registry.register_primitive("slow", SlowPrimitive)
    return registry


@pytest.fixture
def workflow_engine(primitive_registry):
    """Create test workflow engine."""
    return WorkflowEngine(primitive_registry=primitive_registry)


@pytest.fixture
def simple_workflow():
    """Create simple test workflow."""
    return WorkflowDefinition(
        id="simple_workflow",
        name="Simple Test Workflow",
        description="A simple workflow for testing",
        nodes=[
            WorkflowNode(
                id="node1",
                type="test",
                config={"test_param": "value1"}
            ),
            WorkflowNode(
                id="node2",
                type="test",
                config={"test_param": "value2"}
            )
        ],
        edges=[
            WorkflowEdge(
                from_node="node1",
                to_node="node2"
            )
        ]
    )


@pytest.fixture
def parallel_workflow():
    """Create parallel test workflow."""
    return WorkflowDefinition(
        id="parallel_workflow",
        name="Parallel Test Workflow",
        description="A workflow with parallel nodes",
        nodes=[
            WorkflowNode(id="node1", type="test"),
            WorkflowNode(id="node2", type="test"),
            WorkflowNode(id="node3", type="test"),
            WorkflowNode(id="node4", type="test")
        ],
        edges=[
            WorkflowEdge(from_node="node1", to_node="node4"),
            WorkflowEdge(from_node="node2", to_node="node4"),
            WorkflowEdge(from_node="node3", to_node="node4")
        ]
    )


@pytest.fixture
def failing_workflow():
    """Create workflow with a failing node."""
    return WorkflowDefinition(
        id="failing_workflow",
        name="Failing Workflow",
        description="A workflow with a failing node",
        nodes=[
            WorkflowNode(id="good_node", type="test"),
            WorkflowNode(id="bad_node", type="test", config={"should_fail": True})
        ],
        edges=[]
    )


class TestWorkflowEngine:
    """Test the workflow engine."""

    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self, workflow_engine, simple_workflow):
        """Test executing a simple workflow."""
        result = await workflow_engine.execute_workflow(
            simple_workflow,
            {"input": "test_data"}
        )

        assert result.status == "completed"
        assert len(result.execution_trace.steps) == 2
        assert "result" in result.outputs
        assert "Processed: test_data" in result.outputs["result"]

    @pytest.mark.asyncio
    async def test_execute_parallel_workflow(self, workflow_engine, parallel_workflow):
        """Test executing a workflow with parallel execution."""
        result = await workflow_engine.execute_workflow(
            parallel_workflow,
            {"input": "parallel_data"}
        )

        assert result.status == "completed"
        assert len(result.execution_trace.steps) == 4

    @pytest.mark.asyncio
    async def test_execute_failing_workflow(self, workflow_engine, failing_workflow):
        """Test executing a workflow with a failing node."""
        result = await workflow_engine.execute_workflow(failing_workflow)

        assert result.status == "failed"
        assert any(step.status == "failed" for step in result.execution_trace.steps)

    @pytest.mark.asyncio
    async def test_get_workflow_status(self, workflow_engine, simple_workflow):
        """Test getting workflow status."""
        # Start workflow execution
        execution_task = asyncio.create_task(
            workflow_engine.execute_workflow(simple_workflow)
        )

        # Wait a bit to ensure workflow has started
        await asyncio.sleep(0.1)

        # Get active workflows
        active_workflows = list(workflow_engine.active_workflows.keys())
        assert len(active_workflows) > 0

        # Get status
        status = workflow_engine.get_workflow_status(active_workflows[0])
        assert status is not None
        assert status.workflow_id == simple_workflow.id

        # Wait for completion
        await execution_task

    @pytest.mark.asyncio
    async def test_pause_and_resume_workflow(self, workflow_engine):
        """Test pausing and resuming a workflow."""
        slow_workflow = WorkflowDefinition(
            id="slow_workflow",
            name="Slow Workflow",
            description="A workflow with slow nodes",
            nodes=[
                WorkflowNode(id="slow1", type="slow"),
                WorkflowNode(id="slow2", type="slow")
            ],
            edges=[
                WorkflowEdge(from_node="slow1", to_node="slow2")
            ]
        )

        # Start workflow execution
        execution_task = asyncio.create_task(
            workflow_engine.execute_workflow(slow_workflow)
        )

        # Wait a bit to ensure workflow has started
        await asyncio.sleep(0.1)

        # Get active workflows
        active_workflows = list(workflow_engine.active_workflows.keys())
        assert len(active_workflows) > 0

        # Pause workflow
        execution_id = active_workflows[0]
        pause_result = await workflow_engine.pause_workflow(execution_id)
        assert pause_result

        # Check status
        status = workflow_engine.get_workflow_status(execution_id)
        assert status.status == "paused"

        # Resume workflow
        resume_result = await workflow_engine.resume_workflow(execution_id)
        assert resume_result

        # Wait for completion
        result = await execution_task
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_cancel_workflow(self, workflow_engine):
        """Test cancelling a workflow."""
        slow_workflow = WorkflowDefinition(
            id="slow_workflow",
            name="Slow Workflow",
            description="A workflow with slow nodes",
            nodes=[
                WorkflowNode(id="slow1", type="slow"),
                WorkflowNode(id="slow2", type="slow")
            ],
            edges=[
                WorkflowEdge(from_node="slow1", to_node="slow2")
            ]
        )

        # Start workflow execution
        execution_task = asyncio.create_task(
            workflow_engine.execute_workflow(slow_workflow)
        )

        # Wait a bit to ensure workflow has started
        await asyncio.sleep(0.1)

        # Get active workflows
        active_workflows = list(workflow_engine.active_workflows.keys())
        assert len(active_workflows) > 0

        # Cancel workflow
        execution_id = active_workflows[0]
        cancel_result = await workflow_engine.cancel_workflow(execution_id)
        assert cancel_result

        # Check status
        status = workflow_engine.get_workflow_status(execution_id)
        assert status.status == "cancelled"

        # Wait for completion
        result = await execution_task
        assert result.status == "cancelled"

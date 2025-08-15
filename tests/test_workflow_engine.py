"""Unit tests for workflow orchestration engine.
"""

import asyncio
import shutil
import tempfile
from datetime import datetime
from typing import Any

import pytest

from src.virtual_role_chat.institutional_primitives.base import (
    ExecutionContext,
    ExecutionResult,
    InstitutionalPrimitive,
)
from src.virtual_role_chat.institutional_primitives.registry import PrimitiveRegistry
from src.virtual_role_chat.workflow_engine.engine import WorkflowEngine
from src.virtual_role_chat.workflow_engine.execution_manager import ExecutionManager
from src.virtual_role_chat.workflow_engine.models import (
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowNode,
    WorkflowStatus,
)
from src.virtual_role_chat.workflow_engine.state_manager import StateManager


class TestPrimitive(InstitutionalPrimitive):
    """Test primitive for workflow testing."""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.execution_count = 0
        self.should_fail = config.get('should_fail', False) if config else False
        self.delay = config.get('delay', 0.0) if config else 0.0
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> ExecutionResult:
        """Test execution."""
        self.execution_count += 1
        
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        if self.should_fail:
            return ExecutionResult(
                success=False,
                errors=["Simulated failure"]
            )
        
        return ExecutionResult(
            success=True,
            outputs={
                "result": f"Processed: {inputs.get('input', 'no input')}",
                "execution_count": self.execution_count,
                "node_id": context.node_id
            }
        )
    
    def get_input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "input": {"type": "string"}
            }
        }
    
    def get_output_schema(self) -> dict[str, Any]:
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
    
    async def execute(self, inputs: dict[str, Any], context: ExecutionContext) -> ExecutionResult:
        await asyncio.sleep(2.0)  # 2 second delay
        return ExecutionResult(
            success=True,
            outputs={"result": "slow_result"}
        )
    
    def get_input_schema(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}
    
    def get_output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"result": {"type": "string"}},
            "required": ["result"]
        }


@pytest.fixture()
def temp_dir():
    """Create temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture()
def primitive_registry():
    """Create test primitive registry."""
    registry = PrimitiveRegistry()
    registry.register_primitive("test", TestPrimitive)
    registry.register_primitive("slow", SlowPrimitive)
    return registry


@pytest.fixture()
def state_manager(temp_dir):
    """Create test state manager."""
    return StateManager(temp_dir)


@pytest.fixture()
def workflow_engine(primitive_registry, state_manager):
    """Create test workflow engine."""
    return WorkflowEngine(
        primitive_registry=primitive_registry,
        state_manager=state_manager,
        node_timeout=1.0  # Short timeout for testing
    )


@pytest.fixture()
def simple_workflow():
    """Create simple test workflow."""
    return WorkflowDefinition(
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
                config={"test_param": "value2"},
                dependencies=["node1"]
            )
        ],
        edges=[
            WorkflowEdge(
                from_node="node1",
                to_node="node2",
                data_mapping={"result": "input"}
            )
        ]
    )


@pytest.fixture()
def parallel_workflow():
    """Create parallel test workflow."""
    return WorkflowDefinition(
        name="Parallel Test Workflow",
        description="A workflow with parallel nodes",
        nodes=[
            WorkflowNode(id="node1", type="test"),
            WorkflowNode(id="node2", type="test"),
            WorkflowNode(id="node3", type="test"),
            WorkflowNode(
                id="node4", 
                type="test",
                dependencies=["node1", "node2", "node3"]
            )
        ],
        edges=[
            WorkflowEdge(from_node="node1", to_node="node4"),
            WorkflowEdge(from_node="node2", to_node="node4"),
            WorkflowEdge(from_node="node3", to_node="node4")
        ]
    )


class TestWorkflowModels:
    """Test workflow data models."""
    
    def test_workflow_definition_creation(self):
        """Test creating workflow definition."""
        workflow = WorkflowDefinition(
            name="Test Workflow",
            nodes=[WorkflowNode(id="node1", type="test")],
            edges=[]
        )
        
        assert workflow.name == "Test Workflow"
        assert len(workflow.nodes) == 1
        assert workflow.nodes[0].id == "node1"
        assert workflow.id is not None
        assert isinstance(workflow.created_at, datetime)
    
    def test_workflow_validation_success(self):
        """Test successful workflow validation."""
        workflow = WorkflowDefinition(
            name="Valid Workflow",
            nodes=[
                WorkflowNode(id="node1", type="test"),
                WorkflowNode(id="node2", type="test")
            ],
            edges=[
                WorkflowEdge(from_node="node1", to_node="node2")
            ]
        )
        
        errors = workflow.validate_structure()
        assert len(errors) == 0
    
    def test_workflow_validation_duplicate_nodes(self):
        """Test workflow validation with duplicate node IDs."""
        workflow = WorkflowDefinition(
            name="Invalid Workflow",
            nodes=[
                WorkflowNode(id="node1", type="test"),
                WorkflowNode(id="node1", type="test")  # Duplicate ID
            ],
            edges=[]
        )
        
        errors = workflow.validate_structure()
        assert len(errors) > 0
        assert "Duplicate node IDs" in errors[0]
    
    def test_workflow_validation_invalid_edge(self):
        """Test workflow validation with invalid edge reference."""
        workflow = WorkflowDefinition(
            name="Invalid Workflow",
            nodes=[WorkflowNode(id="node1", type="test")],
            edges=[
                WorkflowEdge(from_node="node1", to_node="nonexistent")
            ]
        )
        
        errors = workflow.validate_structure()
        assert len(errors) > 0
        assert any("unknown" in error.lower() for error in errors)


class TestStateManager:
    """Test workflow state management."""
    
    @pytest.mark.asyncio()
    async def test_save_and_load_execution_state(self, state_manager, simple_workflow):
        """Test saving and loading execution state."""
        from src.virtual_role_chat.workflow_engine.models import WorkflowExecution
        
        execution = WorkflowExecution(
            workflow_definition=simple_workflow,
            status=WorkflowStatus.RUNNING,
            parameters={"test_param": "test_value"}
        )
        
        # Save state
        success = await state_manager.save_execution_state(execution)
        assert success
        
        # Load state
        loaded_execution = await state_manager.load_execution_state(execution.execution_id)
        assert loaded_execution is not None
        assert loaded_execution.execution_id == execution.execution_id
        assert loaded_execution.status == WorkflowStatus.RUNNING
        assert loaded_execution.parameters == {"test_param": "test_value"}
    
    @pytest.mark.asyncio()
    async def test_load_nonexistent_execution(self, state_manager):
        """Test loading non-existent execution."""
        execution = await state_manager.load_execution_state("nonexistent")
        assert execution is None
    
    @pytest.mark.asyncio()
    async def test_delete_execution_state(self, state_manager, simple_workflow):
        """Test deleting execution state."""
        from src.virtual_role_chat.workflow_engine.models import WorkflowExecution
        
        execution = WorkflowExecution(workflow_definition=simple_workflow)
        
        # Save and verify
        await state_manager.save_execution_state(execution)
        loaded = await state_manager.load_execution_state(execution.execution_id)
        assert loaded is not None
        
        # Delete and verify
        success = await state_manager.delete_execution_state(execution.execution_id)
        assert success
        
        loaded = await state_manager.load_execution_state(execution.execution_id)
        assert loaded is None
    
    @pytest.mark.asyncio()
    async def test_list_executions(self, state_manager, simple_workflow):
        """Test listing executions."""
        from src.virtual_role_chat.workflow_engine.models import WorkflowExecution
        
        # Create multiple executions
        execution1 = WorkflowExecution(workflow_definition=simple_workflow, status=WorkflowStatus.RUNNING)
        execution2 = WorkflowExecution(workflow_definition=simple_workflow, status=WorkflowStatus.COMPLETED)
        
        await state_manager.save_execution_state(execution1)
        await state_manager.save_execution_state(execution2)
        
        # List all executions
        all_executions = await state_manager.list_executions()
        assert len(all_executions) >= 2
        assert execution1.execution_id in all_executions
        assert execution2.execution_id in all_executions
        
        # List by status
        running_executions = await state_manager.list_executions(WorkflowStatus.RUNNING)
        assert execution1.execution_id in running_executions
        assert execution2.execution_id not in running_executions


class TestExecutionManager:
    """Test workflow execution management."""
    
    @pytest.mark.asyncio()
    async def test_execute_single_node(self, primitive_registry):
        """Test executing a single node."""
        from src.virtual_role_chat.workflow_engine.models import WorkflowExecution
        
        execution_manager = ExecutionManager(primitive_registry)
        
        node = WorkflowNode(id="test_node", type="test", config={"test_param": "value"})
        execution = WorkflowExecution(
            workflow_definition=WorkflowDefinition(name="Test", nodes=[node], edges=[]),
            parameters={"input": "test_input"}
        )
        
        result = await execution_manager.execute_node(node, execution, {})
        
        assert result.success
        assert "result" in result.outputs
        assert "Processed: test_input" in result.outputs["result"]
        assert node.id in execution.completed_nodes
        assert node.id in execution.node_outputs
    
    @pytest.mark.asyncio()
    async def test_execute_node_failure(self, primitive_registry):
        """Test executing a node that fails."""
        from src.virtual_role_chat.workflow_engine.models import WorkflowExecution
        
        execution_manager = ExecutionManager(primitive_registry)
        
        node = WorkflowNode(id="fail_node", type="test", config={"should_fail": True})
        execution = WorkflowExecution(
            workflow_definition=WorkflowDefinition(name="Test", nodes=[node], edges=[])
        )
        
        result = await execution_manager.execute_node(node, execution, {})
        
        assert not result.success
        assert len(result.errors) > 0
        assert node.id in execution.failed_nodes
    
    @pytest.mark.asyncio()
    async def test_execute_nodes_parallel(self, primitive_registry):
        """Test parallel node execution."""
        from src.virtual_role_chat.workflow_engine.models import WorkflowExecution
        
        execution_manager = ExecutionManager(primitive_registry)
        
        nodes = [
            WorkflowNode(id="node1", type="test"),
            WorkflowNode(id="node2", type="test"),
            WorkflowNode(id="node3", type="test")
        ]
        
        execution = WorkflowExecution(
            workflow_definition=WorkflowDefinition(name="Test", nodes=nodes, edges=[])
        )
        
        start_time = datetime.now()
        results = await execution_manager.execute_nodes_parallel(nodes, execution, {})
        end_time = datetime.now()
        
        assert len(results) == 3
        assert all(result.success for result in results)
        assert len(execution.completed_nodes) == 3
        
        # Should complete faster than sequential execution
        execution_time = (end_time - start_time).total_seconds()
        assert execution_time < 1.0  # Should be much faster than 3 sequential executions


class TestWorkflowEngine:
    """Test main workflow engine."""
    
    @pytest.mark.asyncio()
    async def test_execute_simple_workflow(self, workflow_engine, simple_workflow):
        """Test executing a simple sequential workflow."""
        result = await workflow_engine.execute_workflow(
            simple_workflow,
            {"input": "test_data"}
        )
        
        assert result.status == WorkflowStatus.COMPLETED
        assert len(result.execution_trace) == 2  # Two nodes executed
        assert result.metrics.successful_nodes == 2
        assert result.metrics.failed_nodes == 0
        assert "node1.result" in result.outputs
        assert "node2.result" in result.outputs
    
    @pytest.mark.asyncio()
    async def test_execute_parallel_workflow(self, workflow_engine, parallel_workflow):
        """Test executing a workflow with parallel nodes."""
        result = await workflow_engine.execute_workflow(parallel_workflow)
        
        assert result.status == WorkflowStatus.COMPLETED
        assert len(result.execution_trace) == 4  # Four nodes executed
        assert result.metrics.successful_nodes == 4
        assert result.metrics.failed_nodes == 0
    
    @pytest.mark.asyncio()
    async def test_execute_workflow_with_failure(self, workflow_engine):
        """Test executing a workflow with node failure."""
        failing_workflow = WorkflowDefinition(
            name="Failing Workflow",
            nodes=[
                WorkflowNode(id="good_node", type="test"),
                WorkflowNode(id="bad_node", type="test", config={"should_fail": True})
            ],
            edges=[]
        )
        
        result = await workflow_engine.execute_workflow(failing_workflow)
        
        assert result.status == WorkflowStatus.FAILED
        assert result.metrics.failed_nodes > 0
        assert len(result.errors) > 0
    
    @pytest.mark.asyncio()
    async def test_execute_invalid_workflow(self, workflow_engine):
        """Test executing an invalid workflow."""
        invalid_workflow = WorkflowDefinition(
            name="Invalid Workflow",
            nodes=[WorkflowNode(id="node1", type="nonexistent_type")],
            edges=[]
        )
        
        result = await workflow_engine.execute_workflow(invalid_workflow)
        
        assert result.status == WorkflowStatus.FAILED
        assert len(result.errors) > 0
    
    @pytest.mark.asyncio()
    async def test_workflow_timeout(self, workflow_engine):
        """Test workflow node timeout."""
        timeout_workflow = WorkflowDefinition(
            name="Timeout Workflow",
            nodes=[WorkflowNode(id="slow_node", type="slow")],
            edges=[]
        )
        
        result = await workflow_engine.execute_workflow(timeout_workflow)
        
        assert result.status == WorkflowStatus.FAILED
        assert any("timeout" in error.lower() for error in result.errors)
    
    @pytest.mark.asyncio()
    async def test_pause_and_resume_workflow(self, workflow_engine):
        """Test pausing and resuming workflow execution."""
        slow_workflow = WorkflowDefinition(
            name="Slow Workflow",
            nodes=[
                WorkflowNode(id="node1", type="test", config={"delay": 0.5}),
                WorkflowNode(id="node2", type="test", config={"delay": 0.5})
            ],
            edges=[WorkflowEdge(from_node="node1", to_node="node2")]
        )
        
        # Start workflow execution
        execution_task = asyncio.create_task(
            workflow_engine.execute_workflow(slow_workflow)
        )
        
        # Wait a bit then pause
        await asyncio.sleep(0.1)
        active_executions = workflow_engine.get_active_executions()
        assert len(active_executions) > 0
        
        execution_id = active_executions[0]
        pause_success = await workflow_engine.pause_workflow(execution_id)
        assert pause_success
        
        # Check status
        status = await workflow_engine.get_workflow_status(execution_id)
        assert status == WorkflowStatus.PAUSED
        
        # Resume
        resume_success = await workflow_engine.resume_workflow(execution_id)
        assert resume_success
        
        # Wait for completion
        result = await execution_task
        assert result.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]
    
    @pytest.mark.asyncio()
    async def test_cancel_workflow(self, workflow_engine):
        """Test cancelling workflow execution."""
        slow_workflow = WorkflowDefinition(
            name="Slow Workflow",
            nodes=[WorkflowNode(id="slow_node", type="test", config={"delay": 2.0})],
            edges=[]
        )
        
        # Start workflow execution
        execution_task = asyncio.create_task(
            workflow_engine.execute_workflow(slow_workflow)
        )
        
        # Wait a bit then cancel
        await asyncio.sleep(0.1)
        active_executions = workflow_engine.get_active_executions()
        assert len(active_executions) > 0
        
        execution_id = active_executions[0]
        cancel_success = await workflow_engine.cancel_workflow(execution_id)
        assert cancel_success
        
        # Wait for task to complete
        result = await execution_task
        assert result.status == WorkflowStatus.CANCELLED
    
    @pytest.mark.asyncio()
    async def test_get_execution_details(self, workflow_engine, simple_workflow):
        """Test getting execution details."""
        result = await workflow_engine.execute_workflow(simple_workflow)
        
        details = await workflow_engine.get_execution_details(result.execution_id)
        assert details is not None
        assert details["execution_id"] == result.execution_id
        assert details["workflow_name"] == simple_workflow.name
        assert details["status"] == WorkflowStatus.COMPLETED.value
        assert details["total_nodes"] == 2
        assert details["completed_nodes"] == 2
    
    def test_get_engine_statistics(self, workflow_engine):
        """Test getting engine statistics."""
        stats = workflow_engine.get_engine_statistics()
        
        assert "active_workflows" in stats
        assert "registered_primitives" in stats
        assert "available_services" in stats
        assert "active_executions" in stats
        assert "max_parallel_nodes" in stats
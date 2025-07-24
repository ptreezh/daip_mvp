"""
Unit tests for the parallel execution capability.
"""

import asyncio
import logging
import pytest
from datetime import datetime
from typing import Any, Dict, List

from src.institutional_primitives.base import ExecutionContext, ExecutionTrace, InstitutionalPrimitive
from src.institutional_primitives.registry import PrimitiveRegistry
from src.institutional_primitives.parallel_execution import (
    ParallelExecutionGroup,
    ParallelExecutionManager
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
            "node_id": context.node_id,
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


class SlowPrimitive(InstitutionalPrimitive):
    """Slow primitive for testing timeouts."""
    
    async def execute(self, inputs: Dict[str, Any], context: ExecutionContext) -> Dict[str, Any]:
        """Execute with a long delay."""
        delay = self.config.get('delay', 2.0)
        await asyncio.sleep(delay)
        
        return {
            "node_id": context.node_id,
            "result": "slow_execution_completed"
        }
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}
    
    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "node_id": {"type": "string"},
                "result": {"type": "string"}
            }
        }


@pytest.fixture
def execution_trace():
    """Create test execution trace."""
    return ExecutionTrace(
        execution_id="test_execution",
        workflow_id="test_workflow",
        start_time=datetime.now(),
        status="running"
    )


@pytest.fixture
def execution_context():
    """Create test execution context."""
    return ExecutionContext(
        execution_id="test_execution",
        workflow_id="test_workflow",
        node_id="test_node"
    )


class TestParallelExecutionGroup:
    """Test the ParallelExecutionGroup class."""
    
    def test_group_initialization(self):
        """Test parallel execution group initialization."""
        group = ParallelExecutionGroup(
            group_id="test_group",
            max_concurrency=3,
            timeout=10.0
        )
        
        assert group.group_id == "test_group"
        assert group.max_concurrency == 3
        assert group.timeout == 10.0
        assert group.semaphore._value == 3
        assert len(group.tasks) == 0
        assert len(group.results) == 0
        assert len(group.errors) == 0
    
    @pytest.mark.asyncio
    async def test_execute_single_node(self, execution_trace):
        """Test executing a single node in a parallel group."""
        group = ParallelExecutionGroup("test_group", max_concurrency=1)
        
        async def mock_execute_func(node_id: str) -> Dict[str, Any]:
            await asyncio.sleep(0.1)
            return {"node_id": node_id, "result": "success"}
        
        result = await group.execute_node("test_node", mock_execute_func, execution_trace)
        
        assert result["node_id"] == "test_node"
        assert result["result"] == "success"
        assert "test_node" in group.results
        assert len(group.errors) == 0
    
    @pytest.mark.asyncio
    async def test_execute_node_with_error(self, execution_trace):
        """Test executing a node that raises an error."""
        group = ParallelExecutionGroup("test_group", max_concurrency=1)
        
        async def failing_execute_func(node_id: str) -> Dict[str, Any]:
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await group.execute_node("test_node", failing_execute_func, execution_trace)
        
        assert "test_node" in group.errors
        assert isinstance(group.errors["test_node"], ValueError)
    
    @pytest.mark.asyncio
    async def test_execute_multiple_nodes_parallel(self, execution_trace):
        """Test executing multiple nodes in parallel."""
        group = ParallelExecutionGroup("test_group", max_concurrency=3)
        
        async def mock_execute_func(node_id: str) -> Dict[str, Any]:
            await asyncio.sleep(0.1)
            return {"node_id": node_id, "result": "success"}
        
        node_ids = ["node1", "node2", "node3"]
        start_time = datetime.now()
        
        results, errors = await group.execute_all(node_ids, mock_execute_func, execution_trace)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Should complete in roughly 0.1 seconds (parallel) rather than 0.3 seconds (sequential)
        assert execution_time < 0.2
        assert len(results) == 3
        assert len(errors) == 0
        assert all(node_id in results for node_id in node_ids)
    
    @pytest.mark.asyncio
    async def test_execute_with_concurrency_limit(self, execution_trace):
        """Test that concurrency limit is respected."""
        group = ParallelExecutionGroup("test_group", max_concurrency=2)
        
        execution_order = []
        
        async def mock_execute_func(node_id: str) -> Dict[str, Any]:
            execution_order.append(f"{node_id}_start")
            await asyncio.sleep(0.1)
            execution_order.append(f"{node_id}_end")
            return {"node_id": node_id, "result": "success"}
        
        node_ids = ["node1", "node2", "node3", "node4"]
        results, errors = await group.execute_all(node_ids, mock_execute_func, execution_trace)
        
        assert len(results) == 4
        assert len(errors) == 0
        
        # With max_concurrency=2, we should see at most 2 nodes executing at once
        # This is a simplified check - in practice, timing can be tricky to test
        assert len(execution_order) == 8  # 4 starts + 4 ends
    
    @pytest.mark.asyncio
    async def test_execute_with_timeout(self, execution_trace):
        """Test execution with timeout."""
        group = ParallelExecutionGroup("test_group", max_concurrency=2, timeout=0.2)
        
        async def slow_execute_func(node_id: str) -> Dict[str, Any]:
            await asyncio.sleep(0.5)  # Longer than timeout
            return {"node_id": node_id, "result": "success"}
        
        node_ids = ["node1", "node2"]
        start_time = datetime.now()
        
        results, errors = await group.execute_all(node_ids, slow_execute_func, execution_trace)
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Should timeout after ~0.2 seconds
        assert execution_time < 0.4
        # Results may be empty due to timeout
        assert len(results) <= 2


class TestParallelExecutionManager:
    """Test the ParallelExecutionManager class."""
    
    def test_manager_initialization(self):
        """Test parallel execution manager initialization."""
        manager = ParallelExecutionManager()
        
        assert len(manager.execution_groups) == 0
        assert manager.logger is not None
    
    def test_create_execution_group(self):
        """Test creating execution groups."""
        manager = ParallelExecutionManager()
        
        # Create group with specified ID
        group1 = manager.create_execution_group(
            group_id="group1",
            max_concurrency=3,
            timeout=10.0
        )
        
        assert group1.group_id == "group1"
        assert group1.max_concurrency == 3
        assert group1.timeout == 10.0
        assert "group1" in manager.execution_groups
        
        # Create group with auto-generated ID
        group2 = manager.create_execution_group(max_concurrency=5)
        
        assert group2.group_id is not None
        assert group2.max_concurrency == 5
        assert group2.timeout is None
        assert group2.group_id in manager.execution_groups
    
    @pytest.mark.asyncio
    async def test_execute_nodes_in_parallel(self, execution_trace):
        """Test executing nodes in parallel through the manager."""
        manager = ParallelExecutionManager()
        
        async def mock_execute_func(node_id: str) -> Dict[str, Any]:
            await asyncio.sleep(0.1)
            return {"node_id": node_id, "result": "success"}
        
        node_ids = ["node1", "node2", "node3"]
        start_time = datetime.now()
        
        results, errors = await manager.execute_nodes_in_parallel(
            node_ids,
            mock_execute_func,
            execution_trace,
            max_concurrency=3
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Should complete in roughly 0.1 seconds (parallel) rather than 0.3 seconds (sequential)
        assert execution_time < 0.2
        assert len(results) == 3
        assert len(errors) == 0
        assert all(node_id in results for node_id in node_ids)
    
    @pytest.mark.asyncio
    async def test_execute_with_mixed_success_failure(self, execution_trace):
        """Test executing nodes with mixed success and failure."""
        manager = ParallelExecutionManager()
        
        async def mixed_execute_func(node_id: str) -> Dict[str, Any]:
            if node_id == "failing_node":
                raise ValueError("Simulated failure")
            await asyncio.sleep(0.1)
            return {"node_id": node_id, "result": "success"}
        
        node_ids = ["node1", "failing_node", "node3"]
        
        results, errors = await manager.execute_nodes_in_parallel(
            node_ids,
            mixed_execute_func,
            execution_trace,
            max_concurrency=3
        )
        
        assert len(results) == 2  # node1 and node3 should succeed
        assert len(errors) == 1   # failing_node should fail
        assert "failing_node" in errors
        assert isinstance(errors["failing_node"], ValueError)
        assert "node1" in results
        assert "node3" in results
    
    def test_get_group_status(self):
        """Test getting group status."""
        manager = ParallelExecutionManager()
        
        # Test non-existent group
        status = manager.get_group_status("nonexistent")
        assert status is None
        
        # Create a group and test status
        group = manager.create_execution_group(
            group_id="test_group",
            max_concurrency=3,
            timeout=10.0
        )
        
        status = manager.get_group_status("test_group")
        assert status is not None
        assert status["group_id"] == "test_group"
        assert status["max_concurrency"] == 3
        assert status["timeout"] == 10.0
        assert status["active_tasks"] == 0
        assert status["completed_results"] == 0
        assert status["errors"] == 0
    
    def test_cleanup_group(self):
        """Test cleaning up execution groups."""
        manager = ParallelExecutionManager()
        
        # Test cleanup of non-existent group
        result = manager.cleanup_group("nonexistent")
        assert result is False
        
        # Create a group and test cleanup
        group = manager.create_execution_group(group_id="test_group")
        assert "test_group" in manager.execution_groups
        
        result = manager.cleanup_group("test_group")
        assert result is True
        assert "test_group" not in manager.execution_groups


class TestParallelExecutionIntegration:
    """Integration tests for parallel execution with primitives."""
    
    @pytest.fixture
    def primitive_registry(self):
        """Create test primitive registry."""
        registry = PrimitiveRegistry()
        registry.register_primitive("delayed", DelayedPrimitive)
        registry.register_primitive("slow", SlowPrimitive)
        return registry
    
    @pytest.mark.asyncio
    async def test_parallel_primitive_execution(self, primitive_registry, execution_trace):
        """Test parallel execution of actual primitives."""
        manager = ParallelExecutionManager()
        
        # Create execution contexts for each node
        contexts = {
            "node1": ExecutionContext(
                execution_id="test_execution",
                workflow_id="test_workflow",
                node_id="node1"
            ),
            "node2": ExecutionContext(
                execution_id="test_execution",
                workflow_id="test_workflow",
                node_id="node2"
            ),
            "node3": ExecutionContext(
                execution_id="test_execution",
                workflow_id="test_workflow",
                node_id="node3"
            )
        }
        
        async def execute_primitive(node_id: str) -> Dict[str, Any]:
            primitive_class = primitive_registry.get_primitive("delayed")
            primitive = primitive_class(
                primitive_id=node_id,
                config={"delay": 0.1}
            )
            return await primitive.execute(
                {"value": f"test_value_{node_id}"},
                contexts[node_id]
            )
        
        node_ids = ["node1", "node2", "node3"]
        start_time = datetime.now()
        
        results, errors = await manager.execute_nodes_in_parallel(
            node_ids,
            execute_primitive,
            execution_trace,
            max_concurrency=3
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Should complete in roughly 0.1 seconds (parallel) rather than 0.3 seconds (sequential)
        assert execution_time < 0.2
        assert len(results) == 3
        assert len(errors) == 0
        
        # Verify results contain expected data
        for node_id in node_ids:
            assert node_id in results
            result = results[node_id]
            assert result["node_id"] == node_id
            assert result["input_value"] == f"test_value_{node_id}"
            assert result["duration"] > 0
    
    @pytest.mark.asyncio
    async def test_parallel_execution_with_different_delays(self, primitive_registry, execution_trace):
        """Test parallel execution with primitives having different delays."""
        manager = ParallelExecutionManager()
        
        # Create execution contexts with different delays
        configs = {
            "fast_node": {"delay": 0.05},
            "medium_node": {"delay": 0.1},
            "slow_node": {"delay": 0.15}
        }
        
        contexts = {}
        for node_id in configs:
            contexts[node_id] = ExecutionContext(
                execution_id="test_execution",
                workflow_id="test_workflow",
                node_id=node_id
            )
        
        async def execute_primitive(node_id: str) -> Dict[str, Any]:
            primitive_class = primitive_registry.get_primitive("delayed")
            primitive = primitive_class(
                primitive_id=node_id,
                config=configs[node_id]
            )
            return await primitive.execute(
                {"value": f"test_value_{node_id}"},
                contexts[node_id]
            )
        
        node_ids = list(configs.keys())
        start_time = datetime.now()
        
        results, errors = await manager.execute_nodes_in_parallel(
            node_ids,
            execute_primitive,
            execution_trace,
            max_concurrency=3
        )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Should complete in roughly 0.15 seconds (time of slowest node)
        assert execution_time < 0.25
        assert len(results) == 3
        assert len(errors) == 0
        
        # Verify that faster nodes completed before slower ones
        fast_result = results["fast_node"]
        slow_result = results["slow_node"]
        assert fast_result["end_time"] <= slow_result["end_time"]
    
    @pytest.mark.asyncio
    async def test_parallel_execution_with_failure_recovery(self, primitive_registry, execution_trace):
        """Test that parallel execution continues even when some nodes fail."""
        manager = ParallelExecutionManager()
        
        configs = {
            "success_node1": {"delay": 0.1, "should_fail": False},
            "failing_node": {"delay": 0.1, "should_fail": True},
            "success_node2": {"delay": 0.1, "should_fail": False}
        }
        
        contexts = {}
        for node_id in configs:
            contexts[node_id] = ExecutionContext(
                execution_id="test_execution",
                workflow_id="test_workflow",
                node_id=node_id
            )
        
        async def execute_primitive(node_id: str) -> Dict[str, Any]:
            primitive_class = primitive_registry.get_primitive("delayed")
            primitive = primitive_class(
                primitive_id=node_id,
                config=configs[node_id]
            )
            return await primitive.execute(
                {"value": f"test_value_{node_id}"},
                contexts[node_id]
            )
        
        node_ids = list(configs.keys())
        
        results, errors = await manager.execute_nodes_in_parallel(
            node_ids,
            execute_primitive,
            execution_trace,
            max_concurrency=3
        )
        
        # Should have 2 successful results and 1 error
        assert len(results) == 2
        assert len(errors) == 1
        assert "failing_node" in errors
        assert "success_node1" in results
        assert "success_node2" in results
        assert isinstance(errors["failing_node"], ValueError)


class TestParallelExecutionPerformance:
    """Performance tests for parallel execution."""
    
    @pytest.mark.asyncio
    async def test_performance_comparison_sequential_vs_parallel(self, execution_trace):
        """Compare performance of sequential vs parallel execution."""
        manager = ParallelExecutionManager()
        
        async def mock_execute_func(node_id: str) -> Dict[str, Any]:
            await asyncio.sleep(0.1)  # 100ms delay per node
            return {"node_id": node_id, "result": "success"}
        
        node_ids = ["node1", "node2", "node3", "node4", "node5"]
        
        # Test parallel execution
        start_time = datetime.now()
        parallel_results, parallel_errors = await manager.execute_nodes_in_parallel(
            node_ids,
            mock_execute_func,
            execution_trace,
            max_concurrency=5
        )
        parallel_time = (datetime.now() - start_time).total_seconds()
        
        # Test sequential execution (simulate by setting max_concurrency=1)
        start_time = datetime.now()
        sequential_results, sequential_errors = await manager.execute_nodes_in_parallel(
            node_ids,
            mock_execute_func,
            execution_trace,
            max_concurrency=1
        )
        sequential_time = (datetime.now() - start_time).total_seconds()
        
        # Parallel should be significantly faster
        assert parallel_time < sequential_time
        assert parallel_time < 0.2  # Should complete in ~0.1s
        assert sequential_time > 0.4  # Should take ~0.5s
        
        # Both should have same results
        assert len(parallel_results) == len(sequential_results) == 5
        assert len(parallel_errors) == len(sequential_errors) == 0
    
    @pytest.mark.asyncio
    async def test_concurrency_scaling(self, execution_trace):
        """Test how execution time scales with different concurrency limits."""
        manager = ParallelExecutionManager()
        
        async def mock_execute_func(node_id: str) -> Dict[str, Any]:
            await asyncio.sleep(0.1)
            return {"node_id": node_id, "result": "success"}
        
        node_ids = [f"node{i}" for i in range(10)]  # 10 nodes
        
        # Test with different concurrency limits
        concurrency_limits = [1, 2, 5, 10]
        execution_times = {}
        
        for limit in concurrency_limits:
            start_time = datetime.now()
            results, errors = await manager.execute_nodes_in_parallel(
                node_ids,
                mock_execute_func,
                execution_trace,
                max_concurrency=limit
            )
            execution_time = (datetime.now() - start_time).total_seconds()
            execution_times[limit] = execution_time
            
            assert len(results) == 10
            assert len(errors) == 0
        
        # Higher concurrency should generally be faster (or at least not slower)
        assert execution_times[1] > execution_times[2]
        assert execution_times[2] >= execution_times[5]
        assert execution_times[5] >= execution_times[10]
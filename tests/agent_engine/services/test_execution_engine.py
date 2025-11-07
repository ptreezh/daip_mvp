"""Tests for ExecutionEngineService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Any, Dict

from daip_live.agent_engine_v1.services.execution_engine import (
    ExecutionEngineService,
    ExecutionResult,
    ToolDefinition,
    ExecutionContext,
    SequentialExecutionStrategy,
    ConditionalExecutionStrategy
)


class TestToolDefinition:
    """Test ToolDefinition class."""

    def test_tool_definition_creation(self):
        """Test creating tool definition."""
        def test_function():
            return "test_result"

        tool = ToolDefinition(
            name="test_tool",
            description="Test tool for testing",
            parameters={"param1": {"type": "string"}},
            function=test_function,
            category="test",
            risk_level="low",
            timeout_seconds=10.0,
            requires_permission=False
        )

        assert tool.name == "test_tool"
        assert tool.description == "Test tool for testing"
        assert tool.parameters == {"param1": {"type": "string"}}
        assert tool.function == test_function
        assert tool.category == "test"
        assert tool.risk_level == "low"
        assert tool.timeout_seconds == 10.0
        assert tool.requires_permission is False


class TestExecutionContext:
    """Test ExecutionContext class."""

    def test_execution_context_creation(self):
        """Test creating execution context."""
        context = ExecutionContext(
            session_id="test_session",
            user_id="test_user",
            metadata={"key": "value"}
        )

        assert context.session_id == "test_session"
        assert context.user_id == "test_user"
        assert context.metadata == {"key": "value"}
        assert context.start_time > 0

    def test_context_variables(self):
        """Test context variable management."""
        context = ExecutionContext()

        # Test setting and getting variables
        context.set_variable("test_key", "test_value")
        assert context.get_variable("test_key") == "test_value"
        assert context.get_variable("test_key", "default") == "test_value"
        assert context.get_variable("non_existent") is None

        # Test variable update
        context.set_variable("test_key", "updated_value")
        assert context.get_variable("test_key") == "updated_value"

    def test_execution_time(self):
        """Test execution time calculation."""
        import time

        context = ExecutionContext()
        start_time = context.start_time

        # Wait a bit
        time.sleep(0.01)

        execution_time = context.get_execution_time()
        assert execution_time >= 0.01
        assert execution_time < 0.02  # Should be close to 0.01


class TestSequentialExecutionStrategy:
    """Test sequential execution strategy."""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful sequential execution."""
        strategy = SequentialExecutionStrategy()

        # Mock tool
        tools = {
            "test_tool": ToolDefinition(
                name="test_tool",
                description="Test tool",
                parameters={},
                function=MagicMock(return_value="success"),
                timeout_seconds=5.0
            )
        }

        context = ExecutionContext()
        task = {
            "steps": ["test_tool"]
        }

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is True
        assert result.output is not None
        assert len(result.output) == 1
        assert result.metadata["strategy"] == "sequential"

    @pytest.mark.asyncio
    async def test_execute_multiple_steps(self):
        """Test execution with multiple steps."""
        strategy = SequentialExecutionStrategy()

        tools = {
            "step1": ToolDefinition(
                name="step1",
                description="Step 1",
                parameters={},
                function=MagicMock(return_value="step1_result"),
                timeout_seconds=5.0
            ),
            "step2": ToolDefinition(
                name="step2",
                description="Step 2",
                parameters={},
                function=MagicMock(return_value="step2_result"),
                timeout_seconds=5.0
            )
        }

        context = ExecutionContext()
        task = {
            "steps": ["step1", "step2"]
        }

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is True
        assert len(result.output) == 2
        assert result.output[0] == "step1_result"
        assert result.output[1] == "step2_result"

    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self):
        """Test execution with non-existent tool."""
        strategy = SequentialExecutionStrategy()

        tools = {}  # No tools

        context = ExecutionContext()
        task = {
            "steps": ["non_existent_tool"]
        }

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is False
        assert "Tool 'non_existent_tool' not found" in result.error
        assert result.metadata["step"] == 1

    @pytest.mark.asyncio
    async def test_execute_no_steps(self):
        """Test execution with no steps."""
        strategy = SequentialExecutionStrategy()

        tools = {}
        context = ExecutionContext()
        task = {"steps": []}

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is False
        assert result.error == "No steps found in task"

    @pytest.mark.asyncio
    async def test_execute_step_failure(self):
        """Test execution with step failure."""
        strategy = SequentialExecutionStrategy()

        # Mock tool that fails
        tools = {
            "failing_tool": ToolDefinition(
                name="failing_tool",
                description="Failing tool",
                parameters={},
                function=MagicMock(side_effect=Exception("Tool failed")),
                timeout_seconds=5.0
            )
        }

        context = ExecutionContext()
        task = {
            "steps": ["failing_tool"]
        }

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is False
        assert "Step 1 failed" in result.error
        assert result.metadata["completed_steps"] == 1

    @pytest.mark.asyncio
    async def test_execute_timeout(self):
        """Test execution timeout."""
        strategy = SequentialExecutionStrategy()

        # Mock tool that takes too long
        async def slow_function(**kwargs):
            import asyncio
            await asyncio.sleep(2.0)  # 2 seconds

        tools = {
            "slow_tool": ToolDefinition(
                name="slow_tool",
                description="Slow tool",
                parameters={},
                function=slow_function,
                timeout_seconds=0.1  # Very short timeout
            )
        }

        context = ExecutionContext()
        task = {
            "steps": ["slow_tool"]
        }

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is False
        assert "timed out" in result.error.lower()


class TestConditionalExecutionStrategy:
    """Test conditional execution strategy."""

    @pytest.mark.asyncio
    async def test_execute_condition_matched(self):
        """Test execution with matching condition."""
        strategy = ConditionalExecutionStrategy()

        # Mock tool that returns True
        tools = {
            "check_condition": ToolDefinition(
                name="check_condition",
                description="Check condition",
                parameters={},
                function=MagicMock(return_value=True),
                timeout_seconds=5.0
            ),
            "action_tool": ToolDefinition(
                name="action_tool",
                description="Action tool",
                parameters={},
                function=MagicMock(return_value="action_result"),
                timeout_seconds=5.0
            )
        }

        context = ExecutionContext()
        task = {
            "conditions": [
                {
                    "if": "check_condition",
                    "then": "action_tool"
                }
            ]
        }

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is True
        assert result.output == "action_result"

    @pytest.mark.asyncio
    async def test_execute_condition_not_matched(self):
        """Test execution with non-matching condition."""
        strategy = ConditionalExecutionStrategy()

        # Mock tool that returns False
        tools = {
            "check_condition": ToolDefinition(
                name="check_condition",
                description="Check condition",
                parameters={},
                function=MagicMock(return_value=False),
                timeout_seconds=5.0
            ),
            "default_tool": ToolDefinition(
                name="default_tool",
                description="Default tool",
                parameters={},
                function=MagicMock(return_value="default_result"),
                timeout_seconds=5.0
            )
        }

        context = ExecutionContext()
        task = {
            "conditions": [
                {
                    "if": "check_condition",
                    "else": "default_tool"
                }
            ]
        }

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is True
        assert result.output == "default_result"

    @pytest.mark.asyncio
    async def test_execute_no_conditions_matched(self):
        """Test execution with no conditions matched and no default."""
        strategy = ConditionalExecutionStrategy()

        tools = {}

        context = ExecutionContext()
        task = {
            "conditions": [
                {
                    "if": "check_condition",
                    "then": "action_tool"
                }
            ]
        }

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is False
        assert "No conditions matched" in result.error

    @pytest.mark.asyncio
    async def test_execute_complex_condition(self):
        """Test execution with complex condition logic."""
        strategy = ConditionalExecutionStrategy()

        tools = {
            "tool1": ToolDefinition(
                name="tool1",
                description="Tool 1",
                parameters={},
                function=MagicMock(return_value=True),
                timeout_seconds=5.0
            ),
            "tool2": ToolDefinition(
                name="tool2",
                description="Tool 2",
                parameters={},
                function=MagicMock(return_value="result2"),
                timeout_seconds=5.0
            )
        }

        context = ExecutionContext()
        task = {
            "conditions": [
                {
                    "if": "tool1",
                    "then": "tool2",
                    "else": "fallback_tool"
                }
            ]
        }

        result = await strategy.execute(task, tools, context, 30.0)

        assert result.success is True
        assert result.output == "result2"


class TestExecutionEngineService:
    """Test ExecutionEngineService."""

    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service start/stop lifecycle."""
        service = ExecutionEngineService()

        assert not service.is_healthy()

        await service.start()
        assert service.is_healthy()

        await service.stop()
        assert not service.is_healthy()

    @pytest.mark.asyncio
    async def test_execute_simple_task(self):
        """Test executing a simple task."""
        service = ExecutionEngineService()
        await service.start()

        # Register a test tool
        def test_function(**kwargs):
            return "executed"

        service.register_tool(
            name="test_tool",
            function=test_function,
            description="Test tool"
        )

        try:
            task = {"tool": "test_tool", "args": {}}
            result = await service.execute(task)

            assert result.success is True
            assert result.output == "executed"
            assert result.metadata["tool_name"] == "test_tool"

        finally:
            await service.stop()

    @pytest.asyncio
    async def test_execute_tool(self):
        """Test executing a specific tool."""
        service = ExecutionEngineService()
        await service.start()

        # Register a test tool
        def test_function(**kwargs):
            return "tool_result"

        service.register_tool(
            name="test_tool",
            function=test_function,
            description="Test tool"
        )

        try:
            result = await service.execute_tool("test_tool", {})

            assert result.success is True
            assert result.output == "tool_result"
            assert result.metadata["tool_name"] == "test_tool"

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self):
        """Test execution with custom timeout."""
        service = ExecutionEngineService()

        # Register a slow tool
        async def slow_function(**kwargs):
            import asyncio
            await asyncio.sleep(0.2)  # 200ms delay

        service.register_tool(
            name="slow_tool",
            function=slow_function,
            description="Slow tool",
            timeout_seconds=0.1  # Short timeout
        )

        await service.start()

        try:
            task = {"tool": "slow_tool", "args": {}}
            result = await service.execute_with_timeout(task, 0.15)  # 150ms timeout

            assert result.success is False
            assert "timed out" in result.error.lower()

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self):
        """Test executing non-existent tool."""
        service = ExecutionEngineService()
        await service.start()

        try:
            result = await service.execute_tool("non_existent_tool", {})
            assert result.success is False
            assert "not found" in result.error.lower()

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_register_tool(self):
        """Test tool registration."""
        service = ExecutionEngineService()
        await service.start()

        def test_function(**kwargs):
            return "test"

        try:
            # Register tool
            service.register_tool(
                name="test_tool",
                function=test_function,
                description="Test tool",
                parameters={"param": {"type": "string"}},
                category="test",
                risk_level="low"
            )

            # Verify tool was registered
            assert "test_tool" in service.get_available_tools()

            # Get tool info
            info = service.get_tool_info("test_tool")
            assert info is not None
            assert info["name"] == "test_tool"
            assert info["description"] == "Test tool"
            assert info["parameters"] == {"param": {"type": "string"}}
            assert info["category"] == "test"
            assert info["risk_level"] == "low"

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_unregister_tool(self):
        """Test tool unregistration."""
        service = ExecutionEngineService()
        await service.start()

        def test_function(**kwargs):
            return "test"

        try:
            # Register tool
            service.register_tool("test_tool", test_function)
            assert "test_tool" in service.get_available_tools()

            # Unregister tool
            removed = service.unregister_tool("test_tool")
            assert removed is True
            assert "test_tool" not in service.get_available_tools()

            # Try to unregister non-existent tool
            removed = service.unregister_tool("non_existent")
            assert removed is False

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_get_available_tools(self):
        """Test getting available tools."""
        service = ExecutionEngineService()
        await service.start()

        def test_function1(**kwargs):
            return "test1"

        def test_function2(**kwargs):
            return "test2"

        try:
            # Register multiple tools
            service.register_tool("tool1", test_function1)
            service.register_tool("tool2", test_function2)

            tools = service.get_available_tools()
            assert len(tools) == 2
            assert "tool1" in tools
            assert "tool2" in tools

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_batch_execution(self):
        """Test batch execution functionality."""
        service = ExecutionEngineService()
        await service.start()

        def test_function(**kwargs):
            return f"result_{kwargs.get('name', 'unknown')}"

        # Register tools
        service.register_tool("tool1", test_function)
        service.register_tool("tool2", test_function)

        try:
            # Create tasks
            tasks = [
                {"tool": "tool1", "args": {"name": "test1"}},
                {"tool": "tool2", "args": {"name": "test2"}}
            ]

            # Execute in batch
            results = await service.batch_check_permissions(tasks)

            assert len(results) == 2
            for result in results:
                assert result.success is True

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_service_metrics(self):
        """Test service metrics collection."""
        service = ExecutionEngineService()
        await service.start()

        def test_function(**kwargs):
            return "test"

        service.register_tool("test_tool", test_function)

        try:
            # Perform some operations
            await service.execute({"tool": "test_tool", "args": {}})
            await service.execute_tool("test_tool", {})
            await service.execute_with_timeout(
                {"tool": "test_tool", "args": {}}, 1.0
            )

            # Get metrics
            metrics = service.get_metrics()
            assert metrics["tasks_executed"] == 3
            assert metrics["tools_registered"] == 1
            assert metrics["success_rate"] >= 0.0
            assert "tool_usage" in metrics
            assert "test_tool" in metrics["tool_usage"]

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_concurrency_limit(self):
        """Test concurrency limit enforcement."""
        service = ExecutionEngineService(max_concurrent_tasks=1)  # Limit to 1 concurrent task
        await service.start()

        def slow_function(**kwargs):
            import asyncio
            asyncio.sleep(0.1)  # 100ms delay

        service.register_tool("slow_tool", slow_function, timeout_seconds=0.2)

        try:
            # Start multiple tasks concurrently
            task1 = asyncio.create_task(
                service.execute({"tool": "slow_tool", "args": {}})
            )
            task2 = asyncio.create_task(
                service.execute({"tool": "slow_tool", "args": {}})
            )

            # Wait for both to complete
            result1, result2 = await asyncio.gather(task1, task2)

            # Both should succeed (they run sequentially due to semaphore)
            assert result1.success is True
            assert result2.success is True

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_error_handling_not_running(self):
        """Test error handling when service is not running."""
        service = ExecutionEngineService()

        # Should raise error when not running
        with pytest.raises(RuntimeError, match="not running"):
            await service.execute({"tool": "test", "args": {}})

        with pytest.raises(RuntimeError, match="not running"):
            await service.execute_tool("test", {})

        with pytest.raises(RuntimeError, match="not running"):
            await service.batch_check_permissions([{"tool": "test"}])


class TestToolRegistration:
    """Test tool registration edge cases."""

    @pytest.mark.asyncio
    async def test_register_tool_with_context(self):
        """Test tool function that receives context."""
        service = ExecutionEngineService()
        await service.start()

        def context_function(context, **kwargs):
            return f"Context: {context.session_id}"

        service.register_tool("context_tool", context_function)

        try:
            context = {"session_id": "test_session"}
            result = await service.execute_tool("context_tool", {}, context)

            assert result.success is True
            assert "test_session" in result.output

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_register_tool_with_args(self):
        """Test tool function that receives specific arguments."""
        service = ExecutionEngineService()
        await service.start()

        def args_function(args, **kwargs):
            return f"Args: {args}, Kwargs: {kwargs}"

        service.register_tool("args_tool", args_function)

        try:
            result = await service.execute_tool("args_tool", {"arg1": "value1", "arg2": "value2"})

            assert result.success is True
            assert "arg1" in result.output
            assert "arg2" in result.output

        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_register_sync_tool(self):
        """Test registering a synchronous tool function."""
        service = ExecutionEngineService()
        await service.start()

        def sync_function(**kwargs):
            return "sync_result"

        service.register_tool("sync_tool", sync_function)

        try:
            result = await service.execute_tool("sync_tool", {})
            assert result.success is True
            assert result.output == "sync_result"

        finally:
            await service.stop()
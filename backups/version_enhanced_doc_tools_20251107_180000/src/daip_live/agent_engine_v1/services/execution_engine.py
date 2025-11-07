"""Execution Engine Service implementation."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from .interfaces import (
    IExecutionEngineService,
    ExecutionResult,
    IDomainService
)

logger = logging.getLogger(__name__)


@dataclass
class ToolDefinition:
    """Definition of an available tool."""

    name: str
    description: str
    parameters: Dict[str, Any]  # Parameter schema
    function: Callable
    category: str = "general"
    risk_level: str = "medium"
    timeout_seconds: float = 30.0
    requires_permission: bool = True


class ExecutionContext:
    """Context for task execution."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize execution context.

        Args:
            session_id: Session identifier
            user_id: User identifier
            metadata: Additional context metadata
        """
        self.session_id = session_id
        self.user_id = user_id
        self.metadata = metadata or {}
        self.start_time = time.time()
        self.variables: Dict[str, Any] = {}

    def set_variable(self, name: str, value: Any) -> None:
        """Set a context variable."""
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a context variable."""
        return self.variables.get(name, default)

    def get_execution_time(self) -> float:
        """Get execution time in seconds."""
        return time.time() - self.start_time


class ExecutionStrategy(ABC):
    """Abstract base class for execution strategies."""

    @abstractmethod
    async def execute(
        self,
        task: Dict[str, Any],
        tools: Dict[str, ToolDefinition],
        context: ExecutionContext,
        timeout_seconds: float
    ) -> ExecutionResult:
        """
        Execute a task using this strategy.

        Args:
            task: Task specification
            tools: Available tools
            context: Execution context
            timeout_seconds: Maximum execution time

        Returns:
            Execution result
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        pass


class SequentialExecutionStrategy(ExecutionStrategy):
    """Sequential execution strategy for tasks with multiple steps."""

    async def execute(
        self,
        task: Dict[str, Any],
        tools: Dict[str, ToolDefinition],
        context: ExecutionContext,
        timeout_seconds: float
    ) -> ExecutionResult:
        """Execute task steps sequentially."""
        steps = task.get("steps", [])
        if not steps:
            return ExecutionResult(
                success=False,
                error="No steps found in task"
            )

        results = []
        total_start_time = time.time()

        for i, step in enumerate(steps):
            step_start_time = time.time()

            # Calculate remaining timeout
            elapsed_time = step_start_time - total_start_time
            remaining_timeout = max(1.0, timeout_seconds - elapsed_time)

            # Execute step
            if isinstance(step, str):
                # Simple tool call
                result = await self._execute_tool_call(
                    step, {}, tools, context, remaining_timeout
                )
            elif isinstance(step, dict):
                # Detailed step specification
                tool_name = step.get("tool")
                tool_args = step.get("args", {})
                result = await self._execute_tool_call(
                    tool_name, tool_args, tools, context, remaining_timeout
                )
            else:
                result = ExecutionResult(
                    success=False,
                    error=f"Invalid step type: {type(step)}"
                )

            results.append(result)

            # Stop on first failure
            if not result.success:
                return ExecutionResult(
                    success=False,
                    error=f"Step {i+1} failed: {result.error}",
                    metadata={
                        "step": i+1,
                        "total_steps": len(steps),
                        "completed_steps": i+1,
                        "results": results
                    }
                )

        return ExecutionResult(
            success=True,
            output=results,
            execution_time_ms=(time.time() - total_start_time) * 1000,
            metadata={
                "total_steps": len(steps),
                "strategy": self.get_strategy_name()
            }
        )

    async def _execute_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tools: Dict[str, ToolDefinition],
        context: ExecutionContext,
        timeout_seconds: float
    ) -> ExecutionResult:
        """Execute a single tool call."""
        if tool_name not in tools:
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )

        tool = tools[tool_name]
        start_time = time.time()

        try:
            # Execute tool with timeout
            result = await asyncio.wait_for(
                self._call_tool_function(tool, tool_args, context),
                timeout=timeout_seconds
            )

            execution_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=True,
                output=result,
                execution_time_ms=execution_time,
                metadata={
                    "tool_name": tool_name,
                    "tool_args": tool_args
                }
            )

        except asyncio.TimeoutError:
            execution_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' execution timed out after {timeout_seconds}s",
                execution_time_ms=execution_time
            )
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' execution failed: {str(e)}",
                execution_time_ms=execution_time
            )

    async def _call_tool_function(
        self,
        tool: ToolDefinition,
        tool_args: Dict[str, Any],
        context: ExecutionContext
    ) -> Any:
        """Call the underlying tool function."""
        # Prepare function arguments
        func_args = {
            "args": tool_args,
            "context": context,
            **tool_args  # Pass individual args as well
        }

        # Call the function
        if asyncio.iscoroutinefunction(tool.function):
            return await tool.function(**func_args)
        else:
            # Run synchronous function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, tool.function, **func_args)

    def get_strategy_name(self) -> str:
        return "sequential"


class ConditionalExecutionStrategy(ExecutionStrategy):
    """Conditional execution strategy with if-then-else logic."""

    async def execute(
        self,
        task: Dict[str, Any],
        tools: Dict[str, ToolDefinition],
        context: ExecutionContext,
        timeout_seconds: float
    ) -> ExecutionResult:
        """Execute conditional logic."""
        conditions = task.get("conditions", [])
        default_action = task.get("default")

        for condition in conditions:
            condition_result = await self._evaluate_condition(
                condition.get("if"),
                tools,
                context
            )

            if condition_result.success and condition_result.output:
                # Execute matching action
                action = condition.get("then")
                if action:
                    return await self._execute_action(
                        action, tools, context, timeout_seconds
                    )
            else:
                # Execute else action if present
                else_action = condition.get("else")
                if else_action:
                    return await self._execute_action(
                        else_action, tools, context, timeout_seconds
                    )

        # Execute default action if no conditions matched
        if default_action:
            return await self._execute_action(
                default_action, tools, context, timeout_seconds
            )

        return ExecutionResult(
            success=False,
            error="No conditions matched and no default action provided"
        )

    async def _evaluate_condition(
        self,
        condition: Any,
        tools: Dict[str, ToolDefinition],
        context: ExecutionContext
    ) -> ExecutionResult:
        """Evaluate a condition."""
        if isinstance(condition, str):
            # Simple tool call condition
            tool_name = condition
            return await self._execute_tool_call(
                tool_name, {}, tools, context, 5.0
            )
        elif isinstance(condition, dict):
            # Complex condition
            tool_name = condition.get("tool")
            tool_args = condition.get("args", {})
            expected = condition.get("equals")
            operator = condition.get("operator", "equals")

            result = await self._execute_tool_call(
                tool_name, tool_args, tools, context, 5.0
            )

            if not result.success:
                return result

            # Apply operator
            if operator == "equals":
                return ExecutionResult(
                    success=True,
                    output=result.output == expected
                )
            elif operator == "not_equals":
                return ExecutionResult(
                    success=True,
                    output=result.output != expected
                )
            elif operator == "exists":
                return ExecutionResult(
                    success=True,
                    output=result.output is not None
                )
            else:
                return ExecutionResult(
                    success=False,
                    error=f"Unknown operator: {operator}"
                )

        return ExecutionResult(
            success=False,
            error="Invalid condition format"
        )

    async def _execute_action(
        self,
        action: Any,
        tools: Dict[str, ToolDefinition],
        context: ExecutionContext,
        timeout_seconds: float
    ) -> ExecutionResult:
        """Execute an action."""
        if isinstance(action, str):
            return await self._execute_tool_call(
                action, {}, tools, context, timeout_seconds
            )
        elif isinstance(action, dict):
            tool_name = action.get("tool")
            tool_args = action.get("args", {})
            return await self._execute_tool_call(
                tool_name, tool_args, tools, context, timeout_seconds
            )
        elif isinstance(action, list):
            # Execute multiple actions sequentially
            sequential_strategy = SequentialExecutionStrategy()
            task = {"steps": action}
            return await sequential_strategy.execute(
                task, tools, context, timeout_seconds
            )

        return ExecutionResult(
            success=False,
            error="Invalid action format"
        )

    async def _execute_tool_call(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        tools: Dict[str, ToolDefinition],
        context: ExecutionContext,
        timeout_seconds: float
    ) -> ExecutionResult:
        """Execute a single tool call (same as in SequentialExecutionStrategy)."""
        if tool_name not in tools:
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )

        tool = tools[tool_name]
        start_time = time.time()

        try:
            result = await asyncio.wait_for(
                self._call_tool_function(tool, tool_args, context),
                timeout=timeout_seconds
            )

            execution_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=True,
                output=result,
                execution_time_ms=execution_time
            )

        except asyncio.TimeoutError:
            execution_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' execution timed out",
                execution_time_ms=execution_time
            )
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' execution failed: {str(e)}",
                execution_time_ms=execution_time
            )

    async def _call_tool_function(
        self,
        tool: ToolDefinition,
        tool_args: Dict[str, Any],
        context: ExecutionContext
    ) -> Any:
        """Call the underlying tool function."""
        func_args = {
            "args": tool_args,
            "context": context,
            **tool_args
        }

        if asyncio.iscoroutinefunction(tool.function):
            return await tool.function(**func_args)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, tool.function, **func_args)

    def get_strategy_name(self) -> str:
        return "conditional"


class ExecutionEngineService(IExecutionEngineService):
    """
    Execution Engine Service implementation.

    This service provides task execution capabilities with multiple strategies,
    tool management, and comprehensive error handling.
    """

    def __init__(
        self,
        default_timeout_seconds: float = 30.0,
        enable_metrics: bool = True,
        max_concurrent_tasks: int = 10
    ):
        """
        Initialize execution engine service.

        Args:
            default_timeout_seconds: Default timeout for task execution
            enable_metrics: Whether to collect performance metrics
            max_concurrent_tasks: Maximum number of concurrent tasks
        """
        self.default_timeout_seconds = default_timeout_seconds
        self.enable_metrics = enable_metrics
        self.max_concurrent_tasks = max_concurrent_tasks

        self._tools: Dict[str, ToolDefinition] = {}
        self._strategies: Dict[str, ExecutionStrategy] = {}
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._running = False
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)

        self._metrics = {
            "tasks_executed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time_ms": 0.0,
            "tool_usage": {},
            "strategy_usage": {},
            "avg_execution_time_ms": 0.0
        }

        # Initialize default strategies
        self._initialize_default_strategies()

    def _initialize_default_strategies(self) -> None:
        """Initialize default execution strategies."""
        self._strategies["sequential"] = SequentialExecutionStrategy()
        self._strategies["conditional"] = ConditionalExecutionStrategy()

    async def start(self) -> None:
        """Start the execution engine service."""
        if self._running:
            return

        self._running = True
        logger.info("ExecutionEngineService started")

    async def stop(self) -> None:
        """Stop the execution engine service."""
        if not self._running:
            return

        self._running = False

        # Cancel all running tasks
        for task_id, task in self._running_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._running_tasks.clear()
        logger.info("ExecutionEngineService stopped")

    def is_healthy(self) -> bool:
        """Check if the service is healthy."""
        return self._running

    async def execute(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute a task.

        Args:
            task: Task specification
            context: Optional execution context

        Returns:
            Execution result
        """
        if not self._running:
            raise RuntimeError("ExecutionEngineService is not running")

        execution_context = ExecutionContext(
            session_id=context.get("session_id") if context else None,
            user_id=context.get("user_id") if context else None,
            metadata=context or {}
        )

        # Determine strategy
        strategy_name = task.get("strategy", "sequential")
        strategy = self._strategies.get(strategy_name)

        if not strategy:
            return ExecutionResult(
                success=False,
                error=f"Unknown execution strategy: {strategy_name}"
            )

        # Determine timeout
        timeout_seconds = task.get("timeout", self.default_timeout_seconds)

        # Execute with semaphore to limit concurrency
        async with self._semaphore:
            start_time = time.time()
            self._metrics["tasks_executed"] += 1

            try:
                result = await strategy.execute(
                    task, self._tools, execution_context, timeout_seconds
                )

                # Update metrics
                execution_time = (time.time() - start_time) * 1000
                self._update_metrics(result, execution_time, strategy_name)

                return result

            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                self._metrics["tasks_failed"] += 1
                self._metrics["total_execution_time_ms"] += execution_time

                return ExecutionResult(
                    success=False,
                    error=f"Task execution failed: {str(e)}",
                    execution_time_ms=execution_time
                )

    async def execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute a specific tool.

        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            context: Optional execution context

        Returns:
            Execution result
        """
        if tool_name not in self._tools:
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )

        tool = self._tools[tool_name]
        execution_context = ExecutionContext(
            session_id=context.get("session_id") if context else None,
            user_id=context.get("user_id") if context else None,
            metadata=context or {}
        )

        start_time = time.time()
        self._metrics["tasks_executed"] += 1

        try:
            result = await asyncio.wait_for(
                self._call_tool_function(tool, tool_args, execution_context),
                timeout=tool.timeout_seconds
            )

            execution_time = (time.time() - start_time) * 1000
            self._update_metrics(
                ExecutionResult(success=True, output=result, execution_time_ms=execution_time),
                execution_time,
                "direct_tool_call"
            )

            # Update tool usage
            self._metrics["tool_usage"][tool_name] = self._metrics["tool_usage"].get(tool_name, 0) + 1

            return ExecutionResult(
                success=True,
                output=result,
                execution_time_ms=execution_time,
                metadata={"tool_name": tool_name}
            )

        except asyncio.TimeoutError:
            execution_time = (time.time() - start_time) * 1000
            self._metrics["tasks_failed"] += 1
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' execution timed out after {tool.timeout_seconds}s",
                execution_time_ms=execution_time
            )
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self._metrics["tasks_failed"] += 1
            return ExecutionResult(
                success=False,
                error=f"Tool '{tool_name}' execution failed: {str(e)}",
                execution_time_ms=execution_time
            )

    async def execute_with_timeout(
        self,
        task: Dict[str, Any],
        timeout_seconds: float,
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        """
        Execute a task with a timeout.

        Args:
            task: Task specification
            timeout_seconds: Maximum execution time
            context: Optional execution context

        Returns:
            Execution result
        """
        task_with_timeout = task.copy()
        task_with_timeout["timeout"] = timeout_seconds

        return await self.execute(task_with_timeout, context)

    async def _call_tool_function(
        self,
        tool: ToolDefinition,
        tool_args: Dict[str, Any],
        context: ExecutionContext
    ) -> Any:
        """Call the underlying tool function."""
        func_args = {
            "args": tool_args,
            "context": context,
            **tool_args
        }

        if asyncio.iscoroutinefunction(tool.function):
            return await tool.function(**func_args)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, tool.function, **func_args)

    def _update_metrics(
        self,
        result: ExecutionResult,
        execution_time_ms: float,
        strategy_name: str
    ) -> None:
        """Update execution metrics."""
        if result.success:
            self._metrics["tasks_completed"] += 1
        else:
            self._metrics["tasks_failed"] += 1

        self._metrics["total_execution_time_ms"] += execution_time_ms
        self._metrics["strategy_usage"][strategy_name] = self._metrics["strategy_usage"].get(strategy_name, 0) + 1

        total_tasks = self._metrics["tasks_executed"]
        if total_tasks > 0:
            self._metrics["avg_execution_time_ms"] = self._metrics["total_execution_time_ms"] / total_tasks

    def register_tool(
        self,
        name: str,
        function: Callable,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        category: str = "general",
        risk_level: str = "medium",
        timeout_seconds: float = 30.0,
        requires_permission: bool = True
    ) -> None:
        """
        Register a tool with the execution engine.

        Args:
            name: Tool name
            function: Tool function
            description: Tool description
            parameters: Parameter schema
            category: Tool category
            risk_level: Risk level
            timeout_seconds: Default timeout
            requires_permission: Whether permission is required
        """
        tool = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or {},
            function=function,
            category=category,
            risk_level=risk_level,
            timeout_seconds=timeout_seconds,
            requires_permission=requires_permission
        )

        self._tools[name] = tool
        logger.info(f"Registered tool '{name}' in category '{category}'")

    def unregister_tool(self, name: str) -> bool:
        """
        Unregister a tool.

        Args:
            name: Tool name to unregister

        Returns:
            True if tool was unregistered, False if not found
        """
        if name in self._tools:
            del self._tools[name]
            logger.info(f"Unregistered tool '{name}'")
            return True
        return False

    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return list(self._tools.keys())

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        if tool_name not in self._tools:
            return None

        tool = self._tools[tool_name]
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters,
            "category": tool.category,
            "risk_level": tool.risk_level,
            "timeout_seconds": tool.timeout_seconds,
            "requires_permission": tool.requires_permission
        }

    def add_strategy(self, name: str, strategy: ExecutionStrategy) -> None:
        """Add a custom execution strategy."""
        self._strategies[name] = strategy
        logger.info(f"Added execution strategy '{name}'")

    def remove_strategy(self, name: str) -> bool:
        """Remove an execution strategy."""
        if name in self._strategies and name not in ["sequential", "conditional"]:
            del self._strategies[name]
            logger.info(f"Removed execution strategy '{name}'")
            return True
        return False

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        total_tasks = self._metrics["tasks_executed"]
        return {
            **self._metrics,
            "success_rate": (
                self._metrics["tasks_completed"] / total_tasks
                if total_tasks > 0 else 0.0
            ),
            "failure_rate": (
                self._metrics["tasks_failed"] / total_tasks
                if total_tasks > 0 else 0.0
            ),
            "tools_registered": len(self._tools),
            "strategies_available": len(self._strategies),
            "running_tasks": len(self._running_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks
        }

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task by ID."""
        if task_id in self._running_tasks:
            task = self._running_tasks[task_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self._running_tasks[task_id]
            return True
        return False
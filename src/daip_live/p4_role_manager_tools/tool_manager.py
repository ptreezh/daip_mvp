"""The ToolManager and its secure execution pipeline."""

import inspect
from functools import wraps
from typing import Any, Callable, Dict, Type, Optional, Set

from pydantic import BaseModel, create_model, ValidationError

from daip_live.core.exceptions import DAIPError
from daip_live.core.models import SessionContext, ToolPermissionConfig # Assuming SessionContext is defined here


# Custom Exceptions for the Tool Pipeline
class ToolError(DAIPError):
    """Base exception for all tool-related errors."""
    pass

class ToolNotFoundError(ToolError):
    """Raised when a tool is not found in the registry."""
    pass

class ToolInputError(ToolError):
    """Raised when tool input validation fails."""
    pass

class ToolPreconditionError(ToolError):
    """Raised when a tool's precondition (e.g., write-after-read) is not met."""
    pass

class ToolTimeoutError(ToolError):
    """Raised when a tool execution times out."""
    pass

class ToolPermissionError(ToolError):
    """Raised when a tool is denied by the permission policy."""
    pass

class ToolPermissionRequest(DAIPError):
    """A control-flow exception to request user permission."""
    def __init__(self, tool_name: str, args: Dict[str, Any]):
        self.tool_name = tool_name
        self.args = args
        super().__init__(f"Permission required for tool '{tool_name}' with args: {args}")


class ToolManager:
    """
    Manages the registration and secure execution of tools.
    """
    def __init__(self):
        self._registry: Dict[str, Callable] = {}
        self.tool_permission_config = ToolPermissionConfig() # Initialize with default config

    def register_tool(self, tool_func: Callable):
        """Registers a function decorated with @tool."""
        if not getattr(tool_func, "is_tool", False):
            raise ValueError("Function must be decorated with @tool to be registered.")
        
        tool_name = tool_func.__name__
        if tool_name in self._registry:
            # For now, let's allow re-registration for easier interactive development
            # In a stricter environment, this might raise an error.
            pass
        
        self._registry[tool_name] = tool_func

    def execute_tool(self, name: str, args: Dict[str, Any], session_context: SessionContext, confirmation_granted: bool = False) -> Any:
        """
        Executes a tool through the 6-stage secure execution pipeline.
        """
        # Stage 1: Discovery
        if name not in self._registry:
            raise ToolNotFoundError(f"Tool '{name}' not found.")
        
        tool_func = self._registry[name]
        input_schema = getattr(tool_func, "input_schema", None)

        # Stage 2: Input Validation
        if input_schema:
            try:
                validated_args = input_schema.model_validate(args)
                # Use the validated and potentially coerced arguments for execution
                args_to_execute = validated_args.model_dump()
            except ValidationError as e:
                raise ToolInputError(f"Input validation failed for tool '{name}': {e}") from e
        else:
            # Should not happen if @tool decorator is used correctly
            args_to_execute = args

        # Stage 3: Precondition Check (Write-After-Read)
        is_write_tool = getattr(tool_func, "is_write", False)
        target_resource_arg = getattr(tool_func, "resource_arg", None)

        if is_write_tool and target_resource_arg:
            resource_path = args_to_execute.get(target_resource_arg)
            if resource_path and resource_path not in session_context.recently_read_resources:
                raise ToolPreconditionError(
                    f"Resource '{resource_path}' was not recently read. "
                    "Write operations require a prior read operation on the target resource."
                )
        
        # Stage 4: Permission Check
        permission_status = self.tool_permission_config.tools.get(name, self.tool_permission_config.default)

        if permission_status == "deny":
            raise ToolPermissionError(f"Tool '{name}' is denied by policy.")
        elif permission_status == "ask" and not confirmation_granted:
            raise ToolPermissionRequest(tool_name=name, args=args_to_execute)

        # Stage 5: Execution
        try:
            result = tool_func(**args_to_execute)
        except TimeoutError as e:
            raise ToolTimeoutError(f"Tool '{name}' timed out.") from e
        except Exception as e:
            # Stage 6: Result Formatting (for exceptions)
            return f"Error executing tool '{name}': {type(e).__name__}('{e}')"

        # Stage 6: Result Formatting (for successful execution)
        if not isinstance(result, str):
            result = str(result)

        # After execution, if it's a read tool, add the resource to recently_read_resources
        if not is_write_tool and target_resource_arg: # Assuming 'read' tools are not 'write' tools
            resource_path = args_to_execute.get(target_resource_arg)
            if resource_path:
                session_context.recently_read_resources.add(resource_path)

        return result
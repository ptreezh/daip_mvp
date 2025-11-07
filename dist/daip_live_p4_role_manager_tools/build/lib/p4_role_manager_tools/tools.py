"""Tool registration and management."""

import inspect
from functools import wraps
from typing import Any, Callable, Dict, Literal, Optional, Type

from pydantic import BaseModel, create_model


def tool(
    func: Callable = None,
    tool_type: Literal["read", "write"] = "read", # Default to read
    resource_arg: Optional[str] = None
) -> Callable:
    """
    A decorator that registers a function as a tool, dynamically creating a
    Pydantic model for its arguments to be used for input validation.
    """
    if func is None: # Allows decorator to be used with arguments: @tool(tool_type="write")
        return lambda f: tool(f, tool_type=tool_type, resource_arg=resource_arg)

    # 1. Inspect the function signature
    sig = inspect.signature(func)

    # 2. Create a dictionary of fields for the Pydantic model
    fields: Dict[str, Any] = {}
    for param in sig.parameters.values():
        # Exclude self, cls, args, kwargs for now
        if param.name in ('self', 'cls', 'args', 'kwargs'):
            continue

        # Get type annotation and default value
        param_type = param.annotation if param.annotation is not inspect.Parameter.empty else Any

        if param.default is inspect.Parameter.empty:
            # This is a required argument
            fields[param.name] = (param_type, ...)
        else:
            # This is an optional argument with a default value
            fields[param.name] = (param_type, param.default)

    # 3. Dynamically create the Pydantic model
    model_name = f"{func.__name__.capitalize()}Input"
    input_schema: Type[BaseModel] = create_model(model_name, **fields)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # The wrapper itself doesn't do much yet, the main logic is in the
        # ToolManager. For now, it just calls the original function.
        return func(*args, **kwargs)

    # 4. Attach the schema and other metadata to the wrapped function
    setattr(wrapper, "input_schema", input_schema)
    setattr(wrapper, "is_tool", True)
    setattr(wrapper, "tool_type", tool_type)
    setattr(wrapper, "is_write", tool_type == "write") # Convenience flag
    setattr(wrapper, "resource_arg", resource_arg)

    return wrapper

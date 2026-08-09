"""Enhanced tool extension mechanism following SOLID principles."""

import inspect
from functools import wraps
from typing import Any, Callable, Literal, Optional

from pydantic import BaseModel, create_model


class ToolMetadata:
    """工具元数据类，用于存储工具的详细信息"""

    def __init__(
        self,
        name: str,
        description: str,
        tool_type: Literal["read", "write"] = "read",
        resource_arg: Optional[str] = None,
        category: str = "general",
        version: str = "1.0.0",
    ):
        self.name = name
        self.description = description
        self.tool_type = tool_type
        self.resource_arg = resource_arg
        self.category = category
        self.version = version
        self.is_write = tool_type == "write"


class ToolRegistry:
    """工具注册表，遵循单一职责原则"""

    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._metadata: dict[str, ToolMetadata] = {}

    def register(self, tool_func: Callable, metadata: ToolMetadata):
        """注册工具及其元数据"""
        tool_name = metadata.name
        self._tools[tool_name] = tool_func
        self._metadata[tool_name] = metadata

    def get_tool(self, name: str) -> Optional[Callable]:
        """获取工具函数"""
        return self._tools.get(name)

    def get_metadata(self, name: str) -> Optional[ToolMetadata]:
        """获取工具元数据"""
        return self._metadata.get(name)

    def list_tools(self) -> list[str]:
        """列出所有已注册的工具"""
        return list(self._tools.keys())

    def list_tools_by_category(self, category: str) -> list[str]:
        """按类别列出工具"""
        return [
            name
            for name, metadata in self._metadata.items()
            if metadata.category == category
        ]


def tool(
    func: Callable = None,
    tool_type: Literal["read", "write"] = "read",
    resource_arg: Optional[str] = None,
    category: str = "general",
    description: Optional[str] = None,
) -> Callable:
    """
    增强的工具装饰器，支持更多元数据
    """
    if func is None:
        return lambda f: tool(
            f,
            tool_type=tool_type,
            resource_arg=resource_arg,
            category=category,
            description=description,
        )

    # 1. Inspect the function signature
    sig = inspect.signature(func)

    # 2. Create a dictionary of fields for the Pydantic model
    fields: dict[str, Any] = {}
    for param in sig.parameters.values():
        # Exclude self, cls, args, kwargs for now
        if param.name in ("self", "cls", "args", "kwargs"):
            continue

        # Get type annotation and default value
        param_type = (
            param.annotation if param.annotation is not inspect.Parameter.empty else Any
        )

        if param.default is inspect.Parameter.empty:
            # This is a required argument
            fields[param.name] = (param_type, ...)
        else:
            # This is an optional argument with a default value
            fields[param.name] = (param_type, param.default)

    # 3. Dynamically create the Pydantic model
    model_name = f"{func.__name__.capitalize()}Input"
    input_schema: type[BaseModel] = create_model(model_name, **fields)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # The wrapper itself doesn't do much yet, the main logic is in the
        # ToolManager. For now, it just calls the original function.
        return func(*args, **kwargs)

    # 4. Attach the schema and other metadata to the wrapped function
    setattr(wrapper, "input_schema", input_schema)
    setattr(wrapper, "is_tool", True)
    setattr(wrapper, "tool_type", tool_type)
    setattr(wrapper, "is_write", tool_type == "write")
    setattr(wrapper, "resource_arg", resource_arg)

    # 5. 创建并附加工具元数据
    tool_description = description or func.__doc__ or f"Tool {func.__name__}"
    metadata = ToolMetadata(
        name=func.__name__,
        description=tool_description,
        tool_type=tool_type,
        resource_arg=resource_arg,
        category=category,
    )
    setattr(wrapper, "metadata", metadata)

    return wrapper


class ToolExtensionManager:
    """工具扩展管理器，遵循开闭原则"""

    def __init__(self):
        self.registry = ToolRegistry()

    def register_tool(self, tool_func: Callable):
        """注册工具，无需修改现有代码"""
        if not getattr(tool_func, "is_tool", False):
            raise ValueError("Function must be decorated with @tool to be registered.")

        metadata = getattr(tool_func, "metadata", None)
        if metadata is None:
            # 兼容旧版本工具
            tool_name = tool_func.__name__
            metadata = ToolMetadata(name=tool_name, description=f"Tool {tool_name}")

        self.registry.register(tool_func, metadata)

    def extend_with_module(self, module):
        """从模块中自动注册所有工具"""
        for name in dir(module):
            attr = getattr(module, name)
            if callable(attr) and getattr(attr, "is_tool", False):
                self.register_tool(attr)

    def get_tool_info(self, name: str) -> dict[str, Any]:
        """获取工具信息"""
        tool_func = self.registry.get_tool(name)
        metadata = self.registry.get_metadata(name)

        if not tool_func or not metadata:
            return {}

        # 获取输入模式信息
        input_schema = getattr(tool_func, "input_schema", None)
        schema_info = {}
        if input_schema:
            schema_info = {
                field_name: {
                    "type": field_info.annotation.__name__
                    if hasattr(field_info.annotation, "__name__")
                    else str(field_info.annotation),
                    "required": field_info.is_required(),
                    "default": field_info.default
                    if not field_info.is_required()
                    else None,
                }
                for field_name, field_info in input_schema.model_fields.items()
            }

        return {
            "name": metadata.name,
            "description": metadata.description,
            "type": metadata.tool_type,
            "category": metadata.category,
            "is_write": metadata.is_write,
            "resource_arg": metadata.resource_arg,
            "version": metadata.version,
            "input_schema": schema_info,
        }

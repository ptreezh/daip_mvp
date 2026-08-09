"""Tests for enhanced tool extension mechanism."""

from typing import Any

from daip_live.core.models import SessionContext, ToolPermissionConfig
from daip_live.p4_role_manager_tools.tool_extension import (
    ToolExtensionManager,
    ToolMetadata,
    tool,
)
from daip_live.p4_role_manager_tools.tool_manager import ToolManager


class TestEnhancedToolExtension:
    """测试增强的工具扩展机制"""

    def test_tool_decorator_with_enhanced_metadata(self):
        """测试带有增强元数据的工具装饰器"""

        @tool(
            tool_type="write",
            resource_arg="file_path",
            category="file_operations",
            description="Writes content to a file with enhanced features",
        )
        def enhanced_write_file(
            file_path: str, content: str, encoding: str = "utf-8"
        ) -> str:
            """Writes content to a file with specified encoding."""
            return f"Enhanced write '{content}' to {file_path} with {encoding} encoding"

        # 验证工具属性
        assert hasattr(enhanced_write_file, "is_tool")
        assert enhanced_write_file.is_tool

        assert hasattr(enhanced_write_file, "tool_type")
        assert enhanced_write_file.tool_type == "write"

        assert hasattr(enhanced_write_file, "is_write")
        assert enhanced_write_file.is_write

        assert hasattr(enhanced_write_file, "resource_arg")
        assert enhanced_write_file.resource_arg == "file_path"

        # 验证元数据
        assert hasattr(enhanced_write_file, "metadata")
        metadata = enhanced_write_file.metadata
        assert isinstance(metadata, ToolMetadata)
        assert metadata.name == "enhanced_write_file"
        assert metadata.description == "Writes content to a file with enhanced features"
        assert metadata.tool_type == "write"
        assert metadata.resource_arg == "file_path"
        assert metadata.category == "file_operations"

        # 验证输入模式
        assert hasattr(enhanced_write_file, "input_schema")
        schema_fields = enhanced_write_file.input_schema.model_fields
        assert "file_path" in schema_fields
        assert "content" in schema_fields
        assert "encoding" in schema_fields
        assert schema_fields["encoding"].default == "utf-8"

    def test_tool_extension_manager_registration(self):
        """测试工具扩展管理器的注册功能"""
        extension_manager = ToolExtensionManager()

        @tool(category="math")
        def power(base: float, exponent: float) -> float:
            """Calculates base raised to the power of exponent."""
            return base**exponent

        # 注册工具
        extension_manager.register_tool(power)

        # 验证工具已注册
        assert "power" in extension_manager.registry.list_tools()

        # 验证工具信息
        tool_info = extension_manager.get_tool_info("power")
        assert tool_info["name"] == "power"
        assert tool_info["category"] == "math"
        assert (
            tool_info["description"]
            == "Calculates base raised to the power of exponent."
        )
        assert "base" in tool_info["input_schema"]
        assert "exponent" in tool_info["input_schema"]

    def test_tool_extension_without_modifying_existing_code(self):
        """测试新增工具无需修改现有代码"""
        # 使用现有的ToolManager
        manager = ToolManager()
        manager.tool_permission_config = ToolPermissionConfig(default="allow")

        # 创建扩展管理器
        extension_manager = ToolExtensionManager()

        # 定义新工具
        @tool(category="math")
        def subtract(a: int, b: int) -> int:
            """Subtracts b from a."""
            return a - b

        # 通过扩展管理器注册
        extension_manager.register_tool(subtract)

        # 将工具注册到现有的ToolManager
        manager.register_tool(subtract)

        # 验证工具可以被现有系统使用
        session_context = SessionContext()
        result = manager.execute_tool("subtract", {"a": 10, "b": 3}, session_context)

        assert result == "7"
        assert "subtract" in manager._registry

    def test_tool_extension_interface_compliance(self):
        """测试新增工具符合接口规范"""
        extension_manager = ToolExtensionManager()

        # 定义符合接口规范的新工具
        @tool(tool_type="read", resource_arg="path", category="file_system")
        def read_config(path: str) -> dict[str, Any]:
            """Reads configuration from a file."""
            return {"key": "value", "path": path}

        @tool(tool_type="write", resource_arg="path", category="file_system")
        def write_config(path: str, config: dict[str, Any]) -> str:
            """Writes configuration to a file."""
            return f"Written config to {path}"

        # 注册工具
        extension_manager.register_tool(read_config)
        extension_manager.register_tool(write_config)

        # 验证工具信息
        read_info = extension_manager.get_tool_info("read_config")
        assert read_info["type"] == "read"
        assert read_info["resource_arg"] == "path"
        assert read_info["category"] == "file_system"

        write_info = extension_manager.get_tool_info("write_config")
        assert write_info["type"] == "write"
        assert write_info["resource_arg"] == "path"
        assert write_info["category"] == "file_system"

        # 验证输入模式
        assert "path" in read_info["input_schema"]
        assert "path" in write_info["input_schema"]
        assert "config" in write_info["input_schema"]

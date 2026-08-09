"""Tests for tool extension mechanism."""

from daip_live.core.models import SessionContext, ToolPermissionConfig
from daip_live.p4_role_manager_tools.tool_manager import ToolManager
from daip_live.p4_role_manager_tools.tools import tool


class TestToolExtension:
    """测试工具扩展机制"""

    def test_tool_extension_without_modifying_existing_code(self):
        """测试新增工具无需修改现有代码"""
        # 创建工具管理器
        manager = ToolManager()
        manager.tool_permission_config = ToolPermissionConfig(default="allow")

        # 定义一个新工具，不修改现有代码
        @tool
        def multiply(x: int, y: int) -> int:
            """Multiplies two numbers."""
            return x * y

        # 注册新工具
        manager.register_tool(multiply)

        # 验证工具可以被发现和执行
        session_context = SessionContext()
        result = manager.execute_tool("multiply", {"x": 3, "y": 4}, session_context)

        assert result == "12"
        assert "multiply" in manager._registry

    def test_tool_extension_interface_compliance(self):
        """测试新增工具符合接口规范"""
        # 创建工具管理器
        manager = ToolManager()
        manager.tool_permission_config = ToolPermissionConfig(default="allow")

        # 定义符合接口规范的新工具
        @tool(tool_type="read", resource_arg="file_path")
        def read_file_custom(file_path: str) -> str:
            """Reads content from a file."""
            return f"Custom read content from {file_path}"

        @tool(tool_type="write", resource_arg="file_path")
        def write_file_custom(file_path: str, content: str) -> str:
            """Writes content to a file."""
            return f"Custom write '{content}' to {file_path}"

        # 注册工具
        manager.register_tool(read_file_custom)
        manager.register_tool(write_file_custom)

        # 验证读工具符合规范
        session_context = SessionContext()
        read_result = manager.execute_tool(
            "read_file_custom", {"file_path": "test.txt"}, session_context
        )
        assert "Custom read content from test.txt" in read_result

        # 验证写工具符合规范
        # 先添加到已读资源中以满足写后读约束
        session_context.recently_read_resources.add("test.txt")
        write_result = manager.execute_tool(
            "write_file_custom",
            {"file_path": "test.txt", "content": "hello"},
            session_context,
        )
        assert "Custom write 'hello' to test.txt" in write_result

        # 验证工具元数据
        assert hasattr(read_file_custom, "input_schema")
        assert hasattr(read_file_custom, "is_tool")
        assert hasattr(read_file_custom, "tool_type")
        assert read_file_custom.tool_type == "read"
        assert not read_file_custom.is_write

        assert hasattr(write_file_custom, "input_schema")
        assert hasattr(write_file_custom, "is_tool")
        assert hasattr(write_file_custom, "tool_type")
        assert write_file_custom.tool_type == "write"
        assert write_file_custom.is_write

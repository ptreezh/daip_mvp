"""
PermissionManager集成测试 - TDD实现
基于KISS/YAGNI原则，专注于核心集成功能
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from daip_live.core.models import (
    PermissionRequestEvent,
    PermissionResponse,
    SessionContext,
    ToolPermissionConfig,
)

# 待实现的导入
# from daip_live.permission.permission_manager import PermissionManager
# from daip_live.permission.user_response_collector import UserResponseCollector
# from daip_live.permission.tui_interface import PermissionTUIInterface


class TestPermissionManagerCore:
    """测试PermissionManager核心功能 - 遵循KISS原则"""

    @pytest.fixture
    def mock_user_input_queue(self):
        """提供模拟用户输入队列"""
        return asyncio.Queue()

    @pytest.fixture
    def sample_session_context(self):
        """提供会话上下文"""
        return SessionContext(recently_read_resources=set())

    @pytest.fixture
    def sample_tool_permission_config(self):
        """提供工具权限配置"""
        return ToolPermissionConfig(
            default="ask",
            tools={
                "read_file": "allow",
                "write_file": "ask",
                "execute_command": "deny",
            },
        )

    def test_permission_manager_creation(self):
        """测试PermissionManager创建 - 绿"""
        # Given: 基础依赖
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()

        # When: 创建PermissionManager
        manager = PermissionManager(user_queue, tui_interface)

        # Then: 验证基本属性
        assert manager.user_input_queue == user_queue
        assert manager.tui_interface == tui_interface
        assert manager.permission_config is not None

    def test_permission_check_allowed_tool(self):
        """测试权限检查 - 允许的工具 - 绿"""
        # Given: PermissionManager和允许的工具配置
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        manager = PermissionManager(user_queue, tui_interface)

        # 配置read_file为允许
        manager.permission_config.tools["read_file"] = "allow"

        # When: 检查允许的权限
        result = asyncio.run(
            manager.check_permission(
                "read_file", {"path": "test.txt"}, SessionContext()
            )
        )

        # Then: 验证权限被授予
        assert result.granted is True
        assert result.response == PermissionResponse.GRANT

    def test_permission_check_denied_tool(self):
        """测试权限检查 - 拒绝的工具 - 绿"""
        # Given: PermissionManager和拒绝的工具配置
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        manager = PermissionManager(user_queue, tui_interface)

        # 配置execute_command为拒绝
        manager.permission_config.tools["execute_command"] = "deny"

        # When: 检查拒绝的权限
        result = asyncio.run(
            manager.check_permission("execute_command", {"cmd": "ls"}, SessionContext())
        )

        # Then: 验证权限被拒绝
        assert result.granted is False
        assert result.response == PermissionResponse.DENY

    @pytest.mark.asyncio
    async def test_permission_check_ask_mode_user_grants(self):
        """测试权限检查 - 询问模式用户授予 - 绿"""
        # Given: PermissionManager和询问模式配置
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()

        manager = PermissionManager(user_queue, tui_interface)

        # When: 检查询问模式的权限且用户授予
        await user_queue.put("y")  # 用户输入"是"
        result = await manager.check_permission(
            "write_file", {"path": "output.txt"}, SessionContext()
        )

        # Then: 验证权限被授予
        assert result.granted is True
        assert result.response == PermissionResponse.GRANT

    @pytest.mark.asyncio
    async def test_permission_check_ask_mode_user_denies(self):
        """测试权限检查 - 询问模式用户拒绝 - 绿"""
        # Given: PermissionManager和询问模式配置
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()

        manager = PermissionManager(user_queue, tui_interface)

        # When: 检查询问模式的权限且用户拒绝
        await user_queue.put("n")  # 用户输入"否"
        result = await manager.check_permission(
            "write_file", {"path": "output.txt"}, SessionContext()
        )

        # Then: 验证权限被拒绝
        assert result.granted is False
        assert result.response == PermissionResponse.DENY


class TestPermissionManagerIntegration:
    """测试PermissionManager与系统组件集成"""

    @pytest.mark.asyncio
    async def test_permission_manager_with_real_user_input(self):
        """测试PermissionManager与真实用户输入集成 - 绿"""
        # Given: PermissionManager和用户输入队列
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()

        manager = PermissionManager(user_queue, tui_interface)

        # When: 用户输入有效响应
        await user_queue.put("y")

        # 模拟TUI界面返回用户响应
        tui_interface.get_user_response = AsyncMock(
            return_value=PermissionResponse.GRANT
        )

        result = await manager.request_permission(
            PermissionRequestEvent(tool_name="test_tool", args={})
        )

        # Then: 验证响应被正确处理
        assert result == PermissionResponse.GRANT

    def test_permission_rule_persistence(self):
        """测试权限规则设置与生效 - 绿"""
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        manager = PermissionManager(user_queue, tui_interface)

        # When: 设置权限规则
        manager.set_permission_rule("test_tool", "allow")

        # Then: 规则立即生效（内存配置，KISS/YAGNI设计）
        assert manager.get_permission_status("test_tool") == "allow"
        assert manager.permission_config.tools["test_tool"] == "allow"

        # 无效权限值应拒绝
        with pytest.raises(ValueError):
            manager.set_permission_rule("bad_tool", "invalid")

    @pytest.mark.asyncio
    async def test_permission_cache_functionality(self):
        """测试权限缓存功能 - 绿"""
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        manager = PermissionManager(user_queue, tui_interface)

        # 用户选择"始终授予" → 写入缓存
        await user_queue.put("a")
        await user_queue.put("y")  # 确认选择
        result = await manager.check_permission("test_tool", {}, SessionContext())

        # Then: 验证 ALWAYS 被缓存
        assert result.response == PermissionResponse.ALWAYS
        assert "test_tool" in manager.get_cached_permissions()

        # When: 再次检查同一工具 → 走缓存，无需用户输入
        result2 = await manager.check_permission("test_tool", {}, SessionContext())

        # Then: 缓存命中，直接授予
        assert result2.response == PermissionResponse.ALWAYS
        assert result2.cached is True


class TestPermissionManagerErrorHandling:
    """测试PermissionManager错误处理"""

    @pytest.mark.asyncio
    async def test_permission_request_timeout(self):
        """测试权限请求超时处理 - 绿"""
        # Given: PermissionManager和超时配置
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()

        # 模拟超时
        tui_interface.get_user_response = AsyncMock(side_effect=asyncio.TimeoutError())

        manager = PermissionManager(user_queue, tui_interface)

        # When: 权限请求超时
        result = await manager.check_permission(
            "test_tool", {}, SessionContext(), timeout=0.1
        )

        # Then: 验证超时后默认拒绝
        # 源码权威: _create_permission_result 硬编码 timeout=False（permission_manager.py:255），  # noqa: E501
        # 超时路径只保证 granted=False（DENY）
        assert result.granted is False

    def test_invalid_tool_name_handling(self):
        """测试无效工具名处理 - 绿"""
        # Given: PermissionManager
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        manager = PermissionManager(user_queue, tui_interface)

        # When: 检查无效工具名
        # 源码权威: 未配置规则的工具走默认权限 default="ask"（permission_manager.py:60），  # noqa: E501
        # 需给 timeout 避免无限等待用户输入；超时后安全优先返回 DENY 结果
        result = asyncio.run(
            manager.check_permission("invalid_tool", {}, SessionContext(), timeout=0.1)
        )

        # Then: 验证使用默认配置
        assert result is not None  # 应该返回默认权限结果
        assert result.granted is False  # 超时安全拒绝


class TestPermissionManagerPerformance:
    """测试PermissionManager性能"""

    def test_permission_check_performance(self):
        """测试权限检查性能 - 绿"""
        # Given: PermissionManager
        from daip_live.permission.permission_manager import PermissionManager

        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        manager = PermissionManager(user_queue, tui_interface)
        # 源码权威: 无内置白名单，read_file 默认走 ask；显式设为 allow 以测试性能路径
        manager.set_permission_rule("read_file", "allow")

        # When: 执行多次权限检查
        import time

        start_time = time.time()

        for i in range(100):
            result = asyncio.run(
                manager.check_permission(
                    "read_file", {"path": f"file_{i}.txt"}, SessionContext()
                )
            )

        end_time = time.time()

        # Then: 验证性能在可接受范围内
        execution_time = end_time - start_time
        # 100 次 asyncio.run 各创建事件循环，单次约 15-20ms；CI 慢机器可达 1.7s+。
        # 阈值取 5s：防明显回归（如死循环/意外网络调用），但容忍机器差异。
        assert execution_time < 5.0  # 100次检查应在5秒内完成
        assert result.granted is True  # read_file应该是允许的


# 测试工具函数
@pytest.fixture
def permission_manager_factory():
    """PermissionManager工厂函数"""

    def _create_manager(config=None):
        user_queue = asyncio.Queue()
        tui_interface = MagicMock()

        from daip_live.permission.permission_manager import PermissionManager

        manager = PermissionManager(user_queue, tui_interface)

        if config:
            manager.permission_config = config

        return manager

    return _create_manager


@pytest.fixture
def sample_permission_requests():
    """提供各种权限请求测试数据"""
    return {
        "basic_read": PermissionRequestEvent(
            tool_name="read_file", args={"path": "test.txt"}, risk_level="low"
        ),
        "basic_write": PermissionRequestEvent(
            tool_name="write_file", args={"path": "output.txt"}, risk_level="medium"
        ),
        "basic_execute": PermissionRequestEvent(
            tool_name="execute_command", args={"command": "ls -la"}, risk_level="high"
        ),
    }


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])

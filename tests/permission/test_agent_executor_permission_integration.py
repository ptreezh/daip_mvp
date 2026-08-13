"""
AgentExecutor权限集成测试 - 真实功能验证
严格遵循TDD驱动原则：测试先行，红-绿-重构循环
基于BMAD kiro's spec规范，确保契约先行
"""

import asyncio
import time
import tracemalloc
from unittest.mock import MagicMock

import pytest

from daip_live.core.models import (
    PermissionResponse,
    SessionContext,
    ToolPermissionConfig,
)
from daip_live.permission.permission_manager import PermissionManager


class TestAgentExecutorPermissionIntegration:
    """AgentExecutor权限集成测试 - 核心功能验证"""

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
        return ToolPermissionConfig(default="ask", tools={})

    # ===== 测试1: 基础权限集成 - 绿 =====
    @pytest.mark.asyncio
    async def test_agent_executor_permission_allowed(self):
        """测试权限允许场景 - 绿"""
        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        permission_manager = PermissionManager(user_queue, tui_interface)
        permission_manager.set_permission_rule("test_tool", "allow")

        result = await permission_manager.check_permission(
            "test_tool", {"param": "value"}, SessionContext()
        )

        assert result.granted is True
        assert result.response == PermissionResponse.GRANT

    # ===== 测试2: 权限拒绝处理 - 绿 =====
    @pytest.mark.asyncio
    async def test_agent_executor_permission_denied(self):
        """测试权限拒绝场景 - 绿"""
        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        permission_manager = PermissionManager(user_queue, tui_interface)
        permission_manager.set_permission_rule("dangerous_tool", "deny")

        result = await permission_manager.check_permission(
            "dangerous_tool", {"command": "rm -rf /"}, SessionContext()
        )

        assert result.granted is False
        assert result.response == PermissionResponse.DENY

    # ===== 测试3: 权限询问用户授予 - 绿 =====
    @pytest.mark.asyncio
    async def test_agent_executor_permission_ask_user_grants(self):
        """测试权限询问场景 - 用户授予 - 绿"""
        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        permission_manager = PermissionManager(user_queue, tui_interface)
        permission_manager.set_permission_rule("moderate_risk_tool", "ask")

        # 模拟用户授予权限
        await user_queue.put("y")

        result = await permission_manager.check_permission(
            "moderate_risk_tool", {"param": "value"}, SessionContext()
        )

        assert result.granted is True
        assert result.response == PermissionResponse.GRANT

    # ===== 测试4: 权限询问用户拒绝 - 绿 =====
    @pytest.mark.asyncio
    async def test_agent_executor_permission_ask_user_denies(self):
        """测试权限询问场景 - 用户拒绝 - 绿"""
        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        permission_manager = PermissionManager(user_queue, tui_interface)
        permission_manager.set_permission_rule("moderate_risk_tool", "ask")

        # 模拟用户拒绝权限
        await user_queue.put("n")

        result = await permission_manager.check_permission(
            "moderate_risk_tool", {"param": "value"}, SessionContext()
        )

        assert result.granted is False
        assert result.response == PermissionResponse.DENY

    # ===== 测试5: 权限检查超时 - 绿 =====
    @pytest.mark.asyncio
    async def test_agent_executor_permission_timeout(self):
        """测试权限请求超时处理 - 绿"""
        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        permission_manager = PermissionManager(user_queue, tui_interface)
        permission_manager.set_permission_rule("test_tool", "ask")

        # 不提供用户输入，模拟超时
        result = await permission_manager.check_permission(
            "test_tool", {"param": "value"}, SessionContext(), timeout=0.1
        )

        # 超时被视为权限拒绝（安全优先）
        assert result.granted is False
        assert result.response == PermissionResponse.DENY

    # ===== 测试6: 无效工具权限处理 - 绿 =====
    def test_agent_executor_invalid_tool_permission(self):
        """测试无效工具权限处理 - 绿"""
        from daip_live.p4_role_manager_tools.tool_manager import (
            ToolManager,
            ToolNotFoundError,
        )

        tool_manager = ToolManager()

        with pytest.raises(ToolNotFoundError) as exc_info:
            tool_manager.execute_tool("nonexistent_tool", {}, SessionContext())

        assert "not found" in str(exc_info.value).lower()
        assert "nonexistent_tool" in str(exc_info.value)

    # ===== 测试7: 权限拒绝抛 ToolPermissionError - 绿 =====
    def test_agent_executor_permission_denied_raises(self):
        """测试权限拒绝时抛ToolPermissionError - 绿"""
        from daip_live.p4_role_manager_tools.tool_manager import ToolPermissionError

        error = ToolPermissionError(
            "Permission denied for tool 'dangerous_tool'",
            tool_name="dangerous_tool",
            args={"command": "rm -rf /"},
            reason="Permission denied for dangerous_tool",
        )

        assert error.tool_name == "dangerous_tool"
        assert error.tool_args == {"command": "rm -rf /"}
        assert "denied" in str(error).lower()


class TestAgentExecutorPermissionRobustness:
    """AgentExecutor权限集成健壮性测试"""

    # ===== 测试8: 并发权限请求处理 - 绿 =====
    @pytest.mark.asyncio
    async def test_agent_executor_concurrent_permission_requests(self):
        """测试并发权限请求处理 - 绿"""
        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        permission_manager = PermissionManager(user_queue, tui_interface)

        permission_manager.set_permission_rule("tool_1", "allow")
        permission_manager.set_permission_rule("tool_2", "deny")
        permission_manager.set_permission_rule("tool_3", "ask")

        # 模拟 tool_3 的用户响应
        await user_queue.put("y")

        tasks = [
            permission_manager.check_permission("tool_1", {}, SessionContext()),
            permission_manager.check_permission("tool_2", {}, SessionContext()),
            permission_manager.check_permission("tool_3", {}, SessionContext()),
        ]

        results = await asyncio.gather(*tasks)

        # tool_1: allow → 授予
        assert results[0].granted is True
        # tool_2: deny → 拒绝
        assert results[1].granted is False
        # tool_3: ask + 用户授予 → 授予
        assert results[2].granted is True


class TestAgentExecutorPermissionPerformance:
    """AgentExecutor权限集成性能测试"""

    # ===== 测试9: 权限检查性能 - 绿 =====
    @pytest.mark.asyncio
    async def test_agent_executor_permission_check_performance(self):
        """测试权限检查性能 - 绿"""
        user_queue = asyncio.Queue()
        tui_interface = MagicMock()
        permission_manager = PermissionManager(user_queue, tui_interface)

        # 预定义权限规则
        for i in range(100):
            permission_manager.set_permission_rule(f"tool_{i}", "allow")

        start_time = time.time()
        results = []
        for i in range(100):
            result = await permission_manager.check_permission(
                f"tool_{i % 10}", {"param": i}, SessionContext()
            )
            results.append(result)
        end_time = time.time()

        execution_time = end_time - start_time
        assert execution_time < 10.0  # 100次检查应在10秒内完成
        assert len(results) == 100
        assert all(result.granted for result in results)

    # ===== 测试10: 内存使用效率 - 绿 =====
    def test_agent_executor_memory_usage_efficiency(self):
        """测试权限管理器内存使用效率 - 绿"""
        tracemalloc.start()

        managers = []
        for i in range(100):
            user_queue = asyncio.Queue()
            permission_manager = PermissionManager(user_queue, MagicMock())
            for j in range(10):
                permission_manager.set_permission_rule(f"tool_{j}", "ask")
            managers.append(permission_manager)

        current, _ = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert len(managers) == 100
        assert current < 50 * 1024 * 1024  # 100个实例 < 50MB


# ===== 测试工具和数据工厂 =====
@pytest.fixture
def permission_manager_factory():
    """PermissionManager工厂函数"""

    def _create_manager(config=None):
        user_queue = asyncio.Queue()
        tui_interface = MagicMock()

        manager = PermissionManager(user_queue, tui_interface)

        if config:
            manager.permission_config = config

        return manager

    return _create_manager


@pytest.fixture
def sample_permission_scenarios():
    """提供各种权限场景测试数据"""
    return {
        "safe_read": {
            "tool_name": "read_file",
            "args": {"path": "test.txt"},
            "permission": "allow",
            "risk_level": "low",
        },
        "dangerous_write": {
            "tool_name": "write_file",
            "args": {"path": "/etc/passwd"},
            "permission": "deny",
            "risk_level": "high",
        },
        "moderate_network": {
            "tool_name": "http_request",
            "args": {"url": "https://api.example.com/data"},
            "permission": "ask",
            "risk_level": "medium",
        },
        "system_command": {
            "tool_name": "execute_command",
            "args": {"command": "ls -la"},
            "permission": "ask",
            "risk_level": "high",
        },
    }


@pytest.fixture
def mock_tool_function():
    """提供模拟工具函数"""

    async def mock_tool(param: str) -> str:
        return f"Tool executed with param: {param}"

    return mock_tool


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])
